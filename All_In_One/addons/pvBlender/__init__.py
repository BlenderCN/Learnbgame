import bpy

bl_info = {
  "name": "VTK nodes",
  "category": "Learnbgame",
}

import paraview
import paraview.simple
import paraview.servermanager

class pvNodeTree(bpy.types.NodeTree):
  bl_description = "VTK Node Tree"
  bl_icon = "MESH_TORUS"
  bl_label = "VTK node tree"

class pvNodeSocket(bpy.types.NodeSocket):
  bl_label = "VTK Node Socket"
  def draw(self, context, layout, node, x):
    layout.label(self.name)
  def draw_color(self, context, node):
    return (1,1,1,1)

from .nodedata import pvDataNode

from .category import pvNodeCategory

from bpy.app.handlers import persistent

from . import pvnodes,inspector,object,polydata

@persistent
def post_init(something):
    global vtknodes_tmp_mesh
    print("------------------------- POST INIT  -------------------")
    polydata.post_init(something)
    for g in bpy.data.node_groups:
        print(g)
        if type(g) == pvNodeTree:
            for n in g.nodes:
                n.update()

def post_init_once(something):
    if post_init_once in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.remove(post_init_once)
    post_init(something)

def register():
    global my_pvClasses, vtknodes_tmp_mesh
    print("------------------------- REGISTER PV -------------------")
    bpy.utils.register_class(pvNodeTree)
    bpy.utils.register_class(pvNodeSocket)
    pvnodes.register()
    inspector.register()
    object.register()
    if not post_init in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(post_init)
    if not post_init_once in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.append(post_init_once)
    

def unregister():
    global my_pvClasses
    print("------------------------- UNREGISTER PV -------------------")
    pvnodes.unregister()
    inspector.unregister()
    object.unregister()
    bpy.utils.unregister_class(pvNodeTree)
    bpy.utils.unregister_class(pvNodeSocket)

