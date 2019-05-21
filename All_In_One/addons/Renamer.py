######################################################################################################
# A tool to easely renamer objects, materials,...                                                    #
# Actualy partly uncommented - if you do not understand some parts of the code,                      #
# please see further version or contact me                                                           #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################


############# Add-on description (used by Blender)

bl_info = {
    "name": "Renamer",
    "description": '',
    "author": "Lapineige",
    "version": (1, 0),
    "blender": (2, 71, 0),
    "location": "3D View > Toolself > Rename (tab)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "http://le-terrier-de-lapineige.over-blog.com/contact",
    "category": "Learnbgame"
}

import bpy

bpy.types.Scene.source_name = bpy.props.StringProperty()
bpy.types.Scene.new_name = bpy.props.StringProperty()
bpy.types.Scene.rename_mode = bpy.props.EnumProperty(items =[('objects','Object',"",1),('materials','Material',"",2),('textures','Texture',"",3),('meshes','Mesh',"",4),('lamps','Lamp',"",5),('scenes','Scene',"",6),('worlds','World',"",7)])
bpy.types.Scene.only_selection= bpy.props.BoolProperty(default=False)

class Rename(bpy.types.Operator):
    """  """
    bl_idname = "scene.rename"
    bl_label = "Rename"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        source_name = context.scene.source_name
        new_name = context.scene.new_name
        
        if context.scene.rename_mode == 'objects' and context.scene.only_selection:
            to_rename_list = bpy.data.objects
            for foo in to_rename_list:
                if source_name in foo.name and foo.select:
                    foo.name = foo.name[:foo.name.index(source_name)] + new_name + foo.name[foo.name.index(source_name)+len(source_name):]
        else:
            exec('to_rename_list = bpy.data.' + context.scene.rename_mode +'\n' +'for foo in to_rename_list:' +'\n'+ '    if source_name in foo.name:'+'\n'+'        foo.name = foo.name[:foo.name.index(source_name)] + new_name + foo.name[foo.name.index(source_name)+len(source_name):]')
        return {'FINISHED'}

class SwitchName(bpy.types.Operator):
    """  """
    bl_idname = "scene.switch_name"
    bl_label = "Switch source/new name"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        context.scene.new_name , context.scene.source_name = context.scene.source_name , context.scene.new_name
        return {'FINISHED'}

class RenamePanel(bpy.types.Panel):
    """ """
    bl_label = "Rename"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Rename"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "rename_mode", text="Mode")
        if context.scene.rename_mode == 'objects':
            layout.prop(context.scene, 'only_selection', text='Only Selected')
        layout.prop(context.scene, "source_name")
        layout.prop(context.scene, "new_name")
        row = layout.row(align=True)
        row.operator("scene.rename", icon="FILE_TEXT")
        row.operator("scene.switch_name", text='', icon="ARROW_LEFTRIGHT")


def register():
    bpy.utils.register_class(RenamePanel)
    bpy.utils.register_class(Rename)
    bpy.utils.register_class(SwitchName)



def unregister():
    bpy.utils.unregister_class(RenamePanel)
    bpy.utils.unregister_class(Rename)
    bpy.utils.unregister_class(SwitchName)


if __name__ == "__main__":
    register()
