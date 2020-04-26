import unittest
from pam import grid
from pam import kernel
import numpy as np
import cProfile
#import matplotlib.pyplot as plt
from pam import pam_vis as pv
from imp import reload

reload(grid)

N = 5000

def plotArray(grid,fac=1.):
    for x, row in enumerate(grid):
        for y, cell in enumerate(row):
            pv.visualizePoint([x/4, y/4, cell*fac])

def testGrid():
    np.random.seed(42)
    g = grid.UVGrid(None)
    print("Computing post mask")
    # g.compute_post_mask(kernel.gauss, [1.0, 1.0, 0.0, 0.0])
    g.compute_post_mask(kernel.gauss, [0.5, 0.5, 0., 0.])
    print("Inserting post neurons")
    uvs = np.random.rand(N, 2)
    for i, uv in enumerate(uvs):
        g.insert_postNeuron(i, uv, (1., 2., 3.), 42)
    print("Compute pre-mask")
    g.compute_pre_mask(kernel.gauss, [2., 0.5, 0., 0.])
    print("selecting")
    # for i in range(N/10):
    random_points = g.select_random((0.2, 0.3), N)
    # pdb.set_trace()
    # plt.scatter([p[1][0] for p in random_points], [p[1][1] for p in random_points])
    # plt.hist([p[1][0] for p in random_points], 20)
    # plt.hist([p[1][1] for p in random_points], 20)
    # plt.axis([0, 1, 0, 1])
    # plt.show()
    return g, random_points

cProfile.run('testGrid()')