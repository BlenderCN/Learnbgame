#Copyright (C) 2012 Henrique P. K. PÃ©rigo
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
 
 
#Thanks everybody in the blender artists forum for their thougts and doubts, especially CoDEmanX for the update in the UI!
 
# Add-on info 
bl_info = {
    "name": "Mesh from particles",
    "description": "bakes a sequence of meshes from a particle system",
    "author": "Henrique P. K. Perigo <hperigo@gmail.com>",
    "version": (1, 3),
    "blender": (2, 6, 4),
    "location": "View3D > Add > Mesh",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "http://blenderartists.org/forum/showthread.php?255694-Addon-Mesh-from-particles"
                "none",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"
                   "func=detail&aid=<number>",
    "category": "Learnbgame",
} 

import bpy
from bpy.props import *
import time
 
 

def animateMesh(mainObj):
    frame = bpy.context.scene.frame_current
    end_frame = bpy.data.scenes['Scene'].frame_end
    start_frame = bpy.data.scenes['Scene'].frame_start
    obj = mainObj
    
    matName = obj['bake_material']
    mat = bpy.data.materials[matName] # assign a material for every mesh, on every frame
 
    if(frame < end_frame and frame > start_frame):
        mesh = bpy.data.meshes['FluidMesh_' + str(frame)] #the baked meshes, need to have the name "MetaMesh_" + frame
        obj.data = mesh
        obj.data.use_fake_user = True
        if obj.material_slots[0].material != mat:
            obj.material_slots[0].material = mat
        return 1.0
    else:
        return 0.0
 

def deleteBakedMesh():
    for m in bpy.data.meshes:
        name = m.name
        name_split = name.split("_", 1)
        if name_split[0] == 'FluidMesh':
            m.use_fake_user = False
            print(name_split)

def makeMesh(context):
    
    print('start')
    start_time = time.time()
    scene = bpy.context.scene
    start = scene.frame_start
    end = scene.frame_end
    
    scene.frame_current = start    

    
    ob = bpy.context.object
    ob2 = bpy.context.object
    
    partName = ob['bake_particle_system']
    part = ob.particle_systems[partName].settings
    part.render_type = 'OBJECT'
    
    matName = ob['bake_material']
    mat = bpy.data.materials[matName]
    
    scale = scene.MetaBallScale
    resolution = scene.MetaBallResolution
    
    while scene.frame_current <= end:
    
        bpy.ops.object.metaball_add(type='BALL', view_align=False, enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0),  layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        
        for obs in bpy.data.objects:
            obs.select = False
            if obs.type == 'META':
                ob = obs
                
            
        ob.select = True
        bpy.context.scene.objects.active = ob
        
        ob.data.resolution = resolution
    
        part.dupli_object = ob
        bpy.ops.object.editmode_toggle()
        
        bpy.ops.transform.resize(value=(scale, scale, scale), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), texture_space=False, release_confirm=False)
        
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.convert(target='MESH', keep_original= False)
        
        for obs in bpy.data.objects:
            obs.select = False
            if obs.name == 'Mball.001':
                ob = obs
                
            
        ob.select = True
        bpy.context.scene.objects.active = ob
 
        ob.data.name  = 'FluidMesh_' + str(scene.frame_current)        

        ob.data.materials.append(mat)
        print("elapsed time: " + str(time.clock() - start_time) )
        print("frame: " + str(scene.frame_current))
        
        bpy.ops.object.delete(use_global = False)
        scene.frame_current += 1
    
    ob2.select = True
    bpy.context.scene.objects.active = ob2
    bpy.ops.object.animate_baked_mesh()



class MakeMeshOperator(bpy.types.Operator):
    '''Make an sequence of meshes from a givem particle system'''
    bl_idname = "object.bake_mesh_from_particles"
    bl_label = "Bake mesh"
    

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
        
        
    def execute(self, context):
        print("MAKE MESH CALL")
        makeMesh(context)
        return {'FINISHED'}
    
class AnimateMeshOperator(bpy.types.Operator):
    '''Animates active object with baked mesh from particles'''
    bl_idname = "object.animate_baked_mesh"
    bl_label = "Animate mesh"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
        
    def execute(self, context):
        bpy.app.driver_namespace["animateMesh"] = animateMesh
        ob = bpy.context.object
        ob["meshDriver"] = 1.0
        ob.driver_add('["meshDriver"]')
        ob.animation_data.drivers[0].driver.expression = "animateMesh(bpy.data.objects['" + ob.name + "'])"
        
        print("FINISHED")
        return {'FINISHED'}
    
class DeleteMeshOperator(bpy.types.Operator):
    '''Deletes baked mesh from particles'''
    bl_idname = "object.delete_baked_mesh"
    bl_label = "Delete baked mesh"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
        
    def execute(self, context):
        deleteBakedMesh()
        
        print("FINISHED")
        return {'FINISHED'}

class MeshFromParticlesUI(bpy.types.Panel):
    """"Particle mesh baker"""
    
    bl_label = "Mesh from particles"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    #"
    #
    
    bpy.types.Object.bake_particle_system = StringProperty(name="Particle System:")
    bpy.types.Object.bake_material = StringProperty(name="Material:")
     
    
    bpy.types.Scene.MetaBallScale = FloatProperty(name = "Metaball scale", default = 2.0, description = "Scale for the metalBall used for mesh creation")
    
    bpy.types.Scene.MetaBallResolution = FloatProperty(name = "Metaball resolution", default = .3, min = .1, max = 2.0, description = "Resolution for the metalBall used for mesh creation")

    
    

 
    @classmethod
    def poll(self, context):
        return context.object.type == 'MESH'
       
    def draw(self, context):
        layout = self.layout
       
        ob = context.object
       
        split = layout.split(0.32)
        split.label(text="Active Object:")
        split.label(text=" " + ob.name, icon='OBJECT_DATAMODE')
       
        layout.prop_search(ob, "bake_particle_system", ob, "particle_systems")
        layout.prop_search(ob, "bake_material", ob, "material_slots")
        layout.prop(bpy.context.scene, 'MetaBallScale')
        layout.prop(bpy.context.scene, 'MetaBallResolution')
       
        col = layout.row(align=True)
        col.label("Mesh:")
        col.operator("object.bake_mesh_from_particles", "Bake")
        col.operator("object.animate_baked_mesh", "Animate")
        col.operator("object.delete_baked_mesh", "Delete baked")
        
        


    

def register():
    bpy.utils.register_class(MakeMeshOperator)
    bpy.utils.register_class(AnimateMeshOperator)
    bpy.utils.register_class(DeleteMeshOperator)
    
    bpy.utils.register_class(MeshFromParticlesUI)
    
def unregister():
    bpy.utils.unregister_class(MakeMeshOperator)
    bpy.utils.unregister_class(AnimateMeshOperator)
    bpy.utils.unregister_class(DeleteMeshOperator)
        
    bpy.utils.unregister_class(MeshFromParticlesUI)

if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.object.bake_mesh_from_particles()
    #bpy.ops.object.animate_baked_mesh()