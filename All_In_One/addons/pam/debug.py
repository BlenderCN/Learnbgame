from pam import model
from pam import pam
from pam import constants

import bpy
import numpy
import logging

logger = logging.getLogger(__package__)

def getUniqueUVMapErrors():
    """Returns a list of unique connection errors that occur during uv-mapping phase.

    :return: list of failed UV-Mappings
    :rtype: list of exceptions.UVMapError"""
    errors = {}
    for err in model.CONNECTION_ERRORS:
        if str(err) not in errors:
            errors[str(err)] = err
    return list(errors.values())

def showErrorOnUVMap(err):
    """Displays an UVMapping error in an Image panel

    The specified UV Mapping error is displayed in an Image panel and the 2D cursor 
    position is set to the position of the mapping error

    :param err: The Mapping error to be displayed
    :type err: exceptions.UVMapError"""
    bpy.context.scene.objects.active = err.layer
    err.layer.select = True
    bpy.ops.object.mode_set()
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action = 'SELECT')

    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':   #find the UVeditor
            area.spaces.active.cursor_location = err.data   # set cursor location

    print("Displaying error " + str(err))

def debugPreMapping(no_connection):
    """Debugs a specified pre-mapping for unconnected neurons

    Checks all pre-neurons of a connection that do not connect to a different neuron
    using the debug mode of pam.computeMapping()
    :param no_connection: The connection index of the mapping
    :type no_connection: int"""
    rows, cols = numpy.where(model.CONNECTION_RESULTS[no_connection]['c'] == -1)
    neuronIDs = numpy.unique(rows)
    logger.info("Checking pre mapping " + str(model.MODEL.connections[no_connection]))
    if len(neuronIDs):
        logger.info(str(len(neuronIDs)) + " neurons unconnected")
        for neuronID in neuronIDs:
            logger.info("Pre-index: " + str(neuronID))
            debugPreNeuron(no_connection, neuronID)
    else:
        logger.info("No unconnected neurons")

def debugPreNeuron(no_connection, pre_index):
    """Debugs a single neuron on the pre layer of a single mapping

    Tries to map the neuron step by step up to the synapse layer, stopping as soon as it fails to connect.
    Prints information about every step while doing so.

    :param no_connection: The connection index of the mapping
    :type no_connection: int
    :param pre_index: The pre-index of the neuron
    :type pre_index: int"""
    
    con = model.MODEL.connections[no_connection] 
    layers = con.layers
    slayer = con.synaptic_layer_index
    connections = con.mapping_connections
    distances = con.mapping_distances

    for s in range(2, (slayer + 1)):
        pre_p3d, pre_p2d, pre_d = pam.computeMapping(
            layers[0:s],
            connections[0:(s - 1)],
            distances[0:(s - 2)] + [constants.DIS_euclidUV],
            con.pre_layer.getNeuronPosition(pre_index),
            debug=True
        )
        logger.info("Layer: " + layers[s-1].name)
        logger.info("   pre_p3d: " + str(pre_p3d))
        logger.info("   pre_p2d: " + str(pre_p2d))
        logger.info("   pre_d: " + str(pre_d))
        if pre_d is None:
            break
    logger.info("==========================")

def debugPostMapping(no_connection):
    """Debugs a specified post-mapping for unconnected neurons

    Checks all post-neurons of a connection that do not connect to a different neuron
    using the debug mode of pam.computeMapping()
    :param no_connection: The connection index of the mapping
    :type no_connection: int"""

    con = model.MODEL.connections[no_connection] 
    layers = con.layers
    slayer = con.synaptic_layer_index
    connections = con.mapping_connections
    distances = con.mapping_distances

    neuronIDs = []

    logger.info("Checking post mapping " + str(model.MODEL.connections[no_connection]))

    for i in range(0, con.post_layer.neuron_count):
        post_p3d, post_p2d, post_d = pam.computeMapping(layers[:(slayer - 1):-1],
                                                    connections[:(slayer - 1):-1],
                                                    distances[:(slayer - 1):-1],
                                                    con.post_layer.getNeuronPosition(i))
        if post_p3d is None:
            neuronIDs.append(i)
    if len(neuronIDs):
        logger.info(str(len(neuronIDs)) + " neurons unconnected")
    else:
        logger.info("No unconnected neurons")

    for neuronID in neuronIDs:
        logger.info("Post-index: " + str(neuronID))
        debugPostNeuron(no_connection, neuronID)

def debugPostNeuron(no_connection, post_index):
    """Debugs a single neuron on the post layer of a single mapping

    Tries to map the neuron step by step up to the synapse layer, stopping as soon as it fails to connect.
    Prints information about every step while doing so.

    :param no_connection: The connection index of the mapping
    :type no_connection: int
    :param post_index: The post-index of the neuron
    :type post_index: int"""

    con = model.MODEL.connections[no_connection] 
    layers = con.layers
    slayer = con.synaptic_layer_index
    connections = con.mapping_connections
    distances = con.mapping_distances

    for s in range(len(layers) - 1, slayer, -1):
        post_p3d, post_p2d, post_d = pam.computeMapping(layers[:s-2:-1],
                                                        connections[:s-2:-1],
                                                        distances[:s-2:-1],
                                                        con.post_layer.getNeuronPosition(post_index),
                                                        debug = True)
        logger.info("Layer: " + str(s))
        logger.info("   post_p3d: " + str(post_p3d))
        logger.info("   post_p2d: " + str(post_p2d))
        logger.info("   post_d: " + str(post_d))
        if post_d is None:
            break
    logger.info("==========================")