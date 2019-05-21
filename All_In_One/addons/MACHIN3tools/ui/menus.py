import bpy
from .. utils.registration import get_prefs



class MenuMACHIN3toolsObjectContextMenu(bpy.types.Menu):
    bl_idname = "MACHIN3_MT_machin3tools_object_context_menu"
    bl_label = "MACHIN3tools"

    def draw(self, context):
        layout = self.layout

        if getattr(bpy.types, "MACHIN3_OT_unmirror", False):
            layout.operator("machin3.unmirror", text="Un-Mirror")

        if getattr(bpy.types, "MACHIN3_OT_select_center_objects", False):
            layout.operator("machin3.select_center_objects", text="Select Center Objects")

        if getattr(bpy.types, "MACHIN3_OT_apply_transformations", False):
            layout.operator("machin3.apply_transformations", text="Apply Transformations")

        if getattr(bpy.types, "MACHIN3_OT_mesh_cut", False):
            layout.operator("machin3.mesh_cut", text="Mesh Cut")


class MenuAppendMaterials(bpy.types.Menu):
    bl_idname = "MACHIN3_MT_append_materials"
    bl_label = "Append Materials"

    def draw(self, context):
        layout = self.layout

        names = [mat.name for mat in get_prefs().appendmats]

        if names:
            names.insert(0, "ALL")
        else:
            layout.label(text="No Materials added yet!", icon="ERROR")
            layout.label(text="Check MACHIN3tools prefs.", icon="INFO")


        for name in names:
            layout.operator_context = 'INVOKE_DEFAULT'

            if name == "ALL":
                layout.operator("machin3.append_material", text=name, icon="MATERIAL_DATA").name = name
                layout.separator()

            elif name == "---":
                layout.separator()

            else:
                mat = bpy.data.materials.get(name)
                icon_val = layout.icon(mat) if mat else 0

                layout.operator("machin3.append_material", text=name, icon_value=icon_val).name = name
