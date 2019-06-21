"""
Re : motion by Nicolas Candia <ncandia.pro@gmail.com>

Copyright (C) 2018 Nicolas Candia
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import argparse
import random

from math import fabs

import utils

# Break animation -------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="Input animation in AMC format")
    parser.add_argument("-o", "--output", help="Output file of break animation")
    parser.add_argument("-m", "--method", default="random", help="Method for breaking file (random or zero)")
    parser.add_argument("-b", "--interval", help="Frames intervals to break (if not precised it's all animation (format start:end)")
    parser.add_argument("-s", "--seed", help="Seed used for random", default=123456789, type=int)
    parser.add_argument("-r", "--random", type=int, help="Break n random frame in interval")

    args = parser.parse_args()

    if not args.input or not args.output:
        exit()

    print("Load animation " + args.input)
    animation = utils.AMCParse(args.input)

    nb_vars = animation.get_number_value_per_frame()

    interval = None
    if args.interval:
        interval_range = args.interval.split(':')
        interval = (int(interval_range[0]), int(interval_range[1]))

    if args.method == "random":
        print("Break animation using random method ...")

        random.seed(args.seed)

        data = []
        for i in range(animation.get_total_frame()):
            for j in range(3, nb_vars):
                data.append(animation.data[(i*nb_vars)+j])

        min_max = (min(data), max(data))

        if args.random:
            for i in range(args.random):
                frame = random.randint(0, animation.get_total_frame() - 1)
                if interval:
                    frame = random.randint(interval[0], interval[1])
                for j in range(3, nb_vars):
                    animation.data[(frame*nb_vars)+j] = (random.random() * (fabs(min_max[0]) + min_max[1])) - min_max[0]
        else:
            for i in range(animation.get_total_frame()):
                if interval is None or (i >= interval[0] and i <= interval[1]):
                    for j in range(3, nb_vars):
                        animation.data[(i*nb_vars)+j] = (random.random() * (fabs(min_max[0]) + min_max[1])) - min_max[0]
    
    elif args.method == "zero":
        print("Break animation using zero method ...")

        if args.random:
            for i in range(args.random):
                frame = random.randint(0, animation.get_total_frame() - 1)
                if interval:
                    frame = random.randint(interval[0], interval[1])
                for j in range(3, nb_vars):
                    animation.data[(frame*nb_vars)+j] = 0.0
        else:
            for i in range(animation.get_total_frame()):
                if interval is None or (i >= interval[0] and i <= interval[1]):
                    for j in range(3, nb_vars):
                        animation.data[(i*nb_vars)+j] = 0.0

    with open(args.output, "w") as file:
        file.write(animation.to_amc())

    print("Breaked animation saved in " + args.output)