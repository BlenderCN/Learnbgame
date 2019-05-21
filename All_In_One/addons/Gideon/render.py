import os.path

import bpy
from math import *

from . import sync
from . import engine
from . import source
import ctypes

class GideonRenderEngine(bpy.types.RenderEngine):
    bl_idname = 'GIDEON_RENDER_ENGINE'
    bl_label = "Gideon"
    bl_use_shading_nodes = True
    use_highlight_tiles = True
    libgideon = engine.load_gideon(os.path.join(os.path.dirname(__file__), "libgideon.so"))
    
    def __init__(self):
        self.gideon = GideonRenderEngine.libgideon
        self.loader = source.SourceLoader(self.gideon)
        self.context = engine.create_context(self.gideon)
        self.ready = False

    def __del__(self):
        if hasattr(self, "context"):
            engine.destroy_context(self.gideon, self.context)
            
    def update(self, data, scene):
        self.update_stats("", "Compiling render kernel")

        try:
            self.ready = False
            kernel = self.rebuild_kernel(scene)

            #sync this scene with gideon
            self.update_stats("", "Syncing scene data")
            gd_scene = sync.GideonScene(self.gideon, kernel)
            sync.convert_scene(scene, gd_scene)
            engine.context_set_scene(self.gideon, self.context, gd_scene.scene)

            #build the BVH
            self.update_stats("", "Building BVH")
            engine.context_build_bvh(self.gideon, self.context)

            self.ready = True
        except RuntimeError:
            self.update_stats("", "Render Update Failed")

    #Reports any errors to the console.
    def report_render_error(self, error_short, error_msg):
        print(error_msg)
        self.report({'ERROR'}, error_short)
    
    #Compiles the render kernel.
    def rebuild_kernel(self, scene):
        #load and compile all programs
        self.loader.set_search_paths([bpy.path.abspath(scene.gideon.std_path),
                                      bpy.path.abspath(scene.gideon.source_path)])
                                     
        program = engine.create_program(self.gideon, "render", self.loader)

        for source in scene.gideon.sources:
            engine.program_load_source(self.gideon, program, source.name)

        error_cb = lambda error_str : self.report_render_error("Compiler Error - Check Console",
                                                               error_str.decode('ascii'))
        
        kernel = engine.program_compile(self.gideon, program, error_cb)
        if kernel != None:
            engine.context_set_kernel(self.gideon, self.context, kernel)

            #rebuild the function lists
            scene.gideon.shader_list.clear()
            scene.gideon.entry_list.clear()
            
            #lookup material function list
            func_list = engine.get_material_list(self.gideon, program)
            for func in func_list:
                f = scene.gideon.shader_list.add()
                f.name = func[0]
                f.intern_name = func[1]

            #lookup entry points
            func_list = engine.get_entry_list(self.gideon, program)
            for func in func_list:
                f = scene.gideon.entry_list.add()
                f.name = func[0]
                f.intern_name = func[1]
        
        engine.destroy_program(self.gideon, program)

        if kernel == None:
            raise RuntimeError("Could not compile kernel.")
        
        return kernel

    def render(self, scene):
        if not self.ready:
            return

        #call the renderer's entry point
        pixel_scale = scene.render.resolution_percentage * 0.01
        x_pixels = floor(pixel_scale * scene.render.resolution_x)
        y_pixels = floor(pixel_scale * scene.render.resolution_y)

        tile_x = scene.render.tile_x
        tile_y = scene.render.tile_y

        num_x_tiles = int(ceil(float(x_pixels) / tile_x))
        num_y_tiles = int(ceil(float(y_pixels) / tile_y))
        
        start_px = 0
        start_py = 0

        print("Num Tiles: ", num_x_tiles, num_y_tiles)
        print("Entry Point: ", scene.gideon.entry_point)

        try:
            entry_obj = scene.gideon.entry_list[scene.gideon.entry_point]
        except KeyError:
            self.report({'ERROR'}, "Invalid choice of render entry function")
            return

        total_tiles = num_x_tiles * num_y_tiles
        completed_tiles = 0
        
        for ty in range(num_y_tiles):
            end_py = min(start_py + tile_y, y_pixels)
            th = end_py - start_py

            for tx in range(num_x_tiles):
                end_px = min(start_px + tile_x, x_pixels)
                tw = end_px - start_px
                
                r = self.begin_result(start_px, start_py, tw, th)
                
                float4_ty = 4 * ctypes.c_float
                result = (tw * th * float4_ty)()
                engine.render_tile(self.gideon, self.context,
                                   entry_obj.intern_name.encode('ascii'),
                                   start_px, start_py, tw, th,
                                   result)
                r.layers[0].rect = result
                
                self.end_result(r)

                completed_tiles += 1
                self.update_stats("", str.format("Completed {0}/{1} tiles", completed_tiles, total_tiles))
                start_px += tile_x

                if self.test_break():
                    return
                
            start_px = 0
            start_py += tile_y    

class KERNEL_FUNCTION_LIST_update(bpy.types.Operator):
    bl_idname = "gideon.update_kernel_functions"
    bl_label = "Update Kernel Function List"
    bl_description = "Recompiles the kernel and rebuilds the entry/material function list"

    def report_compile_error(self, message):
        self.report({'ERROR'}, "Compile Error - Check Console")
        print(message)

    def invoke(self, context, event):
        #load and compile all programs
        scene = context.scene
        libgideon = GideonRenderEngine.libgideon
        loader = source.SourceLoader(libgideon)
        loader.set_search_paths([bpy.path.abspath(scene.gideon.std_path),
                                 bpy.path.abspath(scene.gideon.source_path)])
                                     
        program = engine.create_program(libgideon, "test", loader)

        for src_prop in scene.gideon.sources:
            engine.program_load_source(libgideon, program, src_prop.name)

        error_cb = lambda error_str : self.report_compile_error(error_str.decode('ascii'))
        
        kernel = engine.program_compile(libgideon, program, error_cb)
        if kernel != None:
            #clear old list
            scene.gideon.shader_list.clear()
            scene.gideon.entry_list.clear()

            #lookup material function list
            func_list = engine.get_material_list(libgideon, program)
            for func in func_list:
                f = scene.gideon.shader_list.add()
                f.name = func[0]
                f.intern_name = func[1]

            #lookup entry points
            func_list = engine.get_entry_list(libgideon, program)
            for func in func_list:
                f = scene.gideon.entry_list.add()
                f.name = func[0]
                f.intern_name = func[1]
            
        #cleanup
        engine.destroy_compiled(libgideon, kernel)
        engine.destroy_program(libgideon, program)
        return {'FINISHED'}
