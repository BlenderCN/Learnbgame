import uuid

import bpy
import cv2
import numpy as np
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLfindHomography2Node(OCVLNodeBase):

    n_doc = "This is an overloaded member function, provided for convenience. It differs from the above function only in what argument(s) it accepts."

    img1_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node)
    img2_in: bpy.props.StringProperty(default=str(uuid.uuid4()), update=update_node)
    min_match_counts_in: bpy.props.IntProperty(default=10, min=1, max=1000, update=update_node)
    min_distance_in: bpy.props.FloatProperty(default=0.7, min=0.1, max=10, update=update_node)

    img3_out: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Output retval.")

    def init(self, context):
        self.inputs.new("StringsSocket", "img1_in")
        self.inputs.new("StringsSocket", "img2_in")
        self.inputs.new("StringsSocket", "min_match_counts_in").prop_name = "min_match_counts_in"
        self.inputs.new("StringsSocket", "min_distance_in").prop_name = "min_distance_in"

        self.outputs.new("StringsSocket", "img3_out")

    def wrapped_process(self):
        self.check_input_requirements(["img1_in", "img1_in"])
        img1 = self.get_from_props("img1_in")
        img2 = self.get_from_props("img2_in")

        min_match_counts_in = self.get_from_props("min_match_counts_in")
        min_distance_in = self.get_from_props("min_distance_in")

        # Initiate SIFT detector
        sift = cv2.xfeatures2d.SIFT_create()

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)

        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1, des2, k=2)

        # store all the good matches as per Lowe's ratio test.
        good = []
        for m, n in matches:
            if m.distance < min_distance_in * n.distance:
                good.append(m)

        if len(good) > min_match_counts_in:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            matchesMask = mask.ravel().tolist()

            h, w = img1.shape
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            try:
                dst = cv2.perspectiveTransform(pts, M)
            except cv2.error:
                return

            img3_out = cv2.polylines(img2, [np.int32(dst)], True, (255,255,0), 3, cv2.LINE_AA)
        else:
            img3_out = img2
        self.refresh_output_socket("img3_out", img3_out, is_uuid_type=True)
