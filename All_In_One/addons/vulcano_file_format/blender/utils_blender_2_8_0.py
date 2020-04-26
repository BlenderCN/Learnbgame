def apply_modifiers(object, context, operator):
    return object.to_mesh(context.depsgraph,
        operator.apply_modifiers)
