######################################################
# parent selected objects to the faces of a new mesh #
######################################################

bl_info = {
    "name": "Parent to Mesh",
    "author": "liero",
    "version": (0, 4),
    "blender": (2, 5, 5),
    "api": 33333,
    "location": "View3D > Tool Shelf",
    "description": "Parents each selected object to the faces of a new mesh.",
    "category": "Learnbgame"
}
    
import bpy, mathutils
from mathutils import Vector
from bpy.props import IntProperty

bpy.types.WindowManager.scale = IntProperty(name="Scale", description="Scale factor of new faces", min=1, max=100, default=5)
bpy.types.WindowManager.rotate = bpy.props.BoolProperty(name='Oriented Faces', default=False, description='Get faces orientation from object Z axis')
bpy.types.WindowManager.single = bpy.props.BoolProperty(name='Use Single Vertex', default=False, description='Parent each object to a single vertex instead of 3 vertices')

def emparentar(seleccionados):
    wm = bpy.context.window_manager
    nube, caras, objetos = [], [], []
    d1 = Vector([0.06, 0.08, 0.0])
    d2 = Vector([0.06, -0.08, 0.0])
    d3 = Vector([-0.1, 0.0, 0.0])
    c = 0

    for ob in seleccionados:
        objetos.append(ob)
        dd = ob.location
        mat = ob.matrix_world

        if wm.single:
            nube.append(dd)
        else:
            dd1 = d1.copy()
            dd2 = d2.copy()
            dd3 = d3.copy()
            if wm.rotate:
                dd1.rotate(mat)
                dd2.rotate(mat)
                dd3.rotate(mat)
            nube.append(dd + dd1 * wm.scale)
            nube.append(dd + dd2 * wm.scale)
            nube.append(dd + dd3 * wm.scale)
            caras.append([c, c + 1, c + 2])
            c += 3
    malla = bpy.data.meshes.new('puntos')
    padre = bpy.data.objects.new('padre', malla)
    bpy.context.scene.objects.link(padre)
    padre.hide_render = True
    padre.draw_type = 'WIRE'
    malla.from_pydata(nube, [], caras)
    malla.update()

    bpy.context.scene.objects.active = padre
    bpy.ops.object.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set()

    for c in range(len(nube)):
        malla.vertices[c].select = False

    for c in range(len(objetos)):
        objetos[c].select = True
        if wm.single:
            malla.vertices[c].select = True
        else:
            for n in range(3):
                malla.vertices[c * 3 + n].select = True
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.vertex_parent_set()
        bpy.ops.object.editmode_toggle()
        if wm.single:
            malla.vertices[c].select = False
        else:
            for n in range(3):
                malla.vertices[c * 3 + n].select = False
        objetos[c].select = False
    padre.select = True

class MeshParent(bpy.types.Operator):
    bl_idname = 'object.parent_tri'
    bl_label = 'Parent to Mesh'
    bl_description = 'Create a mesh and parent selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.selected_objects)

    def execute(self, context):
        emparentar(context.selected_objects)
        return {'FINISHED'}
        
class PanelMP(bpy.types.Panel):
    bl_label = 'Parent to Mesh'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        wm = bpy.context.window_manager
        layout = self.layout
        column = layout.column()
        column.operator('object.parent_tri')
        if not wm.single:
            column.prop(wm,'scale')
            column.prop(wm,'rotate')
        column.prop(wm,'single')

def register():
    bpy.utils.register_class(MeshParent)
    bpy.utils.register_class(PanelMP)

def unregister():
    bpy.utils.unregister_class(MeshParent)
    bpy.utils.unregister_class(PanelMP)

if __name__ == '__main__':
    register()
