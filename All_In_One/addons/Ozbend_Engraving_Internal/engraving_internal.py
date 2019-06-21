# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_Engraving_Internal


import json
import os
import bpy
import math


class EngravingInternal:

    objname = ''        # Name of current imported obj file
    obj = []            # list of current obj meshes
    objd_m = []         # list of current obj meshes with dynamic metals
    objd_g = []         # list of current obj meshes with dynamic gems
    gravi = []          # gravi meshes list
    nongravi = []       # meshes without gravi list
    mode = 'NOGRAVI'    # NOGRAVI, GRAVI
    variants = []       # render variants for current obj

    @staticmethod
    def processobjlist(context):
        # process next obj in list
        __class__.clear()
        if EngravingInternalOptions.objlist:
            __class__.objname = EngravingInternalOptions.objlist.pop()
            __class__.importobj(context, __class__.objname)
            if __class__.obj:
                __class__.transformobj(context)
                __class__.setstablematerialstoobj(context)
                __class__.makerendervariants()
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
        source_obj_path = EngravingInternalOptions.options['source_obj_dir']
        rez = bpy.ops.import_scene.obj(filepath=os.path.join(source_obj_path, filename), use_smooth_groups=False, use_split_groups=True)
        if rez == {'FINISHED'}:
            __class__.obj = context.selected_objects
            __class__.gravi = __class__.getgravimesh()
            __class__.nongravi = __class__.getnongravimesh()
            for mesh in __class__.obj:
                if int(mesh.name[EngravingInternalOptions.materialidtextlength:EngravingInternalOptions.materialidlength]) == 0:
                    if mesh.name[:EngravingInternalOptions.materialidtextlength] == EngravingInternalOptions.materialmetid:
                        __class__.objd_m.append(mesh)
                    elif mesh.name[:EngravingInternalOptions.materialidtextlength] == EngravingInternalOptions.materialgemid:
                        __class__.objd_g.append(mesh)
        else:
            print('Error importing ', os.path.join(source_obj_path, filename))
            __class__.processobjlist(context)   # process next obj


    @staticmethod
    def setstablematerialstoobj(context):
        # set stable materials to current obj
        if __class__.nongravi:
            for mesh in __class__.nongravi:
                # set transparent to all non gravi meshes
                __class__.setmaterialtomesh(mesh, bpy.data.materials[EngravingInternalOptions.materialtransparentname])

    @staticmethod
    def transformobj(context):
        # scale
        bpy.ops.transform.resize(value=(EngravingInternalOptions.options['correction']['scale']['X'],
                                        EngravingInternalOptions.options['correction']['scale']['Y'],
                                        EngravingInternalOptions.options['correction']['scale']['Z']),
                                 constraint_orientation='LOCAL')
        # translate
        bpy.ops.transform.translate(value=(EngravingInternalOptions.options['correction']['translate']['X'],
                                           EngravingInternalOptions.options['correction']['translate']['Y'],
                                           EngravingInternalOptions.options['correction']['translate']['Z']),
                                    constraint_orientation='LOCAL')
        # rotate
        bpy.ops.transform.rotate(value=EngravingInternalOptions.options['correction']['rotate']['X']*math.pi/180,
                                 axis=(1, 0, 0),
                                 constraint_orientation='LOCAL')
        bpy.ops.transform.rotate(value=EngravingInternalOptions.options['correction']['rotate']['Y']*math.pi/180,
                                 axis=(0, 1, 0),
                                 constraint_orientation='LOCAL')
        bpy.ops.transform.rotate(value=EngravingInternalOptions.options['correction']['rotate']['Z']*math.pi/180,
                                 axis=(0, 0, 1),
                                 constraint_orientation='LOCAL')
    @staticmethod
    def makerendervariants():
        # create a list with all variants for current obj to render
        # format: [camera1 => [mesh1 => current_mat, mesh2 => current_mat...] 'GRAVI', camera2 => ...]
        for camera in EngravingInternalOptions.cameraslist:
            # only 1 variant with cameras, transparent non-gravi meshes and gravi
            newvariant_g = [camera, [], 'GRAVI']
            if __class__.gravi and newvariant_g not in __class__.variants:
                __class__.variants.append(newvariant_g.copy())
        # print('-'*50)
        # for i in __class__.variants:
        #     print(i[0])
        #     for j in i[1]:
        #         print('    ', j[0].name, ' => ', j[1].name)
        #     print(i[2])
        # print('-'*50)

    @staticmethod
    def setscenevariant(context, variant):
        # set scene by current variant from __class__.variants
        # select camera
        context.scene.camera = variant[0]
        # materials to meshes
        for meshmat in variant[1]:
            __class__.setmaterialtomesh(meshmat[0], meshmat[1])
        # use Gravi or not
        if variant[2] == 'GRAVI':
            __class__.gravion()
            __class__.mode = 'GRAVI'
        else:   # 'NOGRAVI'
            __class__.gravioff()
            __class__.mode = 'NOGRAVI'

    @staticmethod
    def getgravimesh():
        # all meshes with gravi
        return [gravi for gravi in bpy.data.objects if EngravingInternalOptions.options['gravi_mesh_name'] in gravi.name]

    @staticmethod
    def getnongravimesh():
        # all meshes without gravi
        return [obj for obj in bpy.data.objects if EngravingInternalOptions.options['gravi_mesh_name'] not in obj.name and obj.type == 'MESH']

    @staticmethod
    def gravion():
        # on gravi
        if __class__.gravi:
            for gravi in __class__.gravi:
                gravinum = __class__.graviindex(gravi)  # 01 ...
                gravimatname = 'Gravi' + gravinum
                # if not exists - make copy from gravi mesh and on gravi
                if gravimatname not in bpy.data.materials.keys():
                    # create copy from special gravi material
                    gravimat = bpy.data.materials[EngravingInternalOptions.materialgraviname].copy()
                    gravimat.name = gravimatname
                    gravimat.use_fake_user = False
                # load texture mask
                texturename = os.path.splitext(__class__.objname)[0] + gravinum + '.png'
                texturepath = os.path.join(EngravingInternalOptions.options['source_obj_dir'], texturename)
                if EngravingInternalOptions.const_gravi_name and os.path.exists(EngravingInternalOptions.const_gravi_name):
                    # if const_gravi_name (from command line)
                    texturepath = EngravingInternalOptions.const_gravi_name
                    texturename = os.path.basename(EngravingInternalOptions.const_gravi_name)
                if os.path.exists(texturepath):
                    bpy.data.images.load(texturepath, check_existing=True)
                    # bpy.data.images.load(texturepath)
                    # set texture mask to gravi-mesh
                    if EngravingInternalOptions.options['engine'] == 'internal':
                        texture = bpy.data.textures.new(texturename, type='IMAGE')
                        texture.image = bpy.data.images[texturename]
                        bpy.data.materials[gravimatname].texture_slots[0].texture = texture
                    elif EngravingInternalOptions.options['engine'] == 'cycles':
                        bpy.data.materials[gravimatname].node_tree.nodes['Gravi_Text'].image = bpy.data.images[texturename]
                else:
                    print('Error - no texture file with gravi')
                # set mat with on gravi to gravi mesh
                __class__.setmaterialtomesh(gravi, bpy.data.materials[gravimatname])
        else:
            print('Error - no gravi mesh found ', bpy.data.objects.keys())

    @staticmethod
    def gravioff():
        # off gravi
        for gravi in __class__.gravi:
            material = [mat for mat in bpy.data.materials if gravi.data.materials[0].name[:EngravingInternalOptions.materialidlength] in mat.name and mat.use_fake_user]
            if material:
                __class__.setmaterialtomesh(gravi, material[0])

    @staticmethod
    def setmaterialtomesh(mesh, material):
        if mesh and material:
            if mesh.data.materials:
                mesh.data.materials[0] = material
            else:
                mesh.data.materials.append(material)

    @staticmethod
    def selectobj():
        if __class__.obj:
            for ob in __class__.obj:
                ob.select = True

    @staticmethod
    def graviindex(gravi):
        # 01 from Met01Gravi01
        return gravi.name[:12][10:]

    @staticmethod
    def moveobjtorendered(objname):
        # move processed obj-file to archive directory
        if os.path.exists(EngravingInternalOptions.options['rendered_obj_dir']):
            clearname = os.path.splitext(objname)[0]
            if os.path.exists(os.path.join(EngravingInternalOptions.options['source_obj_dir'], clearname + '.obj')):
                if os.path.exists(os.path.join(EngravingInternalOptions.options['rendered_obj_dir'], clearname + '.obj')):
                    os.remove(os.path.join(EngravingInternalOptions.options['rendered_obj_dir'], clearname + '.obj'))
                os.rename(os.path.join(EngravingInternalOptions.options['source_obj_dir'], clearname + '.obj'), os.path.join(EngravingInternalOptions.options['rendered_obj_dir'], clearname + '.obj'))
            if os.path.exists(os.path.join(EngravingInternalOptions.options['source_obj_dir'], clearname + '.mtl')):
                if os.path.exists(os.path.join(EngravingInternalOptions.options['rendered_obj_dir'], clearname + '.mtl')):
                    os.remove(os.path.join(EngravingInternalOptions.options['rendered_obj_dir'], clearname + '.mtl'))
                os.rename(os.path.join(EngravingInternalOptions.options['source_obj_dir'], clearname + '.mtl'), os.path.join(EngravingInternalOptions.options['rendered_obj_dir'], clearname + '.mtl'))
            for gravi in __class__.gravi:
                if os.path.exists(os.path.join(EngravingInternalOptions.options['source_obj_dir'], clearname + __class__.graviindex(gravi) + '.png')):
                    if os.path.exists(os.path.join(EngravingInternalOptions.options['rendered_obj_dir'], clearname + __class__.graviindex(gravi) + '.png')):
                        os.remove(os.path.join(EngravingInternalOptions.options['rendered_obj_dir'], clearname + __class__.graviindex(gravi) + '.png'))
                    os.rename(os.path.join(EngravingInternalOptions.options['source_obj_dir'], clearname + __class__.graviindex(gravi) + '.png'), os.path.join(EngravingInternalOptions.options['rendered_obj_dir'], clearname + __class__.graviindex(gravi) + '.png'))
        else:
            print('Error - rendered obj directory not exists')

    @staticmethod
    def removeobj():
        # remove obj meshes from scene
        if __class__.obj:
            for ob in __class__.obj:
                # ob.name = ob.name + '_rem'  # to prevent error while removing and then importing meshes with the same name
                bpy.data.objects.remove(ob, True)

    @staticmethod
    def render(context):
        # statrt render by variants
        if __class__.variants:
            currentvariant = __class__.variants.pop()
            # set scene to current variant
            __class__.setscenevariant(context, currentvariant)
            # statr render from events
            if __class__.onrenderfinished not in bpy.app.handlers.render_complete:
                bpy.app.handlers.render_complete.append(__class__.onrenderfinished)
            if __class__.onrendercancel not in bpy.app.handlers.render_cancel:
                bpy.app.handlers.render_cancel.append(__class__.onrendercancel)
            if __class__.onsceneupdate not in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate)
        else:
            # done - move obj files to rendered
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
        __class__.objd_m = []
        __class__.objd_g = []
        __class__.gravi = []
        __class__.nongravi = []
        __class__.mode = 'NOGRAVI'
        __class__.variants = []
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
        if os.path.exists(EngravingInternalOptions.options['dest_dir']):
            path = EngravingInternalOptions.options['dest_dir'] + os.sep    # dir
            if EngravingInternalOptions.const_dest_name is not None:        # + filename
                path += EngravingInternalOptions.const_dest_name
            else:
                path += os.path.splitext(__class__.objname)[0]
            # + engraves names
            if __class__.gravi:
                for mesh in sorted(__class__.gravi, reverse=True, key=lambda x: x.name):
                    path += mesh.name
            # + camera
            path += '_' + camera.name     # + camera
            if __class__.mode == 'NOGRAVI':
                path += '_noeng'
            path += '.png'
            if EngravingInternalOptions.command_line_render:
                bpy.data.images['Render Result'].save_render(filepath=path)
            else:
                for currentarea in bpy.context.window_manager.windows[0].screen.areas:
                    if currentarea.type == 'IMAGE_EDITOR':
                        overridearea = bpy.context.copy()
                        overridearea['area'] = currentarea
                        bpy.ops.image.save_as(overridearea, copy=True, filepath=path)
                        break
        else:
            print('Error - no destination directory')


class EngravingInternalOptions:

    options = None
    command_line_render = False # True if render from command line (without gui)
    objlist = []    # list of filenames
    cameraslist = []
    materialslist = []
    materialslist_met = []
    materialslist_gem = []
    materialidlength = 5        # identifier length (ex: MET01, GEM01)
    materialidtextlength = 3    # identifier material length (ex: MET, GEM)
    materialmetid = 'Met'
    materialgemid = 'Gem'
    materialtransparentname = None  # 'Trans_internal' or 'Trans_cycles'
    materialgraviname = None        # 'Gravi_internal' or 'Gravi_cycles'
    const_dest_name = None      # if not None - owerwrites obj name in dest render file name
    const_gravi_name = None     # if not None - owerwrites *.png texture file name (with gravi)

    @staticmethod
    def readfromfile(dir):
        with open(dir + os.sep + 'options.json') as currentFile:
            __class__.options = json.load(currentFile)
