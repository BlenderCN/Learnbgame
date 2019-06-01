import os
import bpy
from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper,
        path_reference_mode,
        axis_conversion,
        )

bl_info = {
  "name": "FBX Batch Exporter",
  "description": "Batch exporter for fbx files",
  "location": "File > Export",
  "version": (0, 1, 0),
  "blender": (2, 80, 0),
  "author": "Mack Thompson",
  "category": "Learnbgame",
}

def selectObjectSockets(obj):
  for child in bpy.data.objects:
    if child.parent == obj:
      child.select_set(True)

# Props
class BatchExportFBX(bpy.types.Operator, bpy.types.FileSelectParams):
  """Batch export FBX"""
  bl_idname = "io.export_batch_fbx"
  bl_label = "Batch Export FBX"
  bl_options = {'REGISTER'}

  filename_ext = ".fbx"
  use_filter_folder = True

  directory = StringProperty(
    default = "",
    subtype = "DIR_PATH",
    name = "Export Path",
    description = "The location to export the fbx files"
  )

  prefix = StringProperty(
    default = "SM_",
    name = "File prefix",
    description = "The File prefix"
  )

  suffix = StringProperty(
    default = "",
    name = " File suffix",
    description = "The file suffix"
  )

  bUseObjectOrigin = BoolProperty(
    default = True,
    name = "Use Object Origin",
    description = "Use each individual object's origin as the exported origin"
  )

  bExportSelected = BoolProperty(
    name ="Export Selected",
    description = "Only export the selected meshes"
  )

  bExportSockets = BoolProperty(
    name = "Export Sockets",
    description = "Export mesh sockets"
  )

  def invoke(self, context, event):
    context.window_manager.fileselect_add(self)
    return {'RUNNING_MODAL'}

  def execute(self, context):
    export_objects = context.scene.objects
    if self.bExportSelected == True:
      export_objects = context.selected_objects
    bpy.ops.object.select_all(action='DESELECT')
    for sceneobject in export_objects:
      if sceneobject.type == 'MESH':
        sceneobject.select_set(True)
        if self.bExportSockets == True:
          selectObjectSockets(sceneobject)
        if self.bUseObjectOrigin == True:
          # Temporarly move object to world origin
          originalloc = sceneobject.matrix_world.to_translation()
          sceneobject.location = (0, 0, 0)
          exportpath = os.path.join(self.directory, self.prefix + sceneobject.name + self.suffix + self.filename_ext)
          bpy.ops.export_scene.fbx(
            filepath=exportpath,
            check_existing=True,
            filter_glob="*.fbx",
            ui_tab='MAIN',
            use_selection=True,
            use_active_collection=False,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE',
            bake_space_transform=False,
            object_types={'EMPTY', 'MESH', 'OTHER'},
            use_mesh_modifiers=True,
            use_mesh_modifiers_render=True,
            mesh_smooth_type='FACE',
            use_mesh_edges=False,
            use_tspace=False,
            use_custom_props=False,
            add_leaf_bones=True,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            use_armature_deform_only=False,
            armature_nodetype='NULL',
            bake_anim=False,
            bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=True,
            bake_anim_use_all_actions=True,
            bake_anim_force_startend_keying=True,
            bake_anim_step=1.0,
            bake_anim_simplify_factor=1.0,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=True,
            axis_forward='X', axis_up='-Z'
          )
          # then move it back
          sceneobject.location = originalloc
          sceneobject.select_set(False)
        else:
          exportpath = os.path.join(self.directory, self.prefix + sceneobject.name + self.suffix + self.filename_ext)
          bpy.ops.export_scene.fbx(
            filepath=exportpath,
            check_existing=True,
            filter_glob="*.fbx",
            ui_tab='MAIN',
            use_selection=False,
            use_active_collection=False,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE',
            bake_space_transform=False,
            object_types={'EMPTY', 'MESH', 'OTHER'},
            use_mesh_modifiers=True,
            use_mesh_modifiers_render=True,
            mesh_smooth_type='FACE',
            use_mesh_edges=False,
            use_tspace=False,
            use_custom_props=False,
            add_leaf_bones=True,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            use_armature_deform_only=False,
            armature_nodetype='NULL',
            bake_anim=False,
            bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=True,
            bake_anim_use_all_actions=True,
            bake_anim_force_startend_keying=True,
            bake_anim_step=1.0,
            bake_anim_simplify_factor=1.0,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
            use_metadata=True,
            axis_forward='X', axis_up='-Z'
          )    
    bpy.ops.object.select_all(action='DESELECT') 
    return {'FINISHED'}

def export_menu(self, context):
  self.layout.operator(BatchExportFBX.bl_idname, text="Batch Export FBX")

def register():
  bpy.utils.register_class(BatchExportFBX)
  bpy.types.TOPBAR_MT_file_export.append(export_menu)

def unregister():
  bpy.utils.unregister_class(BatchExportFBX)
  bpy.types.TOPBAR_MT_file_export.remove(export_menu)

if __name__ == "__main__":
  register()