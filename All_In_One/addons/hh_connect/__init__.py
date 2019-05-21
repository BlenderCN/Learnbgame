#Xolotl Studio
#Created by Ymmanuel Flores on 2018
#Copyright 2018 Crowdorchestra SAPI de CV. All rights reserved.
#hhconnect v 1.0.0.4

bl_info = {
    "name": "Hedgehog Connect",
    "author": "Ymmanuel Who",
    "version": (1, 0, 0, 5),
    "blender": (2, 80, 0),
    "category": "Learnbgame",
}

import hh_connect.utils.hh_painter as hhpainter
import bpy
import os

class HHConnectSettings(bpy.types.PropertyGroup):

    active: bpy.props.BoolProperty(
        name="Listen connections",
        description="Enable/Disable Hedgehog Connect service",
        default = False
    )

    time: bpy.props.FloatProperty(
        name="Interval",
        description="Set the listening time interval (seconds) for the Hedgehog Connect service",
        default = 0.1
    )


class HHPresetsTimerOperator(bpy.types.Operator):

    bl_idname = "wm.hhconnect_timer_operator"
    bl_label = "Start Listening"

    _timer = None

    script_file = os.path.realpath(__file__)
    directory = os.path.dirname(script_file)
    filename = os.path.join(directory,"command.txt")

    def readCommand(self):
        if os.path.isfile( self.filename):
            print("Substance Painter Live Link: Command file found")
            with open(self.filename,'r') as file:
                for line in file:
                    line=line.rstrip("\n")
                    cmd = line.split(',')
                    if cmd[0] == 'hh_sp_link':
                        print("Substance Painter Live Link: Command create material received")
                        hhpainter.addMaterial(cmd[1],cmd[2],cmd[3],cmd[4],cmd[5])
            os.remove(self.filename)


    def modal(self, context, event):
        scene = context.scene
        hh_settings = scene.hh_settings

        if hh_settings.active == True:
            if event.type == 'TIMER':
                self.readCommand()
        else:
            if os.path.isfile( self.filename):
                os.remove( self.filename )
            self.cancel(context)
            print("Substance Painter Live Link: Service stopped")
            return {'CANCELLED'}
        return {'PASS_THROUGH'}


    def execute(self, context):
        scene = context.scene
        hh_settings = scene.hh_settings
        hh_settings.active = not hh_settings.active

        if (2,80,0) == bpy.app.version:
            render = bpy.context.scene.render.engine
            if render == 'BLENDER_RENDER' or render == 'BLENDER_GAME' or render == 'BLENDER_CLAY':
                bpy.context.scene.render.engine = 'CYCLES'
        else:
            render = bpy.context.scene.render.engine
            if render == 'BLENDER_RENDER' or render == 'BLENDER_GAME' or render == 'BLENDER_CLAY':
                bpy.context.scene.view_render.engine = 'CYCLES'

        wm = context.window_manager
        self._timer = wm.event_timer_add(hh_settings.time, window=context.window)
        wm.modal_handler_add(self)
        print("Substance Painter Live Link: Service started")

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

class HHDelMatsOps(bpy.types.Operator):
    bl_idname = "hhops.del_mats"
    bl_label = "Remove Materials"
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        for material in bpy.data.materials:
            if not material.users:
                bpy.data.materials.remove(material)
        return {'FINISHED'}

class HHDelTxtsOps(bpy.types.Operator):
    bl_idname = "hhops.del_txts"
    bl_label = "Remove Textures"
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        for image in bpy.data.images:
            if not image.users:
                bpy.data.images.remove(image)
        return {'FINISHED'}

class HHDelAllOps(bpy.types.Operator):
    bl_idname = "hhops.del_all"
    bl_label = "Remove Unused"
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        for material in bpy.data.materials:
            if not material.users:
                bpy.data.materials.remove(material)

        for image in bpy.data.images:
            if not image.users:
                bpy.data.images.remove(image)
        return {'FINISHED'}


class HHPanel(bpy.types.Panel):

    bl_label = "Hedgehog Connect"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "View"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        hh_settings = scene.hh_settings

        lbl = "Start listening"
        if hh_settings.active:
            lbl = "Stop listening"
        layout.operator("wm.hhconnect_timer_operator",text=lbl)
        layout.prop(hh_settings, "time")
        layout.operator("hhops.del_mats",text="Del Unused Mats")
        layout.operator("hhops.del_txts",text="Del Unused Txts")
        layout.operator("hhops.del_all",text="Del Unused")

classes = (
    HHPanel,
    HHDelAllOps,
    HHDelTxtsOps,
    HHDelMatsOps,
    HHConnectSettings,
    HHPresetsTimerOperator
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.hh_settings = bpy.props.PointerProperty(type=HHConnectSettings)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.hh_settings


if __name__ == "__main__":
    register()
