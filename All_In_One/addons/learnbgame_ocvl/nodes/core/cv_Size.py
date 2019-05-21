import bpy

from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLSizeNode(OCVLNodeBase):

    n_doc = "Size node."

    width_in: bpy.props.IntProperty(default=10, min=0, max=2048, update=update_node, description="Width input.")
    height_in: bpy.props.IntProperty(default=10, min=0, max=2048, update=update_node, description="Height input.")

    def init(self, context):
        self.inputs.new("StringsSocket", "width_in").prop_name = "width_in"
        self.inputs.new("StringsSocket", "height_in").prop_name = "height_in"
        self.outputs.new("StringsSocket", "size_out")

    def wrapped_process(self):
        width_in = self.get_from_props("width_in")
        height_in = self.get_from_props("height_in")

        size_out = width_in, height_in
        self.refresh_output_socket("size_out", size_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
