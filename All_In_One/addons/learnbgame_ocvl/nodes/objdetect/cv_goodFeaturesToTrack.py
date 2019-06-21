import uuid

import bpy
import cv2
import numpy as np
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLgoodFeaturesToTrackNode(OCVLNodeBase):

    n_doc = "Determines strong corners on an image."
    _url = "http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_shi_tomasi/py_shi_tomasi.html"

    image_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Input 8-bit or floating-point 32-bit, single-channel image.")
    mask_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node, description="Optional region of interest.")
    maxCorners_in: bpy.props.IntProperty(default=25, min=1, max=1000, update=update_node, description="Output vector of detected corners.")
    qualityLevel_in: bpy.props.FloatProperty(default=0.01, min=0.0001, max=0.9999, update=update_node, description="Maximum number of corners to return.")
    minDistance_in: bpy.props.FloatProperty(default=10, min=1, max=1000, update=update_node, description="Minimum possible Euclidean distance between the returned corners.")
    blockSize_in: bpy.props.IntProperty(default=3, min=2, max=100, update=update_node, description="Size of an average block for computing a derivative covariation matrix over each pixel neighborhood.")
    gradientSize_in: bpy.props.IntProperty(default=3, min=1, max=100, update=update_node, description="")
    useHarrisDetector_in: bpy.props.BoolProperty(default=False, update=update_node, description="Parameter indicating whether to use a Harris detector (see cornerHarris) or cornerMinEigenVal.")
    k_in: bpy.props.FloatProperty(default=0.04, min=0.01, max=1., update=update_node, description="Free parameter of the Harris detector.")

    corners_out: bpy.props.StringProperty(name="corners_out", default=str(uuid.uuid4()), description="Output vector of detected corners.")
    image_out: bpy.props.StringProperty(name="image_out", default=str(uuid.uuid4()), description="Output vector of detected corners.")

    def init(self, context):
        self.inputs.new("StringsSocket", "image_in")
        self.inputs.new("StringsSocket", "mask_in")
        self.inputs.new("StringsSocket", "maxCorners_in").prop_name = "maxCorners_in"
        self.inputs.new("StringsSocket", "qualityLevel_in").prop_name = "qualityLevel_in"
        self.inputs.new("StringsSocket", "minDistance_in").prop_name = "minDistance_in"
        self.inputs.new("StringsSocket", "blockSize_in").prop_name = "blockSize_in"
        self.inputs.new("StringsSocket", "gradientSize_in").prop_name = "gradientSize_in"
        self.inputs.new("StringsSocket", "useHarrisDetector_in").prop_name = "useHarrisDetector_in"
        self.inputs.new("StringsSocket", "k_in").prop_name = "k_in"

        self.outputs.new("StringsSocket", "corners_out")
        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'image_in': self.get_from_props("image_in"),
            'mask_in': self.get_from_props("mask_in"),
            'maxCorners_in': self.get_from_props("maxCorners_in"),
            'qualityLevel_in': self.get_from_props("qualityLevel_in"),
            'minDistance_in': self.get_from_props("minDistance_in"),
            'blockSize_in': self.get_from_props("blockSize_in"),
            'gradientSize_in': self.get_from_props("gradientSize_in"),
            'useHarrisDetector_in': self.get_from_props("useHarrisDetector_in"),
            'k_in': self.get_from_props("k_in"),
            }

        if isinstance(kwargs['mask_in'], str):
            kwargs['mask_in'] = np.ones(shape=kwargs['image_in'].shape, dtype=np.uint8)

        corners_out = self.process_cv(fn=cv2.goodFeaturesToTrack, kwargs=kwargs)
        self.refresh_output_socket("corners_out", corners_out, is_uuid_type=True)

        corners = np.int0(corners_out)
        image_out = kwargs['image_in'].copy()

        for i in corners:
            x, y = i.ravel()
            cv2.circle(image_out, (x, y), 3, 255, -1)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)
