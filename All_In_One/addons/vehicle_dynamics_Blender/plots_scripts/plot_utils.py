"""
Various plotting routines

This file is part of inertial_to_blender project,
a Blender simulation generator from inertial sensor data on cars.

Copyright (C) 2018  Federico Bertani
Author: Federico Bertani
Credits: Federico Bertani, Stefano Sinigardi, Alessandro Fabbri, Nico Curti

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import matplotlib.pyplot as plt
# needed for 3d projection
from mpl_toolkits.mplot3d import axes3d, Axes3D


def plot_vectors(vectors_list, label_list=None, title=None, tri_dim=True, horiz=None):
    """ Plot 3xn numpy array in 2d and 3d

    plt.show() blocking call must be called to show all plot created whit this function

    :param vectors_list: list of 3xn numpy array
    :param label_list: optional list of custom 3d plot label (matching 1-1 with vectors-list)
    :param title: string figure title
    :param tri_dim: boolean toggle 3d plot
    :param horiz: units for x axis in 2d plot
    :return figure
    """

    axis_labels = ['x', 'y', 'z']
    label_list = label_list if (label_list is not None) else [" "] * len(vectors_list)
    if (tri_dim):
        fig = plt.figure(figsize=plt.figaspect(0.5))
        axes_2d = fig.add_subplot(1, 2, 1)
        axes_3d = fig.add_subplot(1, 2, 2, projection='3d')
    else:
        fig = plt.figure()
        axes_2d = fig.add_subplot(1, 1, 1)
    if (title):
        fig.suptitle(title)
    for vectors, label in zip(vectors_list, label_list):
        # if vector is multidimensional
        if (vectors.ndim > 1):
            if (horiz is not None):
                [axes_2d.plot(horiz, ri, label=axis_labels[i] + " " + label) for i, ri in enumerate(vectors)]
            else:
                [axes_2d.plot(ri, label=axis_labels[i] + " " + label) for i, ri in enumerate(vectors)]
            if (tri_dim):
                axes_3d.plot(*vectors, label=label)
                axes_3d.set_xlabel('x')
                axes_3d.set_ylabel('y')
                axes_3d.set_zlabel('z')
        else:
            if (horiz is not None):
                axes_2d.plot(horiz, vectors, label=label)
            else:
                axes_2d.plot(vectors, label=label)
    axes_2d.legend()
    if (tri_dim):
        axes_3d.legend()

    return fig
