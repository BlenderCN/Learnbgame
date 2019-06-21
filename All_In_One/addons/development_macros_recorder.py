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

# <pep8-80 compliant>

bl_info = {
    "name": "Macros Recorder",
    "author": "dairin0d",
    "version": (1, 4, 6),
    "blender": (2, 6, 0),
    "location": "Text Editor -> Text -> Record Macro",
    "description": "Record macros to text blocks",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"\
                "Scripts/Development/Macros_Recorder",
    "tracker_url": "https://github.com/dairin0d/macros-recorder/issues",
    "category": "Learnbgame",
}
#============================================================================#

import bpy

from mathutils import Vector, Matrix, Quaternion, Euler, Color

from collections import namedtuple

#============================================================================#

"""
TODO:
* analyze info log too (some lines may contain invalid syntax, though)

Parametric modeling:
* see Sverchok? (node-based) http://nikitron.cc.ua/sverch/html/nodes.html
* originally, I had a thought about something similar, though
    with heavy emphasis on building the parametric operations list
    from the user actions (using a separate scene to build object(s) from actual operators)

Hmm, numpy is already included in Blender since some version

moth3r suggests to take a look at the "pinning values in 3d view" addon
"""

bpy_props = {
    bpy.props.BoolProperty,
    bpy.props.BoolVectorProperty,
    bpy.props.IntProperty,
    bpy.props.IntVectorProperty,
    bpy.props.FloatProperty,
    bpy.props.FloatVectorProperty,
    bpy.props.StringProperty,
    bpy.props.EnumProperty,
    bpy.props.PointerProperty,
    bpy.props.CollectionProperty,
}

def is_bpy_prop(value):
    if isinstance(value, tuple) and (len(value) == 2):
        if (value[0] in bpy_props) and isinstance(value[1], dict):
            return True
    return False

def iter_public_bpy_props(cls, exclude_hidden=False):
    for key in dir(cls):
        if key.startswith("_"):
            continue
        value = getattr(cls, key)
        if is_bpy_prop(value):
            if exclude_hidden:
                options = value[1].get("options", "")
                if 'HIDDEN' in options:
                    continue
            yield (key, value)

def types2props(tp, empty_enum_to_string=True):
    options = set()
    if tp.is_hidden:
        options.add('HIDDEN')
    if tp.is_skip_save:
        options.add('SKIP_SAVE')
    if tp.is_animatable:
        options.add('ANIMATABLE')
    if tp.is_enum_flag:
        options.add('ENUM_FLAG')
    kwargs = dict(name=tp.name, description=tp.description,
                  options=options)
    
    if tp.type in ('POINTER', 'COLLECTION'):
        kwargs["type"] = tp.fixed_type
        pp = bpy.props.CollectionProperty(**kwargs)
    elif tp.type == 'STRING':
        kwargs["default"] = tp.default
        kwargs["maxlen"] = tp.length_max
        pp = bpy.props.StringProperty(**kwargs)
    elif tp.type == 'ENUM':
        defaults = (set(tp.default_flag) if tp.is_enum_flag
                             else tp.default)
        items = [(item.identifier, item.name, item.description)
                 for item in tp.enum_items]
        ids = set(item.identifier for item in tp.enum_items)
        if tp.is_enum_flag:
            for id in tuple(defaults):
                if id not in ids:
                    defaults.discard(id)
        else:
            if defaults not in ids:
                defaults = (ids[0] if ids else '')
        if (not ids) and empty_enum_to_string:
            pp = bpy.props.StringProperty(**kwargs)
        else:
            if ids:
                kwargs["default"] = defaults
            kwargs["items"] = items
            pp = bpy.props.EnumProperty(**kwargs)
    else:
        is_not_array = (tp.array_length == 0)
        
        subtype_map = {'COORDINATES':'XYZ', 'LAYER_MEMBERSHIP':'LAYER'}
        kwargs["subtype"] = subtype_map.get(tp.subtype, tp.subtype)
        
        if is_not_array:
            kwargs["default"] = tp.default
        else:
            kwargs["default"] = tuple(tp.default_array)
            kwargs["size"] = tp.array_length
        
        if tp.type != 'BOOLEAN':
            kwargs["min"] = tp.hard_min
            kwargs["max"] = tp.hard_max
            kwargs["soft_min"] = tp.soft_min
            kwargs["soft_max"] = tp.soft_max
            kwargs["step"] = tp.step
            if tp.type == 'FLOAT':
                kwargs["precision"] = tp.precision
                kwargs["unit"] = tp.unit
        
        if tp.type == 'BOOLEAN':
            if is_not_array:
                pp = bpy.props.BoolProperty(**kwargs)
            else:
                pp = bpy.props.BoolVectorProperty(**kwargs)
        elif tp.type == 'INT':
            if is_not_array:
                pp = bpy.props.IntProperty(**kwargs)
            else:
                pp = bpy.props.IntVectorProperty(**kwargs)
        elif tp.type == 'FLOAT':
            if is_not_array:
                pp = bpy.props.FloatProperty(**kwargs)
            else:
                pp = bpy.props.FloatVectorProperty(**kwargs)
    
    return pp

def get_instance_type_or_emulator(obj):
    if hasattr(obj, "get_instance"): return type(obj.get_instance())
    rna_type = obj.get_rna_type()
    rna_props = rna_type.properties
    # namedtuple fields can't start with underscores, but so do rna props
    return namedtuple(rna_type.identifier, rna_props.keys())(*rna_props.values()) # For Blender 2.79.6

def get_rna_type(obj):
    if hasattr(obj, "rna_type"): return obj.rna_type
    if hasattr(obj, "get_rna"): return obj.get_rna().rna_type
    return obj.get_rna_type() # For Blender 2.79.6

def get_op(idname):
    category_name, op_name = idname.split(".")
    category = getattr(bpy.ops, category_name)
    return getattr(category, op_name)

class CurrentGeneratorProperties(bpy.types.PropertyGroup):
    pass

def repr_props(obj, limit_to=None):
    rna_props = get_rna_type(obj).properties
    
    args = {}
    
    for k, rna in rna_props.items():
        if k == "rna_type":
            continue
        elif (limit_to is not None) and (k not in limit_to):
            continue
        
        v = getattr(obj, k)
        
        if rna.type == 'POINTER':
            v = repr_props(v)
        elif rna.type == 'COLLECTION':
            v = [repr_props(item) for item in v]
        else:
            if type(v).__name__ == "bpy_prop_array":
                v = tuple(v)
        
        args[k] = v
    
    return args

def repr_op_call(op):
    idname = op.bl_idname.replace("_OT_", ".").lower()
    args = repr_props(op)
    args = [("%s=%s" % (k, repr(v))) for k, v in args.items()]
    return ("bpy.ops.%s(%s)" % (idname, ", ".join(args)))

class StringItem(bpy.types.PropertyGroup):
    value = bpy.props.StringProperty()

class SceneMacros(bpy.types.PropertyGroup):
    ops = bpy.props.CollectionProperty(type=StringItem)
    
    def clear(self):
        while self.ops:
            self.ops.remove(0)
    
    def _add(self, op):
        if isinstance(op, str):
            entry = op
        else:
            entry = repr_op_call(op)
        op_storage = self.ops.add()
        op_storage.value = entry
    
    def add(self, op):
        self._add(op)
    
    def add_diff(self, diff):
        for op in diff:
            self._add(op)
    
    def replace_last(self, op):
        if not self.ops:
            op_storage = self.ops.add()
        else:
            op_storage = self.ops[len(self.ops) - 1]
        op_storage.value = repr_op_call(op)
    
    def write_macro_text(self, textblock):
        # NOTE: we can't do a 'live update', because if the user
        # undoes past the point of textblock creation, any access
        # to texts might crash Blender (at least this happens when
        # you try to change operator's arguments after its execution)
        textblock.clear()
        
        as_script = bpy.context.window_manager.record_macro_as_script
        if as_script:
            tabs = ""
            code_template = """
import bpy
from mathutils import Vector, Matrix, Quaternion, Euler, Color

context = bpy.context

{2}
""".strip()
        else:
            tabs = "        "
            code_template = """
import bpy
from mathutils import Vector, Matrix, Quaternion, Euler, Color

class MacroOperator(bpy.types.Operator):
    bl_idname = "macro.{0}"
    bl_label = "{1}"
    
    def execute(self, context):
{2}
        return {3}

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
""".strip()
        
        op_name = textblock.name.replace(".", "_")
        op_label = bpy.path.display_name(textblock.name.replace(".", " "))
        lines = "\n".join((tabs + op.value) for op in self.ops)
        code = code_template.format(op_name, op_label, lines, "{'FINISHED'}")
        textblock.write(code)

class SceneDiff:
    def __init__(self, context):
        scene = context.scene
        wm = context.window_manager
        
        self.scene_hash = hash(scene)
        self.operators_count = len(wm.operators)
        self.selected = None
        self.active = None
        self.cursor = None
        self.pivot = None
        self.pivot_align = None
        self.orientation = None
        self.proportional = None
        self.proportional_edit = None
        self.proportional_falloff = None
    
    def process(self, context):
        scene = context.scene
        active_obj = context.object
        
        undo_redo = False
        scene_hash = hash(scene)
        if self.scene_hash != scene_hash:
            self.scene_hash = scene_hash
            undo_redo = True
        
        is_updated = False
        if active_obj:
            if 'EDIT' in active_obj.mode:
                if active_obj.is_updated or active_obj.is_updated_data:
                    is_updated = True
                data = active_obj.data
                if data.is_updated or data.is_updated_data:
                    is_updated = True
        
        selected = set(obj.name for obj in context.selected_objects)
        active = (active_obj.name if active_obj else None)
        proportional = scene.tool_settings.use_proportional_edit_objects
        proportional_edit = scene.tool_settings.proportional_edit
        proportional_falloff = scene.tool_settings.proportional_edit_falloff
        cursor = Vector(scene.cursor_location)
        
        v3d = MacroRecorder.v3d
        if v3d:
            cursor = v3d.cursor_location
            pivot = v3d.pivot_point
            pivot_align = v3d.use_pivot_point_align
            orientation = v3d.transform_orientation
        else:
            pivot = None
            pivot_align = None
            orientation = None
        
        if self.selected is None:
            self.selected = selected
        if self.active is None:
            self.active = active
        if self.proportional is None:
            self.proportional = proportional
        if self.proportional_edit is None:
            self.proportional_edit = proportional_edit
        if self.proportional_falloff is None:
            self.proportional_falloff = proportional_falloff
        if self.cursor is None:
            self.cursor = cursor
        if self.pivot is None:
            self.pivot = pivot
        if self.pivot_align is None:
            self.pivot_align = pivot_align
        if self.orientation is None:
            self.orientation = orientation
        
        wm = context.window_manager
        operators_count = len(wm.operators)
        if (operators_count != self.operators_count) or undo_redo or is_updated:
            n_added = operators_count - self.operators_count
            if n_added > 0:
                scene.macros.add_diff(wm.operators[-n_added:])
            elif undo_redo:
                scene.macros.add_diff(wm.operators)
            elif is_updated and (n_added == 0) and wm.operators:
                scene.macros.replace_last(wm.operators[-1])
            self.operators_count = operators_count
        else:
            selected_diff = selected.difference(self.selected)
            unselected_diff = self.selected.difference(selected)
            prefix = "context.scene.objects"
            for name in unselected_diff:
                scene.macros.add("%s[%s].select = False" %
                                 (prefix, repr(name)))
            for name in selected_diff:
                scene.macros.add("%s[%s].select = True" %
                                 (prefix, repr(name)))
            if active != self.active:
                scene.macros.add("{0}.active = {0}[{1}]".format(
                                 prefix, repr(name)))
            if cursor != self.cursor:
                cursor_context = ("space_data" if v3d else "scene")
                scene.macros.add("context.%s.cursor_location = %s" %
                                 (cursor_context, repr(cursor)))
            if proportional != self.proportional:
                scene.macros.add("context.scene.tool_settings."\
                                 "use_proportional_edit_objects = %s" %
                                 repr(proportional))
            if proportional_edit != self.proportional_edit:
                scene.macros.add("context.scene.tool_settings."\
                                 "proportional_edit = %s" %
                                 repr(proportional_edit))
            if proportional_falloff != self.proportional_falloff:
                scene.macros.add("context.scene.tool_settings."\
                                 "proportional_edit_falloff = %s" %
                                 repr(proportional_falloff))
            if (pivot is not None) and (pivot != self.pivot):
                scene.macros.add("context.space_data.pivot_point = %s" %
                                 repr(pivot))
            if (pivot_align is not None) and (pivot_align != self.pivot_align):
                scene.macros.add("context.space_data."\
                                 "use_pivot_point_align = %s" %
                                 repr(pivot_align))
            if (orientation is not None) and (orientation != self.orientation):
                scene.macros.add("context.space_data."\
                                 "transform_orientation = %s" %
                                 repr(orientation))
        
        if selected != self.selected:
            self.selected = selected
        if active != self.active:
            self.active = active
        if proportional != self.proportional:
            self.proportional = proportional
        if proportional_edit != self.proportional_edit:
            self.proportional_edit = proportional_edit
        if proportional_falloff != self.proportional_falloff:
            self.proportional_falloff = proportional_falloff
        if cursor != self.cursor:
            self.cursor = cursor
        if pivot != self.pivot:
            self.pivot = pivot
        if pivot_align != self.pivot_align:
            self.pivot_align = pivot_align
        if orientation != self.orientation:
            self.orientation = orientation

class MacroRecorder(bpy.types.Operator):
    """Record operators to a text block"""
    bl_idname = "wm.record_macro"
    bl_label = "Toggle macro recording"
    
    v3d = None
    
    @classmethod
    def poll(cls, context):
        return context.space_data.type in {'TEXT_EDITOR', 'VIEW_3D'}
    
    def invoke(self, context, event):
        global is_macro_recording
        global macro_window
        global macro_recorder
        
        if not is_macro_recording:
            macro_recorder = SceneDiff(context)
            
            for scene in bpy.data.scenes:
                scene.macros.clear()
            
            is_macro_recording = True
            macro_window = context.window
            
            bpy.ops.ed.undo_push(message="Record Macro")
            
            if context.space_data.type == 'VIEW_3D':
                MacroRecorder.v3d = context.space_data
            else:
                MacroRecorder.v3d = None
        else:
            text_block = bpy.data.texts.new("macro")
            context.scene.macros.write_macro_text(text_block)
            if context.space_data.type == 'TEXT_EDITOR':
                context.space_data.text = text_block
            else:
                self.report({'INFO'}, "Created %s" % text_block.name)
            
            is_macro_recording = False
            macro_window = None
            macro_text_block = None
            
            MacroRecorder.v3d = None
            
            bpy.ops.ed.undo_push(message="End Recording")
            
            macro_recorder = None
        
        return {'FINISHED'}

is_macro_recording = False
macro_window = None
macro_recorder = None

def process_diff(scene):
    if not is_macro_recording:
        return
    if bpy.context.window != macro_window:
        return
    macro_recorder.process(bpy.context)

procgen_attrname = "~current_procedural_generator_properties~"

class RegenerateProceduralObject(bpy.types.Operator):
    """Regenerate procedural object"""
    bl_idname = "object.regenerate_procedural_object"
    bl_label = "Regenerate procedural object"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        obj = context.object
        
        if not ((context.mode == 'OBJECT') and obj):
            return False
        
        if obj.procedural_generator:
            return True
        elif wm.operators and ('REGISTER' in wm.operators[-1].bl_options):
            return True
        
        return False
    
    def idname_params(self, obj):
        i = obj.procedural_generator.index("(")
        op_idname = obj.procedural_generator[:i].split(".")[-2:]
        op_params = obj.procedural_generator[(i + 1):-1]
        return op_idname, op_params
    
    def get_datablocks(self, obj_type):
        datablocks = {
            'MESH':'meshes', 'CURVE':'curves','SURFACE':'curves',
            'META':'metaballs', 'FONT':'fonts', 'ARMATURE':'armatures',
            'LATTICE':'lattices', 'EMPTY':None, 'CAMERA':'cameras', 
            'LAMP':'lamps', 'SPEAKER':'speakers',
        }[obj_type]
        
        if datablocks:
            datablocks = getattr(bpy.data, datablocks)
        
        return datablocks
    
    def invoke(self, context, event):
        forbidden = {"bl_rna", "rna_type", "name"}
        cls = CurrentGeneratorProperties
        
        for k in list(cls.__dict__.keys()):
            if not (k.startswith("__") or (k in forbidden)):
                delattr(cls, k)
        
        obj = context.object
        if not obj.procedural_generator:
            wm = context.window_manager
            op = wm.operators[-1]
            obj.procedural_generator = repr_op_call(op)
            # If we don't push an undo level, the next time
            # execute() will be called, obj.procedural_generator
            # would revert to empty string
            bpy.ops.ed.undo_push(message="Store procedural parameters")
        
        op_idname, op_params = self.idname_params(obj)
        
        op = get_op(".".join(op_idname))
        op_class = get_instance_type_or_emulator(op)
        rna_props = get_rna_type(op).properties
        
        for k in dir(op_class):
            if not (k.startswith("__") or (k in forbidden)):
                setattr(cls, k, getattr(op_class, k))
        
        # Not all operators have their properties declared using bpy.props
        # (e.g. most of built-in AddMesh operators)
        for k, v in rna_props.items():
            if hasattr(cls, k):
                continue
            if not (k.startswith("__") or (k in forbidden)):
                v = types2props(v)
                setattr(cls, k, v)
        
        def set_params(**kwargs):
            sub_op = getattr(context.window_manager, procgen_attrname)
            for k, v, in kwargs.items():
                setattr(sub_op, k, v)
        eval("set_params(%s)" % op_params)
        
        if not hasattr(cls, "draw"):
            def draw(self, context):
                sub_op = getattr(context.window_manager, procgen_attrname)
                layout = self.layout
                cls = type(sub_op)
                bpy_props = [kv[0] for kv in iter_public_bpy_props(cls, True)]
                for kv in iter_public_bpy_props(cls, True):
                    sublayout = layout.column()
                    sublayout.prop(sub_op, kv[0])
            setattr(type(self), "draw", draw)
        else:
            def draw(self, context):
                sub_op = getattr(context.window_manager, procgen_attrname)
                sub_op.layout = self.layout
                try:
                    sub_op.draw(context)
                except Exception:
                    # E.g. Sapling addon gives this error:
                    # AttributeError: 'CurrentGeneratorProperties'
                    # object has no attribute 'properties'
                    pass
            setattr(type(self), "draw", draw)
        
        return self.execute(context)
    
    def execute(self, context):
        obj = context.object
        op_idname, op_params = self.idname_params(obj)
        
        sub_op = getattr(context.window_manager, procgen_attrname)
        
        args = {}
        def set_params(**kwargs):
            for k, v, in kwargs.items():
                v = getattr(sub_op, k)
                if type(v).__name__ == "bpy_prop_array":
                    v = tuple(v)
                args[k] = v
        eval("set_params(%s)" % op_params)
        
        args = [("%s=%s" % (k, repr(v))) for k, v in args.items()]
        procgen = ("bpy.ops.%s(%s)" % (".".join(op_idname), ", ".join(args)))
        obj.procedural_generator = procgen
        
        scene_objects = context.scene.objects
        
        n_objs = len(scene_objects)
        selected = list(context.selected_objects)
        
        eval(procgen)
        
        old_data = obj.data
        old_data_name = obj.data.name
        datablocks = self.get_datablocks(obj.type)
        
        # Most recently added objects have lowest indices
        obj.data = scene_objects[0].data
        
        for i in range(len(scene_objects) - n_objs):
            tmp_obj = scene_objects[0]
            scene_objects.unlink(tmp_obj)
            bpy.data.objects.remove(tmp_obj)
        
        if old_data and (old_data.users == 0):
            if datablocks:
                datablocks.remove(old_data)
            
            if obj.data:
                obj.data.name = old_data_name
        
        scene_objects.active = obj
        for sel_obj in selected:
            sel_obj.select = True
        
        return {'FINISHED'}
    
    # This is necessary to make Blender register the operator
    # as an operator that draws something
    def draw(self, context):
        pass

class VIEW3D_PT_macro(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Macro"
    
    def draw(self, context):
        pass
    
    def draw_header(self, context):
        layout = self.layout
        
        icon = ('CANCEL' if is_macro_recording else 'REC')
        layout.operator("wm.record_macro", text="", icon=icon)
        
        if context.mode == 'OBJECT':
            obj = context.object
            if obj and obj.procedural_generator:
                icon = 'FILE_REFRESH'
            else:
                icon = 'FILE_TICK'
            layout.operator("object.regenerate_procedural_object",
                            text="", icon=icon)

def menu_func_draw(self, context):
    text = ("Recording... (Stop)" if is_macro_recording else "Record Macro")
    icon = ('CANCEL' if is_macro_recording else 'REC')
    self.layout.operator("wm.record_macro", text=text, icon=icon)
    self.layout.prop(context.window_manager, "record_macro_as_script")

#============================================================================#
def register():
    bpy.utils.register_class(StringItem)
    bpy.utils.register_class(SceneMacros)
    bpy.utils.register_class(MacroRecorder)
    bpy.utils.register_class(CurrentGeneratorProperties)
    bpy.utils.register_class(RegenerateProceduralObject)
    bpy.utils.register_class(VIEW3D_PT_macro)
    
    bpy.types.Scene.macros = bpy.props.PointerProperty(type=SceneMacros)
    bpy.types.Object.procedural_generator = bpy.props.StringProperty()
    setattr(bpy.types.WindowManager, procgen_attrname,
            bpy.props.PointerProperty(type=CurrentGeneratorProperties))
    
    setattr(bpy.types.WindowManager, "record_macro_as_script",
            bpy.props.BoolProperty(name="Record Macro as script"))
    
    bpy.types.TEXT_MT_text.append(menu_func_draw)
    
    bpy.app.handlers.scene_update_post.append(process_diff)

def unregister():
    bpy.app.handlers.scene_update_post.remove(process_diff)
    
    bpy.types.TEXT_MT_text.remove(menu_func_draw)
    
    delattr(bpy.types.WindowManager, "record_macro_as_script")
    
    delattr(bpy.types.WindowManager, procgen_attrname)
    del bpy.types.Object.procedural_generator
    del bpy.types.Scene.macros
    
    bpy.utils.unregister_class(VIEW3D_PT_macro)
    bpy.utils.unregister_class(RegenerateProceduralObject)
    bpy.utils.unregister_class(CurrentGeneratorProperties)
    bpy.utils.unregister_class(MacroRecorder)
    bpy.utils.unregister_class(SceneMacros)
    bpy.utils.unregister_class(StringItem)

if __name__ == "__main__":
    register()
