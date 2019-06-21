import bpy
from math import  sqrt
from random import random
from mathutils import Vector, Color
from . ray import Ray
from . hitable_list import Hitable_list
from . sphere import Sphere
from . hit_record import  Hit_record
from . camera import Camera


# http://excamera.com/sphinx/article-srgb.html
def s2lin(color):
    a = 0.055
    return Color([x * (1.0 / 12.92) if x <= 0.04045 else pow((x + a) * (1.0 / (1 + a)), 2.4) for x in color])


class ToasterRenderEngine(bpy.types.RenderEngine):
    # These three members are used by blender to set up the
    # RenderEngine; define its internal name, visible name and capabilities.
    bl_idname = "toaster_renderer"
    bl_label = "Toaster"
    bl_use_preview = True

    # This is the only method called by blender, in this example
    # we use it to detect preview rendering and call the implementation
    # in another method.
    def render(self, sc):
        scene=bpy.data.scenes[0]
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)
        print("Rendering " + str(self.size_x) + "x" + str(self.size_y) + " ("+ str(scale) +" scale)")

        if self.is_preview:
            self.render_preview(scene)
        else:
            self.render_colors(scene)

    def color(self, ray, world):
        #t= self.hit_sphere(Vector((0, 0, -1)), 0.5, ray)
        #if t > 0:
        #    N=Vector(ray.point_at_parameter(t)-Vector((0,0,-1))).normalized()
        #    return(Color( (N+Vector((1,1,1))) * 0.5 ))

        hit_record = Hit_record(t=0, p=Vector((0, 0, 0)), normal=Vector((0, 0, 0)))

        if world.hit(ray, 0.0, 10000, hit_record):
            return(Color( (hit_record.normal+Vector((1,1,1))) * 0.5 )) #Vector((hit_record.normal.x + 1, hit_record.normal.y + 1, hit_record.normal.z + 1)) * 0.5
        else:
            # blend the y-value of direction
            unit_direction = ray.direction.normalized()
            t = 0.5 * (unit_direction.y + 1.0)
            return Color(Vector((1.0, 1.0, 1.0)).lerp(Vector((0.5, 0.7, 1.0)), t))

    def hit_sphere(self, center, radius, ray):

        oc = ray.origin - center
        a = ray.direction.dot(ray.direction)
        b = 2 * oc.dot(ray.direction)
        c = oc.dot(oc) - radius * radius

        discriminant = b * b - 4 * a * c

        if discriminant < 0: return -1.0
        else: return (-b - sqrt(discriminant)) / (2 * a)


    def render_colors(self, scene):
        nx = self.size_x
        ny = self.size_y
        ns = scene.toaster.spp #bpy.data.scenes[0].toaster.spp
        pixel_count = self.size_x * self.size_y

        # The framebuffer is defined as a list of pixels, each pixel
        # itself being a list of R,G,B,A values
        framebuffer = [(0.0, 0.0, 0.0, 1.0)]*pixel_count

        # Here we write the pixel values to the RenderResult
        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]
        pixel = 0

        camera = Camera()

        sphere1 = Sphere(Vector((0.0, 0.0, -1.0)), 0.5)
        sphere2 = Sphere(Vector((0.0, -100.5, -1.0)), 100.0)
        world = Hitable_list([sphere1, sphere2])

        for j in range(0, ny):
            for i in range(0, nx):
                col = Color((0.0, 0.0, 0.0))
                for k in range(0, ns):
                    u = float(i+random()) / float(nx)
                    v = float(j+random()) / float(ny)


                    # simple camera
                    ray = camera.get_ray(u, v)
                    col += self.color(ray, world)

                # update framebuffer
                col /= ns
                col = s2lin(col)
                framebuffer[pixel] = (col.r, col.g, col.b, 1.0)
                pixel += 1

            if j % 100 == 0 :
                layer.rect=framebuffer
                self.update_result(result)

        layer.rect = framebuffer
        self.end_result(result)
