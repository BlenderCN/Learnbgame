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
#   the Free Software Foundation Inc.
#   51 Franklin Street, Fifth Floor
#   Boston, MA 02110-1301, USA
#
# or go online at: http://www.gnu.org/licenses/ to view license options.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Text Appeal",
    "author": "zeffii",
    "version": (0, 1, 0),
    "blender": (2, 6, 1),
    "location": "TextEditor - multiple places",
    "description": "Adds eval and chroma button.",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


if "bpy" in locals():
    import imp
    imp.reload(text_editor_chroma)
    imp.reload(text_editor_eval)
    imp.reload(text_editor_searchpydocs)
    imp.reload(text_editor_searchbpydocs)
    imp.reload(text_editor_searchblenderscripting)
    imp.reload(text_editor_searchstackoverflow)
else:
    from text_editor_extras import text_editor_chroma
    from text_editor_extras import text_editor_eval
    from text_editor_extras import text_editor_searchpydocs
    from text_editor_extras import text_editor_searchbpydocs
    from text_editor_extras import text_editor_searchblenderscripting
    from text_editor_extras import text_editor_searchstackoverflow

import bpy


def draw_item(self, context):
    layout = self.layout
    layout.operator("txt.set_text_prefs", icon='COLOR')


class BasicTextMenu(bpy.types.Menu):
    bl_idname = "TEXT_MT_search_menu"
    bl_label = "Search"

    @classmethod
    def poll(self, context):
        text = bpy.context.edit_text
        return has_selection(text)

    def draw(self, context):
        layout = self.layout
        layout.operator("txt.eval_selected_text", text='Eval Selected')
        layout.operator("txt.search_pydocs", text='Search Pydocs')
        layout.operator("txt.search_bpydocs", text='Search bpy docs')
        layout.operator("txt.search_blenderscripting", text='Search bscripting')
        layout.operator("txt.search_stack", text='Search stack overflow')

def has_selection(text):
    return not (text.select_end_line == text.current_line and \
    text.current_character == text.select_end_character)


# Sets the keymap to Ctrl + I for inside the text editor, will only
# appear if a selection is set.
if True:
    wm = bpy.context.window_manager
    km = wm.keyconfigs.default.keymaps['Text']
    new_shortcut = km.keymap_items.new('wm.call_menu', 'I', 'PRESS', ctrl=True)
    new_shortcut.properties.name = 'TEXT_MT_search_menu'

def register():
    bpy.utils.register_module(__name__)
    bpy.types.TEXT_HT_header.prepend(draw_item)
     

def unregister():
    bpy.utils.unregister_module(__name__)    
    bpy.types.TEXT_HT_header.remove(draw_item)

    
if __name__ == "__main__":
    register()