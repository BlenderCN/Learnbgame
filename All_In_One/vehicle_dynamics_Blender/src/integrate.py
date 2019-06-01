"""
This module expose routines to create car path from accelerometer
and gyroscope data by numerical integration.


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

import numpy as np

def quad_integrate(times, vector, initial=np.zeros(3)):
    current = initial
    result_vector = np.zeros((3, vector.shape[1]))
    result_vector[:, 0] = initial
    for i in range(vector.shape[1] - 1):
        dt = times[i + 1] - times[i]
        dv = vector[:, i + 1] * dt
        current = current + dv
        result_vector[:, i + 1] = current
    return result_vector


def trapz_integrate(times, vector, initial=np.zeros(3)):
    current = initial
    result_vector = np.zeros((3, vector.shape[1]))
    result_vector[:, 0] = initial
    for i in range(vector.shape[1] - 1):
        dt = times[i + 1] - times[i]
        dv = ((vector[:, i] + vector[:, i + 1]) * dt) / 2
        current = current + dv
        result_vector[:, i + 1] = current
    return result_vector

def trapz_integrate_delta(times, vector):
    # multiplying by 0.5 faster than dividing by two
    return ((vector[:,:-1] + vector[:,1:]) * (times[1:]-times[:-1])) * 0.5


def simps_integrate_delta(times, vectors):
    """
    Simpson integration with irregularly-spaced data
    Returns delta vector

    Method from paper https://scholarworks.umt.edu/cgi/viewcontent.cgi?article=1319&context=tme
    Works both with even and odd vectors

    :param times: 1xn np array of timestamps
    :param vectors: 3xn np vector to integrate
    :return: 3xn np array vector of deltas
    """

    rows = vectors.shape[0]
    columns = vectors.shape[1]
    # create vector to keep results
    deltas = np.zeros((rows, columns))
    # iterate through vector to integrate
    for j in range(0, columns - 2):
        # create (x_i,y_i) points
        x = times[j:j + 3]
        # 3x3 array
        vector_locals = vectors[:, j:j + 3]
        for i, y in enumerate(vector_locals):
            # create matrix to solve linear system
            matrix = np.array([
                [x[0] ** 2, x[0], 1],
                [x[1] ** 2, x[1], 1],
                [x[2] ** 2, x[2], 1],
            ])
            # solve linear system
            A, B, C = np.linalg.solve(matrix,y)
            # get integral value only of the "first part" of the parabola
            deltas[i, j + 1] = A / 3 * (x[1] ** 3 - x[0] ** 3) + B / 2 * (x[1] ** 2 - x[0] ** 2) + C * (x[1] - x[0])
            if j == columns - 3:
                # fill last element element with already calculated values
                # get integral value of "last part" of the parabola
                deltas[i, j + 2] = A / 3 * (x[2] ** 3 - x[1] ** 3) + B / 2 * (x[2] ** 2 - x[1] ** 2) + C * (x[2] - x[1])
    return deltas

def cumulative_integrate(times, vectors, initial=None, delta_integrate_func = simps_integrate_delta, adjust_data=None, adjust_frequency=None):
    """
    Optional initial data reset with custom frequency

    :param times: 1xn np array of timestamps
    :param vectors: 3xn np vector to integrate
    :param initial: 3x1 np array integration initial value
    :param adjust_data: 3xn numpy array. Data to reset to each adjust frequency times.
    :param adjust_frequency: 3xn numpy array. Frequency of adjust operations.
    :return: 3xn numpy array integrated vectors

    """
    rows = vectors.shape[0]
    columns = vectors.shape[1]
    delta_vectors = delta_integrate_func(times,vectors)
    # create vector to keep results
    result_vectors = np.zeros((rows,columns))
    # save initial in first result position
    result_vectors[:, 0] = np.zeros(rows) if (initial is None) else np.reshape(initial,(1,rows))
    # iterate delta_vector skipping first position
    for i,delta_vector in enumerate(delta_vectors[:,1:].T,1):
        # if adjust is needed
        if adjust_data is not None and adjust_frequency is not None and i % adjust_frequency == 0:
            # reset result vectors
            if rows == 3:
                # do not adjust z-axis (altitude is not reliable)
                result_vectors[:-1, i] = \
                    adjust_data[:-1, i]*0.01 + (result_vectors[:-1, i - 1] + delta_vectors[:-1, i])*0.99
            elif rows == 1:
                result_vectors[0, i] = \
                    adjust_data[0, i]*0.01 + (result_vectors[0, i - 1] + delta_vectors[0, i])*0.99
        else:
            # cumulative sum
            result_vectors[:,i] = result_vectors[:,i-1] + delta_vectors[:,i]
    return result_vectors