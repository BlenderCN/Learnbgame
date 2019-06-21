import bpy
import inspect

def functions_item(self,context):
    items = []
    from . import func_picker as mod

    for name,func in inspect.getmembers(mod, inspect.isfunction) :
            if inspect.getmodule(func) == mod :
                items.append((name,name,""))

    return items

def bones_item(self,context) :
    items = []

    if context.scene.UI.rig :
        for bone in context.scene.UI.rig.pose.bones :
            items.append((bone.name,bone.name,''))
    return items

class ObjectUISettings(bpy.types.PropertyGroup) :
    shape_type = bpy.props.EnumProperty(items = [(i.upper(),i,"") for i in ('Bone','Display','Function')])
    function = bpy.props.StringProperty()
    arguments = bpy.props.StringProperty()
    shortcut = bpy.props.StringProperty()
    name = bpy.props.StringProperty()


class SceneUISettings(bpy.types.PropertyGroup) :
     rig = bpy.props.PointerProperty(type=bpy.types.Object)
     canevas = bpy.props.PointerProperty(type=bpy.types.Object)
     symmetry = bpy.props.PointerProperty(type=bpy.types.Object)
     functions = bpy.props.EnumProperty(items = functions_item)
     #bone_list = bpy.props.EnumProperty(items = bones_item)

class FunctionSelector(bpy.types.Operator):
     bl_label = "Select function"
     bl_idname = "rigui.function_selector"
     bl_property = "functions"
     #bl_options = {'REGISTER', 'UNDO'}

     functions = SceneUISettings.functions

     def execute(self, context):
         ob = context.object
         ob['UI']['function'] = self.functions
         context.area.tag_redraw()
         return {'FINISHED'}

     def invoke(self, context, event):
         wm = context.window_manager
         wm.invoke_search_popup(self)
         return {'FINISHED'}
