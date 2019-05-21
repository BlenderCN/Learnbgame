import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, BORDER_TYPE_ITEMS


class OCVLborderInterpolateNode(OCVLNodeBase):

    n_doc = "Computes the source location of an extrapolated pixel."

    p_in: bpy.props.IntProperty(name="p", default=5, update=update_node, description="0-based coordinate of the extrapolated pixel along one of the axes, likely <0 or >= len .")
    len_in: bpy.props.IntProperty(name="len", default=10, update=update_node, description="Length of the array along the corresponding axis.")
    borderType_in: bpy.props.EnumProperty(name="borderType", items=BORDER_TYPE_ITEMS, default='BORDER_DEFAULT', update=update_node, description="Pixel extrapolation method, see cv::BorderTypes")

    retval_out: bpy.props.IntProperty(name="retval", default=0, description="")

    def init(self, context):
        self.inputs.new("StringsSocket", "p").prop_name = "p_in"
        self.inputs.new("StringsSocket", "len").prop_name = "len_in"

        self.outputs.new("StringsSocket", "retval")

    def wrapped_process(self):
        self.check_input_requirements([])

        kwargs = {
            'p': self.get_from_props("p_in"),
            'len': self.get_from_props("len_in"),
            'borderType': self.get_from_props("borderType_in"),
            }

        retval = self.process_cv(fn=cv2.borderInterpolate, kwargs=kwargs)
        self.refresh_output_socket("retval", retval)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "borderType_in")
