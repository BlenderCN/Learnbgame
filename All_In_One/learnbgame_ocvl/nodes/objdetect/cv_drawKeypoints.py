import uuid

import bpy
import cv2
import numpy as np
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLdrawKeypointsNode(OCVLNodeBase):

    n_doc = "Class for extracting keypoints and computing descriptors using the Scale Invariant Feature Transform (SIFT) algorithm by D. Lowe"
    _url = "https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_sift_intro/py_sift_intro.html"

    image_in: bpy.props.StringProperty(default=str(uuid.uuid4()),
        description="Source image.")

    keypoints_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node,
        description="Keypoints from the source image.")
    # color_in: bpy.props.FloatProperty(default=1.6, min=0.1, max=5., update=update_node,
    #     description="The sigma of the Gaussian applied to the input image at the octave #0.")
    # flags_in =

    outImage_out: bpy.props.StringProperty(default=str(uuid.uuid4()),
        description="Output image.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new("StringsSocket", "keypoints_in")

        self.outputs.new("ImageSocket", "outImage_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in", "keypoints_in"])

        kwargs = {
            'image_in': self.get_from_props("image_in"),
            'outImage': np.zeros(self.get_from_props("image_in").shape),
            'keypoints_in': self.get_from_props("keypoints_in"),
            'flags_in': cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
            }

        outImage_out = self.process_cv(fn=cv2.drawKeypoints, kwargs=kwargs)
        self.refresh_output_socket("outImage_out", outImage_out, is_uuid_type=True)
