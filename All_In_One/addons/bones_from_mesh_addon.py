#########################################
## huesos desde edge loops / geometria ##
#########################################

bl_info = {
    "name": "Armature from Mesh",
    "author": "liero",
    "version": (0, 1, 3),
    "blender": (2, 6, 3),
    "location": "View3D > Tool Shelf",
    "description": "Grows a chain of bones from edge loops in geometry",
    "category": "Learnbgame",
}

import bpy, mathutils
from mathutils import Vector
from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty

# centroide de una seleccion de vertices
def centro(ver):
    vvv = [v for v in ver if v.select]
    if not vvv or len(vvv) == len(ver): return ('error')
    x = sum([round(v.co[0],4) for v in vvv]) / len(vvv)
    y = sum([round(v.co[1],4) for v in vvv]) / len(vvv)
    z = sum([round(v.co[2],4) for v in vvv]) / len(vvv)
    return (x,y,z)

# recuperar el estado original del objeto
def volver(obj, copia, om, msm, msv):
    for i in copia: obj.data.vertices[i].select = True
    bpy.context.tool_settings.mesh_select_mode = msm
    for i in range(len(msv)):
        obj.modifiers[i].show_viewport = msv[i]

class BB(bpy.types.Operator):
    bl_idname = 'object.mesh2bones'
    bl_label = 'Create Armature'
    bl_description = 'Create an armature rig based on mesh selection'
    bl_options = {'REGISTER', 'UNDO'}

    numb = IntProperty(name='Max Bones', min=1, max=1000, soft_max=100, default=5, description='Max number of bones')
    skip = IntProperty(name='Skip Loops', min=0, max=5, default=0, description='Skip some edges to get longer bones')
    long = FloatProperty(name='Min Length', min=0.01, max=5, default=0.15, description='Discard bones shorter than this value')
    ika = BoolProperty(name='IK constraints', default=True, description='Add IK constraint and Empty as target')
    rotk = BoolProperty(name='IK Rotation', default=False, description='IK constraint follows target rotation')
    auto = BoolProperty(name='Auto weight', default=True, description='Auto weight and assign vertices')
    env = BoolProperty(name='Envelopes', default=False, description='Use envelopes instead of weights')
    rad = FloatProperty(name='Radius', min=0.01, max=5, default=0.25, description='Envelope deform radius')
    nam = StringProperty(name='', default='hueso', description='Default name for bones / groups')

    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return (obj and obj.type == 'MESH')

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)
        column.prop(self,'numb')
        column.prop(self,'skip')
        column.prop(self,'long')
        column = layout.column(align=True)
        column.prop(self,'auto')
        if self.auto:
            column.prop(self,'env')
            if self.env: column.prop(self,'rad')
        column.prop(self,'ika')
        if self.ika: column.prop(self,'rotk')
        layout.prop(self,'nam')

    def execute(self, context):
        scn = bpy.context.scene
        obj = bpy.context.object
        fac = obj.data.polygons
        # guardar estado y seleccion
        ver, om = obj.data.vertices, obj.mode
        msm, msv = list(bpy.context.tool_settings.mesh_select_mode), []
        for i in range(len(obj.modifiers)):
            msv.append(obj.modifiers[i].show_viewport)
            obj.modifiers[i].show_viewport = False
        bpy.ops.object.mode_set(mode='OBJECT')
        copia = [v.index for v in ver if v.select]
        sel = [f.index for f in fac if f.select]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.mesh.select_all(action='DESELECT')
        txt = 'Select a face or a vertex where the chain should end...'
        bpy.ops.object.mode_set(mode='OBJECT')

        # crear rig unico -desde vertice/s y no desde caras-
        if sel == []:
            sel = ['simple']
            for i in copia:
                obj.data.vertices[i].select = True

        # reciclar el rig en cada refresco...
        try: scn.objects.unlink(rig)
        except: pass

        # loop de caras
        for i in sel:
            if sel[0] != 'simple':
                for v in ver: v.select = False
                for v in fac[i].vertices: ver[v].select = True
            lista = [centro(ver)]
            if lista[0] == 'error':
                self.report({'INFO'}, txt)
                volver(obj, copia, om, msm, msv)
                return{'FINISHED'}

            # crear lista de coordenadas para los huesos
            scn.objects.active = obj
            for t in range(self.numb):
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.object.vertex_group_assign(new=True)
                for m in range(self.skip+1):
                    bpy.ops.mesh.select_more()
                bpy.ops.object.vertex_group_deselect()
                bpy.ops.object.mode_set(mode='OBJECT')
                lista.append(centro(ver))
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.object.vertex_group_select()
                bpy.ops.object.vertex_group_remove()
                if lista[-1] == 'error':
                    self.numb = t
                    lista.pop()
                    break
                if len(lista) > 1:
                    delta = Vector(lista[-2]) - Vector(lista[-1])
                    if delta.length < self.long:
                        lista.pop()

            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            # crear armature y copiar transformaciones del objeto
            lista.reverse()
            if len(lista) < 2:
                self.report({'INFO'}, txt)
                volver(obj, copia, om, msm, msv)
                return{'FINISHED'}
            try: arm
            except:
                arm = bpy.data.armatures.new('arm')
                if self.env: arm.draw_type = 'ENVELOPE'
                else: arm.draw_type = 'STICK'
                rig = bpy.data.objects.new(obj.name+'_rig', arm)
                rig.matrix_world = obj.matrix_world
                if self.env: rig.draw_type = 'WIRE'
                rig.show_x_ray = True
                scn.objects.link(rig)
            scn.objects.active = rig
            bpy.ops.object.mode_set(mode='EDIT')

            # crear la cadena de huesos desde la lista
            for i in range(len(lista)-1):
                bon = arm.edit_bones.new(self.nam+'.000')
                bon.use_connect = True
                bon.tail = lista[i+1]
                bon.head = lista[i]
                if self.auto and self.env:
                    bon.tail_radius = self.rad
                    bon.head_radius = self.rad
                if i: bon.parent = padre
                padre = bon
            bpy.ops.object.mode_set(mode='OBJECT')

            # crear IK constraint y un Empty como target
            if self.ika:
                ik = rig.data.bones[-1].name
                loc = rig.matrix_world * Vector(lista[-1])
                rot = rig.matrix_world * rig.data.bones[-1].matrix_local
                bpy.ops.object.add(type='EMPTY', location=loc, rotation=rot.to_euler())
                tgt = bpy.context.object
                tgt.name = obj.name+'_target.000'
                if len(sel) > 1:
                    try: mega
                    except:
                        bpy.ops.object.add(type='EMPTY', location = obj.location)
                        mega = bpy.context.object
                        mega.name = obj.name+'_Controls'
                        tgt.select = True
                    scn.objects.active = mega
                    bpy.ops.object.parent_set(type='OBJECT')

                scn.objects.active = rig
                bpy.ops.object.mode_set(mode='POSE')
                con = rig.pose.bones[ik].constraints.new('IK')
                con.target = tgt
                if self.rotk: con.use_rotation = True
                tgt.select = False
                bpy.ops.object.mode_set(mode='OBJECT')

        obj.select = True
        if self.auto:
            if self.env: bpy.ops.object.parent_set(type='ARMATURE_ENVELOPE')
            else: bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        scn.objects.active = obj
        volver(obj, copia, om, msm, msv)
        return{'FINISHED'}

class IGU(bpy.types.Panel):
    bl_label = 'Bones from mesh'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        layout.operator('object.mesh2bones')

def register():
    bpy.utils.register_class(BB)
    bpy.utils.register_class(IGU)

def unregister():
    bpy.utils.unregister_class(BB)
    bpy.utils.unregister_class(IGU)

if __name__ == '__main__':
    register()