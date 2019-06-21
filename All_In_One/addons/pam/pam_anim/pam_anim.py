import bpy

import math
import random
import heapq
import numpy

from .. import pam_vis
from .. import model
from .. import pam
from .. import mesh
from . import data
from . import anim_spikes
from . import anim_functions
from .helper import *

import traceback
import logging

logger = logging.getLogger(__package__)

# CONSTANTS
DEFAULT_MAT_NAME = "SpikeMaterial"

PATHS_GROUP_NAME = "PATHS"
SPIKE_GROUP_NAME = "SPIKES"

SPIKE_OBJECTS = {}
SPIKE_OBJECTS_PRE = {}
CURVES = {}
CURVES_PRE = {}
TIMING_COLORS = []

class ConnectionCurve:
    """Class for holding connection information for a post connection

    :attribute bpy.types.Object curveObject: The object generated for this curve. 
        May be None if object hasn't been generated.
    :attribute float timeLength: The duration in ms how long a spike needs to 
        get to the end of the curve        
    :attribute int connectionID: The ID of the connection between two neuron groups
    :attribute int sourceNeuronID: The ID of the source neuron in the firing neuron group
    :attribute int targetNeuronID: The ID of the target neuron in the recieving neuron group
    """

    def __init__(self, connectionID, sourceNeuronID, targetNeuronID, timeLength):
        self.curveObject = None
        self.curvePre = None
        self.timeLength = timeLength
        self.connectionID = connectionID
        self.sourceNeuronID = sourceNeuronID
        self.targetNeuronID = targetNeuronID

    def visualize(self):
        """Generates this curve as an object

        This function calls visualizeOneConnection with it's IDs and saves the generated object in curveObject.
        If the pre-curve has not been generated yet, the pre-curve will be generated and this curve will be used 
        for the fork time calculation.
        """
        try:
            self.curveObject = pam_vis.visualizeOneConnectionPost(self.connectionID, self.sourceNeuronID, self.targetNeuronID, 
                bpy.context.scene.pam_visualize.smoothing)

            if self.curvePre.curveObject is None:
                self.curvePre.visualize(self.curveObject)
            
            self.curveObject.name = "curve.%d_%d_%d" % (self.connectionID, self.sourceNeuronID, self.targetNeuronID)
            bpy.data.groups[PATHS_GROUP_NAME].objects.link(self.curveObject)
            
            self.curveObject.data.resolution_u = bpy.context.scene.pam_anim_mesh.path_bevel_resolution
            frameLengthPost = timeToFrames(self.curvePre.timeLength - self.curvePre.post_delay)

            setAnimationSpeed(self.curveObject.data, frameLengthPost)
            self.curveObject.data["timeLength"] = frameLengthPost
        except Exception as e:
            logger.info(traceback.format_exc())
            logger.error("Failed to visualize post connection " + str((self.connectionID, self.sourceNeuronID, self.targetNeuronID)))

class ConnectionCurvePre:
    """Class for holding connection information for a pre connection

    :attribute bpy.types.Object curveObject: The object generated for this curve. 
        May be None if object hasn't been generated.
    :attribute float timeLength: The duration in ms how long a spike needs to 
        get to the end of the curve        
    :attribute int connectionID: The ID of the connection between two neuron groups
    :attribute int sourceNeuronID: The ID of the source neuron in the firing neuron group
    :attribute double post_delay: The delay a post spike has to start with
    """
    def __init__(self, connectionID, sourceNeuronID, timeLength):
        self.curveObject = None
        self.connectionID = connectionID
        self.sourceNeuronID = sourceNeuronID
        self.curves_post = []
        self.timeLength = timeLength

    def visualize(self, post_curve):
        """This visualizes the Pre-connection of a given post-connection. 
        The Post-connection is used to calculate the animation timing and 
        the time the spike forks.
        :param post_curve: The post curve object, to calculate the distance
        :type post_curve: bpy.types.Object or bpy.types.Curve
        """
        
        dist_post = pam_vis.calculatePathLength(post_curve)
        
        try:
            self.curveObject = pam_vis.visualizeOneConnectionPre(self.connectionID, self.sourceNeuronID, 
                bpy.context.scene.pam_visualize.smoothing)
        except Exception as e:
            logger.info(traceback.format_exc())
            logger.error("Failed to visualize pre connection " + str((self.connectionID, self.sourceNeuronID)))
            return

        self.curveObject.name = "curve.%d_%d_pre" % (self.connectionID, self.sourceNeuronID)
        bpy.data.groups[PATHS_GROUP_NAME].objects.link(self.curveObject)
        
        self.curveObject.data.resolution_u = bpy.context.scene.pam_anim_mesh.path_bevel_resolution

        dist_pre = pam_vis.calculatePathLength(self.curveObject)

        fork_percent = dist_pre / (dist_pre + dist_post)
        fork_time = fork_percent * self.timeLength

        frameLengthPre = timeToFrames(fork_time)
        
        self.post_delay = fork_time

        self.curveObject.data["timeLength"] = frameLengthPre
        setAnimationSpeed(self.curveObject.data, frameLengthPre)


class SpikeObject:
    """Class for holding spike information

    :attribute ConnectionCurve curve: The curve object this spike is attatched to
    :attribute bpy.types.Object object: The object generated for this spike.
        May be None if object hasn't been generated
    :attribute float[4] color: The color this spike will have
    :attribute float startTime: The time in ms when this spike has been fired
    :attribute int connectionID: The ID of the connection between two neuron groups
    :attribute int sourceNeuronID: The ID of the source neuron in the firing neuron group
    :attribute int targetNeuronID: The ID of the target neuron in the recieving neuron group
    :attribute int targetNeuronIndex: The index of the target neuron. Useful for maxConns.
    :attribute int timingID: The ID (line in the timing file) of the timing that has fired this neuron
    """
    def __init__(self, connectionID, sourceNeuronID, targetNeuronID, targetNeuronIndex, timingID, curve, curve_pre, startTime):
        self.curve = curve
        self.curve_pre = curve_pre
        self.object = None
        self.color = (1.0, 1.0, 1.0, 1.0)
        self.startTime = startTime
        self.spikeInfo = {}
        self.connectionID = connectionID
        self.sourceNeuronID = sourceNeuronID
        self.targetNeuronID = targetNeuronID
        self.targetNeuronIndex = targetNeuronIndex
        self.timingID = timingID

    def visualizeCurve(self):
        """Visualize the curve if it is not already visualized"""
        if self.curve.curveObject is None:
            self.curve.visualize()

    def getDelay(self):
        """Returns the forking delay for this spike (since it's a post spike)"""
        return self.curve_pre.post_delay

    def visualize(self, meshObject, orientationOptions = {'orientationType': 'NONE'}):
        """Generates an object for this spike

        This function generates a curve object for it's connection if there is none.
        The generated object is saved in self.object.

        :param bpy.types.Object meshObject: The mesh that will be used for this object
        :param dict orientationOptions: Options for orientation:
            orientationType: {'NONE', 'OBJECT', 'FOLLOW'}
            orientationObject: bpy.types.Object, Only used for orientationType OBJECT
        """

        self.visualizeCurve()

        if self.curve.curveObject is None:
            logger.error("No curve object to attatch to for spike " + self.__repr__() + "!")
            return

        obj = bpy.data.objects.new(self.__repr__(), meshObject.data)
        obj.color = self.color

        bpy.data.groups[SPIKE_GROUP_NAME].objects.link(obj)

        bpy.context.scene.objects.link(obj)

        startTime = projectTimeToFrames(self.startTime + self.getDelay())

        constraint = obj.constraints.new(type="FOLLOW_PATH")
        time = self.curve.curveObject.data["timeLength"]
        constraint.offset = startTime / time * 100
        constraint.target = self.curve.curveObject

        startFrame = int(startTime)

        obj.hide = True
        obj.keyframe_insert(data_path="hide", frame=startFrame - 1)
        obj.hide = False
        obj.keyframe_insert(data_path="hide", frame=startFrame)
        obj.hide = True
        obj.keyframe_insert(data_path="hide", frame=math.ceil(startFrame + time))

        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_render", frame=startFrame - 1)
        obj.hide_render = False
        obj.keyframe_insert(data_path="hide_render", frame=startFrame)
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_render", frame=math.ceil(startFrame + time))

        if(orientationOptions.orientationType == 'FOLLOW'):
            constraint.use_curve_follow = True

        if(orientationOptions.orientationType == 'OBJECT'):
            orientConstraint = obj.constraints.new(type="TRACK_TO")
            orientConstraint.target = bpy.data.objects[orientationOptions.orientationObject]
            orientConstraint.track_axis = "TRACK_Z"
            orientConstraint.up_axis = "UP_Y"

        self.object = obj

    def __repr__(self):
        return "Spike" + "_" + str(self.timingID) + "_" + str(self.connectionID) + "_" + str(self.sourceNeuronID) + "_" + str(self.targetNeuronID)

class SpikeObjectPre(SpikeObject):
    def __init__(self, connectionID, sourceNeuronID, timingID, curve, startTime):
        self.curve = curve
        self.object = None
        self.color = (1.0, 1.0, 1.0, 1.0)
        self.startTime = startTime
        self.spikeInfo = {}
        self.connectionID = connectionID
        self.sourceNeuronID = sourceNeuronID
        self.timingID = timingID

    def visualizeCurve(self):
        pass

    def getDelay(self):
        return 0

    def __repr__(self):
        return "Spike_Pre_" + str(self.timingID) + "_" + str(self.connectionID) + "_" + str(self.sourceNeuronID)


def simulate():
    """Simulates all timings

    Calls simulateTiming for every timing in data.TIMINGS
    data.readSimulationData() should be called before this.
    """
    t = data.TIMINGS

    no_timings = len(t)

    for timingID, timing in enumerate(t):
        logger.info("Simulating: " + str(timingID) + "/" + str(no_timings))

        simulateTiming(timingID)

def simulateTiming(timingID):
    """Simulates a timing with a geven timingID

    Calls simulateConnection() with all outgoing connections for the neuron group

    :param int timingID: The ID (line in timing file) of the timing"""

    timing = data.TIMINGS[timingID]

    neuronGroupID = timing[0]
    neuronID = timing[1]
    fireTime = timing[2]

    connectionIDs = [x for x in model.MODEL.connection_indices if x[1] == neuronGroupID]

    c = model.CONNECTION_RESULTS

    for connectionID in connectionIDs:
        # Pre synapse here
        # Connection curves first?

        curve_key = (connectionID[0], neuronID)
        if curve_key not in CURVES_PRE:
            curve_pre = ConnectionCurvePre(connectionID[0], neuronID, numpy.mean(data.DELAYS[connectionID[0]][neuronID]))
            CURVES_PRE[curve_key] = curve_pre
        else:
            curve_pre = CURVES_PRE[curve_key]
        at_least_one = False
        for index, i in enumerate(c[connectionID[0]]['c'][neuronID][:data.noAvailableConnections]):
            if i == -1 or data.DELAYS[connectionID[0]][neuronID][index] == 0:
                continue
            simulateConnection(connectionID[0], neuronID, index, timingID)
            at_least_one = True

        if at_least_one:
            # distance = data.DELAYS[connectionID][neuronID][targetNeuronIndex]
            SPIKE_OBJECTS_PRE[(curve_key, timingID)] = SpikeObjectPre(connectionID[0], neuronID, timingID, curve_pre, fireTime)


def simulateConnection(connectionID, sourceNeuronID, targetNeuronIndex, timingID):
    """Simulates a single connection at a specific timing

    Creates curve object (if not already generated) and spike object for a specific
    connection and a specific timing

    Objects are saved in CURVES and SPIKE_OBJECTS
    
    :attribute int connectionID: The ID of the connection between two neuron groups
    :attribute int sourceNeuronID: The ID of the source neuron in the firing neuron group
    :attribute int targetNeuronID: The ID of the target neuron in the recieving neuron group
    :attribute int targetNeuronIndex: The index of the target neuron.
    :attribute int timingID: The ID (line in the timing file) of the timing that has fired

    """
    global SPIKE_OBJECTS
    targetNeuronID = model.CONNECTION_RESULTS[connectionID]['c'][sourceNeuronID][targetNeuronIndex]
    curveKey = (connectionID, sourceNeuronID, targetNeuronID)
    if curveKey in CURVES:
        curve = CURVES[curveKey]
    else:
        distance = data.DELAYS[connectionID][sourceNeuronID][targetNeuronIndex]
        curve = ConnectionCurve(connectionID, sourceNeuronID, targetNeuronID, distance)
        CURVES[curveKey] = curve

    curve_key_pre = (connectionID, sourceNeuronID)
    curve_pre = CURVES_PRE[curve_key_pre]

    curve_pre.curves_post.append(curve)
    curve.curvePre = curve_pre

    fireTime = data.TIMINGS[timingID][2]
    SPIKE_OBJECTS[(curveKey, timingID)] = SpikeObject(connectionID, sourceNeuronID, targetNeuronID, targetNeuronIndex, timingID, curve, curve_pre, fireTime)

def simulateColorsByLayer(source = "MATERIAL"):
    """Gives each spike the color of its source layer

    :param {"OBJECT", "MATERIAL", "MATERIAL_CYCLES"} source: From where the color should be taken, object color, material diffuse color or cycles diffuse color"""

    global TIMING_COLORS
    TIMING_COLORS = [[1.0, 1.0, 1.0]] * len(data.TIMINGS)

    groupColors = []

    for neuronGroup in model.MODEL.ng_list:
        if source == "MATERIAL_CYCLES":
            mat = bpy.context.scene.objects[neuronGroup[0]].active_material
            if mat:
                diffuseNode = mat.node_tree.nodes.get("Diffuse BSDF")
                if diffuseNode:
                    values = diffuseNode.inputs[0].default_value
                    groupColors.append((values[0], values[1], values[2], values[3]))
                else:
                    source = "MATERIAL"
            else:
                source = "OBJECT"
        
        if source == "MATERIAL":
            mat = bpy.context.scene.objects[neuronGroup[0]]
            if mat:
                color = mat.active_material.diffuse_color
                groupColors.append((color.r, color.g, color.b, 1.0))
            else:
                source = "OBJECT"
                
        if source == "OBJECT":
            groupColors.append(bpy.context.scene.objects[neuronGroup[0]].color)

    for spike in SPIKE_OBJECTS.values():
        connectionID = spike.connectionID
        neuronGroupID = model.MODEL.connection_indices[connectionID][1]
        neuronGroupName = model.MODEL.ng_list[neuronGroupID][0]
        
        groupColor = groupColors[neuronGroupID]
        
        spike.color = groupColor
        if spike.object is not None:
            spike.object.color = groupColor
        TIMING_COLORS[spike.timingID] = groupColor

def simulateColors(labelController = None):
    """Simulates colors for simulated spikes

    :param function decay_func: Function used for calculating decay at a neuron
    :param function initialLabelsFunc: Function for getting the initial labels for
        neurons that have no spiking information
    :param function mixLabelsFunc: Function for calculating the mixing of labels when a spike 
        hits a neuron with color information
    :param function labelToColorFunc: Function for generating color values from the labels
    """

    if labelController == None:
        labelController = anim_functions.labelControllerDict['HSVLabelController']

    t = data.TIMINGS
    d = data.DELAYS
    c = model.CONNECTION_RESULTS

    neuronValues = {}
    neuronUpdateQueue = []

    global TIMING_COLORS
    TIMING_COLORS = [[1.0, 1.0, 1.0]] * len(t)

    for timingID, timing in enumerate(t):
        neuronID = timing[1]
        neuronGroupID = timing[0]
        fireTime = timing[2]

        connectionIDs = [x for x in model.MODEL.connection_indices if x[1] == neuronGroupID]

        # Update the color values of all neurons with queued updates
        poppedValues = getQueueValues(neuronUpdateQueue, fireTime)
        for elem in poppedValues:
            updateTime = elem[0]
            key = (elem[1], elem[2])
            newLayerValues = elem[3]

            # If the key already has values, we have to calculate the decay of the values and then mix them with the incoming values
            if key in neuronValues:
                oldLayerValues = neuronValues[key][0]
                lastUpdateTime = neuronValues[key][1]

                oldLayerValuesDecay = labelController.decay(oldLayerValues, updateTime - lastUpdateTime)
                updatedLayerValues = labelController.mixLabels(oldLayerValuesDecay, newLayerValues)

                neuronValues[key] = (updatedLayerValues, updateTime)
            # If not, we don't need to mix the colors together, as this would just darken the color
            else:
                neuronValues[key] = (newLayerValues, updateTime)

        if (neuronGroupID, neuronID) in neuronValues:
            # Update this neuron
            layerValues = neuronValues[(neuronGroupID, neuronID)][0]
            lastUpdateTime = neuronValues[(neuronGroupID, neuronID)][1]
            layerValuesDecay = labelController.decay(layerValues, fireTime - lastUpdateTime)

            # Now that the neuron has fired, its values go back down to zero
            del(neuronValues[(neuronGroupID, neuronID)])

        else:
            layerValuesDecay = labelController.getInitialLabel(neuronGroupID, neuronID, model.MODEL.ng_list)

        color = labelController.labelToColor(layerValuesDecay, neuronID, neuronGroupID, model.MODEL.ng_list)
        TIMING_COLORS[timingID] = color
        anim_spikes.setNeuronColorKeyframe(neuronID, neuronGroupID, fireTime, color)
        for connectionID in connectionIDs:
            at_least_one = False
            for index, i in enumerate(c[connectionID[0]]["c"][neuronID][:data.noAvailableConnections]):
                if i == -1 or ((connectionID[0], neuronID, i), timingID) not in SPIKE_OBJECTS:
                    continue
                obj = SPIKE_OBJECTS[((connectionID[0], neuronID, i), timingID)]
                if obj.object:
                    obj.object.color = color
                    obj.object['spiking_labels'] = str(layerValuesDecay)
                at_least_one = True

                # Queue an update to the connected neuron
                updateTime = fireTime + d[connectionID[0]][neuronID][index]
                heapq.heappush(neuronUpdateQueue, (updateTime, connectionID[2], i, layerValuesDecay))

            if at_least_one:
                obj = SPIKE_OBJECTS_PRE[((connectionID[0], neuronID), timingID)]
                if obj.object:
                    obj.object.color = color
                    obj.object['spiking_labels'] = str(layerValuesDecay)


def simulateColorsByMask():
    """Paints all spikes originating from a neuron inside of a mask in a different color

    Collects settings from the gui (Mask object, inside mask color, outside mask color)."""
    maskObject = bpy.data.objects[bpy.context.scene.pam_anim_material.maskObject]
    insideMaskColor = bpy.context.scene.pam_anim_material.insideMaskColor
    outsideMaskColor = bpy.context.scene.pam_anim_material.outsideMaskColor

    global TIMING_COLORS
    TIMING_COLORS = [[1.0, 1.0, 1.0]] * len(data.TIMINGS)

    for spike in SPIKE_OBJECTS.values():
        neuron_group = model.MODEL.ng_list[model.MODEL.connection_indices[spike.connectionID][1]]
        layer_name = neuron_group[0]
        particle_system_name = neuron_group[1]
        particle = bpy.data.objects[layer_name].particle_systems[particle_system_name].particles[spike.sourceNeuronID]
        if spike.object is not None:
            if mesh.checkPointInObject(maskObject, particle.location):
                spike.color = insideMaskColor
                spike.object.color = insideMaskColor
            else:
                spike.color = outsideMaskColor
                spike.object.color = outsideMaskColor
            TIMING_COLORS[spike.timingID] = spike.color

def generateAllTimings(frameStart = 0, frameEnd = 250, maxConns = 0, showPercent = 100.0, layerFilter = None):
    """Generates objects for all spikes matching criteria

    :param int frameStart: The frame before which no spikes will be generated
    :param int frameEnd: The frame after which no spikes will be generated
    :param int maxConns: Maximum number of spikes one neuron can generate. 0 for no restrictions.
    :param float showPercent: Probability that a given spike will be generated (Must be between 0.0 and 100.0)
    :param list layerFilter: List of layer indeces that are allowed to generate spikes. None for no restrictions
    """
    connectionIndicesFilter = None
    if layerFilter is not None:
        connectionIndicesFilter = [False]*len(model.MODEL.connection_indices)
        for connection in model.MODEL.connection_indices:
            connectionIndicesFilter[connection[0]] = connection[1] in layerFilter

    # This takes some time, so here's a loading bar!
    wm = bpy.context.window_manager

    total = len(SPIKE_OBJECTS)
    i = 0

    logger.info("Generating " + str(total) + " objects")

    wm.progress_begin(0, 100)

    for (key, spike) in SPIKE_OBJECTS.items():
        i += 1

        wm.progress_update(int(i / total * 100))

        startFrame = projectTimeToFrames(spike.startTime)

        if startFrame < frameStart or startFrame > frameEnd:
            continue

        if maxConns > 0 and getattr(spike, "targetNeuronIndex", 0) > maxConns:
            continue

        if connectionIndicesFilter is not None and not connectionIndicesFilter[spike.connectionID]:
            continue

        random.seed(key)
        if random.random() > showPercent / 100.0:
            continue

        logger.info("Generating spike " + str(i) + "/" + str(total) + ": " + str(spike))
        spike.visualize(bpy.data.objects[bpy.context.scene.pam_anim_mesh.mesh], bpy.context.scene.pam_anim_mesh)
        if SPIKE_OBJECTS_PRE[(key[0][0], key[0][1]), key[1]].object is None:
            SPIKE_OBJECTS_PRE[(key[0][0], key[0][1]), key[1]].visualize(bpy.data.objects[bpy.context.scene.pam_anim_mesh.mesh], bpy.context.scene.pam_anim_mesh)


    wm.progress_end()

# TODO(SK): Rephrase docstring, add a `.. note::` or `.. warning::`
def clearVisualization():
    """Clears all created objects by the animation
    The objects are saved in the specified groups and all
    objects in these groups will be deleted!"""

    anim_spikes.deleteNeurons()
    if SPIKE_GROUP_NAME in bpy.data.groups:
        neuronObjects = bpy.data.groups[SPIKE_GROUP_NAME].objects
        for obj in neuronObjects:
            bpy.context.scene.objects.unlink(obj)
            bpy.data.objects.remove(obj)

    if PATHS_GROUP_NAME in bpy.data.groups:
        paths = bpy.data.groups[PATHS_GROUP_NAME].objects
        for curve in paths:
            bpy.context.scene.objects.unlink(curve)
            data = curve.data
            bpy.data.objects.remove(curve)
            bpy.data.curves.remove(data)

    pam_vis.vis_objects = 0

    global CURVES
    global CURVES_PRE
    global SPIKE_OBJECTS
    global SPIKE_OBJECTS_PRE
    CURVES.clear()
    CURVES_PRE.clear()
    SPIKE_OBJECTS.clear()
    SPIKE_OBJECTS_PRE.clear()

def setAnimationSpeed(curve, animationSpeed):
    """Set the animation speed of a Bezier-curve

    Sets a curves animation speed to the given speed with a linear interpolation. Any object bound to this
    curve with a Follow Curve constraint will have completed its animation along the curve in the given time.

    :param bpy.types.Curve curve: The curve
    :param float animationSpeed:  The animation speed in frames
    """
    curve.eval_time = 0
    curve.keyframe_insert(data_path="eval_time", frame=0)
    curve.eval_time = 100 * 100 / animationSpeed
    curve.keyframe_insert(data_path="eval_time", frame=100)

    # Set all the keyframes to linear interpolation to ensure a constant speed along the curve
    for key in curve.animation_data.action.fcurves[0].keyframe_points:
        key.interpolation = 'LINEAR'
    # Set the extrapolation of the curve to linear (This is important, without it, neurons with an offset start would not be animated)
    curve.animation_data.action.fcurves[0].extrapolation = 'LINEAR'

def decayFunc(layerValues, delta, decayFunc):
    """Calculates the decay of all values in a dictionary

    The given decay function is used on every value in the given dictionary. 
    The values cannot become negative and are clamped to zero. The keys 
    remain unchanged.

    :param dict layerValues:   The given dictionary
    :param float delta:        The time passed onto the decay function
    :param function decayFunc: The function used to calculate the decay"""

    newValues = {}
    for key in layerValues:
        newValues[key] = decayFunc(layerValues[key], delta)
        if newValues[key] < 0:
            newValues[key] = 0
    return newValues

def createDefaultMaterial():
    """Create the default material.

    Creates a default material with a white diffuse color and the use object color
    property set to True.
    The name for this material is defined in the global variable DEFAULT_MAT_NAME"""
    options = bpy.context.scene.pam_anim_material
    if DEFAULT_MAT_NAME not in bpy.data.materials:
        mat = bpy.data.materials.new(DEFAULT_MAT_NAME)
        mat.diffuse_color = (1.0, 1.0, 1.0)
        mat.use_object_color = True
        options.material = mat.name
    else:
        mat = bpy.data.materials
    return mat

def copyModifiers(source_object, target_objects):
    """Copies all modifiers from source_object to all objects in target_objects"""
    for obj in target_objects:
        for mSrc in source_object.modifiers:
            mDst = obj.modifiers.get(mSrc.name, None)
            if not mDst:
                mDst = obj.modifiers.new(mSrc.name, mSrc.type)

            # collect names of writable properties
            properties = [p.identifier for p in mSrc.bl_rna.properties
                          if not p.is_readonly]

            # copy those properties
            for prop in properties:
                setattr(mDst, prop, getattr(mSrc, prop))

def copyDrivers(source_object, target_objects):
    """Copies all drivers from source_object to all objects in target_objects"""
    for obj in target_objects:
        if not source_object.animation_data is None:
            for dr in source_object.animation_data.drivers:
                copyDriver(dr, obj, source_object, obj)
        if not source_object.data.animation_data is None:
            for dr in source_object.data.animation_data.drivers:
                copyDriver(dr, obj.data, source_object, obj)

def copyDriver(src, tgt, replace_src = "", replace_tgt = ""):
    """Copies driver src to object tgt
    Replaces any values in variables that equal replace_src with replace_tgt"""
    if tgt.animation_data is None:
        tgt.animation_data_create()
    # if isArrayPath(src.data_path):
    #     d2 = tgt.driver_add(src.data_path, src.array_index)
    # else:
    d2 = tgt.driver_add(src.data_path)

    d2.driver.expression = src.driver.expression
    for v1 in src.driver.variables:
        v2 = d2.driver.variables.new()
        v2.type = v1.type
        v2.name = v1.name
        for i, target in enumerate(v1.targets):
            v2.targets[i].data_path = target.data_path
            # v2.targets[i].id_type = target.id_type
            v2.targets[i].id = target.id
            if target.id == replace_src:
                v2.targets[i].id = replace_tgt
        # except:
        #     print("Could not copy driver varible, %s %s"%(src, v1) )

# TODO(SK): Rephrase docstring
# TODO(SK): max 80 characters per line
def getUsedNeuronGroups():
    """Checks in pam.model which neuron groups are actually be used and return
    the indices of those neurongroups. This routine is used by visualize() in order
    to reduce the number of neurongroups for which neurons should be created """
    inds = []
    for c in model.MODEL.connection_indices:
        inds.append(c[1])
        inds.append(c[2])
    return numpy.unique(inds)

def animateSpikePropagation():
    """Generates spike propagation objects from simulated data

    Collects all information from the GUI, calls generateAllTimings() 
    and then adds the generated objects to their respective groups"""

    # Create a default material if needed
    if bpy.context.scene.pam_anim_material.materialOption == "DEFAULT":
        createDefaultMaterial()
        material = bpy.data.materials[DEFAULT_MAT_NAME]
    else:
        material = bpy.data.materials[bpy.context.scene.pam_anim_material.material]
    
    frameStart = bpy.context.scene.pam_anim_animation.startFrame
    frameEnd = bpy.context.scene.pam_anim_animation.endFrame
    showPercent = bpy.context.scene.pam_anim_animation.showPercent
    maxConns = bpy.context.scene.pam_anim_animation.connNumber

    # Create groups if they do not already exist
    if PATHS_GROUP_NAME not in bpy.data.groups:
        bpy.data.groups.new(PATHS_GROUP_NAME)
    if SPIKE_GROUP_NAME not in bpy.data.groups:
        bpy.data.groups.new(SPIKE_GROUP_NAME)

    logger.info('Visualize spike propagation')
    generateAllTimings(frameStart = frameStart, frameEnd = frameEnd, maxConns = maxConns, showPercent = showPercent)
    
    # Apply material to paths
    if bpy.context.scene.pam_anim_material.pathMaterial in bpy.data.materials:
        for curveObj in CURVES.values():
            if curveObj.curveObject:
                curveObj.curveObject.active_material = bpy.data.materials[bpy.context.scene.pam_anim_material.pathMaterial]

    # Copy modifiers and drivers
    copyModifiers(bpy.data.objects[bpy.context.scene.pam_anim_mesh.mesh], [spike.object for spike in SPIKE_OBJECTS.values() if spike.object is not None])
    copyDrivers(bpy.data.objects[bpy.context.scene.pam_anim_mesh.mesh], [spike.object for spike in SPIKE_OBJECTS.values() if spike.object is not None])

    # Apply material to mesh
    mesh = bpy.data.objects[bpy.context.scene.pam_anim_mesh.mesh].data
    mesh.materials.clear()
    mesh.materials.append(material)

def animateNeuronSpiking():
    """Generates neuron spiking using anim_spikes.py

    Collects inforamtion for neuron spiking from the GUI and generates all objects.
    Also animates the spikes."""
    logger.info("Create neurons")
    neuron_object = bpy.data.objects[bpy.context.scene.pam_anim_mesh.neuron_object]
    ng_inds = getUsedNeuronGroups()
    for ind in ng_inds:
        logger.info("Generate neurons for ng " + str(ind))
        anim_spikes.generateLayerNeurons(bpy.data.objects[model.MODEL.ng_list[ind][0]], model.MODEL.ng_list[ind][1], neuron_object)
    logger.info("Create spike animation for neurons")
    anim_spikes.animNeuronSpiking(anim_spikes.animNeuronScaling)

def colorizeAnimation():
    """Gives the spiking animation its color

    Collects information for colorization from the GUI and chooses 
    the appropiate function for colorizing spikes"""

    simulateColors(anim_functions.labelControllerDict[bpy.context.scene.pam_anim_simulation])

class ClearPamAnimOperator(bpy.types.Operator):
    """Clear Animation"""
    bl_idname = "pam_anim.clear_pamanim"
    bl_label = "Clear Animation"
    bl_description = "Deletes the Spike-Animation"

    def execute(self, context):
        clearVisualization()
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class RecolorSpikesOperator(bpy.types.Operator):
    """Recolorize the already generated spikes"""
    bl_idname = "pam_anim.recolor_spikes"
    bl_label = "Recolor spikes"
    bl_description = "Recolors the already generated spikes"

    def execute(self, context):
        colorizeAnimation()
        return {'FINISHED'}

class ReadSimulationData(bpy.types.Operator):
    """Operator for reading simulation data in data.py"""
    bl_idname = "pam_anim.read_simulation_data"
    bl_label = "Read simulation data"
    bl_description = "Read simulation data from zip"

    def execute(self, context):
        data.readSimulationData(bpy.context.scene.pam_anim_data.simulationData)
        return {'FINISHED'}

class GenerateOperator(bpy.types.Operator):
    """Generates connections between neuron groups and objects representing the spiking activity.

    Executing this operator does some prep work, loads the model and then calls the visualize function.

    For this, the PAM model, the model data and the simulation data need to be provided."""

    bl_idname = "pam_anim.generate"
    bl_label = "Generate"
    bl_description = "Generates the animation"

    @classmethod
    def poll(cls, context):

        # Check if a valid mesh has been selected
        if context.scene.pam_anim_mesh.mesh not in bpy.data.objects:
            return False

        # Check if a model is loaded into pam
        if not model.MODEL.ng_list:
            return False

        # Check if either spikes or paths are to be animated (would generate nothing if not active)
        if not (context.scene.pam_anim_mesh.animSpikes or context.scene.pam_anim_mesh.animPaths):
            return False

        # Return True if all data is accessible
        return True

    def execute(self, context):
        # Clear old objects if available
        clearVisualization()

        # Read data from files
        logger.info('Read spike-data')
        data.readSimulationData(bpy.context.scene.pam_anim_data.simulationData)
        logger.info('Prepare Visualization')

        if bpy.context.scene.pam_anim_mesh.animPaths:

            # Create the visualization
            logger.info("Simulate spike propagation")
            simulate()
            logger.info("Generating spike propagation")
            animateSpikePropagation()

        # Animate spiking if option is selected
        if bpy.context.scene.pam_anim_mesh.animSpikes is True:
            logger.info("Generating neuron spiking")
            animateNeuronSpiking()

        # Colorize spikes:
        if bpy.context.scene.pam_anim_material.simulate_colors is True:
            logger.info("Colorizing animation")
            colorizeAnimation()
        
        logger.info("Visualization done")
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class GenerateNeuronSpikingTexture(bpy.types.Operator):
    bl_idname = "pam_anim.generate_spiking_texture"
    bl_label = "Generate spiking texture"
    bl_description = "Generates a spiking activity texture, time on the x-axis, neuron_id on the y-axis"

    def execute(self, context):
        active_obj = bpy.context.active_object
        if active_obj.name not in model.MODEL.ng_dict:
            logger.info("Please select a pre- or post-synaptic layer, for which the spiking texture should be generated")
            return {'CANCELLED'}
        data.readSimulationData(bpy.context.scene.pam_anim_data.simulationData)
        layer_id = model.NG_DICT[active_obj.name][active_obj.particle_systems[0].name]

        colors = None
        if bpy.context.scene.pam_anim_material.colorizingMethod != 'NONE': # Using color simulation
            simulate()
            colorizeAnimation()
            global TIMING_COLORS
            colors = TIMING_COLORS

        anim_spikes.generateSpikingTexture(layer_id, bpy.context.scene.pam_anim_mesh.spikeFadeout, colors)
        return {'FINISHED'}

def register():
    """Registers the operators"""
    # Custom property for the length of a curve for easy accessibility
    bpy.types.Curve.timeLength = bpy.props.FloatProperty()
    bpy.utils.register_class(GenerateOperator)
    bpy.utils.register_class(ClearPamAnimOperator)
    bpy.utils.register_class(RecolorSpikesOperator)
    bpy.utils.register_class(ReadSimulationData)
    bpy.utils.register_class(GenerateNeuronSpikingTexture)
    anim_functions.register()

def unregister():
    """Unregisters the operators"""
    bpy.utils.unregister_class(GenerateOperator)
    bpy.utils.unregister_class(ClearPamAnimOperator)
    bpy.utils.unregister_class(RecolorSpikesOperator)
    bpy.utils.unregister_class(ReadSimulationData)
    bpy.utils.unregister_class(GenerateNeuronSpikingTexture)
    anim_functions.unregister()
