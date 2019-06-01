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

# <pep8 compliant>

'''
Module with functions for exporting Neverwinter Nights models from Blender.

The module contains a number of functions for exporting a blender model to a
model usable in the game Neverwinter Nights from Bioware. The export works in
concert with the other modules in this package, and especially the borealis
GUI.

@author: Erik Ylipää
'''

import os

import bpy
from bpy.props import CollectionProperty, StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper
import mathutils
from mathutils import Vector

from . import basic_props
from . import node_props
from . import blend_props
from . import mdl


class BorealisExport(bpy.types.Operator, ExportHelper):
    """ Exports a Blender Object hierarchy to a Neverwinter Nights mdl model.

            This class is the Blender Operator which initiates the export.

    """

    bl_idname = "export_mesh.nwn_mdl"
    bl_label = "Export NWN .mdl"

    filepath = bpy.props.StringProperty(name="File Path",
                          description="File path used for exporting "
                                      "the NWN model",
                          maxlen=1024,
                          default="")
    filename_ext = ".mdl"
    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})

    use_root_name = BoolProperty(name="Use Root Object Name",
                                 description=("Use the name of the root object "
                                 "as the model name and filename like "
                                 "Neverwinter Nights expects, if false the "
                                 "filename will be used as the model name in"
                                 " the model file"),
                                 default=True)
    do_export_animations = BoolProperty(name="Export Animations",
                                     description="Toggle whether animations "
                                     "should be exported or not",
                                     default=True)
    force_tris = BoolProperty(name="Autotriangulate quad faces",
                                       description="Automatically convert quad"
                                       " faces to tris. The export will fail"
                                       " if this is unchecked and there are"
                                       " quad faces in any mesh",
                                       default=True)

    @classmethod
    def poll(cls, context):
        ## Check to see that the root object exists

        return context.scene.nwn_props.root_object_name != None

    def execute(self, context):
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        return export_nwn_mdl(context,
                              **self.as_keywords(ignore=("check_existing",
                                                         "filter_glob")))


def export_nwn_mdl(context, use_root_name=True,
                   do_export_animations=True,
                   **kwargs):
    """ Exports an Object tree into a nwn mdl.

            Initiates the export of the Blender Object tree into a
            Neverwinter Nights mdl Model.

            For the export to work, the custom property on the current Scene
            object should have the property scene.nwn_props.root_object_name
            set to a valid name.

            The objects which should be exported also has to have the
            is_nwn_object flag set to true, otherwise they will be ignored,
            as well as any children they might have.

            Arguments:
                context - the current context, should be passed from the
                    Operator doing the export.

            Keyword arguments:
                use_root_name - The model will be named according to the name
                    of the Object set as root object of the mdl
                export_animations - Whether to export animations or not. True
                    to export animations, False to only export geometry
    """
    #We assume the first frame contains the static pose and change frame accordingly
    context.scene.frame_current = 1
    scene_props = context.scene.nwn_props
    root_object = context.scene.objects[scene_props.root_object_name]

    if use_root_name:
        model_name = root_object.name
    else:
        filepath = kwargs['filepath']
        base_name = os.path.basename(kwargs['filepath'])
        model_name, ext = os.path.splitext(base_name)

    #poll should catch this
    if not root_object:
        return {'CANCELLED'}

    mdl_object = mdl.Model(model_name)
    mdl_object.classification = scene_props.classification
    if scene_props.supermodel:
        mdl_object.supermodel = scene_props.supermodel
    else:
        mdl_object.supermodel = "NULL"
    mdl_object.setanimationscale = scene_props.animationscale

    #this will act as an accumulator, containing the exported objects
    exported_objects = []
    export_geometry(mdl_object, root_object, exported_objects, **kwargs)

    if do_export_animations:
        export_animations(context.scene, mdl_object, root_object,
                          exported_objects, **kwargs)

#    if os.path.exists(kwargs['filepath']):
#        print("Path exists")
#    else:
    file = open(kwargs['filepath'], 'w')
    file.write(str(mdl_object))
    file.close()

    return {'FINISHED'}


def export_geometry(mdl_object, obj, exported_objects, **kwargs):
    """ Export the root Object as the mdl root node """
    node = mdl_object.new_geometry_node("dummy", obj.name)
    node['parent'] = "NULL"
    exported_objects.append(obj)
    for child in obj.children:
        if blend_props.get_nwn_props(child).is_nwn_object:
            export_node(mdl_object, child, obj.name, exported_objects, **kwargs)


def export_node(mdl_object, obj, parent, exported_objects, **kwargs):
    """ Export an object as a NWN geometry node.

    """

    props = blend_props.get_nwn_props(obj)
    node_type = props.nwn_node_type

    node = mdl_object.new_geometry_node(node_type, obj.name)
    node['parent'] = parent

    w, x, y, z = obj.rotation_axis_angle
    orientation = [x, y, z, w]
    node['orientation'] = orientation

    node['position'] = obj.location

    for prop in node_props.GeometryNodeProperties.get_node_properties(node_type):
        #only export the properties which are set in the properties group
        if prop.name in props.node_properties and not prop.blender_ignore:
            node[prop.name] = eval("props.node_properties." + prop.name)

    if node_type in ["trimesh", "skin", "danglymesh", "aabb"]:
        export_mesh(obj, node, **kwargs)
    elif node_type == "light":
        node['color'] = obj.data.color[:]
        node['radius'] = obj.data.distance

    exported_objects.append(obj)
    for child in obj.children:
        if props.is_nwn_object:
            export_node(mdl_object, child, obj.name, exported_objects, **kwargs)


def export_mesh(obj, node, force_tris=True, **kwargs):
    """ Exports the mesh data of a Mesh object to a nwn node """
    mesh = obj.data
    uv_faces = None
    image = None

    #since NWN only accepts triangles as faces, we have to convert the mesh
    # to tris. We don't wont to do this destructively though, so we do it to a
    # copy of the mesh
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_name(name=obj.name)
    bpy.ops.object.duplicate()
    ob_dup = bpy.context.object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode='OBJECT')

    mesh = ob_dup.data

    if mesh.uv_textures:
        uv_faces = mesh.uv_textures.active.data
        image = uv_faces[0].image

    vertices = [vert.co[:] for vert in mesh.vertices]
    node['verts'] = vertices

    faces = []
    uv_verts = []
    uv_verts_dict = {}

    uv_verts
    for i, face in enumerate(mesh.faces):
        v1, v2, v3 = face.vertices[:]
        smooth_group = 1
        mat_id = 1
        if mesh.materials:
            if "smooth" in mesh.materials[face.material_index].name.lower():
                smooth_group = face.material_index + 1
            mat = mesh.materials[face.material_index]
            mat_names = [mat_["name"] for mat_ in basic_props.walkmesh_materials]
            if mat.name in mat_names:
                mat_id = mat_names.index(mat.name)

        if uv_faces:
            uv_co1, uv_co2, uv_co3 = uv_faces[i].uv1, uv_faces[i].uv2, uv_faces[i].uv3

            if uv_co1[0] not in uv_verts_dict:
                uv_verts_dict[uv_co1[0]] = {}
            if uv_co1[1] not in uv_verts_dict[uv_co1[0]]:
                uv1 = len(uv_verts)
                uv_verts.append(uv_co1[:])
                uv_verts_dict[uv_co1[0]][uv_co1[1]] = uv1
            else:
                uv1 = uv_verts_dict[uv_co1[0]][uv_co1[1]]

            if uv_co2[0] not in uv_verts_dict:
                uv_verts_dict[uv_co2[0]] = {}
            if uv_co2[1] not in uv_verts_dict[uv_co2[0]]:
                uv2 = len(uv_verts)
                uv_verts.append(uv_co2[:])
                uv_verts_dict[uv_co2[0]][uv_co2[1]] = uv2
            else:
                uv2 = uv_verts_dict[uv_co2[0]][uv_co2[1]]

            if uv_co3[0] not in uv_verts_dict:
                uv_verts_dict[uv_co3[0]] = {}
            if uv_co3[1] not in uv_verts_dict[uv_co3[0]]:
                uv3 = len(uv_verts)
                uv_verts.append(uv_co3[:])
                uv_verts_dict[uv_co3[0]][uv_co3[1]] = uv3
            else:
                uv3 = uv_verts_dict[uv_co3[0]][uv_co3[1]]
        else:
            uv1, uv2, uv3 = 0, 0, 0
        face_line = [v1, v2, v3, smooth_group, uv1, uv2, uv3, mat_id]

        faces.append(face_line)

    #add the third value to the tverts
    tverts = [[uv1, uv2, 0] for uv1, uv2 in uv_verts]
    node['tverts'] = tverts
    node['faces'] = faces

    if image:
        #use the filename for the texture as primary name
        #fall back on the name of the image
        if os.path.exists(image.filepath):
            image_filename = os.path.basename(image.filepath)
            node['bitmap'], ext = os.path.splitext(image_filename)
        else:
            node['bitmap'] = image.name
    else:
        node['bitmap'] = "NULL"

    if node.type == "danglymesh":
        vertex_group_name = blend_props.get_nwn_props(obj).danglymesh_vertexgroup
        if vertex_group_name:
            vertex_group = obj.vertex_groups[vertex_group_name]
            constraints = []
            for i in range(len(mesh.vertices)):
                constraint = vertex_group.weight(i) * 255
                constraint = 255 - int(constraint)
                constraints.append([constraint])
            node['constraints'] = constraints

    elif node.type == "skin":
        bones = []
        hooks = [mod for mod in obj.modifiers if mod.type == 'HOOK']

        bones_list = [{} for vert in mesh.vertices]

        for hook in hooks:
            if not (hook.vertex_group and hook.object):
                break

            vertex_group = obj.vertex_groups[hook.vertex_group]

            for i, bones in enumerate(bones_list):
                #there doesn't seem to be any way of checking whether a vertex i in a group
                # hence this try-clause
                try:
                    if vertex_group.weight(i) > 0:
                        bones[hook.object.name] = vertex_group.weight(i)
                except RuntimeError:
                    pass

        weights = []
        for bones in bones_list:
            total_weight = 0
            for weight in bones.values():
                total_weight += weight
            norm_co = 1 / total_weight
            line = []
            for bone, weight in bones.items():
                line.append(bone)
                line.append("%.9g" % (weight * norm_co))
            weights.append(line)

        node["weights"] = weights

    elif node.type == "aabb":
        root_node = build_aabb_tree(ob_dup)
        node["aabb"] = root_node

    bpy.ops.object.delete()


def build_aabb_tree(obj):
    """ Takes a object as an argument and returns a axis aligned bounding box tree """
    faces = obj.data.faces

    # Since the face-list in the mesh only contains the indices for the
    # verts, we create our own facelist whith the verts coords directly
    # available. For simplicity.
    facelist = [{"verts": [obj.data.vertices[v].co for v in face.vertices],
                 "index": index,
                 "center": face.center} for index, face in enumerate(faces)]
    level = 1
    root_node = recursive_aabb(facelist, None, level)
    return root_node


def recursive_aabb(facelist, parent, level):
    """ Recursively build a tree of aabb nodes, returns the root of the subtree.
    """
    # This code is heavily inspired by nwmax and Waylands original code
    if level > 20:
        raise RuntimeError("Max recursion depth reached when building aabb "
                           "tree. Look for duplicate faces.")

    bottom_left = Vector((10000, 10000, 10000))
    top_right = Vector((-10000, -10000, -10000))
    midpoints = Vector((0, 0, 0))
    # First we calculate the bounding box
    for face in facelist:
        for x, y, z in face["verts"]:
            if x < bottom_left.x:
                bottom_left.x = x
            if y < bottom_left.y:
                bottom_left.y = y
            if z < bottom_left.z:
                bottom_left.z = z

            if x > top_right.x:
                top_right.x = x
            if y > top_right.y:
                top_right.y = y
            if z > top_right.z:
                top_right.z = z
        midpoints += face["center"]

    midpoint = midpoints / len(facelist)

    bounding_box = {"co1": bottom_left[:], "co2": top_right[:],
                    "index": -1, "left": None,
                    "right": None, "parent": parent}

    ## If this is a leaf we're done
    if len(facelist) == 1:
        bounding_box["index"] = facelist[0]["index"]
        return bounding_box

    ## Otherwise we have to decide how to do the splits
    splits = {"x": {"left": [], "right": []},
              "y": {"left": [], "right": []},
              "z": {"left": [], "right": []}}

    #find the best split, which is the split where the two sides are balanced
    for face in facelist:
        if face["center"].x < midpoint.x:
            splits["x"]["left"].append(face)
        else:
            splits["x"]["right"].append(face)
        if face["center"].y < midpoint.y:
            splits["y"]["left"].append(face)
        else:
            splits["y"]["right"].append(face)
        if face["center"].z < midpoint.z:
            splits["z"]["left"].append(face)
        else:
            splits["z"]["right"].append(face)

    split = None

    #We calculate the difference between the two sides
    delta_x = abs(len(splits["x"]["right"]) - len(splits["x"]["left"]))
    delta_y = abs(len(splits["y"]["right"]) - len(splits["y"]["left"]))
    delta_z = abs(len(splits["z"]["right"]) - len(splits["z"]["left"]))

    # We pick the split where the difference between the splits are as small as possible
    if delta_x < delta_y and delta_x < delta_z:
        split = splits["x"]
    elif delta_y < delta_z:
        split = splits["y"]
    else:
        split = splits["z"]

    if split["left"]:
        bounding_box["left"] = recursive_aabb(split["left"], bounding_box, level + 1)
    if split["right"]:
        bounding_box["right"] = recursive_aabb(split["right"], bounding_box, level + 1)
    return bounding_box


def export_animations(scene, mdl_object, root_object, exported_objects, **kwargs):
    """ Exports the Blender animations of the model """
    animations = scene.nwn_props.animations

    if not animations:
        return

    animation_data = build_animation_data(exported_objects, animations)

    for animation in animations:
        export_animation(animation_data[animation.name], scene, animation, mdl_object, root_object)


def export_animation(animation_data, scene, animation, mdl_object, root_object):
    """ Exports a single animation from Blender to the nwn mdl_object """

    fps = scene.render.fps
    nwn_anim = mdl_object.new_animation(animation.name)
    nwn_anim.animroot = animation.animroot
    start_frame = animation.start_frame
    end_frame = animation.end_frame
    nwn_anim.length = (end_frame - start_frame) / fps
    nwn_anim.transtime = animation.transtime

    for event in animation.events:
        nwn_anim.events.append((event.time, event.type))
    root_node = nwn_anim.new_node("dummy", root_object.name)
    root_node['parent'] = 'NULL'

    for child in root_object.children:
        if blend_props.get_nwn_props(child).is_nwn_object:
            export_animation_node(fps, animation_data, animation, nwn_anim, mdl_object, child, root_object.name)


def export_animation_node(fps, animation_data, animation, nwn_anim, mdl_object, obj, parent):
    """ Exports the animations of a Blender Object as a nwn animation node.

    """
    props = blend_props.get_nwn_props(obj)
    node_type = props.nwn_node_type
    node = nwn_anim.new_node("dummy", obj.name)
    node['parent'] = parent
    start_frame = animation.start_frame
    if obj.name in animation_data['nodes']:
        if "location" in animation_data['nodes'][obj.name]:
            locations = sorted(animation_data['nodes'][obj.name]["location"].items())
            positionkeys = [[(time - start_frame) / fps, pos['x'], pos['y'], pos['z']] for time, pos in locations]
            node['positionkey'] = positionkeys

        if "rotation_axis_angle" in animation_data['nodes'][obj.name]:
            rotations = sorted(animation_data['nodes'][obj.name]["rotation_axis_angle"].items())
            orientationkey = [[(time - start_frame) / fps, ori['x'], ori['y'], ori['z'], ori['w']] for time, ori in rotations]
            node['orientationkey'] = orientationkey

    for child in obj.children:
        if blend_props.get_nwn_props(child).is_nwn_object:
            export_animation_node(fps, animation_data, animation, nwn_anim, mdl_object, child, obj.name)


def build_animation_data(objects, animations):
    """ Creates a dictionary with the blender animation data suitable for nwn.

           The function builds a nested dictionary with a layout similar to how
           animations are describe by the neverwinter nights ascii mdl.
    """

    #The animation_list is a list of animations represented as dictionaries
    animation_list = [{"name": animation.name,
                       "start_frame": animation.start_frame,
                       "end_frame": animation.end_frame,
                       "nodes": {}} for animation in animations]

    #We sort the list in the order of the animations start frame
    animation_list.sort(key=lambda x: x["start_frame"])

    #Times is a dictionary where the keys are different times. The values in
    #turn are also dictionaries for all keyframes which occurs at the time
    times = {}

    # We go through all objects animation data and extract all their keyframes
    # the keyframes are inserted into the times dict at the time they occur.
    for object in objects:
        if not object.animation_data:
            continue
        for fcurve in object.animation_data.action.fcurves:
            if fcurve.data_path == "location":
                if fcurve.array_index == 0:
                    attribute_name = "x"
                elif fcurve.array_index == 1:
                    attribute_name = "y"
                elif fcurve.array_index == 2:
                    attribute_name = "z"
            elif fcurve.data_path == "rotation_axis_angle":
                if fcurve.array_index == 0:
                    attribute_name = "w"
                elif fcurve.array_index == 1:
                    attribute_name = "x"
                elif fcurve.array_index == 2:
                    attribute_name = "y"
                elif fcurve.array_index == 3:
                    attribute_name = "z"

            for point in fcurve.keyframe_points:
                frame, value = point.co
                if frame not in times:
                    times[frame] = {}
                if object.name not in times[frame]:
                    times[frame][object.name] = {}
                if fcurve.data_path not in times[frame][object.name]:
                    times[frame][object.name][fcurve.data_path] = {}
                times[frame][object.name][fcurve.data_path][attribute_name] = value

    #We now extract the data as a list of tuples, and sort them according to
    #the time they occur
    times_list = sorted(times.items())

    # We go through all the times in order, starting with the first and insert
    # them into the right animation. The animation_list has to be sorted
    # for this to work, which is done at the top
    current_frame, key_nodes = times_list.pop(0)
    done = False
    for animation in animation_list:
        if done:
            break
        while(current_frame <= animation['end_frame']):
            #The animation has to have a keyframe after the start frame,
            #otherwise it won't get inserted into this animation
            if current_frame >= animation['start_frame']:
                for node, data_paths in key_nodes.items():
                    if node not in animation['nodes']:
                        animation['nodes'][node] = {}
                    for path, attributes in data_paths.items():
                        if path not in animation['nodes'][node]:
                            animation['nodes'][node][path] = {}
                        animation['nodes'][node][path][current_frame] = attributes
            if times_list:
                current_frame, key_nodes = times_list.pop(0)
            else:
                done = True

    animation_dict = dict(zip([animation['name'] for animation in animation_list],
                               animation_list))
    return animation_dict
