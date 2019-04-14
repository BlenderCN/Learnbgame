
import bpy
from bpy.props import *
from mathutils import *
from mathutils.noise import *
from math import *

# Create a new mesh (object) from verts/edges/faces.
# verts/edges/faces ... List of vertices/edges/faces for the
#                    new mesh (as used in from_pydata).
# name ... Name of the new mesh (& object).
def create_wedge_mesh(context, options, name):
    # Create new mesh
    mesh = bpy.data.meshes.new( name )
    verts = []
    faces = []

    pref_width = options[0]
    pref_height = options[1]
    pref_depth = options[2]

    half_width = pref_width * .5
    half_height = pref_height * .5
    half_depth = pref_depth * .5

    verts.append( Vector( (-half_width, -half_height, half_depth) ) )
    verts.append( Vector( (-half_width, -half_height, -half_depth) ) )

    verts.append( Vector( (half_width, -half_height, half_depth) ) )
    verts.append( Vector( (half_width, -half_height, -half_depth) ) )

    verts.append( Vector( (-half_width, half_height, half_depth) ) )
    verts.append( Vector( (-half_width, half_height, -half_depth) ) )

    faces.append( (0, 2, 4) )
    faces.append( (1, 3, 5) )
    faces.append( (0, 1, 3, 2) )
    faces.append( (0, 4, 5, 1) )
    faces.append( (2, 3, 5, 4) )

    # Make a mesh from a list of verts/edges/faces.
    mesh.from_pydata(verts, [], faces)

    # Update mesh geometry after adding stuff.
    mesh.update()

    from bpy_extras import object_utils
    return object_utils.object_data_add(context, mesh, operator=None)
# end create_mesh_object

# ------------------------------------------------------------
# Add wedge
class wedge_add(bpy.types.Operator):
    """Add a wedge mesh"""
    bl_idname = "mesh.wedge_add"
    bl_label = "Wedge"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    bl_description = "Add wedge mesh"

    # properties
    MeshWidth : FloatProperty(name="Width",
                min = 0.01,
                max = 100000.0,
                default = 3.5,
                description = "Mesh width")

    MeshHeight : FloatProperty(name="Height",
                min = 0.01,
                max = 100000.0,
                default = 1.2,
                description = "Mesh height")

    MeshDepth : FloatProperty(name="Depth",
                min = 0.01,
                max = 100000.0,
                default = 1.2,
                description = "Mesh depth")

    # ------------------------------------------------------------
    # Draw the context menu
    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, 'MeshWidth')
        box.prop(self, 'MeshHeight')
        box.prop(self, 'MeshDepth')
    # end draw

    # ------------------------------------------------------------
    # Execute
    def execute(self, context):
        #mesh update

        # turn off undo
        undo = bpy.context.preferences.edit.use_global_undo
        bpy.context.preferences.edit.use_global_undo = False

        # deselect all objects when in object mode
        if bpy.ops.object.select_all.poll():
            bpy.ops.object.select_all( action='DESELECT' )

        options = [
            self.MeshWidth,
            self.MeshHeight,
            self.MeshDepth
        ]
        # create mesh object
        obj = create_wedge_mesh( context, options, "Wedge" )
        bpy.ops.object.mode_set( mode='EDIT' )
        bpy.ops.mesh.remove_doubles( threshold=0.0001 )
        # Fix normals that might be broken on the mesh
        bpy.ops.mesh.normals_make_consistent( inside=False )
        bpy.ops.object.mode_set( mode='OBJECT' )
        ob = context.view_layer.objects.active
        # Rotate it around 90 degrees about the X axis
        ob.rotation_euler = ( radians(90), 0, 0 )
        # Apply the rotation transform so it appears as 0 degrees
        # on all 3 axes
        bpy.ops.object.transform_apply( rotation = True )

        # restore pre operator undo state
        bpy.context.preferences.edit.use_global_undo = undo

        return {'FINISHED'}
    # end execute

    def invoke(self, context, event) :
        self.execute(context)
        return {"FINISHED"}
    #end invoke

# end class


# ------------------------------------------------------------
# Register

# Define "Wedge" menu
def menu_func_wedge(self, context):
    self.layout.operator(wedge_add.bl_idname, text="Wedge", icon="TRIA_RIGHT")


def register():
    bpy.utils.register_class(wedge_add)

    bpy.types.VIEW3D_MT_mesh_add.append(menu_func_wedge)


def unregister():
    bpy.utils.unregister_class(wedge_add)

    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func_wedge)


if __name__ == "__main__":
    register()