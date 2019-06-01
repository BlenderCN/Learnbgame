# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Created by Matti 'Menithal' Lahtinen

import copy
import bpy
import re


def get_images_from(meshes):
    images = []
    for mesh in meshes:
        if(mesh.type == "MESH"):
            for material_slot in mesh.material_slots:
                print("Iterating material", material_slot)
                if material_slot is not None:
                    material = material_slot.material
                    for texture_slot in material.texture_slots:
                        print("Iterating texture slot", texture_slot)
                        if texture_slot is not None and texture_slot.texture is not None and texture_slot.texture.image is not None:
                            images.append(texture_slot.texture.image)

    return images


def cleanup_alpha(materials):
    for material in materials:
        if material.alpha > 0.9:
            material.alpha = 1

        if material.specular_alpha > 0.9:
            material.specular_alpha = 1


def cleanup_unused(images):
    for image in images:
        pixel_count = len(image.pixels)
        if not (image.users > 0 and pixel_count > 0):
            bpy.data.images.remove(image)


def convert_to_png(images):
    if not bpy.data.is_saved:
        print("Select a Directory")
        bpy.ops.hifi_error.save_file('INVOKE_DEFAULT')
        return

    pack_images(images)
    unpack_images(images)


def pack_images(images):
    mode = bpy.context.area.type
    bpy.context.area.type = 'IMAGE_EDITOR'
    filename_re = re.compile("\\.[a-zA-Z]{2,4}$")

    for image in images:
        pixel_count = len(image.pixels)
        if image.users > 0 and pixel_count > 0:
            bpy.context.area.spaces.active.image = image
            bpy.ops.image.pack(as_png=True)

            image.name = filename_re.sub(".png", image.name)
            image.packed_files[0].filepath = filename_re.sub(".png",
                                                             image.packed_files[0].filepath)

            bpy.context.area.spaces.active.image = image

            bpy.ops.image.save()
            bpy.ops.image.reload()
            print("+ Packing", image.name, image.filepath)
        else:
            bpy.data.images.remove(image)

    bpy.context.area.type = mode


def unpack_images(images):
    print("#########")
    print(" Unpacking Images ")
    mode = bpy.context.area.type
    bpy.context.area.type = 'IMAGE_EDITOR'
    for image in images:
        bpy.context.area.spaces.active.image = image
        bpy.ops.image.unpack(method='WRITE_LOCAL')
        bpy.ops.image.save()
        bpy.ops.image.reload()

    bpy.context.area.type = mode


def convert_image_to_mask(image, threshold):
    print("Copying image to memory", image.name)
    pixels = list(image.pixels)
    size = len(pixels)

    mode = bpy.context.area.type
    bpy.context.area.type = 'IMAGE_EDITOR'
    bpy.context.area.spaces.active.image = image
    if size == 0:
        return
    pxs = range(0, int(size/4))
    print(" Starting Mask pass")
    for pixel_index in pxs:
        index = pixel_index*4 + 3
        if pixels[index] > threshold:
            pixels[index] = 1
        else:
            pixels[index] = 0
    image.pixels = pixels

    bpy.ops.image.save()
    bpy.context.area.type = mode


def convert_images_to_mask(images, threshold=0.3):
    for image in images:
        convert_image_to_mask(image, threshold)

def make_material_shadeless(material):
    if material is not None:
        material.specular_shader = 'WARDISO'
        material.use_shadeless = True
        material.specular_color = (0, 0, 0)

def make_materials_shadeless(materials):
    for material in materials:
        make_material_shadeless(material)

def remove_materials_metallic(materials):
    for material in materials:
        material.specular_color = (0, 0, 0)

def make_material_shaded(material):
    if material is not None:
        material.specular_shader = 'PHONG'
        material.use_shadeless = False

def make_materials_shaded(materials):
    for material in materials:
        make_material_shaded(material)

def make_materials_fullbright(materials):
    for material in materials:
        for texture_slot in material.texture_slots:
            if texture_slot is not None and texture_slot.use_map_color_diffuse:
                texture_slot.use_map_emit = True

def get_textures_for_slot(texture_slots, texture_type="ALL"):
    texture_list = []

    for slot in texture_slots:
        if slot.image is not None and (texture_type == "ALL" or
                                       (texture_type == "COLOR" and slot.use_map_color_diffuse) or
                                       (texture_type == "SPECULAR" and (slot.use_map_color_spec or slot.use_map_specular)) or
                                       (texture_type == "NORMAL" and slot.use_map_normal) or
                                       (texture_type == "ALPHA" and slot.use_map_alpha) or
                                       (texture_type == "EMIT" and slot.use_map_emit) or
                                       (texture_type == "EMISSION" and slot.use_map_emission) or
                                       (texture_type == "HARDNESS" and slot.use_map_hardness) or
                                       (texture_type == "ROUGHNESS" and slot.use_map_roughness)) and slot.image not in texture_list:

            texture_list.append(slot.image)

    return texture_list

def clean_textures(material):
    textures = []
    for idx, texture_slot in enumerate(material.texture_slots):
        if texture_slot is not None and texture_slot.texture is not None and texture_slot.texture.image is not None:
            image_path = texture_slot.texture.image.filepath_raw
            texture_name = texture_slot.name
            print("# Checking", texture_name, image_path)
            if (not texture_slot.use or texture_slot.texture_coords != "UV"):
                print(" - Removing Texture", texture_name, image_path)
                try:
                    bpy.data.textures.remove(texture_slot.texture)
                # catch exception if there are remaining texture users or texture is None
                except (RuntimeError, TypeError):
                    pass

                material.texture_slots.clear(idx)
            else:
                textures.append(texture_slot.texture)
    return textures


def merge_textures(materials_slots, unique_textures=None):
    if unique_textures is None:
        unique_textures = {}
        for slot in materials_slots:
            textures = get_textures_for_slot(slot.texture_slots)
            if len(textures) > 0:
                unique_textures[textures[0].name] = textures

    print("Processing", unique_textures)
    for key in unique_textures.keys():
        material_list = unique_textures[key]

        if material_list is None:
            continue

        print("Creating new material Texture", key, material_list)
        first_material = material_list.pop(0)
        print("First material", first_material)
        if first_material is None:
            print("Could not find", first_material)
            continue

        root_material = key + "_material"
        first_material.name = root_material

        root_index = materials_slots.find(root_material)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')

        print("Deselected objects, now continueing")
        if len(material_list) > 0:
            for material in material_list:
                print(material, materials_slots)
                index = materials_slots.find(material.name)
                print("First Index issue")
                if index > -1:
                    print("  + Selecting", key, material.name)
                    bpy.context.object.active_material_index = index
                    bpy.ops.object.material_slot_select()

        print("  + Selecting", key, root_index)
        bpy.context.object.active_material_index = root_index
        bpy.ops.object.material_slot_select()

        print(" + Assigning to", key)
        bpy.ops.object.material_slot_assign()

        bpy.ops.object.mode_set(mode='OBJECT')
        print(" - Clean up", key)
        if len(material_list) > 0:
            for material in material_list:
                index = materials_slots.find(material.name)
                print("Second Index issue")

                if index > -1:
                    print("  - Deleting", material)
                    bpy.context.object.active_material_index = index
                    bpy.ops.object.material_slot_remove()

def clean_materials(materials_slots):
    try:
        print("#######################################")
        print("Cleaning Materials")

        _unique_textures = {}
        for material_slot in materials_slots:
            if material_slot is not None and material_slot.material is not None:
                textures = clean_textures(material_slot.material)

                for texture in textures:
                    if texture is not None:
                        if _unique_textures.get(texture.name) is None:
                            print("Creating new", texture.name)
                            _unique_textures[texture.name] = [
                                material_slot.material]
                        else:
                            print("Appending to", texture.name)
                            _unique_textures[texture.name].append(
                                material_slot.material)

        print("Found", len(_unique_textures.keys()),
              "unique textures from", len(materials_slots), "slots")

        merge_textures(materials_slots, _unique_textures)
    except Exception as args:
        print("ERROR OCCURRED WHILE TRYING TO PROCESS TEXTURES", args)
    # make_materials_fullbright(materials_slots) # enable this only if fullbright avatars every become supported

def flip_material_specular(material):
    material.specular_color = (0, 0, 0)
    for texture in material.texture_slots:
        if texture is not None and texture.use_map_color_spec:
            texture.use_map_color_spec = False
            texture.use_map_hardness = True

