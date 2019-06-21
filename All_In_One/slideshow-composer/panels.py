import bpy

class SlideshowComposerPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Slideshow Composer panel"
    bl_idname = "slideshow_composer.seqencer_panel"
    bl_category = "Slideshow"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    @staticmethod
    def has_sequencer(context):
        return (context.space_data.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'})

    @classmethod
    def poll(cls, context):
        #return cls.has_sequencer(context) and (act_strip(context) is not None)
        return True

    def draw(self, context):

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences

        layout = self.layout

        box = layout.box()
        box.label(text="Import media files")

        row = box.row()
        row.prop(addon_prefs, "image_strip_frames")

        row = box.row()
        row.prop(addon_prefs, "strips_cross_frames")

        row = box.row()
        row.prop(addon_prefs, "generate_ken_burns_effect")

        row = box.row()
        operator_props = row.operator("slideshow_composer.import_files",
                                      text='Import selected files',
                                      icon='FILE_IMAGE')
        operator_props.image_strip_frames = addon_prefs.image_strip_frames
        operator_props.strips_cross_frames = addon_prefs.strips_cross_frames
        operator_props.generate_ken_burns_effect = addon_prefs.generate_ken_burns_effect

        row = box.row()
        operator_props = row.operator("slideshow_composer.import_directory",
                                      text='Import all from directory',
                                      icon='FILE_FOLDER')
        operator_props.image_strip_frames = addon_prefs.image_strip_frames
        operator_props.strips_cross_frames = addon_prefs.strips_cross_frames
        operator_props.generate_ken_burns_effect = addon_prefs.generate_ken_burns_effect

