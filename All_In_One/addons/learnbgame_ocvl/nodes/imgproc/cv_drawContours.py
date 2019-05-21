import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, LINE_TYPE_ITEMS


class OCVLdrawContoursNode(OCVLNodeBase):

    n_doc = "Draws contours outlines or filled contours."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input image.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output image.")

    contours_in: bpy.props.StringProperty(default="", update=update_node, description="All the input contours. Each contour is stored as a point vector.")
    contourIdx_in: bpy.props.IntProperty(default=-1, min=-1, max=10, update=update_node, description="Parameter indicating a contour to draw. If it is negative, all the contours are drawn.")
    color_in: bpy.props.FloatVectorProperty(update=update_node, default=(.7, .7, .1, 1.0), size=4, min=0.0, max=1.0, subtype='COLOR', description="Color of the contours.")
    thickness_in: bpy.props.IntProperty(default=2, min=1, max=10, update=update_node, description="Thickness of lines the contours are drawn with. If it is negative (for example, thickness=CV_FILLED ), the contour interiors are drawn.")
    lineType_in: bpy.props.EnumProperty(items=LINE_TYPE_ITEMS, default="LINE_AA",update=update_node, description="Line connectivity. See cv::LineTypes.")
    hierarchy_in: bpy.props.StringProperty(default="", update=update_node, description="Optional information about hierarchy. It is only needed if you want to draw only some of the contours (see maxLevel ).")
    maxLevel_in: bpy.props.IntProperty(default=1, min=0, max=10, update=update_node, description="""Maximal level for drawn contours. If it is 0, only the specified contour is drawn.
        .   If it is 1, the function draws the contour(s) and all the nested contours. If it is 2, the function
        .   draws the contours, all the nested contours, all the nested-to-nested contours, and so on. This
        .   parameter is only taken into account when there is hierarchy available.""")
    offset_in: bpy.props.IntVectorProperty(default=(0, 0), size=2, update=update_node, description="Optional contour shift parameter. Shift all the drawn contours by the specified \f$\texttt{offset}=(dx,dy)\f$ .")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "contours_in")
        self.inputs.new('StringsSocket', "hierarchy_in")
        self.inputs.new('StringsSocket', "contourIdx_in").prop_name = 'contourIdx_in'
        self.inputs.new('SvColorSocket', 'color_in').prop_name = 'color_in'
        self.inputs.new('StringsSocket', "thickness_in").prop_name = 'thickness_in'
        self.inputs.new('StringsSocket', "maxLevel_in").prop_name = 'maxLevel_in'
        self.inputs.new('StringsSocket', "offset_in").prop_name = 'offset_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'image_in': self.get_from_props("image_in"),
            'contours_in': self.get_from_props("contours_in"),
            'hierarchy_in': self.get_from_props("hierarchy_in"),
            'contourIdx_in': self.get_from_props("contourIdx_in"),
            'color_in': self.get_from_props("color_in"),
            'thickness_in': self.get_from_props("thickness_in"),
            'lineType_in': self.get_from_props("lineType_in"),
            'maxLevel_in': self.get_from_props("maxLevel_in"),
            'offset_in': self.get_from_props("offset_in"),
            }

        image_out = self.process_cv(fn=cv2.drawContours, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'lineType_in')
