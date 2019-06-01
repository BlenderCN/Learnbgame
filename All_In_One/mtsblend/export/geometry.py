# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENSE BLOCK *****

from collections import OrderedDict

import os
import math

import bpy
import mathutils

from ..outputs import MtsLog
from ..outputs.mesh_ply import write_ply_mesh
from ..outputs.mesh_serialized import write_serialized_mesh
from ..export import ExportProgressThread, ExportCache
from ..export import is_deforming
from ..export import get_output_subdir
from ..export import get_param_recursive
from ..export.materials import export_material


class InvalidGeometryException(Exception):
    #MtsLog("Invalid Geometry Exception ")
    pass


class UnexportableObjectException(Exception):
    #MtsLog("Unexportable Object exception")
    pass


class MeshExportProgressThread(ExportProgressThread):
    #MtsLog("Mash Export Progress Thread  ")
    message = 'Exporting meshes: %i%%'


class DupliExportProgressThread(ExportProgressThread):
    #MtsLog("Dupli Export Progress Tread ")
    message = '... %i%% ...'


class GeometryExporter:

    # for partial mesh export
    KnownExportedObjects = set()
    KnownModifiedObjects = set()
    NewExportedObjects = set()

    def __init__(self, export_ctx, visibility_scene):
        self.export_ctx = export_ctx
        self.visibility_scene = visibility_scene

        self.ExportedMeshes = ExportCache('ExportedMeshes')
        self.ExportedObjects = ExportCache('ExportedObjects')
        self.ExportedFiles = ExportCache('ExportedFiles')
        # start fresh
        GeometryExporter.NewExportedObjects = set()

        self.objects_used_as_duplis = set()

        self.serializer = None
        self.fast_export = False

        from ..outputs.pure_api import PYMTS_AVAILABLE

        if PYMTS_AVAILABLE:
            from ..outputs.pure_api import Serializer

            self.serializer = Serializer()
            self.fast_export = True

    def buildMesh(self, obj, seq=0.0):
        """
        Decide which mesh format to output.
        """

        # Using a cache on object massively speeds up dupli instance export
        obj_cache_key = (self.geometry_scene, obj)

        if self.ExportedObjects.have(obj_cache_key):
            return self.ExportedObjects.get(obj_cache_key)

        mesh_definitions = self.writeMesh(obj, seq=seq)

        self.ExportedObjects.add(obj_cache_key, mesh_definitions)

        return mesh_definitions

    def writeMesh(self, obj, file_format='auto', base_frame=None, seq=0.0):
        """
        Convert supported blender objects into a MESH, and then split into parts
        according to vertex material assignment, and construct a serialized mesh
        file for Mitsuba.
        """

        if file_format not in {'serialized', 'ply'}:
            mesh_type = obj.data.mitsuba_mesh.mesh_type
            global_type = self.visibility_scene.mitsuba_engine.mesh_type

            if mesh_type == 'binary_ply' or (mesh_type == 'global' and global_type == 'binary_ply'):
                file_format = 'ply'

            else:
                file_format = 'serialized'

        if base_frame is None:
            base_frame = self.visibility_scene.frame_current

        try:
            mesh_definitions = []
            mesh = obj.to_mesh(self.geometry_scene, True, 'RENDER')

            if mesh is None:
                raise UnexportableObjectException('Cannot create render/export mesh')

            # collate faces by mat index
            ffaces_mats = {}
            mesh_faces = mesh.tessfaces

            for f in mesh_faces:
                mi = f.material_index

                if mi not in ffaces_mats.keys():
                    ffaces_mats[mi] = []

                ffaces_mats[mi].append(f)

            material_indices = ffaces_mats.keys()

            number_of_mats = len(mesh.materials)

            if number_of_mats > 0:
                iterator_range = range(number_of_mats)

            else:
                iterator_range = [0]

            for i in iterator_range:
                try:
                    if i not in material_indices:
                        continue

                    # If this mesh/mat-index combo has already been processed, get it from the cache
                    mesh_cache_key = (self.geometry_scene, obj.data, i, seq)

                    if self.allowShapeInstancing(obj, i) and self.ExportedMeshes.have(mesh_cache_key):
                        mesh_definitions.append(self.ExportedMeshes.get(mesh_cache_key))
                        continue

                    # Put files in frame-numbered subfolders to avoid
                    # clobbering when rendering animations
                    sc_fr = get_output_subdir(self.geometry_scene, base_frame)

                    def make_filename():
                        file_serial = self.ExportedFiles.serial(mesh_cache_key)
                        mesh_name = '%s_%04d_m%03d_%f' % (obj.data.name, file_serial, i, seq)
                        file_name = '%s.%s' % (bpy.path.clean_name(mesh_name), file_format)
                        file_path = '/'.join([sc_fr, file_name])
                        return mesh_name, file_path

                    mesh_name, file_path = make_filename()

                    # Ensure that all files have unique names
                    while self.ExportedFiles.have(file_path):
                        mesh_name, file_path = make_filename()

                    self.ExportedFiles.add(file_path, None)

                    # skip writing the file if the box is checked
                    skip_exporting = obj in self.KnownExportedObjects and not obj in self.KnownModifiedObjects

                    if not os.path.exists(file_path) or not (self.visibility_scene.mitsuba_engine.partial_export and skip_exporting):

                        GeometryExporter.NewExportedObjects.add(obj)

                        if file_format == 'ply':
                            write_ply_mesh(file_path, mesh_name, mesh, ffaces_mats[i])

                        else:
                            if self.fast_export:
                                self.serializer.serialize(file_path, mesh_name, mesh, i)

                            else:
                                write_serialized_mesh(file_path, mesh_name, mesh, ffaces_mats[i])

                        MtsLog('Mesh file written: %s' % (file_path))

                    else:
                        MtsLog('Skipping already exported mesh: %s' % mesh_name)

                    shape_params = {
                        'filename': self.export_ctx.get_export_path(file_path, relative = True),
                        'doubleSided': mesh.show_double_sided
                    }

                    if obj.data.mitsuba_mesh.normals == 'facenormals':
                        shape_params.update({'faceNormals': 'true'})

                    mesh_definition = (
                        mesh_name,
                        i,
                        file_format,
                        shape_params,
                        seq
                    )

                    # Only export Shapegroup and cache this mesh_definition if we plan to use instancing
                    if self.allowShapeInstancing(obj, i):
                        instance_params = self.exportShapeGroup(obj, mesh_definition)

                        mesh_definition = (
                            mesh_name,
                            i,
                            'instance',
                            instance_params,
                            seq
                        )
                        self.ExportedMeshes.add(mesh_cache_key, mesh_definition)

                    mesh_definitions.append(mesh_definition)

                except InvalidGeometryException as err:
                    MtsLog('Mesh export failed, skipping this mesh: %s' % err)

            del ffaces_mats
            bpy.data.meshes.remove(mesh)

        except UnexportableObjectException as err:
            MtsLog('Object export failed, skipping this object: %s' % err)

        return mesh_definitions

    is_preview = False

    def allowDoubleSided(self, mat_params):
        types = get_param_recursive(self.export_ctx.scene_data, mat_params, 'type')

        for t in types:
            if t in {'null', 'dielectric', 'thindielectric', 'roughdielectric', 'difftrans', 'hk', 'mask', 'twosided'}:
                return False

        return True

    def allowMaterialInstancing(self, material):
        ntree = material.mitsuba_nodes.get_node_tree()

        if not ntree:
            if material.use_nodes:
                try:
                    for node in material.node_tree.nodes:
                        if node.type == 'EMISSION':
                            return False

                except:
                    pass

            elif material.emit > 0:
                return False

            return True

        output_node = ntree.find_node('MtsNodeMaterialOutput')

        if output_node:
            for socket in output_node.inputs:
                if socket.name in {'Subsurface', 'Interior Medium', 'Exterior Medium', 'Emitter'} and \
                        socket.is_linked:
                    return False

        return True

    def allowShapeInstancing(self, obj, mat_index):

        # Only allow instancing if the mesh material is safe to use on instances
        try:
            ob_mat = obj.material_slots[mat_index].material

            if ob_mat and not self.allowMaterialInstancing(ob_mat):
                return False

        except IndexError:
            pass

        # Only allow instancing if the mesh is not deformed
        if is_deforming(obj):
            return False

        # If the mesh is only used once, instancing is a waste of memory
        # However, duplis don't increase the users count, so we cout those separately
        if (not ((obj.parent and obj.parent.is_duplicator) or obj in self.objects_used_as_duplis)) and obj.data.users == 1:
            return False

        # Only allow instancing for duplis and particles in non-hybrid mode, or
        # for normal objects if the object has certain modifiers applied against
        # the same shared base mesh.
        if hasattr(obj, 'modifiers') and len(obj.modifiers) > 0 and obj.data.users > 1:
            instance = False

            for mod in obj.modifiers:
                # Allow non-deforming modifiers
                instance |= mod.type in {'COLLISION', 'PARTICLE_INSTANCE', 'PARTICLE_SYSTEM', 'SMOKE'}

            return instance

        else:
            return not self.is_preview

    def exportShapeMaterial(self, obj, mat_index):
        try:
            ob_mat = obj.material_slots[mat_index].material
            # create material xml
            return export_material(self.export_ctx, ob_mat)

        except IndexError:
            MtsLog('WARNING: material slot %d on object "%s" is unassigned!' % (mat_index + 1, obj.name))

        return None

    def exportShapeGroup(self, obj, mesh_definition):
        """
        If the mesh is valid and instancing is allowed for this object, export
        a Shapegroup block containing the Shape definition.
        """

        me_name = mesh_definition[0]
        me_mat_index = mesh_definition[1]
        me_shape_type, me_shape_params = mesh_definition[2:4]

        if len(me_shape_params) == 0:
            return

        shape_params = me_shape_params.copy()
        double_sided = shape_params.pop('doubleSided')

        shape = {
            'type': me_shape_type,
            'id': '%s_shape' % me_name,
        }
        shape.update(shape_params)

        mat_params = self.exportShapeMaterial(obj, me_mat_index)

        if mat_params:
            if double_sided and 'bsdf' in mat_params and \
                    self.allowDoubleSided(mat_params['bsdf']):
                mat_params['bsdf'] = {
                    'type': 'twosided',
                    'bsdf': mat_params['bsdf']
                }

            shape.update(mat_params)

        self.export_ctx.data_add({
            'type': 'shapegroup',
            'id': '%s_shapegroup' % me_name,
            'shape': shape
        })

        MtsLog('Mesh definition exported: %s' % me_name)

        return {'shapegroup': {'type': 'ref', 'id': '%s_shapegroup' % me_name}}

    def exportShapeInstances(self, instance, name):
        seq = len(instance.mesh)
        meshes = len(instance.mesh[0])

        # Don't export empty definitions
        if seq < 1 or meshes < 1:
            return

        # Let's test if matrix is singular, don't export singular matrix
        for mat in instance.motion:
            if mat[1].determinant() == 0:
                MtsLog('WARNING: skipping export of singular matrix in object "%s" - "%s" - %f!'
                        % (name, instance.mesh[0][0][0], mat[0]))
                return

        mdefs = []

        for m in range(meshes):
            mdefs.append([])
            for s in range(seq):
                mdefs[m].append(instance.mesh[s][m])

        for mesh_def in mdefs:
            shapes = []

            for me_name, me_mat_index, me_shape_type, me_shape_params, me_seq in mesh_def:
                motion = instance.motion if seq == 1 else [instance.motion[len(shapes)]]
                shape_params = me_shape_params.copy()

                try:
                    double_sided = shape_params.pop('doubleSided')

                except:
                    double_sided = False

                shape = {
                    'type': me_shape_type,
                    'id': '%s_%s' % (name, me_name),
                    'toWorld': self.export_ctx.animated_transform(motion),
                }
                shape.update(shape_params)

                if me_shape_type != 'instance':
                    mat_params = self.exportShapeMaterial(instance.obj, me_mat_index)

                    if mat_params:
                        if double_sided and 'bsdf' in mat_params and \
                                self.allowDoubleSided(mat_params['bsdf']):
                            mat_params['bsdf'] = {
                                'type': 'twosided',
                                'bsdf': mat_params['bsdf']
                            }

                        shape.update(mat_params)

                shapes.append((me_seq, shape))

            if len(shapes) == 1:
                self.export_ctx.data_add(shapes[0][1])

            else:
                if shapes[0][0] > 0.0:
                    s = shapes[0][1].copy()
                    del s['id']
                    shapes.insert(0, (0.0, s))

                if shapes[-1][0] < 1.0:
                    s = shapes[-1][1].copy()
                    del s['id']
                    shapes.append((1.0, s))

                deformable = OrderedDict([
                    ('type', 'deformable'),
                ])

                times = []

                for (t, s) in shapes:
                    times.append(t)
                    deformable.update([('seq_%f' % t, s)])

                deformable.update([('times', ', '.join([str(f) for f in times]))])

                self.export_ctx.data_add(deformable)

    def BSpline(self, points, dimension, degree, u):
        controlpoints = []

        def Basispolynom(controlpoints, i, u, degree):
            if degree == 0:
                temp = 0

                if (controlpoints[i] <= u) and (u < controlpoints[i + 1]):
                    temp = 1

            else:
                N0 = Basispolynom(controlpoints, i, u, degree - 1)
                N1 = Basispolynom(controlpoints, i + 1, u, degree - 1)

                if N0 == 0:
                    sum1 = 0

                else:
                    sum1 = (u - controlpoints[i]) / (controlpoints[i + degree] - controlpoints[i]) * N0

                if N1 == 0:
                    sum2 = 0

                else:
                    sum2 = (controlpoints[i + 1 + degree] - u) / (controlpoints[i + 1 + degree] - controlpoints[i + 1]) * N1

                temp = sum1 + sum2

            return temp

        for i in range(len(points) + degree + 1):
            if i <= degree:
                controlpoints.append(0)

            elif i >= len(points):
                controlpoints.append(len(points) - degree)

            else:
                controlpoints.append(i - degree)

        if dimension == 2:
            temp = mathutils.Vector((0.0, 0.0))

        elif dimension == 3:
            temp = mathutils.Vector((0.0, 0.0, 0.0))

        for i in range(len(points)):
            temp = temp + Basispolynom(controlpoints, i, u, degree) * points[i]

        return temp

    def handler_Duplis_PATH(self, obj, psys):
        if not psys.settings.type == 'HAIR':
            MtsLog('ERROR: handler_Duplis_PATH can only handle Hair particle systems ("%s")' % psys.name)
            return ''

        for mod in obj.modifiers:
            if mod.type == 'PARTICLE_SYSTEM' and mod.show_render is False:
                return ''

        MtsLog('Exporting Hair system "%s"...' % psys.name)

        psys.set_resolution(self.geometry_scene, obj, 'RENDER')
        steps = 2 ** psys.settings.render_step
        num_parents = len(psys.particles)
        num_children = len(psys.child_particles)

        partsys_name = '%s_%s' % (obj.name, psys.name)
        det = DupliExportProgressThread()
        det.start(num_parents + num_children)

        # Put Hair files in frame-numbered subfolders to avoid
        # clobbering when rendering animations
        sc_fr = get_output_subdir(self.geometry_scene, self.visibility_scene.frame_current)

        hair_filename = '%s.hair' % bpy.path.clean_name(partsys_name)
        hair_file_path = '/'.join([sc_fr, hair_filename])

        hair_file = open(hair_file_path, 'w')

        transform = obj.matrix_world.inverted()

        for pindex in range(num_parents + num_children):
            det.exported_objects += 1
            points = []

            for step in range(0, steps + 1):
                co = psys.co_hair(obj, pindex, step)
                if not co.length_squared == 0:
                    points.append(transform * co)

            if psys.settings.use_hair_bspline:
                temp = []
                degree = 2
                dimension = 3

                for i in range(math.trunc(math.pow(2, psys.settings.render_step))):
                    if i > 0:
                        u = i * (len(points) - degree) / math.trunc(math.pow(2, psys.settings.render_step) - 1) - 0.0000000000001

                    else:
                        u = i * (len(points) - degree) / math.trunc(math.pow(2, psys.settings.render_step) - 1)
                    temp.append(self.BSpline(points, dimension, degree, u))

                points = temp

            for p in points:
                hair_file.write('%f %f %f\n' % (p[0], p[1], p[2]))

            hair_file.write('\n')

        hair_file.close()

        psys.set_resolution(self.geometry_scene, obj, 'PREVIEW')
        det.stop()
        det.join()

        MtsLog('... done, exported %s hairs' % det.exported_objects)

        return self.export_ctx.get_export_path(hair_file_path)
