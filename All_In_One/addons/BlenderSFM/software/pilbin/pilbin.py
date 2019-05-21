# File: pilbin.py

import os
import sys
import argparse
from PIL import Image
from PIL.ExifTags import TAGS
from io import BytesIO

def convertImage(image, outputImage):
    bufferjpg = BytesIO()
    image.save(bufferjpg, format = "jpeg")
    open(outputImage + ".jpg", "wb").write(bufferjpg.getvalue())

    # Write PGM output image
    bufferpgm = BytesIO()
    image.convert("L").save(bufferpgm, format = "ppm")
    open(outputImage + ".jpg.pgm", "wb").write(bufferpgm.getvalue())

def printExif(image):
    exifAttrs = set(["Model", "Make", "ExifImageWidth", "ExifImageHeight", "FocalLength"])
    exif = {}
    info = image._getexif()
    if info:
        for attr, value in info.items():
            decodedAttr = TAGS.get(attr, attr)
            if decodedAttr in exifAttrs: exif[decodedAttr] = value
    if 'FocalLength' in exif: exif['FocalLength'] = float(exif['FocalLength'][0])/float(exif['FocalLength'][1])

    outputString = ""
    if ('Make' in exif):
        outputString += exif['Make']
    outputString += ","

    if ('Model' in exif):
        outputString += exif['Model']
    outputString += ","

    if ('FocalLength' in exif):
        outputString += str(exif['FocalLength'])
    outputString += ","

    outputString += str(exif['ExifImageWidth']) + "," + str(exif['ExifImageHeight'])

    print(outputString)

def main():
    # Parse parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("inputImage")
    parser.add_argument("outputImage")
    args = parser.parse_args()

    # Open input image
    image = Image.open(args.inputImage)

    # Convert images
    convertImage(image, args.outputImage)

    # Print exif data: Make, Model, Focal Length, Image Width, Image Height
    printExif(image)
    sys.exit(0)
 
if __name__ == "__main__":
    main()