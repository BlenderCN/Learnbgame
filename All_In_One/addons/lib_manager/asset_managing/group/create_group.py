import bpy
import sys
from mathutils import Matrix

args = sys.argv

filepath = args[-1]
name = args[-2]


scene = bpy.context.scene

group = bpy.data.groups.new(name)

for ob in bpy.data.objects :
    scene.objects.link(ob)
    group.objects.link(ob)
    ob.matrix_world = Matrix()

bpy.ops.wm.save_as_mainfile(filepath = filepath)
