'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Dieses Programm ist Freie Software: Sie können es unter den Bedingungen
    der GNU General Public License, wie von der Free Software Foundation,
    Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren
    veröffentlichten Version, weiter verteilen und/oder modifizieren.

    Dieses Programm wird in der Hoffnung bereitgestellt, dass es nützlich sein wird, jedoch
    OHNE JEDE GEWÄHR,; sogar ohne die implizite
    Gewähr der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
    Siehe die GNU General Public License für weitere Einzelheiten.

    Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
    Programm erhalten haben. Wenn nicht, siehe <https://www.gnu.org/licenses/>.
'''
bl_info = {
    "name": "unregis AddOn",
    "author": "unregi Resident",
    "description": "Tools for merging and simplifying multiple objects to fit OpenSim / sl",
    "version": (0, 2),
    "category": "Learnbgame",
    "blender": (2, 80, 0),
}

import bpy
import os
import bpy.utils.previews
icons_dict = {}

if bpy.app.version < (2, 80):
    from .unregis_addon_279 import *
else:
    from .unregis_addon_280 import *

def register_icons(icons_dict):
    pcoll = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    for f in os.listdir(icons_dir):
        name, ext = os.path.splitext(f)
        if ext == ".png":
            pcoll.load(name, os.path.join(icons_dir, f), 'IMAGE')
            icons_dict[name] = {"icon_value": pcoll[name].icon_id}
    icons_dict["pcoll"] = pcoll

def unregister_icons(icons_dict):
    bpy.utils.previews.remove(icons_dict["pcoll"])
    icons_dict.clear()

cor_unregister = unregister
def unregister():
    cor_unregister()
    unregister_icons(icons_dict)

cor_register = register
def register():
    try:
        register_icons(icons_dict)
        cor_register()
    except Exception as e:
        try:
            unregister()
        except:
            pass
        raise e

