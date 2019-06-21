import bpy
from .ot_preview import set_fr_steps
from math import pi, cos, sin, radians
from mathutils import Quaternion, Vector, Matrix
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    IntVectorProperty,
    PointerProperty,
    StringProperty,
    )

# Collection
class WalkCycleNewBones(bpy.types.PropertyGroup):
    def to_quaternion(self, context):
        rig = context.object
        try: # context.awc_bone not in locals if reset to default values :(
            bone = rig.pose.bones[context.awc_bone.name]
            if bone.rotation_mode == 'AXIS_ANGLE':
                self.qua1 = Quaternion(self.axi1[1:], self.axi1[0])
                self.qua2 = Quaternion(self.axi2[1:], self.axi2[0])
            else:
                eul1 = self.eul1.copy()
                eul2 = self.eul2.copy()
                eul1.order = eul2.order = bone.rotation_mode
                self.qua1 = eul1.to_quaternion()
                self.qua2 = eul2.to_quaternion()
        except:
            self.qua1 = self.qua2 = 1.0,0.0,0.0,0.0

    _seq_items = [
        ("ES", "Each Step", "Starts when a foot starts moving and ends when the other foot starts moving."),
        ("LR", "Left to Right", "Starts and ends with the left foot starts moving (Foot lower)"),
        ("M", "Middle", "Starts and ends in the middle of a step (Foot higher)"),
        ]
    name = StringProperty(
        name="",
        options = {'LIBRARY_EDITABLE','TEXTEDIT_UPDATE'},
        )
    seq_type = EnumProperty(
        items=_seq_items,
        name="Sequence type",
        default="LR",
        )
    loc1 = FloatVectorProperty(
        name="Initial Location",
        default=(0.0, 0.0, 0.0),
        subtype='TRANSLATION',
        )
    loc2 = FloatVectorProperty(
        name="Final Location",
        default=(0.0, 0.0, 0.0),
        subtype='TRANSLATION',
        )
    qua1 = FloatVectorProperty(
        name="Initial Rotation",
        default=(1.0, 0.0, 0.0, 0.0),
        subtype='QUATERNION',
        size=4,
        )
    qua2 = FloatVectorProperty(
        name="Final Rotation",
        default=(1.0, 0.0, 0.0, 0.0),
        subtype='QUATERNION',
        size=4,
        )
    eul1 = FloatVectorProperty(
        name="Initial Rotation",
        default=(0.0, 0.0, 0.0),
        subtype='EULER',
        size=3,
        update = to_quaternion,
        )
    eul2 = FloatVectorProperty(
        name="Final Rotation",
        default=(0.0, 0.0, 0.0),
        subtype='EULER',
        size=3,
        update = to_quaternion,
        )
    axi1 = FloatVectorProperty(
        name="Initial Rotation",
        default=(0.0, 0.0, 1.0, 0.0),
        subtype='AXISANGLE',
        size=4,
        update = to_quaternion,
        )
    axi2 = FloatVectorProperty(
        name="Final Rotation",
        default=(0.0, 0.0, 1.0, 0.0),
        subtype='AXISANGLE',
        size=4,
        update = to_quaternion,
        )
    expand = BoolProperty(
        name="Expand",
        description="1",
        options = {'LIBRARY_EDITABLE'},
        default=True
        )
    show = BoolProperty(
        name="Show",
        default=True
        )
    add_torso = BoolProperty(
        name="Add torso movement",
        description="Adds the location and rotation of the torso",
        default=False
        )

class WalkCycleSettings(bpy.types.PropertyGroup):

    @staticmethod
    def set_vec(axis):
        if axis == 'x_axis':
            vec = Vector((1.0, 0.0, 0.0))
        elif axis == 'y_axis':
            vec = Vector((0.0, 1.0, 0.0))
        elif axis == 'z_axis':
            vec = Vector((0.0, 0.0, 1.0))
        elif axis == '-x_axis':
            vec = Vector((-1.0, 0.0, 0.0))
        elif axis == '-y_axis':
            vec = Vector((0.0, -1.0, 0.0))
        elif axis == '-z_axis':
            vec = Vector((0.0, 0.0, -1.0))
        else:
            vec = Vector()
        return vec

    def reset_torso(self, context):
        rig = context.object
        bone = rig.pose.bones[self.torso]
        bone_dat = rig.data.bones[self.torso]
        parent = bone.parent.matrix*bone_dat.parent.matrix_local.inverted()
        bone.matrix = parent*bone_dat.matrix_local

    def update_axis(self, context):
        _up = self.set_vec(self.up_torso)
        _fr = self.set_vec(self.forward_torso)
        self.up_axis = _up
        self.front_axis = _fr
        self.side_axis = _fr.cross(_up)

    _axis = [
        ("x_axis", "X", ""),
        ("y_axis", "Y", ""),
        ("z_axis", "Z", ""),
        ("-x_axis", "-X", ""),
        ("-y_axis", "-Y", ""),
        ("-z_axis", "-Z", ""),
        ]
    new_bones = CollectionProperty(
        type=WalkCycleNewBones,
        )
    torso = StringProperty(
        name="Torso",
        description="Torso Bone",
        subtype='NONE',
        )
    expand = BoolProperty(
        name="Expand",
        default=True
        )
    forward_torso = EnumProperty(
        items=_axis,
        name="Forward",
        description="Axis that points forward",
        default="-y_axis",
        update = update_axis,
        )
    up_torso = EnumProperty(
        items=_axis,
        name="Up",
        description="Axis that points upward",
        default="z_axis",
        update = update_axis,
        )
    l_foot_ik = StringProperty(
        name="L_Foot_ik",
        description="Left Foot Bone IK",
        subtype='NONE',
        )
    r_foot_ik = StringProperty(
        name="R_Foot_ik",
        description="Right Foot Bone IK",
        subtype='NONE',
        )
    anticipation = FloatProperty(
        name="Anticipation",
        description="Movement Anticipation",
        default=0.55,
        min=0.0,
        max=1.0,
        )
    step = FloatProperty(
        name="Step",
        description="",
        default=0.7,
        min=0.0,
        unit='LENGTH',
        precision=7,
        update = set_fr_steps,
        )
    step_by_frames = BoolProperty(
        name="Step by Frames",
        description="A step is defined by the difference in frames",
        default=False,
        update = set_fr_steps,
        )
    step_frames = IntProperty(
        name="Frames",
        description="Frames between two steps",
        default=24,
        update = set_fr_steps,
        )
    amp = FloatProperty(
        name="Amplitude",
        description="Maximum feet movement",
        default=0.08,
        min=0.0,
        unit='LENGTH',
        )
    openness = FloatProperty(
        name="Openness",
        description="Lateral movement of the foot",
        default=-0.06,
        unit='LENGTH',
        )
    foot_rot = FloatProperty(
        name="Rotation",
        description="Maximum feet movement",
        default=0.785398,
        unit='ROTATION',
        )
    anim = BoolProperty(
        name="Get Animation",
        description="Get Animation",
        default=True,
        update = reset_torso,
        )
    frequency = IntProperty(
        name="Frequency",
        description="Frames between two steps",
        default=24,
        )
    up_axis = FloatVectorProperty(
        default=(0.0, 0.0, 1.0),
        subtype='XYZ',
        )
    front_axis = FloatVectorProperty(
        default=(0.0, -1.0, 0.0),
        subtype='XYZ',
        )
    side_axis = FloatVectorProperty(
        default=(-1.0, 0.0, 0.0),
        subtype='XYZ',
        )
    frame_start = IntProperty(
        name="Start",
        description="Frame that begins to generate",
        default=1,
        )
    frame_end = IntProperty(
        name="End",
        description="Frame that ends to generate",
        default=250,
        )

def register():
    bpy.utils.register_class(WalkCycleNewBones)
    bpy.utils.register_class(WalkCycleSettings)
    bpy.types.Armature.aut_walk_cycle = PointerProperty(type=WalkCycleSettings)
    #bpy.app.handlers.frame_change_pre.clear()


def unregister():
    del bpy.types.Armature.aut_walk_cycle
    bpy.utils.unregister_class(WalkCycleSettings)
    bpy.utils.unregister_class(WalkCycleNewBones)

if __name__ == "__main__":
    register()
