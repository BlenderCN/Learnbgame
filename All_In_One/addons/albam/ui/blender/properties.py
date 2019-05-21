import bpy

from albam.registry import albam_registry


@albam_registry.blender_prop_group()
class AlbamImportedItem(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(options={'HIDDEN'})
    source_path : bpy.props.StringProperty(options={'HIDDEN'})
    folder : bpy.props.StringProperty(options={'HIDDEN'}) # Always in posix format
    data : bpy.props.StringProperty(options={'HIDDEN'}, subtype='BYTE_STRING')
    file_type : bpy.props.StringProperty(options={'HIDDEN'})


@albam_registry.blender_prop(bpy.types.Object, 'albam_imported_item', bpy.props.PointerProperty)
class AlbamImportedItemProp():
    kwargs = {
        'type': 'AlbamImportedItem'
    }


@albam_registry.blender_prop(bpy.types.Scene, 'albam_items_imported', bpy.props.CollectionProperty)
class AlbamImportedItemProp():
    kwargs = {
        'type': 'AlbamImportedItem'
    }


@albam_registry.blender_prop(bpy.types.Scene,
                             'albam_item_to_export',
                             bpy.props.StringProperty)
class AlbamItemToExport():
    kwargs = {
        'name': 'label'
    }
