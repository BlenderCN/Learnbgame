import bpy
import os
from .functions import *

import bpy
import math

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


############## from here operators to export text ########################


class OBJECT_OT_ExportButtonName(bpy.types.Operator):
    bl_idname = "export.coordname"
    bl_label = "Export coord name"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        bpy.ops.export_test.some_data('INVOKE_DEFAULT')
            
        return {'FINISHED'}

def write_some_data(context, filepath, shift, rot, cam, nam):
    print("running write some data...")
    
    selection = bpy.context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')
#    activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)
#    fn = os.path.join(basedir, activename)

    f = open(filepath, 'w', encoding='utf-8')
        
#    file = open(fn + ".txt", 'w')

    # write selected objects coordinate
    for obj in selection:
        obj.select_set(True)

        x_coor = obj.location[0]
        y_coor = obj.location[1]
        z_coor = obj.location[2]
        
        if rot == True or cam == True:
            rotation_grad_x = math.degrees(obj.rotation_euler[0])
            rotation_grad_y = math.degrees(obj.rotation_euler[1])
            rotation_grad_z = math.degrees(obj.rotation_euler[2])

        if shift == True:
            shift_x = context.scene.BL_x_shift
            shift_y = context.scene.BL_y_shift
            shift_z = context.scene.BL_z_shift
            x_coor = x_coor+shift_x
            y_coor = y_coor+shift_y
            z_coor = z_coor+shift_z

        # Generate UV sphere at x = lon and y = lat (and z = 0 )

        if rot == True:
            if nam == True:
                f.write("%s %s %s %s %s %s %s\n" % (obj.name, x_coor, y_coor, z_coor, rotation_grad_x, rotation_grad_y, rotation_grad_z))
            else:    
                f.write("%s %s %s %s %s %s\n" % (x_coor, y_coor, z_coor, rotation_grad_x, rotation_grad_y, rotation_grad_z))
        if cam == True:
            if obj.type == 'CAMERA':
                f.write("%s %s %s %s %s %s %s %s\n" % (obj.name, x_coor, y_coor, z_coor, rotation_grad_x, rotation_grad_y, rotation_grad_z, obj.data.lens))        
        if rot == False and cam == False:
            if nam == True:
                f.write("%s %s %s %s\n" % (obj.name, x_coor, y_coor, z_coor))
            else:
                f.write("%s %s %s\n" % (x_coor, y_coor, z_coor))
        
    f.close()    
    
#    f.write("Hello World %s" % use_some_setting)
#    f.close()

    return {'FINISHED'}

class ExportCoordinates(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Coordinate Data"

    # ExportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob: StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.

    nam: BoolProperty(
            name="Add names of objects",
            description="This tool includes name",
            default=True,
            )

    rot: BoolProperty(
            name="Add coordinates of rotation",
            description="This tool includes name, position and rotation",
            default=False,
            )

    cam: BoolProperty(
            name="Export only cams",
            description="This tool includes name, position, rotation and focal lenght",
            default=False,
            )

    shift: BoolProperty(
            name="World shift coordinates",
            description="Shift coordinates using the General Shift Value (GSV)",
            default=False,
            )

    def execute(self, context):
        return write_some_data(context, self.filepath, self.shift, self.rot, self.cam, self.nam)

# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportCoordinates.bl_idname, text="Text Export Operator")

############## from here operators to export geometry ########################

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
        activename = bpy.path.clean_name(bpy.context.active_object.name)
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
            obj.select_set(True)
            name = bpy.path.clean_name(obj.name)
            fn = os.path.join(basedir, name)
            bpy.ops.export_scene.obj(filepath=str(fn + '.obj'), use_selection=True, axis_forward='Y', axis_up='Z', path_mode='RELATIVE')
            obj.select_set(False)
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
        obj = bpy.context.active_object
        name = bpy.path.clean_name(obj.name)
        fn = os.path.join(basedir, subfolder, name)
        bpy.ops.export_scene.fbx(filepath = fn + ".fbx", check_existing=True, filter_glob="*.fbx", ui_tab='MAIN', use_selection=True, use_active_collection=False, global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', bake_space_transform=False, object_types={'MESH'}, use_mesh_modifiers=True, use_mesh_modifiers_render=True, mesh_smooth_type='OFF', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=False, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True, axis_forward='-Z', axis_up='Y')

#       bpy.ops.export_scene.fbx(filepath= fn + ".fbx", check_existing=True, axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", ui_tab='MAIN', use_selection=True, global_scale=1.0, apply_unit_scale=True, bake_space_transform=False, object_types={'MESH'}, use_mesh_modifiers=True, mesh_smooth_type='EDGE', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True, use_anim_action_all=True, use_default_take=True, use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
#       filepath = fn + ".fbx", filter_glob="*.fbx", version='BIN7400', use_selection=True, global_scale=100.0, axis_forward='-Z', axis_up='Y', bake_space_transform=False, object_types={'MESH','EMPTY'}, use_mesh_modifiers=False, mesh_smooth_type='EDGE', use_mesh_edges=False, use_tspace=False, use_armature_deform_only=False, bake_anim=False, bake_anim_use_nla_strips=False, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=False, use_anim_action_all=False, use_default_take=False, use_anim_optimize=False, anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)

#        obj.select = False
        return {'FINISHED'}

#_______________________________________________________________________________________________________________

def createfolder(basedir, foldername):
    if not os.path.exists(os.path.join(basedir, foldername)):
        os.mkdir(os.path.join(basedir, foldername))
        print('There is no '+ foldername +' folder. Creating one...')
    else:
        print('Found previously created FBX folder. I will use it')
    if not basedir:
        raise Exception("Save the blend file before to export")

class OBJECT_OT_fbxexportbatch(bpy.types.Operator):
    bl_idname = "fbx.exportbatch"
    bl_label = "Fbx export batch UE4"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        basedir = os.path.dirname(bpy.data.filepath)
        subfolder = 'FBX'
        createfolder(basedir, subfolder)
        subfolderpath = os.path.join(basedir, subfolder)

        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in selection:
            obj.select_set(True)
            colfolder = obj.users_collection[0].name
            createfolder(subfolderpath, colfolder)
            name = bpy.path.clean_name(obj.name)
            fn = os.path.join(basedir, subfolder, colfolder, name)
#            bpy.ops.export_scene.fbx(filepath = fn + ".fbx", filter_glob="*.fbx", use_selection=True, global_scale=1.0, axis_forward='-Z', axis_up='Y', bake_space_transform=False, object_types={'MESH'}, use_mesh_modifiers=False, mesh_smooth_type='FACE', use_mesh_edges=False, use_tspace=False, use_armature_deform_only=False, bake_anim=False, bake_anim_use_nla_strips=False, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=False, use_anim_action_all=False, use_default_take=False, use_anim_optimize=False, anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
            bpy.ops.export_scene.fbx(filepath = fn + ".fbx", check_existing=True, filter_glob="*.fbx", ui_tab='MAIN', use_selection=True, use_active_collection=False, global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', bake_space_transform=False, object_types={'MESH'}, use_mesh_modifiers=True, use_mesh_modifiers_render=True, mesh_smooth_type='OFF', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=False, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True, axis_forward='-Z', axis_up='Y')
            obj.select_set(False)
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
        return {'FINISHED'}


