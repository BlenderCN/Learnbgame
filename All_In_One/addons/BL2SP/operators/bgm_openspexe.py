#import bpy
#import os

#class bgmopenspexe(bpy.types.Operator):
#    bl_idname = "my_operator.bgmopenspexe"
#    bl_label = "Bgmsppath"
#    bl_description = ""
#    bl_options = {"REGISTER"}
#    
#    filename_ext = ".txt"

#    filter_glob = bpy.props.StringProperty(
#            default="*.txt",
#            options={'HIDDEN'},
#            maxlen=255,  # Max internal buffer length, longer would be clamped.
#            )
#    directory = bpy.props.StringProperty(subtype='DIR_PATH')
#    
#    @classmethod
#    def poll(cls, context):
#        return True

#    def execute(self, context):

#        return {"FINISHED"}
    
import bpy
import os
import sys
# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
def writetxt(path):
    print(sys.argv[0])
    fp=open(sys.argv[0]+'sppath.txt',"w")
    fp.write(path)
    fp.close()
    
    

class ImportFilesCollection(bpy.types.PropertyGroup):
    name = StringProperty(
            name="File Path",
            description="Filepath used for importing the substance painter.exe",
            maxlen=1024,
            subtype='FILE_PATH',
            )
bpy.utils.register_class(ImportFilesCollection)


class ImportSomeData(Operator, ImportHelper):
    """Find Substance Painter execute Path"""
    bl_idname = "my_operator.bgmopenspexe"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Substance Painter exe"

    # ImportHelper mixin class uses this
    filename_ext = ".exe"
    filter_glob = StringProperty(
            default="*Painter.exe",
            options={'HIDDEN'},
            )
            
    files = bpy.props.CollectionProperty(type=ImportFilesCollection)


    def execute(self, context):
        print(len(self.files))
        for i, f in enumerate(self.files, 1):
            print("File %i: %s" % (i, f.name))  
            print("Second file:", self.filepath.replace("\\","\\\\"))  
            str= self.filepath.replace("\\","\\\\")
            writetxt(str)   
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="Text Import Operator")


#def register():
#    bpy.utils.register_class(ImportSomeData)
#    bpy.types.INFO_MT_file_import.append(menu_func_import)


#def unregister():
#    bpy.utils.unregister_class(ImportSomeData)
#    bpy.types.INFO_MT_file_import.remove(menu_func_import)


#if __name__ == "__main__":
#    register()

#    # test call
#    bpy.ops.import_test.some_data('INVOKE_DEFAULT')