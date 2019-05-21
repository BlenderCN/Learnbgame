import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node

SOBEL_SIZE_ITEMS = (
    ("3", "3", "3", "", 0),
    ("5", "5", "5", "", 1),
    ("7", "7", "7", "", 2),
)


class OCVLCannyNode(OCVLNodeBase):

    n_doc = "Finds edges in an image using the [Canny86] algorithm."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="8-bit input image.")
    threshold1_in: bpy.props.FloatProperty(default=100, min=0, max=255, update=update_node, description="First threshold for the hysteresis procedure.")
    threshold2_in: bpy.props.FloatProperty(default=200, min=0, max=255, update=update_node, description="Second threshold for the hysteresis procedure.")
    apertureSize_in: bpy.props.EnumProperty(items=SOBEL_SIZE_ITEMS, default="3", update=update_node, description="Aperture size for the Sobel operator.")
    L2gradient_in: bpy.props.BoolProperty(default=False, update=update_node, description="Flag, indicating whether a more accurate.")

    edges_out: bpy.props.StringProperty(name="edges_out", default=str(uuid.uuid4()), description="Output edge map. Single channels 8-bit image, which has the same size as image.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "threshold1_in").prop_name = 'threshold1_in'
        self.inputs.new('StringsSocket', "threshold2_in").prop_name = 'threshold2_in'

        self.outputs.new("StringsSocket", "edges_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'image_in': self.get_from_props("image_in"),
            'threshold1_in': self.get_from_props("threshold1_in"),
            'threshold2_in': self.get_from_props("threshold2_in"),
            'apertureSize_in': int(self.get_from_props("apertureSize_in")),
            'L2gradient_in': self.get_from_props("L2gradient_in"),
            }

        edges_out = self.process_cv(fn=cv2.Canny, kwargs=kwargs)
        self.refresh_output_socket("edges_out", edges_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'L2gradient_in')
        self.add_button(layout, 'apertureSize_in', expand=True)
