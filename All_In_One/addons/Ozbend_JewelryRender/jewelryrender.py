# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_JewelryRender


import json
import os
import bpy
import math


class JewelryRender:

    objname = ''    # Name of current imported obj file
    obj = []    # list of current obj meshes
    turn = 1
    cameras_1turn = []    # current working cameras list for 1 turn
    cameras_2turn = []    # current working cameras list for 1 turn

    @staticmethod
    def processobjlist(context):
        # process obj list
        __class__.clear()
        if JewelryRenderOptions.objlist:
            __class__.objname = JewelryRenderOptions.objlist.pop()
            __class__.importobj(context, __class__.objname)
            if __class__.obj:
                __class__.setmeterialstoobj(context)
                __class__.transformobj(context)
                # 1 turn (with gravi)
                __class__.cameras_1turn = JewelryRenderOptions.cameraslist.copy()
                # 2 turn (without gravi)
                if __class__.getgravimesh():
                    __class__.cameras_2turn = JewelryRenderOptions.cameraslist.copy()
                else:
                    print('Warning - no gravi mesh found', bpy.data.objects.keys())
                __class__.render(context)
            else:
                print('Error - no meshes in obj ')
                __class__.processobjlist(context)  # process next obj
        else:
            __class__.clear()
            print('-- FINISHED --')


    @staticmethod
    def importobj(context, filename):
        # import current obj
        bpy.ops.object.select_all(action='DESELECT')
        rez = bpy.ops.import_scene.obj(filepath=JewelryRenderOptions.options['source_obj_dir'] + os.sep + filename, use_smooth_groups=False, use_split_groups=True)
        if rez == {'FINISHED'}:
            __class__.obj = context.selected_objects
        else:
            print('Error importing ', filename)
            __class__.processobjlist(context)   # process next obj


    @staticmethod
    def setmeterialstoobj(context):
        # set materials to current obj
        if __class__.obj:
            for mesh in __class__.obj:
                # materialid = mesh.data.materials[0].name[:JewelryRenderOptions.materialidlength]  # by obj material name
                materialid = mesh.name[:JewelryRenderOptions.materialidlength]  # by obj mesh name
                if materialid == JewelryRenderOptions.options['gravi_mesh_name']:   # gravi mesh (name = 'GraviMet01')
                    materialid = mesh.name[JewelryRenderOptions.materialidlength:][:JewelryRenderOptions.materialidlength]
                for material in JewelryRenderOptions.materialslist:     # all other meshes
                    if material.name[:JewelryRenderOptions.materialidlength] == materialid:
                        if mesh.data.materials:
                            mesh.data.materials[0] = material
                        else:
                            mesh.data.materials.append(material)

    @staticmethod
    def transformobj(context):
        # scale
        bpy.ops.transform.resize(value=(JewelryRenderOptions.options['correction']['scale']['X'],
                                        JewelryRenderOptions.options['correction']['scale']['Y'],
                                        JewelryRenderOptions.options['correction']['scale']['Z']),
                                 constraint_orientation='LOCAL')
        # translate
        bpy.ops.transform.translate(value=(JewelryRenderOptions.options['correction']['translate']['X'],
                                           JewelryRenderOptions.options['correction']['translate']['Y'],
                                           JewelryRenderOptions.options['correction']['translate']['Z']),
                                    constraint_orientation='LOCAL')
        # rotate
        bpy.ops.transform.rotate(value=JewelryRenderOptions.options['correction']['rotate']['X']*math.pi/180,
                                 axis=(1, 0, 0),
                                 constraint_orientation='LOCAL')
        bpy.ops.transform.rotate(value=JewelryRenderOptions.options['correction']['rotate']['Y']*math.pi/180,
                                 axis=(0, 1, 0),
                                 constraint_orientation='LOCAL')
        bpy.ops.transform.rotate(value=JewelryRenderOptions.options['correction']['rotate']['Z']*math.pi/180,
                                 axis=(0, 0, 1),
                                 constraint_orientation='LOCAL')
    @staticmethod
    def getgravimesh():
        gravimesh = [gravi for gravi in bpy.data.objects.keys() if JewelryRenderOptions.options['gravi_mesh_name'] in gravi]
        if gravimesh:
            return bpy.data.objects[sorted(gravimesh, reverse=True)[0]]
        else:
            return None

    @staticmethod
    def setgravi():
        gravimesh = __class__.getgravimesh()
        if gravimesh:
            # # v1 - remove the whole mesh
            # bpy.data.objects.remove(gravimesh, True)
            # for ob in __class__.obj:
            #     if JewelryRenderOptions.options['gravi_mesh_name'] in ob.name:
            #         __class__.obj.remove(ob)

            # v2 - change material - set material with texture
            # if gravimesh.data.materials:
            #     gravimesh.data.materials[0] = bpy.data.materials[JewelryRenderOptions.options['gravimat']]
            # else:
            #     gravimesh.data.materials.append(bpy.data.materials[JewelryRenderOptions.options['gravimat']])

            # if exists copy with gravi_name - use it, else create and use it
            if gravimesh.data.materials and gravimesh.data.materials[0].use_fake_user:
                matname_gravi = 'gravi_'+gravimesh.data.materials[0].name[:JewelryRenderOptions.materialidlength]
                if matname_gravi not in bpy.data.materials.keys():
                    mat_gravi = gravimesh.data.materials[0].copy()
                    mat_gravi.name = matname_gravi
                    input = mat_gravi.node_tree.nodes['Gravi_Mix'].inputs['Fac']
                    output = mat_gravi.node_tree.nodes['Gravi_Text'].outputs['Alpha']
                    mat_gravi.node_tree.links.new(output, input)
                gravimesh.data.materials[0] = bpy.data.materials[matname_gravi]
                # change texture for gravi mesh
                # load texture mask
                texturename = os.path.splitext(__class__.objname)[0] + '.png'
                bpy.data.images.load(os.path.join(JewelryRenderOptions.options['source_obj_dir'], texturename), check_existing=True)
                # set texture mask to gravi-mesh node tree and create links
                gravimesh.data.materials[0].node_tree.nodes['Gravi_Text'].image = bpy.data.images[texturename]
        else:
            print('Error - no gravi mesh found to remove', bpy.data.objects.keys())

    @staticmethod
    def selectobj():
        if __class__.obj:
            for ob in __class__.obj:
                ob.select = True

    @staticmethod
    def moveobjtorendered(objname):
        # move processed obj-file to archive directory
        if os.path.exists(JewelryRenderOptions.options['rendered_obj_dir']):
            clearname = os.path.splitext(objname)[0]
            if os.path.exists(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.obj')):
                os.rename(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.obj'), os.path.join(JewelryRenderOptions.options['rendered_obj_dir'], clearname + '.obj'))
            if os.path.exists(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.mtl')):
                os.rename(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.mtl'), os.path.join(JewelryRenderOptions.options['rendered_obj_dir'], clearname + '.mtl'))
            if os.path.exists(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.png')):
                os.rename(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.png'), os.path.join(JewelryRenderOptions.options['rendered_obj_dir'], clearname + '.png'))
        else:
            print('Error - rendered obj directory not exists')

    @staticmethod
    def removeobj():
        # remove obj meshes from scene
        if __class__.obj:
            for ob in __class__.obj:
                bpy.data.objects.remove(ob, True)

    @staticmethod
    def render(context):
        # statrt render by cameras
        if __class__.cameras_1turn:
            context.scene.camera = __class__.cameras_1turn.pop()
            if __class__.onrenderfinished not in bpy.app.handlers.render_complete:
                bpy.app.handlers.render_complete.append(__class__.onrenderfinished)
            if __class__.onrendercancel not in bpy.app.handlers.render_cancel:
                bpy.app.handlers.render_cancel.append(__class__.onrendercancel)
            if __class__.onsceneupdate not in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate)
        elif __class__.cameras_2turn:
            __class__.setgravi()
            __class__.turn = 2
            context.scene.camera = __class__.cameras_2turn.pop()
            if __class__.onrenderfinished not in bpy.app.handlers.render_complete:
                bpy.app.handlers.render_complete.append(__class__.onrenderfinished)
            if __class__.onrendercancel not in bpy.app.handlers.render_cancel:
                bpy.app.handlers.render_cancel.append(__class__.onrendercancel)
            if __class__.onsceneupdate not in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate)
        else:
            # 2 turns done - move files
            if __class__.objname:
                __class__.moveobjtorendered(__class__.objname)
            # and process next obj
            __class__.processobjlist(context)

    @staticmethod
    def clear():
        __class__.objname = ''
        if __class__.obj:
            __class__.removeobj()
        __class__.obj = []
        __class__.turn = 1
        __class__.cameras_1turn = []
        __class__.cameras_2turn = []
        if __class__.onrenderfinished in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(__class__.onrenderfinished)
        if __class__.onrendercancel in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(__class__.onrendercancel)
        if __class__.onsceneupdate in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate)
        if __class__.onsceneupdate_saverender in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate_saverender)

    @staticmethod
    def onsceneupdate(scene):
        # start next render
        if __class__.onsceneupdate in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate)
        status = bpy.ops.render.render('INVOKE_DEFAULT')
        if status == {'CANCELLED'}:
            if __class__.onsceneupdate not in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate)

    @staticmethod
    def onsceneupdate_saverender(scene):
        # save render rezult on scene update
        if __class__.onsceneupdate_saverender in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate_saverender)
        __class__.saverenderrezult(scene.camera)
        # and start next render
        __class__.render(bpy.context)

    @staticmethod
    def onrenderfinished(scene):
        # save render rezult on scene update
        if __class__.onsceneupdate_saverender not in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate_saverender)

    @staticmethod
    def onrendercancel(scene):
        __class__.clear()
        print('-- ABORTED BY USER --')

    @staticmethod
    def saverenderrezult(camera):
        if os.path.exists(JewelryRenderOptions.options['dest_dir']):
            path = JewelryRenderOptions.options['dest_dir'] + os.sep + os.path.splitext(__class__.objname)[0]   # dir + filename
            for mesh in __class__.obj:
                if JewelryRenderOptions.options['gravi_mesh_name'] not in mesh.name:
                    path += '_' + mesh.data.materials[0].name[:JewelryRenderOptions.materialidlength]   # + mat
            path += '_' + camera.name     # + camera
            if __class__.turn == 1:
                path += '_noeng'
            path += '.jpg'
            for currentarea in bpy.context.window_manager.windows[0].screen.areas:
                if currentarea.type == 'IMAGE_EDITOR':
                    overridearea = bpy.context.copy()
                    overridearea['area'] = currentarea
                    bpy.ops.image.save_as(overridearea, copy=True, filepath=path)
                    break
        else:
            print('Error - no destination directory')


class JewelryRenderOptions:

    options = None
    objlist = []    # list of filenames
    cameraslist = []
    materialslist = []
    materialidlength = 5    # identifier length (ex: MET01, GOL01)

    @staticmethod
    def readfromfile(dir):
        with open(dir + os.sep + 'options.json') as currentFile:
            __class__.options = json.load(currentFile)
