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
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "ImageStripConsistency",
    "author": "Jiri Kuba",
    "version": (0, 9, 2),
    "blender": (2, 79, 0),
    "location": "Sequencer > Strip > Image strips consistency",
    "description": "Check image strip file name consistency",
    "wiki_url": "https://github.com/jiriKuba/blender.addons.ImageStripConsistency/blob/master/README.md",
    "tracker_url": "https://github.com/jiriKuba/blender.addons.ImageStripConsistency",
    "support": "COMMUNITY",
    "category": "Learnbgame",
}

import re
import bpy

class MessageOperator(bpy.types.Operator):
    bl_idname = "prompt.message"
    bl_label = "Message"
    message = bpy.props.StringProperty()
 
    def execute(self, context):
        self.report(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=460, height=200)
 
    def draw(self, context):
        self.layout.label("Image strips file name consistency result:")
        row = self.layout.row()
        row.label(text=self.message)

class ImageStripConsistencyAddon(bpy.types.Operator):
    """Check image strip file name consistency"""
    bl_idname = "sequence.image_strip_consistency"
    bl_label = "Image strips consistency"
    bl_options = {'REGISTER'} 

    def execute(self, context):
        for scene in bpy.data.scenes: 
            if scene.sequence_editor is not None:
                strips = scene.sequence_editor.sequences_all
                if strips is not None:
                    for strip in strips:
                        if strip.type == 'IMAGE':
                            is_strip_valid, image_number_should_be = isImageStripConsistent(strip)
                            if is_strip_valid is not True:
                                bpy.ops.prompt.message('INVOKE_DEFAULT', message = 'Inconsistency detected in strip named %s. Expected image with number %d.' % (strip.name, image_number_should_be))
                                return {'FINISHED'}

        bpy.ops.prompt.message('INVOKE_DEFAULT', message = "No inconsistency detected.")
            
        return {'FINISHED'}


def isImageStripConsistent(strip):
    last_number = None
    for ele in strip.elements:
        number_in_filename = re.findall(r'\d+', ele.filename)
        number_in_filename_count = len(number_in_filename)
        
        if number_in_filename_count is 0:
            continue #no number in filename = skip
        
        current_number = int(number_in_filename[number_in_filename_count - 1])
        
        if last_number is not None:
            current_number_should_be = last_number + 1
            if current_number is not current_number_should_be:
                return False, current_number_should_be
            
        last_number = current_number

    return True, None
 
def sequencer_strip_menu_func(self, context):
    self.layout.operator(ImageStripConsistencyAddon.bl_idname)


def register():
    bpy.utils.register_class(MessageOperator)
    bpy.utils.register_class(ImageStripConsistencyAddon)

    bpy.types.SEQUENCER_MT_strip.prepend(sequencer_strip_menu_func)

def unregister():
    bpy.utils.unregister_class(MessageOperator)
    bpy.utils.unregister_class(ImageStripConsistencyAddon)

    bpy.types.SEQUENCER_MT_strip.remove(sequencer_strip_menu_func)

if __name__ == "__main__":
    register()
