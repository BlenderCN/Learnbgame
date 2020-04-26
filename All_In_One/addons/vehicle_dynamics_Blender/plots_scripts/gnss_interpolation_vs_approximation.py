#!/usr/bin/env python
"""
Plots the difference between interpolation the GNSS coordinates and fit a polynomial with leat square method.
Approximation should remove small anomalies.

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
import matplotlib.pyplot as plt

from src.input_manager import parse_input, InputType
from src.clean_data_utils import converts_measurement_units
from src.gnss_utils import get_positions
from plots_scripts.plot_utils import plot_vectors

if __name__ == "__main__":
    # load dataset
    crash_01_dataset = 'tests/test_fixtures/split_log_1321_1322_USB0_unmodified-fullinertial.txt'
    times, coordinates, altitudes, gps_speed, heading, accelerations, angular_velocities = parse_input(
        crash_01_dataset, [InputType.UNMOD_FULLINERTIAL])
    converts_measurement_units(accelerations, angular_velocities, gps_speed, coordinates)
    #get cartesian position from world one
    gnss_positions, headings = get_positions(coordinates, altitudes)
    # creates empty array to fill
    approx_points = np.zeros((2, len(times)))
    # size of step using iterating array
    step = round(len(times)/10)
    for i in range(0,len(times),step):
        # creates local slice of times and positions
        local_times = times[i:i+step]
        local_positions = gnss_positions[0:2,i:i+step]
        # calculate coefficients of polynomial approximation for x-coordinates
        poly_x = np.polyfit(local_times,local_positions[0],deg=1)
        # calculate coefficients of polynomial approximation for y-coordinates
        poly_y = np.polyfit(local_times,local_positions[1],deg=1)
        # plot interpolation and approximation
        approx_points[0, i:i + step] = np.polyval(poly_x, local_times)
        approx_points[1, i:i + step] = np.polyval(poly_y, local_times)

    plot_vectors([gnss_positions[0:2],approx_points], ["interp","approx"])
    plt.show()