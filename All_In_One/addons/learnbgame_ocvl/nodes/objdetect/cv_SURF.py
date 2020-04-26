import uuid

import bpy
import cv2
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase, update_node
from ocvl.operatores.abc import InitFeature2DOperator


class OCVLSURFNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Class for extracting Speeded Up Robust Features from an image."
    _url = "https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_surf_intro/py_surf_intro.html"
    _init_method = cv2.xfeatures2d.SURF_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_sockets(context)
        update_node(self, context)

    hessianThreshold_init: bpy.props.FloatProperty(default=100, min=10, max=1000, step=100, update=update_and_init, description="Threshold for hessian keypoint detector used in SURF.")
    nOctaves_init: bpy.props.IntProperty(default=4, min=1, max=10, update=update_and_init, description="Number of pyramid octaves the keypoint detector will use.")
    nOctaveLayers_init: bpy.props.IntProperty(default=3, min=1, max=3, update=update_and_init, description="Number of octave layers within each octave.")
    extended_init: bpy.props.BoolProperty(default=False, update=update_and_init, description="Extended descriptor flag (true - use extended 128-element descriptors; false - use 64-element descriptors).")
    upright_init: bpy.props.BoolProperty(default=False, update=update_and_init, description="	Up-right or rotated features flag (true - do not compute orientation of features; false - compute orientation).")

    def init(self, context):
        super().init(context)

    def wrapped_process(self):
        surf = FEATURE2D_INSTANCES_DICT.get("{}.{}".format(self.id_data.name, self.name))

        if self.loc_work_mode == "DETECT":
            self._detect(surf)
        elif self.loc_work_mode == "COMPUTE":
            self._compute(surf)
        elif self.loc_work_mode == "DETECT-COMPUTE":
            self._detect_and_compute(surf)
