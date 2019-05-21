import bpy

class DriverPanel(bpy.types.Panel):
    bl_idname = "en_DriverPanel"
    bl_label = "Drivers"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        layout.operator("en.add_driver")

        for i, driver in enumerate(context.active_object.node_drivers):
            row = layout.row(align = True)
            row.prop(driver, "path", text = "", icon = "RNA")
            row.prop(driver, "data_flow_group", text = "")
            props = row.operator("en.print_driver_dependencies", text = "", icon = "CONSTRAINT")
            props.index = i
