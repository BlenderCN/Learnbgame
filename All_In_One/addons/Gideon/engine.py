from ctypes import *
import bpy

#Loads the gideon library.
def load_gideon(path):
    cdll.LoadLibrary(path)
    libgideon = CDLL('libgideon.so')

    init = libgideon.gd_api_initialize
    init.argtypes = [c_char_p]
    init('libgideon.so'.encode('ascii'))
    return libgideon

#-- Helper Functions --#

def string_copy(libgideon, s):
    copy = libgideon.gd_api_string_copy
    copy.restype = c_void_p
    copy.argtypes = [c_char_p]
    return copy(s.encode('ascii'))

def set_status(libgideon, s_ptr, s):
    set_status = libgideon.gd_api_set_status
    set_status.restype = None
    set_status.argtypes = [c_void_p, c_int]
    set_status(s_ptr, s)

#-- Context Management --#

#Creates a new gideon context.
def create_context(libgideon):
    create = libgideon.gd_api_create_context
    create.restype = c_void_p
    return create()

#Destroys a gideon context.
def destroy_context(libgideon, context):
    destroy = libgideon.gd_api_destroy_context
    destroy.argtypes = [c_void_p]
    destroy(context)

#Sets the context's render kernel.
def context_set_kernel(libgideon, context, kernel):
    set_kernel = libgideon.gd_api_context_set_kernel
    set_kernel.argtypes = [c_void_p, c_void_p]
    set_kernel(context, kernel)

#Sets the context's scene.
def context_set_scene(libgideon, context, scene):
    set_scene = libgideon.gd_api_context_set_scene
    set_scene.argtypes = [c_void_p, c_void_p]
    set_scene(context, scene)

#Rebuild's the BVH for the context's current scene.
def context_build_bvh(libgideon, context):
    build = libgideon.gd_api_context_build_bvh
    build.argtypes = [c_void_p]
    build(context)

#-- Program Management --#

#Returns a handle to the renderer program.
def create_program(libgideon, name,
                   source_loader):
    create = libgideon.gd_api_create_program
    create.restype = c_void_p

    create.argtypes = [c_char_p,
                       source_loader.path_resolver_cb_type,
                       source_loader.source_loader_cb_type]

    return create(name.encode('ascii'),
                  source_loader.get_resolve_cb(), source_loader.get_load_cb())

#Destroys a renderer program.
def destroy_program(libgideon, prog):
    destroy = libgideon.gd_api_destroy_program
    destroy.argtypes = [c_void_p]
    destroy(prog)

#Instructs the program to open the given source file.
def program_load_source(libgideon, prog, filename):
    loader = libgideon.gd_api_program_load_source
    loader.argtypes = [c_void_p, c_char_p]
    loader(prog, filename.encode('ascii'))

#Compiles the given program.
def program_compile(libgideon, prog, error_cb):
    cb_func_type = CFUNCTYPE(None, c_char_p)
    compiler = libgideon.gd_api_program_compile
    compiler.restype = c_void_p
    compiler.argtypes = [c_void_p, cb_func_type]

    return compiler(prog, cb_func_type(error_cb))

#Destroys a compiled program.
def destroy_compiled(libgideon, prog):
    destroy = libgideon.gd_api_destroy_renderer
    destroy.argtypes = [c_void_p]
    destroy(prog)

#Lists all the material functions (may only be called after compilation).
def get_material_list(libgideon, prog):
    func_list = []
    on_func = lambda name, full_name : func_list.append((name.decode('ascii'), full_name.decode('ascii')))

    cb_func_type = CFUNCTYPE(None, c_char_p, c_char_p)

    do_list = libgideon.gd_api_list_material_functions
    do_list.restype = None
    do_list.argtypes = [c_void_p, cb_func_type]
    do_list(prog, cb_func_type(on_func))

    return func_list

#Lists all the entry point functions (may only be called after compilation).
def get_entry_list(libgideon, prog):
    func_list = []
    on_func = lambda name, full_name : func_list.append((name.decode('ascii'), full_name.decode('ascii')))

    cb_func_type = CFUNCTYPE(None, c_char_p, c_char_p)

    do_list = libgideon.gd_api_list_entry_functions
    do_list.restype = None
    do_list.argtypes = [c_void_p, cb_func_type]
    do_list(prog, cb_func_type(on_func))

    return func_list

#Returns a pointer to a function inside the program.
def lookup_function(libgideon, renderer, name):
    lookup = libgideon.gd_api_lookup_function
    lookup.restype = c_void_p
    lookup.argtypes = [c_void_p, c_char_p]
    return lookup(renderer, name.encode('ascii'))

#Creates a new scene object.
def create_scene(libgideon):
    create = libgideon.gd_api_create_scene
    create.restype = c_void_p
    return create()

#Deletes a scene object.
def destroy_scene(libgideon, scene):
    destroy = libgideon.gd_api_destroy_scene
    destroy.argtypes = [c_void_p]
    destroy(scene)

#Creates a BVH for the given scene.
def build_bvh(libgideon, scene):
    build = libgideon.gd_api_build_bvh
    build.restype = c_void_p
    build.argtypes = [c_void_p]

    return build(scene)

#Destroys a BVH.
def destroy_bvh(libgideon, bvh):
    destroy = libgideon.gd_api_destroy_bvh
    destroy.argtypes = [c_void_p]
    destroy(bvh)

#Adds a mesh object to a scene, returns its object ID.
def scene_add_mesh(libgideon, scene, mesh):
    add_mesh = libgideon.gd_api_add_mesh
    add_mesh.argtypes = [c_void_p,
                         c_uint, POINTER(c_float), POINTER(c_float),
                         c_uint, POINTER(c_int), POINTER(c_void_p), POINTER(c_void_p)]
    add_mesh.restype = c_int
    
    return add_mesh(scene,
                    len(mesh['vertices']), mesh['vertices'], mesh['vertex_norms'],
                    len(mesh['triangles']), mesh['triangles'],
                    mesh['shaders'], mesh['volumes'])

#Adds texture coordinates (vec2 attributes) to a mesh object.
def mesh_add_texcoord(libgideon, scene, object_id, attr_name,
                      tcoord_data):
    add_texcoord = libgideon.gd_api_add_texcoord
    add_texcoord.argtypes = [c_void_p, c_int,
                             c_char_p, POINTER(c_float), c_uint]

    add_texcoord(scene, object_id, attr_name.encode('ascii'),
                 tcoord_data, len(tcoord_data))
    
#Adds vertex colors (vec3 attributes) to a mesh object.
def mesh_add_vertex_color(libgideon, scene, object_id, attr_name,
                          vcolor_data):
    add_vcolor = libgideon.gd_api_add_vertex_color
    add_vcolor.argtypes = [c_void_p, c_int,
                           c_char_p, POINTER(c_float), c_uint]

    add_vcolor(scene, object_id, attr_name.encode('ascii'),
               vcolor_data, len(vcolor_data))
    
    
#Sets the scene's camera.
def scene_set_camera(libgideon, scene, camera):
    set_camera = libgideon.gd_api_set_camera
    set_camera.argtypes = [c_void_p,
                           c_int, c_int,
                           c_float, c_float,
                           POINTER(c_float), POINTER(c_float)]
    set_camera(scene,
               camera['resolution'][0], camera['resolution'][1],
               camera['clip'][0], camera['clip'][1],
               camera['camera_to_world'], camera['raster_to_camera'])

#Adds a new lamp to the scene.
def scene_add_lamp(libgideon, scene, lamp):
    add_lamp = libgideon.gd_api_add_lamp
    add_lamp.argtypes = [c_void_p, c_float,
                         c_float, c_float, c_float,
                         c_float, POINTER(c_float)]
    add_lamp(scene,
             lamp['energy'],
             lamp['color'][0], lamp['color'][1], lamp['color'][2],
             lamp['size'],
             lamp['location'])
             

#Renders a tile.
def render_tile(libgideon, context,
                entry_name,
                tile_x, tile_y, tile_w, tile_h,
                output_buffer):
    render = libgideon.gd_api_render_tile
    
    render.argtypes = [c_void_p, c_char_p,
                       c_int, c_int, c_int, c_int,
                       POINTER(4*c_float)]
    
    render(context, entry_name,
           tile_x, tile_y, tile_w, tile_h,
           output_buffer)
    
