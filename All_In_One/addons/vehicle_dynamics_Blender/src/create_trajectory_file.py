#!/usr/bin/env python
"""
CLI program to create trajectory file from dataset given as program argument

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

if __name__ == '__main__':
    import sys, os
    # fix import path
    sys.path[0] = os.path.dirname(os.path.dirname(__file__))
    from src import get_trajectory_from_path
    import numpy as np
    # for benchmarking
    import time
    import argparse

    # parse program parameters
    parser = argparse.ArgumentParser(description='Inertia[+GNSS] data to trajectory')
    parser.add_argument('input', type=str, help='Input file')
    parser.add_argument('output', type=str, help='Output file')
    args = parser.parse_args()

    # get absolute path of input file
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, args.input)

    #integrate positions
    positions, times, angular_positions = get_trajectory_from_path(path)
    #reshape times to merge it with position
    times = np.reshape(times, (1, len(times)))
    # merge times and positions in one array
    timesPosition = np.concatenate((times, positions, angular_positions), axis=0)
    # save to txt
    np.savetxt(args.output, timesPosition.T, delimiter=";", newline="\n")


