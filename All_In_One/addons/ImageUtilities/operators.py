import bpy
import os
from bpy.types import Operator
from .imageFile_utils import ImageFormatEnum
from .csv_util import csvToDic, dicToCsv, appendDicToCsv,inCsv

csvName = "_materialCSV"


def getCsvPath():
    global csvName
    '''Checks if a valid File path exists other wise adds a new file in the same directory as the .blend file'''
    wm = wm = bpy.context.window_manager

    blendPath = bpy.path.abspath('//')
    blendFile = bpy.data.filepath
    blendFile = os.path.basename(blendFile)
    filename, file_extension = os.path.splitext(blendFile)
    fn = filename + csvName + ".csv"

    if wm.csv_dir == '' or wm.csv_dir is None:
        fn = os.path.join(blendPath, fn)
    else:
        fn = os.path.join(wm.csv_dir, fn)
    return fn

class IMAGES_change_extension(Operator):
    """Replaces image file extensions"""
    bl_idname = "images.path_change_extension"
    bl_label = "Change All Image Extensions"
    bl_description = "Replace the image file extension with an other file type. For example jpg with png"
    bl_options = {'REGISTER', 'UNDO'}


    my_fileFormat = bpy.props.EnumProperty(
        items=ImageFormatEnum.items,
        name="File Extensions",
        default = 'png',
        description="",
        )

    @classmethod
    def poll(cls, context):
        return True


    def execute(self, context):
        extension = self.my_fileFormat
        for img in bpy.data.images:
            if img.filepath != '':
                filename, file_extension = os.path.splitext(img.filepath)
                newFilepath = filename + "." + str(extension)
                img.filepath = newFilepath

        return {'FINISHED'}

class IMAGES_export_csv(Operator):
    """Export all texturepaths to a csv file"""
    bl_idname = "images.path_export_csv"
    bl_label = "Export Textures to CSV"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}


    my_append = bpy.props.BoolProperty(name= "append", default = False)
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.file.make_paths_absolute()

        imageData = bpy.data.images
        assets = {}

        fn = getCsvPath()

        for img in imageData:
            properties = [img.size[0],img.size[1],img.filepath]
            assets[img.name] = properties

        if self.my_append == False:
            dicToCsv(fn,assets)
        else:
           appendDicToCsv(fn, assets)
        bpy.ops.file.make_paths_relative()
        return {'FINISHED'}

class IMAGES_print_csv(Operator):
    """Create a new Mesh Object"""
    bl_idname = "images.path_print_import_csv"
    bl_label = "Print CSV"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        fn = getCsvPath()
        dic = csvToDic(fn)
        print (str(dic))
        bpy.ops.file.make_paths_relative()
        return {'FINISHED'}

class IMAGES_import_paths_from_csv(Operator):
    """Create a new Mesh Object"""
    bl_idname = "images.load_from_csv"
    bl_label = "Import CSV"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        fn = getCsvPath()
        dic = csvToDic(fn)

        for key, imgData in dic.items():
            if key in bpy.data.images:
                if bpy.data.images[key] is not None:
                    bpy.data.images[key].filepath = imgData[2]
        print (str(dic))
        bpy.ops.file.make_paths_relative()
        return {'FINISHED'}

class IMAGES_load_paths_from_csv_02(Operator):
    """Load image paths from csv and replace '.001' with '' """
    bl_idname = "images.load_from_csv_replace001"
    bl_label = "Import CSV 02"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        fn = getCsvPath()
        dic = csvToDic(fn)

        for key, imgData in dic.items():
            if key in bpy.data.images:
                if bpy.data.images[key] is not None:
                    bpy.data.images[key].filepath = imgData[2]
            elif key.replace(".001", "") in bpy.data.images:
                if bpy.data.images[key.replace(".001", "")] is not None:
                    bpy.data.images[key.replace(".001", "")].filepath = imgData[2]

        print (str(dic))
        bpy.ops.file.make_paths_relative()
        return {'FINISHED'}


############# DEBUG OPERATORS #############
class IMAGES_import_csv(Operator):
    """Print csv content (mainly debug function)"""
    bl_idname = "images.path_print_csv"
    bl_label = "Print CSV"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True


    def execute(self, context):
        fn = getCsvPath()
        dic = csvToDic(fn)
        print (str(dic))

        return {'FINISHED'}



class IMAGES_findIn_csv(Operator):
    """Create a new Mesh Object"""
    bl_idname = "images.find_in_csv"
    bl_label = "Print CSV"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True


    def execute(self, context):
        imageData = bpy.data.images[7].name
        print(imageData)
        fn = getCsvPath()
        key, line = inCsv(fn,imageData)
        print ("#######################" + key + str(line))
        bpy.ops.file.make_paths_relative()
        return {'FINISHED'}


