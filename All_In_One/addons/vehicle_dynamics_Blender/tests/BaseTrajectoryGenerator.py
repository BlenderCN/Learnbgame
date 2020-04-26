"""
Provide a base abstract class to generate a trajectory and get accelerations from it.
Then check a integrated trajectory against original one to measure level of error.

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

from abc import ABC, abstractmethod

import numpy as np


class BaseTrajectoryGenerator(ABC):

    def __init__(self, max_time=100, time_step=1e-2):
        dt = time_step  # timestep
        self.max_time = max_time
        # timestamps
        self.times = np.arange(0, max_time, dt)
        # create a trajectory here only because check_trajectory would require one
        self.trajectory = np.zeros((3, 100))

    @abstractmethod
    def get_analytical_accelerations(self):
        pass

    @abstractmethod
    def get_analytical_velocities(self):
        pass

    @abstractmethod
    def get_numerical_derived_accelerations(self):
        pass

    @abstractmethod
    def get_start_velocity(self):
        pass

    @abstractmethod
    def check_trajectory(self, external_trajectory):
        pass

    @abstractmethod
    def plot_trajectory(self):
        pass
