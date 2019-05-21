import bpy
import os
from .functions import *

class ToolsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "3DSC"
    bl_label = "Exporters"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        if obj is not None:
            self.layout.operator("export.coordname", icon="WORLD_DATA", text='Coordinates')
            row = layout.row()
            row.label(text="Active object is: " + obj.name)
            row = layout.row()
            row.label(text="Override")
            row = layout.row()
            row.prop(obj, "name")
            row = layout.row()
            self.layout.operator("export.object", icon="OBJECT_DATA", text='Exp. one obj')
            row = layout.row()
            row.label(text="Resulting file: " + obj.name + ".obj")
            row = layout.row()
            self.layout.operator("obj.exportbatch", icon="OBJECT_DATA", text='Exp. several obj')
            row = layout.row()
            self.layout.operator("fbx.exportbatch", icon="OBJECT_DATA", text='Exp. several fbx UE4')
            row = layout.row()
            self.layout.operator("fbx.exp", icon="OBJECT_DATA", text='Exp. fbx UE4')
            row = layout.row()
#            self.layout.operator("osgt.exportbatch", icon="OBJECT_DATA", text='Exp. several osgt files')
#            row = layout.row()
#            if is_windows():
#                row = layout.row()
#                row.label(text="We are under Windows..")
        else:
            row.label(text="Select object(s) to see tools here.")
            row = layout.row()

        
        
class OBJECT_OT_ExportButtonName(bpy.types.Operator):
    bl_idname = "export.coordname"
    bl_label = "Export coord name"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        bpy.ops.export_test.some_data('INVOKE_DEFAULT')
            
        return {'FINISHED'}

#class OBJECT_OT_ExportButtonName(bpy.types.Operator):
#    bl_idname = "export.coordname"
#    bl_label = "Export coord name"
#    bl_options = {"REGISTER", "UNDO"}

#    def execute(self, context):

#        basedir = os.path.dirname(bpy.data.filepath)

#        if not basedir:
#            raise Exception("Save the blend file")

#        selection = bpy.context.selected_objects
#        bpy.ops.object.select_all(action='DESELECT')
#        activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
#        fn = os.path.join(basedir, activename)
#        file = open(fn + ".txt", 'w')

#        # write selected objects coordinate
#        for obj in selection:
#            obj.select = True
#            file.write("%s %s %s %s\n" % (obj.name, obj.location[0], obj.location[1], obj.location[2]))
#        file.close()
#        return {'FINISHED'}

#class OBJECT_OT_ExportabsButtonName(bpy.types.Operator):
#    bl_idname = "export.abscoordname"
#    bl_label = "Export abs coord name"
#    bl_options = {"REGISTER", "UNDO"}

#    def execute(self, context):

#        basedir = os.path.dirname(bpy.data.filepath)

#        if not basedir:
#            raise Exception("Save the blend file")

#        selection = bpy.context.selected_objects
#        bpy.ops.object.select_all(action='DESELECT')
#        activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
#        fn = os.path.join(basedir, activename)
#        file = open(fn + ".txt", 'w')

#        # write selected objects coordinate
#        for obj in selection:
#            obj.select = True
#            x_abs = obj.location[0] + bpy.data.window_managers['WinMan'].crsx
#            y_abs = obj.location[1] + bpy.data.window_managers['WinMan'].crsy
#            file.write("%s %s %s %s\n" % (obj.name, x_abs, y_abs, obj.location[2]))
#        file.close()
#        return {'FINISHED'}

    
class OBJECT_OT_ExportObjButton(bpy.types.Operator):
    bl_idname = "export.object"
    bl_label = "Export object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)

        if not basedir:
            raise Exception("Save the blend file")

#        selection = bpy.context.selected_objects
#        bpy.ops.object.select_all(action='DESELECT')
        activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
        fn = os.path.join(basedir, activename)

        # write active object in obj format
        bpy.ops.export_scene.obj(filepath=fn + ".obj", use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')
        return {'FINISHED'}
    
class OBJECT_OT_objexportbatch(bpy.types.Operator):
    bl_idname = "obj.exportbatch"
    bl_label = "Obj export batch"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)
        if not basedir:
            raise Exception("Blend file is not saved")

        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in selection:
            obj.select = True
            name = bpy.path.clean_name(obj.name)
            fn = os.path.join(basedir, name)
            bpy.ops.export_scene.obj(filepath=str(fn + '.obj'), use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')
            obj.select = False
        return {'FINISHED'}

#_______________________________________________________________________________________________________________

class OBJECT_OT_fbxexp(bpy.types.Operator):
    bl_idname = "fbx.exp"
    bl_label = "Fbx export UE4"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)
        subfolder = 'FBX'
        if not os.path.exists(os.path.join(basedir, subfolder)):
            os.mkdir(os.path.join(basedir, subfolder))
            print('There is no FBX folder. Creating one...')
        else:
            print('Found previously created FBX folder. I will use it')
        if not basedir:
            raise Exception("Save the blend file")
            
        obj = bpy.context.scene.objects.active
        name = bpy.path.clean_name(obj.name)
        fn = os.path.join(basedir, subfolder, name)
        bpy.ops.export_scene.fbx(filepath= fn + ".fbx", check_existing=True, axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", version='BIN7400', ui_tab='MAIN', use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LAMP', 'MESH', 'OTHER'}, use_mesh_modifiers=True, mesh_smooth_type='EDGE', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True, use_anim_action_all=True, use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
#filepath = fn + ".fbx", filter_glob="*.fbx", version='BIN7400', use_selection=True, global_scale=100.0, axis_forward='-Z', axis_up='Y', bake_space_transform=False, object_types={'MESH','EMPTY'}, use_mesh_modifiers=False, mesh_smooth_type='EDGE', use_mesh_edges=False, use_tspace=False, use_armature_deform_only=False, bake_anim=False, bake_anim_use_nla_strips=False, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=False, use_anim_action_all=False, use_default_take=False, use_anim_optimize=False, anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)

#        obj.select = False
        return {'FINISHED'}

#_______________________________________________________________________________________________________________

class OBJECT_OT_fbxexportbatch(bpy.types.Operator):
    bl_idname = "fbx.exportbatch"
    bl_label = "Fbx export batch UE4"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)
        subfolder = 'FBX'
        if not os.path.exists(os.path.join(basedir, subfolder)):
            os.mkdir(os.path.join(basedir, subfolder))
            print('There is no FBX folder. Creating one...')
        else:
            print('Found previously created FBX folder. I will use it')
        if not basedir:
            raise Exception("Save the blend file")

        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in selection:
            obj.select = True
            name = bpy.path.clean_name(obj.name)
            fn = os.path.join(basedir, subfolder, name)
            bpy.ops.export_scene.fbx(filepath = fn + ".fbx", filter_glob="*.fbx", version='BIN7400', use_selection=True, global_scale=1.0, axis_forward='-Z', axis_up='Y', bake_space_transform=False, object_types={'MESH'}, use_mesh_modifiers=False, mesh_smooth_type='FACE', use_mesh_edges=False, use_tspace=False, use_armature_deform_only=False, bake_anim=False, bake_anim_use_nla_strips=False, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=False, use_anim_action_all=False, use_default_take=False, use_anim_optimize=False, anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
            obj.select = False
        return {'FINISHED'}
#_______________________________________________________________________________________________________________
class OBJECT_OT_osgtexportbatch(bpy.types.Operator):
    bl_idname = "osgt.exportbatch"
    bl_label = "osgt export batch"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)
        if not basedir:
            raise Exception("Blend file is not saved")

        bpy.ops.osg.export(SELECTED=True)

#        selection = bpy.context.selected_objects
#        bpy.ops.object.select_all(action='DESELECT')
#
#        for obj in selection:
#            obj.select = True
#            name = bpy.path.clean_name(obj.name)
#            fn = os.path.join(basedir, name)
#            bpy.ops.osg.export(filepath = fn + ".osgt", SELECTED=True)
#            bpy.ops.osg.export(SELECTED=True)
#            obj.select = False
        return {'FINISHED'}


