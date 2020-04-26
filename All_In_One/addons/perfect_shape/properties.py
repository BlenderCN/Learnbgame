import bpy
import bmesh
from bpy.app.handlers import persistent
from perfect_shape.shaper import get_loops
from perfect_shape.utils import get_icon, clear_cache


def enum_shape_types(self, context):
    shapes = [("CIRCLE", "Circle", "Simple circle", get_icon("circle"), 0),
              ("RECTANGLE", "Rectangle", "Simple rectangle", get_icon("rectangle"), 1),
              ("OBJECT", "Object", "Custom shape from object", get_icon("object"), 2)]

    if len(context.scene.perfect_shape.patterns) > 0:
        idx = context.scene.perfect_shape.active_pattern
        pattern = context.scene.perfect_shape.patterns[int(idx)]
        shapes.append(("PATTERN", pattern.name, "Active 'Perfect Pattern'", get_icon(idx, "patterns"), 3))
    return shapes


def enum_patterns(self, context):
    patterns = []
    for idx, pattern in enumerate(context.scene.perfect_shape.patterns):
        patterns.append((str(idx), pattern.name, "", get_icon(str(idx), "patterns"), idx))
    return patterns


def object_update(self, context):
    shape = context.scene.perfect_shape.shape
    shape.verts.clear()
    shape.faces.clear()
    if self.target in bpy.data.objects:
        object = bpy.data.objects[self.target]
        shape_bm = bmesh.new()
        shape_bm.from_object(object, context.scene)
        loops = get_loops(shape_bm.edges[:])
        if loops and len(loops) == 1:
            for vert in loops[0][0][0]:
                item = shape.verts.add()
                item.co = vert.co
            shape_bm.clear()
            for vert in shape.verts:
                shape_bm.verts.new(vert.co)
            shape_bm.verts.ensure_lookup_table()
            verts = shape_bm.verts[:]
            for i in range(len(verts)-1):
                shape_bm.edges.new((verts[i], verts[i+1 % len(verts)]))
            bmesh.ops.contextual_create(shape_bm, geom=shape_bm.edges)
            bmesh.ops.triangulate(shape_bm, faces=shape_bm.faces)
            for face in shape_bm.faces:
                item = shape.faces.add()
                item.indices = [v.index for v in face.verts]
            del shape_bm


def shape_update(self, context):
    clear_cache(self.as_pointer())


class PerfectShape:
    bl_idname = "mesh.perfect_shape"
    bl_label = "To Perfect Shape"
    bl_options = {"REGISTER", "UNDO"}

    mode = bpy.props.EnumProperty(name="Mode",
                                  items=[("RESHAPE", "Reshape", "Only reshape edges or faces", "", 0),
                                         ("INDENT", "Indent", "Indent amd reshape edges or faces", "", 1)],
                                  default="RESHAPE")

    active_tab = bpy.props.EnumProperty(name="Active Tab",
                                  items=[("POSITIONING", "Positioning", "", "", 0),
                                         ("SHAPING", "Shaping", "", "", 1),
                                         ("SELECTION", "Selection", "", "", 2)],
                                  default="POSITIONING")

    shape = bpy.props.EnumProperty(name="A perfect", items=enum_shape_types, update=shape_update)
    fill_type = bpy.props.EnumProperty(name="Fill Type",
                                       items=[("ORIGINAL", "Original", "", "", 0),
                                              ("COLLAPSE", "Collapse", "", "", 1),
                                              ("HOLE", "Hole", "", "", 2),
                                              ("NGON", "Ngon", "", "", 3)],
                                       default="ORIGINAL", description="Type of loop-inside geometry")

    projection = bpy.props.EnumProperty(name="Projection",
                                        items=[("NORMAL", "Normal", "", "", 0),
                                               ("X", "X", "", "", 1),
                                               ("Y", "Y", "", "", 2),
                                               ("Z", "Z", "", "", 3)],
                                        default="NORMAL")

    invert_projection = bpy.props.BoolProperty(name="Invert Direction", default=False)
    use_ray_cast = bpy.props.BoolProperty(name="Wrap to surface", default=False, description="Cast shape to base mesh")
    fill_flatten = bpy.props.BoolProperty(name="Flatten", default=False, description="Flatten loop-inside geometry")

    loop_rotation = bpy.props.BoolProperty(name="Loop Rotation", default=False, description="Apply loop rotation")
    shape_rotation = bpy.props.BoolProperty(name="Shape Rotation", default=False,
                                            description="Apply shape rotation")

    shape_translation = bpy.props.FloatVectorProperty(name="Translation", subtype="XYZ", precision=4,
                                                      description="Additional shape translation")

    ratio_a = bpy.props.IntProperty(name="Ratio a", min=1, default=1, update=shape_update,
                                    description="Number of edges on rectangle 'a' side")
    ratio_b = bpy.props.IntProperty(name="Ratio b", min=1, default=1, update=shape_update,
                                    description="Number of edges on rectangle 'b' side")
    is_square = bpy.props.BoolProperty(name="Square", default=False, update=shape_update,
                                       description="Equal sides")

    target = bpy.props.StringProperty(name="Object", update=object_update)
    factor = bpy.props.IntProperty(name="Factor", min=0, max=100, default=100, subtype="PERCENTAGE",
                                   description="Reshape factor")
    inset = bpy.props.FloatProperty(name="Inset", min=0.0, default=0, precision=3,
                                    description="Additional inset loop")
    outset = bpy.props.FloatProperty(name="Outset", min=0.0, default=0, precision=3,
                                     description="Additional outset loop")
    side_inset = bpy.props.FloatProperty(name="Side Inset", min=0.0, default=0, precision=3,
                                         description="Additional side inset loop")
    offset = bpy.props.FloatProperty(name="Offset", precision=3, description="Changes shape size")
    shift = bpy.props.IntProperty(name="Shift", description="Changes the order of vertices for the given number")
    rotation = bpy.props.FloatProperty(name="Rotation", subtype="ANGLE", default=0, precision=3,
                                       description="Additional shape rotation")
    span = bpy.props.IntProperty(name="Span", min=0, update=shape_update, description="Additional circle segments")
    extrude = bpy.props.FloatProperty(name="Extrude", default=0, precision=3, description="Extrude value.")
    cuts = bpy.props.IntProperty(name="Cuts", min=0, max=100, default=0, description="Number of side cuts")
    cuts_len = bpy.props.IntProperty(name="Cuts Length", min=1, default=1, description="Number of edges to cut")
    cuts_repeat = bpy.props.IntProperty(name="Cuts Repeat", min=1, max=100, default=1,
                                        description="Number of cut repeats")
    cuts_shift = bpy.props.IntProperty(name="Shift", default=0, description="Changes the order of cuts")
    cuts_rings = bpy.props.IntProperty(name="Rings", min=0, max=100, default=0, description="Number of side rings")

    pivot_point = bpy.props.StringProperty()
    transform_orientation = bpy.props.StringProperty()


class Vert(bpy.types.PropertyGroup):
    co = bpy.props.FloatVectorProperty(precision=6)
    precision = 0


class Face(bpy.types.PropertyGroup):
    indices = bpy.props.IntVectorProperty()


class PerfectPattern(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(default="Pattern")
    verts = bpy.props.CollectionProperty(type=Vert)
    faces = bpy.props.CollectionProperty(type=Face)


class PerfectShapeProperties(bpy.types.PropertyGroup):
    objects = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    preview_verts_count = bpy.props.IntProperty(min=4, default=4)
    shape = bpy.props.PointerProperty(type=PerfectPattern)

    active_pattern = bpy.props.EnumProperty(name="Active Pattern", items=enum_patterns)
    patterns = bpy.props.CollectionProperty(type=PerfectPattern)


@persistent
def handler(scene):
    if bpy.data.objects.is_updated:
        ps = scene.perfect_shape
        ps.objects.clear()
        for object in bpy.data.objects:
            if object.type == "MESH":
                item = ps.objects.add()
                item.name = object.name


def register():
    bpy.utils.register_class(Vert)
    bpy.utils.register_class(Face)
    bpy.utils.register_class(PerfectPattern)
    bpy.utils.register_class(PerfectShapeProperties)
    bpy.types.Scene.perfect_shape = bpy.props.PointerProperty(type=PerfectShapeProperties)
    bpy.app.handlers.scene_update_pre.append(handler)


def unregister():
    del bpy.types.Scene.perfect_shape
    bpy.utils.unregister_class(Vert)
    bpy.utils.unregister_class(Face)
    bpy.utils.unregister_class(PerfectPattern)
    bpy.utils.unregister_class(PerfectShapeProperties)
    bpy.app.handlers.scene_update_pre.remove(handler)
