import sys 
sys.path.append("/usr/local/lib/python3.7/dist-packages/")

import logging
import os

import bpy
import requests
from ocvl.core.exceptions import NoDataError
from ocvl.core.image_utils import convert_to_gl_image
from ocvl.core.register_utils import ocvl_register, ocvl_unregister
from ocvl.tutorial_engine.engine_app import NodeCommandHandler
from pynput.keyboard import Controller, Key

logger = logging.getLogger(__name__)
TUTORIAL_HEARTBEAT_INTERVAL_RTSP_REFRESH = 2


class OCVLImageFullScreenOperator(bpy.types.Operator):
    bl_idname = "image.image_full_screen"
    bl_label = "OCVL Image Full Screen"

    origin = bpy.props.StringProperty("")

    def modal(self, context, event):
        if event.type in {'ESC'}:
            return self._exit(context, exit_mode='CANCELLED')

        return {'PASS_THROUGH'}

    def _load_np_img_to_blender_data_image(self, img_name, img_data):
        bl_img = bpy.data.images.get(img_name)
        if bl_img:
            return bl_img
        gl_img_data = convert_to_gl_image(img_data)
        height, width = img_data.shape[:2]
        bl_img = bpy.data.images.new(img_name, width, height)
        bl_img.pixels = list(gl_img_data.flat)
        return bl_img

    def _exit(self, context, exit_mode='FINISHED'):
        bpy.context.area.type = "NODE_EDITOR"
        if context.window.screen.show_fullscreen:
            bpy.ops.screen.back_to_previous()
        return {exit_mode}

    def invoke(self, context, event):
        self.points = []
        self.points = []
        node_tree, node_name, *props_name = self.origin.split('|><|')
        self.node = node = bpy.data.node_groups[node_tree].nodes[node_name]
        self.props_name = props_name
        self.props_counter = 0
        if node.inputs["image_in"].is_linked:

            try:
                img_data = node.get_from_props("image_in")
                img_name = node.inputs.get("image_in").sv_get()
            except NoDataError as e:
                return {'CANCELLED'}
            bl_img = self._load_np_img_to_blender_data_image(img_name, img_data)
        else:
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)
        bpy.context.area.type = "IMAGE_EDITOR"
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.spaces.active.image = bl_img
        bpy.context.area.type = "IMAGE_EDITOR"
        bpy.ops.image.view_all(fit_view=True)
        bpy.ops.screen.screen_full_area()

        args = (self, context)

        return {'RUNNING_MODAL'}


class OCVLImageImporterOperator(bpy.types.Operator):
    bl_idname = "image.image_importer"
    bl_label = "Open Image"
    bl_options = {'REGISTER'}

    n_id = bpy.props.StringProperty(default='')

    filepath = bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for importing the font file",
        maxlen=1024, default="", subtype='FILE_PATH')

    origin = bpy.props.StringProperty("")

    def execute(self, context):
        node_tree, node_name = self.origin.split('|><|')
        node = bpy.data.node_groups[node_tree].nodes[node_name]
        node.loc_filepath = self.filepath
        node.loc_name_image = ''
        node.process()
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}



class EscapeFullScreenOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "screen.escape_full_screen"
    bl_label = "Escape Full Screen Operator"

    def execute(self, context):
        keyboard = Controller()
        keyboard.press(Key.esc)
        bpy.ops.screen.back_to_previous()
        return {'FINISHED'}


class OCVLImageFullScreenOperator(bpy.types.Operator):
    bl_idname = "image.image_full_screen"
    bl_label = "OCVL Image Full Screen"

    origin = bpy.props.StringProperty("")

    def modal(self, context, event):
        if event.type in {'ESC'}:
            return self._exit(context, exit_mode='CANCELLED')

        return {'PASS_THROUGH'}

    def _load_np_img_to_blender_data_image(self, img_name, img_data):
        bl_img = bpy.data.images.get(img_name)
        if bl_img:
            return bl_img
        gl_img_data = convert_to_gl_image(img_data)
        height, width = img_data.shape[:2]
        bl_img = bpy.data.images.new(img_name, width, height)
        bl_img.pixels = list(gl_img_data.flat)
        return bl_img

    def _exit(self, context, exit_mode='FINISHED'):
        if context.window.screen.show_fullscreen:
            bpy.ops.screen.back_to_previous()
        bpy.context.area.type = "NODE_EDITOR"
        return {exit_mode}

    def invoke(self, context, event):
        self.points = []
        self.points = []
        node_tree, node_name, *props_name = self.origin.split('|><|')
        self.node = node = bpy.data.node_groups[node_tree].nodes[node_name]
        self.props_name = props_name
        self.props_counter = 0
        if node.inputs["image_in"].is_linked:

            try:
                img_data = node.get_from_props("image_in")
                img_name = node.inputs.get("image_in").sv_get()
            except NoDataError as e:
                return {'CANCELLED'}
            bl_img = self._load_np_img_to_blender_data_image(img_name, img_data)
        else:
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)
        bpy.context.area.type = "IMAGE_EDITOR"
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.spaces.active.image = bl_img
        bpy.context.area.type = "IMAGE_EDITOR"
        bpy.ops.image.view_all(fit_view=True)
        bpy.ops.screen.screen_full_area()

        args = (self, context)

        return {'RUNNING_MODAL'}


class OCVLShowTextInTextEditorOperator(bpy.types.Operator):
    bl_idname = "text.show_help_in_text_editor"
    bl_label = "OCVL show help in text editor"

    origin = bpy.props.StringProperty("")

    def modal(self, context, event):

        if event.type in {'ESC'}:

            bpy.context.area.type = "NODE_EDITOR"
            if context.window.screen.show_fullscreen:
                bpy.ops.screen.back_to_previous()
            if 'TEXT_INPUT_NODE' in bpy.data.texts.keys():
                bpy.data.texts.remove(bpy.data.texts["TEXT_INPUT_NODE"])
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        bpy.context.area.type = "TEXT_EDITOR"
        node_tree, node_name, *props_name = self.origin.split('|><|')
        self.node = bpy.data.node_groups[node_tree].nodes[node_name]

        if node_name not in bpy.data.texts.keys():
            bpy.data.texts.new(node_name)
            text = bpy.data.texts[node_name]
            doc = getattr(self.node, '__doc__', None) or 'Lack of offline documentation.'
            text.write(doc)

        self.text = context.space_data.text = bpy.data.texts[node_name]
        context.space_data.show_line_numbers = True
        context.space_data.show_word_wrap = True
        context.space_data.show_syntax_highlight = True
        context.space_data.font_size = 16
        bpy.ops.screen.screen_full_area()

        return {'RUNNING_MODAL'}


class OCVLClearDeskOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "node.clean_desk"
    bl_label = "Clean Desk"

    def execute(self, context):
        for node_group in bpy.data.node_groups:
            for node in node_group.nodes:
                node.select = True
        bpy.ops.node.delete()
        return {'FINISHED'}


class OCVLRequestsSplashOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "node.login_in_request_in_splash"
    bl_label = "Requests Splash"

    origin = bpy.props.StringProperty("")

    def invoke(self, context, event):
        node_tree, node_name, username, password = self.origin.split('|><|')
        node = bpy.data.node_groups[node_tree].nodes[node_name]
        auth_node = self._get_auth_node(node_tree, node)
        return
        try:
            # logger.info("Request: {}".format(OCVL_PANEL_LOGIN_URL))
            login_data = {"username": username, "password": password}
            # response = requests.post(OCVL_PANEL_LOGIN_URL, data=login_data, headers={"Referer": "OCVL client"})
        except Exception as e:
            # logger.error("Request error: URL: {}, exception: {}".format(OCVL_PANEL_LOGIN_URL, e))
            # auth_problem(OCVL_PANEL_LOGIN_URL, str(e))
            response = requests.Response()

        if response.status_code == 200:
            pass
            # auth_remote_confirm(login_data, response, node=node)
        else:
            pass
            # auth_remote_reject(OCVL_PANEL_LOGIN_URL, response)
        auth_node["status_code"] = response.status_code
        auth_node["response_content"] = response.content


        return {'FINISHED'}

    @staticmethod
    def _get_auth_node(node_tree, fall_back):
        for link in bpy.data.node_groups[node_tree].links:
            if link.to_node.name == "TestUser":  # TODO: AUTH_NODE_NAME:
                return link.to_node
        return fall_back


class OCVLChangeThemeLightOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "node.change_theme_light"
    bl_label = "Theme light"

    def execute(self, context):
        # current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        # themes_dir = os.path.abspath(os.path.join(current_dir, "../../presets/interface_theme"))
        # filepath = os.path.join(themes_dir, "softblend.xml")
        # bpy.ops.script.execute_preset(
        #     filepath=filepath,
        #     menu_idname="USERPREF_MT_interface_theme_presets")
        # bpy.ops.wm.save_userpref()
        return {'FINISHED'}


class OCVLChangeThemeDarkOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "node.change_theme_dark"
    bl_label = "Theme dark"

    def execute(self, context):
        # current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        # themes_dir = os.path.abspath(os.path.join(current_dir, "../../presets/interface_theme"))
        # filepath = os.path.join(themes_dir, "graph.xml")
        # bpy.ops.script.execute_preset(
        #     filepath=filepath,
        #     menu_idname="USERPREF_MT_interface_theme_presets")
        # bpy.ops.wm.save_userpref()
        return {'FINISHED'}


class OCVLChangeThemeOrangeOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "node.change_themeorange"
    bl_label = "Theme orange"

    def execute(self, context):
        current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        themes_dir = os.path.abspath(os.path.join(current_dir, "../../presets/interface_theme"))
        filepath = os.path.join(themes_dir, "blend_swap_5.xml")
        bpy.ops.script.execute_preset(
            filepath=filepath,
            menu_idname="USERPREF_MT_interface_theme_presets")
        return {'FINISHED'}


class OCVLShowNodeSplashOperator(bpy.types.Operator):
    bl_idname = "node.show_node_splash"
    bl_label = "Show Node Splash"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'NODE_EDITOR':
                NodeCommandHandler.clear_node_groups()
                NodeCommandHandler.get_or_create_node_tree()
                NodeCommandHandler.create_node("OCVLAuthNode", location=(520, 560))
                NodeCommandHandler.create_node("OCVLSettingsNode", location=(-300, 240))
                NodeCommandHandler.create_node("OCVLDocsNode", location=(-300, 100))
                NodeCommandHandler.create_node("OCVLSplashNode", location=(-60, 460))

                NodeCommandHandler.connect_nodes("Splash", "settings", "Settings", "settings")
                NodeCommandHandler.connect_nodes("Splash", "docs", "Docs", "docs")
                NodeCommandHandler.connect_nodes("Auth", "auth", "Splash", "auth")
                NodeCommandHandler.view_all()
                return {'FINISHED'}
        return {'CANCELLED'}


class OCVLImageImporterOperator(bpy.types.Operator):
    bl_idname = "image.image_importer"
    bl_label = "Open Image"
    bl_options = {'REGISTER'}

    n_id = bpy.props.StringProperty(default='')

    filepath = bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for importing the font file",
        maxlen=1024, default="", subtype='FILE_PATH')

    origin = bpy.props.StringProperty("")

    def execute(self, context):
        node_tree, node_name = self.origin.split('|><|')
        node = bpy.data.node_groups[node_tree].nodes[node_name]
        node.loc_filepath = self.filepath
        node.loc_name_image = ''
        node.process()
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class OCVLGeneratePythonCodeOperator(bpy.types.Operator):
    bl_idname = "node.generate_python_code"
    bl_label = "Generate code"
    bl_options = {'INTERNAL'}

    n_id = bpy.props.StringProperty(default='')
    origin = bpy.props.StringProperty("")

    def execute(self, context):
        node_tree, node_name = self.origin.split('|><|')
        node = bpy.data.node_groups[node_tree].nodes[node_name]
        node.generate_code()
        return {'FINISHED'}


def register():
    ocvl_register(OCVLImageFullScreenOperator)
    ocvl_register(OCVLImageImporterOperator)

    ocvl_register(OCVLImageFullScreenOperator)
    ocvl_register(EscapeFullScreenOperator)
    ocvl_register(OCVLShowTextInTextEditorOperator)
    ocvl_register(OCVLClearDeskOperator)
    ocvl_register(OCVLRequestsSplashOperator)
    ocvl_register(OCVLChangeThemeLightOperator)
    ocvl_register(OCVLChangeThemeDarkOperator)
    ocvl_register(OCVLShowNodeSplashOperator)
    ocvl_register(OCVLImageImporterOperator)
    ocvl_register(OCVLGeneratePythonCodeOperator)


def unregister():
    ocvl_unregister(OCVLImageFullScreenOperator)
    ocvl_unregister(OCVLImageImporterOperator)

    ocvl_unregister(OCVLGeneratePythonCodeOperator)
    ocvl_unregister(OCVLImageImporterOperator)
    ocvl_unregister(OCVLShowNodeSplashOperator)
    ocvl_unregister(OCVLChangeThemeDarkOperator)
    ocvl_unregister(OCVLChangeThemeLightOperator)
    ocvl_unregister(OCVLRequestsSplashOperator)
    ocvl_unregister(OCVLClearDeskOperator)
    ocvl_unregister(OCVLShowTextInTextEditorOperator)
    ocvl_unregister(EscapeFullScreenOperator)
    ocvl_unregister(OCVLImageFullScreenOperator)
