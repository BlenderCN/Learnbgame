import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, BORDER_TYPE_ITEMS


class OCVLGaussianBlurNode(OCVLNodeBase):

    bl_icon = 'FILTER'
    n_doc = "Blurs an image using a Gaussian filter."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input image.")
    ksize_in: bpy.props.IntVectorProperty(default=(1, 1), min=1, max=30, size=2, update=update_node, description="Gaussian kernel size.")
    sigmaX_in: bpy.props.FloatProperty(default=0, min=0, max=255, update=update_node, description="Gaussian kernel standard deviation in X direction.")
    sigmaY_in: bpy.props.FloatProperty(default=0, min=0, max=255, update=update_node, description="Gaussian kernel standard deviation in Y direction.")
    borderType_in: bpy.props.EnumProperty(items=BORDER_TYPE_ITEMS, default='None', update=update_node, description="Pixel extrapolation method, see cv::BorderTypes.")

    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output image.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "ksize_in").prop_name = 'ksize_in'
        self.inputs.new('StringsSocket', "sigmaX_in").prop_name = 'sigmaX_in'
        self.inputs.new('StringsSocket', "sigmaY_in").prop_name = 'sigmaY_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'src': self.get_from_props("image_in"),
            'ksize_in': self.get_from_props("ksize_in"),
            'sigmaX_in': self.get_from_props("sigmaX_in"),
            'sigmaY_in': self.get_from_props("sigmaY_in"),
            'borderType_in': self.get_from_props("borderType_in"),
            }

        image_out = self.process_cv(fn=cv2.GaussianBlur, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "borderType_in")
