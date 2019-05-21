# System Libs
import os, subprocess, threading, time, sys, random

# Blender Libs
import bpy, bl_ui            #@UnresolvedImport

# EF Libs
from ..extensions_framework import util as efutil

# Indigo Libs
from .. import bl_info
from .. export import indigo_log
from .. import operators # init
from .. panels import * # init


'''
# Exporter Property Groups need to be imported to ensure initialisation
import indigo.properties.camera
import indigo.properties.environment
import indigo.properties.lamp
import indigo.properties.material
import indigo.properties.medium
import indigo.properties.object
import indigo.properties.render_settings
import indigo.properties.tonemapping

# Exporter Interface Panels need to be imported to ensure initialisation
import indigo.panels.camera
#import indigo.panels.image
import indigo.panels.lamp
import indigo.panels.material
import indigo.panels.medium
import indigo.panels.object
import indigo.panels.render
import indigo.panels.world

# Exporter Operators need to be imported to ensure initialisation
import indigo.operators
'''

from . util import getVersion, getGuiPath, getConsolePath, getInstallPath, count_contiguous

BL_IDNAME = 'indigo_renderer'

# Add standard Blender Interface elements
'''
'''
bl_ui.properties_render.RENDER_PT_render.COMPAT_ENGINES.add(BL_IDNAME)
bl_ui.properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add(BL_IDNAME)
bl_ui.properties_render.RENDER_PT_output.COMPAT_ENGINES.add(BL_IDNAME)

bl_ui.properties_scene.SCENE_PT_scene.COMPAT_ENGINES.add(BL_IDNAME)
bl_ui.properties_scene.SCENE_PT_audio.COMPAT_ENGINES.add(BL_IDNAME)
bl_ui.properties_scene.SCENE_PT_physics.COMPAT_ENGINES.add(BL_IDNAME) #This is the gravity panel
bl_ui.properties_scene.SCENE_PT_keying_sets.COMPAT_ENGINES.add(BL_IDNAME)
bl_ui.properties_scene.SCENE_PT_keying_set_paths.COMPAT_ENGINES.add(BL_IDNAME)
bl_ui.properties_scene.SCENE_PT_unit.COMPAT_ENGINES.add(BL_IDNAME)
bl_ui.properties_scene.SCENE_PT_custom_props.COMPAT_ENGINES.add(BL_IDNAME)

bl_ui.properties_material.MATERIAL_PT_context_material.COMPAT_ENGINES.add(BL_IDNAME)
bl_ui.properties_texture.TEXTURE_PT_context_texture.COMPAT_ENGINES.add(BL_IDNAME)

def compatible(module):
    module = getattr(bl_ui, module)
    for subclass in module.__dict__.values():
        try:    subclass.COMPAT_ENGINES.add(BL_IDNAME)
        except: pass

compatible("properties_data_mesh")
compatible("properties_data_camera")
compatible("properties_particle")

class RENDERENGINE_indigo(bpy.types.RenderEngine):
    bl_idname = BL_IDNAME
    bl_label = 'Indigo'
    bl_use_preview = False

    render_lock = threading.Lock()

    def render(self, context):
        '''
        Render the scene file, or in our case, export the frame(s)
        and launch an Indigo process.
        '''
        
        with RENDERENGINE_indigo.render_lock:    # Just render one thing at a time.
            self.renderer            = None
            self.message_thread      = None
            self.stats_thread        = None
            self.framebuffer_thread  = None
            self.render_update_timer = None
            self.rendering           = False

            # force scene update to current rendering frame
            # Not sure why - Yves
            #context.frame_set(context.frame_current)

            #------------------------------------------------------------------------------
            # Export the Scene

            # Get the frame path.
            frame_path = efutil.filesystem_path(context.render.frame_path())

            # Get the filename for the frame sans extension.
            image_out_path = os.path.splitext(frame_path)[0]

            # Generate the name for the scene file(s).
            if context.indigo_engine.use_output_path == True:
                # Get the output path from the frame path.
                output_path = os.path.dirname(frame_path)

                # Generate the output filename
                output_filename = '%s.%s.%05i.igs' % (efutil.scene_filename(), bpy.path.clean_name(context.name), context.frame_current)
            else:
                # Get export path from the indigo_engine.
                export_path = efutil.filesystem_path(context.indigo_engine.export_path)

                # Get the directory name from the output path.
                output_path = os.path.dirname(export_path)

                # Get the filename from the output path and remove the extension.
                output_filename = os.path.splitext(os.path.basename(export_path))[0]

                # Count contiguous # chars and replace them with the frame number.
                # If the hash count is 0 and we are exporting an animation, append the frame numbers.
                hash_count = util.count_contiguous('#', output_filename)
                if hash_count != 0:
                    output_filename = output_filename.replace('#'*hash_count, ('%%0%0ii'%hash_count)%context.frame_current)
                elif self.is_animation:
                    output_filename = output_filename + ('%%0%0ii'%4)%context.frame_current

                # Add .igs extension.
                output_filename += '.igs'


            # The full path of the exported scene file.
            exported_file = '/'.join([
                output_path,
                output_filename
            ])

            # Create output_path if it does not exist.
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            # If an animation is rendered, write an indigo queue file (.igq).
            if self.is_animation:
                igq_filename = '%s/%s.%s.igq'%(output_path, efutil.scene_filename(), bpy.path.clean_name(context.name))

                if context.frame_current == context.frame_start:
                    # Start a new igq file.
                    igq_file = open(igq_filename, 'w')
                    igq_file.write('<?xml version="1.0" encoding="utf-8" standalone="no" ?>\n')
                    igq_file.write('<render_queue>\n')
                else:
                    # Append to existing igq.
                    igq_file = open(igq_filename, 'a')
                    
                rnd = random.Random()
                rnd.seed(context.frame_current)

                # Write igq item.
                igq_file.write('\t<item>\n')
                igq_file.write('\t\t<scene_path>%s</scene_path>\n' % exported_file)
                igq_file.write('\t\t<halt_time>%d</halt_time>\n' % context.indigo_engine.halttime)
                igq_file.write('\t\t<halt_spp>%d</halt_spp>\n' % context.indigo_engine.haltspp)
                igq_file.write('\t\t<output_path>%s</output_path>\n' % image_out_path)
                igq_file.write('\t\t<seed>%s</seed>\n' % rnd.randint(1, 1000000))
                igq_file.write('\t</item>\n')

                # If this is the last frame, write the closing tag.
                if context.frame_current == context.frame_end:
                    igq_file.write('</render_queue>\n')

                igq_file.close()

                # Calculate the progress by frame with frame range (fr) and frame offset (fo).
                fr = context.frame_end - context.frame_start
                fo = context.frame_current - context.frame_start
                self.update_progress(fo/fr)

            scene_writer = operators._Impl_OT_indigo(
                directory = output_path,
                filename = output_filename
            ).set_report(self.report)

            # Write the scene file.
            export_result = scene_writer.execute(context)

            # Return if the export didn't finish.
            if not 'FINISHED' in export_result:
                return

            #------------------------------------------------------------------------------
            # Update indigo defaults config file .
            config_updates = {
                'auto_start': context.indigo_engine.auto_start,
                'console_output': context.indigo_engine.console_output
            }

            if context.indigo_engine.use_console:
                indigo_path = getConsolePath(context)
            else:
                indigo_path = getGuiPath(context)

            if os.path.exists(indigo_path):
                config_updates['install_path'] = getInstallPath(context)

            try:
                for k,v in config_updates.items():
                    efutil.write_config_value('indigo', 'defaults', k, v)
            except Exception as err:
                indigo_log('Saving indigo config failed: %s' % err, message_type='ERROR')

            # Make sure that the Indigo we are going to launch is at least as
            # new as the exporter version.
            version_ok = True
            if not context.indigo_engine.skip_version_check:
                iv = getVersion(context)
                for i in range(3):
                    version_ok &= iv[i]>=bl_info['version'][i]

            #------------------------------------------------------------------------------
            # Conditionally Spawn Indigo.
            if context.indigo_engine.auto_start:

                exe_path = efutil.filesystem_path( indigo_path )

                if not os.path.exists(exe_path):
                    print("Failed to find indigo at '" + str(exe_path) + "'")
                    msg = "Failed to find indigo at '" + str(exe_path) + "'."
                    msg + "\n  "
                    msg += "Please make sure you have Indigo installed, and that the path to indigo in the 'Indigo Render Engine Settings' is set correctly."
                    self.report({'ERROR'}, msg)

                #if not version_ok:
                    #indigo_log("Unsupported version v%s; Cannot start Indigo with this scene" % ('.'.join(['%s'%i for i in iv])), message_type='ERROR')
                    #return

                # if it's an animation, don't execute until final frame
                if self.is_animation and context.frame_current != context.frame_end:
                    return

                # if animation and final frame, launch queue instead of single frame
                if self.is_animation and context.frame_current == context.frame_end:
                    exported_file = igq_filename
                    indigo_args = [
                        exe_path,
                        exported_file
                    ]
                else:
                    indigo_args = [
                        exe_path,
                        exported_file,
                        '-o',
                        image_out_path + '.png'
                    ]

                # export exrs
                if context.indigo_engine.save_exr_utm:
                    indigo_args.extend(['-uexro', image_out_path + '_untonemapped.exr'])
                if context.indigo_engine.save_exr_tm:
                    indigo_args.extend(['-texro', image_out_path + '_tonemapped.exr'])
                if context.indigo_engine.save_igi:
                    indigo_args.extend(['-igio', image_out_path + '.igi'])
                if context.indigo_engine.save_render_channels_exr:
                    indigo_args.extend(['-channels', image_out_path + '_channels.exr'])

                # Set master or working master command line args.
                if context.indigo_engine.network_mode == 'master':
                    indigo_args.extend(['-n', 'm'])
                elif context.indigo_engine.network_mode == 'working_master':
                    indigo_args.extend(['-n', 'wm'])

                # Set port arg if network rendering is enabled.
                if context.indigo_engine.network_mode in ['master', 'working_master']:
                    indigo_args.extend([
                        '-p',
                        '%i' % context.indigo_engine.network_port
                    ])

                # Set hostname and port arg.
                if context.indigo_engine.network_mode == 'manual':
                    indigo_args.extend([
                        '-h',
                        '%s:%i' % (context.indigo_engine.network_host, context.indigo_engine.network_port)
                ])

                # indigo_log("Starting indigo: %s" % indigo_args)

                # If we're starting a console or should wait for the process, listen to the output.
                if context.indigo_engine.use_console or context.indigo_engine.wait_for_process:
                    f_stdout = subprocess.PIPE
                else:
                    f_stdout = None

                # Launch the Indigo process.
                from . util import isMac
                if isMac():
                    indigo_args = ['open','-a'] + [indigo_args[0]] + ['-n', '--args'] + indigo_args[1:]
                indigo_proc = subprocess.Popen(indigo_args, stdout=f_stdout)
                indigo_pid = indigo_proc.pid
                indigo_log('Started Indigo process, PID: %i' % indigo_pid)

                # Wait for the render to finish if we use the console or should wait for the process.
                if context.indigo_engine.use_console or context.indigo_engine.wait_for_process:
                    while indigo_proc.poll() == None:
                        indigo_proc.communicate()
                        time.sleep(2)

                    indigo_proc.wait()
                    if not indigo_proc.stdout.closed:
                        indigo_proc.communicate()
                    if indigo_proc.returncode == -1:
                        sys.exit(-1)

            else:
                indigo_log("Scene was exported to %s" % exported_file)

            #------------------------------------------------------------------------------
            # Finished
            return

    def stats_timer(self):
        '''
        Update the displayed rendering statistics and detect end of rendering

        Returns None
        '''

        self.update_stats('', 'Indigo Renderer: Rendering %s' % self.stats_thread.stats_string)
        if self.test_break() or not self.message_thread.isAlive():
            self.renderer.terminate_rendering()
            self.stats_thread.stop()
            self.stats_thread.join()
            self.message_thread.stop()
            self.message_thread.join()
            self.framebuffer_thread.stop()
            self.framebuffer_thread.join()
            # self.framebuffer_thread.kick() # Force get final image
            self.update_stats('', '')
            self.rendering = False
            self.renderer = None # destroy/unload the renderer instance