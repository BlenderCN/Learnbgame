# TODO(SK): module Missing docstring

import logging

import bpy
import numpy
import mathutils

from . import pam
from . import model
from . import colormaps
from . import constants
from . import mesh
from . import connection_mapping

logger = logging.getLogger(__package__)

vis_objects = 0


def setCursor(loc):
    """Just a more convenient way to set the location of the cursor"""

    bpy.data.screens['Default'].scene.cursor_location = loc


def getCursor():
    """Just return the cursor location. A bit shorter to type ;)"""

    return bpy.data.screens['Default'].scene.cursor_location


def visualizePostNeurons(no_connection, pre_neuron):
    """Visualize the post-synaptic neurons that are connected with a given
    neuron from the presynaptic layer

    :param int no_connection: connection index
    :param int pre_neuron: index of pre-synaptic neuron

    """

    global vis_objects

    layer = pam.pam_connections[no_connection][0][-1]  # get last layer of connection
    neuronset = pam.pam_connections[no_connection][2]  # neuronset 2
    connectivity = pam.pam_connection_results[no_connection]['c'][pre_neuron]

    for i in connectivity:
        if (i >= 0):
            bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False, location=layer.particle_systems[neuronset].particles[i].location, layers=(True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))
            bpy.context.selected_objects[0].name = "visualization.%03d" % vis_objects
            vis_objects = vis_objects + 1


def generateLayerNeurons(layer, particle_system, obj, object_color=[],
                         indices=-1):
    """Generate for each particle (neuron) a cone with appropriate naming"""
    # generate first mesh
    i = 0
    p = layer.particle_systems[particle_system].particles[0]

    if indices == -1:
        particles = layer.particle_systems[particle_system].particles
    else:
        particles = layer.particle_systems[particle_system].particles[indices[0]:indices[1]]

    # generates linked duplicates of this mesh
    for i, p in enumerate(particles):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = obj
        bpy.context.object.select = True

        bpy.ops.object.duplicate(linked=True, mode='INIT')
        dupli = bpy.context.active_object
        dupli.name = 'n' + '_' + layer.name + '_' + '%05d' % (i + 1)
        dupli.location = p.location
        if object_color:
            dupli.color = object_color[i]


def getColors(colormap, v, interval=[], alpha=True, zeroBlack=False, offset=0.0):
    """Based on a colormaps, values in the vector are converted to colors
    from the colormap

    :param list colormap: colormap to be used
    :param list v: list of values
    :param list interval: min and maximal range to be used, if empty these
                          values are computed based on v
    :param list alpha: default true, usually not to be changed
    :param list zeroBlack: if true, zero values are colored in black with 0 alpha independent on the chosen colormap
    :param list offset: shifts the entire colormap. range between -1 and 1. 
    """
    if not interval:
        interval = [min(v), max(v)]

    l = len(colormap) - 1
    span = float(interval[1] - interval[0])
    colors = []

    for i in v:
        if i == 0:
            if alpha:
                colors.append([0.,0.,0.,0.])
            else:
                colors.append([0.,0.,0.])
            continue
        ind = int(numpy.floor((((i - interval[0]) / span) + offset) * l))
        ind = max(min(l, ind), 0)
        if alpha:
            colors.append(colormap[ind])
        else:
            colors.append(colormap[ind][:3])
    return colors


def visualizeNeuronProjLength(no_connection, obj):
    """Visualizes the connection-length of the pre-synaptic neurons for a given
    mapping-index

    :param int no_connection: connection index (mapping index)

    """
    global vis_objects
    layers = model.MODEL.connections[no_connection].pre_layer.obj  # get first layer
    neuronset1 = model.MODEL.connections[no_connection].pre_layer.neuronset_name

    ds = numpy.mean(model.CONNECTION_RESULTS[no_connection]['d'], 1)
    colors = getColors(colormaps.standard, ds)

    generateLayerNeurons(layers, neuronset1, obj, colors)


def visualizePoint(point, obj=None):
    """Visualize a point in 3d by creating a small sphere
    providing an onject as the obj argument duplicates the object instead of creating a sphere"""
    global vis_objects
    
    if not obj:
        bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False, location=point, layers=(True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.ops.transform.resize(value=(0.05, 0.05, 0.05))
    else:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        bpy.ops.object.duplicate(linked=True, mode='INIT')
        bpy.context.selected_objects[0].location = point
        
    bpy.context.selected_objects[0].name = "visualization.%03d" % vis_objects
    vis_objects = vis_objects + 1


def visualizePath(pointlist, smoothing=0, material=None, bevel_resolution = 0):
    """Create path for a given point list

    :param list pointlist: 3d-vectors that are converted to a path
    :param list smoothing: smoothing stepts that should be applied afterwards

    This code is taken and modified from the bTrace-Addon for Blender
    http://blenderartists.org/forum/showthread.php?214872

    """

    global vis_objects

    # trace the origins
    tracer = bpy.data.curves.new('tracer', 'CURVE')
    tracer.dimensions = '3D'
    spline = tracer.splines.new('BEZIER')
    spline.bezier_points.add(len(pointlist) - 1)
    curve = bpy.data.objects.new('curve', tracer)
    bpy.context.scene.objects.link(curve)

    # render ready curve
    tracer.resolution_u = 1
    tracer.bevel_resolution = bevel_resolution  # Set bevel resolution from Panel options
    tracer.fill_mode = 'FULL'
    tracer.bevel_depth = bpy.context.scene.pam_visualize.bevel_depth # Set bevel depth from Panel options

    # move nodes to objects
    for i in range(0, len(pointlist)):
        p = spline.bezier_points[i]
        p.co = pointlist[i]
        p.handle_right_type = 'VECTOR'
        p.handle_left_type = 'VECTOR'

    # bpy.context.scene.objects.active = curve
    # bpy.ops.object.mode_set()
    curve.name = "visualization.%03d" % vis_objects

    vis_objects = vis_objects + 1

    # apply material if given
    if material is not None:
        curve.active_material = material

    # apply smoothing if requested
    if smoothing > 0:
        bpy.context.scene.objects.active = curve
        bpy.ops.object.mode_set()
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action='SELECT')
        for i in range(0, smoothing):
            bpy.ops.curve.smooth()
        bpy.ops.object.editmode_toggle()

    return curve

def calculatePathLength(curveObject):
    """Calculates the length of the path of a curve. 
    Does not take bezier interpolation into account, only distance between points
    :param bpy.types.Object curveObject: The curve
    :return float: The length of the curve"""
    if type(curveObject) == bpy.types.Object:
        data = curveObject.data
    elif type(curveObject) == bpy.types.Curve:
        data = curveObject
    else:
        raise ValueError("curveObject needs to be an Object or a Curve")
    length = 0.0
    for spline in data.splines:
        for i in range(len(spline.bezier_points) - 1):
            dist = spline.bezier_points[i+1].co - spline.bezier_points[i].co
            length += dist.length
    return length

def visualizeForwardMapping(no_connection, pre_index):
    """This is a debugging routine. The procedure tries to visualize the maximal
    amount of mappings to determine, where the mapping fails
    no_connection       : connection/mapping-index
    pre_index           : index of pre-synaptic neuron
    """
    con = model.MODEL.connections[no_connection] 
    layers = con.layers
    slayer = con.synaptic_layer_index
    connections = con.mapping_connections
    distances = con.mapping_distances

    material = bpy.data.materials.get(bpy.context.scene.pam_visualize.connection_material, None)

    for s in range(2, (slayer + 2)):
        pre_p3d, pre_p2d, pre_d = pam.computeMapping(
            layers[0:s],
            connections[0:(s - 1)],
            distances[0:(s - 2)] + [constants.DIS_euclidUV],
            con.pre_layer.getNeuronPosition(pre_index),
            debug=True
        )
        logger.debug(s)
        logger.debug(pre_p3d)
        logger.debug(pre_p2d)
        logger.debug(pre_d)
        if pre_p3d:
            visualizePath(pre_p3d, material = material)


def visualizeBackwardMapping(no_connection, post_index):
    """ This is a debugging routine. The procedure tries to visualize the maximal
    amount of mappings to determine, where the mapping fails
    no_connection       : connection/mapping-index
    post_index          : index of post-synaptic neuron
    """
    con = model.MODEL.connections[no_connection]
    layers = con.layers
    slayer = con.synaptic_layer_index
    connections = con.mapping_connections
    distances = con.mapping_distances

    material = bpy.data.materials.get(bpy.context.scene.pam_visualize.connection_material, None)

    for s in range(len(layers)-3, slayer-2, -1):
        post_p3d, post_p2d, post_d = pam.computeMapping(layers[-1:s:-1],
                                                        connections[-1:s:-1],
                                                        distances[-1:s:-1],
                                                        con.post_layer.getNeuronPosition(post_index))
        logger.debug(s)
        logger.debug(post_p3d)
        if post_p3d:
            visualizePath(post_p3d, material = material)


def visualizeConnectionsForNeuron(no_connection, pre_index, smoothing=0, print_statistics = False):
    """ Visualizes all connections between a given pre-synaptic neuron and its connections
    to all post-synaptic neurons
    layers              : list of layers connecting a pre- with a post-synaptic layer
    neuronset1,
    neuronset2          : name of the neuronset (particle system) of the pre- and post-synaptic layer
    slayer              : index in layers for the synaptic layer
    connections         : list of values determining the type of layer-mapping
    distances           : list of values determining the calculation of the distances between layers
    pre_index           : index of pre-synaptic neuron
    post_indices        : index-list of post-synaptic neurons
    synapses            : optional list of coordinates for synapses
    """

    con = model.MODEL.connections[no_connection]
    layers = con.layers
    slayer = con.synaptic_layer_index
    connections = con.mapping_connections
    distances = con.mapping_distances

    post_indices = model.CONNECTION_RESULTS[no_connection]['c'][pre_index]
    synapses = model.CONNECTION_RESULTS[no_connection]['s'][pre_index]

    if print_statistics:
        print("Visualizing connections for neuron", pre_index, "from", " -> ".join([l.name for l in layers]))

    # path of the presynaptic neuron to the synaptic layer
    pre_p3d, pre_p2d, pre_d = pam.computeMapping(layers[0:(slayer + 1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 con.pre_layer.getNeuronPosition(pre_index))

    first_item = True
    first_item_distance = 0.0
    path_lengthes = []

    material = bpy.data.materials.get(bpy.context.scene.pam_visualize.connection_material, None)

    layers_post = layers[:(slayer - 1):-1]
    connections_post = connections[:(slayer - 1):-1]
    distances_post = distances[:(slayer - 1):-1]

    mapping_post = connection_mapping.Mapping(layers_post, connections_post, distances_post)

    for i in range(0, len(post_indices)):
        if post_indices[i] == -1:
            continue
        post_p3d, post_p2d, post_d = mapping_post.computeMapping(con.post_layer.getNeuronPosition(int(post_indices[i])))
        if synapses is None:
            curve = visualizePath(pre_p3d + post_p3d[::-1], material = material)
            distance = calculatePathLength(curve)
            path_lengthes.append(distance)
        else:
            if (len(synapses[i]) > 0):
                distances_pre, pre_path = pam.computeDistanceToSynapse(
                    layers[slayer - 1], layers[slayer], pre_p3d[-1], mathutils.Vector(synapses[i]), distances[slayer - 1])
                if distances_pre >= 0:
                    distances_post, post_path = pam.computeDistanceToSynapse(
                        layers[slayer + 1], layers[slayer], post_p3d[-1], mathutils.Vector(synapses[i]), distances[slayer])
                    if (distances_post >= 0):
                        if first_item:
                            curve = visualizePath(pre_p3d, smoothing, material = material)
                            first_item_distance = calculatePathLength(curve)
                            curve = visualizePath([pre_p3d[-1]] + pre_path + post_path[::-1] + post_p3d[::-1], smoothing, material = material)
                            first_item_distance += calculatePathLength(curve)
                            first_item = False
                        else:
                            curve = visualizePath([pre_p3d[-1]] + pre_path + post_path[::-1] + post_p3d[::-1], smoothing, material = material)
                            distance = calculatePathLength(curve) + first_item_distance
                            path_lengthes.append(distance)
    
    if print_statistics:
        path_lengthes = numpy.array(path_lengthes)
        delay = layers[0].obj.particle_systems[layers[0].neuronset_name].settings.get('delay', 1.0)
        print("Using a delay modifier of ", delay)
        path_lengthes *= delay

        average_path_length = numpy.mean(path_lengthes)
        standard_deviation = numpy.std(path_lengthes)
        print("Average connection length:", average_path_length)
        print("Standard deviation:       ", standard_deviation)
        print("Maximum connection length:", numpy.amax(path_lengthes))
        print("Minimum connection length:", numpy.amin(path_lengthes))

    if not first_item:
        return [pre_p3d[-1]] + pre_path + post_path[::-1] + post_p3d[::-1]
    else:
        return []


def visualizeOneConnection(no_connection, pre_index, post_index, smoothing=0):
    """ Visualizes all connections between a given pre-synaptic and a given post-synaptic
    no_connection       : connection/mapping-id
    pre_index           : index of pre-synaptic neuron
    post_index          : index of post-synaptic neuron
    post_list_index     : index to be used in c[pre_index][post_list_index] to address post_index
    synapses            : optional list of coordinates for synapses
    """

    where_list = numpy.where(model.CONNECTION_RESULTS[no_connection]['c'][pre_index] == post_index)[0]
    if len(where_list)==0:
        return None
    post_list_index = where_list[0]
    
    con = model.MODEL.connections[no_connection]
    layers = con.layers
    slayer = con.synaptic_layer_index
    connections = con.mapping_connections
    distances = con.mapping_distances

    synapses = model.CONNECTION_RESULTS[no_connection]['s'][pre_index]

    material = bpy.data.materials.get(bpy.context.scene.pam_visualize.connection_material, None)

    # path of the presynaptic neuron to the synaptic layer
    pre_p3d, pre_p2d, pre_d = pam.computeMapping(layers[0:(slayer + 1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 con.pre_layer.getNeuronPosition(pre_index))

    post_p3d, post_p2d, post_d = pam.computeMapping(layers[:(slayer - 1):-1],
                                                    connections[:(slayer - 1):-1],
                                                    distances[:(slayer - 1):-1],
                                                    con.post_layer.getNeuronPosition(post_index))
    if synapses is None:
        return visualizePath(pre_p3d + post_p3d[::-1], smoothing, material = material)
    else:
        distances_pre, pre_path = pam.computeDistanceToSynapse(
            layers[slayer - 1], layers[slayer], pre_p3d[-1], mathutils.Vector(synapses[post_list_index]), distances[slayer - 1])
        if distances_pre >= 0:
            distances_post, post_path = pam.computeDistanceToSynapse(
                layers[slayer + 1], layers[slayer], post_p3d[-1], mathutils.Vector(synapses[post_list_index]), distances[slayer])
            if distances_post >= 0:
                return visualizePath(pre_p3d + pre_path + post_path[::-1] + post_p3d[::-1], smoothing, material = material)

def visualizeOneConnectionPre(no_connection, pre_index, smoothing=0):
    """ Visualizes the connection up to the forking just before the synapse
    :param no_connection: connection/mapping-id
    :type no_connection: int
    :param pre_index: index of pre-synaptic neuron
    :type pre_index: int
    :return: The created curve object
    :rtype: bpy.types.Object
    """
    
    con = model.MODEL.connections[no_connection]
    layers = con.layers
    slayer = con.synaptic_layer_index
    connections = con.mapping_connections
    distances = con.mapping_distances

    synapses = model.CONNECTION_RESULTS[no_connection]['s'][pre_index]

    material = bpy.data.materials.get(bpy.context.scene.pam_visualize.connection_material, None)

    # path of the presynaptic neuron to the synaptic layer
    pre_p3d, pre_p2d, pre_d = pam.computeMapping(layers[0:(slayer + 1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 con.pre_layer.getNeuronPosition(pre_index))

    return visualizePath(pre_p3d, smoothing, material = material)
    
def visualizeOneConnectionPost(no_connection, pre_index, post_index, smoothing=0):
    """ Visualizes only the part of a connection, where the connection starts to fork to the given post-neuron
    :param no_connection: connection/mapping-id
    :type no_connection: int
    :param pre_index: index of pre-synaptic neuron
    :type pre_index: int
    :param post_index: index of post-synaptic neuron
    :type post_index: int
    :return: The created curve object
    :rtype: bpy.types.Object
    """

    where_list = numpy.where(model.CONNECTION_RESULTS[no_connection]['c'][pre_index] == post_index)[0]
    if len(where_list)==0:
        return None
    post_list_index = where_list[0]
    
    con = model.MODEL.connections[no_connection]
    layers = con.layers
    slayer = con.synaptic_layer_index
    connections = con.mapping_connections
    distances = con.mapping_distances

    synapses = model.CONNECTION_RESULTS[no_connection]['s'][pre_index]

    material = bpy.data.materials.get(bpy.context.scene.pam_visualize.connection_material, None)

    # path of the presynaptic neuron to the synaptic layer
    pre_p3d, pre_p2d, pre_d = pam.computeMapping(layers[0:(slayer + 1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 con.pre_layer.getNeuronPosition(pre_index))

    post_p3d, post_p2d, post_d = pam.computeMapping(layers[:(slayer - 1):-1],
                                                    connections[:(slayer - 1):-1],
                                                    distances[:(slayer - 1):-1],
                                                    con.post_layer.getNeuronPosition(post_index))
    if synapses is None:
        return visualizePath(post_p3d[::-1], smoothing, material = material)
    else:
        distances_pre, pre_path = pam.computeDistanceToSynapse(
            layers[slayer - 1], layers[slayer], pre_p3d[-1], mathutils.Vector(synapses[post_list_index]), distances[slayer - 1])
        if distances_pre >= 0:
            distances_post, post_path = pam.computeDistanceToSynapse(
                layers[slayer + 1], layers[slayer], post_p3d[-1], mathutils.Vector(synapses[post_list_index]), distances[slayer])
            if distances_post >= 0:
                return visualizePath(pre_path + post_path[::-1] + post_p3d[::-1], smoothing, material = material)


def visualizeNeuronSpread(connections, neuron):
    """Visualize for a collection of connections, the post-synaptic targets
    of a given neuron number of the first layer in the first connection and
    iteratively uses the post-synaptic targets as pre-synaptic neurons for
    the following connections

    :param list connections: list of connection-ids
    :param int neuron: neuron number for the pre-synaptic layer of the first
                       connection

    """
    visualizeConnectionsForNeuron(connections[0], neuron)
    if (len(connections) > 1):
        post_indices = model.CONNECTION_RESULTS[connections[0]]['c'][neuron]
        for post_index in post_indices[0:1]:
            if post_index >= 0:
                visualizeNeuronSpread(connections[1:], post_index)


def visualizeUnconnectedNeurons(no_connection):
    """ Visualizes unconnected neurons for a given connection_index """
    c = numpy.array(model.CONNECTION_RESULTS[no_connection]['c'])
    sums = numpy.array([sum(row) for row in c])
    indices = numpy.where(sums == -model.MODEL.connections[no_connection].synaptic_layer.no_synapses)[0]

    logger.info(indices)
    neuron_count = len(c)
    unconnected_count = len(indices)
    logger.info(str(unconnected_count) + "/" + str(neuron_count) + ", " + str(round((unconnected_count / neuron_count) * 10000) / 100) + "%")

    layer = model.MODEL.connections[no_connection].pre_layer

    for index in indices:
        visualizePoint(layer.getNeuronPosition(index))
        
def visualizeUnconnectedPostNeurons(no_connection):
    """ Visualizes unconnected neurons for a given connection_index """
    c = model.CONNECTION_RESULTS[no_connection]['c']
    
    layer = model.MODEL.connections[no_connection].post_layer    #last layer of connection
    indices = []
    neuron_count = len(c)

    for index in range(neuron_count):
        if not index in c:
            visualizePoint(layer.getNeuronPosition(index))
            indices.append(index)

    logger.info(indices)
    unconnected_count = len(indices)
    logger.info(str(unconnected_count) + "/" + str(neuron_count) + ", " + str(round((unconnected_count / neuron_count) * 10000) / 100) + "%")


def visualizePartlyConnectedNeurons(no_connection):
    """ Visualizes neurons which are only partly connected """
    c = numpy.array(model.CONNECTION_RESULTS[no_connection]['c'])
    sums = numpy.array([sum(row) for row in c])
    indices = numpy.where(sums < model.MODEL.connections[no_connection].synaptic_layer.no_synapses)[0]

    logger.info(indices)

    layer = model.MODEL.connections[no_connection].pre_layer

    for index in indices:
        visualizePoint(layer.getNeuronPosition(index))

def visualizeClean():
    """delete all visualization objects"""

    # delete all previous spheres
    global vis_objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern="visualization*")
    bpy.ops.object.delete(use_global=False)
    vis_objects = 0


def polygons_coordinate(obj):
    r = []
    for p in obj.data.polygons:
        co = []
        for v in p.vertices:
            co.append(obj.data.vertices[v].co)
        r.append(co)
    return r


def color_polygons(obj, colors):
    if len(obj.data.polygons) != len(colors):
        raise Exception("number of colors given does not match polgyons")

    if not obj.data.vertex_colors:
        obj.data.vertex_colors.new()

    vc = obj.data.vertex_colors.active

    for c, p in zip(colors, obj.data.polygons):
        for v in p.loop_indices:
            vc.data[v].color = c


def vertices_coordinate(obj):
    return [v.co for v in obj.data.vertices]


def color_vertices(obj, colors):
    if len(obj.data.vertices) != len(colors):
        raise Exception("number of colors given does not match vertices")

    if not obj.data.vertex_colors:
        obj.data.vertex_colors.new()

    vc = obj.data.vertex_colors.active

    vc_index = [v for p in obj.data.polygons for v in p.vertices]

    for i, n in enumerate(vc_index):
        vc.data[i].color = colors[n]


# TODO(SK): Parameter types
def colorize_vertices(obj, v, interval=[]):
    """Colorize vertices of an object based on values in v and a
    given interval

    :param bpy.types.Object obj: objects, whose vertices should be used
    :param (???) v: vector length must correspond to number of vertices
    :param interval: min and maximal range. if empty, it will be computed
                     based on v

    """
    
    
    colors = getColors(colormaps.standard, v, interval, alpha=False)
    color_vertices(obj, colors)


def visualizeMappingDistance(no_mapping):
    """ visualizes the mapping distance for a pre-synaptic layer and a given
    mapping. The mapping distance is visualized by colorizing the vertices
    of the layer """
    layers = model.MODEL.connections[no_mapping].layers

    distances = []

    for ds in model.CONNECTION_RESULTS[no_mapping]['d']:
        distances.append(numpy.mean(ds))

    colorize_vertices(layers[0].obj, distances)


def computeAxonLengths(no_connection, pre_index, visualize=False):
    """ Computes the axon length to each synapse for each post-synaptic neuron the pre-
    synaptic neuron is connected with
    no_connection       : connection/mapping-id
    pre_index           : index of pre-synaptic neuron
    """

    con = model.MODEL.connections[no_connection]
    layers = con.layers
    slayer = con.synaptic_layer_index
    connections = con.mapping_connections
    distances = con.mapping_distances

    post_indices = model.CONNECTION_RESULTS[no_connection]['c'][pre_index]
    synapses = model.CONNECTION_RESULTS[no_connection]['s'][pre_index]

    # path of the presynaptic neuron to the synaptic layer
    pre_p3d, pre_p2d, pre_d = pam.computeMapping(layers[0:(slayer + 1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 con.pre_layer.getNeuronPosition(pre_index))

    first_item = True
    
    result = []

    for i in range(0, len(post_indices)):
        if post_indices[i] == -1:
            continue

        if synapses is None:
            result.append(mesh.compute_path_length(pre_p3d))
        else:
            if (len(synapses[i]) > 0):
                distances_pre, pre_path = pam.computeDistanceToSynapse(
                    layers[slayer - 1], layers[slayer], pre_p3d[-1], synapses[i], distances[slayer - 1])
                result.append(mesh.compute_path_length(pre_p3d + pre_path))
                if visualize:
                    visualizePath(pre_p3d + pre_path)
    return result


def hideAllLayers():
    """ Hide all layers involved in all mappings. If a layer occurs multiple times
    it is also called here multiple times """
    for m in model.MODEL.connections:
        for layer in m.layers:
            layer.obj.hide = True
            
def showMappingLayers(index):
    """ shows for a given mapping all layers involved in but hides everything else """
    hideAllLayers()
    for layer in model.MODEL.connections[index].layers:
        layer.obj.hide = False
        
def showPrePostLayers():
    """ shows for all mappings all the pre- and post-layers and hides everything else """
    hideAllLayers()
    for m in model.MODEL.connections:
        m.pre_layer.obj.hide = False
        m.post_layer.obj.hide = False
