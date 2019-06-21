import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLclipLineNode(OCVLNodeBase):

    bl_icon = 'GREASEPENCIL'
    n_doc = "Clips the line against the image rectangle."

    imgRect_in: bpy.props.StringProperty(name="imgRect_in", default=str(uuid.uuid4()), description="Image rectangle.")
    retval_out: bpy.props.StringProperty(name="retval_out", default=str(uuid.uuid4()), description="Return value.")
    pt1_out: bpy.props.StringProperty(name="pt1_out", default=str(uuid.uuid4()), description="Pt1 output.")
    pt2_out: bpy.props.StringProperty(name="pt2_out", default=str(uuid.uuid4()), description="Pt2 output.")

    pt1_in: bpy.props.IntVectorProperty(default=(0, 0), size=2, min=0, update=update_node, description="First point of the line segment.")
    pt2_in: bpy.props.IntVectorProperty(default=(1, 1), size=2, min=0, update=update_node, description="Second point of the line segment.")

    def init(self, context):
        self.width = 200
        self.inputs.new("StringsSocket", "imgRect_in")
        self.inputs.new('StringsSocket', "pt1_in").prop_name = 'pt1_in'
        self.inputs.new('StringsSocket', "pt2_in").prop_name = 'pt2_in'

        self.outputs.new("StringsSocket", "retval_out")
        self.outputs.new("StringsSocket", "pt1_out")
        self.outputs.new("StringsSocket", "pt2_out")

    def wrapped_process(self):
        self.check_input_requirements(["imgRect_in"])

        kwargs = {
            'imgRect_in': self.get_from_props("imgRect_in"),
            'pt1_in': self.get_from_props("pt1_in"),
            'pt2_in': self.get_from_props("pt2_in"),
            }

        retval_out, pt1_out, pt2_out = self.process_cv(fn=cv2.clipLine, kwargs=kwargs)
        self.refresh_output_socket("retval_out", retval_out, is_uuid_type=True)
        self.refresh_output_socket("pt1_out", pt1_out, is_uuid_type=True)
        self.refresh_output_socket("pt2_out", pt2_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
