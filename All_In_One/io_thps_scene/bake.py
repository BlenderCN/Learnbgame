#############################################
# AUTO SCENE BAKING TOOLS
#############################################
import bpy
import bmesh
import struct
import mathutils
import math
import os
import numpy
from bpy.props import *
from . helpers import *
from . material import *

from . import prefs
from . prefs import *


# METHODS
#############################################

#----------------------------------------------------------------------------------
#- Returns an inverted/clamped version of the given image - for lightmap bakes
#----------------------------------------------------------------------------------
def invert_image(img, clamp_factor):
    pixels = list(img.pixels) # create an editable copy (list)
    shadow_clamp = 0.48 * clamp_factor
    for i in range(0, len(pixels), 4):
        pixels[i] = numpy.clip((1.0 - pixels[i]), 0.0, shadow_clamp)
    for i in range(1, len(pixels), 4):
        pixels[i] = numpy.clip((1.0 - pixels[i]), 0.0, shadow_clamp)
    for i in range(2, len(pixels), 4):
        pixels[i] = numpy.clip((1.0 - pixels[i]), 0.0, shadow_clamp)
    img.pixels[:] = pixels
    img.update()
    #return img
    
#----------------------------------------------------------------------------------
#- Checks for the temp baking material
#----------------------------------------------------------------------------------
def get_filler_mat():
    if bpy.data.materials.get("_tmp_bakemat"):
        return bpy.data.materials.get("_tmp_bakemat")
        
def get_empty_tex():
    if bpy.data.textures.get("_tmp_fillertex"):
        return bpy.data.textures.get("_tmp_fillertex")
    
    blender_tex = bpy.data.textures.new("_tmp_fillertex", "IMAGE")
    blender_tex.image = get_empty_image()
    blender_tex.thug_material_pass_props.blend_mode = 'vBLEND_MODE_BLEND'
    return blender_tex
    
#----------------------------------------------------------------------------------
#- Creates or returns the transparent texture used for 'filler' texture slots
#----------------------------------------------------------------------------------
def get_empty_image():
    if bpy.data.images.get("_tmp_empty"):
        return bpy.data.images.get("_tmp_empty")
    size = 32, 32
    img = bpy.data.images.new(name="_tmp_empty", width=size[0], height=size[1])
    pixels = [None] * size[0] * size[1]
    for x in range(size[0]):
        for y in range(size[1]):
            r = 1.0
            g = 1.0
            b = 1.0
            a = 0.0
            pixels[(y * size[0]) + x] = [r, g, b, a]
    pixels = [chan for px in pixels for chan in px]
    img.pixels = pixels
    img.use_fake_user = True
    return img
    
#----------------------------------------------------------------------------------
#- Checks for the temp off-white image used for baking onto a surface
#----------------------------------------------------------------------------------
def get_filler_image(color, img_name, img_size, persist=False):
    if bpy.data.images.get(img_name):
        return bpy.data.images.get(img_name)
        
    size = img_size, img_size
    img = bpy.data.images.new(name=img_name, width=size[0], height=size[1])
    ## For white image
    # pixels = [1.0] * (4 * size[0] * size[1])
    pixels = [None] * size[0] * size[1]
    for x in range(size[0]):
        for y in range(size[1]):
            # assign RGBA to something useful
            r = color[0]
            g = color[1]
            b = color[2]
            a = color[3]
            pixels[(y * size[0]) + x] = [r, g, b, a]

    # flatten list
    pixels = [chan for px in pixels for chan in px]
    # assign pixels
    img.pixels = pixels
    if persist:
        img.use_fake_user = True
        img.pack(as_png=True)
    return img
    
    
#----------------------------------------------------------------------------------
#- Collects the materials assigned to an object and stores in original_mats
#----------------------------------------------------------------------------------
def store_materials(obj, remove_mats = False):
    stored_mats = []
    # We also want to store the names of the materials on the object itself
    # This way we can 'un-bake' and restore the original mats later on
    if not "is_baked" in obj or obj["is_baked"] == False:
        original_mats = []
    
    for mat_slot in obj.material_slots:
        if not mat_slot.material.name.startswith('Lightmap_'):
            stored_mats.append(mat_slot.material)
            if not "is_baked" in obj or obj["is_baked"] == False:
                # Make sure it won't be deleted upon close!
                mat_slot.material.use_fake_user = True 
                original_mats.append(mat_slot.material.name)
            
    if remove_mats == True:
        for i in range(len(obj.material_slots)):
            obj.active_material_index = i
            bpy.ops.object.material_slot_remove({'object': obj})

    if not "is_baked" in obj or obj["is_baked"] == False:
        obj["original_mats"] = original_mats
    
    return stored_mats
    
#----------------------------------------------------------------------------------
#- Restores materials previously assigned to an object
#----------------------------------------------------------------------------------
def restore_mats(obj, stored_mats):
    new_mats = []
    for mat_slot in obj.material_slots:
        new_mats.append(mat_slot.material)

    for i in range(len(obj.material_slots)):
        obj.active_material_index = i
        bpy.ops.object.material_slot_remove({'object': obj})
        
    for mat in stored_mats:
        #mat.use_nodes = False
        #obj.data.materials.append(mat.copy())
        obj.data.materials.append(mat)
    #for mat in new_mats:
    #    obj.data.materials.append(mat)
        
#----------------------------------------------------------------------------------
#- Restores face material assignments
#----------------------------------------------------------------------------------
def restore_mat_assignments(obj, orig_polys):
    #polys = obj.data.polygons
    face_list = [face for face in obj.data.polygons]
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data) 
    
    for face in bm.faces: 
        face.select = False
    for face in bm.faces: 
        face.select = True
        face.material_index = orig_polys[face.index]
        #print("assigning mat {} to face {}".format(face.material_index, face.index))
        
    obj.data.update()
        
    # toggle to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
            
def mat_get_pass(blender_mat, type):
    for p in blender_mat.texture_slots:
        if p is None:
            continue
        if type == 'Diffuse' and p.use_map_color_diffuse:
            return p.texture
        elif type == 'Normal' and p.use_map_normal:
            return p.texture
            
    return None
    
def get_cycles_node(nodes, name, type, create_if_none=True):
    if nodes.get(name):
        return nodes.get(name)
    if create_if_none:
        new_node = nodes.new(type)
        new_node.name = name
        return new_node
    return None
    
#----------------------------------------------------------------------------------
#- Ensures the Cycles scene is using Cycles materials before baking
#----------------------------------------------------------------------------------
def setup_cycles_scene(use_uglymode = False):
    if use_uglymode:
        print("USING UGLY MODE!")
        for mat in bpy.data.materials:
            mat.use_nodes = False
    else:
        print("TURNING ON CYCLES MAT NODES!")
        for mat in bpy.data.materials:
            mat.use_nodes = True
    

def setup_cycles_nodes(node_tree, diffuse_tex = None, normal_tex = None, color = [1.0, 1.0, 1.0, 1.0], uv_map = ""):
    nodes = node_tree.nodes
    # First, add textures...
    # Add dummy diffuse texture node (off white)
    node_d = get_cycles_node(nodes, 'Filler Tex', 'ShaderNodeTexImage')
    node_d.image = get_filler_image(color, "_tmp_flat", 512)
    node_d.location = (-680,40)
    
    node_t = get_cycles_node(nodes, 'Diffuse Texture', 'ShaderNodeTexImage')
    if diffuse_tex and hasattr(diffuse_tex, 'image'):
        node_t.image = diffuse_tex.image
    node_t.location = (-660,320)
        
    node_n = get_cycles_node(nodes, 'Normal Texture', 'ShaderNodeTexImage')
    if normal_tex and hasattr(normal_tex, 'image'):
        node_n.image = normal_tex
    node_n.color_space = 'NONE'
    node_n.location = (-680,-220)
        
    # Now, add shaders!
    # Add diffuse shader (if it doesn't exist, which it should!)
    node_sd = get_cycles_node(nodes, 'Diffuse BSDF', 'ShaderNodeBsdfDiffuse')
    node_sd.location = (-160,280)
    
    # Add the transparent BDSF
    node_st = get_cycles_node(nodes, 'Transparent BDSF', 'ShaderNodeBsdfTransparent')
    node_st.location = (-160,400)
    
    # Add a shader mix node (for transparent and diffuse shaders)
    node_sm = get_cycles_node(nodes, 'Mix Shader', 'ShaderNodeMixShader')
    node_sm.location = (80,340)
    
    # Add a normal map node 
    node_sn = get_cycles_node(nodes, 'Normal Map', 'ShaderNodeNormalMap')
    node_sn.location = (-420,0)
    node_sn.uv_map = uv_map
    
    # Add a UV map node 
    node_uv = get_cycles_node(nodes, 'UV Map', 'ShaderNodeUVMap')
    node_uv.location = (-1060,60)
    node_uv.uv_map = uv_map
    
    # Material output (if that somehow doesn't exist already)
    node_mo = get_cycles_node(nodes, 'Material Output', 'ShaderNodeOutputMaterial')
    node_mo.location = (300, 340)
    
    # Now, add links!
    node_tree.links.new(node_t.inputs[0], node_uv.outputs[0]) # Diffuse Texture UV
    node_tree.links.new(node_n.inputs[0], node_uv.outputs[0]) # Normal Texture UV
    
    if normal_tex:
        node_tree.links.new(node_sn.inputs[1], node_n.outputs[0]) # Normal Map color
    node_tree.links.new(node_sd.inputs[0], node_d.outputs[0]) # Diff Shader color
    node_tree.links.new(node_sd.inputs[2], node_sn.outputs[0]) # Diff Shader Normal
    node_tree.links.new(node_sm.inputs[0], node_t.outputs[1]) # Mix Shader fac
    node_tree.links.new(node_sm.inputs[1], node_st.outputs[0]) # Mix Shader Shader1
    node_tree.links.new(node_sm.inputs[2], node_sd.outputs[0]) # Mix Shader Shader2
    
    node_tree.links.new(node_mo.inputs[0], node_sm.outputs[0]) # Material Output Surface
    
    

#----------------------------------------------------------------------------------
#- Removes baked vertex color data on specified objects
#----------------------------------------------------------------------------------
def clear_bake_vcs(scene, meshes):
    for obj in meshes:
        if obj.data.vertex_colors.get('bake'):
            obj.data.vertex_colors.remove(obj.data.vertex_colors.get('bake'))
            
#----------------------------------------------------------------------------------
#- Converts a baked texture to vertex colors (allows Cycles VC bakes)
#----------------------------------------------------------------------------------
def convert_bake_to_vcs(scene, meshes):
    for obj in meshes:
        bake_vcs = get_vcs(obj, 'bake')
        
        obdata = obj.data
        obdata.vertex_colors.active = bake_vcs
        
        if not obdata.uv_layers.get('Lightmap'):
            print('Object {} is not baked, skipping...'.format(obj.name))
            continue
            
        # Determine what image we are looking for
        # If the object is part of a lightmap group, search by group name
        if obj.thug_lightmap_group_id > -1 and scene.thug_lightmap_groups[obj.thug_lightmap_group_id]:
            group_name = scene.thug_lightmap_groups[obj.thug_lightmap_group_id].name
            pbr_lightmap_name = 'PM_{}_{}'.format(scene.thug_bake_slot, group_name)
            lightmap_name = 'LM_{}_{}'.format(scene.thug_bake_slot, group_name)
            legacy_name = 'LM_{}'.format(group_name)
        else:
            pbr_lightmap_name = 'PM_{}_{}'.format(scene.thug_bake_slot, obj.name)
            lightmap_name = 'LM_{}_{}'.format(scene.thug_bake_slot, obj.name)
            legacy_name = 'LM_{}'.format(obj.name)
        
        if not bpy.data.images.get(pbr_lightmap_name):
            if not bpy.data.images.get(lightmap_name):
                if not bpy.data.images.get(legacy_name):
                    print('Lightmap texture not found for {}, skipping...'.format(obj.name))
                    continue
                lightmap_img = bpy.data.images.get(legacy_name)
            else:
                lightmap_img = bpy.data.images.get(lightmap_name)
        else:
            lightmap_img = bpy.data.images.get(pbr_lightmap_name)
            
        image_size_x = lightmap_img.size[0] 
        image_size_y = lightmap_img.size[1] 
        uv_pixels = lightmap_img.pixels[:]
        
        print('Flattening bake for {} into vertex colors from texture {}...'.format(obj.name, lightmap_img.name))
        for p in obdata.polygons:
            for loop in p.loop_indices:
                obdata.uv_textures['Lightmap'].data[p.index].image = get_filler_image([1.0, 1.0, 1.0, 1.0], "_tmp_white", 16, True)
                co = obdata.uv_layers['Lightmap'].data[loop].uv
                x_co = round(co[0] * (image_size_x - 1))
                y_co = round(co[1] * (image_size_y - 1))
                
                col_out = bake_vcs.data[loop].color
                    
                pixelNumber = (image_size_x * y_co) + x_co
                r = uv_pixels[pixelNumber*4]
                g = uv_pixels[pixelNumber*4 + 1]
                b = uv_pixels[pixelNumber*4 + 2]
                a = uv_pixels[pixelNumber*4 + 3]
                
                col_in = r, g, b # texture-color
                col_result = [r,g,b] # existing / 'base' color
                col_result = col_in
                bake_vcs.data[loop].color = col_result
        
#----------------------------------------------------------------------------------
#- 'Un-bakes' the object (restores the original materials)
#----------------------------------------------------------------------------------
def unbake(obj):
    if not "is_baked" in obj or obj["is_baked"] == False:
        # Don't try to unbake something that isn't baked to begin with!
        return
        
    if not "original_mats" in obj:
        raise Exception("Cannot unbake object - unable to find original materials.")
        
    # First, remove the existing mats on the object (these should be lightmapped)
    for i in range(len(obj.material_slots)):
        obj.active_material_index = i
        bpy.ops.object.material_slot_remove({'object': obj})
        
    for mat_name in obj["original_mats"]:
        if not bpy.data.materials.get(mat_name):
            raise Exception("Material {} no longer exists. Uh oh!".format(mat_name))
        _mat = bpy.data.materials.get(mat_name)
        obj.data.materials.append(_mat)
        
    obj["is_baked"] = False
    obj["thug_last_bake_res"] = 0

def save_baked_texture(img, folder):
    img.filepath_raw = "{}/{}.png".format(folder, img.name)
    img.file_format = "PNG"
    img.save()
    print("Saved texture {}.png to {}".format(img.name, folder))
    #bpy.path.abspath("//my/file.txt")
    
#----------------------------------------------------------------------------------
#- Bakes a set of objects to vertex colors (Blender Render only)
#----------------------------------------------------------------------------------
def bake_thug_vcs(meshes, context):
    scene = context.scene
    # De-select any objects currently selected
    if context.selected_objects:
        for ob in context.selected_objects:
            ob.select = False
            
    # We need to be in Cycles to run the lightmap bake
    previous_engine = 'BLENDER_RENDER'
    if scene.render.engine != 'BLENDER_RENDER':
        previous_engine = scene.render.engine
        scene.render.engine = 'BLENDER_RENDER'
        
    # Set up the actual bake (man, this is so easy compared to texture bakes!)
    bpy.context.scene.render.bake_type = "FULL"
    #bpy.context.scene.render.bake_normal_space = "WORLD"
    bpy.context.scene.render.use_bake_to_vertex_color = True
    bpy.context.scene.render.use_bake_selected_to_active = False
    bpy.context.scene.render.use_bake_multires = False
    
    total_meshes = len(meshes)
    mesh_num = 0
    baked_obs = []
    for ob in meshes:
        mesh_num += 1
        print("****************************************")
        print("BAKING LIGHTING FOR OBJECT #" + str(mesh_num) + " OF " + str(total_meshes) + ": " + ob.name)
        print("****************************************")
        if ob.thug_export_scene == False:
            print("Object {} not marked for export to scene, skipping bake!".format(ob.name))
            continue
        # Set it to active and go into edit mode
        scene.objects.active = ob
        ob.select = True
        
        # Add the 'color' vertex color channel (used by THUG) and make sure we are baking onto it
        if "color" not in ob.data.vertex_colors:
            bpy.ops.mesh.vertex_color_add({"object": ob})
            ob.data.vertex_colors[len(ob.data.vertex_colors)-1].name = 'color'
        ob.data.vertex_colors["color"].active_render = True
        
        # Also grab the original mesh data so we can remap the material assignments
        # - if we have more than one material assigned to our object
        if len(ob.data.materials) > 1:
            orig_polys = [0] * len(ob.data.polygons)
            for f in ob.data.polygons:
                orig_polys[f.index] = f.material_index
                
        # Store the materials assigned to the object so we can use a flat color on the mesh (better bake results)
        orig_mats = store_materials(ob, True)
        orig_index = ob.active_material_index
        try:
            bpy.ops.object.bake_image()
        except RuntimeError:
            print("Bake failed on this object! :(")
        
        # Now, for the cleanup! Let's restore the missing mats
        restore_mats(ob, orig_mats)
        if orig_index != None and orig_index >= 0:
            ob.active_material_index = orig_index
            
        # If there is more than one material, restore the per-face material assignment
        if len(ob.data.materials) > 1:
            restore_mat_assignments(ob, orig_polys)
            
        print("Object " + ob.name + " baked to vertex colors!")
        ob.select = False
        
        
#----------------------------------------------------------------------------------
#- Bakes 'Half Life 2' Radiosity light maps
#----------------------------------------------------------------------------------
def bake_hl2_lightmaps(meshes, context):
    scene = context.scene
    # De-select any objects currently selected
    if context.selected_objects:
        for ob in context.selected_objects:
            ob.select = False
            
    is_cycles = True
    previous_engine = 'CYCLES'
    if scene.render.engine != 'CYCLES':
        previous_engine = scene.render.engine
        scene.render.engine = 'CYCLES'
    
    # If the user saved but didn't pack images, the filler image will be black
    # so we should get rid of it to ensure the bake result is always correct
    if bpy.data.images.get("_tmp_flat"):
        bpy.data.images["_tmp_flat"].user_clear()
        bpy.data.images.remove(bpy.data.images.get("_tmp_flat"))
        
    # Create destination folder for the baked textures
    _lightmap_folder = bpy.path.basename(bpy.context.blend_data.filepath)[:-6] # = Name of blend file
    _folder = bpy.path.abspath("//Tx_Lightmap_PBR/{}".format(_lightmap_folder))
    os.makedirs(_folder, 0o777, True)
    
    setup_cycles_scene(scene.thug_lightmap_uglymode)
    
    total_meshes = len(meshes)
    mesh_num = 0
    baked_obs = []
    rebake_existing_pass = False
    dont_change_resolution = True
    
    for ob in meshes:
        mesh_num += 1
        print("****************************************")
        print("BAKING LIGHTING FOR OBJECT #" + str(mesh_num) + " OF " + str(total_meshes) + ": " + ob.name)
        print("****************************************")
    
        if "is_baked" in ob and ob["is_baked"] == True:
            print("Object has been previously baked.")
            
        if ob.thug_export_scene == False:
            print("Object {} not marked for export to scene, skipping bake!".format(ob.name))
            continue
            
        if not ob.data.uv_layers:
            print("Object {} has no UV maps. Cannot bake lighting!".format(ob.name))
            continue
            
        if not ob.data.materials:
            print("Object {} has no materials. Cannot bake lighting!".format(ob.name))
            continue
            
        # Set it to active and go into edit mode
        scene.objects.active = ob
        ob.select = True
        
        # Set the desired resolution, both for the UV map and the lightmap texture
        img_res = 128
        bake_margin = 1.0
        lightmap_name_x = 'LM_{}_{}_X'.format(scene.thug_bake_slot, ob.name)
        lightmap_name_y = 'LM_{}_{}_Y'.format(scene.thug_bake_slot, ob.name)
        lightmap_name_z = 'LM_{}_{}_Z'.format(scene.thug_bake_slot, ob.name)
        
        
        if ob.thug_lightmap_resolution:
            img_res = int(ob.thug_lightmap_resolution)
            print("Object lightmap resolution is: {}x{}".format(img_res, img_res))
        if scene.thug_lightmap_scale:
            img_res = int(img_res * float(scene.thug_lightmap_scale))
            if img_res < 16:
                img_res = 16
            print("Resolution after scene scale is: {}x{}".format(img_res, img_res))
            
        if dont_change_resolution and "thug_last_bake_res" in ob:
            if ob["thug_last_bake_res"] > 0:
                print("Re-baking with same resolution as previously used: {}".format(ob["thug_last_bake_res"]))
                img_res = ob["thug_last_bake_res"]
            
        lightmap_img_x = get_image(lightmap_name_x, img_res, img_res)
        lightmap_img_y = get_image(lightmap_name_y, img_res, img_res)
        lightmap_img_z = get_image(lightmap_name_z, img_res, img_res)
        
        # Blender's UV margins seem to scale with resolution, so we need to make them smaller
        # as the UV resolution increases 
        uv_padding = 0.05
        if img_res > 2048:
            bake_margin = 0.025
            uv_padding = 0.002
        elif img_res > 1024:
            bake_margin = 0.1
            uv_padding = 0.005
        elif img_res > 512:
            bake_margin = 0.25
            uv_padding = 0.01
        elif img_res > 64:
            uv_padding = 0.01
            
        # Grab original UV map, so any diffuse/normal textures are mapped correctly
        orig_uv = ob.data.uv_layers[0].name
        
        # Also grab the original mesh data so we can remap the material assignments
        # - if we have more than one material assigned to our object
        if len(ob.data.materials) > 1:
            orig_polys = [0] * len(ob.data.polygons)
            for f in ob.data.polygons:
                orig_polys[f.index] = f.material_index
        
        uvs_are_new = False
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Recreate the UV map if it's a different resolution than we want now
        if dont_change_resolution == False:
            if ("thug_last_bake_res" in ob and ob["thug_last_bake_res"] != img_res) \
            or ("thug_last_bake_type" in ob and ob["thug_last_bake_type"] != ob.thug_lightmap_type) \
            or ("thug_last_bake_res" not in ob or "thug_last_bake_type" not in ob)\
            or scene.thug_bake_force_remake == True:
                print("Removing existing images/UV maps.")
                if ob.data.uv_layers.get('Lightmap'):
                    ob.data.uv_textures.remove(ob.data.uv_textures['Lightmap'])
                if lightmap_img:
                    lightmap_img.source = 'GENERATED'
                if shadowmap_img:
                    shadowmap_img.source = 'GENERATED'
                
        # Create the Lightmap UV layer 
        if not ob.data.uv_layers.get('Lightmap'):
            uvs_are_new = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.uv_texture_add({"object": ob})
            ob.data.uv_layers[len(ob.data.uv_layers)-1].name = 'Lightmap'
            ob.data.uv_textures['Lightmap'].active = True
            
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            # Unwrap the mesh based on the type specified on the object properties!
            if ob.thug_lightmap_type == 'Lightmap':
                bpy.ops.uv.lightmap_pack(
                    PREF_CONTEXT='ALL_FACES', PREF_PACK_IN_ONE=True, PREF_NEW_UVLAYER=False,
                    PREF_APPLY_IMAGE=False, PREF_IMG_PX_SIZE=img_res, 
                    PREF_BOX_DIV=48, PREF_MARGIN_DIV=bake_margin)
            elif ob.thug_lightmap_type == 'Smart':
                bpy.ops.uv.smart_project()
            else:
                raise Exception("Unknown lightmap type specified on object {}".format(ob.name))
                
        else:
            ob.data.uv_textures['Lightmap'].active = True
            
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        if uvs_are_new and scene.thug_bake_pad_uvs == True:
            # Argh, Blender's UV projection sometimes creates seams on the edges of the image!
            # Add some padding by scaling the whole thing down a little bit
            scale_uvs(ob.data.uv_layers['Lightmap'], mathutils.Vector((1.0-uv_padding, 1.0-uv_padding)))
        
        #-----------------------------------------------------------------------------------------
        # Multi-pass bake: render multiple bake textures, then flatten then into a single image
        # First, bake each pass to a separate image...
        bake_passes = [ 'X', 'Y', 'Z' ]
        
        for bakepass in bake_passes:
            print("**********************")
            print("Baking {} pass...".format(bakepass))
            orig_index = ob.active_material_index
            store_materials(ob)
            
            if bakepass == 'X':
                image = lightmap_img_x
                pass_name = lightmap_name_x
            elif bakepass == 'Y':
                image = lightmap_img_y
                pass_name = lightmap_name_y
            elif bakepass == 'Z':
                image = lightmap_img_z
                pass_name = lightmap_name_z
            
            image.use_fake_user = True # Ensure it won't be deleted when closing the scene
            
            # Create or retrieve the lightmap texture
            blender_tex = get_texture("Baked_{}".format(ob.name))
            blender_tex.image = image
            blender_tex.thug_material_pass_props.blend_mode = 'vBLEND_MODE_MODULATE'
            
            for mat in ob.data.materials:
                node_n = get_cycles_node(mat.node_tree.nodes, 'Normal Map', 'ShaderNodeNormalMap')
                if node_n == None:
                    raise Exception("No Normal Map node :(")
                    
                if len(node_n.inputs[1].links):
                    mat.node_tree.links.remove(node_n.inputs[1].links[0])
                if bakepass == 'X':
                    new_normal = [ -(1/math.sqrt(6)), -(1/math.sqrt(2)), 1/math.sqrt(3), 1.0 ]
                if bakepass == 'Y':
                    new_normal = [ -(1/math.sqrt(6)), (1/math.sqrt(2)), 1/math.sqrt(3), 1.0 ]
                elif bakepass == 'Z':
                    new_normal = [ math.sqrt(2/3), 0, 1/math.sqrt(3), 1.0 ]
                
                new_normal[0] = (new_normal[0] + 1.0) * 0.5
                new_normal[1] = (new_normal[1] + 1.0) * 0.5
                new_normal[2] = (new_normal[2] + 1.0) * 0.5
                
                node_n.inputs[1].default_value = (new_normal[0], new_normal[1], new_normal[2], 1.0)
                
                node_d = get_cycles_node(mat.node_tree.nodes, 'Bake Result', 'ShaderNodeTexImage')
                node_d.image = blender_tex.image
                node_d.location = (-880,40)
                mat.node_tree.nodes.active = node_d
                
                # Add a UV map node 
                node_uv = get_cycles_node(mat.node_tree.nodes, 'Bake Result UV', 'ShaderNodeUVMap')
                node_uv.location = (-1060,60)
                node_uv.uv_map = "Lightmap"
                mat.node_tree.links.new(node_d.inputs[0], node_uv.outputs[0]) # Bake Texture UV
                
            # Bake the lightmap for Cycles!
            scene.cycles.bake_type = 'DIFFUSE'
            bpy.context.scene.render.bake.use_pass_color = False
            bpy.context.scene.render.bake.use_pass_indirect = True
            bpy.context.scene.render.bake.use_pass_direct = True
            
            if scene.thug_bake_automargin:
                scene.render.bake_margin = 1 # Used to be bake_margin
            if ob.thug_lightmap_quality != 'Custom':
                if ob.thug_lightmap_quality == 'Draft':
                    scene.cycles.samples = 64
                    scene.cycles.max_bounces = 2
                if ob.thug_lightmap_quality == 'Preview':
                    scene.cycles.samples = 100
                    scene.cycles.max_bounces = 2
                if ob.thug_lightmap_quality == 'Good':
                    scene.cycles.samples = 300
                    scene.cycles.max_bounces = 2
                if ob.thug_lightmap_quality == 'High':
                    scene.cycles.samples = 600
                    scene.cycles.max_bounces = 3
                if ob.thug_lightmap_quality == 'Ultra':
                    scene.cycles.samples = 1280
                    scene.cycles.max_bounces = 3
            print("Using {} bake quality. Samples: {}, bounces: {}".format(ob.thug_lightmap_quality, scene.cycles.samples, scene.cycles.max_bounces))
            bpy.ops.object.bake(type='DIFFUSE')
            save_baked_texture(image, _folder)
            
               
        print("Object " + ob.name + " baked to texture " + blender_tex.name)
        baked_obs.append(ob.name)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        if scene.thug_bake_type == 'FULL' or scene.thug_bake_type == 'FULL_BI' or scene.thug_bake_type == 'LIGHT' or scene.thug_bake_type == 'INDIRECT' or scene.thug_bake_type == 'SHADOW':
            ob.active_material_index = orig_index
        
        ob.data.uv_textures[orig_uv].active = True
        ob.data.uv_textures[orig_uv].active_render = True
        
        #for mat in ob.data.materials:
        #    node_n = get_cycles_node(mat.node_tree.nodes, 'Normal Map', 'ShaderNodeNormalMap')
        #    if node_n != None:
        #        node_n.inputs[1].default_value = (0.5, 0.5, 1.0, 1.0)
        
        # If there is more than one material, restore the per-face material assignment
        if len(ob.data.materials) > 1:
            restore_mat_assignments(ob, orig_polys)
        ob.select = False
        ob["is_baked"] = True
        ob["thug_last_bake_res"] = img_res
        ob["thug_last_bake_type"] = ob.thug_lightmap_type
        # Done!!
    
    # Once we have finished baking everything, we then duplicate the materials and assign
    # the lightmap texture to them - should be faster than doing it during the baking step
    print("Baking complete. Setting up lightmapped materials...")
    for obname in baked_obs:
        ob = bpy.data.objects.get(obname)
        if not ob: 
            raise Exception("Unable to find baked object {}".format(obname))
        for mat in ob.data.materials:
            mat.use_nodes = False
        for mat_slot in ob.material_slots:
            mat_slot.material = mat_slot.material.copy()
            
            lightmap_img_x = maybe_get_image('LM_{}_{}_X'.format(scene.thug_bake_slot, ob.name))
            lightmap_img_y = maybe_get_image('LM_{}_{}_Y'.format(scene.thug_bake_slot, ob.name))
            lightmap_img_z = maybe_get_image('LM_{}_{}_Z'.format(scene.thug_bake_slot, ob.name))
            lightmap_img = maybe_get_image('PM_{}_{}'.format(scene.thug_bake_slot, ob.name))
            blender_tex = bpy.data.textures.get("Baked_{}".format(obname))
            # Add the lightmap into the new UG+ material system, for the corresponding lightmap slot
            if scene.thug_bake_slot == 'DAY':
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap.tex_image = lightmap_img_x
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap2.tex_image = lightmap_img_y
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap3.tex_image = lightmap_img_z
            elif scene.thug_bake_slot == 'EVENING':
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap2.tex_image = lightmap_img
            elif scene.thug_bake_slot == 'NIGHT':
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap3.tex_image = lightmap_img
            elif scene.thug_bake_slot == 'MORNING':
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap4.tex_image = lightmap_img
            
            # Also add the image to the legacy material system
            if not mat_slot.material.texture_slots.get(blender_tex.name):
                slot = mat_slot.material.texture_slots.add()
            else:
                slot = mat_slot.material.texture_slots.get(blender_tex.name)
            slot.texture = blender_tex
            slot.uv_layer = str('Lightmap')
            slot.blend_type = 'MULTIPLY'
        print("Processed object: {}".format(obname))
          
    print("COMPLETE! Thank you for your patience!")
    # Switch back to the original engine, if it wasn't Cycles
    if previous_engine != scene.render.engine:
        scene.render.engine = previous_engine
    # Toggle use_nodes on the whole scene materials, if desired (depending on the engine we are on)
    if previous_engine == 'BLENDER_RENDER':
        for mat in bpy.data.materials:
            mat.use_nodes = False
    elif previous_engine == 'CYCLES':
        for mat in bpy.data.materials:
            mat.use_nodes = True
        
        
        

#----------------------------------------------------------------------------------
#- Bakes lightmaps to an object group, rather than individually
#- objects are merged, unwrapped, baked, then separated
#----------------------------------------------------------------------------------
def bake_to_group(objects, group_name, context):
    bake_group = bpy.data.groups.get(group_name)
    if not bake_group:
        raise Exception('Group {} not found.'.format(group_name))
        
    # Remove existing merged object, if it exists
    ob_merged_old = bpy.data.objects.get(group_name + "_tempMerged")
    if ob_merged_old is not None:
        bpy.data.objects.remove(ob)
        
        
        
        
#----------------------------------------------------------------------------------
#- Bakes light/shadow maps for UG+/UG Classic's PBR shaders
#----------------------------------------------------------------------------------
def bake_ugplus_lightmaps(meshes, context):
    scene = context.scene
    # De-select any objects currently selected
    if context.selected_objects:
        for ob in context.selected_objects:
            ob.select = False
            
    is_cycles = True
    previous_engine = 'CYCLES'
    if scene.render.engine != 'CYCLES':
        previous_engine = scene.render.engine
        scene.render.engine = 'CYCLES'
    
    # If the user saved but didn't pack images, the filler image will be black
    # so we should get rid of it to ensure the bake result is always correct
    if bpy.data.images.get("_tmp_flat"):
        bpy.data.images["_tmp_flat"].user_clear()
        bpy.data.images.remove(bpy.data.images.get("_tmp_flat"))
        
    # Create destination folder for the baked textures
    _lightmap_folder = bpy.path.basename(bpy.context.blend_data.filepath)[:-6] # = Name of blend file
    _folder = bpy.path.abspath("//Tx_Lightmap_PBR/{}".format(_lightmap_folder))
    os.makedirs(_folder, 0o777, True)
    
    setup_cycles_scene(scene.thug_lightmap_uglymode)
    
    total_meshes = len(meshes)
    mesh_num = 0
    baked_obs = []
    rebake_existing_pass = False
    dont_change_resolution = True
    
    for ob in meshes:
        mesh_num += 1
        print("****************************************")
        print("BAKING LIGHTING FOR OBJECT #" + str(mesh_num) + " OF " + str(total_meshes) + ": " + ob.name)
        print("****************************************")
    
        if "is_baked" in ob and ob["is_baked"] == True:
            print("Object has been previously baked.")
            
        if ob.thug_export_scene == False:
            print("Object {} not marked for export to scene, skipping bake!".format(ob.name))
            continue
            
        if not ob.data.uv_layers:
            print("Object {} has no UV maps. Cannot bake lighting!".format(ob.name))
            continue
            
        if not ob.data.materials:
            print("Object {} has no materials. Cannot bake lighting!".format(ob.name))
            continue
            
        # Set it to active and go into edit mode
        scene.objects.active = ob
        ob.select = True
        
        # Set the desired resolution, both for the UV map and the lightmap texture
        img_res = 128
        bake_margin = 1.0
        lightmap_name = 'PM_{}_{}'.format(scene.thug_bake_slot, ob.name)
        shadowmap_name = 'LM_{}_{}'.format(scene.thug_bake_slot, ob.name)
        legacy_name = 'LM_{}'.format(ob.name)
        
        lightmap_img = maybe_get_image(lightmap_name)
        shadowmap_img = maybe_get_image(shadowmap_name)
        legacy_img = maybe_get_image(legacy_name)
        
        if ob.thug_lightmap_resolution:
            img_res = int(ob.thug_lightmap_resolution)
            print("Object lightmap resolution is: {}x{}".format(img_res, img_res))
        if scene.thug_lightmap_scale:
            img_res = int(img_res * float(scene.thug_lightmap_scale))
            if img_res < 16:
                img_res = 16
            print("Resolution after scene scale is: {}x{}".format(img_res, img_res))
            
        if dont_change_resolution and "thug_last_bake_res" in ob:
            if ob["thug_last_bake_res"] > 0:
                print("Re-baking with same resolution as previously used: {}".format(ob["thug_last_bake_res"]))
                img_res = ob["thug_last_bake_res"]
            
        # Blender's UV margins seem to scale with resolution, so we need to make them smaller
        # as the UV resolution increases 
        uv_padding = 0.05
        if img_res > 2048:
            bake_margin = 0.025
            uv_padding = 0.002
        elif img_res > 1024:
            bake_margin = 0.1
            uv_padding = 0.005
        elif img_res > 512:
            bake_margin = 0.25
            uv_padding = 0.01
        elif img_res > 64:
            uv_padding = 0.01
            
        # Grab original UV map, so any diffuse/normal textures are mapped correctly
        orig_uv = ob.data.uv_layers[0].name
        
        # Also grab the original mesh data so we can remap the material assignments
        # - if we have more than one material assigned to our object
        if len(ob.data.materials) > 1:
            orig_polys = [0] * len(ob.data.polygons)
            for f in ob.data.polygons:
                orig_polys[f.index] = f.material_index
        
        uvs_are_new = False
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Recreate the UV map if it's a different resolution than we want now
        if dont_change_resolution == False:
            if ("thug_last_bake_res" in ob and ob["thug_last_bake_res"] != img_res) \
            or ("thug_last_bake_type" in ob and ob["thug_last_bake_type"] != ob.thug_lightmap_type) \
            or ("thug_last_bake_res" not in ob or "thug_last_bake_type" not in ob)\
            or scene.thug_bake_force_remake == True:
                print("Removing existing images/UV maps.")
                if ob.data.uv_layers.get('Lightmap'):
                    ob.data.uv_textures.remove(ob.data.uv_textures['Lightmap'])
                if lightmap_img:
                    lightmap_img.source = 'GENERATED'
                if shadowmap_img:
                    shadowmap_img.source = 'GENERATED'
                
        # Create the Lightmap UV layer 
        if not ob.data.uv_layers.get('Lightmap'):
            uvs_are_new = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.uv_texture_add({"object": ob})
            ob.data.uv_layers[len(ob.data.uv_layers)-1].name = 'Lightmap'
            ob.data.uv_textures['Lightmap'].active = True
            
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            # Unwrap the mesh based on the type specified on the object properties!
            if ob.thug_lightmap_type == 'Lightmap':
                bpy.ops.uv.lightmap_pack(
                    PREF_CONTEXT='ALL_FACES', PREF_PACK_IN_ONE=True, PREF_NEW_UVLAYER=False,
                    PREF_APPLY_IMAGE=False, PREF_IMG_PX_SIZE=img_res, 
                    PREF_BOX_DIV=48, PREF_MARGIN_DIV=bake_margin)
            elif ob.thug_lightmap_type == 'Smart':
                bpy.ops.uv.smart_project()
            else:
                raise Exception("Unknown lightmap type specified on object {}".format(ob.name))
                
        else:
            ob.data.uv_textures['Lightmap'].active = True
            
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        if uvs_are_new and scene.thug_bake_pad_uvs == True:
            # Argh, Blender's UV projection sometimes creates seams on the edges of the image!
            # Add some padding by scaling the whole thing down a little bit
            scale_uvs(ob.data.uv_layers['Lightmap'], mathutils.Vector((1.0-uv_padding, 1.0-uv_padding)))
        
        #-----------------------------------------------------------------------------------------
        # Multi-pass bake: render multiple bake textures, then flatten then into a single image
        # First, bake each pass to a separate image...
        bake_passes = [ 'INDIRECT', 'DIFFUSE' ]
        
        for bakepass in bake_passes:
            print("**********************")
            print("Baking {} pass...".format(bakepass))
            orig_index = ob.active_material_index
            store_materials(ob)
            
            image = shadowmap_img if bakepass == 'DIFFUSE' else lightmap_img
            pass_name = shadowmap_name if bakepass == 'DIFFUSE' else lightmap_name
            
            # Create a new image to bake the pass to, if it doesn't exist
            if image != None and rebake_existing_pass == False:
                print("Baked image for pass {} already exists, skipping!".format(bakepass))
                blender_tex = get_texture("Baked_{}".format(ob.name))
                blender_tex.image = image
                blender_tex.thug_material_pass_props.blend_mode = 'vBLEND_MODE_MODULATE'
                continue
            elif image == None:
                if bakepass == 'DIFFUSE' and legacy_img != None:
                    print("(Legacy) Baked image for pass {} already exists, skipping!".format(bakepass))
                    blender_tex = get_texture("Baked_{}".format(ob.name))
                    blender_tex.image = legacy_img
                    blender_tex.thug_material_pass_props.blend_mode = 'vBLEND_MODE_MODULATE'
                    continue
                bpy.ops.image.new(name=pass_name, width=img_res, height=img_res, color=[0,0,0,1], alpha=True, generated_type='BLANK')
                image = bpy.data.images[pass_name]
            image.generated_width = img_res
            image.generated_height = img_res
            image.use_fake_user = True
            
            # Create or retrieve the lightmap texture
            blender_tex = get_texture("Baked_{}".format(ob.name))
            blender_tex.image = image
            blender_tex.thug_material_pass_props.blend_mode = 'vBLEND_MODE_MODULATE'
            
            for mat in ob.data.materials:
                node_d = get_cycles_node(mat.node_tree.nodes, 'Bake Result', 'ShaderNodeTexImage')
                node_d.image = blender_tex.image
                node_d.location = (-880,40)
                mat.node_tree.nodes.active = node_d
                # Add a UV map node 
                node_uv = get_cycles_node(mat.node_tree.nodes, 'Bake Result UV', 'ShaderNodeUVMap')
                node_uv.location = (-1060,60)
                node_uv.uv_map = "Lightmap"
                mat.node_tree.links.new(node_d.inputs[0], node_uv.outputs[0]) # Bake Texture UV
                
            # Bake the lightmap for Cycles!
            scene.cycles.bake_type = 'DIFFUSE'
            bpy.context.scene.render.bake.use_pass_color = False
            bpy.context.scene.render.bake.use_pass_indirect = True
            if bakepass == 'DIFFUSE':
                bpy.context.scene.render.bake.use_pass_direct = True
            else:
                bpy.context.scene.render.bake.use_pass_direct = False
            
            if scene.thug_bake_automargin:
                scene.render.bake_margin = 1 # Used to be bake_margin
            if ob.thug_lightmap_quality != 'Custom':
                if ob.thug_lightmap_quality == 'Draft':
                    scene.cycles.samples = 16
                    scene.cycles.max_bounces = 2
                if ob.thug_lightmap_quality == 'Preview':
                    scene.cycles.samples = 32
                    scene.cycles.max_bounces = 4
                if ob.thug_lightmap_quality == 'Good':
                    scene.cycles.samples = 108
                    scene.cycles.max_bounces = 5
                if ob.thug_lightmap_quality == 'High':
                    scene.cycles.samples = 225
                    scene.cycles.max_bounces = 6
                if ob.thug_lightmap_quality == 'Ultra':
                    scene.cycles.samples = 450
                    scene.cycles.max_bounces = 8
            print("Using {} bake quality. Samples: {}, bounces: {}".format(ob.thug_lightmap_quality, scene.cycles.samples, scene.cycles.max_bounces))
            bpy.ops.object.bake(type='DIFFUSE')
               
        print("Object " + ob.name + " baked to texture " + blender_tex.name)
        print("Combining bake passes into a single image {}...".format(lightmap_name))
        baked_obs.append(ob.name)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        lightmap_img = maybe_get_image(lightmap_name)
        shadowmap_img = maybe_get_image(shadowmap_name)
        legacy_img = maybe_get_image(legacy_name)
        
        destination_img = lightmap_img
        source_img = shadowmap_img if shadowmap_img != None else legacy_img
        
        replace_img_channel(destination_img, source_img, 'a')
        
        if scene.thug_bake_type == 'FULL' or scene.thug_bake_type == 'FULL_BI' or scene.thug_bake_type == 'LIGHT' or scene.thug_bake_type == 'INDIRECT' or scene.thug_bake_type == 'SHADOW':
            ob.active_material_index = orig_index
        
        save_baked_texture(destination_img, _folder)
        if shadowmap_img:
            save_baked_texture(shadowmap_img, _folder)
        ob.data.uv_textures[orig_uv].active = True
        ob.data.uv_textures[orig_uv].active_render = True
        
        # If there is more than one material, restore the per-face material assignment
        if len(ob.data.materials) > 1:
            restore_mat_assignments(ob, orig_polys)
        ob.select = False
        ob["is_baked"] = True
        ob["thug_last_bake_res"] = img_res
        ob["thug_last_bake_type"] = ob.thug_lightmap_type
        # Done!!
    
    # Once we have finished baking everything, we then duplicate the materials and assign
    # the lightmap texture to them - should be faster than doing it during the baking step
    print("Baking complete. Setting up lightmapped materials...")
    for obname in baked_obs:
        ob = bpy.data.objects.get(obname)
        if not ob: 
            raise Exception("Unable to find baked object {}".format(obname))
        for mat in ob.data.materials:
            mat.use_nodes = False
        for mat_slot in ob.material_slots:
            mat_slot.material = mat_slot.material.copy()
            
            lightmap_img = maybe_get_image('PM_{}_{}'.format(scene.thug_bake_slot, ob.name))
            blender_tex = bpy.data.textures.get("Baked_{}".format(obname))
            # Add the lightmap into the new UG+ material system, for the corresponding lightmap slot
            if scene.thug_bake_slot == 'DAY':
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap.tex_image = lightmap_img
            elif scene.thug_bake_slot == 'EVENING':
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap2.tex_image = lightmap_img
            elif scene.thug_bake_slot == 'NIGHT':
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap3.tex_image = lightmap_img
            elif scene.thug_bake_slot == 'MORNING':
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap4.tex_image = lightmap_img
            
            # Also add the image to the legacy material system
            if not mat_slot.material.texture_slots.get(blender_tex.name):
                slot = mat_slot.material.texture_slots.add()
            else:
                slot = mat_slot.material.texture_slots.get(blender_tex.name)
            slot.texture = blender_tex
            slot.uv_layer = str('Lightmap')
            slot.blend_type = 'MULTIPLY'
        print("Processed object: {}".format(obname))
          
    print("COMPLETE! Thank you for your patience!")
    # Switch back to the original engine, if it wasn't Cycles
    if previous_engine != scene.render.engine:
        scene.render.engine = previous_engine
    # Toggle use_nodes on the whole scene materials, if desired (depending on the engine we are on)
    if previous_engine == 'BLENDER_RENDER':
        for mat in bpy.data.materials:
            mat.use_nodes = False
    elif previous_engine == 'CYCLES':
        for mat in bpy.data.materials:
            mat.use_nodes = True
        
            
            
            
            
            
            
            
            
#----------------------------------------------------------------------------------
#- Bakes a set of objects to textures
#----------------------------------------------------------------------------------
def bake_thug_lightmaps(meshes, context):
    scene = context.scene
    
    total_meshes = len(meshes)
    wm = context.window_manager
    wm.progress_begin(0, total_meshes)
    
    # De-select any objects currently selected
    if context.selected_objects:
        for ob in context.selected_objects:
            ob.select = False
            
    is_cycles = ( scene.thug_bake_type in [ 'LIGHT', 'FULL', 'SHADOW', 'INDIRECT' ] )
    if is_cycles:
        print("USING CYCLES RENDER ENGINE FOR BAKING!")
    else:
        print("Using Blender Render engine for baking.")
        # For BI, configure bake settings here since we won't need to change anything per-object
        if scene.thug_bake_type == 'AO':
            scene.render.bake_type = "AO"
        else:
            scene.render.bake_type = "FULL"
        scene.render.use_bake_to_vertex_color = False
        scene.render.use_bake_selected_to_active = False
        scene.render.use_bake_multires = False
        if scene.thug_bake_automargin:
            scene.render.bake_margin = 1
        
    # Set the correct render engine used for baking
    if is_cycles:
        previous_engine = 'CYCLES'
        if scene.render.engine != 'CYCLES':
            previous_engine = scene.render.engine
            scene.render.engine = 'CYCLES'
    else:
        previous_engine = 'BLENDER_RENDER'
        if scene.render.engine != 'BLENDER_RENDER':
            previous_engine = scene.render.engine
            scene.render.engine = 'BLENDER_RENDER'
        
    # If the user saved but didn't pack images, the filler image will be black
    # so we should get rid of it to ensure the bake result is always correct
    if bpy.data.images.get("_tmp_flat"):
        bpy.data.images["_tmp_flat"].user_clear()
        bpy.data.images.remove(bpy.data.images.get("_tmp_flat"))
        
    # Create destination folder for the baked textures
    _lightmap_folder = bpy.path.basename(bpy.context.blend_data.filepath)[:-6] # = Name of blend file
    _folder = bpy.path.abspath("//Tx_Lightmap/{}".format(_lightmap_folder))
    os.makedirs(_folder, 0o777, True)
    
    # Setup nodes for Cycles materials
    if is_cycles:
        setup_cycles_scene(scene.thug_lightmap_uglymode)
    
    mesh_num = 0
    baked_obs = []
    wm.progress_update(mesh_num)
    for ob in meshes:
        mesh_num += 1
        print("****************************************")
        print("BAKING LIGHTING FOR OBJECT #" + str(mesh_num) + " OF " + str(total_meshes) + ": " + ob.name)
        print("****************************************")
        
        if "is_baked" in ob and ob["is_baked"] == True:
            print("Object has been previously baked.")
            
        if ob.thug_export_scene == False:
            print("Object {} not marked for export to scene, skipping bake!".format(ob.name))
            continue
            
        if not ob.data.uv_layers:
            print("Object {} has no UV maps. Cannot bake lighting!".format(ob.name))
            continue
            
        if not ob.data.materials:
            print("Object {} has no materials. Cannot bake lighting!".format(ob.name))
            continue
            
        # Check this object for a lightmap group - if it is part of a group we need to tweak
        # the bake process slightly to ensure the bake goes to the shared texture
        # rather than an object-specific texture
        group_name = ''
        if ob.thug_lightmap_group_id > -1:
            group_name = scene.thug_lightmap_groups[ob.thug_lightmap_group_id].name
            
        # Set it to active and go into edit mode
        scene.objects.active = ob
        ob.select = True
        
        # Set the desired resolution, both for the UV map and the lightmap texture
        img_res = 128
        bake_margin = 0.5
        lightmap_name = 'LM_{}_{}'.format(scene.thug_bake_slot, ob.name)
        if group_name != '':
            lightmap_name = 'LM_{}_{}'.format(scene.thug_bake_slot, group_name)
            img_res = int(scene.thug_lightmap_groups[ob.thug_lightmap_group_id].resolution)
            print("Lightmap resolution is: {}x{}".format(img_res, img_res))
        elif ob.thug_lightmap_resolution:
            img_res = int(ob.thug_lightmap_resolution)
            print("Object lightmap resolution is: {}x{}".format(img_res, img_res))

        if scene.thug_lightmap_scale:
            img_res = int(img_res * float(scene.thug_lightmap_scale))
            if img_res < 16:
                img_res = 16
            print("Resolution after scene scale is: {}x{}".format(img_res, img_res))
            
        # Blender's UV margins seem to scale with resolution, so we need to make them smaller
        # as the UV resolution increases 
        uv_padding = 0.05
        if img_res >= 2048:
            bake_margin = 0.05
            uv_padding = 0.002
        elif img_res >= 1024:
            bake_margin = 0.1
            uv_padding = 0.005
        elif img_res >= 512:
            bake_margin = 0.25
            uv_padding = 0.01
        elif img_res > 64:
            uv_padding = 0.01
            
        # Grab original UV map, so any diffuse/normal textures are mapped correctly
        orig_uv_actual = ob.data.uv_layers.active.name
        orig_uv = ob.data.uv_layers[0].name
        
        # Also grab the original mesh data so we can remap the material assignments
        # - if we have more than one material assigned to our object
        if len(ob.data.materials) > 1:
            orig_polys = [0] * len(ob.data.polygons)
            for f in ob.data.polygons:
                orig_polys[f.index] = f.material_index
        
        uvs_are_new = False
        bpy.ops.object.mode_set(mode='OBJECT')
        # Recreate the UV map if it's a different resolution than we want now
        if ("thug_last_bake_res" in ob and ob["thug_last_bake_res"] != img_res) \
        or ("thug_last_bake_type" in ob and ob["thug_last_bake_type"] != ob.thug_lightmap_type) \
        or ("thug_last_bake_res" not in ob or "thug_last_bake_type" not in ob)\
        or scene.thug_bake_force_remake == True:
            if group_name == '':
                print("Removing existing images/UV maps.")
                if ob.data.uv_layers.get('Lightmap'):
                    ob.data.uv_textures.remove(ob.data.uv_textures['Lightmap'])
                if bpy.data.images.get(lightmap_name):
                    _img = bpy.data.images.get(lightmap_name)
                    _img.user_clear()
                    bpy.data.images.remove(_img)
                
        if not ob.data.uv_layers.get('Lightmap'):
            if group_name != '':
                print("ERROR: Object {} is part of group {}, but has no Lightmap UVs. Unable to bake.".format(ob.name, group_name))
                continue
            uvs_are_new = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            # Create a new UV layer for the ambient occlusion map
            bpy.ops.mesh.uv_texture_add({"object": ob})
            ob.data.uv_layers[len(ob.data.uv_layers)-1].name = 'Lightmap'
            ob.data.uv_textures['Lightmap'].active = True
            #ob.data.uv_textures['Lightmap'].active_render = True
            
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            # Unwrap the mesh based on the type specified on the object properties!
            if ob.thug_lightmap_type == 'Lightmap':
                bpy.ops.uv.lightmap_pack(
                    PREF_CONTEXT='ALL_FACES', PREF_PACK_IN_ONE=True, PREF_NEW_UVLAYER=False,
                    PREF_APPLY_IMAGE=False, PREF_IMG_PX_SIZE=img_res, 
                    PREF_BOX_DIV=48, PREF_MARGIN_DIV=bake_margin)
            elif ob.thug_lightmap_type == 'Smart':
                bpy.ops.uv.smart_project()
            else:
                raise Exception("Unknown lightmap type specified on object {}".format(ob.name))
                
            
        else:
            ob.data.uv_textures['Lightmap'].active = True
            #ob.data.uv_textures['Lightmap'].active_render = True
            
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        if uvs_are_new and scene.thug_bake_pad_uvs == True:
            # Argh, Blender's UV projection sometimes creates seams on the edges of the image!
            # Add some padding by scaling the whole thing down a little bit
            scale_uvs(ob.data.uv_layers['Lightmap'], mathutils.Vector((1.0-uv_padding, 1.0-uv_padding)))
        
        #-----------------------------------------------------------------------------------------
        # For FULL bakes, we just need to loop through all the Cycles mats and add the image slot
        # to store the bake result, pretty easy!
        if scene.thug_bake_type == 'FULL' or scene.thug_bake_type == 'FULL_BI' or scene.thug_bake_type == 'LIGHT' or scene.thug_bake_type == 'INDIRECT' or scene.thug_bake_type == 'SHADOW':
            orig_index = ob.active_material_index
            store_materials(ob)
            
            # Create a new image to bake the lighting in to, if it doesn't exist
            if not bpy.data.images.get(lightmap_name):
                bpy.ops.image.new(name=lightmap_name, width=img_res, height=img_res)
                image = bpy.data.images[lightmap_name]
            else:
                image = bpy.data.images.get(lightmap_name)
            image.generated_width = img_res
            image.generated_height = img_res
            image.use_fake_user = True
            
            # Create or retrieve the lightmap texture
            tex_name = "Baked_{}".format(ob.name)
            if group_name != '':
                tex_name = "Baked_{}".format(group_name)
            blender_tex = get_texture(tex_name)
            blender_tex.image = image
            blender_tex.thug_material_pass_props.blend_mode = 'vBLEND_MODE_BLEND'
            if scene.thug_bake_type == 'LIGHT' or scene.thug_bake_type == 'INDIRECT' or scene.thug_bake_type == 'SHADOW':
                blender_tex.thug_material_pass_props.blend_mode = 'vBLEND_MODE_MODULATE'
            
            if is_cycles:
                for mat in ob.data.materials:
                    node_d = get_cycles_node(mat.node_tree.nodes, 'Bake Result', 'ShaderNodeTexImage')
                    node_d.image = blender_tex.image
                    node_d.location = (-880,40)
                    mat.node_tree.nodes.active = node_d
                    # Add a UV map node 
                    node_uv = get_cycles_node(mat.node_tree.nodes, 'Bake Result UV', 'ShaderNodeUVMap')
                    node_uv.location = (-1060,60)
                    node_uv.uv_map = "Lightmap"
                    mat.node_tree.links.new(node_d.inputs[0], node_uv.outputs[0]) # Bake Texture UV
            else:
                for d in ob.data.uv_textures['Lightmap'].data:
                    d.image = image
                    
        #-----------------------------------------------------------------------------------------
        # For BI lighting/AO bakes, it's more complicated! We clear out the materials, add a temp material
        # to bake the result onto, then restore the original materials and apply the bake texture
        else:
            # First, we need to store the materials assigned to the object
            # As baking will fail if there are any materials without textures
            orig_mats = store_materials(ob, True)
            orig_index = ob.active_material_index
            if orig_index == None or orig_index < 0:
                orig_index = 0
                
            # Create a new image to bake the lighting in to, if it doesn't exist
            if not bpy.data.images.get(lightmap_name):
                bpy.ops.image.new(name=lightmap_name, width=img_res, height=img_res)
                image = bpy.data.images[lightmap_name]
            else:
                image = bpy.data.images.get(lightmap_name)
            # Always set width and height, in case the user changed the lightmap res
            image.generated_width = img_res
            image.generated_height = img_res
            image.use_fake_user = True
            
            if not is_cycles:
                for d in ob.data.uv_textures['Lightmap'].data:
                    d.image = image
                    
            # Create or retrieve the lightmap material
            if not bpy.data.textures.get("Baked_{}".format(ob.name)):
                blender_tex = bpy.data.textures.new("Baked_{}".format(ob.name), "IMAGE")
            else:
                blender_tex = bpy.data.textures.get("Baked_{}".format(ob.name))
            blender_tex.image = image
            blender_tex.thug_material_pass_props.blend_mode = 'vBLEND_MODE_MODULATE'
            blender_tex.thug_material_pass_props.blend_fixed_alpha = 108
            blender_mat = get_material("Lightmap_" + ob.name)
            if not blender_mat.texture_slots.get(blender_tex.name):
                tex_slot = blender_mat.texture_slots.add()
            else:
                tex_slot = blender_mat.texture_slots.get(blender_tex.name)
            tex_slot.texture = blender_tex
            tex_slot.uv_layer = str('Lightmap')
            tex_slot.blend_type = 'MIX'
            blender_mat.use_textures[0] = True
            if not ob.data.materials.get(blender_mat.name):
                ob.data.materials.append(blender_mat)
            
            if is_cycles:
                # Create a material tree node in Cycles
                blender_mat.use_nodes = True
                # Look for diffuse and normal textures in the original active material
            test_mat = orig_mats[orig_index]
            tx_d = mat_get_pass(test_mat, 'Diffuse')
            tx_n = mat_get_pass(test_mat, 'Normal')
            if is_cycles:
                setup_cycles_nodes(blender_mat.node_tree, tx_d, tx_n, scene.thug_lightmap_color, orig_uv)
                # Finally, add the result texture, this is what will actually store the bake
                node_bake = get_cycles_node(blender_mat.node_tree.nodes, 'Bake Result', 'ShaderNodeTexImage')
                node_bake.image = blender_tex.image
                node_bake.location = (-160,100)
                node_bake.select = True
                blender_mat.node_tree.nodes.active = node_bake
            else:
                blender_mat.use_textures[0] = False
                if tx_n != None:
                    normal_slot = blender_mat.texture_slots.add()
                    normal_slot.texture = tx_n
                    normal_slot.uv_layer = orig_uv
                    normal_slot.blend_type = 'MIX'
                    normal_slot.use_map_normal = True
                
            
        #return {"FINISHED"}
        
        # Bake the lightmap for Cycles!
        if is_cycles:
            if scene.thug_bake_type == 'SHADOW':
                scene.cycles.bake_type = 'SHADOW'
            else:
                scene.cycles.bake_type = 'DIFFUSE'
                if scene.thug_bake_type == 'FULL' or scene.thug_bake_type == 'FULL_BI':
                    bpy.context.scene.render.bake.use_pass_color = True
                else:
                    bpy.context.scene.render.bake.use_pass_color = False
                    if scene.thug_bake_type == 'INDIRECT':
                        bpy.context.scene.render.bake.use_pass_direct = False
                    else:
                        bpy.context.scene.render.bake.use_pass_direct = True
                        
            if scene.thug_bake_automargin:
                scene.render.bake_margin = 2 # Used to be bake_margin
            if ob.thug_lightmap_quality != 'Custom':
                if ob.thug_lightmap_quality == 'Draft':
                    scene.cycles.samples = 32
                    scene.cycles.max_bounces = 2
                if ob.thug_lightmap_quality == 'Preview':
                    scene.cycles.samples = 64
                    scene.cycles.max_bounces = 2
                if ob.thug_lightmap_quality == 'Good':
                    scene.cycles.samples = 128
                    scene.cycles.max_bounces = 3
                if ob.thug_lightmap_quality == 'High':
                    scene.cycles.samples = 256
                    scene.cycles.max_bounces = 3
                if ob.thug_lightmap_quality == 'Ultra':
                    scene.cycles.samples = 512
                    scene.cycles.max_bounces = 3
            print("Using {} bake quality. Samples: {}, bounces: {}".format(ob.thug_lightmap_quality, scene.cycles.samples, scene.cycles.max_bounces))
            if scene.thug_bake_type == 'SHADOW':
                bpy.ops.object.bake(type='SHADOW')
            else:
                bpy.ops.object.bake(type='DIFFUSE')
            
        # Bake the lightmap for BI!
        else:
            print("Baking to texture...")
            bpy.ops.object.bake_image()
            if 'blender_mat' in locals():
                blender_mat.use_textures[0] = True
            
        print("Object " + ob.name + " baked to texture " + blender_tex.name)
        
        baked_obs.append(ob.name)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        if scene.thug_bake_type == 'FULL' or scene.thug_bake_type == 'FULL_BI' or scene.thug_bake_type == 'LIGHT' or scene.thug_bake_type == 'INDIRECT' or scene.thug_bake_type == 'SHADOW':
            ob.active_material_index = orig_index
        
        else:
            # Now, for the cleanup! Let's get everything back to BI and restore the missing mats
            #blender_mat.use_nodes = False
            restore_mats(ob, orig_mats)
            bpy.data.materials.remove(blender_mat)
            # Assign the texture pass from the bake material to the base material(s)
            ob.active_material_index = orig_index
            #invert_image(blender_tex.image, scene.thug_lightmap_clamp)
            
        save_baked_texture(blender_tex.image, _folder)
        
        if scene.lightmap_view != 'LIGHTMAP':
            ob.data.uv_textures[orig_uv_actual].active = True
            ob.data.uv_textures[orig_uv_actual].active_render = True
        
        for p in ob.data.polygons:
            ob.data.uv_textures['Lightmap'].data[p.index].image = blender_tex.image
            
        if scene.thug_bake_type == 'FULL' or scene.thug_bake_type == 'FULL_BI':
            ob.select = False
        else:
            # If there is more than one material, restore the per-face material assignment
            if len(ob.data.materials) > 1:
                restore_mat_assignments(ob, orig_polys)
        ob.select = False
        ob["is_baked"] = True
        ob["thug_last_bake_res"] = img_res
        ob["thug_last_bake_type"] = ob.thug_lightmap_type
        # Done!!
        wm.progress_update(mesh_num)
    
    # Once we have finished baking everything, we then duplicate the materials and assign
    # the lightmap texture to them - should be faster than doing it during the baking step
    print("Baking complete. Setting up lightmapped materials...")
    for obname in baked_obs:
        ob = bpy.data.objects.get(obname)
        if not ob: 
            raise Exception("Unable to find baked object {}".format(obname))
        for mat in ob.data.materials:
            mat.use_nodes = False
        for mat_slot in ob.material_slots:
            if group_name != '':
                group_mat_name = '{}_{}'.format(mat_slot.material.name, group_name)
                mat_slot.material = get_material(group_mat_name, mat_slot.material)
                blender_tex = bpy.data.textures.get("Baked_{}".format(group_name))
            else:
                mat_slot.material = mat_slot.material.copy()
                blender_tex = bpy.data.textures.get("Baked_{}".format(obname))
                
            # Add the lightmap into the new UG+ material system, for the corresponding lightmap slot
            if scene.thug_bake_slot == 'DAY':
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap.tex_image = blender_tex.image
            elif scene.thug_bake_slot == 'EVENING':
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap2.tex_image = blender_tex.image
            elif scene.thug_bake_slot == 'NIGHT':
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap3.tex_image = blender_tex.image
            elif scene.thug_bake_slot == 'MORNING':
                mat_slot.material.thug_material_props.ugplus_matslot_lightmap4.tex_image = blender_tex.image
            
            # Also add the image to the legacy material system
            if not mat_slot.material.texture_slots.get(blender_tex.name):
                slot = mat_slot.material.texture_slots.add()
            else:
                slot = mat_slot.material.texture_slots.get(blender_tex.name)
            slot.texture = blender_tex
            slot.uv_layer = str('Lightmap')
            if scene.thug_bake_type == 'FULL' or scene.thug_bake_type == 'FULL_BI':
                slot.blend_type = 'MIX'
            else:
                slot.blend_type = 'MULTIPLY'
        print("Processed object: {}".format(obname))
          
    print("COMPLETE! Thank you for your patience!")
    wm.progress_end()
    
    # Switch back to the original engine, if it wasn't Cycles
    if previous_engine != scene.render.engine:
        scene.render.engine = previous_engine
    # Toggle use_nodes on the whole scene materials, if desired (depending on the engine we are on)
    if previous_engine == 'BLENDER_RENDER':
        for mat in bpy.data.materials:
            mat.use_nodes = False
    elif previous_engine == 'CYCLES':
        for mat in bpy.data.materials:
            mat.use_nodes = True
    
        
#----------------------------------------------------------------------------------
#- Fills baked materials with empty material passes to ensure that the 
#- UV indices line up with the material pass indices
#----------------------------------------------------------------------------------
def fill_bake_materials():
    meshes = [o for o in bpy.data.objects if o.type == 'MESH' and "is_baked" in o and o["is_baked"] == True]
    processed_mats = []
    for ob in meshes:
        for mat in ob.data.materials:
            #if mat.name in processed_mats: continue
            if not hasattr(mat, 'texture_slots'): continue
            passes = [tex_slot for tex_slot in mat.texture_slots if tex_slot and tex_slot.use and tex_slot.use_map_color_diffuse][:4]
            pass_number = -1
            passes_to_add = 0
            baked_slot = None
            for slot in passes:
                pass_number += 1
                if slot.name.startswith("Baked_"):
                    uv_pass = get_uv_index(ob, slot.uv_layer)
                    if uv_pass < 0:
                        raise Exception("Unable to find UV index for map {}".format(slot.uv_layer))
                    if pass_number != uv_pass:
                        print("Lightmap tex {} (pass #{}) doesn't match lightmap UV index {}!".format(slot.name, pass_number, uv_pass))
                        passes_to_add = uv_pass - pass_number
                        baked_slot = slot.texture
                        mat.texture_slots.clear(pass_number)
                        break
            if passes_to_add != 0:
                filler_slot = get_empty_tex()
                for i in range(0, passes_to_add):
                    _slot = mat.texture_slots.add()
                    _slot.texture = filler_slot
            if baked_slot:
                _slot = mat.texture_slots.add()
                _slot.texture = baked_slot
                _slot.uv_layer = "Lightmap"
                _slot.blend_type = "MIX"
            processed_mats.append(mat.name)
            

#----------------------------------------------------------------------------------
#- Renders the faces of the desired cubemap
#----------------------------------------------------------------------------------
def render_cubemap(probe):
    import subprocess, shutil, datetime
    import platform
    wine = [] if platform.system() == "Windows" else ["wine"]
    j = os.path.join
    
    probe_type = probe.thug_empty_props.empty_type
    src_resolution = probe.thug_cubemap_props.resolution
    dst_resolution = probe.thug_cubemap_props.resolution
    if probe_type == 'LightProbe': # Use fixed resolution for light probes
        dst_resolution = 32
        
    scene = bpy.context.scene
    orig_res_x = scene.render.resolution_x
    orig_res_y = scene.render.resolution_y
    orig_res_pct = scene.render.resolution_percentage
    
    print("Attempting to render cubemap from probe {}...".format(probe.name))
        
    # Set render resolution to match the probe setting
    scene.render.resolution_x = int(src_resolution)
    scene.render.resolution_y = int(src_resolution)
    scene.render.resolution_percentage = 100
    
    # Look for camera
    cam_found = False
    for obj in probe.children:
        if obj.type == 'CAMERA':
            camera_ob = obj
            cam_found = True
            
    if not cam_found:
        print("Unable to find camera object D:")
        raise Exception("Camera attached to cubemap probe {} not found.".format(probe.name))
    
    # Set camera properties
    camera_ob.data.lens_unit = 'FOV'
    camera_ob.data.angle = math.radians(90)
    camera_ob.data.clip_start = 0.1
    camera_ob.data.clip_end = 1000000.0
    camera_ob.data.shift_x = 0
    camera_ob.data.shift_y = 0
    
    scene.camera = camera_ob
    
    # Create destination folder for the textures
    _lightmap_folder = bpy.path.basename(bpy.context.blend_data.filepath)[:-6] # = Name of blend file
    _folder = bpy.path.abspath("//Tx_Cubemap\\{}".format(_lightmap_folder))
    os.makedirs(_folder, 0o777, True)
    
    # Rotate camera and render each face!
    print("Rendering FRONT face...")
    probe.rotation_euler = [math.radians(90), 0, math.radians(-90)] # FRONT
    probe.rotation_euler = [math.radians(90), 0, math.radians(90)] # FRONT
    #probe.rotation_euler = [math.radians(90), 0, 0] # FRONT
    scene.render.filepath = "{}/{}_{}.png".format(_folder, probe.name, 'front')
    bpy.ops.render.render( write_still=True )
    
    print("Rendering BACK face...")
    probe.rotation_euler = [math.radians(90), 0, math.radians(90)] # BACK
    probe.rotation_euler = [math.radians(90), 0, math.radians(-90)] # BACK
    #probe.rotation_euler = [math.radians(90), 0, math.radians(180)] # BACK
    scene.render.filepath = "{}/{}_{}.png".format(_folder, probe.name, 'back')
    bpy.ops.render.render( write_still=True )
    
    print("Rendering LEFT face...")
    probe.rotation_euler = [math.radians(90), 0, 0] # LEFT
    probe.rotation_euler = [math.radians(90), 0, math.radians(180)] # LEFT
    #probe.rotation_euler = [math.radians(90), 0, math.radians(90)] # LEFT
    scene.render.filepath = "{}/{}_{}.png".format(_folder, probe.name, 'left')
    bpy.ops.render.render( write_still=True )
    
    print("Rendering RIGHT face...")
    probe.rotation_euler = [math.radians(90), 0, math.radians(180)] # RIGHT
    probe.rotation_euler = [math.radians(90), 0, 0] # RIGHT
    #probe.rotation_euler = [math.radians(90), 0, math.radians(-90)] # RIGHT
    scene.render.filepath = "{}/{}_{}.png".format(_folder, probe.name, 'right')
    bpy.ops.render.render( write_still=True )
    
    print("Rendering UP face...")
    probe.rotation_euler = [math.radians(180), 0, math.radians(180)] # UP
    scene.render.filepath = "{}/{}_{}.png".format(_folder, probe.name, 'up')
    bpy.ops.render.render( write_still=True )
    
    print("Rendering DOWN face...")
    probe.rotation_euler = [0, 0, math.radians(180)] # DOWN
    scene.render.filepath = "{}/{}_{}.png".format(_folder, probe.name, 'down')
    bpy.ops.render.render( write_still=True )
    
    print("Finished rendering! Restoring render settings...")
    # Return to front-facing orientation
    probe.rotation_euler = [math.radians(90), 0, 0]
    # Restore render settings
    scene.render.resolution_x = orig_res_x
    scene.render.resolution_y = orig_res_y
    scene.render.resolution_percentage = orig_res_pct
    
    # Attempt to auto-generate the DX9 DDS cubemap!
    print("Done. Attempting to generate DDS file {}.dds...".format(probe.name))
    
    addon_prefs = bpy.context.user_preferences.addons[ADDON_NAME].preferences
    base_files_dir_error = prefs._get_base_files_dir_error(addon_prefs)
    if base_files_dir_error:
        self.report({"ERROR"}, "Base files directory error: {} Check the base files directory addon preference. Unable to generate DDS file.".format(base_files_dir_error))
        return False
    base_files_dir = addon_prefs.base_files_dir
    
    texassemble_args = [
        j(base_files_dir, "texassemble.exe"),
        "cube",
        "-w",
        "{}".format(src_resolution),
        "-h",
        "{}".format(src_resolution),
        "-o",
        "{}/{}.dds".format(_folder, probe.name),
        "-y",
        "{}/{}_{}.png".format(_folder, probe.name, 'front'),
        "{}/{}_{}.png".format(_folder, probe.name, 'back'),
        "{}/{}_{}.png".format(_folder, probe.name, 'up'),
        "{}/{}_{}.png".format(_folder, probe.name, 'down'),
        "{}/{}_{}.png".format(_folder, probe.name, 'left'),
        "{}/{}_{}.png".format(_folder, probe.name, 'right')
    ]
    
    cmft_args_irradiance = [
        j(base_files_dir, "cmft.exe"),
        "--input \"{}\\{}.dds\"".format(_folder, probe.name),
        
        "--filter irradiance",
        "--srcFaceSize {}".format(src_resolution),
        "--dstFaceSize {}".format(dst_resolution),
        "--outputNum 1",
        "--output0 \"{}\\{}\"".format(_folder, probe.name),
        "--output0params dds,bgra8,cubemap"
    ]
    cmft_args_radiance = [
        j(base_files_dir, "cmft.exe"),
        "--input \"{}\\{}.dds\"".format(_folder, probe.name),
        
        "--filter radiance",
        "--srcFaceSize {}".format(src_resolution),
        "--excludeBase true",
        "--mipCount 7",
        "--glossScale 10",
        "--glossBias 3",
        "--excludeBase true",
        "--lightingModel blinnbrdf",
        "--dstFaceSize {}".format(dst_resolution),
        "--numCpuProcessingThreads 4",
        "--useOpenCL true",
        "--clVendor anyGpuVendor",
        "--deviceType gpu",
        "--deviceIndex 0",
        "--inputGammaNumerator 1.0",
        "--inputGammaDenominator 1.0",
        "--outputGammaNumerator 1.0",
        "--outputGammaDenominator 1.0",
        "--generateMipChain false",
        "--outputNum 1",
        "--output0 \"{}\\{}\"".format(_folder, probe.name),
        "--output0params dds,bgra8,cubemap",
        "--edgeFixup warp"
    ]
    cmft_args = cmft_args_irradiance if probe_type == 'LightProbe' else cmft_args_radiance
    
    dds_output = subprocess.run(wine + texassemble_args, stdout=subprocess.PIPE)
    print(dds_output)
    
    print("Cubemap assembled. Running radiance/irradiance filter on {}.dds...".format(probe.name))
    
    cmft_output = subprocess.run(" ".join(wine + cmft_args), stdout=subprocess.PIPE)
    print(cmft_output)
    
    probe.thug_cubemap_props.exported = True
    print("Finished!")
    
      
def change_bake_slot(self, context):
    scene = context.scene
    if scene.thug_bake_slot == 'DAY':
        search_for = 'LM_DAY_'
    elif scene.thug_bake_slot == 'EVENING':
        search_for = 'LM_EVENING_'
    elif scene.thug_bake_slot == 'NIGHT':
        search_for = 'LM_NIGHT_'
    elif scene.thug_bake_slot == 'MORNING':
        search_for = 'LM_MORNING_'
        
    for mat in bpy.data.materials:
        if not hasattr(mat, 'texture_slots'): continue
        passes = [tex_slot for tex_slot in mat.texture_slots]
        for slot in passes:
            if hasattr(slot, 'texture') and slot.texture.name.startswith("Baked_"):
                ob_name = slot.texture.name[6:]
                print("Searching for...{}{}".format(search_for, ob_name))
                if bpy.data.images.get('{}{}'.format(search_for, ob_name)):
                    slot.texture.image = bpy.data.images.get('{}{}'.format(search_for, ob_name))

def change_lightmap_view(self, context):
    meshes = [o for o in bpy.data.objects if o.type == 'MESH' ]
    scene = context.scene

    if scene.lightmap_view == 'LIGHTMAP':
        for obj in meshes:
            obdata = obj.data
            if not obdata.uv_layers.get('Lightmap'):
                continue
            obdata.uv_textures['Lightmap'].active = True
            
    elif scene.lightmap_view == 'DEFAULT':
        for obj in meshes:
            obdata = obj.data
            if not obdata.uv_layers.get('Lightmap'):
                continue
            obdata.uv_textures[0].active = True
    
    

def all_objects_visible(self, context):
    scene = context.scene
    group = scene.thug_lightmap_groups[scene.thug_lightmap_groups_index]
    isAllObjectsVisible = True
    bpy.ops.object.select_all(action='DESELECT')
    for thisObject in bpy.data.groups[group.name].objects:
        isThisObjectVisible = False
        # scene.objects.active = thisObject
        for thisLayerNumb in range(20):
            if thisObject.layers[thisLayerNumb] is True and scene.layers[thisLayerNumb] is True:
                isThisObjectVisible = True
                break
        # If object is on an invisible Layer
        if isThisObjectVisible is False:
            isAllObjectsVisible = False
    return isAllObjectsVisible

    
def lightmap_group_exists(self, context, use_report=True):
    scene = context.scene
    group = scene.thug_lightmap_groups[scene.thug_lightmap_groups_index]

    if group.name in bpy.data.groups:
        return True
    else:
        if use_report:
            self.report({'INFO'}, "No such group: {}".format(group.name))
        return False
    
def register_props_bake():
    bpy.types.Scene.lightmap_view = EnumProperty(items=(
        ("DEFAULT", "Default", "Default view"),
        ("LIGHTMAP", "Lightmap Only", "Shows only the lightmap textures/vertex colors"),
        ), name="View Mode", default="DEFAULT", update=change_lightmap_view)
    bpy.types.Scene.thug_lightmap_scale = EnumProperty(
        name="Lightmap Scale",
        items=[
            ("0.25", "0.25", ""),
            ("0.5", "0.5", ""),
            ("1", "1", ""),
            ("2", "2", ""),
            ("4", "4", ""),
            ("8", "8", "")],
        default="1", 
        description="Scales the resolution of all lightmaps by the specified factor")
    bpy.types.Scene.thug_lightmap_uglymode = BoolProperty(
        name="Performance Mode",
        default=False, 
        description="Disable all Cycles materials when baking. Bakes faster, but with much less accuracy")
    bpy.types.Scene.thug_lightmap_clamp = FloatProperty(
        name="Shadow Intensity",
        description="Controls the maximum intensity of shadowed areas. Reduce in low-light scenes if you need to improve visibility",
        min=0, max=1.0, default=1.0)
    bpy.types.Scene.thug_lightmap_color = FloatVectorProperty(name="Ambient Color",
                       subtype='COLOR',
                       default=(1.0, 1.0, 1.0, 1.0),
                       size=4,
                       min=0.0, max=1.0,
                       description="Lightmaps are baked onto a surface of this color")
    bpy.types.Scene.thug_bake_type = EnumProperty(
        name="Bake Type",
        items=[
            ("LIGHT", "Lighting Only (Cycles)", "(Uses the Cycles render engine) Bake lighting and mix with original textures. Preserves texture resolution, but less accurate lighting"),
            ("FULL", "Full Diffuse (Cycles)", "(Uses the Cycles render engine) Bake everything onto a single texture. The most accurate results, but lowers base texture resolution"),
            ("VERTEX_COLORS", "Vertex Colors (BR)", "Bake lighting to vertex colors. Fast and cheap, accuracy depends on mesh density"),
            ("LIGHT_BI", "Lighting Only (BR)", "Bake lighting to texture and mix with original textures"),
            ("FULL_BI", "Full Diffuse (BR)", "Bake everything to a single texture"),
            ("AO", "Ambient Occlusion (BR)", "Bakes only ambient occlusion. Useful for models/skins, or scenes where you intend to have dynamic lighting"),
            ("SHADOW", "Shadow (Cycles)", "Bakes only shadow contributions. Faster, not photorealistic"),
            ("INDIRECT", "PBR Lightmap (Cycles)", "Bakes indirect lighting and shadows for PBR shaders (UG+/Classic)")
            ],
        default="LIGHT_BI", 
        description="Type of bakes to use for this scene")
    bpy.types.Scene.thug_bake_slot = EnumProperty(
        name="Bake Slot",
        items=[
            ("DAY", "Day (Default)", "Bakes lighting into the Day TOD slot"),
            ("EVENING", "Evening", "Bakes lighting into the Evening TOD slot"),
            ("NIGHT", "Night", "Bakes lighting into the Night TOD slot"),
            ("MORNING", "Morning", "Bakes lighting into the Morning TOD slot")],
        default="DAY", 
        description="(Underground+ 1.5+ only) TOD slot to bake lighting into. Multiple TOD bakes are only supported by the new material system", update=change_bake_slot)
        
    bpy.types.Scene.thug_bake_automargin = BoolProperty(name="Calculate Margins", default=True, description="Automatically determine the ideal bake margin. If unchecked, uses the margin specified in the Blender bake settings")                       
    bpy.types.Scene.thug_bake_force_remake = BoolProperty(name="Force new UVs", default=False, description="Always discards and recreates the lightmap UVs. Slower, use only as a shortcut if you are making changes to meshes or need to fix UV issues")                       
    bpy.types.Scene.thug_bake_pad_uvs = BoolProperty(name="Pad UVs", default=True, description="Adds a 'safe zone' to the edges of the UV map. Use if you are experiencing problems with seams/gaps in bake results")                       
    
    bpy.types.Object.thug_lightmap_resolution = EnumProperty(
        name="Lightmap Resolution",
        items=[
            ("16", "16", ""),
            ("32", "32", ""),
            ("64", "64", ""),
            ("128", "128", ""),
            ("256", "256", ""),
            ("512", "512", ""),
            ("1024", "1024", ""),
            ("2048", "2048", ""),
            ("4096", "4096", ""),
            ("8192", "8192", "")],
        default="128", 
        description="Controls the resolution (squared) of baked lightmaps")
    bpy.types.Object.thug_lightmap_quality = EnumProperty(
        name="Lightmap Quality",
        items=[
            ("Draft", "Draft", ""),
            ("Preview", "Preview", ""),
            ("Good", "Good", ""),
            ("High", "High", ""),
            ("Ultra", "Ultra", ""),
            ("Custom", "Custom", "Uses existing Cycles render settings")],
        default="Preview", 
        description="Preset controls for the bake quality.")
    bpy.types.Object.thug_lightmap_type = EnumProperty(
        name="UV Type",
        items=[
            ("Lightmap", "Lightmap", "Lightmap pack with preset margins"),
            ("Smart", "Smart", "Smart UV projection with default settings")],
        default="Lightmap", 
        description="Determines the type of UV unwrapping done on the object for the bake.")
    
    bpy.types.Object.thug_lightmap_merged_objects = CollectionProperty(type=THUGMergedObjects)
    bpy.types.Object.thug_lightmap_group_id = IntProperty(default=-1)
    bpy.types.Scene.thug_lightmap_groups = CollectionProperty(type=THUGLightmapGroup)
    bpy.types.Scene.thug_lightmap_groups_index = IntProperty()
        
# CLASSES
#############################################
class THUGMergedObjects_UVLayers(bpy.types.PropertyGroup):
    name = StringProperty(default="")
class THUGMergedObjects_VertexGroups(bpy.types.PropertyGroup):
    name = StringProperty(default="")
class THUGMergedObjects_Groups(bpy.types.PropertyGroup):
    name = StringProperty(default="")
class THUGMergedObjects(bpy.types.PropertyGroup):
    name = StringProperty()
    vertex_groups = CollectionProperty(type=THUGMergedObjects_VertexGroups)
    groups = CollectionProperty(type=THUGMergedObjects_Groups)
    uv_layers = CollectionProperty(type=THUGMergedObjects_UVLayers)
    
class THUGLightmapGroup(bpy.types.PropertyGroup):
    name = StringProperty(default="", description="Name for this lightmap group")
    bake = BoolProperty(default=True)
    unwrap_type = EnumProperty(
        name="UV Type",
        items=[
            ("Lightmap", "Lightmap", "Lightmap pack with preset margins"),
            ("Smart", "Smart", "Smart UV projection with default settings")],
    )
    resolution = EnumProperty(
        name="Resolution",
        items=(('256', '256', ''),
               ('512', '512', ''),
               ('1024', '1024', ''),
               ('2048', '2048', ''),
               ('4096', '4096', ''),
               ('8192', '8192', ''),
               ('16384', '16384', ''),
               ),
        default='1024',
        description="Controls the resolution (squared) of baked lightmaps"
    )
    template_list_controls = StringProperty(
        default="bake",
        options={"HIDDEN"},
    )
    
# OPERATORS
#############################################
class THUG_AddSelectedToGroup(bpy.types.Operator):
    bl_idname = "scene.thug_bake_add_selected_to_group"
    bl_label = "Add to Group"
    bl_description = "Add selected objects to lightmap group"

    def execute(self, context):
        scene = context.scene
        group_name = scene.thug_lightmap_groups[scene.thug_lightmap_groups_index].name

        # Create a new group if it was deleted
        obj_group = bpy.data.groups.get(group_name)
        if obj_group is None:
            obj_group = bpy.data.groups.new(group_name)

        # Add objects to a group
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        for object in context.selected_objects:
            if object.type == 'MESH' and object.name not in obj_group.objects:
                obj_group.objects.link(object)
                object.thug_lightmap_group_id = scene.thug_lightmap_groups_index

        return {'FINISHED'}


class THUG_SelectGroup(bpy.types.Operator):
    bl_idname = "scene.thug_bake_select_group"
    bl_label = "Select Group"
    bl_description = "Select objects in this lightmap group"

    def execute(self, context):
        scene = context.scene
        group_name = scene.thug_lightmap_groups[scene.thug_lightmap_groups_index].name

        # Check if group exists
        if lightmap_group_exists(self, context) is False:
            return {'CANCELLED'}

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.object.select_all(action='DESELECT')
        obj_group = bpy.data.groups[group_name]
        for object in obj_group.objects:
            object.select = True
        return {'FINISHED'}


class THUG_RemoveFromGroup(bpy.types.Operator):
    bl_idname = "scene.thug_bake_remove_selected"
    bl_label = "Remove Selected"
    bl_description = "Unbake and remove selected objects from lightmap group"

    def execute(self, context):
        scene = context.scene

        # Check if group exists
        if lightmap_group_exists(self, context) is False:
            return {'CANCELLED'}

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        for group in scene.thug_lightmap_groups:
            group_name = group.name
            obj_group = bpy.data.groups[group_name]
            for object in context.selected_objects:
                scene.objects.active = object
                if object.type == 'MESH' and object.name in obj_group.objects:
                    # Remove UV channel
                    tex = object.data.uv_textures.get('Lightmap')
                    if tex is not None:
                        object.data.uv_textures.remove(tex)

                    # Remove from group
                    obj_group.objects.unlink(object)
                    object.hide_render = False
                    object.thug_lightmap_group_id = -1
                    
                    # If this object is marked as baked, unbake it
                    if ("is_baked" in object and object["is_baked"] == True):
                        orig_polys = [0] * len(object.data.polygons)
                        for f in object.data.polygons:
                            orig_polys[f.index] = f.material_index
                        unbake(object)
                        bpy.context.scene.objects.active = object
                        object.select = True
                        restore_mat_assignments(object, orig_polys)
                        object.select = False
                    

        return {'FINISHED'}

        
class THUG_AddLightmapGroup(bpy.types.Operator):
    bl_idname = "scene.thug_bake_add_lightmap_group"
    bl_label = "Add Lightmap Group"
    bl_description = "Adds a new Lightmap Group"

    name = StringProperty(name="Group Name", default='LightmapGroup', description="Name for this lightmap group")

    def execute(self, context):
        scene = context.scene
        obj_group = bpy.data.groups.new(self.name)

        item = scene.thug_lightmap_groups.add()
        item.name = obj_group.name
        scene.thug_lightmap_groups_index = len(scene.thug_lightmap_groups) - 1

        # Add selested objects to group
        for object in context.selected_objects:
            if object.type == 'MESH':
                obj_group.objects.link(object)
                object.thug_lightmap_group_id = scene.thug_lightmap_groups_index

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class THUG_DelLightmapGroup(bpy.types.Operator):
    bl_idname = "scene.thug_bake_del_lightmap_group"
    bl_label = "Delete Lightmap Group"
    bl_description = "Deletes selected Lightmap Group"

    def execute(self, context):
        scene = context.scene
        if len(scene.thug_lightmap_groups) > 0:
            idx = scene.thug_lightmap_groups_index
            group_name = scene.thug_lightmap_groups[idx].name

            # Remove group
            group = bpy.data.groups.get(group_name)
            if group is not None:
                # Unhide objects if they are hidden
                for obj in group.objects:
                    obj.hide_render = False
                    obj.hide = False
                bpy.data.groups.remove(group, do_unlink=True)

            # Remove lightmap group
            scene.thug_lightmap_groups.remove(scene.thug_lightmap_groups_index)
            scene.thug_lightmap_groups_index -= 1
            if scene.thug_lightmap_groups_index < 0:
                scene.thug_lightmap_groups_index = 0

        return {'FINISHED'}

        
class THUG_CreateLightmap(bpy.types.Operator):
    bl_idname = "object.thug_bake_create_lightmap"
    bl_label = "Create Lightmap"
    bl_description = "Creates a lightmap"

    group_name = StringProperty(default='')
    resolution = IntProperty(default=1024)

    def execute(self, context):
        scene = context.scene

        # Create/Update Image
        image = get_image(self.group_name, self.resolution, self.resolution)
        obj_group = bpy.data.groups[self.group_name]

        # non MESH objects for removal list
        NON_MESH_LIST = []
        uv_layer_name = 'Lightmap'
        
        for object in obj_group.objects:
            # Remove non MESH objects
            if object.type != 'MESH':
                NON_MESH_LIST.append(object)
            elif object.type == 'MESH' and len(object.data.vertices) == 0:
                NON_MESH_LIST.append(object)
            else:
                # Add Image to faces
                if object.data.uv_textures.active is None:
                    tex = object.data.uv_textures.new()
                    tex.name = uv_layer_name
                else:
                    if uv_layer_name not in object.data.uv_textures:
                        tex = object.data.uv_textures.new()
                        tex.name = uv_layer_name
                        tex.active = True
                        tex.active_render = True
                    else:
                        tex = object.data.uv_textures[uv_layer_name]
                        tex.active = True
                        tex.active_render = True

                for face_tex in tex.data:
                    face_tex.image = image

        # remove non MESH objects
        for object in NON_MESH_LIST:
            obj_group.objects.unlink(object)

        NON_MESH_LIST.clear()  # clear array

        return{'FINISHED'}

class THUG_MergeObjects(bpy.types.Operator):
    bl_idname = "object.thug_lightmap_merge_objects"
    bl_label = "Merge Objects"
    bl_description = "Merges objects and stores origins"

    group_name = StringProperty(default='')
    unwrap = BoolProperty(default=False)

    def execute(self, context):
        scene = context.scene

        bpy.ops.object.select_all(action='DESELECT')
        ob_merged_old = bpy.data.objects.get(self.group_name + "_mergedObject")
        if ob_merged_old is not None:
            ob_merged_old.select = True
            scene.objects.active = ob_merged_old
            bpy.ops.object.delete(use_global=True)

        me = bpy.data.meshes.new(self.group_name + '_mergedObject')
        ob_merge = bpy.data.objects.new(self.group_name + '_mergedObject', me)
        ob_merge.location = scene.cursor_location   # position object at 3d-cursor
        scene.objects.link(ob_merge)                # Link object to scene
        me.update()
        ob_merge.select = False

        bpy.ops.object.select_all(action='DESELECT')

        # We do the MergeList beacuse we will duplicate grouped objects
        mergeList = []
        for object in bpy.data.groups[self.group_name].objects:
            mergeList.append(object)

        for object in mergeList:
            # Make object temporary visible
            isObjHideSelect = object.hide_select
            object.hide = False
            object.hide_select = False

            bpy.ops.object.select_all(action='DESELECT')
            object.select = True

            # Activate lightmap UVs
            for uv in object.data.uv_textures:
                if uv.name == 'Lightmap':
                    uv.active = True
                    scene.objects.active = object

            # Duplicate temp object
            bpy.ops.object.select_all(action='DESELECT')
            object.select = True
            scene.objects.active = object
            bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
            activeNowObject = scene.objects.active
            activeNowObject.select = True

            # Hide render of original mesh
            object.hide_render = True
            object.hide = True
            object.select = False
            object.hide_select = isObjHideSelect

            # Remove UVs
            UVLIST = []
            for uv in activeNowObject.data.uv_textures:
                if uv.name != 'Lightmap':
                    UVLIST.append(uv.name)

            for uvName in UVLIST:
                tex = activeNowObject.data.uv_textures[uvName]
                activeNowObject.data.uv_textures.remove(tex)

            UVLIST.clear()

            # Create vertex groups for each selected object
            scene.objects.active = activeNowObject
            vgroup = activeNowObject.vertex_groups.new(name=object.name)
            vgroup.add(list(range(len(activeNowObject.data.vertices))), weight=1.0, type='ADD')

            # Save object name in merged object
            item = ob_merge.thug_lightmap_merged_objects.add()
            item.name = object.name

            # Add temp material if there are no material slots
            if not activeNowObject.data.materials:
                mat = get_material("_THUG_TEMP_MATERIAL_")
                activeNowObject.data.materials.append(mat)

            # Merge objects together
            bpy.ops.object.select_all(action='DESELECT')
            activeNowObject.select = True
            ob_merge.select = True
            scene.objects.active = ob_merge
            bpy.ops.object.join()

        mergeList.clear()

        bpy.ops.object.select_all(action='DESELECT')
        ob_merge.select = True
        scene.objects.active = ob_merge

        # Unhide all faces
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        if self.unwrap is True:
            groupProps = scene.thug_lightmap_groups[self.group_name]
            unwrapType = groupProps.unwrap_type

            bpy.ops.object.mode_set(mode='EDIT')
            if unwrapType == 'Smart':
                bpy.ops.uv.smart_project(
                    angle_limit=72.0, island_margin=0.1, user_area_weight=0.0)
            elif unwrapType == 'Lightmap':
                bpy.ops.uv.lightmap_pack(
                    PREF_CONTEXT='ALL_FACES', PREF_PACK_IN_ONE=True, PREF_NEW_UVLAYER=False,
                    PREF_APPLY_IMAGE=False, PREF_IMG_PX_SIZE=int(groupProps.resolution), PREF_BOX_DIV=48, PREF_MARGIN_DIV=0.1)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return{'FINISHED'}

        
        
class THUG_SeparateObjects(bpy.types.Operator):
    bl_idname = "object.thug_lightmap_separate_objects"
    bl_label = "Separate Objects"
    bl_description = "Separates objects and restores origins"

    group_name = StringProperty(default='')

    def execute(self, context):
        scene = context.scene

        ob_merged = bpy.data.objects.get(self.group_name + "_mergedObject")
        if ob_merged is not None:
            bpy.ops.object.select_all(action='DESELECT')
            ob_merged.hide = False
            ob_merged.select = True
            groupSeparate = bpy.data.groups.new(ob_merged.name)
            groupSeparate.objects.link(ob_merged)
            ob_merged.select = False

            doUnhidePolygons = False
            for ms_obj in ob_merged.thug_lightmap_merged_objects:
                # Select vertex groups and separate group from merged object
                bpy.ops.object.select_all(action='DESELECT')
                ob_merged.select = True
                scene.objects.active = ob_merged

                bpy.ops.object.mode_set(mode='EDIT')
                if doUnhidePolygons is False:
                    bpy.ops.mesh.reveal()
                    doUnhidePolygons = True

                bpy.ops.mesh.select_all(action='DESELECT')
                ob_merged.vertex_groups.active_index = ob_merged.vertex_groups[
                    ms_obj.name].index
                bpy.ops.object.vertex_group_select()
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                # scene.objects.active.select = False

                # Find separated object
                ob_separeted = None
                for obj in groupSeparate.objects:
                    if obj != ob_merged:
                        ob_separeted = obj
                        break

                # Copy UV coordinates to the original mesh
                if ms_obj.name in scene.objects:
                    ob_merged.select = False
                    ob_original = scene.objects[ms_obj.name]
                    isOriginalToSelect = ob_original.hide_select
                    ob_original.hide_select = False
                    ob_original.hide = False
                    ob_original.select = True
                    scene.objects.active = ob_separeted
                    bpy.ops.object.join_uvs()
                    ob_original.hide_render = False
                    ob_original.select = False
                    ob_original.hide_select = isOriginalToSelect
                    ob_original.data.update()

                # Delete separated object
                bpy.ops.object.select_all(action='DESELECT')
                ob_separeted.select = True
                bpy.ops.object.delete(use_global=False)

            # Delete duplicated object
            bpy.ops.object.select_all(action='DESELECT')
            ob_merged.select = True
            bpy.ops.object.delete(use_global=False)

        return{'FINISHED'}

        
class THUG_AutoUnwrap(bpy.types.Operator):
    bl_idname = "object.thug_lightmap_autounwrap"
    bl_label = "Auto Unwrapping"
    bl_description = "Automatically generate lightmap UVs"

    def execute(self, context):
        scene = context.scene

        # Store old context
        old_context = None
        if context.area:
            old_context = context.area.type

        # Check if group exists
        if lightmap_group_exists(self, context) is False:
            return {'CANCELLED'}

        group = scene.thug_lightmap_groups[scene.thug_lightmap_groups_index]
        if context.area:
            context.area.type = 'VIEW_3D'

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        if group.bake is True and bpy.data.groups[group.name].objects:
            # Check if objects are all on the visible layers
            isAllObjVisible = all_objects_visible(self, context)

            if isAllObjVisible is True:
                bpy.ops.object.thug_bake_create_lightmap(
                    group_name=group.name, resolution=int(group.resolution))
                bpy.ops.object.thug_lightmap_merge_objects(
                    group_name=group.name, unwrap=True)
                bpy.ops.object.thug_lightmap_separate_objects(group_name=group.name)
            else:
                self.report({'INFO'}, "Not all objects are visible!")

        # Set old context back
        if context.area:
            context.area.type = old_context

        return{'FINISHED'}


class THUG_ManualUnwrapStart(bpy.types.Operator):
    bl_idname = "object.thug_lightmap_manualunwrap"
    bl_label = "Manual Unwrap"
    bl_description = "Generate lightmap UVs for this group manually"

    def execute(self, context):
        scene = context.scene

        # Store old context
        old_context = None
        if context.area:
            old_context = context.area.type

        # Check if group exists
        if lightmap_group_exists(self, context) is False:
            return {'CANCELLED'}

        if context.area:
            context.area.type = 'VIEW_3D'
        group = scene.thug_lightmap_groups[scene.thug_lightmap_groups_index]

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        if group.bake is True and bpy.data.groups[group.name].objects:
            # Check if objects are all on the visible layers
            isAllObjVisible = all_objects_visible(self, context)

            if bpy.data.objects.get(group.name + "_mergedObject") is not None:
                self.report({'INFO'}, "Old merged object exists!")
            elif isAllObjVisible is False:
                self.report({'INFO'}, "Not all objects are visible!")
            else:
                bpy.ops.object.thug_bake_create_lightmap(
                    group_name=group.name, resolution=int(group.resolution))
                bpy.ops.object.thug_lightmap_merge_objects(
                    group_name=group.name, unwrap=False)

        # Set old context back
        if context.area:
            context.area.type = old_context

        return{'FINISHED'}


class THUG_ManualUnwrapFinish(bpy.types.Operator):
    bl_idname = "object.thug_lightmap_manualunwrap_end"
    bl_label = "Finish Manual Unwrap"
    bl_description = "Finish manual setup of lightmap UVs and restore original objects"

    def execute(self, context):
        scene = context.scene

        # Store old context
        old_context = None
        if context.area:
            old_context = context.area.type

        # Check if group exists
        if lightmap_group_exists(self, context) is False:
            return {'CANCELLED'}

        group = scene.thug_lightmap_groups[scene.thug_lightmap_groups_index]
        if context.area:
            context.area.type = 'VIEW_3D'

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        if group.bake is True and bpy.data.groups[group.name].objects:
            # Check if objects are all on the visible layers
            isAllObjVisible = all_objects_visible(self, context)

            if isAllObjVisible is True:
                bpy.ops.object.thug_lightmap_separate_objects(group_name=group.name)
            else:
                self.report({'INFO'}, "Not all objects are visible!")

        # Set old context back
        if context.area:
            context.area.type = old_context

        return{'FINISHED'}



class ToggleLightmapPreview(bpy.types.Operator):
    bl_idname = "object.thug_toggle_lightmap_preview"
    bl_label = "Toggle Lightmap Preview"
    bl_options = {'REGISTER', 'UNDO'}
    
    preview_on = bpy.props.BoolProperty()
    
    @classmethod
    def poll(cls, context):
        meshes = [o for o in bpy.data.objects if o.type == 'MESH' and "is_baked" in o and o["is_baked"] == True]
        return len(meshes) > 0

    def execute(self, context):
        if self.preview_on:
            for mat in bpy.data.materials:
                mat.use_nodes = True
            self.preview_on = False
        else:
            for mat in bpy.data.materials:
                mat.use_nodes = False
            self.preview_on = True
        
        return {"FINISHED"}
        
        
#----------------------------------------------------------------------------------
class ConvertLightmapsToVCs(bpy.types.Operator):
    bl_idname = "object.thug_convert_bake_to_vcs"
    bl_label = "To VCs"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        meshes = [o for o in context.selected_objects if o.type == 'MESH']
        return len(meshes) > 0

    def execute(self, context):
        meshes = [o for o in context.selected_objects if o.type == 'MESH']
        convert_bake_to_vcs(context.scene, meshes)
        return {"FINISHED"}
        
#----------------------------------------------------------------------------------
class UnBakeLightmaps(bpy.types.Operator):
    bl_idname = "object.thug_unbake_scene"
    bl_label = "Un-Bake Objects"
    bl_options = {'REGISTER', 'UNDO'}
    unbake_option = EnumProperty(items=(
        ("ClearToVCs", "Convert to vertex colors", "Converts baked lightmap texture to vertex colors (more efficient, less accurate)"),
        ("ClearAll", "Clear All", "Completely clears baked results and deletes baked vertex colors"),
        ), name="Options", default="ClearToVCs")
    
    @classmethod
    def poll(cls, context):
        meshes = [o for o in context.selected_objects if o.type == 'MESH' and ("is_baked" in o and o["is_baked"] == True) ]
        return len(meshes) > 0

    def execute(self, context):
        scene = context.scene
        meshes = [o for o in context.selected_objects if o.type == 'MESH' and ("is_baked" in o and o["is_baked"] == True) ]

        if self.unbake_option == 'ClearToVCs':
            convert_bake_to_vcs(scene, meshes)
        elif self.unbake_option == 'ClearAll':
            clear_bake_vcs(scene, meshes)
            for ob in meshes: # Also remove lightmap UVs
                if ob.data.uv_layers.get('Lightmap'):
                    ob.data.uv_textures.remove(ob.data.uv_textures['Lightmap'])
        
        bpy.ops.object.select_all(action='DESELECT')
        for ob in meshes:
            print("----------------------------------------")
            print("Attempting to un-bake object {}...".format(ob.name))
            print("----------------------------------------")
            
            # Grab the original mesh data so we can remap the material assignments 
            orig_polys = [0] * len(ob.data.polygons)
            for f in ob.data.polygons:
                orig_polys[f.index] = f.material_index
                
            unbake(ob)
            
            bpy.context.scene.objects.active = ob
            ob.select = True
            restore_mat_assignments(ob, orig_polys)
            ob.select = False
            
            # If this object belongs to a lightmap group, remove it
            if ob.thug_lightmap_group_id > -1:
                if scene.thug_lightmap_groups[ob.thug_lightmap_group_id]:
                    group_name = scene.thug_lightmap_groups[ob.thug_lightmap_group_id].name
                    obj_group = bpy.data.groups[group_name]
                    obj_group.objects.unlink(ob)
                    ob.thug_lightmap_group_id = -1
                    print("Removed from lightmap group {}".format(group_name))
                    
            print("... Un-bake successful!")
        
        print("Unbake completed on all objects!")
        return {"FINISHED"}
        
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600, height=350)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        row = col.row()
        row.prop(self, "unbake_option", icon='SETTINGS', expand=True)
        
#----------------------------------------------------------------------------------
class BakeLightmaps(bpy.types.Operator):
    bl_idname = "object.thug_bake_scene"
    bl_label = "Bake Lighting"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        meshes = [o for o in context.selected_objects if o.type == 'MESH']
        return len(meshes) > 0

    def execute(self, context):
        meshes = [o for o in context.selected_objects if o.type == 'MESH']
        if context.scene.thug_bake_type == 'VERTEX_COLORS':
            bake_thug_vcs(meshes, context)
        else:
            if context.scene.thug_bake_type == 'INDIRECT':
                #bake_ugplus_lightmaps(meshes, context)
                bake_hl2_lightmaps(meshes, context)
            else:
                bake_thug_lightmaps(meshes, context)
        return {"FINISHED"}
        
#----------------------------------------------------------------------------------
class FixLightmapMaterials(bpy.types.Operator):
    bl_idname = "object.thug_bake_fix_mats"
    bl_label = "Fix Materials"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        meshes = [o for o in bpy.data.objects if o.type == 'MESH' and "is_baked" in o and o["is_baked"] == True ]
        return len(meshes) > 0

    def execute(self, context):
        fill_bake_materials()
        return {"FINISHED"}
        
#----------------------------------------------------------------------------------
class ReBakeLightmaps(bpy.types.Operator):
    bl_idname = "object.thug_rebake_scene"
    bl_label = "Re-Bake All"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        meshes = [o for o in bpy.data.objects if o.type == 'MESH' and "is_baked" in o and o["is_baked"] == True ]
        return len(meshes) > 0

    def execute(self, context):
        meshes = [o for o in bpy.data.objects if o.type == 'MESH' and "is_baked" in o and o["is_baked"] == True ]
        bake_thug_lightmaps(meshes, context)
        return {"FINISHED"}

#----------------------------------------------------------------------------------
class BakeNewLightmaps(bpy.types.Operator):
    bl_idname = "object.thug_bake_scene_new"
    bl_label = "Bake All New"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        meshes = [o for o in bpy.data.objects if o.type == 'MESH' and ("is_baked" not in o or o["is_baked"] == False) ]
        return len(meshes) > 0

    def execute(self, context):
        meshes = [o for o in bpy.data.objects if o.type == 'MESH' and ("is_baked" not in o or o["is_baked"] == False) ]
        bake_thug_lightmaps(meshes, context)
        return {"FINISHED"}
        
#----------------------------------------------------------------------------------
class SelectAllBaked(bpy.types.Operator):
    bl_idname = "object.thug_bake_select_all"
    bl_label = "Select Baked"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        meshes = [o for o in bpy.data.objects if o.type == 'MESH' and "is_baked" in o and o["is_baked"] == True ]
        return len(meshes) > 0

    def execute(self, context):
        meshes = [o for o in bpy.data.objects if o.type == 'MESH' and "is_baked" in o and o["is_baked"] == True ]
        for ob in meshes:
            ob.select = True
        return {"FINISHED"}
        
#----------------------------------------------------------------------------------
class SelectAllNotBaked(bpy.types.Operator):
    bl_idname = "object.thug_bake_select_new"
    bl_label = "Select New"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        meshes = [o for o in bpy.data.objects if o.type == 'MESH' and ("is_baked" not in o or o["is_baked"] == False) ]
        return len(meshes) > 0

    def execute(self, context):
        meshes = [o for o in bpy.data.objects if o.type == 'MESH' and ("is_baked" not in o or o["is_baked"] == False) ]
        for ob in meshes:
            ob.select = True
        return {"FINISHED"}
        
#----------------------------------------------------------------------------------
class AutoLightmapResolution(bpy.types.Operator):
    bl_idname = "object.thug_auto_lightmap"
    bl_label = "Auto-set Resolution"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        meshes = [o for o in bpy.data.objects if o.type == 'MESH' ]
        return len(meshes) > 0

    def execute(self, context):
        meshes = [o for o in bpy.data.objects if o.type == 'MESH' ]
        
        for ob in meshes:
            # We will use the object's area and density (number of faces) to determine
            # The approximate 'best' lightmap resolution, and then set that
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            ob_area = sum(f.calc_area() for f in bm.faces)
            ob_polys = len(ob.data.polygons)
            bm.free()
            print("Area of {}: {}".format(ob.name, ob_area))
            print("Density of {}: {} polys".format(ob.name, ob_polys))
            # Start with the poly count and use that to set a 'base' resolution
            base_res = 32
            res_multi = 1
            if ob_polys >= 256:
                base_res = 512
            elif ob_polys >= 96:
                base_res = 256
            elif ob_polys >= 48:
                base_res = 128
            elif ob_polys >= 16:
                base_res = 64
                
            if ob_area >= 500000000:
                res_multi = 8
            elif ob_area >= 50000000:
                res_multi = 4
            elif ob_area >= 100000:
                res_multi = 2
                
            actual_res = (base_res * res_multi)
            ob.thug_lightmap_resolution = str(actual_res)
            print("Calculated lightmap res: {}".format(actual_res))
            print("**************************************************")
        return {"FINISHED"}

        
class RenderCubemaps(bpy.types.Operator):
    bl_idname = "object.thug_render_cubemaps"
    bl_label = "Render Cubemap"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        probes = [o for o in context.selected_objects if o.type == 'EMPTY' \
            and o.thug_empty_props and o.thug_empty_props.empty_type in ['CubemapProbe','LightProbe']]
        return len(probes) > 0

    def execute(self, context):
        probes = [o for o in context.selected_objects if o.type == 'EMPTY' \
            and o.thug_empty_props and o.thug_empty_props.empty_type in ['CubemapProbe','LightProbe']]
        
        for probe in probes:
            render_cubemap(probe)
            
        return {"FINISHED"}
        
        

# PANELS
#############################################
#----------------------------------------------------------------------------------
class THUGLightingTools(bpy.types.Panel):
    bl_label = "TH Lighting Tools"
    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"
    bl_category = "THUG Tools"

    @classmethod
    def poll(cls, context):
        return context.user_preferences.addons[ADDON_NAME].preferences.object_settings_tools

    def draw(self, context):
        if not context.object: return
        ob = context.object
        if ob.type == "MESH" and ob.thug_export_scene:
            box = self.layout.box().column()
            if ob.thug_lightmap_group_id < 0:
                box.row().prop(ob, "thug_lightmap_resolution")
                box.row().prop(ob, "thug_lightmap_quality")
                box.row().prop(ob, "thug_lightmap_type", expand=True)
            else:
                box.row().prop(ob, "thug_lightmap_quality")
                
            tmp_row = box.row().split()
            tmp_row.column().operator(BakeLightmaps.bl_idname, text=BakeLightmaps.bl_label, icon='LIGHTPAINT')
            tmp_row.column().operator(UnBakeLightmaps.bl_idname, text=UnBakeLightmaps.bl_label, icon='SMOOTH')
            
            
        elif ob.type == 'EMPTY' and ob.thug_empty_props and ob.thug_empty_props.empty_type in ['CubemapProbe','LightProbe']:
            box = self.layout.box().column(True)
            tmp_row = box.row().split()
            tmp_row.column().operator(RenderCubemaps.bl_idname, text=RenderCubemaps.bl_label, icon='MAT_SPHERE_SKY')

        if context.space_data.viewport_shade == 'TEXTURED':
            self.layout.row().prop(context.scene, "lightmap_view", expand=False)
            
class THUGSceneLightingTools(bpy.types.Panel):
    bl_label = "TH Lighting Settings"
    bl_region_type = "WINDOW"
    bl_space_type = "PROPERTIES"
    bl_context = "world"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        if not context.scene: return
        scene = context.scene
        self.layout.row().prop(scene, "thug_lightmap_scale")
        self.layout.row().prop(scene, "thug_bake_type")
        self.layout.row().prop(scene, "thug_bake_slot")
        self.layout.row().prop(scene, "thug_bake_automargin")
        tmp_row = self.layout.split()
        col = tmp_row.column()
        col.prop(scene, "thug_bake_force_remake")
        col = tmp_row.column()
        col.prop(scene, "thug_bake_pad_uvs")
        self.layout.row().operator(ToggleLightmapPreview.bl_idname, text=ToggleLightmapPreview.bl_label, icon='SEQ_PREVIEW')
        
        tmp_row = self.layout.split()
        col = tmp_row.column()
        col.operator(SelectAllBaked.bl_idname, text=SelectAllBaked.bl_label, icon='UV_SYNC_SELECT')
        col = tmp_row.column()
        col.operator(SelectAllNotBaked.bl_idname, text=SelectAllNotBaked.bl_label, icon='UV_SYNC_SELECT')
        tmp_row = self.layout.split()
        col = tmp_row.column()
        col.operator(AutoLightmapResolution.bl_idname, text=AutoLightmapResolution.bl_label, icon='SCRIPT')
        col = tmp_row.column()
        col.operator(FixLightmapMaterials.bl_idname, text=FixLightmapMaterials.bl_label, icon='MATERIAL')
        
        self.layout.separator()
            
        # New lightmap group settings
        self.layout.row().label(text="Lightmap Groups", icon='GROUP')
        row = self.layout.row()
        row.template_list("UI_UL_list", "template_list_controls", scene,
                          "thug_lightmap_groups", scene, "thug_lightmap_groups_index", rows=2, maxrows=8)
        col = row.column(align=True)
        col.operator("scene.thug_bake_add_lightmap_group", icon='ZOOMIN', text="")
        col.operator("scene.thug_bake_del_lightmap_group", icon='ZOOMOUT', text="")

        row = self.layout.row(align=True)

        # Resolution and Unwrap types (only if Lightmap group is added)
        if context.scene.thug_lightmap_groups:
            group = scene.thug_lightmap_groups[scene.thug_lightmap_groups_index]
            
            row = self.layout.row()
            row.operator("scene.thug_bake_select_group", text="Select Group", icon="NODE_SEL")

            row = self.layout.row()
            row.operator("scene.thug_bake_add_selected_to_group", text="Add Selected", icon="LINKED")
            row.operator("scene.thug_bake_remove_selected", text="Remove Selected", icon="UNLINKED")

            row = self.layout.row()
            row.prop(group, 'resolution')
            row = self.layout.row()
            row.prop(group, 'unwrap_type', expand=True)
            
            row = self.layout.row()
            row.operator("object.thug_lightmap_autounwrap", text="Generate UVs", icon="GROUP_UVS")
            #row.prop(group, 'autoUnwrapPrecision', text='')

            if context.selected_objects and context.selected_objects[0].name.endswith("_mergedObject"):
                row.operator("object.thug_lightmap_manualunwrap_end", text="Finish Unwrap", icon="MESH_UVSPHERE")
            else:
                row.operator("object.thug_lightmap_manualunwrap", text="Manual Unwrap", icon="UV_VERTEXSEL")

