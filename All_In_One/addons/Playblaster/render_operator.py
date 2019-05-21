import bpy
import os
import shutil

from .preferences import get_addon_preferences
from .misc_functions import absolute_path, create_dir, get_file_in_folder, delete_file
from .global_variables import blender_executable
from .thread_functions import threading_render

blend_temp = ""
video_temp = ""

class PlayblasterRenderOperator(bpy.types.Operator):
    """Create Playblast of current scene"""
    bl_idname = "playblaster.render"
    bl_label = "Playblaster Render"

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved and not context.scene.playblaster_is_rendering

    def execute(self, context):
        # global
        global blend_temp
        global video_temp

        # variables
        prefs = get_addon_preferences()
        folder_path = absolute_path(prefs.prefs_folderpath)

        scn = context.scene
        blender = blender_executable
        blend_filepath = bpy.data.filepath
        blend_dir = os.path.dirname(blend_filepath)
        blend_file = bpy.path.basename(blend_filepath)
        blend_name = os.path.splitext(blend_file)[0]
        new_blend_filepath = blend_temp = os.path.join(blend_dir, "temp_" + blend_file)
        output_name = "playblast_" + blend_name + "_" + scn.name + "_"
        output_filepath = video_temp = os.path.join(folder_path, output_name)
        render_engine = scn.playblaster_render_engine

        scn.playblaster_is_rendering = True
        scn.playblaster_completion = 0

        # create dir if does not exist
        create_dir(folder_path)

        # delete old playblast
        to_delete = get_file_in_folder(folder_path, output_name)
        if to_delete != "" :
            delete_file(to_delete)

        rd = scn.render
        ffmpeg = rd.ffmpeg

        ### store settings ###
        old_filepath = rd.filepath
        old_file_format = rd.image_settings.file_format
        old_res_pct = rd.resolution_percentage
        old_format = ffmpeg.format
        old_rate_factor = ffmpeg.constant_rate_factor
        old_ffmpeg_preset = ffmpeg.ffmpeg_preset
        old_gopsize = ffmpeg.gopsize
        old_codec = ffmpeg.codec
        old_audio_codec = ffmpeg.audio_codec
            # postprod
        old_compositing = rd.use_compositing
        old_sequencer = rd.use_sequencer
            # simplify
        if scn.playblaster_simplify :
            old_simplify_toggle = rd.use_simplify
            old_simplify_subdiv_render = rd.simplify_subdivision_render
            old_simplify_particles = rd.simplify_child_particles_render
            # EEVEE
        if render_engine == "BLENDER_EEVEE" :
            old_render_samples = scn.eevee.taa_render_samples
            old_eevee_dof = scn.eevee.use_dof
            old_eevee_ao = scn.eevee.use_gtao

            # frame range
        if scn.playblaster_frame_range_override and scn.playblaster_frame_range_in < scn.playblaster_frame_range_out :
            old_range_in = scn.frame_start
            old_range_out = scn.frame_end

        ### change settings ###
        rd.filepath = output_filepath
        rd.image_settings.file_format = 'FFMPEG'
        rd.resolution_percentage = scn.playblaster_resolution_percentage
        ffmpeg.format = 'MPEG4'
        ffmpeg.codec = 'H264'
        ffmpeg.constant_rate_factor = 'HIGH'
        ffmpeg.ffmpeg_preset = 'REALTIME'
        ffmpeg.gopsize = 10
        ffmpeg.audio_codec = 'AAC'
            # postprod
        rd.use_compositing = scn.playblaster_use_compositing
        rd.use_sequencer = False
            # simplify
        if scn.playblaster_simplify :
            rd.use_simplify = True
            rd.simplify_subdivision_render = scn.playblaster_simplify_subdivision
            rd.simplify_child_particles_render = scn.playblaster_simplify_particles
            # EEVEE
        if render_engine == "BLENDER_EEVEE" :
            scn.eevee.taa_render_samples = scn.playblaster_eevee_samples
            scn.eevee.use_dof = scn.playblaster_eevee_dof
            scn.eevee.use_gtao = scn.playblaster_eevee_ambient_occlusion
            # frame range
        if scn.playblaster_frame_range_override and scn.playblaster_frame_range_in < scn.playblaster_frame_range_out :
            scn.frame_start = scn.playblaster_frame_range_in
            scn.frame_end = scn.playblaster_frame_range_out

        # get total number of frames
        total_frame = context.scene.frame_end - context.scene.frame_start + 1

        # save current file
        bpy.ops.wm.save_as_mainfile(filepath = blend_filepath)

        # save temporary file
        shutil.copy(blend_filepath, new_blend_filepath)

        ### restore settings ###
        rd.filepath = old_filepath
        rd.image_settings.file_format = old_file_format
        rd.resolution_percentage = old_res_pct
        ffmpeg.format = old_format
        ffmpeg.constant_rate_factor = old_rate_factor
        if old_ffmpeg_preset != "" :
            ffmpeg.ffmpeg_preset = old_ffmpeg_preset
        ffmpeg.gopsize = old_gopsize
        ffmpeg.codec = old_codec
        ffmpeg.audio_codec = old_audio_codec
            # postprod
        rd.use_compositing = old_compositing
        rd.use_sequencer = old_sequencer
            # simplify
        if scn.playblaster_simplify :
            rd.use_simplify = old_simplify_toggle
            rd.simplify_subdivision_render = old_simplify_subdiv_render
            rd.simplify_child_particles_render = old_simplify_particles
            # EEVEE
        if render_engine == "BLENDER_EEVEE" :
            scn.eevee.taa_render_samples = old_render_samples
            scn.eevee.use_dof = old_eevee_dof
            scn.eevee.use_gtao = old_eevee_ao
            # frame range
        if scn.playblaster_frame_range_override and scn.playblaster_frame_range_in < scn.playblaster_frame_range_out :
            scn.frame_start = old_range_in
            scn.frame_end = old_range_out


        # save current file
        bpy.ops.wm.save_as_mainfile(filepath = blend_filepath)

        new_scn = bpy.context.scene

        cmd = blender + " -b " + new_blend_filepath + " -E " + render_engine + " -a"

        threading_render([cmd, total_frame, new_scn, folder_path, output_name, new_blend_filepath])

        # launch modal check
        for w in bpy.context.window_manager.windows :
            s = w.screen
            for a in s.areas:
                if a.type == 'VIEW_3D' :
                    window = w
                    area = a
                    screen = window.screen
        override = {'window': window, 'screen': screen, 'area': area}

        bpy.ops.playblaster.modal_check(override)

        return {'FINISHED'}
