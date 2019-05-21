bl_info = {
    'name': 'CaveGen',
    'author': 'sdfgeoff',
    'version': (0, 0),
    "blender": (2, 6, 3),
    'location': 'View3D > Add > Mesh',
    'description': 'Makes Caves using metaballs converted to mesh',
    'warning': 'Murrently WIP',  # used for warning icon and text in addons panel
    'category': 'Add Mesh'}


import bpy
import random

from bpy.props import IntProperty, FloatProperty, BoolProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add

def addCave(self, context):
    print ("regen Cave")


    oldLoc = [0.0, 0.0, 0.0]
    oldScale = [self.chaos, self.chaos, self.chaos]
    random.seed(self.random_seed)

    print ("generating initial metaball")

    bpy.ops.object.metaball_add(type='BALL', view_align=False, enter_editmode=True, location=(0.0, 0.0, 0.0))
    def randLoc():
        rand = (random.random()-0.5) * 5
        if rand > 1:
            rand = 1
        if rand < -1:
            rand = -1
        return rand

    def randScale():
        rand = (random.random()*2)+0.2
        return rand

    def randType():
        types = ['BALL', 'ELLIPSOID', 'CAPSULE', 'CUBE']
        rand = random.choice(types)
        return rand

    def addRandLights(Prob, oldLoc,passedName,passedScene):
        print("user wants lights")
        if random.random() < Prob:
            print("create a light")
            la_lamp = bpy.data.lamps.new("la_" + passedName,'POINT')
            la_lamp.energy = 0.1
            la_lamp.distance = 15
            ob_light = bpy.data.objects.new(passedName,la_lamp)
            ob_light.location = oldLoc
            passedScene.objects.link(ob_light)
            '''
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.lamp_add(type='POINT', view_align=False, location=oldLoc)
            #cave = bpy.data.objects['Mball.001']
            print (bpy.data.objects)
            #bpy.context.scene.objects.active = cave
            #bpy.ops.object.editmode_toggle()
            '''            

    def generateNew(oldLoc, oldScale, run,passedScene):
        newLoc = randLoc()*oldScale[0]+oldLoc[0], randLoc()*oldScale[1]+oldLoc[1], randLoc()*oldScale[2]+oldLoc[2]
        
        ball = bpy.ops.object.metaball_add(type=randType(), location=(newLoc))
        if self.lights == True:
            light_name = "cave_lamp_" + str(run)
            addRandLights(self.lightProb, oldLoc,light_name,passedScene)
        #if random.random() > 0.9:
        #    createLamp(newLoc, run)
        #mball = bpy.context.visible_objects[run]
        #metaball = mball.data

        #newScale = [randScale(), randScale(), randScale()]
        #mball.scale[0] = newScale[0]
        #mball.scale[1] = newScale[1]
        #mball.scale[2] = newScale[2]
        return newLoc, oldScale

    mball = bpy.context.selected_objects[0]
    metaball = mball.data
    metaball.resolution = self.res
    metaball.render_resolution = self.res
    metaball.update_method = 'NEVER' 

    run = 0
    while run < self.iterations+1:
        print ("adding mball "+str(run))
        oldLoc, oldScale= generateNew(oldLoc, oldScale, run,context.scene)
        run += 1

    
    metaball.update_method = 'FAST' 

    bpy.ops.object.editmode_toggle()

    if self.mesh == True:   
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.vertices_smooth(repeat=2)
        bpy.ops.mesh.subdivide(number_cuts=1, fractal=5, seed=0)
        bpy.ops.mesh.vertices_smooth(repeat=1)
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.editmode_toggle()


class caveGen(bpy.types.Operator, AddObjectHelper):
    """Add a Mesh Object"""
    bl_idname = "mesh.primitive_cave_gen"
    bl_label = "Cave"
    bl_options = {'REGISTER', 'UNDO'}

    iterations = IntProperty(name="Iterations", default=15,
                                min=2, max=10000,
                                description="Sets how many metaballs to use in the cave")

    chaos = FloatProperty(name="Chaos", default=1.0,
                                min=0.1, max=2,
                                description="Sets the scaling of distance between metaballs")

    res = FloatProperty(name="Resolution", default=0.8,
                                min=0.1, max=2.0,
                                description="Changes the resolution of the cave")

    mesh = BoolProperty(name="Convert to mesh", default=True, description="Converts to mesh and does some subdivide/fractal functions")
    lights = BoolProperty(name="Lights", default=False, description="Adds Lights in the passage")
    lightProb = FloatProperty(name="Light Probability", default=0.1, min=0.001, max=1.0, description="Chance of a light being placed at any given point")
    random_seed = IntProperty(name="Random Seed", description="Set the random seed for this cave object", default = 101, min = -420, max = 420)


    def execute(self, context):
        addCave(self, context)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(caveGen.bl_idname, text="Metaball Cave", icon="PLUGIN")


def register():
    bpy.utils.register_class(caveGen)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(caveGen)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()