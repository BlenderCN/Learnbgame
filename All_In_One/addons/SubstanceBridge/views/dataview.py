import bpy


# -----------------------------------------------------------------------------
# Substance Project panel
# -----------------------------------------------------------------------------
class SubstanceData(bpy.types.Panel):
    bl_label = "Substance Data"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(self, context):
        obj_slt = context.active_object

        return obj_slt is not None and obj_slt.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        ob = context.object

        # Substance Info save in object and data mesh.
        if ob.get('substance_project') is not None:
            layout.label("Sbs Project Name : ")
            layout.label(ob['substance_project'])

        # Debug Option
        layout.label("Debug Call")
        layout.operator("debug.sbs_data", text="Debug Sbs")


def register():
    bpy.utils.register_class(SubstanceData)


def unregister():
    bpy.utils.unregister_class(SubstanceData)
