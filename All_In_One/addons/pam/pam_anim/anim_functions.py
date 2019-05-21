import bpy

import numpy
from .. import pam
from .. import mesh

from collections import OrderedDict

labelControllerDict = OrderedDict()

def addLabelController(labelController):
    labelControllerDict[labelController.identifier] = labelController
    bpy.types.Scene.pam_anim_simulation = bpy.props.EnumProperty(name = 'Simulation type', 
        items = [(c.identifier, c.name, c.description) for c in reversed(list(labelControllerDict.values()))],
        default = 'LabelController')
    
    if labelController.properties:
        try:
            bpy.utils.register_class(labelController.properties)
        except ValueError:
            pass
        setattr(bpy.types.Scene, 'pam_anim_simulation_' + labelController.identifier + '_props', bpy.props.PointerProperty(type=labelController.properties))

class LabelController():
    """Controls how the labels are changing during the animation.
    The animation can be modified by overriding the four main functions of 
    this class or one of its subclasses.

    This base class creates a blue label for even neuron indices and a red
    label for uneven neuron indices. The rgb-values are then mixed together
    """

    identifier = 'LabelController'
    name = 'RGB'
    description = 'Creates random red and blue spikes and mixes them using RGB'

    properties = None

    def __init__(self, tau = 20):
        self.tau = tau

    def draw(self, layout, context):
        # props = self.getProps(context)
        pass

    def getProps(self, context):
        return getattr(context.scene, 'pam_anim_simulation_' + self.identifier + '_props')

    def mixLabels(self, layerValue1, layerValue2):
        """Function that is called when a spike hits a neuron and the two 
        labels need to be mixed together
        :param dict layerValues1: label of the given neuron
        :param dict layerValues2: label for the incoming spike
        :return: mixed colors
        :rtype: dict
        """
        newValue = {"blue": 0.0, "red": 0.0, "green": 0.0}

        newValue["blue"] = (layerValue1["blue"] + layerValue2["blue"]) / 2
        newValue["red"] = (layerValue1["red"] + layerValue2["red"]) / 2
        newValue["green"] = (layerValue1["green"] + layerValue2["green"]) / 2

        return newValue


    def decay(self, labels, delta):
        """Calculate decay of a given label dict in a neuron
        :param float value: label value
        :param float delta: time since the last update for this neuron in ms
        :return: The new value after a decay has been applied
        :rtype: float
        """

        for key in labels:
            labels[key] = labels[key] * numpy.exp(-delta / self.tau)
        return labels


    def getInitialLabel(self, neuronGroupID, neuronID, neuronGroups):
        """Return an initial label for a neuron when an update is called
        for the first time
        :param int neuronGroupID: id of neuron group
        :param int neuronID: id of neuron
        :param list neuronGroups: all neuron groups
        .. note::
            Every entry in `neuronGroups` is an object with the following properties:
                * name
                * particle_system
                * count
                * areaStart
                * areaEnd
                * connections
            See data.py for a detailed description
        :return: color values
        :rtype: dict
        """
        ng = neuronGroups[neuronGroupID]

        layerValue = {"blue": 0.0, "red": 0.0, "green": 0.0}
        if (neuronID + neuronGroupID) % 2 == 0:
            layerValue["blue"] = 1.0
        else:
            layerValue["red"] = 1.0
        return layerValue

    def labelToColor(self, layerValues, neuronID, neuronGroupID, neuronGroups):
        """Apply a color to a spike object from a given label
        :param layerValues: The label for this spike.
        :type layerValues: dict
        :param neuronID: The ID of the neuron this spike is originating from
        :type neuronID: int
        :param neuronGroupID: The ID of the neuron group
        :type neuronGroupID: int
        :param neuronGroups: A list of all neuron groups available. Every entry
          in this list is an object with the following properties:
            * name
            * particle_system,
            * count
            * areaStart
            * areaEnd
            * connections
            See data.py for a detailed description.
        :return: the color for this spike
        :rtype:  float[4]
        """
        red = layerValues["red"]
        blue = layerValues["blue"]
        green = layerValues["green"]

        return (red, green, blue, 1.0)

class MaskLabelController(LabelController):
    """Similar to LabelController, but initializes the labels whether the neuron 
    is masked by an object"""

    identifier = 'MaskLabelController'
    name = 'RGB Masked'
    description = 'Creates one color inside a mask and mixes using RGB'

    class MaskProperties(bpy.types.PropertyGroup):
        maskObject = bpy.props.StringProperty(name = "Mask")
        insideMaskColor = bpy.props.FloatVectorProperty(name = "Spike color inside", default = (1.0, 0.0, 0.0, 1.0), subtype = 'COLOR', size = 4, min = 0.0, max = 1.0)
        outsideMaskColor = bpy.props.FloatVectorProperty(name = "Spike color outside", default = (0.0, 1.0, 0.0, 1.0), subtype = 'COLOR', size = 4, min = 0.0, max = 1.0)

    properties = MaskProperties

    def draw(self, layout, context):
        props = self.getProps(context)

        row = layout.row()
        row.prop_search(props, "maskObject", bpy.data, "objects")

        row = layout.row()
        row.prop(props, "insideMaskColor")

        row = layout.row()
        row.prop(props, "outsideMaskColor")

    def getInitialLabel(self, neuronGroupID, neuronID, neuronGroups):
        """Checks if a neuron is inside or outside of the mask, and returns
        a color label.
        :param neuronID: The ID of the neuron this spike is originating from
        :type neuronID: int
        :param neuronGroupID: The ID of the neuron group
        :type neuronGroupID: int
        :param neuronGroups: A list of all neuron groups available. Every entry
          in this list is an object with the following properties:
            * name
            * particle_system,
            * count
            * areaStart
            * areaEnd
            * connections
            See data.py for a detailed description.
        :return: The label for this spike
        :rtype:  dict
        """
        props = self.getProps(bpy.context)
        maskObject = bpy.data.objects[props.maskObject]
        insideMaskColor = props.insideMaskColor
        outsideMaskColor = props.outsideMaskColor
        neuron_group = neuronGroups[neuronGroupID]
        layer_name = neuron_group[0]
        particle_system_name = neuron_group[1]
        particle = bpy.data.objects[layer_name].particle_systems[particle_system_name].particles[neuronID]
        
        if mesh.checkPointInObject(maskObject, particle.location):
            return {"red": insideMaskColor[0], "green": insideMaskColor[1], "blue": insideMaskColor[2]}
        else:
            return {"red": outsideMaskColor[0], "green": outsideMaskColor[1], "blue": outsideMaskColor[2]}

class HSVLabelController(LabelController):
    """Similar to LabelController, but stores color values in the HSV format, 
    decays value, and mixes value and hue (For better color mixing)"""
    
    identifier = 'HSVLabelController'
    name = 'HSV'
    description = 'Creates random red and green spikes and mixes them using HSV'

    def mixLabels(self, layerValue1, layerValue2):
        newValue = {"hue": 0.0, "saturation": 0.0, "value": 0.0}

        h1 = layerValue1["hue"]
        h2 = layerValue2["hue"]
        if abs(h1 - h2) < 180:
            newValue["hue"] = (h1 + h2) / 2
        else:
            # Find the average modulo 360
            newValue["hue"] = (((h1 - 180) % 360.0 + (h2 - 180) % 360) / 2 + 180) % 360
        newValue["saturation"] = (layerValue1["saturation"] + layerValue2["saturation"]) / 2
        newValue["value"] = (layerValue1["value"] + layerValue2["value"]) / 2

        return newValue

    def decay(self, labels, delta):
        # for key in labels:
        #     labels[key] = labels[key] * numpy.exp(-delta / self.tau)
        labels['value'] = labels['value'] * numpy.exp(-delta / self.tau)
        return labels


    def getInitialLabel(self, neuronGroupID, neuronID, neuronGroups):
        ng = neuronGroups[neuronGroupID]

        layerValue = {"hue": 0.0, "saturation": 1.0, "value": 1.0}
        if (neuronID + neuronGroupID) % 2 == 0:
            layerValue["hue"] = 240.0
        else:
            layerValue["hue"] = 0.0
        return layerValue

    def labelToColor(self, layerValues, neuronID, neuronGroupID, neuronGroups):

        hue = layerValues['hue']
        sat = layerValues['saturation']
        val = layerValues['value']

        rgb = self.hsv_to_rgb(hue, sat, val)

        return (rgb[0], rgb[1], rgb[2], 1.0)

    @staticmethod
    def rgb_to_hsv(r, g, b):
        max_col = max(r, g, b)
        min_col = min(r, g, b)
        c = max_col - min_col
        if c == 0.0:
            return (0, 0, 0)
        if max_col == r:
            hue = ((g - b) / c) % 6.0
        elif max_col == g:
            hue = ((b - r) / c) + 2
        elif max_col == b:
            hue = ((r - g) / c) + 4
        value = max_col
        if c == 0:
            saturation = 0
        else:
            saturation = c / value
        return (hue * 60, saturation, value)

    @staticmethod
    def hsv_to_rgb(hue, sat, val):
        c = val * sat
        h = hue / 60.0
        x = c*(1 - abs((h % 2) - 1))
        if h < 1:
            rgb = (c, x, 0)
        elif h < 2:
            rgb = (x, c, 0)
        elif h < 3:
            rgb = (0, c, x)
        elif h < 4:
            rgb = (0, x, c)
        elif h < 5:
            rgb = (x, 0, c)
        elif h < 6:
            rgb = (c, 0, x)

        m = val - c

        return (rgb[0] + m, rgb[1] + m, rgb[2] + m, 1.0)

class HSVMaskLabelController(HSVLabelController, MaskLabelController):
    """Masked version of HSVLabelController"""

    identifier = 'HSVMaskLabelController'
    name = 'Masked HSV'
    description = 'Creates colored spikes inside a mask and mixes them using HSV'

    def getInitialLabel(self, neuronGroupID, neuronID, neuronGroups):
        props = self.getProps(bpy.context)
        maskObject = bpy.data.objects[props.maskObject]
        insideMaskColor = props.insideMaskColor
        outsideMaskColor = props.outsideMaskColor
        neuron_group = neuronGroups[neuronGroupID]
        layer_name = neuron_group[0]
        particle_system_name = neuron_group[1]
        particle = bpy.data.objects[layer_name].particle_systems[particle_system_name].particles[neuronID]
        
        col_inside = self.rgb_to_hsv(*insideMaskColor[:3])
        col_outside = self.rgb_to_hsv(*outsideMaskColor[:3])

        if mesh.checkPointInObject(maskObject, particle.location):
            return {"hue": col_inside[0], "saturation": col_inside[1], "value": col_inside[2]}
        else:
            return {"hue": col_outside[0], "saturation": col_outside[1], "value": col_outside[2]}

def register():
    addLabelController(LabelController())
    addLabelController(MaskLabelController())
    addLabelController(HSVLabelController())
    addLabelController(HSVMaskLabelController())

def unregister():
    del bpy.types.Scene.pam_anim_simulation
    for controller in labelControllerDict.values():
        if controller.properties:
            delattr(bpy.types.Scene, 'pam_anim_simulation_' + controller.identifier + '_props')
            try:
                bpy.utils.unregister_class(controller.properties)
            except RuntimeError:
                pass
