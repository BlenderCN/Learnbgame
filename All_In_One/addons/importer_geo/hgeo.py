'''
    Module to interpret the schema of Houdini's JSON geometry format.
'''

import os, sys, time
import numpy
import functools

VERBOSE = False
_START = time.time()
_LAP = _START

_VERSION = '12.0.0'

def _Assert(condition, message):
    ''' Print out verbose information about processing '''
    if not condition:
        print(message)
        sys.exit(1)

def _Verbose(msg):
    ''' Print out verbose information about processing '''
    if VERBOSE:
        global _LAP
        now = time.time()
        sys.stdout.write('+++ %6.3f (%6.3f): %s\n' % (now-_START, now-_LAP, msg))
        _LAP = now
        sys.stdout.flush()

try:
    import hjson
except:
    # If there's an issue loading hjson, fall back to simplejson.  This doesn't
    # support binary JSON but works for ASCII files.
    _Verbose('Falling back to simplejson')
    import json
    hjson = json


def listToDict(l):
    # Since JSON doesn't enforce order for dictionary objects, the geometry
    # schema often stores dictionaries as lists of name/value pairs.  This
    # function will throw the list into a dictionary for easier access.
    if l and type(l) == list:
        d = {}
        for i in range(0, len(l), 2):
            d[l[i]] = l[i+1]
        return d
    return l

def _rawPageDataToTupleArray(raw, packing, pagesize, constflags, total_tuples):
    ''' Marshall raw page data into an array of tuples '''
    # Raw page data is stored interleaved as:
    # [ <subvector0_page0> <subvector1_page0> <subvector2_page0>
    #   <subvector0_page1> <subvector1_page1> <subvector2_page1>
    #   <subvector0_page2> <subvector1_page2> <subvector2_page2>
    #  ...
    #   <subvector0_pageN> <subvector1_pageN> <subvector2_pageN>]
    #
    # <subvectorI_PageJ> will be a single subvector value if constflags[i][j]
    # is True.
    import operator
    tuple_size = sum(packing)
    n_pages = 0
    # We can extract the number of pages from the length of a constant flag
    # table if any subvectors have one.
    if constflags is not None:
        n_pages = functools.reduce(lambda x,y: x if x > 0 else len(y), constflags, 0)
    # Failing that, we know that raw contains no constant pages, and so we
    # can compute the number of pages directly from the length of raw.
    if n_pages == 0:
        full_pagesize = tuple_size * pagesize
        n_pages = (len(raw) + full_pagesize - 1) // full_pagesize

    # Build list of the subvector index and offset into that subvector for
    # each tuple component.
    tuple_pack_info = []
    for i in range(0, len(packing)):
        tuple_pack_info.extend([(i, j) for j in range(0, packing[i])])

    # Precompute the increments for pages where all subvectors are varying
    # as these don't change.
    varying_steps = [1] * len(packing)
    varying_steps = map(operator.mul, packing, varying_steps)

    result = []
    raw_index = 0
    raw_left = len(raw)
    # Iterate over the input pages
    for i in range(0, n_pages):
        # Compute the packed vector steps, i.e., the step to take in raw to
        # move to the start of the next packed subvector.  This will be 0
        # for constant pages.
        if constflags is not None:
            pv_steps = [0 if (len(x) > 0 and x[i]) else 1 for x in constflags]
            pv_steps = map(operator.mul, packing, pv_steps)
        else:
            pv_steps = varying_steps
        # Compute the number of varying components on this page using the
        # already computed vec_increments.
        n_varying = sum(pv_steps)
        # Use the number of varying components and the amount of data left
        # to compute the number of tuples this page represents.  When the
        # last page is constant for all the subvectors, i.e., there are no
        # varying components, we load a single tuple in this iteration and
        # later duplicate it to create the remaining tuples.
        if n_varying > 0:
            n_tuples = min(pagesize, (raw_left - (tuple_size - n_varying)) // n_varying)
        else:
            _Assert( raw_left >= tuple_size, "Expected more data" )
            n_tuples = pagesize if raw_left > tuple_size else 1

        # Compute the list of offsets into raw for the start of each packed
        # subvector.
        curr_offset = raw_index
        pv_offsets = []
        for i, step in enumerate(pv_steps):
            pv_offsets.append(curr_offset)
            curr_offset += max(step * n_tuples, packing[i])
            
        # Finally, extract each tuple on the page from the raw list.
        if tuple_size > 1:
            for j in range(0, n_tuples):
                result.append([raw[pv_offsets[x]+y] for x,y in tuple_pack_info])
                pv_offsets = map(operator.add, pv_offsets, pv_steps)
        else:
            for j in range(0, n_tuples):
                result.append(raw[pv_offsets[0]])
                pv_offsets = map(operator.add, pv_offsets, pv_steps)

        consumed = n_varying * n_tuples + (tuple_size - n_varying)
        raw_index += consumed
        raw_left -= consumed
        _Assert( raw_index == curr_offset, "Indexing bug" )

    # The loop above marshalls all the available data in raw into our result,
    # but without explicitly using the total_tuples argument, we had no way
    # of computing the size of the last page if it was constant for all the
    # subvectors.  In such a case, we treated it as if it contained a single
    # tuple, and so we now add any missing tuples.
    if constflags is not None and result:
        copy_source = result[-1]
        if tuple_size > 1:
            for i in range(len(result), total_tuples):
                result.append(list(copy_source))
        else:
            for i in range(len(result), total_tuples):
                result.append(copy_source)
            
    _Assert( len(result) == total_tuples, "Expected more data" )
    return result

class Basis:
    ''' Simple basis definition '''
    def __init__(self, btype='NURBS', order=2,
                    endinterpolation=True, knots=[0,0,1,1]):
        self.Type = btype
        self.Order = order
        self.EndInterpolation = endinterpolation
        self.Knots = knots

    def load(self, bdata):
        bdata = listToDict(bdata)
        self.Type = bdata.get('type', self.Type)
        self.Order = bdata.get('order', self.Order)
        self.EndInterpolation = bdata.get('endinterpolation', self.EndInterpolation)
        self.Knots = bdata.get('knots', self.Knots)

    def save(self):
        return [
            "type", self.Type,
            "order", self.Order,
            "endinterpolation", self.EndInterpolation,
            "knots", self.Knots
        ]

class TrimRegion:
    ''' Class to define a trim region of a profile curve '''
    def __init__(self):
        ''' Create an empty trim region '''
        self.OpenCasual = False
        self.Faces = []

    def load(self, tdata):
        ''' Interpret the JSON schema to create a list of faces (with extents)
            which define a single trim region '''
        tdata = listToDict(tdata)
        self.OpenCasual = tdata["opencasual"]
        self.Faces = []
        for face in tdata["faces"]:
            fdata = listToDict(face)
            self.Faces.append({
                "face":fdata['face'],
                "u0"  :fdata['u0'],
                "u1"  :fdata['u1'],})

    def save(self):
        ''' Create an object reflecting the JSON schema for the trim region '''
        data = [ "opencasual", self.OpenCasual ]
        fdata = []
        for f in self.Faces:
            fdata.append([ "face", f["face"],
                            "u0", f["u0"],
                            "u1", f["u1"] ])
        data += [ "faces", fdata ]
        return data

class Attribute:
    '''
        An attribute may be bound to point, primitive, vertex or detail
        elements.  The attribute stores an array of values, one for each
        element in the detail.
    '''
    def __init__(self, name, attrib_type, attrib_scope):
        ''' Initialize an attribute of the given name, type and scope '''
        # Data defined in definition block
        self.Name = name
        self.Type = attrib_type
        self.Scope = attrib_scope
        self.Options = {}
        # Data defined in per-attribute value block
        self.TupleSize = 1
        self.Array = []
        self.Defaults = None
        self.Strings = None

    def loadDefaults(self, obj):
        ''' Load defaults from the JSON schema '''
        obj = listToDict(obj)
        self.Defaults = None
        if obj:
            self.Defaults = obj.get('values', None)

    def getValue(self, offset):
        ''' Implemented for numeric/string attributes.
            Return's the value for the element offset '''
        if self.Type == "numeric":
            return self.Array[offset]
        elif self.Type == "string":
            str_idx = self.Array[offset]
            if str_idx < 0 or str_idx >= len(self.Strings):
                return ''
            return self.Strings[str_idx]
        return None

    def loadValues(self, obj, element_count):
        ''' Interpret the JSON schema to load numeric/string attributes '''
        obj = listToDict(obj)
        self.loadDefaults(obj.get('defaults', None))
        if self.Type == 'numeric':
            values = listToDict(obj['values'])
            self.TupleSize = values.get('size', 1)
            self.Array = values.get('tuples', None)
            self.Storage = values.get('storage', 'fpreal32')
            if not self.Array:
                pagedata = values.get('rawpagedata', None)
                if pagedata is not None:
                    packing = values.get('packing', [self.TupleSize])
                    pagesize = values.get('pagesize', -1)
                    _Assert(pagesize >= 0, "Expected pagesize field")
                    constflags = values.get('constantpageflags', None)
                    self.Array = _rawPageDataToTupleArray(
                                                raw=pagedata,
                                                packing=packing,
                                                pagesize=pagesize,
                                                constflags=constflags,
                                                total_tuples=element_count)
            if not self.Array:
                self.Array = values.get('arrays', None)
                _Assert(self.Array and self.TupleSize == 1,
                        "Expected a single value")
                # Stored as a tuple of arrays rather than an array of tuples,
                # so de-reference the index, giving the expected result.
                self.Array = self.Array[0]
        elif self.Type == 'string':
            self.Strings = obj['strings']
            indices = listToDict(obj['indices'])
            self.TupleSize = indices.get('size', 1)
            self.Array = indices.get('tuples', None)
            self.Storage = indices.get('storage', 'int32')
            if not self.Array:
                pagedata = indices.get('rawpagedata', None)
                if pagedata is not None:
                    packing = indices.get('packing', [self.TupleSize])
                    pagesize = indices.get('pagesize', -1)
                    _Assert(pagesize >= 0, "Expected pagesize field")
                    constflags = indices.get('constantpageflags', None)
                    self.Array = _rawPageDataToTupleArray(
                                                raw=pagedata,
                                                packing=packing,
                                                pagesize=pagesize,
                                                constflags=constflags,
                                                total_tuples=element_count)
            if not self.Array:
                self.Array = indices.get('arrays', None)
                _Assert(self.Array and self.TupleSize == 1,
                        "Expected a single value")
                self.Array = self.Array[0]
        else:
            # Unknown attribute type, so just store the entire attribute value
            # block
            print ('Unknown attribute type', self.Type)
            self.Array = obj

    def save(self):
        ''' Create the JSON schema from the attribute's data '''
        adef = [
            "scope", self.Scope,
            "type", self.Type,
            "name", self.Name,
            "options", self.Options
        ]
        avalue = [
            "size", self.TupleSize,
        ]
        if self.Defaults:
            avalue += [
                "defaults", [
                    "size", len(self.Defaults),
                    "storage", "fpreal64",
                    "values", self.Defaults
                ]
            ]
        if self.Strings:
            avalue += [ "strings", self.Strings ]

        kword = "tuples"
        a = self.Array
        if self.TupleSize == 1:
            kword = "arrays"    # Store tuple of arrays not an array of tuples
            a = [self.Array]
        if self.Type == 'numeric':
            avalue += [ 'storage', self.Storage ]
            avalue += [
                "values", [
                    "size", self.TupleSize,
                    "storage", self.Storage,
                    kword, self.Array
                ]
            ]
        elif self.Type == 'string':
            avalue += [
                "indices", [
                    "size", self.TupleSize,
                    "storage", "int32",
                    kword, self.Array ]
            ]
        else:
            avalue += self.Array
        return [ adef, avalue ]

def _unpackRLE(rle):
    ''' Unpack a run-length encoded array of bit data (used to save groups) '''
    a = []
    for run in range(0, len(rle), 2):
        count = rle[run]
        state = [False,True][rle[run+1]]
        a += [state] * count
    return a

class ElementGroup:
    ''' There are different group types in GA.  ElementGroup's are used for
        groups of primitive, vertex and point objects.  They may be ordered or
        unordered
    '''
    def __init__(self, name):
        ''' Create a new element group of the given name '''
        self.Name = name
        self.Selection = []
        self.Order = None
        self.Defaults = None
        self.Count = 0

    def updateMembership(self):
        ''' Count the number of elements in the group '''
        self.Count = self.Selection.sum()

    def loadUnordered(self, obj):
        ''' Load an unordered group.  There are currently two encodings to
        store the bit-array.  The runlengh encoding is an array of pairs
        [count, value, count, value], while the "i8" encoding stores as 8-bit
        integers (binary mode) '''
        self.Selection = numpy.array([], dtype=bool)
        obj = listToDict(obj)
        rle = obj.get('boolRLE', None)
        if rle:
            self.Selection = numpy.array(_unpackRLE(rle), dtype=bool)
            return
        i8 = obj.get('i8', None)
        if i8:
            self.Selection = numpy.array(i8, dtype=bool)
            return
        _Assert(False, 'Unknown element group encoding')

    def loadOrdered(self, obj, element_count):
        ''' Ordered groups are stored as a list of the elements in the group
        (in order) '''
        self.Order = obj
        self.Selection = numpy.resize(numpy.array([False], dtype=bool),
                                    element_count)
        for i in obj:
            self.Selection[i] = True

    def loadSelection(self, obj, element_count):
        ''' Interpret the schema, loading the group selection '''
        obj = listToDict(obj)
        sel = listToDict(obj['selection'])
        self.Defaults = sel['defaults']
        style = sel.get('unordered', None)
        if style:
            self.loadUnordered(style)
        else:
            self.loadOrdered(sel['ordered'], element_count)
        self.updateMembership()
    def save(self, gtype):
        ''' Create the JSON schema for the group (definition & values) '''
        gdef = [ "name", self.Name, "type", gtype ]
        if self.Order:
            selection = [
                "defaults", self.Defaults,
                "ordered", self.Order
            ]
        else:
            # JSON can't handle numpy arrays
            bools = [ [0,1][i] for i in self.Selection ]
            selection = [
                "defaults", self.Defaults,
                "unordered", [ "i8", bools ]
            ]
        return [ gdef, [ "selection", selection ] ]

def savePoly(prim):
    ''' Create the schema for the primitive '''
    return [
        "vertex", prim.Vertices,
        "closed", prim.Closed
    ]

def saveMesh(prim):
    ''' Create the schema for the primitive '''
    return [
        "vertex", prim.Vertices,
        "surface", prim.Surface,
        "uwrap", prim.Uwrap,
        "vwrap", prim.Vwrap,
    ]

def saveMetaBall(prim):
    ''' Create the schema for the primitive '''
    return [
        "vertex", prim.Vertices[0],
        "transform", prim.Transform,
        "metakernel", prim.Kernel,
        "metaweight", prim.Weight
    ]
def saveMetaSQuad(prim):
    ''' Create the schema for the primitive '''
    return [
        "vertex", prim.Vertices[0],
        "transform", prim.Transform,
        "metakernel", prim.Kernel,
        "metaweight", prim.Weight,
        "xy-exponent", prim.XYExponent,
        "z-exponent", prim.ZExponent
    ]
def saveParticle(prim):
    ''' Create the schema for the primitive '''
    return [
        "vertex", prim.Vertices,
        "renderproperties", prim.RenderProperties,
    ]

def saveQuadric(prim):
    ''' Create the schema for the primitive '''
    return [
        "vertex", prim.Vertices[0],
        "transform", prim.Transform,
    ]

def saveTube(prim):
    ''' Create the schema for the primitive '''
    return [
        "vertex", prim.Vertices[0],
        "transform", prim.Transform,
        "caps", prim.Caps,
        "taper", prim.Taper,
    ]

def saveSplineCurve(prim):
    ''' Create the schema for the primitive '''
    return [
        "vertex", prim.Vertices,
        "closed", prim.Closed,
        "basis", prim.Basis.save()
    ]

def saveSplineMesh(prim):
    ''' Create the schema for the primitive '''
    data = [
        "vertex", prim.Vertices,
        "surface", prim.Surface,
        "uwrap", prim.Uwrap,
        "vwrap", prim.Vwrap,
        "ubasis", prim.UBasis.save(),
        "vbasis", prim.VBasis.save()
    ]
    if hasattr(prim, 'Profiles'):
        # Profiles are stored as a contained detail
        data.append("profiles")
        data.append(prim.Profiles.saveJSON())
    return data

def saveVolume(prim):
    ''' Create the schema for the primitive '''
    return [
        "vertex", prim.Vertices[0],
        "transform", prim.Transform,
        "res", prim.Resolution,
        "border", prim.Border,
        "compression", prim.Compression,
        "voxels", prim.Voxels
    ]
def saveUnknown(prim):
    ''' Create the schema for an unknown primitive primitive.  This is simply
        the primitive data loaded for an unknown primitive. '''
    return prim.Data

primSavers = {
    'BezierCurve' : saveSplineCurve,
    'BezierMesh'  : saveSplineMesh,
    'Circle'      : saveQuadric,
    'Mesh'        : saveMesh,
    'MetaBall'    : saveMetaBall,
    'MetaSQuad'   : saveMetaSQuad,
    'NURBCurve'   : saveSplineCurve,
    'NURBMesh'    : saveSplineMesh,
    'Part'        : saveParticle,
    'Poly'        : savePoly,
    'Sphere'      : saveQuadric,
    'Tube'        : saveTube,
    'Volume'      : saveVolume,
}

class Primitive:
    '''
        A primitive represents a geometric primitive in a detail.  Every
        primitive has a vertex list and may have other intrinsic attributes
        (i.e. a closed flag for faces, a transform for quadrics, etc.).
    '''
    def __init__(self, prim_type, vertices=[]):
        ''' Initialize the primitive of the given type.  All primitives have a
        list of vertices '''
        self.Type = prim_type
        self.Vertices = vertices

    def save(self):
        ''' Call the appropriate save method to generate the schema for the
        primitive. '''
        return [
            [ "type", self.Type ],
            primSavers.get(self.Type, saveUnknown)(self)
        ]

    def getVertexCount(self):
        ''' Return the number of vertices used by the primitive '''
        return len(self.Vertices)
    def getVertexOffset(self, vertex_index):
        ''' Return vertex offset for the N'th vertex of the primitive '''
        return self.Vertices[vertex_index]

def loadBasis(bdata):
    ''' Create a Basis object from the schema '''
    b = Basis()
    b.load(bdata)
    return b

def loadPoly(ptype, pdata):
    ''' Load the primitive from the schema '''
    pdata = listToDict(pdata)
    prim = Primitive('Poly', pdata['vertex'])
    prim.Closed = pdata.get('closed', True)
    return prim

def loadMesh(ptype, pdata):
    ''' Load the primitive from the schema '''
    pdata = listToDict(pdata)
    prim = Primitive('Mesh', pdata['vertex'])
    prim.Surface = pdata['surface']
    prim.Uwrap = pdata['uwrap']
    prim.Vwrap = pdata['vwrap']
    return prim

def loadMetaBall(ptype, pdata):
    ''' Load the primitive from the schema '''
    pdata = listToDict(pdata)
    prim = Primitive(ptype, [pdata['vertex']])
    prim.Transform = pdata['transform']
    prim.Kernel = pdata['metakernel']
    prim.Weight = pdata['metaweight']
    return prim
def loadMetaSQuad(ptype, pdata):
    ''' Load the primitive from the schema '''
    pdata = listToDict(pdata)
    prim = Primitive(ptype, [pdata['vertex']])
    prim.Transform = pdata['transform']
    prim.Kernel = pdata['metakernel']
    prim.Weight = pdata['metaweight']
    prim.XYExponent = pdata['xy-exponent']
    prim.ZExponent = pdata['z-exponent']
    return prim

def loadQuadric(ptype, pdata):
    ''' Load the primitive from the schema '''
    pdata = listToDict(pdata)
    prim = Primitive(ptype, [pdata['vertex']])
    prim.Transform = pdata['transform']
    return prim

def loadTube(ptype, pdata):
    ''' Load the primitive from the schema '''
    pdata = listToDict(pdata)
    prim = Primitive('Tube', [pdata['vertex']])
    prim.Transform = pdata['transform']
    prim.Caps = pdata.get('caps', False)
    prim.Taper = pdata.get('taper', 1)
    return prim

def loadSplineCurve(ptype, pdata):
    ''' Load the primitive from the schema '''
    pdata = listToDict(pdata)
    prim = Primitive(ptype, pdata['vertex'])
    prim.Closed = pdata['closed']
    prim.Basis = loadBasis(pdata['basis'])
    return prim

def loadSplineMesh(ptype, pdata):
    ''' Load the primitive from the schema '''
    pdata = listToDict(pdata)
    prim = Primitive(ptype, pdata['vertex'])
    prim.Surface = pdata['surface']
    prim.Uwrap = pdata['uwrap']
    prim.Vwrap = pdata['vwrap']
    prim.UBasis = loadBasis(pdata['ubasis'])
    prim.VBasis = loadBasis(pdata['vbasis'])
    profiles = pdata.get('profiles', None)
    if profiles:
        prim.Profiles = Detail()
        prim.Profiles.loadJSON(profiles)
    return prim

def loadParticle(ptype, pdata):
    ''' Load the primitive from the schema '''
    pdata = listToDict(pdata)
    prim = Primitive(ptype, pdata['vertex'])
    prim.RenderProperties = pdata.get('renderproperties', {})
    return prim
def loadVolume(ptype, pdata):
    ''' Load the primitive from the schema '''
    pdata = listToDict(pdata)
    prim = Primitive(ptype, [pdata['vertex']])
    prim.Transform = pdata['transform']
    # Voxel resolution
    prim.Resolution = pdata['res']
    # Dictionary of border parameters
    prim.Border = pdata['border']
    # Dictionary of compression parameters
    prim.Compression = pdata['compression']
    # JSON encoding of UT_VoxelArray
    prim.Voxels = pdata['voxels']
    return prim
def loadUnknown(ptype, pdata):
    ''' Load the primitive from the schema '''
    prim = Primitive(ptype, [])
    prim.Data = pdata
    return prim

primLoaders = {
    'BezierCurve'  : loadSplineCurve,
    'BezierMesh'   : loadSplineMesh,
    'Circle'       : loadQuadric,
    'Mesh'        : loadMesh,
    'MetaBall'    : loadMetaBall,
    'MetaSQuad'    : loadMetaSQuad,
    'NURBCurve'    : loadSplineCurve,
    'NURBMesh'     : loadSplineMesh,
    'Part'         : loadParticle,
    'Poly'         : loadPoly,
    'Sphere'       : loadQuadric,
    'Tube'        : loadTube,
    'Volume'       : loadVolume,

    # Uncommon primitive types.  These are passed through verbatim currently
    'MetaBezier'   : loadUnknown,
    'MetaLine'     : loadUnknown,
    'MetaTriangle' : loadUnknown,
    'PasteSurf'    : loadUnknown,
    'TriBezier'    : loadUnknown,
    'TriFan'       : loadUnknown,
    'TriStrip'     : loadUnknown,
}

def primRun(pdef, pdata):
    ''' Load a run of primitives.  A run consists of a set of "uniform" fields
        which have the same value for all primitives in the run as well as a
        list of the varying fields (fields which have different values for the
        primitives in the run).  Each primitive's data in the run has a simple
        list of data which maps exactly (in size and order) to the list of
        varying fields.'''
    # Load a run of primitives
    ptype = pdef['runtype']
    vfield = pdef['varyingfields']      # Values unique to each primitive
    data = pdef['uniformfields']      # Values shared by all run primitives
    primlist = []
    for v in pdata:
        vidx = 0
        for field in vfield:
            data[field] = v[vidx]
            vidx += 1
        primlist.append(primLoaders.get(ptype, loadUnknown)(ptype, data))
    return primlist

class Detail:
    '''
        A detail object contains:
            - Point Attributes
            - Vertex Attributes
            - Primitive Attributes
            - Global/Detail Attributes
            - VertexMap (which points are referenced by which vertices)
            - A list of primitives
            - Group information
    '''
    def __init__(self):
        ''' Initialize an empty detail '''
        self.PointAttributes = {}
        self.PrimitiveAttributes = {}
        self.VertexAttributes = {}
        self.GlobalAttributes = {}
        self.VertexMap = []
        self.Primitives = []
        self.Info = None

    def pointCount(self):
        ''' Return the number of points '''
        P = self.PointAttributes['P']
        return len(P.Array)
    def vertexCount(self):
        ''' Return the total number of vertices '''
        return len(self.VertexMap)
    def primitiveCount(self):
        ''' Return the number of primitives '''
        return len(self.Primitives)

    def vertexPoint(self, vertex_offset):
        ''' Return the point offset for the given vertex offset.  That is, the
            point referenced by the given vertex. '''
        return self.VertexMap[vertex_offset]

    def loadTopology(self, obj):
        ''' Load the topology -- the map of the unique vertices to shared
            points '''
        obj = listToDict(obj)
        pointref = listToDict(obj.get('pointref', None))
        _Assert(pointref, "Missing 'pointref' for topology")
        self.VertexMap = pointref.get('indices', None)
        _Assert(self.VertexMap and type(self.VertexMap) == list,
                "Invalid vertex topology")

    def loadSingleAttribute(self, attrib_data, element_count):
        ''' Interpret the schema for an attribute and create the attribute.
            Attributes are stored in a list of 2 objects.  The first object is
            the attribute definition, the second is the attribute's data.'''
        _Assert(type(attrib_data) == list and len(attrib_data) == 2,
                    'Invalid attribute defintion block')
        adef = listToDict(attrib_data[0])
        attrib = Attribute(adef['name'], adef['type'], adef['scope'])
        attrib.Options = adef.get('options', {})
        attrib.loadValues(attrib_data[1], element_count)
        return attrib

    def loadAttributeDict(self, attrib_list, element_count):
        ''' Interpret the schema for a dictionary of attributes.  That is, all
            the attributes for a given element type (point, vertex, etc.) '''
        if not attrib_list:
            return {}
        attributes = {}
        for attrib in attrib_list:
            a = self.loadSingleAttribute(attrib, element_count)
            if a:
                attributes[a.Name] = a
        return attributes

    def loadAttributes(self, obj, pointcount, vertexcount, primitivecount):
        ''' Interpret the schema to load all attributes '''
        obj = listToDict(obj)
        self.VertexAttributes = self.loadAttributeDict(
                        obj.get('vertexattributes', None), vertexcount)
        self.PointAttributes = self.loadAttributeDict(
                        obj.get('pointattributes', None), pointcount)
        self.PrimitiveAttributes = self.loadAttributeDict(
                        obj.get('primitiveattributes', None), primitivecount)
        self.GlobalAttributes = self.loadAttributeDict(
                        obj.get('globalattributes', None), 1)

    def loadElementGroup(self, obj, element_count):
        ''' Interpret the schema to load all element groups for a given type '''
        glist = {}
        nload = 0
        if obj:
            for g in obj:
                gdef = listToDict(g[0])
                gname = gdef['name']
                glist[gname] = ElementGroup(gname)
                glist[gname].loadSelection(g[1], element_count)
                nload += 1
                if nload % 100 == 0:
                    _Verbose('Loaded %d groups' % nload)
        return glist

    def loadElementGroups(self, obj):
        ''' Load all vertex, point and primitive groups '''
        self.VertexGroups = self.loadElementGroup(
                        obj.get('vertexgroups', None), self.vertexCount())
        self.PointGroups = self.loadElementGroup(
                        obj.get('pointgroups', None), self.pointCount())
        self.PrimitiveGroups = self.loadElementGroup(
                        obj.get('primitivegroups', None), self.primitiveCount())

    def loadSinglePrimitive(self, pdef, pdata):
        ''' Load a single primitive by finding a function to interpret the
            schema for the type.  If there's no known schema, we just hold onto
            the data block so it can be saved (see loadUnknown)'''
        pdef = listToDict(pdef)
        ptype = pdef['type']
        if ptype == 'run':
            self.Primitives += primRun(pdef, pdata)
        else:
            self.Primitives.append(primLoaders.get(ptype, loadUnknown)(ptype, pdata))

    def loadPrimitives(self, obj):
        ''' Load all primitives from the schema '''
        for p in obj:
            self.loadSinglePrimitive(p[0], p[1])

    def loadJSON(self, file):
        ''' Interpret the JSON object schema to create a Detail object '''
        file = listToDict(file)
        self.Info = file.get('info', None)
        self.loadTopology(file['topology'])
        _Verbose('Loaded Topology')
        self.loadAttributes(file['attributes'], pointcount=file['pointcount'],
                            vertexcount=file['vertexcount'],
                            primitivecount=file['primitivecount'])
        _Verbose('Loaded Attributes')
        self.loadPrimitives(file['primitives'])
        _Verbose('Loaded Primitives')
        self.loadElementGroups(file)
        _Verbose('Loaded Groups')

        # Trim regions for profile curves
        """
        if file.has_key("altitude"):
            self.Altitude = file["altitude"]
        if file.has_key("trimregions"):
            self.TrimRegions = []
            for t in file["trimregions"]:
                region = TrimRegion()
                region.load(t)
                self.TrimRegions.append(region)
        """
    def saveAttributes(self, name, adict):
        ''' Create the JSON schema for an attribute dictionary '''
        if not adict:
            return []
        attribs = []
        for a in adict:
            attribs += [adict[a].save()]
        return [ name, attribs ]

    def savePrimitives(self):
        ''' Create the JSON schema for all the primitives '''
        prims = []
        for p in self.Primitives:
            prims.append(p.save())
        return [ "primitives", prims ]

    def saveGroups(self, glabel, gtype, glist):
        ''' Create the JSON schema for the element groups for a single element
            type.'''
        if glist:
            groups = []
            for gname in glist:
                g = glist[gname]
                groups.append(g.save(gtype))
            return [ glabel, groups ]
        return []

    def saveJSON(self):
        ''' Create the JSON schema for the detail:  all the attributes,
            primitives, groups.
            For 2D (trim curves), the detail also contains special properties
            for the altitude and trim regions.'''
        data = []
        data += [ 'fileversion', _VERSION ]
        data += [ 'pointcount', self.pointCount() ]
        data += [ 'vertexcount', self.vertexCount() ]
        data += [ 'primitivecount', self.primitiveCount() ]
        data += [ 'topology', [ 'pointref', [ 'indices', self.VertexMap ] ] ]
        attribs = []
        attribs += self.saveAttributes('vertexattributes', self.VertexAttributes)
        attribs += self.saveAttributes('pointattributes', self.PointAttributes)
        attribs += self.saveAttributes('primitiveattributes', self.PrimitiveAttributes)
        attribs += self.saveAttributes('globalattributes', self.GlobalAttributes)
        if attribs:
            data += ["attributes", attribs]
        data += self.savePrimitives()
        data += self.saveGroups("pointgroups", "point", self.PointGroups)
        data += self.saveGroups("vertexgroups", "vertex", self.VertexGroups)
        data += self.saveGroups("primitivegroups", "primitive", self.PrimitiveGroups)
        if hasattr(self, 'Altitude'):
            data += ["altitude", self.Altitude]
        if hasattr(self, 'TrimRegions'):
            regions = []
            for t in self.TrimRegions:
                regions.append(t.save())
            data += ["trimregions", regions]
        return data

    def save(self, fp, indent=None):
        ''' Save the JSON schema to a file '''
        hjson.dump(self.saveJSON(), fp, indent=indent)


#############################################################
#  Test Functions
#############################################################
def _ginfoAttributes(style, attributes):
    # Print out attributes
    if attributes:
        print('%s Attributes' % style)
        for name in attributes:
            a = attributes[name]
            print('    %s %s[%d]' % (a.Type, a.Name, a.TupleSize))

def _ginfoGroups(style, groups):
    # Print out group information
    if groups:
        print('%s Groups' % style)
        for name in groups:
            g = groups[name]
            ordered = ''
            if g.Order:
                ordered = 'ordered, '
            print('    %s (%s%d elements)' % (g.Name, ordered, g.Count))

def _ginfoPrimitives(primlist):
    # Print out primitive information
    counts = {}
    for p in primlist:
        counts[p.Type] = counts.get(p.Type, 0) + 1
    print('%d Primitives' % (len(primlist)))
    for p in counts:
        print(' %10d %s' % (counts[p], p))

def _dumpPrimitive(detail, prim_num):
    prim = detail.Primitives[prim_num]
    nvtx = prim.getVertexCount()
    print('Primitive', prim_num, 'is a', prim.Type, 'and has', nvtx, 'vertices.')
    P = detail.PointAttributes['P']
    for i in range(nvtx):
        vertex = prim.getVertexOffset(i)
        point = detail.vertexPoint(vertex)
        print('  Vertex[%d]->Point[%d]  P=' % (i, point), P.getValue(point))

def _ginfo(filename):
    try:
        fp = open(filename, 'r')
    except:
        print('Unable to open', filename)
        return
    _Verbose('Loading %s' % filename)
    fdata = hjson.load(fp)
    _Verbose('Done Loading %s' % filename)
    d = Detail()
    d.loadJSON(fdata)
    print('='*10, filename, '='*10)
    print('%12d Points' % d.pointCount())
    print('%12d Vertices' % d.vertexCount())
    print('%12d Primitives' % d.primitiveCount())
    print('-'*5, 'Attributes', '-'*5)
    _ginfoAttributes('Point', d.PointAttributes)
    _ginfoAttributes('Vertex', d.VertexAttributes)
    _ginfoAttributes('Primitive', d.PrimitiveAttributes)
    _ginfoAttributes('Global', d.GlobalAttributes)
    _ginfoGroups('Point', d.PointGroups)
    _ginfoGroups('Vertex', d.VertexGroups)
    _ginfoGroups('Primitive', d.PrimitiveGroups)
    _ginfoPrimitives(d.Primitives)
    _dumpPrimitive(d, 0)

def test():
    if len(sys.argv) == 1:
        _ginfo(os.path.expandvars('$HH/geo/defgeo.bgeo'))
    else:
        for f in sys.argv[1:]:
            _ginfo(f)

if __name__ == "__main__":
    VERBOSE = True
    test()
