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

class OBJECT_OT_LOD0(bpy.types.Operator):
    """Set selected objs as LOD0. It creates an additional ATLAS Map"""
    bl_idname = "lod0.creation"
    bl_label = "LOD0"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected_objs = bpy.context.selected_objects
        for obj in bpy.context.selected_objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()
            baseobj = obj.name
            if not baseobj.endswith('LOD0'):
                obj.name = baseobj + '_LOD0'
            if len(obj.data.uv_layers) > 1:
                if obj.data.uv_layers[0].name =='MultiTex' and obj.data.uv_layers[1].name =='Atlas':
                    pass
            else:
                create_double_UV(obj)
        return {'FINISHED'}

#_____________________________________________________________________________

def ratio_for_current_lod(lod,context):
    if lod == 1:
        ratio = context.scene.LOD1_dec_ratio
    if lod == 2:
        ratio = context.scene.LOD2_dec_ratio
    if lod == 3:
        ratio = context.scene.LOD3_dec_ratio
    return ratio

def tex_res_for_current_lod(lod,context):
    if lod == 1:
        tex_res = context.scene.LOD1_tex_res
    if lod == 2:
        tex_res = context.scene.LOD2_tex_res
    if lod == 3:
        tex_res = context.scene.LOD3_tex_res
    return tex_res

class OBJECT_OT_LOD(bpy.types.Operator):
    """Creates the desired LODs and export them as obj(s) in LOD(x) subfolders"""
    bl_idname = "lod.creation"
    bl_label = "LOD"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        start_time = time.time()
        context = bpy.context
        selected_objects = context.selected_objects
        ob_tot = len(selected_objects)
        LODnum = context.scene.LODnum
        i_lodbake_counter = 1

        basedir = os.path.dirname(bpy.data.filepath)
        if not basedir:
            raise Exception("Save the blend file")
        # si prende il numero di LOD impostato e i parametri base per LOD ovvero tex_res e decimation_ratio
        # iniziamo con un contatore i_lodbake_counter che parte da 0
        
        print("Number of LOD(s) to be created is: " + str(LODnum))

        # si producono ciclicamente i livelli di dettaglio ad esaurire i LOD richiesti dall'utente nell'UI (normalmente da 1 a 3 LOD)
        while i_lodbake_counter <= LODnum:
            currentLOD = 'LOD' + str(i_lodbake_counter)
            subfolder = currentLOD
            
            if not os.path.exists(os.path.join(basedir, subfolder)):
                os.mkdir(os.path.join(basedir, subfolder))
                print('There is no '+ subfolder +' folder. Creating one...')
            else:
                print('Found previously created '+ subfolder +' folder. I will use it')

            ob_counter = 1
            
            print('<<<<<<<<<<<<<< CREATION OF '+ currentLOD +' >>>>>>>>>>>>>>')
            print('>>>>>> '+str(ob_tot)+' objects will be processed')

            for obj_LOD0 in selected_objects:
                
                start_time_ob = time.time()

                print('>>> '+ currentLOD + ' >>>')
                print('>>>>>> processing the object ""'+ obj_LOD0.name+'"" ('+str(ob_counter)+'/'+str(ob_tot)+')')
                bpy.ops.object.select_all(action='DESELECT')
                obj_LOD0.select_set(True)
                context.view_layer.objects.active = obj_LOD0
                obj_LOD0_name = obj_LOD0.name
                if '_LOD0' in obj_LOD0_name:
                    obj_base_name = obj_LOD0_name.replace("_LOD0", "")
                else:
                    obj_base_name = obj_LOD0_name

                print('Creating new LOD'+ str(i_lodbake_counter) +' object..')
                #bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
                bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
                obj_LODnew = context.view_layer.objects.active

                LOD0layerCol = context.view_layer.active_layer_collection
                LOD0Col = bpy.data.collections.get(LOD0layerCol.name)

                if bpy.data.collections.get(currentLOD) is None:
                    currentLODCol = bpy.data.collections.new(currentLOD)
                    currentLODCol.name = currentLOD
                    context.scene.collection.children.link(currentLODCol)
                else:
                    currentLODCol = bpy.data.collections.get(currentLOD)

                # link the object to collection
                currentLODCol.objects.link(obj_LODnew)
                # unlink from previous collection
                LOD0Col.objects.unlink(obj_LODnew)

                bpy.ops.object.select_all(action='DESELECT')
                context.view_layer.objects.active = obj_LODnew
                obj_LODnew.select_set(True)
                obj_LODnew.name = obj_base_name + "_" + currentLOD
                obj_LODnew_name = obj_LODnew.name

                for i in range(0,len(bpy.data.objects[obj_LODnew_name].material_slots)):
                    bpy.ops.object.material_slot_remove()

                if obj_LODnew.data.uv_layers[1] and obj_LODnew.data.uv_layers[1].name =='Atlas':
                    print('Found Atlas UV mapping layer. I will use it.')
                    uv_layers = obj_LODnew.data.uv_layers
                    uv_layers.remove(uv_layers[0])
                else:
                    print('Creating new UV mapping layer.')
                    create_double_UV(obj_LODnew)

                obj_LOD0.data.uv_layers["MultiTex"].active_render = True
                
                # mesh decimation
                decimate_mesh(context,obj_LODnew,ratio_for_current_lod(i_lodbake_counter,context),currentLOD)

                # now the mesh is decimated
                #------------------------------------------------------------------

                print('Creating new texture atlas for ' + currentLOD + '....')
                tex_res = tex_res_for_current_lod(i_lodbake_counter,context)
                tex_LODnew_name = "T_"+ obj_LODnew_name
                tempimage = bpy.data.images.new(name=tex_LODnew_name, width=tex_res, height=tex_res, alpha=False)
                tempimage.filepath_raw = "//"+subfolder+'/'+tex_LODnew_name+".jpg"
                filepathimage = "//"+subfolder+'/'+tex_LODnew_name+".jpg"
                tempimage.file_format = 'JPEG'

                # annotate current cycles render settings to maintain things clean
                #--------------------------------------------------------------

                to_be_restored_render_engine = context.scene.render.engine
                context.scene.render.engine = 'CYCLES'

                context.scene.cycles.bake_type = 'DIFFUSE'
                context.scene.render.bake.use_pass_direct = False
                context.scene.render.bake.use_pass_indirect = False
                context.scene.render.bake.use_pass_color = True
                context.scene.render.bake.use_selected_to_active = True

                to_restore_samples = context.scene.cycles.samples
                context.scene.cycles.samples = 1

                to_restore_bounces = context.scene.cycles.diffuse_bounces
                context.scene.cycles.diffuse_bounces = 1

                # creating a new material
                #--------------------------------------------------------------
                print('Creating custom material for '+ currentLOD +'...')
                bpy.ops.object.select_all(action='DESELECT')
                obj_LODnew.select_set(True)
                context.view_layer.objects.active = obj_LODnew
                mat, texImage, bsdf = create_material_from_image(context,tempimage,obj_LODnew,False)

                # baking textures
                #--------------------------------------------------------------
                print('Passing color data from LOD0 to '+ currentLOD + '...')

                bpy.ops.object.select_all(action='DESELECT')
                obj_LODnew.select_set(True)
                obj_LOD0.select_set(True)
                obj_LOD0_LODnew_selected = context.selected_objects
                context.view_layer.objects.active = obj_LODnew
                bpy.ops.object.bake(type='DIFFUSE')
                tempimage.save()

                # annotate current cycles render settings to maintain things clean
                #-----------------------------------------------------------------
                context.scene.cycles.diffuse_bounces = to_restore_bounces
                context.scene.cycles.samples = to_restore_samples
                context.scene.render.engine = to_be_restored_render_engine
                mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
                obj_LODnew.data.name = 'SM_' + obj_LODnew.name

                # Saving on obj/mtl file for currentLOD
                #-----------------------------------------------------------------
                print('Saving on obj/mtl file for '+ currentLOD +'...')
                activename = bpy.path.clean_name(obj_LODnew.name)
                fn = os.path.join(basedir, subfolder, activename)
                bpy.ops.export_scene.obj(filepath=fn + ".obj", use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')
                
                print('>>> "'+obj_LODnew.name+'" ('+str(ob_counter)+'/'+ str(ob_tot) +') object baked in '+str(time.time() - start_time_ob)+' seconds')
                ob_counter += 1

            i_lodbake_counter += 1
        end_time = time.time() - start_time
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(ob_tot)+' objects processed in '+str(end_time)+' seconds')
        return {'FINISHED'}

#_______________________________________________________________________________________________

class OBJECT_OT_ExportGroupsLOD(bpy.types.Operator):
    """LOD cluster(s) export to FBX"""
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
        listobjects = context.selected_objects
        for obj in listobjects:
            if obj.type == 'EMPTY':
                if obj.get('fbx_type') is not None:
                    print('Found LOD cluster to export: "'+obj.name+'", object')
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj
                    for ob in getChildren(obj):
                        ob.select_set(True)
                    name = bpy.path.clean_name(obj.name)
                    fn = os.path.join(basedir, name)
                    bpy.ops.export_scene.fbx(filepath= fn + ".fbx", check_existing=True, axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", ui_tab='MAIN', use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}, use_mesh_modifiers=True, mesh_smooth_type='EDGE', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='RELATIVE', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
                else:
                    print('The "' + obj.name + '" empty object has not the correct settings to export an FBX - LOD enabled file. I will skip it.')
                    obj.select_set(False)
                    print('>>> Object number '+str(ob_counter)+' processed in '+str(time.time() - start_time)+' seconds')
                    ob_counter += 1

        end_time = time.time() - start_time
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(ob_counter)+' objects processed in '+str(end_time)+' seconds')

        return {'FINISHED'}

#_______________________________________________________________



class OBJECT_OT_RemoveGroupsLOD(bpy.types.Operator):
    """Removes LOD cluster(s)"""
    bl_idname = "remove.grouplod"
    bl_label = "Remove Group LOD"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        listobjects = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in listobjects:
            if obj.get('fbx_type') is not None:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                for ob in getChildren(obj):
                    ob.select_set(True)
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.delete()
        return {'FINISHED'}

#_______________________________________________________________


class OBJECT_OT_CreateGroupsLOD(bpy.types.Operator):
    """Creates LOD cluster(s): empty objects with nested LODs"""
    bl_idname = "create.grouplod"
    bl_label = "Create Group LOD"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        listobjects = bpy.context.selected_objects
        for obj in listobjects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            baseobjwithlod = obj.name

            if '_LOD0' in baseobjwithlod:
                baseobj = baseobjwithlod.replace("_LOD0", "")
                print('Found LOD0 object:' + baseobjwithlod)
                local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
                global_bbox_center = obj.matrix_world @ local_bbox_center
                emptyofname = 'GLOD_' + baseobj
                obempty = bpy.data.objects.new( emptyofname, None )
                bpy.context.collection.objects.link(obempty)

                obempty.empty_display_size = 2
                obempty.empty_display_type = 'PLAIN_AXES'
                obempty.location = global_bbox_center
                bpy.ops.object.select_all(action='DESELECT')
                obempty.select_set(True)
                bpy.context.view_layer.objects.active = obempty
                obempty['fbx_type'] = 'LodGroup'

                num = 0
                child = selectLOD(listobjects, num, baseobj)
                print(child)
                print(baseobj)
                print(str(num))
                while child is not None:
                    child.parent = obempty
                    child.matrix_parent_inverse = obempty.matrix_world.inverted()
                    #oldway to do this:
                    #bpy.ops.object.select_all(action='DESELECT')
                    #child.select_set(True)
                    #obempty.select_set(True)
                    #bpy.context.view_layer.objects.active = obempty
                    #bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
                    num += 1
                    print(str(num))
                    child = selectLOD(listobjects, num, baseobj)
        return {'FINISHED'}

