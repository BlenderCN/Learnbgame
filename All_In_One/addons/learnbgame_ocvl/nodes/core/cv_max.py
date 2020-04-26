import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


class OCVLmaxNode(OCVLNodeBase):

    n_doc = "Calculates per-element maximum of two arrays or an array and a scalar."

    n_id: bpy.props.StringProperty(default='')
    n_meta: bpy.props.StringProperty(default='')
    src1_in: bpy.props.StringProperty(name="src1_in", default=str(uuid.uuid4()), description="First input array.")
    src2_in: bpy.props.StringProperty(name="src2_in", default=str(uuid.uuid4()), description="Second input array of the same size and type as src1.")

    array_out: bpy.props.StringProperty(name="array_out", default=str(uuid.uuid4()), description="Output array of the same size and type as src1.")

    def init(self, context):
        self.inputs.new("StringsSocket", "src1_in")
        self.inputs.new("StringsSocket", "src2_in")
        self.outputs.new("StringsSocket", "array_out")

    def wrapped_process(self):
        self.check_input_requirements(["src1_in", "src2_in"])

        kwargs = {
            'src1_in': self.get_from_props("src1_in"),
            'src2_in': self.get_from_props("src2_in"),
            }

        array_out = self.process_cv(fn=cv2.max, kwargs=kwargs)
        self.refresh_output_socket("array_out", array_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
