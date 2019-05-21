#!/usr/bin/env python
"""
Plot integrated distance traveled
This is abstract from rotation problems.

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

import matplotlib.pyplot as plt
import numpy as np

from src.clean_data_utils import converts_measurement_units, reduce_disturbance, \
    clear_gyro_drift, correct_z_orientation, normalize_timestamp, \
    get_stationary_times, truncate_if_crash
from src.gnss_utils import get_positions, get_velocities, get_accelerations
from src.input_manager import parse_input, InputType
from src.integrate import cumulative_integrate

if __name__ == '__main__':
    window_size = 20

    # for benchmarking
    import time

    start_time = time.time()

    #input path
    parking_fullinertial_unmod = 'tests/test_fixtures/parking.tsv'
    crash = False
    times, coordinates, altitudes, gps_speed, heading, accelerations, angular_velocities = parse_input(
        parking_fullinertial_unmod, [InputType.UNMOD_FULLINERTIAL])
    converts_measurement_units(accelerations, angular_velocities, gps_speed, coordinates, heading)
    period = times[1] - times[0]

    times, gps_speed, accelerations, angular_velocities, coordinates, heading = \
        truncate_if_crash(crash, times, gps_speed, accelerations, angular_velocities, coordinates, heading)

    # get positions from GNSS data
    gnss_positions, headings_2 = get_positions(coordinates, altitudes)

    gnss_distance = np.linalg.norm(np.array([gnss_positions[:, i] - gnss_positions[:, i - 1]
                                   for i, x in enumerate(gnss_positions[:, 1:].T, 1)]), axis=1).cumsum()
    # insert initial distance
    gnss_distance = np.insert(gnss_distance, 0, 0)
    # reshape to 1xn shape
    gnss_distance = np.reshape(gnss_distance, (1, len(gnss_distance)))
    real_velocities = get_velocities(times, gnss_positions)
    real_acc = get_accelerations(times, real_velocities)

    # scalar speed from GNSS position (better than from dataset because avoids Kalmar filter)
    real_velocities_module = np.linalg.norm(real_velocities, axis=0)

    stationary_times = get_stationary_times(gps_speed,period)
    # reduce accelerations disturbance
    times, accelerations = reduce_disturbance(times, accelerations, window_size)
    # reduce angular velocities disturbance
    _, angular_velocities = reduce_disturbance(times, angular_velocities, window_size)
    # truncate other array to match length of acc, thetas, times array
    real_acc = real_acc[:, round(window_size / 2):-round(window_size / 2)]
    real_velocities = real_velocities[:, round(window_size / 2):-round(window_size / 2)]
    gnss_positions = gnss_positions[:, round(window_size / 2):-round(window_size / 2)]
    gnss_distance = gnss_distance[:, round(window_size / 2):-round(window_size / 2)]

    # clear gyroscope drift
    angular_velocities = clear_gyro_drift(angular_velocities, stationary_times)
    # set times start to 0
    normalize_timestamp(times)

    # correct z-axis alignment
    accelerations, angular_velocities = correct_z_orientation(accelerations, angular_velocities, stationary_times)
    # remove g
    accelerations[2] -= accelerations[2, stationary_times[0][0]:stationary_times[0][-1]].mean()

    accelerations_module = np.linalg.norm(accelerations, axis=0)
    accelerations_module = np.reshape(accelerations_module, (1, len(accelerations_module)))

    real_acc_module = np.linalg.norm(real_acc, axis=0)

    real_velocities_module = np.reshape(real_velocities_module, (1, len(real_velocities_module)))

    # integrate acceleration with gss velocities correction
    correct_velocities_module = cumulative_integrate(times, accelerations_module, real_velocities_module[0, 0],
                                                     adjust_data=real_velocities_module,
                                                     adjust_frequency=1)

    correct_distance = cumulative_integrate(times, correct_velocities_module, adjust_data=gnss_distance,
                                            adjust_frequency=1)

    print("Execution time: %s seconds" % (time.time() - start_time))

    # plotting

    fig1, ax1 = plt.subplots()
    ax1.plot(real_acc_module, label='acc gnss')
    ax1.plot(accelerations_module.T, label='acc sensor')
    ax1.legend()

    fig, ax2 = plt.subplots()
    ax2.plot(real_velocities_module.T, label='speed gss')
    ax2.plot(correct_velocities_module.T, label='speed int')
    ax2.legend()

    fig, ax2 = plt.subplots()
    ax2.plot(gnss_distance.T, label='distance gnss')
    ax2.plot(correct_distance.T, label='distance int')
    ax2.legend()

    plt.show()
