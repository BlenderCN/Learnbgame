import bpy

class SlideShowMainMenu(bpy.types.Menu):
    bl_label = "SlideShow Composer"
    bl_idname = "slideshow_composer.main_menu"

    def draw(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__package__].preferences
        layout = self.layout

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator('slideshow_composer.import_files', icon='SEQUENCE', text='Import files')
        operator_props = layout.operator('slideshow_composer.ken_burns_effect', icon='SEQUENCE', text='Ken Burns effect')
        operator_props.ken_burns_transformation_x_value = addon_prefs.ken_burns_transformation_x_value
        operator_props.ken_burns_transformation_x_value_max_deviation = addon_prefs.ken_burns_transformation_x_value_max_deviation
        operator_props.ken_burns_transformation_y_value = addon_prefs.ken_burns_transformation_y_value
        operator_props.ken_burns_transformation_y_value_max_deviation = addon_prefs.ken_burns_transformation_y_value_max_deviation
        operator_props.ken_burns_transformation_scale_value = addon_prefs.ken_burns_transformation_scale_value
        operator_props.ken_burns_transformation_scale_value_max_deviation = addon_prefs.ken_burns_transformation_scale_value_max_deviation
        operator_props.ken_burns_transformation_rotation_value = addon_prefs.ken_burns_transformation_rotation_value
        operator_props.ken_burns_transformation_rotation_value_max_deviation = addon_prefs.ken_burns_transformation_rotation_value_max_deviation
        operator_props.ken_burns_combined_effect_probability = addon_prefs.ken_burns_combined_effect_probability
        operator_props.replace = True

if __name__ == "__main__":
   bpy.utils.register_class(SlideShowMainMenu)