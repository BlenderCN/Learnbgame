import bpy
import bmesh
import math
from .addon import prefs
from .uv_utils import *


# def calculate_angle(bm, uv_layer, delta=1):
#     indexes = []
#     cont_face = 0
#     cont_loop = 0
#     cont_vert = 0
#     points = []

#     for face in bm.faces:
#         cont_1 = 0
#         for loop in face.loops:
#             if loop[uv_layer].select and cont_1 < 2:
#                 indexes.append(cont_loop)
#                 point = tuple(loop[uv_layer].uv)
#                 if point not in points:
#                     points.append(point)
#                     cont_1 += 1
#             cont_loop += 1
#         cont_face += 1

#     if len(points) == 0:
#         rads = 0
#         degs = 0

#     elif len(points) == 2:
#         x1 = points[0][0]
#         y1 = points[0][1]

#         x2 = points[-1][0]
#         y2 = points[-1][1]

#         #########
#         ############
#         if x1 > x2:
#             x1, x2 = x2, x1
#             y1, y2 = y2, y1
#         ############
#         #########

#         if x1 == x2 and y1 == y2:
#             try:
#                 x2 = points[-2][0]
#                 y2 = points[-2][1]
#             except:
#                 return None

#         dx, dy = x2 - x1, y2 - y1

#         rads = math.atan2(dy, dx)
#         degs = math.degrees(rads)

#         if abs(degs) >= 135:
#             degs -= 180 * abs(degs) / degs
#         elif abs(degs) >= 45:
#             degs -= 90 * abs(degs) / degs

#         return rads, degs, indexes, points

#     else:
#         return None


class SUV_OT_uv_align_by_edge(bpy.types.Operator):
    bl_idname = 'suv.uv_align_by_edge'
    bl_label = 'Align Island by Edge'
    bl_description = "Align island by edge"
    bl_options = {'REGISTER', 'UNDO'}

    delta = bpy.props.IntProperty(options={'SKIP_SAVE'}, default=1)

    @classmethod
    def poll(self, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT' and \
            context.scene.tool_settings.uv_select_mode in {'EDGE'}

    def get_selected_edge(self, island):
        for fi in island:
            f = self.bm.faces[fi]
            for l in f.loops:
                ll = l.link_loop_next
                if l[self.uvl].select and ll[self.uvl].select:
                    return (l, ll)

        return None

    def select_island(self, island):
        for fi in island:
            f = self.bm.faces[fi]
            for l in f.loops:
                l[self.uvl].select = True

    def rotate_island(self, island, edge):
        pr = prefs()

        x1 = edge[0][self.uvl].uv[0]
        y1 = edge[0][self.uvl].uv[1]
        x2 = edge[1][self.uvl].uv[0]
        y2 = edge[1][self.uvl].uv[1]

        if x1 == x2 and y1 == y2:
            return

        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        dx, dy = x2 - x1, y2 - y1

        rads = math.atan2(dy, dx)
        degs = math.degrees(rads)

        if abs(degs) >= 135:
            degs -= 180 * abs(degs) / degs
        elif abs(degs) >= 45:
            degs -= 90 * abs(degs) / degs

        bpy.context.space_data.pivot_point = 'CURSOR'
        bpy.ops.uv.select_all(action='DESELECT')
        edge[0][self.uvl].select = True
        edge[1][self.uvl].select = True
        bpy.ops.uv.snap_cursor(target='SELECTED')
        self.select_island(island)

        if degs in {0.0, 90.0, -90.0, 180, -180.0}:
            if pr.rotate_again:
                bpy.ops.transform.rotate(
                    value=math.radians(
                        90 if self.delta > 0 else -90))
        else:
            bpy.ops.transform.rotate(value=math.radians(degs))

        for f in self.bm.faces:
            for l in f.loops:
                l[self.uvl].select = l.index in self.selected_loops

    def execute(self, context):
        cursor = tuple(context.area.spaces.active.cursor_location)
        pivot = context.space_data.pivot_point

        pr = prefs()
        self.bm = init_bm(context.object.data)
        self.uvl = self.bm.loops.layers.uv.verify()

        self.selected_loops = set()
        for f in self.bm.faces:
            for l in f.loops:
                if l[self.uvl].select:
                    self.selected_loops.add(l.index)

        islands = get_islands(self.bm, selected_only=True)
        for island in islands:
            edge = self.get_selected_edge(island)
            if edge:
                self.rotate_island(island, edge)

        context.area.spaces.active.cursor_location = cursor
        bpy.context.space_data.pivot_point = pivot
        bmesh.update_edit_mesh(context.object.data, False, False)
        return {'FINISHED'}




        # for area in bpy.context.screen.areas:
        #     if area.type == 'IMAGE_EDITOR':

        #         cursor = tuple(area.spaces.active.cursor_location)
        #         pivot = bpy.context.space_data.pivot_point

        #         me = bpy.context.object.data
        #         bm = bmesh.from_edit_mesh(me)

        #         bpy.context.tool_settings.use_uv_select_sync = False

        #         uv_layer = bm.loops.layers.uv.verify()

        #         selectedUV = set()

        #         for face in bm.faces:
        #             for loop in face.loops:
        #                 if loop[uv_layer].select:
        #                     selectedUV.add(loop.index)

        #         angle = calculate_angle(bm, uv_layer, self.delta)
        #         if angle:
        #             degs = angle[1]

        #             bpy.context.space_data.pivot_point = 'CURSOR'
        #             bpy.ops.uv.snap_cursor(target='SELECTED')
        #             bpy.ops.uv.select_linked(extend=False)

        #             if degs in [0.0, 90.0, -90.0, 180, -180.0]:
        #                 if pr.rotate_again:
        #                     bpy.ops.transform.rotate(
        #                         value=math.radians(
        #                             90 if self.delta > 0 else -90))

        #             else:
        #                 bpy.ops.transform.rotate(value=math.radians(degs))

        #             bpy.ops.uv.select_all(action='DESELECT')
        #             for face in bm.faces:
        #                 for loop in face.loops:
        #                     if loop.index in selectedUV:
        #                         loop[uv_layer].select = True

        #         area.spaces.active.cursor_location = cursor
        #         bpy.context.space_data.pivot_point = pivot

        #         bm.select_flush(True)
        #         bmesh.update_edit_mesh(me, False, False)

        # return {'FINISHED'}

