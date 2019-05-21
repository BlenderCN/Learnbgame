import cv2
import uuid

import bpy

from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode, STATE_MODE_ITEMS
from ocvl.operatores.abc import InitFeature2DOperator
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import update_node, OCVLNodeBase

BYTES_ITEMS = (
    ("16", "16", "16", "", 0),
    ("32", "32", "32", "", 1),
    ("64", "64", "64", "", 2),
)

BDE_WORK_MODE_ITEMS = (
    ("DETECT", "DETECT", "DETECT", "CANCEL", 0),
    ("COMPUTE", "COMPUTE", "COMPUTE", "", 1),
    ("DETECT-COMPUTE", "DETECT-COMPUTE", "DETECT-COMPUTE", "CANCEL", 2),
)

class OCVLBriefDescriptorExtractorNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Class for computing BRIEF descriptors described in [27]."
    _url = "https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_feature2d/py_brief/py_brief.html#brief"
    _init_method = cv2.xfeatures2d.BriefDescriptorExtractor_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_layout(context)

    bytes_init: bpy.props.EnumProperty(items=BYTES_ITEMS, default="32", update=update_and_init, description="")
    use_orientation_init: bpy.props.BoolProperty(default=False, update=update_and_init, description="")

    def init(self, context):
        super().init(context)

    def wrapped_process(self):
        sift = FEATURE2D_INSTANCES_DICT.get("{}.{}".format(self.id_data.name, self.name))

        if self.loc_work_mode == "DETECT":
            pass
        elif self.loc_work_mode == "COMPUTE":
            self._compute(sift)
        elif self.loc_work_mode == "DETECT-COMPUTE":
            pass
