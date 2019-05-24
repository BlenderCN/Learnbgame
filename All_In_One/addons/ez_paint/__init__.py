# -*- coding: utf8 -*-
# python
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>


bl_info = {
    'name': 'EZ_Paint',
    'author': 'Bart Crouch, scorpion81, Spirou4D, artistCDMJ, brockmann',
    'version': (3, 12),
    'blender': (2, 79, 0),
    'location': 'Paint editor > 3D view',
    'warning': '',
    'description': 'Several improvements for PAINT MODE',
    'wiki_url': '',
    'tracker_url': '',
    "category": "Learnbgame",
}


import bgl, blf, bpy, mathutils, os, time, copy, math

from bpy.types import Operator, Menu, Panel, UIList
from bpy_extras.io_utils import ImportHelper


#################################################
#                                               #
#                  Functions                    #
#                                               #
#################################################

# Ecrit sur l'écran 3D: le nom de l'outil de peinture + le mode de fusion
def toolmode_draw_callback(self, context):
    # polling
    if not bpy.ops.paint.image_paint.poll():
        return
    # Fixe la ligne d'écriture
    if context.region:                     # fixee à une hauteur de l'écran - 32px
        main_y = context.region.height - 100
    else:
        return                       # Abandon car nous ne sommes pas en vue3D
    blend_dic = {"MIX": "Mix",
        "ADD": "Add",
        "SUB": "Subtract",
        "MUL": "Multiply",
        "LIGHTEN": "Lighten",
        "DARKEN": "Darken",
        "ERASE_ALPHA": "Erase Alpha",
        "ADD_ALPHA": "Add Alpha",
        "OVERLAY": "Overlay",
        "HARDLIGHT": "Hard light",
        "COLORBURN": "Color burn",
        "LINEARBURN": "Linear burn",
        "COLORDODGE": "Color dodge",
        "SCREEN": "Screen",
        "SOFTLIGHT": "Soft light",
        "PINLIGHT": "Pin light",
        "VIVIDLIGHT": "Vivid light",
        "LINEARLIGHT": "Linear light",
        "DIFFERENCE": "Difference",
        "EXCLUSION": "Exclusion",
        "HUE": "Hue",
        "SATURATION": "Saturation",
        "LUMINOSITY": "Luminosity",
        "COLOR": "Color"
    }                               # dictionnaire des modes de fusion

    wm = context.window_manager
    brush = context.tool_settings.image_paint.brush
    bhn, bhb = brush.name, brush.blend
    # brush.blend ne fait pas référence à un fichier mais au mode de la brosse
    text = bhn + " - " + blend_dic[bhb]

    # écriture du texte au coin haut-gauche
    bgl.glColor3f(.9, .9, .9)              # en blanc sale
    blf.position(0, 21, main_y, 0)         # à la position en 4 chiffres
    blf.draw(0, text)

    # Texte estompé selon le temps, au dessus de la brosse à 40px en rouge
    dt = time.time() - wm["ezp_toolmode_time"]
    if dt < 2:    # Aténuation de l'affichage selon le temps
        if "ezp_toolmode_brushloc" not in wm:
            return

        brush_x, brush_y = wm["ezp_toolmode_brushloc"]
        brush_x -= blf.dimensions(0, text)[0] / 2
        bgl.glColor4f(0.9, 0.16, 0.16, min(1.0, (2 - dt)*2))
        blf.position(0, brush_x, brush_y + 40, 0)
        blf.draw(0, text)



# ---------------------------------------------------------------------------
# ajouter une propriété d'ID au gestionnaire de fenêtre
def init_temp_props():
    wm = bpy.context.window_manager
    wm["ezp_automergeuv"] = False                 # 1 int
    wm["ezp_toolmode_time"] = time.time()         # 1 int in sec
    wm["ezp_toolmode_brushloc"] = (-1, -1)        # 2 int



# enlever toutes propriétés d'ID du gestionnaire de fenêtres
def remove_temp_props():
    wm = bpy.context.window_manager
    if "ezp_automergeuv" in wm:
        del wm["ezp_automergeuv"]

    if "ezp_toolmode_time" in wm:
        del wm["ezp_toolmode_time"]

    if "ezp_toolmode_brushloc" in wm:
        del wm["ezp_toolmode_brushloc"]

    if "ezp_toolmode_on_screen" in wm:
        del wm["ezp_toolmode_on_screen"]


# -----------------------------------------------------------------------------
# Retourner une liste de toutes les images qui ont été affichée dans un editeur d'image
def get_images_in_editors(context):
    images = []
    for area in context.screen.areas:
        if area.type != 'IMAGE_EDITOR':
            continue
        for space in area.spaces:
            if space.type != 'IMAGE_EDITOR':
                continue
            if space.image:
                images.append(space.image)
                area.tag_redraw() # mise à jour de l'editeur d'image

    return(images)


##########################################
#                                        #
#                  Classes               #
#                                        #
##########################################

###############################################################################
# PANNEAU DES OUTILS DE PEINTURE
class BrushPopup(Operator):
    """Brush popup"""
    bl_idname = "view3d.brush_popup"
    bl_label = "Brush settings"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'CYCLES'}
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if context.active_object:
            A = context.active_object.type == 'MESH'
            B = context.mode in {'PAINT_TEXTURE','PAINT_VERTEX','PAINT_WEIGHT'}
            return A and B

    @staticmethod
    def check(self, context):
        return True


    @staticmethod
    def paint_settings(context):
        toolsettings = context.tool_settings

        if context.vertex_paint_object:
            return toolsettings.vertex_paint
        elif context.weight_paint_object:
            return toolsettings.weight_paint
        elif context.image_paint_object:
            if (toolsettings.image_paint and toolsettings.image_paint.detect_data()):
                return toolsettings.image_paint

            return None
        return None

    @staticmethod
    def unified_paint_settings(parent, context):
        ups = context.tool_settings.unified_paint_settings
        parent.label(text="Unified Settings:")
        row = parent.row()
        row.prop(ups, "use_unified_size", text="Size")
        row.prop(ups, "use_unified_strength", text="Strength")
        if context.weight_paint_object:
            parent.prop(ups, "use_unified_weight", text="Weight")
        elif context.vertex_paint_object or context.image_paint_object:
            parent.prop(ups, "use_unified_color", text="Color")
        else:
            parent.prop(ups, "use_unified_color", text="Color")

    @staticmethod
    def prop_unified_size(parent, context, brush, prop_name, icon='NONE', text="", slider=False):
        ups = context.tool_settings.unified_paint_settings
        ptr = ups if ups.use_unified_size else brush
        parent.prop(ptr, prop_name, icon=icon, text=text, slider=slider)

    @staticmethod
    def prop_unified_strength(parent, context, brush, prop_name, icon='NONE', text="", slider=False):
        ups = context.tool_settings.unified_paint_settings
        ptr = ups if ups.use_unified_strength else brush
        parent.prop(ptr, prop_name, icon=icon, text=text, slider=slider)

    @staticmethod
    def prop_unified_weight(parent, context, brush, prop_name, icon='NONE', text="", slider=False):
        ups = context.tool_settings.unified_paint_settings
        ptr = ups if ups.use_unified_weight else brush
        parent.prop(ptr, prop_name, icon=icon, text=text, slider=slider)

    @staticmethod
    def prop_unified_color(parent, context, brush, prop_name, text=""):
        ups = context.tool_settings.unified_paint_settings
        ptr = ups if ups.use_unified_color else brush
        parent.prop(ptr, prop_name, text=text)

    @staticmethod
    def prop_unified_color_picker(parent, context, brush, prop_name, value_slider=True):
        ups = context.tool_settings.unified_paint_settings
        ptr = ups if ups.use_unified_color else brush
        parent.template_color_picker(ptr, prop_name, value_slider=value_slider)




    def brush_texpaint_common(self, layout, context, brush, settings, projpaint=False):
        capabilities = brush.image_paint_capabilities

        col = layout.column()

        if brush.image_tool in {'DRAW', 'FILL'}:
            if brush.blend not in {'ERASE_ALPHA', 'ADD_ALPHA'}:
                if not brush.use_gradient:
                    self.prop_unified_color_picker(col, context, brush, "color", value_slider=True)

                if settings.palette:
                    col.template_palette(settings, "palette", color=True)

                if brush.use_gradient:
                    col.label("Gradient Colors")
                    col.template_color_ramp(brush, "gradient", expand=True)

                    if brush.image_tool != 'FILL':
                        col.label("Background Color")
                        row = col.row(align=True)
                        self.prop_unified_color(row, context, brush, "secondary_color", text="")

                    if brush.image_tool == 'DRAW':
                        col.prop(brush, "gradient_stroke_mode", text="Mode")
                        if brush.gradient_stroke_mode in {'SPACING_REPEAT', 'SPACING_CLAMP'}:
                            col.prop(brush, "grad_spacing")
                    elif brush.image_tool == 'FILL':
                        col.prop(brush, "gradient_fill_mode")
                else:
                    row = col.row(align=True)
                    self.prop_unified_color(row, context, brush, "color", text="")
                    if brush.image_tool == 'FILL' and not projpaint:
                        col.prop(brush, "fill_threshold")
                    else:
                        self.prop_unified_color(row, context, brush, "secondary_color", text="")
                        row.separator()
                        row.operator("paint.brush_colors_flip", icon='FILE_REFRESH', text="")

        elif brush.image_tool == 'SOFTEN':
            col = layout.column(align=True)
            col.row().prop(brush, "direction", expand=True)
            col.separator()
            col.prop(brush, "sharp_threshold")
            if not projpaint:
                col.prop(brush, "blur_kernel_radius")
            col.separator()
            col.prop(brush, "blur_mode")

        elif brush.image_tool == 'MASK':
            col.prop(brush, "weight", text="Mask Value", slider=True)

        elif brush.image_tool == 'CLONE':
            col.separator()
            if projpaint:
                if settings.mode == 'MATERIAL':
                    col.prop(settings, "use_clone_layer", text="Clone from paint slot")
                elif settings.mode == 'IMAGE':
                    col.prop(settings, "use_clone_layer", text="Clone from image/UV map")

                if settings.use_clone_layer:
                    ob = context.active_object
                    col = layout.column()

                    if settings.mode == 'MATERIAL':
                        if len(ob.material_slots) > 1:
                            col.label("Materials")
                            col.template_list("MATERIAL_UL_matslots", "",
                                              ob, "material_slots",
                                              ob, "active_material_index", rows=2)

                        mat = ob.active_material
                        if mat:
                            col.label("Source Clone Slot")
                            col.template_list("TEXTURE_UL_texpaintslots", "",
                                              mat, "texture_paint_images",
                                              mat, "paint_clone_slot", rows=2)

                    elif settings.mode == 'IMAGE':
                        mesh = ob.data

                        clone_text = mesh.uv_texture_clone.name if mesh.uv_texture_clone else ""
                        col.label("Source Clone Image")
                        col.template_ID(settings, "clone_image")
                        col.label("Source Clone UV Map")
                        col.menu("VIEW3D_MT_tools_projectpaint_clone", text=clone_text, translate=False)
            else:
                col.prop(brush, "clone_image", text="Image")
                col.prop(brush, "clone_alpha", text="Alpha")

        col.separator()

        if capabilities.has_radius:
            row = col.row(align=True)
            self.prop_unified_size(row, context, brush, "size", slider=True, text="Radius")
            self.prop_unified_size(row, context, brush, "use_pressure_size")

        row = col.row(align=True)

        if capabilities.has_space_attenuation:
            row.prop(brush, "use_space_attenuation", toggle=True, icon_only=True)

        self.prop_unified_strength(row, context, brush, "strength", text="Strength")
        self.prop_unified_strength(row, context, brush, "use_pressure_strength")

        if brush.image_tool in {'DRAW', 'FILL'}:
            col.separator()
            col.prop(brush, "blend", text="Blend")

        col = layout.column()

        # use_accumulate
        if capabilities.has_accumulate:
            col = layout.column(align=True)
            col.prop(brush, "use_accumulate")

        if projpaint:
            col.prop(brush, "use_alpha")

        col.prop(brush, "use_gradient")

        col.separator()
        col.template_ID(settings, "palette", new="palette.new")



    def draw(self, context):
        # Init values
        toolsettings = context.tool_settings
        settings = self.paint_settings(context)

        layout = self.layout
        col = layout.column()

        if not settings:
            row = col.row(align=True)
            row.label(text="Setup texture paint, please!")
        else:
            brush = settings.brush
            ipaint = toolsettings.image_paint
            # Stroke mode
            col.prop(brush, "stroke_method", text="")

            if brush.use_anchor:
                col.separator()
                col.prop(brush, "use_edge_to_edge", "Edge To Edge")

            if brush.use_airbrush:
                col.separator()
                col.prop(brush, "rate", text="Rate", slider=True)

            if brush.use_space:
                col.separator()
                row = col.row(align=True)
                row.prop(brush, "spacing", text="Spacing")
                row.prop(brush, "use_pressure_spacing", toggle=True, text="")

            if brush.use_line or brush.use_curve:
                col.separator()
                row = col.row(align=True)
                row.prop(brush, "spacing", text="Spacing")

            if brush.use_curve:
                col.separator()
                col.template_ID(brush, "paint_curve", new="paintcurve.new")
                col.operator("paintcurve.draw")

            else:
                col.separator()

                row = col.row(align=True)
                row.prop(brush, "use_relative_jitter", icon_only=True)
                if brush.use_relative_jitter:
                    row.prop(brush, "jitter", slider=True)
                else:
                    row.prop(brush, "jitter_absolute")
                row.prop(brush, "use_pressure_jitter", toggle=True, text="")

                col = layout.column()
                col.separator()

                if brush.brush_capabilities.has_smooth_stroke:
                    col.prop(brush, "use_smooth_stroke")
                    if brush.use_smooth_stroke:
                        sub = col.column()
                        sub.prop(brush, "smooth_stroke_radius", text="Radius", slider=True)
                        sub.prop(brush, "smooth_stroke_factor", text="Factor", slider=True)

            layout.prop(settings, "input_samples")

            # Curve stroke
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("brush.curve_preset", icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
            row.operator("brush.curve_preset", icon='SPHERECURVE', text="").shape = 'ROUND'
            row.operator("brush.curve_preset", icon='ROOTCURVE', text="").shape = 'ROOT'
            row.operator("brush.curve_preset", icon='SHARPCURVE', text="").shape = 'SHARP'
            row.operator("brush.curve_preset", icon='LINCURVE', text="").shape = 'LINE'
            row.operator("brush.curve_preset", icon='NOCURVE', text="").shape = 'MAX'

            # Symetries mode
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(ipaint, "use_symmetry_x", text="X", toggle=True)
            row.prop(ipaint, "use_symmetry_y", text="Y", toggle=True)
            row.prop(ipaint, "use_symmetry_z", text="Z", toggle=True)

            # imagepaint tool operate  buttons: UILayout.template_ID_preview()
            col = layout.split().column()
            ###################################### ICI PROBLEME d'icones de brosse !
            # bpy.context.tool_settings.image_paint.brush

            col.template_ID_preview(settings, "brush", new="brush.add", rows=1, cols=3   )

            ########################################################################

            # Texture Paint Mode #
            if context.image_paint_object and brush:
                self.brush_texpaint_common( layout, context, brush, settings, True)

            ########################################################################
            # Weight Paint Mode #
            elif context.weight_paint_object and brush:

                col = layout.column()

                row = col.row(align=True)
                self.prop_unified_weight(row, context, brush, "weight", slider=True, text="Weight")

                row = col.row(align=True)
                self.prop_unified_size(row, context, brush, "size", slider=True, text="Radius")
                self.prop_unified_size(row, context, brush, "use_pressure_size")

                row = col.row(align=True)
                self.prop_unified_strength(row, context, brush, "strength", text="Strength")
                self.prop_unified_strength(row, context, brush, "use_pressure_strength")

                col.prop(brush, "vertex_tool", text="Blend")

                if brush.vertex_tool == 'BLUR':
                    col.prop(brush, "use_accumulate")
                    col.separator()

                col = layout.column()
                col.prop(toolsettings, "use_auto_normalize", text="Auto Normalize")
                col.prop(toolsettings, "use_multipaint", text="Multi-Paint")

            ########################################################################
            # Vertex Paint Mode #
            elif context.vertex_paint_object and brush:
                col = layout.column()
                self.prop_unified_color_picker(col, context, brush, "color", value_slider=True)
                if settings.palette:
                    col.template_palette(settings, "palette", color=True)
                self.prop_unified_color(col, context, brush, "color", text="")

                col.separator()
                row = col.row(align=True)
                self.prop_unified_size(row, context, brush, "size", slider=True, text="Radius")
                self.prop_unified_size(row, context, brush, "use_pressure_size")

                row = col.row(align=True)
                self.prop_unified_strength(row, context, brush, "strength", text="Strength")
                self.prop_unified_strength(row, context, brush, "use_pressure_strength")

                col.separator()
                col.prop(brush, "vertex_tool", text="Blend")

                col.separator()
                col.template_ID(settings, "palette", new="palette.new")




    def invoke(self, context, event):
        if context.space_data.type == 'IMAGE_EDITOR':
            context.space_data.mode = 'PAINT'

        return context.window_manager.invoke_props_dialog(self, width=148)
        # return {'PASS_THROUGH'} ou {'CANCELLED'} si le bouton ok est cliqué

    def execute(self, context):
        return {'FINISHED'}


# PANNEAU DES MASQUES DE PEINTURE
class TexturePopup(Operator):
    """Texture popup"""
    bl_idname = "view3d.texture_popup"
    bl_label = "Texture & Mask"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'CYCLES'}
    bl_options = {'REGISTER', 'UNDO'}

    toggleMenu = bpy.props.BoolProperty(default=True)  # toogle texture or Mask menu

    def check(self, context):
        return True

    @classmethod
    def poll(self, context):
        obj =  context.active_object
        if obj is not None:
            A = obj.type == 'MESH'
            B = context.mode == 'PAINT_TEXTURE'
            return A and B

    def draw(self, context):
        # Init values
        toolsettings = context.tool_settings
        brush = toolsettings.image_paint.brush
        tex_slot = brush.texture_slot
        mask_tex_slot = brush.mask_texture_slot

        unified = toolsettings.unified_paint_settings
        settings = toolsettings.image_paint

        # ================================================== textures panel
        layout = self.layout

        # Parameter Toggle Menu
        _TITLE = 'TEXTURES' if self.toggleMenu else 'MASKS'
        _ICON = 'TEXTURE' if self.toggleMenu else 'MOD_MASK'
        Menu = layout.row()
        Menu.prop(self, "toggleMenu", text=_TITLE, icon=_ICON)


        if self.toggleMenu:
            col = layout.column()                                   #TEXTURES
            col.template_ID_preview(brush, "texture", new="texture.new", rows=3, cols=8)

            if brush.texture:
                row = layout.row(align=True)
                row.operator("paint.modify_brush_textures", text="Modify brush Texture", icon='IMAGE_COL').toggleType=True

            layout.label(text="Brush Mapping:")

            # texture_map_mode
            layout.row().prop(tex_slot, "tex_paint_map_mode", text="")
            layout.separator()

            if tex_slot.map_mode == 'STENCIL':
                if brush.texture and brush.texture.type == 'IMAGE':
                    layout.operator("brush.stencil_fit_image_aspect")
                layout.operator("brush.stencil_reset_transform")

            # angle and texture_angle_source
            if tex_slot.has_texture_angle:
                col = layout.column()
                col.label(text="Angle:")
                col.prop(tex_slot, "angle", text="")
                if tex_slot.has_texture_angle_source:
                    col.prop(tex_slot, "use_rake", text="Rake")

                    if brush.brush_capabilities.has_random_texture_angle \
                                        and tex_slot.has_random_texture_angle:
                        col.prop(tex_slot, "use_random", text="Random")
                        if tex_slot.use_random:
                            col.prop(tex_slot, "random_angle", text="")


            # scale and offset
            split = layout.split()
            split.prop(tex_slot, "offset")
            split.prop(tex_slot, "scale")

            row = layout.row()
            row.operator(MakeBrushImageTexture.bl_idname)
        else:
            col = layout.column()                                 #MASK TEXTURE
            col.template_ID_preview(brush, "mask_texture", new="texture.new", \
                                                                rows=3, cols=8)

            if brush.mask_texture:
                row = layout.row(align=True)
                row.operator("paint.modify_brush_textures", text="Modify brush Texture", icon='IMAGE_COL').toggleType=False

            layout.label(text="Mask Mapping:")
            # map_mode
            layout.row().prop(mask_tex_slot, "mask_map_mode", text="")
            layout.separator()

            if mask_tex_slot.map_mode == 'STENCIL':
                if brush.mask_texture and brush.mask_texture.type == 'IMAGE':
                    layout.operator("brush.stencil_fit_image_aspect").mask = True
                layout.operator("brush.stencil_reset_transform").mask = True

            col = layout.column()
            col.prop(brush, "use_pressure_masking", text="")
            # angle and texture_angle_source
            if mask_tex_slot.has_texture_angle:
                col = layout.column()
                col.label(text="Angle:")
                col.prop(mask_tex_slot, "angle", text="")
                if mask_tex_slot.has_texture_angle_source:
                    col.prop(mask_tex_slot, "use_rake", text="Rake")

                    if brush.brush_capabilities.has_random_texture_angle and mask_tex_slot.has_random_texture_angle:
                        col.prop(mask_tex_slot, "use_random", text="Random")
                        if mask_tex_slot.use_random:
                            col.prop(mask_tex_slot, "random_angle", text="")

            # scale and offset
            split = layout.split()
            split.prop(mask_tex_slot, "offset")
            split.prop(mask_tex_slot, "scale")
            row = layout.row()
            row.operator(MakeBrushImageTextureMask.bl_idname)


    def invoke(self, context, event):
        if context.space_data.type == 'IMAGE_EDITOR':
            context.space_data.mode = 'PAINT'
        return context.window_manager.invoke_props_dialog(self, width=146)

    def execute(self, context):
        return {'FINISHED'}


# PANNEAU DES PROJECTPAINT SLOTS (& Blender MASKs)
class ProjectpaintPopup(Operator):
    """Slots ProjectPaint popup"""
    bl_idname = "view3d.projectpaint"
    bl_label = "Slots & VGroups"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'CYCLES'}
    bl_options = {'REGISTER', 'UNDO'}

    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        brush = context.tool_settings.image_paint.brush
        ob = context.active_object
        group = ob.vertex_groups.active
        if (brush is not None and ob is not None):
            A = ob.type == 'MESH'
             # -------------------------------
            B = context.space_data.type == 'VIEW_3D'
            if A:
                C = context.mode in {'PAINT_TEXTURE','PAINT_VERTEX','PAINT_WEIGHT'}
                D = context.mode == 'EDIT_MESH'
            # -------------------------------
            E = context.space_data.type == 'IMAGE_EDITOR'
            if E:
                F = context.mode == 'EDIT_MESH'
                G = context.space_data.mode == 'PAINT'
            # -------------------------------
            H = context.mode == 'WEIGHT_PAINT' and ob.vertex_groups and ob.data.use_paint_mask_vertex
            return A and (( B and (C or  D)) or (E and (F or G) or H))
        return False

    def draw(self, context):
        settings = context.tool_settings.image_paint
        ob = context.active_object

        Egne = bpy.context.scene.render.engine

        layout = self.layout
        #-----------------------------------------------------------Vertex Paint
        ob = context.object
        group = ob.vertex_groups.active
        rows = 4 if group else 2

        row = layout.row()
        row.template_list("MESH_UL_vgroups", "", ob, "vertex_groups", ob.vertex_groups, "active_index", rows=rows)

        col = row.column(align=True)
        col.operator("object.vertex_group_add", icon='ZOOMIN', text="")
        col.operator("object.vertex_group_remove", icon='ZOOMOUT', text="").all = False
        col.menu("MESH_MT_vertex_group_specials", icon='DOWNARROW_HLT', text="")


        if group:
            col.separator()
            col.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if ob.vertex_groups and (ob.mode == 'EDIT' or (ob.mode == 'WEIGHT_PAINT' and ob.type == 'MESH' and ob.data.use_paint_mask_vertex)):
            row = layout.row()

            sub = row.row(align=True)
            sub.operator("object.vertex_group_assign", text="Assign")
            sub.operator("object.vertex_group_remove_from", text="Remove")

            sub = row.row(align=True)
            sub.operator("object.vertex_group_select", text="Select")
            sub.operator("object.vertex_group_deselect", text="Deselect")

            layout.prop(context.tool_settings, "vertex_group_weight", text="Weight")


        #--------------------------------------------------------------Mat Paint
        if context.mode == 'PAINT_TEXTURE':
            col = layout.column()
            col.label("Painting Mode")
            col.prop(settings, "mode", text="")
            col.separator()

            if settings.mode == 'MATERIAL':
                if len(ob.material_slots) > 1:
                    col.label("Materials")
                    col.template_list("MATERIAL_UL_matslots", "layers",
                                      ob, "material_slots",
                                      ob, "active_material_index", rows=2)

                mat = ob.active_material
                if mat:
                    col.label("Available Paint Slots")
                    col.template_list("TEXTURE_UL_texpaintslots", "",
                                      mat, "texture_paint_images",
                                      mat, "paint_active_slot", rows=2)

                    if mat.texture_paint_slots:
                        slot = mat.texture_paint_slots[mat.paint_active_slot]
                    else:
                        slot = None

                    if (not mat.use_nodes) and context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}:
                        row = col.row(align=True)
                        row.operator_menu_enum("paint.add_texture_paint_slot", "type")
                        row.operator("paint.delete_texture_paint_slot", text="", icon='X')

                        if slot:
                            col.prop(mat.texture_slots[slot.index], "blend_type")
                            col.separator()

                    if slot and slot.index != -1:
                        col.label("UV Map")
                        col.prop_search(slot, "uv_layer", ob.data, "uv_textures", text="")

            elif settings.mode == 'IMAGE':
                mesh = ob.data
                uv_text = mesh.uv_textures.active.name if mesh.uv_textures.active else ""
                col.label("Canvas Image")
                col.template_ID(settings, "canvas")
                col.operator("image.new", text="New").gen_context = 'PAINT_CANVAS'
                col.label("UV Map")
                col.menu("VIEW3D_MT_tools_projectpaint_uvlayer", text=uv_text, translate=False)

            col.separator()
            if Egne == 'CYCLES':
                col.operator("paint.add_texture_paint_slot", text="Add Texture", icon="FACESEL_HLT").type="DIFFUSE_COLOR"
                col.operator("object.save_ext_paint_texture", text="Save selected Slot")
            else:
                col.operator("image.save_dirty", text="Save All Images")

    def invoke(self, context,event):
        return context.window_manager.invoke_props_dialog(self, width=240)

    def execute(self, context):
        return {'FINISHED'}




################################################################################
# Ajouter un mat + 1 texture DIFF 1024x1024-alpha à l'objet selectionné
class AddDefaultMatDiff(Operator):
    '''Create and assign a new mat + DIFF texture to the object'''
    bl_idname = "object.add_default_image"
    bl_label = "Add default image"


    @classmethod
    def poll(cls, context):
        if context.active_object!=None:
            return context.active_object.type=='MESH'
        return False

    def invoke(self, context, event):
        ob = context.active_object
        mat = bpy.data.materials.new("default")

        #Add texture to the mat
        tex = bpy.data.textures.new("default", 'IMAGE')
        img = bpy.data.images.new("default", 1024, 1024, alpha=True)
        ts = mat.texture_slots.add()
        tex.image = img
        ts.texture_coords = 'UV'
        ts.use_map_color_diffuse = True
        ts.texture = tex

        ob.data.materials.append(mat)
        return {'FINISHED'}

# Ajouter un mat standart + 3 textures DIFF/SPEC/NORM sans image à tous les objets selectionnés
class DefaultMaterial(Operator):
    '''Add a default dif/spec/normal material to an object'''
    bl_idname = "object.default_material"
    bl_label = "Default material"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if not object or not object.data:
            return False
        return object.type == 'MESH'

    def invoke(self, context, event):
        objects = context.selected_objects
        for ob in objects:
            if not ob.data or ob.type != 'MESH':
                continue

            mat = bpy.data.materials.new(ob.name)

            # diffuse texture
            tex = bpy.data.textures.new(ob.name+"_DIFF", 'IMAGE')
            ts = mat.texture_slots.add()
            ts.texture_coords = 'UV'
            ts.texture = tex
            # specular texture
            tex = bpy.data.textures.new(ob.name+"_SPEC", 'IMAGE')
            ts = mat.texture_slots.add()
            ts.texture_coords = 'UV'
            ts.use_map_color_diffuse = False
            ts.use_map_specular = True
            ts.texture = tex
            # normal texture
            tex = bpy.data.textures.new(ob.name+"_NORM", 'IMAGE')
            tex.use_normal_map = True
            ts = mat.texture_slots.add()
            ts.texture_coords = 'UV'
            ts.use_map_color_diffuse = False
            ts.use_map_normal = True
            ts.texture = tex

            ob.data.materials.append(mat)

        return {'FINISHED'}

class MakeBrushImageTexture(Operator):
    bl_label = "New Texture from Image"
    bl_idname = "gizmo.image_texture"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self,context):
        tex = bpy.data.textures.new("ImageTexture",'NONE')
        tex.use_nodes = True
        remove = tex.node_tree.nodes[1]
        tex.node_tree.nodes.remove(remove)
        tex.node_tree.nodes.new("TextureNodeImage")
        tex.node_tree.links.new(tex.node_tree.nodes[0].inputs[0],tex.node_tree.nodes[1].outputs[0])
        tex.node_tree.nodes[1].location = [0,50]
        tex.node_tree.nodes[0].location = [200,50]

        i = bpy.data.images.load(self.filepath)
        tex.node_tree.nodes[1].image = i

        if bpy.context.mode == 'PAINT_TEXTURE':
            bpy.context.tool_settings.image_paint.brush.texture = tex
        elif bpy.context.mode == 'PAINT_VERTEX':
            bpy.context.tool_settings.vertex_paint.brush.texture = tex
        elif bpy.context.mode == 'PAINT_WEIGHT':
            bpy.context.tool_settings.weight_paint.brush.texture = tex
        #elif bpy.context.mode == 'SCULPT':
            #bpy.context.tool_settings.sculpt.brush.texture = tex

        return set()


class MakeBrushImageTextureMask(Operator):
    bl_label = "New Mask Texture from Image"
    bl_idname = "gizmo.image_texture_mask"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self,context):
        tex = bpy.data.textures.new("ImageTextureMask",'NONE')
        tex.use_nodes = True
        remove = tex.node_tree.nodes[1]
        tex.node_tree.nodes.remove(remove)
        tex.node_tree.nodes.new("TextureNodeImage")
        tex.node_tree.nodes.new("TextureNodeRGBToBW")

        tex.node_tree.links.new(tex.node_tree.nodes[0].inputs[0],tex.node_tree.nodes[2].outputs[0])
        tex.node_tree.links.new(tex.node_tree.nodes[2].inputs[0],tex.node_tree.nodes[1].outputs[0])
        tex.node_tree.nodes[1].location = [0,50]
        tex.node_tree.nodes[2].location = [200,50]
        tex.node_tree.nodes[0].location = [400,50]

        i = bpy.data.images.load(self.filepath)
        tex.node_tree.nodes[1].image = i

        if bpy.context.mode == 'PAINT_TEXTURE':
            bpy.context.tool_settings.image_paint.brush.mask_texture = tex
        elif bpy.context.mode == 'PAINT_VERTEX':
            bpy.context.tool_settings.vertex_paint.brush.mask_texture = tex
        elif bpy.context.mode == 'PAINT_WEIGHT':
            bpy.context.tool_settings.weight_paint.brush.mask_texture = tex
        #elif bpy.context.mode == 'SCULPT':
            #bpy.context.tool_settings.sculpt.brush.mask_texture = tex

        return set()



# Importer en même temps tous les objets de plusieurs [fichiers .blend étant dans un dossier]!
class MassLinkAppend(Operator, ImportHelper):
    '''Import objects from multiple blend-files at the same time'''
    bl_idname = "wm.mass_link_append"
    bl_label = "Mass Link/Append"
    bl_options = {'REGISTER', 'UNDO'}

    active_layer = bpy.props.BoolProperty(name="Active Layer",
            default=True,
            description="Put the linked objects on the active layer"
    )

    autoselect = bpy.props.BoolProperty(name="Select",
            default=True,
            description="Select the linked objects"
    )

    instance_groups = bpy.props.BoolProperty(name="Instance Groups",
            default=False,
            description="Create instances for each group as a DupliGroup"
    )

    link = bpy.props.BoolProperty(name="Link",
            default=False,
            description="Link the objects or datablocks rather than appending"
    )

    relative_path = bpy.props.BoolProperty(name="Relative Path",
            default=True,
            description="Select the file relative to the blend file"
    )

    def execute(self, context):
        directory, filename = os.path.split(bpy.path.abspath(self.filepath))
        files = []

        # find all blend-files in the given directory
        for root, dirs, filenames in os.walk(directory):
            for file in filenames:
                if file.endswith(".blend"):
                    files.append([root+os.sep, file])
            break # don't search in subdirectories

        # append / link objects
        old_selection = context.selected_objects
        new_selection = []
        print("_______ Texture Paint Plus _______")
        print("You can safely ignore the line(s) below")
        for directory, filename in files:
            # get object names
            with bpy.data.libraries.load(directory + filename) as (append_lib, current_lib):
                ob_names = append_lib.objects  # les noms des objets à ajouter
            for name in ob_names:
                append_libs = [{"name":name} for name in ob_names] # ajout des objets à la librairie
            # appending / linking
            bpy.ops.wm.link_append(filepath=os.sep+filename+os.sep+"Object"+os.sep,
                filename=name, directory=directory+filename+os.sep+"Object"+os.sep,
                link=self.link, autoselect=True, active_layer=self.active_layer,
                relative_path=self.relative_path, instance_groups=self.instance_groups,
                files=append_libs)
            if not self.link:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.make_local()
                bpy.ops.object.make_local(type='SELECTED_OBJECTS_DATA')
            new_selection += context.selected_objects   # importance de autoselect=True
        print("__________________________________")
        bpy.ops.object.select_all(action='DESELECT')    # déselection de tous les objets

        if self.autoselect:                     # en fonction du choix en important les objets
            for ob in new_selection:
                ob.select = True
        else:
            for ob in old_selection:
                ob.select = True                # selectionne tous ou seulement ceux sélectionnés au début

        return {'FINISHED'}


# Recharger les images affichées dans l'editeur d'images + syncroniser les vues 3D
class ReloadImage(Operator):      # non utilisée
    '''Reload image displayed in image-editor'''
    bl_idname = "paint.reload_image"
    bl_label = "Reload image"


    def invoke(self, context, event):
        images = get_images_in_editors(context)
        for img in images:
            img.reload()

        # get_images_in_editors() met à jour l'éditor d'image
        # Iici on syncronise le changement immédiatement en vue 3d
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        return{'FINISHED'}


# Recharge TOUTES LES images de Blender et syncroniser l'editeur d'image et la vue 3D
class ReloadImages(Operator):
    '''Reload all images in Blender'''
    bl_idname = "paint.reload_images"
    bl_label = "Reload all images"

    def invoke(self, context, event):
        reloaded = [0, 0]
        for img in bpy.data.images:
            img.reload()

        # Mise a jour immédiate dans l'editeur d'image & en vue 3D
        # cad rafraichir l'écran des éditeurs
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR' or area.type == 'VIEW_3D':
                area.tag_redraw()

        return {'FINISHED'}


# Enregistre les images affichées dans l'Editeur d'Images
class SaveImage(Operator):
    '''Save image displayed in image-editor'''
    bl_idname = "paint.save_image"
    bl_label = "Save image"

    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()

    def invoke(self, context, event):
        images = get_images_in_editors(context)
        for img in images:
            img.save()

        return{'FINISHED'}


# Enregistrer TOUTES LES images de Blender quelque soit le context
# Improved function than official "save_dirty()" function
class SaveImages(Operator):
    '''Save all images'''
    bl_idname = "wm.save_images"
    bl_label = "Save all images"

    def invoke(self, context, event):
        saved, withoutpath = 0, 0
        for img in bpy.data.images:
            try:
                image.save()
                saved += 1
            except:
                withoutpath += 1
                pass

        self.report({'WARNING'}, "Warning: " + str(withoutpath) + " without path and " + str(saved) + " image(s) saved!" )

        return {'FINISHED'}


class SaveExtPaintTexture(Operator):
    bl_idname = "object.save_ext_paint_texture"
    bl_label = "Save New Image"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def get_active_image(self, context):
        active_slot = context.object.active_material.paint_active_slot
        return context.object.active_material.texture_paint_images[active_slot]

    def path_exists(self, image_path):
        ipath = bpy.path.abspath(image_path)
        if os.path.exists(ipath):
            return True


    def invoke(self, context, event):
        slot_image = self.get_active_image(context)

        if slot_image.filepath == '' or not self.path_exists(slot_image.filepath):
            context.window_manager.fileselect_add(self)
        else:
            self.execute(context)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        slot_image = self.get_active_image(context)

        # old area stock
        area = bpy.context.area
        old_type, area.type = area.type, "IMAGE_EDITOR"    # Assez génial pour passer de l'image editor to 3Dview
        context.space_data.image = slot_image

        # function
        if slot_image.filepath == '':
            bpy.ops.image.save_as(filepath=self.filepath)
            self.report({'INFO'}, "{} saved!".format(slot_image.filepath))
        else:
            bpy.ops.image.save_dirty()

        # replace area type
        area.type = old_type

        return {"FINISHED"}




##############################################################################
# Outil pipette personnalisé en enlevant temporairement les masques!
class SampleColorMaskOff(Operator):
    '''Sample color without mask'''
    bl_idname = "paint.sample_color_custom"
    bl_label = "Sample color"

    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()            # bon operateur!

    def invoke(self, context, event):
        mesh = context.active_object.data
        paint_mask = mesh.use_paint_mask
        mesh.use_paint_mask = False
        bpy.ops.paint.sample_color('INVOKE_REGION_WIN')
        mesh.use_paint_mask = paint_mask

        return {'FINISHED'}


# Défilement de la texture peinte de l'objet ou d'une texture UV ou d'une grille couleur
class GridTexture(Operator):
    '''Toggle between current texture / UV / Colour grids'''    # EXCELLENT CODE !
    bl_idname = "paint.grid_texture"
    bl_label = "Grid texture"

    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()

    def execute(self, context):
        Egne = bpy.context.scene.render.engine
        if Egne == 'BLENDER_RENDER':
            objects = bpy.context.selected_objects
            meshes = [object.data for object in objects if object.type == 'MESH']  # génial code!
            if not meshes:
                self.report({'INFO'}, "Couldn't locate meshes to operate on")
                return {'CANCELLED'}

            tex_images = []                      # Stocke les images de texture
            for mesh in meshes:
                for mat in mesh.materials:
                    for tex in [ts.texture for ts in mat.texture_slots if ts and ts.texture.type=='IMAGE' and ts.texture.image]:  # Wonderful code!
                        tex_images.append([tex.name, tex.image.name])
            if not tex_images:
                self.report({'INFO'}, "Couldn't locate textures to operate on")
                return {'CANCELLED'}

            first_image = bpy.data.images[tex_images[0][1]]
            if "grid_texture_mode" in first_image:
                mode = first_image["grid_texture_mode"]
            else:
                mode = 1

            if mode == 1:
                # original textures, change to new UV grid
                width = max([bpy.data.images[image].size[0] for tex, image in tex_images])
                height = max([bpy.data.images[image].size[1] for tex, image in tex_images])
                new_image = bpy.data.images.new("temp_grid", width=width, height=height)

                new_image.generated_type = 'UV_GRID'
                new_image["grid_texture"] = tex_images  # ?
                new_image["grid_texture_mode"] = 2
                for tex, image in tex_images:
                    bpy.data.textures[tex].image = new_image
            elif mode == 2:
                # change from UV grid to Colour grid
                first_image.generated_type = 'COLOR_GRID'
                first_image["grid_texture_mode"] = 3
            elif mode == 3:
                # change from Colour grid back to original textures
                if "grid_texture" not in first_image:
                    first_image["grid_texture_mode"] = 1
                    self.report({'ERROR'}, "Couldn't retrieve original images")
                    return {'FINISHED'}
                tex_images = first_image["grid_texture"]
                for tex, image in tex_images:
                    if tex in bpy.data.textures and image in bpy.data.images:
                        bpy.data.textures[tex].image = bpy.data.images[image]
                bpy.data.images.remove(first_image)
        elif Egne =='CYCLES':
            # TODO!
            pass

        return {'FINISHED'}


# Augmente ou diminue la selection de point/arete/face
class ChangeSelection(Operator):
    '''Select more or less vertices/edges/faces, connected to the original selection'''
    bl_idname = "paint.change_selection"
    bl_label = "Change selection"

    # propriété du mode +/- de selection
    mode = bpy.props.EnumProperty(name="Mode",
                                  items = (("more", "More", "Select more vertices/edges/faces"),
                                           ("less", "Less", "Select less vertices/edges/faces")),
                                  description = "Choose whether the selection should be increased or decreased",
                                  default = 'more')

    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='EDIT')            # mise en mode édition
        if self.mode == 'more':                         # si mode = +
            bpy.ops.mesh.select_more()
        else:                                           # si mode = -
            bpy.ops.mesh.select_less()
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')   # retour en mode objet

        return {'FINISHED'}


class ToggleToolmodeOnScreen(Operator):
    '''Draw on the screen tools & blend mode'''
    bl_idname = "paint.toolmode_on_screen"
    bl_label = "Draw on screen the blend mode"

    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()

    def invoke(self, context, event):
        init_temp_props()
        wm = context.window_manager
        wm["ezp_toolmode_on_screen"] = True
        co2d = (event.mouse_region_x, event.mouse_region_y)
        wm["ezp_toolmode_brushloc"] = co2d

        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(\
                                                    toolmode_draw_callback,
                                                    args,
                                                    'WINDOW',
                                                    'POST_PIXEL')
        return {'FINISHED'}



class ToggleAddMultiply(Operator):
    '''Toggle between Add and Multiply blend modes'''
    bl_idname = "paint.toggle_add_multiply"
    bl_label = "Toggle add/multiply"

    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()

    def invoke(self, context, event):
        brush = context.tool_settings.image_paint.brush
        if brush.blend != 'MUL':
            brush.blend = 'MUL'
        else:
            brush.blend = 'ADD'

        wm = context.window_manager
        if "ezp_toolmode_on_screen" in wm:
            init_temp_props()
            co2d = (event.mouse_region_x, event.mouse_region_y)
            wm["ezp_toolmode_brushloc"] = co2d
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(\
                                                        toolmode_draw_callback,
                                                        args,
                                                        'WINDOW',
                                                        'POST_PIXEL')
        return {"FINISHED"}


class ToggleColorSoftLightScreen(Operator):
    '''Toggle between Color and Softlight and Screen blend modes'''
    bl_idname = "paint.toggle_color_soft_light_screen"
    bl_label = "Toggle color-softlight-screen"

    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()

    def invoke(self, context, event):
        brush = context.tool_settings.image_paint.brush
        if brush.blend != 'COLOR' and brush.blend != 'SOFTLIGHT':
            brush.blend = 'COLOR'
        elif brush.blend == 'COLOR':
            brush.blend = 'SOFTLIGHT'
        elif brush.blend == 'SOFTLIGHT':
            brush.blend = 'SCREEN'

        wm = context.window_manager
        if "ezp_toolmode_on_screen" in wm:
            init_temp_props()
            co2d = (event.mouse_region_x, event.mouse_region_y)
            wm["ezp_toolmode_brushloc"] = co2d
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(\
                                                        toolmode_draw_callback,
                                                        args,
                                                        'WINDOW',
                                                        'POST_PIXEL')
        return{'FINISHED'}


class ToggleAlphaMode(Operator):
    '''Toggle between Add Alpha and Erase Alpha blend modes'''
    bl_idname = "paint.toggle_alpha_mode"
    bl_label = "Toggle alpha mode"

    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()


    def invoke(self, context, event):
        brush = context.tool_settings.image_paint.brush
        if brush.blend != 'ERASE_ALPHA':
            brush.blend = 'ERASE_ALPHA'
        else:
            brush.blend = 'ADD_ALPHA'

        wm = context.window_manager
        if "ezp_toolmode_on_screen" in wm:
            init_temp_props()
            co2d = (event.mouse_region_x, event.mouse_region_y)
            wm["ezp_toolmode_brushloc"] = co2d
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(\
                                                        toolmode_draw_callback,
                                                        args,
                                                        'WINDOW',
                                                        'POST_PIXEL')
        return{'FINISHED'}


# init blend mode
class InitPaintBlend(Operator):
    '''Init to mix paint  mode'''
    bl_idname = "paint.init_blend_mode"
    bl_label = "Init paint blend mode"

    @classmethod
    def poll(cls, context):
        return bpy.ops.paint.image_paint.poll()

    def invoke(self, context, event):
        brush = context.tool_settings.image_paint.brush
        brush.blend = 'MIX'

        wm = context.window_manager
        if "ezp_toolmode_on_screen" in wm:
            init_temp_props()
            co2d = (event.mouse_region_x, event.mouse_region_y)
            wm["ezp_toolmode_brushloc"] = co2d
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(\
                                                        toolmode_draw_callback,
                                                        args,
                                                        'WINDOW',
                                                        'POST_PIXEL')
        return{'FINISHED'}



#-----------------------------------------------------------# in UV/image editor
# in UV/Image editor
class UVSelectSync(Operator):
    '''Toggle use_uv_select_sync in the UV editor'''
    bl_idname = "uv.uv_select_sync"
    bl_label = "UV Select Sync"

    @classmethod
    def poll(self, context):
        A = context.space_data.type == 'IMAGE_EDITOR'
        B = context.space_data.show_uvedit
        return A and B

    def execute(self, context):
        context.scene.tool_settings.use_uv_select_sync = not context.scene.tool_settings.use_uv_select_sync

        return {'FINISHED'}


# Active par defaut la fusion d'UVs entre iles du mesh in Paint mode
class AutoMergeUV(Operator):
    '''Have UV Merge enabled by default for merge actions'''
    bl_idname = "paint.auto_merge_uv"
    bl_label = "AutoMerge UV"

    def invoke(self, context, event):
        wm = context.window_manager
        if "ezp_automergeuv" not in wm:
            init_temp_props()
        wm["ezp_automergeuv"] = True

        km = bpy.context.window_manager.keyconfigs.default.keymaps['Mesh']
        for kmi in km.keymap_items:
            if kmi.idname == "mesh.merge":
                kmi.properties.uvs = True

        return {'FINISHED'}


# in UV/image editor
class ToggleImagePaint(Operator):
    '''Toggle image painting in the UV/Image editor'''
    bl_idname = "paint.toggle_image_paint"
    bl_label = "Image Painting"

    @classmethod
    def poll(cls, context):
        return(context.space_data.type == 'IMAGE_EDITOR')

    def invoke(self, context, event):
        if (context.space_data.mode == 'VIEW'):
            context.space_data.mode = 'PAINT'
        elif (context.space_data.mode == 'PAINT'):
            context.space_data.mode = 'MASK'
        elif (context.space_data.mode == 'MASK'):
            context.space_data.mode = 'VIEW'

        return {'FINISHED'}


#-----------------------------------------------------------#special Image Editor Popup

class DisplayActivePaintSlot(Operator):
    '''Display selected paint slot in new window'''
    bl_label = "Display active Slot"
    bl_idname = "paint.display_active_slot"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object.active_material.texture_paint_images

    def execute(self, context):
        if context.object.active_material.texture_paint_images:
            # Get the Image
            mat = bpy.context.object.active_material
            image = mat.texture_paint_images[mat.paint_active_slot]
            # Call user prefs window
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
            # Change area type
            area = context.window_manager.windows[-1].screen.areas[0]
            area.type = 'IMAGE_EDITOR'
            # Assign the Image
            context.area.spaces.active.image = image
            context.space_data.mode = 'PAINT'
        else:
            self.report({'INFO'}, "No active Slot")
        return {'FINISHED'}

#-----------------------------------------------------------#Modify Texture/mask image
def find_brush(context):                 # Trouver la brosse
    tool_settings = context.tool_settings
    if context.mode == 'SCULPT':
        return tool_settings.sculpt.brush
    elif context.mode == 'PAINT_TEXTURE':
        return tool_settings.image_paint.brush
    elif context.mode == 'PAINT_VERTEX':
        return tool_settings.vertex_paint.brush
    else:
        return None


class ModifyBrushTextures(Operator):
    '''Modify Active Brush Textures in new window'''
    bl_label = "Modify active Brush Texture"
    bl_idname = "paint.modify_brush_textures"
    bl_options = {'REGISTER', 'UNDO'}

    toggleType = bpy.props.BoolProperty(default=True)  # toogle texture or Mask menu

    @classmethod
    def poll(cls, context):
        brush = find_brush(context)
        return brush

    def execute(self, context):
        brush = find_brush(context)
        name_tex = brush.texture_slot.name
        name_mask = brush.mask_texture_slot.name


        if brush:
            # Get the brush Texture
            j = -1
            tux  = name_tex if self.toggleType else  name_mask
            for i in range(len(bpy.data.textures)):
                 if bpy.data.textures[i].name == tux:
                    j = i

            # Call user prefs window
            bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
            area = context.window_manager.windows[-1].screen.areas[0]
            area.type = 'IMAGE_EDITOR'
            if j != -1:
                context.area.spaces.active.image = bpy.data.images[j]
            context.space_data.mode = 'PAINT'
        else:
            self.report({'INFO'}, "No selected texture")
        return {'FINISHED'}

##########################################
#                                        #
#              New UI Menus              #
#                                        #
##########################################

# Ajouter dans UI > Menu Mesh  [MODE EDITION] => case à cocher "Automerge uv"
def menu_func(self, context):
    layout = self.layout
    wm = context.window_manager

    AME = "ezp_automergeuv"  in wm    # Astucieux! utilise "in"
    Icon = 'CHECKBOX_HLT' if AME else 'CHECKBOX_DEHLT'
    layout.operator("paint.auto_merge_uv", icon = Icon)


# Ajouter au menu des modes de Selection (ctrl Tab) [MODE EDITION] => les multi-selections
def menu_mesh_select_mode(self, context):
    layout = self.layout
    layout.separator()

    prop = layout.operator("wm.context_set_value", text="Vertex + Edge", icon='EDITMODE_HLT')
    prop.value = "(True, True, False)"
    prop.data_path = "tool_settings.mesh_select_mode"

    prop = layout.operator("wm.context_set_value", text="Vertex + Face", icon='ORTHO')
    prop.value = "(True, False, True)"
    prop.data_path = "tool_settings.mesh_select_mode"

    prop = layout.operator("wm.context_set_value", text="Edge + Face", icon='SNAP_FACE')
    prop.value = "(False, True, True)"
    prop.data_path = "tool_settings.mesh_select_mode"

    layout.separator()

    prop = layout.operator("wm.context_set_value", text="All", icon='OBJECT_DATAMODE')
    prop.value = "(True, True, True)"
    prop.data_path = "tool_settings.mesh_select_mode"


# Ajouter au menu aimantation (Shift S)[MODE OBJET]  => changer les origines de l'objet
def menu_snap(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("object.origin_set", text="Geometry to Origin")
    layout.operator("object.origin_set", text="Origin to Geometry").type = 'ORIGIN_GEOMETRY'
    layout.operator("object.origin_set", text="Origin to 3D Cursor").type = 'ORIGIN_CURSOR'


# Ajouter au menu SLOTS  =>  le bouton d'un UV Texture Editor.
def draw_display_slot_operator(self, context):
    if context.object.active_material.texture_paint_images:
        layout = self.layout
        row = layout.row(align=True)
        row.operator("paint.display_active_slot", text="UV Texture Editor", icon='IMAGE_COL')


##########################################
#                                        #
#             CLASSES LIST               #
#                                        #
##########################################

classes =   [BrushPopup,                    #brush panel (W) PAINT
            DisplayActivePaintSlot,         #2d Editor Popup for Active Paint Slot (Shift Alt W) PAINT
            TexturePopup,                   #textures et mask panel (Alt W) PAINT
            ProjectpaintPopup,              #images slots panel (Shift W) PAINT

            AddDefaultMatDiff,              #add a mat + defauft paint image (Shift ALt X) 3DVIEW
            DefaultMaterial,                #add a mat + 3 textures DIFF/SPEC/NORM (Ctrl Alt X) 3DVIEW
            MakeBrushImageTexture,          #Load a new image as paint texture (panel button)
            MakeBrushImageTextureMask,      #Load a new image as mask paint texture (panel button)
            MassLinkAppend,                 #add several linked objects from .blend folder (Ctrl F1) WINDOW

            ReloadImage,                    #reload active paint image (Alt R ) [IMAGE EDITOR]
            ReloadImages,                   #reload all paint images (Ctrl Alt R) [IMAGE EDITOR]

            SaveImages,                     #save all paint images (Ctrl Alt S) WINDOW => "save_dirty()" clearer!
            SaveExtPaintTexture,            #save externaly the new image in Cycles (panel button) [PAINT MODE]

            SampleColorMaskOff,             #Colorsample to paint immediately, different to colorsample S (OS + clic droit) PAINT
            GridTexture,                    #Toggle between paint image, UV image and grid image (G) PAINT [BI]
            ChangeSelection,                #Augmenter/diminuer les selections (alt + / alt -) [PAINT MODE] 3Dview

            ToggleToolmodeOnScreen,         #Toggle display the toolsmode options (Shift M) PAINT
            ToggleAddMultiply,              #Toggle Add/Multiply paint mode (D) PAINT
            ToggleColorSoftLightScreen,     #Toggle Color*softlight paint mode (shift D) PAINT
            ToggleAlphaMode,                #Toggle AddAlpha/EraseAlpha paint mode (A) PAINT
            InitPaintBlend,                 #Re-init default mix paint mode (Alt D) PAINT

            SaveImage,                      #save paint image (ALt S) [IMAGE EDITOR]
            UVSelectSync,             #Toggle the UVsync property ( Alt I ) UV_EDITOR
            AutoMergeUV,                    #UI > Menu Mesh  => "Automerge uv" [Shift I) [PAINT MODE]
            ToggleImagePaint]               #Cyclic image/paint/mask  mode (B) IMAGE_EDITOR
                                            # Toggle "Use mipmaps" ( Y ) [PAINT MODE] 3Dview
#legend:
#(--) =  No shortcut!

addon_keymaps = []

# kmi_defs entry: (identifier, key, action, CTRL, SHIFT, ALT, OSKEY , props, nice name)
# props entry: ,((property name, property value), (property name, property value), ...),....
kmi_defs = (
    # Save all images [Window] with: Ctrl + Alt S.
    (('Window', 'EMPTY'), "wm.save_images", 'S', 'PRESS', True, False, True, False, None, "Save dirty all images"),
    # Add linked assets from .blend files folders [Image Paint] with: Ctrl + F1.
    (('Window', 'EMPTY'), "wm.mass_link_append", 'F1', 'PRESS', True, False, False, False, None, "Add linked assets from .blend files folders"),
    # Brushes Popup [Image Paint] with: W.
    (('Image Paint', 'EMPTY'), "view3d.brush_popup", 'W', 'PRESS', False, False, False, False, None, "Brushes Popup"),
    # 2D Editor Popup with Active Paint Slot with Shift + Alt + W
    (('Image Paint', 'EMPTY'), "paint.display_active_slot", 'W', 'PRESS', False, True, True, False, None, "2D Editor Popup"),
    # Slots Popup [Image Paint] with: Shift + W.
    (('Image Paint', 'EMPTY'), "view3d.projectpaint", 'W', 'PRESS', False, True, False, False, None, "Slots Popup"),
    # Textures Popup [Image Paint] with: Alt + W.
    (('Image Paint', 'EMPTY'), "view3d.texture_popup", 'W', 'PRESS', False, False, True, False, None, "Textures Popup"),
    # Reload just the current image [Image Paint] with: Alt + R.
    (('Image Paint', 'EMPTY'), "paint.reload_image", 'R', 'PRESS', False, False, True, False, None, "Reload just the current image"),
    # Reload all images [Image Paint] with: Ctrl + Alt + R.
    (('Image Paint', 'EMPTY'), "paint.reload_images", 'R', 'PRESS', True, False, True, False, None, "Reload all images"),
    # Sample Colors Customly [Image Paint] with: Os key + RIGHTMOUSE
    (('Image Paint', 'EMPTY'), "paint.sample_color_custom", 'RIGHTMOUSE', 'PRESS', False, False, False, True, None, "Sample Colors Customly"),
    # Toggle paint/UVs/Grid textures [Image Paint] with: G.
    (('Image Paint', 'EMPTY'), "paint.grid_texture", 'G', 'PRESS', False, False, False, False, None, "Toggle paint/UVs/Grid textures"),
    # Toggle crease faces selections  [Image Paint] with: Ctrl +.
    (('Image Paint', 'EMPTY'), "paint.change_selection", 'NUMPAD_PLUS', 'PRESS', True, False, False, False, (('mode','more'),), "Toggle crease faces selections"),
    # Toggle decrease selections  [Image Paint] with: Ctrl -.
    (('Image Paint', 'EMPTY'), "paint.change_selection", 'NUMPAD_MINUS', 'PRESS', True, False, False, False, (('mode','less'),), "Toggle decrease faces selections"),
    # Display the tools & modes on screen [Image Paint] with: Shift + M.
    (('Image Paint', 'EMPTY'), "paint.toolmode_on_screen", 'M', 'PRESS', False, True, False, False, None, "Display the tools & modes on screen"),
    # Toggle add/multily modes [Image Paint] with: D.
    (('Image Paint', 'EMPTY'), "paint.toggle_add_multiply", 'D', 'PRESS', False, False, False, False, None, "Toggle add/multiply modes"),
    # Toggle color/soft light modes [Image Paint] with: Ctrl + D
    (('Image Paint', 'EMPTY'), "paint.toggle_color_soft_light_screen", 'D', 'PRESS', False, True, False, False, None, "Toggle color/soft light modes"),
    # Toggle Alpha modes [Image Paint] with: A.
    (('Image Paint', 'EMPTY'), "paint.toggle_alpha_mode", 'A', 'PRESS', False, False, False, False, None, "Toggle Alpha modes"),
    # Re-init Mix mode [Image Paint] with: Alt + D.
    (('Image Paint', 'EMPTY'), "paint.init_blend_mode", 'D', 'PRESS', False, False, True, False, None, "Re-init Mix mode"),
    # Save the current image [Image Editor] with: Alt + S.
    (('Image Generic', 'IMAGE_EDITOR'), "paint.save_image", 'S', 'PRESS', False, False, True, False, None, "Save the current image"),
    # Merge Auto UVs [Image Paint] with: Y.
    (('Image Paint', 'EMPTY'), "wm.context_toggle", 'I', 'PRESS', False, True, False, False, (('data_path','paint.auto_merge_uv'),), "Merge Auto UVs"),
    # Use Mipmaps [Image Paint] with: Shift + I.
    (('Image Paint', 'EMPTY'), "wm.context_toggle", 'Y', 'PRESS', False, False, False, False, (('data_path','user_preferences.system.use_mipmaps'),), "Use Mipmaps"),
    # Sync. 3Dview with UVs Editor [UV Editor] with: Alt + I.
    (('UV Editor', 'EMPTY'), "uv.uv_select_sync", 'I', 'PRESS', False, False, True, False, None, "Sync. 3Dview with UVs Editor")
)

def Register_Shortcuts():
    addon_keymaps.clear()
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        # for each kmi_def:
        for (spacetype, identifier, key, action, CTRL, SHIFT, ALT, OS_KEY, props, nicename) in kmi_defs:
            if spacetype[0] in bpy.context.window_manager.keyconfigs.addon.keymaps.keys():
                if spacetype[1] in kc.keymaps[spacetype[0]].space_type:
                    km = kc.keymaps[spacetype[0]]
            else:
                km = kc.keymaps.new(name = spacetype[0], space_type = spacetype[1])
            kmi = km.keymap_items.new(identifier, key, action, ctrl=CTRL, shift=SHIFT, alt=ALT, oskey=OS_KEY)
            if props:
                for prop, value in props:
                    setattr(kmi.properties, prop, value)
            addon_keymaps.append((km, kmi))


##########################################
#                                        #
# REGISTER FUNCTIONS                     #
#                                        #
##########################################

def register():
    init_temp_props()
    bpy.utils.register_module(__name__)

    # keymaps
    Register_Shortcuts()

    # add menu entries
    bpy.types.VIEW3D_MT_edit_mesh.prepend(menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_select_mode.append(menu_mesh_select_mode)
    bpy.types.VIEW3D_MT_snap.append(menu_snap)
    bpy.types.VIEW3D_PT_slots_projectpaint.prepend(draw_display_slot_operator)


def unregister():
    remove_temp_props()

    # keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    # menu entries
    bpy.types.VIEW3D_PT_slots_projectpaint.remove(draw_display_slot_operator)
    bpy.types.VIEW3D_MT_snap.remove(menu_snap)
    bpy.types.VIEW3D_MT_edit_mesh_select_mode.remove(menu_mesh_select_mode)
    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)

    # Remove module
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
