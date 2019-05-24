# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    'name': 'Add Mesh: Integrated Library',
    'author': 'Jishnu <jishnu7@gmail.com>, ivo <ivo@ivogrigull.com>',
    'version': '0.2',
    'blender': (2, 56, 6),
    'location': 'Properties > Object > Library Panel',
    'description': 'Integrated Library',
    "category": "Learnbgame",
}

__bpydoc__ = """
Integrated Library

This add-on will help to save stages of mesh creation an adding your meshes quickly.

Usage:

This functionality can be accessed via the "Tool Shelf" in 3D View ([T] key).

Version history:

v0.1 - Initial revision. Seems to work fine for most purposes.
v0.2 - Updated to work with the API changes. Thanks to ivo <ivo@ivogrigull.com> for the update.

"""

import bpy
from bpy.props import *


FILE_NAME = ".library.conf"
def write_file(name,ver,fac,edg):
    f=open(FILE_NAME, 'a+')
    f.write(name + ":")
    for i in range(len(ver)):
        for j in range(len(ver[i])):
            f.write(str(ver[i][j]))
            if(j<len(ver[i])-1):
                f.write(" ")
            else:
                if(i<len(ver)-1):
                    f.write(",")
                else:
                    f.write("")
    f.write(":")
    for i in range(len(fac)):
        for j in range(len(fac[i])):
            f.write(str(fac[i][j]))
            if(j<(len(fac[i])-1)):
                f.write(" ")
            else:
                if(i<len(fac)-1):
                    f.write(",")
    f.write(":")
    for i in range(len(edg)):
        for j in range(len(edg[i])):
            f.write(str(edg[i][j]))
            if(j<(len(edg[i])-1)):
                f.write(" ")
            else:
                if(i<len(edg)-1):
                    f.write(",")
    f.write("\n")
    f.close()

# Function to extract data from a line
def s_split(line):
    ret=[]
    temp=[]
    line=line.split(",")
    for i in range(len(line)):
        line[i]=line[i].split(" ")
        for j in range(len(line[i])):
            try:
                temp.append(int(line[i][j]))
            except: temp.append(float(line[i][j]))
        ret.append(temp)
        temp=[]
    return ret

# Function to read from file.
# If no data is found, returns 0.
# If multiple data of same name in file, only the first one is returned.
def read_file(name):
    for line in open(FILE_NAME, 'r'):
        line=line.strip("\n")
        line=line.split(":")
        flag = 0
        if(line[0]==name):
            ret1=s_split(line[1])
            try:
                ret2=s_split(line[2])
            except:
                ret2=[]
            try:
                ret3=s_split(line[3])
            except:
                ret3=[]
            flag=1
            break
    if(flag==1):
        return ret1, ret2, ret3
    else:
        return 0

def mesh_names():
    names=[]
    for line in open(FILE_NAME, 'r'):
        line=line.strip("\n")
        line=line.split(":")
        names.append(line[0])
    return names

def delete_from_lib(obj_name):
    data_list=[]
    for line in open(FILE_NAME, 'r'):
        tmp = line.split(":")
        if (tmp[0] == obj_name):
            print ("Found")
        else:
            data_list.append(line)
    fout = open(FILE_NAME,'w')
    fout.writelines(data_list)
    fout.close()

def create_mesh_object(context, verts, edges, faces, name):

    # Get the current scene
    scene = context.scene
    
    # Get the active object.
    obj_act = scene.objects.active

    # Create new mesh
    mesh = bpy.data.meshes.new(name)

    # Make a mesh from a list of verts/edges/faces.
    mesh.from_pydata(verts, edges, faces)

    # Update mesh geometry after adding stuff.
    mesh.update()

    # Deselect all objects.
    bpy.ops.object.select_all(action='DESELECT')

    # Create new object
    ob_new = bpy.data.objects.new(name, mesh)

    # Link new object to the given scene and select it.
    scene.objects.link(ob_new)
    ob_new.select = True

    # Place the object at the 3D cursor location.
    ob_new.location = context.scene.cursor_location

    if obj_act and obj_act.mode == 'EDIT':
        # We are in EditMode, switch to ObjectMode.
        bpy.ops.object.mode_set(mode='OBJECT')

        # Select the active object as well.
        obj_act.select = True

        # Apply location of new object.
        scene.update()

        # Join new object into the active.
        bpy.ops.object.join()

        # Switching back to EditMode.
        bpy.ops.object.mode_set(mode='EDIT')

        ob_new = obj_act

    else:
        # We are in ObjectMode.
        # Make the new object the active one.
        scene.objects.active = ob_new

    return ob_new


class AddToLibrary(bpy.types.Operator):
    ''''''
    bl_idname = "object.add_to_library"
    bl_label = "Add Selected Object to Library"

    # do nothing if none selected
    @classmethod
    def poll(self, context):
        name = mesh_names()
        for i in name:
            if i == context.object.name:
                return 0
        return (context.active_object != None)

    def execute(self, context):
        obj_data = bpy.context.object.data
        
        # Save selected objects vertices
        verts = []
        for i in obj_data.vertices:
            temp = []
            for j in i.co:
                temp.append(j)
            verts.append(temp)

        # Save selected objects faces
        faces = []
        for i in obj_data.faces:
            temp = []
            for j in i.vertices:
                temp.append(j)
            faces.append(temp)

        edges = []
        for i in obj_data.edges:
            temp = []
            for j in i.vertices:
                temp.append(j)
            edges.append(temp)

        # Write object data to file
        write_file(context.object.name,verts,faces,edges)

        return {'FINISHED'}

class RemoveFromLibrary(bpy.types.Operator):
    ''''''
    bl_idname = "object.remove_from_library"
    bl_label = "Remove Selected Object to Library"
    
    obj_name = StringProperty(name = "Name of the object", attr="name")

    def execute(self, context):
        delete_from_lib(self.properties.obj_name)
        return {'FINISHED'}



class library(bpy.types.Operator):
    ''''''
    bl_idname = "object.add_from_library"
    bl_label = "Add an Object From Library"
    obj_name = StringProperty(name = "Name of the object", attr="name")

    def execute(self, context):
        # read the parameters of the object from library file
        verts,faces, edges=read_file(self.properties.obj_name)
        obj = create_mesh_object(context, verts, edges, faces,self.properties.obj_name)
        return {'FINISHED'}


class library_panel(bpy.types.Panel):
    bl_label = "Library Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"


    def draw(self, context):
        scene = context.scene
        layout = self.layout
        split = layout.split()

        col = split.column()
        col.label(text="Library items", icon='WORLD_DATA')
        
        # add selected object to library
        col = split.column()
        col.operator("object.add_to_library", text="Add to Library")
        names = mesh_names()
        
        row = layout.row()
        split = row.split(percentage=0.7)
        colL = split.column()
        colR = split.column()
        for i in names:
            colL.operator("object.add_from_library", text=i).obj_name=i
            colR.operator("object.remove_from_library", text="Delete").obj_name=i

def register():
    bpy.utils.register_module(__name__)    

def unregister():
    bpy.utils.unregister_module(__name__)
if __name__ == "__main__":
    register()
