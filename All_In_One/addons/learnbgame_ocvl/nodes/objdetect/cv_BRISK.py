import bpy
import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.operatores.abc import InitFeature2DOperator

BYTES_ITEMS = (
    ("16", "16", "16", "", 0),
    ("32", "32", "32", "", 1),
    ("64", "64", "64", "", 2),
)

BDE_WORK_MODE_ITEMS = (
    ("DETECT", "DETECT", "DETECT", "", 0),
    ("COMPUTE", "COMPUTE", "COMPUTE", "", 1),
    ("DETECT-COMPUTE", "DETECT-COMPUTE", "DETECT-COMPUTE", "", 2),
)


class OCVLBRISKNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Class implementing the BRISK keypoint detector and descriptor extractor, described in [LCS11]."
    _url = "https://docs.opencv.org/3.0-beta/modules/features2d/doc/feature_detection_and_description.html?highlight=brisk#BRISK%20:%20public%20Feature2D"
    _init_method = cv2.BRISK_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_layout(context)

    thresh_init: bpy.props.IntProperty(default=30, min=5, max=100, update=update_and_init)
    octaves_init: bpy.props.IntProperty(default=3, min=1, max=10, update=update_and_init)
    patternScale_init: bpy.props.IntProperty(default=1.0, min=0.1, max=10., update=update_and_init)

    def init(self, context):
        super().init(context)

    def wrapped_process(self):
        brisk = FEATURE2D_INSTANCES_DICT.get("{}.{}".format(self.id_data.name, self.name))

        if self.loc_work_mode == "DETECT":
            self._detect(brisk)
        elif self.loc_work_mode == "COMPUTE":
            self._compute(brisk)
        elif self.loc_work_mode == "DETECT-COMPUTE":
            self._detect_and_compute(brisk)
