bl_info = {
    "name": "Export Move3D files",
    "author": "Alexandre Boeuf",
    "version": (0, 9, 2),
    "blender": (2, 69, 0),
    "location": "File > Import-Export",
    "description": "Export Move3D files (.p3d/.macro)",
    "category": "Learnbgame",
}

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper
import os
import math

def meshesAreEquals(obA, obB, typeMesh):

    ''' Compares vertices and polygons of the meshes of the two given objects to
        determine if they are geometrically the same i.e. if they have both the
        same vertices and faces '''
    
    if not obA or not obB or not obA.data or not obB.data:
        return False
        
    mA = obA.data
    mB = obB.data
    
    if type(mA) != typeMesh or type(mA) != typeMesh:
        return False
    
    if obA == obB:
        return True        
    
    if mA == mB:
        return True

    if mA.vertices == mB.vertices and mA.polygons == mB.polygons:
        return True

    # Comparing the number of vertices
    if len(mA.vertices) != len(mB.vertices):
        return False

    # Comparing the number of faces
    if len(mA.polygons) != len(mB.polygons):
        return False

    # Comparing faces
    for i in range(len(mA.polygons)):
        vA = mA.polygons[i].vertices
        vB = mB.polygons[i].vertices
        if len(vA) != len(vB):
            return False
        for j in range(len(vA)):
            if vA[j] != vB[j]:
                return False

    # Comparing vertices
    for i in range(len(mA.vertices)):
        vA = mA.vertices[i]
        vB = mB.vertices[i]
        for j in range(3):
            if obA.scale[j] * vA.co[j] != obB.scale[j] * vB.co[j]:
                return False

    # Meshes are equal
    return True

def sortObjects(bpy):

    ''' Return a dictionary with:
            keys: the p3d names of the geometrically equal meshes
            values: a list of the objects having the same mesh '''

    # Returns None if there is no active scene (not sure if possible)
    scene = bpy.context.scene
    if not scene:
        return None

    # Returns None if there is no object in the scene
    objects = scene.objects
    if not objects:
        return None
    k = 0
    while k < len(objects) and (not objects[k] or not objects[k].data or type(objects[k].data) != bpy.types.Mesh ): 
        k = k + 1
    ob = None
    if k < len(objects):
        ob = objects[k]
    if not ob or not ob.data or type(ob.data) != bpy.types.Mesh:
        return None

    # First object is added
    mesh = ob.data
    name = mesh.name.lower().replace(" ","_").replace(".","_")
    sortedObjects = {name: [ob]}

    # For every following object in the scene ...
    for i in range(1, len(objects)):
        found = False
        ob = objects[i]
        if not ob or not ob.data or type(ob.data) != bpy.types.Mesh:
            continue
        name = ob.data.name.lower().replace(" ","_").replace(".","_")
        # ... compare its mesh to every mesh we already stored ...
        for item in sortedObjects:
            if meshesAreEquals(ob, sortedObjects[item][0], bpy.types.Mesh):
                # we have this one already
                if len(name) < len(item):
                    # if it has a shorter name we update the key
                    sortedObjects[name] = sortedObjects[item]
                    del sortedObjects[item]
                    # and we add it to sortedObjects[name]
                    sortedObjects[name].append(ob)
                else:
                    # otherwise we add it to sortedObjects[item]
                    sortedObjects[item].append(ob)
                found = True
                break
        #  ... and store it if need be in a new item
        if not found:
            sortedObjects[name] = [ob]

    return sortedObjects

def writeString(file, string):
    ''' Write string into a file opened in byte mode with UTF+8 encoding '''
    file.write(bytes(string,"UTF+8"))

def exportMeshes(objects, macrosPath):
    ''' Export meshes as separate .macro files into the directory macrosPath '''
    if not objects:
        return
    for item in objects:
        if not objects[item]:
            continue
        if not objects[item][0]:
            continue
        mesh = objects[item][0].data
        scale = objects[item][0].scale
        if not mesh:
            continue
        vertices = mesh.vertices
        if not vertices:
            continue
        polygons = mesh.polygons
        if not polygons:
            continue
        try:
            file = open(os.path.join(macrosPath, item + '.macro'), 'wb')
        except IOError:
            file = None
        if file:
            writeString(file, 'p3d_add_desc_poly '+item+'\n')
            for v in vertices:
                writeString(file, '   p3d_add_desc_vert')
                writeString(file, ' {0:.6f}'.format(scale[0]*v.co[0]))
                writeString(file, ' {0:.6f}'.format(scale[1]*v.co[1]))
                writeString(file, ' {0:.6f}'.format(scale[2]*v.co[2]))
                writeString(file, '\n')
            writeString(file, '\n')
            for f in polygons:
                if f.vertices:
                    writeString(file, '   p3d_add_desc_face ')
                    for i in f.vertices:
                        writeString(file, '{0} '.format(i+1))
                    writeString(file, '\n')
            writeString(file, 'p3d_end_desc_poly\n')

def addObject(ob, macroName, filepath):
    if not ob:
        return None
    try:
        file = open(filepath, 'ab')
    except IOError:
        file = None
    if file:
        obName = ob.name.lower().replace(" ","_").replace(".","_")
        writeString(file, 'p3d_read_macro ')
        writeString(file, macroName)
        writeString(file, '.macro ')
        writeString(file, obName)
        writeString(file, '\np3d_set_prim_pos ')
        writeString(file, obName)
        writeString(file, '.' + macroName)
        writeString(file, ' {0:.6f}'.format(ob.location[0]))
        writeString(file, ' {0:.6f}'.format(ob.location[1]))
        writeString(file, ' {0:.6f}'.format(ob.location[2]))
        ob.rotation_mode = 'XYZ'
        writeString(file, ' {0:.6f}'.format(math.degrees(ob.rotation_euler[0])))
        writeString(file, ' {0:.6f}'.format(math.degrees(ob.rotation_euler[1])))
        writeString(file, ' {0:.6f}'.format(math.degrees(ob.rotation_euler[2])))
        if ob.active_material and ob.active_material.diffuse_color:
            writeString(file, '\np3d_set_prim_color ')
            writeString(file, obName)
            writeString(file, '.' + macroName)
            writeString(file, ' Any {0:.6f}'.format(ob.active_material.diffuse_color[0]))
            writeString(file, ' {0:.6f}'.format(ob.active_material.diffuse_color[1]))
            writeString(file, ' {0:.6f}'.format(ob.active_material.diffuse_color[2]))
            writeString(file, '\n\n')
        else:
            writeString(file, '\n\n')

def exportObjects(objects, filepath):
    ''' Assemble all objects in .macro file referencing the other .macro files '''
    if objects:
        try:
            file = open(filepath, 'wb')
        except IOError:
            file = None
        if file:
            file.close()
            for item in objects:
                for ob in objects[item]:
                    addObject(ob, item, filepath)

def logObjects(objects):
    if objects:
        try:
            file = open('/home/aboeuf/BuildingYoan/log.txt', 'wb')
        except IOError:
            file = None
        if file:
            for item in objects:
                writeString(file,'{0} -> [ '.format(item))
                for ob in objects[item]:
                    obName = ob.name.lower().replace(" ","_").replace(".","_")
                    writeString(file,'{0} '.format(obName))
                writeString(file,']\n');
            file.close()
                    

def exportScene(bpy, dirname, filename):
    objects = sortObjects(bpy)
    logObjects(objects)
    exportMeshes(objects, dirname)
    exportObjects(objects, os.path.join(dirname, filename))

class ExportP3D(bpy.types.Operator, ExportHelper):
    """Export scene or object to Move3D file(s)"""
    bl_idname = "export_scene.p3d"
    bl_label = "Export P3D"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".macro"
    filter_glob = StringProperty(
            default="*.macro",
            options={'HIDDEN'},
            )
    def execute(self, context):
        (dirname, filename) = os.path.split(self.properties.filepath)
        exportScene(bpy, dirname, filename)
        return {'FINISHED'}

def menu_func_export(self, context):
    self.layout.operator(ExportP3D.bl_idname, text="Move3D (.p3d/.macro)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
