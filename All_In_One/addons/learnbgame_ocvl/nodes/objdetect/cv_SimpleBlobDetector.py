import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase, update_node
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.operatores.abc import InitFeature2DOperator

SBD_WORK_MODE_ITEMS = (
    ("DETECT", "DETECT", "DETECT", "CANCEL", 0),
    ("COMPUTE", "COMPUTE", "COMPUTE", "", 1),
    ("DETECT-COMPUTE", "DETECT-COMPUTE", "DETECT-COMPUTE", "CANCEL", 2),
)


class OCVLSimpleBlobDetectorNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Class for extracting blobs from an image."
    _init_method = cv2.SimpleBlobDetector_create

    def update_layout(self, context):
        self.update_sockets(context)
        update_node(self, context)

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_sockets(context)
        update_node(self, context)

    # nfeatures_init: bpy.props.IntProperty(default=0, min=0, max=100, update=update_and_init,
    #     description=_("The number of best features to retain.")
    # nOctaveLayers_init: bpy.props.IntProperty(default=3, min=1, max=3, update=update_and_init,
    #     description=_("The number of layers in each octave.")
    # contrastThreshold_init: bpy.props.FloatProperty(default=0.04, min=0.01, max=0.1, update=update_and_init,
    #     description=_("The contrast threshold used to filter out weak features in semi-uniform (low-contrast) regions.")
    # edgeThreshold_init: bpy.props.FloatProperty(default=10, min=0.1, max=100, update=update_and_init,
    #     description=_("Size of an average block for computing a derivative covariation matrix over each pixel neighborhood.")
    # sigma_init: bpy.props.FloatProperty(default=1.6, min=0.1, max=5., update=update_and_init,
    #     description="The sigma of the Gaussian applied to the input image at the octave #0.")

    def init(self, context):
        super().init(context)

    def wrapped_process(self):
        instance = FEATURE2D_INSTANCES_DICT.get("{}.{}".format(self.id_data.name, self.name))

        if self.loc_work_mode == "DETECT":
            pass
            # self._detect(instance)
        elif self.loc_work_mode == "COMPUTE":
            self._compute(instance)
        elif self.loc_work_mode == "DETECT-COMPUTE":
            pass
            # self._detect_and_compute(instance)
