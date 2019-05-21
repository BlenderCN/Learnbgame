import bpy
import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase, update_node
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.operatores.abc import InitFeature2DOperator

SCORE_TYPE_ITEMS = (
    ("ORB_K_BYTES", "ORB_K_BYTES", "ORB_K_BYTES", "", 0),
    ("ORB_HARRIS_SCORE", "ORB_HARRIS_SCORE", "ORB_HARRIS_SCORE", "", 1),
    ("ORB_FAST_SCORE", "ORB_FAST_SCORE", "ORB_FAST_SCORE", "", 2),
)

class OCVLORBNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Class implementing the ORB (oriented BRIEF) keypoint detector and descriptor extractor."
    _url = "https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_orb/py_orb.html"
    _init_method = cv2.ORB_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_sockets(context)
        update_node(self, context)

    scoreType_init: bpy.props.EnumProperty(default="ORB_HARRIS_SCORE", items=SCORE_TYPE_ITEMS, update=update_and_init,
        description="The default HARRIS_SCORE means that Harris algorithm is used to rank features.")
    nfeatures_init: bpy.props.IntProperty(default=500, min=1, max=10000, update=update_and_init,
        description="The maximum number of features to retain.")
    scaleFactor_init: bpy.props.FloatProperty(default=1.2, min=1.1, max=10., update=update_and_init,
        description="Pyramid decimation ratio, greater than 1. scaleFactor==2 means the classical pyramid.")
    nlevels_init: bpy.props.IntProperty(default=8, min=2, max=16, update=update_and_init,
        description="The number of pyramid levels.")
    edgeThreshold_init: bpy.props.IntProperty(default=31, min=10, max=100, update=update_and_init,
        description="This is size of the border where the features are not detected.")
    firstLevel_init: bpy.props.IntProperty(default=0, min=0, max=0, update=update_and_init,
        description="It should be 0 in the current implementation.")
    WTA_K_init: bpy.props.IntProperty(default=2, min=0, max=4, update=update_and_init,
        description="The number of points that produce each element of the oriented BRIEF descriptor.")
    patchSize_init: bpy.props.IntProperty(default=31, min=1, max=100, update=update_and_init,
        description="Size of the patch used by the oriented BRIEF descriptor.")
    fastThreshold_init: bpy.props.IntProperty(default=20, min=1, max=100, update=update_and_init,
        description="fastThreshold_in")

    def init(self, context):
        super().init(context)

    def wrapped_process(self):
        sift = FEATURE2D_INSTANCES_DICT.get("{}.{}".format(self.id_data.name, self.name))

        if self.loc_work_mode == "DETECT":
            self._detect(sift)
        elif self.loc_work_mode == "COMPUTE":
            self._compute(sift)
        elif self.loc_work_mode == "DETECT-COMPUTE":
            self._detect_and_compute(sift)
