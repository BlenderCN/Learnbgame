import bpy
from mathutils import Vector
from ... preferences import get_preferences, get_color_for_drawing


class HOPS_OT_SetHopsColorToTheme(bpy.types.Operator):
    """
    Set HOPS theme to User Theme

    """
    bl_idname = "hops.color_to_theme"
    bl_label = "Set Hops Color To Theme"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Sets hops overlay color to theme in use"

    def execute(self, context):

        txtcol = bpy.context.preferences.themes[0].user_interface.wcol_pie_menu.text
        bgcol = bpy.context.preferences.themes[0].user_interface.wcol_pie_menu.inner
        bgcol2 = bpy.context.preferences.themes[0].user_interface.wcol_pie_menu.inner_sel

        bg2R = bgcol2[0]
        bg2G = bgcol2[1]
        bg2B = bgcol2[2]
        bg2A = bgcol2[3]

        bgR = bgcol[0]
        bgG = bgcol[1]
        bgB = bgcol[2]
        bgA = bgcol[3]

        txR = txtcol[0]
        txG = txtcol[1]
        txB = txtcol[2]
        txA = 0.9

        get_preferences().Hops_text_color = Vector((txR, txG, txB, txA))

        get_preferences().Hops_text2_color = Vector((txR, txG, txB, txA))

        get_preferences().Hops_border_color = Vector((bgR, bgG, bgB, bgA))

        get_preferences().Hops_border2_color = Vector((bg2R, bg2G, bg2B, bg2A))

        return {"FINISHED"}


class HOPS_OT_SetHopsColorToDefault(bpy.types.Operator):
    """
    Set HOPS theme to Default Theme

    """
    bl_idname = "hops.color_to_default"
    bl_label = "Set Hops Color To Default"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Sets hops overlay color to tdefault"

    def execute(self, context):

        bg2R, bg2G, bg2B, bg2A, bgR, bgG, bgB, bgA, txR, txG, txB, txA = get_color_for_drawing()

        get_preferences().Hops_text_color = Vector((txR, txG, txB, txA))

        get_preferences().Hops_text2_color = Vector((txR, txG, txB, txA))

        get_preferences().Hops_border_color = Vector((bgR, bgG, bgB, bgA))

        get_preferences().Hops_border2_color = Vector((bg2R, bg2G, bg2B, bg2A))

        return {"FINISHED"}


class HOPS_OT_SetHopsColorToTheme2(bpy.types.Operator):
    """
    Set HOPS theme to Theme 2

    """
    bl_idname = "hops.color_to_theme2"
    bl_label = "Set Hops Color To Theme 2"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Sets hops overlay color to theme in use"

    def execute(self, context):

        txtcol = bpy.context.preferences.themes[0].user_interface.wcol_pie_menu.text
        bgcol = bpy.context.preferences.themes[0].view_3d.grid
        bgcol2 = bpy.context.preferences.themes[0].view_3d.object_selected

        bg2R = bgcol2[0]
        bg2G = bgcol2[1]
        bg2B = bgcol2[2]
        bg2A = 0.7

        bgR = bgcol[0]
        bgG = bgcol[1]
        bgB = bgcol[2]
        bgA = 0.9

        txR = txtcol[0]
        txG = txtcol[1]
        txB = txtcol[2]
        txA = 0.9

        get_preferences().Hops_text_color = Vector((txR, txG, txB, txA))

        get_preferences().Hops_text2_color = Vector((txR, txG, txB, txA))

        get_preferences().Hops_border_color = Vector((bgR, bgG, bgB, bgA))

        get_preferences().Hops_border2_color = Vector((bg2R, bg2G, bg2B, bg2A))

        return {"FINISHED"}
