"""
Utility module to parse input. It's auto-detects input type and returns parsed numpy array accordingly.

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

from enum import Enum, unique
from io import StringIO

import numpy as np


@unique
class InputType(Enum):
    ACCELERATION = 1
    FULLINERTIAL = 2
    GNSS = 3
    GYROSCOPE = 4
    INERTIAL = 5
    UNMOD_FULLINERTIAL = 6
    UNMOD_INERTIAL = 7
    UNRECOGNIZED = 8


def detect_input_type(array, filepath):
    """

    :param array:
    :param filepath:
    :return:
    """
    # default file type
    filetype = InputType.UNRECOGNIZED
    # analyze file name
    if filepath.find("acc") != -1:
        filetype = InputType.ACCELERATION
    elif filepath.find("gnss") != -1:
        filetype = InputType.GNSS
    elif filepath.find("gyr") != -1:
        filetype = InputType.GYROSCOPE
    elif filepath.find("unmodified-fullinertial") != -1:
        filetype = InputType.UNMOD_FULLINERTIAL
    elif filepath.find("unmodified-inertial") != -1:
        filetype = InputType.UNMOD_INERTIAL
    elif filepath.find("fullinertial") != -1:
        filetype = InputType.FULLINERTIAL
    elif filepath.find("inertial") != -1:
        filetype = InputType.INERTIAL
    # if no match are found try with column count
    else:
        column_count = array.shape[1]
        if column_count == 4:
            # TODO acc or gyr
            filetype = InputType.ACCELERATION
        elif column_count == 10:
            if np.any(np.isnan(array)):
                filetype = InputType.UNMOD_INERTIAL
            else:
                filetype = InputType.INERTIAL
        elif column_count == 14:
            if np.any(np.isnan(array)):
                filetype = InputType.UNMOD_FULLINERTIAL
            else:
                filetype = InputType.FULLINERTIAL
    return filetype


def get_vectors(array, input_type):
    """
    Get various numpy vectors based from dataframe columns based on input type

    :param array: pandas dataframe
    :param input_type: InputType enum
    :return:
        times, gps_speed, accelerations, angular_velocities if input is inertial \n
        times, coordinates, altitudes, gps_speed, heading, accelerations, angular_velocities if input is fullinertial
    """
    if input_type == InputType.INERTIAL or input_type == InputType.UNMOD_INERTIAL:
        # ax ay az
        accelerations = array[:,2:5].T
        # gx gy gz
        angular_velocities = array[:,5:8].T
        times = array[:,0]
        gps_speed = array[:,1].T
        return times, gps_speed, accelerations, angular_velocities
    elif input_type == InputType.FULLINERTIAL:
        coordinates = array[:,1:3].T
        altitudes = array[:,3].T
        accelerations = array[:,6:9].T
        angular_velocities = array[:,9:12].T
        times = array[:,0].T
        gps_speed = array[:,5].T
        heading = array[:,4].T
        return times, coordinates, altitudes, gps_speed, heading, accelerations, angular_velocities
    elif input_type == InputType.UNMOD_FULLINERTIAL:
        # TODO use DataFrame.interpolate
        # the input has gnss and inertial records mixed
        # filter to get records with gnss data
        clean_gnss_data = array[~np.isnan(array[:,1])]
        # interpolate coordinates
        # get numpy array
        gnss_data = clean_gnss_data[:,1:6]
        # get numpy array of timestamp from gnss data
        gnss_data_timestamp = clean_gnss_data[:,0]
        # get from original dataframe records with inertial data
        inertial_array = array[~np.isnan(array[:,6])]
        # get accelerations array
        accelerations = inertial_array[:,6:9].T
        # get angular velocities array
        angular_velocities = inertial_array[:,9:12].T
        # get timestamp of records with inertial data (more frequent than gnss)
        times = inertial_array[:,0]
        # get gnss data at inertial frequency by interpolation
        try:
            altitudes, coordinates, gps_speed, heading = interpolate_gnss_data(gnss_data, gnss_data_timestamp, times)
        except (ValueError):
            print("raised exception on interpolation, this can be caused by records with same timestamp")
            # if an exception is raised it can be caused by x vector not being sorted, so sort it
            # this is a rare case and is sign of a bad input dataset
            gnss_data_timestamp = np.sort(gnss_data_timestamp)
            #retry
            try:
                altitudes, coordinates, gps_speed, heading = interpolate_gnss_data(gnss_data, gnss_data_timestamp, times)
            except (ValueError):
                print("Possibile presence of records with same timestamp")
                # rare case
                # TODO handle case removing duplicate timestamp record
                exit()
        # correct heading
        heading = 270 - heading
        return times, coordinates, altitudes, gps_speed, heading, accelerations, angular_velocities


def interpolate_gnss_data(gnss_data, gnss_data_timestamp, times):
    coordinatesX = np.interp(times, gnss_data_timestamp, gnss_data[:, 0])
    coordinatesY = np.interp(times, gnss_data_timestamp, gnss_data[:, 1])
    # create single array from x e y coordinates
    coordinates = np.array([x for x in zip(coordinatesX, coordinatesY)]).T
    altitudes = np.interp(times, gnss_data_timestamp, gnss_data[:, 2])
    heading = np.interp(times, gnss_data_timestamp, gnss_data[:, 3])
    gps_speed = np.interp(times, gnss_data_timestamp, gnss_data[:, 4])
    return altitudes, coordinates, gps_speed, heading


def parse_input(filepath, accepted_types=[input_type for input_type in InputType], slice_start=None, slice_end=None):
    """ Parse input file from filetype

    If the input is not one of the specified accepted format raise Expection
    Additional slicing can be specified with sliceStar and sliceEnd

    :param filepath: string
    :param accepted_types: list of accepted input types from <InputType> enum. Default accept all types.
    :param slice_start: integer
    :param slice_end: integer
    :return:
        times, gps_speed, accelerations, angular_velocities if input is inertial \n
        times, coordinates, gps_speed, heading, accelerations, angular_velocities if input is fullinertial
    :raises:
        Exception if format is not accepted or recognized
    """

    # open file
    with open(filepath, mode='r') as file:
        # read all content into string
        file_content = file.read()
    # remove beginning hashtag and tab
    file_content = file_content.strip("#\t")
    # i used this technique to not modify input file
    # use StringIO to simulate file read
    string_io = StringIO(file_content)
    # use pandas to parse tsv
    # set to not use first column as index
    # TODO use skip-read to max-row to slicing
    input_array = np.genfromtxt(string_io, delimiter='\t',skip_header=1)
    # detect file type
    input_type = detect_input_type(input_array, filepath)

    if input_type != InputType.UNRECOGNIZED:
        # slice input
        if slice_start is not None and slice_start < 0:
            raise Exception("Slice start must be positive")
        if slice_end is not None and abs(slice_end) > input_array.shape[0]:
            raise Exception("Slice end must not exceed dataframe rows")
        input_array = input_array[slice_start:slice_end]
        if input_type not in accepted_types:
            raise Exception("Not accepted format")
        # extrapolate vectors from input
        return get_vectors(input_array, input_type)
    else:
        raise Exception("Unrecognized input format")
