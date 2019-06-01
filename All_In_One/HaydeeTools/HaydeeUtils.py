import bpy

NAME_LIMIT = 31

def boneRenameBlender(bone_name):
    name = bone_name
    if name.startswith("SK_R_"):
        name = "SK_" + name[5:] + "_R"
    if name.startswith("SK_L_"):
        name = "SK_" + name[5:] + "_L"
    return stripName(name)


def boneRenameHaydee(bone_name):
    name = bone_name
    if name.startswith("SK_") and name.endswith("_R"):
        name = "SK_R_" + name[3:-2]
    if name.startswith("SK_") and name.endswith("_L"):
        name = "SK_L_" + name[3:-2]
    return stripName(name)[:NAME_LIMIT]


def stripName(name):
    return name.replace(" ", "_").replace("*", "_").replace("-", "_")


def decodeText(text):
    return text.decode('latin1').split('\0', 1)[0]


def d(number):
    r = ('%.6f' % number).rstrip('0').rstrip('.')
    if r == "-0":
        return "0"
    return r

# --------------------------------------------------------------------------------
#  Finds a suitable armature in the current selection or scene
# --------------------------------------------------------------------------------

def find_armature(operator, context):
    armature = None
    checking = "ARMATURE"
    list = context.selected_objects
    if len(list) == 0:
        list = context.scene.objects
    while True:
        for ob in list:
            if ob.type == checking:
                if checking == "MESH":
                    for modifier in ob.modifiers:
                        if modifier.type == 'ARMATURE':
                            ob = modifier.object
                            break
                    if ob.type != 'ARMATURE':
                        continue
                if armature != None and armature != ob:
                    operator.report({'ERROR'}, "Multiples armatures found, please select a single one and try again")
                armature = ob
        if armature != None:
            return armature
        if checking == "ARMATURE":
            checking = "MESH"
        else:
            operator.report({'ERROR'}, "No armature found in scene" if list == context.scene.objects else "No armature or weighted mesh selected")
            return None



def materials_list(a,b):
    materials = {}
    for ob in bpy.context.scene.objects:
        if ob.type == "MESH":
            for material_slot in ob.material_slots:
                materials[material_slot.name] = True
    list = [('__ALL__', 'Export all materials', '')]
    for name in materials.keys():
        list.append((name, name, ''))
    return list


def fit_to_armature():
    '''Fit selected armatures to the active armature.
    Replaces selected armature with active armature.
    Also modifies the pose of the meshes.'''
    active = bpy.context.active_object
    if not (active and active.type == 'ARMATURE'):
        return {'FINISHED'}
    selected = next((armature for armature in bpy.context.selected_objects if (armature.type=='ARMATURE' and armature!=active)), None)
    if not (selected and selected.type == 'ARMATURE'):
        return {'FINISHED'}
    match_to_armature(selected, active)
    apply_pose(selected, active)
    bpy.data.armatures.remove(selected.data, do_unlink=True)


def match_to_armature(armature, target):
    for pose_bone in armature.pose.bones:
        if target.pose.bones.get(pose_bone.name):
            constraint = pose_bone.constraints.new('COPY_TRANSFORMS')
            constraint.target = target
            constraint.subtarget = pose_bone.name


def apply_pose(selected, active):
    objs = [obj for obj in bpy.data.objects if (obj.parent == selected)]
    modifiers = [modif for obj in bpy.data.objects for modif in obj.modifiers if (modif.type=='ARMATURE' and modif.object==selected)]
    for obj in objs:
        obj.parent = active
    for modif in modifiers:
        obj = modif.id_data
        bpy.context.view_layer.objects.active = obj
        index = obj.modifiers.find(modif.name)
        bpy.ops.object.modifier_copy(modifier=modif.name)
        new_modif_name = obj.modifiers[index+1].name
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=new_modif_name)
        modif.object = active
    bpy.context.view_layer.objects.active = active


def fit_to_mesh():
    '''Fit selected armatures to active'''
    active = bpy.context.active_object
    if not (active and active.type == 'ARMATURE'):
        return {'FINISHED'}
    selected = next((armature for armature in bpy.context.selected_objects if (armature.type=='ARMATURE' and armature!=active)), None)
    if not (selected and selected.type == 'ARMATURE'):
        return {'FINISHED'}
    match_to_armature(active, selected)
    new_rest_pose(selected, active)
    bpy.data.armatures.remove(selected.data, do_unlink=True)


def new_rest_pose(selected, active):
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.context.view_layer.objects.active = active
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    bpy.ops.pose.armature_apply()
    for pose_bone in active.pose.bones:
        for constraint in pose_bone.constraints:
            if constraint.type == 'COPY_TRANSFORMS':
                pose_bone.constraints.remove(constraint)
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    objs = [obj for obj in bpy.data.objects if (obj.parent == selected)]
    modifiers = [modif for obj in bpy.data.objects for modif in obj.modifiers if (modif.type=='ARMATURE' and modif.object==selected)]
    for obj in objs:
        obj.parent = active
    for modif in modifiers:
        modif.object = active



class HaydeeToolFitArmature_Op(bpy.types.Operator):
    bl_idname = 'haydee_tools.fit_to_armature'
    bl_label = 'Cycles'
    bl_description = 'Select the mesh armature then the haydee Skel. Raplces the Armature with the skel. Uses the Skel pose'
    bl_options = {'PRESET'}

    def execute(self, context):
        fit_to_armature()
        return {'FINISHED'}


class HaydeeToolFitMesh_Op(bpy.types.Operator):
    bl_idname = 'haydee_tools.fit_to_mesh'
    bl_label = 'Cycles'
    bl_description = 'Select the mesh armature then the haydee Skel. Raplces the Armature with the skel. Uses the Armature pose'
    bl_options = {'PRESET'}

    def execute(self, context):
        fit_to_mesh()
        return {'FINISHED'}

