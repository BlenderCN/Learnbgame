import bpy
import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase, update_node
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.operatores.abc import InitFeature2DOperator

GFTT_WORK_MODE_ITEMS = (
    ("DETECT", "DETECT", "DETECT", "", 0),
    ("COMPUTE", "COMPUTE", "COMPUTE", "CANCEL", 1),
    ("DETECT-COMPUTE", "DETECT-COMPUTE", "DETECT-COMPUTE", "CANCEL", 2),
)


class OCVLGFTTDetectorNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Wrapping class for feature detection using the goodFeaturesToTrack function."
    _init_method = cv2.GFTTDetector_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_sockets(context)
        update_node(self, context)

    maxCorners_init: bpy.props.IntProperty(default=1000, min=10, max=10000, update=update_and_init, description="")
    qualityLevel_init: bpy.props.FloatProperty(default=0.01, min=0.001, max=0.99, update=update_and_init, description="")
    minDistance_init: bpy.props.FloatProperty(default=1., min=1.0, max=3., update=update_and_init, description="")
    blockSize_init: bpy.props.IntProperty(default=3, min=1, max=8, update=update_and_init, description="")
    useHarrisDetector_init: bpy.props.BoolProperty(default=False, update=update_and_init, description="")
    k_init: bpy.props.FloatProperty(default=0.04, min=0.01, max=0.1, update=update_and_init, description="")
    gradiantSize_init: bpy.props.IntProperty(default=1, min=0, max=100, update=update_and_init, description="")

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
