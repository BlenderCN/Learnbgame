import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


class OCVLinvertAffineTransformNode(OCVLNodeBase):

    n_doc = "Inverts an affine transformation."

    matrix_invert_in: bpy.props.StringProperty(name="matrix_invert_in", default=str(uuid.uuid4()), description="Original affine transformation.")
    matrix_invert_out: bpy.props.StringProperty(name="matrix_invert_out", default=str(uuid.uuid4()), description="Output reverse affine transformation.")

    def init(self, context):
        self.inputs.new("StringsSocket", "matrix_invert_in")
        self.outputs.new("StringsSocket", "matrix_invert_out")

    def wrapped_process(self):
        self.check_input_requirements(["matrix_invert_in"])

        kwargs = {
            'M_in': self.get_from_props("matrix_invert_in"),
            }

        matrix_invert_out = self.process_cv(fn=cv2.invertAffineTransform, kwargs=kwargs)
        self.refresh_output_socket("matrix_invert_out", matrix_invert_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
