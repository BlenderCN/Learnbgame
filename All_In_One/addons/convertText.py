
# from http://blender.stackexchange.com/a/27926

bl_info = {
    "name" : "text objects to-from xml",
    "author" : "chebhou",
    "version" : (1, 0),
    "blender" : (2, 7, 3),
    "location" : "file->export->text to-from xml",
    "discription" : "copys an text objectx from-to xml file",
    "warning" : "this add-on is extremly unusefull",
    "wiki_url" : "http://blender.stackexchange.com/a/27926",
    "tracker_url" : "chebhou@gmail.com",
    "category" : "Import-Export"
    }

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy.props import EnumProperty, BoolProperty
from xml.dom import minidom
from xml.dom.minidom import Document

def txt_sync(filepath):
    dom = minidom.parse(filepath)
    scenes =dom.getElementsByTagName('scene')
    for scene in scenes:
        scene_name=scene.getAttribute('name')
        print("\n",scene_name)
        bl_scene = bpy.data.scenes[scene_name]
        txt_objs =scene.getElementsByTagName('object')
        for obj in txt_objs:
            obj_name = obj.getAttribute('name')
            obj_body = obj.childNodes[0].nodeValue 
            bl_obj = bl_scene.objects[obj_name].data.body = obj_body
            print(obj_name,"  ",obj_body)

def txt_export(filepath):

    doc = Document()
    root = doc.createElement('data')
    doc.appendChild(root)

    for sce in bpy.data.scenes :
        #create a scene
        scene = doc.createElement('scene')
        scene.setAttribute('name', sce.name)
        root.appendChild(scene)

        for obj in sce.objects :
            if obj.type == 'FONT':   
                #add object element
                object = doc.createElement('object')
                object.setAttribute('name', obj.name)
                txt_node = doc.createTextNode(obj.data.body)
                object.appendChild(txt_node) 
                scene.appendChild(object)

    #write to a file
    file_handle = open(filepath,"wb")

    file_handle.write(bytes(doc.toprettyxml(indent='\t'), 'UTF-8'))
    file_handle.close()

class   text_export(Operator, ExportHelper):  

    """write and read text objects to a file"""        
    bl_idname = "export_scene.text_xml"  
    bl_label = "text from-to xml"     
    bl_options = {'REGISTER', 'UNDO'}    #should remove undo ? 

    # ExportHelper mixin class uses this
    filename_ext = ".xml"

    #parameters and variables
    convert = EnumProperty(
                name="Convert",
                description="Choose conversion",
                items=(('W', "write objects", "write text objects to xml"),
                       ('R', "read objects", "read text objects from xml")),
                default='W',
                )

    #main function
    def execute(self, context): 
        bpy.ops.object.mode_set(mode = 'OBJECT')
        if self.convert == 'W':
            txt_export(self.filepath)
        else:
            txt_sync(self.filepath)

        bpy.context.scene.update()
        self.report({'INFO'},"Conversion is Done")
        return {'FINISHED'}

def menu_func_export(self, context):
    self.layout.operator(text_export.bl_idname, text="Text to-from xml")

def register():
    bpy.utils.register_class(text_export)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(text_export)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":  
    register()


