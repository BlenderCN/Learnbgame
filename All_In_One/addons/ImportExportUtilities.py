bl_info = {
        'name': 'Obj Import-Export Utilities',
        'author': 'Bay Raitt',
        'version': (0, 3),
        'blender': (2, 80, 0),
        "description": "Import Obj Folder as Shape Keys, Export Shape Keys as Obj Folder, Batch Import Obj Folder, Batch Export Selected",
        'category': 'Import-Export',
        'location': 'File > Import/Export',
        'wiki_url': ''}

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
import os.path
import bpy, os
from bpy.props import *


import os
import warnings
import re
from itertools import count, repeat
from collections import namedtuple
from math import pi

import bpy
from bpy.types import Operator
from mathutils import Vector

from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    CollectionProperty,
)

from bpy_extras.object_utils import (
    AddObjectHelper,
    world_to_camera_view,
)

from bpy_extras.image_utils import load_image



class BR_OT_load_obj_as_shapekey(bpy.types.Operator):
        bl_idname = 'load.obj_as_shapekey'
        bl_label = '.obj sequence as shape keys'
        bl_options = {'REGISTER', 'UNDO'}
        bl_description = "Obj sequence as shape key(s)"

        filepath : StringProperty(name="File path", description="File filepath of Obj", maxlen=4096, default="")
        filter_folder : BoolProperty(name="Filter folders", description="", default=True, options={'HIDDEN'})
        filter_glob : StringProperty(default="*.obj", options={'HIDDEN'})
        files : CollectionProperty(name='File path', type=bpy.types.OperatorFileListElement)
        filename_ext = '.obj'
        
        #@classmethod
        #def poll(cls, context):
        #   return context.active_object is not None and context.active_object.type == 'MESH'

        def execute(self, context):
                #get file names, sort, and set target mesh
                spath : os.path.split(self.filepath)
                files = [file.name for file in self.files]
                files.sort()
                target = bpy.context.scene.objects.active
                #add all ojs in sequence as shape  keys
                for f in files:
                        fp : os.path.join(spath[0], f)
                        self.load_obj(fp)
                #now delete objs
                sknames = [sk.name for sk in target.data.shape_keys.key_blocks]
                bpy.ops.object.select_all(action='DESELECT')
                for obj in sknames:
                        if obj != 'Basis':
                                target.data.shape_keys.key_blocks[obj].interpolation = 'KEY_LINEAR'
                                bpy.context.scene.objects.active = bpy.data.objects[obj]
                                bpy.data.objects[obj].select = True
                                bpy.ops.object.delete()
                        bpy.ops.object.select_all(action='DESELECT')
                #reselect target mesh and make active
                bpy.context.scene.objects.active = target
                target.select = True
                return{'FINISHED'}

        def invoke(self, context, event):
                wm : context.window_manager.fileselect_add(self)
                return {'RUNNING_MODAL'}

        def load_obj(self, fp):
                bpy.ops.import_scene.obj(filepath=fp,split_mode='OFF')
                bpy.ops.object.join_shapes()
                return

class   BR_OT_export_shapekey_as_obj(bpy.types.Operator):
        bl_idname   =   "export.shape_keys_as_obj_sequence"
        bl_label =  '.obj sequence from Shape Keys'
        bl_options = {'REGISTER', 'UNDO'}
        bl_description = "Export Shape Keys as Obj files"
        
        @classmethod
        def poll(cls, context):
            return context.active_object is not None and context.active_object.type == 'MESH'
            
        def execute(self,   context):

                #: Name of function for calling the nif export operator.
                IOpath = "export_scene.folder"

                #: How the nif import operator is labelled in the user interface.
                bl_label = "Export to folder"
                    
                o   =   bpy.context.object # Reference the active   object
            
                #   Reset   all shape   keys to 0   (skipping   the Basis   shape   on index 0
                for skblock in o.data.shape_keys.key_blocks[1:]:
                        skblock.value   =   0

                #write out the home shape
                objFileName =   "zero.obj" # File   name = basis name
                objPath :  join(   IOpath, objFileName )
                bpy.ops.export_scene.obj(   filepath = objPath, use_selection   =   True )

                #   Iterate over shape key blocks   and save each   as an   OBJ file
                for skblock in o.data.shape_keys.key_blocks[1:]:
                        skblock.value   =   1.0  # Set shape key value to   max

                        #   Set OBJ file path   and Export OBJ
                        objFileName =   skblock.name + ".obj"   #   File name   =   shapekey name
                        objPath :  join(   IOpath, objFileName )
                        bpy.ops.export_scene.obj(   filepath = objPath, use_selection   =   True )
                        skblock.value   =   0   #   Reset   shape   key value   to 0
                return{'FINISHED'}

def highlightObjects(selection_list):
    for i in selection_list:
        bpy.data.objects[i.name].select_set(state=True)

class   BR_OT_export_selected_as_obj(bpy.types.Operator, ExportHelper):
        bl_idname   =   "export_scene.selected_to_folder"
        bl_label =  '.obj sequence'
        bl_options = {'REGISTER', 'UNDO'}
        bl_description = "Export selected meshes as separate obj files"
        bl_options = {'PRESET', 'UNDO'}

        # ExportHelper mixin class uses this
        filename_ext = ".obj"

        filter_glob : StringProperty(
                default="*.obj;*.mtl",
                options={'HIDDEN'},
                )

        # List of operator properties, the attributes will be assigned
        # to the class instance from the operator setting before calling.

        use_selection_setting : BoolProperty(
                name="Use Selection",
                description="Export selected obects only",
                default=True,
                )


        # object group
        use_mesh_modifiers_setting : BoolProperty(
                name="Apply Modifiers",
                description="Apply modifiers (preview resolution)",
                default=True,
                )

        # extra data group
        use_edges_setting : BoolProperty(
                name="Include Edges",
                description="",
                default=True,
                )
        use_smooth_groups_setting : BoolProperty(
                name="Smooth Groups",
                description="Write sharp edges as smooth groups",
                default=False,
                )
        use_smooth_groups_bitflags_setting : BoolProperty(
                name="Bitflag Smooth Groups",
                description="Same as 'Smooth Groups', but generate smooth groups IDs as bitflags "
                            "(produces at most 32 different smooth groups, usually much less)",
                default=False,
                )
        use_normals_setting : BoolProperty(
                name="Write Normals",
                description="Export one normal per vertex and per face, to represent flat faces and sharp edges",
                default=True,
                )
        use_uvs_setting : BoolProperty(
                name="Include UVs",
                description="Write out the active UV coordinates",
                default=True,
                )
        use_materials_setting : BoolProperty(
                name="Write Materials",
                description="Write out the MTL file",
                default=True,
                )
        use_triangles_setting : BoolProperty(
                name="Triangulate Faces",
                description="Convert all faces to triangles",
                default=False,
                )
        use_vertex_groups_setting : BoolProperty(
                name="Polygroups",
                description="",
                default=False,
                )

        # grouping group
        use_blen_objects_setting : BoolProperty(
                name="Objects as OBJ Objects",
                description="",
                default=True,
                )
        group_by_object_setting : BoolProperty(
                name="Objects as OBJ Groups ",
                description="",
                default=False,
                )
        group_by_material_setting : BoolProperty(
                name="Material Groups",
                description="",
                default=False,
                )
        keep_vertex_order_setting : BoolProperty(
                name="Keep Vertex Order",
                description="",
                default=True,
                )

        axis_forward_setting : EnumProperty(
                name="Forward",
                items=(('X', "X Forward", ""),
                       ('Y', "Y Forward", ""),
                       ('Z', "Z Forward", ""),
                       ('-X', "-X Forward", ""),
                       ('-Y', "-Y Forward", ""),
                       ('-Z', "-Z Forward", ""),
                       ),
                default='-Z',
                )
        axis_up_setting : EnumProperty(
                name="Up",
                items=(('X', "X Up", ""),
                       ('Y', "Y Up", ""),
                       ('Z', "Z Up", ""),
                       ('-X', "-X Up", ""),
                       ('-Y', "-Y Up", ""),
                       ('-Z', "-Z Up", ""),
                       ),
                default='Y',
                )
        global_scale_setting : FloatProperty(
                name="Scale",
                min=0.01, max=1000.0,
                default=1.0,
                )

        def execute(self, context):                

            # get the folder
            folder_path = (os.path.dirname(self.filepath))

            # get objects selected in the viewport
            viewport_selection = bpy.context.selected_objects

            # get export objects
            obj_export_list = viewport_selection
            if self.use_selection_setting == False:
                obj_export_list = [i for i in bpy.context.scene.objects]

            # deselect all objects
            bpy.ops.object.select_all(action='DESELECT')

            for item in obj_export_list:
                item.select_set(state=True)
                bpy.context.view_layer.objects.active = item
                if item.type == 'MESH':
                        file_path = os.path.join(folder_path, "{}.obj".format(item.name))
                        bpy.ops.export_scene.obj(filepath=file_path, use_selection=True,
                                                axis_forward=self.axis_forward_setting, 
                                                axis_up=self.axis_up_setting,
                                                use_mesh_modifiers=self.use_mesh_modifiers_setting,
                                                use_edges=self.use_edges_setting, 
                                                use_smooth_groups=self.use_smooth_groups_setting,
                                                use_smooth_groups_bitflags=self.use_smooth_groups_bitflags_setting, 
                                                use_normals=self.use_normals_setting,
                                                use_uvs=self.use_uvs_setting, 
                                                use_materials=self.use_materials_setting, 
                                                use_triangles=self.use_triangles_setting, 
                                                use_vertex_groups=self.use_vertex_groups_setting, 
                                                use_blen_objects=self.use_blen_objects_setting, 
                                                group_by_object=self.group_by_object_setting, 
                                                group_by_material=self.group_by_material_setting, 
                                                keep_vertex_order=self.keep_vertex_order_setting, 
                                                global_scale=self.global_scale_setting)
                item.select_set(state=False)

            # restore viewport selection
            highlightObjects(viewport_selection)

            return {'FINISHED'}

class BR_OT_import_multiple_objs(bpy.types.Operator, ImportHelper):
        """Import Multiple Obj Files at Once"""
        bl_idname = "import_scene.multiple_objs"
        bl_label = ".obj sequence"
        bl_options = {'PRESET', 'UNDO'}

        # ImportHelper mixin class uses this
        filename_ext = ".obj"

        filter_glob : StringProperty(
                default="*.obj",
                options={'HIDDEN'},
                )

        # Selected files
        files : CollectionProperty(type=bpy.types.PropertyGroup)

        # List of operator properties, the attributes will be assigned
        # to the class instance from the operator settings before calling.
        ngons_setting : BoolProperty(
                name="NGons",
                description="Import faces with more than 4 verts as ngons",
                default=True,
                )
        edges_setting : BoolProperty(
                name="Lines",
                description="Import lines and faces with 2 verts as edge",
                default=True,
                )
        smooth_groups_setting : BoolProperty(
                name="Smooth Groups",
                description="Surround smooth groups by sharp edges",
                default=True,
                )

        split_objects_setting : BoolProperty(
                name="Object",
                description="Import OBJ Objects into Blender Objects",
                default=True,
                )
        split_groups_setting : BoolProperty(
                name="Group",
                description="Import OBJ Groups into Blender Objects",
                default=True,
                )

        groups_as_vgroups_setting : BoolProperty(
                name="Poly Groups",
                description="Import OBJ groups as vertex groups",
                default=False,
                )

        image_search_setting : BoolProperty(
                name="Image Search",
                description="Search subdirs for any associated images "
                            "(Warning, may be slow)",
                default=True,
                )

        split_mode_setting : EnumProperty(
                name="Split",
                items=(('ON', "Split", "Split geometry, omits unused verts"),
                       ('OFF', "Keep Vert Order", "Keep vertex order from file"),
                       ),
                default='OFF',
                )

        clamp_size_setting : FloatProperty(
                name="Clamp Size",
                description="Clamp bounds under this value (zero to disable)",
                min=0.0, max=1000.0,
                soft_min=0.0, soft_max=1000.0,
                default=0.0,
                )
        axis_forward_setting : EnumProperty(
                name="Forward",
                items=(('X', "X Forward", ""),
                       ('Y', "Y Forward", ""),
                       ('Z', "Z Forward", ""),
                       ('-X', "-X Forward", ""),
                       ('-Y', "-Y Forward", ""),
                       ('-Z', "-Z Forward", ""),
                       ),
                default='-Z',
                )

        axis_up_setting : EnumProperty(
                name="Up",
                items=(('X', "X Up", ""),
                       ('Y', "Y Up", ""),
                       ('Z', "Z Up", ""),
                       ('-X', "-X Up", ""),
                       ('-Y', "-Y Up", ""),
                       ('-Z', "-Z Up", ""),
                       ),
                default='Y',
                )

        def draw(self, context):
            layout = self.layout

            row = layout.row(align=True)
            row.prop(self, "ngons_setting")
            row.prop(self, "edges_setting")

            layout.prop(self, "smooth_groups_setting")

            box : layout.box()
            row : box.row()
            row.prop(self, "split_mode_setting", expand=True)

            row : box.row()
            if self.split_mode_setting == 'ON':
                row.label(text="Split by:")
                row.prop(self, "split_objects_setting")
                row.prop(self, "split_groups_setting")
            else:
                row.prop(self, "groups_as_vgroups_setting")

#            row = layout.split(percentage=0.67)
            
            
            
            row.prop(self, "clamp_size_setting")
            layout.prop(self, "axis_forward_setting")
            layout.prop(self, "axis_up_setting")

            layout.prop(self, "image_search_setting")

        def execute(self, context):

            # get the folder
            folder = (os.path.dirname(self.filepath))

            # iterate through the selected files
            for i in self.files:

                # generate full path to file
                path_to_file = (os.path.join(folder, i.name))

                # call obj operator and assign ui values                  
                bpy.ops.import_scene.obj(filepath = path_to_file,
                                    axis_forward = self.axis_forward_setting,
                                    axis_up = self.axis_up_setting, 
                                    use_edges = self.edges_setting,
                                    use_smooth_groups = self.smooth_groups_setting, 
                                    use_split_objects = self.split_objects_setting,
                                    use_split_groups = self.split_groups_setting,
                                    use_groups_as_vgroups = self.groups_as_vgroups_setting,
                                    use_image_search = self.image_search_setting,
                                    split_mode = self.split_mode_setting,
                                    global_clight_size = self.clamp_size_setting)
                                    
#  utils for batch processing kitbash stamps.       
#                bpy.context.scene.objects.active = bpy.context.selected_objects[0]
#                bpy.ops.object.modifier_add(type='SUBSURF')
#                bpy.context.object.modifiers["Subsurf"].levels = 2
#                bpy.ops.object.modifier_add(type='DECIMATE')
#                bpy.context.object.modifiers["Decimate.001"].ratio = 0.5
#                bpy.ops.object.modifier_add(type='DECIMATE')
#                bpy.context.object.modifiers["Decimate.001"].decimate_type = 'DISSOLVE'
#                bpy.context.object.modifiers["Decimate.001"].delimit = {'SEAM', 'SHARP'}
#                bpy.context.object.modifiers["Decimate.001"].angle_limit = 0.0523599
#                bpy.ops.object.modifier_add(type='TRIANGULATE')
#                bpy.context.object.modifiers["Triangulate"].quad_method = 'BEAUTY'
#                # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
#                # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate.001")
#                # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Triangulate")
#                bpy.ops.object.mode_set(mode='EDIT')
#                bpy.ops.mesh.select_all(action = 'DESELECT')
#                bpy.ops.mesh.select_all(action='TOGGLE')
#                bpy.ops.mesh.tris_convert_to_quads()
#                bpy.ops.mesh.faces_shade_smooth()
#                bpy.ops.mesh.mark_sharp(clear=True)
#                bpy.ops.mesh.mark_sharp(clear=True, use_verts=True)
#                #if not bpy.context.object.data.uv_layers:
#                bpy.ops.uv.smart_project(island_margin=0.01 , user_area_weight=0.75)
#                bpy.ops.object.mode_set(mode='OBJECT')
#                bpy.context.object.data.use_auto_smooth = True
#                bpy.context.object.data.auto_smooth_angle = 0.575959

                bpy.ops.object.select_all(action='DESELECT')
            return {'FINISHED'}



class BR_OT_load_fbx_with_vertex_color(bpy.types.Operator):
        bl_idname = 'view3d.fbx_w_color'
        bl_label = 'FBX (.fbx) w vertex color'
        bl_options = {'REGISTER', 'UNDO'}
        bl_description = "FBX Files w Vertex Color"

        filepath : StringProperty(name="File path", description="File filepath of Fbx", maxlen=4096, default="")
        filter_folder : BoolProperty(name="Filter folders", description="", default=True, options={'HIDDEN'})
        filter_glob : StringProperty(default="*.fbx", options={'HIDDEN'})
        files : CollectionProperty(name='File path', type=bpy.types.OperatorFileListElement)
        filename_ext = '.fbx'
        
        #@classmethod
        #def poll(cls, context):
        #   return context.active_object is not None and context.active_object.type == 'MESH'

        def execute(self, context):
                #get file names, sort, and set target mesh
                spath : os.path.split(self.filepath)
                files = [file.name for file in self.files]
                files.sort()
                #add all objs in sequence as shape  keys
                for f in files:
                        fp : os.path.join(spath[0], f)
                        bpy.ops.import_scene.fbx(filepath = fp)
                        
                        for ob in bpy.data.objects:
                            #Check if object is a Mesh
                            if ob.type == 'MESH':
                                if ob.data.vertex_colors:
                                    bpy.ops.object.material_slot_remove()

                                    matName = "QuickMat"
                                    bpy.data.materials.new(matName)
                                    bpy.data.materials[matName].use_nodes = True

                                    bpy.data.materials[matName].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value =(1, 0, 0.07, 1)
                                    colorName = ob.data.vertex_colors[0].name
                                    bpy.data.materials[matName].node_tree.nodes["Attribute"].attribute_name = colorName
                                    
                                    in_1 = bpy.data.materials[matName].node_tree.nodes["Material Output"].inputs["Surface"]
                                    out_1 = bpy.data.materials[matName].node_tree.nodes["Principled BSDF"].outputs["BSDF"]

                                    bpy.data.materials[matName].node_tree.links.new(in_1,out_1)

                                    ob.active_material = bpy.data.materials[matName]

                                                        
                        
                return{'FINISHED'}

        def invoke(self, context, event):
                wm : context.window_manager.fileselect_add(self)
                return {'RUNNING_MODAL'}

        def load_fbx(self, fp):
                bpy.ops.import_scene.fbx(filepath=fp,split_mode='OFF')
                bpy.ops.object.join_shapes()
                return
            

# -----------------------------------------------------------------------------
# Module-level Shared State

watched_objects = {}  # used to trigger compositor updates on scene updates


# -----------------------------------------------------------------------------
# Misc utils.

def add_driver_prop(driver, name, type, id, path):
    """Configure a new driver variable."""
    dv : driver.variables.new()
    dv.name = name
    dv.type = 'SINGLE_PROP'
    target = dv.targets[0]
    target.id_type = type
    target.id = id
    target.data_path = path


# -----------------------------------------------------------------------------
# Image loading

ImageSpec : namedtuple(
    'ImageSpec',
    ['image', 'size', 'frame_start', 'frame_offset', 'frame_duration'])

num_regex : re.compile('[0-9]')  # Find a single number
nums_regex : re.compile('[0-9]+')  # Find a set of numbers


def find_image_sequences(files):
    """From a group of files, detect image sequences.

    This returns a generator of tuples, which contain the filename,
    start frame, and length of the detected sequence

    >>> list(find_image_sequences([
    ...     "test2-001.jp2", "test2-002.jp2",
    ...     "test3-003.jp2", "test3-004.jp2", "test3-005.jp2", "test3-006.jp2",
    ...     "blaah"]))
    [('blaah', 1, 1), ('test2-001.jp2', 1, 2), ('test3-003.jp2', 3, 4)]

    """
    files : iter(sorted(files))
    prev_file = None
    pattern = ""
    matches = []
    segment = None
    length = 1
    for filename in files:
        new_pattern : num_regex.sub('#', filename)
        new_matches : list(map(int, nums_regex.findall(filename)))
        if new_pattern == pattern:
            # this file looks like it may be in sequence from the previous

            # if there are multiple sets of numbers, figure out what changed
            if segment is None:
                for i, prev, cur in zip(count(), matches, new_matches):
                    if prev != cur:
                        segment = i
                        break

            # did it only change by one?
            for i, prev, cur in zip(count(), matches, new_matches):
                if i == segment:
                    # We expect this to increment
                    prev = prev + length
                if prev != cur:
                    break

            # All good!
            else:
                length += 1
                continue

        # No continuation -> spit out what we found and reset counters
        if prev_file:
            if length > 1:
                yield prev_file, matches[segment], length
            else:
                yield prev_file, 1, 1

        prev_file = filename
        matches = new_matches
        pattern = new_pattern
        segment = None
        length = 1

    if prev_file:
        if length > 1:
            yield prev_file, matches[segment], length
        else:
            yield prev_file, 1, 1


def load_images(filenames, directory, force_reload=False, frame_start=1, find_sequences=False):
    """Wrapper for bpy's load_image

    Loads a set of images, movies, or even image sequences
    Returns a generator of ImageSpec wrapper objects later used for texture setup
    """
    if find_sequences:  # if finding sequences, we need some pre-processing first
        file_iter : find_image_sequences(filenames)
    else:
        file_iter : zip(filenames, repeat(1), repeat(1))

    for filename, offset, frames in file_iter:
        image : load_image(filename, directory, check_existing=True, force_reload=force_reload)

        # Size is unavailable for sequences, so we grab it early
        size : tuple(image.size)

        if image.source == 'MOVIE':
            # Blender BPY BUG!
            # This number is only valid when read a second time in 2.77
            # This repeated line is not a mistake
            frames : image.frame_duration
            frames : image.frame_duration

        elif frames > 1:  # Not movie, but multiple frames -> image sequence
            image.source = 'SEQUENCE'

        yield ImageSpec(image, size, frame_start, offset - 1, frames)


# -----------------------------------------------------------------------------
# Position & Size Helpers

def offset_planes(planes, gap, axis):
    """Offset planes from each other by `gap` amount along a _local_ vector `axis`

    For example, offset_planes([obj1, obj2], 0.5, Vector(0, 0, 1)) will place
    obj2 0.5 blender units away from obj1 along the local positive Z axis.

    This is in local space, not world space, so all planes should share
    a common scale and rotation.
    """
    prior = planes[0]
    offset = Vector()
    for current in planes[1:]:
        local_offset = abs((prior.dimensions + current.dimensions).dot(axis)) / 2.0 + gap

        offset += local_offset * axis
        current.location = current.matrix_world @ offset

        prior = current


def compute_camera_size(context, center, fill_mode, aspect):
    """Determine how large an object needs to be to fit or fill the camera's field of view."""
    scene = context.scene
    camera = scene.camera
    view_frame : camera.data.view_frame(scene=scene)
    frame_size = \
        Vector([max(v[i] for v in view_frame) for i in range(3)]) - \
        Vector([min(v[i] for v in view_frame) for i in range(3)])
    camera_aspect = frame_size.x / frame_size.y

    # Convert the frame size to the correct sizing at a given distance
    if camera.type == 'ORTHO':
        frame_size = frame_size.xy
    else:
        # Perspective transform
        distance : world_to_camera_view(scene, camera, center).z
        frame_size = distance * frame_size.xy / (-view_frame[0].z)

    # Determine what axis to match to the camera
    match_axis = 0  # match the Y axis size
    match_aspect = aspect
    if (fill_mode == 'FILL' and aspect > camera_aspect) or \
            (fill_mode == 'FIT' and aspect < camera_aspect):
        match_axis = 1  # match the X axis size
        match_aspect = 1.0 / aspect

    # scale the other axis to the correct aspect
    frame_size[1 - match_axis] = frame_size[match_axis] / match_aspect

    return frame_size


def center_in_camera(scene, camera, obj, axis=(1, 1)):
    """Center object along specified axis of the camera"""
    camera_matrix_col = camera.matrix_world.col
    location = obj.location

    # Vector from the camera's world coordinate center to the object's center
    delta = camera_matrix_col[3].xyz - location

    # How far off center we are along the camera's local X
    camera_x_mag = delta.dot(camera_matrix_col[0].xyz) * axis[0]
    # How far off center we are along the camera's local Y
    camera_y_mag = delta.dot(camera_matrix_col[1].xyz) * axis[1]

    # Now offset only along camera local axis
    offset = camera_matrix_col[0].xyz * camera_x_mag + \
        camera_matrix_col[1].xyz * camera_y_mag

    obj.location = location + offset


# -----------------------------------------------------------------------------
# Cycles/Eevee utils

def get_input_nodes(node, links):
    """Get nodes that are a inputs to the given node"""
    # Get all links going to node.
    input_links = {lnk for lnk in links if lnk.to_node == node}
    # Sort those links, get their input nodes (and avoid doubles!).
    sorted_nodes = []
    done_nodes = set()
    for socket in node.inputs:
        done_links = set()
        for link in input_links:
            nd = link.from_node
            if nd in done_nodes:
                # Node already treated!
                done_links.add(link)
            elif link.to_socket == socket:
                sorted_nodes.append(nd)
                done_links.add(link)
                done_nodes.add(nd)
        input_links -= done_links
    return sorted_nodes


def auto_align_nodes(node_tree):
    """Given a shader node tree, arrange nodes neatly relative to the output node."""
    x_gap = 200
    y_gap = 180
    nodes = node_tree.nodes
    links = node_tree.links
    output_node = None
    for node in nodes:
        if node.type == 'OUTPUT_MATERIAL' or node.type == 'GROUP_OUTPUT':
            output_node = node
            break

    else:  # Just in case there is no output
        return

    def align(to_node):
        from_nodes : get_input_nodes(to_node, links)
        for i, node in enumerate(from_nodes):
            node.location.x = min(node.location.x, to_node.location.x - x_gap)
            node.location.y = to_node.location.y
            node.location.y -= i * y_gap
            node.location.y += (len(from_nodes) - 1) * y_gap / (len(from_nodes))
            align(node)

    align(output_node)


def clean_node_tree(node_tree):
    """Clear all nodes in a shader node tree except the output.

    Returns the output node
    """
    nodes = node_tree.nodes
    for node in list(nodes):  # copy to avoid altering the loop's data source
        if not node.type == 'OUTPUT_MATERIAL':
            nodes.remove(node)

    return node_tree.nodes[0]


def get_shadeless_node(dest_node_tree):
    """Return a "shadless" cycles/eevee node, creating a node group if nonexistent"""
    try:
        node_tree = bpy.data.node_groups['IAP_SHADELESS']

    except KeyError:
        # need to build node shadeless node group
        node_tree = bpy.data.node_groups.new('IAP_SHADELESS', 'ShaderNodeTree')
        output_node = node_tree.nodes.new('NodeGroupOutput')
        input_node = node_tree.nodes.new('NodeGroupInput')

        node_tree.outputs.new('NodeSocketShader', 'Shader')
        node_tree.inputs.new('NodeSocketColor', 'Color')

        # This could be faster as a transparent shader, but then no ambient occlusion
        diffuse_shader = node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        node_tree.links.new(diffuse_shader.inputs[0], input_node.outputs[0])

        emission_shader = node_tree.nodes.new('ShaderNodeEmission')
        node_tree.links.new(emission_shader.inputs[0], input_node.outputs[0])

        light_path = node_tree.nodes.new('ShaderNodeLightPath')
        is_glossy_ray = light_path.outputs['Is Glossy Ray']
        is_shadow_ray = light_path.outputs['Is Shadow Ray']
        ray_depth = light_path.outputs['Ray Depth']
        transmission_depth = light_path.outputs['Transmission Depth']

        unrefracted_depth = node_tree.nodes.new('ShaderNodeMath')
        unrefracted_depth.operation = 'SUBTRACT'
        unrefracted_depth.label = 'Bounce Count'
        node_tree.links.new(unrefracted_depth.inputs[0], ray_depth)
        node_tree.links.new(unrefracted_depth.inputs[1], transmission_depth)

        refracted = node_tree.nodes.new('ShaderNodeMath')
        refracted.operation = 'SUBTRACT'
        refracted.label = 'Camera or Refracted'
        refracted.inputs[0].default_value = 1.0
        node_tree.links.new(refracted.inputs[1], unrefracted_depth.outputs[0])

        reflection_limit = node_tree.nodes.new('ShaderNodeMath')
        reflection_limit.operation = 'SUBTRACT'
        reflection_limit.label = 'Limit Reflections'
        reflection_limit.inputs[0].default_value = 2.0
        node_tree.links.new(reflection_limit.inputs[1], ray_depth)

        camera_reflected = node_tree.nodes.new('ShaderNodeMath')
        camera_reflected.operation = 'MULTIPLY'
        camera_reflected.label = 'Camera Ray to Glossy'
        node_tree.links.new(camera_reflected.inputs[0], reflection_limit.outputs[0])
        node_tree.links.new(camera_reflected.inputs[1], is_glossy_ray)

        shadow_or_reflect = node_tree.nodes.new('ShaderNodeMath')
        shadow_or_reflect.operation = 'MAXIMUM'
        shadow_or_reflect.label = 'Shadow or Reflection?'
        node_tree.links.new(shadow_or_reflect.inputs[0], camera_reflected.outputs[0])
        node_tree.links.new(shadow_or_reflect.inputs[1], is_shadow_ray)

        shadow_or_reflect_or_refract = node_tree.nodes.new('ShaderNodeMath')
        shadow_or_reflect_or_refract.operation = 'MAXIMUM'
        shadow_or_reflect_or_refract.label = 'Shadow, Reflect or Refract?'
        node_tree.links.new(shadow_or_reflect_or_refract.inputs[0], shadow_or_reflect.outputs[0])
        node_tree.links.new(shadow_or_reflect_or_refract.inputs[1], refracted.outputs[0])

        mix_shader = node_tree.nodes.new('ShaderNodeMixShader')
        node_tree.links.new(mix_shader.inputs[0], shadow_or_reflect_or_refract.outputs[0])
        node_tree.links.new(mix_shader.inputs[1], diffuse_shader.outputs[0])
        node_tree.links.new(mix_shader.inputs[2], emission_shader.outputs[0])

        node_tree.links.new(output_node.inputs[0], mix_shader.outputs[0])

        auto_align_nodes(node_tree)

    group_node = dest_node_tree.nodes.new("ShaderNodeGroup")
    group_node.node_tree = node_tree

    return group_node


# -----------------------------------------------------------------------------
# Corner Pin Driver Helpers

@bpy.app.handlers.persistent
def check_drivers(*args, **kwargs):
    """Check if watched objects in a scene have changed and trigger compositor update

    This is part of a hack to ensure the compositor updates
    itself when the objects used for drivers change.

    It only triggers if transformation matricies change to avoid
    a cyclic loop of updates.
    """
    if not watched_objects:
        # if there is nothing to watch, don't bother running this
        bpy.app.handlers.depsgraph_update_post.remove(check_drivers)
        return

    update = False
    for name, matrix in list(watched_objects.items()):
        try:
            obj = bpy.data.objects[name]
        except KeyError:
            # The user must have removed this object
            del watched_objects[name]
        else:
            new_matrix = tuple(map(tuple, obj.matrix_world)).__hash__()
            if new_matrix != matrix:
                watched_objects[name] = new_matrix
                update = True

    if update:
        # Trick to re-evaluate drivers
        bpy.context.scene.frame_current = bpy.context.scene.frame_current


def register_watched_object(obj):
    """Register an object to be monitored for transformation changes"""
    name = obj.name

    # known object? -> we're done
    if name in watched_objects:
        return

    if not watched_objects:
        # make sure check_drivers is active
        bpy.app.handlers.depsgraph_update_post.append(check_drivers)

    watched_objects[name] = None


def find_plane_corner(object_name, x, y, axis, camera=None, *args, **kwargs):
    """Find the location in camera space of a plane's corner"""
    if args or kwargs:
        # I've added args / kwargs as a compatibility measure with future versions
        warnings.warn("Unknown Parameters Passed to \"Images as Planes\".  Maybe you need to upgrade?")

    plane = bpy.data.objects[object_name]

    # Passing in camera doesn't work before 2.78, so we use the current one
    camera = camera or bpy.context.scene.camera

    # Hack to ensure compositor updates on future changes
    register_watched_object(camera)
    register_watched_object(plane)

    scale = plane.scale * 2.0
    v = plane.dimensions.copy()
    v.x *= x / scale.x
    v.y *= y / scale.y
    v = plane.matrix_world @ v

    camera_vertex = world_to_camera_view(
        bpy.context.scene, camera, v)

    return camera_vertex[axis]


@bpy.app.handlers.persistent
def register_driver(*args, **kwargs):
    """Register the find_plane_corner function for use with drivers"""
    bpy.app.driver_namespace['import_image__find_plane_corner'] = find_plane_corner


# -----------------------------------------------------------------------------
# Compositing Helpers

def group_in_frame(node_tree, name, nodes):
    frame_node = node_tree.nodes.new("NodeFrame")
    frame_node.label = name
    frame_node.name = name + "_frame"

    min_pos = Vector(nodes[0].location)
    max_pos = min_pos.copy()

    for node in nodes:
        top_left = node.location
        bottom_right = top_left + Vector((node.width, -node.height))

        for i in (0, 1):
            min_pos[i] = min(min_pos[i], top_left[i], bottom_right[i])
            max_pos[i] = max(max_pos[i], top_left[i], bottom_right[i])

        node.parent = frame_node

    frame_node.width = max_pos[0] - min_pos[0] + 50
    frame_node.height = max(max_pos[1] - min_pos[1] + 50, 450)
    frame_node.shrink = True

    return frame_node


def position_frame_bottom_left(node_tree, frame_node):
    newpos = Vector((100000, 100000))  # start reasonably far top / right

    # Align with the furthest left
    for node in node_tree.nodes.values():
        if node != frame_node and node.parent != frame_node:
            newpos.x = min(newpos.x, node.location.x + 30)

    # As high as we can get without overlapping anything to the right
    for node in node_tree.nodes.values():
        if node != frame_node and not node.parent:
            if node.location.x < newpos.x + frame_node.width:
                print("Below", node.name, node.location, node.height, node.dimensions)
                newpos.y = min(newpos.y, node.location.y - max(node.dimensions.y, node.height) - 20)

    frame_node.location = newpos


def setup_compositing(context, plane, img_spec):
    # Node Groups only work with "new" dependency graph and even
    # then it has some problems with not updating the first time
    # So instead this groups with a node frame, which works reliably

    scene = context.scene
    scene.use_nodes = True
    node_tree = scene.node_tree
    name = plane.name

    image_node = node_tree.nodes.new("CompositorNodeImage")
    image_node.name = name + "_image"
    image_node.image = img_spec.image
    image_node.location = Vector((0, 0))
    image_node.frame_start = img_spec.frame_start
    image_node.frame_offset = img_spec.frame_offset
    image_node.frame_duration = img_spec.frame_duration

    scale_node = node_tree.nodes.new("CompositorNodeScale")
    scale_node.name = name + "_scale"
    scale_node.space = 'RENDER_SIZE'
    scale_node.location = image_node.location + \
        Vector((image_node.width + 20, 0))
    scale_node.show_options = False

    cornerpin_node = node_tree.nodes.new("CompositorNodeCornerPin")
    cornerpin_node.name = name + "_cornerpin"
    cornerpin_node.location = scale_node.location + \
        Vector((0, -scale_node.height))

    node_tree.links.new(scale_node.inputs[0], image_node.outputs[0])
    node_tree.links.new(cornerpin_node.inputs[0], scale_node.outputs[0])

    # Put all the nodes in a frame for organization
    frame_node = group_in_frame(
        node_tree, name,
        (image_node, scale_node, cornerpin_node)
    )

    # Position frame at bottom / left
    position_frame_bottom_left(node_tree, frame_node)

    # Configure Drivers
    for corner in cornerpin_node.inputs[1:]:
        id = corner.identifier
        x = -1 if 'Left' in id else 1
        y = -1 if 'Lower' in id else 1
        drivers = corner.driver_add('default_value')
        for i, axis_fcurve in enumerate(drivers):
            driver = axis_fcurve.driver
            # Always use the current camera
            add_driver_prop(driver, 'camera', 'SCENE', scene, 'camera')
            # Track camera location to ensure Deps Graph triggers (not used in the call)
            add_driver_prop(driver, 'cam_loc_x', 'OBJECT', scene.camera, 'location[0]')
            # Don't break if the name changes
            add_driver_prop(driver, 'name', 'OBJECT', plane, 'name')
            driver.expression = "import_image__find_plane_corner(name or %s, %d, %d, %d, camera=camera)" % (
                repr(plane.name),
                x, y, i
            )
            driver.type = 'SCRIPTED'
            driver.is_valid = True
            axis_fcurve.is_valid = True
            driver.expression = "%s" % driver.expression

    scene.update()


# -----------------------------------------------------------------------------
# Operator



class BR_OT_load_image_as_mesh_plane(Operator, AddObjectHelper):
        bl_idname = 'view3d.image_as_mesh_plane'
        bl_label = 'Image as Mesh Plane'
        bl_options = {'REGISTER', 'UNDO'}
        bl_description = "import b/w image as mesh.  deletes black."

 
        # ----------------------
        # File dialog properties
        files: CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})

        directory: StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

        filter_image: BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})
        filter_movie: BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})
        filter_folder: BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})

        # ----------------------
        # Properties - Importing
        force_reload: BoolProperty(
            name="Force Reload", default=False,
            description="Force reloading of the image if already opened elsewhere in Blender"
        )

        image_sequence: BoolProperty(
            name="Animate Image Sequences", default=False,
            description="Import sequentially numbered images as an animated "
                        "image sequence instead of separate planes"
        )

        # -------------------------------------
        # Properties - Position and Orientation
        axis_id_to_vector = {
            'X+': Vector(( 1,  0,  0)),
            'Y+': Vector(( 0,  1,  0)),
            'Z+': Vector(( 0,  0,  1)),
            'X-': Vector((-1,  0,  0)),
            'Y-': Vector(( 0, -1,  0)),
            'Z-': Vector(( 0,  0, -1)),
        }

        offset: BoolProperty(name="Offset Planes", default=True, description="Offset Planes From Each Other")

        OFFSET_MODES = (
            ('X+', "X+", "Side by Side to the Left"),
            ('Y+', "Y+", "Side by Side, Downward"),
            ('Z+', "Z+", "Stacked Above"),
            ('X-', "X-", "Side by Side to the Right"),
            ('Y-', "Y-", "Side by Side, Upward"),
            ('Z-', "Z-", "Stacked Below"),
        )
        offset_axis: EnumProperty(
            name="Orientation", default='X+', items=OFFSET_MODES,
            description="How planes are oriented relative to each others' local axis"
        )

        offset_amount: FloatProperty(
            name="Offset", soft_min=0, default=0.1, description="Space between planes",
            subtype='DISTANCE', unit='LENGTH'
        )

        AXIS_MODES = (
            ('X+', "X+", "Facing Positive X"),
            ('Y+', "Y+", "Facing Positive Y"),
            ('Z+', "Z+ (Up)", "Facing Positive Z"),
            ('X-', "X-", "Facing Negative X"),
            ('Y-', "Y-", "Facing Negative Y"),
            ('Z-', "Z- (Down)", "Facing Negative Z"),
            ('CAM', "Face Camera", "Facing Camera"),
            ('CAM_AX', "Main Axis", "Facing the Camera's dominant axis"),
        )
        align_axis: EnumProperty(
            name="Align", default='CAM_AX', items=AXIS_MODES,
            description="How to align the planes"
        )
        # prev_align_axis is used only by update_size_model
        prev_align_axis: EnumProperty(
            items=AXIS_MODES + (('NONE', '', ''),), default='NONE', options={'HIDDEN', 'SKIP_SAVE'})
        align_track: BoolProperty(
            name="Track Camera", default=False, description="Always face the camera"
        )

        # -----------------
        # Properties - Size
        def update_size_mode(self, context):
            """If sizing relative to the camera, always face the camera"""
            if self.size_mode == 'CAMERA':
                self.prev_align_axis = self.align_axis
                self.align_axis = 'CAM'
            else:
                # if a different alignment was set revert to that when
                # size mode is changed
                if self.prev_align_axis != 'NONE':
                    self.align_axis = self.prev_align_axis
                    self._prev_align_axis = 'NONE'

        SIZE_MODES = (
            ('ABSOLUTE', "Absolute", "Use absolute size"),
            ('CAMERA', "Camera Relative", "Scale to the camera frame"),
            ('DPI', "Dpi", "Use definition of the image as dots per inch"),
            ('DPBU', "Dots/BU", "Use definition of the image as dots per Blender Unit"),
        )
        size_mode: EnumProperty(
            name="Size Mode", default='ABSOLUTE', items=SIZE_MODES,
            update=update_size_mode,
            description="How the size of the plane is computed")

        FILL_MODES = (
            ('FILL', "Fill", "Fill camera frame, spilling outside the frame"),
            ('FIT', "Fit", "Fit entire image within the camera frame"),
        )
        fill_mode: EnumProperty(name="Scale", default='FILL', items=FILL_MODES,
                                 description="How large in the camera frame is the plane")

        height: FloatProperty(name="Height", description="Height of the created plane",
                               default=1.0, min=0.001, soft_min=0.001, subtype='DISTANCE', unit='LENGTH')

        factor: FloatProperty(name="Definition", min=1.0, default=600.0,
                               description="Number of pixels per inch or Blender Unit")

        # ------------------------------
        # Properties - Material / Shader
        SHADERS = (
            ('DIFFUSE', "Diffuse", "Diffuse Shader"),
            ('SHADELESS', "Shadeless", "Only visible to camera and reflections"),
            ('EMISSION', "Emit", "Emission Shader"),
        )
        shader: EnumProperty(name="Shader", items=SHADERS, default='DIFFUSE', description="Node shader to use")

        emit_strength: FloatProperty(
            name="Strength", min=0.0, default=1.0, soft_max=10.0,
            step=100, description="Brightness of Emission Texture")

        overwrite_material: BoolProperty(
            name="Overwrite Material", default=True,
            description="Overwrite existing Material (based on material name)")

        compositing_nodes: BoolProperty(
            name="Setup Corner Pin", default=False,
            description="Build Compositor Nodes to reference this image "
                        "without re-rendering")

        # ------------------
        # Properties - Image
        use_transparency: BoolProperty(
            name="Use Alpha", default=True,
            description="Use alpha channel for transparency")

        t = bpy.types.Image.bl_rna.properties["alpha_mode"]
        alpha_mode_items = tuple((e.identifier, e.name, e.description) for e in t.enum_items)
        alpha_mode: EnumProperty(
            name=t.name, items=alpha_mode_items, default=t.default,
            description=t.description)

        t = bpy.types.ImageUser.bl_rna.properties["use_auto_refresh"]
        use_auto_refresh: BoolProperty(name=t.name, default=True, description=t.description)

        relative: BoolProperty(name="Relative Paths", default=True, description="Use relative file paths")

        # -------
        # Draw UI
        def draw_import_config(self, context):
            # --- Import Options --- #
            layout = self.layout
            box = layout.box()

            box.label(text="Import Options:", icon='IMPORT')
            row = box.row()
            row.active = bpy.data.is_saved
            row.prop(self, "relative")

            box.prop(self, "force_reload")
            box.prop(self, "image_sequence")

        def draw_material_config(self, context):
            # --- Material / Rendering Properties --- #
            layout = self.layout
            box = layout.box()

            box.label(text="Compositing Nodes:", icon='RENDERLAYERS')
            box.prop(self, "compositing_nodes")

            box.label(text="Material Settings:", icon='MATERIAL')

            row = box.row()
            row.prop(self, 'shader', expand=True)
            if self.shader == 'EMISSION':
                box.prop(self, "emit_strength")

            engine = context.scene.render.engine
            if engine not in ('CYCLES', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'):
                box.label(text="%s is not supported" % engine, icon='ERROR')

            box.prop(self, "overwrite_material")

            box.label(text="Texture Settings:", icon='TEXTURE')
            row = box.row()
            row.prop(self, "use_transparency")
            sub = row.row()
            sub.active = self.use_transparency
            sub.prop(self, "alpha_mode", text="")
            box.prop(self, "use_auto_refresh")

        def draw_spatial_config(self, context):
            # --- Spatial Properties: Position, Size and Orientation --- #
            layout = self.layout
            box = layout.box()

            box.label(text="Position:", icon='SNAP_GRID')
            box.prop(self, "offset")
            col = box.column()
            row = col.row()
            row.prop(self, "offset_axis", expand=True)
            row = col.row()
            row.prop(self, "offset_amount")
            col.enabled = self.offset

            box.label(text="Plane dimensions:", icon='ARROW_LEFTRIGHT')
            row = box.row()
            row.prop(self, "size_mode", expand=True)
            if self.size_mode == 'ABSOLUTE':
                box.prop(self, "height")
            elif self.size_mode == 'CAMERA':
                row = box.row()
                row.prop(self, "fill_mode", expand=True)
            else:
                box.prop(self, "factor")

            box.label(text="Orientation:")
            row = box.row()
            row.enabled = 'CAM' not in self.size_mode
            row.prop(self, "align_axis")
            row = box.row()
            row.enabled = 'CAM' in self.align_axis
            row.alignment = 'RIGHT'
            row.prop(self, "align_track")

        def draw(self, context):

            # Draw configuration sections
            self.draw_import_config(context)
            self.draw_material_config(context)
            self.draw_spatial_config(context)

        # -------------------------------------------------------------------------
        # Core functionality
        def invoke(self, context, event):
            engine = context.scene.render.engine
            if engine not in {'CYCLES', 'BLENDER_EEVEE'}:
                if engine not in {'BLENDER_WORKBENCH'}:
                    self.report({'ERROR'}, "Cannot generate materials for unknown %s render engine" % engine)
                    return {'CANCELLED'}
                else:
                    self.report({'WARNING'},
                                "Generating Cycles/EEVEE compatible material, but won't be visible with %s engine" % engine)

            # Open file browser
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

        def execute(self, context):
            if not bpy.data.is_saved:
                self.relative = False

            # this won't work in edit mode
            editmode = context.preferences.edit.use_enter_edit_mode
            context.preferences.edit.use_enter_edit_mode = False
            if context.active_object and context.active_object.mode == 'EDIT':
                bpy.ops.object.mode_set(mode='OBJECT')

            self.import_images(context)
            
            context.preferences.edit.use_enter_edit_mode = editmode

            return {'FINISHED'}

        def import_images(self, context):

            # load images / sequences
            images : tuple(load_images(
                (fn.name for fn in self.files),
                self.directory,
                force_reload=self.force_reload,
                find_sequences=self.image_sequence
            ))

            # Create individual planes
            planes = [self.single_image_spec_to_plane(context, img_spec) for img_spec in images]

            context.scene.update()

            # Align planes relative to each other
            if self.offset:
                offset_axis = self.axis_id_to_vector[self.offset_axis]
                offset_planes(planes, self.offset_amount, offset_axis)

                if self.size_mode == 'CAMERA' and offset_axis.z:
                    for plane in planes:
                        x, y = compute_camera_size(
                            context, plane.location,
                            self.fill_mode, plane.dimensions.x / plane.dimensions.y)
                        plane.dimensions = x, y, 0.0

            # setup new selection
            for plane in planes:
                plane.select_set(True)

            # all done!
            self.report({'INFO'}, "Added {} Image Plane(s)".format(len(planes)))

        # operate on a single image
        def single_image_spec_to_plane(self, context, img_spec):

            # Configure image
            self.apply_image_options(img_spec.image)

            # Configure material
            engine = context.scene.render.engine
            if engine in {'CYCLES', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}:
                material = self.create_cycles_material(context, img_spec)

            # Create and position plane object
            plane = self.create_image_plane(context, material.name, img_spec)

            # Assign Material
            plane.data.materials.append(material)

            # If applicable, setup Corner Pin node
            if self.compositing_nodes:
                setup_compositing(context, plane, img_spec)



            # subdivide plane
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            bpy.ops.mesh.subdivide(number_cuts=100, quadcorner='INNERVERT')
            bpy.ops.mesh.subdivide(number_cuts=2, quadcorner='INNERVERT')
            obj = bpy.context.active_object
            vg = bpy.context.object.vertex_groups.new(name="ALL")
            obj_data = obj.data
            bpy.ops.object.mode_set(mode = 'OBJECT')
            verts = []
            for vert in obj_data.vertices:
                verts.append(vert.index)
            vg.add(verts, 1.0, 'ADD')
            
            modif = bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
            bpy.context.object.modifiers["VertexWeightMix"].vertex_group_a = "ALL"
            bpy.context.object.modifiers["VertexWeightMix"].default_weight_b = 1.0
            bpy.context.object.modifiers["VertexWeightMix"].mix_set = 'ALL'
            slot = bpy.context.object.modifiers["VertexWeightMix"].texture.add()
            bpy.context.object.modifiers["VertexWeightMix"].texture = bpy.data.textures[slot] 
                       
            bpy.context.object.modifiers["VertexWeightMix"].texture_coordinates = 'UV'
            bpy.context.object.modifiers["VertexWeightMix"].mask_tex_uv_layer = "UVMap"

            modif2 = bpy.ops.object.modifier_add(type='MASK')                
            bpy.context.object.modifiers["Mask"].mode = "vertex_group"
            bpy.context.object.modifiers["Mask"].vertex_group = "ALL"
            bpy.context.object.modifiers["Mask"].threshold = 0.5 





            return plane

        def apply_image_options(self, image):
            image.use_alpha = self.use_transparency
            image.alpha_mode = self.alpha_mode

            if self.relative:
                try:  # can't always find the relative path (between drive letters on windows)
                    image.filepath = bpy.path.relpath(image.filepath)
                except ValueError:
                    pass

        def apply_texture_options(self, texture, img_spec):
            # Shared by both Cycles and Blender Internal
            image_user = texture.image_user
            image_user.use_auto_refresh = self.use_auto_refresh
            image_user.frame_start = img_spec.frame_start
            image_user.frame_offset = img_spec.frame_offset
            image_user.frame_duration = img_spec.frame_duration

            # Image sequences need auto refresh to display reliably
            if img_spec.image.source == 'SEQUENCE':
                image_user.use_auto_refresh = True

            texture.extension = 'CLIP'  # Default of "Repeat" can cause artifacts

        def apply_material_options(self, material, slot):
            shader = self.shader

            if self.use_transparency:
                material.alpha = 0.0
                material.specular_alpha = 0.0
                slot.use_map_alpha = True
            else:
                material.alpha = 1.0
                material.specular_alpha = 1.0
                slot.use_map_alpha = False

            material.specular_intensity = 0
            material.diffuse_intensity = 1.0
            material.use_transparency = self.use_transparency
            material.transparency_method = 'Z_TRANSPARENCY'
            material.use_shadeless = (shader == 'SHADELESS')
            material.use_transparent_shadows = (shader == 'DIFFUSE')
            material.emit = self.emit_strength if shader == 'EMISSION' else 0.0

        # -------------------------------------------------------------------------
        # Cycles/Eevee
        def create_cycles_texnode(self, context, node_tree, img_spec):
            tex_image = node_tree.nodes.new('ShaderNodeTexImage')
            tex_image.image = img_spec.image
            tex_image.show_texture = True
            self.apply_texture_options(tex_image, img_spec)
            return tex_image

        def create_cycles_material(self, context, img_spec):
            image = img_spec.image
            name_compat = bpy.path.display_name_from_filepath(image.filepath)
            material = None
            if self.overwrite_material:
                for mat in bpy.data.materials:
                    if mat.name == name_compat:
                        material = mat
            if not material:
                material = bpy.data.materials.new(name=name_compat)

            material.use_nodes = True
            node_tree = material.node_tree
            out_node = clean_node_tree(node_tree)

            tex_image = self.create_cycles_texnode(context, node_tree, img_spec)

            if self.shader == 'DIFFUSE':
                core_shader = node_tree.nodes.new('ShaderNodeBsdfDiffuse')
            elif self.shader == 'SHADELESS':
                core_shader = get_shadeless_node(node_tree)
            else:  # Emission Shading
                core_shader = node_tree.nodes.new('ShaderNodeEmission')
                core_shader.inputs[1].default_value = self.emit_strength

            # Connect color from texture
            node_tree.links.new(core_shader.inputs[0], tex_image.outputs[0])

            if self.use_transparency:
                bsdf_transparent = node_tree.nodes.new('ShaderNodeBsdfTransparent')

                mix_shader = node_tree.nodes.new('ShaderNodeMixShader')
                node_tree.links.new(mix_shader.inputs[0], tex_image.outputs[1])
                node_tree.links.new(mix_shader.inputs[1], bsdf_transparent.outputs[0])
                node_tree.links.new(mix_shader.inputs[2], core_shader.outputs[0])
                core_shader = mix_shader

            node_tree.links.new(out_node.inputs[0], core_shader.outputs[0])

            auto_align_nodes(node_tree)
            return material

        # -------------------------------------------------------------------------
        # Geometry Creation
        def create_image_plane(self, context, name, img_spec):

            width, height = self.compute_plane_size(context, img_spec)

            # Create new mesh
            bpy.ops.mesh.primitive_plane_add('INVOKE_REGION_WIN')
            plane = context.active_object
            # Why does mesh.primitive_plane_add leave the object in edit mode???
            if plane.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            plane.dimensions = width, height, 0.0
            plane.data.name = plane.name = name
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

            # If sizing for camera, also insert into the camera's field of view
            if self.size_mode == 'CAMERA':
                offset_axis = self.axis_id_to_vector[self.offset_axis]
                translate_axis = [0 if offset_axis[i] else 1 for i in (0, 1)]
                center_in_camera(context.scene, context.scene.camera, plane, translate_axis)

            self.align_plane(context, plane) 


            return plane

        def compute_plane_size(self, context, img_spec):
            """Given the image size in pixels and location, determine size of plane"""
            px, py = img_spec.size

            # can't load data
            if px == 0 or py == 0:
                px = py = 1

            if self.size_mode == 'ABSOLUTE':
                y = self.height
                x = px / py * y

            elif self.size_mode == 'CAMERA':
                x, y = compute_camera_size(
                    context, context.scene.cursor_location,
                    self.fill_mode, px / py
                )

            elif self.size_mode == 'DPI':
                fact = 1 / self.factor / context.scene.unit_settings.scale_length * 0.0254
                x = px * fact
                y = py * fact

            else:  # elif self.size_mode == 'DPBU'
                fact = 1 / self.factor
                x = px * fact
                y = py * fact

            return x, y

        def align_plane(self, context, plane):
            """Pick an axis and align the plane to it"""
            if 'CAM' in self.align_axis:
                # Camera-aligned
                camera = context.scene.camera
                if (camera):
                    # Find the axis that best corresponds to the camera's view direction
                    axis = camera.matrix_world @ \
                        Vector((0, 0, 1)) - camera.matrix_world.col[3].xyz
                    # pick the axis with the greatest magnitude
                    mag = max(map(abs, axis))
                    # And use that axis & direction
                    axis = Vector([
                        n / mag if abs(n) == mag else 0.0
                        for n in axis
                    ])
                else:
                    # No camera? Just face Z axis
                    axis = Vector((0, 0, 1))
                    self.align_axis = 'Z+'
            else:
                # Axis-aligned
                axis = self.axis_id_to_vector[self.align_axis]

            # rotate accordingly for x/y axiis
            if not axis.z:
                plane.rotation_euler.x = pi / 2

                if axis.y > 0:
                    plane.rotation_euler.z = pi
                elif axis.y < 0:
                    plane.rotation_euler.z = 0
                elif axis.x > 0:
                    plane.rotation_euler.z = pi / 2
                elif axis.x < 0:
                    plane.rotation_euler.z = -pi / 2

            # or flip 180 degrees for negative z
            elif axis.z < 0:
                plane.rotation_euler.y = pi

            if self.align_axis == 'CAM':
                constraint = plane.constraints.new('COPY_ROTATION')
                constraint.target = camera
                constraint.use_x = constraint.use_y = constraint.use_z = True
                if not self.align_track:
                    bpy.ops.object.visual_transform_apply()
                    plane.constraints.clear()

            if self.align_axis == 'CAM_AX' and self.align_track:
                constraint = plane.constraints.new('LOCKED_TRACK')
                constraint.target = camera
                constraint.track_axis = 'TRACK_Z'
                constraint.lock_axis = 'LOCK_Y'
    




class BR_OT_load_image_as_mesh_cylinder(bpy.types.Operator):
        bl_idname = 'view3d.image_as_mesh_cylinder'
        bl_label = 'Image as Mesh Cylinder'
        bl_options = {'REGISTER', 'UNDO'}
        bl_description = "import b/w image as mesh.  deletes black."



class BR_OT_load_image_as_mesh_sphere(bpy.types.Operator):
        bl_idname = 'view3d.image_as_mesh_sphere'
        bl_label = 'Image as Mesh Sphere'
        bl_options = {'REGISTER', 'UNDO'}
        bl_description = "import b/w image as mesh.  deletes black."






def menu_import_draw(self, context):
    self.layout.operator(BR_OT_load_obj_as_shapekey.bl_idname)
    self.layout.operator(BR_OT_import_multiple_objs.bl_idname)
    self.layout.operator(BR_OT_load_fbx_with_vertex_color.bl_idname)
    self.layout.operator(BR_OT_load_image_as_mesh_plane.bl_idname)
#    self.layout.operator(BR_OT_load_image_as_mesh_cylinder.bl_idname)
#    self.layout.operator(BR_OT_load_image_as_mesh_sphere.bl_idname)
    
def menu_export_draw(self, context):
    self.layout.operator(BR_OT_export_shapekey_as_obj.bl_idname)
    self.layout.operator(BR_OT_export_selected_as_obj.bl_idname)


classes = (
    BR_OT_load_obj_as_shapekey,
    BR_OT_export_shapekey_as_obj,
    BR_OT_export_selected_as_obj,
    BR_OT_import_multiple_objs,
    BR_OT_load_fbx_with_vertex_color,
    BR_OT_load_image_as_mesh_plane,
)



def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_import_draw)
    bpy.types.TOPBAR_MT_file_export.append(menu_export_draw)


                

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
            
    bpy.types.TOPBAR_MT_file_import.remove(menu_import_draw)
    bpy.types.TOPBAR_MT_file_export.remove(menu_export_draw)


if __name__ == "__main__":
    try:
        # by running unregister here we can run this script
        # in blenders text editor
        # the first time we run this script inside blender
        # we get an error that removing the changes fails
        unregister()
    except:
        pass
    register()
