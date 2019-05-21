bl_info = {
    "name": "Import Move3D files",
    "author": "Alexandre Boeuf",
    "version": (0, 9, 1),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "description": "Import Move3D files (.p3d/.macro)",
    "category": "Learnbgame"
}

import bpy
import os
import math
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

def read_macro(filepath):
    objects = []
    (dirname, filename) = os.path.split(filepath)
    (shortname, extension) = os.path.splitext(filename)
    try:
        with open(filepath, encoding='utf-8') as macrofile:
            for line in macrofile:
                line_list = line.split()
                if line_list:
                    if line_list[0] == 'p3d_set_prim_pos':
                        if len(line_list)>7:
                            object = None
                            for ob in objects:
                                if ob['name'] == line_list[1]:
                                    object = ob
                                    break
                            if object:
                                object['location'][0] = float(line_list[2])
                                object['location'][1] = float(line_list[3])
                                object['location'][2] = float(line_list[4])
                                object['rotation'][0] = math.radians(float(line_list[5]))
                                object['rotation'][1] = math.radians(float(line_list[6]))
                                object['rotation'][2] = math.radians(float(line_list[7]))
                    if line_list[0] == 'p3d_read_macro':
                        if len(line_list)>1:
                            sub_objects = read_macro(os.path.join(dirname, line_list[1]))
                            for ob in sub_objects:
                                if len(line_list)>2:
                                    ob['name'] = line_list[2]+'.'+ob['name']
                                objects.append(ob)
                    if line_list[0] == 'p3d_add_desc_poly':
                        object = {'name': shortname+'_'+str(len(objects)+1)}
                        object['mode'] = 'P3D_REAL';
                        object['vertices'] = []
                        object['faces'] = []
                        object['location'] = [0, 0, 0]
                        object['rotation'] = [0, 0, 0]
                        objects.append(object)
                        if len(line_list)>1:
                            object['name']=line_list[1]
                        if len(line_list)>2:
                            object['mode']=line_list[2]
                    if line_list[0] == 'p3d_add_desc_vert':
                        coords = []
                        for coord in line_list[1:]:
                            coords.append(float(coord))
                        ((objects[-1])['vertices']).append(coords)
                    if line_list[0] == 'p3d_add_desc_face':
                        indexes = []
                        for index in line_list[1:]:
                            indexes.append(int(index)-1)
                        ((objects[-1])['faces']).append(indexes)
    except FileNotFoundError:
        print('error: read_macro: '+filepath+': no such file')
    return objects

def add_object(object):
    bpy.ops.object.add(type='MESH')
    ob = bpy.context.object
    me = ob.data
    split = object['name'].split('.');
    me.name = split[-1]
    ob.name = me.name
    if(len(split)>1):
        ob.name = split[-2]
    me.from_pydata(object['vertices'],[],object['faces'])
    me.update()
    ob.location[0] = object['location'][0]
    ob.location[1] = object['location'][1]
    ob.location[2] = object['location'][2]
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler[0] = object['rotation'][0]
    ob.rotation_euler[1] = object['rotation'][1]
    ob.rotation_euler[2] = object['rotation'][2]

def import_meshes(filepath):
    objects = read_macro(filepath)
    for ob in objects:
        add_object(ob)

class ImportP3D(bpy.types.Operator, ImportHelper):
    """Load a Move3D file ()"""
    bl_idname = "import_scene.p3d"
    bl_label = "Import P3D"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".macro"
    filter_glob = StringProperty(
            default="*.p3d;*.macro",
            options={'HIDDEN'},
            )
    def execute(self, context):
        import_meshes(self.properties.filepath)
        return {'FINISHED'}
        
def menu_func_import(self, context):
    self.layout.operator(ImportP3D.bl_idname, text="Move3D (.p3d/.macro)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
