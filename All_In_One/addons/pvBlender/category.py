import nodeitems_utils

class pvNodeCategory(nodeitems_utils.NodeCategory):
  @classmethod
  def poll(cls, context):
    return context.space_data.tree_type == "pvNodeTree"
