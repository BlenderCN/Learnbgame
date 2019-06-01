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
from mathutils.interpolate import poly_3d_calc
import math
import colorsys

# Blender imports
import bpy

# Addon imports
from ...functions import *
from ..Brick import Bricks
from ..Brick.legal_brick_sizes import *


def getMatAtFaceIdx(obj, face_idx):
    """ get material at target face index of object """
    if len(obj.material_slots) == 0:
        return ""
    face = obj.data.polygons[face_idx]
    slot = obj.material_slots[face.material_index]
    mat = slot.material
    matName = mat.name if mat else ""
    return matName


def getUVCoord(mesh, face, point, image):
    """ returns UV coordinate of target point in source mesh image texture
    mesh  -- mesh data from source object
    face  -- face object from mesh
    point -- coordinate of target point on source mesh
    image -- image texture for source mesh
    """
    # get active uv layer data
    uv_layer = mesh.uv_layers.active
    if uv_layer is None:
        return None
    uv = uv_layer.data
    # get 3D coordinates of face's vertices
    lco = [mesh.vertices[i].co for i in face.vertices]
    # get uv coordinates of face's vertices
    luv = [uv[i].uv for i in face.loop_indices]
    # calculate barycentric weights for point
    lwts = poly_3d_calc(lco, point)
    # multiply barycentric weights by uv coordinates
    uv_loc = sum((p*w for p,w in zip(luv,lwts)), Vector((0,0)))
    # ensure uv_loc is in range(0,1)
    # TODO: possibly approach this differently? currently, uv verts that are outside the image are wrapped to the other side
    uv_loc = Vector((uv_loc[0] % 1, uv_loc[1] % 1))
    # convert uv_loc in range(0,1) to uv coordinate
    image_size_x, image_size_y = image.size
    x_co = round(uv_loc.x * (image_size_x - 1))
    y_co = round(uv_loc.y * (image_size_y - 1))
    uv_coord = (x_co, y_co)

    # return resulting uv coordinate
    return Vector(uv_coord)


def getUVLayerData(obj):
    """ returns data of active uv texture for object """
    obj_uv_layers = obj.data.uv_layers if b280() else obj.data.uv_textures
    if len(obj_uv_layers) == 0:
        return None
    active_uv = obj_uv_layers.active
    if active_uv is None:
        obj_uv_layers.active = obj_uv_layers[0]
        active_uv = obj_uv_layers.active
    return active_uv.data


def getFirstImgTexNodes(obj, mat_slot_idx):
    """ return first image texture found in a material slot """
    mat = obj.material_slots[mat_slot_idx].material
    if mat is None or not mat.use_nodes:
        return None
    nodes_to_check = list(mat.node_tree.nodes)
    active_node = mat.node_tree.nodes.active
    if active_node is not None: nodes_to_check.insert(0, active_node)
    img = None
    for node in nodes_to_check:
        if node.type != "TEX_IMAGE":
            continue
        img = verifyImg(node.image)
        if img is not None:
            break
    return img


def getAllFirstImgTexNodes(obj):
    """ return set of first image textures found in all material slots """
    images = set()
    for idx in range(len(obj.material_slots)):
        img = getFirstImgTexNodes(obj, idx)
        if img is not None:
            images.add(img)
    return images



# reference: https://svn.blender.org/svnroot/bf-extensions/trunk/py/scripts/addons/uv_bake_texture_to_vcols.py
def getUVImages(obj):
    """ returns dictionary with duplicate pixel arrays for all UV textures in object """
    scn, cm, _ = getActiveContextInfo()
    # get list of images to store
    if b280():
        # TODO: Reinstate this 2.79 functionality
        images = set()
    else:
        uv_tex_data = getUVLayerData(obj)
        images = set([uv_tex.image for uv_tex in uv_tex_data if uv_tex.image is not None]) if uv_tex_data else set()
    images.add(cm.uvImage)
    images |= getAllFirstImgTexNodes(obj)
    # store images
    uv_images = {}
    for img in images:
        if verifyImg(img) is None:
            continue
        uv_images[img.name] = (img.size[0],
                               img.size[1],
                               img.pixels[:]
                               # Accessing pixels directly is far too slow.
                               #Copied to new array for massive performance-gain.
                               )
    return uv_images


# reference: https://svn.blender.org/svnroot/bf-extensions/trunk/py/scripts/addons/uv_bake_texture_to_vcols.py
def getPixel(pixels, uv_coord):
    """ get RGBA value for specified coordinate in UV image
    pixels    -- list of pixel data from UV texture image
    uv_coord  -- UV coordinate of desired pixel value
    """
    image_size_x, image_size_y, uv_pixels = pixels
    pixelNumber = (image_size_x * int(uv_coord.y)) + int(uv_coord.x)
    r = uv_pixels[pixelNumber*4 + 0]
    g = uv_pixels[pixelNumber*4 + 1]
    b = uv_pixels[pixelNumber*4 + 2]
    a = uv_pixels[pixelNumber*4 + 3]
    # gamma correct RGB value
    r, g, b, a = gammaCorrect([r, g, b, a], 2.0167)
    return (r, g, b, a)


def getAverage(rgba0:Vector, rgba1:Vector, weight:float):
    """ returns weighted average of two rgba values """
    return (rgba1 * weight + rgba0) / (weight + 1)


def getFirstNode(mat, types:list=None):
    """ get first node in material of specified type """
    scn = bpy.context.scene
    if types is None:
        # get material type(s) based on render engine
        if scn.render.engine in ("CYCLES", "BLENDER_EEVEE"):
            types = ("BSDF_PRINCIPLED", "BSDF_DIFFUSE")
        elif scn.render.engine == "octane":
            types = ("OCT_DIFFUSE_MAT")
        # elif scn.render.engine == "LUXCORE":
        #     types = ("CUSTOM")
        else:
            types = ()
    # get first node of target type
    mat_nodes = mat.node_tree.nodes
    for node in mat_nodes:
        if node.type in types:
            return node
    # get first node of any BSDF type
    for node in mat_nodes:
        if len(node.inputs) > 0 and node.inputs[0].type == "RGBA":
            return node
    # no valid node was found
    return None


def createNewMaterial(model_name, rgba, rgba_vals, sss, sat_mat, specular, roughness, ior, transmission, colorSnap, colorSnapAmount, includeTransparency, curFrame=None):
    """ create new material with specified rgba values """
    scn = bpy.context.scene
    # get or create material with unique color
    min_diff = float("inf")
    snapAmount = 0.000001 if colorSnap == "NONE" else colorSnapAmount
    if rgba is None:
        return ""
    r0, g0, b0, a0 = rgba
    for i in range(len(rgba_vals)):
        diff = distance(rgba, rgba_vals[i])
        if diff < min_diff and diff < snapAmount:
            min_diff = diff
            r0, g0, b0, a0 = rgba_vals[i]
            break
    mat_name_end_string = "".join((str(round(r0, 5)), str(round(g0, 5)), str(round(b0, 5)), str(round(a0, 5))))
    mat_name_hash = str(hash_str(mat_name_end_string))[:14]
    mat_name = "Bricker_{n}{f}_{hash}".format(n=model_name, f="_f_%(curFrame)s" % locals() if curFrame is not None else "", hash=mat_name_hash)
    mat = bpy.data.materials.get(mat_name)
    mat_is_new = mat is None
    mat = mat or bpy.data.materials.new(name=mat_name)
    # set diffuse and transparency of material
    if mat_is_new:
        mat.diffuse_color = rgba if b280() else rgba[:3]
        if scn.render.engine == "BLENDER_RENDER":
            mat.diffuse_intensity = 1.0
            if a0 < 1.0:
                mat.use_transparency = True
                mat.alpha = rgba[3]
        elif scn.render.engine in ("CYCLES", "BLENDER_EEVEE", "octane"):
            mat.use_nodes = True
            mat_nodes = mat.node_tree.nodes
            mat_links = mat.node_tree.links
            if scn.render.engine in ("CYCLES", "BLENDER_EEVEE"):
                if b280():
                    # get principled material node
                    principled = mat_nodes.get('Principled BSDF')
                else:
                    # a new material node tree already has a diffuse and material output node
                    output = mat_nodes['Material Output']
                    # remove default Diffuse BSDF
                    diffuse = mat_nodes['Diffuse BSDF']
                    mat_nodes.remove(diffuse)
                    # add Principled BSDF
                    principled = mat_nodes.new('ShaderNodeBsdfPrincipled')
                    # link Principled BSDF to output node
                    mat_links.new(principled.outputs['BSDF'], output.inputs['Surface'])
                # set values for Principled BSDF
                principled.inputs[0].default_value = rgba
                principled.inputs[1].default_value = sss
                principled.inputs[3].default_value[:3] = mathutils_mult(Vector(rgba[:3]), sat_mat).to_tuple()
                principled.inputs[5].default_value = specular
                principled.inputs[7].default_value = roughness
                principled.inputs[14].default_value = ior
                principled.inputs[15].default_value = transmission
                if includeTransparency:
                    # a new material node tree already has a diffuse and material output node
                    output = mat_nodes['Material Output']
                    # create transparent and mix nodes
                    transparent = mat_nodes.new("ShaderNodeBsdfTransparent")
                    mix = mat_nodes.new("ShaderNodeMixShader")
                    # link these nodes together
                    mat_links.new(principled.outputs['BSDF'], mix.inputs[1])
                    mat_links.new(transparent.outputs['BSDF'], mix.inputs[2])
                    mat_links.new(mix.outputs['Shader'], output.inputs["Surface"])
                    # set mix factor to 1 - alpha
                    mix.inputs[0].default_value = 1 - rgba[3]
            elif scn.render.engine == "octane":
                # a new material node tree already has a diffuse and material output node
                output = mat_nodes['Material Output']
                # remove default Diffuse shader
                diffuse = mat_nodes['Octane Diffuse Mat']
                mat_nodes.remove(diffuse)
                # add Octane Glossy shader
                oct_glossy = mat_nodes.new('ShaderNodeOctGlossyMat')
                # set values for Octane Glossy shader
                oct_glossy.inputs[0].default_value = rgba
                oct_glossy.inputs['Specular'].default_value = specular
                oct_glossy.inputs['Roughness'].default_value = roughness
                oct_glossy.inputs['Index'].default_value = ior
                oct_glossy.inputs['Opacity'].default_value = rgba[3]
                oct_glossy.inputs['Smooth'].default_value = True
                mat_links.new(oct_glossy.outputs['OutMat'], output.inputs['Surface'])
            # elif scn.render.engine == "LUXCORE":
            #     # get default Matte shader
            #     matte = mat_nodes['Matte Material']
            #     # set values for Matte shader
            #     matte.inputs[0].default_value = rgba
            #     matte.inputs['Opacity'].default_value = rgba[3]
    else:
        if scn.render.engine == "BLENDER_RENDER":
            # make sure 'use_nodes' is disabled
            mat.use_nodes = False
            # update material color
            if b280():
                r1, g1, b1, a1 = mat.diffuse_color
            else:
                r1, g1, b1 = mat.diffuse_color
                a1 = mat.alpha
            r2, g2, b2, a2 = getAverage(Vector(rgba), Vector((r1, g1, b1, a1)), mat.num_averaged)
            mat.diffuse_color = [r2, g2, b2]
            mat.alpha = a2
        # if scn.render.engine in ("CYCLES", "BLENDER_EEVEE", "octane", "LUXCORE"):
        if scn.render.engine in ("CYCLES", "BLENDER_EEVEE", "octane"):
            # make sure 'use_nodes' is enabled
            mat.use_nodes = True
            # get first node
            first_node = getFirstNode(mat)
            # update first node's color
            if first_node:
                rgba1 = first_node.inputs[0].default_value
                newRGBA = getAverage(Vector(rgba), Vector(rgba1), mat.num_averaged)
                first_node.inputs[0].default_value = newRGBA
                first_node.inputs[3].default_value[:3] = mathutils_mult(Vector(newRGBA[:3]), sat_mat).to_tuple()
    mat.num_averaged += 1
    return mat_name


def verifyImg(im):
    """ verify image has pixel data """
    return im if im is not None and im.pixels is not None and len(im.pixels) > 0 else None


def getUVImage(scn, obj, face_idx, uvImage):
    """ returns UV image (priority to user settings, then face index, then first one found in object """
    image = verifyImg(uvImage)
    # TODO: Reinstate this functionality for b280()
    if not b280() and image is None and obj.data.uv_textures.active:
        image = verifyImg(obj.data.uv_textures.active.data[face_idx].image)
    if image is None:
        try:
            mat_idx = obj.data.polygons[face_idx].material_index
            image = verifyImg(getFirstImgTexNodes(obj, mat_idx))
        except IndexError:
            mat_idx = 0
            while image is None and mat_idx < len(obj.material_slots):
                image = verifyImg(getFirstImgTexNodes(obj, mat_idx))
                mat_idx += 1
    return image


def getUVPixelColor(scn, obj, face_idx, point, uv_images, uvImage):
    """ get RGBA value for point in UV image at specified face index """
    if face_idx is None:
        return None
    # get closest material using UV map
    face = obj.data.polygons[face_idx]
    # get uv_layer image for face
    image = getUVImage(scn, obj, face_idx, uvImage)
    if image is None:
        return None
    # get uv coordinate based on nearest face intersection
    uv_coord = getUVCoord(obj.data, face, point, image)
    # retrieve rgba value at uv coordinate
    rgba = getPixel(uv_images[image.name], uv_coord)
    return rgba


def getMaterialColor(matName):
    """ get RGBA value of material """
    mat = bpy.data.materials.get(matName)
    if mat is None:
        return None
    if mat.use_nodes:
        node = getFirstNode(mat)
        if not node:
            return None
        r, g, b = node.inputs[0].default_value[:3]
        if node.type in ("BSDF_GLASS", "BSDF_TRANSPARENT", "BSDF_REFRACTION"):
            a = 0.25
        elif node.type in ("VOLUME_SCATTER", "VOLUME_ABSORPTION", "PRINCIPLED_VOLUME"):
            a = node.inputs["Density"].default_value
        else:
            a = node.inputs[0].default_value[3]
    else:
        if b280():
            r, g, b, a = mat.diffuse_color
        else:
            r, g, b = mat.diffuse_color
            intensity = mat.diffuse_intensity
            r = r * intensity
            g = g * intensity
            b = b * intensity
            a = mat.alpha if mat.use_transparency else 1.0
    return [r, g, b, a]


def getBrickRGBA(scn, obj, face_idx, point, uv_images, uvImage=None):
    """ returns RGBA value for brick """
    if face_idx is None:
        return None, None
    # get material based on rgba value of UV image at face index
    image = getUVImage(scn, obj, face_idx, uvImage)
    if image is not None:
        origMatName = ""
        rgba = getUVPixelColor(scn, obj, face_idx, point, uv_images, image)
    else:
        # get closest material using material slot of face
        origMatName = getMatAtFaceIdx(obj, face_idx)
        rgba = getMaterialColor(origMatName) if origMatName is not None else None
    return rgba, origMatName


def getDetailsAndBounds(obj, cm=None):
    """ returns dimensions and bounds of object """
    cm = cm or getActiveContextInfo()[1]
    obj_details = bounds(obj)
    dimensions = Bricks.get_dimensions(cm.brickHeight, cm.zStep, cm.gap)
    return obj_details, dimensions


def getArgumentsForBricksDict(cm, source=None, dimensions=None, brickSize=[1, 1, 3]):
    """ returns arguments for makeBricksDict function """
    source = source or cm.source_obj
    customData = [None] * 3
    if dimensions is None:
        dimensions = Bricks.get_dimensions(cm.brickHeight, cm.zStep, cm.gap)
    for i, customInfo in enumerate([[cm.hasCustomObj1, cm.customObject1], [cm.hasCustomObj2, cm.customObject2], [cm.hasCustomObj3, cm.customObject3]]):
        hasCustomObj, customObj = customInfo
        if (i == 0 and cm.brickType == "CUSTOM") or hasCustomObj:
            scn = bpy.context.scene
            # duplicate custom object
            customObjName = customObj.name + "__dup__"
            customObj1 = bpy.data.objects.get(customObjName)
            customObj0 = duplicate(customObj)
            # TODO: remove this object on delete action
            safeUnlink(customObj0)
            customObj0.name = customObjName
            customObj0.parent = None
            # TODO: apply modifiers & shape keys here with Object.to_mesh?
            # apply transformation to custom object
            apply_transform(customObj0)
            # get custom object details
            curCustomObj_details = bounds(customObj0)
            # set brick scale
            scale = cm.brickHeight/curCustomObj_details.dist.z
            brickScale = Vector((scale * curCustomObj_details.dist.x + dimensions["gap"],
                        scale * curCustomObj_details.dist.y + dimensions["gap"],
                        scale * curCustomObj_details.dist.z + dimensions["gap"]))
            # get transformation matrices
            t_mat = Matrix.Translation(-curCustomObj_details.mid)
            maxDist = max(curCustomObj_details.dist)
            s_mat_x = Matrix.Scale((brickScale.x - dimensions["gap"]) / curCustomObj_details.dist.x, 4, Vector((1, 0, 0)))
            s_mat_y = Matrix.Scale((brickScale.y - dimensions["gap"]) / curCustomObj_details.dist.y, 4, Vector((0, 1, 0)))
            s_mat_z = Matrix.Scale((brickScale.z - dimensions["gap"]) / curCustomObj_details.dist.z, 4, Vector((0, 0, 1)))
            # apply transformation to custom object dup mesh
            customObj0.data.transform(t_mat)
            customObj0.data.transform(mathutils_mult(s_mat_x, s_mat_y, s_mat_z))
            # center mesh origin
            centerMeshOrigin(customObj0.data, dimensions, brickSize)
            # store fresh data to customData variable
            customData[i] = customObj0.data
            # remove extra object and replace old custom data
            if customObj1 is not None:
                customObj1.data = customObj0.data
                bpy.data.objects.remove(customObj0)
    if cm.brickType != "CUSTOM":
        brickScale = Vector((dimensions["width"] + dimensions["gap"],
                    dimensions["width"] + dimensions["gap"],
                    dimensions["height"]+ dimensions["gap"]))
    return brickScale, customData


def isBrickExposed(bricksDict, zStep, key=None, loc=None):
    """ return top and bottom exposure of brick loc/key """
    assert key is not None or loc is not None
    # initialize vars
    key = key or listToStr(loc)
    loc = loc or getDictLoc(bricksDict, key)
    keysInBrick = getKeysInBrick(bricksDict, bricksDict[key]["size"], zStep, loc=loc)
    topExposed, botExposed = False, False
    # top or bottom exposed if even one location is exposed
    for k in keysInBrick:
        if bricksDict[k]["top_exposed"]: topExposed = True
        if bricksDict[k]["bot_exposed"]: botExposed = True
    return topExposed, botExposed


def setAllBrickExposures(bricksDict, zStep, key=None, loc=None):
    """ updates top_exposed/bot_exposed for all bricks in bricksDict """
    assert key is not None or loc is not None
    # initialize vars
    key = key or listToStr(loc)
    loc = loc or getDictLoc(bricksDict, key)
    keysInBrick = getKeysInBrick(bricksDict, bricksDict[key]["size"], zStep, loc=loc)
    topExposed, botExposed = False, False
    # set brick exposures
    for k in keysInBrick:
        curTopExposed, curBotExposed = setBrickExposure(bricksDict, k)
        if curTopExposed: topExposed = True
        if curBotExposed: botExposed = True
    return topExposed, botExposed


def setBrickExposure(bricksDict, key=None, loc=None):
    """ set top and bottom exposure of brick loc/key """
    assert key is not None or loc is not None
    # initialize parameters unspecified
    loc = loc or getDictLoc(bricksDict, key)
    key = key or listToStr(loc)
    # get size of brick and break conditions
    if key not in bricksDict: return None, None
    # get keys above and below
    x, y, z = loc
    keyBelow = listToStr((x, y, z - 1))
    keyAbove = listToStr((x, y, z + 1))
    # check if brick top or bottom is exposed
    topExposed = checkExposure(bricksDict, keyAbove, obscuringTypes=getTypesObscuringBelow())
    botExposed = checkExposure(bricksDict, keyBelow, obscuringTypes=getTypesObscuringAbove())
    bricksDict[key]["top_exposed"] = topExposed
    bricksDict[key]["bot_exposed"] = botExposed
    return topExposed, botExposed


def checkExposure(bricksDict, key, obscuringTypes=[]):
    """ checks if brick at given key is exposed """
    try:
        val = bricksDict[key]["val"]
    except KeyError:
        return True
    parent_key = getParentKey(bricksDict, key)
    typ = bricksDict[parent_key]["type"]
    return val == 0 or typ not in obscuringTypes
