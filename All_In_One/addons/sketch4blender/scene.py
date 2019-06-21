import math

from copy import deepcopy

from .geometry import Vector, Point, Transform, hermite_interp

import bpy
import bmesh
from bmesh.types import BMesh, BMVert, BMEdge, BMFace


class Renderable(object):
    uuid = 0
    def __init__(self):
        self.uuid = Renderable.uuid
        Renderable.uuid += 1

    def flatten(self, transform):
        print("no flatten:", repr(self))
        return self

    def render_to_blender(self, context):
        print("no to_blender:", repr(self))

    def _get_gpencil_frame(self):
        S = bpy.context.scene
        if not S.grease_pencil:
            a = [ a for a in bpy.context.screen.areas if a.type == "VIEW_3D" ][0]
            override = {
                    'scene' : S,
                    'screen' : bpy.context.screen,
                    'object' : bpy.context.object,
                    'area' : a,
                    'region' : a.regions[0],
                    'window' : bpy.context.window,
                    'active_object' : bpy.context.object,
            }
            bpy.ops.gpencil.data_add(override)

        gp = S.grease_pencil

        if gp.palettes:
            gpp = gp.palettes[0]
        else:
            gpp = gp.palettes.new("test", set_active = True)

        gpc = gpp.colors.new()
        gpc.name = "black"

        if gp.layers:
            gpl = gp.layers[0]
        else:
            gpl = gp.layers.new('gpl' + str(self.uuid), set_active = True)

        if gpl.frames:
            fr = gpl.active_frame if gpl.active_frame else gpl.frames[0]
        else:
            fr = gpl.frames.new(1)

        return fr


class Tag(Renderable):
    def __init__(self):
        super(Tag, self).__init__()


class Dots(Renderable):
    def __init__(self, options, points):
        super(Dots, self).__init__()
        self.opts = options
        self.points = deepcopy(points)

    def __repr__(self):
        return "Dots(" + repr(self.points) + ")"

    def flatten(self, transform):
        points = [p for p in self.points]
        return Dots(self.opts, points)

    def render_to_blender(self, context):
        fr = self._get_gpencil_frame()
        for p in self.points:
            str = fr.strokes.new()
            str.draw_mode = "3DSPACE"

            str.points.add(count = 1)
            str.points[0].co = tuple(p)


class Line(Renderable):
    def __init__(self, options, points):
        super(Line, self).__init__()
        self.opts = options
        self.points = deepcopy(points)

    def __repr__(self):
        return "Line(" + repr(self.points) + ")"

    def flatten(self, transform):
        # TODO(david): filter line options properly
        points = [p for p in self.points]
        return Line(self.opts, points)

    def render_to_blender(self, context):
        fr = self._get_gpencil_frame()
        str = fr.strokes.new("black")
        str.line_width = 3
        str.draw_mode = "3DSPACE"

        str.points.add(count = len(self.points))
        for i, p in enumerate(self.points):
            str.points[i].co = tuple(p)


class Curve(Renderable):
    def __init__(self, options, points):
        super(Curve, self).__init__()
        self.opts = options
        self.points = deepcopy(points)

    def __repr__(self):
        return "Curve(" + repr(self.points) + ")"

    def flatten(self, transform):
        points = [p for p in self.points]
        return Curve(self.opts, points)

    def render_to_blender(self, context):
        fr = self._get_gpencil_frame()
        str = fr.strokes.new()
        str.line_width = 3
        str.draw_mode = "3DSPACE"

        hermite_points = self.hermite_points()
        str.points.add(count = len(hermite_points))
        for i, p in enumerate(hermite_points):
            str.points[i].co = tuple(p)

    def hermite_points(self):
        # extend the points to create full points
        pts = [self.points[0]] + self.points + [self.points[-1]]
        if len(pts) < 4:
            return []

        result = []
        # do this for all consecutive 4
        for i in range(len(pts) - 3):
            xs, ys, zs = zip(*pts[i:i+4])
            # calculate and zip the points to interpolate
            # TODO(david): pick denominator based on distance
            result += list(zip([hermite_interp(xs, mu/10.0) for mu in range(0, 11)],
                               [hermite_interp(ys, mu/10.0) for mu in range(0, 11)],
                               [hermite_interp(zs, mu/10.0) for mu in range(0, 11)]))
        return result


class Polygon(Renderable):
    def __init__(self, options, points):
        super(Polygon, self).__init__()
        self.opts = options
        self.points = deepcopy(points)

    def __repr__(self):
        return "Polygon(" + repr(self.points) + ")"

    def render_to_blender(self, context):
        # create the correct vertices and face
        verts = tuple(tuple(p) for p in self.points)
        faces = (tuple(i for i in range(len(self.points))),)

        # mesh and object created separately
        me = bpy.data.meshes.new("polygon" + str(self.uuid) + "mesh")
        ob = bpy.data.objects.new("polygon" + str(self.uuid), me)
        # TODO(david): see if this has to be changed, depending on the
        # coordinates of the mesh itself?
        ob.location = (0, 0, 0)
        # debugging use mainly
        ob.show_name = True

        bpy.context.scene.objects.link(ob)

        # add the actual data to the mesh, and generate edges
        me.from_pydata(verts, [], faces)
        me.update(calc_edges = True)

        # all generated objects should be selected when done
        ob.select = True


class Sweep(Renderable):
    def __init__(self, options, slices, closed, transforms, swept):
        super(Sweep, self).__init__()
        self.opts = options
        self.slices = int(slices)
        self.closed = closed
        self.transforms = transforms
        self.swept = deepcopy(swept)

    def __repr__(self):
        return "Sweep(" + repr(self.slices) + ", " + repr(self.closed) + ", " + repr(self.swept) + ")"

    def flatten(self, transform):
        def best_split(v0, v1, v2, v3):
            d0 = v2 - v0
            d1 = v3 - v1
            n = d0.cross(d1)

            if n.length < 0.001:
                return -1

            def length_sqr(v):
                return v.length_squared
            e_max = max([v1 - v0, v2 - v1, v3 - v2], key=length_sqr)
            warp = e_max.dot(n)

            if abs(warp) < 1e-5:
                return -1
            elif d0.length_squared < d1.length_squared:
                return 0
            else:
                return 1

        def make_face(opts, transform, v0, v1, v2, v3, split):
            result = []
            
            sp = best_split(v0, v1, v2, v3)
            if split or sp == -1:
                result.append(Polygon(opts, []))
                result[-1].points.append(transform * v0)
                result[-1].points.append(transform * v1)
                result[-1].points.append(transform * v2)
                result[-1].points.append(transform * v3)
            elif sp == 0:
                result.append(Polygon(opts, []))
                result[-1].points.append(transform * v0)
                result[-1].points.append(transform * v1)
                result[-1].points.append(transform * v2)
                result.append(Polygon(opts, []))
                result[-1].points.append(transform * v2)
                result[-1].points.append(transform * v3)
                result[-1].points.append(transform * v0)
            else:
                result.append(Polygon(opts, []))
                result[-1].points.append(transform * v1)
                result[-1].points.append(transform * v2)
                result[-1].points.append(transform * v3)
                result.append(Polygon(opts, []))
                result[-1].points.append(transform * v3)
                result[-1].points.append(transform * v0)
                result[-1].points.append(transform * v1)

            return result

        pts_1 = []
        pts_2 = []
        output = []

        if self.opts:
            split = self.opts.get("split", True)
        else:
            split = True

        if type(self.swept) == Point:
            accum = [Transform.Identity(4) for i in self.transforms]
            if self.closed:
                polygon = Polygon(self.opts, [])
                for i in range(self.slices):
                    sweep_xf = Transform.Identity(4)
                    for xf in accum:
                        sweep_xf = xf * sweep_xf
                    sweep_xf = transform * sweep_xf
                    polygon.points.append(sweep_xf * self.swept)
                    for j in range(len(accum)):
                        accum[j] = accum[j] * self.transforms[j]
                output.append(polygon)
            else:
                line = Line(self.opts, [])
                for i in range(self.slices):
                    sweep_xf = Transform.Identity(4)
                    for xf in accum:
                        sweep_xf = xf * sweep_xf
                    sweep_xf = transform * sweep_xf
                    line.points.append(sweep_xf * self.swept)
                    for j in range(len(accum)):
                        accum[j] = accum[j] * self.transforms[j]
                output.append(line)
        else:
            swept_list = self.swept if type(self.swept) == list else [self.swept]
            for swept in swept_list:
                # have to flatten all drawable objects
                swept = swept.flatten(Transform.Identity(4))
                accum = [Transform.Identity(4) for i in self.transforms]

                # specific for each individual swept
                if type(swept) == Line:
                    a = pts_1
                    b = pts_2
                    a = swept.points[:]

                    # make faces for each pair of created lines
                    # if this is closed, then create polygons to seal the "tube"
                    # that gets created ultimately
                    if self.closed:
                        e1 = Polygon(self.opts, [])
                        e2 = Polygon(self.opts, [])
                        face_opts = swept.opts if swept.opts else self.opts

                        for i in range(self.slices - 1):
                            for j in range(len(accum)):
                                accum[j] = accum[j] * self.transforms[j]
                            sweep_xf = transform.Identity(4)
                            for xf in accum:
                                sweep_xf = xf * sweep_xf
                            b = [sweep_xf * p for p in swept.points]
                            e1.points.append(transform * b[-1])
                            e2.points = [transform * b[0]] + e2.points
                            for j in range(len(a) - 1):
                                output += make_face(self.opts,
                                                    transform,
                                                    b[j], b[j + 1],
                                                    a[j + 1], a[j],
                                                    split)
                            a, b = b, a

                        e1.points.append(transform * swept.points[-1])
                        e2.points = [transform * swept.points[0]] + e2.points
                        for j in range(len(a) - 1):
                            output += make_face(face_opts,
                                                transform,
                                                swept.points[j], swept.points[j + 1],
                                                a[j + 1], a[j],
                                                split)
                        output.append(e1)
                        output.append(e2)
                    else:
                        for i in range(self.slices):
                            for j in range(len(accum)):
                                accum[j] = accum[j] * self.transforms[j]
                            sweep_xf = transform.Identity(4)
                            for xf in accum:
                                sweep_xf = xf * sweep_xf
                            b = [sweep_xf * p for p in swept.points]
                            for j in range(len(a) - 1):
                                output += make_face(self.opts,
                                                    Transform.Identity(4), #transform,
                                                    b[j], b[j + 1],
                                                    a[j + 1], a[j],
                                                    split)
                            a, b = b, a
                elif type(swept) == Polygon:
                    end_opts = swept.opts if swept.opts else self.opts
                    # if self.closed: warn about ignored
                    a = swept.points[:]
                    output.append(Polygon(end_opts, []))
                    output[-1].points = [transform * i for i in a]
                    for i in range(self.slices):
                        for j in range(len(accum)):
                            accum[j] = accum[j] * self.transforms[j]
                        sweep_xf = transform.Identity(4)
                        for xf in accum:
                            sweep_xf = xf * sweep_xf
                        b = [sweep_xf * p for p in swept.points]
                        for j in range(len(a) - 1):
                            output += make_face(self.opts,
                                                Transform.Identity(4), #transform,
                                                b[j], b[j + 1],
                                                a[j + 1], a[j],
                                                split)
                        a, b = b, a
                    output.append(Polygon(end_opts, []))
                    output[-1].points = [transform * i for i in a.__reversed__()]

        return Compound(Transform.Identity(4), output)


class Repeat(Renderable):
    def __init__(self, count, transforms, repeated):
        super(Repeat, self).__init__()
        self.n = count
        self.transforms = transforms
        self.repeated = deepcopy(repeated)

    def __repr__(self):
        return "Repeat(" + repr(self.repeated) + ", " + repr(self.n) + ")"

    def flatten(self, transform):
        if self.n <= 0:
            return None
        flat_repeated = self.repeated.flatten(Transform.Identity(4))
        accum = deepcopy(self.transforms)
        output = []
        for i in range(self.n):
            child_xf = transform.Identity(4)
            for xf in accum:
                child_xf = xf * child_xf
            output = child.flatten(child_xf) + output
            for j in range(len(accum)):
                accum[j] = accum[j] * self.transforms[j]


class Compound(Renderable):
    def __init__(self, transform, child):
        super(Compound, self).__init__()
        self.transform = transform
        self.child = deepcopy(child) if type(child) == list else [deepcopy(child)]

    def __repr__(self):
        return "Compound(" + repr(self.child) + ")"

    def flatten(self, transform):
        transform *= self.transform
        # TODO(david): should flatten return the flattened object?
        #              just in case that this requies a different return
        children = [c.flatten(transform) for c in self.child]
        return Compound(Transform.Identity(4), children)

    def render_to_blender(self, context):
        for c in self.child:
            c.render_to_blender(context)


class Special(Renderable):
    # TODO(david): don't need this, really
    def __init__(self, code, args, line):
        super(Special, self).__init__()
        self.code = code
        self.args = args
        self.line = line


if __name__=="__main__":
    o = Compount(Transform.Identity(4), Line(None, [Point(1, 2, 3)]))
    o.flatten(Transform.Identity(4))
    o.render_to_blender(None)

