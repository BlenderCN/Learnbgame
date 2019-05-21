import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLcreateBackgroundSubtractorMOG2Node(OCVLNodeBase):

    image_1_in: bpy.props.StringProperty(name="image_1_in", default=str(uuid.uuid4()))
    image_2_in: bpy.props.StringProperty(name="image_2_in", default=str(uuid.uuid4()))
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()))

    history_in: bpy.props.IntProperty(default=200, update=update_node, min=1, max=400, description='Length of the history.')
    varThreshold_in: bpy.props.FloatProperty(default=16, update=update_node, min=0.0, max=1000.0, description="Threshold on the squared Mahalanobis distance between the pixel and the model.")
    detectShadows_in: bpy.props.BoolProperty(default=False, update=update_node, description="If true, the algorithm will detect shadows and mark them.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_1_in")
        self.inputs.new("StringsSocket", "image_2_in")
        self.inputs.new('StringsSocket', "history_in").prop_name = 'history_in'
        self.inputs.new('StringsSocket', "varThreshold_in").prop_name = 'varThreshold_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_1_in", "image_2_in"])

        kwargs = {
            'history_in': self.get_from_props("history_in"),
            'varThreshold_in': self.get_from_props("varThreshold_in"),
            'detectShadows_in': self.get_from_props("detectShadows_in"),
            }

        fgbg = self.process_cv(fn=cv2.createBackgroundSubtractorMOG2, kwargs=kwargs)
        image_1_in = self.get_from_props("image_1_in")
        image_2_in = self.get_from_props("image_2_in")
        for i in range(100):
            if i % 2 == 55:
                fgbg.apply(image_2_in)
            fgbg.apply(image_1_in)

        fgmask = fgbg.apply(image_2_in)
        self.refresh_output_socket("image_out", fgmask, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
