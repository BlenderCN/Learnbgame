"""
This unit test checks numerical integration functions from integrate.py with TrajectoryGenerator.

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
from CircularTrajectoryGenerator import CircularTrajectoryGenerator
from src.integrate import cumulative_integrate, quad_integrate, trapz_integrate
from src.constants import pi
from src import rotate_accelerations


def integrate_and_test(method):
    """ Integrate trajectory accelerations and return errors compared to analytical trajectory

    :param method: callable ``f(times, vectors, start)``
        integration method to integrate vectors over times
    :return 1xn numpy array of absolute errors
    """
    integrated_trajectory = get_integrated_trajectory(method)
    # check integrated trajectory
    error = SpringTrajectoryGenerator().check_trajectory(integrated_trajectory)
    return error


def get_integrated_trajectory(method):
    """ Return TrajectoryGenerator trajectory integrated with given methods

    :param method callable ``f(times, vectors, start)``
        integration method to integrate vectors over times
    """

    # create trajectory
    trajectory = SpringTrajectoryGenerator()
    # get motion timestamps
    times = trajectory.times
    start_position = trajectory.start_position
    start_velocity = trajectory.get_start_velocity()
    # get analytical accelerations
    accelerations = trajectory.get_analytical_accelerations()
    # numerical integrate acceleration to get velocities
    velocities = method(times, accelerations, start_velocity)
    # numerical integrate velocities to get trajectory
    integrated_trajectory = method(times, velocities, start_position)
    return integrated_trajectory


class IntegrationTest(TestCase):

    def test_trajectory_generator(self):
        error = integrate_and_test(cumulative_integrate)
        self.assertLess(error.mean(), 0.05)

    def test_simple_integrate(self):
        """ Simple integration methods test with trigonometry functions"""

        # TODO remove when trajectory will be generalized
        times = np.arange(start=0, stop=100, step=1e-2)
        sinus = np.array([np.sin(x) for x in times])
        cosines = np.array([np.cos(x) for x in times])
        vector = np.vstack((sinus, cosines, -sinus))
        # for each integration method
        for method in [quad_integrate, trapz_integrate, cumulative_integrate]:
            # numerical integrate with selected method
            integrated = method(times, vector, initial=[-1, 0, 1])
            # calculate absolute error
            error = abs(np.array(
                [integrated[0] - (-cosines),
                 integrated[1] - sinus,
                 integrated[2] - cosines]
            ))
            # check error is below a threshold
            self.assertTrue(error.mean() < 0.005)


class RotationTest(TestCase):

    def test_rotation(self):
        # 90°/s around z
        angular_velocity = np.array([
            [0, 0, 0],
            [0, 0, 0],
            [pi / 2, pi / 2, pi / 2]])
        times = np.array([0, 1, 2])
        # unitary x vector
        vectors_to_rotate = np.array([
            [1, 1, 1],
            [0, 0, 0],
            [0, 0, 0]])
        headings = None
        # test also initial angular position with different angle for testing quaternion product order correctness
        vectors_to_rotate, angular_velocity = \
            rotate_accelerations(times, vectors_to_rotate, angular_velocity, headings, np.array([0, 0, pi]))
        expected_result = np.array([
            [-1, 0, 1],
            [0, -1, 0],
            [0, 0, 0]])
        np.testing.assert_array_almost_equal(vectors_to_rotate, expected_result)

    def test_local_to_lab(self):
        """ Tests conversion from local acceleration reference frame to laboratory reference frame
        by rotation using integrated angular velocity. Tests both integrator and rotator.
        """

        # generated Trajectory Generator object
        circular_tra = CircularTrajectoryGenerator()
        # get trajectory times
        times = circular_tra.times
        # get local accelerations
        accelerations = circular_tra.get_analytical_local_accelerations()
        # get angular velocities
        angular_velocities = circular_tra.get_angular_velocities()
        heading = None
        # convert to laboratory frame of reference
        accelerations, angular_positions = rotate_accelerations(times, accelerations, angular_velocities,heading,
                                                                initial_angular_position=[0, 0, np.pi / 2])
        initial_speed = np.array([[0], [circular_tra.initial_tangential_speed], [0]])
        velocities = cumulative_integrate(times, accelerations, initial_speed)
        initial_position = np.array([[1], [0], [0]])
        positions = cumulative_integrate(times, velocities, initial_position)
        # if the integrated trajectory and the analytical one are equal thant both the integrator and the rotator works
        np.testing.assert_array_almost_equal(positions, circular_tra.trajectory, decimal=3)
