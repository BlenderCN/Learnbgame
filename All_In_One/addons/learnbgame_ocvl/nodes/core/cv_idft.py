import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLidftNode(OCVLNodeBase):

    n_doc = "Calculates the inverse Discrete Fourier Transform of a 1D or 2D array."
    bl_flags_list = 'DFT_INVERSE, DFT_SCALE, DFT_ROWS, DFT_COMPLEX_OUTPUT, DFT_REAL_OUTPUT'

    src_in: bpy.props.StringProperty(name="src_in", default=str(uuid.uuid4()), description="Input floating-point real or complex array.")
    flags_in: bpy.props.BoolVectorProperty(default=[False for i in bl_flags_list.split(",")], size=len(bl_flags_list.split(",")), update=update_node, subtype="NONE", description=bl_flags_list)
    nonzeroRows_in: bpy.props.IntProperty(default=0, min=0, update=update_node, description="Number of dst rows to process.")

    dst_out: bpy.props.StringProperty(name="dst_out", default=str(uuid.uuid4()), description="Output array whose size and type depend on the flags.")

    def init(self, context):
        self.inputs.new("StringsSocket", "src_in")
        self.inputs.new("StringsSocket", "nonzeroRows_in").prop_name = "nonzeroRows_in"

        self.outputs.new("StringsSocket", "dst_out")

    def wrapped_process(self):
        self.check_input_requirements(["src_in"])

        kwargs = {
            'src_in': self.get_from_props("src_in"),
            'nonzeroRows_in': self.get_from_props("nonzeroRows_in"),
            'flags_in': self.get_from_props("flags_in"),
            }

        dst_out = self.process_cv(fn=cv2.idft, kwargs=kwargs)
        self.refresh_output_socket("dst_out", dst_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "flags_in")
