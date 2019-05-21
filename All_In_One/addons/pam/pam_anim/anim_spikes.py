import logging

import csv
import bpy

from pam import model
from . import data
from . import helper

logger = logging.getLogger(__package__)

NEURON_GROUP_NAME = "NEURONS"
NEURON_SPIKES = {}

class NeuronSpike():
    def __init__(self, neuronID, neuronGroupID, position):
        self.neuronID = neuronID
        self.neuronGroupID = neuronGroupID
        self.position = position
        self.fireTimes = []
        self.color = [1.0, 1.0, 1.0, 1.0]

# TODO(SK): Missing docstring
def readSpikeData(filename):
    """Read spike-data from a csv-file and returns them as list"""
    file = open(filename, 'r')

    reader = csv.reader(file, delimiter=";")
    data = [row for row in reader]

    file.close()
    return data


# TODO(SK): Fill in docstring parameters/return values
def generateLayerNeurons(layer, particle_system, obj, object_color=[],
                         indices=-1):
    """Generates for each particle (neuron) a cone with appropriate naming"""
    # generate first mesh
    i = 0
    p = layer.particle_systems[particle_system].particles[0]

    if indices == -1:
        particles = layer.particle_systems[particle_system].particles
    else:
        particles = layer.particle_systems[particle_system].particles[indices[0]:indices[1]]

    # generates linked duplicates of this mesh
    for i, p in enumerate(particles):
        name = 'n' + '_' + layer.name + '_' + particle_system + '_' + '%05d' % (i)
        dupli = bpy.data.objects.new(name, obj.data)
        bpy.context.scene.objects.link(dupli)
        dupli.location = p.location

        # Add neuron to group
        if NEURON_GROUP_NAME not in bpy.data.groups:
            bpy.data.groups.new(NEURON_GROUP_NAME)

        bpy.data.groups[NEURON_GROUP_NAME].objects.link(dupli)

        if object_color:
            dupli.color = object_color[i]

        elif bpy.context.scene.pam_anim_mesh.spikeUseLayerColor:
            dupli.color = layer.color

        else:
            dupli.color = bpy.context.scene.pam_anim_mesh.spikeColor


# TODO(SK): Missing docstring
def generateNetworkNeurons(obj):
    for neurongroup in model.MODEL.ng_list:
        layer = bpy.data.objects[neurongroup[0]]
        particle_system = neurongroup[1]
        generateLayerNeurons(layer, particle_system, obj)


# TODO(SK): Missing docstring
def animNeuronSpiking(func):
    timings = data.TIMINGS
    neuronGroups = model.MODEL.ng_list

    no_timings = len(timings)

    logger.info('Animate spiking data')
    for i, (neuronGroupID, neuronIDinGroup, fireTime) in enumerate(timings):
        logger.info(str(i) + "/" + str(no_timings))
        layer_name = neuronGroups[neuronGroupID][0] + '_' + neuronGroups[neuronGroupID][1] + '_%05d' % (neuronIDinGroup)
        frame = int(helper.projectTimeToFrames(fireTime))
        func(layer_name, neuronIDinGroup, frame)

def generateSpikingTexture(layer_id, fadeoutFrames, colors = None):
    timings = data.TIMINGS
    neuronGroups = model.MODEL.ng_list
    layer = neuronGroups[layer_id]
    neuron_count = layer[2]
    frames = bpy.context.scene.pam_anim_animation.endFrame
    image = bpy.data.images.new(name = layer[0] + "_spikeTexture",
        width = frames, 
        height = neuron_count,
        alpha = False)
    fade = [0.0, 0.0, 0.0, 1.0] * fadeoutFrames
    for fadeStep in range(fadeoutFrames):
        fadeAmount = 1 - fadeStep / fadeoutFrames
        fade[fadeStep*4:(fadeStep+1)*4] = [fadeAmount, fadeAmount, fadeAmount, 1.0]

    if colors is not None and len(colors) == len(timings):
        for i, (neuronGroupID, neuronIDinGroup, fireTime) in enumerate(timings):
            if layer_id == neuronGroupID and fireTime < bpy.context.scene.pam_anim_animation.endTime:
                frame = int(helper.projectTimeToFrames(fireTime))
                tex_pos = neuronIDinGroup * frames + frame
                
                color = [colors[i][0], colors[i][1], colors[i][2], 1.0]
                image.pixels[tex_pos * 4: (tex_pos + 1) * 4] = color
                
                # Avoid drawing fade to next line or out of bounds
                fadeEnd = min(fadeoutFrames, frames - frame - 1)
                colorFade = [fade[f] * color[f % 4] for f in range(len(fade))]
                
                image.pixels[(tex_pos + 1) * 4: (tex_pos + fadeEnd + 1) * 4] = colorFade[:fadeEnd*4]
    else:
        for i, (neuronGroupID, neuronIDinGroup, fireTime) in enumerate(timings):
            if layer_id == neuronGroupID and fireTime < bpy.context.scene.pam_anim_animation.endTime:
                frame = int(helper.projectTimeToFrames(fireTime))
                tex_pos = neuronIDinGroup * frames + frame
                image.pixels[tex_pos * 4: (tex_pos + 1) * 4] = [1.0, 1.0, 1.0, 1.0]
                
                # Avoid drawing fade to next line or out of bounds
                fadeEnd = min(fadeoutFrames, frames - frame - 1)
                image.pixels[(tex_pos + 1) * 4: (tex_pos + fadeEnd + 1) * 4] = fade[:fadeEnd*4]
    # Pack image so its preserved after saving
    image.pack(as_png = True)

# TODO(SK): Fill in docstring parameters/return values
def animNeuronScaling(layer_name, n_id, frame):
    """Animate neuron spiking for a given neuron defined by
    layer_name, neuron-id and a given frame"""
    neuron = bpy.data.objects['n_' + layer_name]

    # define the animation
    animSpikeScale = bpy.context.scene.pam_anim_mesh.spikeScale
    animSpikeFadeout = bpy.context.scene.pam_anim_mesh.spikeFadeout

    neuron.keyframe_insert(data_path = 'scale', frame=frame - 1)

    neuron.scale = (animSpikeScale, animSpikeScale, animSpikeScale)
    neuron.keyframe_insert(data_path = 'scale', frame=frame)

    neuron.scale = (1.0, 1.0, 1.0)
    neuron.keyframe_insert(data_path = 'scale', frame=frame + animSpikeFadeout)

def setNeuronColor(neuronID, neuronGroupID, color):
    layer_name = model.MODEL.ng_list[neuronGroupID][0]
    neuron_name = 'n_' + layer_name + '_%05d' % (neuronID)
    if neuron_name in bpy.data.objects:
        neuron = bpy.data.objects[neuron_name]
        neuron.color = color

def setNeuronColorKeyframe(neuronID, neuronGroupID, fireTime, color):
    layer_name = model.MODEL.ng_list[neuronGroupID][0]
    neuron_name = 'n_' + layer_name + "_" + model.MODEL.ng_list[neuronGroupID][1]+ '_%05d' % (neuronID)
    if neuron_name in bpy.data.objects:
        frame = int(helper.projectTimeToFrames(fireTime))
        neuron = bpy.data.objects[neuron_name]
        neuron.keyframe_insert(data_path = 'color', frame = frame - 1)
        neuron.color = color
        neuron.keyframe_insert(data_path = 'color', frame = frame)
    else:
        logger.info("No neuron spiking object found for " + neuron_name)

# TODO(SK): Rephrase docstring, purpose?
def deleteNeurons():
    """Delete all objects in the group specified in NEURON_GROUP_NAME"""
    if NEURON_GROUP_NAME in bpy.data.groups:
        for obj in bpy.data.groups[NEURON_GROUP_NAME].objects:
            bpy.context.scene.objects.unlink(obj)
            bpy.data.objects.remove(obj)
