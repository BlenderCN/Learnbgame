import bpy
import mathutils
from mathutils import Vector
from math import sin, cos
from math import pi as PI

from .notnum import poly1d, linspace
from .util import clip


class Spline1DBase:
    """Base class for 1D splines."""
    
    def __init__(self, pmin, pmax):
        """Set min and max value of the spline's parameter range."""
        assert pmin < pmax
        self.pmin = pmin
        self.pmax = pmax
    
    @property
    def prange(self):
        """Parameter range on which the spline is defined. Outside of this range, evaluating the spline leads to undefined behaviour."""
        return self.pmin, self.pmax
    
    def __call__(self, t):
        """
        Evaluate the spline at parameter value t. Must be implemented in sub-classes.
        Behaviour outside the parameter range may be undefined.
        """
        raise NotImplementedError(self.__class__, "can not be evaluated, as it does not implement method '__call__'")
    
    def samples(self, count=2):
        """
        Returns an array of count samples along the spline.
        Count must be at least 2.
        """
        count = int(count)
        assert count >= 2
        return [ self(x) for x in linspace(self.pmin, self.pmax, count) ]
    
    def sampleStep(self, spacing=.1):
        """
        Returns an array of samples along the spline.
        The samples are roughly spacing apart in parameter space.
        At least two samples are returned.
        """
        return [ self(x) for x in linspace(self.pmin, self.pmax, max(int((self.pmax-self.pmin)/spacing), 2)) ]
    
    def derive(self, nu):
        """
        Return a spline corresponding to the nu-th derivative. Does not change self.
        Nu is expected to be non-negative. For 'nu==0' self may be returned.
        At least first and second derivative ought to be implemented by sub-classes.
        """
        raise NotImplementedError(self.__class__, "does not implement method 'derive'")
    
    def __add__(self, other):
        return SplineSum(self, other)
    
    def __mul__(self, other):
        return SplineProduct(self, other)
    
    def reparam(self, pmin, pmax):
        return SplineReparam(self, pmin, pmax)

#############################################

class SplineSum(Spline1DBase):
    """Class encapsulating the sum of two splines"""
    
    def __init__(self, s1, s2):
        super().__init__(min(s1.pmin, s2.pmin), max(s1.pmax, s2.pmax))
        self._s1 = s1
        self._s2 = s2
    
    def __call__(self, t):
        return self._s1(t) + self._s2(t)
    
    def derive(self, nu):
        return self._s1.derive(nu) + self._s2.derive(nu)

class SplineProduct(Spline1DBase):
    """Class encapsulating the product of two splines"""
    
    def __init__(self, s1, s2):
        super().__init__(min(s1.pmin, s2.pmin), max(s1.pmax, s2.pmax))
        self._s1 = s1
        self._s2 = s2
    
    def __call__(self, t):
        return self._s1(t) * self._s2(t)
    
    def derive(self, nu):
        if nu <= 0:
            return self
        return ( (self._s1.derive(1) * self._s2) + (self._s1 * self._s2.derive(1)) ).derive(nu-1)

class SplineReparam(Spline1DBase):
    """Wrapper-class to assign a spline to a new parammeter range"""
    
    def __init__(self, base, pmin, pmax):
        "asdasa"
        super().__init__(pmin, pmax)
        self.base = base
    
    def __call__(self, t):
        tbase = (self.base.pmax - self.base.pmin) * (t - self.pmin) / (self.pmax - self.pmin) + self.base.pmin
        return self.base(tbase)
    
    def derive(self, nu):
        # FIXME should get a factor of '(self.base.pmax - self.base.pmin) / (self.pmax - self.pmin)' for each derivation
        #  but scale is not that important for now
        return SplineReparam(self.base.derive(nu), self.pmin, self.pmax)

#############################################

# cubic hermite basis functions
H30 = poly1d([ 2, -3, 0, 1])
H31 = poly1d([ 1, -2, 1, 0])
H32 = poly1d([ 1, -1, 0, 0])
H33 = poly1d([-2,  3, 0, 0])

class HermiteInterpolator(Spline1DBase):
    
    def __init__(self, x, y, dy, nu=0):
        if len(x) != len(y) or len(y) != len(dy):
            raise ValueError
        super().__init__(min(x), max(x))
        self.x = x
        self.y = y
        self.dy = dy
        self.nu = nu
    
    def _locate(self, xval):
        """ find index and normalised parameter t for the given x. clamps to the range of x. """
        for i, xi in enumerate(self.x, -1):
            if xval < xi:
                if i == -1:
                    return 0, 0
                return i, (xval-self.x[i])/(xi-self.x[i])
        return len(self.x)-2, 1
    
    def __call__(self, xval):
        i, t = self._locate(xval)
        tangentScale = self.x[i+1]-self.x[i] # necessary, as we do not generally interpolate over unit intervals
        return ( float(H30.deriv(self.nu)(t)) * self.y [i] +
                 float(H31.deriv(self.nu)(t)) * tangentScale * self.dy[i] +
                 float(H32.deriv(self.nu)(t)) * tangentScale * self.dy[i+1] +
                 float(H33.deriv(self.nu)(t)) * self.y [i+1] )
    
    def derive(self, nu):
        return HermiteInterpolator(self.x, self.y, self.dy, self.nu+nu)

#############################################

class FunctionSpline(Spline1DBase):
    
    def __init__(self, function, pmin, pmax, *derivatives, derivator=None):
        """
        function: evaluation rule for the spline
        pmin, pmax: parameter range of the spline
        derivatives: the derivatives of the function in order (i.e. 1st deriv., 2nd deriv., ...)
        derivator: alternatively to passing the derivatives, a function for derivation may be passed
            given a single parameter nu it should return the nu-th derivative of the spline function
        """
        super().__init__(pmin, pmax)
        self.function = function
        if derivator is None:
            def deriv(nu):
                if nu <= 0:
                    return self.function
                if nu <= len(derivatives):
                    return derivatives[nu-1]
                raise Exception(str(nu)+"th derivative was not defined")
            derivator = deriv
        else:
            assert len(derivatives) == 0, "Do not pass explicit derivatives if you specify a derivator"
        self.derivator = derivator
    
    def __call__(self, t):
        return self.function(t)
    
    def derive(self, nu):
        return FunctionSpline(self.derivator(nu), self.pmin, self.pmax, derivator = lambda nu2: self.derivator(nu+nu2))

#############################################

class Bezier(Spline1DBase):
    
    def __init__(self, points):
        super().__init__(0, 1)
        assert points, "no control points defined"
        self.points = points
    
    def __call__(self, t):
        t = clip(t, 0, 1)
        
        def casteljau(points):
            if len(points) == 1:
                return points[0]
            return casteljau( [ points[i+1]*t + points[i]*(1-t) for i in range(len(points)-1) ] )
        
        return casteljau(self.points)
    
    def derive(self, nu):
        if nu <= 0:
            return self
        order = len(self.points)
        if order <= nu:
            return Bezier( [ 0*self.points[0] ] )
        return Bezier([ order* (self.points[i+1]-self.points[i]) for i in range(order-1) ]).derive(nu-1)

#############################################

def bevelCircle(spline, radius, LODp=8, LODl=10, closeEnds=False):
    """
    Bevel a circle along a spline.
    The radius can be a number or a 1D spline.
    If it is a spline, its parameter range will be stretched/compressed to that of the main curve.
    LODp: number of points to use for each circle
    LODl: number of samples along the curve
    closeEnds: whether to close the ends with a disk
    """
    from numbers import Real
    if isinstance(radius, Real):
        radius = Bezier([radius, radius])
    vertices = []
    faces = []
    
    i1 = None
    s_pre = None
    for s, r, dsdx, dsdx2 in zip(spline.samples(LODl), radius.samples(LODl), spline.derive(1).samples(LODl), spline.derive(2).samples(LODl)):
        i2 = len(vertices)
        
        # a local, Frenet-like frame
        T, A = dsdx.to_3d(), dsdx2.to_3d()
        if abs(T.angle(A, 0)%PI) > 0.0001: # A musn't be zero or parallel to T
            N = T.cross(A).cross(T).normalized()
        else: # fallback, as with vanishing curvature the frame fails
            N = T.orthogonal().normalized()
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
    
    if closeEnds:
        vertices.extend(spline.samples(2)) # first and last point of the spline
        faces.extend( (fi, (fi+1)%LODp, len(vertices)-2) for fi in range(LODp) )
        fiBase = len(vertices)-LODp-2 # idx start for end vertices
        faces.extend( (fiBase+(fi+1)%LODp, fiBase+fi, len(vertices)-1) for fi in range(LODp) )
    
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

def curvedScrew(outline, spine, LODr, LODp, normalsDown=False, rScale=None):
    """
    Like screw(), creates a surface by rotating a spline around the z axis.
    In addition, the surface is then bent along the spine.
    The z values of the outline are mapped to the parameter space of the spine.
    The vertices and face indices are returned.
    outline, spine: 3d splines describing the desired surface
    LODr: number of samples along the spline, i.e. 'rings'
    LODp: number of 'spokes'
    normalsDown: flag indicating, where normals should point (assumes the spline goes outward)
    rScale: optional spline over [0,2*PI], giving a radial scale to apply at every angle
    """
    verts = []
    faces = []
    order = -1 if normalsDown else 1
    if rScale is None:
        rScale = lambda _: 1
    
    samples = outline.samples(LODr)
    zSamples = [v.z for v in samples]
    zSamplesSortedIds = [i[0] for i in sorted(enumerate(zSamples), key=lambda x:x[1])] # argsort

    spine = spine.reparam(min(zSamples), max(zSamples))
    
    # local base at the start of the spline
    spineDx = spine.derive(1)
    baseZ = spineDx(spine.pmin)
    baseX = baseZ.orthogonal().normalized()
    #TODO could scale radius according to changed length; i.e. length(spine)/(zmax-zmin)
    base = [ baseZ, baseX, baseZ.cross(baseX).normalized() ]

    # the bases at each point are determined by iteratively moving a base along the sampled positions
    bases = [None]*len(samples)
    for zIdx in zSamplesSortedIds:
        dsdx = spineDx(zSamples[zIdx])
        rotation = base[0].rotation_difference(dsdx)
        base[0] = dsdx
        base[1].rotate(rotation)
        base[2].rotate(rotation)
        bases[zIdx] = [ v.copy() for v in base ]
    
    i1 = len(verts) + (LODp-1)*LODr # connect last and first line
    for angle in linspace(0, 2*PI, LODp, endpoint=False):
        i2 = len(verts)
        for i, surfPoint in enumerate(samples):
            spinePoint = spine(surfPoint.z)
            # use local x and y axis to reconstruct point
            verts.append( rScale(angle) * ( surfPoint.x*bases[i][1] + surfPoint.y*bases[i][2] ) )
            verts[-1].rotate( mathutils.Quaternion(bases[i][0], angle) ) # rotate around local z axis
            verts[-1] += spinePoint # move to correct position
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
