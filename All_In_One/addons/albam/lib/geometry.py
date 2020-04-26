
def y_up_to_z_up(x_y_z_tuple):
    x, y, z = x_y_z_tuple
    return x, z * -1, y


def z_up_to_y_up(x_y_z_tuple):
    x, y, z = x_y_z_tuple
    return x, z, y * -1


def vertices_from_bbox(box_min_x, box_min_y, box_min_z,
                       box_max_x, box_max_y, box_max_z):
    """
    Return a tuple with
    1 - a list with 8 tuples representing the vertices of the box that the
    given bounding box min and max values represent
    2 - the faces of that box
    """
    v0 = (box_min_x, box_min_y, box_min_z)
    v1 = (box_min_x, box_min_y, box_max_z)
    v2 = (box_min_x, box_max_y, box_min_z)
    v3 = (box_min_x, box_max_y, box_max_z)
    v4 = (box_max_x, box_min_y, box_min_z)
    v5 = (box_max_x, box_min_y, box_max_z)
    v6 = (box_max_x, box_max_y, box_min_z)
    v7 = (box_max_x, box_max_y, box_max_z)

    faces = [
        (1, 3, 2, 0),
        (3, 7, 6, 2),
        (7, 5, 4, 6),
        (5, 1, 0, 4),
        (0, 2, 6, 4),
        (5, 7, 3, 1)
        ]

    return [v0, v1, v2, v3, v4, v5, v6, v7], faces
