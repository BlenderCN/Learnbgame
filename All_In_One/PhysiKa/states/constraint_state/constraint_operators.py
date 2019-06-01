import bpy

class PhysikaEnableConstraint(bpy.types.Operator):
    bl_idname = "physika_operators.enable_constraint"
    bl_label = "Enable add constraint"
    bl_description = "Enable add hard position constraint"
    bl_options = {'REGISTER'}

    
    
    def execute(self, context):
        # obj = context.scene.physika.get_physika_object()
        obj = context.scene.objects.active
        vertex_group_name = obj.name + "_PhysikaConstraint"
        if not obj.physika.enable_constraint:
            bpy.ops.object.mode_set(mode='EDIT')
            obj.vertex_groups.new(name=vertex_group_name)
        
            vertex_group = obj.vertex_groups.get(vertex_group_name)
            vertex_group.lock_weight = True
            obj.physika.enable_constraint = True
        else:
            obj.physika.enable_constraint = False
            vertex_group = obj.vertex_groups.get(vertex_group_name)
            obj.vertex_groups.remove(vertex_group)
            bpy.ops.object.mode_set(mode='OBJECT')
    
        return {'FINISHED'}

    
class PhysiKaAddConstraint(bpy.types.Operator):
    bl_idname = "physika_operators.add_constraint"
    bl_label = "add constraint"
    bl_description = "add hard position constraint"
    bl_options = {'REGISTER' }

    def execute(self, context):
        # obj = context.scene.physika.get_physika_object()
        
        obj = context.scene.objects.active
        vertex_group_name = obj.name + "_PhysikaConstraint"
        
        vertex_group = obj.vertex_groups.get(vertex_group_name)
        vertex_group.lock_weight = False
        # vertex_index = [ v for v in obj.data.vertices if v.select ]
        # bpy.ops.object.mode_set(mode='OBJECT')
        # vertex_group.add(vertex_index, 1.0, "ADD")
        bpy.ops.object.vertex_group_assign()
        vertex_group.lock_weight = True        
        return {'FINISHED'}
    
class PhysikaClearConstraint(bpy.types.Operator):
    bl_idname = "physika_operators.clear_constraint"
    bl_label = "clear constraint"
    bl_description = "clear constraint"
    bl_options = {'REGISTER'}


    def execute(self, context):
        # obj = context.scene.physika.get_physika_object()
        obj = context.scene.objects.active
        vertex_group_name = obj.name + "_PhysikaConstraint"
        vertex_group = obj.vertex_groups.get(vertex_group_name)
        vertex_group.lock_weight = False
        bpy.ops.object.vertex_group_remove_from(use_all_verts = True)
        vertex_group.lock_weight = True        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(PhysikaEnableConstraint)
    bpy.utils.register_class(PhysiKaAddConstraint)
    bpy.utils.register_class(PhysikaClearConstraint)

def unregister():
    bpy.utils.unregister_class(PhysikaEnableConstraint)
    bpy.utils.unregister_class(PhysiKaAddConstraint)
    bpy.utils.unregister_class(PhysikaClearConstraint)

