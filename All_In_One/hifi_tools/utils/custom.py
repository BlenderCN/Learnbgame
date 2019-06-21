import bpy
import re
from hifi_tools.utils import bones, mesh, materials, bpyutil
from bpy.props import StringProperty, BoolProperty, PointerProperty

def poll(self, object):
    return object.type == "BONE"

def get_armatures(self, context):
    obj = []

    count = 0
    for ob in context.scene.objects:
        if ob.type == 'ARMATURE':
            # (key, label, descr, id, icon)
            # [(identifier, name, description, icon, number)
            obj.append((ob.name, ob.name, "ARMATURE_DATA"))
            count += 1

    return obj

def get_bones(self, context):

    armature = context.scene.objects.get(self.custom_armatures)

    print("--- get bones", armature)
    if armature is None:
        return
    return [(bone.name, bone.name, "") for bone in armature.data.bones]

hips_names = ["hips", "pelvis"]

neck_names = ["neck", "collar"]

shoulder_names = ["clavicle", "shoulder"]

foot_name = "foot"
toe_name = "toe"

hand_name = ["hand", "wrist"]

hand_re = re.compile("(hand)|(wrist)$")

hand_thumb_re = re.compile("thumb(finger)?1")
hand_index_re = re.compile("index(finger)?1")
hand_middle_re = re.compile("middle(finger)?1")
hand_ring_re = re.compile("ring(finger)?1")
hand_pinky_re = re.compile("(pinky)|(little)(finger)?1")

spine_name = "spine"
spine1_name = "spine1"
head_name = "head"
eye_name = "eye"

class BlendShapeMapping():
    frm =""
    to=""
    value=0
    override=False
    def __init__(self, frm, to, value, override = False):
        self.to = to
        self.value = value
        self.frm = frm
        self.override = override


common_cats_blend_mapping = [
#    BlendShapeMapping('Basis', 'BrowsU_C', 1.0),
#    BlendShapeMapping('Eyebrow Lower', 'Basis', 0.5, True), # Swap Lower Eyebrows at 0.5 as the new basis.
    BlendShapeMapping('Blink', 'EyeBlink_L', 1.0), # This assumes abit too much but MMD Avatars are fidly regardless, since
    BlendShapeMapping('vrc.v_th', 'JawOpen', 0.8),
    BlendShapeMapping('vrc.v_ss', 'MouthSmile_L', 0.8),
    BlendShapeMapping('vrc.v_nn', 'LipsFunnel', 0.8),
    BlendShapeMapping('U', 'LipsUpperClose', 0.8)
]

def automatic_bind_bones(self, avatar_bones):
    print('------')
    knee_check = False
    cleaned_bones = dict()
    for bone in avatar_bones:
        cleaned_bones[bones.clean_up_bone_name(bone.name).lower()] = bone

    keys = list(cleaned_bones.keys())
    for cleaned_name in keys:
        bone = cleaned_bones[cleaned_name]

        for hip_bone in hips_names:
            if hip_bone in cleaned_name:
                self.hips = bone.name

        if "spine2" in cleaned_name or "chest" in cleaned_name or "breast" in cleaned_name:
            self.spine2 = bone.name
        elif spine1_name in cleaned_name:
            ## if there is no Spine2, chest or breast, its likely that spine1 is the chest. Convert it.
            if cleaned_bones["spine2"] is None and cleaned_bones["chest"] is None and cleaned_bones["breast"] is None:
                self.spine2 = bone.name
            else:
                self.spine1 = bone.name
            
        elif spine_name in cleaned_name:
            self.spine = bone.name

        for neck_bone in neck_names:
            if neck_bone in cleaned_name:
                self.neck = bone.name

        if "lowerarm" in cleaned_name or "forearm" in cleaned_name or "elbow" in cleaned_name:
            self.fore_arm = bone.name
        elif "arm" in cleaned_name or "upperarm" in cleaned_name:
            self.arm = bone.name

        for shoulder_bone in shoulder_names:
            if shoulder_bone in cleaned_name:
                self.shoulder = bone.name

        if "upleg" in cleaned_name or "thigh" in cleaned_name or "upleg" in cleaned_name:
            self.up_leg = bone.name
        elif "knee" in cleaned_name or "calf" in cleaned_name:
            self.leg = bone.name

        if "knee" in cleaned_name:
            knee_check = True

        # Counter: If Knee exists somewhere, it is most likely that Leg is the upper leg.
        if knee_check and "leg" in cleaned_name:
            self.up_leg = bone.name

        if foot_name in cleaned_name or "ankle" in cleaned_name:
            self.foot = bone.name

        if toe_name in cleaned_name:
            self.toe = bone.name

        if hand_thumb_re.search(cleaned_name):
            self.hand_thumb = bone.name

        elif hand_index_re.search(cleaned_name):
            self.hand_index = bone.name

        elif hand_middle_re.search(cleaned_name):
            self.hand_middle = bone.name

        elif hand_ring_re.search(cleaned_name):
            self.hand_ring = bone.name

        elif hand_pinky_re.search(cleaned_name):
            self.hand_pinky = bone.name

        elif hand_re.search(cleaned_name) is not None:
            self.hand = bone.name

        if head_name in cleaned_name:
            self.head = bone.name

        if eye_name in cleaned_name:
            self.eye = bone.name
    


def update_bone_name(edit_bones, from_name, to_name):
    print("  - update_bone_name", from_name, "to", to_name)
    bone_to_edit = edit_bones.get(from_name)
    if bone_to_edit is not None:
        bone_to_edit.name = to_name
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")  


def update_bone_name_mirrored(edit_bones, from_name, to_name):
    print(' - update_bone_name_mirrored', from_name, to_name)
    mirrored = bones.get_bone_side_and_mirrored(from_name)
    if mirrored is not None:
        update_bone_name(edit_bones, from_name, mirrored.side + to_name)
        update_bone_name(edit_bones, mirrored.mirror_name,
                         mirrored.mirror + to_name)


def update_bone_name_chained_mirrored(edit_bones, from_name, to_name):
    print(' - update_bone_name_chained_mirrored', from_name, to_name)
    bone = bones.get_bone_side_and_mirrored(from_name)
    
    if bone is not None and bone.index is not None:
        update_bone_name(edit_bones, bone.name, bone.side + to_name + bone.index)
        update_bone_name(edit_bones, bone.mirror_name, bone.mirror + to_name + bone.index)
        
        next_index = str(int(bone.index)+1)
        
        print("going down chain to ", bone.name.replace(bone.index, next_index))
        ebone = edit_bones.get(bone.name.replace(bone.index, next_index))

        if ebone is not None and bone.index is not None:
            update_bone_name_chained_mirrored(edit_bones, ebone.name, to_name)


def rename_bones_and_fix_most_things(self, context):
    print("Rename bones fix most things", self.armature)
    if len(self.armature) < 1:
        print("Armature Update cancelled")
        return {"CANCELLED"}

    bpy.ops.wm.console_toggle()
    mode = bpy.context.area.type

    # Naming Converted
    bpy.ops.object.mode_set(mode="EDIT")
    armature = bpy.data.armatures[self.armature]
    ebones = armature.edit_bones
    
    print("--------")
    print("Updating Bone Names")
    update_bone_name(ebones, self.hips, "Hips")
    update_bone_name(ebones, self.spine, "Spine")
    update_bone_name(ebones, self.spine2, "Spine2")

    spine_was_split = False
    if len(self.spine1) < 1:
        spine1 = ebones.get("Spine2") # Get what is supposed to be the last spine.
        spine1.select = True
        bpy.ops.armature.subdivide()

        # Spine2.001 = new spine 2
        # Spine2 = spine1
        spine2 = ebones.get("Spine2.001")
        spine1.name = "Spine1"
        spine2.name = "Spine2"
        spine_was_split = True

    else:
        update_bone_name(ebones, self.spine1, "Spine1")
    
    update_bone_name(ebones, self.neck, "Neck")
    update_bone_name(ebones, self.head, "Head")

    print("--------")
    print("Updating Bone Names Mirrored")
    update_bone_name_mirrored(ebones, self.eye, "Eye")
    update_bone_name_mirrored(ebones, self.shoulder, "Shoulder")
    update_bone_name_mirrored(ebones, self.arm, "Arm")
    update_bone_name_mirrored(ebones, self.fore_arm, "ForeArm")
    update_bone_name_mirrored(ebones, self.hand, "Hand")

    update_bone_name_mirrored(ebones, self.up_leg, "UpLeg")
    update_bone_name_mirrored(ebones, self.leg, "Leg")
    update_bone_name_mirrored(ebones, self.foot, "Foot")
    update_bone_name_mirrored(ebones, self.toe, "Toe")

    print("--------")
    print("Updating Bone Names Chained Mirrored")
    update_bone_name_chained_mirrored(ebones, self.hand_thumb, "HandThumb")
    update_bone_name_chained_mirrored(ebones, self.hand_index, "HandIndex")
    update_bone_name_chained_mirrored(ebones, self.hand_middle, "HandMiddle")
    update_bone_name_chained_mirrored(ebones, self.hand_ring, "HandRing")
    update_bone_name_chained_mirrored(ebones, self.hand_pinky, "HandPinky")
    
    bpy.ops.object.mode_set(mode="OBJECT")
    armature = bpy.data.armatures[self.armature]

    object_armature = None
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE" and obj.data == armature:
            object_armature = obj
            break

    bones.reset_scale_rotation(object_armature)

    # Fixing Rotations and Scales
    # Now Refresh datablocks

    print("Reset Scale to unit scale")
    print("--------")
    print("Fix Rotations")


    bpy.ops.object.mode_set(mode="EDIT")
    
    ebones = armature.edit_bones

    for bone in ebones:
        bone.hide = False
        bone.name = bones.clean_up_bone_name(bone.name)
        bones.correct_bone_rotations(bone)
        bones.correct_bone(bone, ebones)
        

    bones.correct_bone_parents(armature.edit_bones)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    # TODO: This should be more selective and only affect the armature object's children.

    children = bpy.data.objects 
    for child in children:
        if child.type == "ARMATURE":
            child.select = True
            bones.correct_scale_rotation(child, True)
            bpy.ops.object.mode_set(mode="POSE")
            bpy.ops.pose.select_all(action="SELECT")
            bpy.ops.pose.transforms_clear()
            bpy.ops.pose.select_all(action="DESELECT")
            bpy.ops.object.mode_set(mode="OBJECT")
                
            if self.pin_problems:
                print("PIN PROBLEM")
                bpy.ops.object.mode_set(mode="EDIT")
                bones.pin_common_bones(child, self.fix_rolls)
            
        if child.type == "MESH":
            #        mesh.clean_unused_vertex_groups(child)
            bones.reset_scale_rotation(child)
            if spine_was_split:
                print("Dealing with the Spine split for" + child.name)
                spine1_weights = child.vertex_groups["Spine1"]
                if spine1_weights is not None:
                    spine1_weights.name = "Spine2"
                 
            if self.common_shapekey_correct:
                # common_cats_blend_mapping
                # Reset all shapekeys.
                ## TODO: Perhaps dettach this into a function.
                print("Going Through blendshapes and creating new ones")
                bpy.ops.object.mode_set(mode="OBJECT")
                bpy.ops.object.select_all(action="DESELECT")
                bpy.context.scene.objects.active = child
                child.select = True
                blocks = child.data.shape_keys.key_blocks

                for shape_key in blocks:
                    shape_key.value = 0

               
                for blend_map in common_cats_blend_mapping:
                    blocks.update()
                    block = blocks.get(blend_map.frm)
                    if block is not None:
                        target_block = blocks.get(blend_map.to)
                        if target_block is None:
                            block.value = blend_map.value
                            child.shape_key_add(name=blend_map.to, from_mix=True)
                            block.value = 0
            
            if self.compress_materials:
                materials.clean_materials(child.material_slots)
    
    if self.remove_ends:
        bpy.context.area.type = mode
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")
        bones.clean_ends(child)


    for material in bpy.data.materials:
        materials.flip_material_specular(material)

    if self.remove_metallic:
        materials.remove_materials_metallic(bpy.data.materials)
    
    if self.mask_textures:
        materials.convert_images_to_mask(bpy.data.images)

    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.context.area.type = mode
    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.wm.console_toggle()
    return {"FINISHED"}


class HifiCustomAvatarBinderOperator(bpy.types.Operator):
    bl_idname = "hifi.mirror_custom_avatar_bind"
    bl_label = "Custom Avatar Binding Tool"

    custom_armature_name = bpy.props.StringProperty()
    armatures = bpy.props.EnumProperty(
        name="Select Armature", items=get_armatures)

    armature = bpy.props.StringProperty()

    hips = bpy.props.StringProperty()
    spine = bpy.props.StringProperty()
    spine1 = bpy.props.StringProperty()
    spine2 = bpy.props.StringProperty()
    neck = bpy.props.StringProperty()
    head = bpy.props.StringProperty()
    # Head
    eye = bpy.props.StringProperty()
    head_top = bpy.props.StringProperty()
    # Arms
    # right
    shoulder = bpy.props.StringProperty()
    arm = bpy.props.StringProperty()
    fore_arm = bpy.props.StringProperty()
    hand = bpy.props.StringProperty()

    # Fingers
    hand_thumb = bpy.props.StringProperty()
    hand_index = bpy.props.StringProperty()
    hand_middle = bpy.props.StringProperty()
    hand_ring = bpy.props.StringProperty()
    hand_pinky = bpy.props.StringProperty()
    # Legs
    up_leg = bpy.props.StringProperty()
    leg = bpy.props.StringProperty()
    foot = bpy.props.StringProperty()
    toe = bpy.props.StringProperty()

    pin_problems = bpy.props.BoolProperty(default=True, name="Pin Problem Bones", description="Straightens spines and fixes usual feet issues")
    fix_rolls = bpy.props.BoolProperty(default=True, name="Fix Rolls", description="Fixes the rolls of all the bones to match the HumanIK reference")
    remove_metallic = bpy.props.BoolProperty(default=True, name="Remove Metallic", description="Removes pre-emptively specular color to avoid any metallicness issues")
    mask_textures = bpy.props.BoolProperty(default=True, name="Convert Textures to Masked", description="Pre-emptively converts all textures with alpha into Masked Textures as opaque textures are not supported")
    compress_materials = bpy.props.BoolProperty(default=True, name="Compress Materials", description="Pre-emptively compress materials, simplifying material count")
    remove_ends = bpy.props.BoolProperty(default=False, name="Remove _end Leaf Bones", description="Remove _end Leaf bones.")
    common_shapekey_correct = bpy.props.BoolProperty(default=True, name="Common CATs/PMD/VRC Shapekey convert", description="CATS/PMD/VRC Shapekeys into Faceshift format")

    def execute(self, context):
        return rename_bones_and_fix_most_things(self, context)

    def invoke(self, context, event):
        if self.armatures:
            armature = context.scene.objects[self.armatures]
            bpy.ops.object.mode_set(mode="OBJECT")

            bpy.ops.object.select_all(action='DESELECT')
            armature.select = True
            context.scene.objects.active = armature

            bpy.ops.object.mode_set(mode="EDIT")
            data = armature.data
            self.armature = data.name

            bones.nuke_mixamo_prefix(data.edit_bones)

            bpy.ops.object.mode_set(mode="OBJECT")
            automatic_bind_bones(self, data.bones)

        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, context):
        layout = self.layout
        layout.label(
            "Experimental Feature. Please report any issues.")
        layout.label("Everything is mirrored.")
        column = layout.column()

       # column.prop_search(scene, "custom_current_armature", bpy.data, "armatures", icon='ARMATURE_DATA', text="Select Armature")
        column.prop(self, "armatures")
        # context.scene.object[self.armatures]
        # TODO: If avatar is not selected by default.

        if self.armatures is not "":
            data = context.scene.objects[self.armatures].data

            # Do Filtering of the data set

            column.prop_search(self, 'hips', data, 'bones',
                               icon='BONE_DATA', text='Hips')
            column.prop_search(self, 'spine', data, 'bones',
                               icon='BONE_DATA', text='Spine')
            column.prop_search(self, 'spine1', data, 'bones',
                               icon='BONE_DATA', text='Spine Additional*')
            column.prop_search(self, 'spine2', data, 'bones',
                               icon='BONE_DATA', text='Chest')
            column.prop_search(self, 'neck', data, 'bones',
                               icon='BONE_DATA', text='Neck')
            column.prop_search(self, 'head', data, 'bones',
                               icon='BONE_DATA', text='Head')

            # Head
            column.prop_search(self, 'eye', data, 'bones',
                               icon='BONE_DATA', text='Left Eye')

            column.prop_search(self, 'head_top', data, 'bones',
                               icon='BONE_DATA', text='Head Top')
            # Arms
            column.prop_search(self, 'shoulder', data, 'bones',
                               icon='BONE_DATA', text='Shoulder')
            column.prop_search(self, 'arm', data, 'bones',
                               icon='BONE_DATA', text='Arm')
            column.prop_search(self, 'fore_arm', data, 'bones',
                               icon='BONE_DATA', text='ForeArm')
            column.prop_search(self, 'hand', data, 'bones',
                               icon='BONE_DATA', text='Hand')

            column.prop_search(self, 'hand_thumb', data,
                               'bones', icon='BONE_DATA', text='Thumb 1st')
            column.prop_search(self, 'hand_index', data, 'bones',
                               icon='BONE_DATA', text='Index Finger 1st')
            column.prop_search(self, 'hand_middle', data, 'bones',
                               icon='BONE_DATA', text='Middle Finger 1st')
            column.prop_search(self, 'hand_ring', data, 'bones',
                               icon='BONE_DATA', text='Ring Finger 1st')
            column.prop_search(self, 'hand_pinky', data,
                               'bones', icon='BONE_DATA', text='Pinky 1st')

            # Legs
            column.prop_search(self, 'up_leg', data, 'bones',
                               icon='BONE_DATA', text='Thigh')
            column.prop_search(self, 'leg', data, 'bones',
                               icon='BONE_DATA', text='Leg')
            column.prop_search(self, 'foot', data, 'bones',
                               icon='BONE_DATA', text='Foot')
            column.prop_search(self, 'toe', data, 'bones',
                               icon='BONE_DATA', text='Toe')

            column.prop(self, "cats_convert")
            column.label("Bones")

            row = column.row()
            row.prop(self, "pin_problems")
            row.prop(self, "fix_rolls")
            

            column.label("Materials")
            
            row = column.row()
            row.prop(self, "remove_metallic")
            row.prop(self, "mask_textures")

            row = column.row()
            row.prop(self, "compress_materials")

        else:
            print(" No Armatures")

        print("custom_armature_name", self.custom_armature_name)
        # After selecting armature, iterate through bones.

# https://blender.stackexchange.com/questions/19293/prop-search-armature-bones


def scene_define():
    bpy.types.Scene.custom_armature_name = bpy.props.StringProperty()

    bpy.types.Scene.custom_armature_collection = bpy.props.CollectionProperty(
        type=bpy.types.PropertyGroup)


def scene_delete():
    del bpy.types.Scene.custom_armature_collection
    del bpy.types.Scene.custom_armature_name


def custom_register():
    bpy.utils.register_class(HifiCustomAvatarBinderOperator)


def custom_unregister():
    bpy.utils.unregister_class(HifiCustomAvatarBinderOperator)
