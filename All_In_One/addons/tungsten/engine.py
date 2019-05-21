import bpy
import os.path
import time

from . import tungsten, scene, base

@base.register_class
class TungstenRenderEngine(bpy.types.RenderEngine):
    bl_idname = 'TUNGSTEN'
    bl_label = 'Tungsten'

    bl_use_preview = True

    def update(self, data, blscene):
        self.scene = scene.TungstenScene()
        self.scene.add_all(blscene, preview=self.is_preview)
        self.scene.save()

        self.threads = blscene.render.threads

    def render(self, blscene):
        result = self.begin_result(0, 0, self.scene.width, self.scene.height)
        layer = result.layers[0]

        prefs = bpy.context.user_preferences.addons[__package__].preferences
        pexe = prefs.tungsten_server_path

        if not pexe:
            self.report({'ERROR'}, 'Tungsten Server path not set')
            return

        exe = bpy.path.abspath(pexe)
        if not os.path.exists(exe):
            self.report({'ERROR'}, 'Tungsten Server path does not exist: ' + pexe)
            return

        print('rendering...')
        start = time.time()
        t = tungsten.Tungsten(exe, self.scene.scenefile, threads=self.threads)
        last_spp = 0
        while t.running:
            time.sleep(0.1)
            # do not do status if it's a preview
            if self.is_preview:
                continue
            
            try:
                s = t.get_status()
            except OSError:
                break
            
            # cancel if needed
            if self.test_break():
                t.cancel()
                self.end_result(result)
                return
            
            if s['current_spp'] != last_spp:
                last_spp = s['current_spp']

                # update status, image
                tmpf = None
                try:
                    layer.load_from_file(t.get_render())
                    self.update_result(result)
                except OSError:
                    pass

                self.update_stats('current spp: {0}'.format(last_spp), 'total spp: {0}'.format(s['total_spp']))
                self.update_progress(last_spp / s['total_spp'])
                
        if t.finish() != 0 or not os.path.exists(self.scene.outputfile):
            self.report({'ERROR'}, 'Tungsten exited in error.')
            return

        end = time.time()
        print('done rendering in', end - start, 's')
        layer.load_from_file(self.scene.outputfile)

        self.end_result(result)
