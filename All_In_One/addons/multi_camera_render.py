######################################################################################################
# An add-on to render automaticaly with all the selected camera                                      #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################
  
  
############# Add-on description (used by Blender)

bl_info = {
    "name": "Multiple camera rendering",
    "description": "Render with all the camera selected",
    "author": "Lapineige",
    "version": (2, 1),
    "blender": (2, 7, 1),
    "location": "Properties > Render > Multiple Camera Render",
    "warning": "", 
    "wiki_url": "http://www.le-terrier-de-lapineige.over-blog.com",
    "tracker_url": "http://blenderlounge.fr/forum/viewtopic.php?f=18&t=622",
    "category": "Learnbgame",
}
############# 

import bpy
from os.path import isdir

bpy.types.Scene.MultiOutputDir = bpy.props.StringProperty(subtype='DIR_PATH', default='//', description="Output directory for the render")
bpy.types.Scene.MultiOutputFile = bpy.props.StringProperty(subtype='FILE_NAME', default='Render_', description='Render file name suffix. Can be empty')
bpy.types.Scene.MultiOutputNameMode = bpy.props.EnumProperty(items=[('0', 'Number', "Use a counter as suffix", 1), ('1', 'Name', "Use the camera's name as suffix", 2)], description="Suffix type for the render images")

############### Operator
class MultiCameraRender(bpy.types.Operator):
    """ Render with all camera selected """
    bl_idname = "render.multiple_camera_render"
    bl_label = "Multiple Camera Render"

    @classmethod
    def poll(cls, context):
        return True in [obj.type == 'CAMERA' for obj in context.selected_objects]

    def execute(self, context):
        print()
        previous = bpy.context.area.type
        context.area.type = 'VIEW_3D'
        count = 0
        context.scene.MultiOutputDir = bpy.path.abspath(context.scene.MultiOutputDir)
        if not isdir(context.scene.MultiOutputDir):
            context.scene.MultiOutputDir = bpy.path.abspath('//')
        print('Output directory: ' + context.scene.MultiOutputDir)
        for obj in context.selected_objects:
            if obj.type == 'CAMERA':
                count += 1
                context.scene.camera = obj
                bpy.ops.render.render()
                #print('Rendering with camera: ' + obj.name)
                render = bpy.data.images['Render Result'].copy()
                if int(context.scene.MultiOutputNameMode):
                    #print('File created: "' + context.scene.MultiOutputFile + obj.name + bpy.context.scene.render.file_extension + '"')
                    render.save_render(context.scene.MultiOutputDir + context.scene.MultiOutputFile + obj.name + bpy.context.scene.render.file_extension)
                else:
                    #print('File created: "' + context.scene.MultiOutputFile + str(count) + bpy.context.scene.render.file_extension + '"')
                    render.save_render(context.scene.MultiOutputDir + context.scene.MultiOutputFile + str(count) + bpy.context.scene.render.file_extension)
        
        self.report({'INFO'}, str(count) + " files created at: " + context.scene.MultiOutputDir)
        context.area.type = previous
        #print()
        return {'FINISHED'}

#################### Panel
class MultiCameraRendering(bpy.types.Panel):
    """ Label with some options for add-on Multi-Camera Rendering """
    bl_label = "Multi-Camera Render"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "MultiOutputFile", text='File Prefix')
        row = layout.row()
        row.label(text='Suffix type:')
        row.prop(context.scene, "MultiOutputNameMode", expand=True)
        layout.prop(context.scene, "MultiOutputDir", text='Directory')
        layout.operator("render.multiple_camera_render")


def register():
    bpy.utils.register_class(MultiCameraRender)
    bpy.utils.register_class(MultiCameraRendering)
    
def unregister():
    bpy.utils.unregister_class(MultiCameraRender)
    bpy.utils.unregister_class(MultiCameraRendering)


if __name__ == "__main__":
    register()

