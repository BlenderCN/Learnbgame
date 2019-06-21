import bpy


# TODO(SK): Missing docstring
class MaterialProperty(bpy.types.PropertyGroup):
    material = bpy.props.StringProperty(name="Material")
    materialOption = bpy.props.EnumProperty(
        name="materialOption",
        items=(
            ('DEFAULT', 'Default', 'Creates a default material for you'),
            ('CUSTOM', 'Custom', 'You can choose a custom material for the neurons. Remember to turn on Object Color!')
        ),
        default='DEFAULT'
    )

    pathMaterial = bpy.props.StringProperty(name="Path material", description = "Material applied to paths. Leave blank for no material.")

    simulate_colors = bpy.props.BoolProperty(name = "Simulate Colors", description = "When checked, simulates color labels for the animation", default = True)


# TODO(SK): Missing docstring
def register():
    bpy.utils.register_class(MaterialProperty)
    bpy.types.Scene.pam_anim_material = bpy.props.PointerProperty(type=MaterialProperty)


# TODO(SK): Missing docstring
def unregister():
    del bpy.types.Scene.pam_anim_material
    bpy.utils.unregister_class(MaterialProperty)
