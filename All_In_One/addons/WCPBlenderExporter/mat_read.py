# -*- coding: utf8 -*-
# Blender WCP IFF mesh import/export script by Kevin Caccamo
# Copyright © 2013-2016 Kevin Caccamo
# E-mail: kevin@ciinet.org
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# <pep8-80 compliant>

# MAT reader
import struct
import array
import os
import os.path
import threading
from . import iff_read
from multiprocessing import cpu_count


class MATReader:

    def __init__(self, matfpath):
        self.matfpath = matfpath
        self.iff_reader = iff_read.IffReader(matfpath)
        self.palette = None  # To be initialized in read_palette
        self.pixels = None  # To be initialized in read_info

    def look_for(self, fname, in_dir, par_dir=True):
        from os.path import join, normpath, isfile, isdir
        mfiledir = self.matfpath[:self.matfpath.rfind(os.sep)]
        if par_dir:
            abs_dir = normpath(join(mfiledir, ".."))
            dirents = os.listdir(abs_dir)
            # Enter in_dir
            for dirent in dirents:
                if (dirent.lower() == in_dir.lower() and
                        isdir(join(abs_dir, dirent))):
                    abs_dir = normpath(join(abs_dir, dirent))
                    break
        else:
            # Enter in_dir
            abs_dir = normpath(join(mfiledir, in_dir))

        # Get the file
        dirents = os.listdir(abs_dir)
        for dirent in dirents:
            if (dirent.lower() == fname.lower() and
                    isfile(join(abs_dir, dirent))):
                return normpath(join(abs_dir, dirent))

    def read_info(self, info_chunk):
        dimensions = struct.unpack_from("<II", info_chunk["data"], 0)
        self.img_width, self.img_height = dimensions
        # Image width * height * 4 channels per pixel (RGB + Alpha)

    def read_palette(self, cmap_chunk):
        # Each colour is three bytes (R, G, B)
        if cmap_chunk["name"] == b"CMAP":
            self.palette = array.array("B", cmap_chunk["data"])
            return self.palette
        elif cmap_chunk["name"] == b"NAME":
            palname = cmap_chunk["data"].decode("ascii").strip(" \x00\t")
            palname = palname.lower() + ".pal"
            palpath = self.look_for(palname, "pal")
            if palpath is not None:
                palreader = iff_read.IffReader(palpath)
                palform = palreader.read_data()
                if palform["type"] == "form" and palform["name"] == b"PAL ":
                    paldata = palreader.read_data()
                    self.palette = array.array("B", paldata["data"])
                    return self.palette

        # Generate placeholder grayscale palette
        gspal = []
        for x in range(256): gspal.extend([x] * 3)
        self.palette = array.array("B", gspal)
        return self.palette

    def read_pxls(self, pxls_chunk):
        self.pixels = array.array(
            'B', [0 for x in range(self.img_width * self.img_height * 4)])
        palpixels = array.array("B", pxls_chunk["data"])

        def modify_pixels(start, end):
            # One byte references a colour in the palette
            for cpxl in range(start, end):
                palref = palpixels[cpxl]

                self.pixels[cpxl * 4:cpxl * 4 + 3] = (
                    self.palette[palref * 3:palref * 3 + 3])
                # Colour at index 0 is transparent by default.
                self.pixels[cpxl * 4 + 3] = 0 if palref == 0 else 255

        cores = cpu_count()
        threads = []
        pxl_amt = len(pxls_chunk["data"]) // cores
        for pxl_set in range(cores):
            pxl_start = pxl_set * pxl_amt
            pxl_end = pxl_start + pxl_amt
            if pxl_set == cores - 1:
                pxl_end = len(pxls_chunk["data"])
            thread = threading.Thread(
                target=modify_pixels, args=(pxl_start, pxl_end))
            threads.append(thread)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def read_pxls_flipped(self, pxls_chunk):
        self.pixels = array.array(
            'B', [0 for x in range(self.img_width * self.img_height * 4)])
        palpixels = array.array("B", pxls_chunk["data"])

        def modify_rows(start_row, end_row):
            # For reader threads
            for row in range(start_row, end_row):
                rrow = self.img_height - row - 1
                for col in range(self.img_width):
                    ipxl = self.img_height * row + col
                    cpxl = rrow * self.img_height + col
                    palref = palpixels[cpxl]

                    self.pixels[ipxl * 4:ipxl * 4 + 3] = (
                        self.palette[palref * 3:palref * 3 + 3])
                    # Colour at index 0 is transparent by default.
                    self.pixels[ipxl * 4 + 3] = 0 if palref == 0 else 255

        cores = cpu_count()
        threads = []
        row_amt = self.img_height // cores
        for row_set in range(cores):
            row_start = row_set * row_amt
            row_end = row_start + row_amt
            if row_set == cores - 1:
                row_end = self.img_height
            thread = threading.Thread(
                target=modify_rows, args=(row_start, row_end))
            threads.append(thread)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def read_alph(self, alph_chunk):
        # One byte for each pixel. The alpha channel is inverted,
        # so 255 would be fully transparent, and 0 is fully opaque
        for apxl in range(alph_chunk["length"]):
            self.pixels[apxl * 4 + 3] = 255 - (struct.unpack_from(
                "<B", alph_chunk["data"], apxl)[0])

    def read(self, blender=False):
        root_form = self.iff_reader.read_data()
        if root_form["name"] == b"BITM":
            inner_rform = self.iff_reader.read_data()
            if inner_rform["name"] == b"FRAM":
                inner_rform_read = 4

                while inner_rform_read < inner_rform["length"]:

                    mat_data = self.iff_reader.read_data()
                    if (mat_data["type"] == "chunk" and
                            mat_data["name"] == b"INFO"):
                        self.read_info(mat_data)

                    elif (mat_data["type"] == "form" and
                            mat_data["name"] == b"PAL "):
                        self.read_palette(self.iff_reader.read_data())

                    elif (mat_data["type"] == "chunk" and
                            mat_data["name"] == b"PXLS"):
                        if blender:
                            self.read_pxls_flipped(mat_data)
                        else:
                            self.read_pxls(mat_data)

                    elif (mat_data["type"] == "chunk" and
                            mat_data["name"] == b"ALPH"):
                        self.read_alph(mat_data)

                    inner_rform_read += mat_data["length"] + 8
            else:
                raise TypeError("Invalid texture! (root form is {})".format(
                                inner_rform["name"]))
        else:
            raise TypeError("Invalid texture! (root form is {})".format(
                            root_form["name"]))
        self.iff_reader.close()

    def flip_y(self):
        # Flip the image vertically, row by row
        img_rows = array.array("B")

        for rowidx in range(self.img_height):
            # Get each row of pixels, and put them into a list of pixel rows
            cur_row_start = (self.img_height - rowidx) * self.img_width * 4
            cur_row_end = cur_row_start + self.img_width * 4

            img_rows.extend(self.pixels[cur_row_start:cur_row_end])

        self.pixels = img_rows
