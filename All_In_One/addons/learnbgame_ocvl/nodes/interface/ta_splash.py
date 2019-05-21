import os
import uuid
from logging import getLogger

import bpy
import cv2
from ocvl.auth import (
    COMMUNITY_VERSION, OCVL_AUTHORS, OCVL_AUTH_PARAMS_LICENCE_KEY_TEMPALTE, OCVL_AUTH_PARAMS_LOGIN_PASSWORD_TEMPALTE, OCVL_LINK_TO_CREATE_ACCOUNT,
    OCVL_LINK_TO_MORE_TUTORIALS, OCVL_LINK_TO_STORE, OCVL_VERSION, PRO_VERSION, ocvl_auth, ocvl_user,
)
from ocvl.core.node_base import OCVLPreviewNodeBase

logger = getLogger(__name__)


class OCVLSplashNode(OCVLPreviewNodeBase):
    origin: bpy.props.StringProperty("")
    image_out: bpy.props.StringProperty(default=str(uuid.uuid4()))

    login_in: bpy.props.StringProperty(name="Login", default="", description="Login", maxlen=60)
    password_in: bpy.props.StringProperty(name="Password", default="", subtype="PASSWORD", description="Password", maxlen=60)
    is_remember_in: bpy.props.BoolProperty(name="Remember", default=True, description="Remember credentials")

    is_licence_key: bpy.props.BoolProperty(name="Licence Key", default=False)
    licence_key_in: bpy.props.StringProperty(name="Licence Key", default="", description="licence_key_in", maxlen=600)

    auth: bpy.props.BoolProperty(default=False)
    docs: bpy.props.BoolProperty(default=False)
    settings: bpy.props.BoolProperty(default=False)

    is_splash_loaded: bpy.props.BoolProperty(default=False)

    def init(self, context):
        self.width = 512
        # self.use_custom_color = True
        # self.color = (0, 0, 0)
        self.outputs.new("StringsSocket", "auth")
        self.inputs.new("StringsSocket", "settings")
        self.inputs.new("StringsSocket", "docs")

    def wrapped_process(self):
        self.login_in = ocvl_user.name
        self.password_in = ocvl_user.password
        current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        baner_dir = os.path.abspath(os.path.join(current_dir, "../../datafiles/"))
        loc_filepath = os.path.join(baner_dir, "splash_banner.png")
        image = cv2.imread(loc_filepath)
        if ocvl_auth.ocvl_version is COMMUNITY_VERSION:
            image = image[0:512, 0:1024]
            font_color = (0, 233, 0)
            img_org = (330, 107)
        else:
            image = image[512:1024, 0:1024]
            font_color = (236, 189, 0)
            img_org = (358, 107)
        author_text = "{} Copyright(C) 2018".format(OCVL_AUTHORS)
        font_face = cv2.FONT_HERSHEY_PLAIN
        font_scale = thickness = 1


        image = cv2.putText(image, "v.{}".format(OCVL_VERSION), img_org, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, font_color)
        retval, baseLine = cv2.getTextSize(author_text, font_face, font_scale, thickness)

        image = cv2.putText(image, author_text, (1024 - retval[0] - 10, 505), font_face, font_scale, (255, 255, 255))
        image, self.image_out = self._update_node_cache(image=image, resize=False)
        self.make_textures(image, uuid_=self.image_out, width=1024, height=1024)

    def _update_node_cache(self, image=None, resize=False, uuid_=None):
        old_image_out = self.image_out
        self.socket_data_cache.pop(old_image_out, None)
        uuid_ = uuid_ if uuid_ else str(uuid.uuid4())
        self.socket_data_cache[uuid_] = image
        return image, uuid_

    def draw_buttons(self, context, layout):
        self.draw_preview(layout=layout, prop_name="image_out", location_x=10, location_y=50, proportion=0.5)
        if ocvl_auth.ocvl_version is COMMUNITY_VERSION:
            self.layout_for_community_version(context, layout)
        if ocvl_auth.ocvl_version is PRO_VERSION:
            self.layout_for_pro_version(context, layout)

    def layout_for_community_version(self, context, layout):
        self.layout_start_work(context, layout)
        if not ocvl_user.is_login:
            self.layout_auth_form(context, layout)

    def layout_add_store_link(self, row):
        row.operator('wm.recover_last_session', text='Recover last session', icon="RECOVER_LAST")
        if ocvl_user.is_login:
            row.operator('wm.url_open', text="Store".format(self.bl_label), icon='MOD_CLOTH').url = OCVL_LINK_TO_STORE + "?token={}".format(ocvl_user.token)
        else:
            row.operator('wm.url_open', text="Create account".format(self.bl_label), icon='INFO').url = OCVL_LINK_TO_CREATE_ACCOUNT

    def layout_start_work(self, context, layout):
        row = layout.row()
        row.operator('node.clean_desk', text="Start with blank desk", icon='FILE_TICK')
        self.layout_add_store_link(row)
        row = layout.row()
        col = row.column()
        col_split = col.split(factor=0.5, align=True)
        col_split.operator('node.tutorial_show_first_step', text="Tutorial - First steps", icon='PARTICLES')
        col_split.operator('wm.url_open', text="More mutorials".format(self.bl_label), icon='INFO').url = OCVL_LINK_TO_MORE_TUTORIALS
        for i, tutorial in enumerate(ocvl_user.local_tutorials):
            if i % 2:
                col_split = col.split(factor=0.5, align=True)
            text = tutorial.get("name")
            icon = tutorial.get("icon", "URL")
            col_split.operator('wm.url_open', text=text.format(self.bl_label), icon=icon).url = ocvl_user.tutorials.get("package_site", "http://kube.pl")

    def layout_auth_form(self, context, layout):
        row = layout.row()
        row.prop(self, "login_in", "Login")
        row.prop(self, "password_in", "Password")
        row.prop(self, "is_remember_in", "Remember")
        # get_args = OCVL_AUTH_PARAMS_LOGIN_PASSWORD_TEMPALTE.format(login=self.login_in, password=self.password_in)
        username = self.login_in
        password = self.password_in
        row.operator('node.login_in_request_in_splash', text='Submit', icon='FILE_TICK').origin = self.get_node_origin(props_name=[username, password])

    def layout_for_pro_version(self, context, layout):
        if ocvl_auth.ocvl_pro_version_auth:
            self.layout_start_work(context, layout)
        else:
            # pass
        # if 1:
            col = layout.column(align=True)

            self.add_button(layout, "is_licence_key")

            if not self.is_licence_key:
                row = layout.row()
                row.prop(self, "login_in", "Login")
                row.prop(self, "password_in", "Password")
                row.prop(self, "is_remember_in", "Remember")
                get_args = OCVL_AUTH_PARAMS_LOGIN_PASSWORD_TEMPALTE.format(login=self.login_in, password=self.password_in)
                get_fn_url = 'login'
            else:
                row = layout.row()
                row.prop(self, "licence_key_in", "Licence Key")
                get_args = OCVL_AUTH_PARAMS_LICENCE_KEY_TEMPALTE.format(licence_key=self.licence_key_in)
                get_fn_url = 'licence'
            row = layout.row()
            row.operator('node.login_in_request_in_splash', text='Submit', icon='FILE_TICK').origin = self.get_node_origin(props_name=[get_fn_url, get_args])
            row = layout.row()
            col = row.column()
            col_split = col.split(factor=0.5, align=True)
            col_split.operator('node.tutorial_show_first_step', text="Tutorial - First steps", icon='PARTICLES')
            col_split.operator('node.clean_desk', text="Start with blank desk - Community version", icon='RESTRICT_VIEW_OFF')
