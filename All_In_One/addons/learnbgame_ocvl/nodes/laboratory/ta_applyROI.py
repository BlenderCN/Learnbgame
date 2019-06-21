import uuid

import bpy
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLApplyROINode(OCVLNodeBase):

    n_doc = "Insert ROI to other image."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()))
    image_roi_in: bpy.props.StringProperty(name="image_roi_in", default=str(uuid.uuid4()))
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()))

    pt1_in: bpy.props.IntVectorProperty(default=(0, 0), size=2, min=0, update=update_node, description="Upper left corner ROI inserting.")

    def init(self, context):
        self.width = 200
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new("StringsSocket", "image_roi_in")
        self.inputs.new('StringsSocket', "pt1_in").prop_name = 'pt1_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in", "image_roi_in"])

        image_in = self.get_from_props("image_in")
        image_roi_in = self.get_from_props("image_roi_in")
        pt1_in = self.get_from_props("pt1_in")

        image_out = image_in.copy()
        image_out[pt1_in[0]:image_roi_in.shape[0] + pt1_in[0], pt1_in[1]:image_roi_in.shape[1] + pt1_in[1]] = image_roi_in
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)
