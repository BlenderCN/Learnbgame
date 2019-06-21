import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


class OCVLMahalanobisNode(OCVLNodeBase):

    n_doc = "Calculates the Mahalanobis distance between two vectors."

    v1_in: bpy.props.StringProperty(name="v1_in", default=str(uuid.uuid4()), description="First 1D input vector.")
    v2_in: bpy.props.StringProperty(name="v2_in", default=str(uuid.uuid4()), description="Second 1D input vector.")
    icovar_in: bpy.props.StringProperty(name="icovar_in", default=str(uuid.uuid4()), description="Inverse covariance matrix.")

    retval_out: bpy.props.StringProperty(name="retval_out", default=str(uuid.uuid4()), description="Return value.")

    def init(self, context):
        self.inputs.new("StringsSocket", "v1_in")
        self.inputs.new("StringsSocket", "v2_in")
        self.inputs.new("StringsSocket", "icovar_in")

        self.outputs.new("StringsSocket", "retval_out")

    def wrapped_process(self):
        self.check_input_requirements(["v1_in", "v2_in", "icovar_in"])

        kwargs = {
            'v1_in': self.get_from_props("v1_in"),
            'v2_in': self.get_from_props("v2_in"),
            'icovar_in': self.get_from_props("icovar_in"),
            }

        retval_out = self.process_cv(fn=cv2.Mahalanobis, kwargs=kwargs)
        self.refresh_output_socket("retval_out", retval_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
