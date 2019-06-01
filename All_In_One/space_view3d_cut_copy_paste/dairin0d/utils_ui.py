# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import blf

from mathutils import Color, Vector, Matrix, Quaternion, Euler

from .bpy_inspect import BlRna
from .utils_python import DummyObject
from .utils_gl import cgl

#============================================================================#

# Note: making a similar wrapper for Operator.report is impossible,
# since Blender only shows the report from the currently executing operator.

# ===== MESSAGEBOX ===== #
if not hasattr(bpy.types, "WM_OT_messagebox"):
    class WM_OT_messagebox(bpy.types.Operator):
        bl_idname = "wm.messagebox"
        
        # "Attention!" is quite generic caption that suits
        # most of the situations when "OK" button is desirable.
        # bl_label isn't really changeable at runtime
        # (changing it causes some memory errors)
        bl_label = "Attention!"
        
        # We can't pass arguments through normal means,
        # since in this case a "Reset" button would appear
        args = {}
        
        # If we don't define execute(), there would be
        # an additional label "*Redo unsupported*"
        def execute(self, context):
            return {'FINISHED'}
        
        def invoke(self, context, event):
            text = self.args.get("text", "")
            self.icon = self.args.get("icon", 'NONE')
            if (not text) and (self.icon == 'NONE'):
                return {'CANCELLED'}
            
            border_w = 8*2
            icon_w = (0 if (self.icon == 'NONE') else 16)
            w_incr = border_w + icon_w
            
            width = self.args.get("width", 300) - border_w
            
            self.lines = []
            max_x = cgl.text.split_text(width, icon_w, 0, text, self.lines, font=0)
            width = max_x + border_w
            
            self.spacing = self.args.get("spacing", 0.5)
            self.spacing = max(self.spacing, 0.0)
            
            wm = context.window_manager
            
            confirm = self.args.get("confirm", False)
            
            if confirm:
                return wm.invoke_props_dialog(self, width)
            else:
                return wm.invoke_popup(self, width)
        
        def draw(self, context):
            layout = self.layout
            
            col = layout.column()
            col.scale_y = 0.5 * (1.0 + self.spacing * 0.5)
            
            icon = self.icon
            for line in self.lines:
                if icon != 'NONE': line = " "+line
                col.label(text=line, icon=icon)
                icon = 'NONE'
    
    bpy.utils.register_class(WM_OT_messagebox) # REGISTER

def messagebox(text, icon='NONE', width=300, confirm=False, spacing=0.5):
    """
    Displays a message box with the given text and icon.
    text -- the messagebox's text
    icon -- the icon (displayed at the start of the text)
        Defaults to 'NONE' (no icon).
    width -- the messagebox's max width
        Defaults to 300 pixels.
    confirm -- whether to display "OK" button (this is purely
        cosmetical, as the message box is non-blocking).
        Defaults to False.
    spacing -- relative distance between the lines
        Defaults to 0.5.
    """
    WM_OT_messagebox = bpy.types.WM_OT_messagebox
    WM_OT_messagebox.args["text"] = text
    WM_OT_messagebox.args["icon"] = icon
    WM_OT_messagebox.args["width"] = width
    WM_OT_messagebox.args["spacing"] = spacing
    WM_OT_messagebox.args["confirm"] = confirm
    bpy.ops.wm.messagebox('INVOKE_DEFAULT')
#============================================================================#

# Note:
# if item is property group instance and item["pi"] = 3.14,
# in UI it should be displayed like this: layout.prop(item, '["pi"]')

# ===== NESTED LAYOUT ===== #
class NestedLayout:
    """
    Utility for writing more structured UI drawing code.
    Attention: layout properties are propagated to sublayouts!
    
    Example:
    
    def draw(self, context):
        layout = NestedLayout(self.layout, self.bl_idname)
        
        exit_layout = True
        
        # You can use both the standard way:
        
        sublayout = layout.split()
        sublayout.label("label A")
        sublayout.label("label B")
        
        # And the structured way:
        
        with layout:
            layout.label("label 1")
            if exit_layout: layout.exit()
            layout.label("label 2") # won't be executed
        
        with layout.row(True)["main"]:
            layout.label("label 3")
            with layout.row(True)(enabled=False):
                layout.label("label 4")
                if exit_layout: layout.exit("main")
                layout.label("label 5") # won't be executed
            layout.label("label 6") # won't be executed
        
        with layout.fold("Foldable micro-panel", "box"):
            if layout.folded: layout.exit()
            layout.label("label 7")
            with layout.fold("Foldable 2"):
                layout.label("label 8") # not drawn if folded
    """
    
    _sub_names = {"row", "column", "column_flow", "box", "split", "menu_pie"}
    
    _default_attrs = dict(
        active = True,
        alert = False,
        alignment = 'EXPAND',
        enabled =  True,
        operator_context = 'INVOKE_DEFAULT',
        scale_x = 1.0,
        scale_y = 1.0,
    )
    
    def __new__(cls, layout, idname="", parent=None):
        """
        Wrap the layout in a NestedLayout.
        To avoid interference with other panels' foldable
        containers, supply panel's bl_idname as the idname.
        """
        if isinstance(layout, cls) and (layout._idname == idname): return layout
        
        self = object.__new__(cls)
        self._idname = idname
        self._parent = parent
        self._layout = layout
        self._stack = [self]
        self._attrs = dict(self._default_attrs)
        self._tag = None
        
        # propagate settings to sublayouts
        if parent: self(**parent._stack[-1]._attrs)
        
        return self
    
    def __getattr__(self, name):
        layout = self._stack[-1]._layout
        if not layout:
            # This is the dummy layout; imitate normal layout
            # behavior without actually drawing anything.
            if name in self._sub_names:
                return (lambda *args, **kwargs: NestedLayout(None, self._idname, self))
            else:
                return self._attrs.get(name, self._dummy_callable)
        
        if name in self._sub_names:
            func = getattr(layout, name)
            return (lambda *args, **kwargs: NestedLayout(func(*args, **kwargs), self._idname, self))
        else:
            return getattr(layout, name)
    
    def __setattr__(self, name, value):
        if name.startswith("_"):
            self.__dict__[name] = value
        else:
            wrapper = self._stack[-1]
            wrapper._attrs[name] = value
            if wrapper._layout: setattr(wrapper._layout, name, value)
    
    def __call__(self, **kwargs):
        """Batch-set layout attributes."""
        wrapper = self._stack[-1]
        wrapper._attrs.update(kwargs)
        layout = wrapper._layout
        if layout:
            for k, v in kwargs.items():
                setattr(layout, k, v)
        return self
    
    @staticmethod
    def _dummy_callable(*args, **kwargs):
        return NestedLayout._dummy_obj
    _dummy_obj = DummyObject()
    
    # ===== FOLD (currently very hacky) ===== #
    # Each foldable micropanel needs to store its fold-status
    # as a Bool property (in order to be clickable in the UI)
    # somewhere where it would be saved with .blend, but won't
    # be affected by most of the other things (i.e., in Screen).
    # At first I thought to implement such storage with
    # nested dictionaries, but currently layout.prop() does
    # not recognize ID-property dictionaries as a valid input.
    class FoldPG(bpy.types.PropertyGroup):
        def update(self, context):
            pass # just indicates that the widget needs to be force-updated
        value = bpy.props.BoolProperty(description="Fold/unfold", update=update, name="")
    bpy.utils.register_class(FoldPG) # REGISTER
    
    # make up some name that's unlikely to be used by normal addons
    folds_keyname = "dairin0d_ui_utils_NestedLayout_ui_folds"
    setattr(bpy.types.Screen, folds_keyname, bpy.props.CollectionProperty(type=FoldPG)) # REGISTER
    
    folded = False # stores folded status from the latest fold() call
    
    def fold(self, text, container=None, folded=False, key=None):
        """
        Create a foldable container.
        text -- the container's title/label
        container -- a sequence (type_of_container, arg1, ..., argN)
            where type_of_container is one of {"row", "column",
            "column_flow", "box", "split"}; arg1..argN are the
            arguments of the corresponding container function.
            If you supply just the type_of_container, it would be
            interpreted as (type_of_container,).
        folded -- whether the container should be folded by default.
            Default value is False.
        key -- the container's unique identifier within the panel.
            If not specified, the container's title will be used
            in its place.
        """
        data_path = "%s:%s" % (self._idname, key or text)
        folds = getattr(bpy.context.screen, self.folds_keyname)
        
        try:
            this_fold = folds[data_path]
        except KeyError:
            this_fold = folds.add()
            this_fold.name = data_path
            this_fold.value = folded
        
        is_fold = this_fold.value
        icon = ('DOWNARROW_HLT' if not is_fold else 'RIGHTARROW')
        
        # make the necessary container...
        if not container:
            container_args = ()
            container = "column"
        elif isinstance(container, str):
            container_args = ()
        else:
            container_args = container[1:]
            container = container[0]
        res = getattr(self, container)(*container_args)
        
        with res.row(True)(alignment='LEFT'):
            res.prop(this_fold, "value", text=text, icon=icon, emboss=False, toggle=True)
        
        # make fold-status accessible to the calling code
        self.__dict__["folded"] = is_fold
        
        # If folded, return dummy layout
        if is_fold: return NestedLayout(None, self._idname, self)
        
        return res
    
    # ===== BUTTON (currently very hacky) ===== #
    _button_registrator = None
    def button(self, callback, *args, tooltip=None, **kwargs):
        """Draw a dynamic button. Callback and tooltip are expected to be stable."""
        registrator = self._button_registrator
        op_idname = (registrator.get(callback, tooltip) if registrator else None)
        if not op_idname: op_idname = "wm.dynamic_button_dummy"
        return self.operator(op_idname, *args, **kwargs)
    
    # ===== NESTED CONTEXT MANAGEMENT ===== #
    class ExitSublayout(Exception):
        def __init__(self, tag=None):
            self.tag = tag
    
    @classmethod
    def exit(cls, tag=None):
        """Jump out of current (or marked with the given tag) layout's context."""
        raise cls.ExitSublayout(tag)
    
    def __getitem__(self, tag):
        """Mark this layout with the tag"""
        self._tag = tag
        return self
    
    def __enter__(self):
        # Only nested (context-managed) layouts are stored in stack
        parent = self._parent
        if parent: parent._stack.append(self)
    
    def __exit__(self, type, value, traceback):
        # Only nested (context-managed) layouts are stored in stack
        parent = self._parent
        if parent: parent._stack.pop()
        
        if type == self.ExitSublayout:
            # Is this the layout the exit() was requested for?
            # Yes: suppress the exception. No: let it propagate to the parent.
            return (value.tag is None) or (value.tag == self._tag)

if not hasattr(bpy.types, "WM_OT_dynamic_button_dummy"):
    class WM_OT_dynamic_button_dummy(bpy.types.Operator):
        bl_idname = "wm.dynamic_button_dummy"
        bl_label = " "
        bl_description = ""
        bl_options = {'INTERNAL'}
        arg = bpy.props.StringProperty()
        def execute(self, context):
            return {'CANCELLED'}
        def invoke(self, context, event):
            return {'CANCELLED'}
    bpy.utils.register_class(WM_OT_dynamic_button_dummy)

class DynamicButton:
    def __init__(self, id):
        self.age = 0
        self.id = id
    
    def register(self, btn_info):
        data_path, callback, tooltip = btn_info
        
        if not callback:
            def execute(self, context):
                return {'CANCELLED'}
            def invoke(self, context, event):
                return {'CANCELLED'}
        elif data_path:
            full_path_resolve = BlRna.full_path_resolve
            def execute(self, context):
                _self = full_path_resolve(data_path)
                return ({'CANCELLED'} if callback(_self, context, None, self.arg) is False else {'FINISHED'})
            def invoke(self, context, event):
                _self = full_path_resolve(data_path)
                return ({'CANCELLED'} if callback(_self, context, event, self.arg) is False else {'FINISHED'})
        else:
            def execute(self, context):
                return ({'CANCELLED'} if callback(context, None, self.arg) is False else {'FINISHED'})
            def invoke(self, context, event):
                return ({'CANCELLED'} if callback(context, event, self.arg) is False else {'FINISHED'})
        
        self.op_idname = "wm.dynamic_button_%s" % self.id
        self.op_class = type("WM_OT_dynamic_button_%s" % self.id, (bpy.types.Operator,), dict(
            bl_idname = self.op_idname,
            bl_label = "",
            bl_description = tooltip,
            bl_options = {'INTERNAL'},
            arg = bpy.props.StringProperty(),
            execute = execute,
            invoke = invoke,
        ))
        bpy.utils.register_class(self.op_class)
    
    def unregister(self):
        bpy.utils.unregister_class(self.op_class)

class ButtonRegistrator:
    max_age = 2
    
    def __init__(self):
        self.update_counter = 0
        self.layout_counter = 0
        self.free_ids = []
        self.to_register = set()
        self.to_unregister = set()
        self.registered = {}
    
    def register_button(self, btn_info):
        if self.free_ids:
            btn_id = self.free_ids.pop()
        else:
            btn_id = len(self.registered)
        
        btn = DynamicButton(btn_id)
        btn.register(btn_info)
        
        self.registered[btn_info] = btn
    
    def unregister_button(self, btn_info):
        btn = self.registered.pop(btn_info)
        self.free_ids.append(btn.id)
        btn.unregister()
    
    def update(self):
        if self.to_unregister:
            for btn_info in self.to_unregister:
                self.unregister_button(btn_info)
            self.to_unregister.clear()
        
        if self.to_register:
            for btn_info in self.to_register:
                self.register_button(btn_info)
            self.to_register.clear()
        
        self.update_counter += 1
    
    def increment_age(self):
        for btn_info, btn in self.registered.items():
            btn.age += 1
            if btn.age > self.max_age:
                self.to_unregister.add(btn_info)
    
    def get(self, callback, tooltip):
        if self.layout_counter != self.update_counter:
            self.layout_counter = self.update_counter
            self.increment_age()
        
        if not callback:
            if not tooltip: return None
            btn_info = (None, None, tooltip)
        else:
            if tooltip is None: tooltip = (callback.__doc__ or "") # __doc__ can be None
            
            callback_self = getattr(callback, "__self__", None)
            if isinstance(callback_self, bpy.types.PropertyGroup):
                # we cannot keep reference to this object, only the data path
                full_path = BlRna.full_path(callback_self)
                btn_info = (full_path, callback.__func__, tooltip)
            else:
                btn_info = (None, callback, tooltip)
        
        btn = self.registered.get(btn_info)
        if btn:
            btn.age = 0
            return btn.op_idname
        
        self.to_register.add(btn_info)

#============================================================================#

# TODO: put all these into BlUI class?

def tag_redraw(arg=None):
    """A utility function to tag redraw of arbitrary UI units."""
    if arg is None:
        arg = bpy.context.window_manager
    elif isinstance(arg, bpy.types.Window):
        arg = arg.screen
    
    if isinstance(arg, bpy.types.Screen):
        for area in arg.areas:
            area.tag_redraw()
    elif isinstance(arg, bpy.types.WindowManager):
        for window in arg.windows:
            for area in window.screen.areas:
                area.tag_redraw()
    else: # Region, Area, RenderEngine
        arg.tag_redraw()

def calc_region_rect(area, r, overlap=True):
    # Note: there may be more than one region of the same type (e.g. in quadview)
    if (not overlap) and (r.type == 'WINDOW'):
        x0, y0, x1, y1 = r.x, r.y, r.x+r.width, r.y+r.height
        ox0, oy0, ox1, oy1 = x0, y0, x1, y1
        for r in area.regions:
            if r.type == 'TOOLS':
                ox0 = r.x + r.width
            elif r.type == 'UI':
                ox1 = r.x
        x0, y0, x1, y1 = max(x0, ox0), max(y0, oy0), min(x1, ox1), min(y1, oy1)
        return (Vector((x0, y0)), Vector((x1-x0, y1-y0)))
    else:
        return (Vector((r.x, r.y)), Vector((r.width, r.height)))

def point_in_rect(p, r):
    return ((p[0] >= r.x) and (p[0] < r.x + r.width) and (p[1] >= r.y) and (p[1] < r.y + r.height))

def rv3d_from_region(area, region):
    if (area.type != 'VIEW_3D') or (region.type != 'WINDOW'): return None
    
    space_data = area.spaces.active
    try:
        quadviews = space_data.region_quadviews
    except AttributeError:
        quadviews = None # old API
    
    if not quadviews: return space_data.region_3d
    
    x_id = 0
    y_id = 0
    for r in area.regions:
        if (r.type == 'WINDOW') and (r != region):
            if r.x < region.x: x_id = 1
            if r.y < region.y: y_id = 1
    
    # 0: bottom left (Front Ortho)
    # 1: top left (Top Ortho)
    # 2: bottom right (Right Ortho)
    # 3: top right (User Persp)
    return quadviews[y_id | (x_id << 1)]

# areas can't overlap, but regions can
def ui_contexts_under_coord(x, y, window=None):
    point = int(x), int(y)
    if not window: window = bpy.context.window
    screen = window.screen
    scene = screen.scene
    tool_settings = scene.tool_settings
    for area in screen.areas:
        if point_in_rect(point, area):
            space_data = area.spaces.active
            for region in area.regions:
                if point_in_rect(point, region):
                    yield dict(window=window, screen=screen,
                        area=area, space_data=space_data, region=region,
                        region_data=rv3d_from_region(area, region),
                        scene=scene, tool_settings=tool_settings)
            break

def ui_context_under_coord(x, y, index=0, window=None):
    ui_context = None
    for i, ui_context in enumerate(ui_contexts_under_coord(x, y, window)):
        if i == index: return ui_context
    return ui_context

def find_ui_area(area_type, region_type='WINDOW', window=None):
    if not window: window = bpy.context.window
    screen = window.screen
    scene = screen.scene
    tool_settings = scene.tool_settings
    for area in screen.areas:
        if area.type == area_type:
            space_data = area.spaces.active
            region = None
            for _region in area.regions:
                if _region.type == region_type: region = _region
            return dict(window=window, screen=screen,
                area=area, space_data=space_data, region=region,
                region_data=rv3d_from_region(area, region),
                scene=scene, tool_settings=tool_settings)

def ui_hierarchy(ui_obj):
    if isinstance(ui_obj, bpy.types.Window):
        return (ui_obj, None, None)
    elif isinstance(ui_obj, bpy.types.Area):
        wm = bpy.context.window_manager
        for window in wm.windows:
            for area in window.screen.areas:
                if area == ui_obj: return (window, area, None)
    elif isinstance(ui_obj, bpy.types.Region):
        wm = bpy.context.window_manager
        for window in wm.windows:
            for area in window.screen.areas:
                for region in area.regions:
                    if region == ui_obj: return (window, area, region)

# TODO: relative coords?
def convert_ui_coord(area, region, xy, src, dst, vector=True):
    x, y = xy
    if src == dst:
        pass
    elif src == 'WINDOW':
        if dst == 'AREA':
            x -= area.x
            y -= area.y
        elif dst == 'REGION':
            x -= region.x
            y -= region.y
    elif src == 'AREA':
        if dst == 'WINDOW':
            x += area.x
            y += area.y
        elif dst == 'REGION':
            x += area.x - region.x
            y += area.y - region.y
    elif src == 'REGION':
        if dst == 'WINDOW':
            x += region.x
            y += region.y
        elif dst == 'AREA':
            x += region.x - area.x
            y += region.y - area.y
    return (Vector((x, y)) if vector else (int(x), int(y)))

#============================================================================#
