import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase


class OCVLundistortPointsNode(OCVLNodeBase):

    n_doc = "Computes the ideal point coordinates from the observed point coordinates."

    src_in: bpy.props.StringProperty(name="src_in", default=str(uuid.uuid4()), description="Observed point coordinates, 1xN or Nx1 2-channel (CV_32FC2 or CV_64FC2).")
    cameraMatrix_in: bpy.props.StringProperty(name="cameraMatrix_in", default=str(uuid.uuid4()), description="Camera matrix")
    distCoeffs_in: bpy.props.StringProperty(name="distCoeffs_in", default=str(uuid.uuid4()), description="Input vector of distortion coefficients (k_1, k_2, p_1, p_2[, k_3[, k_4, k_5, k_6]]) of 4, 5, or 8 elements.")
    R_in: bpy.props.StringProperty(name="R_in", default=str(uuid.uuid4()), description="Rectification transformation in the object space (3x3 matrix). R1 or R2 computed by stereoRectify() can be passed here. If the matrix is empty, the identity transformation is used.")
    P_in: bpy.props.StringProperty(name="P_in", default=str(uuid.uuid4()), description="New camera matrix (3x3) or new projection matrix (3x4). P1 or P2 computed by stereoRectify() can be passed here. If the matrix is empty, the identity new camera matrix is used.")

    dst_out: bpy.props.StringProperty(name="dst_out", default=str(uuid.uuid4()), description="Output ideal point coordinates after undistortion and reverse perspective transformation. If matrix P is identity or omitted, dst will contain normalized point coordinates.")

    def init(self, context):
        self.inputs.new("StringsSocket", "src_in")
        self.inputs.new("StringsSocket", "cameraMatrix_in")
        self.inputs.new("StringsSocket", "distCoeffs_in")
        self.inputs.new("StringsSocket", "R_in")
        self.inputs.new("StringsSocket", "P_in")

        self.outputs.new("StringsSocket", "dst_out")

    def wrapped_process(self):
        self.check_input_requirements(["src_in", "cameraMatrix_in", "distCoeffs_in", "R_in", "P_in"])

        kwargs = {
            'src_in': self.get_from_props("src_in"),
            'cameraMatrix_in': self.get_from_props("cameraMatrix_in"),
            'distCoeffs_in': self.get_from_props("distCoeffs_in"),
            'R_in': self.get_from_props("R_in"),
            'P_in': self.get_from_props("P_in"),
            }

        dst_out = self.process_cv(fn=cv2.undistortPoints, kwargs=kwargs)
        self.refresh_output_socket("dst_out", dst_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        pass
