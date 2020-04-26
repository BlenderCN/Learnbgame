import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLapproxPolyDPNode(OCVLNodeBase):

    n_doc = "Approximates a polygonal curve(s) with the specified precision."

    curve_in: bpy.props.StringProperty(name="curve_in", default=str(uuid.uuid4()), description="Input vector of a 2D point stored in std::vector or Mat.")
    epsilon_in: bpy.props.FloatProperty(default=0.1, description="Parameter specifying the approximation accuracy. This is the maximum distance")
    closed_in: bpy.props.BoolProperty(default=False, update=update_node, description="If true, the approximated curve is closed (its first and last vertices are connected). Otherwise, it is not closed.")

    approxCurve_out: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Result of the approximation. The type should match the type of the input curve.")

    loc_from_findContours: bpy.props.BoolProperty(default=True, update=update_node, description="If linked with findContour node switch to True")

    def init(self, context):
        self.inputs.new("StringsSocket", "curve_in")
        self.inputs.new("StringsSocket", "epsilon_in").prop_name = "epsilon_in"

        self.outputs.new("StringsSocket", "approxCurve_out").prop_name = "approxCurve_out"

    def wrapped_process(self):
        self.check_input_requirements(["curve_in"])

        kwargs = {
            'curve_in': self.get_from_props("curve_in")[0] if self.loc_from_findContours else self.get_from_props("curve_in"),
            'epsilon_in': self.get_from_props("epsilon_in"),
            'closed_in': self.get_from_props("closed_in"),
            }

        approxCurve_out = self.process_cv(fn=cv2.approxPolyDP, kwargs=kwargs)
        self.refresh_output_socket("approxCurve_out", approxCurve_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'closed_in')
        self.add_button(layout, 'loc_from_findContours')
