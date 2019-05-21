import bpy
import bpy_extras.view3d_utils
from mathutils import Vector

def get_bookgen_collection():
    for c in bpy.context.scene.collection.children:
        if c.name == "BookGen":
            return c

    col = bpy.data.collections.new("BookGen")
    bpy.context.scene.collection.children.link(col)
    return col

def get_shelf_collection(name):
    bookgen = get_bookgen_collection()
    for c in bookgen.children:
        if c.name == name:
            return c

    col = bpy.data.collections.new(name)
    bookgen.children.link(col)
    return col

def visible_objects_and_instances(context):
    """Loop over (object, matrix) pairs (mesh only)"""

    for obj in context.visible_objects:
        if obj.type == 'MESH':
            yield (obj, obj.matrix_world.copy())

        if obj.instance_type != 'NONE':
            obj.dupli_list_create(context.scene)
            for dob in obj.dupli_list:
                obj_dupli = dob.object
                if obj_dupli.type == 'MESH':
                    yield (obj_dupli, dob.matrix.copy())


def obj_ray_cast(obj, matrix, ray_origin, ray_target):
    """Wrapper for ray casting that moves the ray into object space"""

    # get the ray relative to the object
    matrix_inv = matrix.inverted()
    ray_origin_obj = matrix_inv @ ray_origin
    ray_target_obj = matrix_inv @ ray_target
    ray_direction_obj = ray_target_obj - ray_origin_obj

    # cast the ray
    success, location, normal, _ = obj.ray_cast(ray_origin_obj, ray_direction_obj)

    if success:
        return location, normal
    else:
        return None, None

def get_shelf_parameters():
    properties = bpy.context.collection.BookGenProperties

    parameters = {
        "scale": properties.scale,
        "seed": properties.seed,
        "alignment": properties.alignment,
        "lean_amount": properties.lean_amount,
        "lean_direction": properties.lean_direction,
        "lean_angle": properties.lean_angle,
        "rndm_lean_angle_factor": properties.rndm_lean_angle_factor,
        "book_height": properties.book_height,
        "rndm_book_height_factor": properties.rndm_book_height_factor,
        "book_width": properties.book_width,
        "rndm_book_width_factor": properties.rndm_book_width_factor,
        "book_depth": properties.book_depth,
        "rndm_book_depth_factor": properties.rndm_book_depth_factor,
        "cover_thickness": properties.cover_thickness,
        "rndm_cover_thickness_factor": properties.rndm_cover_thickness_factor,
        "textblock_offset": properties.textblock_offset,
        "rndm_textblock_offset_factor": properties.rndm_textblock_offset_factor,
        "spline_curl": properties.spline_curl,
        "rndm_spline_curl_factor": properties.rndm_spline_curl_factor,
        "hinge_inset": properties.hinge_inset,
        "rndm_hinge_inset_factor": properties.rndm_hinge_inset_factor,
        "hinge_width": properties.hinge_width,
        "rndm_hinge_width_factor": properties.rndm_hinge_width_factor,
        "spacing": properties.spacing,
        "rndm_spacing_factor": properties.rndm_spacing_factor,
        "subsurf": properties.subsurf,
        "smooth": properties.smooth,
        "unwrap": properties.unwrap
    }
    return parameters

def get_click_position_on_object(x,y):
    region = bpy.context.region
    regionData = bpy.context.space_data.region_3d

    view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, regionData, (x,y))
    ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, regionData, (x,y))

    ray_target = ray_origin + view_vector

    best_length_squared = -1.0
    closest_loc = None
    closest_normal = None

    for obj, matrix in visible_objects_and_instances(bpy.context):
        if obj.type == 'MESH':
            hit, normal = obj_ray_cast(obj, matrix, ray_origin, ray_target)
            if hit is not None:
                hit_world = matrix @ hit
                normal_world = matrix @ normal
                length_squared = (hit_world - ray_origin).length_squared
                if closest_loc is None or length_squared < best_length_squared:
                    best_length_squared = length_squared
                    closest_loc = hit_world
                    closest_normal = normal

    return closest_loc, closest_normal


def vector_scale(veca, vecb):
    return Vector(x * y for x, y in zip(veca, vecb))

def get_free_shelf_id():
    shelves = get_bookgen_collection().children

    names = list(map(lambda x: x.name, shelves))
    nameFound = False
    shelf_id = 0
    while not nameFound:
        if "shelf_"+str(shelf_id) not in names:
            return shelf_id
        shelf_id += 1