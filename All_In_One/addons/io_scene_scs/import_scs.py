##############################################################################
#
# Blender add-on for converting 3D models to SCS games
# Copyright (C) 2013  Simon Lušenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
# 
# For any additional information e-mail me to simon_lusenc (at) msn.com
#
##############################################################################

import bpy, os
from . import help_funcs, import_mat
from mathutils import Vector


def load(filepath, basepath, scs_base, pmd, pmg, pmc, use_mats, show_textured, optimize):
    #set viewport shading to TEXTURE
    for area in bpy.data.screens[bpy.context.screen.name].areas:
        if area.type == 'VIEW_3D':
            if show_textured:
                area.spaces.active.viewport_shade = 'TEXTURED'
            else:
                area.spaces.active.viewport_shade = 'SOLID'
            area.spaces.active.show_backface_culling = True
        #set viewport rendering to GLSL
    bpy.context.scene.game_settings.material_mode = 'GLSL'

    #add HEMI lamps and set properties
    bpy.ops.object.lamp_add(type='HEMI', location=Vector((-2, -2, 3)),
                            rotation=Vector((0.87, -0.4542, -0.4872)))
    lamp = bpy.context.active_object
    lamp.data.energy = 1.0
    lamp.name = "SCS_light_specular"
    lamp.hide = True
    lamp.hide_select = True
    bpy.ops.object.lamp_add(type='HEMI', location=Vector((2, 2, 3)),
                            rotation=Vector((0.87, -0.4542, 2.6543)))
    lamp = bpy.context.active_object
    lamp.data.energy = 2.0
    lamp.data.use_specular = False
    lamp.name = "SCS_light_diffuse"
    lamp.hide = True
    lamp.hide_select = True

    #draw pmg model
    startIndx = filepath.rfind('\\')
    if startIndx == -1:
        startIndx = filepath.rfind('/')
    root_name = filepath[startIndx + 1:-4]
    root_node = pmg.draw_model(root_name, optimize)
    root_node["scs_variants"] = {}
    root_node["scs_looks"] = {}

    if pmd is not None:
        #list for sections variants
        sec_variants = [''] * len(pmg.sections)

        #for each pmd variant
        var_no = 'A'
        for variant_visib in pmd.visib_variants:
            #find which section is visible for current variant
            i = 0
            for visib in variant_visib.visib_list:
                if visib == 1:
                    sec_variants[i] += var_no
                i += 1
            var_no = chr(ord(var_no) + 1)

        #add variants to sections empties
        i = 0
        for sec_variant in sec_variants:
            curr_sec = help_funcs.DecodeNameCRC(pmg.sections[i].name)
            bpy.data.objects[curr_sec]["scs_variant_visib"] = sec_variant
            i += 1

        #add variants to custom properties of root empty
        var_no = 'A'
        var_dic = {}
        for variant in pmd.variants:
            prop_val = help_funcs.DecodeNameCRC(variant.name)
            var_dic[var_no] = prop_val
            var_no = chr(ord(var_no) + 1)
        bpy.data.objects[root_name]["scs_variants"] = var_dic

        i = 0
        look_dic = {}
        for look in pmd.looks:
            prop_val = help_funcs.DecodeNameCRC(look.name)
            look_dic[str(i)] = prop_val
            i += 1
        bpy.data.objects[root_name]["scs_looks"] = look_dic

    if pmc is not None:
        pmc.draw_collisions(root_node)


    if use_mats and pmd is not None:
        help_funcs.PrintDeb("Loading materials...", end=" -> ")
        #open material and parse it
        mats = []
        tobj_dic = {}
        i = 0
        real_basepath = None #real path for material and tobjs
        for path in pmd.materials.mat_paths:
            if os.path.exists(basepath + path):
                real_basepath = basepath
            elif os.path.exists(scs_base + path):
                real_basepath = scs_base
            else:
                rel_path = os.path.dirname(filepath)
                if not os.path.exists(rel_path + '/' + path):
                    return -1, "Can't find one of materials! Model is loaded without materials."
                else:
                    real_basepath = rel_path + '/'

            mat = import_mat.MAT(real_basepath, path)
            mat.parse()
            #Depricated in v0.2.2 - scs_look_indx not used anymore as user has complete freedom about materials
            # look_indx = int(i/pmd.header.no_materials)
            # if pmd.header.no_looks == 1:
            #     look_indx = -1
            # mat.create_mat(scs_base, basepath, look_indx, tobj_dic)
            mat.create_mat(scs_base, basepath, tobj_dic)

            mats.append(mat)
            i += 1
        help_funcs.PrintDeb("Done!")

        help_funcs.PrintDeb("Assigning materials to models...", end=" -> ")
        #set materials to pmg models
        for model in pmg.models:
            ob = bpy.data.objects[model.name]
            bpy.context.scene.objects.active = ob
            i = 0
            while i < pmd.header.no_looks:
                bpy.ops.object.material_slot_add()
                #get material name from MAT object name 
                #which is same as name of blender material
                #model.mat_idx = index of material
                mat_name = mats[model.mat_idx + i * pmd.header.no_materials].name
                curr_mat = bpy.data.materials[mat_name]
                ob.material_slots[i].material = curr_mat

                '''
                # saving test data for uv mask recognizion
                if "test_storage" in bpy.data.groups:
                    shading_lib_key = curr_mat.scs_shading
                    uvs_mask_lib = bpy.data.groups["test_storage"]["data"]
                    uvs_mask_lib_files = bpy.data.groups["test_storage"]["files"]

                    value = str(model.uvs_count) + " - " + str(model.uvs_mask)

                    if not shading_lib_key in uvs_mask_lib:
                        uvs_mask_lib[shading_lib_key] = value
                        uvs_mask_lib_files[shading_lib_key] = filepath[filepath.find("/base")+5:]
                    else:
                        #if shader is already in library and mask is different create derivate
                        if uvs_mask_lib[shading_lib_key] != value:
                            postfix = 1
                            postfixed_shading = shading_lib_key + " | variant "
                            while postfixed_shading+str(postfix) in uvs_mask_lib:
                                if uvs_mask_lib[postfixed_shading+str(postfix)] == value:
                                    postfix = 0
                                    break
                                postfix += 1
                            if postfix != 0:
                                uvs_mask_lib[postfixed_shading+str(postfix)] = value
                                uvs_mask_lib_files[postfixed_shading+str(postfix)] = filepath[filepath.find("/base")+5:]
                '''

                j = 0
                for uvtex in ob.data.uv_textures:
                    uvtex.active = True
                    if bpy.data.materials[mat_name].texture_slots[j] is not None:
                        img = bpy.data.materials[mat_name].texture_slots[j].texture.image
                        for p in ob.data.polygons:
                            uvtex.data[p.index].image = img
                    j += 1
                i += 1
        help_funcs.PrintDeb("Done!")
    return 0, root_name