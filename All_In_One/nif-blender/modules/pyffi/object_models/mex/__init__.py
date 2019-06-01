"""Format classes and metaclasses for binary file formats described by a
mexscript file, and mexscript parser for converting the mexscript description
into Python classes.
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2012, Python File Format Interface
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

import logging

import pyffi.object_models
import pyffi.object_models.simple_type


class _MetaMexFileFormat(pyffi.object_models.MetaFileFormat):
    """Converts the mex script into an archive parser."""

    def __init__(self, name, bases, dct):
        super(_MetaMexScriptFileFormat, self).__init__(name, bases, dct)

        # open the mex script
        mexfilename = dct.get('mexfilename')
        if mexfilename:
            mexfile = self.openfile(mexfilename, self.mexfilepath)
            # XXX todo: parse the script


class MexFileFormat(pyffi.object_models.FileFormat):
    """This class can be used as a base class for file formats
    described by a mexscript file.
    """
    mexfilename = None  #: Override.
    mexfilepath = None  #: Override.
    logger = logging.getLogger("pyffi.object_models.mex")

    class FileInfo:
        """Stores information about a file in an archive."""

        stream = None
        """The stream in which the file is archived."""

        filename = ""
        """Name of the file."""

        fileformat = None
        """Potentially, the format of the file."""

        offset = None
        """Offset in the archive."""

        size = None
        """Compressed size in the archive."""

        compression = None
        """The type of compression."""

        uncompressed_size = None
        """Uncompressed size in the archive."""

        offset_offset = None
        """Offset of the offset of this file in the archive."""

        offset_size = None
        """Offset of the size of this file in the archive."""

        offset_uncompressed_size = None
        """Offset of the uncompressed size in the archive."""

        def data(self):
            """Extract the file data from the archive."""
            # look up the data in the stream
            self.stream.seek(self.offset)
            # read it, and uncompress if needed
            if self.compression is None:
                data = self.stream.read(self.size)
            else:
                raise NotImplementedError("compression not yet implemented")
            # convert bytes into the desired format
            if fileformat is None:
                return data
            else:
                raise NotImplementedError("formatting not yet implemented")

    class Data(pyffi.object_models.FileFormat.Data):
        """Process archives described by mexscript files."""

        fileinfos = []
        """List of file info's in the data."""

        def read(self, stream):
            """Open and read a full archive from stream while parsing the
            mexscript. The files in the archive are not actually read,
            but their names, location, size, and compression type, are
            recorded.

            If you want to open the archive without processing the
            full list of files, use :meth:`open`.

            :param stream: The archive to read from.
            :type stream: file
            """
            raise NotImplementedError
