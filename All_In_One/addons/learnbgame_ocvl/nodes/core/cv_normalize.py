import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, NORMALIZATION_TYPE_ITEMS, COLOR_DEPTH_WITH_NONE_ITEMS


class OCVLnormalizeNode(OCVLNodeBase):

    n_doc = "Normalizes the norm or value range of an array."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input array.")
    alpha_in: bpy.props.FloatProperty(default=0, min=0.0, max=1000, update=update_node, description="Norm value to normalize to or the lower range boundary in case of the range normalization.")
    beta_in: bpy.props.FloatProperty(default=255, min=0.0, max=1000, update=update_node, description="Upper range boundary in case of the range normalization; it is not used for the norm normalization.")
    norm_type_in: bpy.props.EnumProperty(items=NORMALIZATION_TYPE_ITEMS, default="NORM_L2", update=update_node, description="Normalization type (see cv::NormTypes).")
    dtype_in: bpy.props.EnumProperty(items=COLOR_DEPTH_WITH_NONE_ITEMS, default='None', update=update_node, description="Channels as src and the depth =CV_MAT_DEPTH(dtype).")

    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output array.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "alpha_in").prop_name = 'alpha_in'
        self.inputs.new('StringsSocket', "beta_in").prop_name = 'beta_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        image_in = self.get_from_props("image_in")
        dst = image_in.copy()
        dtype_in = self.get_from_props("dtype_in")
        dtype_in = -1 if dtype_in is None else dtype_in
        kwargs = {
            'src': self.get_from_props("image_in"),
            'dst': dst,
            'alpha_in': self.get_from_props("alpha_in"),
            'beta_in': self.get_from_props("beta_in"),
            'norm_type_in': self.get_from_props("norm_type_in"),
            'dtype_in': dtype_in
            }

        image_out = self.process_cv(fn=cv2.normalize, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "norm_type_in")
        self.add_button(layout, "dtype_in", expand=True)
