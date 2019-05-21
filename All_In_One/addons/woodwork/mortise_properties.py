import bpy
from bpy.props import *


class MortiseHaunch(bpy.types.PropertyGroup):
    type = bpy.props.EnumProperty(
        items=[('value',
                "Value",
                "Give value to haunch depth"),
               ('percentage',
                "Percentage",
                "Set haunch depth by percentage")],
        name="Haunch value type",
        default='value')

    depth_value = bpy.props.FloatProperty(
        name="Haunch depth",
        description="Haunch depth",
        min=0.0,
        default=-1.0,
        subtype='DISTANCE',
        unit='LENGTH',
        precision=3,
        step=0.1)

    depth_percentage = bpy.props.FloatProperty(
        name="Haunch depth",
        description="Haunch depth (relative to tenon depth)",
        min=0.0,
        max=1.0,
        subtype='PERCENTAGE')

    angle = bpy.props.EnumProperty(
        items=[('straight',
                "Straight",
                "Use a straight haunch"),
               ('sloped',
                "Sloped",
                "Use a sloping haunch")],
        name="Haunch angle",
        default='straight')


class MortiseThicknessPropertyGroup(bpy.types.PropertyGroup):
    type = bpy.props.EnumProperty(
        items=[('max',
                "Max. thickness",
                "Set thickness to the maximum width"),
               ('value',
                "Value",
                "Give value to thickness"),
               ('percentage',
                "Percentage",
                "Set thickness by percentage")],
        name="Thickness type",
        default='value')

    value = bpy.props.FloatProperty(
        name="Thickness",
        description="Mortise thickness (relative to width side)",
        min=0.0,
        default=-1.0,
        subtype='DISTANCE',
        unit='LENGTH',
        precision=3,
        step=0.1)

    percentage = bpy.props.FloatProperty(
        name="Thickness",
        description="Mortise thickness (relative to width side)",
        min=0.0,
        max=1.0,
        subtype='PERCENTAGE')

    centered = bpy.props.BoolProperty(
        name="Centered",
        description="Specify if mortise is centered on width side",
        default=True)

    shoulder_type = bpy.props.EnumProperty(
        items=[('value',
                "Value",
                "Give value to shoulder thickness"),
               ('percentage',
                "Percentage",
                "Set thickness shoulder by percentage")],
        name="Thickness shoulder type",
        default='value')

    shoulder_value = bpy.props.FloatProperty(
        name="Shoulder",
        description="Mortise shoulder on width side",
        min=0.0,
        default=-1.0,
        subtype='DISTANCE',
        unit='LENGTH',
        precision=3,
        step=0.1)

    shoulder_percentage = bpy.props.FloatProperty(
        name="Shoulder",
        description="Mortise shoulder (relative to width side)",
        min=0.0,
        max=1.0,
        subtype='PERCENTAGE')

    reverse_shoulder = bpy.props.BoolProperty(
        name="Reverse shoulder",
        description="Specify shoulder for the other side",
        default=False)

    haunched_first_side = bpy.props.BoolProperty(
        name="Haunched on first side",
        description="Add a little stub tenon at the top of the joint",
        default=False)

    haunch_first_side = bpy.props.PointerProperty(type=MortiseHaunch)

    haunched_second_side = bpy.props.BoolProperty(
        name="Haunched on second side",
        description="Add a little stub tenon at the bottom of the joint",
        default=False)

    haunch_second_side = bpy.props.PointerProperty(type=MortiseHaunch)


class MortiseHeightPropertyGroup(bpy.types.PropertyGroup):
    type = bpy.props.EnumProperty(
        items=[('max',
                "Max. height",
                "Set height to the maximum length"),
               ('value',
                "Value",
                "Give value to height"),
               ('percentage',
                "Percentage",
                "Set height by percentage")],
        name="Height type",
        default='value')

    value = bpy.props.FloatProperty(
        name="Height",
        description="Mortise height relative to length side",
        min=0.0,
        default=-1.0,
        subtype='DISTANCE',
        unit='LENGTH',
        precision=3,
        step=0.1)

    percentage = bpy.props.FloatProperty(
        name="Height",
        description="Mortise height relative to length side",
        min=0.0,
        max=1.0,
        subtype='PERCENTAGE')

    centered = bpy.props.BoolProperty(
        name="Centered",
        description="Specify if mortise is centered on length side",
        default=True)

    shoulder_type = bpy.props.EnumProperty(
        items=[('value',
                "Value",
                "Give value to shoulder height"),
               ('percentage',
                "Percentage",
                "Set shoulder height by percentage")],
        name="Height shoulder type",
        default='value')

    shoulder_value = bpy.props.FloatProperty(
        name="Shoulder",
        description="Mortise shoulder on length side",
        min=0.0,
        default=-1.0,
        subtype='DISTANCE',
        unit='LENGTH',
        precision=3,
        step=0.1)

    shoulder_percentage = bpy.props.FloatProperty(
        name="Shoulder",
        description="Mortise shoulder (relative to length side)",
        min=0.0,
        max=1.0,
        subtype='PERCENTAGE')

    reverse_shoulder = bpy.props.BoolProperty(
        name="Reverse shoulder",
        description="Specify shoulder for the other side",
        default=False)

    haunched_first_side = bpy.props.BoolProperty(
        name="Haunched on first side",
        description="Add a little stub tenon at the top of the joint",
        default=False)

    haunch_first_side = bpy.props.PointerProperty(type=MortiseHaunch)

    haunched_second_side = bpy.props.BoolProperty(
        name="Haunched on second side",
        description="Add a little stub tenon at the bottom of the joint",
        default=False)

    haunch_second_side = bpy.props.PointerProperty(type=MortiseHaunch)


class MortisePropertyGroup(bpy.types.PropertyGroup):
    thickness_properties = bpy.props.PointerProperty(
        type=MortiseThicknessPropertyGroup)
    height_properties = bpy.props.PointerProperty(
        type=MortiseHeightPropertyGroup)

    depth_value = bpy.props.FloatProperty(
        name="Depth",
        description="Mortise depth",
        min=0.0,
        default=-1.0,
        subtype='DISTANCE',
        unit='LENGTH',
        precision=3,
        step=0.1)


def register():
    bpy.utils.register_class(MortiseHaunch)
    bpy.utils.register_class(MortiseThicknessPropertyGroup)
    bpy.utils.register_class(MortiseHeightPropertyGroup)
    bpy.utils.register_class(MortisePropertyGroup)


def unregister():
    bpy.utils.unregister_class(MortisePropertyGroup)
    bpy.utils.unregister_class(MortiseHeightPropertyGroup)
    bpy.utils.unregister_class(MortiseThicknessPropertyGroup)
    bpy.utils.unregister_class(MortiseHaunch)


# ----------------------------------------------
# Code to run the script alone
#----------------------------------------------
if __name__ == "__main__":
    register()
