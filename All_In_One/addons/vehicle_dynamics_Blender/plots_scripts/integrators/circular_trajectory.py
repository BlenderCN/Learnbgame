#!/usr/bin/env python
"""
Plot motion accelerations from tests/CircularTrajectoryGenerator and integrated trajectory

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
import numpy as np

from src import rotate_accelerations
from plots_scripts.plot_utils import plot_vectors
from tests.test_integration import CircularTrajectoryGenerator, \
    cumulative_integrate

if __name__ == "__main__":
    # plots circular trajectory and integrated one for debugging and comparison purpose
    trajectory_gen = CircularTrajectoryGenerator()
    times = trajectory_gen.times
    accelerations = trajectory_gen.get_analytical_local_accelerations()
    angular_velocities = trajectory_gen.get_angular_velocities()
    # convert to laboratory frame of reference
    accelerations, angular_positions = rotate_accelerations(times, accelerations, angular_velocities,
                                                            initial_angular_position=[0, 0, np.pi / 2])
    initial_speed = np.array([[0], [trajectory_gen.initial_tangential_speed], [0]])
    velocities = cumulative_integrate(times, accelerations, initial_speed)
    initial_position = np.array([[1], [0], [0]])
    positions = cumulative_integrate(times, velocities, initial_position)
    plot_vectors([positions])
    plot_vectors([trajectory_gen.trajectory])
    # blocking call to show all plots
    plt.show()
