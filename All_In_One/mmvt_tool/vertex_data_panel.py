import bpy
import mmvt_utils as mu
import mathutils
import numpy as np
import os.path as op
import glob


def _addon():
    return DataInVertMakerPanel.addon


def set_vertex_data(val):
    val_str = _addon().PERC_FORMATS[_addon().get_colorbar_prec() + 1].format(val)
    DataInVertMakerPanel.data_in_cursor = val_str if val != '' else ''


def get_vertex_data():
    return DataInVertMakerPanel.data_in_cursor


def snap_ray():
    # https://blender.stackexchange.com/questions/92720/snappping-the-3d-cursor-to-the-surface-and-find-the-surfaces-face-it-was-snappe
    from mathutils import Vector
    context = bpy.context
    screen = context.screen
    scene = context.scene
    areas3d = [a for a in screen.areas if a.type == 'VIEW_3D']
    for a in areas3d:
        r3d = a.spaces.active.region_3d
        vm = r3d.view_matrix.transposed().to_3x3().to_4x4()
        norm = vm * Vector((0, 0, 1))
        norm.normalize()
        try:
            ray = scene.ray_cast(scene.cursor_location, norm)
        except:
            return None, None, None
        hit, loc, norm, face, obj, matrix = ray
        if hit:
            if obj.name in ['inflated_rh', 'inflated_lh']:
                me = obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
                vertex_ind = obj.data.polygons[face].vertices[0]
                if vertex_ind >= len(me.vertices):
                    print('snap_ray: vertex_ind not in me.vertices!')
                    return None, None, None
                vertex_co = me.vertices[vertex_ind].co * obj.matrix_world
                bpy.data.meshes.remove(me)
                # print("hit object", obj, "on face:", face)
                # print([v for v in obj.data.polygons[face].vertices])
                # print([me.vertices[v].co * obj.matrix_world for v in obj.data.polygons[face].vertices])
                distance = (loc - scene.cursor_location).length
                # print('cast ray dist: {}'.format(distance))
                return obj.name, vertex_ind, vertex_co
            else:
                print('snap ray hit {}'.format(obj.name))
    return None, None, None


def find_closest_vertices(pos, vertices_indices, obj_name, use_shape_keys=True):
    obj = bpy.data.objects[obj_name]
    co_find = pos * obj.matrix_world.inverted()
    mesh = obj.data
    size = len(mesh.vertices)
    kd = mathutils.kdtree.KDTree(size)

    if use_shape_keys:
        me = obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
        for i in vertices_indices:
            try:
                kd.insert(me.vertices[i].co, i)
            except:
                print('find_closest_vertices: exception in the use_shape_keys loop')
                break
        bpy.data.meshes.remove(me)
    else:
        for i in vertices_indices:
            kd.insert(mesh.vertices[i].co, i)

    kd.balance()
    co, index, dist = kd.find(co_find)
    # print('closest vert {} {}'.format(index, co))
    # print('dist from {} to closest vert: {}'.format(co_find, dist))
    return index, co


# @mu.timeit
def find_closest_vertex_index_and_mesh(pos=None, hemis=None, use_shape_keys=False, objects_names=None):
    # If pos is None, take the cursor's pos

    # 3d cursor relative to the object data
    # print('cursor at:' + str(bpy.context.scene.cursor_location))
    # co_find = context.scene.cursor_location * obj.matrix_world.inverted()
    distances, names, vertices_idx, vertices_co = [], [], [], []

    if pos is None and hemis is None and use_shape_keys is True and \
            (objects_names is None or objects_names == mu.INF_HEMIS):
        closest_mesh_name, vertex_ind, vertex_co = snap_ray()
        if closest_mesh_name is not None:
            return closest_mesh_name, vertex_ind, vertex_co
        # else:
        #     print('snap_ray didnt work...')
    if objects_names is not None:
        hemis = objects_names
    elif hemis is None:
        # hemis = mu.HEMIS if _addon().is_pial() else mu.INF_HEMIS
        hemis = mu.INF_HEMIS
    if pos is None:
        pos = bpy.context.scene.cursor_location
    else:
        pos = mathutils.Vector(pos)
    for obj_name in hemis:
        if use_shape_keys and obj_name in ['rh', 'lh']:
            obj_name = 'inflated_{}'.format(obj_name)
        obj = bpy.data.objects[obj_name]
        co_find = pos * obj.matrix_world.inverted()
        mesh = obj.data
        size = len(mesh.vertices)
        kd = mathutils.kdtree.KDTree(size)

        if use_shape_keys:
            me = obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
            for i, v in enumerate(mesh.vertices):
                try:
                    kd.insert(me.vertices[i].co, i)
                except:
                    # in flat map not all the vertices exist
                    # todo handle the case where the brain is sliced and the user click the plane with the image.
                    print('find_closest_vertex_index_and_mesh: exception in the use_shape_keys loop')
                    break
            bpy.data.meshes.remove(me)
        else:
            for i, v in enumerate(mesh.vertices):
                kd.insert(v.co, i)

        kd.balance()
        # print(obj.name)
        for (co, index, dist) in kd.find_n(co_find, 1):
            # print('cursor at {} ,vertex {}, index {}, dist {}'.format(str(co_find), str(co), str(index), str(dist)))
            distances.append(dist)
            names.append(obj.name)
            vertices_idx.append(index)
            vertices_co.append(co)

    distances = np.array(distances)
    closest_mesh_name = names[np.argmin(distances)]
    # print('closest_mesh =' + str(closest_mesh_name))
    vertex_ind = vertices_idx[np.argmin(distances)]
    # print('vertex_ind = ' + str(vertex_ind))
    vertex_co = vertices_co[np.argmin(distances)] * obj.matrix_world
    distance = np.min(distances)
    # print('vertex_co', vertex_co)
    # print(closest_mesh_name, bpy.data.objects[closest_mesh_name].data.vertices[vertex_ind].co)
    # print(closest_mesh_name.replace('inflated_', ''), bpy.data.objects[closest_mesh_name.replace('inflated_', '')].data.vertices[vertex_ind].co)
    return closest_mesh_name, vertex_ind, vertex_co #, distance


class ClearVertexData(bpy.types.Operator):
    bl_idname = "mmvt.vertex_data_clear"
    bl_label = "vertex data clear"
    bl_options = {"UNDO"}

    @staticmethod
    def invoke(self, context, event=None):
        for obj in bpy.data.objects:
            if obj.name.startswith('Activity_in_vertex'):
                obj.select = True
                # bpy.context.scene.objects.unlink(obj)
                bpy.data.objects.remove(obj)

        return {"FINISHED"}


class CreateVertexData(bpy.types.Operator):
    bl_idname = "mmvt.vertex_data_create"
    bl_label = "vertex data create"
    bl_options = {"UNDO"}

    @staticmethod
    def create_empty_in_vertex_location(vertex_location):
        mu.create_empty_in_vertex(vertex_location, 'Activity_in_vertex', DataInVertMakerPanel.addon.ACTIVITY_LAYER)


    @staticmethod
    def keyframe_empty(self, empty_name, closest_mesh_name, vertex_ind, data_path):
        obj = bpy.data.objects[empty_name]
        number_of_time_points = len(glob.glob(op.join(data_path, 'activity_map_' + closest_mesh_name + '2', '', ) + '*.npy'))
        mu.insert_keyframe_to_custom_prop(obj, 'data', 0, 0)
        mu.insert_keyframe_to_custom_prop(obj, 'data', 0, number_of_time_points + 1)
        for ii in range(number_of_time_points):
            # print(ii)
            frame_str = str(ii)
            f = np.load(op.join(data_path, 'activity_map_' + closest_mesh_name + '2', 't' + frame_str + '.npy'))
            mu.insert_keyframe_to_custom_prop(obj, 'data', float(f[vertex_ind, 0]), ii + 1)

        fcurves = bpy.data.objects[empty_name].animation_data.action.fcurves[0]
        mod = fcurves.modifiers.new(type='LIMITS')

    def keyframe_empty_test(self, empty_name, closest_mesh_name, vertex_ind, data_path):
        obj = bpy.data.objects[empty_name]
        lookup = np.load(op.join(data_path, 'activity_map_' + closest_mesh_name + '_verts_lookup.npy'))
        file_num_str = str(int(lookup[vertex_ind, 0]))
        line_num = int(lookup[vertex_ind, 1])
        data_file = np.load(
            op.join(data_path, 'activity_map_' + closest_mesh_name + '_verts', file_num_str + '.npy'))
        data = data_file[line_num, :].squeeze()

        number_of_time_points = len(data)
        mu.insert_keyframe_to_custom_prop(obj, 'data', 0, 0)
        mu.insert_keyframe_to_custom_prop(obj, 'data', 0, number_of_time_points + 1)
        for ii in range(number_of_time_points):
            # print(ii)
            frame_str = str(ii)
            mu.insert_keyframe_to_custom_prop(obj, 'data', float(data[ii]), ii + 1)
            # insert_keyframe_to_custom_prop(obj,'data',0,ii+1)
        fcurves = bpy.data.objects[empty_name].animation_data.action.fcurves[0]
        mod = fcurves.modifiers.new(type='LIMITS')

    def invoke(self, context, event=None):
        closest_mesh_name, vertex_ind, vertex_co = find_closest_vertex_index_and_mesh()
        print(vertex_co)
        self.create_empty_in_vertex_location(vertex_co)
        data_path = mu.get_user_fol()
        self.keyframe_empty_test('Activity_in_vertex', closest_mesh_name, vertex_ind, data_path)
        return {"FINISHED"}


class DataInVertMakerPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "mmvt"
    bl_label = "Data in vertex"
    addon = None
    init = False
    data_in_cursor = None
    activity_maps_exist = False

    def draw(self, context):
        layout = self.layout
        if DataInVertMakerPanel.activity_maps_exist:
            layout.operator(CreateVertexData.bl_idname, text="Get data in vertex", icon='ROTATE')
            layout.operator(ClearVertexData.bl_idname, text="Clear", icon='PANEL_CLOSE')
        if DataInVertMakerPanel.data_in_cursor is not None:
            layout.label(text='Cursor value: {}'.format(DataInVertMakerPanel.data_in_cursor))
        # layout.operator(, text="Get data in vertex", icon='ROTATE')


def init(addon):
    DataInVertMakerPanel.addon = addon
    lookup_files = glob.glob(op.join(mu.get_user_fol(), 'activity_map_*_verts_lookup.npy'))
    if len(lookup_files) == 0:
        print('No lookup files for vertex_data_panel')
        DataInVertMakerPanel.init = False
    DataInVertMakerPanel.activity_maps_exist = \
        op.isdir(op.join(mu.get_user_fol(), 'activity_map_rh')) and \
        op.isdir(op.join(mu.get_user_fol(), 'activity_map_lh'))
    DataInVertMakerPanel.init = True
    register()


def register():
    try:
        unregister()
        bpy.utils.register_class(DataInVertMakerPanel)
        bpy.utils.register_class(CreateVertexData)
        bpy.utils.register_class(ClearVertexData)
        # print('Vertex Panel was registered!')
    except:
        print("Can't register Vertex Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(DataInVertMakerPanel)
        bpy.utils.unregister_class(CreateVertexData)
        bpy.utils.unregister_class(ClearVertexData)
    except:
        pass