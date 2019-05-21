import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node

COMPARE_FLAG_ITEMS = (
    ("CMP_EQ", "CMP_EQ", "CMP_EQ", "", 0),
    ("CMP_GT", "CMP_GT", "CMP_GT", "", 1),
    ("CMP_GE", "CMP_GE", "CMP_GE", "", 2),
    ("CMP_LT", "CMP_LT", "CMP_LT", "", 3),
    ("CMP_LE", "CMP_LE", "CMP_LE", "", 4),
    ("CMP_NE", "CMP_NE", "CMP_NE", "", 5),
)


class OCVLcompareNode(OCVLNodeBase):

    n_doc = "Performs the per-element comparison of two arrays or an array and scalar value."

    src1_in: bpy.props.StringProperty(name="src1_in", default=str(uuid.uuid4()), description="First input array or a scalar (in the case of cvCmp, cv.Cmp, cvCmpS, cv.CmpS it is always an array); when it is an array, it must have a single channel.")
    src2_in: bpy.props.StringProperty(name="src2_in", default=str(uuid.uuid4()), description="Second input array or a scalar (in the case of cvCmp and cv.Cmp it is always an array; in the case of cvCmpS, cv.CmpS it is always a scalar); when it is an array, it must have a single channel.")

    cmpop_in: bpy.props.EnumProperty(items=COMPARE_FLAG_ITEMS, default="CMP_EQ", update=update_node, description="""A flag, that specifies correspondence between the arrays:

        CMP_EQ src1 is equal to src2.
        CMP_GT src1 is greater than src2.
        CMP_GE src1 is greater than or equal to src2.
        CMP_LT src1 is less than src2.
        CMP_LE src1 is less than or equal to src2.
        CMP_NE src1 is unequal to src2.
        """)

    dst_out: bpy.props.StringProperty(name="dst_out", default=str(uuid.uuid4()), description="Output array that has the same size and type as the input arrays.")

    def init(self, context):
        self.inputs.new("StringsSocket", "src1_in")
        self.inputs.new("StringsSocket", "src2_in")

        self.outputs.new("StringsSocket", "dst_out")

    def wrapped_process(self):
        self.check_input_requirements(["src1_in", "src2_in"])

        kwargs = {
            'src1_in': self.get_from_props("src1_in"),
            'src2_in': self.get_from_props("src2_in"),
            'cmpop_in': self.get_from_props("cmpop_in"),
            }

        dst_out = self.process_cv(fn=cv2.compare, kwargs=kwargs)
        self.refresh_output_socket("dst_out", dst_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "cmpop_in")
