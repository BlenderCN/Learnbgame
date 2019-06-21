import bpy
import os
import json

from yallah import YALLAH_FEATURES_DIR

#
# Test Feature. Used to check working directories and relative paths.
print("Feature Test: main body")

cwd = os.getcwd()
print("Feature Test: cwd='{}'".format(cwd))
print("Feature Test: features_dir='{}'".format(YALLAH_FEATURES_DIR))

DATA_FILENAME = os.path.join(YALLAH_FEATURES_DIR, "Test/DataTest.json")

mesh_obj = bpy.context.active_object
assert mesh_obj.type == 'MESH'

arm_obj = mesh_obj.parent
assert arm_obj.type == 'ARMATURE'



def test_method():
    print("Feature Test: this is a test method")


test_method()

print("Loading data...")
with open(DATA_FILENAME, "r") as json_file:
    data = json.load(json_file)
    print(data)


if __name__ == "__main__":
    print("Feature Test: this is a __main__ code")

