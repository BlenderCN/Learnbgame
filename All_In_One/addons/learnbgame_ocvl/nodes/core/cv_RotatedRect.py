import bpy

from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLRotatedRectNode(OCVLNodeBase):

    n_doc = "Rotated Rect node."

    center_in: bpy.props.IntVectorProperty(default=(10, 10), size=2, min=0, max=2048, description="Center input.")
    size_in: bpy.props.IntVectorProperty(default=(10, 10), size=2, min=0, max=2048, description="Size input.")
    angle_in: bpy.props.IntProperty(default=10, min=0, max=360, update=update_node, subtype='ANGLE', description="Angle input.")

    def init(self, context):
        self.inputs.new("StringsSocket", "center_in").prop_name = "center_in"
        self.inputs.new("StringsSocket", "size_in").prop_name = "size_in"
        self.inputs.new("StringsSocket", "angle_in").prop_name = "angle_in"
        self.outputs.new("StringsSocket", "rotated_rect_out")

    def wrapped_process(self):
        center_in = self.get_from_props("center_in")
        size_in = self.get_from_props("size_in")
        angle_in = self.get_from_props("angle_in")

        rotated_rect_out = center_in, size_in, angle_in
        self.refresh_output_socket("rotated_rect_out", rotated_rect_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
