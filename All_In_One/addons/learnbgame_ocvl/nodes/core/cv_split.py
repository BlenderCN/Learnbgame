import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


MODE_ITEMS = [
    ("EMPTY", "EMPTY", "EMPTY", "", 0),
    ("FULL", "FULL", "FULL", "", 1),
    ]


PROPS_MAPS = {
    MODE_ITEMS[0][0]: (),
    MODE_ITEMS[1][0]: ("layer_0_out", "layer_1_out", "layer_2_out", "layer_3_out"),
}


class OCVLsplitNode(OCVLNodeBase):

    n_doc = "Divides a multi-channel array into several single-channel arrays."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input multi-channel array.")

    layer_0_out: bpy.props.StringProperty(name="layer_0_out", default=str(uuid.uuid4()), description="Channel 0.")
    layer_1_out: bpy.props.StringProperty(name="layer_1_out", default=str(uuid.uuid4()), description="Channel 1.")
    layer_2_out: bpy.props.StringProperty(name="layer_2_out", default=str(uuid.uuid4()), description="Channel 2.")
    layer_3_out: bpy.props.StringProperty(name="layer_3_out", default=str(uuid.uuid4()), description="Channel 3.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")

        self.outputs.new("StringsSocket", "layer_0_out")
        self.outputs.new("StringsSocket", "layer_1_out")
        self.outputs.new("StringsSocket", "layer_2_out")
        self.outputs.new("StringsSocket", "layer_3_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'm': self.get_from_props("image_in"),
            }

        vector_layers = self.process_cv(fn=cv2.split, kwargs=kwargs)

        for n, layer_name in enumerate(PROPS_MAPS["FULL"]):
            if layer_name in self.outputs and len(vector_layers) <= n:
                self.outputs.remove(self.outputs[layer_name])
        for n, layer in enumerate(vector_layers):
            prop_name = "layer_{}_out".format(n)
            if not prop_name in self.outputs:
                self.outputs.new('StringsSocket', prop_name).prop_name = prop_name
            self.refresh_output_socket(prop_name, layer, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
