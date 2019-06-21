"""
Entry point to src module functionalities.

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

from src.clean_data_utils import converts_measurement_units, reduce_disturbance, \
    clear_gyro_drift, correct_z_orientation, normalize_timestamp, \
    sign_inversion_is_necessary, get_stationary_times, truncate_if_crash
from src.gnss_utils import get_positions, get_velocities, get_initial_angular_position, get_first_motion_time
from src.input_manager import parse_input, InputType
from src.integrate import cumulative_integrate
from src.rotations import rotate_accelerations, align_to_world

def get_trajectory_from_path(path,use_gps=True,crash=False):
    """
    parse input file from path, clean data and integrate positions

    :param path: string input file
    :return: 3 numpy array: 3xn position, 1xn times, 4xn angular position as quaternions
    """

    if (use_gps):
        print("using GPS")
        # currently default format is unmodified fullinertial but other formats are / will be supported
        times, coordinates, altitudes, gps_speed, heading, accelerations, angular_velocities = parse_input(path, [
            InputType.UNMOD_FULLINERTIAL])

        period = times[1]-times[0]

        converts_measurement_units(accelerations, angular_velocities, gps_speed, coordinates, heading)

        times, gps_speed, accelerations, angular_velocities, coordinates, heading, crash_time = \
            truncate_if_crash(crash, times, gps_speed, accelerations, angular_velocities, coordinates, heading)

        # get positions from GNSS data
        gnss_positions, headings_2 = get_positions(coordinates, altitudes)

        window_size = 20

        # reduce accelerations disturbance
        times, accelerations = reduce_disturbance(times, accelerations, window_size)
        # reduce angular velocities disturbance
        _, angular_velocities = reduce_disturbance(times, angular_velocities, window_size)
        # truncate other array to match length of acc, thetas, times array
        gnss_positions = gnss_positions[:, round(window_size / 2):-round(window_size / 2)]

        # with "final" times now get velocities and
        real_velocities = get_velocities(times, gnss_positions)
        # scalar speed from GNSS position (better than from dataset because avoids Kalmar filter)
        real_speeds = np.linalg.norm(real_velocities, axis=0)

        # get time windows where vehicle is stationary
        stationary_times = get_stationary_times(gps_speed,period,crash_time)

        # clear gyroscope drift
        angular_velocities = clear_gyro_drift(angular_velocities, stationary_times)
        # set times start to 0
        normalize_timestamp(times)

        # correct z-axis alignment
        accelerations, angular_velocities = correct_z_orientation(accelerations, angular_velocities, stationary_times)

        # remove g
        accelerations[2] -= accelerations[2, stationary_times[0][0]:stationary_times[0][-1]].mean()

        motion_time = get_first_motion_time(stationary_times,gnss_positions)
        initial_angular_position = get_initial_angular_position(gnss_positions,motion_time)

        # convert to laboratory frame of reference
        accelerations, angular_positions = rotate_accelerations(times, accelerations, angular_velocities, heading, initial_angular_position)

        # rotate to align y to north, x to east
        accelerations = align_to_world(gnss_positions, accelerations, motion_time)
        # angular position doesn't need to be aligned to world if starting angular position is already aligned and following
        # angular positions are calculated from that

        initial_speed = np.array([[gps_speed[0]], [0], [0]])
        # integrate acceleration with gss velocities correction
        correct_velocities = cumulative_integrate(times, accelerations, initial_speed, adjust_data=real_velocities, adjust_frequency=1)

        if sign_inversion_is_necessary(correct_velocities):
            accelerations *= -1
            correct_velocities *= -1

        correct_position = cumulative_integrate(times, correct_velocities, adjust_data=real_velocities, adjust_frequency=1)

        return correct_position, times, angular_positions

    else:
        print("not using GPS")
        # currently default format is unmodified fullinertial but other formats are / will be supported
        times, _, _, gps_speed, _, accelerations, angular_velocities = parse_input(path, [
            InputType.UNMOD_FULLINERTIAL])

        period = times[1] - times[0]

        converts_measurement_units(accelerations, angular_velocities, gps_speed)

        times, gps_speed, accelerations, angular_velocities, _, _ , crash_time = \
            truncate_if_crash(crash, times, gps_speed, accelerations, angular_velocities)

        # reduce accelerations disturbance
        times, accelerations = reduce_disturbance(times, accelerations)
        # reduce angular velocities disturbance
        _, angular_velocities = reduce_disturbance(times, angular_velocities)

        # get time windows where vehicle is stationary
        stationary_times = get_stationary_times(gps_speed, period, crash_time)

        # clear gyroscope drift
        angular_velocities = clear_gyro_drift(angular_velocities, stationary_times)
        # set times start to 0
        normalize_timestamp(times)

        # correct z-axis alignment
        accelerations, angular_velocities = correct_z_orientation(accelerations, angular_velocities, stationary_times)

        # remove g
        accelerations[2] -= accelerations[2, stationary_times[0][0]:stationary_times[0][-1]].mean()

        # convert to laboratory frame of reference
        accelerations, angular_positions = rotate_accelerations(times, accelerations, angular_velocities)

        initial_speed = np.array([[gps_speed[0]], [0], [0]])
        # integrate acceleration with gss velocities correction
        correct_velocities = cumulative_integrate(times, accelerations, initial_speed)

        if sign_inversion_is_necessary(correct_velocities):
            accelerations *= -1
            correct_velocities *= -1

        correct_position = cumulative_integrate(times, correct_velocities)

        return correct_position, times, angular_positions