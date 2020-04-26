import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLinvertNode(OCVLNodeBase):

    n_doc ="Finds the inverse or pseudo-inverse of a matrix."
    bl_flags_list = 'DECOMP_LU, DECOMP_SVD, DECOMP_CHOLESKY'

    src_in: bpy.props.StringProperty(name="src_in", default=str(uuid.uuid4()), description="Input floating-point M x N matrix.")
    flags_in: bpy.props.BoolVectorProperty(default=[False for i in bl_flags_list.split(",")], size=len(bl_flags_list.split(",")), update=update_node, subtype="NONE", description=bl_flags_list)

    dst_out: bpy.props.StringProperty(name="dst_out", default=str(uuid.uuid4()), description="Output matrix of N x M size and the same type as src.")
    retval_out: bpy.props.StringProperty(name="retval_out", default=str(uuid.uuid4()), description="Return value.")

    def init(self, context):
        self.inputs.new("StringsSocket", "src_in")

        self.outputs.new("StringsSocket", "dst_out")
        self.outputs.new("StringsSocket", "retval_out")

    def wrapped_process(self):
        self.check_input_requirements(["src_in"])

        kwargs = {
            'src_in': self.get_from_props("src_in"),
            'flags_in': self.get_from_props("flags_in"),
            }

        retval_out, dst_out = self.process_cv(fn=cv2.invert, kwargs=kwargs)
        self.refresh_output_socket("dst_out", dst_out, is_uuid_type=True)
        self.refresh_output_socket("retval_out", retval_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "flags_in")
