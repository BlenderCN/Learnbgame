import uuid

import bpy
import cv2
import numpy as np
from ocvl.core.node_base import OCVLNodeBase, update_node

INPUT_NODE_ITEMS = (
    ("FULL", "FULL", "FULL", "", 0),
    ("SIMPLE", "SIMPLE", "SIMPLE", "", 1),
)


PROPS_MAPS = {
    INPUT_NODE_ITEMS[0][0]: ("center_in", "axes_in", "angle_in", "startAngle_in", "endAngle_in"),
    INPUT_NODE_ITEMS[1][0]: ("box_in",),
    }


class OCVLellipse2PolyNode(OCVLNodeBase):

    bl_icon = 'GREASEPENCIL'
    n_doc = "Approximates an elliptic arc with a polyline."

    center_in: bpy.props.IntVectorProperty(default=(0, 0), size=2, update=update_node, description="Center of the ellipse.")
    axes_in: bpy.props.IntVectorProperty(default=(1, 1), size=2, min=0, max=1000, update=update_node, description="Half of the size of the ellipse main axes.")
    angle_in: bpy.props.IntProperty(default=30, min=0, max=360, update=update_node, description="Ellipse rotation angle in degrees.")
    arcStart_in: bpy.props.IntProperty(default=0, min=0, max=360, update=update_node, description="Starting angle of the elliptic arc in degrees.")
    arcEnd_in: bpy.props.IntProperty(default=270, min=0, max=360, update=update_node, description="Ending angle of the elliptic arc in degrees.")
    delta_in: bpy.props.IntProperty(default=40, min=0, max=360, update=update_node, description="Angle between the subsequent polyline vertices. It defines the approximation accuracy.")

    pts_out: bpy.props.StringProperty(name="pts_out", default=str(uuid.uuid4()), description="Output vector of polyline vertices.")

    def init(self, context):
        self.inputs.new('SvColorSocket', 'center_in').prop_name = 'center_in'
        self.inputs.new('StringsSocket', "axes_in").prop_name = 'axes_in'
        self.inputs.new('StringsSocket', "angle_in").prop_name = 'angle_in'
        self.inputs.new('StringsSocket', "arcStart_in").prop_name = 'arcStart_in'
        self.inputs.new('StringsSocket', "arcEnd_in").prop_name = 'arcEnd_in'
        self.inputs.new('StringsSocket', "delta_in").prop_name = 'delta_in'

        self.outputs.new("StringsSocket", "pts_out")
        # self.update_layout(context)

    def wrapped_process(self):
        self.check_input_requirements([])

        kwargs = {
            'center_in': self.get_from_props("center_in"),
            'axes_in': self.get_from_props("axes_in"),
            'angle_in': self.get_from_props("angle_in"),
            'arcStart_in': self.get_from_props("arcStart_in"),
            'arcEnd_in': self.get_from_props("arcEnd_in"),
            'delta_in': self.get_from_props("delta_in"),
            }

        pts_out = self.process_cv(fn=cv2.ellipse2Poly, kwargs=kwargs)
        pts_out.astype(np.uint64)
        self.refresh_output_socket("pts_out", pts_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
