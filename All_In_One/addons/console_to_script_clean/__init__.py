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
    "name": "Console History",
    "author": "Dealga McArdle",
    "version": (0, 1, 0),
    "blender": (2, 6, 4),
    "location": "Console - Copy History",
    "description": "Adds Copy History options to Console button.",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}
    
import bpy

def sanitize_console_dump(tm):


    def of_interest(line):
        return not starts_with_token(line) and not incomplete(line)

    
    def starts_with_token(line):
        tokens = "#~","#!"
        for token in tokens:
            if line.startswith(token):
                return True
        return False
    
    
    def incomplete(line):
        return line.endswith('.')
    
   
    tm = tm.split('\n')
    cleaner = [line for line in tm if of_interest(line)]
    return'\n'.join(cleaner)


class AddToClipboard(bpy.types.Operator):
    bl_label = ""
    bl_idname = "console.copy_history_n"
    
    def execute(self, context):
        bpy.ops.console.copy_as_script()
        tm = context.window_manager.clipboard
        context.window_manager.clipboard = sanitize_console_dump(tm)
        return {'FINISHED'}


def history_menu(self, context):
    layout = self.layout
    layout.operator("console.copy_history_n", text='Copy History (Clean)')    
    

def register():
    bpy.utils.register_module(__name__)
    bpy.types.CONSOLE_MT_console.prepend(history_menu)    

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.CONSOLE_MT_console.remove(history_menu)
    
if __name__ == "__main__":
    register()
    
    