"""Mapping module"""

import logging
import inspect
import random

import bpy
import bpy_extras

import numpy as np


from . import kernel
from . import model
from . import pam
from . import debug
from . import layer

from pam import pam_vis as pv
from pam import constants
from pam.tools import colorizeLayer as CL
from bpy_extras import io_utils

logger = logging.getLogger(__package__)


LAYER_TYPES = [
    ("postsynapse", "Postsynapse", "", "", 0),
    ("postintermediates", "Postintermediate", "", "", 1),
    ("synapse", "Synapse", "", "", 2),
    ("preintermediates", "Preintermediate", "", "", 3),
    ("presynapse", "Presynapse", "", "", 4),
]

MAPPING_TYPES = [
    ("euclid", "Euclidean", "", "", 0),
    ("normal", "Normal", "", "", 1),
    ("top", "Topology", "", "", 2),
    ("uv", "UV", "", "", 3),
    ("rand", "Random", "", "", 4),
    ("mask3D", "3D Mask", "", "", 5)
]

# Temp workaround because MAPPING_TYPES is in the wrong order, but can't be changed for legacy reasons
MAPPING_TYPES_PAM_ORDER = ["euclid", "normal", "rand", "top", "uv", "mask3D"]

MAPPING_DICT = {
    "euclid": constants.MAP_euclid,
    "normal": constants.MAP_normal,
    "rand": constants.MAP_random,
    "top": constants.MAP_top,
    "uv": constants.MAP_uv,
    "mask3D": constants.MAP_mask3D
}

DISTANCE_TYPES = [
    ("euclid", "Euclidean", "", "", 0),
    ("euclidUV", "EuclideanUV", "", "", 1),
    ("jumpUV", "jumpUV", "", "", 2),
    ("UVjump", "UVjump", "", "", 3),
    ("normalUV", "NormalUV", "", "", 4),
    ("UVnormal", "UVnormal", "", "", 5),
]

DISTANCE_DICT = {
    "euclid": constants.DIS_euclid,
    "euclidUV": constants.DIS_euclidUV,
    "jumpUV": constants.DIS_jumpUV,
    "UVjump": constants.DIS_UVjump,
    "normalUV": constants.DIS_normalUV,
    "UVnormal": constants.DIS_UVnormal
}

def updatePanels(m = None, context = None, clear = True):
    """Updates the mapping panels to be up to date with the PAM model

    :param m: The model to convert. If None, the currently active model in model.MODEL is used
    :type m: model.Model
    :param context: The blender context to create the mapping panels in. If None, the currently active context is used
    :type context: bpy.types.Context
    :param clear: If true, clears the mapping sets before adding new sets
    :type clear: Boolean
    """
    if context == None:
        context = bpy.context
    if m is None:
        m = model.MODEL
    mapping = context.scene.pam_mapping
    
    if clear:
        mapping.sets.clear()

    for con in m.connections:
        s = mapping.sets.add()
        s.name = con.pre_layer.name + '-' + con.post_layer.name

        for l in con.layers:
            new_layer = s.layers.add()
            new_layer.object = l.obj_name

            if l is con.pre_layer or l is con.post_layer:
                if l is con.pre_layer:
                    new_layer.type = 'presynapse'
                elif l is con.post_layer:
                    new_layer.type = 'postsynapse'

                new_layer.kernel.function = l.kernel.name
                new_layer.kernel.particles = l.neuronset_name
                new_layer.kernel.object = l.obj_name
                for arg_name, arg_val in l.kernel.get_args().items():
                    a = new_layer.kernel.parameters[arg_name]
                    a.value = arg_val
            elif l is con.synaptic_layer:
                new_layer.type = 'synapse'
                new_layer.synapse_count = l.no_synapses
            elif l in con.pre_intermediate_layers:
                new_layer.type = 'preintermediates'
            elif l in con.post_intermediate_layers:
                new_layer.type = 'postintermediates'

        for con_mapping in con.mappings:
            new_mapping = s.mappings.add()
            new_mapping.function = MAPPING_TYPES_PAM_ORDER[con_mapping[0]]
            new_mapping.distance = DISTANCE_TYPES[con_mapping[1]][0]

def convertAllSetsToModel():
    """Adds the blender model connections to the pam model"""

    for set in bpy.context.scene.pam_mapping.sets:
        pam.addConnection(setToModel(set))

def setToModel(set):
    """Converts a PAM Mapping set to a model connection
    :param set: The set to be converted 
    :type set: mapping.PAMMapSet

    :return: A new connection object containing the information of the set
    :rtype: model.Connection
    """
    pre_neurons = set.layers[0].kernel.particles
    pre_func = set.layers[0].kernel.function
    pre_params = {param.name: param.value for param in set.layers[0].kernel.parameters}
    pre_kernel = kernel.get_kernel(pre_func, pre_params)

    post_neurons = set.layers[-1].kernel.particles
    post_func = set.layers[-1].kernel.function
    post_params = {param.name: param.value for param in set.layers[-1].kernel.parameters}
    post_kernel = kernel.get_kernel(post_func, post_params)

    synapse_layer = -1
    synapse_count = 0
    layers = []

    # collect all
    for i, l in enumerate(set.layers):
        obj = bpy.data.objects[l.object]
        if l.type == 'presynapse':
            layers.append(layer.NeuronLayer(obj.name, obj, pre_neurons, obj.particle_systems[pre_neurons].particles, pre_kernel))
        elif l.type == 'postsynapse':
            layers.append(layer.NeuronLayer(obj.name, obj, post_neurons, obj.particle_systems[post_neurons].particles, post_kernel))
        elif l.type == 'synapse':
            synapse_layer = i
            layers.append(layer.SynapticLayer(obj.name, obj, int(l.synapse_count * bpy.context.scene.pam_mapping.synapse_multiplier)))
        else:
            layers.append(layer.Layer2d(obj.name, obj))

    # error checking procedures
    if synapse_layer == -1:
        raise Exception('no synapse layer given')

    mapping_funcs = []

    for mapping in set.mappings[:len(layers) - 1]:
        mapping_funcs.append((MAPPING_DICT[mapping.function], DISTANCE_DICT[mapping.distance]))
    
    return model.Connection(
        layers,
        synapse_layer,
        mapping_funcs
    )

def particle_systems(self, context):
    """Generator for particle systems on an pam layer

    :param PAMKernelParameter self: a kernel parameter
    :param bpy.types.Context context: current blender context
    :return: list of particle system associated with object in kernel settings
    :rtype: list

    """
    p = []

    if self.object not in context.scene.objects:
        return p

    particles = context.scene.objects[self.object].particle_systems
    if not any(particles):
        return p

    p += [(p.name, p.name, "", "", i) for i, p in enumerate(particles)]

    return p


def active_mapping_index(self, context):
    """Return index of a mapping in active set

    :param PAMMappingParameter self: a mapping parameter
    :param bpy.types.Context context: current blender context
    :return: index of mapping in active set
    :rtype: int

    .. note::
        Returns `-1` if mapping is not in active set

    """
    m = context.scene.pam_mapping
    active_set = m.sets[m.active_set]

    index = -1

    for i, mapping in enumerate(active_set.mappings):
        if self == mapping:
            index = i
            break

    return index


def uv_source(self, context):
    """Return list of source uv layer on pam layer

    :param PAMMappingParameter self: a mapping parameter
    :param bpy.types.Context context: current blender context
    :return: list of uv layer names
    :rtype: list

    """
    p = []

    m = context.scene.pam_mapping
    active_set = m.sets[m.active_set]

    index = active_mapping_index(self, context)

    if index == -1:
        return p

    layer = active_set.layers[index]

    if layer.object not in context.scene.objects:
        return p

    uv_layers = context.scene.objects[layer.object].data.uv_layers
    if not any(uv_layers):
        return p

    p += [(l.name, l.name, "", "", i) for i, l in enumerate(uv_layers, start=1)]

    return p


def uv_target(self, context):
    """Return list of target uv layer on pam layer

    :param PAMMappingParameter self: a mapping parameter
    :param bpy.types.Context context: current blender context
    :return: list of uv layer names
    :rtype: list

    """
    p = []

    m = context.scene.pam_mapping
    active_set = m.sets[m.active_set]

    index = active_mapping_index(self, context)

    if index == -1:
        return p

    if len(active_set.layers) <= index + 1:
        return p

    layer = active_set.layers[index + 1]

    if layer.object not in context.scene.objects:
        return p

    uv_layers = context.scene.objects[layer.object].data.uv_layers
    if not any(uv_layers):
        return p

    p += [(l.name, l.name, "", "", i) for i, l in enumerate(uv_layers, start=1)]

    return p


def update_object(self, context):
    """Update object in kernel parameter

    :param PAMKernelParameter self: a kernel parameter
    :param bpy.types.Context context: current blender context

    """
    self.kernel.object = self.object


def update_kernels(self, context):
    """Update kernel parameters according to a chosen kernel function

    :param PAMMappingParameter self: a mapping parameter
    :param bpy.types.Context context: current blender context

    """
    self.parameters.clear()
    name = next(f for (f, _, _, _) in kernel.KERNEL_TYPES if f == self.function)
    func = getattr(kernel, name)
    if func is not None:
        args, _, _, defaults = inspect.getargspec(func)
        if args and defaults:
            args = args[-len(defaults):]
            params = zip(args, defaults)
            for k, v in params:
                p = self.parameters.add()
                p.name = k
                p.value = v

def update_neuron_number(self, context):
    """Update function, called when neuron set has been changed"""
    if self.object in bpy.data.objects and self.particles in bpy.data.objects[self.object].particle_systems:
        self.particle_count = bpy.data.objects[self.object].particle_systems[self.particles].settings.count

def update_particle_number(self, context):
    """Update function, called when neuron count has been changed"""
    if self.particle_count > 0 and self.object in bpy.data.objects and self.particles in bpy.data.objects[self.object].particle_systems:
        bpy.data.objects[self.object].particle_systems[self.particles].settings.count = self.particle_count * context.scene.pam_mapping.neuron_multiplier

def update_all_particle_numbers(self, context):
    """Update function, called when the neuron multiplier has been changed"""
    for s in self.sets:
        for layer in s.layers:
            if layer.type in ['presynapse', 'postsynapse']:
                update_particle_number(layer.kernel, context)

class PAMKernelValues(bpy.types.PropertyGroup):
    """Represent a kernel name/value pair"""
    name = bpy.props.StringProperty(
        name="Parameter name",
        default="param"
    )
    value = bpy.props.FloatProperty(
        name="Float value",
        default=0.0
    )


class PAMKernelParameter(bpy.types.PropertyGroup):
    """Represent a kernel setting"""
    object = bpy.props.StringProperty()
    function = bpy.props.EnumProperty(
        name="Kernel function",
        items=kernel.KERNEL_TYPES,
        update=update_kernels,
    )
    parameters = bpy.props.CollectionProperty(
        type=PAMKernelValues
    )
    particles = bpy.props.EnumProperty(
        name="Particle system",
        items=particle_systems,
        update = update_neuron_number
    )
    particle_count = bpy.props.IntProperty(
        name='Neuron count',
        min = 0,
        default = 0,
        update = update_particle_number
    )
    active_parameter = bpy.props.IntProperty()


class PAMMappingParameter(bpy.types.PropertyGroup):
    """Represent a mapping"""
    function = bpy.props.EnumProperty(
        name="Mapping function",
        items=MAPPING_TYPES,
    )
    distance = bpy.props.EnumProperty(
        name="Distance function",
        items=DISTANCE_TYPES,
    )
    uv_source = bpy.props.EnumProperty(
        name="UV source",
        items=uv_source,
    )
    uv_target = bpy.props.EnumProperty(
        name="UV target",
        items=uv_target,
    )


class PAMLayer(bpy.types.PropertyGroup):
    """Represent a layer"""
    object = bpy.props.StringProperty(
        update=update_object,
    )
    type = bpy.props.EnumProperty(
        items=LAYER_TYPES,
        name="Layer type",
    )
    collapsed = bpy.props.BoolProperty(
        default=False,
    )
    kernel = bpy.props.PointerProperty(type=PAMKernelParameter)
    synapse_count = bpy.props.IntProperty(
        min=1,
        default=1,
    )


class PAMMapSet(bpy.types.PropertyGroup):
    """Represent a mapping set"""
    name = bpy.props.StringProperty(default="mapping")
    layers = bpy.props.CollectionProperty(type=PAMLayer)
    mappings = bpy.props.CollectionProperty(type=PAMMappingParameter)


class PAMMap(bpy.types.PropertyGroup):
    """Represent pam mapping data"""
    sets = bpy.props.CollectionProperty(type=PAMMapSet)
    active_set = bpy.props.IntProperty()
    num_neurons = bpy.props.IntProperty(
        default=1,
        min=1,
    )
    neuron_multiplier = bpy.props.FloatProperty(
        name = "Neuron count multiplier", 
        min = 0.0,
        subtype = 'UNSIGNED',
        default = 1.0,
        update = update_all_particle_numbers
    )
    synapse_multiplier = bpy.props.FloatProperty(
        name = "Synapse count multiplier", 
        min = 0.0,
        subtype = 'UNSIGNED',
        default = 1.0
    )
    seed = bpy.props.IntProperty(name = "Seed")

class PAMSyncPanelsToModel(bpy.types.Operator):
    bl_idname = "pam.sync_panel_model"
    bl_label = "Sync Panels to Model"
    bl_description = "Synchronize the mapping panel to the pam model"

    def execute(self, context):
        model.reset()
        convertAllSetsToModel()

        return {'FINISHED'}

class PAMSyncModelToPanels(bpy.types.Operator):
    bl_idname = "pam.sync_model_panel"
    bl_label = "Sync Model to Mapping Panels"
    bl_description = "Synchronize the pam model to the mapping panels"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return any(model.MODEL.connections)

    def execute(self, context):
        updatePanels()

        return {'FINISHED'}

class PAMSyncAndSaveMapping(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Save current model"""

    bl_idname = "pam.model_sync_save_json"
    bl_label = "Sync and save"
    bl_description = "Synchronize the model with the mapping panel and save it to JSON"

    filename_ext = ".json"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        convertAllSetsToModel()
        model.saveModelToJson(model.MODEL, self.filepath)

        return {'FINISHED'}

class PAMLoadAndSyncMapping(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load the model and sync it to the mapping panel"""

    bl_idname = "pam.model_load_sync_json"
    bl_label = "Load and sync"
    bl_description = "Load the model from JSON and synchronize it with the mapping panel"

    def execute(self, context):
        m = model.loadModelFromJson(self.filepath)
        model.MODEL = m
        updatePanels(m)

        return {'FINISHED'}


class PAMMappingVisibility(bpy.types.Operator):
    """Make only objects involved in this mapping visible. Hides every other object that is set to be selectable."""
    bl_idname = "pam.mapping_visibility"
    bl_label = "Make mapping objects visible. Hide others."
    bl_description = "Make only objects involved in this mapping visible"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        set = bpy.context.scene.pam_mapping.sets[bpy.context.scene.pam_mapping.active_set]
        
        layers = []
        
        for i, layer in enumerate(set.layers):
            layers.append(bpy.data.objects[layer.object])
            
        bpy.ops.object.select_all(action='DESELECT')
            
        for obj in bpy.data.objects:
            if not obj.hide_select:
                obj.hide  = True
        
        for obj in layers:
            obj.hide = False

        bpy.context.scene.objects.active = layers[0]    #set presynaptic object active
        layers[0].select = True
            
        return {'FINISHED'}

class PAMMappingVisibilityPart(bpy.types.Operator):
    """Make only objects involved in this mapping visible that have particles. Hides every other object that is set to be selectable."""
    bl_idname = "pam.mapping_visibility_part"
    bl_label = "Make mapping objects with paricles visible. Hide others"
    bl_description = "Make only objects involved in this mapping visible that have particles"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        set = bpy.context.scene.pam_mapping.sets[bpy.context.scene.pam_mapping.active_set]
        
        layers = []
        
        for i, layer in enumerate(set.layers):
            layers.append(bpy.data.objects[layer.object])
            
        bpy.ops.object.select_all(action='DESELECT')
            
        for obj in bpy.data.objects:
            if not obj.hide_select:
                obj.hide  = True
        
        for obj in layers:
            if len(obj.particle_systems) > 0:
                obj.hide = False

        bpy.context.scene.objects.active = layers[0]    #set presynaptic object active
        layers[0].select = True
            
        return {'FINISHED'}

class PAMMappingVisibilityAll(bpy.types.Operator):
    """Make all neuron objects visible. Hides every other object that is set to be selectable."""
    bl_idname = "pam.mapping_visibility_all"
    bl_label = "Make neuron objects visible. Hide others"
    bl_description = "Make all neuron objects visible. Hide others"
    bl_options = {"UNDO"}
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        set = bpy.context.scene.pam_mapping.sets[bpy.context.scene.pam_mapping.active_set]
        
        layers = []
        
        for i, layer in enumerate(set.layers):
            layers.append(bpy.data.objects[layer.object])
            
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if not obj.hide_select:
                if len(obj.particle_systems) > 0:
                    obj.hide = False
                else:
                    obj.hide  = True

        bpy.context.scene.objects.active = layers[0]    #set presynaptic object active
        layers[0].select = True
            
        return {'FINISHED'}

class PAMMappingUp(bpy.types.Operator):
    """Move active mapping index up"""
    bl_idname = "pam.mapping_up"
    bl_label = "Move mapping up"
    bl_description = ""
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        m = context.scene.pam_mapping
        return len(m.sets) > 1 and m.active_set > 0

    def execute(self, context):
        m = context.scene.pam_mapping

        last = m.active_set - 1

        if last >= 0:
            m.sets.move(m.active_set, last)
            m.active_set = last

        return {'FINISHED'}


class PAMMappingDown(bpy.types.Operator):
    """Move active mapping index down"""
    bl_idname = "pam.mapping_down"
    bl_label = "Move mapping down"
    bl_description = ""
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        m = context.scene.pam_mapping
        return len(m.sets) > 1 and m.active_set < len(m.sets) - 1

    def execute(self, context):
        m = context.scene.pam_mapping

        next = m.active_set + 1

        if next < len(m.sets):
            m.sets.move(m.active_set, next)
            m.active_set = next

        return {'FINISHED'}


class PAMMappingLayerUp(bpy.types.Operator):
    """Move active layer index up"""
    bl_idname = "pam.mapping_layer_up"
    bl_label = "Move layer up"
    bl_description = ""
    bl_options = {"UNDO"}

    index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        return any(active_set.layers)

    def execute(self, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        last = self.index - 1

        if last >= 0:
            active_set.layers.move(self.index, last)
            active_set.mappings.move(self.index, last)

        return {'FINISHED'}


class PAMMappingLayerDown(bpy.types.Operator):
    """Move active layer index down"""
    bl_idname = "pam.mapping_layer_down"
    bl_label = "Move layer down"
    bl_description = ""
    bl_options = {"UNDO"}

    index = bpy.props.IntProperty()

    @classmethod
    def poll(self, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        return any(active_set.layers)

    def execute(self, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        next = self.index + 1

        if next < len(active_set.layers):
            active_set.layers.move(self.index, next)
            active_set.mappings.move(self.index, next)

        return {'FINISHED'}


class PAMMappingLayerAdd(bpy.types.Operator):
    """Add a new layer"""
    bl_idname = "pam.mapping_layer_add"
    bl_label = "Add layer"
    bl_description = ""
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        l = active_set.layers.add()
        m = active_set.mappings.add()

        return {'FINISHED'}


class PAMMappingLayerRemove(bpy.types.Operator):
    """Remove layer by index"""
    bl_idname = "pam.mapping_layer_remove"
    bl_label = "Remove layer"
    bl_description = ""
    bl_options = {"UNDO"}

    index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        m = context.scene.pam_mapping
        set = m.sets[m.active_set]
        return len(set.layers) > 2

    def execute(self, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        active_set.layers.remove(self.index)
        active_set.mappings.remove(self.index - 1)

        return {'FINISHED'}


class PAMMappingSetObject(bpy.types.Operator):
    """Associate current active object with layer by index"""
    bl_idname = "pam.mapping_layer_set_object"
    bl_label = "Set layer"
    bl_description = ""
    bl_options = {"UNDO"}

    index = bpy.props.IntProperty()

    def execute(self, context):
        active_obj = context.scene.objects.active
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        layer = active_set.layers[self.index]
        layer.object = active_obj.name

        if layer.kernel.particles == "":
            p = particle_systems(layer, context)
            if any(p):
                layer.kernel.particles = p[0][0]

        return {'FINISHED'}


class PAMMappingAddSet(bpy.types.Operator):
    """Add new mapping set"""
    bl_idname = "pam.mapping_add_set"
    bl_label = "Add a mapping set"
    bl_description = ""
    bl_options = {"UNDO"}

    count = bpy.props.IntProperty()

    def execute(self, context):
        active_obj = context.scene.objects.active
        m = context.scene.pam_mapping

        set = m.sets.add()
        set.name = "%s.%03d" % (set.name, self.count)
        self.count += 1

        pre = set.layers.add()
        pre.type = LAYER_TYPES[4][0]

        pre_syn_mapping = set.mappings.add()

        syn = set.layers.add()
        syn.type = LAYER_TYPES[2][0]
        
        syn_post_mapping = set.mappings.add()
        
        post = set.layers.add()
        post.type = LAYER_TYPES[0][0]

        return {'FINISHED'}


class PAMMappingDeleteSet(bpy.types.Operator):
    """Remove a mapping set"""
    bl_idname = "pam.mapping_delete_set"
    bl_label = "Delete active mapping set"
    bl_description = ""
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return any(context.scene.pam_mapping.sets)

    def execute(self, context):
        context.scene.pam_mapping.sets.remove(context.scene.pam_mapping.active_set)

        return {'FINISHED'}


class PAMMappingSetLayer(bpy.types.Operator):
    """Set layer type"""
    bl_idname = "pam.mapping_layer_set"
    bl_label = "Delete active mapping set"
    bl_description = ""
    bl_options = {"UNDO"}

    type = bpy.props.EnumProperty(items=LAYER_TYPES)

    @classmethod
    def poll(cls, context):
        m = context.scene.pam_mapping
        return any(m.sets)

    def execute(self, context):
        active_obj = context.scene.objects.active
        m = context.scene.pam_mapping

        active_set = m.sets[m.active_set]

        layer = active_set.layers.add()
        mapping = active_set.mappings.add()

        layer.object = active_obj.name
        layer.type = self.type

        context.scene.objects.active = active_obj

        return {'FINISHED'}


class PAMMappingCompute(bpy.types.Operator):
    """Compute mapping"""
    bl_idname = "pam.mapping_compute"
    bl_label = "Compute mapping"
    bl_description = ""

    type = bpy.props.EnumProperty(items=LAYER_TYPES)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        pam.initialize3D()
        convertAllSetsToModel()

        pam.resetOrigins()
        pam.computeAllConnections()

        return {'FINISHED'}
    
class PAMMappingComputeSelected(bpy.types.Operator):
    """Compute active mapping"""
    bl_idname = "pam.mapping_compute_sel"
    bl_label = "Compute selected mapping"
    bl_description = ""

    type = bpy.props.EnumProperty(items=LAYER_TYPES)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        pam.model.reset()
        pam.initialize3D()

        set = bpy.context.scene.pam_mapping.sets[bpy.context.scene.pam_mapping.active_set]

        pam.addConnection(setToModel(set))

        pam.resetOrigins()
        pam.computeAllConnections()

        return {'FINISHED'}

class PAMAddNeuronSetLayer(bpy.types.Operator):
    """Adds a new neuron set to the active object

    .. note::
        Only mesh-objects are allowed to own neuron sets as custom
        properties.
    """

    bl_idname = "pam.add_neuron_set_layer"
    bl_label = "Add neuron-set"
    bl_description = "Add a new neuron set"
    bl_options = {'UNDO'}

    # layer = bpy.props.PointerProperty(type=PAMLayer)
    layer_index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return  True#cls.layer.object in bpy.data.objects

    def execute(self, context):
        layer = context.scene.pam_mapping.sets[context.scene.pam_mapping.active_set].layers[self.layer_index]
        active_obj = bpy.data.objects[layer.object]

        context.scene.objects.active = active_obj
        bpy.ops.object.particle_system_add()

        psys = active_obj.particle_systems[-1]
        psys.name = "pam.neuron_group"
        psys.seed = random.randrange(0, 1000000)

        pset = psys.settings
        pset.type = "EMITTER"
        pset.count = layer.kernel.particle_count
        pset.frame_start = pset.frame_end = 1.0
        pset.emit_from = "FACE"
        pset.use_emit_random = True
        pset.use_even_distribution = True
        pset.distribution = "RAND"
        pset.use_rotations = True
        pset.use_rotation_dupli = True
        pset.rotation_mode = "NOR"
        pset.normal_factor = 0.0
        pset.render_type = "OBJECT"
        pset.use_whole_group = True
        pset.physics_type = "NO"
        pset.particle_size = 1.0

        pset['delay'] = 1.0

        bpy.ops.object.select_all(action="DESELECT")

        context.scene.update()

        active_obj.select = True

        layer.kernel.particles = psys.name

        return {'FINISHED'}


class PAMAddNeuronSet(bpy.types.Operator):
    """Adds a new neuron set to the active object

    .. note::
        Only mesh-objects are allowed to own neuron sets as custom
        properties.
    """

    bl_idname = "pam.add_neuron_set"
    bl_label = "Add neuron-set"
    bl_description = "Add a new neuron set"
    bl_options = {'UNDO'}

    glob = bpy.props.BoolProperty(
        default = True
    )
    obj = bpy.props.StringProperty(
        default = ""
    )

    @classmethod
    def poll(cls, context):
        if cls.glob:
            obj = context.object
            if obj:
                return obj.type == "MESH"
            else:
                return False
        else:
            return cls.obj in bpy.data.objects

    def execute(self, context):
        if not self.glob:
            active_obj = bpy.data.objects[self.obj]
        else:
            active_obj = context.active_object
        m = context.scene.pam_mapping

        context.scene.objects.active = active_obj
        bpy.ops.object.particle_system_add()

        psys = active_obj.particle_systems[-1]
        psys.name = "pam.neuron_group"
        psys.seed = random.randrange(0, 1000000)

        pset = psys.settings
        pset.type = "EMITTER"
        pset.count = m.num_neurons
        pset.frame_start = pset.frame_end = 1.0
        pset.emit_from = "FACE"
        pset.use_emit_random = True
        pset.use_even_distribution = True
        pset.distribution = "RAND"
        pset.use_rotations = True
        pset.use_rotation_dupli = True
        pset.rotation_mode = "NOR"
        pset.normal_factor = 0.0
        pset.render_type = "OBJECT"
        pset.use_whole_group = True
        pset.physics_type = "NO"
        pset.particle_size = 1.0

        pset['delay'] = 1.0

        bpy.ops.object.select_all(action="DESELECT")

        context.scene.update()

        active_obj.select = True

        return {'FINISHED'}


class PAMMappingAddSelfInhibition(bpy.types.Operator):
    """Add self-inhibition layer"""

    bl_idname = "pam.mapping_self_inhibition"
    bl_label = "Add layer as self-inhibition mapping"
    bl_description = "Add layer as self-inhibition mapping"
    bl_options = {'UNDO'}

    count = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.object.type == "MESH"

    def execute(self, context):
        active_obj = context.scene.objects.active
        m = context.scene.pam_mapping

        newset = m.sets.add()
        newset.name = "selfinhibition.%03d" % self.count
        self.count += 1

        pre = newset.layers.add()
        pre_mapping = newset.mappings.add()
        pre.object = active_obj.name
        pre.type = LAYER_TYPES[4][0]
        pre_mapping.distance = DISTANCE_TYPES[1][0]
        pre_mapping.function = MAPPING_TYPES[2][0]

        syn = newset.layers.add()
        syn_mapping = newset.mappings.add()
        syn.object = active_obj.name
        syn.type = LAYER_TYPES[2][0]
        syn.synapse_count = 10
        syn_mapping.distance = DISTANCE_TYPES[1][0]
        syn_mapping.function = MAPPING_TYPES[2][0]

        post = newset.layers.add()
        post_mapping = newset.mappings.add()
        post.object = active_obj.name
        post.type = LAYER_TYPES[0][0]

        for layer in [pre, post]:
            layer.kernel.object = active_obj.name
            layer.kernel.function = kernel.KERNEL_TYPES[0][0]
            layer.kernel.parameters.clear()
            var_u = layer.kernel.parameters.add()
            var_u.name = 'var_u'
            var_u.value = 0.2
            var_v = layer.kernel.parameters.add()
            var_v.name = 'var_v'
            var_v.value = 0.2
            shift_u = layer.kernel.parameters.add()
            shift_u.name = 'shift_u'
            shift_u.value = 0
            shift_v = layer.kernel.parameters.add()
            shift_v.name = 'shift_v'
            shift_v.value = 0
            item = particle_systems(layer.kernel, context)
            if len(item) > 1:
                layer.kernel.particles = item[1][0]

        context.scene.objects.active = active_obj

        return {'FINISHED'}


class PAMMappingUpdate(bpy.types.Operator):
    """Update active mapping"""

    bl_idname = "pam.mapping_update"
    bl_label = "Update active mapping"
    bl_description = "Update active mapping"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        m = context.scene.pam_mapping
        return len(model.CONNECTION_RESULTS) > m.active_set

    def execute(self, context):
        m = context.scene.pam_mapping
        active_set = m.sets[m.active_set]

        con = setToModel(active_set)

        index = pam.replaceMapping(m.active_set, con)

        pam.updateMapping(index)

        return {'FINISHED'}

class PAMMappingDebug(bpy.types.Operator):
    """"""
    bl_idname = "pam.mapping_debug"
    bl_label = "Debug Mapping"
    bl_description = "Checks where unconnected neurons failed"

    @classmethod
    def poll(cls, context):
        m = context.scene.pam_mapping
        return len(model.CONNECTION_RESULTS) > m.active_set
        
    def execute(self, context):
        debug.debugPreMapping(context.scene.pam_mapping.active_set)
        debug.debugPostMapping(context.scene.pam_mapping.active_set)

        return {'FINISHED'}

class PAMMappingSaveDistances(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Exports pre and post distances as CSV file"""
    bl_idname = "pam.mapping_distance_csv"
    bl_label = "Export distances"
    bl_description = "Exports pre and post distances as CSV file"
    
    filename_ext = ""

    
    def execute(self, context):
        mapping_id = bpy.context.scene.pam_mapping.active_set       
        pre = model.MODEL.connections[mapping_id].pre_layer.obj
        post = model.MODEL.connections[mapping_id].post_layer.obj
       
        CL.saveUVDistance(self.filepath + '_Pre.csv', pre.name, pre.particle_systems[0].active_particle_target_index, mapping_id)
        CL.saveUVDistanceForPost(self.filepath + '_Post.csv', post.name, post.particle_systems[0].active_particle_target_index, mapping_id)       
  
        return {'FINISHED'}   
   


class PAMMappingColorizeLayer(bpy.types.Operator):
    """Colorizes the layers for a given mapping with color coded distances"""
    bl_idname = "pam.mapping_color_layer"
    bl_label = "Colorize Layer"
    bl_description = "Colorizes the distances on each layer"
    
    def execute(self, context):
        mapping_id = bpy.context.scene.pam_mapping.active_set
        pre = model.MODEL.connections[mapping_id].pre_layer.obj
        post = model.MODEL.connections[mapping_id].post_layer.obj
        #neuron = bpy.data.objects['Neuron_Sphere']

        distances_pre = CL.getDistancesPerParticle(model.CONNECTION_RESULTS[mapping_id]['d'])
        pre_indices = CL.getParticleIndicesForVertices(pre, 0)

        for i, p_ind in enumerate(pre_indices):
            if distances_pre[p_ind] == 0:
                pv.visualizePoint(pre.particle_systems[0].particles[p_ind].location)
        
        distances_post = []
        post_indices = CL.getParticleIndicesForVertices(post, 0)
        
        valid_post_indices = []  # list of post indices with valid distance values
        
        for i, p in enumerate(post.particle_systems[0].particles):
            pre_neurons, synapses = model.getPreIndicesOfPostIndex(mapping_id, i)
            distance = []
            for j in range(len(pre_neurons)):
                distance.append(model.CONNECTION_RESULTS[mapping_id]['d'][pre_neurons[j]][synapses[j]])
                
            mean = np.mean(distance)
            if np.isnan(mean):
                distances_post.append(0)
            else:
                distances_post.append(mean)
                valid_post_indices.append(i)
        
        for i, p_ind in enumerate(post_indices):
            if distances_post[p_ind] == 0:
                pv.visualizePoint(post.particle_systems[0].particles[p_ind].location)

        print(distances_post)
        print(type(distances_pre))
        print(type(distances_post))
        distances_post_valid = list(np.take(distances_post, valid_post_indices))
        mean_d = np.mean(list(distances_pre) + distances_post_valid)
        min_percent = np.min(list(distances_pre) + distances_post_valid) / mean_d
        max_percent = np.max(list(distances_pre) + distances_post_valid) / mean_d
        distances_pre = distances_pre / mean_d
        distances_post = np.array(distances_post) / mean_d    
        
        CL.colorizeLayer(pre, np.take(distances_pre, pre_indices), [min_percent, max_percent])
        CL.colorizeLayer(post, np.take(distances_post, post_indices), [min_percent, max_percent])
        return {'FINISHED'}
        

def register():
    """Call on module register"""
    bpy.utils.register_class(PAMKernelValues)
    bpy.utils.register_class(PAMKernelParameter)
    bpy.utils.register_class(PAMMappingParameter)
    bpy.utils.register_class(PAMLayer)
    bpy.utils.register_class(PAMMapSet)
    bpy.utils.register_class(PAMMap)
    bpy.utils.register_class(PAMMappingColorizeLayer)
    bpy.utils.register_class(PAMMappingSaveDistances)
    bpy.utils.register_class(PAMMappingDebug)
    bpy.types.Scene.pam_mapping = bpy.props.PointerProperty(
        type=PAMMap
    )


def unregister():
    """Call on module unregister"""
    del bpy.types.Scene.pam_mapping


def validate_layer(context, layer):
    """Check if a layer is valid

    :param bpy.types.Context context: current context
    :param PAMLayer layer: a layer
    :return: error message
    :rtype: str

    .. note::
        If there is no error `None` will be returned

    """
    err = None

    if layer.type == "none":
        err = "layer missing type"

    elif layer.object == "":
        err = "layer missing object"

    elif layer.object not in context.scene.objects:
        err = "layer object missing in scene"

    return err


# TODO(SK): Implementation needed
def validate_mapping(mapping):
    """Check if a mapping is valid"""
    return False
