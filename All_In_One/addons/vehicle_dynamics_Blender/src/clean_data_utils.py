"""
Various routines for cleaning input data.
The need of some of these functions is because of the input data format.
See <https://github.com/physycom/file_format_specifications/blob/master/formati_file.md#formato-dati-inerziali>
The need of some other functions is sensor brand and sensor installation dependent.

The purpose of all this module is get inertial data:
- accelerations on m/s^2
- angular velocities in radians/s
- more precise possible inertial measurements in the car's reference frame

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
import math
from quaternion import quaternion
from src.constants import g, kmh, degree_to_radians, pi

crash_acceleration_treshold = 15

def parse_input(df):
    """ Transform single dataframe to multiple numpy array each representing different physic quantity

    :param df: Pandas dataframe
    :return: 4 numpy array: 1xn timestamp, 1xn gps speed,
    3xn accelerations and 3xn angular velocities
    """
    accelerations = df[['ax', 'ay', 'az']].values.T
    angular_velocities = df[['gx', 'gy', 'gz']].values.T
    times = df['timestamp'].values.T
    gps_speed = df['speed'].values.T
    return times, gps_speed, accelerations, angular_velocities

def get_stationary_times(gps_speed, period, crash_time=None):
    """ Returns list of index where the gps speed is near zero

    :param gps_speed: 1xn numpy array of gps speed in m/s
    :return: list of tuples, each one with start and final timestamp of a stationary time index
    """

    speed_threshold = 0.05  # 0.2 m/s
    if crash_time is not None:
        # truncate speeds after crash time because acceleremeter data is unreliable
        # so the routines that use stationary_time don't work on data after crash
        gps_speed = gps_speed[:crash_time]
    stationary_times = []
    # repeat until at least a stationary time is found
    while (len(stationary_times)==0):
        # at least 3 seconds stationary
        min_stationary_time_length = round(1/period)
        # Find times where gps speed is inside threshold
        # Didn't use np.nonzero because i needed contiguous slices and also check on length of slice
        boolean_vect = np.bitwise_and(gps_speed > -speed_threshold, gps_speed < speed_threshold)
        # set a value that can't exist as index
        first_true = math.inf
        last_true = math.inf
        for i, x in enumerate(boolean_vect):
            if first_true == math.inf and x is np.bool_(True):
                # enter stationary time mode
                first_true = i
            if first_true != math.inf and x is np.bool_(True):
                # add a timestamp to slice
                last_true = i
            if first_true != math.inf and last_true != math.inf and x is np.bool_(False):
                # end slice
                # if slice length is greater than a minimum length
                if last_true - first_true > min_stationary_time_length:
                    # add slice to stationary times list
                    stationary_times.append((first_true, last_true))
                # reset
                first_true = math.inf
                last_true = math.inf
        # handle case where stationary times not ends before data ends
        if first_true != math.inf and last_true != math.inf and (last_true - first_true) > min_stationary_time_length:
            stationary_times.append((first_true, last_true))
        # TODO raise exception if there are no stationary times
        # increase speed threshold in case stationary times are not found
        speed_threshold += 0.01
    return stationary_times

def truncate_if_crash(crash, times, gps_speed, accelerations, angular_velocities, coordinates=None, heading=None):
    """
    Removed unreliable data after a crash
    If crash==True then search for a acceleration over a certain treshold, remove records after that
    Coordinates and heading are optional, for supporting both using gps data and not.
    Returning also first crash time if present. If not present crash time is null

    :param crash: bool
    :param times: 1xn numpy array
    :param gps_speed: 1xn numpy array
    :param accelerations: 3xn numpy array
    :param angular_velocities: 3xn numpy array
    :param coordinates: 2xn numpy array
    :param heading: 1xn numpy array
    :return:times, gps_speed, accelerations, angular_velocities, coordinates, [coordinates, heading, crash_time]
    """
    crashes = np.argwhere(np.linalg.norm(accelerations, axis=0) > crash_acceleration_treshold)
    crash_1 = None
    if (len(crashes) > 1):
        crash_1 = crashes[0][0]
        if crash:
            accelerations = accelerations[:, :crash_1]
            angular_velocities = angular_velocities[:, :crash_1]
            gps_speed = gps_speed[:crash_1]
            times = times[:crash_1]
            if coordinates is not None:
                coordinates = coordinates[:,:crash_1]
            if heading is not None:
                heading = heading[:crash_1]
    return times, gps_speed, accelerations, angular_velocities, coordinates, heading, crash_1

def converts_measurement_units(accelerations, angular_velocities, gps_speed=None, coordinates=None, heading=None):
    """ Convert physics quantity measurement unit

    Convert accelerations from g units to m/s^2
    coordinates from degrees to radians
    angular velocities from degrees/s to radians/s
    gps speed from km/h to m/s

    Applies inplace

    :param gps_speed: 1xn array of gps speed in km/h
    :param accelerations: 3xn array of acceleration in g unit
    :param angular_velocities: 3xn array of angular velocities in degrees/s
    :param coordinates: optional 2xn array of coordinates in geographic coordinate system
    """
    accelerations *= g
    if coordinates is not None:
        # multiply to degree to radians constant
        coordinates *= degree_to_radians
    # multiply to degree to radians constant
    angular_velocities *= degree_to_radians
    if gps_speed is not None:
        # multiply to km/h -> m/s constant
        gps_speed *= kmh
    if heading is not None:
        heading *= degree_to_radians


def normalize_timestamp(times):
    """ Normalize timestamp to make it begin from time 0

    :param times: 1xn numpy array of timestamps
    """
    times -= times[0]


def sign_inversion_is_necessary(velocities):
    """ Check if sign of input vector must be inverted by manufacture convention

    This function assumes that speed has been converted to m/s

    :param velocities: 3xn numpy array of velocities
    """
    speed_threshold = -4
    return any(velocities[0] < speed_threshold)


def clear_gyro_drift(angular_velocities, stationary_times):
    """ Remove gyroscope natural offset

    This function assumes the car is stationary in the first 10000 measurements

    :param angular_velocities: 3xn numpy array of angular velocities
    :param stationary_times: list of tuples (start,end)
    """

    # get offset on first stationary time
    main_offset = angular_velocities[:, stationary_times[0][0]:stationary_times[0][1]].mean(axis=1)
    # remove on all data
    angular_velocities = (angular_velocities.T - main_offset).T
    # for remaining stationary times
    for stationary_time in stationary_times[1:]:
        start = stationary_time[0]
        end = stationary_time[1]
        # offset can now be changed by heat, remove only from start time of stationary time to end of data
        offset = angular_velocities[:, start:end].mean(axis=1)
        angular_velocities[:, start:] = (angular_velocities[:, start:].T - offset).T
    return angular_velocities


def reduce_disturbance(times, vectors, window_dimension=100):
    """ Reduce data disturbance with a moving average

    The length of the window is calculated internally in function of vector length
    Some values at the beginning of the array will be dropped.

    :param times: 1xn numpy array of timestamps
    :param vectors: 3xn numpy array of whatever numeric
    :param window_dimension: int rolling average window dimension
    :return 2 numpy vector: new times and new vector
    """

    # iterating moving average is the same of weighting it like a gaussian
    for j in range(10):
        # overwrite dataframe with its moving average
        array = np.zeros(vectors.shape)
        for i in range (0,window_dimension):
            sliced_vec = vectors[:,i:]
            array[:,:sliced_vec.shape[1]] += sliced_vec
        # centered moving average
        array[:,round(window_dimension/2):] /= window_dimension
    # now there ara 0:windows_dimension nan rows at the beginning
    # drop these rows
    new_low_range = round(window_dimension/2)
    #new_low_range = math.floor(window_dimension / 2)
    new_upper_range = math.floor(vectors.shape[1] - round(window_dimension/2))
    # TODO change drop offset
    times = times[new_low_range:new_upper_range]
    vectors = array[:,new_low_range:new_upper_range]
    return times, vectors

def correct_z_orientation(accelerations, angular_velocities, stationary_times):
    """ Use gravity vector direction to align reference frame to correct z-axis

    Assumes the car is stationary for the first 10000 times and the gravity haven't been removed

    :param accelerations: 3xn numpy array angular velocities
    :param angular_velocities: 3xn numpy array angular velocities
    :param stationary_times: list of tuples (start,end)
    :return: numpy arrays: rotated accelerations, rotated angular velocities
    """

    # get value of g in all stationary times
    g = np.mean(np.concatenate(
        [accelerations[:,stationary_time[0]:stationary_time[1]] for stationary_time in stationary_times],axis=1),axis=1)
    def align_from_g_vector(accelerations, angular_velocities, g):
        g_norm = np.linalg.norm(g)
        u = np.cross(g, (0, 0, 1))
        # rotation axis
        u_unit = u / np.linalg.norm(u)
        # rotate angle
        theta = np.arccos(np.dot(g, (0, 0, 1)) / g_norm)
        print("rotating vectors of "+str(np.rad2deg(theta))+" degrees align to z")
        rotator = np.exp(quaternion(*(theta * u_unit)) / 2)
        rotated_accelerations = np.array(
            [(rotator * quaternion(*acceleration_vector) * ~rotator).components[1:]
             for acceleration_vector in accelerations.T])
        rotated_angular_velocities = np.array(
            [(rotator * quaternion(*angular_velocity) * ~rotator).components[1:]
             for angular_velocity in angular_velocities.T])
        return rotated_accelerations.T, rotated_angular_velocities.T

    accelerations, angular_velocities = align_from_g_vector(accelerations, angular_velocities, g)

    # for the remaining stationary times
    for stationary_time in stationary_times[1:]:
        # calculate bad align angle
        g = accelerations[:, stationary_time[0]:stationary_time[1]].mean(axis=1)
        bad_align_angle = np.arccos(np.dot(g, (0, 0, 1)) / np.linalg.norm(g))
        # if the bad align angle is greater than 2 degrees
        if bad_align_angle > np.deg2rad(10):
            # print a warning
            import warnings
            message = " \n Found additional bad z axis of {} degrees alignment at time {} , " \
                      "realigning from now  \n".format(np.rad2deg(bad_align_angle), stationary_time[0])
            warnings.warn(message)
            # re-align
            accelerations, angular_velocities = align_from_g_vector(accelerations, angular_velocities, g)
    return accelerations, angular_velocities
