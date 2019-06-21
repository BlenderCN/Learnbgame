import bpy.app
import bpy.props
import bpy.types
import bpy.utils
from .cqtc_tools_panel import CqtcToolsPanel
from .change_strips_channel_operator import ChangeStripsChannelOperator
from .preferences import CqtcToolsPreferences
from . import handlers

def register():
	bpy.utils.register_class(ChangeStripsChannelOperator)
	bpy.utils.register_class(CqtcToolsPanel)
	bpy.utils.register_class(CqtcToolsPreferences)
	
	handlers.register_handlers()


def unregister():
	bpy.utils.unregister_class(ChangeStripsChannelOperator)
	bpy.utils.unregister_class(CqtcToolsPanel)
	bpy.utils.unregister_class(CqtcToolsPreferences)

	handlers.unregister_handlers()

if __name__ == "__main__":
	register()
