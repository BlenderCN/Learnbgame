import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node

OUTPUT_MAP_TYPE_ITEMS = (
    ("CV_16SC2", "CV_16SC2", "CV_16SC2", "", 0),
    ("CV_32FC1", "CV_32FC1", "CV_32FC1", "", 1),
    ("CV_32FC2", "CV_32FC2", "CV_32FC2", "", 2),
)


class OCVLconvertMapsNode(OCVLNodeBase):

    n_doc = "Converts image transformation maps from one representation to another."

    map1_in: bpy.props.StringProperty(name="map1_in", default=str(uuid.uuid4()), description="The first input map of type CV_16SC2 , CV_32FC1 , or CV_32FC2 .")
    map2_in: bpy.props.StringProperty(name="map2_in", default=str(uuid.uuid4()), description="The second input map of type CV_16UC1 , CV_32FC1 , or none (empty matrix), respectively.")
    dstmap1_out: bpy.props.StringProperty(name="dstmap1_out", default=str(uuid.uuid4()), description="The first output map that has the type dstmap1type and the same size as src .")
    dstmap2_out: bpy.props.StringProperty(name="dstmap2_out", default=str(uuid.uuid4()), description="The second output map.")

    dstmap1type_in: bpy.props.EnumProperty(items=OUTPUT_MAP_TYPE_ITEMS, default='CV_16SC2', update=update_node, description="Type of the first output map that should be.")
    nninterpolation_in: bpy.props.BoolProperty(default=False, update=update_node, description="Flag indicating whether the fixed-point maps are used for the nearest-neighbor or for a more complex interpolation.")

    def init(self, context):
        self.inputs.new("StringsSocket", "map1_in")
        self.inputs.new('StringsSocket', "map2_in")

        self.outputs.new("StringsSocket", "dstmap1_out")
        self.outputs.new("StringsSocket", "dstmap2_out")

    def wrapped_process(self):
        self.check_input_requirements(["map1_in", "map2_in"])

        kwargs = {
            'map1_in': self.get_from_props("map1_in"),
            'map2_in': self.get_from_props("map2_in"),
            'dstmap1type_in': self.get_from_props("dstmap1type_in"),
            'nninterpolation_in': self.get_from_props("nninterpolation_in"),
            }

        dstmap1_out, dstmap2_out = self.process_cv(fn=cv2.convertMaps, kwargs=kwargs)
        self.refresh_output_socket("dstmap1_out", dstmap1_out, is_uuid_type=True)
        self.refresh_output_socket("dstmap2_out", dstmap2_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'dstmap1type_in')
        self.add_button(layout, 'nninterpolation_in')
