#!/usr/bin/env python3
# VISION to GIMP palette converter
# Outputs GIMP palettes to stdout
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
# -*- coding: utf8 -*-

import array
import argparse
import struct
from os import getcwd
from os.path import abspath
import sys
import json
sys.path.append(abspath(getcwd() + "/.."))


class IffPalReader:

    PAL_FMT = "<3B"

    def __init__(self, iff_fname):
        from iff_read import IffReader
        self.iff = IffReader(iff_fname)
        self.pal = None
        self.pxld = array.array("B")

    def parse_pal_form(self, pal_form):
        pal_read = 4
        pal = ''
        pald = array.array("B")

        while pal_read < pal_form["length"]:
            pal_chunk = self.iff.read_data()

            if pal_chunk["type"] == 'chunk' and pal_chunk["name"] == b"NAME":
                pal = 'external:{}'.format(self.parse_cstr(pal_chunk["data"]))
            elif pal_chunk["type"] == 'chunk' and pal_chunk["name"] == b"CMAP":
                pal = 'embedded'
                pald.frombytes(pal_chunk["data"])

            pal_read += 8 + pal_chunk["length"]

        return pal, pald

    def parse_cstr(self, data, offset=0):
        cstr = bytearray()
        while data[offset] != 0:
            cstr.append(data[offset])
            offset += 1
        return cstr.decode("ascii", "ignore")

    def read(self):
        root_form = self.iff.read_data()

        if root_form["name"] == b"BITM":
            fram_form = self.iff.read_data()

            if fram_form["name"] == b"FRAM":
                fram_read = 4
                while fram_read < fram_form["length"]:
                    mdata = self.iff.read_data()

                    if mdata["type"] == 'form' and mdata["name"] == b'PAL ':
                        self.pal, self.pald = self.parse_pal_form(mdata)

                    fram_read += 8 + mdata["length"]
            else:
                print_iff_data(fram_form)
                raise TypeError("Invalid MAT! (no FRAM form found! first "
                                "child of root form is {})".format(
                                    fram_form["name"]))
        elif root_form["name"] == b"PAL ":
            self.pal, self.pald = self.parse_pal_form(mdata)
        else:
            print_iff_data(root_form)
            raise TypeError("Invalid root form! (must be either BITM or PAL,"
                            "root form is %s)" % root_form["name"])


def print_iff_data(iffthing):
    print("--- IFF data ---")
    print("type:", iffthing["type"])
    print("name:", iffthing["name"])
    print("length:", iffthing["length"])
    print("offset:", iffthing["offset"])
    print("data:", iffthing.get("data", "None"))

if __name__ == '__main__':

    argp = argparse.ArgumentParser(
        description="Convert a VISION engine palette to a GIMP palette. Can "
        "convert palettes embedded in MAT files, or PAL files.")

    argp.add_argument('mat', action='store', metavar='XXXXXXXX.mat',
                      help="The MAT to extract the palette from.")

    argp.add_argument('-f', '--out-file', action='store', nargs='?',
                      metavar='FILE', dest='out_file', required=False,
                      help="The file to output the data to.")

    args = argp.parse_args()

    matf = getattr(args, 'mat')
    out_fname = getattr(args, 'out_file')

    mat_reader = IffPalReader(matf)
    mat_reader.read()

    gpal_head = """GIMP Palette
Name: {}
Columns: 16
#
"""

    gpal_colr = "{:3d} {:3d} {:3d}\tIndex {:d}"

    if mat_reader.pal == "embedded":
        gpal = gpal_head.format(matf) + "\n".join(
            [gpal_colr.format(
                mat_reader.pald[x * 3],
                mat_reader.pald[x * 3 + 1],
                mat_reader.pald[x * 3 + 2],
                x
            ) for x in range(len(mat_reader.pald) // 3)]
        )

        if out_fname is not None:
            outfile = open(out_fname, "w")
            outfile.write(gpal)
            outfile.close()
        else:
            print(gpal)
    else:
        print("{} uses an external palette: {}.pal".format(
            matf, mat_reader.pal[9:]))
