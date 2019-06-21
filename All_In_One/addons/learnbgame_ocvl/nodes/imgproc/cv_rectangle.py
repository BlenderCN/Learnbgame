import collections
import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, LINE_TYPE_ITEMS

INPUT_MODE_ITEMS = (
    ("X, Y, W, H", "X, Y, W, H", "X, Y, W, H", "", 0),
    ("PT1, PT2", "PT1, PT2", "PT1, PT2", "", 1),
    ("Rect", "Rect", "Rect", "", 2),
)


PROPS_MAPS = {
    INPUT_MODE_ITEMS[0][0]: ("x_in|", "y_in|", "w_in|", "h_in|"),
    INPUT_MODE_ITEMS[1][0]: ("pt1_in|", "pt2_in|"),
    INPUT_MODE_ITEMS[2][0]: ("rect_in|RectSocket",),
}


class OCVLrectangleNode(OCVLNodeBase):
    bl_icon = 'GREASEPENCIL'

    n_doc = "Draws a simple, thick, or filled up-right rectangle."

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input image.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output image.")

    def update_layout(self, context):
        self.update_sockets(context)
        update_node(self, context)

    # INPUT MODE PROPERTIES
    pt1_in: bpy.props.IntVectorProperty(default=(0, 0), size=2, update=update_node, description="Vertex of the rectangle.")
    pt2_in: bpy.props.IntVectorProperty(default=(1, 1), size=2, update=update_node, description="Vertex of the rectangle opposite to pt1.")

    x_in: bpy.props.IntProperty(default=0, update=update_node, description="X for point of top left corner.")
    y_in: bpy.props.IntProperty(default=0, update=update_node, description="Y for point of top left corner.")
    w_in: bpy.props.IntProperty(default=0, update=update_node, description="Weight of rectangle.")
    h_in: bpy.props.IntProperty(default=0, update=update_node, description="Height of rectangle.")

    rect_in: bpy.props.IntVectorProperty(default=(0, 0, 0, 0), size=4, update=update_node, description="X, Y, Weight, Height in one vector.")

    # COMMON PROPERTIES
    color_in: bpy.props.FloatVectorProperty(update=update_node, default=(.7, .7, .1, 1.0), size=4, min=0.0, max=1.0, subtype='COLOR', description="Rectangle color or brightness (grayscale image).")
    thickness_in: bpy.props.IntProperty(default=2, min=-1, max=10, update=update_node, description="Thickness of lines that make up the rectangle. Negative values, like CV_FILLED, mean that the function has to draw a filled rectangle.")
    lineType_in: bpy.props.EnumProperty(items=LINE_TYPE_ITEMS, default="LINE_AA",update=update_node, description="Type of the line. See the line description.")
    shift_in: bpy.props.IntProperty(default=0, min=1, max=100, update=update_node, description="Number of fractional bits in the point coordinates.")
    loc_input_mode: bpy.props.EnumProperty(items=INPUT_MODE_ITEMS, default="PT1, PT2", update=update_layout, description="Loc input mode.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('SvColorSocket', 'color_in').prop_name = 'color_in'
        self.inputs.new('StringsSocket', "thickness_in").prop_name = 'thickness_in'
        self.inputs.new('StringsSocket', "shift_in").prop_name = 'shift_in'

        self.outputs.new("StringsSocket", "image_out")
        self.update_layout(context)

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])
        pt1_in, pt2_in = self._get_inputs_points(self.loc_input_mode)

        kwargs = {
            'img_in': self.get_from_props("image_in"),
            'pt1_in': pt1_in,
            'pt2_in': pt2_in,
            'color_in': self.get_from_props("color_in"),
            'thickness_in': self.get_from_props("thickness_in"),
            'lineType_in': self.get_from_props("lineType_in"),
            'shift_in': self.get_from_props("shift_in"),
            }

        image_out = self.process_cv(fn=cv2.rectangle, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def update_sockets(self, context):
        self.update_sockets_for_node_mode(PROPS_MAPS, self.loc_input_mode)
        self.process()

    def _get_inputs_points(self, input_mode):
        val = []
        for prop_name in PROPS_MAPS[input_mode]:
            prop_value = self.get_from_props(prop_name)
            if isinstance(prop_value, (list, tuple)):
                val.extend(prop_value)
            else:
                val.append(prop_value)
        return tuple(val[:2]), tuple(val[2:])

    def draw_buttons(self, context, layout):
        self.add_button(layout=layout, prop_name='lineType_in')
        self.add_button(layout=layout, prop_name='loc_input_mode', expand=True)
        if self.loc_input_mode == "PT1, PT2":
            self.add_button_get_points(layout=layout, props_name=('pt1_in', 'pt2_in'))
