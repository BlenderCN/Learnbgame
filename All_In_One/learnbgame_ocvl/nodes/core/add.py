import cv2
import bpy
import uuid

from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLaddNode(OCVLNodeBase):

    n_doc = "Calculates the per-element sum of two arrays or an array and a scalar."

    image_1_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node, description="First input array or a scalar.")
    image_2_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node, description="Second input array or a scalar.")
    mask_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node, description="Optional operation mask, 8-bit single channel array, that specifies elements of the output array to be changed.")

    image_out: bpy.props.StringProperty(default=str(uuid.uuid4()))

    @property
    def n_requirements(self):
        return ["image_1_in", "image_2_in"]

    def init(self, context):
        self.inputs.new("ImageSocket", "image_1_in")
        self.inputs.new("ImageSocket", "image_2_in")
        self.inputs.new('StringsSocket', "mask_in")

        self.outputs.new("ImageSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(self.n_requirements)

        kwargs = {
            'src1': self.get_from_props("image_1_in"),
            'src2': self.get_from_props("image_2_in"),
            'mask_in': self.get_from_props("mask_in"),
            }

        if isinstance(kwargs['mask_in'], str):
            kwargs.pop('mask_in')

        image_out = self.process_cv(fn=cv2.add, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)
