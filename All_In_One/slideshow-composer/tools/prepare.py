import os
import argparse
import os.path
import subprocess
import re
import math

class Operation:
    """ Base class for every operation """

    def get_valid_file_extensions(self):
        return []

    def is_file_valid(self, path):
        supported_extensions = self.get_valid_file_extensions()
        extension = os.path.splitext(path)[1][1:].lower()
        return extension in supported_extensions

    def apply(self, path):
        pass


class StabilizeOperation(Operation):
    """ Performs stabilization of movie files """
    output_file_prefix = 'stabilized'

    def get_valid_file_extensions(self):
        return {'mp4', 'avi', 'mov', 'mkv'}

    def is_file_valid(self, path):
        return Operation.is_file_valid(self, path) and not re.match('.+_{}.+'.format(self.output_file_prefix), path)

    def apply(self, path):
        if self.is_file_valid(path):
            if args.verbose:
                print('Stabilizing file: {}'.format(path))
            (dir, file) = os.path.split(path)
            (root, ext) = os.path.splitext(file)
            output_file = "".join([root, '_', self.output_file_prefix, ext])
            output_path = os.path.join(dir, output_file)
            subprocess.call("ffmpeg -i {} -vf vidstabdetect=stepsize=6:shakiness=8:accuracy=9:result=transform_vectors.trf -f null -".format(path).split(' '))
            subprocess.call("ffmpeg -i {} -vf vidstabtransform=input=transform_vectors.trf:zoom=1:smoothing=30,unsharp=5:5:0.8:3:3:0.4 -vcodec libx264 -preset slow -tune film -crf 23 -acodec copy {}".format(path, output_path).split(' '))


class FixAspectRatioOperation(Operation):
    """ Fix images aspect ratio to correctly display them in Blender VSE """
    output_file_prefix = 'aspect_ratio_fixed'
    target_aspect_ratio = 1920/1080
    image_width = 0
    image_height = 0
    image_aspect_ratio = 0
    image_orientation = None

    def get_valid_file_extensions(self):
        return {'jpg', 'jpeg', 'png'}

    def is_file_valid(self, path):
        return Operation.is_file_valid(self, path) and not re.match('.+_{}.+'.format(self.output_file_prefix), path)

    def has_valid_aspect_ratio(self, path):
        if not self.has_valid_aspect_ratio(path):
            if args.verbose:
                print('Image has wrong EXIF orientation value: {}'.format(self.image_orientation))
            return False

        if not self.has_valid_aspect_ratio():
            if args.verbose:
                print('Image has wrong aspect ratio: {} and should be: {}'.format(image_aspect_ratio, self.target_aspect_ratio))
            return False
        return True

    def has_valid_exif_orientation(self):
        return self.image_orientation == 'TopLeft'

    def has_valid_aspect_ratio(self):
        return math.isclose(self.image_aspect_ratio, self.target_aspect_ratio, rel_tol=0.1)

    def read_image_properties(self, path):
        result = subprocess.check_output(['magick', 'identify', '-ping', '-format', '"%[width] %[height] %[orientation]"', path])
        if args.verbose:
            print('Image properties {}: {}'.format(path, result))
        image_properties = result.decode("utf-8").strip("\"").split(' ')
        self.image_orientation = image_properties[2]
        if self.has_valid_exif_orientation():
            self.image_width = int(image_properties[0])
            self.image_height = int(image_properties[1])
        else:
            self.image_width = int(image_properties[1])
            self.image_height = int(image_properties[0])
        self.image_aspect_ratio = self.image_width / self.image_height

    def apply(self, path):
        if self.is_file_valid(path):
            self.read_image_properties(path)
            if not self.has_valid_aspect_ratio() or not self.has_valid_exif_orientation():
                if args.verbose:
                    print('Fixing orientation: {}'.format(path))
                (dir, file) = os.path.split(path)
                (root, ext) = os.path.splitext(file)
                output_file = "".join([root, '_', self.output_file_prefix, ext])
                input_path = path
                output_path = os.path.join(dir, output_file)
                if not self.has_valid_exif_orientation():
                    subprocess.call("magick convert -auto-orient {} {}".format(input_path, output_path).split(' '))
                    input_path = output_path
                if not self.has_valid_aspect_ratio():
                    new_width = self.image_width
                    new_height = self.image_height
                    if self.target_aspect_ratio > 0:
                        new_width = self.target_aspect_ratio * self.image_height
                    else:
                        new_height = self.target_aspect_ratio * self.image_width
                    subprocess.call("magick convert {} -background black -gravity center -extent {}x{} -flatten {}".format(input_path, new_width, new_height, output_path).split(' '))


operations = {'stabilize': StabilizeOperation(), 'fix_aspect_ratio': FixAspectRatioOperation()}

parser = argparse.ArgumentParser(description='Applies various operations on media files')
parser.add_argument('operation', help='Operation to perform on files', choices=operations.keys())
parser.add_argument('-v', '--verbose', help='Prints more output', action='store_true')
parser.add_argument('--dir', action='store', default='.', help='specifies the input folder (default: current folder)')

args = parser.parse_args()

if args.verbose:
    print('Performing operation:{} on directory:{}'.format(args.operation, args.dir))

# traverse directory and apply chosen operation on files
operation = operations[args.operation]
for root, dirs, files in os.walk(args.dir):
    path = root.split(os.sep)
    for file in files:
        abs_path = os.path.join(root, file)
        operation.apply(abs_path)





