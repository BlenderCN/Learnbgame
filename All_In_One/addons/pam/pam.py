"""THis module contains the core functions needed to compute pam models"""

import logging
import random

import bpy
import mathutils
import numpy

from . import constants
from . import grid
from . import model
from . import exceptions
from . import layer
from . import connection_mapping
from .mesh import *

import multiprocessing
import os

logger = logging.getLogger(__package__)

SEED = 0


# TODO(SK): Rephrase docstring, add parameter/return values
def computeUVScalingFactor(obj):
    """Compute the scaling factor between uv- and 3d-coordinates for a
    given object
    the return value is the factor that has to be multiplied with the
    uv-coordinates in order to have metrical relation

    """

    result = []

    for i in range(len(obj.data.polygons)):
        uvs = [obj.data.uv_layers.active.data[li] for li in obj.data.polygons[i].loop_indices]

        rdist = (obj.data.vertices[obj.data.polygons[i].vertices[0]].co - obj.data.vertices[obj.data.polygons[i].vertices[1]].co).length
        mdist = (uvs[0].uv - uvs[1].uv).length
        result.append(rdist / mdist)

    # TODO (MP): compute scaling factor on the basis of all edges
    return numpy.mean(result), result

def map3dPointToParticle(obj, particle_system, location):
    """Determine based on a 3d-point location (e.g. given by the cursor
    position) the index of the closest particle on an object

    :param obj: The object from which to choose
    :type obj: bpy.types.Object
    :param particle_system: The name of the particle system
    :type particle_system: str
    :param location: The 3d point
    :type location: mathutils.Vector

    :return: The index of the closest particle
    :rtype: int
    """

    index = -1
    distance = float("inf")
    for (i, p) in enumerate(obj.particle_systems[particle_system].particles):
        if (p.location - location).length < distance:
            distance = (p.location - location).length
            index = i

    return index


# TODO(SK): Rephrase docstring, add parameter/return values
def maskParticle(p_layer, p_index, mask_layer, distance=0.2):
    """Return particle-indices of particle_layer that have a smaller
    distance than the distance-argument to mask_layer

    :param bpy.types.Object p_layer: object that contains the particles
    :param int p_index: index of particle-system
    :param bpy.types.Object mask_layer: mask object
    :param float distance: distance threshold
    :return:
    :rtype:

    """
    result = []
    for i, p in enumerate(p_layer.particle_systems[p_index].particles):
        l, n, f = mask_layer.closest_point_on_mesh(p.location)
        if (p.location - l).length < distance:
            result.append(i)
    return result


# TODO(SK): Rephrase docstring, add parameter/return values
def distanceToMask(p_layer, p_index, particle_index, mask_layer):
    """Return the distance for a particle to a mask_layer

    :param bpy.types.Object p_layer: object with particle-system
    :param int p_index: index of particle-system
    :param int particle_index: index of particle
    :param bpy.types.Object mask_layer: object that serves as mask
    :return:
    :rtype:

    """
    p = p_layer.particle_systems[p_index].particles[particle_index]
    l, n, f = mask_layer.closest_point_on_mesh(p.location)
    return (p.location - l).length


# TODO(SK): missing docstring
# TODO(SK): Rephrase docstring, add parameter/return values
def computeConnectivityProbability(uv1, uv2, func, args):
    return func(uv1, uv2, args)



# TODO(SK): Rephrase docstring, add parameter/return values
def computeDistance_PreToSynapse(no_connection, pre_index, synapses=[]):
    """Compute distance for a pre-synaptic neuron and a certain
    connection definition
    synapses can be optionally be used to compute the distance for only a 
    subset of synapses
    """
    con = model.MODEL.connections[no_connection]
    layers = con.layers
    slayer = con.synaptic_layer_index
    connections = con.mapping_connections
    distances = con.mapping_distances

    point = con.pre_layer.getNeuronPosition(pre_index)

    pre_p3d, pre_p2d, pre_d = computeMapping(layers[0:(slayer + 1)] + [layers[slayer]],
                                             connections[0:slayer] + [connections[slayer]],
                                             distances[0:slayer] + [distances[slayer]],
                                             point)
    
    if  pre_p3d:
        if (distances[slayer] == constants.DIS_normalUV) | (distances[slayer] == constants.DIS_euclidUV):
            uv_distances = []
            # if synapses is empty, simply calculate it for all synapses
            if not synapses:
                s2ds = model.CONNECTION_RESULTS[no_connection]['s'][pre_index]
            else:
                s2ds = [model.CONNECTION_RESULTS[no_connection]['s'][pre_index][s] for s in synapses]
                
            for s2d in s2ds:
                #try:
                uv_distance, _ = computeDistanceToSynapse(layers[slayer], layers[slayer], pre_p3d[-1], mathutils.Vector(s2d), distances[slayer])
                uv_distances.append(uv_distance)
                #except exceptions.MapUVError as e:
                #    logger.info("Message-pre-data: ", e)
                #except Exception as e:
                #    logger.info("A general error occured: ", e)

            path_length = compute_path_length(pre_p3d) + numpy.mean(uv_distances)
        else:
            path_length = compute_path_length(pre_p3d)
    else: 
        path_length = 0.

    return path_length, pre_p3d

# TODO(SK): Rephrase docstring, add parameter/return values
def sortNeuronsToUV(layer, neuronset, u_or_v):
    """Sort particles according to their position on the u
    or v axis and returns the permutation indices

    :param bpy.types.Object layer: layer were the neurons are
    :param str neuronset: name or number of the neuronset (particle system)
    :param str u_or_v: `u` means sort for u
                       `v` means sort for v
    :return:
    :rtype:

    """

    if u_or_v == 'u':
        index = 0
    elif u_or_v == 'v':
        index = 1
    else:
        raise Exception("u_or_v must be either 'u' or 'v' ")

    # get all particle positions
    p3d = [i.location for i in layer.particle_systems[neuronset].particles]
    # convert them to 2d and select just the u or v coordinate
    p2d = [map3dPointToUV(layer, layer, p)[index] for p in p3d]

    # return permutation of a sorted list (ascending)
    return numpy.argsort(p2d)


# TODO(SK): Rephrase docstring, add parameter/return values
# TODO(SK): Structure return values in docstring
def computeMapping(layers, connections, distances, point, debug=False):
    """Based on a list of layers, connections-properties and distance-properties,
    this function returns the 3d-point, the 2d-uv-point and the distance from a given
    point on the first layer to the corresponding point on the last layer

    :param list layers: layers connecting the pre-synaptic layer with the synaptic layer
    :param list connections: values determining the type of layer-mapping
    :param list distances: values determining the calculation of the distances between layers
    :param mathutils.Vector point: vector for which the mapping should be calculated
    :param bool debug: if true, the function returns a list of layers that it was able
                          to pass. Helps to debug the mapping-definitions in order to figure
                          our where exactly the mapping stops

    Return values

    p3d                   list of 3d-vector of the neuron position on all layers until the last
                          last position before the synapse. Note, that this might be before the
                          synapse layer!!! This depends on the distance-property.

    p2d                   2d-vector of the neuron position on the UV map of the last layer

    d                     distance between neuron position on the first layer and last position before
                          the synapse! This is not the distance to the p3d point! This is either the
                          distance to the 3d-position of the last but one layer or, in case
                          euclidean-uv-distance was used, the distance to the position of the last
                          layer determind by euclidean-distance. Functions, like computeConnectivity()
                          add the distance to the synapse to value d in order to retrieve
                          the complete distance from the pre- or post-synaptic neuron
                          to the synapse

    """

    mapping = connection_mapping.Mapping(layers, connections, distances, debug)
    return mapping.computeMapping(point)


# TODO(SK): Rephrase docstring, add parameter/return values
def computeDistanceToSynapse(ilayer, slayer, p_3d, s_2d, dis):
    """Compute the distance between the last 3d-point and the synapse

    ilayer      : last intermediate layer
    slayer      : synaptic layer
    p_3d        : last 3d-point
    s_2d        : uv-coordinates of the synapse
    dis         : distance calculation technique

    """
    s_3d = slayer.mapUVPointTo3d([s_2d])
    if not any(s_3d):
        raise exceptions.MapUVError(slayer, dis, s_2d)

    if dis == constants.DIS_euclid:
        return (p_3d - s_3d[0]).length, s_3d

    elif dis == constants.DIS_euclidUV:
        path = [p_3d]
        path = path + slayer.interpolateUVTrackIn3D(p_3d, s_3d[0])
        path.append(s_3d[0])
        return compute_path_length(path), path

    elif dis == constants.DIS_jumpUV:
        path = [p_3d]
        path = path + slayer.interpolateUVTrackIn3D(p_3d, s_3d[0])
        path.append(s_3d[0])
        return compute_path_length(path), path

    elif dis == constants.DIS_UVjump:
        i_3d = ilayer.closest_point_on_mesh(s_3d[0])[0]
        path = [p_3d]
        path = path + ilayer.interpolateUVTrackIn3D(p_3d, i_3d)
        path.append(i_3d)
        path.append(s_3d[0])
        return compute_path_length(path), path

    elif dis == constants.DIS_normalUV:
        path = [p_3d]
        path = path + slayer.interpolateUVTrackIn3D(p_3d, s_3d[0])
        path.append(s_3d[0])
        return compute_path_length(path), path

    elif dis == constants.DIS_UVnormal:
        p, n, f = slayers.closest_point_on_mesh(s_3d[0])
        t_3d = ilayer.map3dPointTo3d(layer, p, n)
        if t_3d is None:
            raise exceptions.MapUVError(slayer, dis, [p, n])
        path = [p_3d]
        path = path + ilayer.interpolateUVTrackIn3D(p_3d, t_3d)
        path.append(t_3d)
        path.append(s_3d[0])
        return compute_path_length(path), path


def addConnection(*args):
    """Adds a new connection to model.MODEL.

    If args is a connection object, the object is added to the model. Otherwise, a new 
    connection object is created using args and then added. The index of the added 
    connection in the model is returned."""

    if type(args[0]) is model.Connection:
        model.MODEL.addConnection(args[0])
    else:
        con = model.Connection(*args)
        model.MODEL.addConnection(con)

    # returns the future index of the connection
    return (len(model.MODEL.connections) - 1)

def replaceMapping(index, connection):
    """ Replaces a mapping with a given index by the given connection

    :param index: The index of the connection to be replaced. If the index is out of bounds, 
    the connection is appended to the connections.
    :type index: int
    :param connection: The new connection
    :type connection: model.Connection

    :return: The index of the replaced connection. Equal to index if index is in bounds.
    :rtype: int
    """

    if index >= len(model.MODEL.connections):
        model.MODEL.connections.append(connection)
        return len(model.MODEL.connections) - 1
    else:
        model.MODEL.connections[index] = connection
        return index

def computeAllConnections():
    """Computes all connections in model.MODEL and saves the result in model.CONNECTION_RESULTS"""
    for c in model.MODEL.connections:
        logger.info(c.pre_layer.name + ' - ' + c.post_layer.name)
        
        result = computeConnectivity(c)

        model.CONNECTION_RESULTS.append(
            {
                'c': result[0],
                'd': result[1],
                's': result[2]
            }
        )


def updateMapping(index):
    """Update a mapping given by index

    Computes a single connection without deleting any other connections results. 
    The results are saved in model.CONNECTION_RESULTS

    :param index: The index of the connection to update
    :type index: int
    """
    c = model.MODEL.connections[index]
    result = computeConnectivity(c, create=False)
    model.CONNECTION_RESULTS[index] = {
        'c': result[0],
        'd': result[1],
        's': result[2]
    }

def computeConnectivity(con, create=True, threads = None):
    """Computes for each pre-synaptic neuron no_synapses connections to post-synaptic neurons
    with the given parameters
    :param Connection con: The connection to be computed (See model.Connection for details)
    :param bool create: if create == True, then create new connection, otherwise it is just updated
    :param int threads: If not -1, computeConnectivityThreaded is called instead with number of given threads.
                        If None, addon preferences are used. If 0, os.cpu_count() is used.
    """
    # Determine if threading is to be used
    if threads == None:
        if bpy.context.user_preferences.addons['pam'].preferences.use_threading:
            return computeConnectivityThreaded(con, create, threads)
    elif threads != -1:
        return computeConnectivityThreaded(con, create, threads)

    no_synapses = con.synaptic_layer.no_synapses
    slayer = con.synaptic_layer_index
    connections, distances = zip(*con.mappings)
    layers = con.layers
    # connection matrix
    conn = numpy.zeros((con.pre_layer.neuron_count, no_synapses), dtype = numpy.int)

    # distance matrix
    dist = numpy.zeros((con.pre_layer.neuron_count, no_synapses))

    # synapse mattrx (matrix, with the uv-coordinates of the synapses)
    syn = [[[] for j in range(no_synapses)] for i in range(con.pre_layer.neuron_count)]

    uv_grid = grid.UVGrid(con.synaptic_layer.obj, 0.02)

    # rescale arg-parameters
    # args_pre = [i / layers[slayer].obj['uv_scaling'] for i in args_pre]
    # args_post = [i / layers[slayer].obj['uv_scaling'] for i in args_post]
    con.pre_layer.kernel.rescale(con.synaptic_layer.obj['uv_scaling'])
    con.post_layer.kernel.rescale(con.synaptic_layer.obj['uv_scaling'])

    logger.info("Prepare Grid")

    uv_grid.compute_pre_mask(con.pre_layer.kernel)
    uv_grid.compute_post_mask(con.post_layer.kernel)

    logger.info("Compute Post-Mapping")

    layers_post = layers[:(slayer - 1):-1]
    connections_post = connections[:(slayer - 1):-1]
    distances_post = distances[:(slayer - 1):-1]

    mapping_post = connection_mapping.Mapping(layers_post, connections_post, distances_post)

    # fill uv_grid with post-neuron-links
    for i in range(0, con.post_layer.neuron_count):
        random.seed(i + SEED)
        post_p3d, post_p2d, post_d = mapping_post.computeMapping(con.post_layer.getNeuronPosition(i))
        if post_p3d is None:
            continue
        
        uv_grid.insert_postNeuron(i, post_p2d, post_p3d[-1].to_tuple(), post_d)


    #uv_grid.convert_postNeuronStructure()
    #for m in uv_grid._masks['post']:
    #    print(len(m))
    logger.info("Compute Pre-Mapping")

    layers_pre = layers[0:(slayer + 1)]
    connections_pre = connections[0:slayer]
    distances_pre = distances[0:slayer]
    mapping_pre = connection_mapping.Mapping(layers_pre, connections_pre, distances_pre)

    num_particles = con.pre_layer.neuron_count
    for i in range(0, num_particles):
        random.seed(i + SEED)
        pre_p3d, pre_p2d, pre_d = mapping_pre.computeMapping(con.pre_layer.getNeuronPosition(i))

        logger.info(str(round((i / num_particles) * 10000) / 100) + '%')

        if pre_p3d is None:
            for j in range(0, len(conn[i])):
                conn[i, j] = -1
            continue

        numpy.random.seed(i + SEED)

        post_neurons = uv_grid.select_random(pre_p2d, no_synapses)

        if (len(post_neurons) == 0):
            for j in range(0, len(conn[i])):
                conn[i, j] = -1
            continue

        for j, post_neuron in enumerate(post_neurons):
            try:
                distance_pre, _ = computeDistanceToSynapse(
                    layers[slayer - 1], layers[slayer], pre_p3d[-1], mathutils.Vector(post_neuron[1]), distances[slayer - 1])
                try: 
                    distance_post, _ = computeDistanceToSynapse(
                        layers[slayer + 1], layers[slayer], mathutils.Vector(post_neuron[0][2]), mathutils.Vector(post_neuron[1]), distances[slayer])
                    conn[i, j] = post_neuron[0][0]      # the index of the post-neuron
                    dist[i, j] = pre_d + distance_pre + distance_post + post_neuron[0][3]      # the distance of the post-neuron
                    syn[i][j] = post_neuron[1]
                except exceptions.MapUVError as e:
                    logger.info("Message-post-data: " + str(e))
                    model.CONNECTION_ERRORS.append(e)
                    conn[i, j] = -1
                    syn[i][j] = mathutils.Vector((0, 0))
                except Exception as e:
                    logger.info("A general error occured: " + str(e))
                    conn[i, j] = -1
                    syn[i][j] = mathutils.Vector((0, 0))
            except exceptions.MapUVError as e:
                logger.info("Message-pre-data: " + str(e))
                model.CONNECTION_ERRORS.append(e)
                conn[i, j] = -1
                syn[i][j] = mathutils.Vector((0, 0))
            except Exception as e:
                logger.info("A general error occured: " + str(e))
                conn[i, j] = -1
                syn[i][j] = mathutils.Vector((0, 0))

        for rest in range(j + 1, no_synapses):
            conn[i, rest] = -1

    if create:
        model.MODEL.connection_indices.append(
            [
                len(model.MODEL.connection_indices),
                model.MODEL.ng_dict[con.pre_layer.name][con.pre_layer.neuronset_name],
                model.MODEL.ng_dict[con.post_layer.name][con.post_layer.neuronset_name]
            ]
        )

    return conn, dist, syn, uv_grid

def post_neuron_wrapper(x):
    """Wrapper for computing post neuron mapping. To be used with multithreading."""
    global mapping_post
    random.seed(x[0] + SEED)
    p3d, p2d, dis = mapping_post.computeMapping(mathutils.Vector(x[1]))
    if p3d is not None:
        p3d = [v[:] for v in p3d]
    if p2d is not None:
        p2d = (p2d[0], p2d[1])
    return (x[0], p3d, p2d, dis)

def post_neuron_initializer(players, pconnections, pdistances):
    """Initialization function for all threads in the threadpool for post neuron mapping.

    NOTE: globals are only available in the executing thread, so don't expect them 
    to be available in the main thread."""
    global mapping_post
    # TODO (PH): Threading sometimes get deadlocked here, probably because of simultaneous access to bpy.data.objects. Use locks?
    layers = [layer.Layer2d("", bpy.data.objects[i]) for i in players]
    connections = pconnections
    distances = pdistances
    mapping_post = connection_mapping.Mapping(layers, connections, distances)
    
def pre_neuron_wrapper(x):
    """Wrapper for computing pre neuron mapping. To be used with multithreading."""
    i, particle = x

    global uv_grid
    global layers
    global mapping_pre
    global distances
    global no_synapses

    random.seed(i + SEED)
    pre_p3d, pre_p2d, pre_d = mapping_pre.computeMapping(mathutils.Vector(particle))

    conn = numpy.zeros(no_synapses)
    dist = numpy.zeros(no_synapses)
    syn = [[] for j in range(no_synapses)]

    if pre_p3d is None:
        for j in range(0, no_synapses):
            conn[j] = -1
        return (conn, dist, syn)

    numpy.random.seed(i + SEED)
    post_neurons = uv_grid.select_random(pre_p2d, no_synapses)
    for j, post_neuron in enumerate(post_neurons):
        try:
            # The layers have been already sliced before being sent to the thread, so the last element is at slayer + 1
            distance_pre, _ = computeDistanceToSynapse(
                layers[-3], layers[-2], pre_p3d[-1], mathutils.Vector(post_neuron[1]), distances[-2])
            try:
                distance_post, _ = computeDistanceToSynapse(
                    layers[-1], layers[-2], mathutils.Vector(post_neuron[0][2]), mathutils.Vector(post_neuron[1]), distances[-1])
               
                conn[j] = post_neuron[0][0]      # the index of the post-neuron
                dist[j] = pre_d + distance_pre + distance_post + post_neuron[0][3]      # the distance of the post-neuron
                syn[j] = post_neuron[1]
            except exceptions.MapUVError as e:
                print("Post mapping error:", i, str(e))
                conn[j] = -1
            except Exception as e:
                print("General error in post:", i, str(e))
                conn[j] = -1
        except exceptions.MapUVError as e:
            print("Pre mapping error:", i, str(e))
            conn[j] = -1
        except Exception as e:
            print("General error in pre:", i, str(e))
            conn[j] = -1

    return (conn, dist, syn)

def pre_neuron_initializer(players, pconnections, pdistances, puv_grid, pno_synapses):
    """Initialization function for pre neuron mapping for multithreading

    NOTE: globals are only available in the executing thread, so don't expect them 
    to be available in the main thread."""
    global uv_grid
    global layers
    global mapping_pre
    global distances
    global no_synapses
    uv_grid = puv_grid
    layers = [layer.Layer2d("", bpy.data.objects[i]) for i in players]
    connections = pconnections
    distances = pdistances
    no_synapses = pno_synapses
    mapping_pre = connection_mapping.Mapping(layers[:-1], connections[:-1], distances[:-1])

def computeConnectivityThreaded(con, create=True, threads = None):
    """Multithreaded version of computeConnectivity()
    Computes for each pre-synaptic neuron no_synapses connections to post-synaptic neurons
    with the given parameters

    :param Connection con: The connection to be computed (See model.Connection for details)
    :param bool create: if create == True, then create new connection, otherwise it is just updated
    :param int threads: Number of threads to be used for multiprocessing. If None, Value in addon preferences is used.
                        If 0, os.cpu_count() is used.

    """
    # Determine number of threads
    if threads == None:
        threads = bpy.context.user_preferences.addons['pam'].preferences.threads
    if threads < 1:
        threads = os.cpu_count()
    logger.info("Using " + str(threads) + " threads")

    no_synapses = con.synaptic_layer.no_synapses
    slayer = con.synaptic_layer_index
    connections, distances = zip(*con.mappings)
    layers = con.layers

    # connection matrix
    conn = numpy.zeros((con.pre_layer.neuron_count, no_synapses), dtype = numpy.int)

    # distance matrix
    dist = numpy.zeros((con.pre_layer.neuron_count, no_synapses))

    # synapse mattrx (matrix, with the uv-coordinates of the synapses)
    syn = [[[] for j in range(no_synapses)] for i in range(con.pre_layer.neuron_count)]

    uv_grid = grid.UVGrid(con.synaptic_layer.obj, 0.02)

    # rescale arg-parameters
    con.pre_layer.kernel.rescale(con.synaptic_layer.obj['uv_scaling'])
    con.post_layer.kernel.rescale(con.synaptic_layer.obj['uv_scaling'])

    logger.info("Compute Post-Mapping")
    
    layers_threading = [x.obj_name for x in layers[:(slayer - 1):-1]]
    connections_threading = connections[:(slayer - 1):-1]
    distances_threading = distances[:(slayer - 1):-1]

    pool = multiprocessing.Pool(processes = threads, 
                                initializer = post_neuron_initializer, 
                                initargs = (layers_threading, connections_threading, distances_threading))

    # Collect particles for post-mapping
    particles = layers[-1].neuronset
    thread_mapping = [(i,  particles[i].location.to_tuple()) for i in range(0, len(particles))]
    
    # Execute the wrapper for multiprocessing
    # Calculates post neuron mappings
    result_async = pool.map_async(post_neuron_wrapper, thread_mapping)

    pool.close()

    # While post neuron mapping is running, we can prepare the grid
    logger.info("Prepare Grid")

    uv_grid.compute_pre_mask(con.pre_layer.kernel)
    uv_grid.compute_post_mask(con.post_layer.kernel)

    logger.info("Finished Grid")
    # Block until the results for the post mapping are in
    result = result_async.get()
    pool.join()
    logger.info("Finished Post-Mapping")
    
    # fill uv_grid with post-neuron-links
    for i, post_p3d, post_p2d, post_d in result:
        if post_p3d is None:
            continue
        uv_grid.insert_postNeuron(i, post_p2d, post_p3d[-1], post_d)

    uv_grid.convert_data_structures()

    #uv_grid.convert_postNeuronStructure()
    logger.info("Compute Pre-Mapping")
    num_particles = layers[0].neuron_count

    layers_pre = [l.obj_name for l in layers[0:(slayer + 2)]]
    connections_pre = connections[0:slayer + 1]
    distances_pre = distances[0:slayer + 1]

    pool = multiprocessing.Pool(processes = threads, 
                                initializer = pre_neuron_initializer, 
                                initargs = (layers_pre, connections_pre, distances_pre, uv_grid, no_synapses))

    # Collect particles for pre-mapping
    particles = layers[0].neuronset
    thread_mapping = [(i,  particles[i].location.to_tuple()) for i in range(0, len(particles))]

    result = pool.map(pre_neuron_wrapper, thread_mapping)

    pool.close()
    pool.join()
    
    for i, item in enumerate(result):
        conn[i] = item[0]
        dist[i] = item[1]
        syn[i] = item[2]

    logger.info("Finished Pre-Mapping")

    if create:
        model.MODEL.connection_indices.append(
            [
                len(model.MODEL.connection_indices),
                model.MODEL.ng_dict[con.pre_layer.name][con.pre_layer.neuronset_name],
                model.MODEL.ng_dict[con.post_layer.name][con.post_layer.neuronset_name]
            ]
        )

    return conn, dist, syn, uv_grid

def computeConnectivityAll(layers, neuronset1, neuronset2, slayer, connections, distances, func, args):
    """DEPRECATED
       ----------
    Compute the connectivity probability between all neurons of both neuronsets
    on a synaptic layer

    :param list layers: layers connecting a pre- with a post-synaptic layer
    :param str neuronset1:
    :param str neuronset2: name of the neuronset (particle system) of the pre- and post-synaptic layer
    :param int slayer: index in layers for the synaptic layer
    :param list connections: values determining the type of layer-mapping
    :param list distances: values determining the calculation of the distances between layers
    :param function func: connectivity kernel
    :param list args: arguments for the connectivity kernel

    """

    # connection matrix
    conn = numpy.zeros((len(layers[0].particle_systems[neuronset1].particles),
                        len(layers[-1].particle_systems[neuronset2].particles)))

    # distance matrix
    dist = numpy.zeros((len(layers[0].particle_systems[neuronset1].particles),
                        len(layers[-1].particle_systems[neuronset2].particles)))

    for i in range(0, len(layers[0].particle_systems[neuronset1].particles)):
        # compute position, uv-coordinates and distance for the pre-synaptic neuron
        pre_p3d, pre_p2d, pre_d = computeMapping(layers[0:(slayer + 1)],
                                                 connections[0:slayer],
                                                 distances[0:slayer],
                                                 layers[0].particle_systems[neuronset1].particles[i].location)
        if pre_p3d is None:
            continue

        for j in range(0, len(layers[-1].particle_systems[neuronset2].particles)):
            # compute position, uv-coordinates and distance for the post-synaptic neuron
            post_p3d, post_p2d, post_d = computeMapping(layers[:(slayer - 1):-1],
                                                        connections[:(slayer - 1):-1],
                                                        distances[:(slayer - 1):-1],
                                                        layers[-1].particle_systems[neuronset2].particles[j].location)

            if post_p3d is None:
                continue

            # determine connectivity probabiltiy and distance values
            conn[i, j] = computeConnectivityProbability(pre_p2d * layers[slayer]['uv_scaling'], post_p2d * layers[slayer]['uv_scaling'], func, args)
            # for euclidean distance
            if distances[slayer - 1] == 0:
                dist[i, j] = pre_d + post_d + (post_p3d[-1] - pre_p3d[-2]).length
            # for normal-uv-distance
            elif distances[slayer - 1] == 1:
                dist[i, j] = pre_d + post_d + (post_p2d - pre_p2d).length * layers[slayer]['uv_scaling']
            # for euclidean-uv-distances
            elif distances[slayer - 1] == 2:
                dist[i, j] = pre_d + post_d + (post_p2d - pre_p2d).length * layers[slayer]['uv_scaling']

    return conn, dist


def printConnections():
    """Print connection pairs"""
    for i, c in enumerate(model.MODEL.connection_indices):
        message = "%d: %s - %s" % (i, model.MODEL.ng_list[c[1]][0],
                                   model.MODEL.ng_list[c[2]][0])

        logger.info(message)


def computeDistance(layer1, layer2, neuronset1, neuronset2, common_layer,
                    connection_matrix):
    """Measure the distance between neurons on the same layer according to the
    connectivity matrix

    :param bpy.types.Object layer1:
    :param bpy.types.Object layer2: layer of pre- and post-synaptic neurons
    :param neuronset1:
    :param str neuronset2: name of the neuronset (particlesystem)
    :param bpy.types.Object common_layer: layer, on which the distances should be measured
    :param numpy.Array connection_matrix: connectivity matrix that determines, which distances
                                          should be measured

    result              matrix of the same structure, like connection_matrix,
                        but with distances
    """
    positions1 = []     # list of uv-positions for the first group
    positions2 = []     # list of uv-positions for the second group

    for p in layer1.particle_systems[neuronset1].particles:
        p2d = map3dPointToUV(common_layer, common_layer, p.location)
        positions1.append(p2d)

    for p in layer2.particle_systems[neuronset2].particles:
        p2d = map3dPointToUV(common_layer, common_layer, p.location)
        positions2.append(p2d)

    result = numpy.zeros(connection_matrix.shape)

    for i in range(len(connection_matrix)):
        for j in range(len(connection_matrix[i])):
            distance = (positions2[connection_matrix[i][j]] - positions1[i]).length
            result[i, j] = distance * common_layer['uv_scaling']

    return result, positions1, positions2


def measureUVs(objects):
    """Return the ratio between real and UV-distance for all edges for all objects in
    objects

    :param objects             : list of objects to compute uv-data for

    Returns:
        uv_data         : list of ratio-vectors
        layer_names     : name of the object
    """
    uv_data = []
    layer_names = []

    for obj in objects:
        if obj.type == 'MESH':
            if any(obj.data.uv_layers):
                _, edges_scaled = computeUVScalingFactor(obj)
                uv_data.append(edges_scaled)
                layer_names.append(obj.name)

    return uv_data, layer_names


def initializeUVs():
    """Compute the UV scaling factor for all layers that have UV-maps"""
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if any(obj.data.uv_layers):
                try:
                    obj['uv_scaling'], _ = computeUVScalingFactor(obj)
                except:
                    logger.error('Could not creaet uv_scaling-factor for ' + obj.name)

            ''' area size of each polygon '''
            p_areas = []

            ''' collect area values for all polygons '''
            for p in obj.data.polygons:
                p_areas.append(p.area)

            # convert everything to numpy
            p_areas = numpy.array(p_areas)
            # compute the cumulative sum
            p_cumsum = p_areas.cumsum()
            # compute the sum of all areas
            p_sum = p_areas.sum()

            obj['area_cumsum'] = p_cumsum
            obj['area_sum'] = p_sum


def returnNeuronGroups():
    """Return a list of neural groups (particle-systems) for the whole model.
    This is used for the NEST import to determine, which neural groups should
    be connected

    """

    r_list = []
    r_dict = {}
    counter = 0

    for obj in bpy.data.objects:
        for p in obj.particle_systems:
            r_list.append([obj.name, p.name, p.settings.count])
            if r_dict.get(obj.name) is None:
                r_dict[obj.name] = {}
            r_dict[obj.name][p.name] = counter
            counter += 1

    return r_list, r_dict

def resetOrigins():
    """Resets the transformations of all objects in the model to avoid false behaviour of mapping functions"""
    active_obj = bpy.context.scene.objects.active   #save active object
    for c in model.MODEL.connections:
        for l in c.layers:
            l.obj.select = True
            bpy.context.scene.objects.active = l.obj
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            l.obj.select = False
    bpy.context.scene.objects.active = active_obj   #restore
    if active_obj:
        active_obj.select = True

def initialize3D():
    """Prepare necessary steps for the computation of connections"""

    SEED = bpy.context.scene.pam_mapping.seed
    model.clearQuadtreeCache()

    logger.info("reset model")
    model.reset()

    logger.info("computing uv-scaling factor")
    initializeUVs()

    logger.info("collecting neuron groups")
    model.MODEL.ng_list, model.MODEL.ng_dict = returnNeuronGroups()

    logger.info("done initalizing")
