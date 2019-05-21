'''
Copyright (C) 2018 SmugTomato

Created by SmugTomato

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import time
import bpy, math
import bmesh
from mathutils import Vector, Matrix, Quaternion
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from rna_prop_ui import rna_idprop_ui_prop_get

from .rcol.gmdc import GMDC
# from .rcol.rcol_data import Rcol
# from .rcol.data_helper import DataHelper
from . import blender_model
from .bone_data import BoneData
from . import neckfixes

class ImportGMDC(Operator, ImportHelper):
    """Sims 2 GMDC Importer"""
    bl_idname = "import.gmdc_import"
    bl_label = "Sims 2 GMDC (.5gd)"
    bl_options = {'REGISTER', 'UNDO'}

    # ImportHelper mixin class uses this
    filename_ext = ".5gd"

    filter_glob = StringProperty(
            default="*.5gd",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    do_skeleton = BoolProperty(
            name="Import Skeleton",
            description="Import Skeleton",
            default=True,
            )

    do_bounddebug = BoolProperty(
            name="[DEBUG] Bound mesh",
            description="Import bounding mesh",
            default=False,
            )

    do_neckdebug = BoolProperty(
            name="[DEBUG] Neck normals",
            description="Lookup neck vertex normals",
            default=False,
            )

    def execute(self, context):
        gmdc_data = GMDC.from_file_data(self.filepath)
        if gmdc_data.load_header() == False:
            print ('Unsupported GMDC version', hex(gmdc_data.header.file_type))
            return False

        gmdc_data.load_data()
        b_models = blender_model.BlenderModel.groups_from_gmdc(gmdc_data)


        # Container for all groups and their armature, keeps the scene clean
        bpy.ops.object.empty_add(
            type='PLAIN_AXES',
            location=(0, 0, 0)
        )
        filename  = gmdc_data.header.file_name
        container = bpy.context.scene.objects.active
        container.name = filename.split("-")[0]
        container["filename"]   = filename


        if self.do_neckdebug:
            self.debug_necknormals(b_models[0])
            return {'FINISHED'}


        armature = None
        if self.do_skeleton and gmdc_data.model.transforms:
            armature = self.import_skeleton(gmdc_data)
            armature.parent = container


        # DEBUG
        if self.do_bounddebug:
            skeldata = BoneData.build_bones(gmdc_data)
            self.debug_boundmesh(gmdc_data.subsets, skeldata)
            return {'FINISHED'}



        if b_models != False:
            for model in b_models:
                print( self.do_import(model, armature, container) )

        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}


    def parse_data(self, context, filepath):
        gmdc_data = GMDC.from_file_data(context, filepath)

        if gmdc_data.load_header() == False:
            print ('Unsupported GMDC version', hex(gmdc_data.header.file_type))
            return False

        gmdc_data.load_data()
        b_models = blender_model.BlenderModel.groups_from_gmdc(gmdc_data)
        return b_models


    def import_skeleton(self, data):
        skeldata = BoneData.build_bones(data)

        # Create armature and object
        name = 'Armature'
        bpy.ops.object.add(
            type='ARMATURE',
            enter_editmode=True,
            location=(0,0,0)
        )
        # Armature object
        # ob = bpy.context.object
        ob = bpy.context.scene.objects.active
        ob.show_x_ray = True
        ob.name = name
        # Armature
        amt = ob.data
        amt.draw_type = 'STICK'

        # Create bones from skeleton data
        # Sims 2 bones seem to be reversed head to tail
        for bonedata in skeldata:
            bone = amt.edit_bones.new(bonedata.name)

            # Negate trans to account for flipped axes
            trans = Vector(bonedata.position)
            trans.negate()
            # Rotate rot quaternion to account for flipped axes
            rot = Quaternion(bonedata.rotation)
            rot.rotate( Quaternion((0,0,0,1)) )

            bone.head = rot * trans
            if bonedata.parent != None:
                parent = amt.edit_bones[bonedata.parent]
                bone.parent = parent
                bone.tail = parent.head
            # Check if the length of a bone is too short for blender
            bonelen = bone.tail.length - bone.head.length
            if bonelen > -0.0005 and bonelen < 0.0005:
                # Blender does not support 0 length bones
                bone.head += Vector((0,0,0.00005))

            # Enter custom properties for exporting later
            # # Translate Vector and Rotation Quaternion
            bone["translate"] = [bonedata.position[0], bonedata.position[1], bonedata.position[2]]
            bone["rotation"] = [bonedata.rotation[0], bonedata.rotation[1], bonedata.rotation[2], bonedata.rotation[3]]


        # Go back to Object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Return the Armature object
        return ob


    def __add_property(self, obj, key, value, range, description):
        obj[key] = value
        prop_ui = rna_idprop_ui_prop_get(obj, key)
        prop_ui["min"] = range[0]
        prop_ui["max"] = range[1]
        prop_ui["soft_min"] = range[0]
        prop_ui["soft_max"] = range[1]
        prop_ui["description"] = description

        for area in bpy.context.screen.areas:
            area.tag_redraw()


    def do_import(self, b_model, armature, container):
        print('Importing group: \'', b_model.name, '\'', sep='')


        # Create object and mesh
        mesh = bpy.data.meshes.new(b_model.name)
        mesh.use_auto_smooth = True
        mesh.auto_smooth_angle = 3.14

        object = bpy.data.objects.new(b_model.name, mesh)
        object.parent = container
        bpy.context.scene.objects.link(object)
        bpy.context.scene.objects.active = object


        # Assign custom properties
        self.__add_property(
            obj   = object,
            key   = "opacity",
            value = b_model.opacity_amount,
            range = [-1, 255],
            description = "Opacity of this mesh."
        )
        self.__add_property(
            obj   = object,
            key   = "is_shadow",
            value = "shadow" in object.name,
            range = [0, 1],
            description = "Is this a shadow mesh?"
        )
        do_tangents = object.get("is_shadow") == False
        self.__add_property(
            obj   = object,
            key   = "calc_tangents",
            value = do_tangents,
            range = [0, 1],
            description = "Should tangents be calculated on export?"
        )
        self.__add_property(
            obj   = object,
            key   = "neck_fix",
            value = -1,
            range = [-1, 5],
            description = "Neck fix to apply (See GMDC Panel)"
        )


        # Load vertices and faces
        mesh.from_pydata(b_model.vertices, [], b_model.faces)


        # Load normals
        for i, vert in enumerate(mesh.vertices):
            vert.normal = b_model.normals[i]


        # Create UV layer and load UV coordinates
        mesh.uv_textures.new('UVMap')
        for i, polygon in enumerate(mesh.polygons):
            for j, loopindex in enumerate(polygon.loop_indices):
                meshuvloop = mesh.uv_layers.active.data[loopindex]

                vertex_index = b_model.faces[i][j]
                meshuvloop.uv = b_model.uvs[vertex_index]


        # Load bone assignments and weights
        # Check for mismatches in index counts
        if armature:
            # Create vertex groups for bone assignments
            for b in armature.data.bones:
                object.vertex_groups.new(b.name)


            if len(b_model.vertices) != len(b_model.bone_assign) or \
                len(b_model.vertices) != len(b_model.bone_weight):
                error = 'ERROR: Group ' + b_model.name + '\'s vertex index counts don\'t match.'
                return error


            print('Applying bone weights...')
            for i in range(len(b_model.bone_assign)):
                remainder = 1.0     # Used for an implied 4th bone weight
                # print(i, b_model.bone_assign[i])
                for j in range(len(b_model.bone_assign[i])):
                    # If it's a sim skeleton, use boneparent table
                    # Otherwise use bone names
                    if len(armature.data.bones) == 65:
                        grpname = BoneData.bone_parent_table[ b_model.bone_assign[i][j] ][0]
                    else:
                        # print(b_model.bone_assign[i][j])
                        grpname = armature.data.bones[ b_model.bone_assign[i][j] ].name

                    vertgroup = object.vertex_groups[grpname]
                    if j != 3:
                        weight = b_model.bone_weight[i][j]
                        remainder -= weight
                        vertgroup.add( [i], weight, 'ADD' )
                    else:
                        vertgroup.add( [i], remainder, 'ADD' )


            # Add Armature modifier
            object.modifiers.new("Armature", 'ARMATURE')
            object.modifiers["Armature"].object = armature
            object.modifiers["Armature"].use_deform_preserve_volume = False


        # Apply Morphs(if any) as shape keys
        print('Loading morphs as shape keys...')
        if b_model.morphs:
            # Blender always needs a base shape key
            shpkey = object.shape_key_add(from_mix=False)
            shpkey.name = "Basis"

            for morph in b_model.morphs:
                if morph.name == ', ':
                    continue

                shpkey = object.shape_key_add(from_mix=False)
                shpkey.name = morph.name

                for i, vert in enumerate(mesh.vertices):
                    shpkey.data[vert.index].co = Vector( (
                        vert.co[0] + morph.deltas[i][0],
                        vert.co[1] + morph.deltas[i][1],
                        vert.co[2] + morph.deltas[i][2]
                    ) )

        # Add vertex group to control whicg verts keep their old normals
        #object.vertex_groups.new("__NORMALS__")
        #vertgroup = object.vertex_groups['__NORMALS__']
        ## Should be done manually by user before exporting
        # for i in range (len(mesh.vertices)):
        #     vertgroup.add( [i], 1, 'ADD' )

        # Import Original normals as vertex colors
        mesh.vertex_colors.new("__NORMALS__")
        color_map = mesh.vertex_colors['__NORMALS__']
        for poly in mesh.polygons:
            for vert_idx, loop_idx in zip(poly.vertices, poly.loop_indices):
                # Convert Vertex normal to a valid Color
                normal = Vector(b_model.normals[vert_idx])
                normal.normalize()
                rgb = ( normal + Vector((1.0, 1.0, 1.0)) ) * 0.5
                # Set Vertex color to new color
                color_map.data[loop_idx].color = rgb
        print("Original normals imported as vertex colors on layer '__NORMALS__'")
        print()


        # After all that, merge doubles and make originally hard edges sharp
        bm = bmesh.new()
        bm.from_mesh(mesh)

        edges = self.get_sharp(b_model)

        bmesh.ops.remove_doubles(bm, verts=bm.verts)

        # Check mesh edges against edge dictionary, mark hard edges sharp after removing doubles
        numedges = 0
        for e in bm.edges:
            edgemid = tuple((e.verts[0].co + e.verts[1].co) / 2)
            if len(edges[edgemid]) > 2:
                numedges += 1
                e.smooth = False

        print(numedges, 'Hard edges found.')
        print()

        bm.to_mesh(mesh)
        bm.free()

        object.select = True
        bpy.ops.object.shade_smooth()


        # Delete loose geometry in case of Maxis object imports
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete_loose()
        bpy.ops.object.mode_set(mode='OBJECT')


        return 'Group \'' + b_model.name + '\' imported.\n'


    def get_sharp(self, b_model):
        print('Checking hard edges...')

        edges = {}

        # Build edges from faces in b_model and check if their normals differ
        for f in b_model.faces:
            for i, vertidx in enumerate(f):
                idx_tocheck = i + 1
                if i == len(f) - 1:
                    idx_tocheck = 0
                e = tuple(
                    ( Vector( b_model.vertices[f[i]] ) + Vector( b_model.vertices[f[idx_tocheck]] ) ) / 2
                )
                if e not in edges:
                    edges[e] = [ b_model.normals[f[i]], b_model.normals[f[idx_tocheck]] ]
                    continue
                if b_model.normals[f[i]] not in edges[e]:
                    edges[e].append(b_model.normals[f[i]])
                if b_model.normals[f[idx_tocheck]] not in edges[e]:
                    edges[e].append(b_model.normals[f[idx_tocheck]])

        return edges



    # DEBUG
    def debug_boundmesh(self, subsets, skeldata):
        vert_offset = 0
        for set, bone in zip(subsets, skeldata):
            if not set.faces:
                continue

            # Negate trans to account for flipped axes
            trans = Vector(bone.position)
            trans.negate()
            # Rotate rot quaternion to account for flipped axes
            rot = Quaternion(bone.rotation)
            rot.rotate( Quaternion((0,0,0,1)) )

            relative_zero = rot * trans
            verts = []
            faces = []
            for vert in set.vertices:
                # Relative vertex position: Absolute position - bone position
                # I guess?
                verts.append( rot * Vector(vert) + relative_zero )

            # Create object and mesh
            mesh = bpy.data.meshes.new(bone.name)

            object = bpy.data.objects.new(bone.name, mesh)
            bpy.context.scene.objects.link(object)
            bpy.context.scene.objects.active = object


            # Load vertices and faces
            mesh.from_pydata(verts, [], [])


    # DEBUG
    def debug_necknormals(self, model):
        print( "######## NECK NORMALS ########" )
        print()
        print()
        print()

        for vco, vno in zip(model.vertices, model.normals):
            if vco in neckfixes.test:
                print(vco, ":\n    ", vno, ",", sep="")
                print(neckfixes.neck_normals[0][vco])

        print()
        print()
        print()
        print( "######## NECK NORMALS ########" )
