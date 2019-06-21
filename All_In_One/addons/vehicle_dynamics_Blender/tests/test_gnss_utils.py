"""
Tests for gnss utils module.

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
from src.gnss_utils import get_positions, get_velocities, get_accelerations
from src import align_to_world
from CircularTrajectoryGenerator import CircularTrajectoryGenerator


class GnssUtilsTests(TestCase):

    def test_get_positions(self):
        # create built-in array of coordinates (lat-lon)
        coordinates = np.array([
            (44.484372, 11.355899),
            (44.484171, 11.355872),
            (44.483912, 11.355410),
            (44.483966, 11.355011)])
        coordinates = np.deg2rad(coordinates)
        # altitude is zero
        altitudes = np.zeros(4)
        # create expected distance (values are taken from a website)
        expected_distance = np.array([0, 22.45, 64.20, 83.67])
        # call method to test
        positions, _ = get_positions(coordinates.T, altitudes)
        # calculate distance from (0,0) with norm
        distance = np.linalg.norm(positions, axis=0)
        # ground truth is calculated online with a website that use haversine distance, while get_position doesn't
        # so limit equality to 2 decimal digit. it would be enough for small distances (gnss is 40hz)
        np.testing.assert_array_almost_equal(expected_distance, distance, decimal=2)

    def test_get_velocities(self):
        # decreasing step from default to allow more precise numerical differentiation (using basic technique for
        # performance)
        trajectory_generator = CircularTrajectoryGenerator(max_time=1, time_step=1e-4)
        # get trajectory from trajectory generator
        trajectory = trajectory_generator.trajectory
        times = trajectory_generator.times
        # call method to test
        velocities = get_velocities(times, trajectory, win_size=1)
        # set initial speed
        velocities[1, 0] = trajectory_generator.initial_tangential_speed
        # check result of method to test is equal to analytical velocities
        np.testing.assert_array_almost_equal(trajectory_generator.get_analytical_velocities()[:-1, :-1],
                                             velocities[:, :-1],
                                             decimal=4)

    def test_get_accelerations(self):
        # decreasing step from default to allow more precise numerical differentiation (using basic technique for
        # performance)
        trajectory_generator = CircularTrajectoryGenerator(max_time=1, time_step=1e-4)
        # remove last element because get_accelerations() cant evaluate it
        velocities = trajectory_generator.get_analytical_velocities()[:-1]
        times = trajectory_generator.times
        # call method to test
        accelerations = get_accelerations(times, velocities, win_size=1)
        # check result of method to test is equal to analytical accelerations
        np.testing.assert_array_almost_equal(trajectory_generator.get_analytical_accelerations()[:-1, :-1],
                                             accelerations[:, :-1],
                                             decimal=4)

    def test_align_to_world(self):
        # create a basic trajectory of a point traveling on x axis
        trajectory = np.vstack((
            np.arange(1, 101),
            np.zeros(100),
            np.zeros(100),
        ))
        # but the point should travel on y axis aligned to world
        world_aligned_trajectory = np.vstack((
            np.zeros(100),
            np.arange(1, 101),
            np.zeros(100)
        ))
        # fake angular positions, not interested in testing this now
        angular_positions = np.vstack((np.full(100, 1),
                                       np.zeros((3, 100))))
        # basic stationary time, the point is never stationary
        motion_time = 50
        # call method to test
        rotate_trajectory = align_to_world(world_aligned_trajectory, trajectory, motion_time)
        # check if rotated trajectory is aligned to world
        np.testing.assert_array_almost_equal(rotate_trajectory, world_aligned_trajectory)
