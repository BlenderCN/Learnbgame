#
# Copyright 2018 Fuji Sunflower
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import bpy
import numpy as np
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy_extras.view3d_utils import location_3d_to_region_2d
import bgl
import blf
from mathutils import Vector, Matrix

bl_info = {
    "name": "Love2D3D",
    "author": "Fuji Sunflower",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "3D View > Object Mode > Tool Shelf > Create > Love2D3D",
    "description": "Create 3D object from 2D image",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/FujiSunflower/love2d3d/wiki",
    "tracker_url": "https://github.com/FujiSunflower/love2d3d/issues",
    "category": "Add Mesh"
}

RGBA = 4  # Color size per pixels
RGB = 3  # Color size per pixels
R = 0  # Index of color
G = 1  # Index of color
B = 2  # Index of color
A = 3  # Index of color
X = 0  # Index
Y = 1  # Index
LEFT = 2  # Index
RIGHT = 3  # Index
BOTTOM = 4  # Index
TOP = 5  # Index
QUAD = 4  # Vertex Numer of Quad
FRONT = 0
BACK = 1
NAME = "Love2D3D"  # Name of 3D object

def draw_callback_px(self, context):
    #print("mouse points", len(self.mouse_path))

    #font_id = 0  # XXX, need to find out how best to get this.

    # draw some text
    #blf.position(font_id, 15, 30, 0)
    #blf.size(font_id, 20, 72)
    #blf.draw(font_id, "Hello Word " + str(len(self.mouse_path)))

    image = context.window_manager.love2d3d.image_front  # Image ID
    if image == "":
        return
    self.image = context.blend_data.images[image]  # Get image

    # 50% alpha, 2 pixel width line
    #bgl.glLineWidth(0)
    bgl.glEnable(bgl.GL_BLEND)
    #bgl.glClearColor(0.0, 0.0, 0.0, 0.0);
    #bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
    self.image.gl_load()
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.image.bindcode[0])
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    bgl.glEnable(bgl.GL_TEXTURE_2D)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST)
    #bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
    #bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)

    #self.image.bind()
    #bgl.glLineWidth(2)

#    bgl.glBegin(bgl.GL_LINE_STRIP)
#    for x, y in self.mouse_path:
#        bgl.glVertex2i(x, y)
#
#    bgl.glEnd()
    #camera = context.space_data.camera.location
    #sclip = context.space_data.clip_start
    #eclip = context.space_data.clip_end
    #lens = context.space_data.lens
    #pers = context.region_data.perspective_matrix
    #fovy = math.atan(pers[5]) * 2
    #aspect = pers[5] / pers[0]
    #bgl.gluPerspective(fovy, aspect, sclip, eclip);
    bgl.glMatrixMode(bgl.GL_MODELVIEW)
    #print(context.region_data.view_matrix)
    #ob = context.active_object
    #buff = bgl.Buffer(bgl.GL_FLOAT, [4, 4], context.region_data.view_matrix.transposed())
    #buff = bgl.Buffer(bgl.GL_FLOAT, [4, 4], ob.matrix_world.transposed())
    #mat = Matrix.Identity(4)
    mat = Matrix.Translation(context.space_data.cursor_location)
    view_align = context.window_manager.love2d3d.view_align
    if view_align:
        iview = Matrix(context.region_data.view_matrix).inverted_safe().to_3x3().to_4x4()
    else:
        iview = Matrix.Identity(4)
    buff = bgl.Buffer(bgl.GL_FLOAT, [4, 4], (mat * iview).transposed())
    bgl.glLoadMatrixf(buff)
    #bgl.glLoadIdentity()
    #camera = context.region_data.view_location
    #bgl.gluLookAt(camera.x, camera.y, camera.z, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    bgl.glMatrixMode(bgl.GL_PROJECTION);
    #bgl.glLoadIdentity();
    buff = bgl.Buffer(bgl.GL_FLOAT, [4, 4], context.region_data.perspective_matrix.transposed())
    bgl.glLoadMatrixf(buff)

    scale = context.window_manager.love2d3d.scale
    w, h = self.image.size
    w *= scale
    h *= scale
    #lb = location_3d_to_region_2d(context.region, context.space_data.region_3d, (-w / 2.0, 0, -h / 2.0))
    #rb = location_3d_to_region_2d(context.region, context.space_data.region_3d, (w / 2.0, 0, -h / 2.0))
    #rt = location_3d_to_region_2d(context.region, context.space_data.region_3d, (w / 2.0, 0, h / 2.0))
    #lt = location_3d_to_region_2d(context.region, context.space_data.region_3d, (-w / 2.0, 0, h /2.0))
    if view_align:
        lb = Vector((-w / 2.0, -h / 2.0, 0))
        rb = Vector((w / 2.0, -h / 2.0, 0))
        rt = Vector((w / 2.0, h / 2.0, 0))
        lt = Vector((-w / 2.0, h /2.0, 0))
    else:
        lb = Vector((-w / 2.0, 0, -h / 2.0))
        rb = Vector((w / 2.0, 0, -h / 2.0))
        rt = Vector((w / 2.0, 0, h / 2.0))
        lt = Vector((-w / 2.0, 0, h /2.0))
    #print(lt)
    bgl.glBegin(bgl.GL_QUADS)
    bgl.glTexCoord2d(0.0, 0.0)
    bgl.glVertex3f(lb.x, lb.y, lb.z)
    bgl.glTexCoord2d(1.0, 0.0)
    bgl.glVertex3f(rb.x, rb.y, lb.z)
    bgl.glTexCoord2d(1.0, 1.0)
    bgl.glVertex3f(rt.x, rt.y, rt.z)
    bgl.glTexCoord2d(0.0, 1.0)
    bgl.glVertex3f(lt.x, lt.y, lt.z)
    bgl.glEnd()
    self.image.gl_free()
    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_TEXTURE_2D)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


class Preview(bpy.types.Operator):

    bl_idname = "object.preview_love2d3d"
    bl_label = "Preview love2D3D"
    bl_description = "Preview love2D3D"
    bl_options = {'INTERNAL'}

    def modal(self, context, event):
        area = context.area        
        if area is None:
            return {'PASS_THROUGH'}
        area.tag_redraw()
        preview = context.window_manager.love2d3d.preview
        if not preview:
            return {'FINISHED'}
        #if event.type == 'MOUSEMOVE':
        #    #self.mouse_path.append((event.mouse_region_x, event.mouse_region_y))
        #    pass
        #elif event.type == 'LEFTMOUSE':
        #    bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        #    #self.image.gl_free()
        #    return {'FINISHED'}
        #
        #elif event.type in {'RIGHTMOUSE', 'ESC'}:
        #    bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        #    #self.image.gl_free()
        #    return {'CANCELLED'}

        #image = context.window_manager.love2d3d.image_front  # Image ID
        #if image == "":
        #    #return {"CANCELLED"}
        #    self.image = context.blend_data.images[image]  # Get image

        #return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        preview = context.window_manager.love2d3d.preview
        if context.area.type == 'VIEW_3D':
            # the arguments we pass the the callback
            args = (self, context)
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            if not preview:
                context.window_manager.love2d3d.preview = True
            else:
                context.window_manager.love2d3d.preview = False
                return {'FINISHED'}
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            #image = context.window_manager.love2d3d.image_front  # Image ID
            #if image == "":
            #    return {"CANCELLED"}
            #self.image = context.blend_data.images[image]  # Get image
            #self.image.gl_load()
            #self.mouse_path = []

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


class CreateObject(bpy.types.Operator, AddObjectHelper):

    bl_idname = "object.create_love2d3d"
    bl_label = "Create love2D3D"
    bl_description = "Create 3D object from 2D image."
    bl_options = {'REGISTER', 'UNDO'}
    #view_align = bpy.context.window_manager.love2d3d.view_align
    #view_align = bpy.props.BoolProperty(name="View align",
    #                                 description="Use view align for mesh")
    #view_align = True

    def execute(self, context):
        image = context.window_manager.love2d3d.image_front  # Image ID
        if image == "":
            return {"CANCELLED"}
        image = context.blend_data.images[image]  # Get image
        resolution = context.window_manager.love2d3d.rough  # Get resolution
        w, h = image.size  # Image width and height
        all = w * h
        pixels = image.pixels[:]  # Get slice of color infomation
        fronts = []
        backs = [[True for i in range(w)] for j in range(h)] # Whether background or not
        ex = h - resolution # End of list
        ey = w - resolution # End of list
        opacity = context.window_manager.love2d3d.opacity # Whether use opacity or not
        threshold = context.window_manager.love2d3d.threshold # threshold of background
        for y in range(resolution, ex)[::resolution]:
            left = 0 + y * w
            il = RGBA * left  # Get left index of color in image
            for x in range(resolution, ey)[::resolution]:
                back = False
                for v in range(resolution):
                    for u in range(resolution):
                        p = (x + u) + (y + v) * w #cuurent index in pixels
                        i = RGBA * p  #Get each index of color in image
                        if opacity:  # Whether opaque or not
                            c = pixels[i + A] # each opacity in image
                            cl = pixels[il + A] # left opacity in image
                            back = back or c <= threshold
                        else:  # Whether same color or not
                            c = pixels[i:i + RGB] # each RGB in image
                            cl = pixels[il:il + RGB] # left RGB in image
                            back = back or abs(c[R] - cl[R]) + \
                                abs(c[G] - cl[G]) \
                                + abs(cl[B] - cl[B]) <= threshold * 3.0
                        if back:
                            break
                    if back:
                        break
                backs[y][x] = back
                if not back:
                    fronts.append((x // resolution, y // resolution))
        del ex, ey, i, il, c, cl, back, pixels, p, left
        terms = [] #Edges of image
        for k, f in enumerate(fronts):
            fx = f[X]
            fy = f[Y]
            x = fx * resolution
            y = fy * resolution
            left = backs[y][x-resolution]
            right = backs[y][x+resolution]
            back = backs[y-resolution][x]
            top = backs[y+resolution][x]
            if not backs[y][x] and (left or right or back or top):
                terms.append((fx, fy))  # Get edge
            fronts[k] = (fx, fy, left, right, back, top)  # Insert edge info
        lens = [[0.0 for i in range(w)[::resolution]]
                for j in range(h)[::resolution]]
        if len(fronts) == 0:
            return {"CANCELLED"}
        sqAll = all ** 2
        xs = np.array([f[X] for f in fronts])  # X coordinates of each point
        ys = np.array([f[Y] for f in fronts])  # Y coordinates of each point
        ls = np.full(len(fronts), sqAll)
        for t in terms:
            ms = np.minimum(ls, np.power(t[X] - xs, 2) + np.power(t[Y] - ys, 2))
            ls = ms  # Watershed algorithm
        ms = np.sqrt(ls) + 1 # length array with softning
        m = np.max(ms)
        ls = np.divide(ms, m)  # Nomalize
        ms = (np.sin(ls * np.pi * 0.5) + 0)
        #ms = (np.arcsin(ls) + 0)

        for k, f in enumerate(fronts):
            fx = f[X]
            fy = f[Y]
            ls = ms[k] / 4.0  # Blur of height for edge
            lens[fy][fx] += ls
            fxi = fx + 1
            fyi = fy + 1
            lens[fy][fxi] += ls
            lens[fyi][fx] += ls
            lens[fyi][fxi] += ls
        del fx, fy, fxi, fyi, left, right, back, top, k, f, ms, ls, m
        verts = []
        nei = 1  # Neighbor
        uvs = []
        uvx = 0 / w
        uvy = 0 / h
        backs = []
        #self.view_align = context.window_manager.love2d3d.view_align
        view_align = context.window_manager.love2d3d.view_align
        scale = context.window_manager.love2d3d.scale
        s = min(w, h) / 8
        depth_front = s * context.window_manager.love2d3d.depth_front * scale
        depth_back = s * context.window_manager.love2d3d.depth_back * scale
        for f in fronts:
            x = f[X]
            y = f[Y]
            xi = x + nei
            yi = y + nei
            x1 = x * resolution
            x2 = xi * resolution
            y1 = y * resolution
            y2 = yi * resolution
            lu = x1 / w
            ru = x2 / w
            bu = y1 / h
            tu = y2 / h
            x1 = (x1 - w / 2) * scale
            x2 = (x2 - w / 2) * scale
            y1 = (y1 - h / 2) * scale
            y2 = (y2 - h / 2) * scale

            # Front face

            #p1 = (x1, -lens[yi][x] * depth_front, y2)
            #p2 = (x1, -lens[y][x] * depth_front, y1)
            #p3 = (x2, -lens[y][xi] * depth_front, y1)
            #p4 = (x2, -lens[yi][xi] * depth_front, y2)
            if view_align:
                p1 = (x1, y2, lens[yi][x] * depth_front)
                p2 = (x1, y1, lens[y][x] * depth_front)
                p3 = (x2, y1, lens[y][xi] * depth_front)
                p4 = (x2, y2, lens[yi][xi] * depth_front)
            else:
                p1 = (x1, -lens[yi][x] * depth_front, y2)
                p2 = (x1, -lens[y][x] * depth_front, y1)
                p3 = (x2, -lens[y][xi] * depth_front, y1)
                p4 = (x2, -lens[yi][xi] * depth_front, y2)
            verts.extend([p1, p2, p3, p4])
            u1 = (lu + uvx, tu + uvy)
            u2 = (lu + uvx, bu + uvy)
            u3 = (ru + uvx, bu + uvy)
            u4 = (ru + uvx, tu + uvy)
            uvs.extend([u1, u2, u3, u4])
            backs.append(FRONT)
            # Back face
            if view_align:
                p5 = (x2,  y2, -lens[yi][xi] * depth_back)
                p6 = (x2, y1, -lens[y][xi] * depth_back)
                p7 = (x1, y1, -lens[y][x] * depth_back)
                p8 = (x1, y2, -lens[yi][x] * depth_back)
            else:
                p5 = (x2, lens[yi][xi] * depth_back, y2)
                p6 = (x2, lens[y][xi] * depth_back, y1)
                p7 = (x1, lens[y][x] * depth_back, y1)
                p8 = (x1, lens[yi][x] * depth_back, y2)
            verts.extend([p5, p6, p7, p8])
            uvs.extend([u4, u3, u2, u1])
            backs.append(BACK)
            if f[LEFT]:  # Left face
                verts.extend([p8, p7, p2, p1])
                uvs.extend([u1, u2, u2, u1])
                backs.append(FRONT)
            if f[RIGHT]:  # Right face
                verts.extend([p4, p3, p6, p5])
                uvs.extend([u4, u3, u3, u4])
                backs.append(FRONT)
            if f[TOP]:  # Top face
                verts.extend([p8, p1, p4, p5])
                uvs.extend([u1, u1, u4, u4])
                backs.append(FRONT)
            if f[BOTTOM]:  # Bottom face
                verts.extend([p2, p7, p6, p3])
                uvs.extend([u2, u2, u3, u3])
                backs.append(FRONT)
        del p1, p2, p3, p4, p5, p6, p7, p8, lens, nei, x, y
        del xi, yi, lu, ru, bu, tu, x1, x2, y1, y2
        del u1, u2, u3, u4
        faces = [(0, 0, 0, 0)] * (len(verts) // QUAD)
        for n, f in enumerate(faces):
            faces[n] = (QUAD * n, QUAD * n + 1, QUAD * n + 2, QUAD * n + 3)
        msh = bpy.data.meshes.new(NAME)
        msh.from_pydata(verts, [], faces)  # Coordinate is Blender Coordinate
        msh.update()
        del verts, faces
        obj = object_data_add(context, msh, operator=self).object
        if view_align:
            iview = Matrix(context.region_data.view_matrix).inverted_safe().to_quaternion()
            angle = iview.angle
            axis = iview.axis
            bpy.ops.transform.rotate(value=angle, axis=axis)
        #obj = object_data_add(context, msh).object
        #obj = bpy.data.objects.new(NAME, msh)  # Create 3D object
        #scene = bpy.context.scene
        #scene.objects.link(obj)
        #bpy.ops.object.select_all(action='DESELECT')
        #if bpy.ops.object.mode_set.poll():
        #    bpy.ops.object.mode_set(mode='OBJECT')
        #obj.select = True
        bpy.context.scene.objects.active = obj
#        obj.location = (-w/2, 0, -h/2)  # Translate to origin
#        bpy.ops.object.transform_apply(location=True)
#        scale = context.window_manager.love2d3d.scale
#        obj.scale = (scale, scale, scale)
#        bpy.ops.object.transform_apply(scale=True)
#        obj.location = context.space_data.cursor_location

        channel_name = "uv"
        msh.uv_textures.new(channel_name)  # Create UV coordinate
        for idx, dat in enumerate(msh.uv_layers[channel_name].data):
            dat.uv = uvs[idx]
        del uvs
        # Crate fornt material
        matf = bpy.data.materials.new('Front')
        tex = bpy.data.textures.new('Front', type='IMAGE')
        tex.image = image
        matf.texture_slots.add()
        matf.texture_slots[0].texture = tex
        obj.data.materials.append(matf)
        # Crate back material
        matb = bpy.data.materials.new('Back')
        tex = bpy.data.textures.new('Back', type='IMAGE')
        image_back = context.window_manager.love2d3d.image_back
        if image_back == "":
            tex.image = image
        else:
            image_back = context.blend_data.images[image_back]
            tex.image = image_back
        matb.texture_slots.add()
        matb.texture_slots[0].texture = tex
        obj.data.materials.append(matb)
        for k, f in enumerate(obj.data.polygons):
            f.material_index = backs[k]  # Set back material
        bpy.context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')  # Remove doubled point
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.objects.active = obj  # Apply modifiers
        bpy.ops.object.modifier_add(type='SMOOTH')
        smo = obj.modifiers["Smooth"]
        smo.iterations = context.window_manager.love2d3d.smooth
        bpy.ops.object.modifier_add(type='DISPLACE')
        dis = obj.modifiers["Displace"]
        dis.strength = context.window_manager.love2d3d.fat * scale / 0.01
        if context.window_manager.love2d3d.modifier:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Displace")
        obj.select = True
        bpy.ops.object.shade_smooth()
        return {'FINISHED'}
    def draw(self, context):
        layout = self.layout
        #col = layout.column()
        #col.label(text="Custom Interface!")
        #row = col.row()
        #row.prop(self, "my_float")
        #row.prop(self, "my_bool")
        #layout.prop(self, "my_string")
        layout.prop(context.window_manager.love2d3d, "view_align")

class VIEW3D_PT_love2d3d(bpy.types.Panel):

    bl_label = "Love2D3D"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Create"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Object", icon="OBJECT_DATA")
        col.operator(CreateObject.bl_idname, text="Create")
        row = col.row()
        row.label(text="Preview")
        preview = context.window_manager.love2d3d.preview
        row.operator(Preview.bl_idname, text="On" if preview else "Off")
        col = layout.column(align=True)
        col.label(text="Image", icon="IMAGE_DATA")
        col.operator("image.open", icon="FILESEL")
        col.prop_search(context.window_manager.love2d3d,
                        "image_front", context.blend_data, "images")
        col.prop_search(context.window_manager.love2d3d,
                        "image_back", context.blend_data, "images")
        layout.separator()
        col = layout.column(align=True)
        col.label(text="Separation", icon="IMAGE_RGB_ALPHA")
        col.prop(context.window_manager.love2d3d, "threshold")
        col.prop(context.window_manager.love2d3d, "opacity")
        layout.separator()
        col = layout.column(align=True)
        col.label(text="Geometry", icon="EDITMODE_HLT")
        col.prop(context.window_manager.love2d3d, "view_align")
        col.prop(context.window_manager.love2d3d, "depth_front")
        col.prop(context.window_manager.love2d3d, "depth_back")
        col.prop(context.window_manager.love2d3d, "scale")
        layout.separator()
        col = layout.column(align=True)
        col.label(text="Quality", icon="MOD_SMOOTH")
        col.prop(context.window_manager.love2d3d, "rough")
        col.prop(context.window_manager.love2d3d, "smooth")
        col.prop(context.window_manager.love2d3d, "fat")
        layout.separator()
        col = layout.column(align=True)
        col.label(text="Option", icon="SCRIPTWIN")
        col.prop(context.window_manager.love2d3d, "modifier")


class Love2D3DProps(bpy.types.PropertyGroup):
    image_front = bpy.props.StringProperty(name="Front",
                                           description="Front image of mesh")
    image_back = bpy.props.StringProperty(name="Back",
                                          description="Back image of mesh")
    rough = bpy.props.IntProperty(name="Rough",
                                  description="Roughness of image", min=1,
                                  default=8, subtype="PIXEL")
    smooth = bpy.props.IntProperty(name="Smooth",
                                   description="Smoothness of mesh",
                                   min=1, default=30)
    scale = bpy.props.FloatProperty(name="Scale",
                                    description="Length per pixel",
                                    unit="LENGTH", min=0.001, default=0.01, precision=4)
    #depth_front = bpy.props.FloatProperty(name="Front",
    #                                      description="Depth of front face",
    #                                      unit="LENGTH", min=0, default=40)
    #depth_back = bpy.props.FloatProperty(name="Back",
    #                                     description="Depth of back face",
    #                                     unit="LENGTH", min=0, default=40)
    depth_front = bpy.props.FloatProperty(name="Front",
                                          description="Depth of front face",
                                          unit="NONE", min=0, default=1)
    depth_back = bpy.props.FloatProperty(name="Back",
                                         description="Depth of back face",
                                         unit="NONE", min=0, default=1)
    fat = bpy.props.FloatProperty(name="Fat",
                                  description="Fat of mesh",
                                  default=0.2, min=0.0)
    modifier = bpy.props.BoolProperty(name="Modifier",
                                      description="Apply modifiers to object",
                                      default=True)
    threshold = bpy.props.FloatProperty(name="Threshold",
                                        description="Threshold of background in image",
                                        min=0.0, max=1.0,
                                        default=0.0, subtype="FACTOR")
    opacity = bpy.props.BoolProperty(name="Opacity",
                                     description="Use Opacity for threshold")
    view_align = bpy.props.BoolProperty(name="View align",
                                     description="Use view align for mesh")
    preview = bpy.props.BoolProperty(name="Preview",
                                     description="Use preview for mesh now",
                                     options={'HIDDEN'})


def register():
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.love2d3d \
        = bpy.props.PointerProperty(type=Love2D3DProps)


def unregister():
    del bpy.types.WindowManager.love2d3d
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
