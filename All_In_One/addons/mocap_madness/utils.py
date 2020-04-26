# Utility Methods
import bpy
from mathutils import Matrix, Vector
from math import acos
import os
from sys import float_info


def is_subdir(path, folder):
    # check for empty string
    if path == "" or folder == "":
        return False
    return path.startswith(folder)
    # look for better way
    # normalize both parameters
    fn = os.path.normpath(path)
    fd = os.path.normpath(folder)

    # get common prefix
    commonprefix = os.path.commonprefix([fn, fd])
    if commonprefix == fd:
        # in case they have common prefix, check more:
        sufix_part = fn.replace(fd, '')
        sufix_part = sufix_part.lstrip('/')
        new_file_name = os.path.join(fd, sufix_part)
        if new_file_name == fn:
            return True
        pass
    # for all other, it's False
    return False

#########################################
## "Visual Transform" helper functions ##
#########################################
# from rigify

def get_pose_matrix_in_other_space(mat, pose_bone):
    """ Returns the transform matrix relative to pose_bone's current
        transform space.  In other words, presuming that mat is in
        armature space, slapping the returned matrix onto pose_bone
        should give it the armature-space transforms of mat.
        TODO: try to handle cases with axis-scaled parents better.
    """
    rest = pose_bone.bone.matrix_local.copy()
    rest_inv = rest.inverted()
    if pose_bone.parent:
        par_mat = pose_bone.parent.matrix.copy()
        par_inv = par_mat.inverted()
        par_rest = pose_bone.parent.bone.matrix_local.copy()
    else:
        par_mat = Matrix()
        par_inv = Matrix()
        par_rest = Matrix()

    # Get matrix in bone's current transform space
    smat = rest_inv * (par_rest * (par_inv * mat))

    # Compensate for non-local location
    #if not pose_bone.bone.use_local_location:
    #    loc = smat.to_translation() * (par_rest.inverted() * rest).to_quaternion()
    #    smat.translation = loc

    return smat


def get_local_pose_matrix(pose_bone):
    """ Returns the local transform matrix of the given pose bone.
    """
    return get_pose_matrix_in_other_space(pose_bone.matrix, pose_bone)


def set_pose_translation(pose_bone, mat):
    """ Sets the pose bone's translation to the same translation as the given matrix.
        Matrix should be given in bone's local space.
    """
    if pose_bone.bone.use_local_location == True:
        pose_bone.location = mat.to_translation()
    else:
        loc = mat.to_translation()

        rest = pose_bone.bone.matrix_local.copy()
        if pose_bone.bone.parent:
            par_rest = pose_bone.bone.parent.matrix_local.copy()
        else:
            par_rest = Matrix()

        q = (par_rest.inverted() * rest).to_quaternion()
        pose_bone.location = q * loc


def set_pose_rotation(pose_bone, mat):
    """ Sets the pose bone's rotation to the same rotation as the given matrix.
        Matrix should be given in bone's local space.
    """
    q = mat.to_quaternion()

    if pose_bone.rotation_mode == 'QUATERNION':
        pose_bone.rotation_quaternion = q
    elif pose_bone.rotation_mode == 'AXIS_ANGLE':
        pose_bone.rotation_axis_angle[0] = q.angle
        pose_bone.rotation_axis_angle[1] = q.axis[0]
        pose_bone.rotation_axis_angle[2] = q.axis[1]
        pose_bone.rotation_axis_angle[3] = q.axis[2]
    else:
        pose_bone.rotation_euler = q.to_euler(pose_bone.rotation_mode)


def set_pose_scale(pose_bone, mat):
    """ Sets the pose bone's scale to the same scale as the given matrix.
        Matrix should be given in bone's local space.
    """
    pose_bone.scale = mat.to_scale()


def match_pose_translation(pose_bone, target_bone):
    """ Matches pose_bone's visual translation to target_bone's visual
        translation.
        This function assumes you are in pose mode on the relevant armature.
    """
    mat = get_pose_matrix_in_other_space(target_bone.matrix, pose_bone)
    set_pose_translation(pose_bone, mat)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def match_pose_rotation(pose_bone, target_bone):
    """ Matches pose_bone's visual rotation to target_bone's visual
        rotation.
        This function assumes you are in pose mode on the relevant armature.
    """
    mat = get_pose_matrix_in_other_space(target_bone.matrix, pose_bone)
    set_pose_rotation(pose_bone, mat)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def match_pose_scale(pose_bone, target_bone):
    """ Matches pose_bone's visual scale to target_bone's visual
        scale.
        This function assumes you are in pose mode on the relevant armature.
    """
    mat = get_pose_matrix_in_other_space(target_bone.matrix, pose_bone)
    set_pose_scale(pose_bone, mat)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')

def add_bone_groups(action, zero_length_bones=[]):
    for f in action.fcurves:
        name = f.data_path.strip('pose.bones["')
        name = name[:name.find('"')]
        group = action.groups.get(name, action.groups.new(name))
        f.group = group
        if name in zero_length_bones:
            group.color.active = (1,0,0)

def AddHipLocator(rig,bone):
    LocatorName = rig.name+"LOCATOR"
    verts = [(-0.0037, 1.0, 0.0),
            (0.1914, 0.9814, 0.0),
            (0.3792, 0.9252, 0.0),
            (0.5524, 0.8333, 0.0),
            (0.7043, 0.7095, 0.0),
            (0.8292, 0.5584, 0.0),
            (0.9222, 0.3858, 0.0),
            (0.9797, 0.1984, 0.0),
            (0.9996, 0.0034, 0.0),
            (0.981, -0.1918, 0.0),
            (0.9248, -0.3796, 0.0),
            (0.8329, -0.5528, 0.0),
            (0.7091, -0.7047, 0.0),
            (0.558, -0.8296, 0.0),
            (0.3854, -0.9226, 0.0),
            (0.198, -0.9801, 0.0),
            (0.003, -1.0, -0.0),
            (-0.1922, -0.9814, -0.0),
            (-0.38, -0.9252, -0.0),
            (-0.5532, -0.8333, -0.0),
            (-0.7051, -0.7095, -0.0),
            (-0.83, -0.5584, -0.0),
            (-0.923, -0.3858, -0.0),
            (-0.9805, -0.1984, -0.0),
            (-1.0004, -0.0034, -0.0),
            (-0.9818, 0.1918, -0.0),
            (-0.9255, 0.3796, -0.0),
            (-0.8337, 0.5528, -0.0),
            (-0.7099, 0.7047, -0.0),
            (-0.5587, 0.8296, -0.0),
            (-0.3862, 0.9226, -0.0),
            (-0.1988, 0.9801, -0.0),
            (-0.1515, 0.7464, -0.0),
            (-0.2942, 0.7026, -0.0),
            (-0.4256, 0.6318, -0.0),
            (-0.5407, 0.5367, -0.0),
            (-0.635, 0.421, -0.0),
            (-0.7049, 0.2891, -0.0),
            (-0.7478, 0.1461, -0.0),
            (-0.7619, -0.0026, -0.0),
            (-0.7468, -0.1511, -0.0),
            (-0.703, -0.2938, -0.0),
            (-0.6321, -0.4252, -0.0),
            (-0.5371, -0.5403, -0.0),
            (-0.4213, -0.6346, -0.0),
            (-0.2895, -0.7045, -0.0),
            (-0.1465, -0.7474, -0.0),
            (0.0022, -0.7615, -0.0),
            (0.1507, -0.7464, 0.0),
            (0.2934, -0.7026, 0.0),
            (0.4248, -0.6318, 0.0),
            (0.5399, -0.5367, 0.0),
            (0.6342, -0.421, 0.0),
            (0.7041, -0.2891, 0.0),
            (0.747, -0.1461, 0.0),
            (0.7611, 0.0026, 0.0),
            (0.746, 0.1511, 0.0),
            (0.7022, 0.2938, 0.0),
            (0.6314, 0.4252, 0.0),
            (0.5363, 0.5403, 0.0),
            (0.4206, 0.6346, 0.0),
            (0.2887, 0.7045, 0.0),
            (0.1457, 0.7474, 0.0),
            (-0.0029, 0.7615, 0.0),
            (-0.1908, -1.3966, -0.0),
            (0.0052, -1.6661, -0.0),
            (0.1994, -1.3953, 0.0),
            (0.0038, -1.263, -0.0),
            (-0.1913, -1.2444, -0.0),
            (0.1989, -1.2431, 0.0)]


    faces = [[0, 31, 32, 63],
            [30, 31, 32, 33],
            [29, 30, 33, 34],
            [29, 28, 35, 34],
            [28, 27, 36, 35],
            [26, 27, 36, 37],
            [25, 26, 37, 38],
            [25, 24, 39, 38],
            [23, 24, 39, 40],
            [23, 22, 41, 40],
            [22, 21, 42, 41],
            [20, 21, 42, 43],
            [20, 19, 44, 43],
            [18, 19, 44, 45],
            [18, 17, 46, 45],
            [16, 17, 46, 47],
            [15, 16, 47, 48],
            [15, 14, 49, 48],
            [13, 14, 49, 50],
            [12, 13, 50, 51],
            [11, 12, 51, 52],
            [11, 10, 53, 52],
            [10, 9, 54, 53],
            [8, 9, 54, 55],
            [8, 7, 56, 55],
            [7, 6, 57, 56],
            [6, 5, 58, 57],
            [4, 5, 58, 59],
            [4, 3, 60, 59],
            [2, 3, 60, 61],
            [2, 1, 62, 61],
            [1, 0, 63, 62],
            [16, 67, 68, 17],
            [67, 65, 64, 68],
            [15, 69, 67, 16],
            [69, 66, 65, 67]]


    mesh = bpy.data.meshes.new("mesh")
    mesh.from_pydata(verts,[],faces)
    locator = bpy.data.objects.new(LocatorName,mesh)
    locator.scale.x = 0.5
    locator.scale.y = 0.5
  
    base = bpy.context.scene.objects.link(locator)
    '''
    code to make the hip bone a parent
    
    locator.parent = rig
    locator.parent_type = "BONE"  
    locator.parent_bone = bone.name
    '''
    con = locator.constraints.new("COPY_TRANSFORMS")
    con.target = rig
    con.subtarget = bone.name
    
    '''
    con = locator.constraints.new("COPY_ROTATION")
    con.target = rig
    con.subtarget = bone.name
    con.use_x = False
    con.use_y = False
    con.target_space = 'WORLD'
    con.owner_space = 'LOCAL'
    print("Added Mocap Madness Hip Locator")
    '''
    return locator

def SetInterpolation(Action,InterpolationType):
        for fcurve in Action.fcurves:
            for point in fcurve.keyframe_points:
                point.interpolation = InterpolationType

def bbox_diagonal(points):
    fmin = -float_info.max
    fmax = float_info.max

    bbox = [fmax, fmin, fmax, fmin, fmax, fmin]

    for v in points:        
        bbox[0] = min(bbox[0], v[0])
        bbox[1] = max(bbox[1], v[0])
        bbox[2] = min(bbox[2], v[1])
        bbox[3] = max(bbox[3], v[1])
        bbox[4] = min(bbox[4], v[2])
        bbox[5] = max(bbox[5], v[2])    
    b = Vector((bbox[0], bbox[2], bbox[4]))
    t = Vector((bbox[1], bbox[3], bbox[5]))
    return b, t


def bbox_from_diagonal(b, t):
    x = Vector((1.0, 0, 0))
    y = x.zxz
    z = x.zzx
    v = t - b 
    x, y, z = v.dot(x) * x, v.dot(y) * y, v.dot(z) * z      
    verts = [b , b + y, t - z, b + x, b + z, t - x, t, t - y]    
    
    return verts           


def bbox_rig(rig, ignore_bones=set()):
    points = [pb.tail for pb in rig.pose.bones if pb.name not in ignore_bones]
    b, t = bbox_diagonal(points)
    return bbox_from_diagonal(b, t)


def global_bbox(ob):    
    if ob.type == 'ARMATURE':
        bb = bbox_rig(ob)
    elif ob.type == 'LATTICE':
        bb = bbox_lattice(ob)
    else:
        # works for MESH, CURVE
        bb = ob.bound_box
    mw = ob.matrix_world
    return [mw * Vector(c) for c in bb]

def bbox_rig_vector(rig, ignore_bones=set()):
    bbox = global_bbox(rig)
    return bbox[6] - bbox[0]
    points = [pb.tail for pb in rig.pose.bones if pb.name not in ignore_bones]
    b, t = bbox_diagonal(points)
    return t - b


def AddHipLocator(rig, bone, scale=(1.0, 1.0, 1.0), set_pos=False):
    LocatorName = rig.name+"LOCATOR"
    verts = [(-0.0037, 1.0, 0.0),
            (0.1914, 0.9814, 0.0),
            (0.3792, 0.9252, 0.0),
            (0.5524, 0.8333, 0.0),
            (0.7043, 0.7095, 0.0),
            (0.8292, 0.5584, 0.0),
            (0.9222, 0.3858, 0.0),
            (0.9797, 0.1984, 0.0),
            (0.9996, 0.0034, 0.0),
            (0.981, -0.1918, 0.0),
            (0.9248, -0.3796, 0.0),
            (0.8329, -0.5528, 0.0),
            (0.7091, -0.7047, 0.0),
            (0.558, -0.8296, 0.0),
            (0.3854, -0.9226, 0.0),
            (0.198, -0.9801, 0.0),
            (0.003, -1.0, -0.0),
            (-0.1922, -0.9814, -0.0),
            (-0.38, -0.9252, -0.0),
            (-0.5532, -0.8333, -0.0),
            (-0.7051, -0.7095, -0.0),
            (-0.83, -0.5584, -0.0),
            (-0.923, -0.3858, -0.0),
            (-0.9805, -0.1984, -0.0),
            (-1.0004, -0.0034, -0.0),
            (-0.9818, 0.1918, -0.0),
            (-0.9255, 0.3796, -0.0),
            (-0.8337, 0.5528, -0.0),
            (-0.7099, 0.7047, -0.0),
            (-0.5587, 0.8296, -0.0),
            (-0.3862, 0.9226, -0.0),
            (-0.1988, 0.9801, -0.0),
            (-0.1515, 0.7464, -0.0),
            (-0.2942, 0.7026, -0.0),
            (-0.4256, 0.6318, -0.0),
            (-0.5407, 0.5367, -0.0),
            (-0.635, 0.421, -0.0),
            (-0.7049, 0.2891, -0.0),
            (-0.7478, 0.1461, -0.0),
            (-0.7619, -0.0026, -0.0),
            (-0.7468, -0.1511, -0.0),
            (-0.703, -0.2938, -0.0),
            (-0.6321, -0.4252, -0.0),
            (-0.5371, -0.5403, -0.0),
            (-0.4213, -0.6346, -0.0),
            (-0.2895, -0.7045, -0.0),
            (-0.1465, -0.7474, -0.0),
            (0.0022, -0.7615, -0.0),
            (0.1507, -0.7464, 0.0),
            (0.2934, -0.7026, 0.0),
            (0.4248, -0.6318, 0.0),
            (0.5399, -0.5367, 0.0),
            (0.6342, -0.421, 0.0),
            (0.7041, -0.2891, 0.0),
            (0.747, -0.1461, 0.0),
            (0.7611, 0.0026, 0.0),
            (0.746, 0.1511, 0.0),
            (0.7022, 0.2938, 0.0),
            (0.6314, 0.4252, 0.0),
            (0.5363, 0.5403, 0.0),
            (0.4206, 0.6346, 0.0),
            (0.2887, 0.7045, 0.0),
            (0.1457, 0.7474, 0.0),
            (-0.0029, 0.7615, 0.0),
            (-0.1908, -1.3966, -0.0),
            (0.0052, -1.6661, -0.0),
            (0.1994, -1.3953, 0.0),
            (0.0038, -1.263, -0.0),
            (-0.1913, -1.2444, -0.0),
            (0.1989, -1.2431, 0.0)]


    faces = [[0, 31, 32, 63],
            [30, 31, 32, 33],
            [29, 30, 33, 34],
            [29, 28, 35, 34],
            [28, 27, 36, 35],
            [26, 27, 36, 37],
            [25, 26, 37, 38],
            [25, 24, 39, 38],
            [23, 24, 39, 40],
            [23, 22, 41, 40],
            [22, 21, 42, 41],
            [20, 21, 42, 43],
            [20, 19, 44, 43],
            [18, 19, 44, 45],
            [18, 17, 46, 45],
            [16, 17, 46, 47],
            [15, 16, 47, 48],
            [15, 14, 49, 48],
            [13, 14, 49, 50],
            [12, 13, 50, 51],
            [11, 12, 51, 52],
            [11, 10, 53, 52],
            [10, 9, 54, 53],
            [8, 9, 54, 55],
            [8, 7, 56, 55],
            [7, 6, 57, 56],
            [6, 5, 58, 57],
            [4, 5, 58, 59],
            [4, 3, 60, 59],
            [2, 3, 60, 61],
            [2, 1, 62, 61],
            [1, 0, 63, 62],
            [16, 67, 68, 17],
            [67, 65, 64, 68],
            [15, 69, 67, 16],
            [69, 66, 65, 67]]


    mesh = bpy.data.meshes.new("mesh")
    mesh.from_pydata(verts,[],faces)
    locator = bpy.data.objects.new(LocatorName,mesh)
    locator.scale = scale
  
    base = bpy.context.scene.objects.link(locator)
    '''
    code to make the hip bone a parent
    
    locator.parent = rig
    locator.parent_type = "BONE"  
    locator.parent_bone = bone.name
    '''
    con = locator.constraints.new("COPY_LOCATION")
    con.target = rig
    con.subtarget = bone.name
    

    con = locator.constraints.new("COPY_ROTATION")
    con.target = rig
    con.subtarget = bone.name

    con.target_space = 'WORLD'
    con.owner_space = 'WORLD'
    #print("Added Mocap Madness Hip Locator")
    
    if set_pos:
        locator.matrix_local = locator.matrix_world
        for c in locator.constraints:
            locator.constraints.remove(c)

    return locator


def bone(op, scene):
    if scene.pose_match.pause:
        return False
    bones = scene.bones

    # offer selection of
    # visual drivers all bones
    # same but grouped
    # single all encompassing driver using SUM
    
    
    ob = op.rig
    
    action = ob.animation_data.action
    dupe = op.dupe
    
    
    #ob = scene.objects.get("16_01")
    #dupe = scene.objects.get("16_01.001")
    strip = op.strip

    tot = 100000
    if strip.action.name == ob.animation_data.action.name:
        if abs(scene.frame_current - strip.action_frame_end) >= 20:
            if scene.pose_match.method == 'BBOX':
                tot = (bbox_rig_vector(ob) - op.dupe_bbox).length
            if scene.pose_match.method == 'BONE_DRIVER':
                tot = scene["tot"]
            if scene.pose_match.method == 'BONE_DRIVER_VIS':
                tot = sum([b.b1 for b in scene.bones])
            
    if tot < scene.pose_match.match:
        print("TOT:", tot)
        #op.wait = True
        

        # look for matches within small distance
        
        h = ob.pose.bones['Hips']
        loc = h.location
        sf = ob.scale.x
        if scene.pose_match.delta_loc > 0:    
            matches = [m for m in op.mt.children
                       if m.users > 0
                       #and m["action_frame"] in list(range(af-5, af+1))
                       and (m.pose.bones["Hips"].location - loc).length < scene.pose_match.delta_loc / sf
                      ]
            if len(matches):
                print("LEN MATCHES", len(matches))
                #print(matches)
                matches.sort(key=lambda x: x["match"])
                # delete all but the best
                if matches[0]["match"] < tot:
                    return False
                #print(matches)
                for o in matches:
                    print("del", o.name, o["action_frame"], o["match_frame"])
                    o.parent = None
                    scene.objects.unlink(o)
                    #o["match"] = scene.pose_match.match



        
        dupe2 = dupe.copy()
        # remove custom props
        for prop in dupe2.keys():
            del dupe2[prop]


        scene.objects.link(dupe2)
        dupe2.name = "[%06.3f]" % tot
        
        af = int(strip.action_frame_start)
        mf = scene.frame_current
        dupe2["match"] = tot
  
        dupe2["action_frame"] = af
        dupe2["action"] = strip.action.name
        dupe2["match_action"] = action.name
        dupe2["match_frame"] = mf

        
        
        dupe2.parent = op.mt

        hips = dupe2.pose.bones['Hips']
        

        #loc = AddHipLocator(dupe2, hips)
        #scene.update()
        #print("adding hiploc")
        
        #print("setting hips on ", dupe2.name)
        

                
        for c in hips.constraints:
            hips.constraints.remove(c)
        hips.matrix_basis = h.matrix_basis.copy()
        #hips.matrix = h.matrix.copy()
        dupe2.animation_data_clear()
        '''
        hips.keyframe_insert('location', options={'INSERTKEY_VISUAL'})
        dupe2.rotation_mode = 'QUATERNION'
        hips.keyframe_insert('rotation_quaternion', options={'INSERTKEY_VISUAL'})
        

        
        # code to add a hip locator instead of armature copy
        loc = AddHipLocator(ob, h)
        
        loc.matrix_local = loc.matrix_world
        for c in loc.constraints:
            loc.constraints.remove(c)
        
        print(scene.frame_current, ":", tot)
        op.wait = False
        
                
        # remove matches that are similar to current
        matches = [m for m in op.mt.children
                   if m.users > 0
                   #and m["action_frame"] in list(range(af-5, af+1))
                   and m["match_frame"] in list(range(mf-1, mf+1))
                  ]
        if len(matches) > 1:
            print("LEN MATCHES", len(matches))
            #print(matches)
            matches.sort(key=lambda x: x["match"])
            # delete all but the best
            matches.pop(0)
            #print(matches)
            for o in matches:
                print("del", o.name, o["action_frame"], o["match_frame"])
                o.parent = None
                scene.objects.unlink(o)
                #o["match"] = scene.pose_match.match

        '''  
 
        


        
        # keep list to 10 matches
        matches = [m["match"] 
                   for m in op.mt.children
                   if m.users > 0
                   ]
        #print("LEN MATCHES", len(matches))
        keep = scene.pose_match.matches
        if len(matches) > keep:
            matches.sort()
            print("10th", matches[keep-1])
            scene.pose_match.match = matches[keep-1]
        #op.mt.name = "Matches (%s)" % len(op.mt.children)
        

    # if at end frame then click up the NLA
    # QUICK HACK TO CHECK
    if scene.frame_current >= int(action.frame_range[1] / 2):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN')
        strip.action_frame_end += 1
        strip.action_frame_start += 1

        scene.frame_set(action.frame_range[0])
        if scene.pose_match.method == 'BBOX':
            op.dupe_bbox = bbox_rig_vector(dupe)            
        if strip.action_frame_start > strip.action.frame_range[1]:
            scene.pose_match.pause = True


def set_up_simulation(operator, scene):
    #operator = operator.__class__
    # set up the action lists
    # put rna checking in the poll method. (both ops)
    operator.rig = rig = scene.objects.active
    
    scene.pose_match.rig = rig.name
    print("RIG", rig)
    if rig is None:
        # ABORT
        pass
    arm = rig.data
    actions = arm.actions
    print(actions)
    action = rig.animation_data.action
    
    dupe = rig.copy()
    scene.objects.link(dupe)
    dupe["dupe"] = True
    scene.pose_match.dupe = dupe.name


    #del dupe.data["bvh_import_settings"]
    #remove the actions list from dupe
    dupe["actions"] = []
    
    dupe.animation_data.action = None
    dupetrack = dupe.animation_data.nla_tracks.new()
    dupetrack.name = "DupeTrack"
    # QUICK HACK TO CHECK
    start = action.frame_range[1] / 2   
    dupestrip = dupetrack.strips.new("DupeStrip", 1, action)
    dupestrip.name = "DupeStrip"
    
    dupestrip.action_frame_start = dupestrip.action_frame_end = int(start)
    dupestrip.scale = 1.0
    
    scene.pose_match.rig = rig.name
    scene.pose_match.action1 = rig.animation_data.action.name
    scene.pose_match.action2 = dupestrip.action.name        
    
    operator.dupe = dupe
    operator.strip = dupestrip
    for bg in scene.bones:
        bg.driver_remove('b1')
        
    for bg in scene.bones:
        scene.bones.remove(0)
        
    if "tot" in scene.keys():
        scene.driver_remove('["tot"]')

    if scene.pose_match.method.startswith('BONE_DRIVER'):
        # ignore the parent bone and zlb's
        bones = [b for b in rig.pose.bones 
                 if b.parent is not None
                 ]
        # remove old drivers
        if scene.pose_match.method == 'BONE_DRIVER_VIS':

            for b in bones:
                #pb = ob.pose.bones.get(b["bvh"])
                bg = scene.bones.add()
                bg.name = b.name
                d = bg.driver_add("b1").driver
                
                v = d.variables.get("bone1", d.variables.new())
                v.name = b.name
                v.type = scene.pose_match.driver_var_type

                # double boner
                v.targets[0].id = rig
                v.targets[0].bone_target = b.name
                v.targets[1].id = dupe
                v.targets[1].bone_target = b.name    
                d.expression = "abs(%s)" % v.name
        elif scene.pose_match.method == 'BONE_DRIVER':    
            scene["tot"] = 0.0
            
            tot_driver = scene.driver_add('["tot"]').driver
            tot_driver.type = scene.pose_match.func
            for b in bones:
                #pb = ob.pose.bones.get(b["bvh"])
                bg = scene.bones.add()
                bg.name = b.name
                d = tot_driver
                v = d.variables.get("bone1", d.variables.new())
                v.name = b.name
                v.type = scene.pose_match.driver_var_type

                # double boner
                v.targets[0].id = rig
                v.targets[0].bone_target = b.name
                v.targets[1].id = dupe
                v.targets[1].bone_target = b.name    
            

        


        # get the angle between them
        #print(angle)
        
    # add copy transforms constraint 

    con = dupe.pose.bones["Hips"].constraints.new(type='COPY_TRANSFORMS')
    con.target = rig
    con.subtarget = "Hips" 
    scene.frame_set(1)
    if scene.pose_match.method == 'BBOX':
        operator.dupe_bbox = bbox_rig_vector(dupe)   
    
    return True   
    
def get_holder_empty(scene, key):
    obs = [mt for mt in scene.objects if mt.data is None and "Matches" in mt.keys()
           and mt["Matches"] == key]
    if len(obs):
        return obs[0]
    
    mt = bpy.data.objects.new("%s (Pose Match)" % key, None)
    mt["Matches"] = key #  number of matches
    return scene.objects.link(mt).object


class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None
    wait = False

    def modal(self, context, event):

        scene = context.scene
        if event.type in {'ESC'} or scene.pose_match.pause:
            return self.cancel(context)
        
        if self.wait:
            return {'PASS_THROUGH'}
        
        if event.type == 'TIMER':
            # change theme color, silly!
            scene = context.scene
            bone(self, scene)
            scene.frame_set(scene.frame_current + 1)


        return {'PASS_THROUGH'}

    def execute(self, context):
        scene = context.scene
        
        if scene.pose_match.timers == 0:       
            set_up_simulation(self, scene)
        else:
            self.rig = scene.objects.get(scene.pose_match.rig)
            self.dupe = scene.objects.get(scene.pose_match.dupe)
            self.dupe_bbox = bbox_rig_vector(self.dupe)
            self.strip = self.dupe.animation_data.nla_tracks["DupeTrack"].strips["DupeStrip"]
        
        wm = context.window_manager
        scene.pose_match.timers += 1
        #holder empty
        
        #mt.location = (0,0,0)

        self.mt = get_holder_empty(scene, self.rig.name)
        self._timer = wm.event_timer_add(0.01, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        
        scene = context.scene
        
        scene.pose_match.timers -= 1
        if scene.pose_match.timers == 0:
            scene.pose_match.pause = False
            if scene.objects.get(self.dupe.name):
                scene.objects.unlink(self.dupe)
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        
        
        return {'CANCELLED'}

class SimpleOperator(bpy.types.Operator):
    """Operator to do the matching non modal"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        scene = context.scene
        scene.pose_match.pause = False
        scene.frame_set(1)
        #holder empty
        
        set_up_simulation(self, scene)
        self.mt = get_holder_empty(scene, self.rig.name)
        action = self.rig.animation_data.action

        while not scene.pose_match.pause:
            bone(self, scene)

            scene.frame_set(scene.frame_current + 1)
            
        # clean up
        if scene.objects.get(self.dupe.name):
            scene.objects.unlink(self.dupe)

        return {'FINISHED'}



def register():
    bpy.utils.register_class(ModalTimerOperator)
    bpy.utils.register_class(SimpleOperator)

def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)
    bpy.utils.unregister_class(SimpleOperator)

