import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


class OCVLboxPointsNode(OCVLNodeBase):

    n_doc = "Finds the four vertices of a rotated rect. Useful to draw the rotated rectangle."

    rect_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Points and angle in one list.")

    def init(self, context):
        self.inputs.new("StringsSocket", "rect_in")
        self.outputs.new("StringsSocket", "points_out")

    def wrapped_process(self):
        self.check_input_requirements(["rect_in"])

        kwargs = {
            'box': tuple(self.get_from_props("rect_in")),
            }

        points_out = self.process_cv(fn=cv2.boxPoints, kwargs=kwargs)
        self.refresh_output_socket("points_out", points_out)

    def draw_buttons(self, context, layout):
        pass
