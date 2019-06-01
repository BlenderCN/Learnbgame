import bpy
print("Load RootOperator Class")

class RootOperator(bpy.types.Operator):
  my_float = bpy.props.FloatProperty()
  bl_idname = "object.root_operator"
  bl_label = "Root Operator"

  def execute(self, context):
      print("##################################")
      print("# Execute ZstTools Root Operator #")
      print("##################################")
      return 'FINISHED'

  @classmethod
  def register(cls):
      print("Register in Root Operator")
      bpy.types.Scene.encouraging_message = bpy.props.StringProperty(
        name=""
        ,description="Root Operator description"
        ,default="Have a nice day!"
      )

  @classmethod
  def unregister():
      print("Unregister in RootOperator")
      del bpy.type.Scene.encouraging_message

if __name__ == "__main__":
    register()

bpy.utils.register_class(RootOperator)
