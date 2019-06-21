import bpy


def copy_properties(source, target):
    # properties = [p.identifier for p in source.bl_rna.properties if not p.is_readonly]
    properties = [p.identifier for p in source.bl_rna.properties if not source.is_property_readonly(p.identifier)]
    for p in properties:
        setattr(target, p, getattr(source, p))


def copy_modifiers(source, target, clear=True):
    # TODO: copy drivers / keyframes
    """
    Copy the modifiers from one object to another.
    :param source: Source object.
    :param target: Target object.
    :param clear: Clear the modifiers on the target object before copying.
    """
    # Clear modifiers.
    if clear:
        target.modifiers.clear()
    # Copy modifiers.
    for mod in source.modifiers:
        # Create modifier for new object.
        new_mod = target.modifiers.new(mod.name, mod.type)
        # Copy properties.
        copy_properties(mod, new_mod)


def copy_constraints(source, target, clear=True):
    # TODO: copy drivers / keyframes
    """
    Copy the constraints from one object to another.
    :param source: Source object.
    :param target: Target object.
    :param clear: Clear the constraints on the target object before copying.
    """
    # Clear constraints.
    if clear:
        target.constraints.clear()

    # Copy constraints.
    for con in source.constraints:
        # Create constraint for new object.
        new_con = target.constraints.new(con.type)
        new_con.name = con.name
        # Copy properties.
        copy_properties(con, new_con)


def copy_keyframes(source, target, overwrite=True, exclude=None, clear=False, fcurve_function=None, **kwargs):
    """
    Copy keyframes from one object to another.
    :param source: Source object.
    :param target: Target object.
    :param overwrite: Remove the old keyframes or add new keyframes.
    :param exclude: List of (data_path, array_index) tuples that are not copied.
    :param clear: Clear excluded properties.
    :param fcurve_function: If not None, this function is applied to each fcurve after it is copied.
    It should take as its first parameter an fcurve. Additional keyword arguments supplied to the copy function
    will be passed to this function.
    """
    if exclude is None:
        exclude = []

    # Create properties if they do not exist.
    if source.animation_data is None:
        source.animation_data_create()
    if target.animation_data is None:
        target.animation_data_create()
    if source.animation_data.action is None:
        source.animation_data.action = bpy.data.actions.new('Action')
    if target.animation_data.action is None:
        target.animation_data.action = bpy.data.actions.new('Action')

    # Get all fcurves that have to be copied.
    fcurves = [f for f in source.animation_data.action.fcurves if (f.data_path, f.array_index) not in exclude]

    for f in fcurves:
        # Get fcurve (possibly creating or overwriting it).
        if overwrite:
            old_f = target.animation_data.action.fcurves.find(f.data_path, f.array_index)
            if old_f is not None:
                target.animation_data.action.fcurves.remove(old_f)
            new_f = target.animation_data.action.fcurves.new(f.data_path, f.array_index)
        else:
            new_f = target.animation_data.action.fcurves.find(f.data_path, f.array_index)
            if new_f is None:
                new_f = target.animation_data.action.fcurves.new(f.data_path, f.array_index)

        # Copy fcurve properties.
        copy_properties(f, new_f)

        # Copy all keyframes.
        for kp in f.keyframe_points:
            new_kp = new_f.keyframe_points.insert(kp.co[0], kp.co[1])
            copy_properties(kp, new_kp)

        # Apply function to fcurve.
        if fcurve_function is not None:
            fcurve_function(new_f, **kwargs)

    # Clear excluded properties.
    if clear:
        fcurves = [f for f in source.animation_data.action.fcurves if (f.data_path, f.array_index) in exclude]
        for f in fcurves:
            target.animation_data.action.fcurves.remove(f)


def copy_fcurve_modifiers():
    pass


def copy_custom_properties(source, target):
    keys = source.keys()
    for key in keys:
        target[key] = source[key]