"""Visualization Module"""

import inspect
import logging
import math

import bpy
import numpy as np

from .. import kernel
from .. import model
from .. import pam
from .. import pam_vis
from .. import tracing
from .. import constants
from ..utils import colors
from ..utils import p

logger = logging.getLogger(__package__)

COLOR = colors.schemes["classic"]


VIEW_LIST = [
    ("NORMAL", "Multitextured", "", 0),
    ("MAPPED", "GLSL", "", 1)
]

MODE_LIST = [
    ("CURSOR", "At cursor", "", 0),
    ("COORDINATES", "At uv", "", 1)
]

INJ_METHOD_LIST = [
    ("ANTEROGRADE", "Anterograde", "", 0),
    ("RETROGRADE", "Retrograde", "", 1)
]

EFFERENT_AFFERENT_LIST = [
    ("EFFERENT", "Efferent", "", 0),
    ("AFFERENT", "Afferent", "", 1)
]


# TODO(SK): rephrase descriptions
# TODO(SK): missing docstring
class PAMVisualizeKernel(bpy.types.Operator):
    bl_idname = "pam.visualize"
    bl_label = "Generate kernel texture"
    bl_description = "Generate kernel texture"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        pam_visualize = context.scene.pam_visualize

        if active_obj is None:
            return False
        if active_obj.type != "MESH":
            return False
        if pam_visualize.kernel == "NONE":
            return False

        return True

    def execute(self, context):
        active_obj = context.active_object
        pam_visualize = context.scene.pam_visualize

        if active_obj.data.uv_layers.active is None:
            message = "active object has no active uv layer"

            logger.warn(message)
            self.report({"WARNING"}, message)

            return {'CANCELLED'}

        cursor = context.scene.cursor_location.copy()

        uv_scaling_factor, _ = pam.computeUVScalingFactor(active_obj)

        u, v = None, None

        if pam_visualize.mode == "CURSOR":
            u, v = pam.map3dPointToUV(
                active_obj,
                active_obj,
                cursor
            )

            logger.debug(
                "object (%s) uvscaling (%f) cursor (%f, %f, %f) uvmapped (%f, %f)",
                active_obj.name,
                uv_scaling_factor,
                cursor[0],
                cursor[1],
                cursor[2],
                u,
                v
            )
        elif pam_visualize.mode == "COORDINATES":
            u = pam_visualize.u
            v = pam_visualize.v

            logger.debug(
                "object (%s) uvscaling (%f) uv (%f, %f)",
                active_obj.name,
                uv_scaling_factor,
                u,
                v
            )

        temp_image = bpy.data.images.new(
            name="pam.temp_image",
            width=pam_visualize.resolution,
            height=pam_visualize.resolution,
            alpha=True
        )


        temp_material = bpy.data.materials.new("temp_material")
        # temp_material.use_shadeless = True

        kwargs = {p.name: p.value for p in pam_visualize.customs}

        # kernel_func = next(getattr(kernel, k) for (k, n, d, n) in kernel.KERNEL_TYPES if k == pam_visualize.kernel)
        kernel_obj = kernel.get_kernel(pam_visualize.kernel, kwargs)
        kernel_obj.rescale(uv_scaling_factor)

        kernel_image(
            np.array([u, v]),
            temp_image,
            kernel_obj
        )

        if context.scene.render.engine == 'CYCLES':
            temp_material.use_nodes = True
            diffuse_node = temp_material.node_tree.nodes['Diffuse BSDF']
            texture_node = temp_material.node_tree.nodes.new(type = "ShaderNodeTexImage")
            temp_material.node_tree.links.new(diffuse_node.inputs['Color'], texture_node.outputs['Color'])
            texture_node.image = temp_image

        else:
            temp_texture = bpy.data.textures.new(
                "temp_texture",
                type="IMAGE"
            )
            temp_texture.image = temp_image

            tex_slot = temp_material.texture_slots.add()
            tex_slot.texture = temp_texture
            tex_slot.texture_coords = "UV"
            tex_slot.mapping = "FLAT"
            # tex_slot.use_map_color_diffuse = True

            temp_material.diffuse_intensity = 1.0
            temp_material.specular_intensity = 0.0

        active_obj.data.materials.clear(update_data=True)
        active_obj.data.materials.append(temp_material)

        context.scene.update()

        return {'FINISHED'}


# TODO(SK): missing docstring
class PAMVisualizeKernelAtCoordinates(bpy.types.Operator):
    bl_idname = "pam.visualize_kernel"
    bl_label = "Visualize kernel"
    bl_description = "Visualize kernel function on object"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        if active_obj is not None:
            return active_obj.type == "MESH"
        else:
            return False

    def execute(self, context):
        context.scene
        return {'FINISHED'}


# TODO(SK): missing docstring
# TODO(SK): needs implementation
class PamVisualizeKernelReset(bpy.types.Operator):
    bl_idname = "pam.visualize_kernel_reset"
    bl_label = "Reset object"
    bl_description = "Reset object visualization"
    bl_options = {'UNDO'}

    def execute(self, context):
        return {'FINISHED'}


# TODO(SK): missing docstring
class PamVisualizeKernelAddCustomParam(bpy.types.Operator):
    bl_idname = "pam.add_param"
    bl_label = "Add param"
    bl_description = "Add custom parameter"
    bl_options = {'UNDO'}

    def execute(self, context):
        prop = context.scene.pam_visualize.customs.add()

        return {'FINISHED'}


# TODO(SK): missing docstring
class PamVisualizeKernelRemoveCustomParam(bpy.types.Operator):
    bl_idname = "pam.remove_param"
    bl_label = "Remove param"
    bl_description = "Remove custom parameter"
    bl_options = {'UNDO'}

    def execute(self, context):
        active_index = context.scene.pam_visualize.active_index
        context.scene.pam_visualize.customs.remove(active_index)

        return {'FINISHED'}


class PamVisualizeKernelResetCustomParams(bpy.types.Operator):
    bl_idname = "pam.reset_params"
    bl_label = "Reset kernel parameter"
    bl_description = "Remove kernel parameter"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        pam_visualize = context.scene.pam_visualize

        if pam_visualize.kernel == "NONE":
            return False

        return True

    def execute(self, context):
        pam_visualize = context.scene.pam_visualize
        update_kernels(pam_visualize, context)

        return {'FINISHED'}


class PamVisualizeClean(bpy.types.Operator):
    bl_idname = "pam_vis.visualize_clean"
    bl_label = "Clean Visualizations"
    bl_description = "Removes all visualizations"
    bl_options = {'UNDO'}

    def execute(self, context):
        active_o = bpy.context.active_object
        pam_vis.visualizeClean()
        if active_o:
            active_o.select = True
        bpy.context.scene.objects.active = active_o

        return {'FINISHED'}


class PamVisualizeAllConnections(bpy.types.Operator):
    bl_idname = "pam_vis.visualize_connections_all"
    bl_label = "Visualize All Connections"
    bl_description = "Visualizes all outgoing connections"
    bl_options = {'UNDO'}

    def execute(self, context):
        object = context.active_object
        connections = context.scene.pam_visualize.connections
        smoothing = context.scene.pam_visualize.smoothing
        for j in range(0, len(model.MODEL.connections)):
            for i in range(0, min(connections, len(pam.model.CONNECTION_RESULTS[j]['c']))):
                pam_vis.visualizeConnectionsForNeuron(j, i, smoothing)

        bpy.context.scene.objects.active = object
        if object:
            object.select = True
        return {'FINISHED'}


class PamVisualizeUnconnectedNeurons(bpy.types.Operator):
    bl_idname = "pam_vis.visualize_unconnected_neurons"
    bl_label = "Visualize Unconnected Neurons"
    bl_description = "Visualizes neurons with no outgoing connection"
    bl_options = {'UNDO'}

    def execute(self, context):
        object = context.active_object
        pv = context.scene.pam_visualize

        if object.name in model.MODEL.ng_dict:
            ng_index = model.MODEL.ng_dict[object.name][object.particle_systems[0].name]
        else:
            return {'FINISHED'}

        for ci in model.MODEL.connection_indices:
            # if ng_index is the pre- or post-synaptic layer, respectively, in a certain mapping
            if pv.efferent_afferent == "EFFERENT":
                if ci[1] == ng_index:                    
                    pam_vis.visualizeUnconnectedNeurons(ci[0])
            elif pv.efferent_afferent == "AFFERENT":
                if ci[2] == ng_index:
                    pam_vis.visualizeUnconnectedPostNeurons(ci[0])

        bpy.context.scene.objects.active = object
        object.select = True
        return {'FINISHED'}


class PamVisualizeConnectionsForNeuron(bpy.types.Operator):
    bl_idname = "pam_vis.visualize_connections_for_neuron"
    bl_label = "Visualize Connections at Cursor"
    bl_description = "Visualizes all outgoing or incoming connections for a neuron at cursor position"
    bl_options = {'UNDO'}

    def execute(self, context):
        object = context.active_object
        cursor = context.scene.cursor_location

        if object.name in model.MODEL.ng_dict:
            ng_index = model.MODEL.ng_dict[object.name][object.particle_systems[0].name]
        else:
            return {'FINISHED'}

        ng_index = model.MODEL.ng_dict[object.name][object.particle_systems[0].name]
        p_index = pam.map3dPointToParticle(object, 0, cursor)
        print('Neuron Number: ' + str(p_index))
        
        pam_vis.visualizePoint(object.particle_systems[0].particles[p_index].location)

        smoothing = context.scene.pam_visualize.smoothing
        for ci in model.MODEL.connection_indices:
            # if ng_index is the pre-synaptic layer in a certain mapping
            if ci[1] == ng_index:
                # visualize the connections
                pam_vis.visualizeConnectionsForNeuron(ci[0], p_index, smoothing, True)

        object.select = True
        bpy.context.scene.objects.active = object
        return {'FINISHED'}


class PamVisualizeForwardConnection(bpy.types.Operator):
    bl_idname = "pam_vis.visualize_forward_connection"
    bl_label = "Visualize Connection for Neuron at Cursor"
    bl_description = "Visualizes as many mappings as possible until the synaptic layer"
    bl_options = {'UNDO'}

    def execute(self, context):
        object = context.active_object
        cursor = context.scene.cursor_location
        pv = context.scene.pam_visualize

        if object.name in model.MODEL.ng_dict:
            ng_index = model.MODEL.ng_dict[object.name][object.particle_systems[0].name]
        else:
            return {'FINISHED'}

        ng_index = model.MODEL.ng_dict[object.name][object.particle_systems[0].name]
        p_index = pam.map3dPointToParticle(object, 0, cursor)
        print('Neuron Number: ' + str(p_index))

        for ci in model.MODEL.connection_indices:
            # if ng_index is the pre- or post-synaptic layer, respectively, in a certain mapping
            if pv.efferent_afferent == "EFFERENT":
                if ci[1] == ng_index:
                    pam_vis.visualizeForwardMapping(ci[0], p_index)
            elif pv.efferent_afferent == "AFFERENT":
                if ci[2] == ng_index:
                    pam_vis.visualizeBackwardMapping(ci[0], p_index)

        bpy.context.scene.objects.active = object
        return {'FINISHED'}

class PamVisualizeTracing(bpy.types.Operator):
    bl_idname = "pam_vis.tracing"
    bl_label = "Visualize tracing for injection site at Cursor"
    bl_description = "Performs an anterograde or retrograde tracing originating from the area around the cursor"
    bl_options = {'UNDO'}

    def execute(self, context):
        pv = context.scene.pam_visualize
        cursor = context.scene.cursor_location
        obj = None
        if pv.mesh != "":
            obj = bpy.data.objects[pv.mesh]
        if pv.inj_method == "ANTEROGRADE":
            if pv.set_color:
                tracing.anterograde_tracing(location=cursor, radius=pv.radius, inj_color=pv.inj_color, dupli_obj=obj, draw_paths=pv.draw_paths, smoothing=pv.smoothing)
            else:
                tracing.anterograde_tracing(location=cursor, radius=pv.radius, dupli_obj=obj, draw_paths=pv.draw_paths, smoothing=pv.smoothing)
        else:
            if pv.set_color:
                tracing.retrograde_tracing(location=cursor, radius=pv.radius, inj_color=pv.inj_color, dupli_obj=obj, draw_paths=pv.draw_paths, smoothing=pv.smoothing)
            else:
                tracing.retrograde_tracing(location=cursor, radius=pv.radius, dupli_obj=obj, draw_paths=pv.draw_paths, smoothing=pv.smoothing)
        return {'FINISHED'}

# TODO(SK): missing docstring
@p.profiling
def kernel_image(guv, image, kernel):
    width, height = image.size
    if width != height:
        pass

    res = 1.0 / width

    ranges = list(map(lambda x: x * res, range(width)))

    values = [kernel.apply(np.array([u, v]), guv) for v in ranges for u in ranges]
    color_index = list(map(lambda x: math.floor(x * 255.0), values))

    color_values = [COLOR[i] for i in color_index]

    image.pixels = [value for color in color_values for value in color]


def get_kernels(self, context):
    return kernel.KERNEL_TYPES


def update_kernels(self, context):
    self.customs.clear()
    func = next(getattr(kernel, k) for (k, n, d, n) in kernel.KERNEL_TYPES if k == self.kernel)
    if func is not None:
        args, _, _, defaults = inspect.getargspec(func)
        if args and defaults:
            args = args[-len(defaults):]
            params = zip(args, defaults)
            for k, v in params:
                p = self.customs.add()
                p.name = k
                p.value = v


# TODO(SK): missing docstring
def uv_visualize_texture():
    if "pam.temp_texture" in bpy.data.textures:
        logger.debug("using former temporary texture")

        temp_texture = bpy.data.textures["pam.temp_texture"]

    else:
        logger.debug("creating new temporary texture")

        temp_texture = bpy.data.textures.new(
            name="pam.temp_texture",
            type="IMAGE"
        )

    return temp_texture


# TODO(SK): missing docstring
def toggle_view(self, context):
    textured_solid = False
    material_mode = "MULTITEXTURE"
    viewport_shade = "SOLID"

    if self.view == "MAPPED":
        textured_solid = True
        material_mode = "GLSL"
        viewport_shade = "TEXTURED"

    context.space_data.show_textured_solid = textured_solid
    context.scene.game_settings.material_mode = material_mode
    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.viewport_shade = viewport_shade


# TODO(SK): missing docstring
def register():
    bpy.utils.register_class(PamVisualizeKernelFloatProperties)
    bpy.utils.register_class(PamVisualizeKernelProperties)
    bpy.types.Scene.pam_visualize = bpy.props.PointerProperty(
        type=PamVisualizeKernelProperties
    )


# TODO(SK): missing docstring
def unregister():
    del bpy.types.Scene.pam_visualize


# TODO(SK): missing docstring
class PamVisualizeKernelFloatProperties(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
        name="Param name",
        default="param"
    )
    value = bpy.props.FloatProperty(
        name="Float value",
        default=0.0
    )


# TODO(SK): missing docstring
class PamVisualizeKernelProperties(bpy.types.PropertyGroup):
    mesh = bpy.props.StringProperty(name="Mesh", description="Object to duplicate for use as neuron visualization. Using spheres when left empty.")
    view = bpy.props.EnumProperty(
        name="View mode",
        items=VIEW_LIST,
        update=toggle_view
    )
    efferent_afferent = bpy.props.EnumProperty(
        name="efferent_afferent",
        items=EFFERENT_AFFERENT_LIST
    )
    mode = bpy.props.EnumProperty(
        name="Mode",
        items=MODE_LIST
    )
    inj_method = bpy.props.EnumProperty(
        name="Injection Method",
        items=INJ_METHOD_LIST
    )
    radius = bpy.props.FloatProperty(
        name="Injection radius",
        default=0.5,
        min=0.0,
        unit="LENGTH",
        subtype="DISTANCE"
    )
    set_color = bpy.props.BoolProperty(
        name="Fix color for injection",
        description="Check to color the injection site neurons in a color different from the object color",
        default=False
    )
    draw_paths = bpy.props.BoolProperty(
        name="Draw connection paths",
        description="Check to draw connection paths between labelled neurons",
        default=False
    )
    inj_color = bpy.props.FloatVectorProperty(
        name="Injection color",
        subtype="COLOR"
    )
    kernel = bpy.props.EnumProperty(
        name="Kernel function",
        items=get_kernels,
        update=update_kernels
    )
    resolution = bpy.props.IntProperty(
        name="Kernel image resolution",
        default=128,
        min=2,
        soft_min=8,
        soft_max=4096,
        subtype="PIXEL"
    )
    connections = bpy.props.IntProperty(
        name="Number of Connections per Mapping",
        default=3,
        min=1,
        max=1000
    )

    smoothing = bpy.props.IntProperty(
        name="Number of smoothing steps",
        default=5,
        min=0,
        max=40
    )

    active_index = bpy.props.IntProperty()
    customs = bpy.props.CollectionProperty(
        type=PamVisualizeKernelFloatProperties
    )
    u = bpy.props.FloatProperty()
    v = bpy.props.FloatProperty()

    connection_material = bpy.props.StringProperty(name="Material")

    bevel_depth = bpy.props.FloatProperty(name = "Curve Bevel Depth", min = 0.0, default = constants.PATH_BEVEL_DEPTH)
