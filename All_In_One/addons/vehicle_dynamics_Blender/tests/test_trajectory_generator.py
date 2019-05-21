"""
Test for correct trajectory generation from TrajectoryGenerator class

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

from unittest import TestCase
import numpy as np

from SpringTrajectoryGenerator import SpringTrajectoryGenerator


class TrajectoryGeneratorTests(TestCase):

    def test_numerical_vs_analytical(self):
        """Calculate difference between numerically derived and analytical derived"""
        # this is only for personal interest and is not so much related to project
        # define a threshold
        arbitrary_acceptable_threshold = 0.1
        # generate trajectory object
        trajectory_generator = SpringTrajectoryGenerator()
        # get numerical accelerations
        accelerations_num = trajectory_generator.get_numerical_derived_accelerations()
        # get analytical accelerations
        accelerations_analytical = trajectory_generator.get_analytical_accelerations()
        # compute the error as the absolute difference
        error = abs(accelerations_analytical - accelerations_num)
        print("median error numerical-analytical derivative {} meters".format(error.mean()))
        self.assertTrue(abs(error.mean()) < arbitrary_acceptable_threshold)
