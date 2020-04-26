# ##### BEGIN MIT LICENSE BLOCK #####
# MIT License
# 
# Copyright (c) 2018 Insma Software
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ##### END MIT LICENSE BLOCK #####

# ----------------------------------------------------------
# Author: Maciej Klemarczyk (mklemarczyk)
# ----------------------------------------------------------

import bpy

# --------------------------------------------------------------------
# Creates new ceramic material
# --------------------------------------------------------------------
def meshlib_ceramic_material():
    (mat, principled_node) = create_principled_material(matname='Ceramic Material (ArchLib)')
    principled_node.distribution = 'MULTI_GGX'
    principled_node.inputs['Base Color'].default_value = (0.604, 0.604, 0.604, 1.0)
    principled_node.inputs['Subsurface'].default_value = 0.0
    principled_node.inputs['Subsurface Radius'].default_value = (1.0, 1.0, 1.0)
    principled_node.inputs['Subsurface Color'].default_value = (0.7, 0.1, 0.1, 1.0)
    principled_node.inputs['Metallic'].default_value = 0.0
    principled_node.inputs['Specular'].default_value = 0.4
    principled_node.inputs['Specular Tint'].default_value = 0.2
    principled_node.inputs['Roughness'].default_value = 0.05
    principled_node.inputs['Anisotropic'].default_value = 0.0
    principled_node.inputs['Anisotropic Rotation'].default_value = 0.0
    principled_node.inputs['Sheen'].default_value = 0.0
    principled_node.inputs['Sheen Tint'].default_value = 0.5
    principled_node.inputs['Clearcoat'].default_value = 0.0
    principled_node.inputs['Clearcoat Roughness'].default_value = 0.03
    principled_node.inputs['IOR'].default_value = 1.45
    principled_node.inputs['Transmission'].default_value = 0.0
    principled_node.inputs['Transmission Roughness'].default_value = 0.0
    return mat

# --------------------------------------------------------------------
# Creates new cloud material
# --------------------------------------------------------------------
def meshlib_cloud_material():
    (mat, principled_node) = create_principled_material(matname='Cloud Material (ArchLib)')
    return mat

# --------------------------------------------------------------------
# Creates new fabric material
# --------------------------------------------------------------------
def meshlib_fabric_material():
    (mat, principled_node) = create_principled_material(matname='Fabric Material (ArchLib)')
    principled_node.distribution = 'MULTI_GGX'
    principled_node.inputs['Base Color'].default_value = (0.1, 0.8, 0.75, 1.0)
    principled_node.inputs['Subsurface'].default_value = 0.0
    principled_node.inputs['Subsurface Radius'].default_value = (1.0, 1.0, 1.0)
    principled_node.inputs['Subsurface Color'].default_value = (0.7, 0.1, 0.1, 1.0)
    principled_node.inputs['Metallic'].default_value = 0.0
    principled_node.inputs['Specular'].default_value = 0.0
    principled_node.inputs['Specular Tint'].default_value = 0.0
    principled_node.inputs['Roughness'].default_value = 0.0
    principled_node.inputs['Anisotropic'].default_value = 0.0
    principled_node.inputs['Anisotropic Rotation'].default_value = 0.0
    principled_node.inputs['Sheen'].default_value = 10.0
    principled_node.inputs['Sheen Tint'].default_value = 0.3
    principled_node.inputs['Clearcoat'].default_value = 0.0
    principled_node.inputs['Clearcoat Roughness'].default_value = 0.03
    principled_node.inputs['IOR'].default_value = 1.45
    principled_node.inputs['Transmission'].default_value = 0.0
    principled_node.inputs['Transmission Roughness'].default_value = 0.0
    return mat

# --------------------------------------------------------------------
# Creates new glass material
# --------------------------------------------------------------------
def meshlib_glass_material():
    (mat, principled_node) = create_principled_material(matname='Glass Material (ArchLib)')
    principled_node.distribution = 'MULTI_GGX'
    principled_node.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
    principled_node.inputs['Subsurface'].default_value = 0.0
    principled_node.inputs['Subsurface Radius'].default_value = (1.0, 1.0, 1.0)
    principled_node.inputs['Subsurface Color'].default_value = (0.7, 0.1, 0.1, 1.0)
    principled_node.inputs['Metallic'].default_value = 0.0
    principled_node.inputs['Specular'].default_value = 0.5
    principled_node.inputs['Specular Tint'].default_value = 0.0
    principled_node.inputs['Roughness'].default_value = 0.0
    principled_node.inputs['Anisotropic'].default_value = 0.0
    principled_node.inputs['Anisotropic Rotation'].default_value = 0.0
    principled_node.inputs['Sheen'].default_value = 0.0
    principled_node.inputs['Sheen Tint'].default_value = 0.5
    principled_node.inputs['Clearcoat'].default_value = 0.0
    principled_node.inputs['Clearcoat Roughness'].default_value = 0.03
    principled_node.inputs['IOR'].default_value = 1.5
    principled_node.inputs['Transmission'].default_value = 1.0
    principled_node.inputs['Transmission Roughness'].default_value = 0.0
    return mat

# --------------------------------------------------------------------
# Creates new matt glass material
# --------------------------------------------------------------------
def meshlib_matt_glass_material():
    (mat, principled_node) = create_principled_material(matname='Matt Glass Material (ArchLib)')
    principled_node.distribution = 'GGX'
    principled_node.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
    principled_node.inputs['Subsurface'].default_value = 0.0
    principled_node.inputs['Subsurface Radius'].default_value = (1.0, 1.0, 1.0)
    principled_node.inputs['Subsurface Color'].default_value = (0.7, 0.1, 0.1, 1.0)
    principled_node.inputs['Metallic'].default_value = 0.0
    principled_node.inputs['Specular'].default_value = 0.5
    principled_node.inputs['Specular Tint'].default_value = 0.0
    principled_node.inputs['Roughness'].default_value = 0.0
    principled_node.inputs['Anisotropic'].default_value = 0.0
    principled_node.inputs['Anisotropic Rotation'].default_value = 0.0
    principled_node.inputs['Sheen'].default_value = 0.0
    principled_node.inputs['Sheen Tint'].default_value = 0.5
    principled_node.inputs['Clearcoat'].default_value = 0.0
    principled_node.inputs['Clearcoat Roughness'].default_value = 0.03
    principled_node.inputs['IOR'].default_value = 1.5
    principled_node.inputs['Transmission'].default_value = 1.0
    principled_node.inputs['Transmission Roughness'].default_value = 1.0
    return mat

# --------------------------------------------------------------------
# Creates new metalic material
# --------------------------------------------------------------------
def meshlib_metalic_material():
    (mat, principled_node) = create_principled_material(matname='Metalic Material (ArchLib)')
    return mat

# --------------------------------------------------------------------
# Creates new plastic material
# --------------------------------------------------------------------
def meshlib_plastic_material():
    (mat, principled_node) = create_principled_material(matname='Plastic Material (ArchLib)')
    principled_node.distribution = 'MULTI_GGX'
    principled_node.inputs['Base Color'].default_value = (0.8, 0.032, 0.032, 1.0)
    principled_node.inputs['Subsurface'].default_value = 0.0
    principled_node.inputs['Subsurface Radius'].default_value = (1.0, 1.0, 1.0)
    principled_node.inputs['Subsurface Color'].default_value = (0.7, 0.1, 0.1, 1.0)
    principled_node.inputs['Metallic'].default_value = 0.0
    principled_node.inputs['Specular'].default_value = 0.4
    principled_node.inputs['Specular Tint'].default_value = 0.25
    principled_node.inputs['Roughness'].default_value = 0.05
    principled_node.inputs['Anisotropic'].default_value = 0.0
    principled_node.inputs['Anisotropic Rotation'].default_value = 0.0
    principled_node.inputs['Sheen'].default_value = 0.0
    principled_node.inputs['Sheen Tint'].default_value = 0.5
    principled_node.inputs['Clearcoat'].default_value = 0.0
    principled_node.inputs['Clearcoat Roughness'].default_value = 0.03
    principled_node.inputs['IOR'].default_value = 1.45
    principled_node.inputs['Transmission'].default_value = 0.0
    principled_node.inputs['Transmission Roughness'].default_value = 0.0
    return mat

# --------------------------------------------------------------------
# Creates new wax material
# --------------------------------------------------------------------
def meshlib_wax_material():
    (mat, principled_node) = create_principled_material(matname='Wax Material (ArchLib)')
    principled_node.distribution = 'MULTI_GGX'
    principled_node.inputs['Base Color'].default_value = (0.39, 0.6, 0.12, 1.0)
    principled_node.inputs['Subsurface'].default_value = 1.0
    principled_node.inputs['Subsurface Radius'].default_value = (1.0, 1.0, 1.0)
    principled_node.inputs['Subsurface Color'].default_value = (0.39, 0.6, 0.12, 1.0)
    principled_node.inputs['Metallic'].default_value = 0.0
    principled_node.inputs['Specular'].default_value = 0.3
    principled_node.inputs['Specular Tint'].default_value = 0.2
    principled_node.inputs['Roughness'].default_value = 0.05
    principled_node.inputs['Anisotropic'].default_value = 0.0
    principled_node.inputs['Anisotropic Rotation'].default_value = 0.0
    principled_node.inputs['Sheen'].default_value = 0.0
    principled_node.inputs['Sheen Tint'].default_value = 0.5
    principled_node.inputs['Clearcoat'].default_value = 0.0
    principled_node.inputs['Clearcoat Roughness'].default_value = 0.03
    principled_node.inputs['IOR'].default_value = 1.45
    principled_node.inputs['Transmission'].default_value = 0.0
    principled_node.inputs['Transmission Roughness'].default_value = 0.0
    return mat

# --------------------------------------------------------------------
# Creates new principled material
# --------------------------------------------------------------------
def create_principled_material(matname):
    mat = bpy.data.materials.new(name=matname)
    mat.use_nodes = True
    mat_nodes = mat.node_tree.nodes
    mat_links = mat.node_tree.links
    mat_nodes.clear()
    principled_node = mat_nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_node.location = (-200, 0)
    output_node = mat_nodes.new('ShaderNodeOutputMaterial')
    mat_links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    return mat, principled_node
