import bpy.props
import bpy.types
import bpy.utils
from .super_effect_panel import SuperEffectPanel
from .super_effect_properties import SuperEffectProperties, ModifyPropertyItemsOperator, SuperEffectIntegerPropertyItem, SuperEffectPositiveFloatPropertyItem, SuperEffectFactorPropertyItem
from .templates import AddSuperEffectTemplateOperator, LoadSuperEffectTemplateOperator, SetSuperEffectTemplateNameOperator, RemoveSuperEffectTemplateOperator
from .create_super_effect_operator import CreateSuperEffectOperator

def register():
	bpy.utils.register_class(CreateSuperEffectOperator)
	bpy.utils.register_class(SuperEffectPanel)
	bpy.utils.register_class(SuperEffectIntegerPropertyItem)
	bpy.utils.register_class(SuperEffectPositiveFloatPropertyItem)
	bpy.utils.register_class(SuperEffectFactorPropertyItem)
	bpy.utils.register_class(SuperEffectProperties)
	bpy.utils.register_class(ModifyPropertyItemsOperator)
	bpy.utils.register_class(AddSuperEffectTemplateOperator)
	bpy.utils.register_class(LoadSuperEffectTemplateOperator)
	bpy.utils.register_class(SetSuperEffectTemplateNameOperator)
	bpy.utils.register_class(RemoveSuperEffectTemplateOperator)
	bpy.types.Scene.super_effect = bpy.props.PointerProperty(type=SuperEffectProperties)

def unregister():
	bpy.utils.unregister_class(CreateSuperEffectOperator)
	bpy.utils.unregister_class(SuperEffectPanel)
	bpy.utils.unregister_class(SuperEffectIntegerPropertyItem)
	bpy.utils.unregister_class(SuperEffectPositiveFloatPropertyItem)
	bpy.utils.unregister_class(SuperEffectFactorPropertyItem)
	bpy.utils.unregister_class(SuperEffectProperties)
	bpy.utils.unregister_class(ModifyPropertyItemsOperator)
	bpy.utils.unregister_class(AddSuperEffectTemplateOperator)
	bpy.utils.unregister_class(LoadSuperEffectTemplateOperator)
	bpy.utils.unregister_class(SetSuperEffectTemplateNameOperator)
	bpy.utils.unregister_class(RemoveSuperEffectTemplateOperator)
	del bpy.types.Scene.super_effect

if __name__ == "__main__":
	register()
