import bpy

def add_properties():
    bpy.types.Object.ArmIk_L = bpy.props.FloatProperty(name='ArmIk_L', default=0.0, min=0.0, 
        max=1.0)
    bpy.types.Object.ArmIk_R = bpy.props.FloatProperty(name='ArmIk_R', default=0.0, min=0.0, 
        max=1.0)
    bpy.types.Object.LegIk_L = bpy.props.FloatProperty(name='LegIk_L', default=0.0, min=0.0, 
        max=1.0)
    bpy.types.Object.LegIk_R = bpy.props.FloatProperty(name='LegIk_R', default=0.0, min=0.0, 
        max=1.0)
    bpy.types.Object.ArmRotationIk_L = bpy.props.FloatProperty(name='ArmRotationIk_L', default=0.0,
        min=0.0, max=1.0)
    bpy.types.Object.ArmRotationIk_R = bpy.props.FloatProperty(name='ArmRotationIk_R', default=0.0,
        min=0.0, max=1.0)
    bpy.types.Object.HeadRotationIk = bpy.props.FloatProperty(name='HeadRotationIk', default=0.0,
        min=0.0, max=1.0)
    