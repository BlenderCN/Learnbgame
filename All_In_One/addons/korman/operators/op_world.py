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
from bpy.props import *
from pathlib import Path

class AgeOperator:
    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == "PLASMA_GAME"


class GameAddOperator(AgeOperator, bpy.types.Operator):
    bl_idname = "world.plasma_game_add"
    bl_label = "Add Plasma Game"

    filepath = StringProperty(subtype="DIR_PATH")
    directory = BoolProperty(default=True, options={"HIDDEN"})
    game_index = IntProperty(default=-1, options={"HIDDEN"})

    def execute(self, context):
        prefs = context.user_preferences.addons["korman"].preferences

        # First, verify this is a valid Uru directory...
        path = Path(self.filepath)

        # Blendsucks likes to tack filenames onto our doggone directories...
        if not path.is_dir():
            path = path.parent
        if not ((path / "UruExplorer.exe").is_file() or (path / "plClient.exe").is_file()):
            self.report({"ERROR"}, "The selected directory is not a copy of URU.")
            return {"CANCELLED"}

        # New game?
        new_game = self.game_index == -1
        if new_game:
            prefs.active_game_index = len(prefs.games)
            game = prefs.games.add()
        else:
            game = prefs.games[self.game_index]

        # Setup game...
        game.path = str(path)
        if (path / "cypython22.dll").is_file():
            game.version = "pvPots"
        else:
            game.version = "pvMoul"
        game.name = path.name

        return {"FINISHED"}


    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class GameConvertOperator(AgeOperator, bpy.types.Operator):
    bl_idname = "world.plasma_game_convert"
    bl_label = "This will save your User Preferences file!"
    bl_description = "Load old per-file Plasma Games into your user preferences"

    def draw(self, context):
        self.layout.label("test")

    def execute(self, context):
        prefs = context.user_preferences.addons["korman"].preferences
        w = context.scene.world

        for old_game in w.plasma_games.games:
            # don't add dupe games
            match = next((i for i in prefs.games if i.path == old_game.path), None)
            if match is not None:
                continue

            new_game = prefs.games.add()
            new_game.name = old_game.name
            new_game.path = old_game.path
            new_game.version = old_game.version

        w.plasma_games.games.clear()
        bpy.ops.wm.save_userpref()
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    @classmethod
    def poll(cls, context):
        return super().poll(context) and bool(context.scene.world.plasma_games.games)


class GameRemoveOperator(AgeOperator, bpy.types.Operator):
    bl_idname = "world.plasma_game_remove"
    bl_label = "Remove Plasma Game"

    def execute(self, context):
        prefs = context.user_preferences.addons["korman"].preferences

        if prefs.active_game_index >= len(prefs.games):
            return {"CANCELLED"}
        prefs.games.remove(prefs.active_game_index)
        prefs.active_game_index = max(prefs.active_game_index - 1, -1)
        return {"FINISHED"}


class PageAddOperator(AgeOperator, bpy.types.Operator):
    bl_idname = "world.plasma_page_add"
    bl_label = "Add Page"
    bl_description = "Adds a new Plasma Registry Page"

    def execute(self, context):
        w = context.world
        if w:
            age = w.plasma_age
            page = age.pages.add()

            # Find the first non-zero ID and suggest that.
            suffixes = {p.seq_suffix for p in age.pages}
            if suffixes:
                test = set(range(min(suffixes), max(suffixes)))
                missing = test - suffixes
                try:
                    suffix = missing.pop()
                except KeyError:
                    suffix = max(suffixes) + 1
                page.make_default_name(suffix)
            else:
                # Page 0 is a magic "catch-all" page. The user *may* define it
                # if he wants. If he doesn't, we'll defer it until export time
                page.make_default_name(1)

            # Finally, select the new page
            age.active_page_index = len(age.pages) - 1
            return {"FINISHED"}
        else:
            return {"CANCELLED"}


class PageRemoveOperator(AgeOperator, bpy.types.Operator):
    bl_idname = "world.plasma_page_remove"
    bl_label = "Remove Page"
    bl_description = "Removes the selected Plasma Registry Page"

    def execute(self, context):
        w = context.world
        if w:
            age = w.plasma_age
            if age.active_page_index >= len(age.pages):
                return {"CANCELLED"}
            page = age.pages[age.active_page_index]

            # Need to reassign objects in this page to the default page
            defpg = ""
            for i in age.pages:
                if i.seq_suffix == 0:
                    defpg = i.name
                    break
            for o in bpy.data.objects:
                if o.plasma_object.page == page.name:
                    o.plasma_object.page = defpg
            age.pages.remove(age.active_page_index)
            return {"FINISHED"}
        else:
            return {"CANCELLED"}
