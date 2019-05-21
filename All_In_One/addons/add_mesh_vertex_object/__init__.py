import bpy
import bmesh

bl_info = {
    'name': 'Add Vertex',
    'author': 'Dealga McArdle (zeffii) <digitalaphasia.com>',
    'version': (1, 0, 0),
    'blender': (2, 6, 3),
    'location': 'Add > Vertex',
    'description': 'adds new object with one selected vertex to location of 3d cursor',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh'}

from bpy.props import FloatProperty, BoolProperty, FloatVectorProperty

class AddVertex(bpy.types.Operator):
    """Add a vertex to 3d cursor location"""
    bl_idname = "mesh.vertex_add"
    bl_label = "Add Vertex"
    bl_options = {'REGISTER', 'UNDO'}


    # generic transform props
    view_align = BoolProperty(
            name="Align to View",
            default=False,
            )
    location = FloatVectorProperty(
            name="Location",
            subtype='TRANSLATION',
            )
    rotation = FloatVectorProperty(
            name="Rotation",
            subtype='EULER',
            )

    def execute(self, context):
    
        vert = (0, 0, 0)
        mesh = bpy.data.meshes.new("Object_From_Vertex")
        bm = bmesh.new()
        bm.verts.new(vert)
        bm.to_mesh(mesh)
        mesh.update()

        # add the mesh as an object into the scene with this utility module
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=self)
        
        #select the vertex for easy extrude
        context.active_object.data.vertices[0].select = True
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddVertex.bl_idname, icon='VERTEXSEL')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.prepend(menu_func)
    #bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()