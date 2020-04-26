#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

"""
# !!! This is the new correct way (the imp module is considered obsolete)
if "bpy" in locals():
    import importlib
    if "import_obj" in locals():
        importlib.reload(import_obj)
    if "export_obj" in locals():
        importlib.reload(export_obj)
"""

import os
import itertools
import json
import time
import random
import inspect
import sys
import traceback

import bpy

from mathutils import Vector, Matrix, Quaternion, Euler, Color

from .version import version
from .utils_python import next_catch, send_catch, ensure_baseclass, issubclass_safe, PrimitiveLock, AttributeHolder, SilentError, attrs_to_dict, dict_to_attrs
from .utils_text import compress_whitespace, indent, unindent
from .utils_gl import cgl
from .utils_ui import messagebox, NestedLayout, ButtonRegistrator, ui_context_under_coord
from .utils_userinput import KeyMapUtils
from .bpy_inspect import BlEnums, BlRna, BpyProp, BpyOp, prop
from .utils_blender import ResumableSelection
from .utils_view3d import ZBufferRecorder

#============================================================================#

# Some tips for [regression] testing:
# * Enable -> disable -> enable
# * Enabled by default, disabled by default
# * Default scene, scene saved without addon, scene saved with addon
# * Stable Blender, nightly build, GSOC/open-project branch

# TODO: "load/save/import/export config" buttons in addon preferences (draw() method)

# ===== ADDON MANAGER ===== #
class AddonManager:
    _textblock_prefix = "textblock://"
    
    _screen_name = "Default"
    _screen_mark = "\x02{addon-internal-storage}\x03"
    
    _hack_classes_count = 0
    
    # ===== INITIALIZATION ===== #
    def __new__(cls, name=None, path=None, config=None):
        varname = "__<blender-addon>__"
        info = AddonManager._init_info(name, path, config, varname)
        
        self = info.get("addon")
        if self is not None: return self # one alreasy exists for this addon
        
        self = object.__new__(cls)
        self.status = 'INITIALIZATION'
        
        self.name = info["name"] # displayable name
        self.path = info["path"] # directory of the main file
        self.module_name = info["module_name"]
        self.is_textblock = info["is_textblock"]
        self.storage_path = info["config_path"]
        
        self.classes = []
        self.objects = {}
        self.attributes = {}
        self.attributes_by_pointer = {}
        self.delayed_reg_info = []
        
        self._preferences = None
        
        self._use_zbuffer = False
        
        self._on_register = []
        self._on_unregister = []
        self._after_register = []
        
        self._ui_monitor = []
        self._scene_update_pre = []
        self._scene_update_post = []
        self._load_pre = []
        self._load_post = []
        self._background_job = []
        self._selection_job = []
        
        self._init_config_storages()
        
        info["module_globals"][varname] = self
        
        return self
    
    def _init_config_storages(self):
        #self.storage_name = "<%s>" % self.module_name
        self.storage_name_external = "<%s-external-storage>" % self.module_name
        self.storage_name_internal = "<%s-internal-storage>" % self.module_name
        
        @classmethod
        def Include(cls, decor_cls):
            for name in dir(decor_cls):
                if not (name.startswith("__") and name.endswith("__")):
                    setattr(cls, name, getattr(decor_cls, name))
            return cls
        
        # Attention: AddonPreferences do not allow adding properties
        # after registration, so we need to register it as a special case
        self._Preferences = type("%s-preferences" % self.module_name, (bpy.types.AddonPreferences,), {"Include":Include, "bl_idname":self.module_name})
        self._External = self.PropertyGroup(type("%s-external-storage" % self.module_name, (), {"Include":Include}))
        self._Internal = self.PropertyGroup(type("%s-internal-storage" % self.module_name, (), {"Include":Include}))
        
        self._Runtime = type("%s-runtime-settings" % self.module_name, (AttributeHolder,), {})
        self._runtime = self._Runtime()
    
    # If this is a textblock, its module will be topmost
    # and will have __name__ == "__main__".
    # If this is an addon in the scripts directory, it will
    # be recognized by blender only if it contains bl_info.
    @classmethod
    def _init_info(cls, name, path, config, varname):
        module_globals = None
        module_locals = None
        module_name = None
        
        for frame_record in reversed(inspect.stack()):
            # Frame record is a tuple of 6 elements:
            # (frame_obj, filename, line_id, func_name, context_lines, context_line_id)
            frame = frame_record[0]
            
            if not module_name:
                module_globals = frame.f_globals
                module_locals = frame.f_locals
                module_name = module_globals.get("__name__", "").split(".")[0]
                _path = module_globals.get("__file__", "")
                _name = os.path.splitext(os.path.basename(_path))[0]
            
            info = frame.f_globals.get("bl_info")
            if info:
                module_globals = frame.f_globals
                module_locals = frame.f_locals
                module_name = module_globals.get("__name__", "").split(".")[0]
                _path = module_globals.get("__file__", "")
                _name = info.get("name", _name)
                break
        
        if varname in module_globals:
            addon = module_globals[varname]
            if isinstance(addon, AddonManager):
                if addon.status == 'INITIALIZATION':
                    return dict(addon=addon) # use this addon object
        
        is_textblock = (module_name == "__main__")
        if is_textblock:
            module_name = os.path.splitext(os.path.basename(_path))[0]
            config_path = cls._textblock_prefix
        else:
            config_path = bpy.utils.user_resource('CONFIG', module_name)
        
        name = name or _name
        path = path or _path
        
        if not os.path.isdir(path):
            # directories/single_file_addon.py
            # directories/some_blend.blend/TextBlockName
            path = os.path.dirname(path)
        
        if os.path.isfile(path):
            # directories/some_blend.blend
            path = os.path.dirname(path)
        
        if not os.path.isdir(path):
            # No such directory in the filesystem
            path = cls._textblock_prefix
        
        if not config:
            config = (bpy.path.clean_name(module_name) if is_textblock else "config") + ".json"
        
        config_path = os.path.join(config_path, config)
        
        return dict(name=name, path=path, config_path=config_path,
                    module_name=module_name, is_textblock=is_textblock,
                    module_locals=module_locals, module_globals=module_globals)
    #========================================================================#
    
    # ===== PREFERENCES / EXTERNAL / INTERNAL ===== #
    # Prevent accidental assignment
    Preferences = property(lambda self: self._Preferences)
    External = property(lambda self: self._External)
    Internal = property(lambda self: self._Internal)
    Runtime = property(lambda self: self._Runtime)
    
    preferences = property(lambda self: self._preferences)
    external = property(lambda self: self.external_attr(self.storage_name_external))
    internal = property(lambda self: self.internal_attr(self.storage_name_internal))
    runtime = property(lambda self: self._runtime)
    
    @classmethod
    def external_attr(cls, name):
        wm = bpy.data.window_managers[0]
        return getattr(wm, name, None)
    
    @classmethod
    def internal_attr(cls, name):
        screen = None
        try:
            screen = bpy.data.screens[cls._screen_name]
            assert cls._screen_mark in screen
        except (KeyError, AssertionError):
            if screen is None:
                # Re-find our screen
                for screen in bpy.data.screens:
                    if cls._screen_mark in screen:
                        cls._screen_name = screen.name
                        break
            # Make sure it is marked as "our"
            screen[cls._screen_mark] = True
        return getattr(screen, name, None)
    
    def path_resolve(self, path, coerce=True):
        if path.startswith(self.storage_name_external):
            obj = self.external
            path = path[len(self.storage_name_external) + 1:]
        elif path.startswith(self.storage_name_internal):
            obj = self.internal
            path = path[len(self.storage_name_internal) + 1:]
        else:
            raise ValueError("Path '%s' could not be resolved" % path)
        return obj.path_resolve(path, coerce)
    
    def external_load(self):
        obj = self.external
        
        if not obj:
            return
        
        path = self.storage_path
        
        if path.startswith(self._textblock_prefix):
            path = path[len(self._textblock_prefix):]
            text_block = bpy.data.texts.get(path)
            if not text_block:
                return
            text = text_block.as_string()
        else:
            try:
                # Settings are expected to be written by
                # the addon, so it shouldn't be necessary
                # to handle BOM-marks and encodings.
                with open(path, "r") as f:
                    text = f.read()
            except IOError:
                return
        
        try:
            data = json.loads(text)
        except ValueError:
            # Maybe display a warning?
            return
        
        BpyProp.deserialize(obj, data, use_skip_save=True)
    
    def external_save(self):
        obj = self.external
        
        if not obj:
            return
        
        data = BpyProp.serialize(obj, use_skip_save=True)
        
        text = json.dumps(data, indent=2)
        
        path = self.storage_path
        
        if path.startswith(self._textblock_prefix):
            path = path[len(self._textblock_prefix):]
            text_block = bpy.data.texts.get(path)
            if not text_block:
                text_block = bpy.data.texts.new(path)
            text_block.from_string(text)
        else:
            try:
                with open(path, "w") as f:
                    f.write(text)
            except IOError:
                messagebox("%s: failed to write config file\n\"%s\"" % (self.name, self.storage_path), 'ERROR')
                return
    #========================================================================#
    
    # ===== PYTHON STORAGE ===== #
    def __getitem__(self, obj):
        """
        Due to the implementation, bpy_struct/PropertyGroup instances
        don't hold arbitrary python attributes. This is due to the fact
        that these python instances are actually constructed each time
        you access them, e.g.:
        
        print(addon.external.obj is addon.external.obj) # prints False
        
        This makes it impossible to store arbitrary python objects in
        instances of PropertyGroups -- only value types supported by
        bpy.props.* and bpy_struct[*] can make it to the next access.
        
        Here I try to map a blender [PropertyGroup] object to a python
        object. Using proxy objects or their pointers is not reliable,
        since the corresponding chunks of bytes can change their addresses.
        So, we can make a UUID for each encountered object and store it as
        a dynamic property, but we still don't have a way to perform a
        reverse operation (find an object by its UUID) other than by
        walking through the reference graph.
        
        This means that the dictionary will only grow with time, and
        we cannot automatically tell when an object related to some
        UUID has been deleted (at least not with the current API).
        The amount of such memory leaking depends on how frequently
        new objects requiring python storage are created and deleted.
        Perhaps in majority of cases it's largely unnoticeable and
        is naturally solved by unregistering the addon or by restarting
        Blender. Also, it's always possible to do manual "memory
        management" by revoking the storage when an object is about
        to be deleted. And, as a last resort, we can also have a
        stop-the-world tracing garbage collector.
        """
        
        # obj is expected to have the corresponding property defined;
        # if not, then storage request is a mistake
        
        if isinstance(obj, BlEnums.extensible_classes):
            ID = addons_registry.UUID_get(obj)
            storage = self.attributes.get(ID)
            
            if storage is None:
                # Note: ID might be != 0 if this item was saved
                # in previous session. It should be reindexed anyway.
                ID = addons_registry.UUID_counter + 1
                addons_registry.UUID_counter = ID
                addons_registry.UUID_set(obj, ID)
                
                storage = AttributeHolder(type(obj))
                self.attributes[ID] = storage
                
                # With this mechanism, __init__ methods in PropertyGroup
                # objects can actually do something useful (perhaps do
                # some complex initialization).
                if hasattr(obj, "__init__"): obj.__init__()
        else: # e.g. Area, Space, Region and the like
            ID = obj.as_pointer()
            storage = self.attributes_by_pointer.get(ID)
            
            if storage is None:
                storage = AttributeHolder()
                self.attributes_by_pointer[ID] = storage
        
        return storage
    #========================================================================#
    
    # ===== HANDLERS AND TYPE EXTENSIONS ===== #
    @property
    def use_zbuffer(self):
        return self._use_zbuffer
    @use_zbuffer.setter
    def use_zbuffer(self, value):
        if self._use_zbuffer == value: return
        if self.status == 'REGISTERED':
            addons_registry.zbuf_users += (1 if value else -1)
        self._use_zbuffer = value
    
    def on_register(self, callback):
        self._on_register.append(callback)
        return callback
    
    def on_unregister(self, callback):
        self._on_unregister.append(callback)
        return callback
    
    def after_register(self, callback):
        self._after_register.append(callback)
        return callback
    
    def ui_monitor(self, callback):
        self._ui_monitor.append(callback)
        return callback
    
    def scene_update_pre(self, callback):
        self._scene_update_pre.append(callback)
        return callback
    
    def scene_update_post(self, callback):
        self._scene_update_post.append(callback)
        return callback
    
    def load_pre(self, callback):
        self._load_pre.append(callback)
        return callback
    
    def load_post(self, callback):
        self._load_post.append(callback)
        return callback
    
    def background_job(self, callback):
        self._background_job.append(callback)
        return callback
    
    def selection_job(self, callback):
        self._selection_job.append(callback)
        return callback
    
    def view3d_draw(self, event, args=(), region='WINDOW', owner=None):
        def decorator(callback):
            self.draw_handler_add(bpy.types.SpaceView3D, callback, args, region, event, owner)
            return callback
        return decorator
    
    def timer_add(self, time_step, window=None, owner=None):
        if self.status == 'INITIALIZATION':
            self.delayed_reg_info.append(("timer_add", time_step, window, owner))
            return
        elif self.status in ('UNREGISTRATION', 'UNREGISTRED'):
            raise RuntimeError("Attempt to add timer during or after addon unregistration")
        
        wm = bpy.context.window_manager
        timer = wm.event_timer_add(time_step, window or bpy.context.window)
        
        self.objects[timer] = {
            "object":timer,
            "struct":wm,
            "family":"timer",
            "time_step":time_step,
            "window":window,
            "owner":owner,
        }
        
        return timer
    
    def ui_append(self, ui, draw_func, owner=None): # e.g. menus: bpy.types.*_MT_*.append()
        if self.status == 'INITIALIZATION':
            self.delayed_reg_info.append(("ui_append", ui, draw_func, owner))
            return
        elif self.status in ('UNREGISTRATION', 'UNREGISTRED'):
            raise RuntimeError("Attempt to append to UI during or after addon unregistration")
        
        if draw_func in self.objects: ui.remove(draw_func)
        ui.append(draw_func)
        
        if draw_func not in self.objects:
            self.objects[draw_func] = {
                "object":draw_func,
                "struct":ui,
                "family":"ui",
                "mode":"append",
                "owner":owner,
            }
        else:
            self.objects[draw_func]["mode"] = "append"
    
    def ui_prepend(self, ui, draw_func, owner=None): # e.g. menus: bpy.types.*_MT_*.prepend()
        if self.status == 'INITIALIZATION':
            self.delayed_reg_info.append(("ui_prepend", ui, draw_func, owner))
            return
        elif self.status in ('UNREGISTRATION', 'UNREGISTRED'):
            raise RuntimeError("Attempt to prepend to UI during or after addon unregistration")
        
        if draw_func in self.objects: ui.remove(draw_func)
        ui.prepend(draw_func)
        
        if draw_func not in self.objects:
            self.objects[draw_func] = {
                "object":draw_func,
                "struct":ui,
                "family":"ui",
                "mode":"prepend",
                "owner":owner,
            }
        else:
            self.objects[draw_func]["mode"] = "prepend"
    
    # Normally, there shouldn't be any need to extend PropertyGroups declared in other addons
    def type_extend(self, type_name, prop_name, prop_info, owner=None):
        if issubclass_safe(prop_info, bpy.types.PropertyGroup):
            prop_info = prop_info | prop()
        
        if self.status == 'INITIALIZATION':
            # bpy types can be extended only after the corresponding PropertyGroups have been registered
            self.delayed_reg_info.append(("type_extend", type_name, prop_name, prop_info, owner))
            return
        elif self.status in ('UNREGISTRATION', 'UNREGISTRED'):
            raise RuntimeError("Attempt to extend type during or after addon unregistration")
        
        prop_args = prop_info[1]
        pg = prop_args.get("type")
        if pg and pg.__name__.endswith(":AUTOREGISTER"):
            if pg not in self.classes:
                addons_registry.UUID_add(pg)
                self.classes.append(pg)
                bpy.utils.register_class(pg)
        
        struct = getattr(bpy.types, type_name)
        setattr(struct, prop_name, prop_info)
        
        if (type_name, prop_name) not in self.objects:
            self.objects[(type_name, prop_name)] = {
                "object":prop_name,
                "struct":struct,
                "family":"bpy_type",
                "owner":owner,
            }
    
    def handler_append(self, handler_name, callback, owner=None): # see bpy.app.handlers
        if self.status == 'INITIALIZATION':
            self.delayed_reg_info.append(("handler_append", handler_name, callback, owner))
            return
        elif self.status in ('UNREGISTRATION', 'UNREGISTRED'):
            raise RuntimeError("Attempt to append handler during or after addon unregistration")
        
        handlers = getattr(bpy.app.handlers, handler_name)
        if callback in self.objects: handlers.remove(callback)
        handlers.append(callback)
        
        if callback not in self.objects:
            self.objects[callback] = {
                "object":callback,
                "struct":handler_name,
                "family":"handler",
                "owner":owner,
            }
    
    def draw_handler_add(self, struct, callback, args, reg, event, owner=None):
        if self.status == 'INITIALIZATION':
            self.delayed_reg_info.append(("draw_handler_add", struct, callback, args, reg, event, owner))
            return
        elif self.status in ('UNREGISTRATION', 'UNREGISTRED'):
            raise RuntimeError("Attempt to add draw callback during or after addon unregistration")
        
        handler = struct.draw_handler_add(callback, args, reg, event)
        
        self.objects[handler] = {
            "object":handler,
            "struct":struct,
            "family":"draw_handler",
            "callback":callback,
            "args":args,
            "region_type":reg,
            "event":event,
            "owner":owner,
        }
        
        return handler
    
    def remove(self, item):
        info = self.objects.get(item)
        if not info: return
        
        struct = info["struct"]
        item_type = info["family"]
        
        if item_type == "timer":
            struct.event_timer_remove(item)
            info["object"] = None
        elif item_type == "ui":
            struct.remove(item)
        elif item_type == "bpy_type":
            delattr(struct, item[1])
        elif item_type == "handler":
            struct = getattr(bpy.app.handlers, struct)
            struct.remove(item)
        elif item_type == "draw_handler":
            struct.draw_handler_remove(item, info["region_type"])
            info["object"] = None
        
        del self.objects[item]
    
    def remove_matches(self, **filters):
        for item, info in tuple(self.objects.items()):
            if all((k in info) and (info[k] == v) for k, v in filters.items()):
                self.remove(item)
    
    def remove_all(self):
        for item in tuple(self.objects):
            self.remove(item)
    
    #========================================================================#
    
    # ===== REGISTER / UNREGISTER ===== #
    def register(self, load_config=False):
        self.status = 'REGISTRATION'
        
        refs = (bpy.props.PointerProperty, bpy.props.CollectionProperty)
        
        # External/Internal classes are added at AddonManager
        # initialization. If at a later point a property referencing
        # some PropertyGroup is added to External/Internal,
        # there would be registration error (the PropertyGroup
        # is further on the list, so it's not registered yet).
        # To also make possible "circular references" (though
        # that may be dangerous!), we just remove all pointer/collection
        # properties, register, then add the properties back.
        
        deps = {}
        
        extra_classes = set()
        
        # This is syntactic sugar for the case when callbacks
        # are defined later than the properties which use them.
        def find_callback(cls, info, name):
            callback = info.get(name)
            if isinstance(callback, str):
                info[name] = getattr(cls, callback)
        
        # Extract dependent properties
        for cls in self.classes:
            for key, info in BpyProp.iterate(cls):
                # Do some autocompletion on property descriptors
                if "name" not in info:
                    info["name"] = bpy.path.display_name(key)
                
                # This is syntactic sugar for the case when callbacks
                # are defined later than the properties which use them.
                find_callback(cls, info, "update")
                find_callback(cls, info, "get")
                find_callback(cls, info, "set")
                
                # Extract dependent properties
                if info.type in refs:
                    pg = info["type"]
                    
                    is_foreign = (pg not in self.classes)
                    
                    if is_foreign and pg.__name__.endswith(":AUTOREGISTER"):
                        addons_registry.UUID_add(pg)
                        extra_classes.add(pg)
                        is_foreign = False
                    
                    if not is_foreign:
                        # This property can actually reside in one of the
                        # base classes, so we need to search the MRO
                        for _cls in type.mro(cls):
                            if BpyProp.validate(_cls.__dict__.get(key)):
                                dep_key = (_cls, key)
                                if dep_key not in deps:
                                    deps[dep_key] = info()
                                # If some properties are overriden,
                                # we can't skip the ancestor classes!
                                #break
        
        self.classes.extend(extra_classes)
        
        # Temporarily remove properties...
        for dep_key in deps.keys():
            delattr(dep_key[0], dep_key[1])
        
        # Register classes
        for cls in self.classes:
            bpy.utils.register_class(cls)
        # Special cases:
        bpy.utils.register_class(self.Preferences)
        
        # Add properties back
        for dep_key, value in deps.items():
            setattr(dep_key[0], dep_key[1], value)
        
        # Infer whether external/internal storages are required
        # by looking at whether any properties were added
        # for them before register() was invoked
        
        if BpyProp.is_in(self.External):
            self.type_extend("WindowManager", self.storage_name_external, self.External)
        
        if BpyProp.is_in(self.Internal):
            self.type_extend("Screen", self.storage_name_internal, self.Internal)
        
        # Don't clear delayed_reg_info! We need it if addon is disabled->enabled again.
        for reg_info in self.delayed_reg_info:
            getattr(self, reg_info[0])(*reg_info[1:])
        
        self._refresh_preferences()
        
        if load_config: self.external_load()
        
        for callback in self._on_register:
            callback()
        
        addons_registry.add(self)
        
        if self.use_zbuffer: addons_registry.zbuf_users += 1
        
        self.status = 'REGISTERED'
    
    def unregister(self):
        self.status = 'UNREGISTRATION'
        
        self._preferences = None
        
        if self.use_zbuffer: addons_registry.zbuf_users -= 1
        
        addons_registry.remove(self)
        
        for callback in self._on_unregister:
            callback()
        
        self.attributes.clear()
        self.attributes_by_pointer.clear()
        
        self.remove_all()
        
        # Special cases:
        bpy.utils.unregister_class(self.Preferences)
        # Unregister classes
        for cls in reversed(self.classes):
            bpy.utils.unregister_class(cls)
        
        self.status = 'UNREGISTERED'
    
    def _refresh_preferences(self):
        # ATTENTION: trying to access preferences cached from previous session
        # will crash Blender. We must ensure the cached value is up-to-date.
        userprefs = bpy.context.user_preferences
        if self.module_name in userprefs.addons:
            self._preferences = userprefs.addons[self.module_name].preferences
        else:
            self._preferences = None
    #========================================================================#
    
    def _wrap_enum_on_item_invoke(self, prop_info):
        label = prop_info["name"]
        description = prop_info["description"]
        
        _hack_classes_count = self._hack_classes_count + 1
        type(self)._hack_classes_count = _hack_classes_count
        
        # TODO: maybe use keywords and syntax-error names?
        
        # OPERATOR
        op_idname = "hacks.hack_%s" % _hack_classes_count
        @self.Operator(idname=op_idname, label=label, description=description)
        class intermediate_operator:
            item = "" | prop() # make it HIDDEN ?
            def invoke(self, context, event):
                callback = prop_info.get("on_item_invoke")
                callback(self, context, event)
                return {'FINISHED'}
        
        # MENU
        menu_idname = "[Hack_Menu_%s]" % _hack_classes_count
        @self.Menu(idname=menu_idname, label=label, description=description)
        class intermediate_menu:
            def draw(self, context):
                layout = self.layout
                icons = prop_info.get("icons", {})
                for k, v, d in prop_info["items"]:
                    layout.operator(op_idname, text=v, icon=icons.get(k, 'NONE')).item = k
        
        # ADD METADATA TO PROPERTY
        prop_info["icons_menu"] = menu_idname
    
    # is this still necessary?
    def _wrap_enum_contextual_title(self, prop_info, cls, prop_name):
        label = cls.bl_label
        description = cls.__doc__
        
        _hack_classes_count = self._hack_classes_count + 1
        type(self)._hack_classes_count = _hack_classes_count
        
        # MENU
        title = prop_info["contextual_title"]
        menu_idname = "[Hack_Menu_%s]" % _hack_classes_count
        @self.Menu(idname=menu_idname, label=title, description=description)
        class intermediate_menu:
            def draw(self, context):
                layout = self.layout
                layout.operator_context = 'INVOKE_DEFAULT'
                icons = prop_info.get("icons", {})
                for k, v, d in prop_info["items"]:
                    op = layout.operator(cls.bl_idname, text=v,
                        icon=icons.get(k, 'NONE'))
                    setattr(op, prop_name, k)
        
        # OPERATOR
        op_idname = "hacks.hack_%s" % _hack_classes_count
        @self.Operator(idname=op_idname, label=label, description=description)
        class intermediate_operator:
            pass
        
        names = []
        for key, info in BpyProp.iterate(cls):
            bp = info(True)
            bp[1].pop("update", None)
            setattr(intermediate_operator, key, bp)
            names.append(key)
        
        def intermediate_invoke(self, context, event):
            for key in names:
                cls._intermediate_storage[key] = getattr(self, key)
            return bpy.ops.wm.call_menu(name=menu_idname)
        intermediate_operator.invoke = intermediate_invoke
        
        # EXTEND SOURCE CLASS
        if not hasattr(cls, "_intermediate_storage"):
            cls._intermediate_storage = {}
            
            _invoke = getattr(cls, "invoke", None)
            _execute = getattr(cls, "execute", None)
            
            def invoke(self, context, event):
                for k, v in self._intermediate_storage.items():
                    if k != prop_name: setattr(self, k, v)
                if _invoke: return _invoke(self, context, event)
                if _execute: return _execute(self, context)
            
            cls.invoke = invoke
        
        # ADD METADATA TO PROPERTY
        prop_info["op_invoke_menu"] = op_idname
    
    def _add_class(self, cls, mixins=None):
        if mixins:
            if isinstance(mixins, type): mixins = (mixins,)
            for mixin in mixins:
                for attr_name in dir(mixin):
                    if hasattr(cls, attr_name): continue
                    setattr(cls, attr_name, getattr(mixin, attr_name))
        
        # Register property-specific classes
        for key, info in BpyProp.iterate(cls):
            if info.type == bpy.props.EnumProperty:
                if "on_item_invoke" in info: # Deprecated? Use get/set instead?
                    self._wrap_enum_on_item_invoke(info)
                
                if "contextual_title" in info: # Deprecated? How was it supposed to be used, anyway?
                    if issubclass(cls, bpy.types.Operator):
                        self._wrap_enum_contextual_title(info, cls, key)
        
        self.classes.append(cls)
    
    # ===== REGISTRABLE TYPES DECORATORS ===== #
    @staticmethod
    def _poll_factory(modes, regions, spaces, poll):
        """Generate poll() method for several typical situations"""
        
        conditions = []
        
        def make_condition(attr, enum, enum_name):
            if enum is not None:
                op = ("==" if isinstance(enum, str) else "in")
                conditions.append("(context.%s %s %s)" % (attr, op, enum_name))
        
        make_condition("mode", modes, "modes")
        make_condition("region.type", regions, "regions")
        make_condition("space_data.type", spaces, "spaces")
        
        if poll:
            conditions.append("poll(context)")
        
        s = "lambda cls, context: %s" % " and ".join(conditions)
        
        return classmethod(eval(s, {"modes":modes, "regions":regions, "spaces":spaces, "poll":poll}, {}))
    
    @staticmethod
    def _normalize(enum_name, enum, enums, single_enum=False, substitutions=()):
        """Make sure enum attributes have proper format"""
        
        if single_enum:
            err_text = "%s must be one of the %s" % (enum_name, enums)
        else:
            err_text = "%s must be an item or a collection of items from %s" % (enum_name, enums)
        
        if isinstance(enum, str):
            enum = {enum}
        else:
            if single_enum: raise TypeError(err_text)
            enum = set(enum)
            if not enum: raise TypeError(err_text)
        
        def find_substitution(v):
            for s in substitutions:
                if v not in s: continue
                for vs in s:
                    if vs in enums: return vs
        
        for v in tuple(enum):
            if v not in enums:
                vs = find_substitution(v)
                if vs is None:
                    raise TypeError(err_text)
                else:
                    enum.discard(v)
                    enum.add(vs)
        
        return (next(iter(enum)) if single_enum else enum)
    
    @staticmethod
    def _func_args_to_bpy_props(func, props_allowed=True):
        # func(a, b, c, d=1, e=2, f=3, *args, g=4, h=5, i=6, **kwargs)
        # * only args with default values can be converted to bpy props
        # * when func is called from wrapper class, the missing
        #   non-optional arguments will be substituted with None
        
        argspec = inspect.getfullargspec(func)
        args = argspec.args
        varargs = argspec.varargs
        varkw = argspec.varkw
        defaults = argspec.defaults
        kwonlyargs = argspec.kwonlyargs
        kwonlydefaults = argspec.kwonlydefaults
        annotations = argspec.annotations
        
        bpy_props = []
        
        n_optional = (0 if defaults is None else len(defaults))
        n_positional = len(args) - n_optional
        n_kwonly = (0 if kwonlyargs is None else len(kwonlyargs))
        use_varargs = bool(varargs) and (n_optional == 0)
        
        if props_allowed:
            empty_dict = {}
            
            def process_arg(name, value):
                annotation = annotations.get(name, empty_dict)
                
                try:
                    bpy_prop = value | prop(**annotation)
                except:
                    return value
                
                bpy_props.append((name, bpy_prop))
                
                if bpy_prop[0] == bpy.props.PointerProperty:
                    return None
                elif bpy_prop[0] == bpy.props.CollectionProperty:
                    return [] # maybe use a collection emulator?
                elif BpyProp.validate(value):
                    return bpy_prop[1].get("default", BpyProp.known[bpy_prop[0]])
                else:
                    return value
            
            if n_optional != 0:
                defaults = list(defaults)
                for i in range(n_optional):
                    name, value = args[n_positional + i], defaults[i]
                    defaults[i] = process_arg(name, value)
                func.__defaults__ = tuple(defaults)
            
            if n_kwonly != 0:
                for name in kwonlyargs:
                    value = kwonlydefaults[name]
                    kwonlydefaults[name] = process_arg(name, value)
                func.__kwdefaults__ = kwonlydefaults
        
        return n_positional, use_varargs, bpy_props
    
    @staticmethod
    def _make_func_call(n_positional, use_varargs, positional, optional):
        n_supplied = len(positional)
        if use_varargs:
            n_positional = max(n_positional, n_supplied)
        params = [(positional[i] if i < n_supplied else "None") for i in range(n_positional)]
        params.extend(optional)
        return params

    # func->class coversion is useful for cases when the class
    # is basically a wrapper of a function which is used in
    # other places as an actual function. Or for more concise code.
    def _func_to_bpy_class(self, base, func, props_allowed, wrapinfos):
        if not inspect.isfunction(func):
            raise TypeError("Cannot convert a %s to operator" % type(func))
        
        is_generator = inspect.isgeneratorfunction(func)
        is_function = not is_generator
        
        n_positional, use_varargs, bpy_props = self._func_args_to_bpy_props(func, props_allowed)
        
        cls = type(func.__name__, (base,), {})
        cls.__doc__ = func.__doc__
        
        optional = []
        for name, bpy_prop in bpy_props:
            optional.append("{0}=self.{0}".format(name))
            setattr(cls, name, bpy_prop)
        
        for wrapinfo in wrapinfos:
            wrapper_name = wrapinfo["name"]
            wrapper_args = wrapinfo.get("args", ())
            resmap = wrapinfo.get("resmap") # map src result tp dst result
            decorator = wrapinfo.get("decorator") # e.g. staticmethod
            func_init = wrapinfo.get("func_init", True)
            gen_init = wrapinfo.get("gen_init", True)
            extra_code = wrapinfo.get("extra_code", "")
            stopped_code = wrapinfo.get("stopped_code", "")
            
            if stopped_code: stopped_code = "if not _yeilded[1]: %s" % stopped_code
            
            extra_code = indent(extra_code, " "*4)
            stopped_code = indent(stopped_code, " "*4)
            
            if (not func_init) and is_function: continue
            
            localvars = dict(resmap=resmap, func=func,
                next_catch=next_catch, send_catch=send_catch)
            
            func_call = self._make_func_call(n_positional, use_varargs, wrapper_args, optional)
            func_call = "func({0})".format(", ".join(func_call))
            
            if resmap is not None:
                if is_generator:
                    if gen_init:
                        code = unindent("""
                        def {0}({1}):
                            self._generator = {2}
                            _yeilded = next_catch(self._generator)
                        {4}
                            _result = resmap(_yeilded[0])
                        {3}
                            return _result
                        """)
                    else:
                        code = unindent("""
                        def {0}({1}):
                            _yeilded = send_catch(self._generator, ({1}))
                        {4}
                            _result = resmap(_yeilded[0])
                        {3}
                            return _result
                        """)
                else:
                    code = unindent("""
                    def {0}({1}):
                        _result = resmap({2})
                    {3}
                        return _result
                    """)
            else:
                if is_generator:
                    if gen_init:
                        code = unindent("""
                        def {0}({1}):
                            self._generator = {2}
                            _yeilded = next_catch(self._generator)
                        {4}
                        """)
                    else:
                        code = unindent("""
                        def {0}({1}):
                            _yeilded = send_catch(self._generator, ({1}))
                        {4}
                        """)
                else:
                    code = unindent("""
                    def {0}({1}):
                        {2}
                    """)
            
            code = code.format(wrapper_name, ", ".join(wrapper_args), func_call, extra_code, stopped_code)
            #code = "\n".join([l for l in code.splitlines() if l.strip()])
            #print(code)
            exec(code, localvars, localvars)
            
            wrapper = localvars[wrapper_name]
            if decorator: wrapper = decorator(wrapper)
            
            setattr(cls, wrapper_name, wrapper)
        
        return cls
    
    # Do some autocompletion on class info
    def _autocomplete(self, cls, base, modes):
        is_panel = (base is bpy.types.Panel)
        is_header = (base is bpy.types.Header)
        is_operator = (base is bpy.types.Operator)
        single_enums = is_panel or is_header
        has_poll = base in {bpy.types.Operator, bpy.types.Panel, bpy.types.Menu}
        has_description = base in {bpy.types.Operator, bpy.types.Macro, bpy.types.Menu,
            bpy.types.Node, bpy.types.NodeTree, bpy.types.KeyingSet, bpy.types.KeyingSetInfo}
        
        regions = None
        spaces = None
        
        if (not hasattr(cls, "bl_idname")) and is_operator:
            cls.bl_idname = ".".join(p.lower() for p in cls.__name__.split("_OT_"))
        
        if not hasattr(cls, "bl_label"): cls.bl_label = bpy.path.clean_name(cls.__name__)
        
        if hasattr(cls, "bl_label"): cls.bl_label = compress_whitespace(cls.bl_label)
        
        if hasattr(cls, "bl_description"):
            cls.bl_description = compress_whitespace(cls.bl_description)
        elif has_description and hasattr(cls, "__doc__"): # __doc__ can be None
            cls.bl_description = compress_whitespace(cls.__doc__ or "")
        
        # Make sure enum-attributes have correct values
        if hasattr(cls, "bl_options"):
            substitutions=[('GRAB_POINTER', 'GRAB_CURSOR')] # in 2.75, one of Operator's bl_options was renamed
            cls.bl_options = self._normalize("bl_options", cls.bl_options, BlEnums.options.get(base.__name__, ()), substitutions=substitutions)
            if isinstance(cls.bl_options, str): cls.bl_options = {cls.bl_options}
        
        if hasattr(cls, "bl_region_type") and has_poll:
            cls.bl_region_type = self._normalize("bl_region_type", cls.bl_region_type, BlEnums.region_types, single_enums)
            regions = cls.bl_region_type
        
        if hasattr(cls, "bl_space_type") and (has_poll or is_header):
            cls.bl_space_type = self._normalize("bl_space_type", cls.bl_space_type, BlEnums.space_types, single_enums)
            spaces = cls.bl_space_type
        
        if hasattr(cls, "bl_context") and is_panel:
            cls.bl_context = self._normalize("bl_context", cls.bl_context, BlEnums.panel_contexts.get(spaces, ()), True)
            if (not modes) and (spaces == 'VIEW_3D'): modes = BlEnums.panel_contexts['VIEW_3D'][cls.bl_context]
        
        # Auto-generate poll() method from context restrictions
        generate_poll = False
        if has_poll:
            generate_poll = bool(modes)
            # For panel, region/space checks are redundant
            if (not generate_poll) and (not is_panel):
                generate_poll = bool(regions or spaces)
        
        if generate_poll:
            poll = getattr(cls, "poll", None)
            cls.poll = self._poll_factory(modes, regions, spaces, poll)
    
    def _add_idnamable(self, cls, base, kwargs, wrapinfos=None):
        if (not isinstance(cls, type)) and wrapinfos:
            if "resmap" in kwargs:
                resmap = kwargs["resmap"]
                wrapinfos = [dict(w) for w in wrapinfos]
                for w in wrapinfos:
                    w["resmap"] = resmap
                kwargs.pop("resmap", None)
            
            props_allowed = base not in (bpy.types.Panel, bpy.types.Menu, bpy.types.Header) # ?
            
            func = cls # Expected to be a function or method
            cls = self._func_to_bpy_class(base, func, props_allowed, wrapinfos)
        else:
            func = None
            cls = ensure_baseclass(cls, base) # Make class an Operator/Menu/Panel, if it's not
        
        modes = None
        
        if kwargs:
            # Add attributes mentioned in the decorator
            for key, value in kwargs.items():
                name = "bl_" + key
                if key == "mode":
                    modes = self._normalize("mode", value, BlEnums.modes)
                elif name in BlEnums.common_attrs:
                    if not hasattr(cls, name): setattr(cls, name, value)
                elif key in BlEnums.common_attrs:
                    if not hasattr(cls, key): setattr(cls, key, value)
                else:
                    raise TypeError("Unexpected attribute '%s'" % key)
        
        self._autocomplete(cls, base, modes)
        
        self._add_class(cls)
        
        # the original function may still be useful
        if func: return func
        
        return cls
    
    def _decorator(self, cls, base, kwargs, wrapinfos=None):
        if cls: return self._add_idnamable(cls, base, kwargs, wrapinfos)
        return (lambda cls: self._add_idnamable(cls, base, kwargs, wrapinfos))
    
    def _Operator_resmap(value):
        if isinstance(value, set): return value
        return ({'FINISHED'} if value else {'CANCELLED'})
    _Operator_wrapinfos = [
        dict(name="execute", args=("self", "context"), func_init=True, gen_init=True,
        resmap=_Operator_resmap, stopped_code="return {'CANCELLED'}"),
        dict(name="invoke", args=("self", "context", "event"), func_init=True, gen_init=True,
        resmap=_Operator_resmap, stopped_code="return {'CANCELLED'}",
        extra_code="if 'RUNNING_MODAL' in _result: context.window_manager.modal_handler_add(self)"),
        dict(name="modal", args=("self", "context", "event"), func_init=False, gen_init=False,
        resmap=_Operator_resmap, stopped_code="return {'CANCELLED'}"),
    ]
    def Operator(self, cls=None, **kwargs):
        return self._decorator(cls, bpy.types.Operator, kwargs, self._Operator_wrapinfos)
    
    def PopupOperator(self, width=300, height=20, **kwargs):
        def decorator(func):
            cls = type(func.__name__, (), dict(
                __doc__ = func.__doc__,
                draw = func,
                execute = (lambda self, context: {'FINISHED'}),
                invoke = (lambda self, context, event:
                    context.window_manager.invoke_popup(self, width, height)),
            ))
            return self._add_idnamable(cls, bpy.types.Operator, kwargs)
        return decorator
    
    _Panel_wrapinfos = [
        dict(name="draw_header", args=("self", "context"), func_init=False, gen_init=True),
        dict(name="draw", args=("self", "context"), func_init=True, gen_init=False),
    ]
    def Panel(self, cls=None, **kwargs):
        return self._decorator(cls, bpy.types.Panel, kwargs, self._Panel_wrapinfos)
    
    _Menu_wrapinfos = [
        dict(name="draw", args=("self", "context"), func_init=True, gen_init=True),
    ]
    def Menu(self, cls=None, **kwargs):
        return self._decorator(cls, bpy.types.Menu, kwargs, self._Menu_wrapinfos)
    
    _Header_wrapinfos = [
        dict(name="draw", args=("self", "context"), func_init=True, gen_init=True),
    ]
    def Header(self, cls=None, **kwargs):
        return self._decorator(cls, bpy.types.Header, kwargs, self._Header_wrapinfos)
    
    _UIList_wrapinfos = [
        dict(name="draw", args=("self", "context", "layout", "data", "item", "icon", "active_data", "active_propname"), func_init=True, gen_init=True),
    ]
    def UIList(self, cls=None, **kwargs):
        return self._decorator(cls, bpy.types.UIList, kwargs, self._UIList_wrapinfos)
    
    def RenderEngine(self, cls=None, **kwargs):
        return self._decorator(cls, bpy.types.RenderEngine, kwargs)
    
    def Node(self, cls=None, **kwargs):
        return self._decorator(cls, bpy.types.Node, kwargs)
    
    def NodeSocket(self, cls=None, **kwargs):
        return self._decorator(cls, bpy.types.NodeSocket, kwargs)
    
    def NodeTree(self, cls=None, **kwargs):
        return self._decorator(cls, bpy.types.NodeTree, kwargs)
    
    def KeyingSet(self, cls=None, **kwargs):
        return self._decorator(cls, bpy.types.KeyingSet, kwargs)
    
    def KeyingSetInfo(self, cls=None, **kwargs):
        return self._decorator(cls, bpy.types.KeyingSetInfo, kwargs)
    #========================================================================#
    
    # ===== PROPERTY GROUP DECORATORS ===== #
    def _gen_pg(self, cls, mixins=None):
        cls = ensure_baseclass(cls, bpy.types.PropertyGroup)
        addons_registry.UUID_add(cls)
        self._add_class(cls, mixins=mixins)
        return cls
    
    def PropertyGroup(self, cls=None, **kwargs):
        if cls: return self._gen_pg(cls, **kwargs)
        return (lambda cls: self._gen_pg(cls, **kwargs))
    
    def _gen_idblock(self, cls, name=None, icon='DOT', sorted=False, show_empty=True, mixins=None):
        name = name or bpy.path.display_name(cls.__name__)
        
        # ===== Item ===== #
        cls = ensure_baseclass(cls, bpy.types.PropertyGroup)
        addons_registry.UUID_add(cls)
        
        addon = self # used here:
        def update_name(self, context):
            selfx = addon[self]
            if hasattr(selfx, "_idblocks"): selfx._idblocks._on_rename(self)
        cls.name = "" | prop(update=update_name)
        
        self._add_class(cls, mixins=mixins)
        # ================ #
        
        # ===== Collection ===== #
        class _IDBlocks(IDBlocks, bpy.types.PropertyGroup):
            _addon = self
            _IDBlock_type = cls
            _typename = name
            _sorted = sorted
            _icon = icon
            collection = [cls] | prop() # make it HIDDEN ?
        addons_registry.UUID_add(_IDBlocks)
        
        cls._IDBlocks = _IDBlocks
        self._add_class(_IDBlocks)
        # ====================== #
        
        # ===== Renamer/selector ===== #
        class _IDBlockSelector(IDBlockSelector, bpy.types.PropertyGroup):
            _addon = self
            _IDBlock_type = cls
        _IDBlockSelector.show_empty = show_empty
        addons_registry.UUID_add(_IDBlockSelector)
        
        def redescribe(attr_name, value):
            bp_type, bp_dict = getattr(_IDBlockSelector, attr_name)
            bp_dict = dict(bp_dict, description=(value % name))
            setattr(_IDBlockSelector, attr_name, (bp_type, bp_dict))
        redescribe("selector", "Choose %s")
        redescribe("renamer", "Active %s ID name")
        
        cls._IDBlockSelector = _IDBlockSelector
        self._add_class(_IDBlockSelector)
        # ============================ #
        
        return cls
    
    # ID blocks are stored in collections which ensure unique name for each item
    def IDBlock(self, cls=None, **kwargs):
        if cls: return self._gen_idblock(cls, **kwargs)
        return (lambda cls: self._gen_idblock(cls, **kwargs))
    #========================================================================#

#============================================================================#

# ===== ID BLOCK(S) ===== #
class IDBlocks:
    def __init__(self):
        selfx = self._addon[self]
        selfx._listeners = set()
        selfx.lock = PrimitiveLock()
    
    def dispose(self):
        selfx = self._addon[self]
        for listener in list(selfx._listeners):
            listener.unbind()
    
    def _add_listener(self, listener):
        selfx = self._addon[self]
        selfx._listeners.add(listener)
    
    def _remove_listener(self, listener):
        selfx = self._addon[self]
        selfx._listeners.discard(listener)
    #========================================================================#
    
    # ===== EVENT SOURCES ===== #
    def _on_rename(self, obj):
        selfx = self._addon[self]
        
        for listener in selfx._listeners:
            listener._on_rename(obj)
        
        if selfx.lock: return
        
        i_obj = -1
        i_ins = -1
        
        name = obj.name
        
        name_collision = False
        
        i = 0
        for obj2 in self.collection:
            if obj2 == obj:
                i_obj = i
            elif obj2.name == name:
                name_collision = True
                i_ins = i
            elif obj2.name < name:
                i_ins = i + 1
            i += 1
        
        if self._sorted:
            self._move(i_obj, i_ins)
        
        # Resolve name collision (if there is one)
        if name_collision:
            if i_ins < i_obj:
                i_obj = i_ins + 1
            else:
                i_obj = i_ins - 1
            
            obj = self.collection[i_obj]
            
            with selfx.lock:
                obj.name, i = self._unique_name(name, i_ins + 1)
            
            if (i != -1) and self._sorted:
                #i = self._insertion_search(obj.name, i_ins + 1)
                self._move(i_obj, i)
    
    def _on_reorder(self, sorted=False):
        selfx = self._addon[self]
        
        for listener in selfx._listeners:
            if sorted:
                i = self._search(self, listener.selector)
            else:
                i = self.find(listener.selector)
            listener._on_reorder(i)
    
    def _delitem(self, i, notify_listeners=True):
        selfx = self._addon[self]
        
        obj = self.collection[i]
        
        if hasattr(obj, "dispose"): obj.dispose()
        
        self.collection.remove(i)
        
        if notify_listeners:
            for listener in selfx._listeners:
                listener._on_delete(i)
    
    def _clear(self):
        selfx = self._addon[self]
        
        while self.collection:
            self._delitem(0, False)
        
        for listener in selfx._listeners:
            listener._on_clear()
    
    def _swap(self, i0, i1):
        if i0 == i1: return
        
        selfx = self._addon[self]
        
        i0, i1 = min(i0, i1), max(i0, i1)
        # we can't just do a[i0], a[i1] = a[i1], a[i0],
        # since intermediate results are not independent
        self.collection.move(i1, i0)
        self.collection.move(i0 + 1, i1)
        
        for listener in selfx._listeners:
            listener._on_swap(i0, i1)
    
    def _move(self, i0, i1):
        if i0 == i1: return
        
        selfx = self._addon[self]
        
        self.collection.move(i0, i1)
        
        for listener in selfx._listeners:
            listener._on_move(i0, i1)
    #========================================================================#
    
    def _search(self, key, low=0, high=None):
        collection = self.collection
        if high is None: high = len(collection) - 1
        
        while low <= high:
            middle = (high + low) // 2
            item_key = collection[middle].name
            if item_key > key:
                high = middle - 1
            elif item_key < key:
                low = middle + 1
            else:
                return middle
        
        return -1
    
    def _insertion_search(self, key, low=0, high=None):
        collection = self.collection
        if high is None:
            high = len(collection) - 1
        
        if high < 0:
            return 0
        
        while low < high:
            middle = (high + low) // 2
            item_key = collection[middle].name
            if item_key > key:
                high = middle - 1
            elif item_key < key:
                low = middle + 1
            else:
                return middle
        
        # check if it goes before or after current item
        item_key = collection[low].name
        return ((low + 1) if (item_key < key) else low)
    
    def _unique_name(self, src_name, lo=0, hi=None):
        name = src_name
        
        if self._sorted:
            id = 1
            while self._search(name) != -1:
                name = "{}.{:0>3}".format(src_name, id)
                id += 1
            i = self._insertion_search(name, lo, hi)
        else:
            existing_names = {obj.name for obj in self.collection}
            id = 1
            while name in existing_names:
                name = "{}.{:0>3}".format(src_name, id)
                id += 1
            i = -1
        
        return (name, i)
    
    def _resolve_index(self, i, err=True):
        if isinstance(i, int):
            n = len(self.collection)
            
            if i < 0: i += n
            
            if (i < 0) or (i >= n):
                if not err: return -1
                raise IndexError("index %s is out of range [%s, %s]" % (i, 0, n - 1))
        else:
            k = i
            i = self.find(i)
            if i == -1:
                if not err: return -1
                raise KeyError("item '%s' not in collection" % k)
        
        return i
    
    def _ensure_link(self, obj):
        # Make sure necessary attributes are initialized
        # (e.g. if item was created in previous session)
        objx = self._addon[obj]
        objx._idblocks = self
        return obj
    
    # These are methods of Blender datablock collections:
    def __getitem__(self, key_or_index):
        if isinstance(key_or_index, slice):
            indices = key_or_index.indices(len(self.collection))
            res = []
            for key_or_index in range(*indices):
                obj = self.collection[self._resolve_index(key_or_index)]
                res.append(self._ensure_link(obj))
        else:
            obj = self.collection[self._resolve_index(key_or_index)]
            return self._ensure_link(obj)
    
    def __setitem__(self, key_or_index, value):
        raise NotImplementedError
    
    def __delitem__(self, key_or_index):
        if isinstance(key_or_index, slice):
            indices = key_or_index.indices(len(self.collection))
            if indices[2] > 0:
                indices = (indices[1] - 1, indices[0] - 1, -indices[2])
            for key_or_index in range(*indices):
                self._delitem(self._resolve_index(key_or_index))
        else:
            self._delitem(self._resolve_index(key_or_index))
    
    def __iter__(self):
        return self.values()
    
    def __contains__(self, key_or_obj):
        return (self.find(key_or_obj) != -1)
    
    def __len__(self):
        return len(self.collection)
    
    def __bool__(self):
        return bool(self.collection)
    
    def new(self, name="", **kwargs):
        selfx = self._addon[self]
        
        if not name: name = self._typename
        
        name, i = self._unique_name(name)
        
        obj = self.collection.add()
        with selfx.lock:
            obj.name = name
        
        for k, v in kwargs.items():
            setattr(obj, k, v)
        
        if i != -1:
            self._move(len(self.collection) - 1, i)
            # After order of items is changed,
            # the old reference is invalid!
            obj = self.collection[i]
        
        return self._ensure_link(obj)
    
    def remove(self, obj):
        i = self.find(obj)
        if i == -1: raise ValueError("item not in collection")
        del self[i]
    
    def find(self, key_or_obj):
        "Returns the index of the key in the collection, or -1 when not found"
        if isinstance(key_or_obj, str):
            if self._sorted: return self._search(key_or_obj)
            for i, obj in enumerate(self.collection):
                if obj.name == key_or_obj: return i
            return -1
        else:
            ID = addons_registry.UUID_get(key_or_obj)
            for i, obj in enumerate(self.collection):
                if addons_registry.UUID_get(obj) == ID: return i
            return -1
    
    def foreach_get(self, attr, seq):
        collection = self.collection
        n = len(seq)
        if n != len(collection):
            raise ValueError("seq has different length than the collection")
        
        for i in range(n):
            seq[i] = getattr(collection[i], attr)
    
    def foreach_set(self, attr, seq):
        collection = self.collection
        n = len(seq)
        if n != len(collection):
            raise ValueError("seq has different length than the collection")
        
        if attr == "name":
            selfx = self._addon[self]
            with selfx.lock:
                names = set()
                for i in range(n):
                    obj = collection[i]
                    obj.name = unique_name(seq[i], names)
                    names.add(obj.name)
                if self._sorted:
                    self.sort()
        else:
            for i in range(n):
                setattr(collection[i], attr, seq[i])
    
    def get(self, key, default=None):
        "Returns the value of the item assigned to key, or default (when key is not found)"
        i = self.find(key)
        if i == -1: return default
        return self._ensure_link(self.collection[i])
    
    def items(self):
        for obj in self.collection:
            yield (obj.name, self._ensure_link(obj))
    
    def keys(self):
        for obj in self.collection:
            yield obj.name
    
    def values(self):
        for obj in self.collection:
            yield self._ensure_link(obj)
    
    # These methods aren't present in Blender datablock collections:
    def sort(self):
        collection = self.collection
        n = len(collection)
        
        # gnome sort
        pos = 1
        last = 0
        while pos < n:
            if collection[pos].name >= collection[pos - 1].name:
                if last != 0:
                    pos = last
                    last = 0
                pos += 1
            else:
                collection.move(pos, pos - 1)
                if pos > 1:
                    if last == 0:
                        last = pos
                    pos -= 1
                else:
                    pos += 1
        
        self._on_reorder(True)
    
    # For compatibility with CollectionProperty
    add = new
    
    def discard(self, key_or_index):
        i = self._resolve_index(key_or_index, False)
        if i != -1: del self[i]
    
    def clear(self):
        self._clear()
    
    def move(self, key_or_index0, key_or_index1):
        if self._sorted: return
        i0 = self._resolve_index(key_or_index0)
        i1 = self._resolve_index(key_or_index1)
        self._move(i0, i1)
    
    def swap(self, key_or_index0, key_or_index1):
        if self._sorted: return
        i0 = self._resolve_index(key_or_index0)
        i1 = self._resolve_index(key_or_index1)
        self._swap(i0, i1)

class IDBlockSelector:
    def _selector_update(self, context):
        selfx = self._addon[self] # "self extended"
        if not selfx.idblocks: return
        if selfx.lock: return
        
        self._set_index(selfx, selfx.idblocks.find(self.selector))
    
    def _renamer_update(self, context):
        selfx = self._addon[self] # "self extended"
        if not selfx.idblocks: return
        if selfx.lock: return
        
        obj = selfx.idblocks[selfx.index]
        
        if obj.name != self.renamer:
            obj.name = self.renamer
    
    use_search_field = False
    
    if use_search_field:
        selector = "" | prop(update=_selector_update)
    else:
        #empty_name = '\x7f' # "Delete" character
        empty_name = '\x1a' # "Substitute" character
        def enum_items(self, context):
            selfx = self._addon[self] # "self extended"
            idblocks = selfx.idblocks
            # references to items' strings must be kept in python!
            selfx._item_names = []
            if idblocks is not None: selfx._item_names.extend(sys.intern(obj.name) for obj in idblocks.collection)
            items = []
            if self.show_empty or (not selfx._item_names): items.append((self.empty_name, "", ""))
            if idblocks is not None: items.extend((name, name, name) for name in selfx._item_names)
            return items
        selector = empty_name | prop(update=_selector_update, items=enum_items)
    
    renamer = "" | prop(update=_renamer_update)
    
    def __init__(self):
        selfx = self._addon[self] # "self extended"
        selfx.idblocks = None
        selfx.update = None
        selfx.new = ""
        selfx.open = ""
        selfx.delete = ""
        selfx.lock = PrimitiveLock()
        selfx.index = -1
        selfx.reselect = False
        selfx.rename = True
    
    def unbind(self):
        selfx = self._addon[self] # "self extended"
        
        if selfx.idblocks:
            selfx.idblocks._remove_listener(self)
            selfx.idblocks = None
            
            self._set_index(selfx, -1)
        
        selfx.new = ""
        selfx.open = ""
        selfx.delete = ""
    
    def dispose(self):
        self.unbind()
    
    def _set_index(self, selfx, i):
        # Necessary to avoid infinite loop/recursion
        if selfx.lock: return
        
        selfx.index = i
        name = ("" if i == -1 else selfx.idblocks[i].name)
        with selfx.lock:
            if self.use_search_field:
                self.selector = name
            else:
                if name or self.empty_name:
                    select_any = False
                    try:
                        self.selector = (name if name else self.empty_name)
                    except:
                        select_any = (not name) and (not self.show_empty)
                    if select_any:
                        idblocks = selfx.idblocks
                        if idblocks and idblocks.collection:
                            self.selector = idblocks.collection[len(idblocks.collection)-1].name
            self.renamer = name
    
    def set_update(self, update):
        selfx = self._addon[self] # "self extended"
        
        selfx.update = update
    
    is_bound = property(lambda self: (self._addon[self].idblocks is not None))
    
    def bind(self, idblocks, new="", open="", delete="", reselect=False, rename=True):
        selfx = self._addon[self] # "self extended"
        
        if selfx.idblocks: selfx.idblocks._remove_listener(self)
        
        if isinstance(idblocks, IDBlocks):
            bp_type, bp_dict = type(idblocks).collection
            if bp_dict["type"] is self._IDBlock_type:
                selfx.idblocks = idblocks
            else:
                raise TypeError("idblocks item type must be %s" % self._IDBlock_type.__name__)
        else:
            raise TypeError("idblocks must be an IDBlocks instance")
        
        idblocks._add_listener(self)
        
        selfx.new = new
        selfx.open = open
        selfx.delete = delete
        
        selfx.reselect = reselect
        selfx.rename = rename
        
        self._set_index(selfx, selfx.idblocks.find(self.selector))
    
    def new(self, name=""):
        selfx = self._addon[self] # "self extended"
        
        obj = selfx.idblocks.new(name)
        if selfx.idblocks._sorted:
            i = selfx.idblocks.find(obj.name)
        else:
            i = len(selfx.idblocks) - 1
        
        self._set_index(selfx, i)
        
        return obj
    
    def delete(self):
        selfx = self._addon[self] # "self extended"
        
        if selfx.index == -1: return
        
        try:
            del selfx.idblocks[selfx.index]
            #del selfx.idblocks[self.selector]
        except IndexError: #KeyError:
            pass
    
    @property
    def object(self):
        selfx = self._addon[self] # "self extended"
        
        if not selfx.idblocks: return None
        
        return selfx.idblocks[selfx.index]
    
    def _on_rename(self, obj):
        selfx = self._addon[self] # "self extended"
        
        if obj == selfx.idblocks[selfx.index]:
            self._set_index(selfx, selfx.index)
    
    def _on_reorder(self, i):
        selfx = self._addon[self] # "self extended"
        
        self._set_index(selfx, i)
    
    def _on_delete(self, i):
        selfx = self._addon[self] # "self extended"
        
        if i < selfx.index:
            self._set_index(selfx, selfx.index - 1)
        elif i != selfx.index:
            return
        
        if selfx.reselect and selfx.idblocks:
            self._set_index(selfx, max(i - 1, 0))
        else:
            self._set_index(selfx, -1)
    
    def _on_clear(self):
        selfx = self._addon[self] # "self extended"
        
        self._set_index(selfx, -1)
    
    def _on_swap(self, i0, i1):
        selfx = self._addon[self] # "self extended"
        
        if selfx.index == i0:
            self._set_index(selfx, i1)
        elif selfx.index == i1:
            self._set_index(selfx, i0)
    
    def _on_move(self, i0, i1):
        selfx = self._addon[self] # "self extended"
        
        i = selfx.index
        
        if i == i0:
            self._set_index(selfx, i1)
        elif (i0 < i1) and (i > i0) and (i <= i1):
            self._set_index(selfx, i - 1)
        elif (i0 > i1) and (i < i0) and (i >= i1):
            self._set_index(selfx, i + 1)
    
    def draw(self, layout):
        selfx = self._addon[self] # "self extended"
        
        idblocks = selfx.idblocks
        if idblocks is None:
            with layout.row()(alert=True):
                layout.label("Selector not bound!")
            return
        
        new = selfx.new
        open = selfx.open
        delete = selfx.delete
        index = selfx.index
        
        rename = selfx.rename
        
        name = idblocks._typename
        icon = idblocks._icon or 'DOT'
        
        # ===== LAYOUT ===== #
        layout = NestedLayout(layout)
        
        with layout.row(True):
            # ===== SELECTOR ===== #
            if rename and ((index != -1) or (new or open)):
                # magical values:
                # alignment == 'EXPAND': scale_x = 0.12..0.13 (0.125)
                # alignment != 'EXPAND': scale_x = 0.23..0.24 (0.235)
                # ...at 0.125 some small letters like "i" can still be seen
                if self.use_search_field:
                    scale_x = 0.12
                    with layout.row(True)(scale_x=scale_x):
                        layout.prop_search(self, "selector", idblocks, "collection", text="", icon=icon)
                else:
                    scale_x = 0.16
                    with layout.row(True)(scale_x=scale_x):
                        layout.prop(self, "selector", text="", icon=icon)
                        #layout.prop_menu_enum(self, "selector", text="", icon=icon)
            else:
                if self.use_search_field:
                    layout.prop_search(self, "selector", idblocks, "collection", text="", icon=icon)
                else:
                    layout.prop(self, "selector", text="", icon=icon)
                    #layout.prop_menu_enum(self, "selector", text="", icon=icon)
            
            # layout.prop_search since some version displays "Clear search field" button, which looks bad
            # layout.prop_menu_enum seems buggy in this particular use case
            # layout.prop does not seem have as severe drawbacks as other layout commands
            
            if index == -1:
                if new: layout.operator(new, text="New", icon='ZOOMIN')
                
                if open: layout.operator(open, text="Open", icon='FILESEL')
            else:
                # ===== RENAMER ===== #
                if rename: layout.prop(self, "renamer", text="")
                
                # ===== New, Open, Delete (unlink) ===== #
                if new: layout.operator(new, text="", icon='ZOOMIN')
                
                if open: layout.operator(open, text="", icon='FILESEL')
                
                if delete: layout.operator(delete, text="", icon='X')

#============================================================================#

# ===== UI MONITOR ===== #
UIMonitor_typename = "BACKGROUND_OT_ui_monitor_%s" % version
UIMonitor = getattr(bpy.types, UIMonitor_typename, None)
if not UIMonitor:
    class BACKGROUND_OT_ui_monitor(bpy.types.Operator):
        bl_idname = "background.ui_monitor"
        bl_label = "Background UI Monitor"
        bl_options = {'INTERNAL'}
        
        _is_running = False
        _undo_hash = None
        _script_reload_kmis = []
        _op_overrides = {}
        
        @classmethod
        def block_operator(cls, op_idname, callback=None):
            for kc, km, kmi in KeyMapUtils.search(op_idname):
                kmi_type = KeyMapUtils.normalize_event_type(kmi.type)
                key = (kmi_type, kmi.value, kmi.alt, kmi.ctrl, kmi.shift, kmi.oskey)
                op_override = cls._op_overrides.get(key)
                if op_override is None:
                    op_override = {}
                    cls._op_overrides[key] = op_override
                op_override[op_idname] = (BlRna.serialize(kmi.properties), km.space_type, km.region_type, callback)
        
        @classmethod
        def unblock_operator(cls, op_idname):
            for key, op_override in tuple(cls._op_overrides.items()):
                op_override.pop(op_idname, None)
                if not op_override: cls._op_overrides.pop(key, None)
        
        event_count = 0
        user_interaction = False
        
        mouse = (0, 0)
        mouse_prev = (0, 0)
        mouse_region = (0, 0)
        mouse_context = None # can be None between areas, for example
        last_mouse_context = None
        last_rv3d_context = None
        
        alt = False
        ctrl = False
        shift = False
        oskey = False
        
        on_next_update = []
        
        @classmethod
        def state_invalidated(cls):
            undo_hash = bpy.data.as_pointer()
            if cls._undo_hash != undo_hash:
                old_undo_hash = cls._undo_hash
                cls._undo_hash = undo_hash
                if old_undo_hash is not None:
                    cls.mouse_context = None
                    cls.last_mouse_context = None
                    cls.last_rv3d_context = None
                    return True
            return False
        
        @classmethod
        def _assign_last_context(cls, name, curr_context):
            if curr_context:
                setattr(cls, name, curr_context)
            else:
                last_context = getattr(cls, name)
                if last_context:
                    area = last_context.get("area")
                    if (not area) or (not area.regions):
                        setattr(cls, name, None)
        
        @classmethod
        def activate(cls):
            if cls._is_running: return
            
            if cls.state_invalidated(): return
            
            if addons_registry.ui_monitor or cls.user_interaction:
                cls._is_running = True
                bpy.ops.background.ui_monitor('INVOKE_DEFAULT')
        
        def invoke(self, context, event):
            cls = self.__class__
            cls._is_running = True
            cls._script_reload_kmis = list(KeyMapUtils.search('script.reload'))
            
            cls.event_count += 1
            
            wm = context.window_manager
            wm.modal_handler_add(self)
            
            # 'RUNNING_MODAL' MUST be present if modal_handler_add is used!
            return {'PASS_THROUGH', 'RUNNING_MODAL'}
        
        def cancel(self, context):
            cls = self.__class__
            cls._is_running = False
        
        def modal(self, context, event):
            cls = self.__class__
            
            cls.event_count += 1
            cls.user_interaction = False
            
            # Scripts cannot be reloaded while modal operators are running
            # Intercept the corresponding event and shut down the monitor
            # (it would be relaunched automatically afterwards)
            reload_key = any(KeyMapUtils.equal(kmi, event) for kc, km, kmi in cls._script_reload_kmis)
            shut_down = ((not cls._is_running) or (not addons_registry.ui_monitor) or reload_key)
            shut_down |= cls.state_invalidated()
            
            if shut_down:
                self.cancel(context)
                return {'PASS_THROUGH', 'CANCELLED'}
            
            cls.update(context, event)
            
            key = (event.type, event.value, event.alt, event.ctrl, event.shift, event.oskey)
            op_override = cls._op_overrides.get(key)
            if op_override:
                context_override = attrs_to_dict(context)
                context_override.update(cls.mouse_context)
                
                for op_idname, op_data in op_override.items():
                    op = BpyOp(op_idname)
                    
                    if op and op.poll(context_override):
                        op_props, space_type, region_type, callback = op_data
                        if space_type and (space_type != 'NONE'):
                            if context_override["space_data"].type != space_type: continue
                        if region_type and (region_type != 'NONE'): # never 'NONE', actually
                            if context_override["region"].type != region_type: continue
                        
                        allow = False
                        if callback:
                            try:
                                allow = callback((op_idname, op_props), context, event)
                            except Exception as exc:
                                print("Error in block_operator callback {}:".format(callback.__name__))
                                traceback.print_exc()
                        
                        if not allow: return {'RUNNING_MODAL'}
            
            return {'PASS_THROUGH'}
        
        @classmethod
        def update(cls, context, event):
            cls.alt = event.alt
            cls.ctrl = event.ctrl
            cls.shift = event.shift
            cls.oskey = event.oskey
            
            if 'MOUSEMOVE' in event.type: # MOUSEMOVE, INBETWEEN_MOUSEMOVE
                cls.mouse = (event.mouse_x, event.mouse_y)
                cls.mouse_prev = (event.mouse_prev_x, event.mouse_prev_y)
                cls.mouse_region = (event.mouse_region_x, event.mouse_region_y)
                cls.mouse_context = ui_context_under_coord(event.mouse_x, event.mouse_y)
                
                cls._assign_last_context("last_mouse_context", cls.mouse_context)
                if cls.mouse_context and cls.mouse_context.get("region_data"):
                    cls._assign_last_context("last_rv3d_context", cls.mouse_context)
                else:
                    cls._assign_last_context("last_rv3d_context", None)
            
            for callback in cls.on_next_update:
                try:
                    callback(context, event, cls)
                except Exception as exc:
                    print("Error in on_next_update callback {}:".format(callback.__name__))
                    traceback.print_exc()
            cls.on_next_update.clear()
            
            for addon in addons_registry.ui_monitor:
                for callback in addon._ui_monitor:
                    try:
                        callback(context, event, cls)
                    except Exception as exc:
                        print("Error in {} ui_monitor {}:".format(addon.module_name, callback.__name__))
                        traceback.print_exc()
    
    BACKGROUND_OT_ui_monitor.__name__ = UIMonitor_typename
    UIMonitor = BACKGROUND_OT_ui_monitor
    
    bpy.utils.register_class(BACKGROUND_OT_ui_monitor) # REGISTER

# ===== ADDONS REGISTRY ===== #
class AddonsRegistry:
    _scene_update_pre_key = "\x02{generic-addon-scene_update_pre-%s}\x03" % version
    _scene_update_post_key = "\x02{generic-addon-scene_update_post-%s}\x03" % version
    _addons_registry_key = "\x02{addons-registry-%s}\x03" % version
    
    _UUID_container_PG_key = "\x02{UUID-container-PG}\x03"
    _UUID_counter_key = "\x02{UUID-counter}\x03"
    _UUID_container_key = "\x02{UUID-container}\x03"
    #_UUID_key = "\x02{UUID}\x03"
    #_UUID_key = "\x02{UUID: %s}\x03" % "{}; {}".format(time.ctime(), time.clock())
    _UUID_key = "\x02{UUID:%s}\x03" % time.time()
    
    @property
    def UUID_counter(self):
        wm = bpy.context.window_manager
        return getattr(wm, self._UUID_counter_key)
    @UUID_counter.setter
    def UUID_counter(self, value):
        wm = bpy.context.window_manager
        setattr(wm, self._UUID_counter_key, value)
    
    # ATTENTION!
    # It seems that 'SKIP_SAVE' option doesn't work.
    # Even if the property was defined with it, it will still be saved.
    
    # We need the main UUID property to have static name (because
    # it's registered during the addon initialization, and cannot
    # be changed on .blend load), but we also need the actual
    # UUID storage to have a completely unique name in each session
    # (to avoid UUID collisions). This requires us to have a
    # "UUID container" which stores all UUIDs from all sessions
    # (since Blender ignores the 'SKIP_SAVE' flag).
    
    # bpy prop is used instead of item access (obj[...])
    # because we need the UUID to stay hidden from
    # the user and not saved with .blend
    def UUID_add(self, cls):
        #if hasattr(cls, self._UUID_key): return
        #setattr(cls, self._UUID_key, 0 | -prop()) # Important: UUID should be unsaveable
        if hasattr(cls, self._UUID_container_key): return
        setattr(cls, self._UUID_container_key, UUID_container_PG | -prop())
    def UUID_get(self, obj):
        # Note: auto-adding UUID property doesn't always work, e.g. in draw() callbacks
        #return getattr(obj, self._UUID_key, None)
        UUID_container = getattr(obj, self._UUID_container_key, None)
        if UUID_container: return UUID_container.get(self._UUID_key)
    def UUID_set(self, obj, value):
        #setattr(obj, self._UUID_key, value)
        UUID_container = getattr(obj, self._UUID_container_key, None)
        if UUID_container: UUID_container[self._UUID_key] = value
    
    # AddonsRegistry is a singleton anyway, it's ok to use class-level collections
    addons = {}
    after_register = []
    ui_monitor = []
    scene_update_pre = []
    scene_update_post = []
    background_job = []
    selection_job = []
    
    job_duration = 0.002
    job_interval = job_duration * 5
    job_next_update = 0.0
    
    zbuf_users = 0
    module_infos = {}
    module_users = {}
    
    def add(self, addon):
        addon_key = (addon.module_name, addon.path)
        if addon_key in self.addons: return
        self.addons[addon_key] = addon
        self.after_register.extend((callback, addon) for callback in addon._after_register)
        if addon._ui_monitor: self.ui_monitor.append(addon)
        if addon._scene_update_pre: self.scene_update_pre.append(addon)
        if addon._scene_update_post: self.scene_update_post.append(addon)
        if addon._background_job: self.background_job.append(addon)
        if addon._selection_job: self.selection_job.append(addon)
        
        for module_path in self.module_infos:
            if module_path.startswith(addon.path):
                self.module_users[module_path] = self.module_users.get(module_path, 0) + 1
    
    def remove(self, addon):
        addon_key = (addon.module_name, addon.path)
        if addon_key not in self.addons: return
        del self.addons[addon_key]
        if addon._ui_monitor: self.ui_monitor.remove(addon)
        if addon._scene_update_pre: self.scene_update_pre.remove(addon)
        if addon._scene_update_post: self.scene_update_post.remove(addon)
        if addon._background_job: self.background_job.remove(addon)
        if addon._selection_job: self.selection_job.remove(addon)
        
        for module_path in self.module_infos:
            if module_path.startswith(addon.path):
                self.module_users[module_path] = self.module_users.get(module_path, 0) - 1
    
    def analyze_selection(self, duration=None):
        event = None # in case loop is skipped (no selected elements processed)
        for event, item in self._sel_iter(duration):
            for addon in self.selection_job:
                for callback in addon._selection_job:
                    try:
                        callback(event, item)
                    except Exception as exc:
                        print("Error in {} selection_job {}:".format(addon.module_name, callback.__name__))
                        traceback.print_exc()
        return event
    
    def __new__(cls, module_info):
        scene_update_pre = None
        for callback in bpy.app.handlers.scene_update_pre:
            if callback.__name__ == cls._scene_update_pre_key:
                scene_update_pre = callback
                break
        
        scene_update_post = None
        for callback in bpy.app.handlers.scene_update_post:
            if callback.__name__ == cls._scene_update_post_key:
                scene_update_post = callback
                break
        
        scene_update = scene_update_pre or scene_update_post
        self = getattr(scene_update, cls._addons_registry_key, None)
        
        if self is None:
            self = object.__new__(cls)
            
            self._sel_iter = ResumableSelection()
            self.event_lock = PrimitiveLock()
            
            @bpy.app.handlers.persistent
            def load_pre(*args, **kwargs):
                addons_registry.load_pre()
            bpy.app.handlers.load_pre.append(load_pre)
            
            @bpy.app.handlers.persistent
            def load_post(*args, **kwargs):
                addons_registry.load_post()
            bpy.app.handlers.load_post.append(load_post)
        
        self.module_infos[module_info["key"]] = module_info
        
        #cls = self.__class__ # make sure we deal with the currently used class
        
        # When scripts are reloaded, draw handlers are removed! So we must make sure they're added each time.
        if self.post_view_handler: bpy.types.SpaceView3D.draw_handler_remove(self.post_view_handler, 'WINDOW')
        self.post_view_handler = bpy.types.SpaceView3D.draw_handler_add(cls.post_view_callback, (), 'WINDOW', 'POST_VIEW')
        if self.post_pixel_handler: bpy.types.SpaceView3D.draw_handler_remove(self.post_pixel_handler, 'WINDOW')
        self.post_pixel_handler = bpy.types.SpaceView3D.draw_handler_add(cls.post_pixel_callback, (), 'WINDOW', 'POST_PIXEL')
        
        self._button_registrator = ButtonRegistrator()
        
        if scene_update_pre is None:
            @bpy.app.handlers.persistent
            def scene_update_pre(scene):
                if self.event_lock: return # prevent infinite recursion
                with self.event_lock:
                    self.detect_undo(True)
                    
                    self._button_registrator.update()
                    
                    for callback, addon in self.after_register:
                        if addon.status != 'REGISTERED': continue
                        try:
                            callback()
                        except Exception as exc:
                            print("Error in {} after_register {}:".format(addon.module_name, callback.__name__))
                            traceback.print_exc()
                    self.after_register.clear()
                    
                    for addon in self.scene_update_pre:
                        for callback in addon._scene_update_pre:
                            try:
                                callback(scene)
                            except Exception as exc:
                                print("Error in {} scene_update_pre {}:".format(addon.module_name, callback.__name__))
                                traceback.print_exc()
            
            scene_update_pre.__name__ = cls._scene_update_pre_key
            setattr(scene_update_pre, cls._addons_registry_key, self)
            
            bpy.app.handlers.scene_update_pre.append(scene_update_pre)
        
        if scene_update_post is None:
            @bpy.app.handlers.persistent
            def scene_update_post(scene):
                if self.event_lock: return # prevent infinite recursion
                with self.event_lock:
                    self.detect_undo(False)
                    
                    # We need to invoke the monitor from somewhere other than
                    # keymap event, since keymap event can lock the operator
                    # to the Preferences window. Scene update, on the other
                    # hand, is always in the main window.
                    UIMonitor.activate()
                    
                    for addon in self.scene_update_post:
                        for callback in addon._scene_update_post:
                            try:
                                callback(scene)
                            except Exception as exc:
                                print("Error in {} scene_update_post {}:".format(addon.module_name, callback.__name__))
                                traceback.print_exc()
                    
                    curr_time = time.clock()
                    if curr_time > self.job_next_update:
                        job_count = sum(len(addon._background_job) for addon in self.background_job)
                        loop_count = (int(job_count > 0) + int(bool(self.selection_job)))
                        loop_duration = self.job_duration / max(loop_count, 1)
                        
                        if job_count > 0:
                            job_duration = loop_duration / job_count
                            
                            for addon in self.background_job:
                                for callback in addon._background_job:
                                    try:
                                        callback(job_duration)
                                    except Exception as exc:
                                        print("Error in {} background job {}:".format(addon.module_name, callback.__name__))
                                        traceback.print_exc()
                        
                        if self.selection_job: self.analyze_selection(loop_duration)
                        
                        self.job_next_update = time.clock() + self.job_interval
            
            scene_update_post.__name__ = cls._scene_update_post_key
            setattr(scene_update_post, cls._addons_registry_key, self)
            
            bpy.app.handlers.scene_update_post.append(scene_update_post)
        
        return self
    
    undo_detected = False
    _undo_hash = None
    def detect_undo(self, reset):
        if reset: self.undo_detected = False
        undo_hash = bpy.data.as_pointer()
        if self._undo_hash != undo_hash:
            self._undo_hash = undo_hash
            self.undo_detected = True
    
    load_count = 0 # 0 is when Blender has just opened (with the default/startup file)
    
    def load_pre(self):
        if self.event_lock: return # prevent infinite recursion
        with self.event_lock:
            for addon in self.addons.values():
                for callback in addon._load_pre:
                    try:
                        callback()
                    except Exception as exc:
                        print("Error in {} load_pre {}:".format(addon.module_name, callback.__name__))
                        traceback.print_exc()
            
            self.load_count += 1
    
    def load_post(self):
        if self.event_lock: return # prevent infinite recursion
        with self.event_lock:
            if self.load_count > 0:
                #self._UUID_key = "\x02{UUID: %s}\x03" % "{}; {}".format(time.ctime(), time.clock())
                self._UUID_key = "\x02{UUID:%s}\x03" % time.time()
            
            for addon in self.addons.values():
                # clear storages left from the previous session
                addon.attributes.clear()
                addon.attributes_by_pointer.clear()
                addon._refresh_preferences()
                
                for callback in addon._load_post:
                    try:
                        callback()
                    except Exception as exc:
                        print("Error in {} load_post {}:".format(addon.module_name, callback.__name__))
                        traceback.print_exc()
    
    post_view_handler = None
    @staticmethod
    def post_view_callback():
        self = addons_registry
        i = 0
        for module_info in self.module_infos.values():
            # if module path is not present among users, it means a shared library is used
            if self.module_users.get(module_info["key"], 1) == 0: continue
            cgl = module_info["cgl"]
            
            if i == 0:
                Matrix_ModelView = cgl.Matrix_ModelView
                Matrix_Projection = cgl.Matrix_Projection
            cgl.Matrix_ModelView_2D = None
            cgl.Matrix_Projection_2D = None
            cgl.Matrix_ModelView_3D = Matrix_ModelView
            cgl.Matrix_Projection_3D = Matrix_Projection
            
            i += 1
    
    post_pixel_handler = None
    @staticmethod
    def post_pixel_callback():
        self = addons_registry
        i = 0
        for module_info in self.module_infos.values():
            # if module path is not present among users, it means a shared library is used
            if self.module_users.get(module_info["key"], 1) == 0: continue
            cgl = module_info["cgl"]
            ZBufferRecorder = module_info["ZBufferRecorder"]
            
            if i == 0:
                Matrix_ModelView = cgl.Matrix_ModelView
                Matrix_Projection = cgl.Matrix_Projection
            cgl.Matrix_ModelView_2D = Matrix_ModelView
            cgl.Matrix_Projection_2D = Matrix_Projection
            
            if i == 0:
                ZBufferRecorder.draw_pixel_callback(self.zbuf_users)
                ZBufferRecorder0 = ZBufferRecorder
            else:
                ZBufferRecorder.copy(ZBufferRecorder0)
            
            i += 1

UUID_container_PG = getattr(bpy.types, AddonsRegistry._UUID_container_PG_key, None)
if UUID_container_PG is None:
    UUID_container_PG = type(AddonsRegistry._UUID_container_PG_key, (bpy.types.PropertyGroup,), {})
    bpy.utils.register_class(UUID_container_PG)

if not hasattr(bpy.types.WindowManager, AddonsRegistry._UUID_counter_key):
    setattr(bpy.types.WindowManager, AddonsRegistry._UUID_counter_key, 0 | -prop())

addons_registry = AddonsRegistry(dict(key=__file__, cgl=cgl, ZBufferRecorder=ZBufferRecorder))

NestedLayout._button_registrator = addons_registry._button_registrator

# ===== FINISH SELECTION ANALYSIS ===== #
class WM_OT_finish_selection_analysis(bpy.types.Operator):
    bl_idname = "wm.finish_selection_analysis"
    bl_label = "Refresh"
    bl_description = "Refresh (finish current round of background calculations)"
    bl_options = {'BLOCKING', 'REGISTER'}
    
    def execute(self, context):
        addons_registry.analyze_selection()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        self.sel_iter = addons_registry._sel_iter
        self.total = self.sel_iter.selection_total
        wm.progress_begin(0.0, 1.0)
        self.timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        wm = context.window_manager
        result = addons_registry.analyze_selection(0.125)
        count = self.sel_iter.selection_count
        wm.progress_update((count/self.total if self.total else 1.0))
        if result == self.sel_iter.FINISHED:
            wm.progress_end()
            wm.event_timer_remove(self.timer)
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

bpy.utils.register_class(WM_OT_finish_selection_analysis)

