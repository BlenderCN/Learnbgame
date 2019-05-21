# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
# ***** END GPL LICENCE BLOCK *****
#
# Blender Libs
import bpy, bl_operators
import os, struct, mathutils

# PBRTv3 Libs
from .. import PBRTv3Addon
from ..outputs import PBRTv3Manager
from ..export.scene import SceneExporter

from ..extensions_framework import util as efutil


@PBRTv3Addon.addon_register_class
class EXPORT_OT_luxrender(bpy.types.Operator):
    bl_idname = 'export.luxrender'
    bl_label = 'Export PBRTv3 Scene (.PBRTv3s)'

    filter_glob = bpy.props.StringProperty(default='*.PBRTv3s', options={'HIDDEN'})
    use_filter = bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    filename = bpy.props.StringProperty(name='LXS filename')
    directory = bpy.props.StringProperty(name='LXS directory')

    api_type = bpy.props.StringProperty(options={'HIDDEN'}, default='FILE')  # Export target ['FILE','API',...]
    write_files = bpy.props.BoolProperty(options={'HIDDEN'}, default=True)  # Write any files ?
    write_all_files = bpy.props.BoolProperty(options={'HIDDEN'},
                                             default=True)  # Force writing all files, don't obey UI settings

    scene = bpy.props.StringProperty(options={'HIDDEN'}, default='')  # Specify scene to export

    def invoke(self, context, event):
        self.filename = efutil.scene_filename() + '.PBRTv3s'  # prefill with blender (temp-) filename
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.properties.scene:
            scene = context.scene
        else:
            scene = bpy.data.scenes[self.properties.scene]

        PBRTv3Manager.SetActive(None)

        return SceneExporter() \
            .set_report(self.report) \
            .set_properties(self.properties) \
            .set_scene(scene) \
            .export()


menu_func = lambda self, context: self.layout.operator("export.luxrender", text="Export PBRTv3 Scene")
bpy.types.INFO_MT_file_export.append(menu_func)


class InvalidGeometryException(Exception):
    pass

class UnexportableObjectException(Exception):
    pass

@PBRTv3Addon.addon_register_class
class PBRTv3_OT_export_pbrtv3_proxy(bpy.types.Operator):
    """Export an object as ply file, replace the original mesh with a preview version and set path to the exported ply file."""

    bl_idname = 'export.export_pbrtv3_proxy'
    bl_label = 'Export as PBRTv3 Proxy'
    bl_description = 'Converts selected objects to PBRTv3 proxies (simple preview geometry, original mesh is loaded at rendertime)'

    original_facecount = bpy.props.IntProperty(name = 'Original Facecount', default = 1)
    # hidden properties
    directory = bpy.props.StringProperty(name = 'PLY directory')
    filter_glob = bpy.props.StringProperty(default = '*.ply', options = {'HIDDEN'})
    use_filter = bpy.props.BoolProperty(default = True, options = {'HIDDEN'})

    def set_proxy_facecount(self, value):
        self["proxy_facecount"] = value
        self["proxy_quality"] = float(value) / float(self.original_facecount)

    def get_proxy_facecount(self):
        try:
            return self["proxy_facecount"]
        except KeyError:
            print("keyerror in get proxy facecount")
            return 0

    def set_proxy_quality(self, value):
        self["proxy_quality"] = value
        self["proxy_facecount"] = self.original_facecount * self.proxy_quality

    def get_proxy_quality(self):
        try:
            return self["proxy_quality"]
        except KeyError:
            print("keyerror in get proxy quality")
            return .5

    proxy_facecount = bpy.props.IntProperty(name = 'Proxy Facecount',
                                            min = 1,
                                            default = 5000,
                                            subtype = 'UNSIGNED',
                                            set = set_proxy_facecount,
                                            get = get_proxy_facecount)

    proxy_quality = bpy.props.FloatProperty(name = 'Preview Mesh Quality',
                                            default = 0.02,
                                            soft_min = 0.001,
                                            max = 1.0,
                                            soft_max = 0.5,
                                            subtype = 'UNSIGNED',
                                            set = set_proxy_quality,
                                            get = get_proxy_quality)

    overwrite = bpy.props.BoolProperty(default = True, name = "Overwrite Existing Files")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)

        active_obj = context.active_object
        if active_obj is not None:
            test_mesh = active_obj.to_mesh(context.scene, True, 'RENDER')
            self.original_facecount = len(test_mesh.polygons) * 2
            bpy.data.meshes.remove(test_mesh, do_unlink=False)

        self.proxy_facecount = 5000

        return {'RUNNING_MODAL'}

    def execute(self, context):
        selection = context.selected_objects.copy()

        for obj in selection:
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            context.scene.objects.active = obj

            if obj.type in ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT']:
                # make sure it's a single-user mesh (is NOT duplicated with Alt+D)
                if obj.data.users > 1:
                    print("[Object: %s] Can't make proxy from multiuser mesh" % obj.name)
                    print("-----------------")
                    continue

                #################################################################
                # Prepare object for PLY export
                #################################################################
                # don't make curves a proxy when their geometry contains no faces
                if obj.type == 'CURVE':
                    test_mesh = obj.to_mesh(context.scene, True, 'RENDER')
                    if len(test_mesh.polygons) == 0:
                        print("[Object: %s] Skipping curve (does not contain geometry)" % obj.name)
                        print("-----------------")
                        continue
                    bpy.data.meshes.remove(test_mesh, do_unlink=False)

                # make sure object is of type 'MESH'
                if obj.type in ['CURVE', 'SURFACE', 'META', 'FONT']:
                    bpy.ops.object.convert(target = 'MESH')

                # rename object
                obj.name = obj.name + '_lux_proxy'

                # apply all modifiers
                for modifier in obj.modifiers:
                    bpy.ops.object.modifier_apply(modifier = modifier.name)

                # find out how many materials are actually used
                used_material_indices = []
                for face in obj.data.polygons:
                    mi = face.material_index
                    if mi not in used_material_indices:
                        used_material_indices.append(mi)
                used_materials_amount = len(used_material_indices)

                # save bounding box for later use
                dimensions = obj.dimensions.copy()
                location = obj.location.copy()
                rotation = obj.rotation_euler.copy()

                # clear parent
                bpy.ops.object.parent_clear(type = 'CLEAR_KEEP_TRANSFORM')
                # split object by materials
                bpy.ops.mesh.separate(type = 'MATERIAL')

                # create list of references to the created objects
                created_objects = context.selected_objects.copy()
                proxy_objects = []

                #################################################################
                # Export split objects to PLY files
                #################################################################
                for object in created_objects:
                    proxy_mesh, ply_path = self.export_ply(context, object)

                    if proxy_mesh is None or ply_path is None:
                        print("[Object: %s] Could not export object" % object.name)
                        continue

                    #################################################################
                    # Create lowpoly preview mesh with decimate modifier
                    # We have to replace the objects with new ones because we can't apply modifiers in this loop
                    # for some reason (only the last one is applied), so we have to use to_mesh() as a workaround
                    #################################################################
                    context.scene.objects.active = object
                    decimate = object.modifiers.new('proxy_decimate', 'DECIMATE')
                    decimate.ratio = self.proxy_quality

                    temp = object.to_mesh(context.scene, True, 'RENDER')

                    context.scene.objects.unlink(object)

                    ob = bpy.data.objects.new(object.name, temp)
                    context.scene.objects.link(ob)
                    proxy_objects.append(ob)

                    #################################################################
                    # Set exported PLY as proxy file
                    #################################################################
                    ob.pbrtv3_object.append_proxy = True
                    ob.pbrtv3_object.external_mesh = ply_path

                    print("[Object: %s] Created proxy object" % ob.name)
                    print("-----------------")

                # create bounding box cube and parent objects to it
                if used_materials_amount > 1:
                    bpy.ops.object.empty_add(rotation=(0, 0, 0),
                                             location=(0, 0, 0),
                                             layers=obj.layers)

                    bounding_cube = context.active_object
                    bounding_cube.name = obj.name + '_boundingBox'
                    bounding_cube.empty_draw_type = 'CUBE'
                    # bounding_cube.scale = dimensions / 2

                    for object in proxy_objects:
                        object.location = (0, 0, 0)
                        object.parent = bounding_cube

                    bounding_cube.location = location
                    bounding_cube.rotation_euler = rotation

        return {'FINISHED'}

    def export_ply(self, context, obj):
        try:
            ply_path = None
            mesh = obj.to_mesh(context.scene, True, 'RENDER')
            if mesh is None:
                raise UnexportableObjectException('Failed to create export mesh from Blender object')
            mesh.name = obj.data.name + '_proxy'
            print('[Object: %s] Exporting PLY...' % obj.name)

            # Collate faces by mat index
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

                    def make_plyfilename():
                        _mesh_name = '%s_m%03d' % (obj.data.name, i)
                        _ply_filename = '%s.ply' % bpy.path.clean_name(_mesh_name)
                        _ply_path = self.directory + _ply_filename

                        return _mesh_name, _ply_path

                    mesh_name, ply_path = make_plyfilename()

                    if (not os.path.exists(ply_path) or self.overwrite) and not obj.pbrtv3_object.append_proxy:
                        uv_textures = mesh.tessface_uv_textures
                        vertex_color = mesh.tessface_vertex_colors.active

                        uv_layer = None
                        vertex_color_layer = None

                        if len(uv_textures) > 0:
                            if mesh.uv_textures.active and uv_textures.active.data:
                                uv_layer = uv_textures.active.data

                        if vertex_color:
                            vertex_color_layer = vertex_color.data

                        # Here we work out exactly which vert+normal combinations
                        # we need to export. This is done first, and the export
                        # combinations cached before writing to file because the
                        # number of verts needed needs to be written in the header
                        # and that number is not known before this is done.

                        # Export data
                        co_no_uv_vc_cache = []
                        face_vert_indices = {}  # mapping of face index to list of exported vert indices for that face

                        # Caches
                        # mapping of vert index to exported vert index for verts with vert normals

                        vert_vno_indices = {}
                        vert_use_vno = set()  # Set of vert indices that use vert normals
                        vert_index = 0  # exported vert index

                        c1 = c2 = c3 = c4 = None

                        for fidx, face in enumerate(ffaces_mats[i]):
                            fvi = []
                            if vertex_color_layer:
                                c1 = vertex_color_layer[fidx].color1
                                c2 = vertex_color_layer[fidx].color2
                                c3 = vertex_color_layer[fidx].color3
                                c4 = vertex_color_layer[fidx].color4

                            for j, vertex in enumerate(face.vertices):
                                v = mesh.vertices[vertex]

                                if vertex_color_layer:
                                    if j == 0:
                                        vert_col = c1
                                    elif j == 1:
                                        vert_col = c2
                                    elif j == 2:
                                        vert_col = c3
                                    elif j == 3:
                                        vert_col = c4

                                if face.use_smooth:
                                    if uv_layer:
                                        if vertex_color_layer:
                                            vert_data = (v.co[:], v.normal[:], uv_layer[face.index].uv[j][:],
                                                         (int(255 * vert_col[0]),
                                                          int(255 * vert_col[1]),
                                                          int(255 * vert_col[2]))[:])
                                        else:
                                            vert_data = (v.co[:], v.normal[:], uv_layer[face.index].uv[j][:])
                                    else:
                                        if vertex_color_layer:
                                            vert_data = (v.co[:], v.normal[:],
                                                         (int(255 * vert_col[0]),
                                                          int(255 * vert_col[1]),
                                                          int(255 * vert_col[2]))[:])
                                        else:
                                            vert_data = (v.co[:], v.normal[:])

                                    if vert_data not in vert_use_vno:
                                        vert_use_vno.add(vert_data)

                                        co_no_uv_vc_cache.append(vert_data)

                                        vert_vno_indices[vert_data] = vert_index
                                        fvi.append(vert_index)

                                        vert_index += 1
                                    else:
                                        fvi.append(vert_vno_indices[vert_data])
                                else:
                                    if uv_layer:
                                        if vertex_color_layer:
                                            vert_data = (v.co[:], face.normal[:], uv_layer[face.index].uv[j][:],
                                                         (int(255 * vert_col[0]),
                                                          int(255 * vert_col[1]),
                                                          int(255 * vert_col[2]))[:])
                                        else:
                                            vert_data = (v.co[:], face.normal[:], uv_layer[face.index].uv[j][:])
                                    else:
                                        if vertex_color_layer:
                                            vert_data = (v.co[:], face.normal[:],
                                                         (int(255 * vert_col[0]),
                                                          int(255 * vert_col[1]),
                                                          int(255 * vert_col[2]))[:])
                                        else:
                                            vert_data = (v.co[:], face.normal[:])

                                    # All face-vert-co-no are unique, we cannot
                                    # cache them
                                    co_no_uv_vc_cache.append(vert_data)
                                    fvi.append(vert_index)
                                    vert_index += 1

                            face_vert_indices[face.index] = fvi

                        del vert_vno_indices
                        del vert_use_vno

                        with open(ply_path, 'wb') as ply:
                            ply.write(b'ply\n')
                            ply.write(b'format binary_little_endian 1.0\n')
                            ply.write(b'comment Created by LuxBlend 2.6 exporter for PBRTv3 - www.luxrender.net\n')

                            # vert_index == the number of actual verts needed
                            ply.write(('element vertex %d\n' % vert_index).encode())
                            ply.write(b'property float x\n')
                            ply.write(b'property float y\n')
                            ply.write(b'property float z\n')

                            ply.write(b'property float nx\n')
                            ply.write(b'property float ny\n')
                            ply.write(b'property float nz\n')

                            if uv_layer:
                                ply.write(b'property float s\n')
                                ply.write(b'property float t\n')

                            if vertex_color_layer:
                                ply.write(b'property uchar red\n')
                                ply.write(b'property uchar green\n')
                                ply.write(b'property uchar blue\n')

                            ply.write(('element face %d\n' % len(ffaces_mats[i])).encode())
                            ply.write(b'property list uchar uint vertex_indices\n')

                            ply.write(b'end_header\n')

                            # dump cached co/no/uv/vc
                            if uv_layer:
                                if vertex_color_layer:
                                    for co, no, uv, vc in co_no_uv_vc_cache:
                                        ply.write(struct.pack('<3f', *co))
                                        ply.write(struct.pack('<3f', *no))
                                        ply.write(struct.pack('<2f', *uv))
                                        ply.write(struct.pack('<3B', *vc))
                                else:
                                    for co, no, uv in co_no_uv_vc_cache:
                                        ply.write(struct.pack('<3f', *co))
                                        ply.write(struct.pack('<3f', *no))
                                        ply.write(struct.pack('<2f', *uv))
                            else:
                                if vertex_color_layer:
                                    for co, no, vc in co_no_uv_vc_cache:
                                        ply.write(struct.pack('<3f', *co))
                                        ply.write(struct.pack('<3f', *no))
                                        ply.write(struct.pack('<3B', *vc))
                                else:
                                    for co, no in co_no_uv_vc_cache:
                                        ply.write(struct.pack('<3f', *co))
                                        ply.write(struct.pack('<3f', *no))

                            # dump face vert indices
                            for face in ffaces_mats[i]:
                                lfvi = len(face_vert_indices[face.index])
                                ply.write(struct.pack('<B', lfvi))
                                ply.write(struct.pack('<%dI' % lfvi, *face_vert_indices[face.index]))

                            del co_no_uv_vc_cache
                            del face_vert_indices

                        print('[Object: %s] Binary PLY file written: %s' % (obj.name, ply_path))
                        return mesh, ply_path
                    else:
                        print('[Object: %s] PLY file %s already exists or object is already a proxy, skipping it' % (
                            obj.name, ply_path))

                except InvalidGeometryException as err:
                    print('[Object: %s] Mesh export failed, skipping this mesh: %s' % (obj.name, err))

            del ffaces_mats
            return mesh, ply_path

        except UnexportableObjectException as err:
            print('[Object: %s] Object export failed, skipping this object: %s' % (obj.name, err))
            return None, None

# Register operator in Blender File -> Export menu
#proxy_menu_func = lambda self, context: self.layout.operator("export.export_pbrtv3_proxy", text="Export PBRTv3 Proxy")
#bpy.types.INFO_MT_file_export.append(proxy_menu_func)