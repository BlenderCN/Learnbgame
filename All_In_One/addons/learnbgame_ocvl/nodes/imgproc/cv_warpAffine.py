import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, BORDER_TYPE_ITEMS


class OCVLwarpAffineNode(OCVLNodeBase):

    bl_flags_list = 'INTER_LINEAR, INTER_NEAREST, WARP_INVERSE_MAP'
    n_doc = "Applies an affine transformation to an image."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input image.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output image.")

    M_in: bpy.props.StringProperty(name="M_in", default=str(uuid.uuid4()), description="Transformation matrix.")

    dsize_in: bpy.props.IntVectorProperty(default=(100, 100), update=update_node, min=1, max=2028, size=2, description="Size of the output image.")
    flags_in: bpy.props.BoolVectorProperty(default=[False for i in bl_flags_list.split(",")], size=len(bl_flags_list.split(",")), update=update_node, subtype="NONE", description=bl_flags_list)
    borderMode_in: bpy.props.EnumProperty(items=BORDER_TYPE_ITEMS, default='None', update=update_node, description="Border mode used to extrapolate pixels outside of the image, see cv::BorderTypes")
    borderValue_in: bpy.props.EnumProperty(items=BORDER_TYPE_ITEMS, default='None', update=update_node, description="Border mode used to extrapolate pixels outside of the image, see cv::BorderTypes")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "M_in")
        self.inputs.new('StringsSocket', "dsize_in").prop_name = 'dsize_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in", "M_in"])

        kwargs = {
            'src': self.get_from_props("image_in"),
            'M_in': self.get_from_props("M_in"),
            'dsize_in': self.get_from_props("dsize_in"),
            'flags_in': self.get_from_props("flags_in"),
            }

        image_out = self.process_cv(fn=cv2.warpAffine, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "flags_in")
