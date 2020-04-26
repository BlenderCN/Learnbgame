import bpy
import bmesh
from bpy.types import WindowManager
from .hotkeys import hotkeys
from .addon import prefs
from .uv_utils import *


def get_island_bounds(bm, island):
    uvl = bm.loops.layers.uv.verify()
    umin, umax, vmin, vmax = 1000, -1000, 1000, -1000
    for f_index in island:
        f = bm.faces[f_index]
        for l in f.loops:
            if umin > l[uvl].uv[0]:
                umin = l[uvl].uv[0]
            if umax < l[uvl].uv[0]:
                umax = l[uvl].uv[0]
            if vmin > l[uvl].uv[1]:
                vmin = l[uvl].uv[1]
            if vmax < l[uvl].uv[1]:
                vmax = l[uvl].uv[1]

    return umin, umax, vmin, vmax


def get_bounds(bounds):
    umin, umax, vmin, vmax = 1000, -1000, 1000, -1000
    for b in bounds:
        if umin > b[0]:
            umin = b[0]
        if umax < b[1]:
            umax = b[1]
        if vmin > b[2]:
            vmin = b[2]
        if vmax < b[3]:
            vmax = b[3]

    return umin, umax, vmin, vmax


class SUV_OT_island_align(bpy.types.Operator):
    bl_idname = "suv.island_align"
    bl_label = "Align Islands"
    bl_description = "Align islands"
    bl_options = {'REGISTER', 'UNDO'}

    mode = bpy.props.EnumProperty(
        name="Mode",
        items=(
            ('TL', "Top Left", "Top Left"),
            ('T', "Top", "Top"),
            ('TR', "Top Right", "Top Right"),
            ('L', "Left", "Left"),
            ('C', "Center", "Center"),
            ('R', "Right", "Right"),
            ('BL', "Bottom Left", "Bottom Left"),
            ('B', "Bottom", "Bottom"),
            ('BR', "Bottom Right", "Bottom Right"),
        ),
        default='T')
    use_uv_bounds = bpy.props.BoolProperty(
        name="Use Bounds", description="Use bounds")

    def move_island(self, island, bounds, umin, umax, vmin, vmax):
        uvl = self.bm.loops.layers.uv.verify()
        du, dv = 0, 0

        if 'B' in self.mode:
            dv = vmin - bounds[2]
        elif 'T' in self.mode:
            dv = vmax - bounds[3]
        if 'L' in self.mode:
            du = umin - bounds[0]
        elif 'R' in self.mode:
            du = umax - bounds[1]
        elif 'C' in self.mode:
            du = 0.5 * (umin + umax - bounds[0] - bounds[1])
            dv = 0.5 * (vmin + vmax - bounds[2] - bounds[3])

        for f_index in island:
            f = self.bm.faces[f_index]
            for l in f.loops:
                l[uvl].uv[0] += du
                l[uvl].uv[1] += dv

    @classmethod
    def poll(self, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT'

    def execute(self, context):
        self.bm = init_bm(context.object.data)
        islands = get_islands(self.bm, True)
        if len(islands) == 1:
            return {'FINISHED'}

        bounds = []
        for island in islands:
            bounds.append(get_island_bounds(self.bm, island))

        if self.use_uv_bounds:
            umin, umax, vmin, vmax = 0, 1, 0, 1
        else:
            umin, umax, vmin, vmax = get_bounds(bounds)

        for i, island in enumerate(islands):
            self.move_island(island, bounds[i], umin, umax, vmin, vmax)

        bmesh.update_edit_mesh(context.object.data, False, False)
        return {'FINISHED'}


class SUV_OT_island_distribute(bpy.types.Operator):
    bl_idname = "suv.island_distribute"
    bl_label = "Distribute Islands"
    bl_description = "Distribute islands"

    mode = bpy.props.EnumProperty(
        name="Mode",
        items=(
            ('VERTICAL', "Vertical", "Vertical"),
            ('HORIZONTAL', "Horizontal", "Horizontal"),
        ))

    @classmethod
    def poll(self, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT'

    def calc_gaps(self, bounds, umin, umax, vmin, vmax):
        bw = umax - umin
        bh = vmax - vmin
        iw, ih = 0, 0
        for b in bounds:
            iw += b[1] - b[0]
            ih += b[3] - b[2]
        self.gu = (bw - iw) / (len(bounds) - 1)
        self.gv = (bh - ih) / (len(bounds) - 1)

    def move_island(self, u, v, island, bounds, umin, umax, vmin, vmax):
        uvl = self.uvl
        du, dv = 0, 0

        if self.mode == 'VERTICAL':
            dv = v + self.gv - bounds[2]
        else:
            du = u + self.gu - bounds[0]

        for f_index in island:
            f = self.bm.faces[f_index]
            for l in f.loops:
                l[uvl].uv[0] += du
                l[uvl].uv[1] += dv

    def execute(self, context):
        self.bm = init_bm(context.object.data)
        self.uvl = self.bm.loops.layers.uv.verify()
        islands = get_islands(self.bm, True)
        if len(islands) == 1:
            return {'FINISHED'}

        bounds = []
        for island in islands:
            bounds.append(get_island_bounds(self.bm, island))

        umin, umax, vmin, vmax = get_bounds(bounds)
        self.calc_gaps(bounds, umin, umax, vmin, vmax)

        data = list(zip(islands, bounds))
        data.sort(
            key=lambda t: t[1][0] if self.mode == 'HORIZONTAL' else t[1][2])

        max_co = -1000
        idx = -1
        for i, (island, bounds) in enumerate(data):
            co = bounds[1] if self.mode == 'HORIZONTAL' else bounds[3]
            if max_co < co and i != 0:
                max_co = co
                idx = i
        data.append(data.pop(idx))

        for i, (island, bounds) in enumerate(data):
            if i > 0 and i < len(data) - 1:
                self.move_island(u, v, island, bounds, umin, umax, vmin, vmax)
            u = bounds[1]
            v = bounds[3]

        bmesh.update_edit_mesh(context.object.data, False, False)
        return {'FINISHED'}