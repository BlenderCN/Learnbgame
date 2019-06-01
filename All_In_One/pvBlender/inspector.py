import bpy
import nodeitems_utils
import paraview
import paraview.simple
import paraview.servermanager

from .nodedata import pvDataNode

class pvInspector(bpy.types.Node):
    bl_label = "PV Inspector"
    def init(self, context):
        self.inputs.new("pvNodeSocket","Input")
    def free(self):
        self.free_data()
    def draw_buttons(self, context, layout):
        socket = self.inputs["Input"]
        if socket.is_linked and len(socket.links) > 0:
            other = socket.links[0].from_socket
            pv = other.node.get_data().pv
            layout.label(pv.GetDataInformation().GetDataSetTypeAsString())
            layout.label("CellData:")
            for i in pv.CellData:
                layout.label(str(i) + str(i.GetRange()))
            layout.label("PointData:")
            for i in pv.PointData:
                layout.label(str(i) + str(i.GetRange()))
            layout.label("FieldData:")
            for i in pv.FieldData:
                layout.label(str(i) + str(i.GetRange()))
    def update(self):
        pass
            
from . import category

def register():
    bpy.utils.register_class(pvInspector)
        
    categories = [
      category.pvNodeCategory("BVTK_INSPECTORS", "Inspectors",
        items = [ nodeitems_utils.NodeItem("pvInspector") ]),
    ]
    nodeitems_utils.register_node_categories("BVTK_CATEGORIES_Insp", categories)

def unregister():
    bpy.utils.unregister_class(pvInspector)
    nodeitems_utils.unregister_node_categories("BVTK_CATEGORIES_Insp")


