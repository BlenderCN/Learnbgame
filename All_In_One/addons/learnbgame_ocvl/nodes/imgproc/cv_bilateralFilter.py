import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, BORDER_TYPE_ITEMS


class OCVLbilateralFilterNode(OCVLNodeBase):

    bl_icon = 'FILTER'
    n_doc = "Applies the bilateral filter to an image."

    d_in: bpy.props.IntProperty(default=2, min=1, max=10, update=update_node, description="Diameter of each pixel neighborhood that is used during filtering. If it is non-positive, it is computed from sigmaSpace.")
    sigmaColor_in: bpy.props.FloatProperty(default=75, min=0, max=255, update=update_node, description="Filter sigma in the color space.")
    sigmaSpace_in: bpy.props.FloatProperty(default=75, min=0, max=255, update=update_node, description="Filter sigma in the coordinate space.")
    borderType_in: bpy.props.EnumProperty(items=BORDER_TYPE_ITEMS, default='None', update=update_node, description="Border mode used to extrapolate pixels outside of the image, see cv::BorderTypes.")

    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output image.")

    def init(self, context):
        self.width = 150
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "d_in").prop_name = 'd_in'
        self.inputs.new('StringsSocket', "sigmaColor_in").prop_name = 'sigmaColor_in'
        self.inputs.new('StringsSocket', "sigmaSpace_in").prop_name = 'sigmaSpace_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'src': self.get_from_props("image_in"),
            'd_in': self.get_from_props("d_in"),
            'sigmaColor_in': self.get_from_props("sigmaColor_in"),
            'sigmaSpace_in': self.get_from_props("sigmaSpace_in"),
            'borderType_in': self.get_from_props("borderType_in"),
            }

        image_out = self.process_cv(fn=cv2.bilateralFilter, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'borderType_in')
