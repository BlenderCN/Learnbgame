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

bl_info = {
    "name": "Compact Object panel",
    "description": "Changes Object panel to a more compact layout",
    "author": "dairin0d",
    "version": (1, 0, 0),
    "blender": (2, 67, 0),
    "location": "Object properties panel",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"\
        "Scripts/System/Compact_Object_Panel",
    "tracker_url": "https://github.com/dairin0d/compact-object-panel/issues",
    "category": "Learnbgame"
}
#============================================================================#

# based on 2.67a UI code

import bpy
from bpy.types import Panel
from rna_prop_ui import PropertyPanel, rna_idprop_context_value

import bl_ui

try:
    import dairin0d
    dairin0d_location = ""
except ImportError:
    dairin0d_location = "."

exec("""
from {0}dairin0d.utils_ui import NestedLayout
""".format(dairin0d_location))


class ObjectButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

class OBJECT_MT_context_object_extra_settings(bpy.types.Menu):
    bl_label = "Extra Settings"
    bl_description = "Extra Settings"
    
    def draw(self, context):
        layout = NestedLayout(self.layout, self.bl_idname)
        
        ob = context.object
        
        layout.prop(ob, "use_extra_recalc_object")
        layout.prop(ob, "use_extra_recalc_data")

class OBJECT_PT_context_object(ObjectButtonsPanel, Panel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}
    
    draw_type_icons = {'BOUNDS':'BBOX', 'WIRE':'WIRE', 'SOLID':'SOLID', 'TEXTURED':'POTATO'}
    
    bounds_icons = {'BOX':'MESH_CUBE', 'SPHERE':'MATSPHERE', 'CYLINDER':'MESH_CYLINDER', 'CONE':'MESH_CONE'}
    
    def draw(self, context):
        layout = NestedLayout(self.layout, self.bl_idname)
        space = context.space_data
        
        with layout.row(True):
            if space.use_pin_id:
                layout.template_ID(space, "pin_id")
            else:
                layout.template_ID(context.scene.objects, "active")
            
            layout.menu("OBJECT_MT_context_object_extra_settings", icon='SCRIPTPLUGINS', text="")
        
        ob = context.object
        
        with layout.split():
            with layout.column()(scale_y=0.6):
                layout.prop(ob, "layers", text="")
            layout.prop(ob, "pass_index")
        
        with layout.row(True):
            with layout.column(True):
                with layout.row(True):
                    layout.prop(ob, "show_texture_space", text="", icon='FACESEL_HLT')
                    layout.prop(ob, "show_name", text="", icon='SORTALPHA')
                    layout.prop(ob, "show_wire", text="", icon='WIRE')
                    with layout.split():
                        layout.prop(ob, "draw_type", text="", icon=self.draw_type_icons[ob.draw_type])
                        with layout.split():
                            layout.prop(ob, "show_all_edges", text="", icon='MESH_GRID')
                            layout.prop(ob, "show_x_ray", text="", icon='RADIO')
                with layout.row(True):
                    layout.prop(ob, "show_transparent", text="", icon='IMAGE_RGB_ALPHA')
                    layout.prop(ob, "show_axis", text="", icon='MANIPUL')
                    layout.prop(ob, "show_bounds", text="", icon='BBOX')
                    with layout.split():
                        layout.prop(ob, "draw_bounds_type", text="", icon=self.bounds_icons[ob.draw_bounds_type])
                        layout.prop(ob, "color", text="")

class OBJECT_PT_transform(ObjectButtonsPanel, Panel):
    bl_label = "Transform"
    
    parent_icons = {
        'OBJECT':'OBJECT_DATAMODE',
        'CURVE':'OUTLINER_OB_CURVE',
        'KEY':'KEY_HLT',
        'ARMATURE':'OUTLINER_OB_ARMATURE',
        'LATTICE':'OUTLINER_OB_LATTICE',
        'VERTEX':'VERTEXSEL',
        'VERTEX_3':'OUTLINER_OB_MESH',
        'BONE':'BONE_DATA',
    }
    
    def draw(self, context):
        layout = NestedLayout(self.layout, self.bl_idname)
        
        ob = context.object
        
        rot_aa = (ob.rotation_mode == 'AXIS_ANGLE')
        rot_q = (ob.rotation_mode == 'QUATERNION')
        
        delta = "\u0394"
        
        # ===== LOCATION ===== #
        with layout.fold("Location:"):
            if layout.folded: layout.exit()
            with layout.row():
                labels = ["X", "Y", "Z"]
                with layout.column(True):
                    for i in range(3):
                        layout.prop(ob, "location", text=labels[i], index=i)
                with layout.column(True):
                    for i in range(3):
                        with layout.row(True):
                            layout.prop(ob, "lock_location", text="", index=i)
                            layout.prop(ob, "delta_location", text=delta+labels[i], index=i)
        
        # ===== ROTATION ===== #
        with layout.row()["main"]:
            if rot_q:
                labels = ["W", "X", "Y", "Z"]
                rname = "quaternion"
                drname = "quaternion"
            elif rot_aa:
                labels = ["\u03b1", "X", "Y", "Z"]
                rname = "axis_angle"
                drname = "quaternion" # Axis-Angle has no delta rotation
            else:
                labels = ["X", "Y", "Z"]
                rname = "euler"
                drname = "euler"
            n = len(labels)
            
            with layout.fold("Rotation:"):
                if layout.folded: layout.exit("main")
                with layout.column(True):
                    for i in range(n):
                        layout.prop(ob, "rotation_"+rname, text=labels[i], index=i)
            
            with layout.column():
                with layout.row(True):
                    layout.row(True)(scale_x=0.1, active=rot_aa).prop(ob, "lock_rotations_4d", text="4L", toggle=True)
                    layout.row(True).prop(ob, "rotation_mode", text="")
                
                with layout.column(True):
                    for i in range(n):
                        with layout.row(True):
                            j = (i if n != 4 else i - 1)
                            if j != -1:
                                layout.prop(ob, "lock_rotation", text="", index=j)
                            else:
                                cond = rot_aa and ob.lock_rotations_4d
                                layout.row(True)(active=cond).prop(ob, "lock_rotation_w", text="")
                            layout.row(True)(enabled=not rot_aa).prop(ob, "delta_rotation_"+drname, text=delta+labels[i], index=i)
        
        # ===== SCALE ===== #
        with layout.fold("Scale:"):
            if layout.folded: layout.exit()
            with layout.row():
                labels = ["X", "Y", "Z"]
                with layout.column(True):
                    for i in range(3):
                        layout.prop(ob, "scale", text=labels[i], index=i)
                with layout.column(True):
                    for i in range(3):
                        with layout.row(True):
                            layout.prop(ob, "lock_scale", text="", index=i)
                            layout.prop(ob, "delta_scale", text=delta+labels[i], index=i)
        
        # ===== PARENT ===== #
        parent = ob.parent
        is_armature = bool(parent and parent.type == 'ARMATURE')
        is_bone = bool(ob.parent_type == 'BONE')
        is_slow = bool(parent and ob.use_slow_parent)
        
        with layout.column()["main"]:
            with layout.split():
                with layout.fold("Parent", "row"):
                    if layout.folded: layout.exit("main")
                    layout.prop_menu_enum(ob, "parent_type", text="", icon=self.parent_icons[ob.parent_type])
                
                with layout.row(True):
                    layout.prop(ob, "use_slow_parent", toggle=True, text="", icon=('CHECKBOX_HLT' if ob.use_slow_parent else 'CHECKBOX_DEHLT'))
                    with layout.row(True)(active=is_slow):
                        layout.prop(ob, "slow_parent_offset", text="Slow")
            
            with layout.row(True):
                layout.prop(ob, "parent", text="")
                with layout.row(True)(active=is_bone):
                    if is_bone:
                        layout.prop_search(ob, "parent_bone", parent.data, "bones", text="")
                    else:
                        layout.prop(ob, "parent_bone", text="")
        # ===== END PARENT ===== #

class OBJECT_PT_groups(ObjectButtonsPanel, Panel):
    bl_label = "Groups"
    
    def draw(self, context):
        layout = NestedLayout(self.layout, self.bl_idname)
        
        ob = context.object
        
        with layout.row(True):
            if bpy.data.groups:
                layout.operator("object.group_link", text="Add to Group")
            else:
                layout.operator("object.group_add", text="Add to Group")
            layout.operator("object.group_add", text="", icon='ZOOMIN')
        
        # object.dupli_offset_from_cursor operator is implemented as
        # ob.users_group[group].dupli_offset = scene.cursor_location
        for index, group in enumerate(ob.users_group):
            with layout.column(True):
                layout.context_pointer_set("group", group)
                
                with layout.box():
                    with layout.row():
                        layout.prop(group, "name", text="")
                        layout.operator("object.group_remove", text="", icon='X', emboss=False)
                
                with layout.box():
                    with layout.split():
                        with layout.column():
                            with layout.column()(scale_y=0.8):
                                layout.label("Dupli Visibility:")
                            with layout.column()(scale_y=0.6):
                                layout.prop(group, "layers", text="")
                            layout.operator("object.dupli_offset_from_cursor", text="From Cursor").group = index
                        with layout.column():
                            layout.prop(group, "dupli_offset", text="")

class OBJECT_PT_duplication(ObjectButtonsPanel, Panel):
    bl_label = "Duplication"

    def draw(self, context):
        layout = NestedLayout(self.layout, self.bl_idname)
        
        ob = context.object
        
        layout.prop(ob, "dupli_type", expand=True)
        
        if ob.dupli_type == 'FRAMES':
            with layout.split():
                with layout.column(True):
                    layout.prop(ob, "dupli_frames_start", text="Start")
                    layout.prop(ob, "dupli_frames_end", text="End")
                with layout.column(True):
                    layout.prop(ob, "dupli_frames_on", text="On")
                    layout.prop(ob, "dupli_frames_off", text="Off")
            with layout.split(0.5):
                with layout.row():
                    layout.prop(ob, "use_dupli_frames_speed", text="Speed", toggle=True)
                    with layout.row()(scale_x=0.7, alignment='RIGHT'):
                        layout.label("Axes:")
                with layout.row(True):
                    layout.prop(ob, "track_axis", text="")
                    layout.prop(ob, "up_axis", text="")
        elif ob.dupli_type == 'VERTS':
            layout.prop(ob, "use_dupli_vertices_rotation", text="Align to normals")
        elif ob.dupli_type == 'FACES':
            with layout.row(True):
                use_scale = ob.use_dupli_faces_scale
                layout.prop(ob, "use_dupli_faces_scale", text="", icon=('CHECKBOX_HLT' if use_scale else 'CHECKBOX_DEHLT'))
                with layout.row(True)(active=use_scale):
                    layout.prop(ob, "dupli_faces_scale", text="Inherit Scale")
        elif ob.dupli_type == 'GROUP':
            layout.prop(ob, "dupli_group", text="Group")

from bl_ui.properties_animviz import MotionPathButtonsPanel, OnionSkinButtonsPanel

class OBJECT_PT_motion_paths(MotionPathButtonsPanel, Panel):
    #bl_label = "Object Motion Paths"
    bl_context = "object"
    
    @classmethod
    def poll(cls, context):
        return (context.object)
    
    def draw(self, context):
        layout = self.layout
        
        ob = context.object
        avs = ob.animation_visualization
        mpath = ob.motion_path
        
        # What 'bones' parameter means?
        self.draw_settings(context, avs, mpath)
    
    def draw_settings(self, context, avs, mpath, bones=False):
        layout = NestedLayout(self.layout, self.bl_idname)
        
        mps = avs.motion_path
        
        layout.prop(mps, "type", expand=True)
        
        with layout.split():
            with layout.column():
                with layout.row(True):
                    icon = ('BONE_DATA' if bones else 'OBJECT_DATA')
                    ctg = ("pose" if bones else "object") # operator category
                    if mpath:
                        text = "%s-%s (cached)" % (mpath.frame_start, mpath.frame_end)
                        '''
                        layout.label(text, icon)
                        
                        layout.operator(ctg + ".paths_update", text="", icon='FILE_REFRESH')
                        '''
                        layout.operator(ctg + ".paths_update", text=" "+text, icon='FILE_REFRESH')
                        
                        layout.operator(ctg + ".paths_clear", text="", icon='X')
                    else:
                        layout.operator(ctg + ".paths_calculate", text="Cache", icon=icon)
                
                with layout.column(True):
                    if (mps.type == 'CURRENT_FRAME'):
                        layout.prop(mps, "frame_before", text="Before")
                        layout.prop(mps, "frame_after", text="After")
                    elif (mps.type == 'RANGE'):
                        layout.prop(mps, "frame_start", text="Start")
                        layout.prop(mps, "frame_end", text="End")
                    
                    layout.prop(mps, "frame_step", text="Step")
                
                if bones:
                    with layout.row():
                        layout.prop(mps, "bake_location", expand=True)
            
            def icon(value):
                return 'NONE'
                return ('RESTRICT_VIEW_OFF' if value else 'RESTRICT_VIEW_ON')
            
            with layout.column(True):
                toggle = 0#True
                emboss = 1#False
                align = 'EXPAND'#'LEFT'
                layout.label(text="Show:")
                with layout.row()(alignment=align):
                    layout.prop(mps, "show_frame_numbers", text="Frame Numbers", toggle=toggle, emboss=emboss, icon=icon(mps.show_frame_numbers))
                with layout.row()(alignment=align):
                    layout.prop(mps, "show_keyframe_numbers", text="Keyframe Numbers", toggle=toggle, emboss=emboss, icon=icon(mps.show_keyframe_numbers))
                with layout.row()(alignment=align):
                    layout.prop(mps, "show_keyframe_highlight", text="Keyframes", toggle=toggle, emboss=emboss, icon=icon(mps.show_keyframe_highlight))
                if bones:
                    with layout.row()(alignment=align):
                        layout.prop(mps, "show_keyframe_action_all", text="+ Non-Grouped Keyframes", toggle=toggle, emboss=emboss, icon=icon(mps.show_keyframe_action_all))

# inherit from panel when ready
class OBJECT_PT_onion_skinning(OnionSkinButtonsPanel): # , Panel):
    #bl_label = "Object Onion Skinning"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return (context.object)

    def draw(self, context):
        ob = context.object

        self.draw_settings(context, ob.animation_visualization)

class OBJECT_PT_custom_props(ObjectButtonsPanel, PropertyPanel, Panel):
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}
    _context_path = "object"
    _property_type = bpy.types.Object

    def draw(self, context):
        layout = NestedLayout(self.layout, self.bl_idname)
        context_member = self._context_path
        property_type = self._property_type
        use_edit = True
        
        def assign_props(prop, val, key):
            prop.data_path = context_member
            prop.property = key
            
            try:
                prop.value = str(val)
            except:
                pass
        
        rna_item, context_member = rna_idprop_context_value(context, context_member, property_type)
        
        # poll should really get this...
        if not rna_item:
            return
        
        if rna_item.id_data.library is not None:
            use_edit = False
        
        assert(isinstance(rna_item, property_type))
        
        items = rna_item.items()
        items.sort()
        
        if use_edit:
            with layout.row():
                props = layout.operator("wm.properties_add", text="Add")
                props.data_path = context_member
        
        rna_properties = {prop.identifier for prop in rna_item.bl_rna.properties if prop.is_runtime} if items else None
        
        with layout.column(True):
            for key, val in items:
                if key == '_RNA_UI':
                    continue
                
                to_dict = getattr(val, "to_dict", None)
                to_list = getattr(val, "to_list", None)
                # val_orig = val  # UNUSED
                if to_dict:
                    val = to_dict()
                    val_draw = str(val)
                elif to_list:
                    val = to_list()
                    val_draw = str(val)
                else:
                    val_draw = val
                
                with layout.row(True):
                    if use_edit:
                        props = layout.operator("wm.properties_edit", text=key)
                        assign_props(props, val_draw, key)
                    else:
                        layout.label(text=key)
                    
                    if to_dict or to_list:
                        if use_edit:
                            props = layout.operator("wm.properties_edit", text=val_draw)
                            assign_props(props, val_draw, key)
                        else:
                            layout.label(text=val_draw)
                    else:
                        if key in rna_properties:
                            layout.prop(rna_item, key, text="")
                        else:
                            layout.prop(rna_item, '["%s"]' % key, text="")
                    
                    if use_edit:
                        props = layout.operator("wm.properties_remove", text="", icon='ZOOMOUT')
                        assign_props(props, val_draw, key)

# ========================================================= #

def reregister_module(module, register):
    reregister = (bpy.utils.register_class if register else bpy.utils.unregister_class)
    
    Panel = bpy.types.Panel
    
    for name in dir(module):
        if name.startswith("__"):
            continue
        
        cls = getattr(module, name)
        if cls is Panel:
            continue
        
        try:
            if not issubclass(cls, Panel):
                continue
        except TypeError:
            # not a class
            continue
        
        try:
            reregister(cls)
        except RuntimeError:
            # class already (un)registered
            pass

def register():
    reregister_module(bl_ui.properties_object, False)
    
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
    
    reregister_module(bl_ui.properties_object, True)

if __name__ == "__main__":  # only for live edit.
    register()
