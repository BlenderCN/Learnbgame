import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLconvexHullNode(OCVLNodeBase):

    n_doc = "Finds the convex hull of a point set."

    hull_out: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Output convex hull. It is either an integer vector of indices or vector of points.")
    points_in: bpy.props.StringProperty(name="points_in", default=str(uuid.uuid4()), description="Input 2D point set, stored in std::vector or Mat.")
    clockwise_in: bpy.props.BoolProperty(default=False, update=update_node, description="Orientation flag. If it is true, the output convex hull is oriented clockwise.")
    returnPoints_in: bpy.props.BoolProperty(default=False, update=update_node, description="Operation flag. In case of a matrix, when the flag is true, the function returns convex hull points.")
    loc_from_findContours: bpy.props.BoolProperty(default=True, update=update_node, description="If linked with findContour node switch to True")

    def init(self, context):
        self.inputs.new("StringsSocket", "points_in")
        self.outputs.new("StringsSocket", "hull_out")

    def wrapped_process(self):
        self.check_input_requirements(["points_in"])

        kwargs = {
            'points_in': self.get_from_props("points_in")[0] if self.loc_from_findContours else self.get_from_props("points_in"),
            'clockwise_in': self.get_from_props("clockwise_in"),
            'returnPoints_in': self.get_from_props("returnPoints_in"),
            }

        hull_out = self.process_cv(fn=cv2.convexHull, kwargs=kwargs)
        self.refresh_output_socket("hull_out", hull_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'clockwise_in')
        self.add_button(layout, 'returnPoints_in')
        self.add_button(layout, 'loc_from_findContours')
