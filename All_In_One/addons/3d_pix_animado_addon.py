#######################################################
# very simple 'pixelization' or 'voxelization' engine #
# this can process the animation of the target object #
#######################################################

bl_info = {
    "name": "3D Pix + animation",
    "version": (0, 6, 5),
    "blender": (2, 6, 6),
    "location": "View3D > Tool Shelf",
    "description": "Creates a 3d pixelated version of the object. Supports animation.",
    "category": "Learnbgame"
}

import bpy, bmesh, mathutils
from mathutils import Vector

bpy.types.Scene.size = bpy.props.FloatProperty(name='Size', min=.01, soft_min=.05, 
max=5, default=.25, description='Size of the cube / grid')
bpy.types.Scene.gap = bpy.props.IntProperty(name='Gap', min=0, max=90, default=10, 
subtype = 'PERCENTAGE', description='Separation - percent of size')
bpy.types.WindowManager.smooth = bpy.props.FloatProperty(name='Smooth', min=0, max=1, 
default=.0, description='Smooth factor when subdividing mesh')
bpy.types.WindowManager.prefix = bpy.props.StringProperty(name='', default='pix.000', 
description='Name prefix for this animation')
bpy.types.WindowManager.start = bpy.props.IntProperty(name='', min=1, soft_max=500, 
max=5000, default=1, description='Start frame for animation')
bpy.types.WindowManager.end = bpy.props.IntProperty(name='', min=1, soft_max=500, 
max=5000, default=1, description='End frame for animation')
bpy.types.WindowManager.hide = bpy.props.BoolProperty(name='Hide dupliverts', 
default=True, description='Hide duplivert objects to reduce visual clutter')

def pix(obj):
    wm = bpy.context.window_manager
    sce = bpy.context.scene
    bpy.ops.object.mode_set()
    obj.select = True
    bpy.ops.group.create(name=wm.prefix)
    mat = bpy.data.materials.new(wm.prefix)
    if wm.end < wm.start: wm.end = wm.start
    fra = wm.start
    sec, vis, max = [], [], 250

    ## crear modulo base
    bpy.ops.mesh.primitive_cube_add()
    box = bpy.context.object.data
    box.materials.append(mat)
    box.name = 'box'
    sce.objects.unlink(bpy.context.object)

    ## bakear la malla animada y crear lista
    for frame in range(wm.start, wm.end+1):
        sce.frame_set(frame)
        mes = obj.to_mesh(sce, True, 'RENDER')
        mes.transform(obj.matrix_world)
        mes.name = 'verts'
        ani = bpy.data.objects.new(wm.prefix, mes)
        sce.objects.link(ani)
        sec.append(ani)
        ani.select = True
        sce.objects.active = obj
        bpy.ops.group.objects_add_active()
    obj.hide = obj.hide_render = True

    ## voxelizar cada objeto de la lista
    for frame in range(wm.start, wm.end+1):
        sce.frame_set(frame)
        dup = sec[frame-wm.start]
        sca = sce.size * (100 - sce.gap) * .005
        sce.objects.active = dup

        ## bmesh - cortar en sucesivas pasadas los edges largos
        bm = bmesh.new()
        bm.from_mesh(dup.data)
        ngn = [f for f in bm.faces if len(f.edges)>4]
        bmesh.ops.triangulate(bm, faces=ngn, use_beauty=True)
        for i in range(250):
            led = [e for e in bm.edges if e.calc_length()>sce.size]
            if not len(led): break
            else:
                bmesh.ops.subdivide_edges(bm, edges=led, smooth=wm.smooth / 10, 
                cuts=1, use_grid_fill=True, use_single_edge=True)
        bm.to_mesh(dup.data)

        ## ajustar los vertices a la grilla
        ver = dup.data.vertices
        for i in ver:
            for n in range(3):
                i.co[n] -= i.co[n] % sce.size

        ## limpiar la malla de verts duplicados caras y edges
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.mesh.delete(type='EDGE_FACE')
        bpy.ops.object.mode_set()

        ## agregar un cubo, escalar y emparentar
        vox = bpy.data.objects.new('vox', box)
        vox.scale = [sca]*3
        sce.objects.link(vox)
        vox.select = True
        sce.objects.active = dup
        dup.dupli_type = 'VERTS'
        vox.parent = dup
        bpy.ops.group.objects_add_active()
        dup.select = False
        vis.append((dup, vox))

        if wm.end == wm.start: return

        ## animar visibilidad del cubo
        for k in range(fra-1, fra+2):
            sce.frame_set(k)
            dup.hide = vox.hide = vox.hide_render = (fra!=k)
            vox.keyframe_insert('hide')
            vox.keyframe_insert('hide_render')
            if wm.hide: dup.keyframe_insert('hide')
        dup.hide = False

        ## avisar de progreso en la consola
        print (fra-wm.start+1, '/', wm.end-wm.start+1)
        fra += 1

    ## extender visibilidad...
    sce.frame_set(wm.end+1)
    if wm.hide: vis[-1][0].keyframe_delete('hide')
    vis[-1][1].keyframe_delete('hide')
    vis[-1][1].keyframe_delete('hide_render')
    sce.frame_set(wm.start-1)
    if wm.hide: vis[0][0].keyframe_delete('hide')
    vis[0][1].keyframe_delete('hide')
    vis[0][1].keyframe_delete('hide_render')

class AniPix(bpy.types.Operator):
    bl_idname = 'object.anipix'
    bl_label = 'Pixelate Object'
    bl_description = 'Create a 3d pixelated version of the object animation.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        tipos = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT']
        return (context.object and context.object.type in tipos)

    def execute(self, context):
        objeto = bpy.context.object
        pix(objeto)
        return {'FINISHED'}

class GUI(bpy.types.Panel):
    bl_label = '3D Pix + animation'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        layout.operator('object.anipix')
        column = layout.column(align=True)
        column.prop(context.scene, "size")
        column.prop(context.scene, "gap")
        layout.prop(context.window_manager, "smooth")
        layout.label(text="Animation Settings:")
        layout.prop(context.window_manager, "prefix")
        row = layout.row(align=True)
        row.prop(context.window_manager, "start")
        row.prop(context.window_manager, "end")
        layout.prop(context.window_manager, "hide")

def register():
    bpy.utils.register_class(AniPix)
    bpy.utils.register_class(GUI)

def unregister():
    bpy.utils.unregister_class(AniPix)
    bpy.utils.unregister_class(GUI)

if __name__ == '__main__':
    register()