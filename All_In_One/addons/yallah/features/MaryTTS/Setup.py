import bpy

import os

from yallah import YALLAH_FEATURES_DIR

print("Creating phonemes for the MaryTTS speech synthesis (ShapeKeys starting with 'phoneme_'")
phonemes_file = os.path.join(YALLAH_FEATURES_DIR, "MaryTTS/PhonemesMBLab1_6.json")
bpy.ops.object.create_shape_keys(shape_keys_filename=phonemes_file)
