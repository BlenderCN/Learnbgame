import uuid

import bpy
import cv2
import numpy as np
from ocvl.core.node_base import OCVLNodeBase, update_node

METHOD_MODE_ITEMS = (
    ("0", "0", "0", "", 0),
    ("RANSAC", "RANSAC", "RANSAC", "", 1),
    ("LMEDS", "LMEDS", "LMEDS", "", 2),
    ("RHO", "RHO", "RHO", "", 3),
)

WORK_MODE_ITEMS = (
    ("DEFAULT", "DEFAULT", "DEFAULT", "", 0),
    ("MATCHES", "MATCHES", "MATCHES", "", 1),
)

COMMON_PROPS = ("ransacReprojThreshold_in", "method_in", "mask_out")
WORK_MODE_PROPS_MAPS = {
    WORK_MODE_ITEMS[0][0]: COMMON_PROPS + ("srcPoints_in", "dstPoints_in"),
    WORK_MODE_ITEMS[1][0]: COMMON_PROPS + ("matches_in", "keypoints1_in", "keypoints2_in"),
}


class OCVLfindHomographyNode(OCVLNodeBase):

    n_doc = "This is an overloaded member function, provided for convenience. It differs from the above function only in what argument(s) it accepts."

    def update_layout(self, context):
        self.update_sockets(context)
        update_node(self, context)

    # Default input
    srcPoints_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node, description="Coordinates of the points in the original plane, a matrix of the type CV_32FC2 or vector<Point2f>.")
    dstPoints_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node, description="Coordinates of the points in the target plane, a matrix of the type CV_32FC2 or a vector<Point2f>.")
    # Matches input
    matches_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node)
    keypoints1_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node)
    keypoints2_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node)
    # img1_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node)
    # img2_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node)

    ransacReprojThreshold_in: bpy.props.FloatProperty(default=3., min=1., max=10., update=update_node, description="Maximum allowed reprojection error to treat a point pair as an inlier (used in the RANSAC and RHO methods only).")
    method_in: bpy.props.EnumProperty(items=METHOD_MODE_ITEMS, default="0", update=update_node, description="Method used to computed a homography matrix.")

    mask_out: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Output mask.")
    retval_out: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Output retval.")
    # img3_out: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Output retval.")

    loc_work_mode: bpy.props.EnumProperty(items=WORK_MODE_ITEMS, default="DEFAULT", update=update_layout, description="")

    def init(self, context):
        self.inputs.new("StringsSocket", "srcPoints_in")
        self.inputs.new("StringsSocket", "dstPoints_in")
        self.inputs.new("StringsSocket", "matches_in")
        self.inputs.new("StringsSocket", "keypoints1_in")
        self.inputs.new("StringsSocket", "keypoints2_in")
        # self.inputs.new("StringsSocket", "img1_in")
        # self.inputs.new("StringsSocket", "img2_in")
        self.inputs.new("StringsSocket", "ransacReprojThreshold_in").prop_name = "ransacReprojThreshold_in"

        self.outputs.new("StringsSocket", "mask_out")
        self.outputs.new("StringsSocket", "retval_out")
        # self.outputs.new("StringsSocket", "img3_out")
        self.update_layout(context)

    def wrapped_process(self):
        self.check_input_requirements(["srcPoints_in", "dstPoints_in"])
        # img1_in = self.get_from_props("img1_in")
        # img2_in = self.get_from_props("img2_in")
        work_mode = self.get_from_props("loc_work_mode")
        if work_mode == "DEFAULT":
            srcPoints_in = self.get_from_props("srcPoints_in")
            dstPoints_in = self.get_from_props("srcPoints_in")
        elif work_mode == "MATCHES":
            matches_in = self.get_from_props("matches_in")

            good = []
            for dmatch in matches_in:
                if dmatch.distance < 1000:
                    good.append(dmatch)
            keypoints1_in = self.get_from_props("keypoints1_in")
            keypoints2_in = self.get_from_props("keypoints2_in")
            srcPoints_in = np.float32([keypoints1_in[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dstPoints_in = np.float32([keypoints2_in[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        kwargs = {
            'srcPoints_in': srcPoints_in,
            'dstPoints_in': dstPoints_in,
            # 'method_in': self.get_from_props("method_in"),
            'method_in': 0,
            'ransacReprojThreshold_in': self.get_from_props("ransacReprojThreshold_in"),
        }

        retval_out, mask_out = self.process_cv(fn=cv2.findHomography, kwargs=kwargs)
        # matchesMask = mask_out.ravel().tolist()

        # h, w = img1_in.shape
        # pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        # dst = cv2.perspectiveTransform(pts, retval_out)
        #
        # img3_out = cv2.polylines(img2_in, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)

        self.refresh_output_socket("retval_out", retval_out, is_uuid_type=True)
        self.refresh_output_socket("mask_out", mask_out, is_uuid_type=True)
        # self.refresh_output_socket("img3_out", img3_out, is_uuid_type=True)

    def update_sockets(self, context):
        self.update_sockets_for_node_mode(WORK_MODE_PROPS_MAPS, self.loc_work_mode)
        self.process()

    def draw_buttons(self, context, layout):
        self.add_button(layout=layout, prop_name='loc_work_mode', expand=True)
        self.add_button(layout=layout, prop_name="method_in", expand=True)
