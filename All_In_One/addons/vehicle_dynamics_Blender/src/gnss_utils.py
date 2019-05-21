"""
Various routines to handle GNSS data

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

from math import cos


import numpy as np


def get_positions(coordinates, altitudes):
    """
    Convert gss data from geographic coordinate system to cartesian

    :param coordinates: 2xn numpy array of coordinates (lat,lon)
    :param altitudes: 1xn numpy array of altitudes
    :return: 2 numpy array: 3xn numpy array of position in cartesian system 1xn heading as array of angles
    """
    earth_radius = 6371000
    # create empty array for final positions
    positions = np.zeros((3, coordinates.shape[1]))
    headings = np.zeros(coordinates.shape[1])
    # current position
    current = np.array([coordinates[0, 0], coordinates[1, 0], altitudes[0]])
    # iterate skipping first position that is zero
    for i, gnss_data in enumerate(zip(coordinates[:, 1:].T, altitudes[1:]), start=1):
        # get data from zipped tuple
        lat = gnss_data[0][0]
        lon = gnss_data[0][1]
        alt = gnss_data[1]
        # current is the previous record
        # use relationship between central angle and arc to calculate delta lat
        delta_lat = earth_radius * (lat - current[0])
        # use same formula but with earth horizontal radius moved to latitude
        delta_lon = earth_radius * cos(lat) * (lon - current[1])
        delta_alt = alt - current[2]
        headings[i] = np.arctan2(delta_lat, delta_lon)
        # update current
        current[0] = lat
        current[1] = lon
        current[2] = alt
        # set position at step i
        positions[0, i] = positions[0, i - 1] + delta_lon
        positions[1, i] = positions[1, i - 1] + delta_lat
        positions[2, i] = positions[2, i - 1] + delta_alt
    return positions, headings


def get_velocities(times, positions, win_size=1):
    """
    Get array of speeds from position in cartesian system

    Increasing windows size improve performance but reduce precision.

    :param times: 1xn numpy array of timestamp
    :param positions: 3xn numpy array of position in cartesian system
    :param win_size: int how often calculate velocity
    :return: 2xn velocities numpy array
    """
    # TODO this is very basic numerical differentiation, can be improved
    # remove altitude because it's unreliable
    positions = np.delete(positions, 2, axis=0)
    # create array
    velocities = np.zeros((2, positions.shape[1]))
    # iterate starting from win size until end of array, with win_size step
    for i in range(win_size, positions.shape[1], win_size):
        delta_x = positions[0, i] - positions[0, i - win_size]
        delta_y = positions[1, i] - positions[1, i - win_size]
        delta_t = times[i] - times[i - win_size]
        velocities[0, i - win_size:i] = delta_x / delta_t
        velocities[1, i - win_size:i] = delta_y / delta_t
    return velocities


def get_accelerations(times, velocities, win_size=1):
    """
    Get array of acceleration from velocities in cartesian system

    :param times: 1xn numpy array of timestamp
    :param velocities: 2xn numpy array of velocities in 2d cartesian system
    :param win_size: int how often calculate acceleration
    :return: 2xn numpy array of accelerations
    """

    accelerations = np.zeros((2, velocities.shape[1]))
    for i in range(win_size, velocities.shape[1], win_size):
        delta_x = velocities[0, i] - velocities[0, i - win_size]
        delta_y = velocities[1, i] - velocities[1, i - win_size]
        delta_t = times[i] - times[i - win_size]
        accelerations[0, i - win_size:i] = delta_x / delta_t
        accelerations[1, i - win_size:i] = delta_y / delta_t
    return accelerations


def get_first_motion_time(stationary_times,positions):
    """
    Get first motion time enough distant from start position

    :param stationary_times: list of 2-tuples
    :return: 2 int: start and end of first motion
    """

    # not in stationary time
    # distance must be at least 10 meters
    # iterate until a motion time (not stationary) is found
    stationary_time_index = 0
    i = 0
    # find the first 100 records in motion times
    position_len = positions.shape[1]
    while i < position_len:
        if i==stationary_times[stationary_time_index][0]:
            # jump to next motion time
            i = stationary_times[stationary_time_index][1]
            if (stationary_time_index<len(stationary_times)-1):
                stationary_time_index += 1
        if np.linalg.norm(positions[:-1, i]) > 10:
            break
        i += 1
    motion_time = i
    return motion_time


def get_initial_angular_position(gnss_position, motion_time):
    """
    Get initial angular position in axis-angle notation

    :param gnss_position: 3xn numpy array. positions from gnss data
    :param stationary_times: list of 2-tuples
    :return: initial angular position in axis-angle notation
    """
    angle_gnss = np.arctan2(gnss_position[1,motion_time],gnss_position[0,motion_time])
    print("Initial position is "+str(np.rad2deg(angle_gnss)))
    return np.array([0,0,angle_gnss])