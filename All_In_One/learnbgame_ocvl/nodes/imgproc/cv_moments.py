import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLmomentsNode(OCVLNodeBase):

    n_doc = "Calculates all of the moments up to the third order of a polygon or rasterized shape."

    moments_out: bpy.props.StringProperty(name="moments_out", default=str(uuid.uuid4()), description="Output moments.")
    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Raster image (single-channel, 8-bit or floating-point 2D array) or an array") #pobrane z opisu dla 'array' nie wiem czy dobrze
    binaryImage_in: bpy.props.BoolProperty(default=False, update=update_node, description="If it is true, all non-zero image pixels are treated as 1's. The parameter is used for images only.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.outputs.new("StringsSocket", "moments_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'array': self.get_from_props("image_in"),
            'binaryImage': self.get_from_props("binaryImage_in"),
            }

        moments_out = self.process_cv(fn=cv2.moments, kwargs=kwargs)
        self.refresh_output_socket("moments_out", moments_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'binaryImage_in')
