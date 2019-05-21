import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, INTERPOLATION_ITEMS, BORDER_TYPE_ITEMS


class OCVLremapNode(OCVLNodeBase):

    n_doc = "Applies a generic geometrical transformation to an image."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input image.")
    map1_in: bpy.props.StringProperty(name="map1_in", default=str(uuid.uuid4()), description="The first map of either (x,y) points or just x values having the type CV_16SC2 , CV_32FC1 , or CV_32FC2 .")
    map2_in: bpy.props.StringProperty(name="map2_in", default=str(uuid.uuid4()), description="The second map of y values having the type CV_16UC1 , CV_32FC1 , or none (empty map if map1 is (x,y) points), respectively.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output image. It has the same size as map1 and the same type as src .")

    interpolation_in: bpy.props.EnumProperty(items=INTERPOLATION_ITEMS, default='INTER_NEAREST', update=update_node, description="Interpolation method.")
    borderMode_in: bpy.props.EnumProperty(items=BORDER_TYPE_ITEMS, default='None', update=update_node, description="Border mode used to extrapolate pixels outside of the image, see cv::BorderTypes.")
    borderValue_in: bpy.props.IntProperty(default=0, min=0, max=255, update=update_node, description="Value used in case of a constant border; by default, it equals 0.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new("StringsSocket", "map1_in")
        self.inputs.new("StringsSocket", "map2_in")
        self.inputs.new('StringsSocket', "borderValue_in").prop_name = 'borderValue_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in", "map1_in", "map2_in"])

        kwargs = {
            'src_in': self.get_from_props("image_in"),
            'map1_in': self.get_from_props("map1_in"),
            'map2_in': self.get_from_props("map2_in"),
            'interpolation_in': self.get_from_props("interpolation_in"),
            'borderMode_in': self.get_from_props("borderMode_in"),
            'borderValue_in': self.get_from_props("borderValue_in"),
            }

        image_out = self.process_cv(fn=cv2.remap, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'interpolation_in')
        self.add_button(layout, 'borderMode_in')
