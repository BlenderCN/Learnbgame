import glob
import os

import bpy
import bpy.props
import mathutils

# Panels -----------------------------------------

class ProcessPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Process'
    bl_context = 'objectmode'
    bl_category = 'Elfin'

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        col = row.column()
        col.prop(context.scene.elfin, 'pp_src_dir', text='Source')
        col.prop(context.scene.elfin, 'pp_dst_dir', text='Destination')
        col.prop(context.scene.elfin, 'pp_decimate_ratio', text='Decimate Ratio')
        col.operator('elfin.batch_process', text='Batch process & export')

# Operators --------------------------------------

class LoadAllObjFiles(bpy.types.Operator):
    bl_idname = 'elfin.load_all_obj_files'
    bl_label = 'Load all Pymol obj files'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        abs_src_path = bpy.path.abspath(context.scene.elfin.pp_src_dir)
        src_path_list = glob.glob(abs_src_path + '*')
        src_folders = list(map(os.path.basename, src_path_list))

        module_types = ['singles', 'doubles', 'hubs']
        
        if sum([folder in src_folders for folder in module_types]) != len(module_types):
            self.report({'ERROR'}, 'Source folder {} does not contain {} folders: {}'. \
                format(abs_src_path, module_types, src_folders))
            return {'CANCELLED'}

        obj_files = [f for flist in [glob.glob(abs_src_path + '/{}/*.obj'.format(mt)) for mt in module_types] for f in flist]

        for src_obj_file in obj_files:
            bpy.ops.import_scene.obj(filepath=src_obj_file)
        
        return {'FINISHED'}

class BatchProcess(bpy.types.Operator):
    bl_idname = 'elfin.batch_process'
    bl_label = 'Batch process all module .obj files and export'

    def execute(self, context):
        if len(context.scene.objects) != 0:
            self.report({'ERROR'}, 'Scene must be empty for processing')
            return {'CANCELLED'}
        
        print('return: ', bpy.ops.elfin.load_all_obj_files())

        make_dir(bpy.path.dirname(context.scene.elfin.pp_dst_dir))
        abs_dst_path = bpy.path.abspath(context.scene.elfin.pp_dst_dir)

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.elfin.process_obj()
        bpy.ops.wm.save_as_mainfile(filepath=abs_dst_path, copy=True)
        
        return {'FINISHED'}

class ProcessObj(bpy.types.Operator):
    bl_idname = 'elfin.process_obj'
    bl_label = 'Process module object'

    def execute(self, context):
        origin_vec = mathutils.Vector([0, 0, 0])
        identity_euler = mathutils.Matrix.Identity(3).to_euler()
        for obj in context.selected_objects:
            # Shrink to scale and lock scaling
            obj.scale = (.1, .1, .1)
            for i in range(3):
                obj.lock_scale[i] = True

            # Move object to centre and zero rotation
            obj.location = origin_vec
            obj.rotation_euler = identity_euler
            context.scene.objects.active = obj
            
            # Fix normals and remove superimposed vertices. Do this before
            # decimate so the ratio works as intended.
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            bpy.ops.mesh.remove_doubles()

            # Reduce polygons
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.modifier_add(type='DECIMATE')
            context.object.modifiers['Decimate'].ratio = context.scene.elfin.pp_decimate_ratio
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Decimate')
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0