import bpy
import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import update_node, OCVLNodeBase
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.operatores.abc import InitFeature2DOperator

VGG_WORK_MODE_ITEMS = (
    ("DETECT", "DETECT", "DETECT", "CANCEL", 0),
    ("COMPUTE", "COMPUTE", "COMPUTE", "", 1),
    ("DETECT-COMPUTE", "DETECT-COMPUTE", "DETECT-COMPUTE", "CANCEL", 2),
)


class OCVLVGGNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Class implementing VGG (Oxford Visual Geometry Group) descriptor trained end to end..."
    _init_method = cv2.xfeatures2d.VGG_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_sockets(context)
        update_node(self, context)

    isigma_init: bpy.props.FloatProperty(default=1.4, min=0, max=10, update=update_and_init, description="")
    img_normalize_init: bpy.props.BoolProperty(default=True, update=update_and_init, description="")
    use_scale_orientation_init: bpy.props.BoolProperty(default=True, update=update_and_init, description="")
    scale_factor_init: bpy.props.FloatProperty(default=6.25, min=1, max=10, update=update_and_init, description="")
    dsc_normalize_init: bpy.props.BoolProperty(default=False, update=update_and_init, description="")

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
