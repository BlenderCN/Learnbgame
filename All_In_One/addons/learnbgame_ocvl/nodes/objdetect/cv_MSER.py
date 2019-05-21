import bpy
import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.operatores.abc import InitFeature2DOperator

MSER_WORK_MODE_ITEMS = (
    ("DETECT", "DETECT", "DETECT", "", 0),
    ("COMPUTE", "COMPUTE", "COMPUTE", "CANCEL", 1),
    ("DETECT-COMPUTE", "DETECT-COMPUTE", "DETECT-COMPUTE", "CANCEL", 2),
)


class OCVLMSERNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Maximally stable extremal region extractor."
    _init_method = cv2.MSER_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_layout()

    T1_delta_init: bpy.props.IntProperty(default=5, min=1, max=100, update=update_and_init, description="")
    T1_min_area_init: bpy.props.IntProperty(default=30, min=1, max=100000, update=update_and_init, description="")
    T1_max_area_init: bpy.props.IntProperty(default=14400, min=1, max=1000000, update=update_and_init, description="")
    T1_max_variation_init: bpy.props.FloatProperty(default=0.25, min=0.0001, max=0.9999, update=update_and_init, description="")
    T1_min_diversity_init: bpy.props.FloatProperty(default=0.2, min=0.0001, max=0.9999, update=update_and_init, description="")
    T1_max_evolution_init: bpy.props.IntProperty(default=200, min=1, max=1000, update=update_and_init, description="")
    T1_area_threshold_init: bpy.props.FloatProperty(default=1.01, min=1000.0, update=update_and_init, description="")
    T1_min_margin_init: bpy.props.FloatProperty(default=0.003, min=0.0001, max=0.9999, update=update_and_init, description="")
    T1_edge_blur_size_init: bpy.props.IntProperty(default=5, min=1, max=1000, update=update_and_init, description="")

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
