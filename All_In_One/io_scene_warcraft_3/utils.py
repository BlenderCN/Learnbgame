
import bpy
from . import constants


ACTION_NAME_UNANIMATED = '#UNANIMATED'


def set_animation(self, context):
    setAnimationName = context.armature.warcraft_3.sequencesList[context.armature.warcraft_3.sequencesListIndex].name
    if len(setAnimationName) and bpy.data.actions.get(setAnimationName, None):
        armatureObject = context.object
        if armatureObject.animation_data == None:
            armatureObject.animation_data_create()
        setAction = bpy.data.actions[setAnimationName]
        armatureObject.animation_data.action = setAction
        bpy.context.scene.frame_start = setAction.frame_range[0]
        bpy.context.scene.frame_end = setAction.frame_range[1]
        for action in bpy.data.actions:
            for object in bpy.context.scene.objects:
                setObjectAnimationName = setAnimationName + ' ' + object.name
                if action.name == setObjectAnimationName:
                    if object.animation_data == None:
                        object.animation_data_create()
                    object.animation_data.action = action
    else:
        action = bpy.data.actions.get(ACTION_NAME_UNANIMATED, None)
        if action:
            armatureObject = context.object
            if armatureObject.animation_data == None:
                armatureObject.animation_data_create()
            setAction = bpy.data.actions[ACTION_NAME_UNANIMATED]
            armatureObject.animation_data.action = setAction
            bpy.context.scene.frame_start = setAction.frame_range[0]
            bpy.context.scene.frame_end = setAction.frame_range[1]
            for object in bpy.context.scene.objects:
                objectActionName = ACTION_NAME_UNANIMATED + ' ' + object.name
                if bpy.data.actions.get(objectActionName, None):
                    if object.animation_data == None:
                        object.animation_data_create()
                    object.animation_data.action = bpy.data.actions[objectActionName]


def set_team_color_property(self, context):
    self.teamColor = constants.TEAM_COLORS[self.setTeamColor]


def set_bone_node_type(self, context):
    bone = context.active_bone
    if bone:
        nodeType = bone.warcraft_3.nodeType
        object = context.object
        boneGroup = object.pose.bone_groups.get(nodeType.lower() + 's', None)
        if not boneGroup:
            if nodeType in {'BONE', 'ATTACHMENT', 'COLLISION_SHAPE', 'EVENT', 'HELPER'}:
                bpy.ops.pose.group_add()
                boneGroup = object.pose.bone_groups.active
                boneGroup.name = nodeType.lower() + 's'
                if nodeType == 'BONE':
                    boneGroup.color_set = 'THEME04'
                elif nodeType == 'ATTACHMENT':
                    boneGroup.color_set = 'THEME09'
                elif nodeType == 'COLLISION_SHAPE':
                    boneGroup.color_set = 'THEME02'
                elif nodeType == 'EVENT':
                    boneGroup.color_set = 'THEME03'
                elif nodeType == 'HELPER':
                    boneGroup.color_set = 'THEME01'
            else:
                boneGroup = None
        object.pose.bones[bone.name].bone_group = boneGroup
