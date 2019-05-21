import os
import uuid
from logging import getLogger

import bpy
import cv2
from ocvl.nodes.interface import ta_first_step
from ocvl.nodes.interface.ta_first_step import show_long_tip
from ocvl.core.node_base import OCVLPreviewNodeBase

logger = getLogger(__name__)


class OCVLTipNode(OCVLPreviewNodeBase):

    tip: bpy.props.IntProperty(default=0)
    image_out: bpy.props.StringProperty(default='')
    is_splash_loaded: bpy.props.BoolProperty(default=False)

    def init(self, context):
        self.width = 512
        self.inputs.new("StringsSocket", "tip")

    def wrapped_process(self):
        if self.tip != bpy.tutorial_first_step:
            self.tip = bpy.tutorial_first_step
            current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
            baner_dir = os.path.abspath(os.path.join(current_dir, "../../tutorials/first_steps/"))
            loc_filepath = os.path.join(baner_dir, "step_{}.png".format(bpy.tutorial_first_step))
            image = cv2.imread(loc_filepath)
            self.make_textures(image, uuid_=self.image_out, width=1024, height=512)

    def _update_node_cache(self, image=None, resize=False, uuid_=None):
        old_image_out = self.image_out
        self.socket_data_cache.pop(old_image_out, None)
        uuid_ = uuid_ if uuid_ else str(uuid.uuid4())
        self.socket_data_cache[uuid_] = image
        return image, uuid_

    def draw_buttons(self, context, layout):
        self.draw_preview(layout=layout, prop_name="image_out", location_x=10, location_y=70, proportion=0.5)
        col = layout.column(align=True)
        show_long_tip(getattr(ta_first_step, 'TIP_STEP_{}'.format(bpy.tutorial_first_step)), col)
