import bpy

import dsf.prop_writer

class ExportDsfProp (bpy.types.Operator):
  """export a dsf prop file.
  """
  bl_idname = "export_scene.dsf_prop"
  bl_label = "Export Dsf Props"

  filepath = bpy.props.StringProperty\
    ('file path', description = 'file path of the .duf file')
  output_group = bpy.props.StringProperty\
    ('group', description = 'subdirectory for data directory')
  rotate_yup = bpy.props.BoolProperty\
    ('y-up', description = 'rotate y-axis up', default = True)
  export_scale = bpy.props.FloatProperty\
    ('scale', description = 'scale factor for exporting',
     min = 1, max = 1000, soft_min = 1, soft_max = 100, default = 100)

  def execute (self, ctx):
    """export selected objects as dsf."""
    filepath = self.filepath
    output_group = self.output_group
    scale = self.export_scale
    rotate = self.rotate_yup
    dsf.prop_writer.export_prop (ctx, filepath, output_group, scale, rotate)
    return {'FINISHED'}

  def invoke (self, ctx, evt):
    """run the operator interactively.
    """
    ctx.window_manager.fileselect_add (self)
    return {'RUNNING_MODAL'}

def register ():
  bpy.utils.register_class (ExportDsfProp)

def unregister ():
  bpy.utils.unregister_class (ExportDsfProp)

def reload ():
  import imp
  import dsf.path_util, dsf.prop_writer, dsf.geom_create, dsf.scene_writer
  import dsf.geom_writer
  imp.reload (dsf.path_util)
  imp.reload (dsf.geom_create)
  imp.reload (dsf.prop_writer)
  imp.reload (dsf.scene_writer)
  imp.reload (dsf.geom_writer)
  unregister ()
  register ()
