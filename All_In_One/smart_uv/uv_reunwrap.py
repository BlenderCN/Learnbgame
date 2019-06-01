import bpy
import bmesh


def _hide_faces():
    me = bpy.context.active_object.data
    bm = bmesh.from_edit_mesh(me)
    uv_layer = bm.loops.layers.uv.verify()
    bm.faces.layers.tex.verify()

    for f in bm.faces:
        f.tag = False
        if not f.select:
            continue

        face_is_sel = True
        for l in f.loops:
            luv = l[uv_layer]
            if not luv.select:
                face_is_sel = False
                break

        if not face_is_sel:
            f.select = False
            f.tag = True


def _reveal_faces():
    bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
    uv_layer = bm.loops.layers.uv.verify()

    for f in bm.faces:
        if not f.tag:
            continue
        f.select = True
        for l in f.loops:
            l[uv_layer].select = False


def _get_bounds():
    bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
    uv_layer = bm.loops.layers.uv.verify()
    min_x, min_y, max_x, max_y = 100000, 100000, -100000, -100000
    print(min_x, min_y, max_x, max_y)

    for f in bm.faces:
        if not f.select:
            continue
        for loop in f.loops:
            l = loop[uv_layer]
            if min_x > l.uv.x:
                min_x = l.uv.x
            if max_x < l.uv.x:
                max_x = l.uv.x
            if min_y > l.uv.y:
                min_y = l.uv.y
            if max_y < l.uv.y:
                max_y = l.uv.y
    return (min_x, max_x, min_y, max_y)


def _update_loops(b0, b):
    bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
    uv_layer = bm.loops.layers.uv.verify()

    sx = (b0[1] - b0[0]) / (b[1] - b[0])
    sy = (b0[3] - b0[2]) / (b[3] - b[2])
    s = 0.5 * (max(sx, sy) + min(sx, sy))

    ox = 0.5 * ((b0[1] - b0[0]) - s * (b[1] - b[0]))
    oy = 0.5 * ((b0[3] - b0[2]) - s * (b[3] - b[2]))

    for f in bm.faces:
        if not f.select:
            continue
        for loop in f.loops:
            l = loop[uv_layer]
            l.uv.x = b0[0] + (l.uv.x - b[0]) * s + ox
            l.uv.y = b0[2] + (l.uv.y - b[2]) * s + oy

    bmesh.update_edit_mesh(bpy.context.active_object.data, True, False)


class SUV_OT_uv_reunwrap(bpy.types.Operator):
    bl_idname = "suv.uv_reunwrap"
    bl_label = "Re-Unwrap"

    def main(self, context) :
        uv_editor = bpy.ops.uv
        for self.area in bpy.context.screen.areas:
            if self.area.type == 'IMAGE_EDITOR':
                _hide_faces()
                bounds = _get_bounds()
                uv_editor.unwrap(method='ANGLE_BASED', margin=0.001)
                new_bounds = _get_bounds()
                _update_loops(bounds, new_bounds)
                _reveal_faces()

                # uv_editor.hide(unselected=True)
                # uv_editor.unwrap(method='ANGLE_BASED', margin=0.001)
                # uv_editor.reveal()
                # uv_editor.select_all(action='TOGGLE')

    @classmethod
    def poll(self, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT'

    def execute(self, context):
        self.main(context)
        return {'FINISHED'}


# class SUV_PT_reunwrap(bpy.types.Panel):
#     bl_label = "Re-Unwrap"
#     bl_space_type = 'IMAGE_EDITOR'
#     bl_region_type = 'UI'

#     def draw(self, context):
#         layout = self.layout
#         layout.operator(SUV_OT_uv_reunwrap.bl_idname)

#     @classmethod
#     def poll(self, context):
#         obj = context.active_object
#         return all([obj is not None, obj.type == 'MESH', obj.mode == 'EDIT'])

