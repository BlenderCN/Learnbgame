import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, BORDER_TYPE_ITEMS


class OCVLcornerHarrisNode(OCVLNodeBase):

    n_doc = "Harris corner detector."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input single-channel 8-bit or floating-point image.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Image to store the Harris detector responses.")

    blockSize_in: bpy.props.IntProperty(default=2, min=1, max=30, update=update_node, description="Neighborhood size (see the details on cornerEigenValsAndVecs ).")
    ksize_in: bpy.props.IntProperty(default=3, min=1, max=30, update=update_node, description="Aperture parameter for the Sobel operator.")
    k_in: bpy.props.FloatProperty(default=0.04, min=0.01, max=1, update=update_node, description="Harris detector free parameter. See the formula below.")
    borderType_in: bpy.props.EnumProperty(items=BORDER_TYPE_ITEMS, default='None', update=update_node, description="Pixel extrapolation method. See cv::BorderTypes.")

    def init(self, context):
        self.width = 150
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "blockSize_in").prop_name = 'blockSize_in'
        self.inputs.new('StringsSocket', "ksize_in").prop_name = 'ksize_in'
        self.inputs.new('StringsSocket', "k_in").prop_name = 'k_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'src': self.get_from_props("image_in"),
            'blockSize_in': self.get_from_props("blockSize_in"),
            'ksize_in': self.get_from_props("ksize_in"),
            'k_in': self.get_from_props("k_in"),
            'borderType_in': self.get_from_props("borderType_in"),
            }

        image_out = self.process_cv(fn=cv2.cornerHarris, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'borderType_in')
