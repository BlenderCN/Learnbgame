import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, COLOR_DEPTH_ITEMS, BORDER_TYPE_ITEMS


class OCVLScharrNode(OCVLNodeBase):

    n_doc = "Calculates the first x- or y- image derivative using Scharr operator."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input image.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output image.")

    dx_in: bpy.props.IntProperty(default=1, min=0, max=1, update=update_node, description="Order of the derivative x.")
    dy_in: bpy.props.IntProperty(default=0, min=0, max=1, update=update_node, description="Order of the derivative y.")
    ddepth_in: bpy.props.EnumProperty(items=COLOR_DEPTH_ITEMS, default='CV_8U', update=update_node, description="Output image depth, see @ref filter_depths 'combinations'.")
    scale_in: bpy.props.FloatProperty(default=1.0, min=1, max=8, update=update_node, description="Optional scale factor for the computed Laplacian values.")
    delta_in: bpy.props.FloatProperty(default=0.0, min=0, max=255, update=update_node, description="Optional delta value that is added to the results prior to storing them in dst.")
    borderType_in: bpy.props.EnumProperty(items=BORDER_TYPE_ITEMS, default='None', update=update_node, description="Pixel extrapolation method, see cv::BorderTypes")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "dx_in").prop_name = 'dx_in'
        self.inputs.new('StringsSocket', "dy_in").prop_name = 'dy_in'
        self.inputs.new('StringsSocket', "scale_in").prop_name = 'scale_in'
        self.inputs.new('StringsSocket', "delta_in").prop_name = 'delta_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'src': self.get_from_props("image_in"),
            'ddepth_in': self.get_from_props("ddepth_in"),
            'dx_in': self.get_from_props("dx_in"),
            'dy_in': self.get_from_props("dy_in"),
            'scale_in': self.get_from_props("scale_in"),
            'delta_in': self.get_from_props("delta_in"),
            'borderType_in': self.get_from_props("borderType_in"),
            }

        image_out = self.process_cv(fn=cv2.Scharr, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'borderType_in')
        self.add_button(layout, 'ddepth_in')
