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
from . import korlib

game_versions = [("pvPrime", "Ages Beyond Myst (63.11)", "Targets the original Uru (Live) game"),
                 ("pvPots", "Path of the Shell (63.12)", "Targets the most recent offline expansion pack"),
                 ("pvMoul", "Myst Online: Uru Live (70)", "Targets the most recent online game")]

class PlasmaGame(bpy.types.PropertyGroup):
    name = StringProperty(name="Name",
                          description="Name of the Plasma Game",
                          options=set())
    path = StringProperty(name="Path",
                          description="Path to this Plasma Game",
                          options=set())
    version = EnumProperty(name="Version",
                           description="Plasma version of this game",
                           items=game_versions,
                           options=set())


class KormanAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    games = CollectionProperty(type=PlasmaGame)
    active_game_index = IntProperty(options={"SKIP_SAVE"})

    def _check_py22_exe(self, context):
        if self._ensure_abspath((2, 2)):
            self._check_python((2, 2))
    def _check_py23_exe(self, context):
        if self._ensure_abspath((2, 3)):
            self._check_python((2, 3))
    def _check_py27_exe(self, context):
        if self._ensure_abspath((2, 7)):
            self._check_python((2, 7))

    python22_executable = StringProperty(name="Python 2.2",
                                         description="Path to the Python 2.2 executable",
                                         options=set(),
                                         subtype="FILE_PATH",
                                         update=_check_py22_exe)
    python23_executable = StringProperty(name="Python 2.3",
                                         description="Path to the Python 2.3 executable",
                                         options=set(),
                                         subtype="FILE_PATH",
                                         update=_check_py23_exe)
    python27_executable = StringProperty(name="Python 2.7",
                                         description="Path to the Python 2.7 executable",
                                         options=set(),
                                         subtype="FILE_PATH",
                                         update=_check_py27_exe)

    def _validate_py_exes(self):
        if not self.is_property_set("python22_valid"):
            self._check_python((2, 2))
        if not self.is_property_set("python23_valid"):
            self._check_python((2, 3))
        if not self.is_property_set("python27_valid"):
            self._check_python((2, 7))
        return True

    # Internal error states
    python22_valid = BoolProperty(options={"HIDDEN", "SKIP_SAVE"})
    python23_valid = BoolProperty(options={"HIDDEN", "SKIP_SAVE"})
    python27_valid = BoolProperty(options={"HIDDEN", "SKIP_SAVE"})
    python_validated = BoolProperty(get=_validate_py_exes, options={"HIDDEN", "SKIP_SAVE"})

    def _check_python(self, py_version):
        py_exe = getattr(self, "python{}{}_executable".format(*py_version))
        if py_exe:
            valid = korlib.verify_python(py_version, py_exe)
        else:
            valid = True
        setattr(self, "python{}{}_valid".format(*py_version), valid)

    def _ensure_abspath(self, py_version):
        attr = "python{}{}_executable".format(*py_version)
        path = getattr(self, attr)
        if path.startswith("//"):
            setattr(self, attr, bpy.path.abspath(path))
            return False
        return True

    def draw(self, context):
        layout = self.layout
        split = layout.split()
        main_col = split.column()

        main_col.label("Plasma Games:")
        row = main_col.row()
        row.template_list("PlasmaGameListRW", "games", self, "games", self,
                          "active_game_index", rows=3)
        col = row.column(align=True)
        col.operator("world.plasma_game_add", icon="ZOOMIN", text="")
        col.operator("world.plasma_game_remove", icon="ZOOMOUT", text="")
        col.operator("world.plasma_game_convert", icon="IMPORT", text="")

        # Game Properties
        active_game_index = self.active_game_index
        if bool(self.games) and active_game_index < len(self.games):
            active_game = self.games[active_game_index]

            col = split.column()
            col.label("Game Configuration:")
            box = col.box().column()

            box.prop(active_game, "path", emboss=False)
            box.prop(active_game, "version")
            box.separator()

            row = box.row(align=True)
            op = row.operator("world.plasma_game_add", icon="FILE_FOLDER", text="Change Path")
            op.filepath = active_game.path
            op.game_index = active_game_index

        # Python Installs
        assert self.python_validated
        col = layout.column()
        col.label("Python Executables:")
        col.alert = not self.python22_valid
        col.prop(self, "python22_executable")
        col.alert = not self.python23_valid
        col.prop(self, "python23_executable")
        col.alert = not self.python27_valid
        col.prop(self, "python27_executable")

    @classmethod
    def register(cls):
        # Register the old-timey per-world Plasma Games for use in the conversion
        # operator. What fun. I guess....
        from .properties.prop_world import PlasmaGames
        PlasmaGames.games = CollectionProperty(type=PlasmaGame)
