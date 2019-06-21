# Copyright (C) 2018 Christopher Gearhart
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

# system imports
import bpy
import fnmatch
import numpy
import os
from .general import getRenderDumpPath

def averageFrames(classObject, outputFileName, verbose=0):
    """ Averages final rendered images in blender to present one render result """
    scn = bpy.context.scene
    if verbose >= 1:
        print("Averaging images...")

    # get image files to average
    renderPath = getRenderDumpPath()[0]
    allFiles = os.listdir(renderPath)
    inFileName = "{outputFileName}_seed-*_{frame}{extension}".format(outputFileName=outputFileName, frame=str(scn.rfc_imFrame).zfill(4), extension=scn.rfc_imExtension)
    imListNames = [filename for filename in allFiles if fnmatch.fnmatch(filename, inFileName)]
    imList = [os.path.join(renderPath, im) for im in imListNames]
    if not imList:
        print("No image files to average")
        return None

    # Assuming all images are the same size, get dimensions of first image
    imRef = bpy.data.images.load(imList[0])
    w = imRef.size[0]
    h = imRef.size[1]
    ch = imRef.channels
    alpha = (ch == 4)
    bpy.data.images.remove(imRef, do_unlink=True)
    if type(classObject.avDict["array"]) == numpy.ndarray:
        arr = classObject.avDict["array"]
    elif ch in [3, 4]:
        arr = numpy.zeros((w * h * ch), numpy.float)
    else:
        arr = numpy.zeros((w * h), numpy.float)
    N = len(imList) + classObject.avDict["numFrames"]

    # Build up average pixel intensities, casting each image as an array of floats
    if verbose >= 2:
        print("Averaging the following images:")

    for image in imList:
        if verbose >= 2:
            print(image)
        # load image                                    # runtime per iteration:
        im = bpy.data.images.load(image)                # ~.0002 sec
        data = list(im.pixels)                          # ~.10 sec
        imarr = numpy.array(data, dtype=numpy.float)    # ~.07 sec
        arr = arr+imarr                                 # ~.008 sec
        bpy.data.images.remove(im, do_unlink=True)      # ~.0002 sec
        os.remove(image)

    # save current info for averaged image to "self" object of class this function was called from
    classObject.avDict["numFrames"] = N
    classObject.avDict["array"] = arr

    arr = arr/N

    # Print details
    if verbose >= 1:
        print("Averaged successfully!")

    # Generate final averaged image and add it to the main database
    imName = "{outputFileName}_{frame}_average{extension}".format(outputFileName=outputFileName, frame=str(scn.rfc_imFrame).zfill(4), extension=scn.rfc_imExtension)
    if bpy.data.images.find(imName) < 0:
        new = bpy.data.images.new(imName, w, h, alpha)
    else:
        new = bpy.data.images[imName]
    new.pixels = arr.tolist()
    return imName
