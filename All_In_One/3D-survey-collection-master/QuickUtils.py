import bpy
import time
import bmesh
from random import randint, choice
from .functions import *
from .qualitycheck import *

class OBJECT_OT_CorrectMaterial(bpy.types.Operator):
    bl_idname = "correct.material"
    bl_label = "Correct photogr. mats"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            obj.select_set(True)
            for i in range(0,len(obj.material_slots)):
#                bpy.ops.object.material_slot_remove()
                obj.active_material_index = i
                ma = obj.active_material
                ma.diffuse_intensity = 1
                ma.specular_intensity = 0
                ma.specular_color[0] = 1
                ma.specular_color[1] = 1         
                ma.specular_color[2] = 1  
                ma.diffuse_color[0] = 1
                ma.diffuse_color[1] = 1         
                ma.diffuse_color[2] = 1       
                ma.alpha = 1.0
                ma.use_transparency = False
                ma.transparency_method = 'Z_TRANSPARENCY'
                ma.use_transparent_shadows = True
                ma.ambient = 0.0
                image = ma.texture_slots[0].texture.image
                image.use_alpha = False
        return {'FINISHED'}

class OBJECT_OT_projectsegmentation(bpy.types.Operator):
    """Project segmentation"""
    bl_idname = "project.segmentation"
    bl_label = "Project segmentation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context = bpy.context
        start_time = time.time()
        ob_counter = 1
        
        data = bpy.data
        ob_cutting = context.scene.objects.active
        #ob_cutting = data.objects.get("secante")
        ob_to_cut = context.selected_objects
        ob_tot = (len(ob_to_cut)-1)
        bpy.ops.object.select_all(action='DESELECT')
        for ob in ob_to_cut:
            if ob == ob_cutting:
                pass
            else:
                start_time_ob = time.time()
                print('>>> CUTTING >>>')
                print('>>>>>> the object is going to be cutted: ""'+ ob.name+'"" ('+str(ob_counter)+'/'+str(ob_tot)+')')
                ob_cutting.select = True
                context.scene.objects.active = ob
                ob.select = True
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.knife_project(cut_through=True)
                try:
                    bpy.ops.mesh.separate(type='SELECTED')
                except:
                    pass
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.editmode_toggle()
                print('>>> "'+ob.name+'" ('+str(ob_counter)+'/'+ str(ob_tot) +') object cutted in '+str(time.time() - start_time_ob)+' seconds')
                ob_counter += 1
                bpy.ops.object.select_all(action='DESELECT')
        end_time = time.time() - start_time
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(ob_tot)+' objects processed in '+str(end_time)+' seconds')
        return {'FINISHED'}

class OBJECT_OT_projectsegmentationinversed(bpy.types.Operator):
    """Project segmentation inverse"""
    bl_idname = "project.segmentationinv"
    bl_label = "Project segmentation inverse"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context = bpy.context
        start_time = time.time()
        ob_counter = 1
        data = bpy.data
        ob_to_cut = context.scene.objects.active
        #ob_cutting = data.objects.get("secante")
        ob_cutting = context.selected_objects
        ob_tot = (len(ob_cutting)-1)
        bpy.ops.object.select_all(action='DESELECT')
        
        for ob in ob_cutting:
            if ob == ob_to_cut:
                pass
            else:
                start_time_ob = time.time()
                print('>>> CUTTING >>>')
                print('>>>>>> the object "'+ ob.name +'" ('+str(ob_counter)+'/'+str(ob_tot)+') is cutting the object'+ ob_to_cut.name)
                ob.select = True
                context.scene.objects.active = ob_to_cut
                ob_to_cut.select = True
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.knife_project(cut_through=True)
                try:
                    bpy.ops.mesh.separate(type='SELECTED')
                except:
                    pass
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.editmode_toggle()
                print('>>> "'+ob.name+'" ('+str(ob_counter)+'/'+ str(ob_tot) +') object used to cut in '+str(time.time() - start_time_ob)+' seconds')
                ob_counter += 1
                bpy.ops.object.select_all(action='DESELECT')
        end_time = time.time() - start_time
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(ob_tot)+' objects processed in '+str(end_time)+' seconds')
        return {'FINISHED'}

class OBJECT_OT_renameGEobject(bpy.types.Operator):
    """Rename data tree of selected objects using the object name"""
    bl_idname = "rename.ge"
    bl_label = "Rename data tree of selected objects using the object name (usefull for GE export)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context = bpy.context
        scene = context.scene

        for ob in context.selected_objects:
            ob.data.name = "ME_"+ob.name
            if ob.material_slots:
                mslot_index = 0
                tslot_index = 0
                for m_slot in ob.material_slots:
                    if m_slot.material:
                        mslot_index += 1
                        if m_slot.material.users == 1:
                            m_slot.material.name = "M_"+str(mslot_index)+"_"+ob.name
                        else:
                            m_slot.material.name = "M_"+str(mslot_index)+"_"+ob.name
                        if m_slot.material.texture_slots:
                            if(len(m_slot.material.texture_slots) > 0):
                                tslot_index += 1
                                m_tex = m_slot.material.texture_slots[0]
                                m_tex.texture.name = "T_"+str(tslot_index)+"_"+ob.name
                                m_tex.texture.image.name = "img_"+str(mslot_index)+"_"+ob.name
        return {'FINISHED'}
    
class OBJECT_OT_objectnamefromfilename(bpy.types.Operator):
    """Set active object name from file name"""
    bl_idname = "obname.ffn"
    bl_label = "Set active object name from file name"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objname = bpy.path.basename(bpy.context.blend_data.filepath)
        sel = bpy.context.active_object
        sel.name = objname.split(".")[0]
        return {'FINISHED'}


class OBJECT_OT_qualitycheck(bpy.types.Operator):
    """Quality check"""
    bl_idname = "quality.check"
    bl_label = "Report on quality of 3d models (install the UVtools addon)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        get_texel_density(self, context)
        return {'FINISHED'}


class OBJECT_OT_tiff2pngrelink(bpy.types.Operator):
    """relink tiff images to png"""
    bl_idname = "tiff2png.relink"
    bl_label = "Relink tiff images to png"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        images = bpy.data.images

        def changetiff(img):
            if img.filepath.endswith("tif"):
                img.filepath = img.filepath.replace(".tif", ".png")
                img.reload()
            if img.name.endswith("tif"):
                img.name = img.name.replace(".tif", ".png")
            
        for img in images:
            changetiff(img)
            
        return {'FINISHED'}


class OBJECT_OT_lightoff(bpy.types.Operator):
    """Turn off light sensibility"""
    bl_idname = "light.off"
    bl_label = "Turn off light sensibility"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.game_settings.material_mode = 'GLSL'
        bpy.context.scene.game_settings.use_glsl_lights = False
        return {'FINISHED'}

class OBJECT_OT_LOD0polyreducer(bpy.types.Operator):
    """Reduce the polygon number to a correct LOD0 set up"""
    bl_idname = "lod0poly.reducer"
    bl_label = "Reduce the polygon number to a correct LOD0 set up"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context = bpy.context

        selected_objs = context.selected_objects

        for obj in selected_objs:
            me = obj.data
            tot_poly = len(me.polygons)
            tot_area = areamesh(obj)
            final_poly = tot_area*1000
            if final_poly < tot_poly:
                ratio = final_poly/tot_poly
                print("ratio is "+ str(ratio))
                decimate_mesh(context,obj,ratio,'LOD0')

        return {'FINISHED'}

class OBJECT_OT_cycles2bi(bpy.types.Operator):
    """Convert cycles to bi"""
    bl_idname = "cycles2bi.material"
    bl_label = "Convert cycles to bi"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        cycles2bi()

        return {'FINISHED'}



#________________________________________________________

class OBJECT_OT_deactivatematerial(bpy.types.Operator):
    """De-activate node  materials for selected object"""
    bl_idname = "deactivatenode.material"
    bl_label = "De-activate cycles node materials for selected object and switch to BI"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                mat.use_nodes = False

        return {'FINISHED'}
    
#-------------------------------------------------------------

class OBJECT_OT_activatematerial(bpy.types.Operator):
    """Activate node materials for selected object"""
    bl_idname = "activatenode.material"
    bl_label = "Activate cycles node materials for selected object and switch to cycles"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.context.scene.render.engine = 'CYCLES'
        for obj in bpy.context.selected_objects:
            for matslot in obj.material_slots:
                mat = matslot.material
                mat.use_nodes = True

        return {'FINISHED'}


class OBJECT_OT_CenterMass(bpy.types.Operator):
    bl_idname = "center.mass"
    bl_label = "Center Mass"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        selection = bpy.context.selected_objects
#        bpy.ops.object.select_all(action='DESELECT')

        # translate objects in SCS coordinate
        for obj in selection:
            obj.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
        return {'FINISHED'}

class OBJECT_OT_LocalTexture(bpy.types.Operator):
    bl_idname = "local.texture"
    bl_label = "Local texture mode ON"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.file.autopack_toggle()
        bpy.ops.file.autopack_toggle()
        bpy.ops.file.unpack_all(method='WRITE_LOCAL')
        bpy.ops.file.make_paths_relative()
        return {'FINISHED'}


class OBJECT_OT_createpersonalgroups(bpy.types.Operator):
    bl_idname = "create.personalgroups"
    bl_label = "Create groups per single object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
            make_group(ob,context)
        return {'FINISHED'}


class OBJECT_OT_removealluvexcept1(bpy.types.Operator):
    bl_idname = "remove.alluvexcept1"
    bl_label = "Remove all the UVs except the first one"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            if ob.data.uv_layers[1]:
                uv_layers = ob.data.uv_layers
                uv_layers.remove(uv_layers[1])
        return {'FINISHED'}

class OBJECT_OT_removefromallgroups(bpy.types.Operator):
    bl_idname = "remove.fromallgroups"
    bl_label = "Remove the object(s) from all the Groups"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            bpy.ops.group.objects_remove_all()
        return {'FINISHED'}
    
    
    
class OBJECT_OT_multimateriallayout(bpy.types.Operator):
    """Create multimaterial layout on selected mesh"""
    bl_idname = "multimaterial.layout"
    bl_label = "Create a multimaterial layout for selected meshe(s)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        start_time = time.time()
        totmodels=len(context.selected_objects)
        padding = 0.05
        #ob = bpy.context.object
        print("Found "+str(totmodels)+" models.")
        currentmod = 1
        for ob in context.selected_objects:
            start_time_ob = time.time()
            print("")
            print("***********************")
            print("I'm starting to process: "+ob.name+" model ("+str(currentmod)+"/"+str(totmodels)+")")
            print("***********************")
            print("")
            bpy.ops.object.select_all(action='DESELECT')
            ob.select = True
            bpy.context.scene.objects.active = ob
            currentobjname = ob.name
            objectname = ob.name
            me = ob.data
            tot_poly = len(me.polygons)
            materialnumber = desiredmatnumber(ob) #final number of whished materials
            materialsoriginal=len(ob.material_slots)
            cleaned_obname = clean_name(objectname)
            print("Removing the old "+str(materialsoriginal)+" materials..")

            for i in range(0,materialsoriginal):
                bpy.ops.object.material_slot_remove()
            current_material = 1
            for mat in range(materialnumber-1):
                bpy.ops.object.editmode_toggle()
                print("Selecting polygons for mat: "+str(mat+1)+"/"+str(materialnumber))
                bpy.ops.mesh.select_all(action='DESELECT')
                me.update()
                poly = len(me.polygons)
                bm = bmesh.from_edit_mesh(me)
                for i in range(5):
                    #print(i+1)
                    r = choice([(0,poly)])
                    random_index=(randint(*r))
                    if hasattr(bm.faces, "ensure_lookup_table"):
                        bm.faces.ensure_lookup_table()
                    bm.faces[random_index].select = True
                    bmesh.update_edit_mesh(me, True)
                poly_sel = 5
                while poly_sel <= (tot_poly/materialnumber):
                    bpy.ops.mesh.select_more(use_face_step=True)
                    ob.update_from_editmode()
                    poly_sel = len([p for p in ob.data.polygons if p.select])
                bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.01, user_area_weight=0.0, use_aspect=True)
#                bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=padding)
                bpy.ops.uv.pack_islands(margin=padding)
                print("Creating new textures (remember to save them later..)")
                bpy.ops.object.editmode_toggle()
                current_tex_name = (cleaned_obname+'_t'+str(current_material))
                newimage2selpoly(ob, current_tex_name)
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.editmode_toggle()
                current_material += 1

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(island_margin=padding)
            bpy.ops.uv.pack_islands(margin=padding)
            bpy.ops.object.editmode_toggle()
            current_tex_name = (cleaned_obname+'_t'+str(current_material))
            newimage2selpoly(ob, current_tex_name)
            bpy.ops.object.select_all(action='DESELECT')
            ob.select = True
            bpy.context.scene.objects.active = ob
            currentobjname = ob.name

            for mat in range(materialnumber-1):

                bpy.data.objects[getnextobjname(currentobjname)].select = True
                nextname = getnextobjname(currentobjname)
                currentobjname = nextname

            bpy.ops.object.join()
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.object.editmode_toggle()
            #bpy.ops.view3d.texface_to_material()
            print('>>> "'+ob.name+'" ('+str(currentmod)+'/'+ str(totmodels) +') object baked in '+str(time.time() - start_time_ob)+' seconds')
            currentmod += 1
        end_time = time.time() - start_time
        print(' ')
        print('<<<<<<< Process done >>>>>>')
        print('>>>'+str(totmodels)+' objects processed in '+str(end_time)+' seconds')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>')       
        return {'FINISHED'}
