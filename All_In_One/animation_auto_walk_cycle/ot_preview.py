import bpy
from math import pi, cos, sin
from mathutils import Euler, Quaternion, Vector, Matrix

def set_fr_steps(self, context):
    if self.anim:
        rig = context.object
        #awc = rig.data.aut_walk_cycle
        torso = self.torso
        bone = rig.pose.bones[torso]
        rot_mode = bone.rotation_mode
        if rot_mode == 'QUATERNION':
            rtype = '.rotation_quaternion'
        elif rot_mode == 'AXIS_ANGLE':
            rtype = '.rotation_axis_angle'
        else:
            rtype = '.rotation_euler'
            
        dp = 'pose.bones["%s"]' %torso

        fc_loc = {}
        fc_rot = {}
        if rig.animation_data.action:
            for fc in rig.animation_data.action.fcurves:
                if dp in fc.data_path:
                    ldp = fc.data_path
                    type = ldp[ldp.rfind("."):]
                    if type == '.location':
                        fc_loc[fc.array_index] = fc
                    elif type == rtype:
                        fc_rot[fc.array_index] = fc
        else:
            rig.data.aut_walk_cycle.anim = False

        if not fc_loc:
            rig.data["frame_steps"] = {}
            return
        if self.step_by_frames:
            dist = self.step_frames
        else:
            dist = self.step/2
        fr_start = context.scene.frame_start
        fr_end = context.scene.frame_end
        bone_dat = rig.data.bones[torso]
        m_loc = bone_dat.matrix_local.copy()
        parent = bone.parent.matrix*bone_dat.parent.matrix_local.inverted()
        frame_steps = {}
        for fr in range(fr_start, fr_end+1):
            vec = Vector((
                fc_loc[0].evaluate(fr) if 0 in fc_loc else 0,
                fc_loc[1].evaluate(fr) if 1 in fc_loc else 0,
                fc_loc[2].evaluate(fr) if 2 in fc_loc else 0
                ))
            if fr in {fr_start, fr_end}:
                d = dist
            elif self.step_by_frames:
                d = fr - lframe
            else: 
                d = (lvec - vec).length
            if d >= dist:
                if rot_mode == 'QUATERNION':
                    rot = Quaternion((
                        fc_rot[0].evaluate(fr) if 0 in fc_rot else 1,
                        fc_rot[1].evaluate(fr) if 1 in fc_rot else 0,
                        fc_rot[2].evaluate(fr) if 2 in fc_rot else 0,
                        fc_rot[3].evaluate(fr) if 3 in fc_rot else 0
                        )).normalized()
                elif rot_mode == 'AXIS_ANGLE':
                    rot = Quaternion((
                        fc_rot[1].evaluate(fr) if 1 in fc_rot else 0,
                        fc_rot[2].evaluate(fr) if 2 in fc_rot else 1,
                        fc_rot[3].evaluate(fr) if 3 in fc_rot else 0),
                        fc_rot[0].evaluate(fr) if 0 in fc_rot else 0
                        ).normalized()
                else:
                    rot = Euler((
                        fc_rot[0].evaluate(fr) if 0 in fc_rot else 0,
                        fc_rot[1].evaluate(fr) if 1 in fc_rot else 0,
                        fc_rot[2].evaluate(fr) if 2 in fc_rot else 0),
                        rot_mode
                        )
                mbasis = Matrix.Translation(vec)*rot.to_matrix().to_4x4()
                mglobal = parent*m_loc*mbasis*m_loc.inverted()
                #rvec.rotate(m_loc.inverted())
                #ant = int((fr - lframe) * (1 - self.anticipation))
                gvec, rot, _ = mglobal.decompose()
                frame_steps[str(fr)] = [gvec, rot]
                lvec = vec
                lframe = fr
        rig.data["frame_steps"] = frame_steps

def frame_pre(scene):
    #if not bpy.context.screen.is_animation_playing:
        #bpy.app.handlers.frame_change_pre.remove(frame_pre)
    obj = bpy.context.object
    if obj and obj.type == 'ARMATURE':
        awc = obj.data.aut_walk_cycle
        try:
            torso_obj = obj.pose.bones[awc.torso]
            l_foot_ik = obj.pose.bones[awc.l_foot_ik]
            r_foot_ik = obj.pose.bones[awc.r_foot_ik]
        except Exception as e:
            print("ERROR", e)
            bpy.app.handlers.frame_change_pre.remove(frame_pre)
            return
        amp = awc.amp
        openness = -awc.openness
        anticipation = 1-awc.anticipation
        fo_rot = awc.foot_rot
        frame = scene.frame_current

        up_axis = awc.up_axis.copy()
        up_axis.rotate(torso_obj.matrix)
        side_axis = awc.side_axis.copy()
        side_axis.rotate(torso_obj.matrix)
        mat_l = obj.data.bones[awc.l_foot_ik].matrix_local.copy()
        mat_r = obj.data.bones[awc.r_foot_ik].matrix_local.copy()
        if not awc.anim:
            front_axis = awc.front_axis.copy()
            front_axis.rotate(torso_obj.matrix)
            #print(up_axis)
            step = awc.step/2
            #(anticipation - .5)
            frequency = awc.frequency
            fr = 2*pi*frame/frequency
            cf = cos(fr/2)
            sf = sin(fr/2)
            cff = cf**2
            mod = (frame/frequency-.5)%2
            f = mod >= 1

            up = up_axis*cff*amp
            front = ((sf/2)*step)*front_axis
            ant = ((anticipation - .5)*step)*front_axis
            side = side_axis*openness
            fo_rot = fo_rot*side_axis

            foot = l_foot_ik, r_foot_ik
            mat = mat_l, mat_r
            sign = 2*f -1
            mod -= f
            mloc = Matrix.Translation(((ant+up+sign*(front+(cff-1)*side))))#*mat[f]))
            mrot = Quaternion((mod-1+anticipation)*fo_rot).to_matrix()
            foot[f].matrix = mloc*mrot.to_4x4()*mat[f]
            front = front_axis*(.5-mod)*step
            mloc = Matrix.Translation((ant+front+sign*side))#*mat[f-1])
            if 2*mod <= anticipation:
                mrot = Quaternion((anticipation-2*mod)*fo_rot).to_matrix()
                matr = mloc*mrot.to_4x4()
            elif 3*mod-2 >= anticipation:
                mrot = Quaternion((anticipation-(3*mod-2))*fo_rot).to_matrix()
                matr = mloc*mrot.to_4x4()
            else:
                matr = mloc
            foot[f-1].matrix = matr*mat[f-1]

            m_cache = {}
            for col_bone in awc.new_bones:
                if col_bone.name and col_bone.show:
                    name = col_bone.name
                    bone = obj.pose.bones[name]
                    bone_dat = obj.data.bones[col_bone.name]
                    m_local = bone_dat.matrix_local
                    #m_ch = m_cache.get(name, Matrix.Identity(4))
                    m_cache[name] = m_cache.get(name, m_local)
                    if col_bone.seq_type == 'LR':
                        fac = sf/2 + .5
                    elif col_bone.seq_type == 'M':
                        fac = cf/2 + .5
                    else: # if col_bone.seq_type == 'ES'
                        fac = cff
                    #mloc = Matrix.Translation(col_bone.loc1.lerp(col_bone.loc2, fac))
                    mrot = col_bone.qua1.slerp(col_bone.qua2, fac).to_matrix()
                    m_cache[name] *= mrot.to_4x4()
                    loc = col_bone.loc1.lerp(col_bone.loc2, fac)
                    if bone_dat.use_local_location:
                        loc.rotate(m_local)
                    m_cache[name].translation += loc
                    parent = bone.parent.matrix*bone_dat.parent.matrix_local.inverted()
                    if col_bone.add_torso:
                        m_cache[name].translation += parent.translation
                        bone.matrix = m_cache[name]

                    else:
                        bone.matrix = parent*m_cache[name]

        else: # awc.anim:
            fr_prev = frame
            fs = obj.data['frame_steps'].to_dict()
            sfs = sorted(fs, key = lambda x: int(x))
            for i, frst in enumerate(sfs):
                fr = int(frst)
                if fr > frame:
                    left = i%2
                    vec2 = Vector(fs[sfs[i-1]][0])
                    vec3 = Vector(fs[sfs[i]][0])
                    if i >= 2:
                        vec1 = Vector(fs[sfs[i-2]][0])
                    else:
                        vec1 = vec2
                    sign = (2*left-1)
                    rang = (frame-fr_prev)/(fr-fr_prev) # = mod%1
                    # |  /
                    # | /
                    # |/___
                    cf = 4*rang*(1-rang)*sign # or sin(rang*pi)
                    # |  __
                    # | /  \
                    # |/____\_

                    rq = Quaternion(fs[sfs[i-1]][1])
                    rrot = rq.slerp(Quaternion(fs[sfs[i]][1]), rang)
                    _mrot = rrot.to_matrix()
                    rvec = Matrix.Translation((vec2.lerp(vec3, rang)))

                    mat_global = rvec*_mrot.to_4x4()

                    torso_dat = obj.data.bones[awc.torso]
                    torso_obj.matrix = mat_global*torso_dat.matrix_local

                    ant = rang+anticipation/2 # antecip real
                    vec2 = vec2.lerp(vec3, anticipation)
                    if ant <= 1:
                        loc = vec1.lerp(vec3, ant)
                    else:
                        try:
                            vec5 = Vector(fs[sfs[i+2]][0])
                            loc = vec3.lerp(vec5, ant-1)
                        except:
                            loc = vec1.lerp(vec3, ant)
                    mt_vec2 = Matrix.Translation(vec2)
                    mat_loc = Matrix.Translation(loc)
                    up2 = up_axis*cf*amp
                    mrot = Matrix.Rotation((ant-1)*fo_rot, 3, side_axis)*_mrot
                    mrot.resize_4x4()

                    lat2 = side_axis*openness
                    if left:
                        m_vec = Matrix.Translation((1-cf)*lat2 + up2)
                        l_foot_ik.matrix = mat_loc*m_vec*mrot*mat_l

                        mt_r = Matrix.Translation(-lat2)
                        if 2*rang <= anticipation:
                            mr_r = Matrix.Rotation((anticipation-2*rang)*fo_rot, 3, side_axis)*_mrot
                        elif 3*rang-2 >= anticipation:
                            mr_r = Matrix.Rotation((anticipation-(3*rang-2))*fo_rot, 3, side_axis)*_mrot
                        else:
                            mr_r = _mrot
                        r_foot_ik.matrix = mt_vec2*mt_r*mr_r.to_4x4()*mat_r
                            
                    else:
                        m_vec = Matrix.Translation(-(cf+1)*lat2 - up2)
                        r_foot_ik.matrix = mat_loc*m_vec*mrot*mat_r

                        mt_l = Matrix.Translation(lat2)
                        if 2*rang <= anticipation:
                            mr_l = Matrix.Rotation((anticipation-2*rang)*fo_rot, 3, side_axis)*_mrot
                        elif 3*rang-2 >= anticipation:
                            mr_l = Matrix.Rotation((anticipation-(3*rang-2))*fo_rot, 3, side_axis)*_mrot
                        else:
                            mr_l = _mrot
                        l_foot_ik.matrix = mt_vec2*mt_l*mr_l.to_4x4()*mat_l

                    m_cache = {}
                    for col_bone in awc.new_bones:
                        if col_bone.name and col_bone.show:
                            name = col_bone.name
                            bone = obj.pose.bones[name]
                            bone_dat = obj.data.bones[name]
                            #m_local = m_cache.get(name, bone_dat.matrix_local)
                            m_local = bone_dat.matrix_local
                            m_cache[name] = m_cache.get(name, m_local)
                            loc1 = col_bone.loc1
                            loc2 = col_bone.loc2
                            rot1 = col_bone.qua1
                            rot2 = col_bone.qua2

                            if col_bone.seq_type == 'LR':
                                sf = cos(rang*pi)*sign
                                # |_        _
                                # | \      /
                                # |__|____|__ 
                                # |  |    |
                                # |   \__/ 
                                fac = sf/2 + .5
                                loc = loc1.lerp(loc2, fac)
                                rot = rot1.slerp(rot2, fac)

                            elif col_bone.seq_type == 'M':
                                fac = .5 - cf/2
                                loc = loc1.lerp(loc2, fac)
                                rot = rot1.slerp(rot2, fac)

                            else: #col_bone.seq_type == 'ES':
                                fac = cf**2
                                loc = loc1.lerp(loc2, fac)
                                rot = rot1.slerp(rot2, fac)

                            mrot = rot.to_matrix()
                            #mloc = Matrix.Translation(vec)
                            m_cache[name] *= mrot.to_4x4()
                            if bone_dat.use_local_location:
                                loc.rotate(m_local)
                            m_cache[name].translation += loc

                            if col_bone.add_torso:
                                bone.matrix = mat_global*m_cache[name]
                            else:
                                parent = bone.parent.matrix*bone_dat.parent.matrix_local.inverted()
                                bone.matrix = parent*m_cache[name]
                    break
                fr_prev = fr
    else:
        bpy.app.handlers.frame_change_pre.remove(frame_pre)
        scene.awc_is_preview = False

def mute_torso(context, mute = True):
    rig = context.object
    awc = rig.data.aut_walk_cycle
    torso = awc.torso
    l_foot = awc.l_foot_ik
    r_foot = awc.r_foot_ik
    sdp = {
        'pose.bones["%s"]' %torso,
        'pose.bones["%s"]' %l_foot,
        'pose.bones["%s"]' %r_foot,
        }
    for col_bone in set(awc.new_bones.keys()):
        sdp.add('pose.bones["%s"]' %col_bone)

    if rig.animation_data and rig.animation_data.action:
        for fc in rig.animation_data.action.fcurves:
            for dp in sdp:
                if dp in fc.data_path:
                    fc.mute = mute
    else:
        rig.data.aut_walk_cycle.anim = False

    if mute:
        bone = rig.pose.bones[torso]
        bone_dat = rig.data.bones[torso]
        if bone.parent:
            bone.matrix = bone.parent.matrix*bone_dat.parent.matrix_local.inverted()*bone_dat.matrix_local
        else:
            bone.matrix = bone_dat.matrix_local

class WalkCyclePreview(bpy.types.Operator):
    """Preview the walk cycle without creating F-curves"""
    bl_idname = "armature.walk_cycle_preview"
    bl_label = "Preview Walk Cycle"

    @classmethod
    def poll(cls, context):
        if not context.armature:
            return False
        return True

    def invoke(self, context, event):
        if frame_pre not in bpy.app.handlers.frame_change_pre:
            context.scene.awc_is_preview = True
            awc = context.object.data.aut_walk_cycle
            mute_torso(context, mute = True)
            set_fr_steps(awc, context)
            bpy.app.handlers.frame_change_pre.append(frame_pre)
        else:
            context.scene.awc_is_preview = False
            bpy.app.handlers.frame_change_pre.remove(frame_pre)
            mute_torso(context, mute = False)
            for func in bpy.app.handlers.frame_change_pre:
                if func.__name__ == 'frame_pre':
                    bpy.app.handlers.frame_change_pre.remove(func)
        return {'FINISHED'}

def register():
    #bpy.app.handlers.frame_change_pre.clear()
    bpy.utils.register_class(WalkCyclePreview)

def unregister():
    bpy.utils.unregister_class(WalkCyclePreview)

    if frame_pre in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(frame_pre)

if __name__ == "__main__":
    register()
