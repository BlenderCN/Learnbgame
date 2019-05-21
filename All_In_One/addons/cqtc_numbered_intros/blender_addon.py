import bpy.props
import bpy.types
import bpy.utils
from .numbered_intro_panel import NumberedIntroPanel
from .numbered_intro_properties import NumberedIntroProperties
from .create_numbered_intro_operator import CreateNumberedIntroOperator
from . import locale


def register(name):
	bpy.utils.register_class(CreateNumberedIntroOperator)
	bpy.utils.register_class(NumberedIntroPanel)
	bpy.utils.register_class(NumberedIntroProperties)
	bpy.types.Scene.numbered_intro = bpy.props.PointerProperty(type=NumberedIntroProperties)
	bpy.app.translations.register(name, locale.translations)


def unregister(name):
	bpy.utils.unregister_class(CreateNumberedIntroOperator)
	bpy.utils.unregister_class(NumberedIntroPanel)
	bpy.utils.unregister_class(NumberedIntroProperties)
	del bpy.types.Scene.numbered_intro
	bpy.app.translations.unregister(name)

if __name__ == "__main__":
	register(__name__)
