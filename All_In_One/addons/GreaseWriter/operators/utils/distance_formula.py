from math import sqrt


def distance_formula(p1, p2):
    """
    Calculate the distance between 2 points on a 2D Cartesian coordinate plane

    Parameters
    ----------
    p1: list of int
        The x and y of a point, ie: [1, 0]
    p2: list of int
        The x and y of a point, ie: [2, 3]

    Returns
    -------
    distance: float
        The distance between the 2 points
    """
    x = p2[0] - p1[0]
    y = p2[1] - p1[1]
    z = p2[2] - p1[2]

    distance = sqrt(x**2 + y**2 + z**2)
    return distance
