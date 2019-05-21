import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


class OCVLexpNode(OCVLNodeBase):

    n_doc = "Calculates the exponent of every array element."

    src_in: bpy.props.StringProperty(name="src_in", default=str(uuid.uuid4()), description="Input array.")
    dst_out: bpy.props.StringProperty(name="dst_out", default=str(uuid.uuid4()), description="Output array of the same size and type as input array.")

    def init(self, context):
        self.inputs.new("StringsSocket", "src_in")
        self.outputs.new("StringsSocket", "dst_out")

    def wrapped_process(self):
        self.check_input_requirements(["src_in"])

        kwargs = {
            'src_in': self.get_from_props("src_in"),
            }

        dst_out = self.process_cv(fn=cv2.exp, kwargs=kwargs)
        self.refresh_output_socket("dst_out", dst_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
