import bpy
import mathutils
from mathutils import Vector
from math import sin, cos
from math import pi as PI

from .notnum import poly1d, linspace
from .util import clip

# cubic hermite basis functions
H30 = poly1d([ 2, -3, 0, 1])
H31 = poly1d([ 1, -2, 1, 0])
H32 = poly1d([ 1, -1, 0, 0])
H33 = poly1d([-2,  3, 0, 0])

class HermiteInterpolator:
    
    def __init__(self, x, y, dy):
        if len(x) != len(y) or len(y) != len(dy):
            raise ValueError
        self.x = x
        self.y = y
        self.dy = dy
    
    def __call__(self, xval, nu=0):
        i, t = self._locate(xval)
        tangentScale = self.x[i+1]-self.x[i] # necessary, as we do not generally interpolate over unit intervals
        return ( float(H30.deriv(nu)(t)) * self.y [i] +
                 float(H31.deriv(nu)(t)) * tangentScale * self.dy[i] +
                 float(H32.deriv(nu)(t)) * tangentScale * self.dy[i+1] +
                 float(H33.deriv(nu)(t)) * self.y [i+1] )
    
    def _locate(self, xval):
        """ find index and normalised parameter t for the given x. clamps to the range of x. """
        for i, xi in enumerate(self.x, -1):
            if xval < xi:
                if i == -1:
                    return 0, 0
                return i, (xval-self.x[i])/(xi-self.x[i])
        return len(self.x)-2, 1
    
    def samples(self, count=2, nu=0):
        """
        returns an array of count samples along the spline.
        count must be at least 2.
        """
        count = int(count)
        assert count >= 2
        xmin, xmax = min(self.x), max(self.x)
        return [self( x, nu ) for x in linspace(xmin, xmax, count)]
    
    def sampleStep(self, spacing=.1, nu=0):
        """
        returns an array of samples along the spline.
        the samples are roughly spacing apart in parameter space.
        at least two samples are returned.
        """
        xmin, xmax = min(self.x), max(self.x)
        return [self( x, nu ) for x in linspace(xmin, xmax, max(int((xmax-xmin)/spacing), 2))]

#############################################

class Bezier:
    
    def __init__(self, points):
        self.points = points
    
    def __call__(self, t, nu = 0):
        t = clip(t, 0, 1)
        
        def casteljau(points):
            if len(points) == 1:
                return points[0]
            return casteljau( [ points[i+1]*t + points[i]*(1-t) for i in range(len(points)-1) ] )
        
        return casteljau(self.derive(nu).points)
    
    def derive(self, nu):
        if nu <= 0:
            return self
        order = len(self.points)
        return Bezier([ order* (self.points[i+1]-self.points[i]) for i in range(order-1) ]).derive(nu-1)
    
    def samples(self, count=2, nu=0):
        """
        returns an array of count samples along the spline.
        count must be at least 2.
        """
        count = int(count)
        assert count >= 2
        deriv = self.derive(nu)
        return [deriv(t) for t in linspace(0, 1, count)]

#############################################

def bevelCircle(spline, radius, LODp=8, LODl=10):
    """
    Bevel a circle along a spline.
    The radius can be a number or a 1D spline.
    If it is a spline, its parameter range will be stretched/compressed to that of the main curve.
    LODp: number of points to use for each circle
    LODl: number of samples along the curve
    """
    from numbers import Real
    if isinstance(radius, Real):
        radius = Bezier([radius, radius])
    vertices = []
    faces = []
    
    i1 = None
    s_pre = None
    for s, r, dsdx, dsdx2 in zip(spline.samples(LODl), radius.samples(LODl), spline.samples(LODl, nu=1), spline.samples(LODl, nu=2)):
        i2 = len(vertices)
        
        # a local, Frenet-like frame
        T, A = dsdx.to_3d(), dsdx2.to_3d()
        N = T.cross(A).cross(T).normalized() if A.length > 0.0001 else T.orthogonal().normalized() # fallback, as with vanishing curvature the frame fails
        B = T.cross(N).normalized()
        # ... is used to add points in a circle
        vertices.extend( s.to_3d()+ (sin(phi)*N+cos(phi)*B)*r for phi in linspace(0, 2*PI, LODp, endpoint=False) )
        
        if i1 != None: # nothing to connect for first points
            # sometimes the frame can twist, so we look for the smoothest connection
            # by minimizing the angle between the side edges and the center line
            tmp = [(vertices[i2+o]-vertices[i1]).angle((s-s_pre).xyz)  for o in range(LODp)]
            offset = tmp.index(min(tmp)) # argmin
            
            for f in range(LODp):
                faces.append((i1 + (f+1)%LODp, i1 + f, i2 + (f+offset)%LODp, i2 + (f+offset+1)%LODp))
        i1 = i2
        s_pre = s
    return vertices, faces

#############################################

def screw(spline, LODr, LODp, normalsDown=False, rScale=None):
    """
    Creates a surface by rotating a spline around the z axis.
    The vertices and face indices are returned.
    LODr: number of samples along the spline, i.e. 'rings'
    LODp: number of 'spokes'
    normalsDown: flag indicating, where normals should point (assumes the spline goes outward)
    rScale: optional spline over [0,2*PI], giving a radial scale to apply at every angle
    """
    verts = []
    faces = []
    order = -1 if normalsDown else 1
    
    i1 = len(verts) + (LODp-1)*LODr # connect last and first line
    for angle in linspace(0, 2*PI, LODp, endpoint=False):
        i2 = len(verts)
        verts.extend(spline.samples(LODr))
        for v in range(i2, i2+LODr):
            verts[v].rotate(mathutils.Euler(Vector((0, 0, angle))))
            if rScale is not None:
                verts[v].xy *= rScale(angle) #*(v-i2)/LODr
        faces.extend( (i1+f, i1+f+1, i2+f+1, i2+f)[::order] for f in range(LODr-1) )
        i1 = i2
    return verts, faces

#############################################

def asEdgeObject(*splines, LOD=10, name="Spline"):
    """Samples the given splines to create blender mesh object of the resultant edges."""
    from numbers import Number
    vertices = []
    edges = []
    
    for spline in splines:
        idx = len(vertices)
        vertices.extend( map(Vector.to_3d, map(lambda x: Vector([x[0]/(LOD-1), 0, x[1]]) if isinstance(x[1], Number) else x[1], enumerate(spline.samples(LOD))) ) )
        edges.extend( zip(range(idx, len(vertices)-1), range(idx+1, len(vertices))) )
    
    newMesh = bpy.data.meshes.new(name)
    newMesh.from_pydata(vertices, edges, [])
    newMesh.update()
    return bpy.data.objects.new(name, newMesh)
