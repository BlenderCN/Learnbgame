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
import bpy
import bmesh
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils import Vector, Quaternion, Color

from .rcol.gmdc import GMDC
from .blender_model import BlenderModel
from .morphmap import MorphMap
from .bone_data import BoneData
from .rcol.boundmesh import BoundMesh
from . import neckfixes


class ExportGMDC(Operator, ExportHelper):
    """Sims 2 GMDC Exporter"""
    bl_idname = "export.gmdc_export"
    bl_label = "Sims 2 GMDC (.5gd)"
    bl_options = {'REGISTER', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ".5gd"

    filter_glob = StringProperty(
            default="*.5gd",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )


    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')

        # Select objects to export depending on user choice
        obs_to_export = []
        scene_obs = []
        filename = "placeholder"
        active = context.scene.objects.active

        if active.parent and active.parent.get("filename", None):
            active = active.parent

        if not active.parent and not active.get("filename", None):
            print("No valid objects selected")
            return {'CANCELLED'}

        filename = active.get("filename", "placeholder")

        custom_bounds = None
        for ob in context.scene.objects:
            if ob.parent == active and ob.type == 'MESH' and "__bounds__" not in ob.name:
                obs_to_export.append(ob)
            elif "__bounds__" in ob.name:
                custom_bounds = ob


        # Further sanity checks, check array length and existance of Armature modifier
        if len(obs_to_export) == 0:
            print('ERROR: No valid objects were found')
            return{'CANCELLED'}
        armature = obs_to_export[0].modifiers.get( 'Armature', None )


        bones = None
        if armature:
            bones = BoneData.from_armature(armature.object)

        print('Objects to export:', obs_to_export)

        # Continue export process
        b_models = []
        for ob in obs_to_export:
            b_models.append( ExportGMDC.build_group(ob, armature, bones) )

        # Create bounding mesh(es)
        boundmesh = None
        riggedbounds = None
        if not armature:
            if custom_bounds:
                boundmesh = BoundMesh.create(obs_to_export, custom=custom_bounds)
            else:
                boundmesh = BoundMesh.create(obs_to_export)
        else:
            # BUGGED FOR SIM MESHES
            riggedbounds = self.create_riggedbounds(obs_to_export, bones)

        # Build gmdc
        gmdc_data = GMDC.build_data(filename, b_models, bones, boundmesh, riggedbounds)

        # Write data
        gmdc_data.write(self.filepath)


        return {'FINISHED'}


    @staticmethod
    def recalc_normals(bm_mesh, neckfix_type):
        # Run through all edges again, check if normals of their verts should be smoothed
        verts_to_smooth = {}
        for e in bm_mesh.edges:
            if not e.seam or not e.smooth:
                continue
            for v in e.verts:
                if tuple( v.co ) not in verts_to_smooth:
                    verts_to_smooth[ tuple( v.co ) ] = [ v ]
                    continue
                if v not in verts_to_smooth[ tuple( v.co ) ]:
                    verts_to_smooth[ tuple( v.co ) ].append( v )

        # Finally run all vertices given by above loop through the normal smooth function
        for vert in verts_to_smooth:
            total = Vector( (0,0,0) )
            for v in verts_to_smooth[vert]:
                total += v.normal
            avg = total / len(verts_to_smooth[vert])
            for v in verts_to_smooth[vert]:
                v.normal = avg

        # IF a neck fix is specified, set apropriate normals
        if neckfix_type != None and neckfix_type != -1:
            for vert in bm_mesh.verts:
                if not tuple(vert.co) in neckfixes.neck_normals[neckfix_type]:
                    continue

                vert.normal = Vector( neckfixes.neck_normals[neckfix_type][tuple(vert.co)] )
            print()


    @staticmethod
    def normals_from_colors(mesh):
        """
        Replace normals based on vertex colors,
        only applies to verts affected by __NORMALS__
        """
        #if not object.vertex_groups['__NORMALS__']:
        #    return
        if not mesh.vertex_colors['__NORMALS__']:
            return

        #mesh = object.data
        color_map = mesh.vertex_colors['__NORMALS__']
        #grp_idx = object.vertex_groups['__NORMALS__'].index

        for poly in mesh.polygons:
            for vert_idx, loop_idx in zip(poly.vertices, poly.loop_indices):
                #groups = [grp.group for grp in mesh.vertices[vert_idx].groups]
                rgb = Vector(color_map.data[loop_idx].color)
                if rgb.x == 0 and rgb.y == 0 and rgb.z == 0:
                    continue
                normal = rgb * 2 - Vector((1,1,1))
                mesh.vertices[vert_idx].normal = normal




    @staticmethod
    def build_group(object, armature, bones):
        neckfix_type = object.get("neck_fix")


        # Mark seams from UV Islands, ideally there would be a nice way to do this without ops
        bpy.context.scene.objects.active = object   # Set active selection to current object
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.uv.seams_from_islands(mark_seams=True, mark_sharp=False)
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.context.scene.objects.active = None     # Revert active selection to None


        # Make a copy of the mesh to keep the original intact
        mesh = object.to_mesh(bpy.context.scene, False, 'RENDER', False, False)
        temp_obj = bpy.data.objects.new('temp_obj', mesh)
        bm = bmesh.new()
        bm.from_mesh(mesh)


        # Triangulate faces
        bmesh.ops.triangulate(bm, faces=bm.faces)

        ## RECALCULATING NORMALS
        # Get all edges to split (UV seams and Sharp edges)
        uvsplit = []
        for e in bm.edges:
            if e.seam or not e.smooth:
                uvsplit.append(e)

        # Split edges given by above loop
        bmesh.ops.split_edges(bm, edges=uvsplit)

        ExportGMDC.recalc_normals(bm, neckfix_type)

        bm.to_mesh(mesh)
        bm.free()

        ExportGMDC.normals_from_colors(mesh)

        vertices    = []
        normals     = []
        tangents    = []
        uvs         = []
        faces       = []
        bone_assign = []
        bone_weight = []
        name        = object.name
        opacity     = object.get("opacity", -1)

        # Vertices, normals and pre-populating uvs
        for vert in mesh.vertices:
            vertices.append( (-vert.co[0], -vert.co[1], vert.co[2]) )
            vert.normal.normalize()
            normals.append( (-vert.normal[0], -vert.normal[1], vert.normal[2]) )


            # c1 = vert.normal.cross(Vector( (0,1,0) )).normalized()
            # c2 = vert.normal.cross(Vector( (0,0,1) )).normalized()
            #
            # if c1.length > c2.length:
            #     tangents.append(c1)
            # else:
            #     tangents.append(c2)


            # print(tan)
            # uvs.append( None )

        # Tangents
        if object.get("calc_tangents") != None and object.get("is_shadow") == False:
            for vert in mesh.vertices:
                tan = vert.normal.orthogonal().normalized()
                tangents.append( (tan[0], tan[1], tan[2]) )


        # Faces
        for f in mesh.polygons:
            faces.append( (f.vertices[0], f.vertices[1], f.vertices[2]) )


        # Tangents
        # mesh.calc_tangents()

        # tangents = [0] * len(vertices)
        # for i, polygon in enumerate(mesh.polygons):
        #     for j, vert in enumerate([mesh.loops[z] for z in polygon.loop_indices]):
        #         tan = ( vert.tangent[0], vert.tangent[1], vert.tangent[2] )
        #         tangents[polygon.vertices[j]] = tan
        #         print(tan, vert.tangent)


        # UVs
        uvs = [None]*len(vertices)
        uv_layer = mesh.uv_layers[0]
        for i, polygon in enumerate(mesh.polygons):
            for j, loopindex in enumerate(polygon.loop_indices):
                meshuvloop = mesh.uv_layers.active.data[loopindex]
                uv = ( meshuvloop.uv[0], -meshuvloop.uv[1] + 1 )
                vertidx = faces[i][j]
                uvs[vertidx] = uv


        # TEMPORARY FIX FOR BAD BONE ASSIGNMENTS IN SIMS
        bonemap = {}
        for i, grp in enumerate(object.vertex_groups):
            for b in BoneData.bone_parent_table:
                if grp.name == b[0]:
                    bonemap[i] = b[2]


        # Vertex groups (Bone assignments and weights)
        if armature:
            for vert in mesh.vertices:
                assign = [255] * 4
                weight = [0] * 3
                for i, assignment in enumerate(vert.groups):
                    if i < 3:
                        weight[i] = assignment.weight
                    if len(bones) == 65:
                        assign[i] = bonemap[assignment.group]
                    else:
                        assign[i] = assignment.group
                bone_assign.append(assign)
                bone_weight.append(weight)


        # Morphs
        morphs = []
        morph_bytemap = None
        if mesh.shape_keys:

            temp_obj.show_only_shape_key = True

            # Recalculate normals for each morph and then create it
            for key in temp_obj.data.shape_keys.key_blocks[1:]:
                # Set active shape key
                idx = temp_obj.data.shape_keys.key_blocks.find(key.name)
                temp_obj.active_shape_key_index = idx

                # Create a copy from active shape key
                morphmesh = temp_obj.to_mesh(bpy.context.scene, True, 'RENDER', False, False)

                # Initialize bmesh
                morph_bm = bmesh.new()
                morph_bm.from_mesh(morphmesh)

                # Recalculate normals and create morph
                ExportGMDC.recalc_normals(morph_bm, neckfix_type)

                # Remove copied mesh
                morph_bm.to_mesh(morphmesh)
                morph_bm.free()

                # Replace normals
                ExportGMDC.normals_from_colors(morphmesh)

                # Create morph and remove copied mesh
                morphs.append( MorphMap.from_blender(mesh, morphmesh, key.name) )
                bpy.data.meshes.remove(morphmesh)


            temp_obj.active_shape_key_index = 0
            temp_obj.show_only_shape_key = False



            morph_bytemap = MorphMap.make_bytemap(morphs, len(vertices))


        # Remove copied mesh once done
        bpy.data.meshes.remove(mesh)


        return BlenderModel(vertices, normals, tangents, faces, uvs, name,
                            bone_assign, bone_weight, opacity, morphs,
                            morph_bytemap)


    def create_riggedbounds(self, objects, bones):
        subsets = [None]*len(bones)

        # TEMPORARY FIX FOR BAD BONE ASSIGNMENTS IN SIMS
        bonemap = {}
        for i, grp in enumerate(objects[0].vertex_groups):
            if len(bones) == 65 and bones[0].name == 'simskel':
                for b in BoneData.bone_parent_table:
                    if grp.name == b[0]:
                        bonemap[i] = b[2]
            else:
                for i in range(len(bones)):
                    bonemap[i] = i

        for subset, b in enumerate(bones):
            # Negate trans to account for flipped axes
            # trans = Vector(b.position)
            # trans.negate()
            # Rotate rot quaternion to account for flipped axes
            rot = Quaternion(bones[bonemap[subset]].rotation)
            # rot.rotate( Quaternion((0,0,0,1)) )

            # relative_zero = rot * trans

            vertices = []
            vertco = []
            faces = []

            for ob in objects:
                ob.modifiers.new("tri", 'TRIANGULATE')
                mesh = ob.to_mesh(bpy.context.scene, True, 'RENDER', False, False)
                ob.modifiers.remove( ob.modifiers["tri"] )


                for f in mesh.polygons:
                    assigncount = 0

                    for idx in f.vertices:
                        for assignment in mesh.vertices[idx].groups:
                            if assignment.group == b.subset:
                                assigncount += 1

                    if assigncount < 1:
                        continue

                    face = []
                    for idx in f.vertices:
                        vert = mesh.vertices[idx]
                        if not vert in vertices:
                            vertices.append(vert)
                        face.append( vertices.index(vert) )
                    faces.append(face)


                for v in vertices:
                    # I don't know how this works, but it seems like it does
                    newco = rot * Vector( (v.co[0], v.co[1], -v.co[2]) )
                    # newco = rot * newcoord
                    vertco.append(tuple(
                        Vector(bones[bonemap[subset]].position) - newco
                    ))


            # print(subset, b.name, len(vertices), len(faces))
            # if len(bones) == 65 and bones[0].name == 'simskel':
            subsets[bonemap[subset]] = BoundMesh(vertco, faces)
            # else:
            #     subsets[subset] = BoundMesh(vertco, faces)

        return subsets






# for vert in mesh.vertices:
#     assign = [255] * 4
#     weight = [0] * 3
#     for i, assignment in enumerate(vert.groups):
#         if i < 3:
#             weight[i] = assignment.weight
#         assign[i] = assignment.group
#     bone_assign.append(assign)
#     bone_weight.append(weight)
