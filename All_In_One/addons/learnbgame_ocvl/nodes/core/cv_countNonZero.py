import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


class OCVLcountNonZeroNode(OCVLNodeBase):

    n_doc = "Counts non-zero array elements."

    src_in: bpy.props.StringProperty(name="src", default=str(uuid.uuid4()), description="First input single channel array or a scalar.")
    retval_out: bpy.props.IntProperty(name="retval", default=0, description="")

    def init(self, context):
        self.inputs.new("StringsSocket", "src_in")
        self.outputs.new("StringsSocket", "retval_out")

    def wrapped_process(self):
        self.check_input_requirements(["src_in"])

        kwargs = {
            'src_in': self.get_from_props("src_in"),
            }

        retval_out = self.process_cv(fn=cv2.countNonZero, kwargs=kwargs)
        self.refresh_output_socket("retval_out", retval_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
