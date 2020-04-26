import bpy
import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase, update_node
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.operatores.abc import InitFeature2DOperator

LATCH_WORK_MODE_ITEMS = (
    ("DETECT", "DETECT", "DETECT", "CANCEL", 0),
    ("COMPUTE", "COMPUTE", "COMPUTE", "", 1),
    ("DETECT-COMPUTE", "DETECT-COMPUTE", "DETECT-COMPUTE", "CANCEL", 2),
)


class OCVLLATCHNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Latch Class for computing the LATCH descriptor."
    _init_method = cv2.xfeatures2d.LATCH_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_sockets(context)
        update_node(self, context)

    bytes_init: bpy.props.IntProperty(default=32, min=2, max=256, update=update_and_init, description="")
    rotationInvariance_init: bpy.props.BoolProperty(default=True, update=update_and_init, description="")
    half_ssd_size_init: bpy.props.IntProperty(default=3, min=1, max=10, update=update_and_init, description="")
    sigma_init: bpy.props.FloatProperty(default=2.0, min=0.01, max=9.99, update=update_and_init, description="")

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
