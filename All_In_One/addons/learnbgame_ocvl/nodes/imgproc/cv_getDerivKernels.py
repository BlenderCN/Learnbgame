import uuid

import bpy
import cv2
import numpy as np
from ocvl.core.node_base import OCVLNodeBase, update_node, COEFFICIENTS_TYPE_ITEMS


class OCVLGetDerivKernelsNode(OCVLNodeBase):

    n_doc = "Returns filter coefficients for computing spatial image derivatives."

    kx_out: bpy.props.StringProperty(name="kx_out", default=str(uuid.uuid4()), description="Output matrix of row filter coefficients. It has the type ktype .")
    ky_out: bpy.props.StringProperty(name="ky_out", default=str(uuid.uuid4()), description="Output matrix of column filter coefficients. It has the type ktype .")
    kernel_out: bpy.props.StringProperty(name="kernel_out", default=str(uuid.uuid4()), description="Output kernel.")

    dx_in: bpy.props.IntProperty(default=3, min=1, max=10, update=update_node, description="Derivative order in respect of x.")
    dy_in: bpy.props.IntProperty(default=3, min=1, max=10, update=update_node, description="Derivative order in respect of y.")
    ksize_in: bpy.props.IntProperty(default=1, update=update_node, min=1, max=30, description="Aperture size. It can be CV_SCHARR, 1, 3, 5, or 7.")
    normalize_in: bpy.props.BoolProperty(default=False, update=update_node, description="Flag indicating whether to normalize (scale down) the filter coefficients or not.")
    ktype_in: bpy.props.EnumProperty(items=COEFFICIENTS_TYPE_ITEMS, default='CV_32F', update=update_node, description="Type of filter coefficients. It can be CV_32f or CV_64F.")

    def init(self, context):
        self.inputs.new('StringsSocket', "dx_in").prop_name = 'dx_in'
        self.inputs.new('StringsSocket', "dy_in").prop_name = 'dy_in'
        self.inputs.new('StringsSocket', "ksize_in").prop_name = 'ksize_in'

        self.outputs.new("StringsSocket", "kernel_out")
        self.outputs.new("StringsSocket", "kx_out")
        self.outputs.new("StringsSocket", "ky_out")

    def wrapped_process(self):

        kwargs = {
            'dx_in': self.get_from_props("dx_in"),
            'dy_in': self.get_from_props("dy_in"),
            'ksize_in': self.get_from_props("ksize_in"),
            'normalize_in': self.get_from_props("normalize_in"),
            'ktype_in': self.get_from_props("ktype_in"),
            }

        kx_out, ky_out = self.process_cv(fn=cv2.getDerivKernels, kwargs=kwargs)
        kernel_out = np.outer(kx_out, ky_out)
        self.refresh_output_socket("kx_out", kx_out, is_uuid_type=True)
        self.refresh_output_socket("ky_out", ky_out, is_uuid_type=True)
        self.refresh_output_socket("kernel_out", kernel_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'normalize_in')
        self.add_button(layout, 'ktype_in')
