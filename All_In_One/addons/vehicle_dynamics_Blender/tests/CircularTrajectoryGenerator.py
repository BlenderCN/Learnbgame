"""
Circular trajectory on 2d plane with object rotation.
Useful for testing local to laboratory.

This file is part of inertial_to_blender project,
a Blender simulation generator from inertial sensor data on cars.

Copyright (C) 2018  Federico Bertani
Author: Federico Bertani, Alessandro Fabbri
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

import numpy as np

from BaseTrajectoryGenerator import BaseTrajectoryGenerator
from plots_scripts.plot_utils import plot_vectors


class CircularTrajectoryGenerator(BaseTrajectoryGenerator):

    def __init__(self, radius=1, max_time=10, time_step=1e-1, tangential_speed=1):
        super().__init__(max_time, time_step)
        self.radius = radius  # m
        self.initial_tangential_speed = tangential_speed
        # angular speed is inversely proportional to radius given tangential speed
        self.angular_speed_z = tangential_speed / self.radius
        # radial accelerations is inversely proportional to radius
        self.radial_acc = pow(self.initial_tangential_speed, 2) / self.radius
        self.initial_position = [self.radius, 0, 0]
        self.trajectory = np.vstack((
            np.cos(self.angular_speed_z * self.times) * self.radius,
            np.sin(self.angular_speed_z * self.times) * self.radius,
            np.zeros(len(self.times))
        ))

    def get_analytical_accelerations(self):
        """ in laboratory frame of reference"""

        # same as integral of get_analytical_velocities.
        return np.vstack((
            -np.cos(self.angular_speed_z * self.times) * self.radial_acc,
            -np.sin(self.angular_speed_z * self.times) * self.radial_acc,
            np.zeros(len(self.times))
        ))

    def get_analytical_local_accelerations(self):
        # left-handed coordinate system.
        # the center of the circumference is on the left of the point.
        size = len(self.times)
        return np.vstack((
            np.zeros(size),
            np.full(size, self.radial_acc),
            np.zeros(size)
        ))

    def get_analytical_velocities(self):
        # same as integral of self.trajectory
        return np.vstack((
            -np.sin(self.angular_speed_z * self.times) * self.initial_tangential_speed,
            np.cos(self.angular_speed_z * self.times) * self.initial_tangential_speed,
            np.zeros(len(self.times))
        ))

    def get_numerical_derived_accelerations(self):
        # no interest of comparison between numerical derived and analytical
        pass

    def get_start_velocity(self):
        return np.array([0, self.initial_tangential_speed, 0])

    def get_angular_velocities(self):
        size = len(self.times)
        return np.vstack((
            np.zeros((2, size)),
            np.full(size, self.angular_speed_z)
        ))

    def check_trajectory(self, external_trajectory):
        # just check almost equality, not interested in size of error here
        np.testing.assert_array_almost_equal(self.trajectory, external_trajectory)

    def plot_trajectory(self):
        plot_vectors([self.trajectory], ["analytical trajectory"])
