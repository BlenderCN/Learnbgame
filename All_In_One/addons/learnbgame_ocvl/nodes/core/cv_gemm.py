import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


INPUT_NODE_ITEMS = (
    ("DOUBLE", "DOUBLE", "DOUBLE", "", 0),
    ("TRIPLE", "TRIPLE", "TRIPLE", "", 1),
)


PROPS_MAPS = {
    INPUT_NODE_ITEMS[0][0]: (),
    INPUT_NODE_ITEMS[1][0]: ("src_3_in", "beta_in"),
    }


class OCVLgemmNode(OCVLNodeBase):
    n_doc = "Performs generalized matrix multiplication."
    bl_flags_list = 'GEMM_1_T, GEMM_2_T, GEMM_3_T'

    src_1_in: bpy.props.StringProperty(name="src_1_in", default=str(uuid.uuid4()), description="First multiplied input matrix that could be real(CV_32FC1, CV_64FC1) or complex(CV_32FC2, CV_64FC2).")
    src_2_in: bpy.props.StringProperty(name="src_2_in", default=str(uuid.uuid4()), description="Second multiplied input matrix of the same type as src1.")
    src_3_in: bpy.props.StringProperty(name="src_3_in", default=str(uuid.uuid4()), description="Third optional delta matrix added to the matrix product; it should have the same type as src1 and src2.")
    flags_in: bpy.props.BoolVectorProperty(default=[False for i in bl_flags_list.split(",")], size=len(bl_flags_list.split(",")), update=update_node, subtype="NONE", description=bl_flags_list)
    alpha_in: bpy.props.FloatProperty(default=0.5, min=0, max=100, description="Weight of the matrix product.")
    beta_in: bpy.props.FloatProperty(default=0.5, min=0, max=100, description="Weight of src3.")

    dst_out: bpy.props.StringProperty(name="dst_out", default=str(uuid.uuid4()), description="Output matrix; it has the proper size and the same type as input matrices.")

    def init(self, context):
        self.inputs.new("StringsSocket", "src_1_in")
        self.inputs.new("StringsSocket", "src_2_in")
        self.inputs.new("StringsSocket", "src_3_in")
        self.inputs.new("StringsSocket", "alpha_in").prop_name = "alpha_in"
        self.inputs.new("StringsSocket", "beta_in").prop_name = "beta_in"

        self.outputs.new("StringsSocket", "dst_out")

    def wrapped_process(self):
        self.check_input_requirements(["src_1_in", "src_2_in", "src_3_in"])

        kwargs = {
            'src1_in': self.get_from_props("src_1_in"),
            'src2_in': self.get_from_props("src_2_in"),
            'src3_in': self.get_from_props("src_3_in"),
            'flags_in': self.get_from_props("flags_in"),
            'alpha_in': self.get_from_props("alpha_in"),
            'beta_in': self.get_from_props("beta_in"),
            }

        dst_out = self.process_cv(fn=cv2.gemm, kwargs=kwargs)
        self.refresh_output_socket("dst_out", dst_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "flags_in")
