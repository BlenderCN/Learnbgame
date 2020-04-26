import bpy
import os
import random
# import sys
from mathutils import Vector, Matrix
import math
import cmath
import itertools
import vsim2blender

# sys.path.insert(0, os.path.abspath(script_directory)+'/..')
from vsim2blender.ascii_importer import (import_vsim,
                                         cell_vsim_to_vectors)
from vsim2blender.arrows import add_arrow, vector_to_euler
import vsim2blender.camera as camera

script_directory = os.path.dirname(__file__)


def draw_bounding_box(cell, offset=(0, 0, 0)):
    """
    Draw unit cell bounding box

    :param cell: Lattice vectors
    :type cell: 3-tuple of 3-Vectors
    :param offset: Location offset from origin
    :type offset: 3-tuple in lattice coordinates
    """
    a, b, c = cell
    verts = list(map(tuple, [(0, 0, 0), a, a+b, b, c, c+a, c+a+b, c+b]))
    faces = [(0, 1, 2, 3), (0, 1, 5, 4), (1, 2, 6, 5),
             (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)]
    box_mesh = bpy.data.meshes.new("Bounding Box")
    box_object = bpy.data.objects.new("Bounding Box", box_mesh)

    offset = Vector(offset)
    cart_offset = offset * Matrix(cell)
    box_object.location = (cart_offset)
    bpy.context.scene.objects.link(box_object)
    box_mesh.from_pydata(verts, [], faces)
    box_mesh.update(calc_edges=True)

    box_material = bpy.data.materials.new("Bounding Box")
    box_object.data.materials.append(box_material)
    box_material.type = "WIRE"
    box_material.diffuse_color = (0, 0, 0)
    box_material.use_shadeless = True


def init_material(symbol, col=False, shadeless=True):
    """
    Create material if non-existent, with random colour if unspecified.

    :param col: RGB color. If False, use a random colour.
    :type col: 3-tuple, list or Boolean False
    :param shadeless: Enable set_shadeless material parameter.
        Informally known as "lights out".
    :type shadeless: Boolean

    :returns: bpy material object
    """

    if symbol in bpy.data.materials.keys():
        return bpy.data.materials[symbol]
    elif not col:
        col = (random.random(), random.random(), random.random())

    material = bpy.data.materials.new(name=symbol)
    material.diffuse_color = col
    material.use_shadeless = shadeless
    return material


def absolute_position(position, lattice_vectors=[1., 1., 1.],
                      cell_id=[0, 0, 0], reduced=False):
    """
    Calculate the absolute position of an atom in a supercell array

    :param position: atom coordinates. Units same as unit cell unless
        reduced=True
    :type position: 3-tuple, list or vector
    :param lattice_vectors: lattice bounding box/repeating unit
    :type lattice_vectors: 3-tuple or list containing 3-Vectors
    :param cell_id: position index of cell in supercell. (0,0,0) is the
            origin cell. Negative values are ok.
    :type cell_id: 3-tuple of integers
    :param reduced: If true, positions are taken to be in units of
        lattice vectors; if false, positions are taken to be Cartesian.
    :type reduced: Boolean

    :returns: cartesian_position
    :rtype: 3-Vector
    """

    if reduced:
        cartesian_position = Vector((0., 0., 0.))
        for i, (position_i, vector) in enumerate(zip(position,
                                                 lattice_vectors)):
            cartesian_position += (position_i + cell_id[i]) * vector
    else:
        cartesian_position = Vector(position)
        for i, vector in enumerate(lattice_vectors):
            cartesian_position += (cell_id[i] * vector)

    return cartesian_position


def add_atom(position, lattice_vectors, symbol, cell_id=(0, 0, 0),
             scale_factor=1., reduced=False, name=False, config=False):
    """
    Add atom to scene

    :param position: Atom coordinates. Units same as unit cell
        unless reduced=True
    :type position: 3-tuple, list or Vector
    :param lattice_vectors: Vectors specifying lattice
        bounding box/repeating unit
    :type  lattice_vectors: 3-tuple or list
    :param symbol: Chemical symbol used for colour and size lookup.
    :type symbol: String
    :param cell_id: position index of cell in supercell. (0,0,0) is the
        origin cell. Negative values are ok.
    :type cell_id: 3-tuple of ints
    :param scale_factor: master scale factor for atomic spheres
    :type scale_factor: float
    :param reduced: If true, positions are taken to be in units of
        lattice vectors; if false, positions are taken to be Cartesian.
    :type reduced: Boolean
    :param name: Label for atom object
    :type name: String
    :param config: Settings from configuration files
        (incl. atom colours and radii)
    :type config: configparser.ConfigParser

    :returns: bpy object
    """

    if not config:
        config = vsim2blender.read_config()

    cartesian_loc = absolute_position(position,
                                      lattice_vectors=lattice_vectors,
                                      cell_id=cell_id, reduced=reduced)

    # Get colour and atomic radius. Priority order is
    # 1. User conf file 2. elements.conf
    if symbol in config['colours']:
        col = [float(x) for x in config['colours'][symbol].split()]
    else:
        col = False
    if symbol in config['radii']:
        radius = float(config['radii'][symbol])
    else:
        radius = 1.0

    size = radius * scale_factor
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,
                                          location=cartesian_loc,
                                          size=size)
    atom = bpy.context.object
    if name:
        atom.name = name

    material = init_material(symbol, col=col)
    atom.data.materials.append(material)
    # Smooth shader goes here; does nothing for flat colours however
    # bpy.ops.object.shade_smooth()

    return atom

# Computing the positions
#
# Key equation is:
# _u_(jl,t) =
#    Sum over k, nu: _U_(j,k,nu) exp(i[k _r_(jl) - w(k,nu)t])
# [M. T. Dove, Introduction to Lattice Dynamics (1993) Eqn 6.18]
#
# Where nu is the mode identity, w is frequency, _U_ is the
# displacement vector, and _u_ is the displacement of atom j in unit
# cell l. We can break this down to a per-mode displacement and so the
# up-to-date position of atom j in cell l in a given mode visualisation
#
# _r'_(jl,t,nu) = _r_(jl) + _U_(j,k,nu) exp(i[k _r_(jl) - w(k,nu)t])
#
# Our unit of time should be such that a full cycle elapses over the
# desired number of frames.
#
# A full cycle usually lasts 2*pi/w, so let t = frame*2*pi/wN;
# -w t becomes -w 2 pi frame/wN = 2 pi frame / N
#
# _r'_(jl,t,nu) = _r_(jl) + _U_(j,k,nu) exp(i[k _r_(jl) - 2 pi frame/N])
#
# The arrows for static images are defined as the vectors from the
# initial (average) positions to one quarter of the vibrational period
# (i.e. max displacement)


def animate_atom_vibs(atom, qpt, d_vector,
                      n_frames=30, start_frame=0, end_frame=None,
                      magnitude=1., mass=1):
    """
    Apply vibrations as series of LOC keyframes

    :param atom: Target atom
    :type atom: bpy Object
    :param qpt: wave vector of mode in *Cartesian coordinates*
    :type qpt: 3-Vector
    :param d_vector: complex vector describing relative
        displacement of atom
    :type d_vector: 3-tuple of Complex numbers
    :param n_frames: total number of animation frames. Animation will
        run from frame 0 to n_frames-1.
    :type n_frames: int
    :param magnitude: Scale factor for vibrations.
    :type magnitude: float
    :param mass: Relative atomic mass (inverse sqrt is used to scale
        vibration magnitude.)
    :type mass: float
    """

    r = atom.location.copy()

    if type(end_frame) != int:
        end_frame = start_frame + n_frames - 1
    for frame in range(start_frame, end_frame+1):
        bpy.context.scene.frame_set(frame)
        exponent = cmath.exp(complex(0, 1) * (r.dot(qpt) -
                             2 * math.pi*frame/n_frames))
        norm_displ = Vector(map((lambda y: (y.real)),
                            [x * exponent for x in d_vector]))
        atom.location = r + mass**-.5 * magnitude * norm_displ
        atom.keyframe_insert(data_path="location", index=-1)


def vector_with_phase(atom, qpt, d_vector):
    """
    Calculate Cartesian vector associated with atom vibrations

    :param atom: Target atom
    :type atom: bpy Object
    :param qpt: wave vector of mode in *Cartesian coordinates*
    :type qpt: 3-Vector
    :param d_vector: complex vector describing relative displacement of atom
    :type d_vector: 3-tuple of Complex numbers
    :param n_frames: total number of animation frames. Animation
        will run from frame 0 to n_frames-1.
    :type n_frames: positive int
    :param magnitude: Scale factor for vibrations.
    :type magnitude: float
    """
    r = atom.location
    exponent = cmath.exp(complex(0, 1) * r.dot(qpt))
    arrow_end = r + Vector(map((lambda y: (y.real)),
                               [x * exponent for x in d_vector]))
    return arrow_end - r


def open_mode(**options):
    """
    Open v_sim ascii file in Blender

    :param input_file: Path to file
    :type input_file: str
    :param camera_rot: Camera tilt adjustment in degrees
    :type camera_rot: float
    :param config: Settings from configuration files
    :type config: configparser.ConfigParser
    :param mass_weighting: Weight eigenvectors by mass.
        This has usually already been done when generating the .ascii file,
        in which case the default value of 0 is acceptable.
        A value of 1 corresponds to the formally correct mass scaling of m^-0.5
        for non-weighted eigenvectors.
        A value of -1 will REMOVE existing mass-weighting.
        In-between values may be useful for re-scaling to see the range of
        movements in a system, but are not physically meaningful.
    :type mass_weighting: float
    :param end_frame: The ending frame number of the rendered Animation
        (default=start_frame+n_frames-1)
    :type end_frame: int or None
    :param miller: Miller indices of view
    :type miller: 3-tuple of floats
    :param mode_index: id of mode; 0 corresponds to first mode in ascii file
    :type mode_index: int
    :param n_frames: Animation length of a single oscillation
        cycle in frames (default=30)
    :type n_frames: Positive int
    :param normalise_vectors: Re-scale vectors so largest arrow is fixed length
    :type normalise_vectors: bool
    :param offset_box: Position of bbox in lattice vector coordinates.
        Default (0,0,0) (Left front bottom)
    :type offset_box: Vector or 3-tuple
    :param preview: Enable preview mode - single frame, smaller render
    :type preview: bool
    :param scale_arrow: Scale factor for arrows
    :type scale_arrow: float
    :param scale_atom: Scale of atoms, relative to covalent radius
    :type scale_atom: float
    :param scale_vib: Scale factor for oscillations
        (angstroms / normalised eigenvector).
    :type scale_vib: float
    :param show_box: If True, show bounding box
    :type show_box: bool
    :param start_frame: The starting frame number of the rendered
        animation (default=0)
    :type start_frame: int or None
    :param static: if True, ignore frame range and use single frame.
        Otherwise, add animation keyframes.
    :type static: bool
    :param supercell: supercell dimensions
    :type supercell: 3-tuple or 3-list of ints
    :param vectors: If True, show arrows
    :type vectors: bool
    :param zoom: Camera zoom adjustment
    :type zoom: float

    """

    # Initialise Opts object, accessing options and user config
    opts = vsim2blender.Opts(options)

    # Work out actual frame range.
    # Priority goes 1. static/preview 2. end_frame 3. n_frames
    start_frame = opts.get('start_frame', 0)
    n_frames = opts.get('n_frames', 30)

    # Preview images default to static, others default to animated
    preview = opts.get('preview', False)
    if preview:
        static = opts.get('static', True)
    else:
        static = opts.get('static', False)

    if static:
        end_frame = start_frame
    else:
        end_frame = opts.get('end_frame', start_frame + n_frames - 1)

    input_file = opts.get('input_file', False)
    if input_file:
        (vsim_cell, positions, symbols, vibs) = import_vsim(input_file)
        lattice_vectors = cell_vsim_to_vectors(vsim_cell)
    else:
        raise Exception('No .ascii file provided')

    if opts.get('mass_weighting', 0):
        f = opts.get('mass_weighting', 1)
        masses = [float(opts.config['masses'][symbol])**f
                      for symbol in symbols]
    else:
        masses = [1 for symbol in symbols]

    # Switch to a new empty scene
    bpy.ops.scene.new(type='EMPTY')

    # Draw bounding box
    if (opts.get('show_box', True)):
        bbox_offset = opts.get('offset_box', (0, 0, 0))
        bbox_offset = Vector(bbox_offset)
        draw_bounding_box(lattice_vectors, offset=bbox_offset)

    # Draw atoms after checking config
    mode_index = opts.get('mode_index', 0)
    supercell = (opts.get('supercell', (2, 2, 2)))
    vectors = opts.get('vectors', False)

    normalise_vectors = opts.get('normalise_vectors', False)
    # Variable for tracking largest arrow
    max_vector = 0
    arrow_objects = []

    mass_weighting = opts.get('mass_weighting', 0.)
    assert type(mass_weighting) == float

    for cell_id_tuple in itertools.product(range(supercell[0]),
                                           range(supercell[1]),
                                           range(supercell[2])):
        cell_id = Vector(cell_id_tuple)
        for (atom_index,
             (position, symbol, mass)) in enumerate(zip(positions,
                                                        symbols,
                                                        masses)):
            atom = add_atom(position, lattice_vectors, symbol,
                            cell_id=cell_id,
                            scale_factor=opts.get('scale_atom', 1.),
                            name='{0}_{1}_{2}{3}{4}'.format(
                                atom_index, symbol, *cell_id_tuple),
                            config=opts.config)
            if vectors or not static:
                displacement_vector = vibs[mode_index].vectors[atom_index]
                qpt = vibs[mode_index].qpt
                B = (2 * math.pi *
                     Matrix(lattice_vectors).inverted().transposed())
                qpt_cartesian = Vector(qpt) * B

            if not static:
                animate_atom_vibs(atom, qpt_cartesian,
                                  displacement_vector,
                                  start_frame=start_frame,
                                  end_frame=end_frame,
                                  n_frames=n_frames,
                                  magnitude=opts.get('scale_vib', 1.),
                                  mass=mass)
            if vectors:
                arrow_vector = vector_with_phase(atom, qpt_cartesian,
                                                 displacement_vector)
                scale = arrow_vector.length
                loc = absolute_position(position,
                                        lattice_vectors=lattice_vectors,
                                        cell_id=cell_id)
                # Arrows are scaled by eigenvector magnitude
                arrow_objects.append(
                    add_arrow(loc=loc,
                              mass=mass,
                              rot_euler=vector_to_euler(arrow_vector),
                              scale=scale))

    if vectors:
        col = str2list(opts.config.get('colours', 'arrow',
                       fallback='0. 0. 0.'))
        bpy.data.materials['Arrow'].diffuse_color = col

    # Rescaling; either by clamping max or accounting for cell size
    if vectors and normalise_vectors:
        master_scale = opts.get('scale_arrow', 1.)
        # Compare first element of object scales; they should be isotropic!
        max_length = max((arrow.scale[0] for arrow in arrow_objects))
        for arrow in arrow_objects:
            arrow.scale *= master_scale / max_length

    elif vectors:
        master_scale = opts.get('scale_arrow', 1.) * len(positions)
        for arrow in arrow_objects:
            arrow.scale *= master_scale

    # Position camera and colour world. Note that cameras as objects and
    # cameras as 'cameras' have different attributes, so need to look up
    # camera in bpy.data.cameras to set field of view.

    camera.setup_camera(lattice_vectors, field_of_view=0.2, opts=opts)

    bpy.context.scene.world = bpy.data.worlds['World']
    bpy.data.worlds['World'].horizon_color = str2list(opts.config.get(
        'colours', 'background', fallback='0.5 0.5 0.5'))


def setup_render(start_frame=0, end_frame=None, n_frames=30, preview=False):
    """
    Setup the render (old style)

    :param n_frames: Animation length of a single oscillation
        cycle in frames
    :type n_frames: Positive int
    :param start_frame: The starting frame number of the
        rendered animation (default=0)
    :type start_frame: int or None
    :param end_frame: The ending frame number of the rendered
        animation (default=start_frame+n_frames-1)
    :type end_frame: int or None
    :param preview: Write to a temporary preview file at low resolution
        instead of the output. Use first frame only.
    :type preview: str or Boolean False

    """
    if type(start_frame) != int:
        start_frame = 0
    if preview:
        end_frame = start_frame
    elif type(end_frame) != int:
        end_frame = start_frame + n_frames - 1
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1080
    if preview:
        bpy.context.scene.render.resolution_percentage = 20
    else:
        bpy.context.scene.render.resolution_percentage = 50
    bpy.context.scene.render.use_edge_enhance = True
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame


def setup_render_freestyle(**options):
    """
    Setup the render setting

    :param n_frames: Animation length of a single oscillation cycle in
        frames
    :type n_frames: Positive int
    :param start_frame: The starting frame number of the rendered
        animation (default=0)
    :type start_frame: int or None
    :param end_frame: The ending frame number of the rendered Animation
        (default=start_frame+n_frames-1)
    :type end_frame: int or None
    :param preview: Write to a temporary preview file at low resolution
        instead of the output. Use first frame only. If no preview, set to
        empty string ''
    :type preview: str
    :param config: Path to user configuration settings -- this function makes
        use of 'x_pixels', 'y_pixels', 'box_thickness' and 'outline_thickness'
        keys in [general] section and 'outline' and 'box' keys in [colours]
        section
    :type config: str

    """

    opts = vsim2blender.Opts(options)
    start_frame = opts.get('start_frame', 0)
    n_frames = opts.get('n_frames', 30)

    if opts.get('static', False):
        end_frame = start_frame
    else:
        end_frame = opts.get('end_frame', start_frame + n_frames - 1)

    x_pixels = opts.get('x_pixels', 512)
    y_pixels = opts.get('y_pixels', 512)

    bpy.context.scene.render.resolution_x = x_pixels
    bpy.context.scene.render.resolution_y = y_pixels
    if opts.get('preview', False):
        bpy.context.scene.render.resolution_percentage = 40
    else:
        bpy.context.scene.render.resolution_percentage = 100

    # These flat renders don't use much memory, so render a single big
    # tiles for high speed
    bpy.context.scene.render.tile_x = x_pixels
    bpy.context.scene.render.tile_y = y_pixels

    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame

    bpy.context.scene.render.use_freestyle = True

    renderlayer = bpy.context.scene.render.layers['RenderLayer']

    if opts.get('show_box', True):
        # Wireframe box and add to "Group" for exclusion from outlining
        # Freestyle doesn't work with wireframes
        bpy.data.materials['Bounding Box'].type = 'SURFACE'
        bpy.data.objects['Bounding Box'].select = True

        bpy.ops.object.modifier_add(type='SUBSURF')
        mesh_to_wireframe(bpy.data.objects['Bounding Box'])
        mark_edges(bpy.data.objects['Bounding Box'])
        # bpy.ops.object.group_add()

        # Bounding box line settings
        bpy.ops.scene.freestyle_lineset_add()
        boxlines = renderlayer.freestyle_settings.linesets.active
        boxlinestyle = boxlines.linestyle
        boxlinestyle.thickness = opts.get('box_thickness', 5)
        boxlinestyle.color = str2list(opts.config.get('colours',
                                                      'box',
                                                      fallback='1. 1. 1.'))
        # Bounding box tracer ignores everything but Freestyle marked edges
        boxlines.select_silhouette = False
        boxlines.select_border = False
        boxlines.select_crease = False
        boxlines.select_edge_mark = True

    # Outline settings
    bpy.ops.scene.freestyle_lineset_add()
    atomlines = renderlayer.freestyle_settings.linesets.active
    atomlinestyle = atomlines.linestyle
    atomlinestyle.thickness = opts.get('outline_thickness', 3)
    atomlinestyle.color = str2list(opts.config.get('colours',
                                                   'outline',
                                                   fallback='0. 0. 0.'))


def str2list(string):
    return [float(x) for x in string.split()]


def mesh_to_wireframe(bpy_object):
    """
    Create and apply a wireframe modifier to a mesh object

    :param bpy_object: Simple mesh object to convert to a wireframe
    :type bpy_object: Blender object

    :returns wire_object: Original object with applied wireframe
    :rtype wire_object: Blender object
    """
    bpy.context.scene.objects.active = bpy_object
    bpy_object.select = True
    bpy.ops.object.modifier_add(type='WIREFRAME')
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Wireframe")
    return bpy_object


def mark_edges(bpy_object):
    """
    Mark all the edges of an object's mesh for Freestyle

    :param bpy_object: Object to mark. Must have a mesh.
    :type bpy_object: Blender object

    :returns marked_object: Original object with Freestyle marks
    :rtype marked_object: Blender object
    """
    bpy.context.scene.objects.active = bpy_object
    bpy_object.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.mark_freestyle_edge()
    bpy.ops.object.mode_set(mode='OBJECT')
    return bpy_object


def render(scene=False, output_file=False, preview=False):
    """
    Render the scene

    :param scene: Name of scene. If False, render active scene.
    :type scene: String or Boolean False
    :param output_file: Blender-formatted output path/filename.
        If False, do not render. This is a useful fall-through as
        calls to render() can be harmlessly included in boilerplate.
    :type output_file: String or Boolean False
    :param preview: Write to a temporary preview file at low resolution
        instead of the output. Set to empty string '' if not a preview.
    :type preview: str

    """
    if preview:
        output_file = preview

    if (not output_file) or output_file == 'False' or output_file == '':
        pass

    else:
        if not scene:
            scene = bpy.context.scene.name

        # Set output path (No sanitising or absolutising at this stage)
        bpy.data.scenes[scene].render.filepath = output_file

        # Work out if animation or still is required

        animate = (bpy.data.scenes[scene].frame_start !=
                   bpy.data.scenes[scene].frame_end)

        # Render!
        bpy.ops.render.render(animation=animate,
                              write_still=(not animate), scene=scene)
