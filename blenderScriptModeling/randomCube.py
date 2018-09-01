# 在一定范围内随机创建100个立方体
# https://jingyan.baidu.com/article/6c67b1d6afa19b2786bb1e78.html

import bpy

from random import randint

bpy.ops.mesh.primitive_cube_add()

#创建模型的数量

count = 100

for c in range(0,count):

    x = randint(-100,100)

    y = randint(-100,100)

    z = randint(-100,100)

    bpy.ops.mesh.primitive_cube_add(location=(x,y,z))
