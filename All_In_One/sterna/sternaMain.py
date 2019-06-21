import bpy, bmesh, random, mathutils, math, sys, statistics
from operator import itemgetter
from bpy.props import *
try:
    import blenderEdgeGroups
except ImportError:
    pass

#scale: 10^-9 m per blender unit
SIZE = 0.04
RADIUS = 0.87
TWIST = 32.73 / 180 * math.pi
AXIS = 139.9 / 180 * math.pi
INCLINATION = -0.745
RISE = 0.281
SCALE = 1.0
BASE_SCALE = 1.0
PADDING = ((RADIUS * TWIST) ** 2 + RISE ** 2) ** 0.5

PSEUDOKNOT = [mathutils.Vector((0.4572869837284088, 0.5845826864242554, -0.3552049994468689)),mathutils.Vector((0.5469346642494202, 0.45932722091674805, -0.18733333051204681)),mathutils.Vector((0.5347004532814026, 0.36931490898132324, 0.04300406202673912)),mathutils.Vector((0.408108115196228, 0.322445273399353, 0.24883319437503815)),mathutils.Vector((0.21678157150745392, 0.29012489318847656, 0.3955526053905487)),mathutils.Vector((0.12219792604446411, 0.12540683150291443, 0.31169795989990234)),mathutils.Vector((0.04380570352077484, -0.14312498271465302, 0.33146655559539795)),mathutils.Vector((0.25417810678482056, -0.11538200080394745, 0.23201553523540497)),mathutils.Vector((0.353906512260437, -0.05814199522137642, 0.045394133776426315)),mathutils.Vector((0.37148767709732056, 0.047506943345069885, -0.15476365387439728)),mathutils.Vector((0.27843713760375977, 0.20184843242168427, -0.31510046124458313)),mathutils.Vector((0.13389913737773895, 0.3663172125816345, -0.3737988770008087)),mathutils.Vector((-0.014406491070985794, 0.5343915820121765, -0.2716743052005768)),mathutils.Vector((-0.1172197237610817, 0.6745545864105225, -0.11854805797338486)),mathutils.Vector((-0.06670432537794113, 0.7806087732315063, 0.07638392597436905)),mathutils.Vector((0.10408409684896469, 0.8677849173545837, 0.22594521939754486)),mathutils.Vector((0.31368061900138855, 0.936124861240387, 0.2840360105037689)),mathutils.Vector((0.5414252281188965, 0.9846553206443787, 0.21302276849746704)),mathutils.Vector((0.7015998959541321, 1.026299238204956, 0.02060226909816265))
]

#",".join(["mathutils." + n.co.to_3d().__repr__() for n in C.object.data.splines[0].points])




class BASE_PRIMITIVE():

    verts = [
        mathutils.Vector((1, 0, 0)),
        mathutils.Vector((-1, 0, 0)),
        mathutils.Vector((0, 1, 0)),
        mathutils.Vector((0, -1, 0)),
        mathutils.Vector((0, 0, 1)),
        mathutils.Vector((0, 0, -1))
    ]


    faces = [
        (0, 2, 4),
        (0, 2, 5),
        (0, 3, 4),
        (0, 3, 5),
        (1, 2, 4),
        (1, 2, 5),
        (1, 3, 4),
        (1, 3, 5),
    ]


def init():
    global blenderEdgeGroups
    try:
        blenderEdgeGroups
    except:
        blenderEdgeGroups = sys.modules[modulesNames['blenderEdgeGroups']]
    global sterna_data
    sterna_data = {}

    bpy.types.Object.normalRotationParam = FloatProperty(
        name="Initial normal angle",
        min = -math.pi, max = math.pi,
        precision = 3,
        default = 0
    )

    bpy.types.Object.sizeParam = FloatProperty(
        name="Size",
        min = 0.001, max = 0.2,
        precision = 4,
        default = SIZE
    )

    bpy.types.Object.paddingParam = FloatProperty(
        name="Base Distance",
        min = 0.01, max = 10,
        precision = 4,
        default = PADDING
    )

    bpy.types.Object.minPadding = IntProperty(
        name="Min padding",
        default = 1,
        min = 0
    )

    bpy.types.Object.maxPadding = IntProperty(
        name="Max padding",
        default = 4,
        min = 0
    )

    bpy.types.Object.scaleParam = FloatProperty(
        name="Scale",
        min = 1, max = 100.0,
        precision = 4,
        step = 100,
        default = SCALE
    )

    bpy.types.Object.radiusParam = FloatProperty(
        name="Radius",
        min = 0.01, max = 1.0,
        precision = 4,
        default = RADIUS
    )

    bpy.types.Object.twistParam = FloatProperty(
        name="Twist",
        min = -3.14, max = 3.14,
        precision = 4,
        default = TWIST
    )

    bpy.types.Object.axisParam = FloatProperty(
        name="Axis",
        min = -3.14, max = 3.14,
        precision = 4,
        default = AXIS
    )

    bpy.types.Object.riseParam = FloatProperty(
        name="Rise",
        min = 0.01, max = 1.0,
        precision = 4,
        default = RISE
    )

    bpy.types.Object.inclinationParam = FloatProperty(
        name="Inclination",
        min = -1.0, max = 1.0,
        precision = 4,
        default = INCLINATION
    )

    bpy.types.Object.offsetParam = FloatProperty(
        name="Corner offset multiplier",
        min = -100.0, max = 100.0,
        precision = 4,
        default = 1
    )


    bpy.types.Object.rstParam = BoolProperty(
        name="Use random spanning tree",
        default = False
    )


    bpy.types.Object.ulParam = BoolProperty(
        name="Try to force integer number of turns",
        default = False
    )


    bpy.types.Object.numTurnsParam = IntProperty(
        name="Number of full turns",
        default = 3,
        min = 0
    )


    bpy.types.Object.isSternaHelix = BoolProperty(
        name="isSternaHelix",
        default = False
    )


    bpy.types.Object.genMesh = BoolProperty(
        name="Generate a mesh",
        default = False
    )


    bpy.types.Object.springRelax = BoolProperty(
        name="Spring relax",
        default = False
    )


    bpy.types.Object.useAdaptiveOffset = BoolProperty(
        name="Use adaptive offset",
        default = False
    )

    bpy.types.Object.springRelaxSteps = IntProperty(
        name="Relaxation steps",
        min = 1, max = 10000,
        default = 100
    )

    bpy.types.Object.springRelaxOrder = FloatProperty(
        name="Spring order",
        min = 1.0, max = 100.0,
        default = 5
    )



def register():
    bpy.utils.register_class(GenerateHelix)
    bpy.utils.register_class(SelectPseudoknots)
    bpy.utils.register_class(SelectBasePairs)
    bpy.utils.register_class(SternaPanel)
    init()
    #bpy.types.PROPERTIES_HT_header.append(draw_item)


def unregister():
    bpy.utils.unregister_class(SelectPseudoknots)
    bpy.utils.unregister_class(GenerateHelix)
    bpy.utils.unregister_class(SelectBasePairs)
    bpy.utils.unregister_class(SternaPanel)


class SternaPanel(bpy.types.Panel):
    """A panel with the buttons and parameters required to generate an RNA nano-
    structure
    """
    bl_category = 'MyTab'
    bl_label = "Sterna"
    bl_idname = "sterna_main_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "modifier"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type in {'MESH', 'LATTICE'})


    def draw(self, context):
        layout = self.layout

        obj = context.object
        me = context.mesh

        row = layout.row()
        row.label(text="Sterna", icon='WORLD_DATA')
        row = layout.row()
        if obj.isSternaHelix:
            if not validate_sterna(context):
                row.label(text="Invalid Sterna Helix")
                row = layout.row()
            row.label(text = "Scale: " + str(obj.scaleParam))
            row.label(text = "Bases: " + str(len(obj.data.vertices)))
            row = layout.row()
            row.operator("object.select_pseudoknots")
            row.operator("object.select_base_pairs")
            row = layout.row()
            row.operator("mesh.hide")
            row.operator("mesh.reveal")

        else:
            row.label(text="Parameters")
            row = layout.row()
            row.label(text="Resolution")
            row = layout.row()
            row.prop(obj, 'scaleParam')
            row = layout.row()
            row.label(text="Visual parameters")
            row = layout.row()
            row.prop(obj, 'genMesh')
            if obj.genMesh:
                row.prop(obj, 'sizeParam')
            row = layout.row()
            row.label(text="Physical parameters")
            row = layout.row()
            row.prop(obj, 'radiusParam')
            row.prop(obj, 'twistParam')
            row = layout.row()
            row.prop(obj, 'axisParam')
            row.prop(obj, 'riseParam')
            row = layout.row()
            row.prop(obj, 'inclinationParam')
            row = layout.row()
            row.label(text="Generator settings")
            row = layout.row()
            row.prop(obj, 'offsetParam')
            row = layout.row()
            row.prop(obj, 'paddingParam')
            row = layout.row()
            row.prop(obj, 'minPadding')
            row.prop(obj, 'maxPadding')
            row = layout.row()
            row.prop(obj, 'useAdaptiveOffset')
            row = layout.row()
            row.prop(obj, 'rstParam')
            row = layout.row()
            row.prop(obj, 'ulParam')
            row = layout.row()
            if obj.ulParam:
                row.prop(obj, 'numTurnsParam')
                row = layout.row()
            row = layout.row()
            row.label(text="Post processing")
            row = layout.row()
            row.prop(obj, 'springRelax')
            row = layout.row()
            row.prop(obj, 'springRelaxOrder')
            row.prop(obj, 'springRelaxSteps')
            row = layout.row()
            row.operator("object.generate_helix")

def validate_sterna(context):
    """ Determines the validity of a sterna helix.

    Returns: bool
    """
    if len(context.object.data.polygons) > 0:
        return False

    return True

class SelectPseudoknots(bpy.types.Operator):
    """ An operator selecting pseudoknots.
    """
    """Tooltip"""
    bl_idname = "object.select_pseudoknots"
    bl_label = "Select Pseudoknots"

    @classmethod
    def poll(cls, context):
        obj = context.object
        bm = 1#blender_edge_groups.dic.get(obj.name)
        return obj.isSternaHelix == 1

    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        for e in context.object.data.edges:
            if e.use_edge_sharp:
                e.select = True
        bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'}

class SelectBasePairs(bpy.types.Operator):
    """ An operator selecting base pairs.
    """
    """Tooltip"""
    bl_idname = "object.select_base_pairs"
    bl_label = "Select Base Pairs"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.isSternaHelix == 1

    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        for e in context.object.data.edges:
            if e.use_seam:
                e.select = True
        bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'}

class GenerateHelix(bpy.types.Operator):
    """ An operator generating a sterna helix from a mesh.
    """
    """Tooltip"""
    bl_idname = "object.generate_helix"
    bl_label = "Generate Helix"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj.isSternaHelix != 1

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")
        eo = context.edit_object
        structure = get_structure(context)
        bases, scale = get_bases(structure, context)
        bpy.ops.object.mode_set(mode="OBJECT")
        if eo.genMesh: create_mesh(bases, context)
        create_sterna_helix(context, bases, scale)
        return {'FINISHED'}


def find_start(bm):
    """ Finds the start vertex of the Sterna Helix by finding the shorterst distance to the end.

    Args:
        bm -- bmesh

    Returns:
        bmesh.Vertex
    """
    v1, i1 = traverse_to_end(bm, True)
    v2, i2 = traverse_to_end(bm, False)
    print(i1)
    print(i2)
    if i1 == i2:
        return bm.verts[0]
    elif i1 <= i2:
        return v1
    else:
        return v2

def traverse_to_end(bm, forwards = True):
    """ Traverses a Sterna Helix and returns the index and vertex of the final vertex.

    Args:
        bm -- bmesh

    KWArgs:
        forwards -- bool, direction of the traversal

    Returns:
        bmesh.Vertex, int
    """
    visited = set()
    c_v = bm.verts[0]
    i = 0
    while True:
        i += 1
        v = c_v
        edges = v.link_edges if forwards else reversed(v.link_edges)
        for e in edges:
            e_verts = set([vx.index for vx in e.verts])
            index_other = sum(e_verts) - v.index
            other = bm.verts[index_other]
            if not e.seam and e.smooth:
                if not index_other in visited:
                    c_v = other
        visited.add(v.index)
        if v == c_v: break
    return c_v, i

def export_sterna_helix(object):
    """ Serializes the BMesh.

    Args:
        Sterna Helix

    Returns:
        coordinates -- str
        secondary_structure -- str
        pseudoknot_numbering -- str

    """
    assert object.isSternaHelix

    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(object.data)
    dotbracket = []
    pseudoknot_numbering = []
    coords = []

    visited = set()
    p_d = {}
    p_num = 0
    in_pknot = False
    prev_other = None
    bm.verts.ensure_lookup_table()

    c_v = find_start(bm)
    while True:
        print(c_v)
        v = c_v
        coords.append(v.co * object.scaleParam)
        edges = v.link_edges
        current = "."
        for e in edges:
            e_verts = set([vx.index for vx in e.verts])
            index_other = sum(e_verts) - v.index
            other = bm.verts[index_other]
            if e.seam:
                if not index_other in visited:
                    current = "("
                else:
                    current = ")"
            elif not e.smooth:
                if not index_other in visited:
                    current = "["
                    if not in_pknot or bm.edges.get((other, prev_other)) == None:
                        p_num = len(set(pseudoknot_numbering))
                    prev_other = other # Need to check whether two pseudoknots start immediately consecutively
                else:
                    current = "]"
                    p_num = p_d[index_other]
            else:
                if not index_other in visited:
                    c_v = other

        dotbracket.append(current)
        p_d[v.index] = p_num
        visited.add(v.index)
        if current in "[]":
            if not in_pknot:
                pseudoknot_numbering.append(p_num)
            in_pknot = True
        else:
            in_pknot = False
        if c_v == v: break


    dotbracket = "".join(dotbracket)
    pseudoknot_numbering = " ".join([str(x) for x in pseudoknot_numbering])
    coords = ", ".join(["{} {} {}".format(*c) for c in coords])

    bpy.ops.object.mode_set(mode="OBJECT")

    return coords, dotbracket, pseudoknot_numbering


def import_sterna_helix(data):
    """ Converts a dictionary to an array of bases

    Args:
        dictionary -- must contain secondary_structure, pseudoknot_numbering and positions

    Returns:
        bases -- array
    """
    secondary_structure = data["secondary_structure"]
    pseudoknot_numbering = data["pseudoknot_numbering"].split(" ")
    positions = data["positions"].strip("[] ").split(",")

    bases = []
    pairs = {}
    stack = []
    p_stack = {}
    p_num = None

    for i, sym in enumerate(secondary_structure):
        pos = positions[i].strip().split(" ")
        b = Base(mathutils.Vector([float(x) for x in pos]))
        if sym in "[]":
            if p_num == None:
                p_num = pseudoknot_numbering.pop(0)
            b.p_num = p_num
            if p_num not in pseudoknot_numbering:
                p_stack[p_num][-1].pair = b
                b.pair = p_stack[p_num].pop()
            else:
                p_stack.setdefault(p_num, []).append(b)
        else:
            p_num = None
            if sym == "(":
                stack.append(b)
            elif sym == ")":
                stack[-1].pair = b
                b.pair = stack.pop()
        bases.append(b)
    return bases

def create_base_primitive(origin, size):
    """ Creates a base primitive at origin with a radius of size.
    """
    # Create mesh and object
    me = bpy.data.meshes.new('Base Mesh')
    ob = bpy.data.objects.new("Base", me)
    ob.location = origin

    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True

    verts = [size * v for v in BASE_PRIMITIVE.verts]

    # Create mesh from given verts, faces.
    me.from_pydata(verts, [], BASE_PRIMITIVE.faces)
    # Update mesh with new data
    me.update()
    """
    bpy.ops.mesh.primitive_uv_sphere_add(location=origin, size=size, segments=6, ring_count=6)
    """


def create_mesh(bases, context):
    """ Creates a 3D mesh of a Sterna Helix
    """
    obj = context.object
    scale = obj.scaleParam;
    size = obj.sizeParam;

    prev_objects = set(bpy.context.scene.objects)
    for o in prev_objects:
        o.select = False

    for b in bases:
        create_base_primitive(b.co, scale * size)
    objects = set(bpy.context.scene.objects) - prev_objects
    for o in objects:
        o.select = True
        bpy.context.scene.objects.active = o
    bpy.ops.object.join()

def create_sterna_helix(context, bases, scale):
    """ Creates a Sterna Helix

    Args:
        context
        bases -- array
        scale -- float, the relation between blender units and nanometers

    Returns:
        Blender.Object
    """
    me = bpy.data.meshes.new('Backbone')
    ob = bpy.data.objects.new("Sterna Helix", me)
    ob.location = context.object.location if context.object else mathutils.Vector()

    scn = bpy.context.scene
    scn.objects.link(ob)
    ob.isSternaHelix = True
    ob.scaleParam = scale
    scn.objects.active = ob
    ob.select = True

    verts = [b.co for b in bases]
    edges = []
    backbone = [(i, i + 1) for i in range(len(bases) - 1)]
    base_pairs = []
    pseudoknots = []
    visited = set()
    indices = []
    pseudo_indices = {}
    in_pknot = False
    for i, b in enumerate(bases):
        if b.p_num != None:
            if b.p_num in pseudo_indices and not in_pknot:
                pseudoknots.append((i, pseudo_indices[b.p_num].pop()))
            else:
                t = pseudo_indices.setdefault(b.p_num, [])
                t.append(i)
                in_pknot = True
        else:
            in_pknot = False
            if b.pair:
                if b.pair in visited:
                    base_pairs.append((i, indices.pop()))
                else:
                    visited.add(b)
                    indices.append(i)
    edges.extend(backbone)
    edges.extend(base_pairs)
    edges.extend(pseudoknots)
    me.from_pydata(verts, edges, [])

    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(me)
    # Mark base pairs
    for e in bm.edges:
        if e.index >= len(backbone):
            e.select = True
        else:
            e.select = False
    bpy.ops.mesh.mark_seam()
    # Mark Pseudoknots
    for e in bm.edges:
        if e.index >= len(backbone) + len(base_pairs):
            e.select = True
        else:
            e.select = False
    bpy.ops.mesh.mark_seam(clear = True)
    bpy.ops.mesh.mark_sharp()

    return ob



def get_structure(context):
    """ Returns a routing of a mesh based on a spanning tree.

    Returns:
        array<edge, type> -- array of edges and their types as either stem edges or pseudoknots
    """
    obj = context.object
    rst = obj.rstParam;

    eo = context.edit_object
    mesh = blenderEdgeGroups.dic.get(eo.name, bmesh.from_edit_mesh(eo.data))

    #dict = mesh_to_dict(mesh)
    spanning_tree, pseudo_knots = get_trees(mesh, rst)
    start = spanning_tree[0].verts[0]
    structure = traverse(start, spanning_tree, pseudo_knots)
    return structure


def get_trees(mesh, rnd = False):
    """ Returns a spanning tree of the mesh.

    KWArgs:
        rnd -- bool, default = False, use random spanning tree rather than edge groups

    Returns:
        array -- edges in spanning tree
        array -- edges in pseudonots
    """
    spanning_tree = []
    pseudo_knots = []
    if rnd: rst = get_rst(0, mesh)
    else: egl = mesh.edges.layers.int.get("edge_groups")
    for e in mesh.edges:
        if not rnd and e[egl] is 1:
            spanning_tree.append(e)
        elif rnd and e in rst:
            spanning_tree.append(e)
        else:
            pseudo_knots.append(e)
    if not is_mst(mesh, spanning_tree):
        raise Exception("Invalid spanning tree")
    return spanning_tree, pseudo_knots


def is_mst(mesh, spanning_tree):
    """ Returns whether the given edges form a spanning tree of the mesh.
    """
    return True
    span = set()
    all = set()
    for e in mesh.edges:
        all.add(e.verts[0])
        all.add(e.verts[1])
    for e in spanning_tree:
        span.add(e.verts[0])
        span.add(e.verts[1])
    expected = len(mesh.verts) - 1
    return len(spanning_tree) == expected and span == all


class Base():
    """ A base object containing the position, pseudoknot number and its base pair.
    """

    def __init__(self, origin, p_num = None, pair = None):
        self.co = origin
        self.p_num = p_num
        self.pair = pair


    def bond(self, other):
        """ Pairs this base with another
        """
        self.pair = other
        other.pair = self

    def __repr__(self):
        return str(self.base)

class Strand():
    """ A representation of an RNA strand.
    """
    def __init__(self, context, structure):
        """
        Args:
            context
            structure -- a routing
        """
        obj = context.object
        self.true_scale = 1.0 / obj.scaleParam

        params = type("Parameters", (), {
            "scale": self.true_scale,
            "radius": obj.radiusParam,
            "twist": obj.twistParam,
            "axis": obj.axisParam,
            "rise": obj.riseParam,
            "inclination": obj.inclinationParam,
            "offset": obj.offsetParam,
            "unit_length": obj.ulParam,
            "num_turns": obj.numTurnsParam,
            "padding": obj.paddingParam,
            "spring_relax": obj.springRelax,
            "spring_relax_steps": obj.springRelaxSteps,
            "spring_relax_order": obj.springRelaxOrder,
            "use_adaptive_offset": obj.useAdaptiveOffset
        })

        self.padding = obj.paddingParam
        self.minPadding = obj.minPadding
        self.maxPadding = obj.maxPadding
        self.offset = obj.offsetParam

        #self.structure = self.translate_to_world(structure, obj.matrix_world)
        #self.initial_rotation = obj.normalRotationParam

        self.bases = []
        self.base_pairs = {}
        self.visited = set() # a set of visited edges
        self.p_visited = {} # A dictionary of visited pseudo knots mapping to their numbering
        self.cur = None # The coordinates of the last base inserted
        self.stack = [] # A stack of unpaired bases

        self.beam_network = self.BeamNetwork(structure, params)
        if params.spring_relax:
            self.beam_network.relax(params.spring_relax_steps, params.spring_relax_order)
        self.structure = structure


    def get_parameters(self):
        return self.beam_network.get_parameters()


    def get_orientation_vectors(self, e):

        """ Calculates the start point, end point and the normal vector for the given edge.

        Returns:
            bmesh.Vector -- start point
            bmesh.Vector -- end point
            bmesh.Vector -- normal vector with a magnitude
            bmesh.Vector -- d_t; (end - start) = d_t * num
            int          -- num
        """
        v1, v2 = e[1]
        cur_visited = (v2, v1) in self.visited
        beam = self.beam_network.get_beam(e)
        a, b, n = beam.get_orientation(cur_visited)
        num = beam.get_length_bases()
        t = (b - a).normalized() * self.get_parameters().rise * self.get_parameters().scale

        return a, b, n, t, num


    def get_padding(self, e):
        """ Creates padding bases between two helices.
        Args:
            e -- edge
        """
        a, b, n = self.get_orientation_vectors(e)[:3]
        end = self.cur
        start = a + n

        base_distance = self.get_parameters().padding * self.get_parameters().scale
        num = math.ceil((start - end).length / base_distance)
        num = max(min(num, self.maxPadding), self.minPadding)
        if num < 1: return
        t = 1.0 / num * (start - end)
        for i in range(1, num):
            coord = end + i * t
            self.bases.append(Base(coord))
            #self.cur = coord
        return 1

    def get_pseudoknot(self, e, visited, p_num):
        """ Creates pseudoknot bases.

        Args:
            e -- edge
            visited -- bool, edge has previously been visited
            p_num -- int, the number of the pseudoknot

        Returns:
            bmesh.Vector -- last coordinates
        """
        a0, b0, n, t, num = self.get_orientation_vectors(e)
        a = mathutils.Vector(a0)
        inclination = self.get_parameters().inclination * self.get_parameters().scale * t.normalized()
        coord = None
        if visited:
            t_n = mathutils.Vector(n)
            half = math.ceil(num / 2 - 4.5)#mathutils.Quaternion(t, self.get_parameter("twist"))
        else:
            t_n = mathutils.Vector(n)
            half = math.floor(num / 2 - 4.5)
        if num < 13:
            raise Exception("Edge too short for a pseudoknot.")
        rot = mathutils.Quaternion(t, self.get_parameters().twist)

        # First Half
        for i in range(half):
            coord = a0 + t_n + i * t
            self.bases.append(Base(coord))
            t_n.rotate(rot)
            self.stack.append(self.bases[-1])

        ## switch direction
        a = a0 + inclination + (half + 6) * t # half + 1 padding + 6 pseudoknot
        t_n = mathutils.Vector(n)
        t_n.rotate(mathutils.Quaternion(t, self.get_parameters().axis + (half + 6) * self.get_parameters().twist)) # half + 1 padding + 6 pseudoknot + axis
        t = -t

        # AA padding
        next_coord = a + t_n
        self.bases.append(Base((2/3) * coord + (1/3) * next_coord))
        self.bases.append(Base((1/3) * coord + (2/3) * next_coord))

        #Pseudo complex
        rot = mathutils.Quaternion(t, self.get_parameters().twist)
        for i in range(6):
            coord = a + t_n
            self.bases.append(Base(coord, p_num = p_num))
            t_n.rotate(rot)
            a += t

        # A padding
        coord = a + t_n
        self.bases.append(Base(coord))
        t_n.rotate(rot)

        # Second half
        for i in range(half):
            coord = a + (i + 1) * t + t_n
            self.bases.append(Base(coord))
            self.bases[-1].bond(self.stack.pop())
            t_n.rotate(rot)
        self.cur = coord
        return coord

    def get_edge(self, e, cur_visited):
        """ Creates the bases of an edge.

        Args:
            e -- edge
            cur_visited -- bool, edge previously visited

        Returns:
            bmesh.Vector -- last coordinates
        """
        a, b, n, t, num = self.get_orientation_vectors(e)
        n_t = None
        coord = None
        for i in range(num):
            rot = mathutils.Quaternion(t, i * self.get_parameters().twist)
            n_t = mathutils.Vector(n)
            n_t.rotate(rot)
            coord = a + i * t + n_t
            self.bases.append(Base(coord))
            if cur_visited:
                self.bases[-1].bond(self.stack.pop())
            else:
                self.stack.append(self.bases[-1])
        self.cur = coord
        return coord

    def get_bases(self):
        """ Does the routing and returns the bases.

        Returns:
            array -- list of bases
            scale -- scale factor used
        """

        for e in self.structure:
            type = e[0]
            v1, v2 = e[1]
            #Padding
            if self.cur:
                self.get_padding(e)
            #Edge
            if type == "e":
                visited = (v2, v1) in self.visited
                c = self.get_edge(e, visited)
                self.visited.add((v1, v2))
            #Pseudoknot
            elif type == "p":
                visited = (v2, v1) in self.p_visited
                if visited:
                    p_num = self.p_visited[(v2, v1)]
                else:
                    p_num = self.p_visited.setdefault((v1, v2), len(self.p_visited))
                c = self.get_pseudoknot(e, visited, p_num)
                self.visited.add((v1, v2))
                #print(len(self.visited))
        #self.normalize_scale()
        return self.bases, 1.0 / self.get_parameters().scale

    def normalize_scale(self):
        """ Sets scale to 1 and moves all bases accordingly.
        """
        for b in self.bases:
            b.co = (self.scale / self.true_scale) * b.co
        self.scale = self.true_scale

    class BeamNetwork():
        """ A beam network containing double helices as beams and methods
        to rescale and orientate the beams.
        """
        def __init__(self, structure, params):
            """
            Args:
                structure
                params -- parameters object
            """
            if params.unit_length:
                for i in range(10):
                    params = self.scale_to_unit_length(structure, params)
            self.beams, self.mapping = self.create_beams(structure, params)
            self.params = params

        def create_beams(self, structure, params):
            """ Creates beams according to the structure.

            Args:
                structure
                params -- parameters object

            Returns:
                Array -- beams array
                Map -- mapping of edges to the associated beam
            """
            created = {}
            mapping = {}
            last = None
            out_slot = 0
            for e in structure:
                if e[1] in created:
                    b = created[e[1]]
                    b.connect(last, 2, out_slot)
                    if e[0] == "e":
                        out_slot = 3
                    else:
                        out_slot = 1
                else:
                    b = self.Beam(e[1], params, type=e[0])
                    created[e[1][::-1]] = b
                    b.connect(last, 0, out_slot)
                    if e[0] == "e":
                        out_slot = 1
                    else:
                        out_slot = 3

                last = b
                mapping[e] = b
            beams = list(created.values())
            print(len(beams), beams)
            return beams, mapping


        def relax(self, steps = 50, order = 1.0):
            """ Relaxes the orientations of the beam network
            using spring relaxation.

            Args:
                steps -- iterations, int
                order -- the order of the spring strength

            Returns:
                float -- total torque in the system
            """
            for i in range(steps):
                force_multiplier = 0.5 ** int(i / (steps / 5))
                tot = 0
                for b in self.beams[::(-1)**i]:
                    tot += b.relax(force_multiplier, order)
                print("Total torque:", tot)
            return tot

        def get_parameters(self):
            """ Returns the parameters associated with this beam network.

            Returns:
                parameters object
            """
            return self.params

        def scale_to_unit_length(self, structure, params):
            """ Sets self.scale in such a way as to maximize the number of edges that are unit length.

            Args:
                structure
                params -- parameters object

            Returns:
                object -- new parameters object
            """
            beams, mapping = self.create_beams(structure, params)

            tolerance = 10000#round((2 * math.pi / self.twist))
            mods = {}
            for b in beams:
                turns = b.get_length_bases() * params.twist / (2 * math.pi)
                print("Turns: ", turns)

                if params.num_turns == 0:
                    f = round((math.floor(turns) / turns) * tolerance)
                else:
                    f = round((turns / params.num_turns) * tolerance) + 100
                if mods.get(f):
                    mods[f] += 1
                else:
                    mods[f] = 1
            print(mods)
            try:
                mod = statistics.mode(mods)
            except statistics.StatisticsError as e:
                mod = next(mods.__iter__())
            print(mod)
            new_scale = params.scale * mod / tolerance
            proportion = new_scale / params.scale
            print("Scale proportions:", proportion)
            print("New scale:", 1 / new_scale)
            params.scale = new_scale * 0.5 + params.scale * 0.5
            #if proportion > 10 or proportion < 0.1:
            #    raise Exception("Could not find unit length scale.")
            return params


        def get_beam(self, edge):
            """ Returns the beam associated with the edge.

            Returns:
                beam object
            """
            return self.mapping[edge]


        class Beam():
            """ A beam object represents a double helix. It contains four input /
            output sockets that can connect to other beams.
            """
            def __init__(self, edge, params, type = "e"):
                """
                Args:
                    edge
                    params -- parameters object
                """
                self.helical_axis = (edge[1].co - edge[0].co).normalized()
                axis = params.axis
                twist = params.twist
                scale = params.scale
                radius = params.radius
                half_inclination = params.inclination * scale * self.helical_axis * 0.5
                rise = params.rise
                start = edge[0].co + self.get_offset(edge, edge[0], params) * self.helical_axis - half_inclination
                end = edge[1].co - self.get_offset(edge, edge[1], params) * self.helical_axis + half_inclination
                length = (end - start).length
                self.num = int(length / scale / params.rise) + 1

                self.rotation = 0
                rot = mathutils.Quaternion(self.helical_axis, math.pi / 2)
                self.north = self.helical_axis.orthogonal().normalized() * scale * radius
                self.east = mathutils.Vector(self.north)
                self.east.rotate(rot)
                self.start = start
                self.end = self.start + (self.num - 1) * rise * scale * self.helical_axis
                self.edge = edge
                self.forces = []

                # Helix 1 A, Helix 1 B, Helix 2 A, Helix 2 B
                self.slots = [
                    0,
                    (self.num - 1) * twist,
                    (self.num - 1) * twist + axis,
                    axis
                ]
                self.positions = [
                    self.start - half_inclination,
                    self.end - half_inclination,
                    self.end + half_inclination,
                    self.start + half_inclination
                ]


            def is_sharp(self, edge, v0):
                """
                """
                sign = None
                if len(v0.link_edges) < 2:
                    return True
                inc = 2 * v0.co - edge[0].co - edge[1].co
                for e in v0.link_edges:
                    if set(e.verts) == set(edge): continue
                    dir = 2 * v0.co - e.verts[0].co - e.verts[1].co
                    if inc.angle(dir) < math.pi / 4:
                        return True
                return False


            def get_offset(self, edge, v0, params):
                """
                """
                #return self.get_cylinder_offset(edge, v0, params)
                if params.use_adaptive_offset:
                    if self.is_sharp(edge, v0):
                        return self.get_sphere_offset(v0, params)
                    else:
                        return self.get_cylinder_offset(edge, v0, params)
                else:
                    return self.get_sphere_offset(v0, params)


            def get_cylinder_offset(self, edge, v0, params):
                """ Calculates the offset required to avoid overlapping helices at vertices.

                Args:
                    edge -- bmesh.Edge, incoming edge
                    v0 -- bmesh.Vertex, end point
                    params -- parameters object

                Returns:
                    float -- offset along the edge
                """
                radius = params.radius * params.scale
                vectors = []
                m = float("inf")
                inc = 2 * v0.co - edge[0].co - edge[1].co
                if len(v0.link_edges) <= 1: return 0
                for e in v0.link_edges:
                    if set(e.verts) == set(edge): continue
                    other = 2 * v0.co - e.verts[0].co - e.verts[1].co
                    angle = inc.angle(other)
                    if angle < m:
                        m = angle
                h = radius / math.sin(m / 2)
                return (h**2.0 - radius**2.0)**0.5 * params.offset


            def get_sphere_offset(self, v0, params):
                """ Calculates the offset required to avoid overlapping helices at vertices.

                Args:
                    edge -- bmesh.Edge, incoming edge
                    v0 -- bmesh.Vertex, end point
                    params -- parameters object

                Returns:
                    float -- offset along the edge
                """
                radius = params.radius * params.scale
                vectors = []
                m = float("inf")
                for e in v0.link_edges:
                    #print(e)
                    if e.verts[0] == v0: vectors.append(e.verts[1].co - v0.co)
                    else: vectors.append(e.verts[0].co - v0.co)
                if len(vectors) <= 1: return 0
                for v1 in vectors:
                    for v2 in vectors:
                        if v2 == v1: continue
                        t = mathutils.Vector.angle(v1, v2)
                        #print(t)
                        if m > t: m = t
                h = radius / math.sin(m / 2)
                return (h**2.0 - radius**2.0)**0.5 * params.offset



            def get_orientation(self, visited):
                """ Returns the orientation of one of the helices associated with this beam.
                Args:
                    visited -- boolean, true if visited before

                Returns:
                    Vector -- start point
                    Vector -- end point
                    Vector -- normal vector of the first base
                """
                #print(visited)
                if visited:
                    rot = mathutils.Quaternion(self.helical_axis, self.get_angle(2))
                    a = self.positions[2]
                    b = self.positions[3]
                else:
                    rot = mathutils.Quaternion(self.helical_axis, self.get_angle(0))
                    a = self.positions[0]
                    b = self.positions[1]
                n = mathutils.Vector(self.east)
                n.rotate(rot)
                return a, b, n

            def get_length(self):
                """ Returns the absolute length of this beam. Note:
                    this is longer than a single helix.

                Returns:
                    float
                """
                return (self.positions[1] - self.positions[0]).length

            def get_length_bases(self):
                """ Returns the length of one helix in the number of bases

                Returns:
                    int
                """
                return self.num


            def connect(self, other, slot, other_slot):
                """ Connects a socket of this beam to another socket in another
                beam and vice versa.

                Args:
                    other -- other beam
                    slot -- socket
                    other_slot -- other socket
                """
                if other == None: return
                self.__connect__(other, slot, other_slot)
                other.__connect__(self, other_slot, slot)


            def __connect__(self, other, slot, other_slot):
                """ Connects a socket of this beam to another socket in another beam.

                Args:
                    other -- other beam
                    slot -- socket
                    other_slot -- other socket
                """
                force = lambda : self.get_force(other, slot, other_slot)
                self.forces.append(force)


            def get_position(self, slot):
                """ Returns the position of the base acting as a socket between
                two beams.

                Args:
                    slot -- socket

                Returns:
                    Vector -- position
                """
                angle = self.get_angle(slot)
                rot = mathutils.Quaternion(self.helical_axis, angle)
                n = mathutils.Vector(self.east)
                n.rotate(rot)
                pos = self.positions[slot] + n
                return pos


            def get_force(self, other, slot, other_slot):
                """ Returns the spring force experienced by one socket due to the
                beam it is connected to.

                Args:
                    other -- other beam
                    slot -- socket
                    other_slot -- other socket

                Returns:
                    float -- a signed angular force
                """
                a_rel = other.get_position(other_slot) - self.positions[slot]
                n = (a_rel - a_rel.dot(self.helical_axis) * self.helical_axis).normalized()
                angle = n.angle(self.east)

                #print(other.get_position(other_slot), self.get_position(slot), "\n--")
                #print(n)

                if n.dot(self.north) > 0: # bottom
                    angle = 2 * math.pi - angle

                dif = angle - self.get_angle(slot)
                if dif > math.pi: dif = dif - 2 * math.pi
                elif dif < -math.pi: dif = 2 * math.pi + dif
                #print("Difference: ", dif)
                return dif


            def get_angle(self, slot):
                """ Returns the angle of a socket in regards to the east
                direction of this beam.

                Args:
                    slot -- socket

                Returns:
                    float -- angle; [0, 2pi]
                """
                #print(slot)
                angle = self.slots[slot] + self.rotation
                angle -= int(angle / 2 / math.pi) * 2 * math.pi
                if angle < 0: angle += 2 * math.pi
                #print("Angle: ", angle)
                return angle

            def relax(self, force_multiplier = 1 / 10, order = 1.0):
                """ Relaxes the orientation of this beam according to the forces
                acting upon it by all other connected beams.

                Args:
                    force_multiplier -- defines the turn rate
                    order -- the spring force order

                Returns:
                    float -- total torque of this beam
                """
                #print(self.forces)
                tot = 0
                forces = []
                for force in self.forces:
                    #print(f())
                    f = force()
                    forces.append(f)
                    tot += abs(f) ** order
                for f in forces:
                    self.rotation += (f * abs(f) ** (order - 1) / tot + (random.random() - 0.5) * 1.52)  * force_multiplier
                #print("rotation:" , self.rotation)
                self.rotation -= int(self.rotation / 2 / math.pi) * 2 * math.pi
                if self.rotation < 0: self.rotation += math.pi * 2
                #print(":: ", tot)
                return abs(tot)



    def translate_to_world(self, structure, world):
        """ Translates all bases from local coordinates to world coordinates

        Args:
            structure
            world -- the matrix of transformation
        """
        #TODO
        return structure
        #print(structure)
        for v in structure:
            v.co = world * v.co

def get_bases(structure, context):
    """ Returns a list of bases in a strand.

    Returns:
        list -- bases
    """
    strand = Strand(context, structure)
    return strand.get_bases()


def sort_edges(vertex, previous):
    """ Sorts edges leading out from a vertex according to the zig-zag selection algorithm.
    If the vertex defines a convex corner, uses its normal vector to define the poles of the
    zig-zag algorithm. Otherwise uses the incoming edge to define the poles.

    Args:
        vertex
        previous -- previous edge visited

    Returns:
        array
    """
    print("----")
    print(vertex)
    print(previous)
    print("----")
    dir = (previous.verts[0].co - previous.verts[1].co).normalized()
    dir = vertex.normal.normalized()
    dir = 2 * len(vertex.link_edges) * vertex.co
    for x in vertex.link_edges:
        dir -= x.verts[0].co + x.verts[1].co
    dir = dir.normalized()
    ort = dir.orthogonal().normalized()
    nor = dir.cross(ort).normalized()
    print(dir, ort, nor)
    basis = mathutils.Matrix((dir, ort, nor)).transposed().inverted()
    edges = vertex.link_edges

    angles = []
    for e in edges:
        dir_t = e.verts[0].co + e.verts[1].co - 2 * vertex.co
        dir2 = basis * dir_t
        print(":::", dir2.x * dir + dir2.y * ort + dir2.z * nor)
        phi = math.atan2(dir2.y, dir2.z)
        if phi < 0: phi += 2 * math.pi
        print(phi, dir_t)
        theta = math.atan2(dir2.x, dir2.z)
        angles.append((e, phi, theta))
    sorted_edges = [x[0] for x in sorted(angles, key=itemgetter(1))]
    print(sorted_edges)
    for i, e in enumerate(sorted_edges):
        if e == previous:
            sorted_edges = sorted_edges[i+1:] + sorted_edges[:i]
    return sorted_edges


def traverse(root, spanning_tree, pseudo_knots, prev=None):
    """Traverses twice around a graph based on its spanning tree.

    Args:
        root -- vertex, root node
        spanning_tree -- array
        pseduo_knots -- array
        prev -- previously visited edge

    Returns:
        structure
    """
    #print("Root:" , root)
    structure = []
    neighbors = []
    if prev == None:
        prev = root.link_edges[0]
        neighbors.append(prev)
    neighbors.extend(sort_edges(root, prev))
    # traverse
    for edge in neighbors:
        if edge.verts[0] == root:
            l = (root, edge.verts[1])
        else:
            l = (root, edge.verts[0])
        if edge in pseudo_knots:
            e = ("p", l)
            structure.append(e)
        elif edge in spanning_tree:
            e1 = ("e", l)
            e2 = ("e", (l[1], l[0]))
            sub = traverse(l[1], spanning_tree, pseudo_knots, prev=edge)
            structure.append(e1)
            structure.extend(sub)
            structure.append(e2)
        else:
            raise Exception("Disconnected edge")
    return structure


def get_rst(start, mesh, seed = 1):
    """Returns a random minimum spanning tree of the given graph.

    Args:
        start -- The start node.
        mesh
        seed -- random seed

    Returns
        set -- A set of edges
    """
    mesh.edges.ensure_lookup_table()
    mesh.verts.ensure_lookup_table()
    rng = random.Random(seed)
    closed = set()
    edges = set()
    stack = [mesh.edges[start]]
    while stack:
        e = rng.choice(stack)
        v1 = e.verts[0]
        v2 = e.verts[1]
        stack.remove(e)
        if(v1 in closed and v2 in closed):
            continue
        closed.add(v1)
        closed.add(v2)
        edges.add(e)
        for e in set(v2.link_edges).union(v1.link_edges):
            stack.append(e)
    assert(len(edges) == len(mesh.verts) - 1)
    return edges


def mesh_to_dict(mesh):
    """Returns a dictionary mapping vertices to an ordered list of neighbors.

    Args:
        bmesh
    Returns:
        dictionary -- vertex => list<vertices>
    """
    dict = {}
    for f in mesh.faces:
        for i in range(len(f.verts)):
            l = dict.setdefault(f.verts[i], [])
            v0 = f.verts[i - 1]
            vc = f.verts[i]
            v1 = f.verts[(i + 1) % len(f.verts)]
            e0 = mesh.edges.get((vc, v0))
            e1 = mesh.edges.get((vc, v1))
            l.append(((v0, e0), (v1, e1)))
    for v in dict:
        #print(v, ":", dict[v], "\n")
        order = []
        _max = 100 # in case infinite loop. Should never happen
        while len(order) < len(v.link_edges) and _max > 0:
            _max -= 1
            assert(_max > 0)
            for t in dict[v]:
                if len(order) < 1:
                    order.append(t[0])
                else:
                    try:
                        if t[0] not in order:
                            order.insert(order.index(t[1]), t[0])
                        if t[1] not in order:
                            order.insert(order.index(t[0]) + 1, t[1])
                    except ValueError as e:
                        continue
        dict[v] = order
    return dict


if __name__ == "__main__":
    register()
