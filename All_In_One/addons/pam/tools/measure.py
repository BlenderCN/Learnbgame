"""PAM Measurements Module"""

import logging
import math

import bpy

logger = logging.getLogger(__package__)


class PAMMeasureLayer(bpy.types.Operator):
    """Calculates neuron quantity across the active object"""

    bl_idname = "pam.measure_layer"
    bl_label = "Measure layer"
    bl_description = "Calculates neuron quantity on mesh"

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        if active_obj is not None:
            return active_obj.type == "MESH"
        else:
            return False

    def execute(self, context):
        active_obj = context.active_object

        surface = surface_area(active_obj)

        measure = context.scene.pam_measure
        area = measure.area
        quantity = measure.quantity

        neurons = math.ceil(surface * (float(quantity) / area))

        logger.debug(
            "%s surface (%f) quantity (%d) area (%f) neurons (%d)",
            active_obj,
            surface,
            quantity,
            area,
            neurons
        )

        context.scene.pam_measure.neurons = neurons
        context.scene.pam_measure.total_area = surface

        return {'FINISHED'}

    def invoke(self, context, event):
        measure = context.scene.pam_measure
        quantity = measure.quantity
        area = measure.area

        if not quantity > 0 or not area > 0.0:
            logger.warn("quantiy/area can not be zero or smaller")
            self.report(
                {'WARNING'},
                "Quantiy/Area must be non-zero and positive."
            )
            return {'CANCELLED'}

        return self.execute(context)


# TODO(SK): missing docstring
class MeasureProperties(bpy.types.PropertyGroup):
    area = bpy.props.FloatProperty(
        name="Area",
        default=1.0,
        min=0.0,
        unit="AREA"
    )
    quantity = bpy.props.IntProperty(
        name="Quantity",
        default=1,
        min=1,
        step=100,
        soft_max=10000000,
        subtype="UNSIGNED"
    )
    neurons = bpy.props.IntProperty(
        name="Neurons",
        default=0,
        subtype="UNSIGNED"
    )
    total_area = bpy.props.FloatProperty(
        name="Total area",
        default=1.0,
        min=0.0,
        unit="AREA"
    )


# TODO(SK): missing docstring
def register():
    bpy.utils.register_class(MeasureProperties)
    bpy.types.Scene.pam_measure = bpy.props.PointerProperty(
        type=MeasureProperties
    )


# TODO(SK): missing docstring
def unregister():
    del bpy.types.Scene.pam_measure


def surface_area(obj):
    """Returns surface area of a mesh

    Important: return value is dependent scene scale"""

    if not obj.type == "MESH":
        raise Exception("Can't calculate area of none-mesh objects")

    return sum([polygon.area for polygon in obj.data.polygons])
