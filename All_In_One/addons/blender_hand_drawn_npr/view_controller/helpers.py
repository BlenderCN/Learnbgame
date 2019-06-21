import logging

import bpy

logger = logging.getLogger(__name__)


def set_pre_hook():
    bpy.app.handlers.render_pre.append(set_pre)


def set_pre(dummy):
    bpy.ops.wm.create_npr_compositor_nodes()
    bpy.ops.wm.prepare_npr_settings()


def toggle_hook(self, context):
    if context.scene.system_settings.is_hook_enabled:
        logger.debug("Enabling hook...")
        bpy.app.handlers.render_post.append(render)
    else:
        logger.debug("Disabling hook...")
        bpy.app.handlers.render_post.remove(render)


def render(dummy):
    bpy.ops.wm.render_npr()
