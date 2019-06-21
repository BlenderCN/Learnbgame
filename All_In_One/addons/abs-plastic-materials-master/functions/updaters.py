# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
# NONE!

# Blender imports
import bpy
from bpy.props import *

# Addon imports
from .common import *


def getMatNames():
    scn = bpy.context.scene
    materials = bpy.props.abs_mats_common.copy()
    materials += bpy.props.abs_mats_transparent
    materials += bpy.props.abs_mats_uncommon
    return materials


def update_abs_subsurf(self, context):
    scn = context.scene
    for mat_name in getMatNames():
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            continue
        nodes = mat.node_tree.nodes
        target_node = nodes.get("ABS Dialectric")
        if target_node is None:
            continue
        input1 = target_node.inputs.get("SSS Default")
        input2 = target_node.inputs.get("SSS Amount")
        if input1 is None or input2 is None:
            continue
        default_amount = input1.default_value
        input2.default_value = default_amount * scn.abs_subsurf


def update_abs_roughness(self, context):
    scn = context.scene
    for mat_name in getMatNames():
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            continue
        nodes = mat.node_tree.nodes
        target_node = nodes.get("ABS Dialectric") or nodes.get("ABS Transparent")
        if target_node is None:
            continue
        input1 = target_node.inputs.get("Rough 1")
        if input1 is None:
            continue
        input1.default_value = scn.abs_roughness * (50 if mat.name in ("ABS Plastic Silver", "ABS Plastic Gold") else (3 if mat.name == "ABS Plastic Trans-Yellowish Clear" else 1))


def update_abs_randomize(self, context):
    scn = context.scene
    for mat_name in getMatNames():
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            continue
        nodes = mat.node_tree.nodes
        target_node = nodes.get("ABS Dialectric") or nodes.get("ABS Transparent")
        if target_node is None:
            continue
        input1 = target_node.inputs.get("Random")
        if input1 is None:
            continue
        input1.default_value = scn.abs_randomize


def update_abs_fingerprints(self, context):
    scn = context.scene
    for mat_name in getMatNames():
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            continue
        nodes = mat.node_tree.nodes
        target_node1 = nodes.get("ABS Dialectric") or nodes.get("ABS Transparent")
        target_node2 = nodes.get("ABS Bump")
        if target_node1 is None or target_node2 is None:
            continue
        input1 = target_node1.inputs.get("Fingerprints")
        input2 = target_node2.inputs.get("Fingerprints")
        if input1 is None or input2 is None:
            continue
        input1.default_value = scn.abs_fingerprints if mat.name not in ["ABS Plastic Silver", "ABS Plastic Gold"] else scn.abs_fingerprints / 8
        input2.default_value = scn.abs_fingerprints * scn.abs_displace


def update_abs_displace(self, context):
    scn = context.scene
    for mat_name in getMatNames():
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            continue
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        target_node = nodes.get("ABS Bump")
        if target_node is None:
            continue
        noise = target_node.inputs.get("Noise")
        waves = target_node.inputs.get("Waves")
        scratches = target_node.inputs.get("Scratches")
        fingerprints = target_node.inputs.get("Fingerprints")
        if noise is None or waves is None or scratches is None or fingerprints is None:
            continue
        noise.default_value = scn.abs_displace if mat.name not in ["ABS Plastic Silver", "ABS Plastic Gold"] else scn.abs_displace * 20
        waves.default_value = scn.abs_displace
        scratches.default_value = scn.abs_displace
        fingerprints.default_value = scn.abs_fingerprints * scn.abs_displace
        # disconnect displacement node if not used
        try:
            displace_in = nodes["Material Output"].inputs["Displacement"]
            displace_out = nodes["Displacement"].outputs["Displacement"] if b280() else target_node.outputs["Color"]
        except KeyError:
            continue
        if scn.abs_displace == 0:
            for l in displace_in.links:
                links.remove(l)
        else:
            links.new(displace_out, displace_in)


def update_abs_uv_scale(self, context):
    scn = context.scene
    for mat_name in getMatNames():
        mat = bpy.data.materials.get(mat_name)
        if mat is None:
            continue
        n_scale = mat.node_tree.nodes.get("ABS Uniform Scale")
        if n_scale is None:
            continue
        n_scale.inputs[0].default_value = scn.abs_uv_scale


def toggle_save_datablocks(self, context):
    scn = context.scene
    for mat_name in getMatNames():
        mat = bpy.data.materials.get(mat_name)
        if mat is not None:
            mat.use_fake_user = scn.save_datablocks


def update_viewport_transparency(self, context):
    scn = context.scene
    for mat_name in bpy.props.abs_mats_transparent:
        mat = bpy.data.materials.get(mat_name)
        if mat is not None:
            mat.diffuse_color[-1] = 0.75 if scn.abs_viewport_transparency else 1


def update_image(self, context):
    im = bpy.data.images.get("ABS Fingerprints and Dust")
    if im is None: return
    scn = context.scene
    res = round(scn.uv_detail_quality, 1)
    resizedImg = getDetailImage(res, im)
    fnode = bpy.data.node_groups.get("ABS_Fingerprint")
    snode = bpy.data.node_groups.get("ABS_Specular Map")
    imageNode1 = fnode.nodes.get("ABS_Fingerprints and Dust")
    imageNode2 = snode.nodes.get("ABS_Fingerprints and Dust")
    for img_node in (imageNode1, imageNode2):
        img_node.image = resizedImg


def getDetailImage(res, full_img):
    # create smaller fingerprints/dust images
    newImgName = "ABS Fingerprints and Dust" if res == 1 else "ABS Fingerprints and Dust (%(res)s)" % locals()
    detail_img_scaled = bpy.data.images.get(newImgName)
    if detail_img_scaled is None:
        detail_img_scaled = duplicateImage(full_img, newImgName)
        newScale = 2000 * res
        detail_img_scaled.scale(newScale, newScale)
    return detail_img_scaled


def duplicateImage(img, name):
    width, height = img.size
    newImage = bpy.data.images.new(name, width, height)
    newImage.pixels = img.pixels[:]
    return newImage
