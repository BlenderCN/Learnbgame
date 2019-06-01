import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


class OCVLequalizeHistNode(OCVLNodeBase):

    n_doc = "Equalizes the histogram of a grayscale image."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Source 8-bit single channel image.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output image.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'src': self.get_from_props("image_in"),
        }

        image_out = self.process_cv(fn=cv2.equalizeHist, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)
