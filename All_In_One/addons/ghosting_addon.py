bl_info = {
    "name": "Ghosting",
    "author": "liero",
    "version": (0, 1, 6),
    "blender": (2, 5, 9),
    "api": 39792,
    "location": "View3D > Tool Shelf",
    "description": "Basic ghosting for spatial transform animations",
    'warning': 'experimental',
    "category": "Learnbgame"
}

import bpy

class Fantasma(bpy.types.Operator):
    bl_idname = 'object.fantasma'
    bl_label = 'Create / Update'
    bl_description = 'Create or Update Ghost Object'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return(obj and obj.animation_data)

    def execute(self, context):
        scn = bpy.context.scene
        obj = bpy.context.object

        # seleccionado el armature y no el objeto > cambio la seleccion
        if obj.type == 'ARMATURE' and obj.name.endswith('_ghost'):
            try:
                obj = scn.objects.get(obj.name.replace('_ghost', ''))
            except:
                return{'FINISHED'}

        # un empty para contener a todos los fantasmas
        if 'Ghost_Objects' not in scn.objects.keys():
            bpy.ops.object.add(type='EMPTY')
            scn.objects.active.name = 'Ghost_Objects'
            scn.objects.active.hide_select = True

        # crear o refrescar el armature / limpiar animacion
        if bpy.data.objects.get(obj.name+'_ghost'):
            rig = scn.objects.get(obj.name+'_ghost')
            rig.animation_data_clear()
        else:
            arm = bpy.data.armatures.new('arm')
            rig = bpy.data.objects.new(obj.name+'_ghost', arm)
            rig.parent = scn.objects.get('Ghost_Objects')
            rig.data.ghost_step = 25
            scn.objects.link(rig)
            scn.update()
            scn.objects.active = rig
            bpy.ops.object.mode_set(mode='EDIT')
            bon = arm.edit_bones.new('clon')
            bon.head = (0,0,0)
            bon.tail = (0,1,0)
            bon.use_local_location = False

        # entro a modo pose y defino el objeto como shape
        rig.animation_data_create()
        rig.animation_data.action = bpy.data.actions.new(name='Ghost')
        grupo = rig.animation_data.action.groups.new(name='Curves')
        scn.objects.active = rig
        rig.select = True
        rig.hide_select = True
        bpy.ops.object.mode_set(mode='POSE')
        pbon = rig.pose.bones['clon']
        pbon.custom_shape = obj
        pbon.rotation_mode = obj.rotation_mode
        pbon.matrix = obj.matrix_world
        pbon.bone.show_wire = True

        # copiar transformaciones delta...
        rig.delta_location = obj.delta_location

        # copiar los keyframes del objeto al pose bone
        for fcu in obj.animation_data.action.fcurves:
            ruta = 'pose.bones["clon"].'+fcu.data_path
            copia = rig.animation_data.action.fcurves.new(data_path=ruta, index=fcu.array_index)
            copia.keyframe_points.add(len(fcu.keyframe_points))
            copia.hide = True
            copia.group = grupo
            for i in range(len(fcu.keyframe_points)):
                try:
                    copia.keyframe_points[i].co = fcu.keyframe_points[i].co
                    copia.keyframe_points[i].handle_left = fcu.keyframe_points[i].handle_left
                    copia.keyframe_points[i].handle_left_type = fcu.keyframe_points[i].handle_left_type
                    copia.keyframe_points[i].handle_right = fcu.keyframe_points[i].handle_right
                    copia.keyframe_points[i].handle_right_type = fcu.keyframe_points[i].handle_right_type
                except: 
                    print ('error'); pass
        scn.objects.active = rig
        return{'FINISHED'}


class BorrarFantasma(bpy.types.Operator):
    bl_idname = 'object.borrar_fantasma'
    bl_label = ''
    bl_description = 'Delete Ghost Object'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = bpy.context.object
        return(obj and obj.animation_data)

    def execute(self, context):
        scn = bpy.context.scene
        obj = bpy.context.object

        if obj.type != 'ARMATURE':
            rig = scn.objects.get(obj.name+'_ghost')
            if rig: obj = rig
            else: return{'FINISHED'}

        if obj.name.endswith('_ghost'):
            scn.objects.active = obj
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            obj.hide_select = False
            obj.select = True
            bpy.ops.object.delete()
        return{'FINISHED'}


class Boton(bpy.types.Panel):
    bl_label = 'Ghosting'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        column = layout.column()
        row = column.row(align=True)
        row.operator('object.fantasma')
        row.operator('object.borrar_fantasma', icon='X')
        obj = bpy.context.object
        if obj and obj.type == 'ARMATURE':
            column = layout.column(align=True)
            column.prop(obj.data, 'ghost_step')
            column.prop(obj.data, 'ghost_size')

def register():
    bpy.utils.register_class(Fantasma)
    bpy.utils.register_class(BorrarFantasma)
    bpy.utils.register_class(Boton)

def unregister():
    bpy.utils.unregister_class(Fantasma)
    bpy.utils.unregister_class(BorrarFantasma)
    bpy.utils.unregister_class(Boton)

if __name__ == '__main__':
    register()