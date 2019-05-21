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
Module with functions for importing a Neverwinter Nights model to Blender.

The module contains function which handles different parts of importing
a Neverwinter Nights mdl model into blender. It depends heavily on custom
properties for all Neverwinter specific settings.

@author: Erik Ylipää
'''

import os

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import CollectionProperty, StringProperty, BoolProperty

from . import mdl
from . import blend_props
from . import basic_props

IMAGE_EXTENSIONS = ["tga", "dds", "TGA", "DDS"]
DEFAULT_IMG_SIZE = 128


class BorealisImport(bpy.types.Operator, ImportHelper):
    '''
    Import Neverwinter Nights model in ascii format
    '''
    bl_idname = "import_mesh.nwn_mdl"
    bl_label = "Import NWN Mdl"

    filename_ext = ".mdl"

    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})

    files = CollectionProperty(name="File Path",
                          description="File path used for importing "
                                      "the MDL file",
                          type=bpy.types.OperatorFileListElement)
    directory = StringProperty(subtype='DIR_PATH')

    do_import_animations = BoolProperty(name="Import animations", default=True,
                                     description="Should the animations be"
                                     "imported as well. If not selected, only"
                                     " geometry will be imported.")

    def execute(self, context):
        kwargs = self.as_keywords(ignore=("check_existing", "filter_glob",
                                          "files" "directory", "filename_ext"))
        import_mdl(self.filepath, context, **kwargs)
        return {'FINISHED'}


def import_mdl(filename, context, enforce_lowercase_names=True,
               do_import_animations=True, **kwargs):
    """
    Imports a Neverwinter Nights model
    """
    mdl_object = mdl.Model()
    mdl_object.from_file(filename)

    objects = []

    print("Import nwn model")

    if enforce_lowercase_names:
        mdl_object.name = mdl_object.name.lower()
        for node in mdl_object.geometry.nodes:
            node.name = node.name.lower()
            node["parent"] = node["parent"].lower()
            if node.type == "skin":
                if node["weights"].value_written:
                    for row in node["weights"]:
                        for i in enumerate(row):
                            row[i] = row[i].lower()
        for animation in mdl_object.animations:
            animation.name = animation.name.lower()
            animation.animroot = animation.animroot.lower()
            for node in animation.nodes:
                node.name = node.name.lower()
                node["parent"] = node["parent"].lower()

    #Some of the import stuff assumes we're in object-mode, and we set it
    #accordingly
    #Theres a bug here; if there are no objects in the scene we can't set the mode to OBJECT
    #bpy.ops.object.mode_set(mode='OBJECT')

    import_geometry(mdl_object, filename, context, objects, **kwargs)
    if mdl_object.animations and do_import_animations:
        import_animations(mdl_object, context, objects,
                          **kwargs)

    #the basic settings for the models are assigned to the active scene object
    scene = context.scene
    scene.nwn_props.root_object_name = mdl_object.name

    scene.nwn_props.classification = mdl_object.classification
    scene.nwn_props.supermodel = mdl_object.supermodel
    scene.nwn_props.animationscale = float(mdl_object.setanimationscale)


def import_geometry(mdl_object, filename, context, objects, **kwargs):
    #create meshes from all nodes
    for node in mdl_object.geometry.nodes:

        node_name = node.name
        if node.type in ["dummy", "emitter", "reference"]:
            ob = bpy.data.objects.new(node_name, None)

        elif node.type in ["trimesh", "danglymesh", "skin", "aabb"]:
            mesh = bpy.data.meshes.new(node_name + "Mesh")
            ob = bpy.data.objects.new(node_name, mesh)

            ### set up geometry ###

            verts = [[float(comp) for comp in vert] for vert in node.get_prop_value("verts")]
            faces = [[int(vert) for vert in face[:3]] for face in node.get_prop_value("faces")]
            mesh.from_pydata(verts, [], faces)

            ### set up texture and uv-coords ###
            setup_texture(mesh, node, filename)

            mesh.validate()
            mesh.update()

            if node.type == "danglymesh":
                #set up a weight-map for the danlgymesh
                vertex_group = ob.vertex_groups.new("danglymesh_constraints")
                blend_props.get_nwn_props(ob).danglymesh_vertexgroup = "danglymesh_constraints"
                for i, [const] in enumerate(node['constraints']):
                    constraint = 255 - const  # a weight of 1 is completely solid when using softbody
                    weight = constraint / 255.0

                    vertex_group.add([i], weight, 'ADD')

            elif node.type == "skin":
                #set up the skin, this will require a non-trivial solution
                nwn_weights = node['weights']
                weights_dict = {}
                for i, weight_line in enumerate(nwn_weights):
                    #this parses the line to simplify creation of the dictionary
                    line = zip([bone for i, bone in enumerate(weight_line) if i % 2 == 0],
                                [float(weight) for i, weight in enumerate(weight_line) if i % 2 != 0])
                    for bone, weight in line:
                        if bone not in weights_dict:
                            weights_dict[bone] = {}
                        weights_dict[bone][i] = weight

                for bone, weights in weights_dict.items():
                    vertex_group_name = "nwn_skin_" + bone
                    vertex_group = ob.vertex_groups.new(vertex_group_name)
                    for index, weight in weights.items():
                        vertex_group.add([index], weight, 'ADD')

                    ##add the hook modifier
                    hook_name = "nwn_skin_hook_" + bone
                    hook_mod = ob.modifiers.new(name=hook_name, type='HOOK')
                    hook_mod.object = bpy.data.objects[bone]
                    hook_mod.vertex_group = vertex_group_name

            elif node.type == "aabb":
                blend_props.create_walkmesh_materials(ob)
                mesh_mats = [mat.name for mat in ob.data.materials[:]]
                for i, face in enumerate(node["faces"]):
                    mat_id = face[-1]
                    material = basic_props.walkmesh_materials[mat_id]

                    index = mesh_mats.index(material["name"])
                    ob.data.faces[i].material_index = index

#                import_aabb(ob, node)

        elif node.type == "light":
            lamp_data = bpy.data.lamps.new(node_name + "Lamp", 'POINT')
            ob = bpy.data.objects.new(node_name, lamp_data)
            lamp_data.color = node['color']
            lamp_data.distance = node['radius']
            lamp_data.use_sphere = True

#        elif node.type == "emitter":
#            #set up a dummy mesh used as the emitter
#            mesh = bpy.data.meshes.new(node_name + "Mesh")
#            ob = bpy.data.objects.new(node_name, mesh)
#
#            verts = [[0, 0, 0]]
#            faces = []
#            mesh.from_pydata(verts, [], [])
#
#            mesh.validate()
#            mesh.update()

        #set up parent, we assume the parent node is already imported
        parent_name = node.get_prop_value("parent")
        try:
            parent_ob = bpy.data.objects[parent_name]
        except KeyError:
            print("No such parent: %s" % parent_name)
        else:
            ob.parent = parent_ob

        #set up location
        location = node.get_prop_value("position")
        if not location:
            location = [0, 0, 0]
        ob.location = location

        #set up rotation
        orientation = node.get_prop_value("orientation")
        if orientation:
            axis = orientation[:3]
            angle = orientation[3]

            ob.rotation_mode = "AXIS_ANGLE"
            ob.rotation_axis_angle = [angle] + axis

        bpy.context.scene.objects.link(ob)
        objects.append(ob)

        #this has to be done after the object has been linked to the scene
        if node.type == "skin":
            bpy.ops.object.select_name(name=ob.name)
            bpy.ops.object.mode_set(mode='EDIT')
            for modifier in ob.modifiers:
                if modifier.type == 'HOOK':

                    bpy.ops.object.hook_reset(modifier=modifier.name)
            bpy.ops.object.mode_set(mode='OBJECT')

        props = blend_props.get_nwn_props(ob)
        props.nwn_node_type = node.type
        props.is_nwn_object = True

        for prop_name, prop in node.properties.items():
            if prop.blender_ignore or not prop.value_written:
                continue
            exec("props.node_properties.%s = prop.value" % prop_name)


def import_aabb(ob, node):
    """ Imports the aabb data of a node as mesh objects """
    def recursive_aabb(current_node, parent_ob):
        bob_mesh = bpy.data.meshes.new("AABB" + "Mesh")
        bob = bpy.data.objects.new("AABB", bob_mesh)
        bob.parent = parent_ob
        x1, y1, z1 = current_node["co1"]
        x2, y2, z2 = current_node["co2"]

        verts = [[x1, y1, z1], [x2, y1, z1], [x2, y2, z1],
                 [x1, y2, z1], [x1, y2, z2], [x1, y1, z2],
                 [x2, y1, z2], [x2, y2, z2]]
        faces = [[0, 1, 4, 2]]
        bob_mesh.from_pydata(verts, [], faces)
        bob.draw_type = 'BOUNDS'

        bpy.context.scene.objects.link(bob)

        left = current_node["left"]
        right = current_node["right"]

        if left:
            recursive_aabb(left, bob)
        if right:
            recursive_aabb(right, bob)

    root_node = node["aabb"]

    recursive_aabb(root_node, ob)


def setup_texture(mesh, node, filename):
    #if the node has no texture vertices, do nothing
    if not node.get_prop_value("tverts"):
        return

    ##load image ###
    image_name = node.get_prop_value("bitmap")
    image_name = image_name.lower()
    image = None
    if image_name not in bpy.data.images:
        image_path_base = os.path.join(os.path.dirname(filename), image_name)
        for ext in IMAGE_EXTENSIONS:
            path = image_path_base + "." + ext
            if os.path.exists(path):
                bpy.ops.image.open(filepath=path)
                image = bpy.data.images[os.path.basename(path)]
                image.name = image_name
                break

        #if the file couldn't be found, we create a dummy image with the right name
        if not image:
            bpy.ops.image.new(name=image_name, width=DEFAULT_IMG_SIZE,
                                      height=DEFAULT_IMG_SIZE)
            image = bpy.data.images[image_name]

    else:
        image = bpy.data.images[image_name]

    #we slice the vert since tverts has one value too many
    texture_verts = [[float(comp) for comp in vert[:2]] for vert in node.get_prop_value("tverts")]

    ## the face list points out which texture_verts to use
    nwn_uv_faces = [[int(vert) for vert in face[4:7]] for face in node.get_prop_value("faces")]

    mesh.uv_textures.new()
    mesh_uv_faces = mesh.uv_textures.active.data[:]

    for index, uv_face in enumerate(mesh_uv_faces):
        nwn_uv_face = nwn_uv_faces[index]
        uv_face.image = image
        uv_face.use_image = True
        uv_face.uv1 = texture_verts[nwn_uv_face[0]]
        uv_face.uv2 = texture_verts[nwn_uv_face[1]]
        uv_face.uv3 = texture_verts[nwn_uv_face[2]]

    #We also set up the smoothing groups as blender materials, since blender
    #doesn't really have the notion of smoothing groups in 2.5
    smoothing_indices = [face[3] for face in node.get_prop_value("faces")]
    faces = mesh.faces
    for face, smoothing_index in enumerate(smoothing_indices):
        mat_name = "Smooth_" + str(smoothing_index)
        if not mat_name in mesh.materials:
            if not mat_name in bpy.data.materials:
                bpy.data.materials.new(name=mat_name)
            mesh.materials.append(bpy.data.materials[mat_name])

        faces[face].material_index = mesh.materials.keys().index(mat_name)


def import_animations(mdl_object, context, objects, **kwargs):
    """
    Imports all animations in a single action, as a long timestrip
    """

    static_poses = {}
    object_paths = {}
    animations_dict = {}
    for ob in objects:
        #save the location and rotation of the static pose for
        poses = {}
        poses['location'] = ob.location[:]
        poses['rotation_axis_angle'] = ob.rotation_axis_angle[:]
        static_poses[ob] = poses

        #create animation data for the object
        ob.animation_data_create()
        ob.animation_data.action = bpy.data.actions.new(name="NWN" + ob.name)

        #Simplify access to the important fcurves
        object_paths[ob.name] = {}
        object_paths[ob.name]['location'] = {}
        object_paths[ob.name]['rotation_axis_angle'] = {}

        object_paths[ob.name]['location']['x'] = ob.animation_data.action.fcurves.new(data_path="location", index=0)
        object_paths[ob.name]['location']['y'] = ob.animation_data.action.fcurves.new(data_path="location", index=1)
        object_paths[ob.name]['location']['z'] = ob.animation_data.action.fcurves.new(data_path="location", index=2)

        object_paths[ob.name]['rotation_axis_angle']['w'] = ob.animation_data.action.fcurves.new(data_path="rotation_axis_angle", index=0)
        object_paths[ob.name]['rotation_axis_angle']['x'] = ob.animation_data.action.fcurves.new(data_path="rotation_axis_angle", index=1)
        object_paths[ob.name]['rotation_axis_angle']['y'] = ob.animation_data.action.fcurves.new(data_path="rotation_axis_angle", index=2)
        object_paths[ob.name]['rotation_axis_angle']['z'] = ob.animation_data.action.fcurves.new(data_path="rotation_axis_angle", index=3)

        #set up the basic information in the animations_dict
        animations_dict[ob.name] = {'location': {'x': [], 'y': [], 'z': []},
                                    'rotation_axis_angle': {'x': [], 'y': [], 'z': [], 'w': []}}

    current_frame = 1

    for animation in mdl_object.animations:
        #set the static frame before every animation
        current_frame = set_static_frame(static_poses, animations_dict, current_frame)
        current_frame += 1
        #import animation
        current_frame = import_animation(animation, animations_dict, current_frame, context, **kwargs)
        current_frame += 1
        #set the static frame after the animation
        current_frame = set_static_frame(static_poses, animations_dict, current_frame)
        current_frame += 10

    #print(animations_dict)
    #go through the animations_dict and actually insert the data in the fcurves
    apply_animations(animations_dict, object_paths)


def apply_animations(animations_dict, object_paths):
    """
    Takes the information inserted in animations_dict and applies it to the fcurve
    of every object
    """
    for ob, data_paths in animations_dict.items():
        for data_path, components in data_paths.items():
            for component, values in components.items():
                fcurve = object_paths[ob][data_path][component]
                fcurve.keyframe_points.add(len(values))
                for i, value in enumerate(values):
                    #print("Setting value %s for fcurve %s" % (str(value), str(data_path + component)))
                    fcurve.keyframe_points[i].co = value
                    #Setting the handles at the same coordinate as the point seems to be
                    #the easiest way of dealing with them for the moment
                    fcurve.keyframe_points[i].handle_right = value
                    fcurve.keyframe_points[i].handle_left = value


def set_static_frame(static_poses, animations_dict, current_frame):
    """
    Inserts the static pose for all objects for the current frame, and returns value of next frame.
    """
    for ob, poses in static_poses.items():
        loc_x, loc_y, loc_z = poses['location']
        rot_w, rot_x, rot_y, rot_z = poses['rotation_axis_angle']

        animations_dict[ob.name]['location']['x'].append((current_frame, loc_x))
        animations_dict[ob.name]['location']['y'].append((current_frame, loc_y))
        animations_dict[ob.name]['location']['z'].append((current_frame, loc_z))

        animations_dict[ob.name]['rotation_axis_angle']['w'].append((current_frame, rot_w))
        animations_dict[ob.name]['rotation_axis_angle']['x'].append((current_frame, rot_x))
        animations_dict[ob.name]['rotation_axis_angle']['y'].append((current_frame, rot_y))
        animations_dict[ob.name]['rotation_axis_angle']['z'].append((current_frame, rot_z))

    return current_frame


def import_animation(animation, animations_dict, current_frame,
                     context, **kwargs):
    """
    Parses a single animation and inserts channel data in animations_dict.
    Returns the frame number of the last frame in the animation
    """
    scene = context.scene
    fps = scene.render.fps
    start_frame = current_frame
    length = int(animation.length * fps)

    end_frame = start_frame + length

    #The animation object holds the borealis-specific data, such as marker information
    anim_ob = scene.nwn_props.animations.add()
    anim_ob.name = animation.name
    anim_ob.animroot = animation.animroot

    #set the start marker
    anim_ob.start_frame = start_frame
    #set the end marker
    anim_ob.end_frame = end_frame

    for (time, event_type) in animation.events:
        event = anim_ob.events.add()
        event.type = event_type
        event.time = time
        event.update_name(None)

    for node in animation.nodes:
        node_name = node.name
        #Found a model where some parts weren't in the geometry
        if node_name not in animations_dict:
            continue
        for property in node.properties.values():
            if not property.value_written:
                continue
            if property.name == "positionkey":
                for time, x, y, z in property.value:
                    key_frame = time * fps + start_frame
#                        print("adding position key to frame %i" % key_frame)
                    animations_dict[node_name]['location']['x'].append((key_frame, x))
                    animations_dict[node_name]['location']['y'].append((key_frame, y))
                    animations_dict[node_name]['location']['z'].append((key_frame, z))

            elif property.name == "orientationkey":
                for time, x, y, z, w in property.value:
                    key_frame = time * fps + start_frame

#                        print("adding orientation key to frame %i" % key_frame)
                    animations_dict[node_name]['rotation_axis_angle']['w'].append((key_frame, w))
                    animations_dict[node_name]['rotation_axis_angle']['x'].append((key_frame, x))
                    animations_dict[node_name]['rotation_axis_angle']['y'].append((key_frame, y))
                    animations_dict[node_name]['rotation_axis_angle']['z'].append((key_frame, z))
    return end_frame
