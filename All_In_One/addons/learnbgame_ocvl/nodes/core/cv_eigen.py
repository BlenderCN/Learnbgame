import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


class OCVLeigenNode(OCVLNodeBase):

    n_doc = "Calculates eigenvalues and eigenvectors of a symmetric matrix."

    src_in: bpy.props.StringProperty(name="src_in", default=str(uuid.uuid4()), description="Input matrix that must have CV_32FC1 or CV_64FC1 type, square size and be symmetrical.")

    retval_out: bpy.props.StringProperty(name="retval_out", default=str(uuid.uuid4()), description="Return value.")
    eigenvalues_out: bpy.props.StringProperty(name="eigenvalues_out", default=str(uuid.uuid4()), description="Output vector of eigenvalues of the same type as src; the eigenvalues are stored in the descending order.")
    eigenvectors_out: bpy.props.StringProperty(name="eigenvectors_out", default=str(uuid.uuid4()), description="Output matrix of eigenvectors; it has the same size and type as src.")

    def init(self, context):
        self.inputs.new("StringsSocket", "src_in")

        self.outputs.new("StringsSocket", "retval_out")
        self.outputs.new("StringsSocket", "eigenvalues_out")
        self.outputs.new("StringsSocket", "eigenvectors_out")

    def wrapped_process(self):
        self.check_input_requirements(["src_in"])

        kwargs = {
            'src_in': self.get_from_props("src_in"),
            }

        retval_out, eigenvalues_out, eigenvectors_out = self.process_cv(fn=cv2.eigen, kwargs=kwargs)
        self.refresh_output_socket("retval_out", retval_out, is_uuid_type=True)
        self.refresh_output_socket("eigenvalues_out", eigenvalues_out, is_uuid_type=True)
        self.refresh_output_socket("eigenvectors_out", eigenvectors_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
