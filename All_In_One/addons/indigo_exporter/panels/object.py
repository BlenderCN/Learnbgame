import bpy
import bl_ui

from .. core import BL_IDNAME


class IndigoUIObjectSettings(bpy.types.Panel):
    bl_idname = "view3d.indigo_ui_object_settings"
    bl_label = "Indigo Object Settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == BL_IDNAME and context.object.type in ('MESH', 'CURVE')
    
    def draw(self, context):
        #if context.object.data.camera is not None:
        indigo_mesh = context.object.data.indigo_mesh
        layout = self.layout
        col = layout.column()
        
        col.prop(indigo_mesh, 'section_plane')
        col.prop(indigo_mesh, 'cull_geometry')
        col.prop(indigo_mesh, 'sphere_primitive')
        col.prop(indigo_mesh, 'disable_smoothing')
        col.prop(indigo_mesh, 'exit_portal')
        col.prop(indigo_mesh, 'invisible_to_camera')
        col.prop(indigo_mesh, 'max_num_subdivisions')
        if indigo_mesh.max_num_subdivisions > 0:
            row = col.row()
            row.prop(indigo_mesh, 'subdivision_smoothing')
            row.prop(indigo_mesh, 'merge_verts')
            col.prop(indigo_mesh, 'view_dependent_subdivision')
            col.prop(indigo_mesh, 'subdivide_pixel_threshold')
            col.prop(indigo_mesh, 'subdivide_curvature_threshold')
            col.prop(indigo_mesh, 'displacement_error_threshold')
        col.prop(indigo_mesh, 'mesh_proxy')
        if indigo_mesh.mesh_proxy:
            col.prop(indigo_mesh, 'mesh_path')