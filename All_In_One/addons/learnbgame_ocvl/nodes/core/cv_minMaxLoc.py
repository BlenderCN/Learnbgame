import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


class OCVLminMaxLocNode(OCVLNodeBase):

    n_doc = "Finds the global minimum and maximum in an array."

    src_in: bpy.props.StringProperty(name="src_in", default=str(uuid.uuid4()), description="Input single-channel array.")
    mask_in: bpy.props.StringProperty(name="mask_in", default=str(uuid.uuid4()), description="Optional mask used to select a sub-array.")

    minVal_out: bpy.props.StringProperty(name="minVal_out", default=str(uuid.uuid4()), description="Pointer to the returned minimum value; NULL is used if not required.")
    maxVal_out: bpy.props.StringProperty(name="maxVal_out", default=str(uuid.uuid4()), description="Pointer to the returned maximum value; NULL is used if not required.")
    minLoc_out: bpy.props.StringProperty(name="minLoc_out", default=str(uuid.uuid4()), description="Pointer to the returned minimum location (in 2D case); NULL is used if not required.")
    maxLoc_out: bpy.props.StringProperty(name="maxLoc_out", default=str(uuid.uuid4()), description="Pointer to the returned maximum location (in 2D case); NULL is used if not required.")

    def init(self, context):
        self.inputs.new("StringsSocket", "src_in")
        self.inputs.new("StringsSocket", "mask_in")

        self.outputs.new("StringsSocket", "minVal_out")
        self.outputs.new("StringsSocket", "maxVal_out")
        self.outputs.new("StringsSocket", "minLoc_out")
        self.outputs.new("StringsSocket", "maxLoc_out")

    def wrapped_process(self):
        self.check_input_requirements(["src_in"])

        kwargs = {
            'src_in': self.get_from_props("src_in"),
            'mask_in': self.get_from_props("mask_in"),
            }

        if isinstance(kwargs['mask_in'], str):
            kwargs.pop('mask_in')

        minVal_out, maxVal_out, minLoc_out, maxLoc_out = self.process_cv(fn=cv2.minMaxLoc, kwargs=kwargs)
        self.refresh_output_socket("minVal_out", minVal_out, is_uuid_type=True)
        self.refresh_output_socket("maxVal_out", maxVal_out, is_uuid_type=True)
        self.refresh_output_socket("minLoc_out", minLoc_out, is_uuid_type=True)
        self.refresh_output_socket("maxLoc_out", maxLoc_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
