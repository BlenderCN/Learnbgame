import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, DISTANCE_TYPE_ITEMS


class OCVLfitLineNode(OCVLNodeBase):

    n_doc = "Fits a line to a 2D or 3D point set."

    points_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Input vector of 2D points, stored in std::vector\<\> or Mat")
    distType_in: bpy.props.EnumProperty(items=DISTANCE_TYPE_ITEMS, default="DIST_L1", update=update_node, description="Distance used by the M-estimator, see cv::DistanceTypes.")
    param_in: bpy.props.FloatProperty(default=0, min=0, max=1, description="Numerical parameter ( C ) for some types of distances. If it is 0, an optimal value is chosen.")
    reps_in: bpy.props.FloatProperty(default=0, min=0, max=1, description="Sufficient accuracy for the radius (distance between the coordinate origin and the line).")
    aeps_in: bpy.props.FloatProperty(default=0.01, min=0, max=1, description="Sufficient accuracy for the angle. 0.01 would be a good default value for reps and aeps.")
    loc_from_findContours: bpy.props.BoolProperty(default=True, update=update_node, description="If linked with findContour node switch to True")

    def init(self, context):
        self.inputs.new("StringsSocket", "points_in")
        self.inputs.new("StringsSocket", "param_in").prop_name = "param_in"
        self.inputs.new("StringsSocket", "reps_in").prop_name = "reps_in"
        self.inputs.new("StringsSocket", "aeps_in").prop_name = "aeps_in"

        self.outputs.new("StringsSocket", "pt1_out")
        self.outputs.new("StringsSocket", "pt2_out")

    def wrapped_process(self):
        self.check_input_requirements(["points_in"])

        kwargs = {
            'points_in': self.get_from_props("points_in")[0] if self.loc_from_findContours else self.get_from_props("points_in"),
            'distType_in': self.get_from_props("distType_in"),
            'param_in': self.get_from_props("param_in"),
            'reps_in': self.get_from_props("reps_in"),
            'aeps_in': self.get_from_props("aeps_in"),
            }

        vx, vy, x, y = self.process_cv(fn=cv2.fitLine, kwargs=kwargs)
        self.refresh_output_socket("pt1_out", (vx, vy))
        self.refresh_output_socket("pt2_out", (x, y))

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'loc_from_findContours')
