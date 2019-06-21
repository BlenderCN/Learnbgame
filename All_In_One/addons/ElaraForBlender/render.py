import bpy
import ctypes as c
import threading
from . import esslib
import tempfile
import os

class eiRenderParameters(c.Structure):
    _fields_ = [('root_instgroup', c.c_char * 128),
                ('camera_inst', c.c_char * 128),
                ('options', c.c_char * 128)]

class eiProcess(c.Structure):
    pass

eiProcess._fields_ = [('pass_started', c.CFUNCTYPE(None, c.POINTER(eiProcess), c.c_int)),
                ('pass_finished', c.CFUNCTYPE(None, c.POINTER(eiProcess), c.c_int)),
                ('job_started', c.CFUNCTYPE(None, c.POINTER(eiProcess), c.POINTER(c.c_uint), c.c_int)),
                ('job_finished', c.CFUNCTYPE(None, c.POINTER(eiProcess), c.POINTER(c.c_uint), c.c_int, c.c_int)),
                ('info', c.CFUNCTYPE(None, c.POINTER(eiProcess), c.c_char_p))]

class eiBucketJob(c.Structure):
    #_pack_ = 1
    _fields_ = [('pos_i', c.c_int),
                ('pos_j', c.c_int),
                ('rect_l', c.c_int),
                ('rect_r', c.c_int),
                ('rect_t', c.c_int),
                ('rect_b', c.c_int),
                ('infoFrameBuffer', c.POINTER(c.c_uint)),
                ('colorFrameBuffer', c.POINTER(c.c_uint)),
                ('opacityFrameBuffer', c.POINTER(c.c_uint)),
                ('frameBuffers', c.POINTER(c.c_uint)),
                ('point_spacing', c.c_float),
                ('pass_id', c.c_int),
                ('win_l', c.c_int),
                ('win_r', c.c_int),
                ('win_t', c.c_int),
                ('win_b', c.c_int)]

class eiColor(c.Structure):
    _fields_ = [('r', c.c_float),
                ('g', c.c_float),
                ('b', c.c_float)]

class eiFrameBufferCache(c.Structure):
    #_pack_ = 1
    _fields_ = [('m_unique_name', c.c_char_p),
                ('m_fb', c.POINTER(c.c_uint)),
                ('m_width', c.c_int),
                ('m_height', c.c_int),
                ('m_border', c.c_int),
                ('m_filter', c.c_bool),
                ('m_point_spacing', c.c_float),
                ('m_inv_point_spacing', c.c_float),
                ('m_pass_id', c.c_int),
                ('m_type', c.c_int),

                ('m_data_size', c.c_int),
                ('m_data_offset', c.c_uint),

                ('m_width1', c.c_int),
                ('m_height1', c.c_int),
                ('m_i', c.c_int),
                ('m_j', c.c_int),
                ('m_tile_left', c.c_int),
                ('m_tile_top', c.c_int),
                ('m_display_gamma', c.c_float),
                ('m_toneop', c.c_void_p),
                ('m_ptr', c.POINTER(c.c_uint8)),
                ('m_tile_tag', c.POINTER(c.c_uint)),
                ('m_copy_item', c.c_void_p),
                #('m_weight_cache', c.c_void_p),
                ('m_temp', c.c_int),
                ('m_rect_l', c.c_int),
                ('m_rect_r', c.c_int),
                ('m_rect_t', c.c_int),
                ('m_rect_b', c.c_int)]

elara = 0

@c.CFUNCTYPE(None, c.POINTER(eiProcess), c.c_int)
def rprocess_pass_started(process, pass_id):
    #print("rprocess_pass_started")
    #print(pass_id)
    return

@c.CFUNCTYPE(None, c.POINTER(eiProcess), c.c_int)
def rprocess_pass_finished(process, pass_id):
    #print("rprocess_pass_finished")
    #print(pass_id)
    return

@c.CFUNCTYPE(None, c.POINTER(eiProcess), c.POINTER(c.c_uint), c.c_int)
def rprocess_job_started(process, job, threadId):
    #print("rprocess_job_started")
    #print(threadId)
    return

image_width = 640
image_height = 480
blue_rect = []

@c.CFUNCTYPE(None, c.POINTER(eiProcess), c.POINTER(c.c_uint), c.c_int, c.c_int)
def rprocess_job_finished(process, job, job_state, threadId):
    global elara
    global image_width
    global image_height
    global blue_rect
    global lock

    jobtype = elara.ei_db_type(job)
    if jobtype != 62:
        return
    if job_state == 3:
        return
    pJob = c.cast(elara.ei_db_access(job), c.POINTER(eiBucketJob))

    if pJob.contents.pass_id <= -5:
        return

    infoFrameBufferCache = eiFrameBufferCache()
    colorFrameBufferCache = eiFrameBufferCache()

    elara.ei_framebuffer_cache_init(c.byref(infoFrameBufferCache),
                                    pJob.contents.infoFrameBuffer,
                                    pJob.contents.pos_i,
                                    pJob.contents.pos_j,
                                    pJob.contents.point_spacing,
                                    pJob.contents.pass_id,
                                    None)

    elara.ei_framebuffer_cache_init(c.byref(colorFrameBufferCache),
                                    pJob.contents.colorFrameBuffer,
                                    pJob.contents.pos_i,
                                    pJob.contents.pos_j,
                                    pJob.contents.point_spacing,
                                    pJob.contents.pass_id,
                                    c.byref(infoFrameBufferCache))
    left = infoFrameBufferCache.m_rect_l
    right = infoFrameBufferCache.m_rect_r
    top = infoFrameBufferCache.m_rect_t
    bottom = infoFrameBufferCache.m_rect_b

    image_end = image_width * image_height - 1
    tile_first = (image_height - pJob.contents.rect_t -1) * image_width + pJob.contents.rect_l
    
    lock.acquire()
    for j in range(top, bottom):
        for i in range(left, right):
            color = eiColor()
            elara.ei_framebuffer_cache_get_final(c.byref(colorFrameBufferCache), i, j, c.byref(color))

            tile_index = tile_first + i
            blue_rect[tile_index] = [color.r, color.g, color.b, 1.0]
            #print("len:%d first:%d index:%d w:%d h:%d"%(len(blue_rect), tile_first, tile_index, image_width, image_height))
            #print("r:%f g:%f b:%f"%(color.r, color.g, color.b))
        tile_first -= image_width
    lock.release()
    elara.ei_framebuffer_cache_exit(c.byref(colorFrameBufferCache))
    elara.ei_framebuffer_cache_exit(c.byref(infoFrameBufferCache))
    elara.ei_db_end(job)
    return

@c.CFUNCTYPE(None, c.POINTER(eiProcess), c.c_char_p)
def rprocess_info(process, text):
    #print("rprocess_info")
    #print(text)
    return

@c.CFUNCTYPE(c.c_uint32, c.c_void_p)
def render_callback(param):
    global elara
    rparam = c.cast(param, c.POINTER(eiRenderParameters))
    elara.ei_job_register_thread()
    elara.ei_render_run(rparam.contents.root_instgroup, rparam.contents.camera_inst, rparam.contents.options)
    elara.ei_job_unregister_thread()
    return 1

class ElaraRenderEngine(bpy.types.RenderEngine):
    # These three members are used by blender to set up the
    # RenderEngine; define its internal name, visible name and capabilities.
    bl_idname = "elara_renderer"
    bl_label = "Elara Renderer"
    bl_use_preview = True

    # This is the only method called by blender, in this example
    # we use it to detect preview rendering and call the implementation
    # in another method.
    def render(self, scene):
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)

        if self.is_preview:
            self.render_preview(scene)
        else:
            self.render_scene(scene)

    # In this example, we fill the preview renders with a flat green color.
    def render_preview(self, scene):
        pixel_count = self.size_x * self.size_y

        # The framebuffer is defined as a list of pixels, each pixel
        # itself being a list of R,G,B,A values
        green_rect = [[0.0, 1.0, 0.0, 1.0]] * pixel_count

        # Here we write the pixel values to the RenderResult
        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]
        layer.rect = green_rect
        self.end_result(result)

    # In this example, we fill the full renders with a flat blue color.
    def render_scene(self, scene):
        ess_file = os.path.join(tempfile.gettempdir(), "elara.ess")

        camera = scene.camera
        env_color = scene.elara_env.color

        exporter = esslib.EssExporter()

        exporter.BeginExport(ess_file)
        exporter.SetOptions()
        exporter.AddDefaultMaterial()
        b = exporter.AddBackground(env_color)
        exporter.AddCameraData(self.size_x, self.size_y, camera.data.angle, camera.data.clip_start, camera.data.clip_end, b, camera.matrix_world)

        for obj in scene.objects:
            exporter.AddObj(obj, scene)

        exporter.EndExport()
        self.elara_render(ess_file)
        # Here we write the pixel values to the RenderResult

    def elara_render(self, ess_file):
        global elara
        global image_width
        global image_height
        global blue_rect
        global lock

        elara_directory = bpy.context.user_preferences.addons["ElaraForBlender"].preferences.elara_directory
        print(elara_directory)

        lock = threading.Lock()
        elara = c.windll.LoadLibrary(elara_directory + "/bin/liber.dll")

        pixel_count = self.size_x * self.size_y
        image_width = self.size_x
        image_height = self.size_y
        # The framebuffer is defined as a list of pixels, each pixel
        # itself being a list of R,G,B,A values
        blue_rect = [[0.0, 0.0, 0.0, 1.0]] * pixel_count

        elara.ei_create_thread.argtypes = [c.CFUNCTYPE(c.c_uint32, c.c_void_p), c.c_void_p, c.POINTER(c.c_uint32)]
        elara.ei_create_thread.restype = c.c_void_p
        elara.ei_get_last_render_params.argtypes = [c.POINTER(eiRenderParameters)]
        elara.ei_echo.argtypes = [c.c_char_p]
        elara.ei_render_run.argtypes = [c.c_char_p, c.c_char_p, c.c_char_p]
        elara.ei_set_low_thread_priority.argtypes = [c.c_void_p]
        elara.ei_job_set_process.argtypes = [c.POINTER(eiProcess)]
        elara.ei_parse2.argtypes = [c.c_char_p, c.c_bool]
        elara.ei_parse2.restype = c.c_bool
        elara.ei_add_shader_searchpath.argtypes = [c.c_char_p]
        elara.ei_verbose.argtypes = [c.c_char_p]
        elara.ei_job_aborted.restype = c.c_bool
        elara.ei_job_get_percent.restype = c.c_double
        elara.ei_wait_thread.argtypes = [c.c_void_p]
        elara.ei_delete_thread.argtypes = [c.c_void_p]
        elara.ei_db_type.argtypes = [c.POINTER(c.c_uint)]
        elara.ei_db_type.restype = c.c_int
        elara.ei_db_access.argtypes = [c.POINTER(c.c_uint)]
        elara.ei_db_access.restype = c.c_void_p
        elara.ei_framebuffer_cache_init.argtypes = [c.POINTER(eiFrameBufferCache), c.POINTER(c.c_uint), c.c_int, c.c_int, c.c_float, c.c_int, c.POINTER(eiFrameBufferCache)]
        elara.ei_framebuffer_cache_get_final.argtypes = [c.POINTER(eiFrameBufferCache), c.c_int, c.c_int, c.c_void_p]
        elara.ei_db_end.argtypes = [c.POINTER(c.c_uint)]
        elara.ei_framebuffer_cache_exit.argtypes = [c.POINTER(eiFrameBufferCache)]
        elara.ei_override_int.argtypes = [c.c_char_p, c.c_char_p, c.c_int]
        elara.ei_override_scalar.argtypes = [c.c_char_p, c.c_char_p, c.c_float]
        elara.ei_job_abort.argtypes = [c.c_bool]

        elara.ei_context()
        elara.ei_verbose(c.c_char_p(b"none"))

        bin_path = elara_directory + "/bin/"
        shader_path = elara_directory + "/shaders/"
        elara.ei_add_shader_searchpath(c.c_char_p(bin_path.encode('utf-8')))
        elara.ei_add_shader_searchpath(c.c_char_p(shader_path.encode('utf-8')))

        elara.ei_override_int(c.c_char_p(b"camera"), c.c_char_p(b"res_x"), image_width)
        elara.ei_override_int(c.c_char_p(b"camera"), c.c_char_p(b"res_y"), image_height)
        elara.ei_override_scalar(c.c_char_p(b"camera"), c.c_char_p(b"aspect"), float(image_width) / float(image_height))

        if elara.ei_parse2(c.c_char_p(ess_file.encode('utf-8')), True):
            print("scusess")
        else:
            print("fail")

        render_params = eiRenderParameters()
        base = eiProcess()

        elara.ei_get_last_render_params(c.byref(render_params))

        base.pass_started = rprocess_pass_started
        base.pass_finished = rprocess_pass_finished
        base.job_started = rprocess_job_started
        base.job_finished = rprocess_job_finished
        base.info = rprocess_info

        elara.ei_job_set_process(c.byref(base))
        elara.ei_render_prepare()
        renderThread = elara.ei_create_thread(render_callback, c.byref(render_params), None)
        elara.ei_set_low_thread_priority(renderThread)
        while True:
            elara.ei_sleep(50)
            if not(elara.ei_job_aborted()):
                job_percent = elara.ei_job_get_percent()
                self.update_progress(job_percent * 0.01)
            else:
                elara.ei_wait_thread(renderThread)
                elara.ei_delete_thread(renderThread)
                print("render finish")
                break

            if self.test_break():
                elara.ei_job_abort(True)
                elara.ei_wait_thread(renderThread)
                elara.ei_delete_thread(renderThread)
                break

            result = self.begin_result(0, 0, self.size_x, self.size_y)
            layer = result.layers[0].passes["Combined"]
            lock.acquire()
            layer.rect = blue_rect
            self.end_result(result)
            lock.release()

        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]
        layer.rect = blue_rect
        self.end_result(result)
        elara.ei_render_cleanup()
        elara.ei_job_set_process(None)
        elara.ei_end_context()
def register():
    # Register the RenderEngine
    bpy.utils.register_class(ElaraRenderEngine)

    # RenderEngines also need to tell UI Panels that they are compatible
    # Otherwise most of the UI will be empty when the engine is selected.
    # In this example, we need to see the main render image button and
    # the material preview panel.
    from bl_ui import (
            properties_render,
            properties_material,
            )
    
    properties_render.RENDER_PT_render.COMPAT_ENGINES.add(ElaraRenderEngine.bl_idname)
    properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add(ElaraRenderEngine.bl_idname)
    #properties_material.MATERIAL_PT_preview.COMPAT_ENGINES.add(ElaraRenderEngine.bl_idname)

def unregister():
    bpy.utils.unregister_class(ElaraRenderEngine)

    from bl_ui import (
            properties_render,
            properties_material,
            )
    properties_render.RENDER_PT_render.COMPAT_ENGINES.remove(ElaraRenderEngine.bl_idname)
    properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.remove(ElaraRenderEngine.bl_idname)
    #properties_material.MATERIAL_PT_preview.COMPAT_ENGINES.remove(ElaraRenderEngine.bl_idname)