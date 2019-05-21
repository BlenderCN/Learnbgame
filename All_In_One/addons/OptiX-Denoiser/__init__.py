bl_info = {
    'name': 'OptiX denoising for Blender 2.80.0',
    'version': (1, 1, 1),
    'blender': (2, 80, 0),
    'category': 'Render'
}
 
import ntpath
import os
import subprocess

import numpy

import bpy
import bpy.utils.previews

custom_icons = None
script_path = None

def retrieve_all_paths():
    global script_path
    script_path = os.path.abspath(__file__)

def load_icons():
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(script_path), "icons")
    print("Icon dir: " + icons_dir)
    custom_icons.load("optix_icon", os.path.join(icons_dir, "optix_logo.png"), 'IMAGE')
    print("OptiX logo path:" + os.path.join(icons_dir, "optix_logo.png"))

def denoise_animation_frame(noisy_frame_path = ""):
    denoiser_path = os.path.abspath(os.path.join(os.path.dirname(script_path), "Denosier_v2.1")) + "\Denoiser.exe"
    file_name = os.path.basename(noisy_frame_path)
    file_directory = noisy_frame_path[:-len(file_name)]
    denoised_frame_path = file_directory + "DENOISED_" + file_name
    print(denoised_frame_path)

    args = [denoiser_path, '-i', noisy_frame_path, "-o", denoised_frame_path]
    subprocess.call(args)
    print("Denoised image " + noisy_frame_path)
    return [denoised_frame_path, file_name]

#
# SHOWS A MESSAGE BOX UNDER THE CURSOR.
#
def show_message_box(message = "", title = "OptiX Denoising", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

#
# OPERATOR TO DENOISE AN ALREADY **RENDERED** IMAGE.
#
class denoise_render_result_operator(bpy.types.Operator):
    bl_idname = 'optix_denoising.denoise_render_result'
    bl_label = 'Denoise Render Result'
    bl_options = {"REGISTER", "UNDO"}
 
    def execute(self, context):
        denoiser_path = os.path.abspath(os.path.join(os.path.dirname(script_path), "Denosier_v2.1")) + "\Denoiser.exe"
        #print(denoiser_path)
        denoising_temp_image_path = os.path.abspath(os.path.dirname(script_path)) + "\denoising_temp.png"
        #print(denoising_temp_image_path)
        denoised_temp_image_path = os.path.abspath(os.path.dirname(script_path)) + "\denoised_temp.png"
        #print(denoised_temp_image_path)

        try:
            if bpy.data.images["Render Result"] == None:
                show_message_box("There is no render result to denoise. Either render manually and then denoise or use the \"Render and denoise\" button.", "OptiX Denoising", 'ERROR')
                return {"FINISHED"}
        except:
            show_message_box("There is no render result to denoise. Either render manually and then denoise or use the \"Render and denoise\" button.", "OptiX Denoising", 'ERROR')
            return {"FINISHED"}

        bpy.data.images["Render Result"].save_render(denoising_temp_image_path)
        args = [denoiser_path, '-i', denoising_temp_image_path, "-o", denoised_temp_image_path]
        subprocess.call(args)
        print("DENOISED!")

        denoised_img = bpy.ops.image.open(filepath=denoised_temp_image_path)
        for area in bpy.context.screen.areas :
            if area.type == 'IMAGE_EDITOR':
                for img in bpy.data.images:
                    if img.name == "denoised_temp.png":
                        area.spaces.active.image = img

        show_message_box("Successfully denoised the image!")
        return {"FINISHED"}

#
# OPERATOR TO RENDER AND THEN DENOISE THE RENDERED IMAGE.
#
class render_and_denoise_operator(bpy.types.Operator):
    bl_idname = 'optix_denoising.render_and_denoise_operator'
    bl_label = 'Render And Denoise'
    bl_options = {"REGISTER", "UNDO"}
 
    def execute(self, context):
        # Show an image viewer
        image_viewer_area = None

        # First try to find an already open image viewer
        for area in bpy.context.screen.areas :
            if area.type == 'IMAGE_EDITOR':
                image_viewer_area = area
                break
        
        # If there is not, try to find a 3D view and change its type to an image viewer
        if image_viewer_area == None:
            for area in bpy.context.screen.areas :
                if area.type == 'VIEW_3D':
                    area.type = 'IMAGE_EDITOR'
                    image_viewer_area = area
                    break

        # If there is neither an open image viewer nor a 3D view, then switch the current area to the image editor
        if image_viewer_area == None:
            bpy.context.area.type = 'IMAGE_EDITOR'
            image_viewer_area = bpy.context.area

        # First render
        bpy.ops.render.render()

        # Then denoise
        denoiser_path = os.path.abspath(os.path.join(os.path.dirname(script_path), "Denosier_v2.1")) + "\Denoiser.exe"
        #print(denoiser_path)
        denoising_temp_image_path = os.path.abspath(os.path.dirname(script_path)) + "\denoising_temp.png"
        #print(denoising_temp_image_path)
        denoised_temp_image_path = os.path.abspath(os.path.dirname(script_path)) + "\denoised_temp.png"
        #print(denoised_temp_image_path)

        bpy.data.images["Render Result"].save_render(denoising_temp_image_path)
        args = [denoiser_path, '-i', denoising_temp_image_path, "-o", denoised_temp_image_path]
        subprocess.call(args)
        print("DENOISED!")

        denoised_img = bpy.ops.image.open(filepath=denoised_temp_image_path)      
        for img in bpy.data.images:
            if img.name == "denoised_temp.png":
                image_viewer_area.spaces.active.image = img

        show_message_box("Successfully rendered and denoised the image!")

        return {"FINISHED"}

#
# OPERATOR TO RENDER THE FULL ANIMATION AND THEN DENOISE IT.
#
class render_and_denoise_animation_operator(bpy.types.Operator):
    bl_idname = 'optix_denoising.render_and_denoise_animation_operator'
    bl_label = 'Render And Denoise Animation'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        # Check if the animation will be saved. If not, cancel, for access to the file will be needed to denoise
        if bpy.context.scene.render.filepath == "/tmp\\" or bpy.context.scene.render.filepath == None or bpy.context.scene.render.filepath == "":
            show_message_box("You must specify where to save the animation for the denoising to work.", "OptiX Denoising", 'ERROR')
            return {"FINISHED"}

        # Show an image viewer
        image_viewer_area = None

        # First try to find an already open image viewer
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                image_viewer_area = area
                break
        
        # If there is not, try to find a 3D view and change its type to an image viewer
        if image_viewer_area == None:
            for area in bpy.context.screen.areas :
                if area.type == 'VIEW_3D':
                    area.type = 'IMAGE_EDITOR'
                    image_viewer_area = area
                    break

        # If there is neither an open image viewer nor a 3D view, then switch the current area to the image editor
        if image_viewer_area == None:
            bpy.context.area.type = 'IMAGE_EDITOR'
            image_viewer_area = bpy.context.area

        # Render the animation
        bpy.ops.render.render(animation=True)

        for img_idx in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
            frame_path = bpy.context.scene.render.frame_path(frame=img_idx)
            print("Denoising \"" + frame_path + "\"...")
            denoise_animation_frame(frame_path)

        show_message_box("Successfully rendered and denoised the animation!")

        return {"FINISHED"}

#
# OPERATOR TO DENOISE A FULL, RENDERED ANIMATION.
#
class denoise_rendered_animation_operator(bpy.types.Operator):
    bl_idname = 'optix_denoising.denoise_rendered_animation_operator'
    bl_label = 'Denoise Rendered Animation'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        # Check if the animation has been saved. If not, cancel, for access to the file will be needed to denoise
        if bpy.context.scene.render.filepath == "/tmp\\" or bpy.context.scene.render.filepath == None or bpy.context.scene.render.filepath == "":
            show_message_box("You must specify the animation output for the denoising to work.", "OptiX Denoising", 'ERROR')
            return {"FINISHED"}
        
        # Denoise the animation
        for img_idx in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
            frame_path = bpy.context.scene.render.frame_path(frame=img_idx)
            
            denoised_img_path_and_filename = denoise_animation_frame(frame_path)

        # end for

        show_message_box("Successfully denoised the rendered animation!")
        return {"FINISHED"}



#
# ADDON PANEL THAT DISPLAYS THE OPTIX DENOISING RELATED BUTTONS.
#
class optix_denoising_panel(bpy.types.Panel):
    bl_idname = "optix_denoising.renderingpanel"
    bl_label = "OptiX Denoising"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    
    def draw_header(self, context):
        self.layout.label(icon_value=custom_icons["optix_icon"].icon_id)

    def draw(self, context):
        layout = self.layout
        row1 = layout.row()
        row1.operator("optix_denoising.denoise_render_result", text="Denoise render result")
        row2 = layout.row()
        row2.operator("optix_denoising.render_and_denoise_operator", text="Render and denoise")
        row3 = layout.row()
        row3.operator("optix_denoising.render_and_denoise_animation_operator", text="Render animation and denoise")
        row4 = layout.row()
        row4.operator("optix_denoising.denoise_rendered_animation_operator", text="Denoise rendered animation")

def register() :
    retrieve_all_paths()
    load_icons()

    try:
        bpy.utils.register_class(denoise_render_result_operator)
    except:
        print("Unable to register the class \"denoise_render_result_operator\"")
    try:
        bpy.utils.register_class(render_and_denoise_operator)
    except:
        print("Unable to register the class \"render_and_denoise_operator\"")
    try:
        bpy.utils.register_class(denoise_rendered_animation_operator)
    except:
        print("Unable to register the class \"denoise_rendered_animation_operator\"")
    try:
        bpy.utils.register_class(render_and_denoise_animation_operator)
    except:
        print("Unable to register the class \"render_and_denoise_animation_operator\"")
    try:
        bpy.utils.register_class(optix_denoising_panel)
    except:
        print("Unable to register the class \"optix_denoising_panel\"")
 
def unregister() :
    global custom_icons
    bpy.utils.previews.remove(custom_icons)

    try:
        bpy.utils.unregister_class(denoise_render_result_operator)
    except:
        print("Unable to unregister the class \"denoise_render_result_operator\"")
    try:
        bpy.utils.unregister_class(render_and_denoise_operator)
    except:
        print("Unable to unregister the class \"render_and_denoise_operator\"")
    try:
        bpy.utils.unregister_class(denoise_rendered_animation_operator)
    except:
        print("Unable to unregister the class \"denoise_rendered_animation_operator\"")
    try:
        bpy.utils.unregister_class(render_and_denoise_animation_operator)
    except:
        print("Unable to unregister the class \"render_and_denoise_animation_operator\"")
    try:
        bpy.utils.unregister_class(optix_denoising_panel)
    except:
        print("Unable to unregister the class \"optix_denoising_panel\"")

if __name__ == "__main__" :
    register()
