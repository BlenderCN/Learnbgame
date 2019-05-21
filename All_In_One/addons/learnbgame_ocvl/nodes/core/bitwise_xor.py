import cv2
import uuid
import bpy

from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLbitwise_xorNode(OCVLNodeBase):
    n_doc = "Calculates the per-element bit-wise 'exclusive or' operation on two arrays or an array and a scalar."

    image_1_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node, description="First input array or a scalar.")
    image_2_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node, description="Second input array or a scalar.")
    mask_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node, description="Optional operation mask, 8-bit single channel array, that specifies elements of the output array to be changed.")

    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()))

    def init(self, context):
        self.inputs.new("StringsSocket", "image_1_in")
        self.inputs.new("StringsSocket", "image_2_in")
        self.inputs.new('StringsSocket', "mask_in")

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_1_in", "image_2_in"])

        kwargs = {
            'src1': self.get_from_props("image_1_in"),
            'src2': self.get_from_props("image_2_in"),
            'mask_in': self.get_from_props("mask_in"),
            }

        if isinstance(kwargs['mask_in'], str):
            kwargs.pop('mask_in')

        image_out = self.process_cv(fn=cv2.bitwise_xor, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)
