# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_JewelryRender

import bpy
from .jewelryrender import JewelryRender
from .jewelryrender import JewelryRenderOptions
import os

class JewelryRenderStart(bpy.types.Operator):
    bl_idname = 'jewelryrender.start'
    bl_label = 'Start JewelryRender'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # load options
        if bpy.data.filepath:
            JewelryRenderOptions.readfromfile(os.path.dirname(bpy.data.filepath))
        else:
            print('Options file mast be in the same directory with blend-file')
            return {'CANCELLED'}
        if JewelryRenderOptions.options:
            context.screen.scene.render.resolution_x = JewelryRenderOptions.options['resolution_x']
            context.screen.scene.render.resolution_y = JewelryRenderOptions.options['resolution_y']
            context.screen.scene.cycles.samples = JewelryRenderOptions.options['samples']
            # search for *.obj
            if JewelryRenderOptions.options['source_obj_dir'] and os.path.exists(JewelryRenderOptions.options['source_obj_dir']):
                JewelryRenderOptions.objlist = [file for file in os.listdir(JewelryRenderOptions.options['source_obj_dir']) if file.endswith(".obj")]
            # serch for cameras
            JewelryRenderOptions.cameraslist = [object for object in context.screen.scene.objects if object.type=='CAMERA']
            # search for materials
            JewelryRenderOptions.materialslist = [material for material in bpy.data.materials if material.use_fake_user]
            # start processing obj by list
            print('-- STARTED --')
            JewelryRender.processobjlist(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(JewelryRenderStart)


def unregister():
    bpy.utils.unregister_class(JewelryRenderStart)
