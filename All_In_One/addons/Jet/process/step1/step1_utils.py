from ... common_utils import select_obj_exclusive

def flat_smooth(obj, smooth):
    select_obj_exclusive(obj)
    mesh = obj.data
    for f in mesh.polygons:
        f.use_smooth = smooth











