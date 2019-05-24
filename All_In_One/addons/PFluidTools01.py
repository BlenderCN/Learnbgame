bl_info = {
    "name": "Particle Fluid Tools",
    "author": "bashi",
    "version": (0, 1),
    "blender": (2, 5, 9),
    "api": 33333,
    "location": "View3D > Toolbar",
    "description": "Converts Particles to Metaball or Mesh",
    "warning": "alpha",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}



import bpy

bpy.types.Scene.pfluid_size = bpy.props.FloatProperty(name = "MBall Size",default = 2, min=0.01, max=10)
bpy.types.Scene.pfluid_resolution = bpy.props.FloatProperty(name = "MBall Resolution",default = 0.8, min=0.05, max=1.0)

bpy.types.Scene.pfluid_mesh_subsurf_level = bpy.props.IntProperty(name = "Mesh Subsurf",default = 0)
bpy.types.Scene.pfluid_mesh_smooth_factor = bpy.props.FloatProperty(name = "Mesh Smooth Factor",default = 2, min=0.0, max=2.5)
bpy.types.Scene.pfluid_mesh_smooth_iterations = bpy.props.IntProperty(name = "Mesh Smooth Iterations",default = 30, min=0 , max=200)

bpy.types.Scene.pfluid_frame_start = bpy.props.IntProperty(name = "MBall Frame Start",default = 1)
bpy.types.Scene.pfluid_frame_end = bpy.props.IntProperty(name = "MBall Frame End",default = 250)






class PFluid_Tools(bpy.types.Panel):
    bl_label = "PFluid Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        
        scene = context.scene
        object = context.object
        #mball = object.data
        
        self.layout.prop(scene, "pfluid_size")
        self.layout.prop(scene, "pfluid_resolution")
        self.layout.operator("particle.pfluid_make_mball", icon="META_DATA")
        #self.layout.prop(object.data, "pfluid_size")
        self.layout.operator("mball.pfluid_update", icon="FILE_REFRESH")
        
        
        self.layout.prop(scene, "pfluid_mesh_subsurf_level")
        self.layout.prop(scene, "pfluid_mesh_smooth_factor")
        self.layout.prop(scene, "pfluid_mesh_smooth_iterations")
        self.layout.operator("mball.pfluid_mesh", icon="OUTLINER_OB_META")
        
        self.layout.prop(scene, "pfluid_frame_start")
        self.layout.prop(scene, "pfluid_frame_end")
        self.layout.operator("mball.pfluid_mesh_seq", icon="OUTLINER_OB_CAMERA")
        #self.layout.operator("import.objseq")








#Makes MBall Object of Particles
class OBJECT_OT_MakeMBall(bpy.types.Operator):
    bl_idname = "particle.pfluid_make_mball"
    bl_label = "Particle to MBall"
    
    def execute(self, context):   
               
        #Get Alive Particles 
        obj = context.selected_objects
        
        particles_alive = []
        
        for ob in range(0, len(obj)):
            
            for part in range(0, len(obj[ob].particle_systems)):
            
                particles = obj[ob].particle_systems[part].particles
                particle_count = len(particles)
                    
                for i in range(0, particle_count):
                    var = 0
                    #global particles_alive
                    
                    if 'ALIVE' in particles[i].alive_state:
                        particles_alive.append(particles[i])
                        var += 1
            
                particles = particles_alive
              

        
        
        
        #Start making Mball
        
        
        bpy.ops.object.metaball_add(type='BALL', enter_editmode=True, location=(particles[0].location))
        
        #global mball
        #global metaball
        mball = bpy.context.selected_objects[0]
        metaball = mball.data
        metaball.resolution = bpy.context.scene.pfluid_resolution
        metaball.render_resolution = bpy.context.scene.pfluid_resolution
        metaball.update_method = 'NEVER'
        #metaball.threshold = hull_threshold
        
        #Set Metaball Size
        hull_size = bpy.context.scene.pfluid_size
        
        mball.scale[0] = particles[0].size*hull_size
        mball.scale[1] = particles[0].size*hull_size
        mball.scale[2] = particles[0].size*hull_size
        
        
        
        for i in range(1,len(particles)):
            bpy.ops.mball.duplicate_metaelems(mode='TRANSLATION')
            
            location = particles[i].location
            relocation = particles[i-1].location *-1
            #print(i)
            #print(location)
           
            bpy.ops.transform.translate(value=(relocation))
            bpy.ops.transform.translate(value=(location))
            
            
        bpy.ops.object.editmode_toggle()
        #bpy.ops.object.select_all()
       
        #for i in range(len(obj)):
        #    obj[i].select = True
                   
        return{'FINISHED'}



#Converts MBall to Mesh and add Subsurf and Smooth modifier
class OBJECT_OT_MBallMesh(bpy.types.Operator):
    bl_idname = "mball.pfluid_mesh"
    bl_label = "Make Mesh"

    def execute(self, context):  
        
        obj = context.selected_objects
        
        def convert(metaball):    
            metaball.update_method='FAST'
                
            #Convert to Mesh
            bpy.ops.object.convert(target='MESH')
              
            mesh = bpy.context.selected_objects[0]
                
            #Add Subsurf level 1
            scene = bpy.context.scene
            
            bpy.ops.object.modifier_add(type='SUBSURF')
            mesh.modifiers['Subsurf'].levels=scene.pfluid_mesh_subsurf_level
            mesh.modifiers['Subsurf'].render_levels=scene.pfluid_mesh_subsurf_level
                
            #Add Smooth
            bpy.ops.object.modifier_add(type='SMOOTH')
            mesh.modifiers['Smooth'].factor = scene.pfluid_mesh_smooth_factor
            mesh.modifiers['Smooth'].iterations = scene.pfluid_mesh_smooth_iterations
            
            mball = bpy.context.selected_objects
                  
        #Check if Object is Mesh or Mball and execute Convert
        
        
        count = 0
        if len(obj) == 1:
            count = 1
        else:
            count = len(obj)-1
        
        for i in range(0, count):
            if obj[i].type == 'MESH':
                print('is Mesh')
                bpy.ops.particle.pfluid_make_mball()
                obj = context.selected_objects
                metaball = obj[i].data
                convert(metaball)
            else:
                metaball = obj[i].data
                convert(metaball)
                    
            

        
        return{'FINISHED'}
        


#Export given Obj to filepath (.obj)
def export_obj(obj, path):
    
    
    frame = str(bpy.context.scene.frame_current)
    
    bpy.ops.export_scene.obj(filepath=filepath+"ObjSequence"+frame+".obj",filter_glob="*.obj", use_selection=True)
 


#Run MBall, make_mesh and Export -obj for Range 
class OBJECT_OT_Mesh_Sequence(bpy.types.Operator):
    bl_idname = "mball.pfluid_mesh_seq"
    bl_label = "Mesh Sequence"
    #def mesh_sequence(frame_start, frame_end):

    def execute(self, context):
        
        
        frame_start = context.scene.pfluid_frame_start
        frame_end = context.scene.pfluid_frame_end
        obj = context.selected_objects
        
        bpy.ops.object.add()
        empty = bpy.context.object
        empty.name = "PFluid Meshes"
        bpy.ops.object.select_all()
        
        mat = bpy.data.materials.new("Fluid")
        
        
        for i in range(len(obj)):
            obj[i].select = True
        
        bpy.context.scene.frame_set(frame_start)
                
        for i in range(frame_start, frame_end+1):
            frame = i + frame_start
            
            
            
                        
            bpy.ops.mball.pfluid_mesh()
            bpy.context.object.parent = empty        
            bpy.context.object.data.materials.append(mat)
            
            set_visibility(context.object)
            
            #bpy.ops.object.select_all()
            for i in range(len(obj)):
                obj[i].select = True
            
            
            
            bpy.context.scene.frame_set(frame)
        return{'FINISHED'}


#Import .obj from Filepath from Range


class OBJECT_OT_Set_Mball_Size(bpy.types.Operator):
    bl_idname = "import.objseq"
    bl_label = "Import .obj Seq"

    #def mball_size(size):
    def execute(self, context):
        bpy.ops.group.create(name="ObjSequence")
        
        bpy.ops.object.add(type='EMPTY')
        empty = bpy.context.selected_objects[0]
        empty.name = "ObjSequence"
        
        scene = context.scene
        
        frame_start = scene.pfluid_frame_start
        frame_end = scene.pfluid_frame_end
                
        for i in range(frame_start, frame_end):
            
            frame = i
            
            bpy.context.scene.frame_set(i)
            
            bpy.ops.import_scene.obj(filepath=path+"ObjSequence"+str(i)+".obj")
            bpy.ops.object.group_link(group='ObjSequence')
            obj = bpy.context.selected_objects[0]
            obj.name = "ObjSequence_"+str(i)
                   
            obj.parent = empty
            
            
            obj.hide_render = False
            obj.hide = False
            obj.keyframe_insert("hide")
            obj.keyframe_insert("hide_render")
            
            bpy.context.scene.frame_set(i-1)
            obj.hide_render = True
            obj.hide = True
            obj.keyframe_insert("hide")
            obj.keyframe_insert("hide_render")
            
            bpy.context.scene.frame_set(i+1)
            obj.hide_render = True
            obj.hide = True
            obj.keyframe_insert("hide")
            obj.keyframe_insert("hide_render")
        
        return{'FINISHED'}       
        

class OBJECT_OT_Set_Mball_Size(bpy.types.Operator):
    bl_idname = "mball.pfluid_update"
    bl_label = "Update MBall"

    #def mball_size(size):
    def execute(self, context):
        obj = bpy.context.selected_objects[0]
        data = context.scene
        
        elements = obj.data.elements
        data = obj.data
        
        data.resolution = bpy.context.scene.pfluid_resolution
        data.render_resolution = bpy.context.scene.pfluid_resolution
        
        scene = context.scene
        
        for i in range(0, len(elements)):
            obj.data.elements[i].stiffness = scene.pfluid_size 
            obj.data.elements[i].radius = scene.pfluid_size 
    
        return{'FINISHED'}




def set_visibility(obj):
    
    i = bpy.context.scene.frame_current
    
    obj.hide_render = False
    obj.hide = False
    obj.keyframe_insert("hide")
    obj.keyframe_insert("hide_render")
            
    bpy.context.scene.frame_set(i-1)
    obj.hide_render = True
    obj.hide = True
    obj.keyframe_insert("hide")
    obj.keyframe_insert("hide_render")
            
    bpy.context.scene.frame_set(i+1)
    obj.hide_render = True
    obj.hide = True
    obj.keyframe_insert("hide")
    obj.keyframe_insert("hide_render")    




def register():
    bpy.utils.register_class(PFluid_Tools)
    bpy.utils.register_class(OBJECT_OT_MakeMBall)
    bpy.utils.register_class(OBJECT_OT_MBallMesh)
    bpy.utils.register_class(OBJECT_OT_Mesh_Sequence)
    bpy.utils.register_class(OBJECT_OT_Set_Mball_Size)



def unregister():
    bpy.utils.unregister_class(PFluid_Tools)
    bpy.utils.unregister_class(OBJECT_OT_MakeMBall)
    bpy.utils.unregister_class(OBJECT_OT_MBallMesh)
    bpy.utils.unregister_class(OBJECT_OT_Mesh_Sequence)
    bpy.utils.unregister_class(OBJECT_OT_Set_Mball_Size)    


if __name__ == '__main__':
    register()



