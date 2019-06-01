bl_info = {
    "name" : "Tetrahedron Object",
    "author" : "mobilefzb",
    "version" : (0,1),
    "blender" : (2,6,3),
    "location" : "View3D > Add > Mesh > Tetrahedron Object",
    "description" : "Adds a new Tetrahedron",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category": "Learnbgame",
}

import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper,object_data_add
import math
import mathutils

def add_tetrahedron(self,context) :
    Vertices = [
        mathutils.Vector((0,-1 / math.sqrt(3),0)),
        mathutils.Vector((0.5,1 / (2 * math.sqrt(3)),0)),
        mathutils.Vector((-0.5,1 / (2 * math.sqrt(3)),0)),
        mathutils.Vector((0,0,math.sqrt(2 / 3)))
    ]

    NewMesh = bpy.data.meshes.new("Terahedron")
    NewMesh.from_pydata 
    (
        Vertices,
        [],
        [[0,1,2],[0,1,3],[1,2,3],[2,0,3]]
    )
    #these code maybe replaced with object_data_data
    #NewMesh.update()
    #NewObj = bpy.data.objects.new("Tetrahedron",NewMesh)
    #context.scene.objects.link(NewObj)
    #return {"FINISHED"}
    object_data_add(context,NewMesh,operator = self)

class OBJECT_OT_add_tetrahedron(Operator,AddObjectHelper) :
    '''add a tetrahedron'''
    bl_idname = "mesh.add_tetrahedron"
    bl_label = "Add Mesh tetrahedron"
    bl_description = "Create a new Mesh tetrahedron"
    bl_options = {'REGISTER','UNDO'}

    def execute(self,context) :
        add_tetrahedron(self,context)
        return {"FINISHED"}

def add_object_button(self,context) :
    self.layout.operator(
        OBJECT_OT_add_tetrahedron.bl_idname,
        text = "Add tetrahedron",
        icon = "PLUGIN")

class OBJECT_PT_Panel(bpy.types.Panel) :
    bl_label = "Add Tetrahedron"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw_header(self,context) :
        layout = self.layout
        layout.label(text = "",icon = "PHYSICS")
    def draw(self,context) :
        row = self.layout.column(align = True)
        row.operator("mesh.add_tetrahedron",text = "Add Tetrahedron")

def register() :
    bpy.utils.register_class(OBJECT_OT_add_tetrahedron)
    bpy.types.INFO_MT_mesh_add.append(add_object_button)
    bpy.utils.register_class(OBJECT_PT_Panel)

def unregister() :
    bpy.utils.unregister_class(OBJECT_OT_add_tetrahedron)
    bpy.types.INFO_MT_mesh_add.remove(add_object_button)
    bpy.utils.unregister_class(OBJECT_PT_Panel)

if __name__ == "__main__" :
    register()
