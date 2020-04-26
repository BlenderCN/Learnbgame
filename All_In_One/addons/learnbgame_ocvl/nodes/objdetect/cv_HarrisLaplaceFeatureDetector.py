import bpy
import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase, update_node
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.operatores.abc import InitFeature2DOperator

HLFD_WORK_MODE_ITEMS = (
    ("DETECT", "DETECT", "DETECT", "", 0),
    ("COMPUTE", "COMPUTE", "COMPUTE", "CANCEL", 1),
    ("DETECT-COMPUTE", "DETECT-COMPUTE", "DETECT-COMPUTE", "CANCEL", 2),
)


class OCVLHarrisLaplaceFeatureDetectorNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Class implementing the Harris-Laplace feature detector as described in [127]."
    _init_method = cv2.xfeatures2d.HarrisLaplaceFeatureDetector_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_sockets(context)
        update_node(self, context)

    numOctaves_init: bpy.props.IntProperty(default=6, min=1, max=10, update=update_and_init, description="")
    corn_thresh_init: bpy.props.FloatProperty(default=0.01, min=0.0001, max=0.9999, update=update_and_init, description="")
    DOG_thresh_init: bpy.props.FloatProperty(default=0.01, min=0.0001, max=0.9999, update=update_and_init, description="")
    maxCorners_init: bpy.props.IntProperty(default=5000, min=1, max=100000, update=update_and_init, description="")
    num_layers_init: bpy.props.IntProperty(default=4, min=1, max=10, update=update_and_init, description="")

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
