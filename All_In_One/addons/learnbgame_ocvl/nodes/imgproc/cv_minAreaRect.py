import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLminAreaRectNode(OCVLNodeBase):

    n_doc = "Finds a rotated rectangle of the minimum area enclosing the input 2D point set."

    points_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Input vector of 2D points, stored in std::vector\<\> or Mat")
    loc_from_findContours: bpy.props.BoolProperty(default=True, update=update_node, description="If linked with findContour node switch to True")

    def init(self, context):
        self.inputs.new("StringsSocket", "points_in")
        self.outputs.new("StringsSocket", "points_out")

    def wrapped_process(self):
        self.check_input_requirements(["points_in"])

        kwargs = {
            'points_in': self.get_from_props("points_in")[0] if self.loc_from_findContours else self.get_from_props("points_in"),
            }

        points_out = tuple(self.process_cv(fn=cv2.minAreaRect, kwargs=kwargs))
        self.refresh_output_socket("points_out", points_out)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'loc_from_findContours')
