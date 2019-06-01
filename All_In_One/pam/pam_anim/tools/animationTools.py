import bpy
from ... import model

# TODO(SK): Missing docstring
class AnimationProperty(bpy.types.PropertyGroup):
    startFrame = bpy.props.IntProperty(name="Start frame", default=0)
    endFrame = bpy.props.IntProperty(name="End frame", default=100)

    startTime = bpy.props.FloatProperty(name="Start time", default=0.0)
    endTime = bpy.props.FloatProperty(name="End time", default=100.0)

    connNumber = bpy.props.IntProperty(name="Max Connection", default=0)

    showPercent = bpy.props.FloatProperty(name="Show percentage", default = 100.0, min = 0.0, max = 100.0, description = "Only generate x% of neurons", subtype = 'PERCENTAGE', precision = 1)

# TODO(SK): Missing docstring
def register():
    bpy.utils.register_class(AnimationProperty)
    bpy.types.Scene.pam_anim_animation = bpy.props.PointerProperty(type=AnimationProperty)


# TODO(SK): Missing docstring
def unregister():
    del bpy.types.Scene.pam_anim_animation
    bpy.utils.unregister_class(AnimationProperty)
