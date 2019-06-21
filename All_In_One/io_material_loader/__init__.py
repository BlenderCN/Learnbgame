# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you may redistribute it, and/or
# modify it, under the terms of the GNU General Public License
# as published by the Free Software Foundation - either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, write to:
#
#	the Free Software Foundation Inc.
#	51 Franklin Street, Fifth Floor
#	Boston, MA 02110-1301, USA
#
# or go online at: http://www.gnu.org/licenses/ to view license options.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Tiny Library",
    "author": "zeffii",
    "version": (0, 6, 0),
    "blender": (2, 6, 1),
    "location": "NodeView > HeaderBar > Materials",
    "description": "Adds a material from your library.",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/Add_Material_Library_light",
    "tracker_url": "https://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=234",
    "category": "Learnbgame",
}



if "bpy" in locals():
    import imp
    imp.reload(prototyper)
else:
    from io_material_loader import prototyper

import bpy


def draw_item(self, context):
    layout = self.layout
    layout.menu(prototyper.CustomMenu.bl_idname)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.NODE_HT_header.append(draw_item)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.NODE_HT_header.remove(draw_item)
    
if __name__ == "__main__":
    register()
