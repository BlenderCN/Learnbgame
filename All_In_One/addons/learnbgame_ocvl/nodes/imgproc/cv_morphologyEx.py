import uuid

import bpy
import cv2
import numpy as np
from ocvl.core.node_base import OCVLNodeBase, update_node, MORPH_TYPE_ITEMS, BORDER_TYPE_ITEMS


class OCVLmorphologyExNode(OCVLNodeBase):

    bl_icon = 'FILTER'
    n_doc = "Performs advanced morphological transformations."

    def get_anchor(self):
        return self.get("anchor_in", (-1, -1))

    def set_anchor(self, value):
        anchor_x = value[0] if -1 <= value[0] < self.ksize_in[0] else self.anchor_in[0]
        anchor_y = value[1] if -1 <= value[1] < self.ksize_in[1] else self.anchor_in[1]
        self["anchor_in"] = (anchor_x, anchor_y)

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Source image. The number of channels can be arbitrary. The depth should be one of CV_8U, CV_16U, CV_16S, CV_32F` or ``CV_64F.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Destination image of the same size and type as src .")

    ksize_in: bpy.props.IntVectorProperty(default=(3, 3), update=update_node, min=1, max=30, size=2, description="Structuring element used for erosion.")
    anchor_in: bpy.props.IntVectorProperty(default=(-1, -1), update=update_node, get=get_anchor, set=set_anchor, size=2, description="Position of the anchor within the element.")
    iterations_in: bpy.props.IntProperty(default=2, min=1, max=10, update=update_node, description="Number of times erosion is applied.")
    op_in: bpy.props.EnumProperty(items=MORPH_TYPE_ITEMS, default='MORPH_BLACKHAT', update=update_node, description="Type of a morphological operation, see cv::MorphTypes.")
    borderType_in: bpy.props.EnumProperty(items=BORDER_TYPE_ITEMS, default='None', update=update_node, description="Border mode used to extrapolate pixels outside of the image, see cv::BorderTypes")

    def init(self, context):
        self.width = 150
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "ksize_in").prop_name = 'ksize_in'
        self.inputs.new('StringsSocket', "anchor_in").prop_name = 'anchor_in'
        self.inputs.new('StringsSocket', "iterations_in").prop_name = 'iterations_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kernel = np.array(self.get_from_props("ksize_in"))
        kwargs = {
            'src': self.get_from_props("image_in"),
            'kernel': kernel,
            'anchor_in': self.get_from_props("anchor_in"),
            'iterations_in': self.get_from_props("iterations_in"),
            'op_in': self.get_from_props("op_in"),
            'borderType_in': self.get_from_props("borderType_in"),
            }

        image_out = self.process_cv(fn=cv2.morphologyEx, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'op_in')
        self.add_button(layout, 'borderType_in')
