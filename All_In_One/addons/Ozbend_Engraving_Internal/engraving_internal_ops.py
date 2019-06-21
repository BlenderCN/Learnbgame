# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_Engraving_Internal

import bpy
from .engraving_internal import EngravingInternal
from .engraving_internal import EngravingInternalOptions
import os
import sys
import argparse

class EngravingInternalStart(bpy.types.Operator):
    bl_idname = 'engravinginternal.start'
    bl_label = 'Start EngravingInternal'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # load options
        if bpy.data.filepath:
            EngravingInternalOptions.readfromfile(os.path.dirname(bpy.data.filepath))
            # correct options with command line arguments
            if '--' in sys.argv:
                argv = sys.argv[sys.argv.index('--') + 1:]  # all args after '--'
                parser = argparse.ArgumentParser()
                parser.add_argument('-sx', '--size_x', dest='size_x', type=int, required=False, help='Image X resolution')
                parser.add_argument('-sy', '--size_y', dest='size_y', type=int, required=False, help='Image Y resolution')
                parser.add_argument('-s', '--scale', dest='scale', type=float, required=False, help='Mesh scale')
                parser.add_argument('-sa', '--samples', dest='samples', type=int, required=False, help='Render samples')
                parser.add_argument('-p', '--path', dest='path', metavar='FILE', required=False, help='Dest path')
                parser.add_argument('-n', '--name', dest='name', type=str, required=False, help='Dest name')
                parser.add_argument('-g', '--gravi', dest='gravi', metavar='FILE', required=False, help='Gravi path')
                parser.add_argument('-o', '--obj_dir', dest='obj_dir', metavar='FILE', required=False, help='Obj custom path')
                parser.add_argument('-c', '--cameras_nums', dest='cameras_nums', type=str, required=False, help='Cameras list')
                parser.add_argument('-e', '--render_engine', dest='render_engine', type=str, required=False, help='Render engine')
                args = parser.parse_known_args(argv)[0]
                if EngravingInternalOptions.options:
                    if args.size_x is not None:
                        EngravingInternalOptions.options['resolution_x'] = args.size_x
                    if args.size_y is not None:
                        EngravingInternalOptions.options['resolution_y'] = args.size_y
                    if args.scale is not None:
                        EngravingInternalOptions.options['correction']['scale']['X'] = args.scale
                        EngravingInternalOptions.options['correction']['scale']['Y'] = args.scale
                        EngravingInternalOptions.options['correction']['scale']['Z'] = args.scale
                    if args.samples is not None:
                        EngravingInternalOptions.options['samples'] = args.samples
                    if args.path is not None:
                        EngravingInternalOptions.options['dest_dir'] = args.path
                    if args.name is not None:
                        EngravingInternalOptions.const_dest_name = args.name
                    if args.gravi is not None:
                        EngravingInternalOptions.const_gravi_name = args.gravi
                    if args.obj_dir is not None:
                        EngravingInternalOptions.options['source_obj_dir'] = args.obj_dir
                    if args.cameras_nums is not None:
                        EngravingInternalOptions.options['cameras'] = list(map(int, args.cameras_nums.split('-')))
                    if args.render_engine is not None:
                        EngravingInternalOptions.options['engine'] = args.render_engine
                EngravingInternalOptions.command_line_render = True
        else:
            print('Options file mast be in the same directory with blend-file')
            return {'CANCELLED'}
        if EngravingInternalOptions.options:
            context.screen.scene.render.resolution_x = EngravingInternalOptions.options['resolution_x']
            context.screen.scene.render.resolution_y = EngravingInternalOptions.options['resolution_y']
            context.screen.scene.cycles.samples = EngravingInternalOptions.options['samples']
            # search for *.obj
            obj_dir = EngravingInternalOptions.options['source_obj_dir']
            if obj_dir and os.path.exists(obj_dir):
                EngravingInternalOptions.objlist = [file for file in os.listdir(obj_dir) if file.endswith('.obj')]
            # serch for cameras
            if EngravingInternalOptions.options['cameras']:
                # from options.json or command line
                EngravingInternalOptions.cameraslist = [obj for obj in context.screen.scene.objects if obj.type == 'CAMERA' and int(obj.name[-2:]) in EngravingInternalOptions.options['cameras']]
            else:
                # no selection - all cameras from scene
                EngravingInternalOptions.cameraslist = [obj for obj in context.screen.scene.objects if obj.type == 'CAMERA']
            # search for materials
            EngravingInternalOptions.materialslist = [material for material in bpy.data.materials if material.use_fake_user]
            EngravingInternalOptions.materialslist_gem = [material for material in EngravingInternalOptions.materialslist if material.name[:EngravingInternalOptions.materialidtextlength] == EngravingInternalOptions.materialgemid]
            EngravingInternalOptions.materialslist_met = [material for material in EngravingInternalOptions.materialslist if material.name[:EngravingInternalOptions.materialidtextlength] == EngravingInternalOptions.materialmetid]
            # set required engine
            if EngravingInternalOptions.options['engine'] == 'internal':
                context.scene.render.engine = 'BLENDER_RENDER'
            elif EngravingInternalOptions.options['engine'] == 'cycles':
                context.scene.render.engine = 'CYCLES'
            if context.scene.render.engine == 'BLENDER_RENDER':
                EngravingInternalOptions.materialgraviname = 'Gravi_internal'
                EngravingInternalOptions.materialtransparentname = 'Trans_internal'
            elif context.scene.render.engine == 'CYCLES':
                EngravingInternalOptions.materialgraviname = 'Gravi_cycles'
                EngravingInternalOptions.materialtransparentname = 'Trans_cycles'
            else:
                print('-- Error: Unsupported render engine --')
                return {'CANCELLED'}
            # start processing obj by list
            print('-- STARTED --')
            print('RENDER IN: ', context.scene.render.engine)
            EngravingInternal.processobjlist(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(EngravingInternalStart)


def unregister():
    bpy.utils.unregister_class(EngravingInternalStart)
