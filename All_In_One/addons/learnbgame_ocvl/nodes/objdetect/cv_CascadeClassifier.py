import os
import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node
from ocvl import BASE_DIR

HAAR_CASCADE_DIR = 'datafiles/haarcascade'


CASCADE_FILENAME_ITEMS = [(i, i, i, "", n) for n, i in enumerate(os.listdir(os.path.join(BASE_DIR, HAAR_CASCADE_DIR)))]
CASCADE_FILENAME_ITEMS_DEFAULT = [i[0] for i in CASCADE_FILENAME_ITEMS if i[0] == 'haarcascade_frontalface_default.xml'][0]


class OCVLCascadeClassifierNode(OCVLNodeBase):

    bl_flags_list = 'CASCADE_SCALE_IMAGE'

    image_in: bpy.props.StringProperty(name="image_in", default=str(uuid.uuid4()))
    scaleFactor_in: bpy.props.FloatProperty(default=1.1, min=1.1, max=10, update=update_node)
    minNeighbors_in: bpy.props.IntProperty(default=5, min=0, max=10, update=update_node)
    minSize_in: bpy.props.IntVectorProperty(default=(30, 30), min=1, max=100, size=2, update=update_node)
    flags_in: bpy.props.BoolVectorProperty(default=[False for i in bl_flags_list.split(",")], size=len(bl_flags_list.split(",")), update=update_node, subtype="NONE", description=bl_flags_list)

    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()))
    objects_out: bpy.props.StringProperty(name="objects_out", default=str(uuid.uuid4()))

    loc_cascade_filename: bpy.props.EnumProperty(items=CASCADE_FILENAME_ITEMS, default=CASCADE_FILENAME_ITEMS_DEFAULT, update=update_node)

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new('StringsSocket', "scaleFactor_in").prop_name = 'scaleFactor_in'
        self.inputs.new('StringsSocket', "minNeighbors_in").prop_name = 'minNeighbors_in'
        self.inputs.new('StringsSocket', "minSize_in").prop_name = 'minSize_in'

        self.outputs.new("StringsSocket", "image_out")
        self.outputs.new("StringsSocket", "objects_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'image_in': self.get_from_props("image_in"),
            'scaleFactor_in': self.get_from_props("scaleFactor_in"),
            'minNeighbors_in': self.get_from_props("minNeighbors_in"),
            'minSize_in': self.get_from_props("minSize_in"),
            'flags_in': self.get_from_props("flags_in"),
            }

        cascade_file = os.path.join(BASE_DIR, HAAR_CASCADE_DIR, self.loc_cascade_filename)
        faceCascade = cv2.CascadeClassifier(cascade_file)
        objects_out = self.process_cv(fn=faceCascade.detectMultiScale, kwargs=kwargs)
        image_out = self.get_from_props("image_in").copy()
        for (x, y, w, h) in objects_out:
            cv2.rectangle(image_out, (x, y), (x + w, y + h), (0, 255, 0), 2)

        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)
        self.refresh_output_socket("objects_out", objects_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "flags_in")
        self.add_button(layout, "loc_cascade_filename")
