import bpy
import cv2
import numpy as np
from bpy.types import Header, Menu
from bpy.types import INFO_HT_header as INFO_HT_header_old


def cv_lab_info(scene):
    cv_version = "CV:{}".format(cv2.__version__)
    np_version = "NumPy:{}".format(np.version.full_version)

    images_number = len(bpy.data.images)
    imgs_total_size = 0
    for img in bpy.data.images:
        imgs_total_size += img.size[0] * img.size[1] * img.depth

    imgs_total_size = "Img:{0:.2f}MB".format(imgs_total_size/(8*1024*1024))

    original_statistics = scene.statistics().split("|")
    blender_version = bpy.app.version
    blender_version_2 = original_statistics[0]
    blender_memory = original_statistics[6]

    node_number = 0
    for node_group in bpy.data.node_groups.values():
        node_number += len(node_group.nodes)
    node_number = "Nodes:{}".format(node_number)
    return "|".join([blender_version_2, cv_version, np_version, imgs_total_size, node_number, blender_memory])



class INFO_HT_header_new(Header):
    bl_space_type = 'INFO'

    def draw(self, context):
        layout = self.layout

        window = context.window
        scene = context.scene
        rd = scene.render

        row = layout.row(align=True)
        row.label(icon='INFO')
        # row.template_header()

        if context.area.show_menus:
            sub = row.row(align=True)
            sub.menu("INFO_MT_file_new")
            sub.menu("INFO_MT_window_new")
            sub.menu("INFO_MT_help_new")

        if window.screen.show_fullscreen:
            # layout.operator("screen.back_to_previous", icon='SCREEN_BACK', text="Back to Previous")
            layout.operator("screen.escape_full_screen", icon='SCREEN_BACK', text="Back to Previous")
            layout.separator()

        layout.separator()


        layout.separator()

        layout.template_running_jobs()

        layout.template_reports_banner()

        row = layout.row(align=True)
        row.operator("node.show_node_splash", text="", icon='COLOR', emboss=False)
        row.label(text=cv_lab_info(scene=scene))


class INFO_MT_file_new(Menu):
    bl_label = "File"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.read_homefile", text="New", icon='NEW')
        layout.operator("wm.open_mainfile", text="Open...", icon='FILE_FOLDER')
        layout.menu("INFO_MT_file_open_recent", icon='OPEN_RECENT')
        layout.operator("wm.revert_mainfile", icon='FILE_REFRESH')
        layout.operator("wm.recover_last_session", icon='RECOVER_LAST')
        layout.operator("wm.recover_auto_save", text="Recover Auto Save...", icon='RECOVER_AUTO')

        layout.separator()

        layout.operator_context = 'EXEC_AREA' if context.blend_data.is_saved else 'INVOKE_AREA'
        layout.operator("wm.save_mainfile", text="Save", icon='FILE_TICK')

        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.save_as_mainfile", text="Save As...", icon='SAVE_AS')
        layout.operator_context = 'INVOKE_AREA'
        layout.operator("wm.save_as_mainfile", text="Save Copy...", icon='SAVE_COPY').copy = True

        layout.separator()

        layout.operator_context = 'EXEC_AREA'
        if bpy.data.is_dirty and context.user_preferences.view.use_quit_dialog:
            layout.operator_context = 'INVOKE_SCREEN'  # quit dialog
        layout.operator("wm.quit_blender", text="Quit", icon='QUIT')


class INFO_MT_window_new(Menu):
    bl_label = "Window"

    def draw(self, context):
        import sys

        layout = self.layout

        layout.operator("wm.window_duplicate")
        layout.operator("wm.window_fullscreen_toggle", icon='FULLSCREEN_ENTER')

        layout.separator()

        layout.operator("screen.screenshot")

        if sys.platform[:3] == "win":
            layout.separator()
            layout.operator("wm.console_toggle", icon='CONSOLE')


class INFO_MT_help_new(Menu):
    bl_label = "Help"

    def draw(self, context):
        layout = self.layout

        layout.operator(
                "wm.url_open", text="OCVL Documentation", icon='HELP',
                ).url = "http://opencv-laboratory.readthedocs.io/en/latest/?badge=latest"
        layout.operator(
                "wm.url_open", text="OpenCV Documentation", icon='HELP',
                ).url = "https://docs.opencv.org/3.0-beta/index.html"
        layout.operator(
                "wm.url_open", text="Blender Documentation", icon='HELP',
                ).url = "https://docs.blender.org/manual/en/dev/editors/node_editor/introduction.html"
        layout.separator()

        layout.operator(
                "wm.url_open", text="OCVL Web Panel", icon='URL',
                ).url = "https://ocvl-cms.herokuapp.com/admin/login/"
        layout.operator(
                "wm.url_open", text="OCVL Blog", icon='URL',
                ).url = "http://kube.pl/"

        layout.separator()

        layout.operator("node.show_node_splash", icon='COLOR')


classes_to_unregister = [
    INFO_HT_header_old,
]

classes = [
    INFO_HT_header_new,
    INFO_MT_file_new,
    INFO_MT_window_new,
    INFO_MT_help_new,
]