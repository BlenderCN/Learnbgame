import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLboundingRectNode(OCVLNodeBase):

    n_doc = "Calculates the up-right bounding rectangle of a point set."

    points_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node, description="Input 2D point set, stored in std::vector or Mat.")

    pt1_out: bpy.props.IntVectorProperty(default=(0, 0), size=2, description="Pt1 output.")
    pt2_out: bpy.props.IntVectorProperty(default=(0, 0), size=2, description="Pt2 output.")

    loc_from_findContours: bpy.props.BoolProperty(default=True, update=update_node, description="If linked with findContour node switch to True")

    def init(self, context):
        self.inputs.new('StringsSocket', "points_in")

        self.outputs.new("StringsSocket", "pt1_out")
        self.outputs.new("StringsSocket", "pt2_out")

    def wrapped_process(self):
        self.check_input_requirements(["points_in"])

        kwargs = {
            'points': self.get_from_props("points_in")[0] if self.loc_from_findContours else self.get_from_props("points_in"),
            }

        x, y, w, h = self.process_cv(fn=cv2.boundingRect, kwargs=kwargs)
        pt1_out, pt2_out = (x, y), (x + w, y + h)
        self.refresh_output_socket("pt1_out", pt1_out)
        self.refresh_output_socket("pt2_out", pt2_out)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'loc_from_findContours')
