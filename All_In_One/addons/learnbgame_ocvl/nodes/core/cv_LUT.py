import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


class OCVLLUTNode(OCVLNodeBase):

    n_doc = "Performs a look-up table transform of an array."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input array of 8-bit elements.")
    lut_in: bpy.props.StringProperty(name="lut_in", default=str(uuid.uuid4()), description="Look-up table of 256 elements; in case of multi-channel input array, the table should either have a single channel (in this case the same table is used for all channels) or the same number of channels as in the input array.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output array of the same size and number of channels as src, and the same depth as lut.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "lut_in")

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in", "lut_in"])

        kwargs = {
            'src': self.get_from_props("image_in"),
            'lut_in': self.get_from_props("lut_in"),
        }

        image_out = self.process_cv(fn=cv2.LUT, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)
