import bpy, ctypes
from . import scene, mesh, engine, camera, lamp

#Converts all scene objects into a usable format for the renderer.
def SyncScene(bl_scene, is_preview):
    s = scene.Scene()
    s.set_camera(bl_scene)
    
    for obj in bl_scene.objects:
        try:
            #try to load this object as a mesh first
            print("Loading Object:", obj.name)
            m = mesh.LoadMeshObject(bl_scene, obj, is_preview)
            s.add_mesh_object(m)
        except RuntimeError:
            if obj.type == 'LAMP':
                print("Loading Lamp:", obj.name)
                lamp = obj.data
                s.add_lamp(obj.location, lamp.energy, lamp.color, lamp.shadow_soft_size)
        
    return s

#Python Wrapper around Gideon's Scene type.
class GideonScene:
    
    def __init__(self, libgideon, renderer):
        self.gideon = libgideon
        self.scene = engine.create_scene(self.gideon)
        self.renderer = renderer
        
    def __del__(self):
        pass
    
    #Converts a mesh object to Gideon's format.
    def add_mesh(self, bl_scene, obj, is_preview = False):
        #apply any modifiers and generate the mesh in world coordinates
        gd_mesh = mesh.LoadMeshObject(bl_scene, obj, is_preview)

        #map material indices to shader handles
        shader_arr = (len(gd_mesh['shaders'])*ctypes.c_void_p)()
        volume_arr = (len(gd_mesh['shaders'])*ctypes.c_void_p)()

        for shader_idx in range(len(gd_mesh['shaders'])):
            material_slot = gd_mesh['shaders'][shader_idx]
            mat = obj.material_slots[material_slot]
            
            shader_key = mat.material.gideon.shader
            shader_func = None
            if len(shader_key) > 0:
                try:
                    shader_obj = bl_scene.gideon.shader_list[shader_key]
                    shader_func = engine.lookup_function(self.gideon, self.renderer, shader_obj.intern_name)
                except KeyError:
                    pass

            volume_key = mat.material.gideon.volume
            volume_func = None
            if len(volume_key) > 0:
                try:
                    volume_obj = bl_scene.gideon.shader_list[volume_key]
                    volume_func = engine.lookup_function(self.gideon, self.renderer, volume_obj.intern_name)
                except KeyError:
                    pass
                
            shader_arr[shader_idx] = shader_func
            volume_arr[shader_idx] = volume_func
        
        gd_mesh['shaders'] = shader_arr
        gd_mesh['volumes'] = volume_arr
        
        #add the mesh to gideon
        obj_id = engine.scene_add_mesh(self.gideon, self.scene, gd_mesh)

        #add all the mesh's attributes
        for texcoord in gd_mesh['texcoords'].keys():
            texcoord_arr = gd_mesh['texcoords'][texcoord]
            engine.mesh_add_texcoord(self.gideon, self.scene, obj_id,
                                     "uv:" + texcoord, texcoord_arr)

        for vcolor in gd_mesh['vertex_colors'].keys():
            vcolor_arr = gd_mesh['vertex_colors'][vcolor]
            engine.mesh_add_vertex_color(self.gideon, self.scene, obj_id,
                                         "attribute:" + vcolor, vcolor_arr)
            
    #Adds a lamp to the scene.
    def add_lamp(self, lamp_object):
        gd_lamp = lamp.convert(lamp_object)
        engine.scene_add_lamp(self.gideon, self.scene, gd_lamp)

    #Sets the main camera of the Gideon scene.
    def set_camera(self, bl_scene):
        gd_cam = camera.convert(bl_scene.camera, bl_scene)
        engine.scene_set_camera(self.gideon, self.scene, gd_cam)

    #Builds the scene's BVH.
    def build_bvh(self):
        return engine.build_bvh(self.gideon, self.scene)

#Convert a Blender Scene to a Gideon Scene
def convert_scene(bl_scene, gd_scene, is_preview = False):
    for obj in bl_scene.objects:
        if obj.type == 'MESH':
            gd_scene.add_mesh(bl_scene, obj, is_preview)
        elif obj.type == 'LAMP':
            gd_scene.add_lamp(obj)
            pass
    
    gd_scene.set_camera(bl_scene)
