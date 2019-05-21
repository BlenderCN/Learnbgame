import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, CODE_COLOR_POOR_ITEMS


class OCVLcvtColorNode(OCVLNodeBase):

    bl_icon = 'COLOR'
    n_doc = "Converts an image from one color space to another."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input image: 8-bit unsigned, 16-bit unsigned ( CV_16UC... ), or single-precision floating-point.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output image of the same size and depth as input image.")

    code_in: bpy.props.EnumProperty(items=CODE_COLOR_POOR_ITEMS, default='COLOR_BGR2GRAY', update=update_node, description="Color space conversion code (see cv::ColorConversionCodes).")
    dstCn_in: bpy.props.IntProperty(default=0, update=update_node, min=0, max=4, description="Number of channels in the destination image; if the parameter is 0, the number of the channels is derived automatically from input image and code.")

    def init(self, context):
        self.width = 200
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new("StringsSocket", "code_in").prop_name = "code_in"
        self.inputs.new("StringsSocket", "dstCn_in").prop_name = "dstCn_in"

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'src': self.get_from_props("image_in"),
            'code_in': self.get_from_props("code_in"),
            'dstCn_in': self.get_from_props("dstCn_in"),
            }

        image_out = self.process_cv(fn=cv2.cvtColor, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
