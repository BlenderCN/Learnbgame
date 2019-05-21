import cv2
import uuid

import bpy

from ocvl.core.node_base import OCVLNodeBase, update_node


COMPARE_FLAG_ITEMS = (
    ("CMP_EQ", "CMP_EQ", "CMP_EQ", "", 0),
    ("CMP_GT", "CMP_GT", "CMP_GT", "", 1),
    ("CMP_GE", "CMP_GE", "CMP_GE", "", 2),
    ("CMP_LT", "CMP_LT", "CMP_LT", "", 3),
    ("CMP_LE", "CMP_LE", "CMP_LE", "", 4),
    ("CMP_NE", "CMP_NE", "CMP_NE", "", 5),
)


class OCVLcalcCovarMatrixNode(OCVLNodeBase):

    n_doc = "Calculates the covariance matrix of a set of vectors."
    bl_flags_list = 'CV_COVAR_SCRAMBLED, CV_COVAR_NORMAL, CV_COVAR_USE_AVG, CV_COVAR_SCALE, CV_COVAR_ROWS, CV_COVAR_COLS'


    samples_in: bpy.props.StringProperty(name="samples_in", default=str(uuid.uuid4()), description="Samples stored either as separate matrices or as rows/columns of a single matrix.")
    mean_in: bpy.props.IntProperty(name="mean_in", default=10, update=update_node, description="Input or output (depending on the flags) array as the average value of the input vectors.")
    flags_in: bpy.props.BoolVectorProperty(default=[False for i in bl_flags_list.split(",")], size=len(bl_flags_list.split(",")), update=update_node, subtype="NONE", description=bl_flags_list)

    covar_out: bpy.props.StringProperty(name="covar_out", default=str(uuid.uuid4()), description="Output covariance matrix of the type ctype and square size.")
    mean_out: bpy.props.IntProperty(name="mean_out", description="Output (depending on the flags) array as the average value of the input vectors.")

    def init(self, context):
        self.inputs.new("StringsSocket", "samples_in")
        self.inputs.new("StringsSocket", "mean_out").prop_name = "mean_in"

        self.outputs.new("StringsSocket", "covar_out")
        self.outputs.new("StringsSocket", "mean_out")

    def wrapped_process(self):
        self.check_input_requirements(["samples_in"])

        kwargs = {
            'samples_in': self.get_from_props("samples_in"),
            'flags_in': self.get_from_props("flags_in"),
            'mean_in': self.get_from_props("mean_in"),
            }

        covar_out, mean_out = self.process_cv(fn=cv2.calcCovarMatrix, kwargs=kwargs)
        self.refresh_output_socket("covar_out", covar_out, is_uuid_type=True)
        self.refresh_output_socket("mean_out", mean_out)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "flags_in")
