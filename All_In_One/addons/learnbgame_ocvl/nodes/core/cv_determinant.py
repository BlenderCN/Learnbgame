import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


class OCVLdeterminantNode(OCVLNodeBase):

    n_doc = "Returns the determinant of a square floating-point matrix."

    mtx_in: bpy.props.StringProperty(name="mtx_in", default=str(uuid.uuid4()), description="Input matrix that must have CV_32FC1 or CV_64FC1 type and square size.")
    retval_out: bpy.props.FloatProperty(name="retval_out", description="")

    def init(self, context):
        self.inputs.new("StringsSocket", "mtx_in")
        self.outputs.new("StringsSocket", "retval_out")

    def wrapped_process(self):
        self.check_input_requirements(["mtx_in"])

        kwargs = {
            'mtx_in': self.get_from_props("mtx_in"),
            }

        retval_out = self.process_cv(fn=cv2.determinant, kwargs=kwargs)
        self.refresh_output_socket("retval_out", retval_out)

    def draw_buttons(self, context, layout):
        pass
