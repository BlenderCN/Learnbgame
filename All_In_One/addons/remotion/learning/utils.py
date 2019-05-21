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

from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from numpy import array, reshape, concatenate
from pandas import DataFrame, concat
from os import listdir
from os.path import isdir, isfile
import os

from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout, Flatten, RepeatVector
from keras.layers import GaussianNoise
from keras.losses import mean_squared_error
from keras.layers.wrappers import TimeDistributed
from keras.layers.recurrent import LSTM
from keras.layers.cudnn_recurrent import CuDNNLSTM
from keras.optimizers import RMSprop, Adam

# AMC Parsing -----------------------------------

class SequenceData:

    def __init__(self):
        self.elements = {}
        self.data = []
        self.headers = []

    def get_total_frame(self):
        total_coord_per_frame = self.get_number_value_per_frame()
        if len(self.elements) > 0:
            return int(len(self.data) / total_coord_per_frame)
        else:
            return 0

    def get_number_value_per_frame(self):
        total_coord_per_frame = 0
        for v in self.elements:
            total_coord_per_frame += self.elements[v]
        return total_coord_per_frame

    def get_frame(self, frame):
        total_coord_per_frame = self.get_number_value_per_frame()
        return self.data[frame * total_coord_per_frame:(frame + 1) * total_coord_per_frame]

    def get_frames(self, start, stop):
        total_coord_per_frame = self.get_number_value_per_frame()
        return self.data[start * total_coord_per_frame:(stop + 1) * total_coord_per_frame]

    def to_literal(self, frame):
        total_coord_per_frame = self.get_number_value_per_frame()
        if len(frame) != total_coord_per_frame:
            return 'SequenceData (to_literal) : not correct size'
        r = ''
        j = 0
        for v in self.elements:
            r += v
            for i in range(self.elements[v]):
                r += ' ' + str(frame[j])
                j += 1
            r += "\n"
        return r

    def to_amc(self):
        total_frame = self.get_total_frame()

        r = ''
        for line in self.headers:
            r += line

        for i in range(total_frame):
            r += str(i + 1) + "\n"
            r += self.to_literal(self.get_frame(i))
        return r

def AMCParse(filename):
    sequence = SequenceData()
    with open(filename, 'r') as file:
        i = 0
        for line in file:
            if len(line) > 0:
                if line[0] == ':' or line[0] == '#':
                    sequence.headers.append(line)
                else:
                    split_line = line.split(' ')
                    if len(split_line) > 1:
                        if split_line[0] not in sequence.elements:
                            sequence.elements[split_line[0]] = len(split_line) - 1
                        for j in range(1,len(split_line)):
                            sequence.data.append(float(split_line[j]))
            i += 1

    #print(filename + " : " + str(sequence.get_number_value_per_frame()) + " - " + str(len(sequence.data) / sequence.get_number_value_per_frame()))
    return sequence

# Prepare data for training ---------------------

class MotionData:

    def __init__(self):
        self.sequences = []
    
    def add_capture(self, motion_file):
        print("Add " + motion_file + " to dataset.")
        self.sequences.append(AMCParse(motion_file))

    def add_captures(self, motion_files):
        for file in motion_files:
            self.add_capture(file)

    def add_capture_dir(self, motion_dir):
        files = listdir(motion_dir)

        for f in files:
            file = os.path.join(motion_dir, f)
            if isfile(file):
                ext = file.split('.')
                ext = ext[len(ext)-1]
                if ext == 'amc':
                    self.add_capture(file)

    def add_all_capture_dir(self, motion_dir):
        self.add_capture_dir(motion_dir)

        folders = listdir(motion_dir)
        for f in folders:
            f = os.path.join(motion_dir, f) + "/"
            if isdir(f):
                self.add_all_capture_dir(f)

    def get_data(self, frame_in, frame_out, split, test = 0.3):
        if len(self.sequences) == 0:
            raise Exception("Dataset is empty !")

        p_data = array([])

        for seq in self.sequences:
            p_data = concatenate([p_data, array(seq.data)])

        #min_max_scaler = preprocessing.Normalizer()
        #p_data = min_max_scaler.fit_transform(reshape(p_data, (1, len(p_data))))
        p_data = reshape(p_data, (1, len(p_data)))

        nb_vars = self.sequences[0].get_number_value_per_frame()
        p_data = reshape(p_data[0], (int(len(p_data[0]) / nb_vars), nb_vars))

        df = DataFrame(p_data)
        df = concat([df.shift(frame_in - i - 1) for i in range(frame_in)], axis=1)
        df.dropna(inplace=True)

        values = df.values
        X = values.reshape(len(values), frame_in, nb_vars)
        Y = values[:, 0:(frame_out * nb_vars)].reshape(len(values), frame_out, nb_vars)

        if split:
            return train_test_split(X, Y, test_size=test)
        else:
            return X, Y

    def get_data_2(self, frame_in, frame_out, split, test = 0.3):
        if len(self.sequences) == 0:
            raise Exception("Dataset is empty !")

        p_data = []

        for seq in self.sequences:
            p_data += seq.data

        nb_vars = self.sequences[0].get_number_value_per_frame()
        total_frame = int(len(p_data) / nb_vars)

        X_data = []
        for i in range(total_frame):
            X_data.append(p_data[i*nb_vars:(i+frame_in)*nb_vars])
        X_data = X_data[:-frame_in - frame_out]

        Y_data = []
        for i in range(total_frame - frame_in - frame_out):
            Y_data.append(p_data[(i+frame_in)*nb_vars:(i+frame_in+frame_out)*nb_vars])

        X = array(X_data).reshape(len(X_data), frame_in, nb_vars)
        Y = array(Y_data).reshape(len(Y_data), frame_out, nb_vars)
        
        if split:
            return train_test_split(X, Y, test_size=test)
        else:
            return X, Y
    
# Build model -----------------------------------

def MotionFixModel_lstm_one(batch_size, timestep, data_dim, gpu = True):
    model = Sequential()

    model.add(GaussianNoise(0.1,  batch_input_shape=(batch_size, timestep, data_dim)))
    
    model.add(CuDNNLSTM(150, batch_input_shape=(batch_size, timestep, data_dim), stateful=True, return_sequences=True))
    
    model.add(Dropout(0.2))

    model.add(CuDNNLSTM(150, stateful=True, return_sequences=True))
    
    model.add(Dense(data_dim, activation='linear'))

    model.compile(loss=mean_squared_error, optimizer='RMSprop', metrics=['acc'])
    
    return model

def MotionFixModel_lstm_two(timestep, data_dim, gpu = True):
    model = Sequential()

    model.add(GaussianNoise(0.1, input_shape=(timestep, data_dim)))

    if gpu:
        model.add(CuDNNLSTM(100, input_shape=(timestep, data_dim), return_sequences=True))
    else:
        model.add(LSTM(100, input_shape=(timestep, data_dim), return_sequences=True))

    model.add(Dropout(0.1))

    if gpu:
        model.add(CuDNNLSTM(100, return_sequences=True))
    else:
        model.add(LSTM(100, return_sequences=True))

    model.add(Dropout(0.1))

    if gpu:
        model.add(CuDNNLSTM(100, return_sequences=True))
    else:
        model.add(LSTM(100, return_sequences=True))

    model.add(Dense(data_dim, activation='linear'))

    model.compile(loss=mean_squared_error, optimizer='RMSprop', metrics=['acc'])

    return model