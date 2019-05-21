
#
#  Copyright (c) 2018 Shane Ambler
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# made in response to https://blender.stackexchange.com/q/106986/935
# provide a way to align strips to edge of frame

bl_info = {
    'name': 'Sequencer Alignment',
    'author': 'sambler',
    'version': (1, 2),
    'blender': (2, 80, 0),
    'location': 'Video Sequencer',
    'description': 'Align sequencer strips.',
    'wiki_url': 'https://github.com/sambler/addonsByMe/blob/master/sequencer_alignment.py',
    'tracker_url': 'https://github.com/sambler/addonsByMe/issues',
    'category': 'Sequencer',
    }

import bpy

alignment = [
    ('TOP', 'Top', 'Align top edges', 1),
    ('LEFT', 'Left', 'Align left edges', 2),
    ('BOTTOM', 'Bottom', 'Align bottom edges', 3),
    ('RIGHT', 'Right', 'Align right edges', 4),
    ('VERT','Centre Height','Align vertical centre',5),
    ('HORIZ','Centre Width','Align horizontal centre',6),
    ]

class VSEStripAlignment(bpy.types.Operator):
    bl_idname = 'sequencer.alignment'
    bl_label = 'Align sequencer strips.'
    bl_options = {'REGISTER','UNDO'}

    direction : bpy.props.EnumProperty(items=alignment)

    def execute(self, context):
        scene = context.scene
        if scene.vse_align_active:
            active_strip = scene.sequence_editor.active_strip
            ast = active_strip.transform
            ase = active_strip.strip_elem_from_frame(active_strip.frame_start)
            asw = ase.orig_width
            ash = ase.orig_height
            for s in context.selected_sequences:
                if s == active_strip: continue
                s.use_translation = True
                st = s.transform
                se = s.strip_elem_from_frame(s.frame_start)
                if self.direction == 'TOP':
                    st.offset_y = ast.offset_y + ash
                elif self.direction == 'BOTTOM':
                    st.offset_y = ast.offset_y - se.orig_height
                elif self.direction == 'LEFT':
                    st.offset_x = ast.offset_x - se.orig_width
                elif self.direction == 'RIGHT':
                    st.offset_x = ast.offset_x + asw
                elif self.direction == 'VERT':
                    st.offset_y = ast.offset_y + (ash/2) - (se.orig_height/2)
                elif self.direction == 'HORIZ':
                    st.offset_x = ast.offset_x + (asw/2) - (se.orig_width/2)

                if s.use_crop:
                    if self.direction == 'TOP':
                        st.offset_y += s.crop.min_y + s.crop.max_y
                    if self.direction == 'RIGHT':
                        st.offset_x += s.crop.min_x + s.crop.max_x
                    if self.direction == 'VERT':
                        st.offset_y += (s.crop.min_y + s.crop.max_y) / 2
                    if self.direction == 'HORIZ':
                        st.offset_x += (s.crop.min_x + s.crop.max_x) / 2
        else:
            width = scene.render.resolution_x
            height = scene.render.resolution_y
            for s in context.selected_sequences:
                s.use_translation = True
                st = s.transform
                se = s.strip_elem_from_frame(s.frame_start)
                if self.direction == 'TOP':
                    st.offset_y = height - se.orig_height
                elif self.direction == 'BOTTOM':
                    st.offset_y = 0
                elif self.direction == 'LEFT':
                    st.offset_x = 0
                elif self.direction == 'RIGHT':
                    st.offset_x = width - se.orig_width
                elif self.direction == 'VERT':
                    st.offset_y = (height/2) - (se.orig_height/2)
                elif self.direction == 'HORIZ':
                    st.offset_x = (width/2) - (se.orig_width/2)

                if s.use_crop:
                    if self.direction == 'TOP':
                        st.offset_y += s.crop.min_y + s.crop.max_y
                    if self.direction == 'RIGHT':
                        st.offset_x += s.crop.min_x + s.crop.max_x
                    if self.direction == 'VERT':
                        st.offset_y += (s.crop.min_y + s.crop.max_y) / 2
                    if self.direction == 'HORIZ':
                        st.offset_x += (s.crop.min_x + s.crop.max_x) / 2

        return {'FINISHED'}


class VSEAlignmentPanel(bpy.types.Panel):
    bl_idname = 'SEQUENCER_PT_Alignment'
    bl_label = 'Align Strips'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        row = self.layout.row()
        row.prop(context.scene, 'vse_align_active', text='Align to active.')
        if context.scene.vse_align_active and context.scene.sequence_editor.active_strip:
            row = self.layout.row()
            row.label(text=context.scene.sequence_editor.active_strip.name)
        row = self.layout.row()
        row.operator(VSEStripAlignment.bl_idname, text='Top').direction = 'TOP'
        row = self.layout.row()
        row.operator(VSEStripAlignment.bl_idname, text='Left').direction = 'LEFT'
        row.operator(VSEStripAlignment.bl_idname, text='Right').direction = 'RIGHT'
        row = self.layout.row()
        row.operator(VSEStripAlignment.bl_idname, text='Bottom').direction = 'BOTTOM'
        row = self.layout.row()
        row.alignment = 'CENTER'
        row.label(text='Centre')
        row = self.layout.row()
        row.operator(VSEStripAlignment.bl_idname, text='^Height^').direction = 'VERT'
        row = self.layout.row()
        row.operator(VSEStripAlignment.bl_idname, text='<-Width->').direction = 'HORIZ'

def register():
    bpy.types.Scene.vse_align_active = bpy.props.BoolProperty()
    bpy.utils.register_class(VSEStripAlignment)
    bpy.utils.register_class(VSEAlignmentPanel)

def unregister():
    bpy.utils.unregister_class(VSEAlignmentPanel)
    bpy.utils.unregister_class(VSEStripAlignment)
    del bpy.types.Scene.vse_align_active

if __name__ == '__main__':
    register()
