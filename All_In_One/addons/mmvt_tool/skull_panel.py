import bpy
import mathutils
import math
import os.path as op
import numpy as np
import mmvt_utils as mu


def _addon():
    return SkullPanel.addon


def thickness_arrows_update(self, context):
    if bpy.context.scene.cast_ray_source == 'inner':
        mu.show_hide_hierarchy(
            bpy.context.scene.thickness_arrows, 'thickness_arrows_from_inner', also_parent=True, select=False)
    else:
        mu.show_hide_hierarchy(
            bpy.context.scene.thickness_arrows, 'thickness_arrows_from_outer', also_parent=True, select=False)


def cast_ray_source_update(self, context):
    inner_skull = bpy.data.objects.get('inner_skull', None)
    outer_skull = bpy.data.objects.get('outer_skull', None)
    if inner_skull is None or outer_skull is None:
        return
    inner_skull.hide = bpy.context.scene.cast_ray_source != 'inner'
    outer_skull.hide = bpy.context.scene.cast_ray_source == 'inner'


def show_point_arrow_update(self, context):
    if SkullPanel.prev_vertex_arrow is not None:
        SkullPanel.prev_vertex_arrow.hide = not SkullPanel.prev_vertex_arrow.hide


def hide_skull_plane_update(self, context):
    plane = bpy.data.objects.get('skull_plane', None)
    if plane is not None:
        plane.hide = bpy.context.scene.hide_skull_plane


def rotate_skull_plane(d_ang):
    from mathutils import Matrix
    plane = bpy.data.objects.get('skull_plane', None)
    if plane is not None and SkullPanel.plane_dir_vec is not None:
        plane.rotation_mode = 'XYZ'
        vec = SkullPanel.plane_dir_vec
        ang = math.radians(d_ang)
        plane.rotation_euler = (Matrix.Rotation(ang, 3, vec) * plane.rotation_euler.to_matrix()).to_euler()


def import_skull():
    mu.change_layer(_addon().BRAIN_EMPTY_LAYER)
    base_path = op.join(mu.get_user_fol(), 'skull')
    emptys_name = 'Skull'
    layers_array = bpy.context.scene.layers
    _addon().create_empty_if_doesnt_exists(emptys_name, _addon().SKULL_LAYER, layers_array)
    mu.change_layer(_addon().SKULL_LAYER)

    for skull_type in ['inner_skull', 'outer_skull']:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.import_mesh.ply(filepath=op.join(base_path, '{}.ply'.format(skull_type)))
        cur_obj = bpy.context.selected_objects[0]
        cur_obj.select = True
        bpy.ops.object.shade_smooth()
        cur_obj.scale = [0.1] * 3
        cur_obj.hide = False
        cur_obj.name = skull_type
        cur_obj.active_material = bpy.data.materials['Activity_map_mat']
        cur_obj.parent = bpy.data.objects[emptys_name]
        cur_obj.hide_select = True
        cur_obj.data.vertex_colors.new()


def import_plane():
    # plane.dimensions[0] = 5.59
    # plane.dimensions[1] = 4.19
    skull_plane = bpy.data.objects.get('skull_plane', None)
    if skull_plane is not None:
        pass
        # return skull_plane
        # skull_plane.select = True
        # bpy.ops.object.delete()
    else:
        mu.change_layer(_addon().SKULL_LAYER)
        emptys_name = 'Skull'
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.import_mesh.ply(filepath=op.join(mu.get_mmvt_dir(), 'skull_plane.ply'))
        if len(bpy.context.selected_objects) == 0:
            return None
        skull_plane = bpy.context.selected_objects[0]
        skull_plane.select = True
        bpy.ops.object.shade_smooth()
        bpy.ops.mesh.uv_texture_add()
        skull_plane.data.uv_textures['UVMap'].data[0].image = bpy.data.images['neuropace.jpg']
        skull_plane.active_material = bpy.data.materials['Activity_map_mat']
        skull_plane.name = 'skull_plane'
        skull_plane.parent = bpy.data.objects[emptys_name]
    skull_plane.hide_select = True
    skull_plane.location[0] = skull_plane.location[1] = 0
    skull_plane.location[2] = 10
    skull_plane.rotation_mode = 'XYZ'
    skull_plane.rotation_euler[0] = skull_plane.rotation_euler[1] = 0
    skull_plane.rotation_euler[2] = -math.pi / 2

    # align_plane(False)


def plot_distances(from_inner=True):
    # f = mu.Bag(np.load(op.join(mu.get_user_fol(), 'skull', 'intersections.npz')))
    # distances = np.linalg.norm(f.intersections[:, 0] - f.intersections[:, 1], axis=1)
    source_str = 'from_inner' if from_inner else 'from_outer'
    distances = np.load(op.join(mu.get_user_fol(), 'skull', 'ray_casts_{}.npy'.format(source_str)))
    faces_verts = np.load(op.join(mu.get_user_fol(), 'skull', 'faces_verts_{}_skull.npy'.format('inner' if from_inner else 'outer')))
    skull_obj = bpy.data.objects['{}_skull'.format('inner' if from_inner else 'outer')]
    data_max = 25 #np.percentile(distances, 75)
    if _addon().colorbar_values_are_locked():
        data_max, data_min = _addon().get_colorbar_max_min()
    else:
        _addon().set_colorbar_max_min(data_max, 0)
    _addon().set_colormap('hot')
    colors_ratio = 256 / data_max
    _addon().activity_map_obj_coloring(skull_obj, distances, faces_verts, 0, True, 0, colors_ratio)


def plot_distances_from_outer():
    f = mu.Bag(np.load(op.join(mu.get_user_fol(), 'skull', 'intersections_from_outer_skull.npz')))
    distances = np.linalg.norm(f.intersections[:, 0] - f.intersections[:, 1], axis=1)
    faces_verts = np.load(op.join(mu.get_user_fol(), 'skull', 'faces_verts_outer_skull.npy'))
    outer_skull = bpy.data.objects['outer_skull']
    data_max = np.percentile(distances, 75)
    if _addon().colorbar_values_are_locked():
        data_max, data_min = _addon().get_colorbar_max_min()
    else:
        _addon().set_colorbar_max_min(data_max, 0)
    colors_ratio = 256 / data_max
    _addon().activity_map_obj_coloring(outer_skull, distances, faces_verts, 0, True, 0, colors_ratio)


def find_point_thickness(cursor_location=None, skull_type=''):
    source_str = 'from_inner' if bpy.context.scene.cast_ray_source == 'inner' else 'from_outer'
    distances_fname = op.join(mu.get_user_fol(), 'skull', 'ray_casts_{}.npy'.format(source_str))
    # ray_info_fname = op.join(mu.get_user_fol(), 'skull', 'ray_casts_info_{}.pkl'.format(source_str))
    if not op.isfile(distances_fname): #or not op.isfile(ray_info_fname):
        print("Can't find distances file! {}".format(distances_fname))
        return
    if skull_type == '':
        skull_type = '{}_skull'.format(bpy.context.scene.cast_ray_source)
    closest_mesh_name, vertex_ind, vertex_co = \
        _addon().find_closest_vertex_index_and_mesh(cursor_location, objects_names=[skull_type])
    if closest_mesh_name is None:
        return
    _addon().create_slices(pos=vertex_co)
    distances = np.load(distances_fname)
    distance = distances[vertex_ind][0]
    SkullPanel.vertex_skull_thickness = distance
    if not bpy.context.scene.thickness_arrows and bpy.context.scene.show_point_arrow:
        if SkullPanel.prev_vertex_arrow is not None:
            SkullPanel.prev_vertex_arrow.hide = True
        vertex_arrow = bpy.data.objects.get('mt_{}'.format(vertex_ind), None)
        if vertex_arrow.parent.name == 'thickness_arrows_from_outer':
            vertex_arrow = bpy.data.objects.get('mt_{}.001'.format(vertex_ind), None)
        if vertex_arrow is not None:
            vertex_arrow.hide = False
            SkullPanel.prev_vertex_arrow = vertex_arrow
    return closest_mesh_name, vertex_ind, vertex_co


# def fix_children_normals():
#     # c = mu.get_view3d_context()
#     bpy.ops.object.select_all(action='DESELECT')
#
#     for skull_type in ['inner_skull', 'outer_skull']:
#         obj = bpy.context.scene.objects[skull_type]
#         obj.select = True
#         bpy.context.scene.objects.active = obj
#         # go edit mode
#         # bpy.ops.object.mode_set(c, mode='OBJECT')
#         # bpy.ops.object.mode_set(c, mode='EDIT')
#         # select al faces
#         # bpy.ops.mesh.select_all(c, action='SELECT')
#         # recalculate outside normals
#         # bpy.ops.mesh.normals_make_consistent(inside=skull_type == 'outer_skull')
#         select_all_faces(obj.data, skull_type=='outer_skull')
#         # go object mode again
#         # bpy.ops.object.editmode_toggle()


# def select_all_faces(mesh, reverse=False):
#     import bmesh
#     bm = bmesh.new()
#     bm.from_mesh(mesh)
#     bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
#     # if reverse:
#     #     bmesh.ops.reverse_faces(bm, faces=bm.faces)
#     bm.to_mesh(mesh)
#     bm.clear()
#     mesh.update()
#     bm.free()

# https://blender.stackexchange.com/questions/44760/rotate-objects-around-their-origin-along-a-global-axis-scripted-without-bpy-op
def align_plane(to_cursor):
    plane = bpy.data.objects['skull_plane']
    skull = bpy.data.objects['outer_skull']
    if to_cursor:
        plane.location = bpy.context.scene.cursor_location
    _, vertex_ind, vertex_co = find_point_thickness(plane.location, skull_type='outer_skull')
    vert = skull.data.vertices[vertex_ind]
    vert_normal = vert.normal
    dir_vec = mathutils.Vector(vert_normal)
    SkullPanel.plane_dir_vec = dir_vec
    plane.rotation_mode = 'QUATERNION'
    plane.rotation_quaternion = dir_vec.to_track_quat('Z','Y')
    if not to_cursor:
        bpy.context.scene.cursor_location = vertex_co
    plane.location = bpy.context.scene.cursor_location + vert_normal * -0.5 # to point outside

    # for space in mu.get_3d_spaces(only_neuro=True):
    #     space.region_3d.view_matrix = plane.rotation_quaternion.to_matrix().to_4x4()


def get_plane_values(direction_vert=None, plot_arrows=False, plot_directional_arrow=False):
    context = bpy.context
    scene = context.scene
    layers_array = bpy.context.scene.layers
    skull_thickness = np.load(op.join(mu.get_user_fol(), 'skull', 'ray_casts_from_outer.npy'))
    emptys_name = 'plane_arrows'
    _addon().create_empty_if_doesnt_exists(emptys_name, _addon().SKULL_LAYER, layers_array, 'Skull')

    skull = bpy.data.objects['outer_skull']
    plane = bpy.data.objects['skull_plane']

    if direction_vert is None:
        _, vertex_ind, vertex_co = find_point_thickness(plane.location, skull_type='outer_skull')
        direction_vert = skull.data.vertices[vertex_ind]

    omw = plane.matrix_world
    factor = np.linalg.inv(omw)[0, 0]
    omwi = omw.inverted()
    imw = skull.matrix_world
    mat = omwi * imw

    o = mat * direction_vert.co
    n = mat * (direction_vert.co + direction_vert.normal * -1) - o
    hit, loc, norm, index = plane.ray_cast(o, n)
    if hit:
        if plot_directional_arrow:
            draw_empty_arrow(scene, emptys_name, 'direction', omw * loc, omw * o - omw * loc)
        dir_vec_length = abs((omw * loc - omw * o).length * factor)
    else:
        print('No hit from directional vertex!')
        return

    plane_thikness, hits = [], []
    vertices = skull.data.vertices
    for vert_ind, vert in enumerate(vertices):
        o = mat * vert.co
        n = mat * (vert.co + direction_vert.normal * -1) - o
        hit, loc, norm, index = plane.ray_cast(o, n)
        if hit:
            length = abs((omw * loc - omw * o).length * factor)
            if length > dir_vec_length * 2:
                continue
            # else:
            #     print(length, dir_vec_length)
            plane_thikness.append(skull_thickness[vert_ind])
            hits.append((vert_ind, o, loc))

    if len(plane_thikness) > 0:
        plane_thikness = np.array(plane_thikness).squeeze()
        SkullPanel.plane_thickness = (np.min(plane_thikness), np.max(plane_thikness), np.mean(plane_thikness))
        if plot_arrows:
            mu.delete_hierarchy(emptys_name)
            _addon().create_empty_if_doesnt_exists(emptys_name, _addon().SKULL_LAYER, layers_array, 'Skull')
            for vert_ind, hit, o in hits:# [hits[np.argmax(plane_thikness)], hits[np.argmin(plane_thikness)]]:
                draw_empty_arrow(scene, emptys_name, vert_ind, omw * o, omw * hit - omw * o)
    else:
        print('No hits from outer skull to the plane!')


def ray_cast(from_inner=True, create_thickness_arrows=None):
    context = bpy.context
    scene = context.scene
    layers_array = bpy.context.scene.layers
    from_string = 'from_{}'.format('inner' if from_inner else 'outer')
    emptys_name = 'thickness_arrows_{}'.format(from_string)
    if create_thickness_arrows is None:
        create_thickness_arrows = bpy.context.scene.create_thickness_arrows
    show_hit = bpy.data.objects.get(emptys_name, None) is None and create_thickness_arrows

    # check thickness by raycasting from inner object out.
    # select inner and outer obj, make inner active
    inner_obj = bpy.data.objects['inner_skull']
    outer_obj = bpy.data.objects['outer_skull']
    omwi = outer_obj.matrix_world.inverted() if from_inner else inner_obj.matrix_world.inverted()
    output_fname = op.join(mu.get_user_fol(), 'skull', 'ray_casts_{}.npy'.format(from_string))
    output_info_fname = op.join(mu.get_user_fol(), 'skull', 'ray_casts_info_{}.pkl'.format(from_string))
    N = len(inner_obj.data.vertices) if from_inner else len(outer_obj.data.vertices)
    vertices_thickness = np.zeros((N, 1))
    thickness_info = {}

    imw = inner_obj.matrix_world if from_inner else outer_obj.matrix_world
    omw = outer_obj.matrix_world if from_inner else inner_obj.matrix_world
    mat = omwi * imw
    factor = np.linalg.inv(omw)[0, 0]
    ray_obj = outer_obj if from_inner else inner_obj
    hits = []
    vertices = inner_obj.data.vertices if from_inner else outer_obj.data.vertices
    for vert_ind, vert in enumerate(vertices):
        o = mat * vert.co
        n = mat * (vert.co + vert.normal) - o
        # if not from_inner:
        #     n *= -1
        hit, loc, norm, index = ray_obj.ray_cast(o, n)
        if hit:
            # print('{}/{} hit {} on face {}'.format(vert_ind, N, 'outer' if from_inner else 'innner', index))
            hits.append((vert_ind, o, loc))
            thickness = (omw * loc - omw * o).length * factor
        else:
            print('{}/{} no hit!'.format(vert_ind, N))
            thickness = 0
        vertices_thickness[vert_ind] = thickness
        thickness_info[vert_ind] = (hit, np.array(loc), np.array(norm), index)

    np.save(output_fname, vertices_thickness)
    mu.save(thickness_info, output_info_fname)

    if hits:
        avge_thickness = sum((omw * hit - omw * o).length for vert_ind, o, hit in hits) / len(hits)
        print(avge_thickness)
        if show_hit:
            _addon().create_empty_if_doesnt_exists(emptys_name, _addon().BRAIN_EMPTY_LAYER, layers_array, 'Skull')
            for vert_ind, hit, o in hits:
                draw_empty_arrow(scene, emptys_name, vert_ind, omw * o, omw * hit - omw * o, from_inner)


def draw_empty_arrow(scene, empty_name, vert_ind, loc, dir, from_inner=None):
    R = (-dir).to_track_quat('Z', 'X').to_matrix().to_4x4()
    if from_inner is not None:
        arr_prefix = 'from_inner_' if from_inner else 'from_outer_'
    else:
        arr_prefix = ''
    mt = bpy.data.objects.new('{}mt_{}'.format(arr_prefix, vert_ind), None)
    mt.name = 'mt_{}'.format(vert_ind)
    R.translation = loc + dir
    # mt.show_name = True
    mt.matrix_world = R
    mt.empty_draw_type = 'SINGLE_ARROW'
    mt.empty_draw_size = dir.length
    scene.objects.link(mt)
    mt.parent = bpy.data.objects[empty_name]


def skull_draw(self, context):
    layout = self.layout
    source_str = 'from_inner' if bpy.context.scene.cast_ray_source == 'inner' else 'from_outer'
    dists_exist = op.isfile(op.join(mu.get_user_fol(), 'skull', 'ray_casts_{}.npy'.format(source_str)))
    skull_exist = bpy.data.objects.get('inner_skull', None) is not None and \
                  bpy.data.objects.get('outer_skull', None) is not None
    plane = bpy.data.objects.get('skull_plane', None)
    plane_exist = plane is not None

    if not skull_exist:
        layout.operator(ImportSkull.bl_idname, text="Import skull", icon='MATERIAL_DATA')
    # layout.operator(CalcThickness.bl_idname, text="calc thickness", icon='MESH_ICOSPHERE')
    debug = True
    if not dists_exist or debug:
        layout.operator(CalcThickness.bl_idname, text="Calc thickness", icon='MESH_ICOSPHERE')
        layout.prop(context.scene, 'create_thickness_arrows', text='Create thickness arrows')
    layout.operator(PlotThickness.bl_idname, text="Plot thickness", icon='GROUP_VCOL')
    text = 'Import plane' if not plane_exist else 'Place plane over the head'
    layout.operator(ImportPlane.bl_idname, text=text, icon='TEXTURE')
    if plane_exist:
        layout.operator(AlignPlane.bl_idname, text="Align plane", icon='LATTICE_DATA')
        layout.operator(CalcPlaneStat.bl_idname, text="Calc plane stat", icon='PARTICLE_DATA')
        if SkullPanel.plane_dir_vec is not None:
            row = layout.row(align=True)
            row.operator(RotateSkullPlaneNeg.bl_idname, text="", icon='PREV_KEYFRAME')
            row.prop(context.scene, 'skull_plane_angle', text='Angle delta')
            row.operator(RotateSkullPlanePos.bl_idname, text="", icon='NEXT_KEYFRAME')
        layout.prop(context.scene, 'align_plane_to_cursor', text='Align to cursor')
        layout.prop(context.scene, 'hide_skull_plane', text='Hide plane')
    if SkullPanel.plane_thickness is not None:
        box = layout.box()
        col = box.column()
        mu.add_box_line(col, 'Min thickness', '{:.2f}mm'.format(SkullPanel.plane_thickness[0]), 0.8)
        mu.add_box_line(col, 'Max thickness', '{:.2f}mm'.format(SkullPanel.plane_thickness[1]), 0.8)
        mu.add_box_line(col, 'Mean thickness', '{:.2f}mm'.format(SkullPanel.plane_thickness[2]), 0.8)

    layout.prop(context.scene, 'cast_ray_source', expand=True)
    # layout.operator(FindPointThickness.bl_idname, text="Calc point thickness", icon='MESH_DATA')
    if SkullPanel.vertex_skull_thickness > 0:
        layout.label(text='Thickness: {:.3f}'.format(SkullPanel.vertex_skull_thickness))

    from_string = 'from_{}'.format('inner' if bpy.context.scene.cast_ray_source else 'outer')
    arrows_empty_name = 'thickness_arrows_{}'.format(from_string)
    if bpy.data.objects.get(arrows_empty_name):
        layout.prop(context.scene, 'show_point_arrow', text='Show point thickness vector')
        layout.prop(context.scene, 'thickness_arrows', text='Thickness arrows')


class ImportSkull(bpy.types.Operator):
    bl_idname = "mmvt.import_skull"
    bl_label = "Import skull"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        import_skull()
        return {'PASS_THROUGH'}


class ImportPlane(bpy.types.Operator):
    bl_idname = "mmvt.import_plane"
    bl_label = "Import plane"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        import_plane()
        return {'PASS_THROUGH'}


class CalcThickness(bpy.types.Operator):
    bl_idname = "mmvt.calc_thickness"
    bl_label = "calc_thickness"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        # fix_children_normals()
        for inner in [True, False]:
            ray_cast(inner, bpy.context.scene.create_thickness_arrows) # and inner and )
        return {'PASS_THROUGH'}


class PlotThickness(bpy.types.Operator):
    bl_idname = "mmvt.plot_thickness"
    bl_label = "plot_thickness"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        if not _addon().colorbar_values_are_locked():
            _addon().set_colorbar_title('Skull thickness (mm)')
        for inner in [True, False]:
            plot_distances(inner) #bpy.context.scene.cast_ray_source == 'inner')
        return {'PASS_THROUGH'}


class FindPointThickness(bpy.types.Operator):
    bl_idname = "mmvt.find_point_thickness"
    bl_label = "find_point_thickness"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        find_point_thickness()
        return {'PASS_THROUGH'}


class AlignPlane(bpy.types.Operator):
    bl_idname = "mmvt.align_plane"
    bl_label = "align_plane"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        align_plane(bpy.context.scene.align_plane_to_cursor)
        return {'PASS_THROUGH'}


class RotateSkullPlaneNeg(bpy.types.Operator):
    bl_idname = "mmvt.rotate_skull_plane_neg"
    bl_label = "rotate_skull_plane_neg"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        rotate_skull_plane(-bpy.context.scene.skull_plane_angle)
        get_plane_values()
        return {'PASS_THROUGH'}


class RotateSkullPlanePos(bpy.types.Operator):
    bl_idname = "mmvt.rotate_skull_plane_pos"
    bl_label = "rotate_skull_plane_pos"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        rotate_skull_plane(bpy.context.scene.skull_plane_angle)
        get_plane_values()
        return {'PASS_THROUGH'}


class CalcPlaneStat(bpy.types.Operator):
    bl_idname = "mmvt.calc_plane_stat"
    bl_label = "calc_plane_stat"
    bl_options = {"UNDO"}

    def invoke(self, context, event=None):
        get_plane_values()
        return {'PASS_THROUGH'}


bpy.types.Scene.thickness_arrows = bpy.props.BoolProperty(default=False, update=thickness_arrows_update)
bpy.types.Scene.show_point_arrow = bpy.props.BoolProperty(default=False, update=show_point_arrow_update)
bpy.types.Scene.cast_ray_source = bpy.props.EnumProperty(items=[('inner', 'inner', '', 0), ('outer', 'outer', '', 1)],
                                                         update=cast_ray_source_update)
bpy.types.Scene.create_thickness_arrows = bpy.props.BoolProperty(default=False)
bpy.types.Scene.align_plane_to_cursor = bpy.props.BoolProperty(default=False)
bpy.types.Scene.hide_skull_plane = bpy.props.BoolProperty(default=False, update=hide_skull_plane_update)
bpy.types.Scene.skull_plane_angle = bpy.props.FloatProperty(default=5, min=1, max=45)


class SkullPanel(bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "skull"
    bl_label = "Skull"
    addon = None
    init = False
    vertex_skull_thickness = 0
    prev_vertex_arrow = None
    plane_thickness = None
    plane_dir_vec = None

    def draw(self, context):
        if SkullPanel.init:
            skull_draw(self, context)


def init(addon):
    SkullPanel.addon = addon
    user_fol = mu.get_user_fol()
    skull_ply_files_exist = op.isfile(op.join(user_fol, 'skull', 'inner_skull.ply')) and \
                            op.isfile(op.join(user_fol, 'skull', 'outer_skull.ply'))
    skull_objs_exist = bpy.data.objects.get('inner_skull', None) is not None and \
                       bpy.data.objects.get('inner_skull', None) is not None
    if not skull_ply_files_exist and not skull_objs_exist:
        return
    for layer_ind in range(len(bpy.context.scene.layers)):
        bpy.context.scene.layers[layer_ind] = layer_ind == _addon().SKULL_LAYER
    plane = bpy.data.objects.get('skull_plane', None)
    if plane is not None:
        import_plane()
    bpy.context.scene.align_plane_to_cursor = False
    bpy.context.scene.skull_plane_angle = 5

    register()
    SkullPanel.init = True
    bpy.context.scene.thickness_arrows = False
    bpy.context.scene.show_point_arrow = False
    bpy.context.scene.hide_skull_plane = False
    # bpy.data.screens['Neuro'].areas[1].spaces[0].region_3d

def register():
    try:
        unregister()
        bpy.utils.register_class(SkullPanel)
        bpy.utils.register_class(ImportSkull)
        bpy.utils.register_class(ImportPlane)
        bpy.utils.register_class(CalcThickness)
        bpy.utils.register_class(PlotThickness)
        bpy.utils.register_class(FindPointThickness)
        bpy.utils.register_class(AlignPlane)
        bpy.utils.register_class(CalcPlaneStat)
        bpy.utils.register_class(RotateSkullPlaneNeg)
        bpy.utils.register_class(RotateSkullPlanePos)
    except:
        print("Can't register Skull Panel!")


def unregister():
    try:
        bpy.utils.unregister_class(SkullPanel)
        bpy.utils.unregister_class(ImportSkull)
        bpy.utils.unregister_class(ImportPlane)
        bpy.utils.unregister_class(CalcThickness)
        bpy.utils.unregister_class(PlotThickness)
        bpy.utils.unregister_class(FindPointThickness)
        bpy.utils.unregister_class(AlignPlane)
        bpy.utils.unregister_class(CalcPlaneStat)
        bpy.utils.unregister_class(RotateSkullPlaneNeg)
        bpy.utils.unregister_class(RotateSkullPlanePos)
    except:
        pass
