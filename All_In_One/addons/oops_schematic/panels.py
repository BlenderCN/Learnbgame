
import bpy


class OopsSchematicBasePanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "OOPS Schematic"

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "OopsSchematic"


class OopsSchematicDisplayOptionsPanel(OopsSchematicBasePanel):
    bl_idname = "NODE_PT_oops_schematic_display_options"
    bl_label = "Display Options"

    def draw(self, context):
        layout = self.layout
        s = context.window_manager.oops_schematic
        layout.prop(s, 'select_3d_view')
        layout.prop(s, 'tree_width')
        layout.prop(s, 'curve_resolution')


class OopsSchematicUsedNodesPanel(OopsSchematicBasePanel):
    bl_idname = "NODE_PT_oops_schematic_used_nodes"
    bl_label = "Used Nodes"

    def draw(self, context):
        layout = self.layout
        s = context.window_manager.oops_schematic
        row = layout.row()
        row.prop(s, 'show_libraries', icon='LIBRARY_DATA_DIRECT', toggle=True, icon_only=True)
        row.prop(s, 'show_scenes', icon='SCENE_DATA', toggle=True, icon_only=True)
        row.prop(s, 'show_worlds', icon='WORLD_DATA', toggle=True, icon_only=True)
        row = layout.row()
        row.prop(s, 'show_objects', icon='OBJECT_DATA', toggle=True, icon_only=True)
        row.prop(s, 'show_meshes', icon='MESH_DATA', toggle=True, icon_only=True)
        row.prop(s, 'show_cameras', icon='CAMERA_DATA', toggle=True, icon_only=True)
        row.prop(s, 'show_lamps', icon='LAMP_DATA', toggle=True, icon_only=True)
        row = layout.row()
        row.prop(s, 'show_materials', icon='MATERIAL_DATA', toggle=True, icon_only=True)
        row.prop(s, 'show_textures', icon='TEXTURE_DATA', toggle=True, icon_only=True)
        row.prop(s, 'show_images', icon='IMAGE_DATA', toggle=True, icon_only=True)


class OopsSchematicNodesColorsPanel(OopsSchematicBasePanel):
    bl_idname = "NODE_PT_oops_schematic_nodes_colors"
    bl_label = "Nodes Colors"

    def draw(self, context):
        layout = self.layout
        s = context.window_manager.oops_schematic
        layout.prop(s, 'color_blend_file_nodes')
        layout.prop(s, 'color_libraries_nodes')
        layout.prop(s, 'color_scenes_nodes')
        layout.prop(s, 'color_worlds_nodes')
        layout.prop(s, 'color_objects_nodes')
        layout.prop(s, 'color_meshes_nodes')
        layout.prop(s, 'color_cameras_nodes')
        layout.prop(s, 'color_lamps_nodes')
        layout.prop(s, 'color_materials_nodes')
        layout.prop(s, 'color_textures_nodes')
        layout.prop(s, 'color_images_nodes')
