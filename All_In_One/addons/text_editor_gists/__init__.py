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
    "name": "Gist IO",
    "author": "Dealga McArdle",
    "version": (0, 1, 0),
    "blender": (2, 6, 4),
    "location": "TextEditor - toolbar",
    "description": "Import downloads gist by ID as new text item, export copies gist url to clipboard.",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}


if "bpy" in locals():
    import imp
    imp.reload(gist_import_addon)
    imp.reload(gist_upload_addon)
else:
    from . import gist_import_addon
    from . import gist_upload_addon

import bpy
from bpy.props import StringProperty


def initSceneGistProperties(scn):
 
    bpy.types.Scene.gist_id_property = StringProperty(
        name = "Gist ID",
        description = "Github Gist ID to download as new internal file",
        default = ""
    )  

    bpy.types.Scene.gist_name = StringProperty(
        name = "Name",
        description = "Name for Gist",
        default = ".py"
    )

    bpy.types.Scene.gist_description = StringProperty(
        name = "Description",
        description = "Description for Gist",
        default = ""
    )

initSceneGistProperties(bpy.context.scene)

gist_classes = (
    gist_import_addon.GistDownloadPanel,
    gist_import_addon.GistDownloadButton,
    gist_upload_addon.GistUploadPanel,
    gist_upload_addon.GistUploadButton
)    


def register():
    for i in gist_classes:
        bpy.utils.register_class(i)


def unregister():
    for i in gist_classes:
        bpy.utils.unregister_class(i)

    
if __name__ == "__main__":
    #initSceneGistProperties(bpy.context.scene)
    register()
