import bpy
import os
import time
from .functions import *
from mathutils import Vector

def selectLOD(listobjects, lodnum, basename):
    name2search = basename + '_LOD' + str(lodnum)
    for ob in listobjects:
        if ob.name == name2search:
            objatgivenlod = ob
            return objatgivenlod
        else:
            objatgivenlod = None
    return objatgivenlod

def getChildren(myObject):
    children = []
    for ob in bpy.data.objects:
        if ob.parent == myObject:
            children.append(ob)
    return children

class ToolsPanel2(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "3DSC"
    bl_label = "LOD generator"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        if obj:
            row.label(text="Override name:")
            row = layout.row()
            row.prop(obj, "name", text='')
            row = layout.row()
        row.label(text="Actions on selected objects:")
        row = layout.row()
        self.layout.operator("lod0.b2osg", icon="MESH_UVSPHERE", text='LOD 0 (set as)')
        row = layout.row()
        row.label(text="Start always selecting LOD0 objs")
        self.layout.operator("lod1.b2osg", icon="MESH_ICOSPHERE", text='LOD 1 (creation)')
        self.layout.operator("lod2.b2osg", icon="MESH_CUBE", text='LOD 2 (creation)')
        self.layout.operator("bake.b2osg", icon="RADIO", text='just bake')

        row = layout.row()
        if obj:
            row.label(text="Resulting files: ")
            row = layout.row()
            row.label(text= "LOD1/LOD2_"+ obj.name + ".obj" )
            row = layout.row()
        self.layout.operator("create.grouplod", icon="OOPS", text='Create LOD cluster(s)')
        row = layout.row()
        self.layout.operator("remove.grouplod", icon="CANCEL", text='Remove LOD cluster(s)')
        row = layout.row()
        self.layout.operator("exportfbx.grouplod", icon="MESH_GRID", text='FBX Export LOD cluster(s)')
        row = layout.row()

class OBJECT_OT_LOD0(bpy.types.Operator):
    bl_idname = "lod0.b2osg"
    bl_label = "LOD0"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected_objs = bpy.context.selected_objects
        for obj in bpy.context.selected_objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            bpy.ops.object.shade_smooth()
            baseobj = obj.name
            if not baseobj.endswith('LOD0'):
                obj.name = baseobj + '_LOD0'
            if len(obj.data.uv_layers) > 1:
                if obj.data.uv_textures[0].name =='MultiTex' and obj.data.uv_textures[1].name =='Atlas':
                    pass
            else:
                mesh = obj.data
                mesh.uv_textures.active_index = 0
                multitex_uvmap = mesh.uv_textures.active
                multitex_uvmap_name = multitex_uvmap.name
                multitex_uvmap.name = 'MultiTex'
                atlas_uvmap = mesh.uv_textures.new()
                atlas_uvmap.name = 'Atlas'
                mesh.uv_textures.active_index = 1
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles()
                bpy.ops.uv.select_all(action='SELECT')
                bpy.ops.uv.pack_islands(margin=0.001)
                bpy.ops.object.editmode_toggle()
                mesh.uv_textures.active_index = 0

        return {'FINISHED'}

#_____________________________________________________________________________

class OBJECT_OT_BAKE(bpy.types.Operator):
    bl_idname = "bake.b2osg"
    bl_label = "bake"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context = bpy.context
        start_time = time.time()
        basedir = os.path.dirname(bpy.data.filepath)
        subfolder = 'BAKE'
        if not os.path.exists(os.path.join(basedir, subfolder)):
            os.mkdir(os.path.join(basedir, subfolder))
            print('There is no BAKE folder. Creating one...')
        else:
            print('Found previously created BAKE folder. I will use it')
        if not basedir:
            raise Exception("Save the blend file")

        ob_counter = 1
        ob_tot = len(bpy.context.selected_objects)
        print('<<<<<<<<<<<<<< CREATION OF BAKE >>>>>>>>>>>>>>')
        print('>>>>>> '+str(ob_tot)+' objects will be processed')

        for obj in bpy.context.selected_objects:
            obj.data.uv_textures["MultiTex"].active_render = True
            start_time_ob = time.time()
            print('>>> BAKE >>>')
            print('>>>>>> processing the object ""'+ obj.name+'"" ('+str(ob_counter)+'/'+str(ob_tot)+')')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            baseobjwithlod = obj.name
            if '_LOD0' in baseobjwithlod:
                baseobj = baseobjwithlod.replace("_LOD0", "")
            else:
                baseobj = baseobjwithlod
            print('Creating new BAKE object..')
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

            for obj in bpy.context.selected_objects:
                obj.name = baseobj + "_BAKE"
                newobj = obj
            for obj in bpy.context.selected_objects:
                lod1name = obj.name
            for i in range(0,len(bpy.data.objects[lod1name].material_slots)):
                bpy.ops.object.material_slot_remove()

            if obj.data.uv_textures[1] and obj.data.uv_textures[1].name =='Atlas':
                print('Found Atlas UV mapping layer. I will use it.')
                uv_textures = obj.data.uv_textures
                uv_textures = obj.data.uv_textures
                uv_textures.remove(uv_textures[0])
            else:
                print('Creating new UV mapping layer.')
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles()
                bpy.ops.uv.select_all(action='SELECT')
                bpy.ops.uv.pack_islands(margin=0.001)
                bpy.ops.object.editmode_toggle()

#            decimate_mesh(context,obj,0.5,'BAKE')


    # procedura di semplificazione mesh

    # ora mesh semplificata
    #------------------------------------------------------------------


            bpy.ops.object.select_all(action='DESELECT')
            oggetto = bpy.data.objects[lod1name]
            oggetto.select = True
            print('Creating new texture atlas for BAKE....')

            tempimage = bpy.data.images.new(name=lod1name, width=2048, height=2048, alpha=False)
            tempimage.filepath_raw = "//"+subfolder+'/'+lod1name+".jpg"
            tempimage.file_format = 'JPEG'

            for uv_face in oggetto.data.uv_textures.active.data:
                uv_face.image = tempimage

            #--------------------------------------------------------------
            print('Passing color data from original to BAKE...')
            bpy.context.scene.render.engine = 'BLENDER_RENDER'
            bpy.context.scene.render.use_bake_selected_to_active = True
            bpy.context.scene.render.bake_type = 'TEXTURE'

            object = bpy.data.objects[baseobjwithlod]
            object.select = True

            bpy.context.scene.objects.active = bpy.data.objects[lod1name]
            #--------------------------------------------------------------

            bpy.ops.object.bake_image()
            tempimage.save()

            print('Creating custom material for BAKE...')
            bpy.ops.object.select_all(action='DESELECT')
            oggetto = bpy.data.objects[lod1name]
            oggetto.select = True
            bpy.context.scene.objects.active = oggetto
            bpy.ops.view3d.texface_to_material()
            oggetto.active_material.name = 'M_'+ oggetto.name
            oggetto.data.name = 'SM_' + oggetto.name
    #        basedir = os.path.dirname(bpy.data.filepath)

            print('Saving on obj/mtl file for BAKE...')
            activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
            fn = os.path.join(basedir, subfolder, activename)
            bpy.ops.export_scene.obj(filepath=fn + ".obj", use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')

            bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False))
            print('>>> "'+obj.name+'" ('+str(ob_counter)+'/'+ str(ob_tot) +') object baked in '+str(time.time() - start_time_ob)+' seconds')
            ob_counter += 1

        bpy.context.scene.layers[11] = True
        bpy.context.scene.layers[0] = False
        end_time = time.time() - start_time
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(ob_tot)+' objects processed in '+str(end_time)+' seconds')
        return {'FINISHED'}

        return {'FINISHED'}


#_____________________________________________________________________________



class OBJECT_OT_LOD1(bpy.types.Operator):
    bl_idname = "lod1.b2osg"
    bl_label = "LOD1"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context = bpy.context
        start_time = time.time()
        basedir = os.path.dirname(bpy.data.filepath)
        subfolder = 'LOD1'
        if not os.path.exists(os.path.join(basedir, subfolder)):
            os.mkdir(os.path.join(basedir, subfolder))
            print('There is no LOD1 folder. Creating one...')
        else:
            print('Found previously created LOD1 folder. I will use it')
        if not basedir:
            raise Exception("Save the blend file")

        ob_counter = 1
        ob_tot = len(bpy.context.selected_objects)
        print('<<<<<<<<<<<<<< CREATION OF LOD 1 >>>>>>>>>>>>>>')
        print('>>>>>> '+str(ob_tot)+' objects will be processed')

        for obj in bpy.context.selected_objects:
            obj.data.uv_textures["MultiTex"].active_render = True
            start_time_ob = time.time()
            print('>>> LOD 1 >>>')
            print('>>>>>> processing the object ""'+ obj.name+'"" ('+str(ob_counter)+'/'+str(ob_tot)+')')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            baseobjwithlod = obj.name
            if '_LOD0' in baseobjwithlod:
                baseobj = baseobjwithlod.replace("_LOD0", "")
            else:
                baseobj = baseobjwithlod
            print('Creating new LOD1 object..')
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

            for obj in bpy.context.selected_objects:
                obj.name = baseobj + "_LOD1"
                newobj = obj
            for obj in bpy.context.selected_objects:
                lod1name = obj.name
            for i in range(0,len(bpy.data.objects[lod1name].material_slots)):
                bpy.ops.object.material_slot_remove()

            if obj.data.uv_textures[1] and obj.data.uv_textures[1].name =='Atlas':
                print('Found Atlas UV mapping layer. I will use it.')
                uv_textures = obj.data.uv_textures
                uv_textures = obj.data.uv_textures
                uv_textures.remove(uv_textures[0])
            else:
                print('Creating new UV mapping layer.')
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles()
                bpy.ops.uv.select_all(action='SELECT')
                bpy.ops.uv.pack_islands(margin=0.001)
                bpy.ops.object.editmode_toggle()

            decimate_mesh(context,obj,0.5,'LOD1')


    # procedura di semplificazione mesh

    # ora mesh semplificata
    #------------------------------------------------------------------


            bpy.ops.object.select_all(action='DESELECT')
            oggetto = bpy.data.objects[lod1name]
            oggetto.select = True
            print('Creating new texture atlas for LOD1....')

            tempimage = bpy.data.images.new(name=lod1name, width=4096, height=4096, alpha=False)
            tempimage.filepath_raw = "//"+subfolder+'/'+lod1name+".jpg"
            tempimage.file_format = 'JPEG'

            for uv_face in oggetto.data.uv_textures.active.data:
                uv_face.image = tempimage

            #--------------------------------------------------------------
            print('Passing color data from LOD0 to LOD1...')
            bpy.context.scene.render.engine = 'BLENDER_RENDER'
            bpy.context.scene.render.use_bake_selected_to_active = True
            bpy.context.scene.render.bake_type = 'TEXTURE'

            object = bpy.data.objects[baseobjwithlod]
            object.select = True

            bpy.context.scene.objects.active = bpy.data.objects[lod1name]
            #--------------------------------------------------------------

            bpy.ops.object.bake_image()
            tempimage.save()

            print('Creating custom material for LOD1...')
            bpy.ops.object.select_all(action='DESELECT')
            oggetto = bpy.data.objects[lod1name]
            oggetto.select = True
            bpy.context.scene.objects.active = oggetto
            bpy.ops.view3d.texface_to_material()
            oggetto.active_material.name = 'M_'+ oggetto.name
            oggetto.data.name = 'SM_' + oggetto.name
    #        basedir = os.path.dirname(bpy.data.filepath)

            print('Saving on obj/mtl file for LOD1...')
            activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
            fn = os.path.join(basedir, subfolder, activename)
            bpy.ops.export_scene.obj(filepath=fn + ".obj", use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')

            bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False))
            print('>>> "'+obj.name+'" ('+str(ob_counter)+'/'+ str(ob_tot) +') object baked in '+str(time.time() - start_time_ob)+' seconds')
            ob_counter += 1

        bpy.context.scene.layers[11] = True
        bpy.context.scene.layers[0] = False
        end_time = time.time() - start_time
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(ob_tot)+' objects processed in '+str(end_time)+' seconds')
        return {'FINISHED'}


#______________________________________


class OBJECT_OT_LOD2(bpy.types.Operator):
    bl_idname = "lod2.b2osg"
    bl_label = "LOD2"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        start_time = time.time()
        basedir = os.path.dirname(bpy.data.filepath)
        subfolder = 'LOD2'
        if not os.path.exists(os.path.join(basedir, subfolder)):
            os.mkdir(os.path.join(basedir, subfolder))
            print('There is no LOD2 folder. Creating one...')
        else:
            print('Found previously created LOD1 folder. I will use it')
        if not basedir:
            raise Exception("Save the blend file")
        ob_counter = 1
        ob_tot = len(bpy.context.selected_objects)
        print('<<<<<<<<<<<<<< CREATION OF LOD 2 >>>>>>>>>>>>>>')
        print('>>>>>> '+str(ob_tot)+' objects will be processed')

        for obj in bpy.context.selected_objects:
            obj.data.uv_textures["MultiTex"].active_render = True
            print('>>> LOD 2 >>>')
            print('>>>>>> processing the object ""'+ obj.name+'"" ('+str(ob_counter)+'/'+str(ob_tot)+')')
            start_time_ob = time.time()

            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            baseobjwithlod = obj.name
            if '_LOD0' in baseobjwithlod:
                baseobj = baseobjwithlod.replace("_LOD0", "")
            else:
                baseobj = baseobjwithlod
            print('Creating new LOD2 object..')
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

            for obj in bpy.context.selected_objects:
                obj.name = baseobj + "_LOD2"
                newobj = obj
            for obj in bpy.context.selected_objects:
                lod2name = obj.name

            for i in range(0,len(bpy.data.objects[lod2name].material_slots)):
                bpy.ops.object.material_slot_remove()

# se abbiamo precedente atlas, inutile rifarlo
            if obj.data.uv_textures[1] and obj.data.uv_textures[1].name =='Atlas':
                print('Found Atlas UV mapping layer. I will use it.')
                uv_textures = obj.data.uv_textures
                uv_textures.remove(uv_textures[0])

            else:
                print('Creating new UV mapping layer.')
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles()
                bpy.ops.uv.select_all(action='SELECT')
                bpy.ops.uv.pack_islands(margin=0.001)
                bpy.ops.object.editmode_toggle()

            # procedura di semplificazione mesh

            print('Decimating the original mesh to obtain the LOD2 mesh...')
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.object.vertex_group_add()
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.editmode_toggle()
            bpy.data.objects[lod2name].modifiers.new("Decimate", type='DECIMATE')
            obj.modifiers["Decimate"].ratio = 0.1
            obj.modifiers["Decimate"].vertex_group = "Group"
            obj.modifiers["Decimate"].invert_vertex_group = True
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
            # ora mesh semplificata
            #------------------------------------------------------------------
            bpy.ops.object.select_all(action='DESELECT')
            oggetto = bpy.data.objects[lod2name]
            oggetto.select = True
            print('Creating new texture atlas for LOD2....')

            tempimage = bpy.data.images.new(name=lod2name, width=512, height=512, alpha=False)
            tempimage.filepath_raw = "//"+subfolder+'/'+lod2name+".jpg"
            tempimage.file_format = 'JPEG'

            for uv_face in oggetto.data.uv_textures.active.data:
                uv_face.image = tempimage

            #--------------------------------------------------------------
            print('Passing color data from LOD0 to LOD2...')
            bpy.context.scene.render.engine = 'BLENDER_RENDER'
            bpy.context.scene.render.use_bake_selected_to_active = True
            bpy.context.scene.render.bake_type = 'TEXTURE'

            object = bpy.data.objects[baseobjwithlod]
            object.select = True

            bpy.context.scene.objects.active = bpy.data.objects[lod2name]
            #--------------------------------------------------------------

            bpy.ops.object.bake_image()
            tempimage.save()

            print('Creating custom material for LOD2...')

            bpy.ops.object.select_all(action='DESELECT')
            oggetto = bpy.data.objects[lod2name]
            oggetto.select = True

            bpy.context.scene.objects.active = oggetto
            bpy.ops.view3d.texface_to_material()

            oggetto.active_material.name = 'M_'+ oggetto.name
            oggetto.data.name = 'SM_' + oggetto.name

            print('Saving on obj/mtl file for LOD2...')
            activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
            fn = os.path.join(basedir, subfolder, activename)
            bpy.ops.export_scene.obj(filepath=fn + ".obj", use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')

            bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False))
            print('>>> "'+obj.name+'" ('+str(ob_counter)+'/'+ str(ob_tot) +') object baked in '+str(time.time() - start_time_ob)+' seconds')
            ob_counter += 1

        bpy.context.scene.layers[10] = True
        bpy.context.scene.layers[0] = False
        end_time = time.time() - start_time
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(ob_tot)+' objects processed in '+str(end_time)+' seconds')
        return {'FINISHED'}


#_______________________________________________________________

class OBJECT_OT_ExportGroupsLOD(bpy.types.Operator):
    bl_idname = "exportfbx.grouplod"
    bl_label = "Export Group LOD"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        start_time = time.time()
        basedir = os.path.dirname(bpy.data.filepath)
        if not basedir:
            raise Exception("Blend file is not saved")
        ob_counter = 1
        scene = context.scene
        listobjects = bpy.context.selected_objects
        for obj in listobjects:
            if obj.type == 'EMPTY':
                if obj.get('fbx_type') is not None:
                    print('Found LOD cluster to export: "'+obj.name+'", object')
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select = True
                    bpy.context.scene.objects.active = obj
                    for ob in getChildren(obj):
                        ob.select = True
                    name = bpy.path.clean_name(obj.name)
                    fn = os.path.join(basedir, name)
                    bpy.ops.export_scene.fbx(filepath= fn + ".fbx", check_existing=True, axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", version='BIN7400', ui_tab='MAIN', use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LAMP', 'MESH', 'OTHER'}, use_mesh_modifiers=True, mesh_smooth_type='EDGE', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True, use_anim_action_all=True, use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='RELATIVE', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
                else:
                    print('The "' + obj.name + '" empty object has not the correct settings to export an FBX - LOD enabled file. I will skip it.')
                    obj.select = False
                    print('>>> Object number '+str(ob_counter)+' processed in '+str(time.time() - start_time)+' seconds')
                    ob_counter += 1

        end_time = time.time() - start_time
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(ob_counter)+' objects processed in '+str(end_time)+' seconds')

        return {'FINISHED'}

#_______________________________________________________________



class OBJECT_OT_RemoveGroupsLOD(bpy.types.Operator):
    bl_idname = "remove.grouplod"
    bl_label = "Remove Group LOD"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        listobjects = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in listobjects:
            if obj.get('fbx_type') is not None:
                obj.select = True
                bpy.context.scene.objects.active = obj
                for ob in getChildren(obj):
                    ob.select = True
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                bpy.ops.object.select_all(action='DESELECT')
                obj.select = True
                bpy.context.scene.objects.active = obj
                bpy.ops.object.delete()
        return {'FINISHED'}

#_______________________________________________________________


class OBJECT_OT_CreateGroupsLOD(bpy.types.Operator):
    bl_idname = "create.grouplod"
    bl_label = "Create Group LOD"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        listobjects = bpy.context.selected_objects
        for obj in listobjects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            baseobjwithlod = obj.name

            if '_LOD0' in baseobjwithlod:
                baseobj = baseobjwithlod.replace("_LOD0", "")
                print('Found LOD0 object:' + baseobjwithlod)
                local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
                global_bbox_center = obj.matrix_world * local_bbox_center
                emptyofname = 'GLOD_' + baseobj
                obempty = bpy.data.objects.new( emptyofname, None )
                bpy.context.scene.objects.link( obempty )
                obempty.empty_draw_size = 2
                obempty.empty_draw_type = 'PLAIN_AXES'
                obempty.location = global_bbox_center
                bpy.ops.object.select_all(action='DESELECT')
                obempty.select = True
                bpy.context.scene.objects.active = obempty
                obempty['fbx_type'] = 'LodGroup'
#                bpy.ops.wm.properties_edit(data_path="object", property="Fbx_Type", value="LodGroup", min=0, max=1, use_soft_limits=False, soft_min=0, soft_max=1, description="")

                num = 0
                child = selectLOD(listobjects, num, baseobj)
                while child is not None:
                    bpy.ops.object.select_all(action='DESELECT')
                    child.select = True
                    obempty.select = True
                    bpy.context.scene.objects.active = obempty
                    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
#                    child.parent= obempty
#                    child.location.x = child.location.x - obempty.location.x
#                    child.location.y = child.location.y - obempty.location.y
                    num += 1
                    child = selectLOD(listobjects, num, baseobj)
        return {'FINISHED'}
