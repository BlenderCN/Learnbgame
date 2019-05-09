import multiprocessing.connection
import os
import queue
import struct
import subprocess
import sys
import tempfile
import threading
import time


from OpenGL import GL


import pman
import bpy


class ExternalConnection:
    ptr = None
    def __init__(self):
        filedir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
        try:
            config = pman.get_config(filedir)
            user_config = pman.get_user_config(config['internal']['projectdir'])
        except pman.NoConfigError:
            config = None
            user_config = None


        self._tmpfnames = set()
        self.update_queue = queue.Queue()

        if user_config is not None and user_config['python']['in_venv']:
            pyprog = 'python'
        else:
            pyprog = pman.get_python_program(config)

        scriptloc = os.path.join(
            os.path.dirname(__file__),
            'processor_app.py'
        )

        with multiprocessing.connection.Listener() as listener:
            args = [
                pyprog,
                scriptloc,
                filedir,
                str(listener.address),
            ]
            self.proc = subprocess.Popen(args)
            if self.proc.poll() is None:
                self.connection = listener.accept()
        self._running = True
        self.timer = threading.Thread(target=self._timer_thread)
        self.timer.start()
        # print('init complete')

    def destroy(self):
        # print("kill extern")
        self._running = False
        self.proc.terminate()
        self.timer.join()
        for tmpfname in self._tmpfnames:
            os.remove(tmpfname)
        # print("del complete")

    def _timer_thread(self):
        while self._running:
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
            time.sleep(0.1)

    def _send_update(self, update_type, data):
        self.update_queue.put({
            'type': update_type,
            'timestamp': time.perf_counter(),
            **data,
        })

        while self.connection is not None and not self.update_queue.empty():
            try:
                update = self.update_queue.get()
                self.connection.send(update)
            except (BrokenPipeError,):
                self.connection = None

    def update_scene(self, filepath):
        self._tmpfnames.add(filepath)
        self._send_update('scene', {
            'path': filepath,
        })

    def update_view(self, width, height, projmat, viewmat):
        self._send_update('view', {
            'width': width,
            'height': height,
            'projection_matrix': projmat,
            'view_matrix': viewmat,
        })

    def update_bg_color(self, color):
        self._send_update('background_color', {
            'color': color
        })

    def get_image(self):
        image = None
        num_images = 0
        while self.connection is not None and self.connection.poll():
            image = self.connection.recv()
            num_images += 1
        # print('collapsed {} images'.format(num_images))
        return image

    @classmethod
    def get_ptr(cls):
        if cls.ptr is None:
            cls.ptr = ExternalConnection()
        return cls.ptr

    @classmethod
    def destroy_ptr(cls):
        if cls.ptr is not None:
            cls.ptr.destroy()
        cls.ptr = None


class PandaEngine(bpy.types.RenderEngine):
    bl_idname = 'PANDA'
    bl_label = 'LearnbgamEngine'

    def __init__(self):
        # print("create render engine")
        self.tex = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tex)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D, 0, GL.GL_RGB8, 1, 1, 0,
            GL.GL_RGB, GL.GL_UNSIGNED_BYTE, struct.pack('=BBB', 0, 0, 0)
        )
        ExternalConnection.get_ptr()
        self._prev_view_mat = None
        self._prev_proj_mat = None
        self._prev_width = None
        self._prev_height = None

    def __del__(self):
        # print('del render engine')
        ExternalConnection.destroy_ptr()


    def _get_extern_conn(self):
        extern_conn = ExternalConnection.get_ptr()
        return extern_conn

    def _draw_texture(self):
        extern_conn = self._get_extern_conn()

        GL.glPushAttrib(GL.GL_ALL_ATTRIB_BITS)
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.tex)
        image = extern_conn.get_image()
        if image:
            GL.glTexImage2D(
                GL.GL_TEXTURE_2D, 0, GL.GL_RGB8, image['x'], image['y'], 0,
                GL.GL_BGR, GL.GL_UNSIGNED_BYTE, image['bytes']
            )
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)

        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_CULL_FACE)
        GL.glDisable(GL.GL_STENCIL_TEST)
        GL.glEnable(GL.GL_TEXTURE_2D)

        GL.glClearColor(0, 0, 1, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()
        GL.glLoadIdentity()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        GL.glLoadIdentity()

        GL.glBegin(GL.GL_QUADS)
        GL.glColor3f(1.0, 1.0, 1.0)
        GL.glTexCoord2f(0.0, 0.0)
        GL.glVertex3i(-1, -1, 0)
        GL.glTexCoord2f(1.0, 0.0)
        GL.glVertex3i(1, -1, 0)
        GL.glTexCoord2f(1.0, 1.0)
        GL.glVertex3i(1, 1, 0)
        GL.glTexCoord2f(0.0, 1.0)
        GL.glVertex3i(-1, 1, 0)
        GL.glEnd()

        GL.glPopMatrix()
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPopMatrix()

        GL.glPopAttrib()

    def convert_scene(self):
        extern_conn = self._get_extern_conn()
        if bpy.data.filepath:
            tmpfname = os.path.join(os.path.dirname(bpy.data.filepath), '__bp_temp__.bam')
        else:
            tmpfile = tempfile.NamedTemporaryFile(suffix='.bam', delete=False)
            tmpfile.close()
            tmpfname = tmpfile.name
        # stime = time.perf_counter()
        bpy.ops.learnbgame_engine.export_bam(filepath=tmpfname)
        # print('conversion took {:.2f}s'.format(
        #     (time.perf_counter() - stime)
        # ))
        extern_conn.update_scene(
            tmpfname
        )

    def view_update(self, context):
        """ Called when the scene is changed """
        # print('view_update')
        extern_conn = self._get_extern_conn()
        extern_conn.update_bg_color(list(context.scene.world.horizon_color[:])+[1.0])
        self.convert_scene()
        self._draw_texture()


    def view_draw(self, context):
        """ Called when viewport settings change """
        # print('view_update')

        region = context.region
        view = context.region_data

        vmat = view.view_matrix.copy()
        vmat_inv = vmat.inverted()
        pmat = view.perspective_matrix * vmat_inv

        require_update = (
            region.width != self._prev_width or
            region.height != self._prev_height or
            vmat != self._prev_view_mat or
            pmat != self._prev_proj_mat
        )
        if require_update:
            self._prev_width = region.width
            self._prev_height = region.height
            self._prev_view_mat = vmat
            self._prev_proj_mat = pmat

            extern_conn = self._get_extern_conn()
            extern_conn.update_view(
                region.width,
                region.height,
                [i for col in pmat.col for i in col],
                [i for col in vmat.col for i in col],
            )
        self._draw_texture()


    @classmethod
    def launch_game(cls):
        bpy.ops.learnbgame_engine.run_project()

    @classmethod
    def register(cls):
        render_engine_class = cls
        class LaunchGame(bpy.types.Operator):
            '''Launch the game in a separate window'''
            bl_idname = '{}.launch_game'.format(cls.bl_idname.lower())
            bl_label = 'Launch Game'

            @classmethod
            def poll(cls, context):
                return context.scene.render.engine == render_engine_class.bl_idname

            def execute(self, _context):
                try:
                    cls.launch_game()
                except Exception: #pylint:disable=broad-except
                    self.report({'ERROR'}, str(sys.exc_info()[1]))
                return {'FINISHED'}

        bpy.utils.register_class(LaunchGame)
        if not bpy.app.background:
            keymap = bpy.context.window_manager.keyconfigs.default.keymaps['Screen']
            keymap.keymap_items.new(LaunchGame.bl_idname, 'P', 'PRESS')

def register():
    bpy.utils.register_class(PandaEngine)

def unregister():
    bpy.utils.unregister_class(PandaEngine)