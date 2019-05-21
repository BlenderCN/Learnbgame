import bpy
import cv2
from ocvl.core.globals import FEATURE2D_INSTANCES_DICT
from ocvl.core.node_base import OCVLNodeBase, update_node
from ocvl.nodes.objdetect.abc_Feature2D import OCVLFeature2DNode
from ocvl.operatores.abc import InitFeature2DOperator


class OCVLSIFTNode(OCVLNodeBase, OCVLFeature2DNode):

    n_doc = "Class for extracting keypoints and computing descriptors using the Scale Invariant Feature Transform (SIFT) algorithm by D. Lowe"
    _url = "https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_sift_intro/py_sift_intro.html"
    _init_method = cv2.xfeatures2d.SIFT_create

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_sockets(context)
        update_node(self, context)

    nfeatures_init: bpy.props.IntProperty(default=0, min=0, max=100, update=update_and_init,
        description="The number of best features to retain.")
    nOctaveLayers_init: bpy.props.IntProperty(default=3, min=1, max=3, update=update_and_init,
        description="The number of layers in each octave.")
    contrastThreshold_init: bpy.props.FloatProperty(default=0.04, min=0.01, max=0.1, update=update_and_init,
        description="The contrast threshold used to filter out weak features in semi-uniform (low-contrast) regions.")
    edgeThreshold_init: bpy.props.FloatProperty(default=10, min=0.1, max=100, update=update_and_init,
        description="Size of an average block for computing a derivative covariation matrix over each pixel neighborhood.")
    sigma_init: bpy.props.FloatProperty(default=1.6, min=0.1, max=5., update=update_and_init,
        description="The sigma of the Gaussian applied to the input image at the octave #0.")

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
