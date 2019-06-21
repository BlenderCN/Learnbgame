import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLcompleteSymmNode(OCVLNodeBase):

    n_doc = "Copies the lower or the upper half of a square matrix to another half."

    mtx_in: bpy.props.StringProperty(name="mtx_in", default=str(uuid.uuid4()), description="Input-output floating-point square matrix.")

    lowerToUpper_in: bpy.props.BoolProperty(name="lowerToUpper_in", default=False, update=update_node, description="Operation flag; if true, the lower half is copied to the upper half. Otherwise, the upper half is copied to the lower half.")
    mtx_out: bpy.props.StringProperty(name="mtx_out", default=str(uuid.uuid4()), description="Input-output floating-point square matrix.")

    def init(self, context):
        self.inputs.new("StringsSocket", "mtx_in")
        self.inputs.new("StringsSocket", "lowerToUpper_in").prop_name = "lowerToUpper_in"

        self.outputs.new("StringsSocket", "mtx_out")

    def wrapped_process(self):
        self.check_input_requirements(["mtx_in"])

        kwargs = {
            'mtx_in': self.get_from_props("mtx_in"),
            'lowerToUpper_in': self.get_from_props("lowerToUpper_in"),
            }

        mtx_out = self.process_cv(fn=cv2.completeSymm, kwargs=kwargs)
        self.refresh_output_socket("mtx_out", mtx_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
