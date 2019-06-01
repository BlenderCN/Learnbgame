import bpy


class RigLinkFaceBones(bpy.types.Operator):
    """ Add Copy Transforms constraint to face bones during setup """
    bl_idname = "pose.rig_face_link"
    bl_label = "Add copy transforms onto face rig"
    bl_context = "pose"

    @classmethod
    def poll(cls, context):
        return (
            len(context.selected_objects) == 2 and
            context.object and
            all(ob.type == 'ARMATURE' for ob in context.selected_objects))

    def execute(self, context):
        active = context.active_object
        selected = [
            ob for ob in context.selected_objects if ob is not active][0]
        face_link(active, selected)


class RigCopyBoneTransforms(bpy.types.Operator):
    """Copy bone transformms from a source armature to a target"""
    bl_idname = "pose.rig_copy_bone_transforms"
    bl_label = "Copy Bone XForms from Source to Target"

    @classmethod
    def poll(cls, context):
        return (
            context.mode == 'OBJECT' or
            (context.mode == 'POSE' and context.selected_pose_bones))

    def execute(self, context):
        source = context.active_object
        target = [obj for obj in context.selected_objects if obj != source][0]
        if context.mode == 'OBJECT':
            copy_bone_transforms(source, target)
        else:
            bones = [b.name for b in context.selected_pose_bones]
            copy_bone_transforms(source, target, bones)
        return {'FINISHED'}


class RigORGDeform(bpy.types.Operator):
    """Toggle Deform option on all selected bones"""
    bl_idname = "pose.rig_org_to_deform"
    bl_label = "Swap ORG/DEF deform bones"
    bl_context = "pose"

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def execute(self, context):
        bones_swap_org_def(context.selected_pose_bones)
        return {'FINISHED'}


class RigUnityUtils(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Rig to Unity"
    bl_idname = "POSE_RIG_TO_UNITY"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Kognito"
    # bl_context = "POSE"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label('Bone Utilities')
        col.operator('pose.rig_org_to_deform')
        col.operator('pose.rig_copy_bone_transforms')


def face_link(ctr, rig):
    """ Link via constraint def rig to control rig """
    deform_face_layer = 16
    for bone in rig.pose.bones:
        dbone = rig.data.bones[bone.name]
        if dbone.layers[16]:
            ctr_bone = bone.name.replace('GEO_', '')
            cons = bone.constraints.new('COPY_TRANSFORMS')
            cons.target = ctr
            cons.subtarget = ctr_bone


def bones_swap_org_def(bones):
    for bone in bones:
        bone.bone.use_deform = not bone.bone.use_deform


def copy_bone_transforms(source, target, bones=None):
    # thanks to https://blender.stackexchange.com/a/15940
    # Assume, that context.object is an armature
    context = bpy.context
    scene = context.scene
    # Store the bone data of source:
    bpy.ops.object.mode_set(mode='EDIT')
    bone_store = []
    if bones:
        source_bones = (source.data.edit_bones[b] for b in bones)
    else:
        source_bones = source.data.edit_bones
    for ebone in source_bones:
        bone_store.append([
            ebone.name, ebone.head.copy(), ebone.tail.copy(), ebone.roll])
    bpy.ops.object.mode_set(mode='OBJECT')

    scene.objects.active = target
    bpy.ops.object.mode_set(mode='EDIT')

    # Transfer the bones to the other armature.
    # The following works because the bone data is defined in local space:

    ebones = target.data.edit_bones
    for bone_data in bone_store:
        bid = bone_data[0]
        if bid in ebones:
            ebone = ebones[bid]
            ebone.head = bone_data[1].copy()
            ebone.tail = bone_data[2].copy()
            ebone.roll = bone_data[3]

    # If bone length has been altered we need to reset stretch to rest length
    bpy.ops.object.mode_set(mode='POSE')
    target.data.pose_position = 'REST'
    target.update_tag()
    bpy.context.scene.update()
    pbones = target.pose.bones
    for bone_data in bone_store:
        bid = bone_data[0]
        if bid in pbones:
            pbone = pbones[bid]
            for constraint in pbone.constraints:
                if constraint.type == 'STRETCH_TO':
                    constraint.rest_length = pbone.length
    target.data.pose_position = 'POSE'
    bpy.ops.object.mode_set(mode='OBJECT')
    scene.objects.active = source


def register():
    bpy.utils.register_class(RigUnityUtils)
    bpy.utils.register_class(RigCopyBoneTransforms)
    bpy.utils.register_class(RigORGDeform)


def unregister():
    bpy.utils.unregister_class(RigUnityUtils)
    bpy.utils.unregister_class(RigCopyBoneTransforms)
    bpy.utils.unregister_class(RigORGDeform)

if __name__ == "__main__":
    register()
