import bpy

from .. core import BL_IDNAME

class IndigoLightLayers(bpy.types.Panel):
    bl_idname = "view3d.indigo_light_layers"
    bl_label = "Indigo Light Layers"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == BL_IDNAME
    
    def draw(self, context):
        indigo_engine = context.scene.indigo_engine
        
        self.layout.label("Default Layer:")
        box = self.layout.box()
        row = box.row()
        lg = context.scene.indigo_lightlayers
        sub = box.column(align=True)
        sub.prop(lg, 'default_SP_type')
        if lg.default_SP_type == 'rgb':
            sub = box.row()
            spl = sub.split(0.25, align=True)
            spl.prop(lg, 'default_SP_rgb', text="")
            spl.prop(lg, 'default_SP_rgb_gain')
        elif lg.default_SP_type == 'blackbody':
            box.separator()
            sub = box.column(align=True)
            sub.prop(lg, 'default_blackbody_temp')
            sub.prop(lg, 'default_blackbody_gain')
        elif lg.default_SP_type == 'xyz':
            box.separator()
            box.row().prop(lg, 'default_SP_xyz', text="")
            box.prop(lg, 'default_SP_xyz_gain')
        
        
        col = self.layout.column()
        col.prop(context.scene.indigo_lightlayers, 'ignore')
        col.separator()
        col.operator('indigo.lightlayer_add', icon="ZOOMIN")
        
        for lg_index in range(len(context.scene.indigo_lightlayers.lightlayers)):
            lg = context.scene.indigo_lightlayers.lightlayers[lg_index]
            box = self.layout.box()
            row = box.row(True)
            
            row.prop(lg, 'lg_enabled')
            row.prop(lg, 'name')
            
            row.operator('indigo.lightlayer_remove', text="", icon="ZOOMOUT").lg_index=lg_index
            
            sub = box.column(align=True)
            sub.prop(lg, 'lightlayer_SP_type')
            if lg.lightlayer_SP_type == 'rgb':
                sub = box.row()
                spl = sub.split(0.25, align=True)
                spl.prop(lg, 'lightlayer_SP_rgb', text="")
                spl.prop(lg, 'lightlayer_SP_rgb_gain')
            elif lg.lightlayer_SP_type == 'blackbody':
                sub = box.column(align=True)
                sub.prop(lg, 'lightlayer_blackbody_temp')
                sub.prop(lg, 'lightlayer_blackbody_gain')
            elif lg.lightlayer_SP_type == 'xyz':
                box.row().prop(lg, 'lightlayer_SP_xyz', text="")
                box.prop(lg, 'lightlayer_SP_xyz_gain')