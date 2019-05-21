import bpy


class SetLightCommon(bpy.types.Operator):
  bl_idname = "radix.set_light_common"
  bl_label = "Common"
  bl_description = "Set a light with predefined color for common lights"
  bl_options = {'UNDO'}

  def execute(self, context):
    objects = bpy.context.selected_objects
    for object in objects:
      if object.type == 'LAMP':
        lamp = object.data

        lamp.color = [1.0, 0.95, 0.9]
        lamp.use_specular = False
      else:
        self.report(
          {'ERROR'},
          "Object of type '%s' can't be converted to the common light." % (object.type)
        )
    return {'FINISHED'}


class AddLightCommon(bpy.types.Operator):
  bl_idname = "radix.add_light_common"
  bl_label = "Common"
  bl_description = "Add a light with predefined color for common lights"
  bl_options = {'UNDO'}

  def execute(self, context):
    bpy.ops.object.lamp_add(type='POINT')
    bpy.ops.radix.set_light_common()
    return {'FINISHED'}


class SetLightEnd(bpy.types.Operator):
  bl_idname = "radix.set_light_end"
  bl_label = "End"
  bl_description = "Set a light with predefined color for end lights"
  bl_options = {'UNDO'}

  def execute(self, context):
    objects = bpy.context.selected_objects
    for object in objects:
      if object.type == 'LAMP':
        lamp = object.data

        lamp.color = [0.5, 0.5, 1]
        lamp.distance = 4
        lamp.energy = 5
        lamp.use_specular = False
      else:
        self.report(
          {'ERROR'},
          "Object of type '%s' can't be converted to the end light." % (object.type)
        )
    return {'FINISHED'}


class AddLightEnd(bpy.types.Operator):
  bl_idname = "radix.add_light_end"
  bl_label = "End"
  bl_description = "Add a light with predefined color for end lights"
  bl_options = {'UNDO'}

  def execute(self, context):
    bpy.ops.object.lamp_add(type='POINT')
    bpy.ops.radix.set_light_end()
    return {'FINISHED'}
