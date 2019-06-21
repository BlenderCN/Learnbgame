import bpy
from mathutils import Euler, Vector, Quaternion, Matrix

def find_remove_keys(fc, dp, size, fr_start, fr_end):
    _fc = []
    for i in range(size):
        _find = fc.find(dp, index=i)
        if _find:
            #print('DELETANDO F-CURVE', _find.data_path)
            y1 = _find.evaluate(fr_start)
            y2 = _find.evaluate(fr_end)
            _find.keyframe_points.add(2)
            _find.keyframe_points[-2].co = fr_start-1, y1
            _find.keyframe_points[-1].co = fr_end+1, y2
            _find.update()

            brk = True
            while brk: # Bad solution.But due to constant updating of Fcurve it is the only solution :(
                brk = False
                for kp in _find.keyframe_points:
                    if fr_start <= kp.co.x <= fr_end:
                        _find.keyframe_points.remove(kp, fast=True)
                        brk = True
                        break
            _fc.append(_find)
        else:
            _fc.append(fc.new(data_path=dp, index=i))
    return _fc

class WalkCycleGenerate(bpy.types.Operator):
    """Generate Walk Cycle"""
    bl_idname = "armature.walk_cycle_generate"
    bl_label = "Generate Walk Cycle"

    '''@classmethod
    def poll(cls, context):
        if not context.armature:
            return False
        return True'''

    def invoke(self, context, event):
        if context.scene.awc_is_preview:
            bpy.ops.armature.walk_cycle_preview('INVOKE_DEFAULT')
        rig = context.object
        awc = rig.data.aut_walk_cycle
        torso = awc.torso
        l_foot = awc.l_foot_ik
        r_foot = awc.r_foot_ik
        torso_obj = rig.pose.bones[torso]
        torso_dat = rig.data.bones[torso]

        mtdat = torso_dat.matrix_local.copy()

        step_by_frames = awc.step_by_frames
        if step_by_frames:
            dist = awc.step_frames/2
        else:
            dist = awc.step/4

        fr_start = awc.frame_start
        fr_end = awc.frame_end
        if awc.anim:
            try:
                fc = rig.animation_data.action.fcurves
            except Exception as e:
                print(e)
                return {'FINISHED'}

            rot_mode = torso_obj.rotation_mode
            if rot_mode == 'QUATERNION':
                rtype = '.rotation_quaternion'
            elif rot_mode == 'AXIS_ANGLE':
                rtype = '.rotation_axis_angle'
            else:
                rtype = '.rotation_euler'

            dp = 'pose.bones["%s"]' %torso
            fc_loc = {}
            fc_rot = {}
            for _fc in fc:
                if dp in _fc.data_path:
                    ldp = _fc.data_path
                    type = ldp[ldp.rfind("."):]
                    if type == '.location':
                        fc_loc[_fc.array_index] = _fc
                    elif type == rtype:
                        fc_rot[_fc.array_index] = _fc

            seq = []
            for fr in range(fr_start, fr_end+1):
                vec = Vector((
                    fc_loc[0].evaluate(fr) if 0 in fc_loc else 0,
                    fc_loc[1].evaluate(fr) if 1 in fc_loc else 0,
                    fc_loc[2].evaluate(fr) if 2 in fc_loc else 0
                    ))

                if fr in {fr_start, fr_end}:
                    d = dist
                else:
                    if step_by_frames:
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
                    mt = Matrix.Translation(vec)
                    mr = rot.to_matrix()
                    mbasis = mt*mr.to_4x4()
                    mat = mtdat*mbasis*mtdat.inverted()
                    seq.append((fr, mat))
                    lvec = vec
                    lframe = fr

            f_curves = {}
            for col_bone in set(awc.new_bones.keys()):
                if col_bone:
                    dp_loc = 'pose.bones["%s"].location' %col_bone
                    rot_mode = rig.pose.bones[col_bone].rotation_mode
                    if rot_mode == 'QUATERNION':
                        dp_rot = 'pose.bones["%s"].rotation_quaternion' %col_bone
                        size = 4
                    elif rot_mode == 'AXIS_ANGLE':
                        dp_rot = 'pose.bones["%s"].rotation_axis_angle' %col_bone
                        size = 4
                    else:
                        dp_rot = 'pose.bones["%s"].rotation_euler' %col_bone
                        size = 3
                    f_curves[col_bone] = (
                        find_remove_keys(fc, dp_loc, 3, fr_start, fr_end),
                        find_remove_keys(fc, dp_rot, size, fr_start, fr_end)
                        )

            ### feet ###
            l_foot_ik = rig.pose.bones[l_foot]
            r_foot_ik = rig.pose.bones[r_foot]

            dp_loc = 'pose.bones["%s"].location' %l_foot
            fc_lf = find_remove_keys(fc, dp_loc, 3, fr_start, fr_end)
            rot_modl = l_foot_ik.rotation_mode
            if rot_modl == 'QUATERNION':
                dp_rot = 'pose.bones["%s"].rotation_quaternion' %l_foot
                size = 4
            elif rot_modl == 'AXIS_ANGLE':
                dp_rot = 'pose.bones["%s"].rotation_axis_angle' %l_foot
                size = 4
            else:
                dp_rot = 'pose.bones["%s"].rotation_euler' %l_foot
                size = 3
            fcqua_lf = find_remove_keys(fc, dp_rot, size, fr_start, fr_end)

            dp_loc = 'pose.bones["%s"].location' %r_foot
            fc_rf = find_remove_keys(fc, dp_loc, 3, fr_start, fr_end)
            rot_modr = r_foot_ik.rotation_mode
            if rot_modr == 'QUATERNION':
                dp_rot = 'pose.bones["%s"].rotation_quaternion' %r_foot
                size = 4
            elif rot_modr == 'AXIS_ANGLE':
                dp_rot = 'pose.bones["%s"].rotation_axis_angle' %r_foot
                size = 4
            else:
                dp_rot = 'pose.bones["%s"].rotation_euler' %r_foot
                size = 3
            fcqua_rf = find_remove_keys(fc, dp_rot, size, fr_start, fr_end)
            
            del size, dp_loc, dp_rot

            lf_dat = rig.data.bones[l_foot]
            rf_dat = rig.data.bones[r_foot]
            
            #m_lo_lf = lf_dat.matrix_local.copy()
            #m_lo_rf = rf_dat.matrix_local.copy()

            mdef = lf_dat.matrix_local.copy(), rf_dat.matrix_local.copy()
            use_local = lf_dat.use_local_location, rf_dat.use_local_location
            fc_loc = fc_lf, fc_rf
            fc_qua = fcqua_lf, fcqua_rf
            rot_mode = rot_modl, rot_modr

            up_axis = awc.up_axis.copy()
            up_axis.rotate(mtdat)
            side_axis = awc.side_axis.copy()
            side_axis.rotate(mtdat)
            openness = awc.openness
            amp = awc.amp
            ant = 1 - awc.anticipation
            fo_rot = awc.foot_rot
            right = True

            for i, tp in enumerate(seq):
                fr_f = i%2 # 01010101010101010101

                fr, mat = tp
                try:
                    fr2, mat2 = seq[i+1]
                except:
                    fr2, mat2 = seq[i]
                try:
                    fr3, mat3 = seq[i+2]
                except:
                    fr3, mat3 = fr2, mat2
                
                #obj_empty = bpy.data.objects.new("Test", None)
                #context.scene.objects.link(obj_empty)
                #obj_empty.matrix_world = mat
                #obj_empty.empty_draw_type = 'ARROWS'
                #obj_empty.empty_draw_size = .3
                
                if not fr_f:
                    right = not right # 0011001100110011001100
                    matf = mat.lerp(mat3, ant)
                    for f in range(2):
                        #matc = matf.copy()
                        mat_loc = mdef[f].copy()
                        if f - right: # foot down
                            mat_loc.translation += (2*f - 1) * openness * side_axis
                            #mat_glo = matf * mat_loc
                            mat_bas = mdef[f].inverted() * matf * mat_loc
                            if not use_local[f]:
                                mat_bas.translation.rotate(mdef[f])
                                #mat_bas = Matrix.Translation(-mdef[f].translation) * matf * Matrix.Translation(mdef[f].translation + (2*f - 1) * openness * side_axis)
                            loc, qua, _ = mat_bas.decompose()

                            # LOCATION DW
                            for ax, fcl in enumerate(fc_loc[f]):
                                fcl.keyframe_points.add(2)
                                fcl.keyframe_points[-2].interpolation = 'BEZIER'
                                fcl.keyframe_points[-2].handle_right_type = 'VECTOR'
                                fcl.keyframe_points[-2].handle_left_type = 'VECTOR'
                                fcl.keyframe_points[-2].co = fr, loc[ax]
                                fcl.keyframe_points[-1].interpolation = 'BEZIER'
                                fcl.keyframe_points[-1].handle_right_type = 'VECTOR'
                                fcl.keyframe_points[-1].handle_left_type = 'VECTOR'
                                fcl.keyframe_points[-1].co = fr3, loc[ax]

                            # ROTATION DW
                            axis = mdef[f].inverted() * side_axis # FOOT LOCAL SIDE_AXIS
                            rot1 = qua*Quaternion(axis, ant*fo_rot)
                            rot2 = qua*Quaternion(axis, (ant-1)*fo_rot)
                            dif_fr = fr3 - fr
                            f1 = fr3 - dif_fr*(1-ant/2)
                            f2 = fr3 - dif_fr*(1-(2+ant)/3)
                            if rot_mode[f] == 'QUATERNION':
                                pass
                            elif rot_mode[f] == 'AXIS_ANGLE':
                                qua = qua.to_axis_angle()
                                qua = qua[1], qua[0][0], qua[0][1], qua[0][2]
                                rot1 = rot1.to_axis_angle()
                                rot1 = rot1[1], rot1[0][0], rot1[0][1], rot1[0][2]
                                rot2 = rot2.to_axis_angle()
                                rot2 = rot2[1], rot2[0][0], rot2[0][1], rot2[0][2]
                            else:
                                qua = qua.to_euler(rot_mode[f])
                                rot1 = rot1.to_euler(rot_mode[f], qua)
                                rot2 = rot2.to_euler(rot_mode[f], qua)
                                
                            for ax, fcq in enumerate(fc_qua[f]):
                                fcq.keyframe_points.add(4)
                                fcq.keyframe_points[-4].interpolation = 'LINEAR'
                                fcq.keyframe_points[-3].interpolation = 'LINEAR'
                                fcq.keyframe_points[-2].interpolation = 'LINEAR'
                                fcq.keyframe_points[-1].interpolation = 'LINEAR'
                                fcq.keyframe_points[-4].co = fr, rot1[ax]
                                fcq.keyframe_points[-3].co = f1, qua[ax]
                                fcq.keyframe_points[-2].co = f2, qua[ax]
                                fcq.keyframe_points[-1].co = fr3, rot2[ax]

                        else:
                            mat_loc.translation += amp*up_axis
                            mat_bas = mdef[f].inverted() * matf * mat_loc
                            if not use_local[f]:
                                mat_bas.translation.rotate(mdef[f])
                            #loc, qua, _ = mat_bas.decompose()
                            loc = mat_bas.translation

                            # LOCATION UP
                            for ax, fcl in enumerate(fc_loc[f]):
                                fcl.keyframe_points.add(1)
                                fcl.keyframe_points[-1].interpolation = 'BEZIER'
                                fcl.keyframe_points[-1].handle_right_type = 'AUTO'
                                fcl.keyframe_points[-1].handle_left_type = 'AUTO'
                                fcl.keyframe_points[-1].co = fr2, loc[ax]

                            # ROTATION UP
                            #for ax, fcq in enumerate(fc_qua[f]):
                            #    fcq.keyframe_points.add(1)
                            #    fcq.keyframe_points[-1].interpolation = 'LINEAR'
                            #    fcq.keyframe_points[-1].co = fr_up, qua[ax]'''

                is_global = set()
                for col_bone in awc.new_bones:
                    name = col_bone.name
                    if col_bone.seq_type == 'LR':
                        if fr_f:
                            lerp = .5
                        elif right:
                            lerp = 0
                        else:
                            lerp = 1
                        #cond = not fr_f
                        #cond2 = right
                    elif col_bone.seq_type == 'M':
                        if not fr_f:
                            lerp = .5
                        elif right:
                            lerp = 1
                        else:
                            lerp = 0
                        #cond = fr_f
                        #cond2 = right
                    else: #col_bone.seq_type == 'ES':
                        if fr_f:
                            lerp = 1
                        else:
                            lerp = 0
                        #cond = True
                        #cond2 = fr_f
                    #if cond and name:
                    if name:
                        bone = rig.pose.bones[name]
                        bone_dat = rig.data.bones[name]
                        _loc = col_bone.loc1.lerp(col_bone.loc2, lerp)
                        #if bone_dat.use_local_location:
                            #_loc.rotate(mat)
                        _rot = col_bone.qua1.slerp(col_bone.qua2, lerp)
                        
                        #if cond2:
                            #_loc = col_bone.loc2
                            #_rot = col_bone.qua2
                        #else:
                            #_loc = col_bone.loc1
                            #_rot = col_bone.qua1

                        if col_bone.add_torso and name not in is_global:
                            is_global.add(name)
                            #print(name, 'not is torso son')
                            mat_loc = bone_dat.matrix_local.copy()  
                            mat_bas = Matrix.Translation(_loc)*_rot.to_matrix().to_4x4() # normalise rot ???
                            #mat_glo = mat*_ma_loc* _ma_bas
                            if bone_dat.use_local_location:
                                mat_bas = mat_loc.inverted() * mat * mat_loc * mat_bas
                            else:
                                mat_bas.translation.rotate(mat_loc)
                                mat_bas = mat_loc.inverted()* mat * mat_loc * mat_bas
                                mat_bas.translation.rotate(mat_loc)
                            _loc, _rot, _ = mat_bas.decompose()

                        for ax, fc in enumerate(f_curves[name][0]):
                            keyp = fc.keyframe_points
                            if keyp and keyp[-1].co.x == fr:
                                fc.keyframe_points[-1].co.y += _loc[ax] # !!!!!!!!!!!!!!!!!!
                            else:
                                fc.keyframe_points.add(1)
                                fc.keyframe_points[-1].interpolation = 'BEZIER'
                                fc.keyframe_points[-1].co = fr, _loc[ax]
                                #fc.update()

                        lrot = {}
                        for ax, fc in enumerate(f_curves[name][1]):
                            keyp = fc.keyframe_points
                            if keyp and keyp[-1].co.x == fr:
                                lrot[ax] = keyp[-1].co.y
                        _rot_mode = bone.rotation_mode
                        if _rot_mode == 'QUATERNION':
                            lrot = Quaternion((
                                lrot[0] if 0 in lrot else 1,
                                lrot[1] if 1 in lrot else 0,
                                lrot[2] if 2 in lrot else 0,
                                lrot[3] if 3 in lrot else 0
                                )).normalized()
                            _rot = lrot*_rot
                        elif _rot_mode == 'AXIS_ANGLE':
                            lrot = Quaternion((
                                lrot[1] if 1 in lrot else 0,
                                lrot[2] if 2 in lrot else 1,
                                lrot[3] if 3 in lrot else 0),
                                lrot[0] if 0 in lrot else 0
                                ).normalized()
                            _rot = lrot*_rot
                            _rot = _rot.to_axis_angle()
                            _rot = _rot[1], _rot[0][0], _rot[0][1], _rot[0][2]
                        else:
                            lrot = Euler((
                                lrot[0] if 0 in lrot else 0,
                                lrot[1] if 1 in lrot else 0,
                                lrot[2] if 2 in lrot else 0),
                                _rot_mode
                                )
                            _rot = lrot.to_quaternion()*_rot
                            _rot = _rot.to_euler(_rot_mode)

                        for ax, fc in enumerate(f_curves[name][1]):
                            keyp = fc.keyframe_points
                            if keyp and keyp[-1].co.x == fr:
                                pass
                            else:
                                fc.keyframe_points.add(1)
                            fc.keyframe_points[-1].interpolation = 'BEZIER'
                            fc.keyframe_points[-1].co = fr, _rot[ax]
            for fc in fc_loc[0]+fc_loc[1]:
                fc.update()
            for fcl, fcr in f_curves.values():
                for fc in fcl+fcr:
                    fc.update()
            return {'FINISHED'}
        else:
            try:
                fc = rig.animation_data.action.fcurves
            except Exception as e:
                rig.animation_data.action = bpy.data.actions.new("rigAction")
                fc = rig.animation_data.action.fcurves
            
            l_foot_ik = rig.pose.bones[l_foot]
            r_foot_ik = rig.pose.bones[r_foot]

            dp_loc = 'pose.bones["%s"].location' %l_foot
            fc_lf = find_remove_keys(fc, dp_loc, 3, fr_start, fr_end)
            rot_modl = l_foot_ik.rotation_mode
            if rot_modl == 'QUATERNION':
                dp_rot = 'pose.bones["%s"].rotation_quaternion' %l_foot
                size = 4
            elif rot_modl == 'AXIS_ANGLE':
                dp_rot = 'pose.bones["%s"].rotation_axis_angle' %l_foot
                size = 4
            else:
                dp_rot = 'pose.bones["%s"].rotation_euler' %l_foot
                size = 3
            fcqua_lf = find_remove_keys(fc, dp_rot, size, fr_start, fr_end)

            dp_loc = 'pose.bones["%s"].location' %r_foot
            fc_rf = find_remove_keys(fc, dp_loc, 3, fr_start, fr_end)
            rot_modr = r_foot_ik.rotation_mode
            if rot_modr == 'QUATERNION':
                dp_rot = 'pose.bones["%s"].rotation_quaternion' %r_foot
                size = 4
            elif rot_modr == 'AXIS_ANGLE':
                dp_rot = 'pose.bones["%s"].rotation_axis_angle' %r_foot
                size = 4
            else:
                dp_rot = 'pose.bones["%s"].rotation_euler' %r_foot
                size = 3
            fcqua_rf = find_remove_keys(fc, dp_rot, size, fr_start, fr_end)
            
            del size, dp_loc, dp_rot

            lf_dat = rig.data.bones[l_foot]
            rf_dat = rig.data.bones[r_foot]
            
            #m_lo_lf = lf_dat.matrix_local.copy()
            #m_lo_rf = rf_dat.matrix_local.copy()

            mdef = lf_dat.matrix_local.copy(), rf_dat.matrix_local.copy()
            mmdef = lf_dat.matrix.copy(), rf_dat.matrix.copy()
            use_local = lf_dat.use_local_location, rf_dat.use_local_location
            fc_loc = fc_lf, fc_rf
            fc_qua = fcqua_lf, fcqua_rf
            rot_mode = rot_modl, rot_modr

            frec = awc.frequency
            up_axis = awc.up_axis.copy()
            up_axis.rotate(mtdat)
            side_axis = awc.side_axis.copy()
            side_axis.rotate(mtdat)
            front_axis = awc.front_axis.copy()
            front_axis.rotate(mtdat)

            openness = awc.openness
            amp = awc.amp
            #ant = 1 - awc.anticipation
            fo_rot = awc.foot_rot
            right = True

            ant = awc.anticipation-1
            dist = awc.step/2
            fr_start = awc.frame_start
            fr_end = awc.frame_end
            dif_fr = fr_end-fr_start
            cycles = int(dif_fr/frec)
            for c in range(cycles):
                f = c%2
                fr1 = c*frec
                fr2 = fr1+frec/2
                fr3 = (c+1)*frec
                fr4 = (c+2)*frec

                s_axis = side_axis.copy()
                f_axis = front_axis.copy()
                u_axis = up_axis.copy()
                if use_local[f]:
                    s_axis.rotate(mmdef[f])
                    f_axis.rotate(mmdef[f])
                    u_axis.rotate(mmdef[f])
                op = (1-2*f)*openness
                loc2 = ((ant*dist*f_axis)+op*s_axis)*mmdef[f].inverted()
                loc1 = ((((2*ant+1)/2)*dist*f_axis)+amp*u_axis)*mmdef[f].inverted()
                loc0 = (((1+ant)*dist*f_axis)+op*s_axis)*mmdef[f].inverted()

                # LOCATION
                for ax, fcl in enumerate(fc_loc[f]):
                    fcl.keyframe_points.add(4)
                    fcl.keyframe_points[-4].interpolation = 'BEZIER'
                    fcl.keyframe_points[-4].handle_right_type = 'VECTOR'
                    fcl.keyframe_points[-4].handle_left_type = 'VECTOR'
                    fcl.keyframe_points[-4].co = fr1, loc0[ax]

                    fcl.keyframe_points[-3].interpolation = 'BEZIER'
                    fcl.keyframe_points[-3].handle_right_type = 'AUTO'
                    fcl.keyframe_points[-3].handle_left_type = 'AUTO'
                    fcl.keyframe_points[-3].co = fr2, loc1[ax]

                    fcl.keyframe_points[-2].interpolation = 'BEZIER'
                    fcl.keyframe_points[-2].handle_right_type = 'VECTOR'
                    fcl.keyframe_points[-2].handle_left_type = 'VECTOR'
                    fcl.keyframe_points[-2].co = fr3, loc2[ax]

                    fcl.keyframe_points[-1].interpolation = 'BEZIER'
                    fcl.keyframe_points[-1].handle_right_type = 'VECTOR'
                    fcl.keyframe_points[-1].handle_left_type = 'VECTOR'
                    fcl.keyframe_points[-1].co = fr4, loc0[ax]
                    
                    #mod = fcl.modifiers.new('CYCLES')
                    #mod.use_restricted_range = True
                    #mod.frame_start = fr_start
                    #mod.frame_end = fr_end

                # ROTATION
                #qua = mdef[f].to_quaternion()
                qua = Quaternion((1,0,0,0))
                axis = s_axis
                rot1 = Quaternion(axis, ant*fo_rot)
                rot2 = Quaternion(axis, (1+ant)*fo_rot)
                f1 = fr4 - frec*(1+ant/2)
                f2 = fr4 - frec*(1-(2-ant)/3)
                if rot_mode[f] == 'QUATERNION':
                    pass
                elif rot_mode[f] == 'AXIS_ANGLE':
                    qua = qua.to_axis_angle()
                    qua = qua[1], qua[0][0], qua[0][1], qua[0][2]
                    rot1 = rot1.to_axis_angle()
                    rot1 = rot1[1], rot1[0][0], rot1[0][1], rot1[0][2]
                    rot2 = rot2.to_axis_angle()
                    rot2 = rot2[1], rot2[0][0], rot2[0][1], rot2[0][2]
                else:
                    qua = qua.to_euler(rot_mode[f])
                    rot1 = rot1.to_euler(rot_mode[f], qua)
                    rot2 = rot2.to_euler(rot_mode[f], qua)

                for ax, fcq in enumerate(fc_qua[f]):
                    fcq.keyframe_points.add(4)
                    fcq.keyframe_points[-4].interpolation = 'LINEAR'
                    fcq.keyframe_points[-3].interpolation = 'LINEAR'
                    fcq.keyframe_points[-2].interpolation = 'LINEAR'
                    fcq.keyframe_points[-1].interpolation = 'LINEAR'
                    fcq.keyframe_points[-4].co = fr3, rot1[ax]
                    fcq.keyframe_points[-3].co = f1, qua[ax]
                    fcq.keyframe_points[-2].co = f2, qua[ax]
                    fcq.keyframe_points[-1].co = fr4, rot2[ax]

                f_curves = {}
                for col_bone in awc.new_bones:
                    name = col_bone.name
                    if name:
                        loc1 = col_bone.loc1.copy()
                        loc2 = col_bone.loc2.copy()
                        qua1 = col_bone.qua1.copy()
                        qua2 = col_bone.qua2.copy()
                        if name not in f_curves:
                            f_curves[name] = {}
                        if col_bone.seq_type == 'ES':
                            if fr1 in f_curves[name]:
                                f_curves[name][fr1][0] += loc1
                                f_curves[name][fr1][1] *= qua1
                            else:
                                f_curves[name][fr1] = [loc1, qua1]

                            if fr2 in f_curves[name]:
                                f_curves[name][fr2][0] += loc2
                                f_curves[name][fr2][1] *= qua2
                            else:
                                f_curves[name][fr2] = [loc2, qua2]

                        elif col_bone.seq_type == 'LR':
                            if fr1 in f_curves[name]:
                                f_curves[name][fr1][0] += loc1 if f else loc2
                                f_curves[name][fr1][1] *= qua1 if f else qua2
                            else:
                                f_curves[name][fr1] = [
                                    loc1 if f else loc2,
                                    qua1 if f else qua2]

                            if fr2 in f_curves[name]:
                                f_curves[name][fr2][0] += loc1.lerp(loc2, .5)
                                f_curves[name][fr2][1] *= qua1.slerp(qua2, .5)
                            else:
                                f_curves[name][fr2] = [
                                    loc1.lerp(loc2, .5),
                                    qua1.slerp(qua2, .5)]

                        elif col_bone.seq_type == 'M':
                            if fr1 in f_curves[name]:
                                f_curves[name][fr1][0] += loc1.lerp(loc2, .5)
                                f_curves[name][fr1][1] *= qua1.slerp(qua2, .5)
                            else:
                                f_curves[name][fr1] = [
                                    loc1.lerp(loc2, .5),
                                    qua1.slerp(qua2, .5)]

                            if fr2 in f_curves[name]:
                                f_curves[name][fr2][0] += loc1 if f else loc2
                                f_curves[name][fr2][1] *= qua1 if f else qua2
                            else:
                                f_curves[name][fr2] = [
                                    loc1 if f else loc2,
                                    qua1 if f else qua2]

                for name in f_curves:
                    bone = rig.pose.bones[col_bone.name]
                    _rot_mode = bone.rotation_mode
                    dp_loc = 'pose.bones["%s"].location' %name

                    for fr in f_curves[name]:
                        loc , rot = f_curves[name][fr]
                        if _rot_mode == 'QUATERNION':
                            dp_rot = 'pose.bones["%s"].rotation_quaternion' %name
                            size = 4
                        elif _rot_mode == 'AXIS_ANGLE':
                            rot = rot.to_axis_angle()
                            rot = rot1[1], rot1[0][0], rot1[0][1], rot1[0][2]
                            dp_rot = 'pose.bones["%s"].rotation_axis_angle' %name
                            size = 4
                        else:
                            rot = rot.to_euler(_rot_mode, qua)
                            dp_rot = 'pose.bones["%s"].rotation_euler' %name
                            size = 3
                        # LOCATION
                        for i in range(3):
                            fcl = fc.find(dp_loc, index=i)
                            if not fcl:
                                fcl = fc.new(data_path=dp_loc, index=i)
                            fcl.keyframe_points.add(1)
                            fcl.keyframe_points[-1].interpolation = 'BEZIER'
                            fcl.keyframe_points[-1].handle_right_type = 'AUTO'
                            fcl.keyframe_points[-1].handle_left_type = 'AUTO'
                            fcl.keyframe_points[-1].co = fr, loc[i]
                            fcl.update()
                        # ROTATION
                        for i in range(size):
                            fcr = fc.find(dp_rot, index=i)
                            if not fcr:
                                fcr = fc.new(data_path=dp_rot, index=i)
                            fcr.keyframe_points.add(1)
                            fcr.keyframe_points[-1].interpolation = 'BEZIER'
                            fcr.keyframe_points[-1].handle_right_type = 'AUTO'
                            fcr.keyframe_points[-1].handle_left_type = 'AUTO'
                            fcr.keyframe_points[-1].co = fr, rot[i]
                            fcr.update()

            #print('not suported')
            for fc in fc_loc[0]+fc_loc[1]+fc_qua[0]+fc_qua[1]:
                fc.update()
            return {'FINISHED'}
def register():
    bpy.utils.register_class(WalkCycleGenerate)

def unregister():
    bpy.utils.unregister_class(WalkCycleGenerate)

if __name__ == "__main__":
    register()
