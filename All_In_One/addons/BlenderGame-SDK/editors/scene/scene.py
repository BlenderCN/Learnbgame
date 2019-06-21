import bpy
from SDK_utils import *
from . import ressource_manager
from . import scene_types

@registerclass
class OP_NEW_Scene(bpy.types.Operator):
    bl_idname = "scene.new"
    bl_label = "New Scene"
    bl_property = "_items"

    template = Scene3D
    _items = bpy.props.EnumProperty(items=get_items, update=new_scene())

    def new_scene(self, context):
        if isinstance(_items, SceneType):
            _items() #create new scene from template

    def get_items(self, context):
        return resource_manager.list_children_ressources(scene_types.Scene)

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"FINISHED"}
