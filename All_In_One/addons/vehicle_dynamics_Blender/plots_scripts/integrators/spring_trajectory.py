#!/usr/bin/env python
"""
Plot motion accelerations from tests/SpringTrajectoryGenerator and integrated trajectory

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

from plots_scripts.plot_utils import plot_vectors
from tests.test_integration import get_integrated_trajectory, SpringTrajectoryGenerator, \
    cumulative_integrate

if __name__ == "__main__":
    trajectory = SpringTrajectoryGenerator()
    trajectory.plot_trajectory()
    accelerations = trajectory.get_analytical_accelerations()
    plot_vectors([accelerations], ["accelerations"])
    integrated_trajectory = get_integrated_trajectory(cumulative_integrate)
    plot_vectors([integrated_trajectory], ["integrated trajectory"])
    # blocking call to show all plots
    plt.show()
