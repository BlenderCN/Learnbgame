#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from pathlib import Path

from .. import korlib


class AgeButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"

    @classmethod
    def poll(cls, context):
        return context.world and context.scene.render.engine == "PLASMA_GAME"


class PlasmaGameHelper:
    @property
    def active_game(self):
        games = bpy.context.world.plasma_games
        prefs = bpy.context.user_preferences.addons["korman"].preferences
        active_game_index = games.active_game_index
        if active_game_index < len(prefs.games):
            return prefs.games[active_game_index]
        else:
            return None

    def format_path(self, dirname="dat", ext=".age"):
        active_game = self.active_game
        if active_game is None:
            return ""
        age_name = bpy.context.world.plasma_age.age_name
        return str((Path(active_game.path) / dirname / age_name).with_suffix(ext))

    @property
    def legal_game(self):
        if self.active_game is not None:
            return bool(bpy.context.world.plasma_age.age_name.strip())


class PlasmaGameExportMenu(PlasmaGameHelper, bpy.types.Menu):
    bl_label = "Plasma Export Menu"

    def draw(self, context):
        layout = self.layout
        age_name = context.world.plasma_age.age_name
        active_game = self.active_game
        legal_game = self.legal_game

        # Localization
        row = layout.row()
        row.operator_context = "EXEC_DEFAULT"
        row.enabled = legal_game
        op = row.operator("export.plasma_loc", icon="FILE_SCRIPT")
        if active_game is not None:
            op.filepath = active_game.path
            op.version = active_game.version

        # Python
        row = layout.row()
        row.operator_context = "EXEC_DEFAULT"
        row.enabled = legal_game and active_game.version != "pvMoul"
        op = row.operator("export.plasma_pak", icon="FILE_SCRIPT")
        op.filepath = self.format_path("Python", ".pak")
        if active_game is not None:
            op.version = active_game.version


class PlasmaGamePanel(AgeButtonsPanel, PlasmaGameHelper, bpy.types.Panel):
    bl_label = "Plasma Games"

    def draw(self, context):
        layout = self.layout
        prefs = context.user_preferences.addons["korman"].preferences
        games = context.world.plasma_games
        age = context.world.plasma_age
        active_game = self.active_game
        legal_game = self.legal_game

        row = layout.row()
        # Remember: game storage moved to addon preferences!
        row.template_list("PlasmaGameListRO", "games", prefs, "games", games,
                          "active_game_index", rows=2)
        row.operator("ui.korman_open_prefs", icon="PREFERENCES", text="")

        layout.separator()
        row = layout.row(align=True)

        # Export Age
        row.operator_context = "EXEC_DEFAULT"
        row.enabled = legal_game
        op = row.operator("export.plasma_age", icon="EXPORT")
        if active_game is not None:
            op.dat_only = False
            op.filepath = self.format_path()
            op.version = active_game.version

        # Package Age
        row = row.row(align=True)
        row.enabled = legal_game
        row.operator_context = "INVOKE_DEFAULT"
        op = row.operator("export.plasma_age", icon="PACKAGE", text="Package Age")
        op.dat_only = False
        op.filepath = "{}.zip".format(age.age_name)
        if active_game is not None:
            op.version = active_game.version

        # Special Menu
        row = row.row(align=True)
        row.menu("PlasmaGameExportMenu", icon='DOWNARROW_HLT', text="")


class PlasmaGameListRO(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0):
        layout.label(item.name, icon="BOOKMARKS")

class PlasmaGameListRW(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0):
        layout.prop(item, "name", text="", emboss=False, icon="BOOKMARKS")


class PlasmaPageList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0):
        layout.prop(item, "name", text="", emboss=False, icon="BOOKMARKS")
        layout.prop(item, "enabled", text="")


class PlasmaAgePanel(AgeButtonsPanel, bpy.types.Panel):
    bl_label = "Plasma Age"

    def draw(self, context):
        layout = self.layout
        age = context.world.plasma_age

        # We want a list of pages and an editor below that
        row = layout.row()
        row.template_list("PlasmaPageList", "pages", age, "pages", age,
                          "active_page_index", rows=2)
        col = row.column(align=True)
        col.operator("world.plasma_page_add", icon="ZOOMIN", text="")
        col.operator("world.plasma_page_remove", icon="ZOOMOUT", text="")

        # Page Properties
        if age.active_page_index < len(age.pages):
            active_page = age.pages[age.active_page_index]

            layout.separator()
            box = layout.box()
            split = box.split()

            col = split.column()
            col.label("Page Flags:")
            col.prop(active_page, "auto_load")
            col.prop(active_page, "local_only")

            col = split.column()
            col.label("Page Info:")
            col.prop(active_page, "name", text="")
            col.prop(active_page, "seq_suffix")
            col.prop_menu_enum(active_page, "version")

        # Age Names should really be legal Python 2.x identifiers for AgeSDLHooks
        legal_identifier = korlib.is_legal_python2_identifier(age.age_name)

        # Core settings
        layout.separator()
        split = layout.split()

        col = split.column()
        col.label("Age Time:")
        col.prop(age, "start_time", text="Epoch")
        col.prop(age, "day_length")

        col = split.column()
        col.label("Age Settings:")
        col.prop(age, "seq_prefix", text="ID")
        col.alert = not legal_identifier or '_' in age.age_name
        col.prop(age, "age_name", text="")

        # Display a hint if the identifier is illegal
        if not legal_identifier:
            if korlib.is_python_keyword(age.age_name):
                layout.label(text="Ages should not be named the same as a Python keyword", icon="ERROR")
            elif age.age_sdl:
                fixed_identifier = korlib.replace_python2_identifier(age.age_name)
                layout.label(text="Age's SDL will use the name '{}'".format(fixed_identifier), icon="ERROR")

        layout.separator()
        split = layout.split()

        col = split.column()
        col.label("Export Settings:")
        col.enabled = korlib.ConsoleToggler.is_platform_supported()
        col.prop(age, "verbose")
        col.prop(age, "show_console")

        col = split.column()
        col.label("Plasma Settings:")
        col.prop(age, "age_sdl")
        col.prop(age, "use_texture_page")

        layout.separator()
        layout.prop(age, "envmap_method")
        layout.prop(age, "lighting_method")
        layout.prop(age, "python_method")
        layout.prop(age, "texcache_method")


class PlasmaEnvironmentPanel(AgeButtonsPanel, bpy.types.Panel):
    bl_label = "Plasma Environment"

    def draw(self, context):
        layout = self.layout
        fni = context.world.plasma_fni

        # basic colors
        split = layout.split()
        col = split.column()
        col.prop(fni, "fog_color")
        col = split.column()
        col.prop(fni, "clear_color")

        split = layout.split()
        col = split.column()
        col.label("Fog Settings:")
        col.prop_menu_enum(fni, "fog_method")
        col.separator()
        if fni.fog_method == "linear":
            col.prop(fni, "fog_start")
        if fni.fog_method != "none":
            col.prop(fni, "fog_end")
            col.prop(fni, "fog_density")

        col = split.column()
        col.label("Draw Settings:")
        col.prop(fni, "yon", text="Clipping")
