# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


linesToAddAtBeginning = [
    "import bpy\n",
    "import json\n",
    # "if bpy.data.filepath == '':\n",
    # "    for obj in bpy.data.objects:\n",
    # "        obj.name = 'background_removed'\n",
    # "    for mesh in bpy.data.meshes:\n",
    # "        mesh.name = 'background_removed'\n",
    "data_blocks = list()\n",
    "python_data = list()\n",
    "def appendFrom(typ, filename):\n",
    "    directory = os.path.join(sourceBlendFile, typ)\n",
    "    filepath = os.path.join(directory, filename)\n",
    "    bpy.ops.wm.append(\n",
    "        filepath=filepath,\n",
    "        filename=filename,\n",
    "        directory=directory)\n",
    "### DO NOT EDIT ABOVE THESE LINES\n\n\n",
]
linesToAddAtEnd = [
    "\n\n### DO NOT EDIT BELOW THESE LINES\n",
    "assert None not in data_blocks  # ensures that all data from data_blocks exists\n",
    # write Blender data blocks to library in temp location 'storagePath'
    "if os.path.exists(storagePath):\n",
    "    os.remove(storagePath)\n",
    "bpy.data.libraries.write(storagePath, set(data_blocks), fake_user=True)\n",
    # write python data to library in temp location 'storagePath'
    "data_file = open(storagePath.replace('.blend', '.py'), 'w')\n",
    "print(json.dumps(python_data), file=data_file)\n",
    "data_file.close()\n"
]


def addLines(script, fullPath, sourceBlendFile, passed_data):
    src=open(script,"r")
    oline=src.readlines()
    for line in linesToAddAtBeginning[::-1]:
        oline.insert(0, line)
    oline.insert(0, "storagePath = os.path.join(*%(fullPath)s)\n" % locals())
    oline.insert(0, "sourceBlendFile = os.path.join(*%(sourceBlendFile)s)\n" % locals())
    oline.insert(0, "import os\n" % locals())
    for key in passed_data:
        value = passed_data[key]
        value_str = str(value) if type(value) != str else "'%(value)s'" % locals()
        oline.insert(0, "%(key)s = %(value_str)s\n" % locals())
    for line in linesToAddAtEnd:
        oline.append(line)
    src.close()
    return oline


def getElapsedTime(startTime, endTime, precision:int=2):
    """From seconds to Days;Hours:Minutes;Seconds"""
    value = endTime-startTime

    valueD = (((value/365)/24)/60)
    Days = int(valueD)

    valueH = (valueD-Days)*365
    Hours = int(valueH)

    valueM = (valueH - Hours)*24
    Minutes = int(valueM)

    valueS = (valueM - Minutes)*60
    Seconds = round(valueS, precision)

    outputString = str(Days) + ";" + str(Hours) + ":" + str(Minutes) + ";" + str(Seconds)
    return outputString
