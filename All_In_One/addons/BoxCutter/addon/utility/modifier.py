import bpy
import bmesh

from . import addon, object, mesh


def shape_bool(ot, obj):
    bc = bpy.context.window_manager.bc

    for mod in reversed(obj.modifiers):
        if mod.type == 'BOOLEAN' and mod.object == bc.shape:

            return mod

    return None


def update(ot, context):
    bc = context.window_manager.bc
    targets = ot.datablock['targets']
    overrides = ot.datablock['overrides']

    if not overrides:
        ot.datablock['overrides'] = [obj.data for obj in targets]

    for pair in zip(targets, overrides):
        obj = pair[0]
        override = pair[1]

        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT')

        old_data = obj.data

        if obj.data != override:
            obj.data = override
        else:
            obj.data = obj.data.copy()

        if old_data not in ot.datablock['overrides']:
            bpy.data.meshes.remove(old_data)

        new = obj.copy()
        coords = [vert.co for vert in new.data.vertices]

        for mod in new.modifiers:
            if mod.type == 'BOOLEAN':
                if mod.object == bc.shape or mod.object in ot.datablock['slices']:
                    new.modifiers.remove(mod)

        for mod in obj.modifiers:
            if mod.type == 'BOOLEAN':
                if mod.object != bc.shape or mod.object in ot.datablock['slices']:
                    obj.modifiers.remove(mod)
            else:
                obj.modifiers.remove(mod)

        context.scene.update()

        obj.data = obj.to_mesh(context.depsgraph, apply_modifiers=True)

        for mod in new.modifiers:
            duplicate(obj, mod)

        bpy.data.objects.remove(new)

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        new_verts = []
        for v in bm.verts:
            if v.co not in coords:
                v.select_set(True)
                new_verts.append(v)

        bm.select_flush(True)

        bm.edges.ensure_lookup_table()
        bw = bm.edges.layers.bevel_weight.verify()
        for e in bm.edges:
            if False not in [v in new_verts for v in e.verts]:
                e[bw] = 0

        bm.to_mesh(obj.data)
        bm.free()

    del targets
    del overrides

    bpy.ops.object.mode_set(mode='EDIT')


def display(ot):
    return bc.lattice.dimensions[2] > 0.01


def sort(ot, obj, force=False):
    preference = addon.preference()
    bc = bpy.context.window_manager.bc

    if preference.behavior.sort_modifiers or force:

        mod_types = []
        if not obj.bc.shape:
            if preference.behavior.sort_bevel and not preference.behavior.sort_bevel_last: mod_types.append('BEVEL')
        if preference.behavior.sort_array: mod_types.append('ARRAY')
        if preference.behavior.sort_mirror: mod_types.append('MIRROR')
        if preference.behavior.sort_solidify: mod_types.append('SOLIDIFY')
        if preference.behavior.sort_weighted_normal: mod_types.append('WEIGHTED_NORMAL')
        if preference.behavior.sort_simple_deform: mod_types.append('SIMPLE_DEFORM')
        if preference.behavior.sort_triangulate: mod_types.append('TRIANGULATE')

        new = obj.copy()

        modifiers = []

        if not obj.bc.shape:
            bevel = [mod for mod in new.modifiers if mod.type == 'BEVEL' and mod.limit_method != 'VGROUP' and not mod.use_only_vertices]
        else:
            bevel = []

        if len(bevel):
            bevel = bevel[-1]

        else:
            bevel = None

        weighted = [mod for mod in new.modifiers if mod.type == 'WEIGHTED_NORMAL']

        if len(weighted):
            weighted = weighted[-1] if bevel else None

        else:
            weighted = None

        sort_bevel = preference.behavior.sort_bevel
        sort_last_bevel = preference.behavior.sort_bevel_last

        for mod in new.modifiers:
            sort_last = mod == bevel and sort_bevel and sort_last_bevel
            sort_last_weight = mod == weighted and sort_bevel and sort_last_bevel

            bgroup = mod.type == 'BEVEL' and mod.limit_method == 'VGROUP' and not bc.running
            only_verts = mod.type == 'BEVEL' and mod.use_only_vertices

            if sort_last or sort_last_weight:
                continue

            if mod.type not in mod_types or bgroup or only_verts:
                modifiers.append(mod)

        for mod in new.modifiers:
            if mod not in modifiers and mod.type == 'BOOLEAN':
                modifiers.append(mod)

        for mod in new.modifiers:
            if mod not in modifiers:
                modifiers.append(mod)

        obj.modifiers.clear()

        for mod in modifiers:
            duplicate(obj, mod)

        del modifiers

        bpy.data.objects.remove(new)

        del new


#TOOD: permanent hide modifier behavior for keeping
def apply(obj=None, mod=None, visible=False, modifiers=[], exclude=[], type='NONE', kitops=False):
    bc = bpy.context.window_manager.bc

    mode = bpy.context.workspace.tools_mode
    mods = []

    if mod:
        mods.append(mod)

    else:
        for m in obj.modifiers:
            if m not in exclude:
                if m in modifiers:

                    if visible:
                        if m.show_viewport:
                            if mode == 'EDIT_MESH':
                                if m.show_in_editmode and m.show_on_cage:
                                    if type == 'NONE' or m.type == type:
                                        mods.append(m)
                                        continue

                            elif type == 'NONE' or m.type == type:
                                mods.append(m)
                                continue

                    elif type == 'NONE' or m.type == type:
                        mods.append(m)
                        continue

                if type == 'NONE' or m.type == type:
                    mods.append(m)
                    continue

    if mods:
        if not kitops:
            for m in mods:
                if m.type == 'BOOLEAN' and m.object and hasattr(m.object, 'kitops') and m.object.kitops.insert:
                    mods.remove(m)

        names = [mod.name for mod in mods]

        new = obj.copy()

        for mod in new.modifiers:
            if mod.name in names:
                new.modifiers.remove(mod)

        old_data = obj.data

        if old_data.users > 1:
            old_data = old_data.copy()

        old_data.bc.removeable = True

        for mod in obj.modifiers:
            if mod.name not in names:
                obj.modifiers.remove(mod)

        bpy.context.scene.update()

        obj.data = obj.to_mesh(bpy.context.depsgraph, apply_modifiers=True)
        obj.data.validate()
        obj.data.name = old_data.name

        obj.modifiers.clear()

        for mod in new.modifiers:
            duplicate(obj, mod)

        bpy.data.objects.remove(new)

        del new
        del old_data

    del mods


def clean(ot, modifier_only=False):
    for obj in ot.datablock['targets']:
        if shape_bool(ot, obj):
            obj.modifiers.remove(shape_bool(ot, obj))

    if not modifier_only:
        for obj in ot.datablock['slices']:
            bpy.data.meshes.remove(obj.data)

        ot.datablock['slices'] = list()


# TODO: move array here
class create:


    def __init__(self, ot):
        self.boolean(ot)


    @staticmethod
    def boolean(ot, show=False):
        preference = addon.preference()
        bc = bpy.context.window_manager.bc

        if shape_bool(ot, ot.datablock['targets'][0]):
            for obj in ot.datablock['targets']:
                if shape_bool(ot, obj):
                    obj.modifiers.remove(shape_bool(ot, obj))

            for obj in ot.datablock['slices']:
                bpy.data.meshes.remove(obj.data)

            ot.datablock['slices'] = []

        bc.shape.display_type = 'WIRE'
        bc.shape.hide_set(True)

        for obj in ot.datablock['targets']:
            if not ot.active_only or obj == bpy.context.view_layer.objects.active:
                mod = obj.modifiers.new(name='Boolean', type='BOOLEAN')
                mod.show_viewport = show
                mod.show_expanded = False
                mod.object = bc.shape
                mod.operation = 'DIFFERENCE' if ot.mode != 'JOIN' else 'UNION'

                sort(ot, obj)

                if ot.mode in {'INSET', 'SLICE'}:
                    new = obj.copy()
                    new.data = obj.data.copy()

                    if preference.behavior.apply_slices:
                        apply(new, exclude=[shape_bool(ot, new)], type='BOOLEAN')

                    wm = bpy.context.window_manager
                    hops = wm.Hard_Ops_material_options if hasattr(wm, 'Hard_Ops_material_options') else False
                    if hops and hops.active_material:
                        for slot in new.material_slots:
                            if slot.link != 'DATA':
                                slot.link == 'DATA'

                        new.data.materials.clear()
                        mat = bpy.data.materials[hops.active_material]
                        new.data.materials.append(mat)

                    new.name = ot.mode.title()
                    new.data.name = ot.mode.title()

                    if ot.mode == 'SLICE':
                        if obj.users_collection:
                            for collection in obj.users_collection:
                                collection.objects.link(new)
                        else:
                            bpy.context.scene.collection.objects.link(new)

                        bc.slice = new

                    else:
                        bc.collection.objects.link(new)
                        new.bc.inset = True
                        new.hide_set(True)

                    shape_bool(ot, new).operation = 'INTERSECT'

                    if addon.preference().behavior.apply_slices or ot.mode == 'INSET':
                        if ot.mode == 'INSET':
                            for index, mod in enumerate(new.modifiers):
                                if mod.type == 'BEVEL':
                                    if index != 0:
                                        new.modifiers.remove(mod)

                        apply(obj=new, exclude=[shape_bool(ot, new)], type='BOOLEAN' if ot.mode == 'SLICE' else '')

                    if ot.mode == 'INSET':
                        new.display_type = 'WIRE'
                        new.cycles_visibility.camera = False
                        new.cycles_visibility.diffuse = False
                        new.cycles_visibility.glossy = False
                        new.cycles_visibility.transmission = False
                        new.cycles_visibility.scatter = False
                        new.cycles_visibility.shadow = False
                        new.cycles.is_shadow_catcher = False
                        new.cycles.is_holdout = False

                        solidify = new.modifiers.new(name='Solidify', type='SOLIDIFY')
                        solidify.thickness = ot.last['thickness']
                        solidify.offset = 0
                        solidify.show_on_cage = True
                        solidify.use_even_offset = True
                        solidify.use_quality_normals = True

                        new.modifiers.remove(shape_bool(ot, new))

                        mod = new.modifiers.new(name='Boolean', type='BOOLEAN')
                        mod.show_viewport = show
                        mod.show_expanded = False
                        mod.object = bc.shape
                        mod.operation = 'INTERSECT'

                        for mod in bc.shape.modifiers:
                            if mod.type == 'SOLIDIFY':
                                bc.shape.modifiers.remove(mod)

                        bool = None
                        for mod in reversed(obj.modifiers):
                            if mod.type == 'BOOLEAN' and mod.object == new:
                                bool = mod
                                break

                        if not bool:
                            mod = obj.modifiers.new(name='Boolean', type='BOOLEAN')
                            mod.show_viewport = show
                            mod.show_expanded = False
                            mod.object = new
                            mod.operation = 'DIFFERENCE'

                            if hasattr(wm, 'Hard_Ops_material_options'):
                                new.hops.status = 'BOOLSHAPE'

                            sort(ot, obj)

                        bc.inset = new

                    ot.datablock['slices'].append(new)


class duplicate:


    def __init__(self, obj, mod):
        self.modifier = obj.modifiers.new(name=mod.name, type=mod.type)
        self.modifier.show_viewport = mod.show_viewport
        self.modifier.show_render = mod.show_render
        self.modifier.show_expanded = mod.show_expanded
        self.modifier.show_in_editmode = mod.show_in_editmode
        self.modifier.show_on_cage = mod.show_on_cage
        getattr(self, mod.type)(mod)


    def ARMATURE(self, mod):
        self.modifier.object = mod.object
        self.modifier.use_deform_preserve_volume = mod.use_deform_preserve_volume
        self.modifier.use_vertex_groups = mod.use_vertex_groups
        self.modifier.use_bone_envelopes = mod.use_bone_envelopes
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.invert_vertex_group = mod.invert_vertex_group
        self.modifier.use_multi_modifier = mod.use_multi_modifier


    def ARRAY(self, mod):
        self.modifier.fit_type = mod.fit_type
        self.modifier.count = mod.count
        self.modifier.fit_length = mod.fit_length
        self.modifier.curve = mod.curve
        self.modifier.use_constant_offset = mod.use_constant_offset
        self.modifier.constant_offset_displace = mod.constant_offset_displace
        self.modifier.use_merge_vertices = mod.use_merge_vertices
        self.modifier.use_merge_vertices_cap = mod.use_merge_vertices_cap
        self.modifier.merge_threshold = mod.merge_threshold
        self.modifier.use_relative_offset = mod.use_relative_offset
        self.modifier.relative_offset_displace = mod.relative_offset_displace
        self.modifier.use_object_offset = mod.use_object_offset
        self.modifier.offset_object = mod.offset_object
        self.modifier.offset_u = mod.offset_u
        self.modifier.offset_v = mod.offset_v
        self.modifier.start_cap = mod.start_cap
        self.modifier.end_cap = mod.end_cap


    def BEVEL(self, mod):
        self.modifier.width = mod.width
        self.modifier.segments = mod.segments
        self.modifier.profile = mod.profile
        self.modifier.material = mod.material
        self.modifier.use_only_vertices = mod.use_only_vertices
        self.modifier.use_clamp_overlap = mod.use_clamp_overlap
        self.modifier.loop_slide = mod.loop_slide
        self.modifier.mark_seam = mod.mark_seam
        self.modifier.mark_sharp = mod.mark_sharp
        self.modifier.harden_normals = mod.harden_normals
        self.modifier.limit_method = mod.limit_method
        self.modifier.angle_limit = mod.angle_limit
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.offset_type = mod.offset_type
        self.modifier.face_strength_mode = mod.face_strength_mode
        self.modifier.show_in_editmode = mod.show_in_editmode
        self.modifier.miter_outer = mod.miter_outer
        self.modifier.miter_inner = mod.miter_inner
        self.modifier.spread = mod.spread


    def BOOLEAN(self, mod):
        self.modifier.operation = mod.operation
        self.modifier.object = mod.object
        self.modifier.double_threshold = mod.double_threshold

        # if bpy.app.debug:
        #     self.modifier.debug_options = mod.debug_options


    def BUILD(self, mod):
        self.modifier.frame_start = mod.frame_start
        self.modifier.frame_duration = mod.frame_duration
        self.modifier.use_reverse = mod.use_reverse
        self.modifier.use_random_order = mod.use_random_order
        self.modifier.seed = mod.seed


    def MESH_CACHE(self, mod):
        self.modifier.cache_format = mod.cache_format
        self.modifier.filepath = mod.filepath
        self.modifier.sub_object = mod.sub_object
        self.modifier.factor = mod.factor
        self.modifier.deform_mode = mod.deform_mode
        self.modifier.interpolation = mod.interpolation
        self.modifier.time_mode = mod.time_mode
        self.modifier.play_mode = mod.play_mode
        self.modifier.frame_start = mod.frame_start
        self.modifier.frame_scale = mod.frame_scale
        self.modifier.eval_frame = mod.eval_frame
        self.modifier.eval_time = mod.eval_time
        self.modifier.eval_factor = mod.eval_factor
        self.modifier.forward_axis = mod.forward_axis
        self.modifier.up_axis = mod.up_axis
        self.modifier.flip_axis = mod.flip_axis


    def MESH_SEQUENCE_CACHE(self, mod):
        self.modifier.cache_file = mod.cache_file
        self.modifier.object_path = mod.object_path
        self.modifier.read_data = mod.read_data


    def CAST(self, mod):
        self.modifier.cast_type = mod.cast_type
        self.modifier.use_x = mod.use_x
        self.modifier.use_y = mod.use_y
        self.modifier.use_z = mod.use_z
        self.modifier.factor = mod.factor
        self.modifier.radius = mod.radius
        self.modifier.size = mod.size
        self.modifier.use_radius_as_size = mod.use_radius_as_size
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.object = mod.object
        self.modifier.use_transform = mod.use_transform


    def CLOTH(self, mod):
        pass


    def COLLISION(self, mod):
        pass


    def CURVE(self, mod):
        self.modifier.object = mod.object
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.deform_axis = mod.deform_axis


    def DECIMATE(self, mod):
        self.modifier.decimate_type = mod.decimate_type
        self.modifier.ratio = mod.ratio
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.invert_vertex_group = mod.invert_vertex_group
        self.modifier.vertex_group_factor = mod.vertex_group_factor
        self.modifier.use_collapse_triangulate = mod.use_collapse_triangulate
        self.modifier.use_symmetry = mod.use_symmetry
        self.modifier.symmetry_axis = mod.symmetry_axis
        self.modifier.iterations = mod.iterations
        self.modifier.angle_limit = mod.angle_limit
        self.modifier.use_dissolve_boundaries = mod.use_dissolve_boundaries
        self.modifier.delimit = mod.delimit


    def DISPLACE(self, mod):
        self.modifier.direction = mod.direction
        self.modifier.space = mod.space
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.texture_coords = mod.texture_coords
        self.modifier.texture_coords_object = mod.texture_coords_object
        self.modifier.uv_layer = mod.uv_layer
        self.modifier.mid_level = mod.mid_level
        self.modifier.strength = mod.strength


    def EDGE_SPLIT(self, mod):
        self.modifier.use_edge_angle = mod.use_edge_angle
        self.modifier.split_angle = mod.split_angle
        self.modifier.use_edge_sharp = mod.use_edge_sharp


    def EXPLODE(self, mod):
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.protect = mod.protect
        self.modifier.particle_uv = mod.particle_uv
        self.modifier.use_edge_cut = mod.use_edge_cut
        self.modifier.show_unborn = mod.show_unborn
        self.modifier.show_alive = mod.show_alive
        self.modifier.show_dead = mod.show_dead
        self.modifier.use_size = mod.use_size


    def FLUID_SIMULATION(self, mod):
        pass


    def HOOK(self, mod):
        self.modifier.object = mod.object
        self.modifier.subtarget = mod.subtarget
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.falloff_radius = mod.falloff_radius
        self.modifier.strength = mod.strength
        self.modifier.falloff_type = mod.falloff_type
        # self.modifier.falloff_curve = mod.falloff_curve
        self.modifier.use_falloff_uniform = mod.use_falloff_uniform


    def LAPLACIANDEFORM(self, mod):
        self.modifier.iterations = mod.iterations
        self.modifier.vertex_group = mod.vertex_group


    def LAPLACIANSMOOTH(self, mod):
        self.modifier.iterations = mod.iterations
        self.modifier.use_x = mod.use_x
        self.modifier.use_y = mod.use_y
        self.modifier.use_z = mod.use_z
        self.modifier.lambda_factor = mod.lambda_factor
        self.modifier.lambda_border = mod.lambda_border
        self.modifier.use_volume_preserve = mod.use_volume_preserve
        self.modifier.use_normalized = mod.use_normalized
        self.modifier.vertex_group = mod.vertex_group


    def LATTICE(self, mod):
        self.modifier.object = mod.object
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.strength = mod.strength


    def MASK(self, mod):
        self.modifier.mode = mod.mode
        self.modifier.armature = mod.armature
        self.modifier.invert_vertex_group = mod.invert_vertex_group
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.invert_vertex_group = mod.invert_vertex_group
        self.modifier.threshold = mod.threshold


    def MESH_DEFORM(self, mod):
        self.modifier.object = mod.object
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.invert_vertex_group = mod.invert_vertex_group
        self.modifier.precision = mod.precision
        self.modifier.use_dynamic_bind = mod.use_dynamic_bind


    def MIRROR(self, mod):
        self.modifier.use_axis = mod.use_axis
        self.modifier.use_bisect_axis = mod.use_bisect_axis
        self.modifier.use_bisect_flip_axis = mod.use_bisect_flip_axis
        self.modifier.use_mirror_merge = mod.use_mirror_merge
        self.modifier.use_clip = mod.use_clip
        self.modifier.use_mirror_vertex_groups = mod.use_mirror_vertex_groups
        self.modifier.use_mirror_u = mod.use_mirror_u
        self.modifier.use_mirror_v = mod.use_mirror_v
        self.modifier.mirror_offset_u = mod.mirror_offset_u
        self.modifier.mirror_offset_v = mod.mirror_offset_v
        self.modifier.offset_u = mod.offset_u
        self.modifier.offset_v = mod.offset_v
        self.modifier.merge_threshold = mod.merge_threshold
        self.modifier.mirror_object = mod.mirror_object
        self.modifier.show_in_editmode = mod.show_in_editmode


    def MULTIRES(self, mod):
        self.modifier.levels = mod.levels
        self.modifier.sculpt_levels = mod.sculpt_levels
        self.modifier.render_levels = mod.render_levels
        self.modifier.quality = mod.quality
        self.modifier.uv_smooth = mod.uv_smooth
        self.modifier.show_only_control_edges = mod.show_only_control_edges
        self.modifier.filepath = mod.filepath


    def OCEAN(self, mod):
        self.modifier.geometry_mode = mod.geometry_mode
        self.modifier.repeat_x = mod.repeat_x
        self.modifier.repeat_y = mod.repeat_y
        self.modifier.time = mod.time
        self.modifier.depth = mod.depth
        self.modifier.random_seed = mod.random_seed
        self.modifier.resolution = mod.resolution
        self.modifier.size = mod.size
        self.modifier.spatial_size = mod.spatial_size
        self.modifier.choppiness = mod.choppiness
        self.modifier.wave_scale = mod.wave_scale
        self.modifier.wave_scale_min = mod.wave_scale_min
        self.modifier.wind_velocity = mod.wind_velocity
        self.modifier.wave_alignment = mod.wave_alignment
        self.modifier.wave_direction = mod.wave_direction
        self.modifier.damping = mod.damping
        self.modifier.use_normals = mod.use_normals
        self.modifier.use_foam = mod.use_foam
        self.modifier.foam_coverage = mod.foam_coverage
        self.modifier.foam_layer_name = mod.foam_layer_name
        self.modifier.frame_start = mod.frame_start
        self.modifier.frame_end = mod.frame_end
        self.modifier.filepath = mod.filepath
        self.modifier.bake_foam_fade = mod.bake_foam_fade


    def PARTICLE_INSTANCE(self, mod):
        self.modifier.object = mod.object
        self.modifier.particle_system = mod.particle_system
        self.modifier.particle_system_index = mod.particle_system_index
        self.modifier.space = mod.space
        self.modifier.use_normal = mod.use_normal
        self.modifier.use_children = mod.use_children
        self.modifier.use_size = mod.use_size
        self.modifier.show_alive = mod.show_alive
        self.modifier.show_unborn = mod.show_unborn
        self.modifier.show_dead = mod.show_dead
        self.modifier.particle_amount = mod.particle_amount
        self.modifier.particle_offset = mod.particle_offset
        self.modifier.axis = mod.axis
        self.modifier.use_path = mod.use_path
        self.modifier.use_preserve_shape = mod.use_preserve_shape
        self.modifier.position = mod.position
        self.modifier.random_position = mod.random_position
        self.modifier.rotation = mod.rotation
        self.modifier.random_rotation = mod.random_rotation
        self.modifier.index_layer_name = mod.index_layer_name
        self.modifier.value_layer_name = mod.value_layer_name


    def PARTICLE_SYSTEM(self, mod):
        pass


    def SCREW(self, mod):
        self.modifier.axis = mod.axis
        self.modifier.object = mod.object
        self.modifier.angle = mod.angle
        self.modifier.steps = mod.steps
        self.modifier.render_steps = mod.render_steps
        self.modifier.use_smooth_shade = mod.use_smooth_shade
        self.modifier.use_merge_vertices = mod.use_merge_vertices
        self.modifier.merge_threshold = mod.merge_threshold
        self.modifier.screw_offset = mod.screw_offset
        self.modifier.use_object_screw_offset = mod.use_object_screw_offset
        self.modifier.use_normal_calculate = mod.use_normal_calculate
        self.modifier.use_normal_flip = mod.use_normal_flip
        self.modifier.iterations = mod.iterations
        self.modifier.use_stretch_u = mod.use_stretch_u
        self.modifier.use_stretch_v = mod.use_stretch_v


    def SHRINKWRAP(self, mod):
        self.modifier.target = mod.target
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.invert_vertex_group = mod.invert_vertex_group
        self.modifier.offset = mod.offset
        self.modifier.wrap_method = mod.wrap_method
        self.modifier.wrap_mode = mod.wrap_mode
        self.modifier.subsurf_levels = mod.subsurf_levels
        self.modifier.project_limit = mod.project_limit
        self.modifier.use_project_x = mod.use_project_x
        self.modifier.use_project_y = mod.use_project_y
        self.modifier.use_project_z = mod.use_project_z
        self.modifier.use_negative_direction = mod.use_negative_direction
        self.modifier.use_positive_direction = mod.use_positive_direction
        self.modifier.use_invert_cull = mod.use_invert_cull
        self.modifier.cull_face = mod.cull_face
        self.modifier.auxiliary_target = mod.auxiliary_target


    def SIMPLE_DEFORM(self, mod):
        self.modifier.deform_method = mod.deform_method
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.invert_vertex_group = mod.invert_vertex_group
        self.modifier.origin = mod.origin
        self.modifier.deform_axis = mod.deform_axis
        self.modifier.lock_x = mod.lock_x
        self.modifier.lock_y = mod.lock_y
        self.modifier.lock_z = mod.lock_z
        self.modifier.factor = mod.factor
        self.modifier.angle = mod.angle
        self.modifier.limits = mod.limits


    def SMOKE(self, mod):
        pass


    def SMOOTH(self, mod):
        self.modifier.use_x = mod.use_x
        self.modifier.use_y = mod.use_y
        self.modifier.use_z = mod.use_z
        self.modifier.factor = mod.factor
        self.modifier.iterations = mod.iterations
        self.modifier.vertex_group = mod.vertex_group


    def SOFT_BODY(self, mod):
        pass


    def SOLIDIFY(self, mod):
        self.modifier.thickness = mod.thickness
        self.modifier.thickness_clamp = mod.thickness_clamp
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.invert_vertex_group = mod.invert_vertex_group
        self.modifier.thickness_vertex_group = mod.thickness_vertex_group
        self.modifier.edge_crease_inner = mod.edge_crease_inner
        self.modifier.edge_crease_outer = mod.edge_crease_outer
        self.modifier.edge_crease_rim = mod.edge_crease_rim
        self.modifier.offset = mod.offset
        self.modifier.use_flip_normals = mod.use_flip_normals
        self.modifier.use_even_offset = mod.use_even_offset
        self.modifier.use_quality_normals = mod.use_quality_normals
        self.modifier.use_rim = mod.use_rim
        self.modifier.use_rim_only = mod.use_rim_only
        self.modifier.material_offset = mod.material_offset
        self.modifier.material_offset_rim = mod.material_offset_rim


    def SUBSURF(self, mod):
        self.modifier.subdivision_type = mod.subdivision_type
        self.modifier.levels = mod.levels
        self.modifier.render_levels = mod.render_levels
        self.modifier.levels = mod.levels
        self.modifier.render_levels = mod.render_levels

        if hasattr(mod, 'quality'):
            self.modifier.quality = mod.quality

        self.modifier.uv_smooth = mod.uv_smooth
        self.modifier.show_only_control_edges = mod.show_only_control_edges


    def SURFACE(self, mod):
        pass


    def SURFACE_DEFORM(self, mod):
        self.modifier.target = mod.target
        self.modifier.falloff = mod.falloff


    def UV_PROJECT(self, mod):
        self.modifier.uv_layer = mod.uv_layer
        self.modifier.projector_count = mod.projector_count

        for index, proj in enumerate(modifier.projectors):
            self.modifier[index].object = proj.object

        self.modifier.aspect_x = mod.aspect_x
        self.modifier.aspect_y = mod.aspect_y
        self.modifier.scale_x = mod.scale_x
        self.modifier.scale_y = mod.scale_y


    def WARP(self, mod):
        self.modifier.object_from = mod.object_from
        self.modifier.use_volume_preserve = mod.use_volume_preserve
        self.modifier.object_to = mod.object_to
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.strength = mod.strength
        self.modifier.falloff_radius = mod.falloff_radius
        self.modifier.falloff_type = mod.falloff_type
        self.modifier.falloff_curve = mod.falloff_curve
        self.modifier.texture = mod.texture
        self.modifier.texture_coords = mod.texture_coords
        self.modifier.texture_coords_object = mod.texture_coords_object
        self.modifier.uv_layer = mod.uv_layer


    def WAVE(self, mod):
        self.modifier.use_x = mod.use_x
        self.modifier.use_y = mod.use_y
        self.modifier.use_cyclic = mod.use_cyclic
        self.modifier.use_normal_x = mod.use_normal_x
        self.modifier.use_normal_y = mod.use_normal_y
        self.modifier.use_normal_z = mod.use_normal_z
        self.modifier.time_offset = mod.time_offset
        self.modifier.lifetime = mod.lifetime
        self.modifier.damping_time = mod.damping_time
        self.modifier.start_position_x = mod.start_position_x
        self.modifier.start_position_y = mod.start_position_y
        self.modifier.falloff_radius = mod.falloff_radius
        self.modifier.start_position_object = mod.start_position_object
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.texture = mod.texture
        self.modifier.texture_coords = mod.texture_coords
        self.modifier.uv_layer = mod.uv_layer
        self.modifier.texture_coords_object = mod.texture_coords_object
        self.modifier.speed = mod.speed
        self.modifier.height = mod.height
        self.modifier.width = mod.width
        self.modifier.narrowness = mod.narrowness


    def REMESH(self, mod):
        self.modifier.octree_depth = mod.octree_depth
        self.modifier.scale = mod.scale
        self.modifier.sharpness = mod.sharpness
        self.modifier.use_smooth_shade = mod.use_smooth_shade
        self.modifier.use_remove_disconnected = mod.use_remove_disconnected
        self.modifier.threshold = mod.threshold

    @staticmethod
    def vertex_weight_mask(layout, modifier):
        self.modifier.mask_constant = mod.mask_constant
        self.modifier.mask_vertex_group = mod.mask_vertex_group
        self.modifier.mask_texture = mod.mask_texture
        self.modifier.mask_tex_mapping = mod.mask_tex_mapping
        self.modifier.mask_tex_use_channel = mod.mask_tex_use_channel
        self.modifier.mask_tex_map_object = mod.mask_tex_map_object
        self.modifier.mask_tex_uv_layer = mod.mask_tex_uv_layer


    def VERTEX_WEIGHT_EDIT(self, mod):
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.default_weight = mod.default_weight
        self.modifier.use_add = mod.use_add
        self.modifier.add_threshold = mod.add_threshold
        self.modifier.use_remove = mod.use_remove
        self.modifier.remove_threshold = mod.remove_threshold
        self.modifier.falloff_type = mod.falloff_type
        self.modifier.map_curve = mod.map_curve


    def VERTEX_WEIGHT_MIX(self, mod):
        self.modifier.vertex_group_a = mod.vertex_group_a
        self.modifier.default_weight_a = mod.default_weight_a
        self.modifier.mix_mode = mod.mix_mode
        self.modifier.vertex_group_b = mod.vertex_group_b
        self.modifier.default_weight_b = mod.default_weight_b
        self.modifier.mix_set = mod.mix_set

        self.vertex_weight_mask(layout, ob, md)


    def VERTEX_WEIGHT_PROXIMITY(self, mod):
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.target = mod.target
        self.modifier.proximity_mode = mod.proximity_mode
        self.modifier.proximity_geometry = mod.proximity_geometry
        self.modifier.min_dist = mod.min_dist
        self.modifier.max_dist = mod.max_dist
        self.modifier.falloff_type = mod.falloff_type

        self.vertex_weight_mask(layout, ob, md)


    def SKIN(self, mod):
        self.modifier.branch_smoothing = mod.branch_smoothing
        self.modifier.use_smooth_shade = mod.use_smooth_shade
        self.modifier.use_x_symmetry = mod.use_x_symmetry
        self.modifier.use_y_symmetry = mod.use_y_symmetry
        self.modifier.use_z_symmetry = mod.use_z_symmetry


    def TRIANGULATE(self, mod):
        self.modifier.quad_method = mod.quad_method
        self.modifier.ngon_method = mod.ngon_method
        self.modifier.min_vertices = mod.min_vertices


    def UV_WARP(self, mod):
        self.modifier.center = mod.center
        self.modifier.axis_u = mod.axis_u
        self.modifier.axis_v = mod.axis_v
        self.modifier.object_from = mod.object_from
        self.modifier.object_to = mod.object_to
        self.modifier.bone_from = mod.bone_from
        self.modifier.bone_to = mod.bone_to
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.uv_layer = mod.uv_layer


    def WIREFRAME(self, mod):
        self.modifier.thickness = mod.thickness
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.invert_vertex_group = mod.invert_vertex_group
        self.modifier.thickness_vertex_group = mod.thickness_vertex_group
        self.modifier.use_crease = mod.use_crease
        self.modifier.crease_weight = mod.crease_weight
        self.modifier.offset = mod.offset
        self.modifier.use_even_offset = mod.use_even_offset
        self.modifier.use_relative_offset = mod.use_relative_offset
        self.modifier.use_boundary = mod.use_boundary
        self.modifier.use_replace = mod.use_replace
        self.modifier.material_offset = mod.material_offset


    def DATA_TRANSFER(self, mod):
        self.modifier.object = mod.object
        self.modifier.use_object_transform = mod.use_object_transform
        self.modifier.use_vert_data = mod.use_vert_data
        self.modifier.vert_mapping = mod.vert_mapping
        self.modifier.data_types_verts = mod.data_types_verts
        self.modifier.layers_vgroup_select_src = mod.layers_vgroup_select_src
        self.modifier.layers_vgroup_select_dst = mod.layers_vgroup_select_dst
        self.modifier.use_edge_data = mod.use_edge_data
        self.modifier.edge_mapping = mod.edge_mapping
        self.modifier.data_types_edges = mod.data_types_edges
        self.modifier.use_loop_data = mod.use_loop_data
        self.modifier.loop_mapping = mod.loop_mapping
        self.modifier.data_types_loops = mod.data_types_loops
        self.modifier.layers_vcol_select_src = mod.layers_vcol_select_src
        self.modifier.layers_vcol_select_dst = mod.layers_vcol_select_dst
        self.modifier.layers_uv_select_src = mod.layers_uv_select_src
        self.modifier.layers_uv_select_dst = mod.layers_uv_select_dst
        self.modifier.islands_precision = mod.islands_precision
        self.modifier.use_poly_data = mod.use_poly_data
        self.modifier.poly_mapping = mod.poly_mapping
        self.modifier.data_types_polys = mod.data_types_polys
        self.modifier.max_distance = mod.max_distance
        self.modifier.use_max_distance = mod.use_max_distance
        self.modifier.ray_radius = mod.ray_radius
        self.modifier.mix_mode = mod.mix_mode
        self.modifier.mix_factor = mod.mix_factor
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.invert_vertex_group = mod.invert_vertex_group


    def NORMAL_EDIT(self, mod):
        self.modifier.mode = mod.mode
        self.modifier.target = mod.target
        self.modifier.offset = mod.offset
        self.modifier.use_direction_parallel = mod.use_direction_parallel
        self.modifier.mix_mode = mod.mix_mode
        self.modifier.mix_factor = mod.mix_factor
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.invert_vertex_group = mod.invert_vertex_group
        self.modifier.mix_limit = mod.mix_limit
        self.modifier.no_polynors_fix = mod.no_polynors_fix


    def CORRECTIVE_SMOOTH(self, mod):
        self.modifier.factor = mod.factor
        self.modifier.iterations = mod.iterations
        self.modifier.smooth_type = mod.smooth_type
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.invert_vertex_group = mod.invert_vertex_group
        self.modifier.use_only_smooth = mod.use_only_smooth
        self.modifier.use_pin_boundary = mod.use_pin_boundary
        self.modifier.rest_source = mod.rest_source


    def WEIGHTED_NORMAL(self, mod):
        self.modifier.mode = mod.mode
        self.modifier.weight = mod.weight
        self.modifier.keep_sharp = mod.keep_sharp
        self.modifier.vertex_group = mod.vertex_group
        self.modifier.invert_vertex_group = mod.invert_vertex_group
        self.modifier.thresh = mod.thresh
        self.modifier.face_influence = mod.face_influence
        self.modifier.show_in_editmode = mod.show_in_editmode
