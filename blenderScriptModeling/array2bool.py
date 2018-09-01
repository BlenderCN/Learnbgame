# 让阵列之后的物体自动布尔
# http://tieba.baidu.com/p/4925186797
import bpy


name=bpy.context.object.name

 

bpy.ops.object.modifier_add(type='ARRAY')
bpy.context.object.modifiers["Array"].count = 2
bpy.context.object.modifiers["Array"].relative_offset_displace[0] = 0.5
bpy.context.object.modifiers["Array"].relative_offset_displace[1] = 0.5
bpy.context.object.modifiers["Array"].relative_offset_displace[2] = 0.5


bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Array")
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.select_all(action='TOGGLE')
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.editmode_toggle()


bpy.ops.object.modifier_add(type='BOOLEAN')
bpy.context.object.modifiers["Boolean"].object = bpy.data.objects["{0}.001".format(name)]
bpy.context.object.modifiers["Boolean"].operation = 'UNION'
bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")