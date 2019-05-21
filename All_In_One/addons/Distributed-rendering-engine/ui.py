import bpy
from dre.operators import *
import os


class configPanel(bpy.types.Panel):
    bl_idname = "panel_config"
    bl_label = "Configurations"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    bpy.types.Scene.mode = EnumProperty(
                    items=(
                            ("RENDER_MASTER", "Master", "Act as render master"),
                            ("RENDER_SLAVE", "Slave", "Act as render slave"),
                        ),
                    name="Network mode",
                    description="Mode of operation of this Machine",
                    default="RENDER_MASTER")


    def draw(self, context):
        layout=self.layout

        layout.prop(context.scene,"mode",expand=True)

        if context.scene.mode == 'RENDER_MASTER':
            # mode Master is selected
            layout.prop(context.scene.MasterConfigs,"path")
            col=layout.column()
            if GlobalData.MasterServiceThread!=None:
                col.enabled=False
            col.prop(context.scene.MasterConfigs,"self_address")
            col.prop(context.scene.MasterConfigs,"port_no")
            if GlobalData.MasterServiceThread==None:
                layout.operator("action.start_service",icon='PLAY')
            else:
                layout.operator("action.stop_service",icon='X')
            layout.operator('action.print_registered_slaves')
            layout.operator('action.stop_data_receiving_service')
        else:
            # mode slave is selected
            col=layout.column()
            if GlobalData.Slave_isRegistered==True:
                col.enabled=False
            col.prop(context.scene.SlaveConfigs,'self_address')
            col.prop(context.scene.SlaveConfigs,"path")
            col.prop(context.scene.SlaveConfigs,"master_address")
            col.prop(context.scene.SlaveConfigs,"port_no")
            if GlobalData.Slave_isRegistered==False:
                layout.operator('action.register_with_master')
            else:
                layout.operator('action.unregister_with_master')
        
class renderPanel(bpy.types.Panel):
    bl_idname = "panel_render"
    bl_label = "Render"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def poll(self,context):
        # create panel only if mode is 'RENDER_MASTER'
        if context.scene.mode == 'RENDER_MASTER':
            return True

    def draw(self, context):
        layout=self.layout
        scene=context.scene

        row = layout.row()
        row.operator("render.render", text="Render", icon='RENDER_STILL')

        row=layout.row()
        column=row.column()
        column.prop(scene.render, "resolution_x", text="X")
        column.prop(scene.render, "resolution_y", text="Y")
        column.prop(scene.render,"resolution_percentage",text="")

        column=row.column()
        column.prop(scene,'frame_start')
        column.prop(scene, "frame_end")







