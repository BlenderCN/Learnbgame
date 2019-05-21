import cv2
import numpy as np
import uuid

import bpy

from ocvl.core.node_base import OCVLNodeBase, update_node, COLOR_DEPTH_ITEMS, BORDER_TYPE_ITEMS


class OCVLsepFilter2dNode(OCVLNodeBase):

    bl_icon = 'FILTER'
    n_doc = "Applies a separable linear filter to an image."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input image.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output image")

    def get_anchor(self):
        return self.get("anchor", (-1, -1))

    def set_anchor(self, value):
        anchor_x = value[0] if -1 <= value[0] < self.kernel_size_in[0] else self.anchor_in[0]
        anchor_y = value[1] if -1 <= value[1] < self.kernel_size_in[1] else self.anchor_in[1]
        self["anchor"] = (anchor_x, anchor_y)

    kernel_size_in: bpy.props.IntVectorProperty(default=(1, 1), update=update_node, min=1, max=30, size=2, description="Coefficients for filtering each row and column.")
    ddepth_in: bpy.props.EnumProperty(items=COLOR_DEPTH_ITEMS, default='CV_8U', update=update_node, description="Destination image depth, see @ref filter_depths 'combinations'")
    anchor_in: bpy.props.IntVectorProperty(default=(-1, -1), update=update_node, get=get_anchor, set=set_anchor, size=2, description="Anchor position within the kernel. The default value \f$(-1,-1)\f$ means that the anchor is at the kernel center.")
    delta_in: bpy.props.IntProperty(default=0, update=update_node, min=0, max=255, description="Value added to the filtered results before storing them.")
    borderType_in: bpy.props.EnumProperty(items=BORDER_TYPE_ITEMS, default='None', update=update_node, description="Pixel extrapolation method, see cv::BorderTypes")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "kernel_size_in").prop_name = 'kernel_size_in'
        self.inputs.new('StringsSocket', "anchor_in").prop_name = 'anchor_in'
        self.inputs.new('StringsSocket', "delta_in").prop_name = 'delta_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kernel_width, kernel_height = self.get_from_props("kernel_size_in")
        kernelX_in = kernelY_in = np.ones((kernel_width, kernel_height), np.float32) / kernel_width * kernel_height
        kwargs = {
            'src': self.get_from_props("image_in"),
            'ddepth_in': self.get_from_props("ddepth_in"),
            'delta_in': self.get_from_props("delta_in"),
            'kernelX_in': kernelX_in,
            'kernelY_in': kernelY_in,
            'anchor_in': self.get_from_props("anchor_in"),
            'borderType_in': self.get_from_props("borderType_in"),
            }

        image_out = self.process_cv(fn=cv2.sepFilter2D, kwargs=kwargs)

        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'ddepth_in')
        self.add_button(layout, 'borderType_in')
