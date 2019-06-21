

def setup_surface_snapping(scene):
    settings = scene.tool_settings

    settings.snap_elements = {'FACE'}
    settings.snap_target = 'MEDIAN'
    settings.use_snap_align_rotation = True
    # TODO: the following seems to misbehave on objects that are parented, possibly a Blender bug
    # settings.use_snap_project = True
