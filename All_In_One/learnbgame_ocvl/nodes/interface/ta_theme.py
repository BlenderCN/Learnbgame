from logging import getLogger

import bpy
from ocvl.core.node_base import OCVLPreviewNodeBase

logger = getLogger(__name__)


class OCVLThemeNode(OCVLPreviewNodeBase):
    origin: bpy.props.StringProperty("")
    theme: bpy.props.BoolProperty(default=False)

    def init(self, context):
        self.width = 180
        self.outputs.new("StringsSocket", "theme")

    def wrapped_process(self):
        pass

    def draw_buttons(self, context, layout):
        row = layout.row()
        col = row.column()
        col_split = col.split(0.5, align=True)
        col_split.operator('node.change_theme_light', text='Light')
        col_split.operator('node.change_theme_dark', text='Dark')
