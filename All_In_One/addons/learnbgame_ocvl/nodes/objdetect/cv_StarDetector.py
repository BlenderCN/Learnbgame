import bpy
import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase, update_node
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.operatores.abc import InitFeature2DOperator

SD_WORK_MODE_ITEMS = (
    ("DETECT", "DETECT", "DETECT", "", 0),
    ("COMPUTE", "COMPUTE", "COMPUTE", "CANCEL", 1),
    ("DETECT-COMPUTE", "DETECT-COMPUTE", "DETECT-COMPUTE", "CANCEL", 2),
)


class OCVLStarDetectorNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "The class implements the keypoint detector introduced by [2], synonym of StarDetector."
    _init_method = cv2.xfeatures2d.StarDetector_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_sockets(context)
        update_node(self, context)

    maxSize_init: bpy.props.IntProperty(default=45, min=1, max=1000, update=update_and_init, description="")
    responseThreshold_init: bpy.props.IntProperty(default=30, min=1, max=1000, update=update_and_init, description="")
    lineThresholdProjected_init: bpy.props.IntProperty(default=10, min=1, max=100, update=update_and_init, description="")
    lineThresholdBinarized_init: bpy.props.IntProperty(default=8, min=1, max=100, update=update_and_init, description="")
    suppressNonmaxSize_init: bpy.props.IntProperty(default=5, min=1, max=100, update=update_and_init, description="")


    def init(self, context):
        super().init(context)

    def wrapped_process(self):
        instance = FEATURE2D_INSTANCES_DICT.get("{}.{}".format(self.id_data.name, self.name))

        if self.loc_work_mode == "DETECT":
            self._detect(instance)
        elif self.loc_work_mode == "COMPUTE":
            self._compute(instance)
        elif self.loc_work_mode == "DETECT-COMPUTE":
            self._detect_and_compute(instance)
