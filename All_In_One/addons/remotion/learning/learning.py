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

import utils
import argparse
import os

from keras.callbacks import TensorBoard

learning_profile = {
    "walk": {
        "data_dir": "../dataset/walk/",
        "save_forecast": os.path.dirname(os.path.realpath(__file__)) + "/saves/walk_1.h5",
        "save": os.path.dirname(os.path.realpath(__file__)) + "/saves/walk_2.h5",
        "frame_in": 30,
        "frame_out": 30,
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
    parser.add_argument("-o", "--save_dst", help="File where learning result will be saved")
    parser.add_argument("-fi", "--frame_in", type=int, help="Number of input frame")
    parser.add_argument("-fo", "--frame_out", type=int, help="Number of predicted frame")
    parser.add_argument("--gpu", help="Enable GPU acceleration")
    parser.add_argument("-e", "--epoch", type=int, help="Number of epoch")
    parser.add_argument("--tensorboard", help="Enable tensorboard log and save it to path")

    args = parser.parse_args()

    motion = args.motion
    save_file = args.save_dst if args.save_dst else learning_profile[motion]["save"]
    frame_in = args.frame_in if args.frame_in else learning_profile[motion]["frame_in"]
    frame_out = args.frame_out if args.frame_out else learning_profile[motion]["frame_out"]
    epoch = args.epoch if args.epoch else 10
    gpu = args.gpu

    # -------------------------------------------

    print("Load dataset ...")
    dataset = utils.MotionData()
    dataset.add_all_capture_dir(os.path.dirname(os.path.realpath(__file__)) + "/" + learning_profile[motion]["data_dir"])

    # -------------------------------------------

    print("\nPreparing data ...")
    Xtrain, Xtest, Ytrain, Ytest = dataset.get_data_2(frame_in, frame_out, True, test=0.3)

    print("Number of loaded animation : " + str(len(dataset.sequences)) + " - Number training of frame : " + str(Xtrain.shape[0]) + " - Number of test frame : " + str(Xtest.shape[0]))

    print("\nBuild learning model ...")
    #model = utils.MotionFixModel_lstm_one(len(Xtrain), Xtrain.shape[1], Xtrain.shape[2], gpu)
    model = utils.MotionFixModel_lstm_two(Xtrain.shape[1], Xtrain.shape[2], gpu)

    print("Start learning process ...")

    callbacks = []
    if args.tensorboard:
        callbacks.append(TensorBoard(log_dir=args.tensorboard))

    model.fit(
        Xtrain, Ytrain, 
        epochs=epoch, 
        batch_size=512, 
        validation_data=(Xtest, Ytest), 
        verbose=1, 
        shuffle=False,
        callbacks=callbacks
    )
    
    """for i in range(epoch):
        print(str(i) + "/" + str(epoch) + "------------------------------------------------------")
        model.fit(Xtrain, Ytrain, epochs=1, batch_size=len(Xtrain), validation_data=(Xtest, Ytest), verbose=1, shuffle=False)
        model.reset_states()"""

    print("Done.\n")

    model.save(learning_profile[motion]["save_forecast"])
    print("Result saved in " + learning_profile[motion]["save_forecast"])

    # -------------------------------------------

    print("\nPreparing data ...")
    Xtrain, Xtest, Ytrain, Ytest = dataset.get_data(frame_in, frame_out, True, test=0.3)

    print("Number of loaded animation : " + str(len(dataset.sequences)) + " - Number training of frame : " + str(Xtrain.shape[0]) + " - Number of test frame : " + str(Xtest.shape[0]))

    print("\nBuild learning model ...")
    model = utils.MotionFixModel_lstm_two(Xtrain.shape[1], Xtrain.shape[2], gpu)

    print("Start learning process ...")

    callbacks = []
    if args.tensorboard:
        callbacks.append(TensorBoard(log_dir=args.tensorboard))

    model.fit(
        Xtrain, Ytrain, 
        epochs=epoch, 
        batch_size=512, 
        validation_data=(Xtest, Ytest), 
        verbose=1, 
        shuffle=False,
        callbacks=callbacks
    )

    print("Done.\n")

    model.save(save_file)
    print("Result saved in " + save_file)