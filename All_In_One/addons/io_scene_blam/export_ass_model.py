#  Copyright (c) 2019 Oliver Hitchcock ojhitchcock@gmail.com
#
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

import bpy
import bmesh
from bpy_extras.io_utils import ExportHelper
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
    PointerProperty,
    EnumProperty,
    )
from bpy.types import Operator
from .utils import (
    get_root_collection,
    get_instancer_collection,
    mesh_triangulate
    )

# ------------------------------------------------------------
# Menu's and panels:
class Blam_ExportAssModel(Operator, ExportHelper):
    bl_idname = "blam.export_ass_model"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Halo 2 model file"
    bl_options = {'PRESET'}

    filename_ext = ".jms"

    filter_glob: StringProperty(
        default="*.jms",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
        )
    
    use_mesh_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers",
        default=True,
        )
    
    use_triangles: BoolProperty(
        name="Triangulate Faces",
        description="Convert all faces to triangles",
        default=True,
        )

    def execute(self, context):
        return write_ass_model(
            context,
            self.filepath,
            self.use_triangles,
            self.use_mesh_modifiers
            )

def menu_func_export(self, context):
    self.layout.operator(Blam_ExportAssModel.bl_idname, text='Halo 2 Model (.ass)')

def write_ass_model(context, filepath,
                    EXPORT_TRI=True,
                    EXPORT_APPLY_MODIFIERS=True):
    root_collection = get_root_collection()
    #instancer_collection = get_instancer_collection()

    # Get all objects and instanced objects
    # Halo CE does not use instanced geometry
    objects = root_collection.all_objects
    materials = []
    object_data = []
    object_instances = []

    material_count = 0
    object_count = 0

    for obj in objects:
        material_indexs = []
        for mat in obj.material_slots:
            if mat.name not in materials:
                materials.append(mat.name)
                material_indexs.append(material_count)
                material_count += 1
            else:
                material_indexs.append(materials.index(mat.name))

        # Mesh changes
        ## Apply modifiers
        mesh = obj.to_mesh(context.depsgraph, EXPORT_APPLY_MODIFIERS)

        ## Triangulate
        if EXPORT_TRI:
            # _must_ do this first since it re-allocs arrays
            mesh_triangulate(mesh)
        
        vertex_count = 0
        tri_count = 0
        vertices = []
        triangles = []

        # Loop triangles
        for poly in mesh.polygons:
            # Vertices
            for i in poly.loop_indices:
                vertices.append(
                    '0\n' +
                    '{0[0]:0.6f}\t{0[1]:0.6f}\t{0[2]:0.6f}\n'.format(
                        mesh.vertices[mesh.loops[i].vertex_index].co
                        ) +
                    '{0[0]:0.6f}\t{0[1]:0.6f}\t{0[2]:0.6f}\n'.format( # vertex normal (is the face normal???)
                        mesh.vertices[mesh.loops[i].vertex_index].normal
                        ) +
                    '0\n' + # node 1 index
                    '1\n' + # node 1 weight
                    '{0[0]:0.6f}\t{0[1]:0.6f}\n'.format( # uv coordinates
                        mesh.uv_layers.active.data[i].uv
                        ) +
                    str(0) + '\n' # unknown
                    )

            # Triangles
            triangles.append(
                str(material_indexs[poly.material_index]) + '\n' + # material index
                str(i) + '\n' # object vertex set index
                )
            vertex_count += 3
            tri_count += 1
        
        object_data.append(
            str(vertex_count) + '\n' +
            (vertex for vertex in vertices) +
            str(tri_count) + '\n' +
            (tri for tri in triangles)
            )

        object_instances.append(
            '\n' + # object index after frame?
            '\"' + obj.name + '\"\n' + # object name
            '\n' + # object index after frame again ?
            '0\n' +
            '0\n' +
            '0.0\t0.0\t0.0\t1.0\n' +
            '{0[0]:0.6f}\t{0[1]:0.6f}\t{0[2]:0.6f}\n'.format( # object position
                obj.location
                ) +
            '{0[0]:0.6f}\t{0[1]:0.6f}\t{0[2]:0.6f}\n'.format( # object scale
                obj.scale
                ) +
            '{0[0]:0.6f}\t{0[1]:0.6f}\t{0[2]:0.6f}\t{0[3]:0.6f}\n'.format( # object rotation
                obj.rotation_euler.to_quaternion()
                ) +
            '0.0\t0.0\t0.0\n' +
            '1.0\n'
            )

        object_count += 1

    # Start write

def get_object_shader_flags(obj):
    blam = obj.blam
    if blam.custom_flags != "":
        return blam.custom_flags
    else:
        flag_string = ""
        if blam.double_sided:
            flag_string += '%'
        if blam.allow_transparency:
            flag_string += '#'
        if blam.render_only:
            flag_string += '!'
        if blam.large_collideable:
            flag_string += '*'
        if blam.fog_plane:
            flag_string += '$'
        if blam.ladder:
            flag_string += '^'
        if blam.breakable:
            flag_string += '-'
        if blam.ai_defeaning:
            flag_string += '&'
        if blam.collision_only:
            flag_string += '@'
        if blam.exact_portal:
            flag_string += '.'

        return flag_string
