bl_info = {"name": "Hand Drawn NPR",
           "category": "Learnbgame"
}

if "bpy" in locals():
    import importlib

    if "properties" in locals():
        importlib.reload(properties)
    if "ui" in locals():
        importlib.reload(ui)
    if "operators" in locals():
        importlib.reload(operators)
    if "engine" in locals():
        importlib.reload(engine)

import logging
import os
import tempfile

# Log to temporary directory.
log_file = os.path.join(tempfile.gettempdir(), "hand_drawn_npr.log")
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s",
                    filename=log_file,
                    filemode="w")
# Set log level for third party modules.
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

print(bl_info["name"] + " logging path: " + log_file)


def register():
    logger.debug("Registering classes...")

    from .view_controller import operators
    from .view_controller import properties
    from .view_controller import ui
    from .view_controller import helpers

    operators.register()
    properties.register()
    ui.register()
    helpers.set_pre_hook()


def unregister():
    logger.debug("Unregistering classes...")

    from .view_controller import operators
    from .view_controller import properties
    from .view_controller import ui

    operators.unregister()
    properties.unregister()
    ui.unregister()
