# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
	"name": "Add Vert & Empty",
	"author": "Meta_Androcto",
	"version": (1, 0),
	"blender": (2, 6, 3),
	"location": "View3D > Add > Mesh > Single Vert",
	"description": "Adds Single Vertice & empty to edit mode",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame"
}
import bpy
import bmesh
from bpy.props import StringProperty, FloatProperty, BoolProperty, FloatVectorProperty

        # add the mesh as an object into the scene with this utility module
from bpy_extras import object_utils

def centro(objetos):
    x = sum([obj.location[0] for obj in objetos])/len(objetos)
    y = sum([obj.location[1] for obj in objetos])/len(objetos)
    z = sum([obj.location[2] for obj in objetos])/len(objetos)
    return (x,y,z)
class P2E(bpy.types.Operator):
    bl_idname = 'object.parent_to_empty'
    bl_label = 'Parent to Empty'
    bl_description = 'Parent selected objects to a new Empty'
    bl_options = {'REGISTER', 'UNDO'}

    nombre = StringProperty(name='', default='OBJECTS', description='Give the empty / group a name')
    grupo = bpy.props.BoolProperty(name='Create Group', default=False, description='Also link objects to a new group')
    cursor = bpy.props.BoolProperty(name='Cursor Location', default=False, description='Add the empty at cursor / selection center')
    renombrar = bpy.props.BoolProperty(name='Rename Objects', default=False, description='Rename child objects')

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.select)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'nombre')
        column = layout.column(align=True)
        column.prop(self,'grupo')
        column.prop(self,'cursor')
        column.prop(self,'renombrar')

    def execute(self, context):
        objs = bpy.context.selected_objects
        bpy.ops.object.mode_set()
        if self.cursor:
            loc = context.scene.cursor_location
        else:
            loc = centro(objs)
        bpy.ops.object.add(type='EMPTY',location=loc)
        bpy.context.object.name = self.nombre
        if self.grupo:
            bpy.ops.group.create(name=self.nombre)
            bpy.ops.group.objects_add_active()
        for o in objs:
            o.select = True
            if not o.parent:
                    bpy.ops.object.parent_set(type='OBJECT')
            if self.grupo:
                bpy.ops.group.objects_add_active()
            o.select = False
        for o in objs:
            if self.renombrar:
                o.name = self.nombre+'_'+o.name
        return {'FINISHED'}



def add_vert(width, height, depth):
    """
    This function takes inputs and returns vertex and face arrays.
    no actual mesh data creation is done here.
    """

    verts = [(+0.0, +0.0, +0.0)
             ]

    faces = []

    # apply size
    for i, v in enumerate(verts):
        verts[i] = v[0] * width, v[1] * depth, v[2] * height

    return verts, faces

def empty_vert(width, height, depth):
    """
    This function takes inputs and returns vertex and face arrays.
    no actual mesh data creation is done here.
    """

    verts = [(+0.0, +0.0, +0.0)
             ]

    faces = []

    # apply size
    for i, v in enumerate(verts):
        verts[i] = v[0] * width, v[1] * depth, v[2] * height

    return verts, faces


class AddVert(bpy.types.Operator):
    '''Add a single vertice in object mode'''
    bl_idname = "mesh.primitive_vert_add"
    bl_label = "Add Single Vert"
    bl_options = {'REGISTER', 'UNDO'}

    width = FloatProperty(
            name="Width",
            description="Box Width",

            )
    height = FloatProperty(
            name="Height",
            description="Box Height",

            )
    depth = FloatProperty(
            name="Depth",
            description="Box Depth",

            )

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

        verts_loc, faces = add_vert(self.width,
                                     self.height,
                                     self.depth,
                                     )

        mesh = bpy.data.meshes.new("Single_Vert")

        bm = bmesh.new()

        for v_co in verts_loc:
            bm.verts.new(v_co)

        for f_idx in faces:
            bm.faces.new([bm.verts[i] for i in f_idx])


        bm.to_mesh(mesh)
        mesh.update()
        object_utils.object_data_add(context, mesh, operator=self)
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all()
        mesh.update()

        return {'FINISHED'}

class AddEmptyVert(bpy.types.Operator):
    '''Add a single vertice in object mode'''
    bl_idname = "mesh.primitive_emptyvert_add"
    bl_label = "Add Empty Object Origin"
    bl_options = {'REGISTER', 'UNDO'}

    width = FloatProperty(
            name="Width",
            description="Box Width",

            )
    height = FloatProperty(
            name="Height",
            description="Box Height",

            )
    depth = FloatProperty(
            name="Depth",
            description="Box Depth",

            )

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

        verts_loc, faces = add_vert(self.width,
                                     self.height,
                                     self.depth,
                                     )

        mesh = bpy.data.meshes.new("Object_Origin")

        bm = bmesh.new()

        for v_co in verts_loc:
            bm.verts.new(v_co)

        for f_idx in faces:
            bm.faces.new([bm.verts[i] for i in f_idx])

        bm.to_mesh(mesh)
        mesh.update()
        object_utils.object_data_add(context, mesh, operator=self)
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all()
        bpy.ops.mesh.delete(type='VERT')
        mesh.update()

        return {'FINISHED'}
		
class INFO_MT_mesh_vert_add(bpy.types.Menu):
    # Define the "Pipe Joints" menu
    bl_idname = "INFO_MT_mesh_vert_add"
    bl_label = "Add Vert"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.primitive_vert_add",
            text="Add Single Vert")
        layout.operator("mesh.primitive_emptyvert_add",
            text="Empty & Origin Only")
			
class ParentPanel(bpy.types.Panel):
    bl_label = 'Add Vert Parent'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.primitive_vert_add")
        layout.operator("mesh.primitive_emptyvert_add")
        layout.operator("object.parent_to_empty")

def menu_func(self, context):
    self.layout.menu("INFO_MT_mesh_vert_add", icon="PLUGIN")

def register():
    bpy.utils.register_class(ParentPanel)
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ParentPanel)
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.mesh.primitive_vert_add()
