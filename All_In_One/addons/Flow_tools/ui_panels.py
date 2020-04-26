import bpy
from bpy import context
from . import lightloader


class FlowTools2(bpy.types.Panel):
    bl_idname = "flow_tools"
    bl_label = "Flow Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Flow Tools 2"

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.label("Booleans")
        row = col.row(align=True)
        row.operator("f_tools_2.multi_object_boolean", text="Add", icon="MOD_ARRAY").operation = "UNION"
        row.operator("f_tools_2.multi_object_boolean", text="Sub", icon="MOD_BOOLEAN").operation = "DIFFERENCE"
        row.operator("f_tools_2.multi_object_boolean", text="Intersect", icon="MOD_MULTIRES").operation = "INTERSECT"

        col.separator()

        row = col.row(align=True)
        row.operator("gpencil.draw", text="Draw", icon="GREASEPENCIL")
        row.operator("gpencil.draw", text="Erase",icon="FORCE_CURVE").mode = "ERASER"
        row = col.row(align=True)
        row.operator
        row.operator("gpencil.draw", text="Line", icon="LINE_DATA").mode = "DRAW_STRAIGHT"
        row.operator("gpencil.draw", text="Poly", icon="MESH_DATA").mode = "DRAW_POLY"

        box = col.box()
        col1 = box.column(align=True)
        col1.label("Boolean Slash",)

        col1.prop(bpy.context.scene, "slash_cut_thickness")
        col1.prop(bpy.context.scene, "slash_cut_distance")
        col1.separator()
        col1.prop(bpy.context.scene, "slash_boolean_solver")

        col1.separator()

        slash_operator = col1.operator(
            "f_tools_2.slash_bool", text="Stroke Slash", icon="SCULPTMODE_HLT")
            
        slash_operator.cut_thickness = bpy.context.scene.slash_cut_thickness
        slash_operator.cut_distance = bpy.context.scene.slash_cut_distance
        slash_operator.boolean_solver = bpy.context.scene.slash_boolean_solver
        slash_operator.is_ciclic = False
        slash_operator.cut_using_mesh = False

        slash_operator = col1.operator("f_tools_2.slash_bool", text="Circular stroke Slash", icon="SCULPTMODE_HLT")
            
        slash_operator.cut_thickness = bpy.context.scene.slash_cut_thickness
        slash_operator.cut_distance = bpy.context.scene.slash_cut_distance
        slash_operator.boolean_solver = bpy.context.scene.slash_boolean_solver
        slash_operator.is_ciclic = True
        slash_operator.cut_using_mesh = False

        slash_operator = col1.operator("f_tools_2.slash_bool", text="Slash Using Mesh", icon="SCULPTMODE_HLT")
            
        slash_operator.cut_thickness = bpy.context.scene.slash_cut_thickness
        slash_operator.cut_distance = bpy.context.scene.slash_cut_distance
        slash_operator.boolean_solver = bpy.context.scene.slash_boolean_solver
        slash_operator.cut_using_mesh = True
        slash_operator.keep_objects = False
        
        col = layout.column(align = True)
        col.label("Remeshing")
        col.operator("f_tools_2.optimized_remesh", icon="MOD_REMESH")
        col.operator("f_tools_2.decimate", icon="MOD_DECIM").ratio = context.scene.decimate_factor
        col.prop(context.scene, "decimate_factor")

        col.separator()
        col.label("Envelope Builder")
        col.operator("f_tools_2.add_envelope_human", icon="MOD_ARMATURE")
        col.operator("f_tools_2.add_envelope_armature", icon="BONE_DATA")
        col.operator("f_tools_2.convert_envelope_to_mesh", icon="MESH_DATA")


class ViewportShader(bpy.types.Panel):
    bl_idname = "Flow lights"
    bl_label = "Solid Lights"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Flow Tools 2"

    def draw(self, context):
        layout = self.layout

        layout.label("Presets")
        row = layout.row(align=True)
        row.prop(context.scene, "lightloader_preset", text="")
        row.operator("f_tools_2.save_light_preset", text="", icon="ZOOMIN")
        row.operator("f_tools_2.delete_light_preset", text="", icon="ZOOMOUT").name = context.scene.lightloader_preset

        for light in context.user_preferences.system.solid_lights:
            layout.separator()
            row = layout.row()
            row.prop(light, "use", icon="OUTLINER_OB_LAMP", text="")

            col = row.column()
            col.prop(light, "direction", text="")
            row = col.row(align=True)
            row.prop(light, "diffuse_color", text="")
            row.prop(light, "specular_color", text="")
            row = col.row(align=True)
            row.label("Diffuse")
            row.label("Specular")
        layout.separator()
