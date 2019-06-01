import bpy

class MeshModifierPanel(bpy.types.Panel):
    bl_idname = "en_MeshModifierPanel"
    bl_label = "Modifier"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout
        modifier = context.active_object.data.node_modifier

        layout.prop(modifier, "enabled")
        layout.prop(modifier, "data_flow_group", text = "")
        layout.prop(modifier, "type", text = "")
        if modifier.type == "OFFSET":
            layout.prop(modifier, "source_object", text = "Source")