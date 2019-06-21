import bpy

from .misc_functions import update_folderpath_shot, update_folderpath_path

#dirpath props coll
class NDDirPathColl(bpy.types.PropertyGroup):
    '''name = StringProperty() '''
    path = bpy.props.StringProperty(subtype="DIR_PATH", name='Path')
    
class NDDirRenderColl(bpy.types.PropertyGroup):
    '''name = StringProperty() '''
    path = bpy.props.StringProperty(subtype="DIR_PATH", name='Path')
    
# scene props
class NDProps(bpy.types.PropertyGroup):
    '''name = StringProperty() '''
    dirpath_coll = bpy.props.CollectionProperty(type=NDDirPathColl, name='Directories')
    render_coll = bpy.props.CollectionProperty(type=NDDirRenderColl, name='Render Settings')
    shot_index = bpy.props.IntProperty(name='Shot', update=update_folderpath_shot, min=1, max=99)
    path_index = bpy.props.IntProperty(name='Index custom path', update=update_folderpath_path)
    #shot_category = bpy.props.EnumProperty()