# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
try:
    # 2.57
    from add_object_utils import object_data_add
except:
    # 2.58 +
    from bpy_extras.object_utils import object_data_add
from bpy.props import FloatProperty, IntProperty, BoolProperty,\
    FloatVectorProperty, EnumProperty, StringProperty
from math import cos, pi, sin, sqrt, ceil, log
from .sculpty import check_clean, map_size, ImageBuffer,\
    create_mesh_object, createFaces, markSeams
from . import config


def vertex_uvs(mesh, uv_layer='sculptie'):
    done = []
    face_idx = len(mesh.faces) - 1
    verts = mesh.faces[face_idx].vertices
    vert_idx = len(verts)
    uv = mesh.uv_textures[uv_layer].data[face_idx].uv_raw
    while face_idx > 0 or vert_idx > 0:
        if vert_idx == 0:
            face_idx -= 1
            verts = mesh.faces[face_idx].vertices
            uv = mesh.uv_textures[uv_layer].data[face_idx].uv_raw
            vert_idx = len(verts)
        vert_idx -= 1
        if verts[vert_idx] not in done:
            done.append(verts[vert_idx])
            uv_idx = 2 * vert_idx
            yield (mesh.vertices[verts[vert_idx]], uv[uv_idx:uv_idx + 2])


class AddUVBase:
    '''Base class, only for subclassing
    subclasses must define
    - base_name, a string for the new object naming
    - get_vector(u, v) which returns a 3D location vector'''

    bl_options = {'REGISTER', 'UNDO'}

    obj_name = StringProperty(name="Name",
        description="Name for the object and sculpt map",
        default="Sculpty")

    sculpt_type = EnumProperty(
        items=(
            ('PRIM_SCULPT_TYPE_TORUS', 'Torus', 'Torus mapping'),
            ('PRIM_SCULPT_TYPE_SPHERE', 'Sphere', 'Spherical mapping'),
            ('PRIM_SCULPT_TYPE_PLANE', 'Plane', 'Planar mapping'),
            ('PRIM_SCULPT_TYPE_CYLINDER', 'Cylinder', 'Cylindrical mapping')),
        name="Sculpt Type",
        description="Sculpt Mapping Type",
        default='PRIM_SCULPT_TYPE_PLANE')
    faces_u = IntProperty(name="U Faces",
        description="Number of horizontal faces on UV map",
        default=8, min=1, max=256)
    faces_v = IntProperty(name="V Faces",
        description="Number of vertical faces on UV map",
        default=8, min=1, max=256)
    subdivision = IntProperty(name="Subdivision Levels",
        description="Number of subdivision levels",
        default=2, min=0, max=4)
    subdivision_mod = EnumProperty(
        items=(
            ('MULTIRES', 'Multires', 'Multiresolution'),
            ('SUBSURF', 'Subsurf', 'Subdivision Surface')),
        name="Modifier",
        description="Subdivision modifier type",
        default='SUBSURF')
    subdivision_type = EnumProperty(
        items=(
            ('SIMPLE', 'Simple', 'Simple subdivision'),
            ('CATMULL_CLARK', 'Catmull', 'Catmull-Clark subdivision')),
        name='Type',
        description='Subdivision type',
        default='CATMULL_CLARK')
    smooth = BoolProperty(name="Smooth Shading",
        description="Use smooth shading on faces",
        default=True)
    sculpty_clean = BoolProperty(name="Sculpty LODs",
        description="Force UV to Second Life sculpty LODs",
        default=True)
    sculpty = BoolProperty(name="Sculpty Map",
        description="Add sculptie UV and map image for baking",
        default=True)
    uvtex = BoolProperty(name="Add UVTex",
        description="Add 'UVTex' UV layout for texturing",
        default=False)
    rotate_u = FloatProperty(name="Rotate U",
        description="Offset U calculation for shape",
        default=0.0, min=-360.0, max=360.0,
        precision=3, step=500)
    rotate_v = FloatProperty(name="Rotate V",
        description="Offset U calculation for shape",
        default=0.0, min=-360.0, max=360.0,
        precision=3, step=500)

    # generic transform props
    view_align = BoolProperty(name="Align to View",
            default=False)
    location = FloatVectorProperty(name="Location",
            subtype='TRANSLATION')
    rotation = FloatVectorProperty(name="Rotation",
            subtype='EULER')

    image = None
    image_based = False
    wrap_u = False
    wrap_v = False
    clean = True
    w = 64
    h = 64
    previous_view_align = False
    u = 0
    v = 0
    flip_normals = False

    def draw_top(self, context):
        layout = self.layout
        layout.prop(self, 'obj_name')
        layout.prop(self, 'faces_u')
        layout.prop(self, 'faces_v')

    def draw_bottom(self, context):
        layout = self.layout
        if self.wrap_u:
            layout.prop(self, 'rotate_u')
        if self.wrap_v:
            layout.prop(self, 'rotate_v')
        layout.prop(self, 'subdivision')
        s, t, w, h, clean_s, clean_t = map_size(
            self.faces_u, self.faces_v, self.subdivision)
        self.clean = check_clean(
            w, h, self.faces_u, self.faces_v, self.sculpty_clean)
        self.w = w
        self.h = h
        if self.sculpty:
            if not self.clean:
                layout.label("Not sculpty aligned", "ERROR")
            if self.subdivision and s < self.faces_u and t < self.faces_v:
                layout.label("Subdivision too high", "ERROR")
            else:
                if s < self.faces_u:
                    layout.label("Max U faces: %s" % s, "ERROR")
                if t < self.faces_v:
                    layout.label("Max V faces: %s" % t, "ERROR")
            if w < 8:
                layout.label("Not enough U faces", "ERROR")
            if h < 8:
                layout.label("Not enough V faces", "ERROR")
        layout.prop(self, 'subdivision_mod')
        layout.prop(self, 'subdivision_type')
        layout.prop(self, 'smooth')
        layout.prop(self, 'sculpty',
            text="Sculpt Map %s x %s" % (self.w, self.h))
        if self.sculpty:
            pow2 = [2, 4, 8, 16, 32, 64, 128, 256]
            if not self.clean or self.faces_u not in pow2 or\
                    self.faces_v not in pow2:
                layout.prop(self, 'sculpty_clean')
            layout.prop(self, 'uvtex')
        layout.prop(self, 'view_align')
        col = layout.column()
        col.prop(self, 'location')
        col.prop(self, 'rotation')

    def draw(self, context):
        self.draw_top(context)
        self.draw_bottom(context)

    def check(self, context):
        # handle turning off view align
        if not self.view_align and self.previous_view_align:
            self.rotation = (0.0, 0.0, 0.0)
        self.previous_view_align = self.view_align
        # min of faces changes if wrap enabled
        if self.wrap_u and self.faces_u < 3:
            self.faces_u = 3
        if self.wrap_v and self.faces_v < 3:
            self.faces_v = 3
        s, t, w, h, clean_s, clean_t = map_size(
            self.faces_u, self.faces_v, self.subdivision)
        ready = True
        if self.sculpty:
            if self.subdivision and s < self.faces_u and t < self.faces_v:
                ready = False
            else:
                if s < self.faces_u or t < self.faces_v:
                    ready = False
            if w < 8 or h < 8:
                ready = False
        return ready

    def execute(self, context):
        # only keep image if using it
        if not self.image_based:
            if self.image:
                if self.image.users:
                    self.image.user_clear()
                if self.image.name in bpy.data.images:
                    bpy.data.images.remove(self.image)
                self.image = None
        # Toggle Edit mode
        try:
            is_editmode = (context.active_object.mode == 'EDIT')
        except:
            is_editmode = False
        if is_editmode:
            bpy.ops.object.mode_set(mode='OBJECT')

        verts_u = self.faces_u + 1
        verts_v = self.faces_v + 1
        if self.wrap_u and self.faces_u == 1:
            verts_u += 1
        if self.wrap_v and self.faces_v == 1:
            verts_v += 1
        uvgrid_u = []
        uvgrid_v = []
        uvgrid_s = []
        uvgrid_t = []
        if self.sculpty:
            # get settings from sculpty map size function
            s, t, w, h, clean_s, clean_t = map_size(
                verts_u - 1, verts_v - 1, self.subdivision)
        else:
            # fixed u v spacing
            w = h = 1
            s = verts_u - 1
            t = verts_v - 1
            clean_s = False
            clean_t = False
        verts_u = s + 1
        verts_v = t + 1
        actual_u = verts_u - self.wrap_u
        actual_v = verts_v - self.wrap_v
        clean_s = clean_s & self.sculpty_clean
        clean_t = clean_t & self.sculpty_clean
        level_mask = 0xFFFE
        for i in range(self.subdivision):
            level_mask = level_mask << 1
        # uvgrid_s and uvgrid_t will hold uv layout positions
        for i in range(s):
            p = w * i / float(s)
            if clean_s:
                p = int(p) & level_mask
            if p:
                p = p / float(w)
            uvgrid_s.append(p)
        uvgrid_s.append(1.0)
        for i in range(t):
            p = h * i / float(t)
            if clean_t:
                p = int(p) & level_mask
            if p:
                p = p / float(h)
            uvgrid_t.append(p)
        uvgrid_t.append(1.0)

        # build list of 3D locations for vertices
        verts = []
        for self.v in range(actual_v):
            for self.u in range(actual_u):
                vec_u = self.u / (verts_u - 1)
                if self.wrap_u:
                    vec_u += self.rotate_u / 360.0
                vec_v = self.v / (verts_v - 1)
                if self.wrap_v:
                    vec_v += self.rotate_v / 360.0
                verts.append(self.get_vector(vec_u, vec_v))

        # build list of faces
        faces = []
        first_row = range(actual_u)
        for v in range(1, actual_v):
            second_row = [idx + actual_u for idx in first_row]
            faces.extend(createFaces(first_row, second_row, self.wrap_u))
            first_row = second_row
        if self.wrap_v:
            faces.extend(createFaces(second_row, range(actual_u), self.wrap_u))

        # build list of seams - these should be all edges with
        # u=0 and/or with v=0 depending on wrap settings
        seams = []
        if self.wrap_u:
            first_vertex = 0
            for i in range(actual_v - 1):
                second_vertex = first_vertex + actual_u
                seams.append((first_vertex, second_vertex))
                first_vertex = second_vertex
            if self.wrap_v:
                seams.append((0, first_vertex))
        if self.wrap_v:
            first_vertex = 0
            for i in range(actual_u - 1):
                second_vertex = first_vertex + 1
                seams.append((first_vertex, second_vertex))
                first_vertex = second_vertex
            if self.wrap_u:
                seams.append((0, first_vertex))

        create_mesh_object(context, verts, [], faces, self.obj_name, self)
        obj = context.active_object
        # end up in edit mode here if set in preferences, so set back.
        bpy.ops.object.mode_set(mode='OBJECT')
        markSeams(obj.data, seams)

        # build list of uv faces
        uvfaces = []
        first_row = [(uvgrid_s[u], 0.0) for u in range(verts_u)]
        for v in range(1, verts_v):
            second_row = [(uvgrid_s[u], uvgrid_t[v]) for u in range(verts_u)]
            faces = createFaces(first_row, second_row, False)
            if self.wrap_u:
                # match face order of wrapped mesh
                faces = [faces[-1]] + faces[:-1]
                # correct vert order for wrapped face
                fix = faces[0]
                faces[0] = (fix[2], fix[3], fix[0], fix[1])
            uvfaces.extend(faces)
            first_row = second_row

        # create UVTex layout
        uvtex = obj.data.uv_textures.new()
        for face_idx in range(len(uvfaces)):
            uvtex.data[face_idx].uv1 = uvfaces[face_idx][0]
            uvtex.data[face_idx].uv2 = uvfaces[face_idx][1]
            uvtex.data[face_idx].uv3 = uvfaces[face_idx][2]
            uvtex.data[face_idx].uv4 = uvfaces[face_idx][3]

        if self.sculpty:
            if self.uvtex:
                s_map = obj.data.uv_textures.new(name="sculptie")
            else:
                s_map = uvtex
                s_map.name = "sculptie"
            if self.image == None:
                if not config.minimise_map:
                    levels = self.subdivision
                    while w * h <= 1024:
                        levels += 1
                        s, t, w, h, cs, ct = map_size(uc, vc, levels)
                self.image = bpy.data.images.new(name=self.obj_name,
                    width=w,
                    height=h,
                    alpha=True)
            for f in s_map.data:
                f.image = self.image
                f.use_image = True
            obj.prim.type = 'PRIM_TYPE_SCULPT'
            obj.prim.sculpt_type = self.sculpt_type

        if self.subdivision:
            bpy.ops.object.modifier_add(type=self.subdivision_mod)
            if self.subdivision_mod == 'MULTIRES':
                m = obj.modifiers['Multires']
                m.subdivision_type = self.subdivision_type
                if  self.sculpty:
                    uv_layer = 'sculptie'
                else:
                    uv_layer = 'UVTex'
                for i in range(self.subdivision):
                    bpy.ops.object.multires_subdivide(modifier="Multires")
                hires = obj.to_mesh(context.scene, True, 'RENDER')
                for v, uv in vertex_uvs(hires, uv_layer):
                    vec_u = uv[0]
                    if self.wrap_u:
                        vec_u += self.rotate_u / 360.0
                    vec_v = uv[1]
                    if self.wrap_v:
                        vec_v += self.rotate_v / 360.0
                    v.co = self.get_vector(vec_u, vec_v)
                object_data_add(context, hires, self)
                obj2 = context.active_object
                context.scene.objects.active = obj
                bpy.ops.object.multires_reshape(modifier="Multires")
                context.scene.objects.unlink(obj2)
                bpy.data.objects.remove(obj2)
                bpy.data.meshes.remove(hires)
                bpy.ops.object.multires_base_apply(modifier="Multires")
            else:
                m = obj.modifiers['Subsurf']
                m.subdivision_type = self.subdivision_type
                m.levels = self.subdivision
                m.render_levels = self.subdivision
                m.use_subsurf_uv = False
                m.show_on_cage = True

        bpy.ops.object.mode_set(mode='EDIT')

        # blender bug: inside not working when set to self.flip_normals
        bpy.ops.mesh.normals_make_consistent(inside=False)
        if self.flip_normals:
            bpy.ops.mesh.flip_normals()
            # arrgh.. still not flipping cone normals correctly..
            # works if done manually.. test again when bug fixed..
        if self.smooth:
            bpy.ops.mesh.faces_shade_smooth()

        if not (is_editmode or \
            context.user_preferences.edit.use_enter_edit_mode):
            bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}

    def invoke(self, context, event):
        self.obj_name = self.base_name
        return self.execute(context)


class AddUVPlane(bpy.types.Operator, AddUVBase):
    base_name = "Plane"
    bl_idname = "mesh.uv_shape_plane_add"
    bl_label = "Add plane UV shape"

    def get_vector(self, u, v):
        return (u - 0.5, v - 0.5, 0.0)


class AddUVBricks(bpy.types.Operator, AddUVBase):
    base_name = "Bricks"
    bl_idname = "mesh.uv_shape_bricks_add"
    bl_label = "Add bricks UV shape"

    sculpt_type = 'PRIM_SCULPT_TYPE_CYLINDER'
    wrap_u = True

    rotate_u = FloatProperty(name="Rotate U",
        description="Offset U calculation for shape",
        default=0.0, min=-90.0, max=180.0,
        precision=3, step=500)

    brick_height = IntProperty(name="Height",
        description="Number of Z faces per brick",
        default=1, min=1, max=15)
    brick_depth = IntProperty(name="Depth",
        description="Number of Y faces per brick",
        default=1, min=1, max=15)
    brick_width = IntProperty(name="Width",
        description="Number of X faces per brick",
        default=1, min=1, max=30)

    count = 0

    def draw(self, context):
        t = self.check(context)
        layout = self.layout
        layout.label("Add %s bricks" % self.count)
        layout.prop(self, 'obj_name')
        layout.prop(self, 'brick_width')
        layout.prop(self, 'brick_depth')
        layout.prop(self, 'brick_height')
        self.draw_bottom(context)

    def check(self, context):
        self.count = 1
        self.faces_u = 2 * (self.brick_depth + self.brick_height)
        self.faces_v = self.brick_width + 2
        u = int(pow(2, 1 + ceil(log(self.faces_u) / log(2))) / 2)
        v = self.faces_v + 1
        cont = True
        while cont:
            vt = self.faces_v + v
            m = 1024 / pow(2, 2 * self.subdivision)
            if u * int(pow(2, 1 + ceil(log(vt) / log(2))) / 2) <= m:
                s, t, w, h, clean_s, clean_t = map_size(
                    u, vt, self.subdivision)
                if w * h <= 4096:
                    self.count += 1
                    self.faces_v = vt
                    self.w = w
                    self.h = h
                else:
                    cont = False
            else:
                cont = False
        r = self.faces_u * self.faces_v * pow(2, self.subdivision) <= 1024
        r = r and AddUVBase.check(self, context)
        return r

    def get_vector(self, u, v):
        faces = 2 * (self.brick_depth + self.brick_height)
        c1 = self.brick_depth / faces
        c2 = 0.5
        c3 = (2 * self.brick_depth + self.brick_height) / faces
        corners = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]
        offsets = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]
        length = self.brick_width + 3
        pos = self.v % length
        if u == 1.0:
            side = 0
            offset = 0
        elif u < c1:
            side = 0
            offset = u / c1
        elif u < c2:
            side = 1
            offset = (u - c1) / (c2 - c1)
        elif u < c3:
            side = 2
            offset = (u - c2) / c1
        else:
            side = 3
            offset = (u - c3) / (c2 - c1)
        y, z = corners[side]
        oy, oz = offsets[side]
        z += oz * offset
        y += oy * offset
        if pos > (self.brick_width + 1):
            z = 0.0
            y = 0.0
            v -= 1.0 / self.faces_v
        if pos == 0:
            z = 0.0
            y = 0.0
            v += 1.0 / self.faces_v
        return (v - 0.5, y, z)

    def invoke(self, context, event):
        self.check(context)
        return AddUVBase.invoke(self, context, event)


class AddUVSphere(bpy.types.Operator, AddUVBase):
    base_name = "Sphere"
    bl_idname = "mesh.uv_shape_sphere_add"
    bl_label = "Add sphere UV shape"

    sculpt_type = 'PRIM_SCULPT_TYPE_SPHERE'
    wrap_u = True

    def get_vector(self, u, v):
        a = pi + 2 * pi * u
        ps = sin(pi * v) / 2.0
        x = sin(a) * ps
        y = -cos(a) * ps
        z = -cos(pi * v) / 2.0
        return (x, y, z)


class AddUVCylinder(bpy.types.Operator, AddUVBase):
    base_name = "Cylinder"
    bl_idname = "mesh.uv_shape_cylinder_add"
    bl_label = "Add cylinder UV shape"

    sculpt_type = 'PRIM_SCULPT_TYPE_CYLINDER'
    wrap_u = True

    def get_vector(self, u, v):
        a = pi + 2 * pi * u
        x = sin(a) / 2.0
        y = -cos(a) / 2.0
        return (x, y, v - 0.5)


class AddUVTorus(bpy.types.Operator, AddUVBase):
    base_name = "Torus"
    bl_idname = "mesh.uv_shape_torus_add"
    bl_label = "Add torus UV shape"

    sculpt_type = 'PRIM_SCULPT_TYPE_TORUS'
    wrap_u = True
    wrap_v = True

    radius = FloatProperty(
        name="Radius",
        description="Radius",
        min=0.05,
        max=0.5,
        default=0.25,
        precision=3,
        step=1)

    axis = bpy.props.EnumProperty(
        items=(
            ('Z', 'Z', 'Rotate around Z'),
            ('Y', 'Y', 'Rotate around Y'),
            ('X', 'X', 'Rotate around X')),
        name="Axis",
        description="Axis to rotate around",
        default='Z')

    def get_vector(self, u, v):
        if self.axis == "X":
            u, v = v, u
        a = pi + 2 * pi * u
        v += 0.25
        ps = ((1.0 - self.radius) - sin(2.0 * pi * v) * self.radius) / 2.0
        x = sin(a) * ps
        y = -cos(a) * ps
        z = cos(2 * pi * v) / 2.0
        if self.axis == "Y":
            x, y, z = -x, z, -y
        elif self.axis == "X":
            x, y, z = z, y, x
        return (x, y, z)

    def draw(self, context):
        self.draw_top(context)
        self.layout.prop(self, 'axis')
        self.layout.prop(self, 'radius')
        self.draw_bottom(context)


class AddUVHemisphere(bpy.types.Operator, AddUVBase):
    base_name = "Hemisphere"
    bl_idname = "mesh.uv_shape_hemisphere_add"
    bl_label = "Add hemisphere UV shape"

    def get_vector(self, u, v):
        z = cos(2 * pi * min(u, v, 1.0 - u, 1.0 - v)) / -2.0
        pa = u - 0.5
        pr = v - 0.5
        ph = sqrt(pa * pa + pr * pr)
        ps = sqrt(sin((0.5 - z) * pi * 0.5) / 2.0)
        if ph == 0.0:
            ph = 1.0
        sr2 = sqrt(2.0)
        x = (pa / ph * ps) / sr2
        y = (pr / ph * ps) / sr2
        return (x, y, 0.25 + z * 0.5)


class AddUVCone(bpy.types.Operator, AddUVBase):
    base_name = "Cone"
    bl_idname = "mesh.uv_shape_cone_add"
    bl_label = "Add cone UV Shape"

    sculpt_type = 'PRIM_SCULPT_TYPE_SPHERE'
    wrap_u = True

    base = FloatProperty(
        name="Base",
        description="Percent of mesh to assign to base",
        min=0.0,
        max=100.0,
        default=50.0,
        precision=2,
        step=100)

    def check(self, context):
        self.flip_normals = True
        if self.base == 0.0 or self.base == 100.0:
            self.sculpt_type = 'PRIM_SCULPT_TYPE_CYLINDER'
            if self.base == 100.0:
                self.flip_normals = False
        else:
            self.sculpt_type = 'PRIM_SCULPT_TYPE_SPHERE'
        return AddUVBase.check(self, context)

    def get_vector(self, u, v):
        b = self.base / 100.0
        if b == 1.0:
            v = 1.0 - v
        if v == 0.0:
            z = 0.0
            if b > 0.0:
                s = 0.0
            else:
                s = 1.0
        elif v <= b:
            z = 0.0
            s = v / b
        else:
            z = (v - b) / (1.0 - b)
            s = 1.0 - z
        a = pi + 2 * pi * u
        x = sin(a) / 2.0 * s
        y = -cos(a) / 2.0 * s
        return (x, y, z)

    def draw(self, context):
        self.draw_top(context)
        self.layout.prop(self, 'base')
        self.draw_bottom(context)


class AddUVRing(bpy.types.Operator, AddUVBase):
    base_name = "Ring"
    bl_idname = "mesh.uv_shape_ring_add"
    bl_label = "Add ring UV shape"

    sculpt_type = 'PRIM_SCULPT_TYPE_TORUS'
    wrap_u = True
    wrap_v = True

    radius = FloatProperty(
        name="Radius",
        description="Radius",
        min=0.1,
        max=0.5,
        default=0.25,
        precision=3,
        step=1)

    axis = bpy.props.EnumProperty(
        items=(
            ('Z', 'Z', 'Rotate around Z'),
            ('Y', 'Y', 'Rotate around Y'),
            ('X', 'X', 'Rotate around X')),
        name="Axis",
        description="Axis to rotate around",
        default='Z')

    def get_vector(self, u, v):
        if self.axis != "Z":
            u, v = v, u
        if v < 0.125:
            z = v * 4.0
            s = 0.5
        elif v < 0.375:
            z = 0.5
            s = 0.5 - self.radius * (v - 0.125) / 0.25
        elif v <= 0.625:
            z = (v - 0.5) * -4.0
            s = 0.5 - self.radius
        elif v < 0.875:
            z = -0.5
            s = (0.5 - self.radius) + self.radius * (v - 0.625) / 0.25
        else:
            z = (1.0 - v) * -4.0
            s = 0.5
        a = pi + 2 * pi * u
        x = sin(a) * s
        y = -cos(a) * s
        if self.axis == "Y":
            x, y, z = y, z, x
        elif self.axis == "X":
            x, y, z = z, y, x
        return (x, y, z)

    def draw(self, context):
        self.draw_top(context)
        self.layout.prop(self, 'axis')
        self.layout.prop(self, 'radius')
        self.draw_bottom(context)


class AddUVSteps(bpy.types.Operator, AddUVBase):
    base_name = "Steps"
    bl_idname = "mesh.uv_shape_steps_add"
    bl_label = "Add steps UV shape"

    capped = BoolProperty(name="Flatten ends",
        description="Flatten ends of steps",
        default=True)

    def check(self, context):
        if self.capped and self.faces_u < 3:
            self.faces_u = 3
        return AddUVBase.check(self, context)

    def draw(self, context):
        self.draw_top(context)
        self.layout.prop(self, 'capped')
        self.draw_bottom(context)

    def get_vector(self, u, v):
        if v == 0:
            z = 0
        elif (self.faces_v * v) % 2:
            z = 1.0 / self.faces_v
        else:
            z = 0
        if self.capped:
            if u < 1.0 / self.faces_u:
                x = -0.5
                z = 0
            elif u > (self.faces_u - 1) / self.faces_u:
                x = 0.5
                z = 0
            else:
                x = (u - 0.5) * (self.faces_u / (self.faces_u - 2))
        else:
            x = u - 0.5
        return (x, v - 0.5, z)


class AddUVStar(bpy.types.Operator, AddUVBase):
    base_name = "Star"
    bl_idname = "mesh.uv_shape_star_add"
    bl_label = "Add star UV shape"

    sculpt_type = 'PRIM_SCULPT_TYPE_CYLINDER'
    wrap_u = True

    depth = FloatProperty(
        name="Depth",
        description="Depth",
        min=-1.0,
        max=1.0,
        default=0.6,
        precision=3,
        step=5)

    taper = FloatProperty(
        name="Taper",
        description="Taper",
        min=0.0,
        max=1.0,
        default=1.0,
        precision=3,
        step=5)

    rotate_u = FloatProperty(name="Rotate U",
        description="Offset U calculation for shape",
        default=0.0, min=-360.0, max=360.0,
        precision=3, step=100)

    def draw(self, context):
        self.draw_top(context)
        self.layout.prop(self, 'depth')
        self.layout.prop(self, 'taper')
        self.draw_bottom(context)

    def get_vector(self, u, v):
        z = v - 0.5
        s = 0.5 - abs(z) * self.taper
        odd = self.u % 2
        offset = abs((self.faces_u * u) % 1 - 0.5) * 2.0
        if odd:
            offset = 1.0 - offset
        s = s * (1.0 - self.depth * offset)
        a = pi + 2 * pi * u
        x = sin(a) * s
        y = -cos(a) * s
        return (x, y, z)

#TODO: AddUVImage is affected by these two bugs. Test and finish when possible
# http://projects.blender.org/tracker/index.php?func=detail&aid=26618
# http://projects.blender.org/tracker/index.php?func=detail&aid=26619


class AddUVImage(bpy.types.Operator, AddUVBase):
    base_name = "Sculptie"
    bl_idname = "mesh.uv_shape_image_add"
    bl_label = "Add UV Shape from Sculpt Map"

    filepath = StringProperty(name='Sculpt Map',
        subtype='FILE_PATH')

    buffer = None
    image_based = True
    prev_name = ""

    def draw_top(self, context):
        layout = self.layout
        self.layout.prop(self, 'filepath')
        if self.buffer is not None:
            layout.prop(self, 'obj_name')
            self.layout.prop(self, 'sculpt_type', text='Type')
        layout.prop(self, 'faces_u')
        layout.prop(self, 'faces_v')
        if self.buffer is not None:
            if self.subdivision_mod == 'MULTIRES':
                s = self.subdivision
            else:
                s = 0
            if self.faces_u * pow(2, s + 1) > self.buffer.x:
                self.layout.label("Image U size exceeded", 'ERROR')
            if self.faces_v * pow(2, s + 1) > self.buffer.y:
                self.layout.label("Image V size exceeded", 'ERROR')

    def get_vector(self, u, v):
        if self.buffer is not None:
            # correct for sliding
            while u < 0.0:
                u += 1.0
            while u > 1.0:
                u -= 1.0
            while v < 0.0:
                v += 1.0
            while v > 1.0:
                v -= 1.0
            if self.sculpt_type[17:] == 'SPHERE':
                if v == 0.0 or v == 1.0:
                    u = 0.5
            x = int(u * self.buffer.x)
            y = int(v * self.buffer.y)
            c = self.buffer.get_pixel(x, y)
            c1 = c
            if c is not None:
                return (c.r - 0.5, c.g - 0.5, c.b - 0.5)
        # Default sculpty shape is small sphere
        vec = AddUVSphere.get_vector(self, u, v)
        return (vec[0] * 0.5, vec[1] * 0.5, vec[2] * 0.5)

    def check(self, context):
        if self.filepath != "":
            for img in bpy.data.images:
                if not img.is_dirty:
                    if img.filepath == self.filepath:
                        img.reload()
            image = bpy.data.images.load(self.filepath)
            image.update()
            self.buffer = ImageBuffer(image, clear=False)
            if self.prev_name != self.filepath:
                self.obj_name = bpy.path.display_name_from_filepath(
                    self.filepath)
                self.faces_u, self.faces_v, self.subdivision =\
                    self.buffer.model()
                type = self.buffer.map_type()
                self.sculpt_type = "PRIM_SCULPT_TYPE_%s" % type
                if self.buffer.x * self.buffer.y <= 8192:
                    for i in range(self.subdivision):
                        self.faces_u *= 2
                        self.faces_v *= 2
                    self.subdivision = 0
                self.prev_name = self.filepath
            type = self.sculpt_type[17:]
            if type != 'PLANE':
                self.wrap_u = True
            else:
                self.wrap_u = False
            if type == 'TORUS':
                self.wrap_v = True
            else:
                self.wrap_v = False
            if self.subdivision_mod == 'MULTIRES':
                s = self.subdivision
            else:
                s = 0
            if self.faces_u * pow(2, s + 1) > self.buffer.x:
                return False
            if self.faces_v * pow(2, s + 1) > self.buffer.y:
                return False
            return AddUVBase.check(self, context)
        if self.image:
            #undo during operator settings doesn't remove images
            if self.image.users:
                self.image.user_clear()
            if self.image.name in bpy.data.images:
                bpy.data.images.remove(self.image)
            self.image = None
        self.buffer = None
        return False

    def execute(self, context):
        if self.filepath != "" and self.buffer is None:
            self.check(context)
        if self.buffer is None:
            self.sculpt_type = 'PRIM_SCULPT_TYPE_SPHERE'
            self.wrap_u = True
            self.wrap_v = False
            if self.image:
                #undo during operator settings doesn't remove images
                if self.image.users:
                    self.image.user_clear()
                if self.image.name in bpy.data.images:
                    bpy.data.images.remove(self.image)
                self.image = None
        else:
            if self.image:
                #undo during operator settings doesn't remove images
                if self.image != self.buffer.image:
                    if self.image.users:
                        self.image.user_clear()
                    if self.image.name in bpy.data.images:
                        bpy.data.images.remove(self.image)
                self.image = None
            # can we use the sculpt map?
            if self.subdivision == 0 or self.subdivision_mod == 'MULTIRES':
                x = self.faces_u * pow(2, self.subdivision + 1)
                y = self.faces_v * pow(2, self.subdivision + 1)
                if (x, y) == (self.buffer.x, self.buffer.y):
                    self.image = self.buffer.image
                    self.image.name = self.obj_name
        return AddUVBase.execute(self, context)

    def invoke(self, context, event):
        return self.execute(context)
