import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node

CONNECTIVITY_ITEMS = (
    ("8", "8", "8", "", 0),
    ("4", "4", "4", "", 1),
)

LTYPE_ITEMS = (
    ("CV_16U", "CV_16U", "CV_16U", "", 0),
    ("CV_32S", "CV_32S", "CV_32S", "", 1),
)


class OCVLconnectedComponentsNode(OCVLNodeBase):

    n_doc = "Connected components."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="The 8-bit single-channel image to be labeled.")
    connectivity_in: bpy.props.EnumProperty(items=CONNECTIVITY_ITEMS, default="8", update=update_node, description="8 or 4 for 8-way or 4-way connectivity respectively.")
    ltype_in: bpy.props.EnumProperty(items=LTYPE_ITEMS, default="CV_16U", update=update_node, description="Output image label type. Currently CV_32S and CV_16U are supported.")

    labels_out: bpy.props.StringProperty(name="labels_out", default=str(uuid.uuid4()), description="Labels output.")
    retval_out: bpy.props.StringProperty(name="retval_out", default=str(uuid.uuid4()), description="Return value.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")

        self.outputs.new("StringsSocket", "labels_out")
        self.outputs.new("StringsSocket", "retval_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'image_in': self.get_from_props("image_in"),
            'connectivity_in': int(self.get_from_props("connectivity_in")),
            'ltype_in': self.get_from_props("ltype_in"),
            }

        retval_out, labels_out = self.process_cv(fn=cv2.connectedComponents, kwargs=kwargs)
        self.refresh_output_socket("retval_out", retval_out, is_uuid_type=True)
        self.refresh_output_socket("labels_out", labels_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "connectivity_in", expand=True)
        self.add_button(layout, "ltype_in", expand=True)
