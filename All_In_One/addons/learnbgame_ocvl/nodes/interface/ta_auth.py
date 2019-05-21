from logging import getLogger
import bpy

from ocvl.auth import (
    ocvl_auth, ocvl_user, OCVL_GITHUB_ISSUE_TEMPLATE, COMMUNITY_VERSION,
    OCVL_LINK_TO_CREATE_ACCOUNT)
from ocvl.core.node_base import OCVLPreviewNodeBase

logger = getLogger(__name__)


class OCVLAuthNode(OCVLPreviewNodeBase):
    origin: bpy.props.StringProperty("")
    auth: bpy.props.BoolProperty(default=False)
    status_code: bpy.props.IntProperty(default=0)
    response_content: bpy.props.StringProperty(default="")

    def init(self, context):
        self.width = 180
        self.inputs.new("StringsSocket", "auth")

    def wrapped_process(self):
        if ocvl_user.is_login:
            self.status_code = 200

    def draw_buttons(self, context, layout):
        name = ocvl_user.name
        msg = ""
        icon = 'QUESTION'

        if self.status_code == 0:
            icon = 'QUESTION'
            if ocvl_auth.ocvl_version == COMMUNITY_VERSION:
                col = layout.column(align=True)
                # col.operator('wm.url_open', text="Upgrade program to PRO".format(self.bl_label), icon='SOLO_ON').url = OCVL_LINK_UPGRADE_PROGRAM_TO_PRO
                col.operator('wm.url_open', text="Create account".format(self.bl_label), icon='INFO').url = OCVL_LINK_TO_CREATE_ACCOUNT
        elif self.status_code == 200:
            col = layout.column(align=True)
            for i, tutorial in enumerate(ocvl_user.tutorials):
                if i % 2:
                    col_split = col.split(factor=0.5, align=True)
                text = tutorial.get("name")
                icon = tutorial.get("icon", "URL")
                col.operator('wm.url_open', text=text.format(self.bl_label),
                                   icon=icon).url = tutorial.get("package_site", "http://kube.pl")
            icon = 'FILE_TICK'
        elif self.status_code == 401:
            msg = "Incorrect credentials / Licence Key"
            icon = "ERROR"
        elif self.status_code >= 500:
            msg = "Server Error"
            icon = "ERROR"
            url = OCVL_GITHUB_ISSUE_TEMPLATE.format(title="OCVL web authenticate error 500", body=self.response_content)
            col = layout.column(align=True)
            col.operator('wm.url_open', text="Report a problem".format(self.bl_label), icon='URL').url = url
        else:
            url = OCVL_GITHUB_ISSUE_TEMPLATE.format(title="OCVL web authenticate unsupported error", body=self.response_content)
            col = layout.column(align=True)
            col.operator('wm.url_open', text="Report a problem".format(self.bl_label), icon='URL').url = url
            msg = "Unsupported error"
            icon = "ERROR"
        layout.label(text=msg)
        layout.label(text=name, icon=icon)


AUTH_NODE_NAME = OCVLAuthNode.__name__[4:-4]
