bl_info = {
    "name": "Edge sum",
    "author": "zeffii",
    "version": (0, 1, 0),
    "blender": (2, 7, 7),
    "location": "3d view, N panel",
    "description": "Adds edge sum box to Mesh Display.",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

# http://blender.stackexchange.com/a/1071/47
# where Adhi suggests the space_view3d_panel_measure import.

import bpy
import bmesh
import space_view3d_panel_measure as pm


def print_details(num_edges, edge_length):
    print("number of edges: {0}".format(num_edges))
    print("combined length: {0:6f}".format(edge_length))


def get_combined_length(object_reference):

    # Get a BMesh representation
    bm = bmesh.from_edit_mesh(object_reference.data)

    selected_edges = [edge for edge in bm.edges if edge.select]
    num_edges = len(selected_edges)

    edge_length = 0
    for edge in selected_edges:
        edge_length += edge.calc_length()
         
    print_details(num_edges, edge_length)
    return round(edge_length, 6)
    

class SumButton(bpy.types.Operator):
    bl_idname = "scene.calculate_length"
    bl_label = "Sometype of operator"

    bpy.types.Scene.sum_addon_length = bpy.props.StringProperty(name = "")
 
    def execute(self, context):
        obj_reference = context.active_object
        length = get_combined_length(obj_reference)
        
        uinfo = pm.getUnitsInfo()    
        length = pm.convertDistance(length, uinfo)
        context.scene.sum_addon_length = length
        return{'FINISHED'}

class CopyLength(bpy.types.Operator):
    bl_idname = "scene.copy_length"
    bl_label = "copy to clipboard"
 
    def execute(self, context):
        context.window_manager.clipboard  = context.scene.sum_addon_length
        return{'FINISHED'}


def draw_item(self, context):
    layout = self.layout
    obj = context.object
    row = layout.row()
    scn = context.scene

    # display label and button
    if obj:
        row.label(text="summed edge length:")
        row = layout.row()
        
        split = row.split(percentage=0.50)
        col = split.column()
        col.prop(scn, 'sum_addon_length')

        split = split.split()
        col = split.column()
        col.operator("scene.calculate_length", text='Sum')

        split = split.split()
        col = split.column()
        col.operator("scene.copy_length", text='Copy')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_PT_view3d_meshdisplay.append(draw_item)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_PT_view3d_meshdisplay.remove(draw_item)

if __name__ == "__main__":
    register()