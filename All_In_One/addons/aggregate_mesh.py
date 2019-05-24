## simple agregador de 'particulas' / mallas
## copia los objetos seleccionados sobre el objeto activo
## basado en la posicion del cursor y un volumen definido
## permite animar el crecimiento usando un modificador Build
## necesita un Blender r38676 o mas reciente

bl_info = {
    "name": "Aggregate Mesh",
    "author": "liero",
    "version": (0, 0, 2),
    "blender": (2, 5, 8),
    "api": 38676,
    "location": "View3D > Properties",
    "description": "Adds geometry to a mesh like in DLA aggregators.",
    "category": "Learnbgame",
}

import bpy, random, time, mathutils
from mathutils import Matrix

def r(n):
    return (round(random.gauss(0,n),2))

def remover(sel=False):
    bpy.ops.object.editmode_toggle()
    if sel: bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(limit=0.001)
    bpy.ops.object.mode_set()

bpy.types.WindowManager.volX = bpy.props.FloatProperty(name='Volume X', min=0.1, max=25, default=3, description='The cloud around cursor')
bpy.types.WindowManager.volY = bpy.props.FloatProperty(name='Volume Y', min=0.1, max=25, default=3, description='The cloud around cursor')
bpy.types.WindowManager.volZ = bpy.props.FloatProperty(name='Volume Z', min=0.1, max=25, default=3, description='The cloud around cursor')
bpy.types.WindowManager.baseSca = bpy.props.FloatProperty(name='Scale', min=0.01, max=5, default=.25, description='Particle Scale')
bpy.types.WindowManager.varSca = bpy.props.FloatProperty(name='Var', min=0, max=1, default=0, description='Particle Scale Variation')
bpy.types.WindowManager.rotX = bpy.props.FloatProperty(name='Rot Var X', min=0, max=2, default=0, description='X Rotation Variation')
bpy.types.WindowManager.rotY = bpy.props.FloatProperty(name='Rot Var Y', min=0, max=2, default=0, description='Y Rotation Variation')
bpy.types.WindowManager.rotZ = bpy.props.FloatProperty(name='Rot Var Z', min=0, max=2, default=1, description='Z Rotation Variation')
bpy.types.WindowManager.numP = bpy.props.IntProperty(name='Number', min=1, max=1000, default=50, description='Number of particles')
bpy.types.WindowManager.nor = bpy.props.BoolProperty(name='Normal Oriented', default=False, description='Align Z axis with Faces normals.')
bpy.types.WindowManager.cent = bpy.props.BoolProperty(name='Use Face Center', default=False, description='Center on Faces.')
bpy.types.WindowManager.track = bpy.props.BoolProperty(name='Move the Cursor', default=False, description='Cursor moves as structure grow / more compact results.')
bpy.types.WindowManager.anim = bpy.props.BoolProperty(name='Animation ready', default=False, description='Order indexes to recreate mesh with Build Modifier, but materials are lost.')
bpy.types.WindowManager.remo = bpy.props.BoolProperty(name='Remove Doubles', default=False, description='Try to remove overlapping faces on each step, can slow down process.')


class Agregar(bpy.types.Operator):
    bl_idname = 'object.agregar'
    bl_label = 'Aggregate'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return(len(bpy.context.selected_objects) > 1 and bpy.context.object.type == 'MESH')

    def execute(self, context):
        tim = time.time()
        scn = bpy.context.scene
        obj = bpy.context.active_object
        wm = context.window_manager
        mat = Matrix(((1, 0, 0, 0),(0, 1, 0, 0),(0, 0, 1, 0),(0, 0, 0, 1)))
        if obj.matrix_world != mat:
            self.report({'WARNING'}, 'Apply transformations to Active Object first..!')
            return{'FINISHED'}
        par = [o for o in bpy.context.selected_objects if o.type == 'MESH' and o != obj]
        if not par: return{'FINISHED'}

        bpy.ops.object.mode_set()
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        msv = []

        for i in range(len(obj.modifiers)):
            msv.append(obj.modifiers[i].show_viewport)
            obj.modifiers[i].show_viewport = False

        cur = scn.cursor_location
        for i in range (wm.numP):
            mes = random.choice(par).data
            x = bpy.data.objects.new('nuevo', mes)
            scn.objects.link(x)
            origen = (r(wm.volX)+cur[0], r(wm.volY)+cur[1], r(wm.volZ)+cur[2])
            cpom = obj.closest_point_on_mesh(origen)

            if wm.cent:
                x.location = obj.data.faces[cpom[2]].center
            else:
                x.location = cpom[0]

            if wm.nor:
                x.rotation_mode = 'QUATERNION'
                x.rotation_quaternion = cpom[1].to_track_quat('Z','Y')
                x.rotation_mode = 'XYZ'
                x.rotation_euler[0] += r(wm.rotX)
                x.rotation_euler[1] += r(wm.rotY)
                x.rotation_euler[2] += r(wm.rotZ)
            else:
                x.rotation_euler = (r(wm.rotX), r(wm.rotY), r(wm.rotZ))

            x.scale = [wm.baseSca + wm.baseSca * r(wm.varSca)] * 3

            if wm.anim:
                x.select = True
                bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', obdata=True)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                tmp = x.data
                num_v = len(obj.data.vertices)
                obj.data.vertices.add(len(tmp.vertices))
                for v in range(len(tmp.vertices)):
                    obj.data.vertices[num_v + v].co = tmp.vertices[v].co
                    if tmp.vertices[v].select:
                        obj.data.vertices[num_v + v].select = True
                num_f = len(obj.data.faces)
                obj.data.faces.add(len(tmp.faces))
                for f in range(len(tmp.faces)):
                    x_fv = tmp.faces[f].vertices
                    o_fv = [i + num_v for i in x_fv]
                    if len(x_fv) == 4: obj.data.faces[num_f + f].vertices_raw = o_fv
                    else: obj.data.faces[num_f + f].vertices = o_fv
                obj.data.update(calc_edges=True)
                scn.update()

                if wm.remo: remover()

                tmp.user_clear()
                bpy.data.meshes.remove(tmp)
                scn.objects.unlink(x)
            else:
                scn.objects.active = obj
                x.select = True
                bpy.ops.object.join()

            if wm.track: cur = scn.cursor_location = cpom[0]
        
        for i in range(len(msv)): obj.modifiers[i].show_viewport = msv[i]
        for o in par: o.select = True
        obj.select = True
        # remover(True) # better do it manually

        print ('Tiempo:',round(time.time()-tim,4),'segundos')
        return{'FINISHED'}


class PanelA(bpy.types.Panel):
    bl_label = 'Aggregate mesh'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        
        column = layout.column(align=True)
        column.prop(wm, 'volX', slider=True)
        column.prop(wm, 'volY', slider=True)
        column.prop(wm, 'volZ', slider=True)
        
        layout.label(text='Particles:')
        column = layout.column(align=True)
        column.prop(wm, 'baseSca', slider=True)
        column.prop(wm, 'varSca', slider=True)
        
        column = layout.column(align=True)
        column.prop(wm, 'rotX', slider=True)
        column.prop(wm, 'rotY', slider=True)
        column.prop(wm, 'rotZ', slider=True)
        
        column = layout.column(align=True)
        column.prop(wm, 'nor')
        column.prop(wm, 'cent')
        column.prop(wm, 'track')
        column.prop(wm, 'anim')
        if wm.anim and wm.nor: column.prop(wm, 'remo')
        
        layout.separator()
        layout.prop(wm, 'numP')
        layout.operator('object.agregar')


def register():
    bpy.utils.register_class(Agregar)
    bpy.utils.register_class(PanelA)

def unregister():
    bpy.utils.unregister_class(Agregar)
    bpy.utils.unregister_class(PanelaA)

if __name__ == '__main__':
    register()