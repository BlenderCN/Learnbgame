import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLgetDefaultNewCameraMatrixNode(OCVLNodeBase):

    n_doc = "Returns the default new camera matrix."

    cameraMatrix_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Input camera matrix.")
    imgsize_in: bpy.props.IntVectorProperty(default=(100, 100), min=1, max=2048, size=2, update=update_node, description="Camera view image size in pixels.")
    centerPrincipalPoint_in: bpy.props.BoolProperty(default=False, update=update_node, description="Location of the principal point in the new camera matrix. The parameter indicates whether this location should be at the image center or not.")

    retval_out: bpy.props.StringProperty(name="retval_out", default=str(uuid.uuid4()), description="Return value.")

    def init(self, context):
        self.inputs.new("StringsSocket", "cameraMatrix_in")
        self.inputs.new("StringsSocket", "imgsize_in").prop_name = "imgsize_in"

        self.outputs.new("StringsSocket", "retval_out")

    def wrapped_process(self):
        self.check_input_requirements(["cameraMatrix_in"])

        kwargs = {
            'cameraMatrix_in': self.get_from_props("cameraMatrix_in"),
            'imgsize_in': self.get_from_props("imgsize_in"),
            'centerPrincipalPoint_in': self.get_from_props("centerPrincipalPoint_in"),
            }

        retval_out = self.process_cv(fn=cv2.getDefaultNewCameraMatrix, kwargs=kwargs)
        self.refresh_output_socket("retval_out", retval_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'centerPrincipalPoint_in')
