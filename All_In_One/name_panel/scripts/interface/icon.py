
# object icon
def object(object):
    '''
        Returns a icon based on object type.
    '''

    # is object
    if object:

        # mesh
        if object.type == 'MESH':
            icon = 'OUTLINER_OB_MESH'

        # curve
        elif object.type == 'CURVE':
            icon = 'OUTLINER_OB_CURVE'

        # surface
        elif object.type == 'SURFACE':
            icon = 'OUTLINER_OB_SURFACE'

        # meta
        elif object.type == 'META':
            icon = 'OUTLINER_OB_META'

        # font
        elif object.type == 'FONT':
            icon = 'OUTLINER_OB_FONT'

        # armature
        elif object.type == 'ARMATURE':
            icon = 'OUTLINER_OB_ARMATURE'

        # lattice
        elif object.type == 'LATTICE':
            icon = 'OUTLINER_OB_LATTICE'

        # empty
        elif object.type == 'EMPTY':
            icon = 'OUTLINER_OB_EMPTY'

        # speaker
        elif object.type == 'SPEAKER':
            icon = 'OUTLINER_OB_SPEAKER'

        # camera
        elif object.type == 'CAMERA':
            icon = 'OUTLINER_OB_CAMERA'

        # lamp
        elif object.type == 'LAMP':
            icon = 'OUTLINER_OB_LAMP'

        # default
        else:
            icon = 'OUTLINER_OB_MESH'
        return icon

# modifier icon
def modifier(modifier):
    '''
        Returns a icon based on modifier type.
    '''

    # data transfer
    if modifier.type == 'DATA_TRANSFER':
        icon = 'MOD_DATA_TRANSFER'

    # mesh cache
    elif modifier.type == 'MESH_CACHE':
        icon = 'MOD_MESHDEFORM'

    # normal edit
    elif modifier.type == 'NORMAL_EDIT':
        icon = 'MOD_NORMALEDIT'

    # uvs project
    elif modifier.type == 'UV_PROJECT':
        icon = 'MOD_UVPROJECT'

    # uvs warp
    elif modifier.type == 'UV_WARP':
        icon = 'MOD_UVPROJECT'

    # vertex weight edit
    elif modifier.type == 'VERTEX_WEIGHT_EDIT':
        icon = 'MOD_VERTEX_WEIGHT'

    # vertex weight mix
    elif modifier.type == 'VERTEX_WEIGHT_MIX':
        icon = 'MOD_VERTEX_WEIGHT'

    # vertex weight proximity
    elif modifier.type == 'VERTEX_WEIGHT_PROXIMITY':
        icon = 'MOD_VERTEX_WEIGHT'

    # array
    elif modifier.type == 'ARRAY':
        icon = 'MOD_ARRAY'

    # bevel
    elif modifier.type == 'BEVEL':
        icon = 'MOD_BEVEL'

    # bolean
    elif modifier.type == 'BOOLEAN':
        icon = 'MOD_BOOLEAN'

    # boptionld
    elif modifier.type == 'BUILD':
        icon = 'MOD_BUILD'

    # decimate
    elif modifier.type == 'DECIMATE':
        icon = 'MOD_DECIM'

    # edge split
    elif modifier.type == 'EDGE_SPLIT':
        icon = 'MOD_EDGESPLIT'

    # mask
    elif modifier.type == 'MASK':
        icon = 'MOD_MASK'

    # mirror
    elif modifier.type == 'MIRROR':
        icon = 'MOD_MIRROR'

    # multires
    elif modifier.type == 'MULTIRES':
        icon = 'MOD_MULTIRES'

    # remesh
    elif modifier.type == 'REMESH':
        icon = 'MOD_REMESH'

    # screw
    elif modifier.type == 'SCREW':
        icon = 'MOD_SCREW'

    # skin
    elif modifier.type == 'SKIN':
        icon = 'MOD_SKIN'

    # solidify
    elif modifier.type == 'SOLIDIFY':
        icon = 'MOD_SOLIDIFY'

    # subsurf
    elif modifier.type == 'SUBSURF':
        icon = 'MOD_SUBSURF'

    # triangulate
    elif modifier.type == 'TRIANGULATE':
        icon = 'MOD_TRIANGULATE'

    # wireframe
    elif modifier.type == 'WIREFRAME':
        icon = 'MOD_WIREFRAME'

    # armature
    elif modifier.type == 'ARMATURE':
        icon = 'MOD_ARMATURE'

    # cast
    elif modifier.type == 'CAST':
        icon = 'MOD_CAST'

    # corrective smooth
    elif modifier.type == 'CORRECTIVE_SMOOTH':
        icon = 'MOD_SMOOTH'

    # curve
    elif modifier.type == 'CURVE':
        icon = 'MOD_CURVE'

    # displace
    elif modifier.type == 'DISPLACE':
        icon = 'MOD_DISPLACE'

    # hook
    elif modifier.type == 'HOOK':
        icon = 'HOOK'

    # laplacian smooth
    elif modifier.type == 'LAPLACIANSMOOTH':
        icon = 'MOD_SMOOTH'

    # laplacian deform
    elif modifier.type == 'LAPLACIANDEFORM':
        icon = 'MOD_MESHDEFORM'

    # lattice
    elif modifier.type == 'LATTICE':
        icon = 'MOD_LATTICE'

    # mesh deform
    elif modifier.type == 'MESH_DEFORM':
        icon = 'MOD_MESHDEFORM'

    # shrinkwrap
    elif modifier.type == 'SHRINKWRAP':
        icon = 'MOD_SHRINKWRAP'

    # simple deform
    elif modifier.type == 'SIMPLE_DEFORM':
        icon = 'MOD_SIMPLEDEFORM'

    # smooth
    elif modifier.type == 'SMOOTH':
        icon = 'MOD_SMOOTH'

    # warp
    elif modifier.type == 'WARP':
        icon = 'MOD_WARP'

    # wave
    elif modifier.type == 'WAVE':
        icon = 'MOD_WAVE'

    # cloth
    elif modifier.type == 'CLOTH':
        icon = 'MOD_CLOTH'

    # collision
    elif modifier.type == 'COLLISION':
        icon = 'MOD_PHYSICS'

    # dynamic paint
    elif modifier.type == 'DYNAMIC_PAINT':
        icon = 'MOD_DYNAMICPAINT'

    # explode
    elif modifier.type == 'EXPLODE':
        icon = 'MOD_EXPLODE'

    # floptiond simulation
    elif modifier.type == 'FLUID_SIMULATION':
        icon = 'MOD_FLUIDSIM'

    # ocean
    elif modifier.type == 'OCEAN':
        icon = 'MOD_OCEAN'

    # particle instance
    elif modifier.type == 'PARTICLE_INSTANCE':
        icon = 'MOD_PARTICLES'

    # particle system
    elif modifier.type == 'PARTICLE_SYSTEM':
        icon = 'MOD_PARTICLES'

    # smoke
    elif modifier.type == 'SMOKE':
        icon = 'MOD_SMOKE'

    # soft body
    elif modifier.type == 'SOFT_BODY':
        icon = 'MOD_SOFT'

    # default
    else:
        icon = 'MODIFIER'
    return icon

# object data icon
def objectData(object):
    '''
        Returns a icon based on object type.
    '''

    # is object
    if object:

        # mesh
        if object.type == 'MESH':
            icon = 'MESH_DATA'

        # curve
        elif object.type == 'CURVE':
            icon = 'CURVE_DATA'

        # surface
        elif object.type == 'SURFACE':
            icon = 'SURFACE_DATA'

        # meta
        elif object.type == 'META':
            icon = 'META_DATA'

        # font
        elif object.type == 'FONT':
            icon = 'FONT_DATA'

        # armature
        elif object.type == 'ARMATURE':
            icon = 'ARMATURE_DATA'

        # lattice
        elif object.type == 'LATTICE':
            icon = 'LATTICE_DATA'

        # speaker
        elif object.type == 'SPEAKER':
            icon = 'SPEAKER'

        # camera
        elif object.type == 'CAMERA':
            icon = 'CAMERA_DATA'

        # lamp
        elif object.type == 'LAMP':
            icon = 'LAMP_DATA'

        # default
        else:
            icon = 'MESH_DATA'
        return icon
