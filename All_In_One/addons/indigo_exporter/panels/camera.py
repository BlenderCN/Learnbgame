import bpy
import bl_ui

from .. core import BL_IDNAME


class IndigoUICamera(bpy.types.Panel):
    bl_idname = "view3d.indigo_ui_camera"
    bl_label = "Indigo Camera"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == BL_IDNAME and context.object.type == 'CAMERA'
    
    def draw(self, context):
        #if context.object.data.camera is not None:
        indigo_camera = context.object.data.indigo_camera
        layout = self.layout
        #col = layout.column()
        
        row = layout.row()
        row.prop(indigo_camera, 'autofocus')
        row.prop(indigo_camera, 'vignetting')
        
        row = layout.row()
        row.prop(indigo_camera, 'autoexposure')
        if not indigo_camera.autoexposure:
            row.prop(indigo_camera, 'exposure')
            
        row = layout.row(align=True)
        row.prop(indigo_camera, 'iso')
        row.prop(indigo_camera, 'fstop')
        
        col = layout.column()
        col.prop(indigo_camera, 'whitebalance')
        if indigo_camera.whitebalance == 'Custom':
            row = layout.row(align=True)
            row.prop(indigo_camera, 'whitebalanceX', slider=True)
            row.prop(indigo_camera, 'whitebalanceY', slider=True)
            
        col = layout.column()
        row = col.row()
        row.prop(indigo_camera, 'ad')
        if indigo_camera.ad:
            row.prop(indigo_camera, 'ad_post')
            col.prop(indigo_camera, 'ad_obstacle')
            col.prop(indigo_camera, 'ad_type')
            if indigo_camera.ad_type == 'image':
                col.prop(indigo_camera, 'ad_image')
            elif indigo_camera.ad_type == 'generated':
                row = col.row(align=True)
                row.prop(indigo_camera, 'ad_blades')
                row.prop(indigo_camera, 'ad_offset')
                
                row = col.row(align=True)
                row.prop(indigo_camera, 'ad_curvature')
                row.prop(indigo_camera, 'ad_angle')
            
            
            
class IndigoUITonemapping(bpy.types.Panel):
    bl_idname = "view3d.indigo_ui_tonemapping"
    bl_label = "Indigo Tonemapping"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == BL_IDNAME and context.object.type == 'CAMERA'
    
    def draw(self, context):
        #if context.object.data.camera is not None:
        indigo_tonemapping = context.object.data.indigo_tonemapping
        layout = self.layout
        #col = layout.column()
        
        row = layout.row()
        row.prop(indigo_tonemapping, 'tonemap_type')
        
        if indigo_tonemapping.tonemap_type == 'linear':
            row = layout.row(align=True)
            row.prop(indigo_tonemapping, 'linear_unit')
            row.prop(indigo_tonemapping, 'linear_exp')
        elif indigo_tonemapping.tonemap_type == 'reinhard':
            row = layout.row(align=True)
            row.prop(indigo_tonemapping, 'reinhard_pre')
            row.prop(indigo_tonemapping, 'reinhard_post')
            row.prop(indigo_tonemapping, 'reinhard_burn')
        elif indigo_tonemapping.tonemap_type == 'camera':
            col = layout.column()
            col.label("Camera Tonemapping Settings")
            row = col.row(align=True)
            row.prop(indigo_tonemapping, 'camera_response_type', expand=True)
            if indigo_tonemapping.camera_response_type == 'preset':
                col.prop(indigo_tonemapping, 'camera_response_preset')
            if indigo_tonemapping.camera_response_type == 'file':
                col.prop(indigo_tonemapping, 'camera_response_file')
            col.prop(indigo_tonemapping, 'camera_ev')
        elif indigo_tonemapping.tonemap_type == 'filmic':
            row = layout.row(align=True)
            row.prop(indigo_tonemapping, 'filmic_scale')