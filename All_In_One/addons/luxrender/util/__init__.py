# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
# ***** END GPL LICENCE BLOCK *****
#
"""
Combined Base64 + zlib encoder/decoder for embedded file data
"""

from copy import deepcopy


def dict_merge(*args):
    vis = {}
    for vis_dict in args:
        vis.update(deepcopy(vis_dict))  # need a deepcopy since nested dicts return references!
    return vis


import base64, io, os, time, zlib


class bEncoder(object):
    """
    Encode binary files to text using base64(zlib.compress(file))
    """

    def __init__(self):
        self.last_encode_size = 0

    def Encode_File2File(self, fSrc_name, fDes_name):
        with open(fSrc_name, 'rb') as fSrc:
            with open(fDes_name, 'w') as fDes:
                self._Encode(fSrc, fDes)

    def Encode_File2String(self, fSrc_name):
        with open(fSrc_name, 'rb') as fSrc:
            with io.StringIO() as fDes:
                fDes.name = '<string>'
                self._Encode(fSrc, fDes)

                return fDes.getvalue()

    def _Encode(self, fSrc, fDes):
        """
        Assumes that fSrc and fDes are already-opened file-like objects
        """

        start_time = time.time()

        input_filename = os.path.basename(fSrc.name)
        filelen = fSrc.seek(0, io.SEEK_END)
        fSrc.seek(0)
        fDes.seek(0)

        # Compress with a specific set of parameters
        comp_obj = zlib.compressobj(
            9,  # compression level
        )

        deflated = comp_obj.compress(
            fSrc.read()
        )
        deflated += comp_obj.flush()

        fDes.write(
            base64.encodebytes(
                deflated
            ).decode()
        )

        self.last_encode_size = fDes.tell()
        elapsed = time.time() - start_time
        print('bEncode %s : %d bytes -> %d bytes -> %d bytes: %0.2f%% : %0.2f sec : %0.2f kb/sec' % (
            input_filename,
            filelen,
            len(deflated),
            self.last_encode_size,
            100 * self.last_encode_size / filelen,
            elapsed,
            filelen / elapsed / 1024)
        )


class bDecoder(object):
    """
    Decode binary files from text using base64(zlib.compress(file))
    """

    def Decode_File2File(self, fSrc_name, fDes_name):
        with open(fSrc_name, 'rb') as fSrc:
            with open(fDes_name, 'wb') as fDes:
                self._Decode(fSrc, fDes)

    def Decode_File2String(self, fSrc_name):
        with open(fSrc_name, 'rb') as fSrc:
            with io.StringIO() as fDes:
                fDes.name = '<string>'
                self._Decode(fSrc, fDes)
                return fDes.getvalue()

    def Decode_String2File(self, in_string, fDes_name):
        fSrc = io.BytesIO()
        fSrc.write(in_string.encode())
        with open(fDes_name, 'wb') as fDes:
            fSrc.name = fDes.name
            self._Decode(fSrc, fDes)

    def _Decode(self, fSrc, fDes):
        """
        Assumes that fSrc and fDes are already-opened file-like objects
        """

        start_time = time.time()

        input_filename = os.path.basename(fSrc.name)
        filelen = fSrc.seek(0, io.SEEK_END)
        fSrc.seek(0)
        fDes.seek(0)

        decomp_obj = zlib.decompressobj()

        fDes.write(
            decomp_obj.decompress(
                base64.decodebytes(
                    fSrc.read()
                )
            )
        )

        outlen = fDes.tell()
        elapsed = time.time() - start_time
        print('bDecode %s : %d bytes -> %d bytes : %0.2f%% : %0.2f sec : %0.2f kb/sec' % (
            input_filename,
            filelen,
            outlen,
            100 * outlen / filelen,
            elapsed,
            filelen / elapsed / 1024)
        )


def bencode_file2file(in_filename, out_filename):
    be = bEncoder()
    be.Encode_File2File(in_filename, out_filename)


def bencode_file2string(in_filename):
    be = bEncoder()
    return be.Encode_File2String(in_filename)


def bencode_file2string_with_size(in_filename):
    be = bEncoder()
    en = be.Encode_File2String(in_filename)
    sz = be.last_encode_size
    return en, sz


def bdecode_file2file(in_filename, out_filename):
    be = bDecoder()
    be.Decode_File2File(in_filename, out_filename)


def bdecode_file2string(in_filename):
    be = bDecoder()
    return be.Decode_File2String(in_filename)


def bdecode_string2file(in_string, out_filename):
    be = bDecoder()
    be.Decode_String2File(in_string, out_filename)
