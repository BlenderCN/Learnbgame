import os
from logging import getLogger

import bpy
from ocvl.core.node_base import OCVLPreviewNodeBase
from ocvl.tutorial_engine.settings import TUTORIAL_PATH

logger = getLogger(__name__)


full_tutorial_path = os.path.abspath(os.path.join(TUTORIAL_PATH, "arithmetic_operations_on_images/arithmetic_operations_on_images.html"))


def drawn_docs_buttons(layout, col, node):
    col.operator('wm.url_open', text="OCVL Web Panel".format(node.bl_label),
                 icon='URL').url = 'https://ocvl-cms.herokuapp.com/admin/login/'
    col.operator('wm.url_open', text="OCVL Blog".format(node.bl_label), icon='URL').url = 'http://kube.pl/'
    col.operator('wm.url_open', text="OCVL Documentation".format(node.bl_label),
                 icon='HELP').url = 'http://opencv-laboratory.readthedocs.io/en/latest/?badge=latest'
    col.operator('wm.url_open', text="OpenCV Documentation".format(node.bl_label),
                 icon='HELP').url = 'https://docs.opencv.org/3.0-beta/index.html'
    col.operator('wm.url_open', text="Blender Documentation".format(node.bl_label),
                 icon='HELP').url = 'https://docs.blender.org/manual/en/dev/editors/node_editor/introduction.html'
    col = layout.column(align=True)
    col.operator('node.tutorial_mode', text="Arithmetic Operations on Images", icon='RENDERLAYERS').loc_tutorial_path = full_tutorial_path


class OCVLDocsNode(OCVLPreviewNodeBase):
    origin: bpy.props.StringProperty("")
    docs: bpy.props.BoolProperty(default=False)

    def init(self, context):
        self.width = 180
        self.outputs.new("StringsSocket", "docs")

    def wrapped_process(self):
        pass

    def draw_buttons(self, context, layout):
        col = layout.column(align=True)
        drawn_docs_buttons(layout, col, self)
