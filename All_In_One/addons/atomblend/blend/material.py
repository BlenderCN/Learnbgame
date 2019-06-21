# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   blend/material.py
# Date:   2014-07-01
# Author: Varvara Efremova
#
# Description:
# Blender API wrapper for material operations.
# =============================================================================

import bpy
import os
import numpy as np

# === Material creation ===
def surface_add(name, mtype='SURFACE', color=(1.0, 1.0, 1.0), specular=(1.0, 1.0, 1.0), shadeless=False, emit=0.0, alpha=1.0):
    """Create basic surface material"""
    mat = bpy.data.materials.new(name)
    mat.type = mtype

    mat.diffuse_color = color
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0

    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5

    mat.emit = emit

    if shadeless:
        mat.use_shadeless = True

    mat.alpha = alpha
    mat.ambient = 1
    return mat

def halo_add(name, mtype='HALO', color=(1.0, 1.0, 1.0), alpha=1.0, hard=0, size=0.1, use_tex=True):
    """Create basic halo material"""
    mat = bpy.data.materials.new(name)
    mat.type = mtype

    mat.diffuse_color = color
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0

    mat.specular_color = color
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5

    mat.alpha = alpha
    mat.ambient = 1

    halo = mat.halo
    halo.hardness = hard
    halo.size = size
    halo.use_texture = use_tex

    halo.add = 0
    halo.seed = 0
    return mat

def texture_add_img(name, path):
    realpath = os.path.expanduser(path)
    try:
        img = bpy.data.images.load(realpath)
    except:
        raise NameError("Cannot load image %s" % realpath)

    tex = bpy.data.textures.new(name, type='IMAGE')
    tex.image = img
    return tex

# === Material manipulation ===
def set(obj, mat):
    """Assign material to object"""
    mesh = obj.data
    mesh.materials.append(mat)

def texture_add(mat, tex):
    """Assign texture to material"""
    # Add texture slot
    mtex = mat.texture_slots.add()
    mtex.texture = tex
    mtex.blend_type = 'MULTIPLY'
    mtex.use_map_alpha = True
    mtex.use_map_color_diffuse = True
    #mtex.use_face_texture_alpha = True
    return mtex
