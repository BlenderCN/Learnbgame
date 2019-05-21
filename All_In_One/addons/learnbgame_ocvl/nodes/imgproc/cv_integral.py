import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node

SDEPTH_ITEMS = (
    ("None", "None", "None", "", 0),
    ("CV_32S", "CV_32S", "CV_32S", "", 1),
    ("CV_32F", "CV_32F", "CV_32F", "", 2),
    ("CV_64F", "CV_64F", "CV_64F", "", 3),
)


class OCVLintegralNode(OCVLNodeBase):

    n_doc = "Calculates the integral of an image."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input image as W x H, 8-bit or floating-point (32f or 64f).")
    sum_out: bpy.props.StringProperty(name="sum_out", default=str(uuid.uuid4()), description="Integral image as (W+1) x (H+1) , 32-bit integer or floating-point (32f or 64f).")

    sdepth_in: bpy.props.EnumProperty(items=SDEPTH_ITEMS, default="None", update=update_node, description="Desired depth of the integral and the tilted integral images, CV_32S, CV_32F, or CV_64F.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")

        self.outputs.new("StringsSocket", "sum_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        sdepth_in = self.get_from_props("sdepth_in")
        sdepth_in = -1 if sdepth_in is None else sdepth_in

        kwargs = {
            'src_in': self.get_from_props("image_in"),
            'sdepth_in': sdepth_in,
            }

        sum_out = self.process_cv(fn=cv2.integral, kwargs=kwargs)
        self.refresh_output_socket("sum_out", sum_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'sdepth_in')
