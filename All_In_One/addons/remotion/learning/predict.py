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

from sklearn.metrics import mean_squared_error

import utils
import argparse
import os

learning_profile = {
    "walk": {
        "data_dir": "../dataset/walk/",
        "save_forecast": os.path.dirname(os.path.realpath(__file__)) + "/saves/walk_1.h5",
        "save": os.path.dirname(os.path.realpath(__file__)) + "/saves/walk_2.h5",
        "frame_in": 10,
        "frame_out": 10,
    },
    "jump": {
        "data_dir": "../dataset/jump/",
        "save_forecast": os.path.dirname(os.path.realpath(__file__)) + "/saves/jump_1.h5",
        "save": os.path.dirname(os.path.realpath(__file__)) + "/saves/jump_2.h5",
        "frame_in": 30,
        "frame_out": 30,
    }
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("motion", help="Motion profile type")
    parser.add_argument("-t", "--tolerance", type=float, help="Tolerance between predicted and sources")
    parser.add_argument("-i", "--input", help="Animation source file")
    parser.add_argument("-o", "--output", help="Animation output file")

    parser.add_argument("--start-frame", type=int)
    parser.add_argument("--end-frame", type=int)

    parser.add_argument("-fi", "--frame_in", type=int, help="Number of input frame")
    parser.add_argument("-fo", "--frame_out", type=int, help="Number of predicted frame")

    parser.add_argument("--gpu", help="Enable GPU acceleration")

    args = parser.parse_args()

    motion = args.motion

    if not args.input or not args.output:
        exit()

    interval = False
    start_frame = 0
    end_frame = 0

    if args.start_frame and args.end_frame:
        interval = True
        start_frame = args.start_frame
        end_frame = args.end_frame

    tolerance = args.tolerance if args.tolerance else 100
    
    frame_in = args.frame_in if args.frame_in else learning_profile[motion]["frame_in"]
    frame_out = frame_in

    gpu = args.gpu

    # --------------------------------------------------------------

    print("Load data ...")
    motion_data = utils.MotionData()
    motion_data.add_capture(args.input)

    raw_motion = motion_data.sequences[0]

    print("\nPreparing data ...")
    X, Y = motion_data.get_data_2(frame_in, frame_out, False)

    #model = utils.MotionFixModel_lstm_one(X.shape[0], X.shape[1], X.shape[2], gpu)
    model = utils.MotionFixModel_lstm_two(X.shape[1], X.shape[2], gpu)
    model.load_weights(learning_profile[motion]["save_forecast"])

    print("Start predict process ...")
    Yresult = model.predict(X, batch_size=len(X), verbose=1)

    n_vars = raw_motion.get_number_value_per_frame()

    for i in range(len(X) - frame_in):
        if interval and (i < start_frame or i > end_frame):
            continue
        
        error = mean_squared_error(Y[i], Yresult[i])
        if error > tolerance:
            raw_motion.data[(i+frame_in)*n_vars + 3:(i+frame_in+1)*n_vars] = Yresult[i][0][3:]

            X[i+frame_in][0][3:] = Yresult[i][0][3:]
            Yresult = model.predict(X, batch_size=len(X), verbose=1)
            
            print("Fix frame : " + str(i) + " [" + str(error) + "]")

    print("\nPreparing data ...")
    X, Y = motion_data.get_data(frame_in, frame_out, False)

    #model = utils.MotionFixModel_lstm_one(X.shape[0], X.shape[1], X.shape[2], gpu)
    model = utils.MotionFixModel_lstm_two(X.shape[1], X.shape[2], gpu)
    model.load_weights(learning_profile[motion]["save"])

    print("Start predict process ...")
    Yresult = model.predict(X, batch_size=len(X), verbose=1)

    for i in range(len(X)):
        if interval and (i < start_frame or i > end_frame):
            continue
        
        error = mean_squared_error(Y[i], Yresult[i])
        if error > tolerance:
            raw_motion.data[i*n_vars+3:(i+1)*n_vars] = Yresult[i][0][3:]

            X[i][0][3:] = Yresult[i][0][3:]
            Yresult = model.predict(X, batch_size=len(X), verbose=1)
            
            print("Fix frame : " + str(i) + " [" + str(error) + "]")

    print("Done.")

    with open(args.output, "w") as file:
        file.write(raw_motion.to_amc())
    
    print("\nFixed animation saved in " + args.output)