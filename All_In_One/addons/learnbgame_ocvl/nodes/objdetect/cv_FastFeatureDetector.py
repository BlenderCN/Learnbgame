import bpy
import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.operatores.abc import InitFeature2DOperator

TYPE_FAST_ITEMS = (
    ("FastFeatureDetector_TYPE_5_8", "FastFeatureDetector_TYPE_5_8", "FastFeatureDetector_TYPE_5_8", "", 0),
    ("FastFeatureDetector_TYPE_7_12", "FastFeatureDetector_TYPE_7_12", "FastFeatureDetector_TYPE_7_12", "", 1),
    ("FastFeatureDetector_TYPE_9_16", "FastFeatureDetector_TYPE_9_16", "FastFeatureDetector_TYPE_9_16", "", 2),
    ("FastFeatureDetector_THRESHOLD", "FastFeatureDetector_THRESHOLD", "FastFeatureDetector_THRESHOLD", "", 3),
    ("FastFeatureDetector_NONMAX_SUPPRESSION", "FastFeatureDetector_NONMAX_SUPPRESSION", "FastFeatureDetector_NONMAX_SUPPRESSION", "", 4),
    ("FastFeatureDetector_FAST_N", "FastFeatureDetector_FAST_N", "FastFeatureDetector_FAST_N", "", 5),
)

FFD_WORK_MODE_ITEMS = (
    ("DETECT", "DETECT", "DETECT", "", 0),
    ("COMPUTE", "COMPUTE", "COMPUTE", "CANCEL", 1),
    ("DETECT-COMPUTE", "DETECT-COMPUTE", "DETECT-COMPUTE", "CANCEL", 2),
)


class OCVLFastFeatureDetectorNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Wrapping class for feature detection using the FAST method."
    _url = "https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_fast/py_fast.html"
    _init_method = cv2.FastFeatureDetector_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_layout(context)

    threshold_init: bpy.props.IntProperty(default=10, min=1, max=100, update=update_and_init, description="")
    type_init: bpy.props.EnumProperty(items=TYPE_FAST_ITEMS, default="FastFeatureDetector_TYPE_9_16", update=update_and_init, description="")
    nonmaxSuppression_init: bpy.props.BoolProperty(default=False, update=update_and_init, description="")

    def init(self, context):
        super().init(context)

    def wrapped_process(self):
        sift = FEATURE2D_INSTANCES_DICT.get("{}.{}".format(self.id_data.name, self.name))

        if self.loc_work_mode == "DETECT":
            self._detect(sift)
        elif self.loc_work_mode == "COMPUTE":
            #self._compute(sift)
            pass
        elif self.loc_work_mode == "DETECT-COMPUTE":
            #self._detect_and_compute(sift)
            pass
