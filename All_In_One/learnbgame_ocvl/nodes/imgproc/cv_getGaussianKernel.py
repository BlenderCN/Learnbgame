import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, COEFFICIENTS_TYPE_ITEMS


class OCVLgetGaussianKernelNode(OCVLNodeBase):

    n_doc = "Returns Gaussian filter coefficients."

    kernel_out: bpy.props.StringProperty(name="kernel_out", default=str(uuid.uuid4()), description="Output kernel.")

    ksize_in: bpy.props.IntProperty(default=5, update=update_node, min=1, max=30, description="Aperture size. It should be odd.")
    sigma_in: bpy.props.FloatProperty(default=0.35, min=0, max=1, update=update_node, description="Gaussian standard deviation.")
    # normalize_in: bpy.props.BoolProperty(default=False, update=update_node,
    #     description='Flag indicating whether to normalize (scale down) the filter coefficients or not.')
    ktype_in: bpy.props.EnumProperty(items=COEFFICIENTS_TYPE_ITEMS, default='CV_32F', update=update_node, description="Type of filter coefficients. It can be CV_32f or CV_64F.")

    def init(self, context):
        self.inputs.new('StringsSocket', "ksize_in").prop_name = 'ksize_in'
        self.inputs.new('StringsSocket', "sigma_in").prop_name = 'sigma_in'

        self.outputs.new("StringsSocket", "kernel_out")

    def wrapped_process(self):

        kwargs = {
            'ksize_in': self.get_from_props("ksize_in"),
            'sigma_in': self.get_from_props("sigma_in"),
            'ktype_in': self.get_from_props("ktype_in"),
            }

        kernel_out = self.process_cv(fn=cv2.getGaussianKernel, kwargs=kwargs)
        self.refresh_output_socket("kernel_out", kernel_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'ktype_in')
