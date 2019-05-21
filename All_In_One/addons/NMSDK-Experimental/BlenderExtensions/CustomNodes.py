import bpy
from bpy.props import (StringProperty, BoolProperty, EnumProperty, IntProperty,
                       FloatProperty)
from bpy.types import NodeTree, Node, NodeSocket
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


def retBool(x):
    return bool(x)


# custom button in the node editor to change the mode to the custom NMS mode
class NMSATTree(NodeTree):
    '''NMS Action Trigger entity creator'''
    bl_idname = 'NMSATTree'
    bl_label = 'NMS Action Trigger Tree'
    bl_icon = 'NODETREE'


# custom socket type. Contains no data but just has the name of the socket for
# clarity.
class NMSSocket(NodeSocket):
    '''NMS Trigger Socket. Gets and sends no data, is simply used as a label'''
    bl_idnname = 'NMSSocket'
    bl_label = 'NMS Trigger Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (1.0, 0.0, 1.0, 0.75)


class NMSJoinSocket(NodeSocket):
    '''NMS inter-Action Trigger Socket. Gets and sends no data, is simply used
    as a label'''
    bl_idnname = 'NMSJoinSocket'
    bl_label = 'NMS Joiner Socket'

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (0.0, 1.0, 0.0, 0.75)


# base class for all the custom NMS Nodes
class NMSATNode:
    @classmethod
    def poll(cls, ntree):       # only show if we are inside the NMS AT Tree
        return ntree.bl_idname == 'NMSATTree'


""" Actions """


class NMS_WarpAction(Node, NMSATNode):
    '''GcWarpAction Node'''
    bl_idname = 'NMS_WarpAction'
    bl_label = 'Warp Action Node'
    bl_icon = 'SOUND'

    WarpType = EnumProperty(
        name='Warp Type',
        description='Type of warp required.',
        items=[("BlackHole", "BlackHole", "Blackhole warp")])

    def init(self, context):
        self.inputs.new('NMSSocket', "Trigger")

    def draw_buttons(self, context, layout):
        layout.prop(self, "WarpType")

    def draw_label(self):
        return "Warp Action"


class NMS_PlayAudioAction(Node, NMSATNode):
    '''GcPlayAudioAction Node'''
    bl_idname = 'NMS_PlayAudioAction'
    bl_label = 'Play Audio Action Node'
    bl_icon = 'SOUND'

    Sound = StringProperty(
        name='Sound Name',
        description='Name of the sound from the game files you wish to play.')
    UseOcclusion = BoolProperty(name='Use Occlusion',
                                description='Whether or not to use occlusion.')
    OcclusionRadius = FloatProperty(
        name='Occlusion Radius',
        description='Radius of occlusion zone if used')

    def init(self, context):
        self.inputs.new('NMSSocket', "Trigger")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Sound")
        layout.prop(self, "UseOcclusion")
        layout.prop(self, "OcclusionRadius")

    def draw_label(self):
        return "Play Audio Action"


class NMS_PlayAnimAction(Node, NMSATNode):
    '''GcPlayAnimAction Node'''
    bl_idname = 'NMS_PlayAnimAction'
    bl_label = 'Play Anim Action Node'
    bl_icon = 'SOUND'

    Anim = StringProperty(
        name='Anim Name',
        description='Name of the anim from the game files you wish to play.')

    def init(self, context):
        self.inputs.new('NMSSocket', "Trigger")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Anim")

    def draw_label(self):
        return "Play Anim Action"


class NMS_GoToStateAction(Node, NMSATNode):
    '''GcGoToStateAction Node'''
    bl_idname = 'NMS_GoToStateAction'
    bl_label = 'Go To State Action Node'
    bl_icon = 'SOUND'

    State = StringProperty(
        name='Action State Name',
        description='Name of the action state you wish to go to.')
    Broadcast = BoolProperty(
        name='Broadcast',
        description='Whether or not to broadcast action to another scene.')
    BroadcastLevel = EnumProperty(
        name='Broadcast Levels',
        description='The level at which to broadcast an action.',
        items=[("Scene", "Scene", "Broadcast to Scene"),
               ("LocalModel", "LocalModel", "Broadcast to Local Model")])

    def init(self, context):
        self.inputs.new('NMSSocket', "Trigger")
        self.outputs.new('NMSJoinSocket', "To Node")

    def draw_buttons(self, context, layout):
        layout.prop(self, "State")
        layout.prop(self, "Broadcast")
        layout.prop(self, "BroadcastLevel")

    def draw_label(self):
        return "Go To State Action"


class NMS_CameraShakeAction(Node, NMSATNode):
    '''GcCameraShakeAction Node'''
    bl_idname = 'NMS_CameraShakeAction'
    bl_label = 'Camera Shake Action Node'
    bl_icon = 'SOUND'

    Shake = StringProperty(name='Shake ID',
                           description='ID for type of camera shake')
    FalloffMin = FloatProperty(name='Falloff Min',
                                    description='Camera shake falloff min.')
    FalloffMax = FloatProperty(name='FalloffMax',
                                    description='Camera shake falloff max.')

    def init(self, context):
        self.inputs.new('NMSSocket', "Trigger")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Shake")
        layout.prop(self, "FalloffMin")
        layout.prop(self, "FalloffMax")

    def draw_label(self):
        return "Camera Shake Action"


class NMS_PainAction(Node, NMSATNode):
    '''GcPainAction Node'''
    bl_idname = 'NMS_PainAction'
    bl_label = 'Pain Action Node'
    bl_icon = 'SOUND'

    Damage = StringProperty(name='Damage ID',
                            description='ID for type of damage.')
    Radius = FloatProperty(name='Radius',
                           description='Distance at which to inflict PAIN')
    AffectsPlayer = BoolProperty(name='Affects Player',
                                 description='Whether to affect player.')

    def init(self, context):
        self.inputs.new('NMSSocket', "Trigger")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Damage")
        layout.prop(self, "Radius")
        layout.prop(self, "AffectsPlayer")

    def draw_label(self):
        return "Pain Action"


class NMS_NodeActivationAction(Node, NMSATNode):
    '''GcNodeActivationAction Node'''
    bl_idname = 'NMS_NodeActivationAction'
    bl_label = 'Node Activation Action Node'
    bl_icon = 'SOUND'

    NodeActiveState = EnumProperty(
        name='Node Active State Values',
        description='Node activation states',
        items=[("Activate", "Activate", "Enable a scene node"),
               ("Deactivate", "Deactivate", "Disable a scene node"),
               ("Toggle", "Toggle", "Toggle a scene node")])
    Name = StringProperty(name='Node name',
                          description='Name of scene node you wish to affect.')
    SceneToAdd = StringProperty(
        name='Scene to add',
        description='Name of scene node you wish to add.')
    IncludePhysics = BoolProperty(name='Include physics',
                                  description='Unclear effects.')
    NotifyNPC = BoolProperty(name='Notify NPC',
                             description='Unclear effects.')
    UseMasterModel = BoolProperty(name='Use master model',
                                  description='Unclear effects.')
    RestartEmitters = BoolProperty(name='Restart emitters',
                                   description='Unclear effects.')

    def init(self, context):
        self.inputs.new('NMSSocket', "Trigger")

    def draw_buttons(self, context, layout):
        layout.prop(self, "NodeActiveState")
        layout.prop(self, "Name")
        layout.prop(self, "SceneToAdd")
        layout.prop(self, "IncludePhysics")
        layout.prop(self, "NotifyNPC")
        layout.prop(self, "UseMasterModel")
        layout.prop(self, "RestartEmitters")

    def draw_label(self):
        return "Node Activation Action"


class NMS_RewardAction(Node, NMSATNode):
    '''GcRewardAction Node'''
    bl_idname = 'NMS_RewardAction'
    bl_label = 'Reward Action Node'
    bl_icon = 'SOUND'

    Reward = StringProperty(
        name='Reward ID',
        description='ID of the reward from REWARDTABLE.MBIN.')

    def init(self, context):
        self.inputs.new('NMSSocket', "Trigger")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Reward")

    def draw_label(self):
        return "Reward Action"


class NMS_SpawnAction(Node, NMSATNode):
    '''GcSpawnAction Node'''
    bl_idname = 'NMS_SpawnAction'
    bl_label = 'Spawn Action Node'
    bl_icon = 'SOUND'

    Event = StringProperty(
        name='Event ID',
        description='ID of the event from the game files you wish to spawn.')

    def init(self, context):
        self.inputs.new('NMSSocket', "Trigger")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Event")

    def draw_label(self):
        return "Spawn Action"


class NMS_DestroyAction(Node, NMSATNode):
    '''GcDestroyAction Node'''
    bl_idname = 'NMS_DestroyAction'
    bl_label = 'Destroy Action Node'
    bl_icon = 'SOUND'

    DestroyAll = BoolProperty(name='Destroy All',
                              description='Unclear effects.')

    def init(self, context):
        self.inputs.new('NMSSocket', "Trigger")

    def draw_buttons(self, context, layout):
        layout.prop(self, "DestroyAll")

    def draw_label(self):
        return "Destroy Action"


class NMS_ParticleAction(Node, NMSATNode):
    '''GcParticleAction Node'''
    bl_idname = 'NMS_ParticleAction'
    bl_label = 'Particle Action Node'
    bl_icon = 'SOUND'

    Effect = StringProperty(
        name='Effect ID',
        description='ID of the effect from the game files you wish to appear.')
    Joint = StringProperty(
        name='Joint name',
        description=('Name of the locator scene node where you wish the '
                     'effect to appear at.'))
    Exact = BoolProperty(
        name='Exact',
        description=('Possibly whether or not for effect to appear exactly on '
                     'joint'))

    def init(self, context):
        self.inputs.new('NMSSocket', "Trigger")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Effect")
        layout.prop(self, "Joint")
        layout.prop(self, "Exact")

    def draw_label(self):
        return "Particle Action"


class NMS_DisplayText(Node, NMSATNode):
    '''GcDisplayText Node'''
    bl_idname = 'NMS_DisplayText'
    bl_label = 'Display Text Node'
    bl_icon = 'SOUND'

    HUDTextDisplayTypeValues = EnumProperty(
        name='HUD Display Text Values',
        description='HUD Display Text Types',
        items=[("Full", "Full", "[Discovery style text display?]"),
               ("Compact", "Compact", "[Uncertain.]"),
               ("EyeLevel", "EyeLevel", "[Uncertain.]"),
               ("Prompt", "Prompt", "[Uncertain.]"),
               ("Tooltip", "Tooltip", "Lower right hand corner tooltips.")])
    Title = StringProperty(name='Title text',
                           description='Title text to display.')
    Subtitle1 = StringProperty(name='Subtitle 1 text',
                               description='Subtitle text to display.')
    Subtitle2 = StringProperty(name='Subtitle 2 text',
                               description='Subtitle text to display.')

    def init(self, context):
        self.inputs.new('NMSSocket', "Trigger")

    def draw_buttons(self, context, layout):
        layout.prop(self, "HUDTextDisplayTypeValues")
        layout.prop(self, "Title")
        layout.prop(self, "Subtitle1")
        layout.prop(self, "Subtitle2")

    def draw_label(self):
        return "Display Text"


""" Triggers """


class NMS_PlayerNearbyEvent(Node, NMSATNode):
    '''GcPlayerNearbyEvent Node'''
    bl_idname = 'NMS_PlayerNearbyEvent'
    bl_label = 'Player Nearby Trigger Node'
    bl_icon = 'SOUND'

    RequirePlayerAction = EnumProperty(
        name='Require Player Action',
        description='State player must be in to cause trigger to occur',
        items=[("None", "None", "No special state"),
               ("Fire", "Fire", "Player must be firing?"),
               ("In Ship", "InShip", "Player must be in their ship"),
               ("On Foot", "OnFoot", "Player must be on foot"),
               ("On Foot Outside", "OnFootOutside", ("Player must be on foot "
                                                     "and outside")),
               ("Upload", "Upload", "Triggered if player is uploading (?)")])
    Distance = FloatProperty(
        name="Distance",
        description="Distance from object to cause trigger")
    Angle = FloatProperty(
        name="Angle",
        description="Angle within which the trigger area is effective")
    AnglePlayerRelative = BoolProperty(
        name="Angle Player Relative",
        description="Angle is relative to player?")
    AngleOffset = FloatProperty(
        name="Angle Offset",
        description="Offset of chosen angle...?")
    AngleReflected = BoolProperty(
        name="Angle Reflected",
        description="Reflection of chosen angle...?")
    AngleMinDistance = FloatProperty(
        name="Angle Min Distance",
        description="Minimum distance to chosen angle...?")
    DistanceCheckTypeValues = EnumProperty(
        name='Distance Check Type',
        description='Distance Check Types',
        items=[("Radius", "Radius", "Radius distance check"),
               ("BoundingBox", "BoundingBox", "BoundingBox distance check")])
    Inverse = BoolProperty(
        name="Inverse",
        description="Invert the distance check.")

    def init(self, context):
        self.inputs.new('NMSJoinSocket', "From Node")
        self.outputs.new('NMSSocket', "Action")

    def draw_buttons(self, context, layout):
        layout.prop(self, "RequirePlayerAction")
        layout.prop(self, "Distance")
        layout.prop(self, "Angle")
        layout.prop(self, "AnglePlayerRelative")
        layout.prop(self, "AngleOffset")
        layout.prop(self, "AngleReflected")
        layout.prop(self, "AngleMinDistance")
        layout.prop(self, "DistanceCheckTypeValues")
        layout.prop(self, "Inverse")

    def draw_label(self):
        return "Play Nearby Trigger"


class NMS_BeenShotEvent(Node, NMSATNode):
    '''GcBeenShotEvent Node'''
    bl_idname = 'NMS_BeenShotEvent'
    bl_label = 'Been Shot Trigger Node'
    bl_icon = 'SOUND'

    ShotBy = EnumProperty(
        name='Been shot by',
        description='What the object has to be shot by to trigger the action',
        items=[("Player", "Player", "The player"),
               ("Anything", "Anything", "Anything")])
    DamageThreshold = IntProperty(
        name="Damage Threshold",
        description="Amount of damage given before action will be triggered")
    HealthThreshold = FloatProperty(
        name="Health Threshold",
        description="Health value at which action will be triggered (?)")

    def init(self, context):
        self.inputs.new('NMSJoinSocket', "From Node")
        self.outputs.new('NMSSocket', "Action")

    def draw_buttons(self, context, layout):
        layout.prop(self, "ShotBy")
        layout.prop(self, "DamageThreshold")
        layout.prop(self, "HealthThreshold")

    def draw_label(self):
        return "Been Shot Trigger"


class NMS_StateTimeEvent(Node, NMSATNode):
    '''GcStateTimeEvent Node'''
    bl_idname = 'NMS_StateTimeEvent'
    bl_label = 'State Time Trigger Node'
    bl_icon = 'SOUND'

    Time = FloatProperty(name="Seconds",
                         description="Seconds to wait for setting off trigger")

    def init(self, context):
        self.inputs.new('NMSJoinSocket', "From Node")
        self.outputs.new('NMSSocket', "Action")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Time")

    def draw_label(self):
        return "State Time Trigger"


class NMS_AnimFrameEvent(Node, NMSATNode):
    '''GcAnimFrameEvent Node'''
    bl_idname = 'NMS_AnimFrameEvent'
    bl_label = 'Anim Frame Trigger Node'
    bl_icon = 'SOUND'

    Anim = StringProperty(
        name='Anim Name',
        description='Name of anim from game files you wish to activate.')
    FrameStart = IntProperty(
        name="Frame Start",
        description="The frame on which to trigger actions.")
    StartFromEnd = BoolProperty(
        name='Start From End',
        description='Whether or not to count frames from end of anim[?]')

    def init(self, context):
        self.inputs.new('NMSJoinSocket', "From Node")
        self.outputs.new('NMSSocket', "Action")

    def draw_buttons(self, context, layout):
        layout.prop(self, "Anim")
        layout.prop(self, "FrameStart")
        layout.prop(self, "StartFromEnd")

    def draw_label(self):
        return "Anim Frame Trigger"


# custom categories for new nodes
class NMSNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'NMSATTree'


class NMSNodes():
    def __init__(self):
        self.node_categories = [
            NMSNodeCategory(
                "ActionNodes",
                "Action Nodes",
                items=[NodeItem('NMS_GoToStateAction'),
                       NodeItem('NMS_PlayAnimAction'),
                       NodeItem('NMS_NodeActivationAction'),
                       NodeItem('NMS_RewardAction'),
                       NodeItem('NMS_PlayAudioAction'),
                       NodeItem('NMS_WarpAction'),
                       NodeItem('NMS_CameraShakeAction'),
                       NodeItem('NMS_PainAction'),
                       NodeItem('NMS_SpawnAction'),
                       NodeItem('NMS_DestroyAction'),
                       NodeItem('NMS_ParticleAction'),
                       NodeItem('NMS_DisplayText')]),
            NMSNodeCategory(
                "TriggerNodes",
                "Trigger Nodes",
                items=[NodeItem('NMS_PlayerNearbyEvent'),
                       NodeItem('NMS_BeenShotEvent'),
                       NodeItem('NMS_StateTimeEvent'),
                       NodeItem('NMS_AnimFrameEvent')]),
            NMSNodeCategory(
                "OtherNodes",
                "Other Nodes",
                items=[NodeItem('NodeFrame')])]

    def register(self):
        # register base classes
        bpy.utils.register_class(NMSATTree)
        bpy.utils.register_class(NMSSocket)
        bpy.utils.register_class(NMSJoinSocket)
        # register Actions
        bpy.utils.register_class(NMS_WarpAction)
        bpy.utils.register_class(NMS_PlayAudioAction)
        bpy.utils.register_class(NMS_PlayAnimAction)
        bpy.utils.register_class(NMS_GoToStateAction)
        bpy.utils.register_class(NMS_CameraShakeAction)
        bpy.utils.register_class(NMS_PainAction)
        bpy.utils.register_class(NMS_NodeActivationAction)
        bpy.utils.register_class(NMS_RewardAction)
        bpy.utils.register_class(NMS_SpawnAction)
        bpy.utils.register_class(NMS_DestroyAction)
        bpy.utils.register_class(NMS_ParticleAction)
        bpy.utils.register_class(NMS_DisplayText)
        # register triggers
        bpy.utils.register_class(NMS_PlayerNearbyEvent)
        bpy.utils.register_class(NMS_BeenShotEvent)
        bpy.utils.register_class(NMS_StateTimeEvent)
        bpy.utils.register_class(NMS_AnimFrameEvent)
        # register menu item
        nodeitems_utils.register_node_categories("CUSTOM_NODES",
                                                 self.node_categories)

    def unregister(self):
        # unregister menu item
        nodeitems_utils.unregister_node_categories("CUSTOM_NODES")
        # unregister Actions
        bpy.utils.unregister_class(NMS_WarpAction)
        bpy.utils.unregister_class(NMS_PlayAudioAction)
        bpy.utils.unregister_class(NMS_PlayAnimAction)
        bpy.utils.unregister_class(NMS_GoToStateAction)
        bpy.utils.unregister_class(NMS_CameraShakeAction)
        bpy.utils.unregister_class(NMS_PainAction)
        bpy.utils.unregister_class(NMS_NodeActivationAction)
        bpy.utils.unregister_class(NMS_RewardAction)
        bpy.utils.unregister_class(NMS_SpawnAction)
        bpy.utils.unregister_class(NMS_DestroyAction)
        bpy.utils.unregister_class(NMS_ParticleAction)
        bpy.utils.unregister_class(NMS_DisplayText)
        # unregister triggers
        bpy.utils.unregister_class(NMS_PlayerNearbyEvent)
        bpy.utils.unregister_class(NMS_BeenShotEvent)
        bpy.utils.unregister_class(NMS_StateTimeEvent)
        bpy.utils.unregister_class(NMS_AnimFrameEvent)
        # unregister base classes
        bpy.utils.unregister_class(NMSATTree)
        bpy.utils.unregister_class(NMSSocket)
        bpy.utils.unregister_class(NMSJoinSocket)
