import bpy
import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase, update_node
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.operatores.abc import InitFeature2DOperator

NORM_ITEMS = (
    ("DAISY_NRM_NONE", "DAISY_NRM_NONE", "DAISY_NRM_NONE", "", 0),
    ("DAISY_NRM_PARTIAL", "DAISY_NRM_PARTIAL", "DAISY_NRM_PARTIAL", "", 1),
    ("DAISY_NRM_FULL", "DAISY_NRM_FULL", "DAISY_NRM_FULL", "", 2),
    ("DAISY_NRM_SIFT", "DAISY_NRM_SIFT", "DAISY_NRM_SIFT", "", 3),
)

DAISY_WORK_MODE_ITEMS = (
    ("DETECT", "DETECT", "DETECT", "CANCEL", 0),
    ("COMPUTE", "COMPUTE", "COMPUTE", "", 1),
    ("DETECT-COMPUTE", "DETECT-COMPUTE", "DETECT-COMPUTE", "CANCEL", 2),
)


class OCVLDAISYNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Class implementing DAISY descriptor, described in [178]."
    _init_method = cv2.xfeatures2d.DAISY_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_sockets(context)
        update_node(self, context)

    radius_init: bpy.props.FloatProperty(default=15, min=0.1, max=100, update=update_and_init, description="")
    q_radius_init: bpy.props.IntProperty(default=3, min=0, max=100, update=update_and_init, description="")
    q_theta_init: bpy.props.IntProperty(default=8, min=0, max=100, update=update_and_init, description="")
    q_hist_init: bpy.props.IntProperty(default=8, min=0, max=100, update=update_and_init, description="")
    norm_init: bpy.props.EnumProperty(items=NORM_ITEMS, default="DAISY_NRM_NONE", update=update_and_init, description="")
    interpolation_init: bpy.props.BoolProperty(default=True, update=update_and_init, description="")
    use_orientation_init: bpy.props.BoolProperty(default=False, update=update_and_init, description="")

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
