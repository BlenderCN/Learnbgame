import numpy
import zipfile
import io
import os
import csv
import bpy
from bpy.path import abspath
from bpy.path import display_name_from_filepath

from .. import model

DELAYS = []
TIMINGS = []
noAvailableConnections = 0

# TODO(SK): Missing docstring
def csv_read(data):
    reader = csv.reader(data, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    return [row for row in reader if len(row) > 0]


# TODO(SK): Refactor, in general global variables are ugly and fault prone.
SUPPORTED_FILETYPES = {
    ".csv": csv_read
}

# TODO(SK): Missing docstring
def csvfile_read(filename):
    f = open(filename, 'r')
    result = csv_read(f)
    f.close()
    return result

# TODO(SK): Missing docstring
def import_model_from_zip(filepath):
    result = {}
    with zipfile.ZipFile(filepath, "r", zipfile.ZIP_DEFLATED) as file:
        for filename in file.namelist():
            filename_split = os.path.splitext(filename)
            filename_extension = filename_split[-1]
            data = io.StringIO(str(file.read(filename), 'utf-8'))
            func = SUPPORTED_FILETYPES[filename_extension]
            matrix = func(data)
            result[filename_split[0]] = (matrix)
    return result

# TODO(SK): Missing docstring
def readSimulationData(simulationFile):
    # Open timing file (output.csv)
    neuronTimingPath = abspath(simulationFile)
    fileName = display_name_from_filepath(simulationFile)
    timingZip = import_model_from_zip(neuronTimingPath)
    
    # read the data into the TIMINGS variable
    global TIMINGS
    TIMINGS = []
    timing_data = timingZip['spikes']

    for row in timing_data:
        if len(row) == 3:
            
            # if start time point is not reached, simply continue
            if (float(row[2]) < bpy.context.scene.pam_anim_animation.startTime):
                continue
            
            # only load data up to the prespecified time point
            if (float(row[2]) < bpy.context.scene.pam_anim_animation.endTime):
                TIMINGS.append((int(row[0]), int(row[1]), float(row[2])))

    # Sort by fire time
    TIMINGS.sort(key = lambda x: x[2])

    global DELAYS
    DELAYS = []
    for i in range(0, len(model.MODEL.connections)):
        try:
            DELAYS.append(timingZip["delay_" + str(i)])
        except:
            print('cannot find file: ' + 'delay_' + str(i) + '.csv')
    
    DELAYS = numpy.array(DELAYS)
    global noAvailableConnections
    noAvailableConnections = len(DELAYS[0][0])