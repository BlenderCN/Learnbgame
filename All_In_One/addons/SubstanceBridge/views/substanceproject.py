import bpy


# -----------------------------------------------------------------------------
# Substance Project panel
# Draw the UI panel, only the Substance project options :
# - Create a new Substance Project
# - Remove from a Substance Project
# - Export and re-export
# -----------------------------------------------------------------------------
class SubstanceProjectPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_substance_project"
    bl_label = "Substance Project"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Substances"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object
        act = context.active_object
        data = scn.sbs_project_settings

        row = layout.row(align=True)

        if act:
            # Check if this object as an Sbs Project.
            if act.get('substance_project') is not None:
                sbs_obj = bpy.context.active_object['substance_project']
                scene_name = bpy.context.scene.name
                scene = bpy.data.scenes[scene_name]['sbs_project_settings']
                scene['prj_name'] = sbs_obj

            row.prop(data, 'prj_name', text="")

            # Panel when the selected object has no Substance Project
            if obj.get("substance_project") is None:
                icon = "ZOOMIN"
                row.operator("sbs_painter.substance_name", text="", icon=icon)

                # Not Substance Project in this blend-file
                layout.label("Create a New Project")

            # If the mesh use a Substance Project
            else:
                icon = "ZOOMIN"
                row.operator("sbs_painter.substance_name", text="", icon=icon)
                icon = "RESTRICT_SELECT_OFF"
                row.operator("sbs_painter.selected_project", text="", icon=icon)
                icon = "PANEL_CLOSE"
                row.operator("sbs_painter.remove_from_project", text="", icon=icon)

                name = "Export New Project"
                ops = "substance.painter_export"
                layout.operator(ops, name).project = False

                data = scn.sbs_project_settings
                layout.prop(data, 'path_spp', text="")

                name = 'Export Update'
                icon = 'FILE_REFRESH'
                layout.operator(ops, name, icon=icon).project = True


def register():
    bpy.utils.register_class(SubstanceProjectPanel)


def unregister():
    bpy.utils.unregister_class(SubstanceProjectPanel)
