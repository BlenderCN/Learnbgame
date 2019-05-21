######################################################
# parent selected objects to the faces of a new mesh #
#  faster version / edit realtime / orientation bug  #
######################################################

bl_info = {
    "name": "Parent to Mesh",
    "author": "liero",
    "version": (0, 5, 5),
    "blender": (2, 6, 0),
    "location": "View3D > Tool Shelf",
    "description": "Parents each selected object to the faces of a new mesh.",
    "category": "Learnbgame"
}

import bpy, mathutils as m
from bpy.props import BoolProperty, FloatProperty, StringProperty

class MeshParent(bpy.types.Operator):
    bl_idname = 'object.parent_tri'
    bl_label = 'Parent to Mesh'
    bl_description = 'Create a mesh and parent selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    scale = bpy.props.FloatProperty(name="Scale", description="Scale factor of new faces", min=.1, max=25, default=2)
    rotate = bpy.props.BoolProperty(name='Oriented Faces', default=False, description='Get faces orientation from object Z axis')
    single = bpy.props.BoolProperty(name='Use Single Vertex', default=False, description='Parent each object to a single vertex instead of 3 vertices')
    name = bpy.props.StringProperty(name='', default='padre', description='Type a name for the Empty here...')

    @classmethod
    def poll(cls, context):
        return (context.selected_objects)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'name')
        column = layout.column()
        column.prop(self,'single')
        if not self.single:
            column.prop(self,'rotate')
            layout.prop(self,'scale')

    def execute(self, context):
        wm = bpy.context.window_manager
        selected = bpy.context.selected_objects
        orfans = [o for o in selected if not o.parent]
        nube, caras, objetos = [], [], []

        # base tri coords
        d1 = m.Vector([-0.0866,-0.05,0])
        d2 = m.Vector([0.0866,-0.05,0])
        d3 = m.Vector([0,0.1,0])

        # go object mode
        try: bpy.ops.object.mode_set()
        except: pass

        # list objects and tris coords
        for c, obj in enumerate(orfans):
            objetos.append(obj)
            dd = obj.location
            mat = obj.matrix_world
            if self.single:
                nube.append(dd)
            else:
                dd1 = d1.copy()
                dd2 = d2.copy()
                dd3 = d3.copy()
                if self.rotate:
                    dd1.rotate(mat)
                    dd2.rotate(mat)
                    dd3.rotate(mat)
                nube.append(dd + dd1 * self.scale)
                nube.append(dd + dd2 * self.scale)
                nube.append(dd + dd3 * self.scale)
                caras.append([c*3, c*3+1, c*3+2])

        # mesh from the list of coords
        malla = bpy.data.meshes.new(self.name)
        padre = bpy.data.objects.new(self.name, malla)
        bpy.context.scene.objects.link(padre)
        padre.hide_render = True
        padre.draw_type = 'WIRE'
        malla.from_pydata(nube, [], caras)
        malla.update()

        # do the parenting to 1 or 3 verts
        bpy.context.scene.objects.active = padre
        for c, obj in enumerate(objetos):
            obj.location = (0,0,0)
            obj.parent = padre
            if self.single:
                obj.parent_type = 'VERTEX'
                obj.parent_vertices = [c,c,c]
            else:
                v = (c*3)
                obj.parent_type = 'VERTEX_3'
                obj.parent_vertices = [v,v+1,v+2]
                if self.rotate:
                    # this needs a fix..!
                    obj.rotation_euler = (0,0,0)
                    obj.scale[0] *= -1
                    obj.scale[1] *= -1
        padre.select = True

        return {'FINISHED'}

class PanelMP(bpy.types.Panel):
    bl_label = 'Parent to Mesh'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        layout.operator('object.parent_tri')

def register():
    bpy.utils.register_class(MeshParent)
    bpy.utils.register_class(PanelMP)

def unregister():
    bpy.utils.unregister_class(MeshParent)
    bpy.utils.unregister_class(PanelMP)

if __name__ == '__main__':
    register()