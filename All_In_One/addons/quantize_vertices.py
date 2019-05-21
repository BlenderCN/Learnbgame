'''
JMP Blender Utilities
Copyright (C) 2018 Jean-Marc Pelletier

quantize_vertices.py

This scripts moves the vertices of the selected object's mesh, so that they snap 
to fixed intervals. Features include:
- Setting the grid interval independently for each axis
- Moving the grid by a certain offset
- Setting the distance threshold within which vertices will snap to the grid
- Setting the maximum number of decimal digits for snapped vertices. This is useful when exporting to certain formats.

This file is part of the JMP Blender Utilities.

    The JMP Blender Utilities is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    The JMP Blender Utilities is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with The JMP Blender Utilities.  If not, see <https://www.gnu.org/licenses/>.
'''


bl_info = {
    "name": "Quantize Vertices", 
    "category": "Object"
}

import bpy
import math
from bpy.props import (FloatVectorProperty, FloatProperty, IntProperty)


class VertexQuantizer(bpy.types.Operator):
    """Snap existing vertices to the grid"""

    bl_idname = 'object.quantize_vertices'
    bl_label = 'Quantize Vertices'
    bl_options = {'REGISTER', 'UNDO'}

    grid_size = FloatVectorProperty(
        name='Grid Size',
        description="Snap intervals",
        default=(1.0,1.0,1.0)
    )

    grid_offset = FloatVectorProperty(
        name='Grid Offset',
        description="The grid offset",
        default=(0.0,0.0,0.0)
    )

    snap_threshold = FloatProperty(
        name='Snap Threshold',
        description='The distance at which vertices snap to the grid',
        default=0.001
    )

    float_precision = IntProperty(
        name='Floating-point Precision',
        description='The maximum number of decimal digits used to represent vertex coordinates',
        default=4
    )

    def closest(self, v, grid, offset):
        if grid != 0:
            return round(offset + round((v - offset) / grid) * grid, self.float_precision)
        else:
            return v

    def distance(self, vert, point):
        dx = vert.co.x - point[0]
        dy = vert.co.y - point[1]
        dz = vert.co.z - point[2]
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def snap_to(self, val, target):
        return target if math.fabs(target - val) <= self.snap_threshold else val

    def execute(self, context):
        scene = bpy.context.scene
        obj = scene.objects.active
        if (obj and obj.data and obj.data.vertices):
            for v in obj.data.vertices:
                target = (
                    self.closest(v.co.x, self.grid_size[0], self.grid_offset[0]),
                    self.closest(v.co.y, self.grid_size[1], self.grid_offset[1]),
                    self.closest(v.co.z, self.grid_size[2], self.grid_offset[2])
                )
                v.co.x = self.snap_to(v.co.x, target[0])
                v.co.y = self.snap_to(v.co.y, target[1])
                v.co.z = self.snap_to(v.co.z, target[2])

        return {'FINISHED'}

def register():
    bpy.utils.register_class(VertexQuantizer)

def unregister():
    bpy.utils.unregister_class(VertexQuantizer)


if __name__ == "__main__":
    register()