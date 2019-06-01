
# constraint
class Constraint:
    '''
        The UI settings for the constraints.
    '''

    # main
    def main(self, context, layout, constraint):

        # row
        row = layout.row(align=True)

        # name
        row.prop(constraint, 'name', text='')

        # context pointer set
        row.context_pointer_set('constraint', constraint)

        # is not first
        if constraint != constraint.id_data.constraints[0]:

            # move up
            row.operator('constraint.move_up', text='', icon='TRIA_UP')

        # is not last
        if constraint != constraint.id_data.constraints[len(constraint.id_data.constraints)-1]:

            # move down
            row.operator('constraint.move_down', text='', icon='TRIA_DOWN')

        # delete
        row.operator('constraint.delete', text='', icon='X')

        # column
        column = layout.column()

        getattr(Constraint, constraint.type)(Constraint, context, column, constraint)

        # is constraint has influence
        if constraint.type not in {'RIGID_BODY_JOINT', 'NULL'}:

            # separate
            column.separator()

            # influence
            column.prop(constraint, 'influence')

    # space template
    @staticmethod
    def space_template(layout, constraint, target=True, owner=True):

        # is target or owner
        if target or owner:

            # split
            split = layout.split(percentage=0.2)

            # label
            split.label(text='Space:')

            # row
            row = split.row()

            # is target
            if target:

                # target space
                row.prop(constraint, 'target_space', text='')

            # is target and owner
            if target and owner:

                # label
                row.label(icon='ARROW_LEFTRIGHT')

            # is owner
            if owner:

                # owner space
                row.prop(constraint, 'owner_space', text='')

    # target template
    @staticmethod
    def target_template(layout, constraint, subtargets=True):

        # target
        layout.prop(constraint, 'target')    # XXX limiting settings for only 'curves' or some type of object

        # is contraint target and sub target
        if constraint.target and subtargets:

            # is target in armature
            if constraint.target.type == 'ARMATURE':

                # subtarget
                layout.prop_search(constraint, 'subtarget', constraint.target.data, 'bones', text='Bone')

                # has head tail
                if hasattr(constraint, 'head_tail'):

                    # row
                    row = layout.row()

                    # label
                    row.label(text='Head/Tail:')

                    # head tail
                    row.prop(constraint, 'head_tail', text='')

            # is target in mesh or lattice
            elif constraint.target.type in {'MESH', 'LATTICE'}:

                # subtarget
                layout.prop_search(constraint, 'subtarget', constraint.target, 'vertex_groups', text='Vertex Group')

    # ik tamplate
    @staticmethod
    def ik_template(layout, constraint):

        # pole target
        layout.prop(constraint, 'pole_target')

        # is target and it in aramture
        if constraint.pole_target and constraint.pole_target.type == 'ARMATURE':

            # pole subtarget
            layout.prop_search(constraint, 'pole_subtarget', constraint.pole_target.data, 'bones', text='Bone')

        # is pole target
        if constraint.pole_target:

            # row
            row = layout.row()

            # label
            row.label()

            # pole target
            row.prop(constraint, 'pole_angle')

        # split
        split = layout.split(percentage=0.33)

        # column
        column = split.column()

        # use tail
        column.prop(constraint, 'use_tail')

        # use stretch
        column.prop(constraint, 'use_stretch')

        # column
        column = split.column()

        # chain count
        column.prop(constraint, 'chain_count')

    # child of
    def CHILD_OF(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Location:')

        # use location x
        column.prop(constraint, 'use_location_x', text='X')

        # use location y
        column.prop(constraint, 'use_location_y', text='Y')

        # use location z
        column.prop(constraint, 'use_location_z', text='Z')

        # column
        column = split.column()

        # label
        column.label(text='Rotation:')

        # use rotation x
        column.prop(constraint, 'use_rotation_x', text='X')

        # use rotation y
        column.prop(constraint, 'use_rotation_y', text='Y')

        # use rotation z
        column.prop(constraint, 'use_rotation_z', text='Z')

        # column
        column = split.column()

        # label
        column.label(text='Scale:')

        # use scale x
        column.prop(constraint, 'use_scale_x', text='X')

        # use scale y
        column.prop(constraint, 'use_scale_y', text='Y')

        # use scale z
        column.prop(constraint, 'use_scale_z', text='Z')

        # row
        row = layout.row()

        # constraint child of set inverse
        row.operator('constraint.childof_set_inverse')

        # constraint child of clear inverse
        row.operator('constraint.childof_clear_inverse')

    # track to
    def TRACK_TO(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # row
        row = layout.row()

        # label
        row.label(text='To:')

        # track axis
        row.prop(constraint, 'track_axis', expand=True)

        # row
        row = layout.row()

        # up axis
        row.prop(constraint, 'up_axis', text='Up')

        # use target
        row.prop(constraint, 'use_target_z')

        # space template
        self.space_template(layout, constraint)

    # ik
    def IK(self, context, layout, constraint):

        # is ik solver in iTaSC
        if context.object.pose.ik_solver == 'ITASC':

            # ik type
            layout.prop(constraint, 'ik_type')
            getattr(self, 'IK_' + constraint.ik_type)(context, layout, constraint)

        # isnt ik solver in iTaSC
        else:

            # target template
            self.target_template(layout, constraint)

            # pole target
            layout.prop(constraint, 'pole_target')

            # is pole target and pole target in armature
            if constraint.pole_target and constraint.pole_target.type == 'ARMATURE':

                # pole subtarget
                layout.prop_search(constraint, 'pole_subtarget', constraint.pole_target.data, 'bones', text='Bone')

            # is poe target
            if constraint.pole_target:

                # row
                row = layout.row()

                # pole angle
                row.prop(constraint, 'pole_angle')

                # label
                row.label()

            # split
            split = layout.split()

            # column
            column = split.column()

            # iterations
            column.prop(constraint, 'iterations')

            # chain count
            column.prop(constraint, 'chain_count')

            # column
            column = split.column()

            # use tail
            column.prop(constraint, 'use_tail')

            # use stretch
            column.prop(constraint, 'use_stretch')

            # label
            layout.label(text='Weight:')

            # split
            split = layout.split()

            # column
            column = split.column()

            # row
            row = column.row(align=True)

            # use location
            row.prop(constraint, 'use_location', text='')

            # sub
            sub = row.row(align=True)

            # sub active if use location
            sub.active = constraint.use_location

            # weight
            sub.prop(constraint, 'weight', text='Position', slider=True)

            # column
            column = split.column()

            # row
            row = column.row(align=True)

            # use rotation
            row.prop(constraint, 'use_rotation', text='')

            # sub
            sub = row.row(align=True)

            # sub active if use rotation
            sub.active = constraint.use_rotation

            # orient weight
            sub.prop(constraint, 'orient_weight', text='Rotation', slider=True)

    # ik copy pose
    def IK_COPY_POSE(self, context, layout, constraint):

        # target templat
        self.target_template(layout, constraint)

        # ik template
        self.ik_template(layout, constraint)

        # row
        row = layout.row()

        # label
        row.label(text='Axis Ref:')

        # reference axis
        row.prop(constraint, 'reference_axis', expand=True)

        # split
        split = layout.split(percentage=0.33)

        # use location
        split.row().prop(constraint, 'use_location')

        # row
        row = split.row()

        # row active if use location
        row.active = constraint.use_location

        # weigth
        row.prop(constraint, 'weight', text='Weight', slider=True)

        # split
        split = layout.split(percentage=0.33)

        # split active if use location
        split.active = constraint.use_location

        # row
        row = split.row()

        # label
        row.label(text='Lock:')

        # row
        row = split.row()

        # lock location x
        row.prop(constraint, 'lock_location_x', text='X')

        # lock location y
        row.prop(constraint, 'lock_location_y', text='Y')

        # lock location z
        row.prop(constraint, 'lock_location_z', text='Z')

        # split
        split = layout.split(percentage=0.33)

        # use rotation
        split.row().prop(constraint, 'use_rotation')

        # row
        row = split.row()

        # row active if use rotation
        row.active = constraint.use_rotation

        # orient weight
        row.prop(constraint, 'orient_weight', text='Weight', slider=True)

        # split
        split = layout.split(percentage=0.33)

        # split active if use rotation
        split.active = constraint.use_rotation

        # row
        row = split.row()

        # label
        row.label(text='Lock:')

        # row
        row = split.row()

        # lock rotation x
        row.prop(constraint, 'lock_rotation_x', text='X')

        # lock rotation y
        row.prop(constraint, 'lock_rotation_y', text='Y')

        # lock rotation z
        row.prop(constraint, 'lock_rotation_z', text='Z')

    # ik distance
    def IK_DISTANCE(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # ik template
        self.ik_template(layout, constraint)

        # limit mode
        layout.prop(constraint, 'limit_mode')

        # row
        row = layout.row()

        # weight
        row.prop(constraint, 'weight', text='Weight', slider=True)

        # distance
        row.prop(constraint, 'distance', text='Distance', slider=True)

    # follow path
    def FOLLOW_PATH(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # constraint follow path, path animate
        layout.operator('constraint.followpath_path_animate', text='Animate Path', icon='ANIM_DATA')

        # plsit
        split = layout.split()

        # column
        column = split.column()

        # use curve follow
        column.prop(constraint, 'use_curve_follow')

        # use curve radius
        column.prop(constraint, 'use_curve_radius')

        # column
        column = split.column()

        # use fixed location
        column.prop(constraint, 'use_fixed_location')

        # is use fixed location
        if constraint.use_fixed_location:

            # offset factor
            column.prop(constraint, 'offset_factor', text='Offset')

        # isnt use fixed location
        else:

            # offset
            column.prop(constraint, 'offset')

        # row
        row = layout.row()

        # label
        row.label(text='Forward:')

        # forward axis
        row.prop(constraint, 'forward_axis', expand=True)

        # row
        row = layout.row()

        # up axis
        row.prop(constraint, 'up_axis', text='Up')

        # separate
        layout.separator()

    # limit rotation
    def LIMIT_ROTATION(self, context, layout, constraint):

        # split
        split = layout.split()

        # column
        column = split.column(align=True)

        # use limit x
        column.prop(constraint, 'use_limit_x')

        # sub
        sub = column.column(align=True)

        # sub active if use limit x
        sub.active = constraint.use_limit_x

        # min x
        sub.prop(constraint, 'min_x', text='Min')

        # max x
        sub.prop(constraint, 'max_x', text='Max')

        # column
        column = split.column(align=True)

        # use limit y
        column.prop(constraint, 'use_limit_y')

        # sub
        sub = column.column(align=True)

        # sub active if use limit y
        sub.active = constraint.use_limit_y

        # min y
        sub.prop(constraint, 'min_y', text='Min')

        # max y
        sub.prop(constraint, 'max_y', text='Max')

        # column
        column = split.column(align=True)

        # use limit z
        column.prop(constraint, 'use_limit_z')

        # sub
        sub = column.column(align=True)

        # sub active if use limit z
        sub.active = constraint.use_limit_z

        # min z
        sub.prop(constraint, 'min_z', text='Min')

        # max z
        sub.prop(constraint, 'max_z', text='Max')

        # use transform limit
        layout.prop(constraint, 'use_transform_limit')

        # row
        row = layout.row()

        # label
        row.label(text='Convert:')

        # owner space
        row.prop(constraint, 'owner_space', text='')

    # limit location
    def LIMIT_LOCATION(self, context, layout, constraint):

        # split
        split = layout.split()

        # column
        column = split.column()

        # use min x
        column.prop(constraint, 'use_min_x')

        # sub
        sub = column.column()

        # sub active if use min x
        sub.active = constraint.use_min_x

        # min x
        sub.prop(constraint, 'min_x', text='')

        # use max x
        column.prop(constraint, 'use_max_x')

        # sub
        sub = column.column()

        # sub active if use max x
        sub.active = constraint.use_max_x

        # max x
        sub.prop(constraint, 'max_x', text='')

        # column
        column = split.column()

        # use min y
        column.prop(constraint, 'use_min_y')

        # sub
        sub = column.column()

        # use min y
        sub.active = constraint.use_min_y

        # min y
        sub.prop(constraint, 'min_y', text='')

        # use max y
        column.prop(constraint, 'use_max_y')

        # sub
        sub = column.column()

        # sub active if use max y
        sub.active = constraint.use_max_y

        # max y
        sub.prop(constraint, 'max_y', text='')

        # column
        column = split.column()

        # use min z
        column.prop(constraint, 'use_min_z')

        # sub
        sub = column.column()

        # sub active if use min z
        sub.active = constraint.use_min_z

        # min z
        sub.prop(constraint, 'min_z', text='')

        # use max z
        column.prop(constraint, 'use_max_z')

        # sub
        sub = column.column()

        # sub active if use max z
        sub.active = constraint.use_max_z

        # max z
        sub.prop(constraint, 'max_z', text='')

        # row
        row = layout.row()

        # use transform limit
        row.prop(constraint, 'use_transform_limit')

        # separate
        layout.separator()

        # row
        row = layout.row()

        # label
        row.label(text='Convert:')

        # owner space
        row.prop(constraint, 'owner_space', text='')

    # limit scale
    def LIMIT_SCALE(self, context, layout, constraint):

        # split
        split = layout.split()

        # column
        column = split.column()

        # use min x
        column.prop(constraint, 'use_min_x')

        # sub
        sub = column.column()

        # sub active if use min x
        sub.active = constraint.use_min_x

        # min x
        sub.prop(constraint, 'min_x', text='')

        # use max x
        column.prop(constraint, 'use_max_x')

        # sub
        sub = column.column()

        # sub active if use max x
        sub.active = constraint.use_max_x

        # max x
        sub.prop(constraint, 'max_x', text='')

        # column
        column = split.column()

        # use min y
        column.prop(constraint, 'use_min_y')

        # sub
        sub = column.column()

        # sub active if use min y
        sub.active = constraint.use_min_y

        # min y
        sub.prop(constraint, 'min_y', text='')

        # use max y
        column.prop(constraint, 'use_max_y')

        # sub
        sub = column.column()

        # sub active
        sub.active = constraint.use_max_y

        # max y
        sub.prop(constraint, 'max_y', text='')

        # column
        column = split.column()

        # use min z
        column.prop(constraint, 'use_min_z')

        # sub
        sub = column.column()

        # sub active if use min z
        sub.active = constraint.use_min_z

        # min z
        sub.prop(constraint, 'min_z', text='')

        # use max z
        column.prop(constraint, 'use_max_z')

        # sub
        sub = column.column()

        # sub active if use max z
        sub.active = constraint.use_max_z

        # max z
        sub.prop(constraint, 'max_z', text='')

        # row
        row = layout.row()

        # use transform limit
        row.prop(constraint, 'use_transform_limit')

        # separate
        layout.separator()

        # row
        row = layout.row()

        # label
        row.label(text='Convert:')

        # owner space
        row.prop(constraint, 'owner_space', text='')

    # copy rotation
    def COPY_ROTATION(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # split
        split = layout.split()

        # column
        column = split.column()

        # use x
        column.prop(constraint, 'use_x', text='X')

        # sub
        sub = column.column()

        # sub active if use x
        sub.active = constraint.use_x

        # invert x
        sub.prop(constraint, 'invert_x', text='Invert')

        # column
        column = split.column()

        # use y
        column.prop(constraint, 'use_y', text='Y')

        # sub
        sub = column.column()

        # sub active if use y
        sub.active = constraint.use_y

        # invert y
        sub.prop(constraint, 'invert_y', text='Invert')

        # column
        column = split.column()

        # use z
        column.prop(constraint, 'use_z', text='Z')

        # sub
        sub = column.column()

        # sub active if use z
        sub.active = constraint.use_z

        # invert z
        sub.prop(constraint, 'invert_z', text='Invert')

        # use offset
        layout.prop(constraint, 'use_offset')

        # space template
        self.space_template(layout, constraint)

    # copy location
    def COPY_LOCATION(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # split
        split = layout.split()

        # column
        column = split.column()

        # use x
        column.prop(constraint, 'use_x', text='X')

        # sub
        sub = column.column()

        # sub active if use x
        sub.active = constraint.use_x

        # invert x
        sub.prop(constraint, 'invert_x', text='Invert')

        # column
        column = split.column()

        # use y
        column.prop(constraint, 'use_y', text='Y')

        # sub
        sub = column.column()

        # sub active if use y
        sub.active = constraint.use_y

        # invert y
        sub.prop(constraint, 'invert_y', text='Invert')

        # column
        column = split.column()

        # use z
        column.prop(constraint, 'use_z', text='Z')

        # sub
        sub = column.column()

        # sub active if use z
        sub.active = constraint.use_z

        # invert z
        sub.prop(constraint, 'invert_z', text='Invert')

        # use offset
        layout.prop(constraint, 'use_offset')

        # space template
        self.space_template(layout, constraint)

    # copy scale
    def COPY_SCALE(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # row
        row = layout.row(align=True)

        # use x
        row.prop(constraint, 'use_x', text='X')

        # use y
        row.prop(constraint, 'use_y', text='Y')

        # use z
        row.prop(constraint, 'use_z', text='Z')

        # use offset
        layout.prop(constraint, 'use_offset')

        # space template
        self.space_template(layout, constraint)

    # maintain volume
    def MAINTAIN_VOLUME(self, context, layout, constraint):

        # row
        row = layout.row()

        # label
        row.label(text='Free:')

        # free axis
        row.prop(constraint, 'free_axis', expand=True)

        # volume
        layout.prop(constraint, 'volume')

        # row
        row = layout.row()

        # label
        row.label(text='Convert:')

        # owner space
        row.prop(constraint, 'owner_space', text='')

    # copy transform
    def COPY_TRANSFORMS(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # space template
        self.space_template(layout, constraint)

    # action
    def ACTION(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='From Target:')

        # transform channel
        column.prop(constraint, 'transform_channel', text='')

        # target space
        column.prop(constraint, 'target_space', text='')

        # column
        column = split.column()

        # label
        column.label(text='To Action:')

        # action
        column.prop(constraint, 'action', text='')

        # use bone object action
        column.prop(constraint, 'use_bone_object_action')

        # split
        split = layout.split()

        # column
        column = split.column(align=True)

        # label
        column.label(text='Target Range:')

        # min
        column.prop(constraint, 'min', text='Min')

        # max
        column.prop(constraint, 'max', text='Max')

        # column
        column = split.column(align=True)

        # label
        column.label(text='Action Range:')

        # frame start
        column.prop(constraint, 'frame_start', text='Start')

        # frame end
        column.prop(constraint, 'frame_end', text='End')

    # locked track
    def LOCKED_TRACK(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # row
        row = layout.row()

        # label
        row.label(text='To:')

        # track axis
        row.prop(constraint, 'track_axis', expand=True)

        # row
        row = layout.row()

        # label
        row.label(text='Lock:')

        # lock axis
        row.prop(constraint, 'lock_axis', expand=True)

    # limit distance
    def LIMIT_DISTANCE(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # column
        column = layout.column(align=True)

        # distance
        column.prop(constraint, 'distance')

        # constraint limit distance reset
        column.operator('constraint.limitdistance_reset')

        # row
        row = layout.row()

        # label
        row.label(text='Clamp Region:')

        # limit mode
        row.prop(constraint, 'limit_mode', text='')

        # row
        row = layout.row()

        # use transform limit
        row.prop(constraint, 'use_transform_limit')

        # separate
        layout.separator()

        # space template
        self.space_template(layout, constraint)

    # stretch to
    def STRETCH_TO(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # row
        row = layout.row()

        # rest length
        row.prop(constraint, 'rest_length', text='Rest Length')

        # constraint stretch to reset
        row.operator('constraint.stretchto_reset', text='Reset')

        # blge
        layout.prop(constraint, 'bulge', text='Volume Variation')

        # split
        split = layout.split()

        # column
        column = split.column(align=True)

        # use bulge min
        column.prop(constraint, 'use_bulge_min', text='Volume Min')

        # sub
        sub = column.column()

        # sub active if use bulge min
        sub.active = constraint.use_bulge_min

        # bulge min
        sub.prop(constraint, 'bulge_min', text='')

        # column
        column = split.column(align=True)

        # use bulge max
        column.prop(constraint, 'use_bulge_max', text='Volume Max')

        # sub
        sub = column.column()

        # sub active if use bulge max
        sub.active = constraint.use_bulge_max

        # bulge max
        sub.prop(constraint, 'bulge_max', text='')

        # column
        column = layout.column()

        # column active if use bulge min or use bulge max
        column.active = constraint.use_bulge_min or constraint.use_bulge_max

        # bulge smooth
        column.prop(constraint, 'bulge_smooth', text='Smooth')

        # row
        row = layout.row()

        # label
        row.label(text='Volume:')

        # volume
        row.prop(constraint, 'volume', expand=True)

        # label
        row.label(text='Plane:')

        # keep axis
        row.prop(constraint, 'keep_axis', expand=True)

    # floor
    def FLOOR(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # row
        row = layout.row()

        # use sticky
        row.prop(constraint, 'use_sticky')

        # use rotation
        row.prop(constraint, 'use_rotation')

        # offset
        layout.prop(constraint, 'offset')

        # row
        row = layout.row()

        # label
        row.label(text='Min/Max:')

        # floor location
        row.prop(constraint, 'floor_location', expand=True)

        # space template
        self.space_template(layout, constraint)

    # rigid body joint
    def RIGID_BODY_JOINT(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint, subtargets=False)

        # pivot type
        layout.prop(constraint, 'pivot_type')

        # child
        layout.prop(constraint, 'child')

        # row
        row = layout.row()

        # use linked collision
        row.prop(constraint, 'use_linked_collision', text='Linked Collision')

        # show pivot
        row.prop(constraint, 'show_pivot', text='Display Pivot')

        # split
        split = layout.split()

        # column
        column = split.column(align=True)

        # label
        column.label(text='Pivot:')

        # pivot x
        column.prop(constraint, 'pivot_x', text='X')

        # pivot y
        column.prop(constraint, 'pivot_y', text='Y')

        # pivot z
        column.prop(constraint, 'pivot_z', text='Z')

        # column
        column = split.column(align=True)

        # label
        column.label(text='Axis:')

        # axis x
        column.prop(constraint, 'axis_x', text='X')

        # axis y
        column.prop(constraint, 'axis_y', text='Y')

        # axis z
        column.prop(constraint, 'axis_z', text='Z')

        # is pivot type in cone twist
        if constraint.pivot_type == 'CONE_TWIST':

            # label
            layout.label(text='Limits:')

            # split
            split = layout.split()

            # column
            column = split.column()

            # use angular limit x
            column.prop(constraint, 'use_angular_limit_x', text='Angle X')

            # sub
            sub = column.column()

            # sub active if use angular limit x
            sub.active = constraint.use_angular_limit_x

            # limit angle max x
            sub.prop(constraint, 'limit_angle_max_x', text='')

            # column
            column = split.column()

            # use angular limit y
            column.prop(constraint, 'use_angular_limit_y', text='Angle Y')

            # sub
            sub = column.column()

            # use angular limit y
            sub.active = constraint.use_angular_limit_y

            # limit nagle max y
            sub.prop(constraint, 'limit_angle_max_y', text='')

            # column
            column = split.column()

            # use angular limit z
            column.prop(constraint, 'use_angular_limit_z', text='Angle Z')

            # sub
            sub = column.column()

            # sub active if use angular limit z
            sub.active = constraint.use_angular_limit_z

            # limit angle max z
            sub.prop(constraint, 'limit_angle_max_z', text='')

        # is pivot type in generic 6 dof
        elif constraint.pivot_type == 'GENERIC_6_DOF':

            # label
            layout.label(text='Limits:')

            # split
            split = layout.split()

            # column
            column = split.column(align=True)

            # use limit x
            column.prop(constraint, 'use_limit_x', text='X')

            # sub
            sub = column.column(align=True)

            # sub active if use limit x
            sub.active = constraint.use_limit_x

            # limit min x
            sub.prop(constraint, 'limit_min_x', text='Min')

            # limit max s
            sub.prop(constraint, 'limit_max_x', text='Max')

            # column
            column = split.column(align=True)

            # use limit y
            column.prop(constraint, 'use_limit_y', text='Y')

            # sub
            sub = column.column(align=True)

            # sub active if use limit y
            sub.active = constraint.use_limit_y

            # limit min y
            sub.prop(constraint, 'limit_min_y', text='Min')

            # limit max y
            sub.prop(constraint, 'limit_max_y', text='Max')

            # column
            column = split.column(align=True)

            # use limit z
            column.prop(constraint, 'use_limit_z', text='Z')

            # sub
            sub = column.column(align=True)

            # sub active if use limit z
            sub.active = constraint.use_limit_z

            # limit min z
            sub.prop(constraint, 'limit_min_z', text='Min')

            # limit max z
            sub.prop(constraint, 'limit_max_z', text='Max')

            # split
            split = layout.split()

            # column
            column = split.column(align=True)

            # use angular limit x
            column.prop(constraint, 'use_angular_limit_x', text='Angle X')

            # sub
            sub = column.column(align=True)

            # sub active if use angular limit x
            sub.active = constraint.use_angular_limit_x

            # limit angle min x
            sub.prop(constraint, 'limit_angle_min_x', text='Min')

            # limit angle max x
            sub.prop(constraint, 'limit_angle_max_x', text='Max')

            # column
            column = split.column(align=True)

            # use angular limit y
            column.prop(constraint, 'use_angular_limit_y', text='Angle Y')

            # sub
            sub = column.column(align=True)

            # sub active if use angular limit y
            sub.active = constraint.use_angular_limit_y

            # limit angle min y
            sub.prop(constraint, 'limit_angle_min_y', text='Min')

            # limit angle max y
            sub.prop(constraint, 'limit_angle_max_y', text='Max')

            # column
            column = split.column(align=True)

            # use angular limit z
            column.prop(constraint, 'use_angular_limit_z', text='Angle Z')

            # sub
            sub = column.column(align=True)

            # sub active if use angular limit z
            sub.active = constraint.use_angular_limit_z

            # limit angle min z
            sub.prop(constraint, 'limit_angle_min_z', text='Min')

            # limit angle max z
            sub.prop(constraint, 'limit_angle_max_z', text='Max')

        # is pivot type in hinge
        elif constraint.pivot_type == 'HINGE':

            # label
            layout.label(text='Limits:')

            # split
            split = layout.split()

            # row
            row = split.row(align=True)

            # column
            column = row.column()

            # use angular limit x
            column.prop(constraint, 'use_angular_limit_x', text='Angle X')

            # column
            column = row.column()

            # column active if use angular limit x
            column.active = constraint.use_angular_limit_x

            # limit angle min x
            column.prop(constraint, 'limit_angle_min_x', text='Min')

            # column
            column = row.column()

            # column active if use angular x
            column.active = constraint.use_angular_limit_x

            # limit angle max x
            column.prop(constraint, 'limit_angle_max_x', text='Max')

    # clamp to
    def CLAMP_TO(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # row
        row = layout.row()

        # label
        row.label(text='Main Axis:')

        # main axis
        row.prop(constraint, 'main_axis', expand=True)

        # use cyclic
        layout.prop(constraint, 'use_cyclic')

    # transform
    def TRANSFORM(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # use motion extrapolate
        layout.prop(constraint, 'use_motion_extrapolate', text='Extrapolate')

        # column
        column = layout.column()

        # label
        column.row().label(text='Source:')

        # map from
        column.row().prop(constraint, 'map_from', expand=True)

        # split
        split = layout.split()

        # ext
        ext = '' if constraint.map_from == 'LOCATION' else '_rot' if constraint.map_from == 'ROTATION' else '_scale'

        # sub
        sub = split.column(align=True)

        # label
        sub.label(text='X:')

        # from min x
        sub.prop(constraint, 'from_min_x' + ext, text='Min')

        # from max x
        sub.prop(constraint, 'from_max_x' + ext, text='Max')

        # sub
        sub = split.column(align=True)

        # label
        sub.label(text='Y:')

        # from min y
        sub.prop(constraint, 'from_min_y' + ext, text='Min')

        # from max y
        sub.prop(constraint, 'from_max_y' + ext, text='Max')

        # sub
        sub = split.column(align=True)

        # label
        sub.label(text='Z:')

        # from min z
        sub.prop(constraint, 'from_min_z' + ext, text='Min')

        # from max z
        sub.prop(constraint, 'from_max_z' + ext, text='Max')

        # column
        column = layout.column()

        # row
        row = column.row()

        # label
        row.label(text='Source to Destination Mapping:')

        # row
        row = column.row()

        # map to x from
        row.prop(constraint, 'map_to_x_from', expand=False, text='')

        # label
        row.label(text=' %s        X' % chr(187)) # note: chr(187) is the ASCII arrow ( >> ). Blender Text Editor can't open it. Thus we are using the hard-coded value instead.

        # row
        row = column.row()

        # map to y from
        row.prop(constraint, 'map_to_y_from', expand=False, text='')

        # label
        row.label(text=' %s        Y' % chr(187))

        # row
        row = column.row()

        # map to z from
        row.prop(constraint, 'map_to_z_from', expand=False, text='')

        # label
        row.label(text=' %s        Z' % chr(187))

        # split
        split = layout.split()

        # column
        column = split.column()

        # label
        column.label(text='Destination:')

        # map to
        column.row().prop(constraint, 'map_to', expand=True)

        # split
        split = layout.split()

        # ext
        ext = '' if constraint.map_to == 'LOCATION' else '_rot' if constraint.map_to == 'ROTATION' else '_scale'

        # column
        column = split.column()

        # label
        column.label(text='X:')

        # sub
        sub = column.column(align=True)

        # to min x
        sub.prop(constraint, 'to_min_x' + ext, text='Min')

        # to max x
        sub.prop(constraint, 'to_max_x' + ext, text='Max')

        # column
        column = split.column()

        # label
        column.label(text='Y:')

        # sub
        sub = column.column(align=True)

        # to min y
        sub.prop(constraint, 'to_min_y' + ext, text='Min')

        # to max y
        sub.prop(constraint, 'to_max_y' + ext, text='Max')

        # column
        column = split.column()

        # label
        column.label(text='Z:')

        # sub
        sub = column.column(align=True)

        # to min z
        sub.prop(constraint, 'to_min_z' + ext, text='Min')

        # to max z
        sub.prop(constraint, 'to_max_z' + ext, text='Max')

        # space template
        self.space_template(layout, constraint)

    # shrinkwrap
    def SHRINKWRAP(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint, False)

        # distance
        layout.prop(constraint, 'distance')

        # shrinkwrap type
        layout.prop(constraint, 'shrinkwrap_type')

        # is shrinkwarp type in project
        if constraint.shrinkwrap_type == 'PROJECT':

            # row
            row = layout.row(align=True)

            # project axis
            row.prop(constraint, 'project_axis', expand=True)

            # split
            split = layout.split(percentage=0.4)

            # label
            split.label(text='Axis Space:')

            # sub
            sub = split.row()

            # project axis space
            sub.prop(constraint, 'project_axis_space', text='')

            # project limit
            layout.prop(constraint, 'project_limit')

    # damped track
    def DAMPED_TRACK(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # row
        row = layout.row()

        # label
        row.label(text='To:')

        # track axis
        row.prop(constraint, 'track_axis', expand=True)

    # spline ik
    def SPLINE_IK(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # column
        column = layout.column()

        # label
        column.label(text='Spline Fitting:')

        # chain count
        column.prop(constraint, 'chain_count')

        # use even divisions
        column.prop(constraint, 'use_even_divisions')

        # use chain offset
        column.prop(constraint, 'use_chain_offset')

        # column
        column = layout.column()

        # label
        column.label(text='Chain Scaling:')

        # use y stretch
        column.prop(constraint, 'use_y_stretch')

        # use curve radius
        column.prop(constraint, 'use_curve_radius')

        # xz scale mode
        layout.prop(constraint, 'xz_scale_mode')

        # is xz scale mode in volume preserve
        if constraint.xz_scale_mode == 'VOLUME_PRESERVE':

            # bulge
            layout.prop(constraint, 'bulge', text='Volume Variation')

            # split
            split = layout.split()

            # column
            column = split.column(align=True)

            # use bulge min
            column.prop(constraint, 'use_bulge_min', text='Volume Min')

            # sub
            sub = column.column()

            # sub active if use bulge min
            sub.active = constraint.use_bulge_min

            # bulge min
            sub.prop(constraint, 'bulge_min', text='')

            # column
            column = split.column(align=True)

            # use bulge max
            column.prop(constraint, 'use_bulge_max', text='Volume Max')

            # sub
            sub = column.column()

            # sub active use bulge max
            sub.active = constraint.use_bulge_max

            # bulge max
            sub.prop(constraint, 'bulge_max', text='')

            # olumn
            column = layout.column()

            # column active if use bulge min or use bulge max
            column.active = constraint.use_bulge_min or constraint.use_bulge_max

            # bulge smooth
            column.prop(constraint, 'bulge_smooth', text='Smooth')

    # pivot
    def PIVOT(self, context, layout, constraint):

        # target template
        self.target_template(layout, constraint)

        # target
        if constraint.target:

            # column
            column = layout.column()

            # offset
            column.prop(constraint, 'offset', text='Pivot Offset')

        # isnt target
        else:

            # column
            column = layout.column()

            # use relative location
            column.prop(constraint, 'use_relative_location')

            # is use relative location
            if constraint.use_relative_location:

                # offset
                column.prop(constraint, 'offset', text='Relative Pivot Point')

            # isnt use relative location
            else:

                # offset
                column.prop(constraint, 'offset', text='Absolute Pivot Point')

        # column
        column = layout.column()

        # rotation range
        column.prop(constraint, 'rotation_range', text='Pivot When')

    # get constraint clip
    @staticmethod
    def _getConstraintClip(context, constraint):

        # isnt use active clip
        if not constraint.use_active_clip:
            return constraint.clip

        # is use active clip
        else:
            return context.scene.active_clip

    # follow track
    def FOLLOW_TRACK(self, context, layout, constraint):

        # clip
        clip = self._getConstraintClip(context, constraint)

        # row
        row = layout.row()

        # use active clip
        row.prop(constraint, 'use_active_clip')

        # use 3d position
        row.prop(constraint, 'use_3d_position')

        # sub
        sub = row.column()

        # sub active if use 3d position
        sub.active = not constraint.use_3d_position

        # use undistorted position
        sub.prop(constraint, 'use_undistorted_position')

        # column
        column = layout.column()

        # is use active clip
        if not constraint.use_active_clip:

            # clip
            column.prop(constraint, 'clip')

        # row
        row = column.row()

        # frame method
        row.prop(constraint, 'frame_method', expand=True)

        # is clip
        if clip:

            # tracking
            tracking = clip.tracking

            # object
            column.prop_search(constraint, 'object', tracking, 'objects', icon='OBJECT_DATA')

            # tracking object
            tracking_object = tracking.objects.get(constraint.object, tracking.objects[0])

            # track
            column.prop_search(constraint, 'track', tracking_object, 'tracks', icon='ANIM_DATA')

        # camera
        column.prop(constraint, 'camera')

        # row
        row = column.row()

        # row isnt active if use 3d position
        row.active = not constraint.use_3d_position

        # depth object
        row.prop(constraint, 'depth_object')

        # clip constraint to fcurve
        layout.operator('clip.constraint_to_fcurve')

    # camera solver
    def CAMERA_SOLVER(self, context, layout, constraint):

        # use active clip
        layout.prop(constraint, 'use_active_clip')

        # is use active clip
        if not constraint.use_active_clip:

            # clip
            layout.prop(constraint, 'clip')

        # clip constraint to fcurve
        layout.operator('clip.constraint_to_fcurve')

    # object solver
    def OBJECT_SOLVER(self, context, layout, constraint):

        # clip
        clip = self._getConstraintClip(context, constraint)

        # use active clip
        layout.prop(constraint, 'use_active_clip')

        # is use active clip
        if not constraint.use_active_clip:

            # clip
            layout.prop(constraint, 'clip')

        # is clip
        if clip:

            # object
            layout.prop_search(constraint, 'object', clip.tracking, 'objects', icon='OBJECT_DATA')

        # camera
        layout.prop(constraint, 'camera')

        # row
        row = layout.row()

        # constraint object solver set inverse
        row.operator('constraint.objectsolver_set_inverse')

        # constraint object solver clear inverse
        row.operator('constraint.objectsolver_clear_inverse')

        # clip constraint to fcurve
        layout.operator('clip.constraint_to_fcurve')

    # script
    def SCRIPT(self, context, layout, constraint):

        # label
        layout.label('Blender 2.7 doesn\'t support python constraints yet')
