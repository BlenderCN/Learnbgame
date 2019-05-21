import multiprocessing.connection
import os
import queue
import struct
import sys
import time
import threading

from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d

sys.path.append(os.path.join(os.path.dirname(__file__), 'pman'))
import pman #pylint:disable=wrong-import-position


p3d.load_prc_file_data(
    '',
    'window-type none\n'
    'pstats-gpu-timing 1\n'
)


class BlenderConnection:
    def __init__(self, conn_addr):
        self.connection = multiprocessing.connection.Client(conn_addr)
        print('connected to', conn_addr)

        self.update_queue = queue.Queue()
        self.image_queue = queue.Queue()
        self.running = True
        self._conn_thread = threading.Thread(target=self._handle_connection)
        self._conn_thread.start()

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        self.running = False
        self.connection.close()

    def _handle_connection(self):
        try:
            while self.running:
                if self.connection.poll():
                    update = self.connection.recv()
                    # print('update {} transfer took {:.2f}ms'.format(
                    #     update['type'],
                    #     (time.perf_counter() - update['timestamp']) * 1000
                    # ))
                    self.update_queue.put(update)

                image = None
                num_images = 0
                while not self.image_queue.empty():
                    num_images += 1
                    image = self.image_queue.get()
                if image is not None:
                    self.connection.send(image)
                # print('collapsed {} images'.format(num_images))
        except (EOFError, OSError):
            self.shutdown()

    def send_image(self, xsize, ysize, imagebytes):
        self.image_queue.put({
            'type': 'image',
            'timestamp': time.perf_counter(),
            'x': xsize,
            'y': ysize,
            'bytes': bytes(imagebytes),
        })

    def get_updates(self):
        updates = []
        while not self.update_queue.empty():
            updates.append(self.update_queue.get())

        return updates


class App(ShowBase):
    def __init__(self, workingdir, conn_addr):
        ShowBase.__init__(self)
        self.view_lens = p3d.MatrixLens()
        self.cam = p3d.NodePath(p3d.Camera('view'))
        self.cam.node().set_lens(self.view_lens)
        self.cam.node().set_active(True)
        self.cam.reparent_to(self.render)

        self.pipe = p3d.GraphicsPipeSelection.get_global_ptr().make_module_pipe('pandagl')

        self.bg_color = p3d.LVecBase4(0.0, 0.0, 0.0, 1.0)

        p3d.get_model_path().prepend_directory(workingdir)
        self.workingdir = workingdir

        self.texture = p3d.Texture()
        self.win = None
        self.renderer = None
        self.make_offscreen(1, 1)

        self.disableMouse()
        self.setFrameRateMeter(True)

        self.image_width = 1
        self.image_height = 1
        self.image_data = struct.pack('=BBB', 0, 0, 0)

        self.scene = self.render.attach_new_node(p3d.PandaNode("Empty Scene"))

        self.connection = BlenderConnection(conn_addr)

        def set_bg_clear_color(task):
            # Keep bg color working even if DisplayRegions get switched around
            # (e.g., from FilterManager)
            for win in self.graphicsEngine.windows:
                for dispregion in win.display_regions:
                    if dispregion.get_camera() == self.cam:
                        dispregion.set_clear_color_active(True)
                        dispregion.set_clear_color(self.bg_color)
            return task.cont
        self.taskMgr.add(set_bg_clear_color, 'Set BG Clear Color')

        def do_updates(task):
            if not self.connection.running:
                sys.exit()

            latest_scene_update = None
            for update in self.connection.get_updates():
                # print('update: {}'.format(update))
                update_type = update['type']
                if update_type == 'view':
                    self.update_view(
                        update['width'],
                        update['height'],
                        self.load_matrix(update['projection_matrix']),
                        self.load_matrix(update['view_matrix']),
                    )
                elif update_type == 'scene':
                    latest_scene_update = update
                elif update_type == 'background_color':
                    self.bg_color = p3d.LVector4(*update['color'])
                else:
                    raise RuntimeError('Unknown update type: {}'.format(update_type))

            if latest_scene_update is not None:
                self.update_scene(latest_scene_update['path'])

            return task.cont
        self.taskMgr.add(do_updates, 'Updates')

        def image_updates(task):
            if self.texture.has_ram_image():
                #start = time.perf_counter()
                self.connection.send_image(
                    self.texture.get_x_size(),
                    self.texture.get_y_size(),
                    memoryview(self.texture.get_ram_image_as('BGR'))
                )
                #print('Extern: Updated image data in {}ms'.format((time.perf_counter() - start) * 1000))
            return task.cont
        self.taskMgr.add(image_updates, 'Upload Images')


    def update_rman(self):
        try:
            pman_conf = pman.get_config(self.workingdir)
            self.renderer = pman.create_renderer(self, pman_conf)
        except pman.NoConfigError:
            from pman import basicrenderer # pylint:disable=no-name-in-module
            print('No configuration found, falling back to basic renderer')
            self.renderer = basicrenderer.BasicRenderer(self)


    def make_offscreen(self, sizex, sizey):
        sizex = p3d.Texture.up_to_power_2(sizex)
        sizey = p3d.Texture.up_to_power_2(sizey)

        if self.win and self.win.get_size()[0] == sizex and self.win.get_size()[1] == sizey:
            # The current window is good, don't waste time making a new one
            return

        use_frame_rate_meter = self.frameRateMeter is not None
        self.setFrameRateMeter(False)

        self.graphicsEngine.remove_all_windows()
        self.win = None
        self.view_region = None

        # First try to create a 24bit buffer to minimize copy times
        fbprops = p3d.FrameBufferProperties()
        fbprops.set_rgba_bits(8, 8, 8, 0)
        fbprops.set_depth_bits(24)
        winprops = p3d.WindowProperties.size(sizex, sizey)
        flags = p3d.GraphicsPipe.BF_refuse_window
        #flags = p3d.GraphicsPipe.BF_require_window
        self.win = self.graphicsEngine.make_output(
            self.pipe,
            'window',
            0,
            fbprops,
            winprops,
            flags
        )

        if self.win is None:
            # Try again with an alpha channel this time (32bit buffer)
            fbprops.set_rgba_bits(8, 8, 8, 8)
            self.win = self.graphicsEngine.make_output(
                self.pipe,
                'window',
                0,
                fbprops,
                winprops,
                flags
            )

        if self.win is None:
            print('Unable to open window')
            sys.exit(-1)

        disp_region = self.win.make_mono_display_region()
        disp_region.set_camera(self.cam)
        disp_region.set_active(True)
        disp_region.set_clear_color_active(True)
        disp_region.set_clear_color(self.bg_color)
        disp_region.set_clear_depth(1.0)
        disp_region.set_clear_depth_active(True)
        self.view_region = disp_region
        self.graphicsEngine.open_windows()

        self.setFrameRateMeter(use_frame_rate_meter)

        self.update_rman()

        self.texture = p3d.Texture()
        self.win.addRenderTexture(self.texture, p3d.GraphicsOutput.RTM_copy_ram)

    def load_matrix(self, mat):
        lmat = p3d.LMatrix4()

        for i in range(4):
            lmat.set_row(i, p3d.LVecBase4(*mat[i * 4: i * 4 + 4]))
        return lmat

    def update_view(self, width, height, projmat, viewmat):
        self.make_offscreen(width, height)
        self.view_lens.set_user_mat(projmat)
        # Panda wants an OpenGL model matrix instead of an OpenGL view matrix
        viewmat.invert_in_place()
        self.view_lens.set_view_mat(viewmat)

    def update_scene(self, bampath):
        #stime = time.perf_counter()
        bampath = p3d.Filename.from_os_specific(bampath)
        new_scene = self.loader.load_model(bampath, noCache=True)
        # print('update took {:.2f}s'.format(
        #     (time.perf_counter() - stime)
        # ))
        self.scene.remove_node()
        new_scene.reparent_to(self.render)
        self.scene = new_scene


def main():
    app = App(sys.argv[1], sys.argv[2])
    app.run()


if __name__ == "__main__":
    main()
