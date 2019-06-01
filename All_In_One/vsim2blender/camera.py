import bpy
import math
from mathutils import Vector
from json import loads
from vsim2blender import read_config, Opts


def setup_camera(lattice_vectors, field_of_view=0.5,
                 scene=bpy.context.scene, opts=Opts({})):
    """
    Set up a camera looking along the y axis

    :param lattice_vectors: Lattice vectors of unit cell
    :type lattice_vectors: 3-tuple of 3-Vectors
    :param field_of_view: Camera field of view in radians
    :type field_of_view: float
    :param scene: Scene in which to insert camera object
    :type scene: bpy Scene
    :param opts: Initialised Opts object. The following parameters,
        either specified in the dict when Opts is initialised or under
        [general] in the specified config file, are used:

        camera_rot
            *(float cast to string)*
            Camera tilt adjustment in degrees
        miller
            *(3-list of floats cast to str)*
            Miller indices of target view. Floating-point values may
            be used for fine adjustments if desired.
        orthographic
            *(bool)*
            If True, use orthographic projection (no perspective)
        supercell
            *(3-list of ints cast to str)*
            Supercell dimensions
        zoom
            *(float)* Camera zoom adjustment
    :type opts: vsim2blender.Opts

    """

    camera_rot = opts.get('camera_rot', 0)
    miller = opts.get('miller', (0, 1, 0))
    supercell = opts.get('supercell', (2, 2, 2))
    zoom = opts.get('zoom', 1.)
    orthographic = opts.get('orthographic', False)

    a, b, c = [n * x for n, x in zip(supercell, lattice_vectors)]
    supercell_centre = 0.5 * sum([a, b, c], Vector((0., 0., 0.)))
    vertices = list([Vector((0, 0, 0)), a, a+b,
                     b, c, c+a, c+a+b, c+b])

    # Create an empty at the centre of the model for
    # the camera to target
    bpy.ops.object.add(type='EMPTY', location=supercell_centre)
    empty_center = bpy.context.object

    # Use Miller index to create a vector to the camera
    # with arbitrary magnitude. Distances perpendicular to this vector
    # determine required camera distance

    camera_direction_vector = sum([i * x for i, x in
                                   zip(miller,
                                       reciprocal(lattice_vectors))],
                                  Vector((0, 0, 0)))

    vertices_from_center = [v - supercell_centre for v in vertices]

    camera_distance = max([dist_to_view_point(
        vertex, camera_direction_vector, field_of_view
        ) for vertex in vertices_from_center])

    # Re-scale position vector
    camera_direction_vector.length = camera_distance
    camera_position = supercell_centre + camera_direction_vector

    bpy.ops.object.camera_add(location=camera_position)
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    if orthographic:
        bpy.data.cameras[camera.name].type = 'ORTHO'
        bpy.data.cameras[camera.name].ortho_scale = camera_distance/2.5
        # Limit clipping to avoid nasty glitches in orthographic mode
        bpy.data.cameras[camera.name].clip_end = 10000
    else:
        bpy.data.cameras[camera.name].angle = field_of_view
        bpy.data.cameras[camera.name].clip_end = 1e8

    # Use tracking to point camera at center of structure
    bpy.ops.object.constraint_add(type='TRACK_TO')
    camera.constraints['Track To'].target = empty_center
    camera.constraints['Track To'].track_axis = 'TRACK_NEGATIVE_Z'
    camera.constraints['Track To'].up_axis = 'UP_Y'

    # Rotate camera by mapping to empty and rotating empty
    camera.constraints['Track To'].use_target_z = True
    empty_center.select = True
    bpy.ops.transform.rotate(value=(camera_rot * 2 * math.pi/360),
                             axis = camera_direction_vector)

    # Tweak zoom level
    bpy.data.cameras[camera.name].lens = zoom * 75


def dist_to_view_point(point, camera_direction_vector, field_of_view):
    """
    Calculate the required camera distance along a vector to keep a
    point in view.

    :param point: Target vertex
    :type point: 3-Vector
    :param camera_direction_vector: Vector of arbitrary length pointing
                                    towards to camera
    :type camera_direction_vector: 3-Vector
    :param field_of_view: The camera field of view in radians
    :type field_of_view: Float

    """
    projection = point.project(camera_direction_vector)
    rejection = point - projection
    cone_width = rejection.length
    distance = cone_width / math.sin(field_of_view)
    return distance


def reciprocal(lattice_vectors):
    """
    Get reciprocal lattice vectors

    Follows the equations outlined by Ashcroft & Mermin
    (Solid State Physics Ch 5, 1976)

    b1 = 2 pi (a2 x a3)/(a1 . (a2 x a3))
    b2 = 2 pi (a3 x a1)/(a1 . (a2 x a3))
    b3 = 2 pi (a1 x a2)/(a1 . (a2 x a3))

    :param lattice_vectors: Real-space lattice vectors
    :type lattice_vectors: 3-tuple of 3-Vectors
    :returns: Reciprocal lattice vectors
    :rtype: 3-tuple of 3-vectors

    """
    a1, a2, a3 = lattice_vectors

    denominator = a1.dot(a2.cross(a3)) / (2. * math.pi)
    b1, b2, b3 = [x1.cross(x2)/denominator for x1, x2 in ((a2, a3),
                                                          (a3, a1),
                                                          (a1, a2))]
    return (b1, b2, b3)
