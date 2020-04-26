"""
Circular trajectory with constant acceleration along z-axis.
Similar to a spring that stretches upward.
Useful for testing numerical integration and quaternions
but doesn't currently provide object rotation.

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
from quaternion import quaternion
from numpy import sin, cos

from BaseTrajectoryGenerator import BaseTrajectoryGenerator
from plots_scripts.plot_utils import plot_vectors


class SpringTrajectoryGenerator(BaseTrajectoryGenerator):
    """
    Create a trajectory and provide accelerations of the motion along it.
    Useful for check quality of numerical integration methods against analytical trajectory.
    Provides a method to do that.
    """

    def __init__(self):
        super().__init__(time_step=0.1)
        """Creates TrajectoryGenerator object"""
        self.v0x = 0  # initial linear velocity
        self.ax = 0.1  # linear acceleration
        self.wz = 0.1  # z angular velocity
        #  point position with respect to origin
        self.start_position = np.array([1, 0, 0])

        def rcm(t):
            """Linear position at time t

            linear uniform accelerated motion along z
            """
            x0 = 0  # initial position
            return np.array([
                0,
                0,
                x0 + self.v0x * t + 1 / 2 * self.ax * t ** 2
            ])

        def thetacm(t):
            """ Angular position at time t

            uniform circular motion around z"""
            return np.array([
                0,
                0,
                self.wz * t
            ])

        # position in all times of linear uniform accelerated motion along z
        r = np.array([rcm(ti) for ti in self.times]).T
        # angular position in all times
        self.th = np.array([thetacm(ti) for ti in self.times])
        # array of quaternion angular positions
        thq = np.array([np.exp(quaternion(*thetai) / 2) for thetai in self.th])
        # get successive rotations of initial point
        r1 = np.array([(tq * quaternion(*self.start_position) * ~tq).components[1:4] for tq in thq])
        # add vertical offset to positions
        self.trajectory = r + r1.T
        # save angular position function as object attribute to future calls
        self.angular_position = thetacm

    def get_analytical_accelerations(self):
        """ Returns 3xn numpy array describing motion accelerations

        Those acceleration are analytical calculated and aren't susceptible to errors
        """
        # create empty numpy array for accelerations
        accelerations = np.zeros((3, len(self.times)))
        # radial accelerations is equal to angular velocity^2 / radius but radius is unitary is this trajectory
        radial_acceleration = self.wz ** 2
        # decompose radial accelerations in x and y components
        accelerations[0, :] = radial_acceleration * -cos(self.th[:, 2])
        accelerations[1, :] = radial_acceleration * -sin(self.th[:, 2])
        # accelerations along x axis is constant
        accelerations[2, :] = self.ax
        return accelerations

    def get_analytical_velocities(self):
        """ Returns 3xn numpy array describing motion velocities

        Those velocities are analytical calculated and aren't susceptible to errors
        """
        # create empty numpy array for accelerations
        velocities = np.zeros((3, len(self.times)))
        # tangential velocity is angular velocity multiplied by radius but radius is one
        vt = self.wz
        # decompose tangential velocity in x and y components
        velocities[0, :] = vt * -sin(self.th[:, 2])
        velocities[1, :] = vt * cos(self.th[:, 2])
        # linear velocity along z axis
        velocities[2, :] = self.v0x + self.ax * self.times
        return velocities

    def get_numerical_derived_accelerations(self):
        """ Returns new array of times and a 3xn numpy array of accelerations derived numerically from trajectory"""
        # calculate numerical 2° order derivative and return it
        return np.gradient(np.gradient(self.trajectory,axis=1),axis=1)

    def get_start_velocity(self):
        """return 3x1 numpy array describing motion initial position"""
        # uniform circular motion have a start velocity of omega
        # TODO generate from start position and rotation direction
        return np.array([0, self.wz, 0])

    def check_trajectory(self, external_trajectory):
        """
        Check an external generated trajectory against the internally one

        :param external_trajectory: 3xn numpy array describing trajectory
        :return: 1xn numpy array of median error along all axis
        """
        # Create empty array for error measure
        error = np.zeros((3, external_trajectory.shape[1]))
        # loop over external trajectory
        for i, external_x in enumerate(external_trajectory.T):
            # get trajectory coordinates at step i
            real_x = self.trajectory[:, i]
            # calculate difference from external trajectory
            error[:, i] = abs(real_x - external_x)
        # return average error on all axis
        return error.mean(axis=0)

    def plot_trajectory(self):
        """ Plots analytical trajectory"""
        plot_vectors([self.trajectory], ["analytical trajectory"])
