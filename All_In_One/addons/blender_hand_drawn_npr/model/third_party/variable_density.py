# Fast irregular domain node layout
### John H. Williamson 2018
#### MIT license (see LICENSE)

import numpy as np


def moving_front_nodes(density_fn, domain, init_pts=500, new_pts=5):
    """Implements the Fast generation of 2-D node distributions for mesh-free PDE
        discretizations algorithm by Fornberg and Flyer
        (see: https://amath.colorado.edu/faculty/fornberg/Docs/2015_FF_Node_placing_CMA.pdf)

    Parameters:
        density_fn: should be a function taking an (x,y) co-ordinate and returning the expected
                    density of points at this point, in terms of points/unit area
                    NOTE: not units per unit distance!
        domain:    rectangular region (x1,y1,x2,y2) to generate points in
        new_pts:   number of new points to generate at each iteration (default:5)
        init_pts:  number of initial points on the bottom of the domain


    Returns:
        pts:       Nx2 matrix of x,y, node locations

    """
    x1, y1, x2, y2 = domain

    # initial bottom row
    xpts = np.random.uniform(x1, x2, (init_pts,))
    pts = np.vstack([xpts, np.ones(init_pts) * y1]).T

    # list of final points, to be populated as we go
    nodes = []

    while len(pts) > 0 and np.any(pts[:, 1] < y2):
        # jitter used to break ties in the lowest point selection
        jitter = np.random.uniform(0, 1e-8, (len(pts),))
        lowest = pts[np.argmin(pts[:, 1] + jitter)]

        # query the density function
        radius = (1.0 / np.sqrt(density_fn(lowest[0], lowest[1])))

        # keep this point
        nodes.append(np.array(lowest))

        # select the potential points to retain (at least radius away)
        keep = np.sqrt(np.sum((pts - lowest) ** 2, axis=1)) >= radius
        pts = pts[keep]

        # compute distances to neighbours on left and right
        distances = np.sqrt(np.sum((pts - lowest) ** 2, axis=1))
        left = np.nonzero(pts[:, 0] < lowest[0])[0]
        right = np.nonzero(pts[:, 0] > lowest[0])[0]

        # find smallest neighbours on left and right
        if len(left) == 0:
            # no points to the left -- use fixed value
            a_left = -np.pi / 2
        else:
            smallest_left = pts[left[np.argmin(distances[left])]]
            l_vector = lowest - smallest_left
            a_left = np.arctan2(l_vector[1], l_vector[0])

        if len(right) == 0:
            # no points to the right -- use fixed value
            a_right = -np.pi / 2
        else:
            smallest_right = pts[right[np.argmin(distances[right])]]
            r_vector = lowest - smallest_right
            a_right = np.arctan2(r_vector[1], r_vector[0])

        if np.abs(a_right - np.pi) < 1e-8:
            a_right = -np.pi

            # space the points inside the sector, but *not* touching the edges of the sector
        # (this was a pain to get right)
        pt_angles = np.linspace(a_left, a_right, new_pts, endpoint=False) + (a_right - a_left) / (new_pts * 2)

        # create the new points
        inserted_pts = np.vstack([np.cos(pt_angles) * radius,
                                  -np.sin(pt_angles) * radius]).T + lowest

        # insert the new points
        pts = np.vstack([pts, inserted_pts])

        # clip to within the domain
        pts = pts[pts[:, 0] <= x2]
        pts = pts[pts[:, 0] >= x1]

    return np.array(nodes)
