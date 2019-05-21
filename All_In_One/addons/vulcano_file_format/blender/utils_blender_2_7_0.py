def apply_modifiers(object, context, operator):
    return object.to_mesh(context.scene,
        operator.apply_modifiers, "PREVIEW")