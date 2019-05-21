import bpy

# Panels -----------------------------------------

class DebugPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Debug'
    bl_context = 'objectmode'
    bl_category = 'Elfin'

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        col = row.column()
        col.operator('elfin.reset', text='Reset Properties')
        col.operator('elfin.load_module_library', text='(Re)load Library')
        col.operator('elfin.load_xdb', text='(Re)load xdb')
        # col.operator('elfin.delete_faces', text='Delete faces (selection)')
        col.operator('elfin.load_all_obj_files', text='Load all obj files')
        col.operator('elfin.process_obj', text='Process obj file (selection)')
        col.operator('elfin.batch_process', text='Batch process all obj files')


# Operators --------------------------------------

# class DeleteFacesOperator(bpy.types.Operator):
#     bl_idname = 'elfin.delete_faces'
#     bl_label = 'Delete Faces (selected only)'
#     bl_options = {'REGISTER', 'UNDO'}
    
#     def execute(self, context):
#         selObjs = context.selected_objects
#         for obj in selObjs:
#             context.scene.objects.active = obj
#             bpy.ops.object.mode_set(mode='EDIT')
#             bpy.ops.mesh.delete(type='ONLY_FACE')
#             bpy.ops.object.mode_set(mode='OBJECT')
#         return {'FINISHED'}

#     @classmethod
#     def poll(cls, context):
#         return len(context.selected_objects) > 0

class ResetOperator(bpy.types.Operator):
    bl_idname = 'elfin.reset'
    bl_label = 'Reset Elfin UI properties'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.elfin.reset()
        return {'FINISHED'}