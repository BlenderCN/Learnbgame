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


class OCVLintegral3Node(OCVLNodeBase):

    n_doc = "Calculates the integral of an image."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input image as W x H, 8-bit or floating-point (32f or 64f).")
    sum_out: bpy.props.StringProperty(name="sum_out", default=str(uuid.uuid4()), description="Integral image as (W+1) x (H+1) , 32-bit integer or floating-point (32f or 64f).")
    sqsum_out: bpy.props.StringProperty(name="sqsum_out", default=str(uuid.uuid4()), description="integral image for squared pixel values; it is (W+1) x (H+1), double-precision floating-point (64f) array.")
    tilted_out: bpy.props.StringProperty(name="tilted_out", default=str(uuid.uuid4()), description="Integral for the image rotated by 45 degrees; it is (W+1) x (H+1) array with the same data type as sum.")

    sdepth_in: bpy.props.EnumProperty(items=SDEPTH_ITEMS, default="None", update=update_node, description="Desired depth of the integral and the tilted integral images, CV_32S, CV_32F, or CV_64F.")
    sqdepth_in: bpy.props.EnumProperty(items=SDEPTH_ITEMS, default="None", update=update_node, description="Desired depth of the integral and the tilted integral images, CV_32S, CV_32F, or CV_64F.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")

        self.outputs.new("StringsSocket", "sum_out")
        self.outputs.new("StringsSocket", "sqsum_out")
        self.outputs.new("StringsSocket", "tilted_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        sdepth_in = self.get_from_props("sdepth_in")
        sdepth_in = -1 if sdepth_in is None else sdepth_in

        sqdepth_in = self.get_from_props("sqdepth_in")
        sqdepth_in = -1 if sqdepth_in is None else sqdepth_in

        kwargs = {
            'src_in': self.get_from_props("image_in"),
            'sdepth_in': sdepth_in,
            'sqdepth_in': sqdepth_in,
            }

        sum_out, sqsum_out, tilted_out = self.process_cv(fn=cv2.integral3, kwargs=kwargs)
        self.refresh_output_socket("sum_out", sum_out, is_uuid_type=True)
        self.refresh_output_socket("sqsum_out", sqsum_out, is_uuid_type=True)
        self.refresh_output_socket("tilted_out", tilted_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'sdepth_in')
        self.add_button(layout, 'sqdepth_in')
