######################## add-in info ######################

bl_info = {
    "name": "Export Collision Spheres",
    "category": "Import-Export",
    "author": "Julian Ewers-Peters",
    "location": "File > Import-Export"
}

######################## imports ##########################

import bpy
from bpy_extras.io_utils import ExportHelper
import os.path
import struct

######################## main #############################

class CollisionSphereExporter(bpy.types.Operator, ExportHelper):
    """Export Collision Spheres"""
    bl_idname   = "export.export_spheres"
    bl_label    = "Export Collision Spheres"
    bl_options = {'REGISTER'}
    
    filename_ext = ".bin"
    
    def execute(self, context):
        ## get list of objects from scene ##
        object_list = list(bpy.data.objects)
        
        ## write as binaries ##
        filepath_binary = self.filepath
        outputfile_binary = open(filepath_binary, 'wb')
        write_binary(object_list, outputfile_binary)
        outputfile_binary.close()

        ## write as java class ##
        filepath_java = filepath_binary[:-4] + '.java'
        outputfile_java = open(filepath_java, 'w')
        write_java(object_list, outputfile_java)
        outputfile_java.close()
        
        return {'FINISHED'}
        
def menu_func(self, context):
    self.layout.operator(CollisionSphereExporter.bl_idname, text="Export Collision Spheres (.bin & .java)");

######################## binary writer ####################

def write_binary(object_list, file):    
    for scene_obj in object_list:
        if(scene_obj.name[:4] == "csx_"):
            pack_and_write_float((float(scene_obj.location.x)), file)
            pack_and_write_float((float(scene_obj.location.y)), file)
            pack_and_write_float((float(scene_obj.location.z)), file)
            pack_and_write_float((float((scene_obj.dimensions.x / 2))), file)

def pack_and_write_float(float_data, file):
    # '>f' forces to write binary float in Big Endian format
    struct_out = struct.pack('>f', float_data)
    file.write(struct_out)

######################## java writer ######################

def write_java(object_list, file):     
    write_header(file)
    write_data_text(object_list, file)
    write_footer(file)

def write_floats_text(obj, file):
    file.write("    ")
    file.write("%.5f," %  obj.location.x)
    file.write("%.5f," %  obj.location.y)
    file.write("%.5f," %  obj.location.z)
    file.write("%.5f," % (obj.dimensions.x / 2))
    file.write("\n")
    
def write_data_text(object_list, file):
    file.write("    //coordinates and radii written as follows (one sphere per line): X.x, Y.y, Z.z, R.r\n")
    for scene_obj in object_list:    
        if(scene_obj.name[:4] == "csx_"):
            write_floats_text(scene_obj, file)    

def write_header(file):
    file.write("/*Collision Spheres*/\n")
    file.write("public class CollSphereData{\n")
    file.write("  public static float CollSphereCoords[] = new float[]{\n")

def write_footer(file):
    file.write("  }\n")        
    file.write("}")

######################## add-in functions #################

def register():
    bpy.utils.register_class(CollisionSphereExporter)
    bpy.types.INFO_MT_file_export.append(menu_func);
    
def unregister():
    bpy.utils.unregister_class(CollisionSphereExporter)
    bpy.types.INFO_MT_file_export.remove(menu_func);

if __name__ == "__main__":
    register()
