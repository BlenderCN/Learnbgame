"""BlenderFDS, Blender panels"""

import bpy
from blenderfds.types import *
from blenderfds.lib import fds_surf

class SCENE_PT_BF():
    bl_label = "BlenderFDS Case"
    bl_idname = "SCENE_PT_BF"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
    bf_namelist_idname = None

    def draw_header(self, context):
        layout = self.layout
        element = context.scene
        self.bl_label = bf_namelists[type(self).bf_namelist_idname].draw_header(layout, context, element)
        
    def draw(self, context):
        layout = self.layout
        element = context.scene
        # Panel
        bf_namelists[type(self).bf_namelist_idname].draw(layout, context, element)
        
class SCENE_PT_BF_HEAD(SCENE_PT_BF, bpy.types.Panel):
    bl_idname = "SCENE_PT_BF_HEAD"
    bf_namelist_idname = "bf_head"

    def draw(self, context):
        layout = self.layout
        element = context.scene
        # Restore cursor in case of unhandled Exception
        w = context.window_manager.windows[0]
        w.cursor_modal_restore()
        # Draw element messages
        element.draw_messages(layout, context, element)
        # Panel
        bf_namelists[type(self).bf_namelist_idname].draw(layout, context, element)
        # Other operators
        row = layout.row()
        row.label("")
        row.operator("scene.bf_props_to_scene") 

class SCENE_PT_BF_TIME(SCENE_PT_BF, bpy.types.Panel):
    bl_idname = "SCENE_PT_BF_TIME"
    bf_namelist_idname = "bf_time"

class SCENE_PT_BF_DUMP(SCENE_PT_BF, bpy.types.Panel):
    bl_idname = "SCENE_PT_BF_DUMP"
    bf_namelist_idname = "bf_dump"

class SCENE_PT_BF_MISC(SCENE_PT_BF, bpy.types.Panel):
    bl_idname = "SCENE_PT_BF_MISC"
    bf_namelist_idname = "bf_misc"

class SCENE_PT_BF_REAC(SCENE_PT_BF, bpy.types.Panel):
    bl_idname = "SCENE_PT_BF_REAC"
    bf_namelist_idname = "bf_reac"

class OBJECT_PT_BF(bpy.types.Panel):
    bl_label = "BlenderFDS Geometric Entity"
    bl_idname = "OBJECT_PT_BF"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob and ob.type in ("MESH", "EMPTY")

    def draw_header(self, context):
        layout = self.layout
        element = context.active_object     
        # Header for temporary object
        if   element.bf_is_tmp: self.bl_label = "BlenderFDS Temporary Object"
        # Header for EMPTY object
        elif element.type == "EMPTY":
            layout.prop(element, "bf_export", text="")
            self.bl_label = "BlenderFDS Empty (Section of namelists)"
        # Header for MESH object
        else: self.bl_label = element.bf_namelist.draw_header(layout, context, element)

    def draw(self, context):
        layout = self.layout
        element = context.active_object
        # Restore cursor in case of unhandled Exception
        w = context.window_manager.windows[0]
        w.cursor_modal_restore()
        # Draw element messages
        element.draw_messages(layout, context, element)
        # Panel for temporary object
        if element.bf_is_tmp:
            layout.operator("scene.bf_del_all_tmp_objects")
            return
        # Panel for EMPTY object
        if element.type == "EMPTY":
            bf_props["bf_id"].draw(layout, context, element)
            bf_props["bf_fyi"].draw(layout, context, element)
            return
        # Panel for MESH object
        if element.type == "MESH":
            split = layout.split(.6)  # namelist
            split.prop(element, "bf_namelist_idname", text="")
            row = split.row(align=True)  # aspect
            row.prop(element, "show_transparent", icon="GHOST", text="")
            row.prop(element, "draw_type", text="")
            row.prop(element, "hide", text="")
            row.prop(element, "hide_select", text="")
            row.prop(element, "hide_render", text="")
            element.bf_namelist.draw(layout, context, element)
            row = layout.row()
            if element.bf_has_tmp: row.operator("scene.bf_del_all_tmp_objects")
            else: row.operator("object.bf_show_fds_geometries")
            row.operator("object.bf_props_to_sel_obs")

class MATERIAL_PT_BF(bpy.types.Panel):
    bl_label = "BlenderFDS Boundary Condition"
    bl_idname = "MATERIAL_PT_BF"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls,context):
        ma = context.material
        ob = context.active_object
        return ma and ob and ob.type == "MESH" and "bf_surf_id" in ob.descendants and not ob.bf_is_tmp

    def draw_header(self, context):
        layout = self.layout
        element = context.material
        self.bl_label = element.bf_namelist.draw_header(layout, context, element)

    def draw(self, context):
        layout = self.layout
        element = context.material
        # Restore cursor in case of unhandled Exception
        w = context.window_manager.windows[0]
        w.cursor_modal_restore()
        # Draw element messages
        element.draw_messages(layout, context, element)
        # Panel
        split = layout.split(.7) # namelist
        split.prop(element, "bf_namelist_idname", text="")
        row = split.row(align=True) # aspect
        row.prop(element, "diffuse_color", text="")
        row.prop(element, "alpha", text="")
        element.bf_namelist.draw(layout, context, element)
        # Other operators
        row = layout.row()
        if fds_surf.has_predefined: row.label("")
        else: row.operator("material.bf_set_predefined", icon="WARNING")
        row.operator("material.bf_surf_to_sel_obs") 
