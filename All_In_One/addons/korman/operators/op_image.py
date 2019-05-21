#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.props import *
from pathlib import Path

from ..helpers import TemporaryObject, ensure_power_of_two
from ..korlib import ConsoleToggler, GLTexture, scale_image
from ..exporter.explosions import *
from ..exporter.logger import ExportProgressLogger
from ..exporter.material import BLENDER_CUBE_MAP

# These are some filename suffixes that we will check to match for the cubemap faces
_CUBE_FACES = {
    "leftFace": "LF",
    "backFace": "BK",
    "rightFace": "RT",
    "bottomFace": "DN",
    "topFace": "UP",
    "frontFace": "FR",
}

class ImageOperator:
    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == "PLASMA_GAME"


class PlasmaBuildCubeMapOperator(ImageOperator, bpy.types.Operator):
    bl_idname = "image.plasma_build_cube_map"
    bl_label = "Build Cubemap"
    bl_description = "Builds a Blender cubemap from six images"

    overwrite_existing = BoolProperty(name="Check Existing",
                                      description="Checks for an existing image and overwrites it",
                                      default=True,
                                      options=set())
    filepath = StringProperty(subtype="FILE_PATH")
    require_cube = BoolProperty(name="Require Square Faces",
                                description="Resize cubemap faces to be square if they are not",
                                default=True,
                                options=set())
    texture_name = StringProperty(name="Texture",
                                  description="Environment Map Texture to stuff this into",
                                  default="",
                                  options={"HIDDEN"})

    def __init__(self):
        self._report = ExportProgressLogger()
        self._report.progress_add_step("Finding Face Images")
        self._report.progress_add_step("Loading Face Images")
        self._report.progress_add_step("Scaling Face Images")
        self._report.progress_add_step("Generating Cube Map")

    def execute(self, context):
        with ConsoleToggler(True) as _:
            try:
                self._execute()
            except ExportError as error:
                self.report({"ERROR"}, str(error))
                return {"CANCELLED"}
            else:
                return {"FINISHED"}

    def _execute(self):
        self._report.progress_start("BUILDING CUBE MAP")
        if not Path(self.filepath).is_file():
            raise ExportError("No cube image found at '{}'".format(self.filepath))

        # Figure out the paths for the six cube faces. We will use the original file
        # only if a face is missing...
        face_image_paths = self._find_cube_files(self.filepath)

        # If no images were loaded, that means we will want to generate a cube map
        # with the single face provided by the image in filepath. Otherwise, we'll
        # use the found faces (and the provided path if any are missing...)
        face_data = list(self._load_all_image_data(face_image_paths, self.filepath))
        face_widths, face_heights, face_data = zip(*face_data)

        # All widths and heights must be the same... so, if needed, scale the stupid images.
        width, height, face_data = self._scale_images(face_widths, face_heights, face_data)

        # Now generate the stoopid cube map
        image_name = Path(self.filepath).name
        idx = image_name.rfind('_')
        if idx != -1:
            suffix = image_name[idx+1:idx+3]
            if suffix in _CUBE_FACES.values():
                image_name = image_name[:idx] + image_name[idx+3:]
        cubemap_image = self._generate_cube_map(image_name, width, height, face_data)

        # If a texture was provided, we can assign this generated cube map to it...
        if self.texture_name:
            texture = bpy.data.textures[self.texture_name]
            texture.environment_map.source = "IMAGE_FILE"
            texture.image = cubemap_image

        self._report.progress_end()
        return {"FINISHED"}

    def _find_cube_files(self, filepath):
        self._report.progress_advance()
        self._report.progress_range = len(BLENDER_CUBE_MAP)
        self._report.msg("Searching for cubemap faces...")

        idx = filepath.rfind('_')
        if idx != -1:
            files = []
            for key in BLENDER_CUBE_MAP:
                suffix = _CUBE_FACES[key]
                face_path = filepath[:idx+1] + suffix + filepath[idx+3:]
                face_name = key[:-4].upper()
                if Path(face_path).is_file():
                    self._report.msg("Found face '{}': {}", face_name, face_path, indent=1)
                    files.append(face_path)
                else:
                    self._report.warn("Using default face data for face '{}'", face_name, indent=1)
                    files.append(None)
                self._report.progress_increment()
            return tuple(files)

    def _generate_cube_map(self, req_name, face_width, face_height, face_data):
        self._report.progress_advance()
        self._report.msg("Generating cubemap image...")

        # If a texture was provided, we should check to see if we have an image we can replace...
        image = bpy.data.textures[self.texture_name].image if self.texture_name else None

        # Init our image
        image_width = face_width * 3
        image_height = face_height * 2
        if image is not None and self.overwrite_existing:
            image.source = "GENERATED"
            image.generated_width = image_width
            image.generated_height = image_height
        else:
            image = bpy.data.images.new(req_name, image_width, image_height, True)
        image_datasz = image_width * image_height * 4
        image_data = bytearray(image_datasz)
        face_num = len(BLENDER_CUBE_MAP)

        # This is the inverse of the operation found in MaterialConverter._finalize_cube_map
        for i in range(face_num):
            col_id = i if i < 3 else i - 3
            row_start = 0 if i < 3 else face_height
            row_end = face_height if i < 3 else image_height

            # TIL: Blender's coordinate system has its origin in the lower left, while Plasma's
            # is in the upper right. We could do some fancy flipping stuff, but there are already
            # mitigations in code for that. So, we disabled the GLTexture's flipping helper and
            # will just swap the locations of the images in the list. le wout.
            j = i + 3 if i < 3 else i - 3
            for row_current in range(row_start, row_end, 1):
                src_start_idx = (row_current - row_start) * face_width * 4
                src_end_idx = src_start_idx + (face_width * 4)
                dst_start_idx = (row_current * image_width * 4) + (col_id * face_width * 4)
                dst_end_idx = dst_start_idx + (face_width * 4)
                image_data[dst_start_idx:dst_end_idx] = face_data[j][src_start_idx:src_end_idx]

        # FFFUUUUU... Blender wants a list of floats
        pixels = [None] * image_datasz
        for i in range(image_datasz):
            pixels[i] = image_data[i] / 255

        # Obligatory remark: "Blender sucks"
        image.pixels = pixels
        image.update()
        image.pack(True)
        return image


    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def _load_all_image_data(self, face_image_paths, default_image_path):
        self._report.progress_advance()
        self._report.progress_range = len(BLENDER_CUBE_MAP)
        self._report.msg("Loading cubemap faces...")

        default_data = None
        for image_path in face_image_paths:
            if image_path is None:
                if default_data is None:
                    default_data = self._load_single_image_data(default_image_path)
                yield default_data
            else:
                yield self._load_single_image_data(image_path)
            self._report.progress_increment()

    def _load_single_image_data(self, filepath):
        images = bpy.data.images
        with TemporaryObject(images.load(filepath), images.remove) as blimage:
            with GLTexture(image=blimage, fast=True) as glimage:
                return glimage.image_data

    def _scale_images(self, face_widths, face_heights, face_data):
        self._report.progress_advance()
        self._report.progress_range = len(BLENDER_CUBE_MAP)
        self._report.msg("Checking cubemap face dimensions...")

        # Take the smallest face width and get its POT variety (so we don't rescale on export)
        min_width = ensure_power_of_two(min(face_widths))
        min_height = ensure_power_of_two(min(face_heights))

        # They're called CUBEmaps, dingus...
        if self.require_cube:
            dimension = min(min_width, min_height)
            min_width, min_height = dimension, dimension

        # Insert grumbling here about tuples being immutable...
        result_data = list(face_data)

        for i in range(len(BLENDER_CUBE_MAP)):
            face_width, face_height = face_widths[i], face_heights[i]
            if face_width != min_width or face_height != min_height:
                face_name = BLENDER_CUBE_MAP[i][:-4].upper()
                self._report.msg("Resizing face '{}' from {}x{} to {}x{}", face_name,
                                 face_width, face_height, min_width, min_height,
                                 indent=1)
                result_data[i] = scale_image(face_data[i], face_width, face_height,
                                                         min_width, min_height)
            self._report.progress_increment()
        return min_width, min_height, tuple(result_data)
