
# imports
import bpy
from bpy.app.translations import pgettext_iface as iface_

# modifier
class Modifier:
    '''
            The UI settings for modifiers.
    '''

    # main
    def main(self, context, layout, object, modifier):

        # context pointer set
        layout.context_pointer_set('modifier', modifier)

        # row
        row = layout.row(align=True)

        # name
        row.prop(modifier, 'name', text='')

        # move up
        if modifier != object.modifiers[0]:

            row.operator('object.modifier_move_up', text='', icon='TRIA_UP')

        # move down
        if modifier != object.modifiers[len(object.modifiers)-1]:

            row.operator('object.modifier_move_down', text='', icon='TRIA_DOWN')

        # delete
        row.operator('object.modifier_remove', text='', icon='X')

        # row
        row = layout.row()

        # isnt collision, particle system
        if modifier.type not in {'COLLISION', 'PARTICLE_SYSTEM'}:

            # apply
            op = row.operator('object.modifier_apply', text='Apply')
            op.apply_as = 'DATA'

            # is ...
            if modifier.type in {'MESH_CACHE', 'ARMATURE', 'CAST', 'CORRECTIVE_SMOOTH', 'CURVE', 'DISPLACE', 'HOOK', 'LAPLACIANSMOOTH', 'LAPLACIANDEFORM', 'LATTICE', 'MESH_DEFORM', 'SHRINKWRAP', 'SIMPLE_DEFORM', 'SMOOTH', 'WARP', 'WAVE', 'CLOTH', 'SOFT_BODY'}:

                # apply
                op = row.operator('object.modifier_apply', text='Apply as Shape Key')
                op.apply_as = 'SHAPE'

            # isnt cloth, fluid simulation, smoke, soft body
            if modifier.type not in {'CLOTH', 'FLUID_SIMULATION', 'SMOKE', 'SOFT_BODY'}:

                # copy
                row.operator('object.modifier_copy', text='Copy')

        # column
        column = layout.column()

        getattr(Modifier, modifier.type)(Modifier, column, object, modifier)

    # armature
    def ARMATURE(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Object:')

        # object
        column.prop(modifier, 'object', text='')

        # use deform preserve volume
        column.prop(modifier, 'use_deform_preserve_volume')

        # column
        column = split.column()

        # label
        column.label(text='Bind To:')

        # use vertex groups
        column.prop(modifier, 'use_vertex_groups', text='Vertex Groups')

        # use bone envelopes
        column.prop(modifier, 'use_bone_envelopes', text='Bone Envelopes')

        # separate
        layout.separator()

        # split
        split = layout.split()

        # row
        row = split.row(align=True)

        # vertex group
        row.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # sub
        sub = row.row(align=True)

        # sub active if vertex group
        sub.active = bool(modifier.vertex_group)

        # invert vertex group
        sub.prop(modifier, 'invert_vertex_group', text='', icon='ARROW_LEFTRIGHT')

        # use multi modifier
        split.prop(modifier, 'use_multi_modifier')

    # array
    def ARRAY(self, layout, object, modifier):

        # fit type
        layout.prop(modifier, 'fit_type')

        # is fit type in fixed count
        if modifier.fit_type == 'FIXED_COUNT':

            # count
            layout.prop(modifier, 'count')

        # is fit type in fit length
        elif modifier.fit_type == 'FIT_LENGTH':

            # fit length
            layout.prop(modifier, 'fit_length')

        # is fit type in fit curve
        elif modifier.fit_type == 'FIT_CURVE':

            # curve
            layout.prop(modifier, 'curve')

        # separate
        layout.separator()

        # split
        split = layout.split()

        # column
        column = split.column()

        # use constant offset
        column.prop(modifier, 'use_constant_offset')

        # sub
        sub = column.column()

        # sub active if use constant offset
        sub.active = modifier.use_constant_offset

        # constant offset displace
        sub.prop(modifier, 'constant_offset_displace', text='')

        # separate
        column.separator()

        # use merge vertices
        column.prop(modifier, 'use_merge_vertices', text='Merge')

        # sub
        sub = column.column()

        # sub active if use merge vertices
        sub.active = modifier.use_merge_vertices

        # use merge vertices cap
        sub.prop(modifier, 'use_merge_vertices_cap', text='First Last')

        # merge threshold
        sub.prop(modifier, 'merge_threshold', text='Distance')

        # column
        column = split.column()

        # use relative offset
        column.prop(modifier, 'use_relative_offset')

        # sub
        sub = column.column()

        # sub active if use relative offset
        sub.active = modifier.use_relative_offset

        # relative offset displace
        sub.prop(modifier, 'relative_offset_displace', text='')

        # separate
        column.separator()

        # use object offset
        column.prop(modifier, 'use_object_offset')

        # sub
        sub = column.column()

        # sub active if use object offset
        sub.active = modifier.use_object_offset

        # offset object
        sub.prop(modifier, 'offset_object', text='')

        # separate
        layout.separator()

        # start cap
        layout.prop(modifier, 'start_cap')

        # start cap
        layout.prop(modifier, 'end_cap')

    # bevel
    def BEVEL(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # width
        column.prop(modifier, 'width')

        # segments
        column.prop(modifier, 'segments')

        # profile
        column.prop(modifier, 'profile')

        # material
        column.prop(modifier, 'material')

        # column
        column = split.column()

        # use only vertices
        column.prop(modifier, 'use_only_vertices')

        # use clamp overlap
        column.prop(modifier, 'use_clamp_overlap')

        # loop slide
        column.prop(modifier, 'loop_slide')

        # label
        layout.label(text='Limit Method:')

        # limit method
        layout.row().prop(modifier, 'limit_method', expand=True)

        # is limit method in angle
        if modifier.limit_method == 'ANGLE':

            # angle limit
            layout.prop(modifier, 'angle_limit')

        # is limit method in vgroup
        elif modifier.limit_method == 'VGROUP':

            # label
            layout.label(text='Vertex Group:')

            # vertex group
            layout.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # label
        layout.label(text='Width Method:')

        # offset type
        layout.row().prop(modifier, 'offset_type', expand=True)

    # boolean
    def BOOLEAN(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Operation:')

        # operation
        column.prop(modifier, 'operation', text='')

        # column
        column = split.column()

        # label
        column.label(text='Object:')

        # object
        column.prop(modifier, 'object', text='')

    # build
    def BUILD(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # frame start
        column.prop(modifier, 'frame_start')

        # frame duration
        column.prop(modifier, 'frame_duration')

        # use reverse
        column.prop(modifier, 'use_reverse')

        # column
        column = split.column()

        # use random order
        column.prop(modifier, 'use_random_order')

        # sub
        sub = column.column()

        # sub active if use random order
        sub.active = modifier.use_random_order

        # seed
        sub.prop(modifier, 'seed')

    # mesh cache
    def MESH_CACHE(self, layout, object, modifier):

        # cache format
        layout.prop(modifier, 'cache_format')

        # filepath
        layout.prop(modifier, 'filepath')

        # label
        layout.label(text='Evaluation:')

        # factor
        layout.prop(modifier, 'factor', slider=True)

        # deform mode
        layout.prop(modifier, 'deform_mode')

        # interpolation
        layout.prop(modifier, 'interpolation')

        # label
        layout.label(text='Time Mapping:')

        # row
        row = layout.row()

        # time mode
        row.prop(modifier, 'time_mode', expand=True)

        # row
        row = layout.row()

        # play mode
        row.prop(modifier, 'play_mode', expand=True)

        # is play mode in scene
        if modifier.play_mode == 'SCENE':

            # frame start
            layout.prop(modifier, 'frame_start')

            # frame scale
            layout.prop(modifier, 'frame_scale')

        # isnt play mode in scene
        else:

            # time mode
            time_mode = modifier.time_mode

            # is time mode in frame
            if time_mode == 'FRAME':

                # eval frame
                layout.prop(modifier, 'eval_frame')

            # is time mode in time
            elif time_mode == 'TIME':

                # eval time
                layout.prop(modifier, 'eval_time')

            # is time mode in factor
            elif time_mode == 'FACTOR':

                # eval factor
                layout.prop(modifier, 'eval_factor')

        # label
        layout.label(text='Axis Mapping:')

        # split
        split = layout.split(percentage=0.5, align=True)

        # split alert if forward axis is up axis
        split.alert = (modifier.forward_axis[-1] == modifier.up_axis[-1])

        # label
        split.label('Forward/Up Axis:')

        # forward axis
        split.prop(modifier, 'forward_axis', text='')

        # up axis
        split.prop(modifier, 'up_axis', text='')

        # split
        split = layout.split(percentage=0.5)

        # label
        split.label(text='Flip Axis:')

        # row
        row = split.row()

        # flip axis
        row.prop(modifier, 'flip_axis')

    # cast
    def CAST(self, layout, object, modifier):

            # split
            split = layout.split(percentage=0.25)

            # label
            split.label(text='Cast Type:')

            # cast type
            split.prop(modifier, 'cast_type', text='')

            # split
            split = layout.split(percentage=0.25)

            # column
            column = split.column()

            # use x
            column.prop(modifier, 'use_x')

            # use y
            column.prop(modifier, 'use_y')

            # use z
            column.prop(modifier, 'use_z')

            # column
            column = split.column()

            # factor
            column.prop(modifier, 'factor')

            # radius
            column.prop(modifier, 'radius')

            # size
            column.prop(modifier, 'size')

            # use radius as size
            column.prop(modifier, 'use_radius_as_size')

            # split
            split = layout.split()

            # column
            column = split.column()

            # label
            column.label(text='Vertex Group:')

            # vertex group
            column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

            # column
            column = split.column()

            # label
            column.label(text='Control Object:')

            # object
            column.prop(modifier, 'object', text='')

            # is object
            if modifier.object:

                # use transform
                column.prop(modifier, 'use_transform')

    # cloth
    def CLOTH(self, layout, object, modifier):

        # label
        layout.label(text='Settings are inside the Physics tab')

    # collision
    def COLLISION(self, layout, object, modifier):

        # label
        layout.label(text='Settings are inside the Physics tab')

    # curve
    def CURVE(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Object:')

        # object
        column.prop(modifier, 'object', text='')

        # column
        column = split.column()

        # label
        column.label(text='Vertex Group:')

        # vertex group
        column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # label
        layout.label(text='Deformation Axis:')

        # deform axis
        layout.row().prop(modifier, 'deform_axis', expand=True)

    # decimate
    def DECIMATE(self, layout, object, modifier):

        # decimate type
        decimate_type = modifier.decimate_type

        # row
        row = layout.row()

        # decimate type
        row.prop(modifier, 'decimate_type', expand=True)

        # is decimate type in collapse
        if decimate_type == 'COLLAPSE':

            # has vgroup
            has_vgroup = bool(modifier.vertex_group)

            # ratio
            layout.prop(modifier, 'ratio')

            # split
            split = layout.split()

            # column
            column = split.column()

            # row
            row = column.row(align=True)

            # vertex group
            row.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

            # invert vertex group
            row.prop(modifier, 'invert_vertex_group', text='', icon='ARROW_LEFTRIGHT')

            # layout info
            layout_info = column

            # column
            column = split.column()

            # row
            row = column.row()

            # has vgroup
            row.active = has_vgroup

            # vertex group factor
            row.prop(modifier, 'vertex_group_factor')

            # use callapse triangulate
            column.prop(modifier, 'use_collapse_triangulate')

        # is decimate type in unsubdiv
        elif decimate_type == 'UNSUBDIV':

            # iterations
            layout.prop(modifier, 'iterations')

            # layout info
            layout_info = layout

        # is decimate type in dissolve
        else:

            # angle limit
            layout.prop(modifier, 'angle_limit')

            # use dissolve boundaries
            layout.prop(modifier, 'use_dissolve_boundaries')

            # label
            layout.label('Delimit:')

            # row
            row = layout.row()

            # delimit
            row.prop(modifier, 'delimit')

            # layout info
            layout_info = layout

        # label
        layout_info.label(text=iface_('Faces: %d') % modifier.face_count, translate=False)

    # displace
    def DISPLACE(self, layout, object, modifier):

        # has texture
        has_texture = (modifier.texture is not None)

        # column
        column = layout.column(align=True)

        # label
        column.label(text='Texture:')

        # texture
        column.template_ID(modifier, 'texture', new='texture.new')

        # split
        split = layout.split()

        # column
        column = split.column(align=True)

        # label
        column.label(text='Direction:')

        # direction
        column.prop(modifier, 'direction', text='')

        # label
        column.label(text='Vertex Group:')

        # vertex group
        column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # column
        column = split.column(align=True)

        # column active if has texture
        column.active = has_texture

        # label
        column.label(text='Texture Coordinates:')

        # texture coords
        column.prop(modifier, 'texture_coords', text='')

        # is texture coords in object
        if modifier.texture_coords == 'OBJECT':

            # label
            column.label(text='Object:')

            # texture coords object
            column.prop(modifier, 'texture_coords_object', text='')

        # is texture coords in uv and type in mesh
        elif modifier.texture_coords == 'UV' and object.type == 'MESH':

            # label
            column.label(text='UV Map:')

            # uv layer
            column.prop_search(modifier, 'uv_layer', object.data, 'uv_textures', text='')

        # separate
        layout.separator()

        # row
        row = layout.row()

        # mid level
        row.prop(modifier, 'mid_level')

        # strength
        row.prop(modifier, 'strength')

    # dynamix paint
    def DYNAMIC_PAINT(self, layout, object, modifier):

        # label
        layout.label(text='Settings are inside the Physics tab')

    # edge split
    def EDGE_SPLIT(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # use edge angle
        column.prop(modifier, 'use_edge_angle', text='Edge Angle')

        # sub
        sub = column.column()

        # sub active if use edge angle
        sub.active = modifier.use_edge_angle

        # split angle
        sub.prop(modifier, 'split_angle')

        # use edge sharp
        split.prop(modifier, 'use_edge_sharp', text='Sharp Edges')

    # explode
    def EXPLODE(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Vertex group:')

        # vertex group
        column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # sub
        sub = column.column()

        # sub active if vertex group
        sub.active = bool(modifier.vertex_group)

        # protext
        sub.prop(modifier, 'protect')

        # label
        column.label(text='Particle UV')

        # particle uv
        column.prop_search(modifier, 'particle_uv', object.data, 'uv_textures', text='')

        # column
        column = split.column()

        # use edge cut
        column.prop(modifier, 'use_edge_cut')

        # show unborn
        column.prop(modifier, 'show_unborn')

        # show alive
        column.prop(modifier, 'show_alive')

        # show dead
        column.prop(modifier, 'show_dead')

        # use size
        column.prop(modifier, 'use_size')

        # object explde refresh
        layout.operator('object.explode_refresh', text='Refresh')

    # fluid simulation
    def FLUID_SIMULATION(self, layout, object, modifier):

        # label
        layout.label(text='Settings are inside the Physics tab')

    # hook
    def HOOK(self, layout, object, modifier):

        # use falloff
        use_falloff = (modifier.falloff_type != 'NONE')

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Object:')

        # object
        column.prop(modifier, 'object', text='')

        # is object and object type in armature
        if modifier.object and modifier.object.type == 'ARMATURE':

                # label
                column.label(text='Bone:')

                # subtarget
                column.prop_search(modifier, 'subtarget', modifier.object.data, 'bones', text='')

        # column
        column = split.column()

        # label
        column.label(text='Vertex Group:')

        # vertex group
        column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # separate
        layout.separator()

        # row
        row = layout.row(align=True)

        # use falloff
        if use_falloff:

            # falloff radius
            row.prop(modifier, 'falloff_radius')

        # strength
        row.prop(modifier, 'strength', slider=True)

        # falloff type
        layout.prop(modifier, 'falloff_type')

        # column
        column = layout.column()

        # is use falloff
        if use_falloff:

            # is folloff type in curve
            if modifier.falloff_type == 'CURVE':

                # folloff curve
                column.template_curve_mapping(modifier, 'falloff_curve')

        # split
        split = layout.split()

        # column
        column = split.column()

        # use falloff uniform
        column.prop(modifier, 'use_falloff_uniform')

        # is mode in edit
        if object.mode == 'EDIT':

            # row
            row = column.row(align=True)

            # object hook reset
            row.operator('object.hook_reset', text='Reset')

            # object hook recenter
            row.operator('object.hook_recenter', text='Recenter')

            # row
            row = layout.row(align=True)

            # object hook select
            row.operator('object.hook_select', text='Select')

            # object hook assign
            row.operator('object.hook_assign', text='Assign')

    # laplacian deform
    def LAPLACIANDEFORM(self, layout, object, modifier):

        # is bind
        is_bind = modifier.is_bind

        # iterations
        layout.prop(modifier, 'iterations')

        # row
        row = layout.row()

        # row active if isnt bind
        row.active = not is_bind

        # label
        row.label(text='Anchors Vertex Group:')

        # row
        row = layout.row()

        # row enabled if isnt bind
        row.enabled = not is_bind

        # vertex group
        row.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # separate
        layout.separator()

        # row
        row = layout.row()

        # row enabled if vertex group
        row.enabled = bool(modifier.vertex_group)

        # object laplacian deform bind
        row.operator('object.laplaciandeform_bind', text='Unbind' if is_bind else 'Bind')

    # laplacian smooth
    def LAPLACIANSMOOTH(self, layout, object, modifier):

        # iterations
        layout.prop(modifier, 'iterations')

        # split
        split = layout.split(percentage=0.25)

        # column
        column = split.column()

        # label
        column.label(text='Axis:')

        # use x
        column.prop(modifier, 'use_x')

        # use y
        column.prop(modifier, 'use_y')

        # use z
        column.prop(modifier, 'use_z')

        # column
        column = split.column()

        # label
        column.label(text='Lambda:')

        # lambda factor
        column.prop(modifier, 'lambda_factor', text='Factor')

        # lambda border
        column.prop(modifier, 'lambda_border', text='Border')

        # separate
        column.separator()

        # use volume preserve
        column.prop(modifier, 'use_volume_preserve')

        # use normalized
        column.prop(modifier, 'use_normalized')

        # label
        layout.label(text='Vertex Group:')

        # vertex group
        layout.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

    # lattice
    def LATTICE(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Object:')

        # object
        column.prop(modifier, 'object', text='')

        # column
        column = split.column()

        # label
        column.label(text='Vertex Group:')

        # vertex group
        column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # separate
        layout.separator()

        # strength
        layout.prop(modifier, 'strength', slider=True)

    # mask
    def MASK(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Mode:')

        # mode
        column.prop(modifier, 'mode', text='')

        # column
        column = split.column()

        # is mode in armature
        if modifier.mode == 'ARMATURE':

            # label
            column.label(text='Armature:')

            # row
            row = column.row(align=True)

            # armature
            row.prop(modifier, 'armature', text='')

            # sub
            sub = row.row(align=True)

            # sub active if armature
            sub.active = (modifier.armature is not None)

            # invert vertex group
            sub.prop(modifier, 'invert_vertex_group', text='', icon='ARROW_LEFTRIGHT')

        # is mode in vertex group
        elif modifier.mode == 'VERTEX_GROUP':

            # label
            column.label(text='Vertex Group:')

            # row
            row = column.row(align=True)

            # vertex group
            row.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

            # sub
            sub = row.row(align=True)

            # sub active if vertex group
            sub.active = bool(modifier.vertex_group)

            # invert vertex group
            sub.prop(modifier, 'invert_vertex_group', text='', icon='ARROW_LEFTRIGHT')

    # mesh deform
    def MESH_DEFORM(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # column active if not is bound
        column.active = not modifier.is_bound

        # label
        column.label(text='Object:')

        # object
        column.prop(modifier, 'object', text='')

        # column
        column = split.column()

        # label
        column.label(text='Vertex Group:')

        # row
        row = column.row(align=True)

        # vertex group
        row.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # sub
        sub = row.row(align=True)

        # sub active if vertex group
        sub.active = bool(modifier.vertex_group)

        # invert vertex group
        sub.prop(modifier, 'invert_vertex_group', text='', icon='ARROW_LEFTRIGHT')

        # separate
        layout.separator()

        # is bound
        if modifier.is_bound:

            # object mesh deform bind
            layout.operator('object.meshdeform_bind', text='Unbind')

        # isnt bount
        else:

            # object mesh deform bind
            layout.operator('object.meshdeform_bind', text='Bind')

            # row
            row = layout.row()

            # precision
            row.prop(modifier, 'precision')

            # use dynamic bind
            row.prop(modifier, 'use_dynamic_bind')

    # mirror
    def MIRROR(self, layout, object, modifier):

        # split
        split = layout.split(percentage=0.25)

        # column
        column = split.column()

        # label
        column.label(text='Axis:')

        # use x
        column.prop(modifier, 'use_x')

        # use y
        column.prop(modifier, 'use_y')

        # use z
        column.prop(modifier, 'use_z')

        # column
        column = split.column()

        # label
        column.label(text='Options:')

        # use mirror merge
        column.prop(modifier, 'use_mirror_merge', text='Merge')

        # use clip
        column.prop(modifier, 'use_clip', text='Clipping')

        # use mirror vertex groups
        column.prop(modifier, 'use_mirror_vertex_groups', text='Vertex Groups')

        # column
        column = split.column()

        # label
        column.label(text='Textures:')

        # use mirror u
        column.prop(modifier, 'use_mirror_u', text='U')

        # use mirror v
        column.prop(modifier, 'use_mirror_v', text='V')

        # column
        column = layout.column()

        # is use mirror merge
        if modifier.use_mirror_merge is True:

            # merge threshhold
            column.prop(modifier, 'merge_threshold')

        # label
        column.label(text='Mirror Object:')

        # mirror object
        column.prop(modifier, 'mirror_object', text='')

    # multires
    def MULTIRES(self, layout, object, modifier):

        layout.context_pointer_set('modifier', modifier)

        layout.row().prop(modifier, 'subdivision_type', expand=True)

        # split
        split = layout.split()

        # column
        column = split.column()

        # levels
        column.prop(modifier, 'levels', text='Preview')

        # sculpt levels
        column.prop(modifier, 'sculpt_levels', text='Sculpt')

        # render levels
        column.prop(modifier, 'render_levels', text='Render')

        # column
        column = split.column()

        # sub
        sub = column.column()
        # sub.enabled = False

        # object multires subdivide
        sub.operator('object.multires_subdivide', text='Subdivide')

        # object multires higher levels delete
        sub.operator('object.multires_higher_levels_delete', text='Delete Higher')

        # object multires reshape
        sub.operator('object.multires_reshape', text='Reshape')

        # object multires base apply
        sub.operator('object.multires_base_apply', text='Apply Base')

        column.enabled = object.mode != 'EDIT'

        # use subsurf uv
        column.prop(modifier, 'use_subsurf_uv')

        # show only control edges
        column.prop(modifier, 'show_only_control_edges')

        # separate
        layout.separator()

        # column
        column = layout.column()
        column.enabled = False

        # row
        row = column.row()

        # is external
        if modifier.is_external:

            # object multires external pack
            row.operator('object.multires_external_pack', text='Pack External')

            # label
            row.label()

            # row
            row = column.row()

            # filepath
            row.prop(modifier, 'filepath', text='')

        # isnt external
        else:

            # object multires external save
            row.operator('object.multires_external_save', text='Save External...')

            # label
            row.label()

    # ocean
    def OCEAN(self, layout, object, modifier):

        # is mod oceansim
        if not bpy.app.build_options.mod_oceansim:

            # label
            layout.label('Built without OceanSim modifier')
            return

        # geometry mode
        layout.prop(modifier, 'geometry_mode')

        if modifier.geometry_mode == 'GENERATE':
            # row
            row = layout.row()

            # repeat x
            row.prop(modifier, 'repeat_x')

            # repeat y
            row.prop(modifier, 'repeat_y')

        # separate
        layout.separator()

        # split
        split = layout.split()

        # column
        column = split.column()

        # time
        column.prop(modifier, 'time')

        # depth
        column.prop(modifier, 'depth')

        # random seed
        column.prop(modifier, 'random_seed')

        # column
        column = split.column()

        # resolution
        column.prop(modifier, 'resolution')

        # size
        column.prop(modifier, 'size')

        # spatial size
        column.prop(modifier, 'spatial_size')

        # label
        layout.label('Waves:')

        # split
        split = layout.split()

        # column
        column = split.column()

        # choppiness
        column.prop(modifier, 'choppiness')

        # wave scale
        column.prop(modifier, 'wave_scale', text='Scale')

        # wave scale min
        column.prop(modifier, 'wave_scale_min')

        # wind velocity
        column.prop(modifier, 'wind_velocity')

        # column
        column = split.column()

        # wave alignment
        column.prop(modifier, 'wave_alignment', text='Alignment')

        # sub
        sub = column.column()

        # sub active if wave alignment more then 0
        sub.active = (modifier.wave_alignment > 0.0)

        # wave direction
        sub.prop(modifier, 'wave_direction', text='Direction')

        # damping
        sub.prop(modifier, 'damping')

        # separate
        layout.separator()

        # use normals
        layout.prop(modifier, 'use_normals')

        # split
        split = layout.split()

        # column
        column = split.column()

        # use foam
        column.prop(modifier, 'use_foam')

        # sub
        sub = column.row()

        # sub active if use foam
        sub.active = modifier.use_foam

        # foam coverage
        sub.prop(modifier, 'foam_coverage', text='Coverage')

        # column
        column = split.column()

        # column active if use foam
        column.active = modifier.use_foam

        # label
        column.label('Foam Data Layer Name:')

        # foam layer name
        column.prop(modifier, 'foam_layer_name', text='')

        # separate
        layout.separator()

        # is cached
        if modifier.is_cached:

            # object ocean bake
            layout.operator('object.ocean_bake', text='Free Bake').free = True

        # isnt cached
        else:

            # object ocean bake
            layout.operator('object.ocean_bake').free = False

        # split
        split = layout.split()

        # split enabled is not cached
        split.enabled = not modifier.is_cached

        # column
        column = split.column(align=True)

        # frame start
        column.prop(modifier, 'frame_start', text='Start')

        # frame end
        column.prop(modifier, 'frame_end', text='End')

        # column
        column = split.column(align=True)

        # label
        column.label(text='Cache path:')

        # filepath
        column.prop(modifier, 'filepath', text='')

        # split
        split = layout.split()

        # split enabled is not cached
        split.enabled = not modifier.is_cached

        # column
        column = split.column()

        # column active if use foam
        column.active = modifier.use_foam

        # bake foam fade
        column.prop(modifier, 'bake_foam_fade')

        # column
        column = split.column()

    # particle instance
    def PARTICLE_INSTANCE(self, layout, object, modifier):

        # object
        layout.prop(modifier, 'object')

        # particle system index
        layout.prop(modifier, 'particle_system_index', text='Particle System')

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Create From:')

        # use normal
        column.prop(modifier, 'use_normal')

        # use children
        column.prop(modifier, 'use_children')

        # use size
        column.prop(modifier, 'use_size')

        # column
        column = split.column()

        # label
        column.label(text='Show Particles When:')

        # show alive
        column.prop(modifier, 'show_alive')

        # show unborn
        column.prop(modifier, 'show_unborn')

        # show dead
        column.prop(modifier, 'show_dead')

        # separate
        layout.separator()

        # use path
        layout.prop(modifier, 'use_path', text='Create Along Paths')

        # split
        split = layout.split()

        # split active if use path
        split.active = modifier.use_path

        # column
        column = split.column()

        # axis
        column.row().prop(modifier, 'axis', expand=True)

        # use preserve shape
        column.prop(modifier, 'use_preserve_shape')

        # column
        column = split.column()

        # position
        column.prop(modifier, 'position', slider=True)

        # Random
        column.prop(modifier, 'random_position', text='Random', slider=True)

    # particel system
    def PARTICLE_SYSTEM(self, layout, object, modifier):

        # label
        layout.label(text='Settings can be found inside the Particle context')

    # screw
    def SCREW(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # axis
        column.prop(modifier, 'axis')

        # object
        column.prop(modifier, 'object', text='AxisOb')

        # angle
        column.prop(modifier, 'angle')

        # steps
        column.prop(modifier, 'steps')

        # render steps
        column.prop(modifier, 'render_steps')

        # use smooth shade
        column.prop(modifier, 'use_smooth_shade')

        # column
        column = split.column()

        # row
        row = column.row()

        # row active if object and not use object screw offset
        row.active = (modifier.object is None or modifier.use_object_screw_offset is False)

        # screw offset
        row.prop(modifier, 'screw_offset')

        # row
        row = column.row()

        # row active if object
        row.active = (modifier.object is not None)

        # use object screw offset
        row.prop(modifier, 'use_object_screw_offset')

        # use normal calculate
        column.prop(modifier, 'use_normal_calculate')

        # use normal flip
        column.prop(modifier, 'use_normal_flip')

        # iterations
        column.prop(modifier, 'iterations')

        # use stretch u
        column.prop(modifier, 'use_stretch_u')

        # use stretch v
        column.prop(modifier, 'use_stretch_v')

    # shrinkwrap
    def SHRINKWRAP(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Target:')

        # target
        column.prop(modifier, 'target', text='')

        # column
        column = split.column()

        # label
        column.label(text='Vertex Group:')

        # vertex groups
        column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # split
        split = layout.split()

        # column
        column = split.column()

        # offset
        column.prop(modifier, 'offset')

        # column
        column = split.column()

        # label
        column.label(text='Mode:')

        # wrap method
        column.prop(modifier, 'wrap_method', text='')

        # is wrap method in project
        if modifier.wrap_method == 'PROJECT':

            # split
            split = layout.split()

            # column
            column = split.column()

            # subsurf levels
            column.prop(modifier, 'subsurf_levels')

            # column
            column = split.column()

            # project limit
            column.prop(modifier, 'project_limit', text='Limit')

            # split
            split = layout.split(percentage=0.25)

            # column
            column = split.column()

            # label
            column.label(text='Axis:')

            # use project x
            column.prop(modifier, 'use_project_x')

            # use project y
            column.prop(modifier, 'use_project_y')

            # use project z
            column.prop(modifier, 'use_project_z')

            # column
            column = split.column()

            # label
            column.label(text='Direction:')

            # use negative direction
            column.prop(modifier, 'use_negative_direction')

            # use positive direction
            column.prop(modifier, 'use_positive_direction')

            # column
            column = split.column()

            # label
            column.label(text='Cull Faces:')

            # cull face
            column.prop(modifier, 'cull_face', expand=True)

            # auxiliary target
            layout.prop(modifier, 'auxiliary_target')

        # is wrap method in nearest surface point
        elif modifier.wrap_method == 'NEAREST_SURFACEPOINT':

            # use keep above surface
            layout.prop(modifier, 'use_keep_above_surface')

    # simple deform
    def SIMPLE_DEFORM(self, layout, object, modifier):

        # deform method
        layout.row().prop(modifier, 'deform_method', expand=True)

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Vertex Group:')

        # vertex groups
        column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Origin:')

        # origin
        column.prop(modifier, 'origin', text='')

        # is deform method in taper, stretch, twist
        if modifier.deform_method in {'TAPER', 'STRETCH', 'TWIST'}:

            # label
            column.label(text='Lock:')

            # lock x
            column.prop(modifier, 'lock_x')

            # lock y
            column.prop(modifier, 'lock_y')

        # column
        column = split.column()

        # label
        column.label(text='Deform:')

        # is deform method in taper, stretch
        if modifier.deform_method in {'TAPER', 'STRETCH'}:

            # factor
            column.prop(modifier, 'factor')

        # is deform method in bend
        else:

            # angle
            column.prop(modifier, 'angle')

        # limits
        column.prop(modifier, 'limits', slider=True)

    # smoke
    def SMOKE(self, layout, object, modifier):

        # label
        layout.label(text='Settings are inside the Physics tab')

    # smooth
    def SMOOTH(self, layout, object, modifier):

        # split
        split = layout.split(percentage=0.25)

        # column
        column = split.column()

        # label
        column.label(text='Axis:')

        # use x
        column.prop(modifier, 'use_x')

        # use y
        column.prop(modifier, 'use_y')

        # use z
        column.prop(modifier, 'use_z')

        # column
        column = split.column()

        # factor
        column.prop(modifier, 'factor')

        # iterations
        column.prop(modifier, 'iterations')

        # label
        column.label(text='Vertex Group:')

        # vertex groups
        column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

    def SOFT_BODY(self, layout, object, modifier):

        # label
        layout.label(text='Settings are inside the Physics tab')

    def SOLIDIFY(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # thickness
        column.prop(modifier, 'thickness')

        # thickness clamp
        column.prop(modifier, 'thickness_clamp')

        column.separator()

        # row
        row = column.row(align=True)

        # vertex groups
        row.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # sub
        sub = row.row(align=True)

        # sub active if vertex group
        sub.active = bool(modifier.vertex_group)

        # invert vertex group
        sub.prop(modifier, 'invert_vertex_group', text='', icon='ARROW_LEFTRIGHT')

        # sub
        sub = column.row()

        # sub active if vertex group
        sub.active = bool(modifier.vertex_group)

        # thickness vertex group
        sub.prop(modifier, 'thickness_vertex_group', text='Factor')

        # label
        column.label(text='Crease:')

        # edge crease inner
        column.prop(modifier, 'edge_crease_inner', text='Inner')

        # edge crease outer
        column.prop(modifier, 'edge_crease_outer', text='Outer')

        # edge crease rim
        column.prop(modifier, 'edge_crease_rim', text='Rim')

        # column
        column = split.column()

        # offset
        column.prop(modifier, 'offset')

        # use flip normals
        column.prop(modifier, 'use_flip_normals')

        # use even offset
        column.prop(modifier, 'use_even_offset')

        # use quality normals
        column.prop(modifier, 'use_quality_normals')

        # use rim
        column.prop(modifier, 'use_rim')

        # sub
        sub = column.column()

        # sub active if use rim
        sub.active = modifier.use_rim

        # use rim only
        sub.prop(modifier, 'use_rim_only')

        # separate
        column.separator()

        # label
        column.label(text='Material Index Offset:')

        # sub
        sub = column.column()

        # row
        row = sub.split(align=True, percentage=0.4)

        # material offset
        row.prop(modifier, 'material_offset', text='')

        # row
        row = row.row(align=True)

        # row active if use rim
        row.active = modifier.use_rim

        # material offset rim
        row.prop(modifier, 'material_offset_rim', text='Rim')

    # subsurf
    def SUBSURF(self, layout, object, modifier):

        # subdivision type
        layout.row().prop(modifier, 'subdivision_type', expand=True)

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Subdivisions:')

        # levels
        column.prop(modifier, 'levels', text='View')

        # render levels
        column.prop(modifier, 'render_levels', text='Render')

        # column
        column = split.column()

        # label
        column.label(text='Options:')

        # use subsurf uv
        column.prop(modifier, 'use_subsurf_uv')

        # show only control edges
        column.prop(modifier, 'show_only_control_edges')

        # has use opensubdiv
        if hasattr(modifier, 'use_opensubdiv'):

            # use opensubdiv
            column.prop(modifier, 'use_opensubdiv')

    # surface
    def SURFACE(self, layout, object, modifier):

        # label
        layout.label(text='Settings are inside the Physics tab')

    # uv project
    def UV_PROJECT(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Image:')

        # image
        column.prop(modifier, 'image', text='')

        # column
        column = split.column()

        # label
        column.label(text='UV Map:')

        # uv textures
        column.prop_search(modifier, 'uv_layer', object.data, 'uv_textures', text='')

        # split
        split = layout.split()

        # column
        column = split.column()

        # use image override
        column.prop(modifier, 'use_image_override')

        # projector count
        column.prop(modifier, 'projector_count', text='Projectors')

        # process projectors
        for proj in modifier.projectors:

            # object
            column.prop(proj, 'object', text='')

        # column
        column = split.column()

        # sub
        sub = column.column(align=True)

        # aspect x
        sub.prop(modifier, 'aspect_x', text='Aspect X')

        # aspect y
        sub.prop(modifier, 'aspect_y', text='Aspect Y')

        # sub
        sub = column.column(align=True)

        # scale x
        sub.prop(modifier, 'scale_x', text='Scale X')

        # scale y
        sub.prop(modifier, 'scale_y', text='Scale Y')

    # warp
    def WARP(self, layout, object, modifier):

        # use falloff
        use_falloff = (modifier.falloff_type != 'NONE')

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='From:')

        # object from
        column.prop(modifier, 'object_from', text='')

        # use volume preserve
        column.prop(modifier, 'use_volume_preserve')

        # column
        column = split.column()

        # label
        column.label(text='To:')

        # object to
        column.prop(modifier, 'object_to', text='')

        # vertex groups
        column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # column
        column = layout.column()

        # row
        row = column.row(align=True)

        # strength
        row.prop(modifier, 'strength')

        # is use falloff
        if use_falloff:

            # falloff radius
            row.prop(modifier, 'falloff_radius')

        # falloff type
        column.prop(modifier, 'falloff_type')

        # is use faloff
        if use_falloff:

            # is falloff type in curve
            if modifier.falloff_type == 'CURVE':

                # falloff curve
                column.template_curve_mapping(modifier, 'falloff_curve')

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Texture:')

        # texture
        column.template_ID(modifier, 'texture', new='texture.new')

        # column
        column = split.column()

        # label
        column.label(text='Texture Coordinates:')

        # texture coords
        column.prop(modifier, 'texture_coords', text='')

        # is texture coords in object
        if modifier.texture_coords == 'OBJECT':

            # texture coords object
            layout.prop(modifier, 'texture_coords_object', text='Object')

        # is texture coords in uv and type in mesh
        elif modifier.texture_coords == 'UV' and object.type == 'MESH':

            # uv layer
            layout.prop_search(modifier, 'uv_layer', object.data, 'uv_textures')

    # wave
    def WAVE(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Motion:')

        # use x
        column.prop(modifier, 'use_x')

        # use y
        column.prop(modifier, 'use_y')

        # use cyclic
        column.prop(modifier, 'use_cyclic')

        # column
        column = split.column()

        # use normal
        column.prop(modifier, 'use_normal')

        # sub
        sub = column.column()

        # use normal
        sub.active = modifier.use_normal

        # use normal x
        sub.prop(modifier, 'use_normal_x', text='X')

        # use normal y
        sub.prop(modifier, 'use_normal_y', text='Y')

        # use normal z
        sub.prop(modifier, 'use_normal_z', text='Z')

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Time:')

        # sub
        sub = column.column(align=True)

        # time offset
        sub.prop(modifier, 'time_offset', text='Offset')

        # lifetime
        sub.prop(modifier, 'lifetime', text='Life')

        # damping time
        column.prop(modifier, 'damping_time', text='Damping')

        # column
        column = split.column()

        # label
        column.label(text='Position:')

        # sub
        sub = column.column(align=True)

        # start position x
        sub.prop(modifier, 'start_position_x', text='X')

        # start position y
        sub.prop(modifier, 'start_position_y', text='Y')

        # falloff radius
        column.prop(modifier, 'falloff_radius', text='Falloff')

        layout.separator()

        # start position object
        layout.prop(modifier, 'start_position_object')

        # vertex group
        layout.prop_search(modifier, 'vertex_group', object, 'vertex_groups')

        # split
        split = layout.split(percentage=0.33)

        # column
        column = split.column()

        # label
        column.label(text='Texture')

        # column
        column = split.column()

        # texture
        column.template_ID(modifier, 'texture', new='texture.new')

        # texture coords
        layout.prop(modifier, 'texture_coords')

        # is texture coords in uv and type in mesh
        if modifier.texture_coords == 'UV' and object.type == 'MESH':

            # uv layer
            layout.prop_search(modifier, 'uv_layer', object.data, 'uv_textures')

        # is texture coords in object
        elif modifier.texture_coords == 'OBJECT':

            # texture coords object
            layout.prop(modifier, 'texture_coords_object')

        # separate
        layout.separator()

        # split
        split = layout.split()

        # column
        column = split.column()

        # speed
        column.prop(modifier, 'speed', slider=True)

        # height
        column.prop(modifier, 'height', slider=True)

        # column
        column = split.column()

        # width
        column.prop(modifier, 'width', slider=True)

        # narrowness
        column.prop(modifier, 'narrowness', slider=True)

    # remesh
    def REMESH(self, layout, object, modifier):

        # mode
        layout.prop(modifier, 'mode')

        # row
        row = layout.row()

        # octree depth
        row.prop(modifier, 'octree_depth')

        # scale
        row.prop(modifier, 'scale')

        # sharp
        if modifier.mode == 'SHARP':

            # sharpness
            layout.prop(modifier, 'sharpness')

        # use smooth shade
        layout.prop(modifier, 'use_smooth_shade')

        # use remove disconnected
        layout.prop(modifier, 'use_remove_disconnected')

        # row
        row = layout.row()

        # row active if use remove disconnected
        row.active = modifier.use_remove_disconnected

        # threshold
        row.prop(modifier, 'threshold')

    # vertex weight mask
    @staticmethod
    def vertex_weight_mask(layout, object, modifier):

        # label
        layout.label(text='Influence/Mask Options:')

        # split
        split = layout.split(percentage=0.4)

        # label
        split.label(text='Global Influence:')

        # mask constant
        split.prop(modifier, 'mask_constant', text='')

        # is not mask texture
        if not modifier.mask_texture:

            # split
            split = layout.split(percentage=0.4)

            # label
            split.label(text='Vertex Group Mask:')

            # vertex groups
            split.prop_search(modifier, 'mask_vertex_group', object, 'vertex_groups', text='')

        # is not mask vertex groups
        if not modifier.mask_vertex_group:

            # split
            split = layout.split(percentage=0.4)

            # label
            split.label(text='Texture Mask:')

            # mask texture
            split.template_ID(modifier, 'mask_texture', new='texture.new')

            # is mask texture
            if modifier.mask_texture:

                # split
                split = layout.split()

                # column
                column = split.column()

                # label
                column.label(text='Texture Coordinates:')

                # mask tex mapping
                column.prop(modifier, 'mask_tex_mapping', text='')

                # column
                column = split.column()

                # label
                column.label(text='Use Channel:')

                # mask tex use channel
                column.prop(modifier, 'mask_tex_use_channel', text='')

                # is mask tex mapping in object
                if modifier.mask_tex_mapping == 'OBJECT':

                    # mask tex map object
                    layout.prop(modifier, 'mask_tex_map_object', text='Object')

                # is mask tex mapping in uv and type in mesh
                elif modifier.mask_tex_mapping == 'UV' and object.type == 'MESH':

                    # mask tex uv layer
                    layout.prop_search(modifier, 'mask_tex_uv_layer', object.data, 'uv_textures')

    # vertex weight edit
    def VERTEX_WEIGHT_EDIT(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Vertex Group:')

        # vertex groups
        column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # label
        column.label(text='Default Weight:')

        # default weight
        column.prop(modifier, 'default_weight', text='')

        # column
        column = split.column()

        # use add
        column.prop(modifier, 'use_add')

        # sub
        sub = column.column()

        # sub active if use add
        sub.active = modifier.use_add

        # add threshold
        sub.prop(modifier, 'add_threshold')

        # column
        column = column.column()

        # use remove
        column.prop(modifier, 'use_remove')

        # sub
        sub = column.column()

        # use remove
        sub.active = modifier.use_remove

        # remove threshold
        sub.prop(modifier, 'remove_threshold')

        # separate
        layout.separator()

        # falloff type
        layout.prop(modifier, 'falloff_type')

        # is falloff type in curve
        if modifier.falloff_type == 'CURVE':

            # map curve
            layout.template_curve_mapping(modifier, 'map_curve')

        # separate
        layout.separator()

        # vertex weight mask
        self.vertex_weight_mask(layout, object, modifier)

    # vertex weight mix
    def VERTEX_WEIGHT_MIX(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Vertex Group A:')

        # vertex groups
        column.prop_search(modifier, 'vertex_group_a', object, 'vertex_groups', text='')

        # label
        column.label(text='Default Weight A:')

        # default weight a
        column.prop(modifier, 'default_weight_a', text='')

        # label
        column.label(text='Mix Mode:')

        # mix mode
        column.prop(modifier, 'mix_mode', text='')

        # column
        column = split.column()

        # label
        column.label(text='Vertex Group B:')

        # vertex groups
        column.prop_search(modifier, 'vertex_group_b', object, 'vertex_groups', text='')

        # label
        column.label(text='Default Weight B:')

        # default weight b
        column.prop(modifier, 'default_weight_b', text='')

        # label
        column.label(text='Mix Set:')

        # mix set
        column.prop(modifier, 'mix_set', text='')

        # separate
        layout.separator()

        # vertex weight mask
        self.vertex_weight_mask(layout, object, modifier)

    # vertex weight proximity
    def VERTEX_WEIGHT_PROXIMITY(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Vertex Group:')

        # vertex groups
        column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # column
        column = split.column()

        # label
        column.label(text='Target Object:')

        # target
        column.prop(modifier, 'target', text='')

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Distance:')

        # proximity mode
        column.prop(modifier, 'proximity_mode', text='')

        # is proximity mode in geometry
        if modifier.proximity_mode == 'GEOMETRY':

            # proximity geometry
            column.row().prop(modifier, 'proximity_geometry')

        # column
        column = split.column()

        # label
        column.label()

        # min dist
        column.prop(modifier, 'min_dist')

        # max dist
        column.prop(modifier, 'max_dist')

        # separate
        layout.separator()

        # falloff type
        layout.prop(modifier, 'falloff_type')

        # Common mask options
        layout.separator()

        # vertex weight edit
        self.vertex_weight_mask(layout, object, modifier)

    # skin
    def SKIN(self, layout, object, modifier):

        # row
        row = layout.row()

        # object skin armature create
        row.operator('object.skin_armature_create', text='Create Armature')

        # mesh customodifierata skin add
        row.operator('mesh.customdata_skin_add')

        # separate
        layout.separator()

        # row
        row = layout.row(align=True)

        # branch smoothing
        row.prop(modifier, 'branch_smoothing')

        # use smooth shade
        row.prop(modifier, 'use_smooth_shade')

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Selected Vertices:')

        # sub
        sub = column.column(align=True)

        # object skin loose mark clear
        sub.operator('object.skin_loose_mark_clear', text='Mark Loose').action = 'MARK'

        # object skin loose mark clear
        sub.operator('object.skin_loose_mark_clear', text='Clear Loose').action = 'CLEAR'

        # sub
        sub = column.column()

        # object skin root mark
        sub.operator('object.skin_root_mark', text='Mark Root')

        # object skin radii equalize
        sub.operator('object.skin_radii_equalize', text='Equalize Radii')

        # column
        column = split.column()

        # label
        column.label(text='Symmetry Axes:')

        # use x symmetry
        column.prop(modifier, 'use_x_symmetry')

        # use y symmetry
        column.prop(modifier, 'use_y_symmetry')

        # use z symmetry
        column.prop(modifier, 'use_z_symmetry')

    # triangulate
    def TRIANGULATE(self, layout, object, modifier):

        # row
        row = layout.row()

        # column
        column = row.column()

        # label
        column.label(text='Quad Method:')

        # quad method
        column.prop(modifier, 'quad_method', text='')

        # column
        column = row.column()

        # label
        column.label(text='Ngon Method:')

        # ngon method
        column.prop(modifier, 'ngon_method', text='')

    # uv warp
    def UV_WARP(self, layout, object, modifier):

        # split
        split = layout.split()

        # column
        column = split.column()

        # center
        column.prop(modifier, 'center')

        # column
        column = split.column()

        # label
        column.label(text='UV Axis:')

        # axis u
        column.prop(modifier, 'axis_u', text='')

        # axis v
        column.prop(modifier, 'axis_v', text='')

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='From:')

        # object from
        column.prop(modifier, 'object_from', text='')

        # column
        column = split.column()

        # label
        column.label(text='To:')

        # object to
        column.prop(modifier, 'object_to', text='')

        # split
        split = layout.split()

        # column
        column = split.column()

        # obj
        obj = modifier.object_from

        # if type in armature
        if obj and obj.type == 'ARMATURE':

            # label
            column.label(text='Bone:')

            # bones
            column.prop_search(modifier, 'bone_from', obj.data, 'bones', text='')

        # column
        column = split.column()

        # obj
        obj = modifier.object_to

        # if type in armature
        if obj and obj.type == 'ARMATURE':

            # label
            column.label(text='Bone:')

            # bones
            column.prop_search(modifier, 'bone_to', obj.data, 'bones', text='')

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Vertex Group:')

        # vertex groups
        column.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # column
        column = split.column()

        # label
        column.label(text='UV Map:')

        # uv textures
        column.prop_search(modifier, 'uv_layer', object.data, 'uv_textures', text='')

    # wireframe
    def WIREFRAME(self, layout, object, modifier):

        # has vgroup
        has_vgroup = bool(modifier.vertex_group)

        # split
        split = layout.split()

        # column
        column = split.column()

        # thickness
        column.prop(modifier, 'thickness', text='Thickness')

        # row
        row = column.row(align=True)

        # vertex groups
        row.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # sub
        sub = row.row(align=True)

        # sub active if has vgroup
        sub.active = has_vgroup

        # invert vertex group
        sub.prop(modifier, 'invert_vertex_group', text='', icon='ARROW_LEFTRIGHT')

        # row
        row = column.row(align=True)

        # row active if has vgroup
        row.active = has_vgroup

        # thickness vertex group
        row.prop(modifier, 'thickness_vertex_group', text='Factor')

        # use crease
        column.prop(modifier, 'use_crease', text='Crease Edges')

        # crease weight
        column.prop(modifier, 'crease_weight', text='Crease Weight')

        # column
        column = split.column()

        # offset
        column.prop(modifier, 'offset')

        # use even offset
        column.prop(modifier, 'use_even_offset', text='Even Thickness')

        # use relative offset
        column.prop(modifier, 'use_relative_offset', text='Relative Thickness')

        # use boundary
        column.prop(modifier, 'use_boundary', text='Boundary')

        # use replace
        column.prop(modifier, 'use_replace', text='Replace Original')

        # material offset
        column.prop(modifier, 'material_offset', text='Material Offset')

    # data transfer
    def DATA_TRANSFER(self, layout, object, modifier):

        # row
        row = layout.row(align=True)

        # object
        row.prop(modifier, 'object')

        # sub
        sub = row.row(align=True)

        # sub active if object
        sub.active = bool(modifier.object)

        # use object transform
        sub.prop(modifier, 'use_object_transform', text='', icon='GROUP')

        # separate
        layout.separator()

        # split
        split = layout.split(0.333)

        # use vert data
        split.prop(modifier, 'use_vert_data')

        # use verts
        use_vert = modifier.use_vert_data

        # row
        row = split.row()

        # row active if use vert
        row.active = use_vert

        # vert mapping
        row.prop(modifier, 'vert_mapping', text='')

        # use vert
        if use_vert:

            # column
            column = layout.column(align=True)

            # split
            split = column.split(0.333, align=True)

            # sub
            sub = split.column(align=True)

            # data types verts vgroup
            sub.prop(modifier, 'data_types_verts_vgroup')

            # row
            row = split.row(align=True)

            # layers vgroup select src
            row.prop(modifier, 'layers_vgroup_select_src', text='')

            # label
            row.label(icon='RIGHTARROW_THIN')

            # layers vgroup select dst
            row.prop(modifier, 'layers_vgroup_select_dst', text='')

            # split
            split = column.split(0.333, align=True)

            # sub
            sub = split.column(align=True)

            # data types verts
            sub.prop(modifier, 'data_types_verts')

        # separato
        layout.separator()

        # split
        split = layout.split(0.333)

        # use edge data
        split.prop(modifier, 'use_edge_data')

        # use edge
        use_edge = modifier.use_edge_data

        # row
        row = split.row()

        # row active if use dodge
        row.active = use_edge

        # edge mapping
        row.prop(modifier, 'edge_mapping', text='')

        # use edge
        if use_edge:


            # column
            column = layout.column(align=True)

            # split
            split = column.split(0.333, align=True)

            # sub
            sub = split.column(align=True)

            # data types edges
            sub.prop(modifier, 'data_types_edges')

        # separate
        layout.separator()

        # split
        split = layout.split(0.333)

        # use loop data
        split.prop(modifier, 'use_loop_data')

        # use loop
        use_loop = modifier.use_loop_data

        # row
        row = split.row()

        # use loop
        row.active = use_loop

        # loop mapping
        row.prop(modifier, 'loop_mapping', text='')

        # use loop
        if use_loop:

            # column
            column = layout.column(align=True)

            # split
            split = column.split(0.333, align=True)

            # sub
            sub = split.column(align=True)

            # data types loops
            sub.prop(modifier, 'data_types_loops')

            # split
            split = column.split(0.333, align=True)

            # sub
            sub = split.column(align=True)

            # data types loops vcol
            sub.prop(modifier, 'data_types_loops_vcol')

            # row
            row = split.row(align=True)

            # layers vcolumn select src
            row.prop(modifier, 'layers_vcol_select_src', text='')

            # label
            row.label(icon='RIGHTARROW')

            # layers vcolumn select dst
            row.prop(modifier, 'layers_vcol_select_dst', text='')

            # split
            split = column.split(0.333, align=True)

            # sub
            sub = split.column(align=True)

            # data types loops uv
            sub.prop(modifier, 'data_types_loops_uv')

            # row
            row = split.row(align=True)

            # layers uv select src
            row.prop(modifier, 'layers_uv_select_src', text='')

            # label
            row.label(icon='RIGHTARROW')

            # layers uv select dst
            row.prop(modifier, 'layers_uv_select_dst', text='')

            # islands precision
            column.prop(modifier, 'islands_precision')

        # separate
        layout.separator()

        # split
        split = layout.split(0.333)

        # use poly data
        split.prop(modifier, 'use_poly_data')

        # use poly
        use_poly = modifier.use_poly_data

        # row
        row = split.row()

        # use only
        row.active = use_poly

        # poly mapping
        row.prop(modifier, 'poly_mapping', text='')

        # use poly
        if use_poly:

            # column
            column = layout.column(align=True)

            # split
            split = column.split(0.333, align=True)

            # sub
            sub = split.column(align=True)

            # data types polys
            sub.prop(modifier, 'data_types_polys')

        # separate
        layout.separator()

        # split
        split = layout.split()

        # column
        column = split.column()

        # row
        row = column.row(align=True)

        # sub
        sub = row.row(align=True)

        # sub active if use max distance
        sub.active = modifier.use_max_distance

        # max distance
        sub.prop(modifier, 'max_distance')

        # use max distance
        row.prop(modifier, 'use_max_distance', text='', icon='STYLUS_PRESSURE')

        # column
        column = split.column()

        # ray radius
        column.prop(modifier, 'ray_radius')

        # separate
        layout.separator()

        # split
        split = layout.split()

        # column
        column = split.column()

        # mix mode
        column.prop(modifier, 'mix_mode')

        # mix factor
        column.prop(modifier, 'mix_factor')

        # column
        column = split.column()

        # row
        row = column.row()

        # row active if object
        row.active = bool(modifier.object)

        # object datalayout transfer
        row.operator('object.datalayout_transfer', text='Generate Data Layers')

        # row
        row = column.row(align=True)

        # vertex groups
        row.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # sub
        sub = row.row(align=True)

        # sub active if vertex group
        sub.active = bool(modifier.vertex_group)

        # invert vertex group
        sub.prop(modifier, 'invert_vertex_group', text='', icon='ARROW_LEFTRIGHT')

    # normal edit
    def NORMAL_EDIT(self, layout, object, modifier):

        # has vgroup
        has_vgroup = bool(modifier.vertex_group)

        # needs object offset
        needs_object_offset = (((modifier.mode == 'RADIAL') and not modifier.target) or
                                                     ((modifier.mode == 'DIRECTIONAL') and modifier.use_direction_parallel))

        # row
        row = layout.row()

        # mode
        row.prop(modifier, 'mode', expand=True)

        # split
        split = layout.split()

        # column
        column = split.column()

        # target
        column.prop(modifier, 'target', text='')

        # sub
        sub = column.column(align=True)

        # sub active if needs object offset
        sub.active = needs_object_offset

        # offset
        sub.prop(modifier, 'offset')

        # row
        row = column.row(align=True)

        # column
        column = split.column()

        # row
        row = column.row()

        # row active if mode in directional
        row.active = (modifier.mode == 'DIRECTIONAL')

        # use direction parallel
        row.prop(modifier, 'use_direction_parallel')

        # column
        sub = column.column(align=True)

        # label
        sub.label('Mix Mode:')

        # mix mode
        sub.prop(modifier, 'mix_mode', text='')

        # mix factor
        sub.prop(modifier, 'mix_factor')

        # row
        row = sub.row(align=True)

        # vertex groups
        row.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # sub
        subsub = row.row(align=True)

        # sub active if has vgroup
        subsub.active = has_vgroup

        # invert vertex group
        subsub.prop(modifier, 'invert_vertex_group', text='', icon='ARROW_LEFTRIGHT')

    # corrective smooth
    def CORRECTIVE_SMOOTH(self, layout, object, modifier):

        # is bind
        is_bind = modifier.is_bind

        # factor
        layout.prop(modifier, 'factor', text='Factor')

        # iterations
        layout.prop(modifier, 'iterations')

        # row
        row = layout.row()

        # smooth type
        row.prop(modifier, 'smooth_type')

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Vertex Group:')

        # row
        row = column.row(align=True)

        # vertex groups
        row.prop_search(modifier, 'vertex_group', object, 'vertex_groups', text='')

        # invert vertex group
        row.prop(modifier, 'invert_vertex_group', text='', icon='ARROW_LEFTRIGHT')

        # column
        column = split.column()

        # use only smooth
        column.prop(modifier, 'use_only_smooth')

        # use pin boundary
        column.prop(modifier, 'use_pin_boundary')

        # rest source
        layout.prop(modifier, 'rest_source')

        # is rest source in bind
        if modifier.rest_source == 'BIND':

            # object correctivesmooth bind
            layout.operator('object.correctivesmooth_bind', text='Unbind' if is_bind else 'Bind')
