bl_info = {
    "name": "Transform Fragments",
    "author": "nemyax",
    "version": (0, 1, 20121228),
    "blender": (2, 6, 4),
    "location": "",
    "description": "Transform selection by contiguous fragment, as in Wings3D",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy
import bmesh
import mathutils as mu
import math
from bpy.props import FloatProperty, EnumProperty

def orientation(context):
    viewport = context.space_data
    orient = viewport.transform_orientation
    if orient in {'GLOBAL', 'GIMBAL', 'NORMAL'}:
        obj_m = context.active_object.matrix_world
        return obj_m.inverted().to_3x3().to_4x4()
    if orient == 'LOCAL':
        return mu.Matrix.Identity(4)
    elif orient == 'VIEW':
        obj_m = context.active_object.matrix_world
        view_m = viewport.region_3d.view_matrix
        return obj_m.inverted().to_3x3().to_4x4() * \
            view_m.inverted().to_3x3().to_4x4()
    else: # custom orientation with any name
        obj_m = context.active_object.matrix_world
        custom_m = viewport.current_orientation.matrix
        return obj_m.inverted().to_3x3().to_4x4() * \
            custom_m.to_4x4()

def rotate_xyz(angle, axis, orientation):
    ar = math.radians(angle)
    if axis == 'X':
        vec = orientation * mu.Vector((1, 0, 0))
    elif axis == 'Y':
        vec = orientation * mu.Vector((0, 1, 0))
    else: # 'Z'
        vec = orientation * mu.Vector((0, 0, 1))
    return mu.Matrix.Rotation(ar, 4, vec)

def rotate_n(angle, normal):
    ar = math.radians(angle)
    return mu.Matrix.Rotation(ar, 4, normal)

def scale_xyz(factor, axes, orientation):
    if axes == 'X':
        vec = orientation * mu.Vector((1, 0, 0))
        return mu.Matrix.Scale(factor, 4, vec)
    elif axes == 'Y':
        vec = orientation * mu.Vector((0, 1, 0))
        return mu.Matrix.Scale(factor, 4, vec)
    elif axes == 'Z':
        vec = orientation * mu.Vector((0, 0, 1))
        return mu.Matrix.Scale(factor, 4, vec)
    elif axes =='XYZ':
        return mu.Matrix.Scale(factor, 4)
    else:
        if axes == 'XY':
            vec1 = orientation * mu.Vector((1, 0, 0))
            vec2 = orientation * mu.Vector((0, 1, 0))
        elif axes == 'XZ':
            vec1 = orientation * mu.Vector((1, 0, 0))
            vec2 = orientation * mu.Vector((0, 0, 1))
        else: # 'YZ'
            vec1 = orientation * mu.Vector((0, 1, 0))
            vec2 = orientation * mu.Vector((0, 0, 1))
        m1 = mu.Matrix.Scale(factor, 4, vec1)
        m2 = mu.Matrix.Scale(factor, 4, vec2)
        return m2 * m1

def scale_n(factor, axes, normal):
    if axes == 'Normal':
        return mu.Matrix.Scale(factor, 4, normal)
    else: # 'Normal Radial'
        if factor == 0.0:
            factor = 1e-30
        uniform_m = mu.Matrix.Scale(factor, 4)
        compensate_m = mu.Matrix.Scale(1 / factor, 4, normal)
        return compensate_m * uniform_m

def xform_centers(groups, bm):
    centers = {}
    for g in groups:
        num = len(g)
        x = sum([bm.verts[v].co.x for v in g]) / num
        y = sum([bm.verts[v].co.y for v in g]) / num
        z = sum([bm.verts[v].co.z for v in g]) / num
        for v in g:
            centers[v] = mu.Vector((x, y, z))
    return centers

def average_normals(groups, bm):
    normals = {}
    for g in groups:
        avg = bm.verts[g[0]].normal
        for v in g[1:]:
            avg = avg + bm.verts[v].normal
        avg.normalize()
        for v in g:
            normals[v] = avg
    return normals

def initial_coords(groups, bm):
    coords = {}
    for g in groups:
        for v in g:
            coords[v] = bm.verts[v].co.copy()
    return coords

def reset(context, coords):
    bm = bmesh.from_edit_mesh(context.active_object.data)
    for v in coords.keys():
        bm.verts[v].co = coords[v]
    context.active_object.data.update()
    return

def make_groups(edges, e_links, v_links):
    groups = [[edges.pop(0)]]
    while len(edges):
        def check(x):
            return x in groups[-1]
        def stamp(maybe_connected):
            exts1 = v_links[e_links[maybe_connected][0]]
            exts2 = v_links[e_links[maybe_connected][1]]
            if any(map(check, exts1)) or any(map(check, exts2)):
                return maybe_connected
            else:
                return
        candidates = list(filter(lambda y: y, map(stamp, edges)))
        if len(candidates):
            for c in candidates:
                groups[-1].append(c)
                edges.remove(c)
        else:
            groups.append([edges[0]])
            edges.pop(0)
    return groups

def group_by_adjacency(edges, bm):
    e_links = {}
    v_links = {}
    for e in edges:
        e_links[e] = [v.index for v in bm.edges[e].verts]
    vs = []
    [vs.extend(x) for x in e_links.values()]
    vs = list(set(vs))
    for v in vs:
        v_links[v] = [e.index for e in bm.verts[v].link_edges
            if e.select]
    groups = make_groups(edges, e_links, v_links)
    frags = []
    for g in groups:
        frags.append([])
        [frags[-1].extend(e_links[e]) for e in g]
    return frags

class XformFragmentsView3DPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_idname = "VIEW3D_PT_Xform_Fragments"
    bl_label = "Transform Fragments"

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def draw(self, context):
        col = self.layout.column(align = True)
        col.operator("mesh.rotate_fragments", text = "Rotate")
        col.operator("mesh.scale_fragments", text = "Scale")
        col.operator("mesh.move_fragments", text = "Move Normal")
        

class RotateFragments(bpy.types.Operator):
    bl_idname = "mesh.rotate_fragments"
    bl_label = "Rotate Fragments"
    bl_options = {'GRAB_POINTER', 'BLOCKING', 'REGISTER', 'UNDO'}
    angle = FloatProperty(
        name="Angle",
        description="Angle to rotate fragments by",
        min=-100000.0,
        max=100000.0,
        default=0.0)
    axis = EnumProperty(
        name = "Axis",
        description="Axis to rotate about",
        items = [
            ('Normal', "Normal", ""),
            ('Z', "Z", ""),
            ('Y', "Y", ""),
            ('X', "X", "")],
        default = 'Normal')

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            reset(context, self.initial_coords)
            return {'CANCELLED'}
        elif event.type == 'X':
            reset(context, self.initial_coords)
            self.initial_pos = event.mouse_y
            self.axis = 'X'
        elif event.type == 'Y':
            reset(context, self.initial_coords)
            self.initial_pos = event.mouse_y
            self.axis = 'Y'
        elif event.type == 'Z':
            reset(context, self.initial_coords)
            self.initial_pos = event.mouse_y
            self.axis = 'Z'
        elif event.type == 'N':
            reset(context, self.initial_coords)
            self.initial_pos = event.mouse_y
            self.axis = 'Normal'
        elif event.type == 'MOUSEMOVE':
            self.angle = math.degrees(
                (event.mouse_y - self.initial_pos) * 0.01)
            self.execute(context)
        elif event.type in {'RET', 'LEFTMOUSE'}:
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            self.initial_pos = event.mouse_y
            bm = bmesh.from_edit_mesh(context.active_object.data)
            sel_edges = [e.index for e in bm.edges if e.select]
            if sel_edges:
                self.frags = group_by_adjacency(sel_edges, bm)
                self.initial_coords = initial_coords(self.frags, bm)
                self.normals = average_normals(self.frags, bm)
                self.xform_centers = xform_centers(self.frags, bm)
                self.orientation = orientation(context)
                self.angle = 0.0
                self.axis = 'Normal'
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                return {'CANCELLED'}
        else:
            return {'CANCELLED'}

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        for f in self.frags:
            for v in f:
                tm = mu.Matrix.Translation(self.xform_centers[v])
                rel_coords = self.initial_coords[v] - self.xform_centers[v]
                if self.axis == 'Normal':
                    rm = rotate_n(self.angle, self.normals[v])
                else:
                    rm = rotate_xyz(
                         self.angle, self.axis, self.orientation)
                bm.verts[v].co = tm * rm * rel_coords
            context.active_object.data.update()
        return {'FINISHED'}

class ScaleFragments(bpy.types.Operator):
    bl_idname = "mesh.scale_fragments"
    bl_label = "Scale Fragments"
    bl_options = {'GRAB_POINTER', 'BLOCKING', 'REGISTER', 'UNDO'}
    factor = FloatProperty(
        name="Factor",
        description="Scale factor",
        min=-100000.0,
        max=100000.0,
        default=1.0)
    axes = EnumProperty(
        name = "Axes",
        description="Axis or axes to apply scaling to",
        items = [
            ('Normal Radial', "Normal Radial", ""),
            ('Normal', "Normal", ""),
            ('XYZ', "XYZ", ""),
            ('XZ', "XZ", ""),
            ('YZ', "YZ", ""),
            ('XY', "XY", ""),
            ('Z', "Z", ""),
            ('Y', "Y", ""),
            ('X', "X", "")],
        default = 'XYZ')

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            reset(context, self.initial_coords)
            return {'CANCELLED'}
        elif event.type == 'X':
            reset(context, self.initial_coords)
            self.initial_pos = event.mouse_y
            if event.shift:
                self.axes = 'YZ'
            else:
                self.axes = 'X'
        elif event.type == 'Y':
            reset(context, self.initial_coords)
            self.initial_pos = event.mouse_y
            if event.shift:
                self.axes = 'XZ'
            else:
                self.axes = 'Y'
        elif event.type == 'Z':
            reset(context, self.initial_coords)
            self.initial_pos = event.mouse_y
            if event.shift:
                self.axes = 'XY'
            else:
                self.axes = 'Z'
        elif event.type == 'N':
            reset(context, self.initial_coords)
            self.initial_pos = event.mouse_y
            if event.shift:
                self.axes = 'Normal Radial'
            else:
                self.axes = 'Normal'
        elif event.type == 'U':
            reset(context, self.initial_coords)
            self.initial_pos = event.mouse_y
            self.axes = 'XYZ'
        elif event.type == 'MOUSEMOVE':
            self.factor = 1.0 + (event.mouse_y - self.initial_pos) * 0.01
            self.execute(context)
        elif event.type in {'RET', 'LEFTMOUSE'}:
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            self.initial_pos = event.mouse_y
            bm = bmesh.from_edit_mesh(context.active_object.data)
            sel_edges = [e.index for e in bm.edges if e.select]
            if sel_edges:
                self.frags = group_by_adjacency(sel_edges, bm)
                self.initial_coords = initial_coords(self.frags, bm)
                self.normals = average_normals(self.frags, bm)
                self.xform_centers = xform_centers(self.frags, bm)
                self.orientation = orientation(context)
                self.axes = 'XYZ'
                self.factor = 1.0
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                return {'CANCELLED'}
        else:
            return {'CANCELLED'}

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        for f in self.frags:
            for v in f:
                tm = mu.Matrix.Translation(self.xform_centers[v])
                rel_coords = (self.initial_coords[v] - self.xform_centers[v])
                if self.axes in {'Normal', 'Normal Radial'}:
                    sm = scale_n(self.factor, self.axes, self.normals[v])
                else:
                    sm = scale_xyz(self.factor, self.axes, self.orientation)
                bm.verts[v].co = tm * sm * rel_coords
        context.active_object.data.update()
        return {'FINISHED'}

class MoveFragments(bpy.types.Operator):
    bl_idname = "mesh.move_fragments"
    bl_label = "Move Fragments"
    bl_options = {'GRAB_POINTER', 'BLOCKING', 'REGISTER', 'UNDO'}
    distance = FloatProperty(
        name="Distance",
        description="How far to move fragments along their averaged normals",
        min=-100000.0,
        max=100000.0,
        default=0.0)

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            bm = bmesh.from_edit_mesh(context.active_object.data)
            self.initial_pos = event.mouse_y
            sel_edges = [e.index for e in bm.edges if e.select]
            if sel_edges:
                self.frags = group_by_adjacency(sel_edges, bm)
                self.initial_coords = initial_coords(self.frags, bm)
                self.normals = average_normals(self.frags, bm)
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                return {'CANCELLED'}
        else:
            return {'CANCELLED'}

    def execute(self, context):
        if context.area.type == 'VIEW_3D':
            bm = bmesh.from_edit_mesh(context.active_object.data)
            for f in self.frags:
                for v in f:
                    bm.verts[v].co = \
                        self.initial_coords[v] + \
                        self.normals[v] * self.distance
            context.active_object.data.update()
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            reset(context, self.initial_coords)
            return {'CANCELLED'}
        elif event.type in {'RET', 'LEFTMOUSE'}:
            return {'FINISHED'}
        elif event.type == 'MOUSEMOVE':
            self.distance = (event.mouse_y - self.initial_pos) * 0.01
            self.execute(context)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(XformFragmentsView3DPanel)
    bpy.utils.register_class(RotateFragments)
    bpy.utils.register_class(ScaleFragments)
    bpy.utils.register_class(MoveFragments)

def unregister():
    bpy.utils.unregister_class(XformFragmentsView3DPanel)
    bpy.utils.unregister_class(RotateFragments)
    bpy.utils.unregister_class(ScaleFragments)
    bpy.utils.unregister_class(MoveFragments)

if __name__ == "__main__":
    register()

