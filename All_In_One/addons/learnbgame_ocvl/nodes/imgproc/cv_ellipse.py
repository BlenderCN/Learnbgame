import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node, LINE_TYPE_ITEMS

INPUT_NODE_ITEMS = (
    ("FULL", "FULL", "FULL", "", 0),
    ("SIMPLE", "SIMPLE", "SIMPLE", "", 1),
)


PROPS_MAPS = {
    INPUT_NODE_ITEMS[0][0]: ("center_in", "axes_in", "angle_in", "startAngle_in", "endAngle_in"),
    INPUT_NODE_ITEMS[1][0]: ("box_in",),
    }


class OCVLellipseNode(OCVLNodeBase):

    bl_icon = 'GREASEPENCIL'
    n_doc = "Draws a simple or thick elliptic arc or fills an ellipse sector."

    def update_layout(self, context):
        self.update_sockets(context)
        update_node(self, context)

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()), description="Input image.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output image.")

    # INPUT MODE PROPERTIES
    box_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Alternative ellipse representation via RotatedRect. This means that the function draws an ellipse inscribed in the rotated rectangle.")

    center_in: bpy.props.IntVectorProperty(default=(0, 0), size=2, update=update_node, description="Center of the ellipse.")
    axes_in: bpy.props.IntVectorProperty(default=(1, 1), size=2, min=0, max=1000, update=update_node, description="Half of the size of the ellipse main axes.")
    angle_in: bpy.props.IntProperty(default=30, min=0, max=360, update=update_node, description="Ellipse rotation angle in degrees.")
    startAngle_in: bpy.props.IntProperty(default=0, min=0, max=360, update=update_node, description="Starting angle of the elliptic arc in degrees.")
    endAngle_in: bpy.props.IntProperty(default=270, min=0, max=360, update=update_node, description="Ending angle of the elliptic arc in degrees")

    # COMMON PROPERTIES
    color_in: bpy.props.FloatVectorProperty(update=update_node, default=(.7, .7, .1, 1.0), size=4, min=0.0, max=1.0, subtype='COLOR', description="Ellipse color.")
    thickness_in: bpy.props.IntProperty(default=2, min=-1, max=10, update=update_node, description="Thickness of the ellipse arc outline, if positive. Otherwise, this indicates that a filled ellipse sector is to be drawn.")
    lineType_in: bpy.props.EnumProperty(items=LINE_TYPE_ITEMS, default="LINE_AA",update=update_node, description="Type of the ellipse boundary. See the line description.")
    loc_input_mode: bpy.props.EnumProperty(items=INPUT_NODE_ITEMS, default="SIMPLE", update=update_layout, description="Input mode.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('SvColorSocket', 'color_in').prop_name = 'color_in'
        self.inputs.new('StringsSocket', "thickness_in").prop_name = 'thickness_in'

        self.outputs.new("StringsSocket", "image_out")
        self.update_layout(context)

    def update_sockets(self, context):
        self.update_sockets_for_node_mode(PROPS_MAPS, self.loc_input_mode)
        self.process()

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])
        self.check_inputs_requirements_mode(requirements=(("box_in", "SIMPLE"),), props_maps=PROPS_MAPS, input_mode=self.loc_input_mode)
        kwargs_inputs= self.get_kwargs_inputs(PROPS_MAPS, self.loc_input_mode)

        kwargs = {
            'img_in': self.get_from_props("image_in"),
            'color_in': self.get_from_props("color_in"),
            'thickness_in': self.get_from_props("thickness_in"),
            'lineType_in': self.get_from_props("lineType_in"),
            }
        kwargs.update(kwargs_inputs)

        image_out = self.process_cv(fn=cv2.ellipse, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'lineType_in')
        self.add_button(layout, 'loc_input_mode', expand=True)
