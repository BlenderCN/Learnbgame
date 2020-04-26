import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLinpaintNode(OCVLNodeBase):

    n_doc = "doc"
    bl_flags_list = 'INPAINT_NS, INPAINT_TELEA'

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="desc")
    inpaintMask_in: bpy.props.StringProperty(name="inpaintMask_in", default=str(uuid.uuid4()), description="Inpainting mask, 8-bit 1-channel image. Non-zero pixels indicate the area that needs to be inpainted.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="desc")

    inpaintRadius_in: bpy.props.FloatProperty(default=3, min=1, max=10, update=update_node, description="Radius of a circular neighborhood of each point inpainted that is considered by the algorithm.")
    flags_in: bpy.props.BoolVectorProperty(default=[False for i in bl_flags_list.split(",")], size=len(bl_flags_list.split(",")), update=update_node, subtype="NONE", description=bl_flags_list)

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "inpaintMask_in")
        self.inputs.new('StringsSocket', "inpaintRadius_in").prop_name = 'inpaintRadius_in'

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in", "inpaintMask_in"])

        kwargs = {
            'src': self.get_from_props("image_in"),
            'inpaintMask_in': self.get_from_props("inpaintMask_in"),
            'inpaintRadius_in': self.get_from_props("inpaintRadius_in"),
            'flags_in': self.get_from_props("flags_in"),
            }

        image_out = self.process_cv(fn=cv2.inpaint, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "flags_in")
