import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLfitEllipseNode(OCVLNodeBase):

    n_doc = "Fits an ellipse around a set of 2D points."

    points_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Input vector of 2D points, stored in std::vector\<\> or Mat")
    ellipse_out: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Output ellipse.")
    loc_from_findContours: bpy.props.BoolProperty(default=True, update=update_node, description="If linked with findContour node switch to True")

    def init(self, context):
        self.inputs.new("StringsSocket", "points_in")
        self.outputs.new("StringsSocket", "ellipse_out")

    def wrapped_process(self):
        self.check_input_requirements(["points_in"])

        kwargs = {
            'points': self.get_from_props("points_in")[0] if self.loc_from_findContours else self.get_from_props("points_in"),
            }

        ellipse_out = self.process_cv(fn=cv2.fitEllipse, kwargs=kwargs)
        self.refresh_output_socket("ellipse_out", ellipse_out)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'loc_from_findContours')
