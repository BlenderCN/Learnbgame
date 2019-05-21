import uuid
from functools import partial

import bpy
import cv2
from ocvl.core.node_base import OCVLNodeBase, update_node


class OCVLdrawMatchesNode(OCVLNodeBase):
    bl_flags_list = 'DRAW_MATCHES_FLAGS_DEFAULT, DRAW_MATCHES_FLAGS_DRAW_OVER_OUTIMG, DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS, DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS'
    n_doc = "This is an overloaded member function, provided for convenience. It differs from the above function only in what argument(s) it accepts."
    
    img1_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Source image.")
    img2_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Source image.")
    keypoints1_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Keypoints from the first source image.")
    keypoints2_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Keypoints from the first source image.")
    matches1to2_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Matches from the first image to the second one.")
    matchesMask_in: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Mask determining which matches are drawn. If the mask is empty, all matches are drawn.")

    matchColor_in: bpy.props.FloatVectorProperty(update=update_node, name='matchColor', default=(.3, .3, .2, 1.0), size=4, min=0.0, max=1.0, subtype='COLOR')
    singlePointColor_in: bpy.props.FloatVectorProperty(update=update_node, name='singlePointColor_in', default=(.3, .3, .2, 1.0), size=4, min=0.0, max=1.0, subtype='COLOR')
    loc_max_distance_in: bpy.props.IntProperty(default=500, min=100, max=10000, update=update_node)

    flags_in: bpy.props.BoolVectorProperty(default=[False for i in bl_flags_list.split(",")], size=len(bl_flags_list.split(",")), update=update_node, subtype="NONE", description=bl_flags_list)

    outImg_out: bpy.props.StringProperty(default=str(uuid.uuid4()), description="Output image.")


    def init(self, context):
        self.inputs.new("StringsSocket", "img1_in")
        self.inputs.new("StringsSocket", "img2_in")
        self.inputs.new("StringsSocket", "keypoints1_in")
        self.inputs.new("StringsSocket", "keypoints2_in")
        self.inputs.new("StringsSocket", "matches1to2_in")
        self.inputs.new("StringsSocket", "matchesMask_in")
        self.inputs.new("StringsSocket", "matchColor_in").prop_name = "matchColor_in"
        self.inputs.new("StringsSocket", "singlePointColor_in").prop_name = "singlePointColor_in"
        self.inputs.new("StringsSocket", "loc_max_distance_in").prop_name = "loc_max_distance_in"

        self.outputs.new("StringsSocket", "outImg_out")

    def wrapped_process(self):
        self.check_input_requirements(["img1_in", "img2_in", "keypoints1_in", "keypoints2_in", "matches1to2_in"])

        img1 = self.get_from_props("img1_in")
        img2 = self.get_from_props("img2_in")
        keypoints1_in = self.get_from_props("keypoints1_in")
        keypoints2_in = self.get_from_props("keypoints2_in")
        matches1to2_in = self.get_from_props("matches1to2_in")
        loc_max_distance_in = self.get_from_props("loc_max_distance_in")

        good = []
        for dmatch in matches1to2_in:
            if dmatch.distance < loc_max_distance_in:
                good.append(dmatch)

        draw_params = {
            'matchColor': self.get_from_props("matchColor_in"),
            'singlePointColor': self.get_from_props("singlePointColor_in"),
            'flags': self.get_from_props("flags_in"),
            'matchesMask': None,  # self.get_from_props("matchesMask_in")
        }
        drawMatches_partial = partial(cv2.drawMatches, img1, keypoints1_in, img2, keypoints2_in, good, None)
        outImg_out = self.process_cv(fn=drawMatches_partial, kwargs=draw_params)
        self.refresh_output_socket("outImg_out", outImg_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "flags_in")
