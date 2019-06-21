"""
Plot integrated trajectory by trapezoid and simpson integration techniques.

Thesis:show that even if trapezoid is less precise, with small interval the difference in unnoticeable

Conclusion: using weighted average the difference is noticeable because error accumulates through time.

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
    sign_inversion_is_necessary, get_stationary_times
from src.gnss_utils import get_positions, get_velocities, get_initial_angular_position, get_first_motion_time
from src.input_manager import parse_input, InputType
from src.integrate import cumulative_integrate, trapz_integrate_delta, simps_integrate_delta
from src import rotate_accelerations, align_to_world
from plots_scripts.plot_utils import plot_vectors


import matplotlib.pyplot as plt

if __name__ == '__main__':
    window_size = 20
    path = '../tests/test_fixtures/parking.tsv'

    # currently default format is unmodified fullinertial but other formats are / will be supported
    times, coordinates, altitudes, gps_speed, heading, accelerations, angular_velocities = parse_input(path, [
        InputType.UNMOD_FULLINERTIAL])

    converts_measurement_units(accelerations, angular_velocities, gps_speed, coordinates)

    # get positions from GNSS data
    gnss_positions, headings = get_positions(coordinates, altitudes)

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
    stationary_times = get_stationary_times(gps_speed)

    # clear gyroscope drift
    angular_velocities = clear_gyro_drift(angular_velocities, stationary_times)
    # set times start to 0
    normalize_timestamp(times)

    # correct z-axis alignment
    accelerations, angular_velocities = correct_z_orientation(accelerations, angular_velocities, stationary_times)

    # remove g
    accelerations[2] -= accelerations[2, stationary_times[0][0]:stationary_times[0][-1]].mean()

    # convert to laboratory frame of reference
    motion_time = get_first_motion_time(stationary_times, gnss_positions)
    initial_angular_position = get_initial_angular_position(gnss_positions, motion_time)

    # convert to laboratory frame of reference
    accelerations, angular_positions = rotate_accelerations(times, accelerations, angular_velocities, heading,
                                                            initial_angular_position)

    # rotate to align y to north, x to east
    accelerations = align_to_world(gnss_positions, accelerations, motion_time)

    initial_speed = np.array([[gps_speed[0]], [0], [0]])
    # integrate acceleration with gss velocities correction
    import time
    start_time = time.time()
    correct_velocities_simps = cumulative_integrate(times, accelerations, initial_speed, simps_integrate_delta)
    print("time integrating velocities simps " + str(time.time()-start_time))
    start_time = time.time()
    correct_velocities_trapz = cumulative_integrate(times, accelerations, initial_speed, trapz_integrate_delta)
    print("time integrating velocities trapz " + str(time.time()-start_time))

    correct_position_simps = cumulative_integrate(times, correct_velocities_simps)
    correct_position_trapz = cumulative_integrate(times,correct_velocities_trapz)
    plt.plot(correct_position_simps[0],label='PaIS')
    plt.plot(correct_position_trapz[0],label='Trapezoid')
    plt.ylabel('meters')
    plt.xlabel('seconds')
    plt.legend()
    plt.show()