import uuid

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node

M1TYPE_ITEMS = (
    ("CV_32FC1", "CV_32FC1", "CV_32FC1", "", 0),
    ("CV_16SC2", "CV_16SC2", "CV_16SC2", "", 1),
)


class OCVLinitUndistortRectifyMapNode(OCVLNodeBase):

    n_doc = "Computes the undistortion and rectification transformation map."

    cameraMatrix_in: bpy.props.StringProperty(name="cameraMatrix_in", default=str(uuid.uuid4()), description="Input camera matrix A")
    distCoeffs_in: bpy.props.StringProperty(name="distCoeffs_in", default=str(uuid.uuid4()), description="Input vector of distortion coefficients (k_1, k_2, p_1, p_2[, k_3[, k_4, k_5, k_6]]) of 4, 5, or 8 elements. If the vector is NULL/empty, the zero distortion coefficients are assumed.")
    newCameraMatrix: bpy.props.StringProperty(name="newCameraMatrix", default=str(uuid.uuid4()), description="New camera matrix A'")
    R_in: bpy.props.StringProperty(name="R_in", default=str(uuid.uuid4()), description="Optional rectification transformation in the object space (3x3 matrix). R1 or R2 , computed by stereoRectify() can be passed here.")
    size_in: bpy.props.IntVectorProperty(default=(100, 100), min=1, max=2048, size=2, update=update_node, description="Undistorted image size.")
    m1type_in: bpy.props.EnumProperty(items=M1TYPE_ITEMS, default="CV_32FC1", update=update_node, description="Type of the first output map that can be CV_32FC1 or CV_16SC2.")

    map1_out: bpy.props.StringProperty(name="map1_out", default=str(uuid.uuid4()), description="First output map")
    map2_out: bpy.props.StringProperty(name="map2_out", default=str(uuid.uuid4()), description="Second output map")

    def init(self, context):
        self.inputs.new("StringsSocket", "cameraMatrix_in")
        self.inputs.new("StringsSocket", "distCoeffs_in")
        self.inputs.new("StringsSocket", "newCameraMatrix")
        self.inputs.new("StringsSocket", "R_in")
        self.inputs.new("StringsSocket", "size_in").prop_name = "size_in"

        self.outputs.new("StringsSocket", "map1_out")
        self.outputs.new("StringsSocket", "map2_out")

    def wrapped_process(self):
        self.check_input_requirements(["cameraMatrix_in", "distCoeffs_in", "newCameraMatrix", "R_in"])

        kwargs = {
            'cameraMatrix_in': self.get_from_props("cameraMatrix_in"),
            'newCameraMatrix': self.get_from_props("newCameraMatrix"),
            'distCoeffs_in': self.get_from_props("distCoeffs_in"),
            'R_in': self.get_from_props("R_in"),
            'size_in': self.get_from_props("size_in"),
            'm1type_in': self.get_from_props("m1type_in"),
            }

        map1_out, map2_out = self.process_cv(fn=cv2.initUndistortRectifyMap, kwargs=kwargs)
        self.refresh_output_socket("map1_out", map1_out, is_uuid_type=True)
        self.refresh_output_socket("map2_out", map2_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "m1type_in", expand=True)
