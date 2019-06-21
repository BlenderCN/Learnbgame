import bpy
import nodeitems_utils
import paraview
import paraview.simple
import paraview.servermanager
import paraview.vtk

from . import polydata

from .nodedata import pvDataNode

import vtkCommonDataModelPython

class pvObjectNode(bpy.types.Node):
    bl_label = "Blender Legacy Mesh"
    obName = bpy.props.StringProperty(default="VTKObj")
    def init(self, context):
        print("Init node: ", self.name)
        self.inputs.new("pvNodeSocket", "Input")
        me = bpy.data.meshes.new(self.obName + "Mesh")
        ob = bpy.data.objects.new(self.obName, me)
        self.obName = ob.name
        bpy.context.scene.objects.link(ob)
    def update(self):
        print("Updating node: ", self.name)
        socket = self.inputs["Input"]
        if socket.is_linked and len(socket.links) > 0:
            other = socket.links[0].from_socket.node
            other.load_data()
            pv = other.data.pv
            print("Fetching data from",pv,"...")
            pvd = paraview.servermanager.Fetch(pv)
            self.make_mesh(pvd)
    def make_mesh(self,d):
        ob = bpy.data.objects[self.obName]        
        if type(d) == vtkCommonDataModelPython.vtkPolyData:
            polydata.PolyDataMesh(d,ob)
    def draw_buttons(self, context, layout):
        layout.prop(self, "obName")
    def free(self):
        self.free_data()

import bmesh

class pvBMeshNode(bpy.types.Node, pvDataNode):
    bl_label = "Blender Object"
    obName = bpy.props.StringProperty(default="VTKObj")
    def init(self, context):
        print("Init node: ", self.name)
        me = bpy.data.meshes.new(self.obName + "Mesh")
        ob = bpy.data.objects.new(self.obName, me)
        self.obName = ob.name
        bpy.context.scene.objects.link(ob)
        self.load_data()
        self.inputs.new("pvNodeSocket", "Input")
    def init_data(self):
        self.data.ob = bpy.data.objects[self.obName]
        self.data.bm = bmesh.new()
        self.data.bm.from_mesh(self.data.ob.data)
    def update(self):
        self.load_data()
        print("Updating node: ", self.name)
        socket = self.inputs["Input"]
        if socket.is_linked and len(socket.links) > 0:
            other = socket.links[0].from_socket.node
            other.load_data()
            pv = other.data.pv
            print("Fetching data from",pv,"...")
            pvd = paraview.servermanager.Fetch(pv)
            self.make_mesh(pvd)
    def make_mesh(self,d):
        if type(d) == vtkCommonDataModelPython.vtkPolyData:
            self.make_polydata(d)
    def make_polydata(self,pdata):
        bm = self.data.bm
        polydata.bmesh_from_polydata(bm,pdata)
        bm.to_mesh(self.data.ob.data)
        self.data.ob.data.update()
    def draw_buttons(self, context, layout):
        layout.prop(self, "obName", text="Object name")
    def free(self):
        self.free_data()

            
from . import category

def register():
    bpy.utils.register_class(pvObjectNode)
    bpy.utils.register_class(pvBMeshNode)
        
    categories = [
      category.pvNodeCategory("BVTK_Blender", "Blender",
        items = [
            nodeitems_utils.NodeItem("pvObjectNode"),
            nodeitems_utils.NodeItem("pvBMeshNode"),
        ]),
    ]
    nodeitems_utils.register_node_categories("BVTK_CATEGORIES_Blend", categories)

def unregister():
    bpy.utils.unregister_class(pvObjectNode)
    bpy.utils.unregister_class(pvBMeshNode)
    nodeitems_utils.unregister_node_categories("BVTK_CATEGORIES_Blend")


