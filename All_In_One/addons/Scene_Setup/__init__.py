bl_info = {
    "name": "Scene Setup",
    "category": "Learnbgame",
}

import sys
import os

from . import parser
from . import pather
from . import sizer

from . import err
from . import log

bpy = None
try:
    import bpy
except ImportError:
    sys.stderr.write('Warning: no bpy\n')

if bpy != None:

    from bpy.props import StringProperty
    from bpy.props import BoolProperty

    from . import cycler
    from . import semver
    from . import linker
    from . import mover

    class Starter(bpy.types.Operator):

        bl_idname = "common.start"
        bl_options = {'REGISTER', 'UNDO'}
        bl_label = 'Start {}'.format(bl_info['name'])

        blend = StringProperty()

        def execute(self, context): 
            # Open if blend given
            if self.blend and os.path.exists(self.blend):
                log.yaml('Loading blend file', self.blend)
                bpy.ops.wm.open_mainfile(filepath=self.blend)

            # Cycles
            scene = context.scene
            scene.render.engine = 'CYCLES' 
            scene.cycles.samples = 64

            if scene.world is None:
                scene.world = bpy.data.worlds.new("World")
            scene.world.cycles.sample_as_light = True

            def remove_object(o):
                iters = {
                    'MESH': bpy.data.meshes,
                    'LAMP': bpy.data.lamps,
                }
                o_data = o.data
                o_iter = iters.get(o.type, None)
                if o.name in scene.objects:
                    scene.objects.unlink(o)
                bpy.data.objects.remove(o)
                if o_iter:
                    o_iter.remove(o_data)

            bad_mesh = {'Cube'}
            bad_lamp = {'Lamp'}
            bad = bad_mesh | bad_lamp
            # Remove unwanted objects
            for o in bpy.data.objects:
                names = {o.name, o.data.name}
                if names & bad:
                    log.yaml('Removed', names)
                    remove_object(o)

            # Create the sun
            if 'Sun' not in bpy.data.lamps:
                bpy.ops.object.lamp_add(**{
                    'type': 'SUN',
                })
                sun = context.active_object
                sun.data.name = 'Sun'
                sun.name = 'Sun'

            good_area = {'Area', 'Under', 'Over'}
            area_loc = {
                'Area': (2.0, 2.0, 10.0),
                'Over': (0.0, 0.0, 1.0),
                'Under': (0.0, 0.0, -1.0),
            }
            area_size = {
                'Area': 0.6,
                'Over': 0.5,
                'Under': 0.5,
            }
            area_shadow = {
                'Area': True,
                'Over': False,
                'Under': False,
            }
            # Create an area lamp
            def make_area(_name, _location):
                if _name in bpy.data.lamps:
                    return
                bpy.ops.object.lamp_add(**{
                    'location': _location,
                    'type': 'AREA',
                })
                area = context.active_object
                area.data.name = _name
                area.name = _name

            # Set up some area lamps
            for name in good_area:
                loc = area_loc[name]
                make_area(name, loc)
                area = bpy.data.lamps[name]
                area.shadow_buffer_soft = 100
                area.size = area_size[name]
                # Calculate energy
                area.energy = mover.energy(area, loc[-1])
                area.cycles.cast_shaddow = area_shadow[name]

            # Set up the sun
            sun = bpy.data.lamps['Sun']
            sun.cycles.cast_shadow = False
            sun.energy = 2

            log.yaml('Lamps', bpy.data.lamps.keys())
            return {'FINISHED'}


    class Stopper(bpy.types.Operator):

        bl_idname = "common.stop"
        bl_options = {'REGISTER', 'UNDO'}
        bl_label = 'Stop {}'.format(bl_info['name'])

        blend = StringProperty()
        output = StringProperty()
        movie = BoolProperty()

        def device(self, context):
            # Show available devices
            my_sys = context.user_preferences.system
            my_devices = my_sys.bl_rna.properties['compute_device']
            my_types = my_sys.bl_rna.properties['compute_device_type']
            # Show available types and devices
            msg_d = 'Device {} from'.format(my_sys.compute_device)
            msg_t = 'Type {} from'.format(my_sys.compute_device_type)
            log.yaml(msg_d, [t for t in my_devices.enum_items])
            log.yaml(msg_t, [t for t in my_types.enum_items])

        def render(self, context):
            scene = context.scene
            render = scene.render
            # All frames in scene
            frames = scene.frame_start, scene.frame_end
            outdir = os.path.dirname(self.output)
            pather.make(outdir)
            # Path as the output of the scene
            render.filepath = self.output
            log.yaml('Rendering', self.output)
            # Resolution double actual output
            render.resolution_x = 900 * 2
            render.resolution_y = 500 * 2
            # Render images to the output files
            if self.movie:
                log.yaml('Frames', frames)
                # Set frame to first frame
                scene.frame_set(frames[0])
                render.ffmpeg.codec = 'H264'
                render.ffmpeg.format = 'MPEG4'
                render.fps_base = render.fps / 24
                render.image_settings.file_format = 'FFMPEG'
                # Animate movie
                bpy.ops.render.render(**{
                    'animation': True
                })
                return
            # Look at meshes
            mover.look(scene)
            #bpy.ops.view3d.view_orbit(angle=90.0, type='ORBITLEFT')
            render.image_settings.file_format = 'PNG'
            bpy.ops.render.render(**{
                'write_still': True
            })

        def execute(self, context): 
            # Render if file given
            if self.output:
                self.device(context)
                self.render(context)

            # Save if blend given
            if self.blend:
                outdir = os.path.dirname(self.blend)
                pather.make(outdir)
                log.yaml('Saving blend file', self.blend)
                
                bpy.ops.wm.save_mainfile(**{
                    'filepath': self.blend,
                })

            return {'FINISHED'}

    def register():
        bpy.utils.register_module(__name__)

    def unregister():
        bpy.utils.unregister_module(__name__)
