#!/usr/bin/env python3

import bpy
import mathutils
import json

bl_info = {
  'name': 'Import/Export Transformation',
  'author': 'Owen Trueblood',
  'version': (1, 0),
  'blender': (2, 79, 0),
  'location': 'File > Import/Export > Transformation',
  'warning': '',
  'description': 'Export or import position and rotation of selected object via JSON',
  'category': 'Import-Export',
  'wiki_url': ''
}

class ExportTransformation(bpy.types.Operator):
  '''Export transformation of selected object as JSON'''
  bl_idname = 'export.transformation_as_json'
  bl_label = 'Export Transformation'

  filepath = bpy.props.StringProperty(subtype='FILE_PATH')

  @classmethod
  def poll(cls, context):
    return context.object is not None

  def execute(self, context):
    recall_mode = context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    translation, rotation, scale = context.active_object.matrix_world.decompose()

    data = {
      'translation': {
        'x': translation.x,
        'y': translation.y,
        'z': translation.z,
      },
      'rotation': {
        'w': rotation.w,
        'x': rotation.x,
        'y': rotation.y,
        'z': rotation.z,
      },
      'scale': {
        'x': scale.x,
        'y': scale.y,
        'z': scale.z,
      },
    }

    with open(self.filepath, 'w') as export_file:
      json.dump(data, export_file, indent=2)

    bpy.ops.object.mode_set(mode=recall_mode)

    return {'FINISHED'}

  def invoke(self, context, event):
    context.window_manager.fileselect_add(self)
    return {'RUNNING_MODAL'}

class ImportTransformation(bpy.types.Operator):
  '''Import transformation from JSON and apply to selected object'''
  bl_idname = 'import.transformation_as_json'
  bl_label = 'Import Transformation'

  filepath = bpy.props.StringProperty(subtype='FILE_PATH')

  @classmethod
  def poll(cls, context):
    return context.object is not None

  def execute(self, context):
    recall_mode = context.object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    try:
      with open(self.filepath, 'r') as import_file:
        data = json.load(import_file)

        with open('/tmp/blog', 'a') as logfile:
          logfile.write('test')

        x = data['translation']['x']
        y = data['translation']['y']
        z = data['translation']['z']

        rw = data['rotation']['w']
        rx = data['rotation']['x']
        ry = data['rotation']['y']
        rz = data['rotation']['z']

        sx = data['scale']['x']
        sy = data['scale']['y']
        sz = data['scale']['z']

        mat_scale = mathutils.Matrix.Scale(sx, 4, (1, 0, 0)) * \
          mathutils.Matrix.Scale(sy, 4, (1, 0, 0)) * \
          mathutils.Matrix.Scale(sz, 4, (1, 0, 0))
        mat_rot = mathutils.Quaternion((rw, rx, ry, rz)).to_matrix().to_4x4()
        mat_pos = mathutils.Matrix.Translation(mathutils.Vector((x, y, z))).to_4x4()

        context.active_object.matrix_world = mat_scale * mat_pos * mat_rot

    except FileNotFoundError:
      self.report(type={'ERROR_INVALID_INPUT'}, message='File not found')

    bpy.ops.object.mode_set(mode=recall_mode)

    return {'FINISHED'}

  def invoke(self, context, event):
    context.window_manager.fileselect_add(self)
    return {'RUNNING_MODAL'}

def export_menu_func(self, context):
  self.layout.operator_context = 'INVOKE_DEFAULT'
  self.layout.operator(ExportTransformation.bl_idname, text='Transform (.json)')

def import_menu_func(self, context):
  self.layout.operator_context = 'INVOKE_DEFAULT'
  self.layout.operator(ImportTransformation.bl_idname, text='Transform (.json)')

def register():
  bpy.utils.register_class(ExportTransformation)
  bpy.utils.register_class(ImportTransformation)

  bpy.types.INFO_MT_file_export.append(export_menu_func)
  bpy.types.INFO_MT_file_import.append(import_menu_func)

def unregister():
  bpy.utils.unregister_class(ExportTransformation)
  bpy.utils.unregister_class(ImportTransformation)

  bpy.types.INFO_MT_file_export.remove(export_menu_func)
  bpy.types.INFO_MT_file_import.remove(import_menu_func)

if __name__ == '__main__':
  register()
