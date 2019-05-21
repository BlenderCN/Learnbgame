bl_info = {
    "name": "Snap Bisect",
    "author": "Addam Dominec (emu)",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D Toolbox > Snap Bisect",
    "description": "Calls the Bisect operator aligned to three vertices",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}


import bpy
import bgl
import bmesh
from mathutils import Matrix, Vector
from mathutils.geometry import normal
from bpy_extras.view3d_utils import location_3d_to_region_2d as region_2d


def is_view_transparent(view):
    return False #TODO view.viewport_shade in {'BOUNDBOX', 'WIREFRAME'} or not view.use_occlude_geometry


def is_perspective(region):
    return region.view_perspective == 'PERSP'


def window_project(point, context):
    return region_2d(context.region, context.space_data.region_3d, point)


def camera_center(matrix):
    result = matrix.inverted() @ Vector((0, 0, 0, 1))
    return result.xyz / result.w


def ortho_axis(matrix):
    return matrix.row[2].to_3d()


def draw_callback(self, context):
    return #TODO
    bgl.glPolygonOffset(0, -20)
    bgl.glEnable(bgl.GL_BLEND)
    if is_view_transparent(context.space_data):
        bgl.glDisable(bgl.GL_DEPTH_TEST)

    bgl.glPointSize(10)
    bgl.glColor4f(1.0, 0.0, 0.0, 0.5)
    bgl.glBegin(bgl.GL_POINTS)
    for point in self.points:
        bgl.glVertex3f(*point.co)
    bgl.glEnd()

    bgl.glPointSize(3)
    bgl.glColor4f(0.0, 1.0, 1.0, 0.5 if is_view_transparent(context.space_data) else 1.0)
    bgl.glBegin(bgl.GL_POINTS)
    for point in self.midpoints:
        bgl.glVertex3f(*point)
    bgl.glEnd()

    bgl.glPointSize(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    bgl.glPolygonOffset(0, 0)


def edge_centers(mesh, tsf):
    return [0.5 * tsf @ (e.verts[0].co + e.verts[1].co) for e in mesh.edges]


class Point(bpy.types.PropertyGroup):
    co: bpy.props.FloatVectorProperty(name="Coordinates", size=3)
bpy.utils.register_class(Point)


class SnapBisect(bpy.types.Operator):
    """Calls the Bisect operator aligned to three vertices"""
    bl_idname = "view3d.snap_bisect"
    bl_label = "Snap Bisect"
    bl_options = {'REGISTER', 'UNDO'}
    offset: bpy.props.FloatProperty(name="Offset", description="Distance from the given points", unit='LENGTH')
    points: bpy.props.CollectionProperty(type=Point, options={'HIDDEN', 'SKIP_SAVE'})
    use_fill: bpy.props.BoolProperty(name="Fill", description="Fill in the cut")
    clear_inner: bpy.props.BoolProperty(name="Clear Inner", description="Remove geometry behind the plane")
    clear_outer: bpy.props.BoolProperty(name="Clear Inner", description="Remove geometry in front of the plane")


    def pick(self, context, event):
        coords = Vector((event.mouse_region_x, event.mouse_region_y))
        if is_perspective(context.space_data.region_3d):
            origin = camera_center(context.space_data.region_3d.view_matrix)
            direction = None
        else:
            origin = None
            direction = ortho_axis(context.space_data.region_3d.view_matrix)
        sce = context.scene
        layer = context.view_layer
        def distance(v):
            v_co = region_2d(context.region, context.space_data.region_3d, v)
            return (coords - v_co).length if v_co else float("inf")
        def visible(v, direction=direction):
            if origin is not None:
                direction = v - origin
            is_hit, *data = sce.ray_cast(layer, v - direction, direction, distance=direction.length - 1e-5)
            return not is_hit
        if is_view_transparent(context.space_data):
            return min((distance(v), v) for v in self.anchors)
        else:
            return min((distance(v), v) for v in self.anchors if visible(v))


    def modal(self, context, event):
        max_distance = 10
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            distance, point = self.pick(context, event)
            if distance < max_distance:
                self.points.add().co = point
                context.region.tag_redraw()
                context.area.header_text_set("LMB: mark cut point, X/Y/Z: plane-aligned cut" if len(self.points) == 1 else "LMB: mark cut point, X/Y/Z: axis-aligned cut, Enter/Space: view-aligned cut")
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
            context.region.tag_redraw()
            context.area.header_text_set(None)
            return {'CANCELLED'}
        elif event.type in {'RET', 'SPACE', 'NUMPAD_ENTER'}:
            if len(self.points) == 2:
                mat = context.space_data.region_3d.view_matrix
                self.points.add().co = camera_center(mat) if is_perspective(context.space_data.region_3d) else Vector(self.points[0].co) + ortho_axis(mat)
        elif event.type in {'X', 'Y', 'Z'} and self.points:
            origin = Vector(self.points[0].co)
            offset = [Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))]
            if len(self.points) == 1:
                self.points.add().co = origin + offset[("XYZ".index(event.type) + 1) % 3]
                self.points.add().co = origin + offset[("XYZ".index(event.type) + 2) % 3]
            if len(self.points) == 2:
                self.points.add().co = origin + offset["XYZ".index(event.type)]
        else:
            return {'PASS_THROUGH'}
        if len(self.points) >= 3:
            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
            return self.execute(context)
        return {'RUNNING_MODAL'}


    def execute(self, context):
        nor = normal(p.co for p in self.points[:3])
        co = Vector(self.points[-1].co) + nor * self.offset
        bpy.ops.mesh.bisect(plane_co=co, plane_no=nor, use_fill=self.use_fill, clear_inner=self.clear_inner, clear_outer=self.clear_outer)
        context.area.header_text_set(None)
        return {'FINISHED'}


    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D' and context.mode == 'EDIT_MESH'


    def invoke(self, context, event):
        bm = bmesh.from_edit_mesh(context.edit_object.data)
        tsf = context.edit_object.matrix_world
        self.midpoints = edge_centers(bm, tsf)
        self.anchors = [tsf @ v.co for v in bm.verts] + self.midpoints
        self.handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback, (self, context), 'WINDOW', 'POST_VIEW')
        context.region.tag_redraw()
        context.window_manager.modal_handler_add(self)
        context.area.header_text_set("LMB: mark cut point")
        return {'RUNNING_MODAL'}


def menu_func(self, context):
    self.layout.operator(SnapBisect.bl_idname)


def register():
    bpy.utils.register_class(SnapBisect)
    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)
    #TODO bpy.types.VIEW3D_PT_tools_meshedit.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
    #TODO bpy.types.VIEW3D_PT_tools_meshedit.remove(menu_func)
    bpy.utils.unregister_class(SnapBisect)


if __name__ == "__main__":
    register()
