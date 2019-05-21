# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# PEP8 compliant (https://www.python.org/dev/peps/pep-0008)

# ----------------------------------------------------------
# support routines and general functions
# Author: Antonio Vazquez (antonioya)
#
# ----------------------------------------------------------
# noinspection PyUnresolvedReferences
import bpy

# --------------------------------------------------------------------
# Set normals
# True= faces to inside
# False= faces to outside
# --------------------------------------------------------------------


def set_normals(myobject, direction=False):
    bpy.context.scene.objects.active = myobject
    # go edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    # select all faces
    bpy.ops.mesh.select_all(action='SELECT')
    # recalculate outside normals
    bpy.ops.mesh.normals_make_consistent(inside=direction)
    # go object mode again
    bpy.ops.object.editmode_toggle()


# --------------------------------------------------------------------
# Remove doubles
# --------------------------------------------------------------------


def remove_doubles(myobject):
    bpy.context.scene.objects.active = myobject
    # go edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    # select all faces
    bpy.ops.mesh.select_all(action='SELECT')
    # remove
    bpy.ops.mesh.remove_doubles()
    # go object mode again
    bpy.ops.object.editmode_toggle()


# --------------------------------------------------------------------
# Get Node Index(multilanguage support)
# --------------------------------------------------------------------
def get_node_index(nodes, datatype):
    idx = 0
    for m in nodes:
        if m.type == datatype:
            return idx
        idx += 1

    # by default
    return 1


# --------------------------------------------------------------------
# Create cycles diffuse material
# --------------------------------------------------------------------
def create_diffuse_material(matname, replace, r, g, b, rv=0.8, gv=0.8, bv=0.8, mix=0.1, twosides=False):
    # Avoid duplicate materials
    if replace is False:
        matlist = bpy.data.materials
        for m in matlist:
            if m.name == matname:
                return m
    # Create material
    scn = bpy.context.scene
    # Set cycles render engine if not selected
    if not scn.render.engine == 'CYCLES':
        scn.render.engine = 'CYCLES'

    mat = bpy.data.materials.new(matname)
    mat.diffuse_color = (rv, gv, bv)  # viewport color
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # support for multilanguage
    node = nodes[get_node_index(nodes, 'BSDF_DIFFUSE')]
    node.name = 'Diffuse BSDF'
    node.label = 'Diffuse BSDF'

    node.inputs[0].default_value = [r, g, b, 1]
    node.location = 200, 320

    node = nodes.new('ShaderNodeBsdfGlossy')
    node.name = 'Glossy_0'
    node.location = 200, 0

    node = nodes.new('ShaderNodeMixShader')
    node.name = 'Mix_0'
    node.inputs[0].default_value = mix
    node.location = 500, 160

    node = nodes[get_node_index(nodes, 'OUTPUT_MATERIAL')]
    node.location = 1100, 160

    # Connect nodes
    outn = nodes['Diffuse BSDF'].outputs[0]
    inn = nodes['Mix_0'].inputs[1]
    mat.node_tree.links.new(outn, inn)

    outn = nodes['Glossy_0'].outputs[0]
    inn = nodes['Mix_0'].inputs[2]
    mat.node_tree.links.new(outn, inn)

    if twosides is False:
        outn = nodes['Mix_0'].outputs[0]
        inn = nodes[get_node_index(nodes, 'OUTPUT_MATERIAL')].inputs[0]
        mat.node_tree.links.new(outn, inn)

    if twosides is True:
        node = nodes.new('ShaderNodeNewGeometry')
        node.name = 'Input_1'
        node.location = -80, -70

        node = nodes.new('ShaderNodeBsdfDiffuse')
        node.name = 'Diffuse_1'
        node.inputs[0].default_value = [0.30, 0.30, 0.30, 1]
        node.location = 200, -280

        node = nodes.new('ShaderNodeMixShader')
        node.name = 'Mix_1'
        node.inputs[0].default_value = mix
        node.location = 800, -70

        outn = nodes['Input_1'].outputs[6]
        inn = nodes['Mix_1'].inputs[0]
        mat.node_tree.links.new(outn, inn)

        outn = nodes['Diffuse_1'].outputs[0]
        inn = nodes['Mix_1'].inputs[2]
        mat.node_tree.links.new(outn, inn)

        outn = nodes['Mix_0'].outputs[0]
        inn = nodes['Mix_1'].inputs[1]
        mat.node_tree.links.new(outn, inn)

        outn = nodes['Mix_1'].outputs[0]
        inn = nodes[get_node_index(nodes, 'OUTPUT_MATERIAL')].inputs[0]
        mat.node_tree.links.new(outn, inn)

    return mat


# --------------------------------------------------------------------
# Create cycles glass material
# --------------------------------------------------------------------
def create_glass_material(matname, replace, rv=0.352716, gv=0.760852, bv=0.9):
    # Avoid duplicate materials
    if replace is False:
        matlist = bpy.data.materials
        for m in matlist:
            if m.name == matname:
                return m
    # Create material
    scn = bpy.context.scene
    # Set cycles render engine if not selected
    if not scn.render.engine == 'CYCLES':
        scn.render.engine = 'CYCLES'

    mat = bpy.data.materials.new(matname)
    mat.use_nodes = True
    mat.diffuse_color = (rv, gv, bv)
    nodes = mat.node_tree.nodes

    # support for multilanguage
    node = nodes[get_node_index(nodes, 'BSDF_DIFFUSE')]
    mat.node_tree.nodes.remove(node)  # remove not used

    node = nodes.new('ShaderNodeLightPath')
    node.name = 'Light_0'
    node.location = 10, 160

    node = nodes.new('ShaderNodeBsdfGlass')
    node.name = 'Glass_0'
    node.location = 250, 300

    node = nodes.new('ShaderNodeBsdfTransparent')
    node.name = 'Transparent_0'
    node.location = 250, 0

    node = nodes.new('ShaderNodeMixShader')
    node.name = 'Mix_0'
    node.inputs[0].default_value = 0.1
    node.location = 500, 160

    node = nodes.new('ShaderNodeMixShader')
    node.name = 'Mix_1'
    node.inputs[0].default_value = 0.1
    node.location = 690, 290

    node = nodes[get_node_index(nodes, 'OUTPUT_MATERIAL')]
    node.location = 920, 290

    # Connect nodes
    outn = nodes['Light_0'].outputs[1]
    inn = nodes['Mix_0'].inputs[0]
    mat.node_tree.links.new(outn, inn)

    outn = nodes['Light_0'].outputs[2]
    inn = nodes['Mix_1'].inputs[0]
    mat.node_tree.links.new(outn, inn)

    outn = nodes['Glass_0'].outputs[0]
    inn = nodes['Mix_0'].inputs[1]
    mat.node_tree.links.new(outn, inn)

    outn = nodes['Transparent_0'].outputs[0]
    inn = nodes['Mix_0'].inputs[2]
    mat.node_tree.links.new(outn, inn)

    outn = nodes['Mix_0'].outputs[0]
    inn = nodes['Mix_1'].inputs[1]
    mat.node_tree.links.new(outn, inn)

    outn = nodes['Mix_1'].outputs[0]
    inn = nodes[get_node_index(nodes, 'OUTPUT_MATERIAL')].inputs[0]
    mat.node_tree.links.new(outn, inn)

    return mat


# -----------------------------------------
# Define BI materials
# -----------------------------------------
def create_bi_material(ad, red, green, blue):
    if ad not in bpy.data.materials:
        mtl = bpy.data.materials.new(ad)
        mtl.diffuse_color = ([red, green, blue])
        mtl.diffuse_shader = 'LAMBERT'
        mtl.diffuse_intensity = 1.0
    else:
        mtl = bpy.data.materials[ad]
    return mtl
