# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy

from array import array
import itertools
import os
from struct import unpack
import sys
import xml.etree.ElementTree as ET


class MayaCache(object):
    """
    MayaCache(filepath)

        A class to store and read all information of a Maya Cache.
        'filepath' should be the .xml file from the Maya Cache.
    """

    def __init__(self, filepath):
        if not os.path.isfile(filepath):
            raise_cachefile_error(2, filepath)
        elif not os.path.splitext(filepath)[-1].lower() == ".xml":
            raise_cachefile_error(5,
                "The file is not a valid Maya Cache file", filepath)
        self.__xmlfile = filepath
        self.__name = os.path.splitext(os.path.split(filepath)[-1])[0]
        self.__cacheinfo = self._parse_xmlfile(filepath)
        self.__mc_filepath = self._open_mcfile()

    def __str__(self):
        prettyprint = "{line}\n"\
                "** Maya Cache File: {self.name}.xml **\n"\
                "{line}\n"\
                "- Cache type: {self.cachetype}\n"\
                "- Time per frame: {self.timeperframe}\n"\
                "- Frames per second: {fps}\n"\
                "- Start time: {starttime} seconds\n"\
                "- Start frame: {startframe}\n"\
                "- End time:  {endtime} seconds\n"\
                "- End frame: {endframe}\n"\
                "- Number of channels: {numchannels}".format(self=self,
                        line="*" * (27 + len(self.name)),
                        starttime=self._ticks_to_seconds(self.starttime),
                        startframe=self.startframe,
                        endtime=self._ticks_to_seconds(self.endtime),
                        endframe=self.endframe,
                        fps=self.fps,
                        numchannels=self.numchannels)
        if self.numchannels:
            prettyprint += "\n- Channels:\n  - "
            prettyprint += "\n  - ".join(self.channels)

        return prettyprint

    @property
    def name(self):
        return self.__name

    @property
    def cachetype(self):
        return self.__cacheinfo['cachetype']

    @property
    def timeperframe(self):
        return self.__cacheinfo['timeperframe']

    @property
    def fps(self):
        return 6000 / self.timeperframe

    @property
    def starttime(self):
        return self.__cacheinfo['cachestarttime']

    @property
    def startframe(self):
        return int(self._ticks_to_frames(self.starttime))

    @property
    def endtime(self):
        return self.__cacheinfo['cacheendtime']

    @property
    def endframe(self):
        return int(self._ticks_to_frames(self.endtime))

    @property
    def numchannels(self):
        return len(self.__cacheinfo['channels'])

    @property
    def channels(self):
        return sorted([self.__cacheinfo['channels'][k]['channelname']
                for k in self.__cacheinfo['channels']])

    @staticmethod
    def _parse_xmlfile(filepath):
        """
        _parse_xmlfile(filepath)

            Parses the xml file accompanying the mc file for the Maya Cache.
            Returns all needed information as a dict.
        """

        # Parse the file to a tree and get the relevant information.
        tree = ET.parse(filepath)
        cache = tree.getroot()
        cachename = cache.tag
        cachetype = cache.find("cacheType").attrib['Type']
        cacheformat = cache.find("cacheType").attrib['Format']
        timerange = cache.find("time").attrib['Range']
        timerange_split = timerange.split("_")
        if len(timerange_split) > 2:
            raise Exception("The time range {} is not valid.".
                    format(timerange))
        cachestarttime = int(timerange.split("-")[0])
        cacheendtime = int(timerange.split("-")[1])
        timeperframe = int(cache.find("cacheTimePerFrame").
                attrib['TimePerFrame'])
        cacheversion = float(cache.find("cacheVersion").attrib['Version'])
        channels = cache.find("Channels").getchildren()

        # Do sanity checks for some values.
        if cachename != "Autodesk_Cache_File":
            raise Exception("Cache file is unsupported type {}, should be"\
                    " 'Autodesk_Cache_File'.".format(cachename))
        if cachetype not in ("OneFile", "OneFilePerFrame"):
            raise Exception("Cache type is unsupported type '{}', should be "\
                    "'OneFile' or 'OneFilePerFrame'.".format(cachetype))
        if cacheformat != "mcc":
            raise Exception("Cache format is unsupported format {}, should be"\
                    " 'mcc'.".format(cacheformat))
        if str(cacheversion) != "2.0":
            raise Exception("Cache version {} is not supported, only version"\
                    " 2.0 is supported.".format(cacheversion))

        # Get the information per channel.
        channels_info = dict()
        for channel in channels:
            channel_info = {attr.lower(): channel.attrib[attr]
                    for attr in channel.attrib if "channel" in channel.tag}
            channels_info[channel.tag] = channel_info

        # Store all the info in the cache_info dictionary.
        cache_info = dict()
        cache_info['cachetype'] = cachetype
        cache_info['cachestarttime'] = cachestarttime
        cache_info['cacheendtime'] = cacheendtime
        cache_info['timeperframe'] = timeperframe
        cache_info['channels'] = channels_info

        return cache_info

    def _ticks_to_frames(self, ticks):
        return ticks / self.timeperframe

    def _frames_to_ticks(self, frames):
        return frames * self.timeperframe

    def _ticks_to_seconds(self, ticks):
        return ticks / 6000

    def _seconds_to_ticks(self, seconds):
        return seconds * 6000

    def _open_mcfile(self, framenumber=None):
        """
        _open_mcfile(framenumber=None)

            First checks the type of the Maya Cache. According to this
            it opens the correct .mc file, checks the header and then returns
            the open file object at the current position (after the header).
        """

        # Check the cache type and get the right .mc file for this.
        (base, _) = os.path.splitext(self.__xmlfile)
        if self.cachetype == "OneFile":
            mc_filepath = "".join((base, ".mc"))
        elif self.cachetype == "OneFilePerFrame":
            if not framenumber:
                raise TypeError("The frame number is not specified.")
            elif not isinstance(framenumber, int):
                # Convert to int or raise an error.
                try:
                    framenumber = int(framenumber)
                except ValueError:
                    raise TypeError("The frame number should be an integer.")
            mc_filepath = "".join((base,
                    "Frame{}".format(framenumber), ".mc"))
        else:
            mc_filepath = None
        if not mc_filepath:
            raise_cachefile_error(2, "",
                    "No Maya Cache .mc file could be found")
        # Check if the file exists.
        if not os.path.isfile(mc_filepath):
            raise_cachefile_error(2, mc_filepath)
        # Open the file and read till the end of the header.
        with open(mc_filepath, "rb") as f:
#        f = open(mc_filepath, "rb")
            blocktag = f.read(4).decode()
            if blocktag and blocktag != "FOR4":
                raise_runtime_error("'FOR4' (at start of file)")
            headersize = unpack(">l", f.read(4))[0]
            f.seek(headersize, 1)

            self.__mcfile_after_header = f.tell()

        return mc_filepath

    def read_channel_at_time(self, **kwargs):
        """
        read_channel_at_time(**kwargs)

            channel=None,
            cachetime=None,

            Reads the channel at the specified time. Returns the list
            of vertex positions (as tuples per vertex) at that time.
            Returns None if no info is found (non existing channel, wrong time
            or end of file).

            Warning: Nice to use to get the information for 1 channel at the
            specified time, but quite slow if you want to process all the
            frames for 1 or more channels. Because it looks up the time and
            the channel every time for every object at every frame.
            Could make it so that if no cachetime is given, it will read every
            frame. And if no channel(s) are given it will read every channel.
        """

        # Get the keyword args, default to None if it's not given.
        channel = kwargs.get("channel", None)
        cachetime = kwargs.get("cachetime", None)
        cachetype = self.cachetype
        mc_filepath = self.__mc_filepath
        with open(mc_filepath, "rb") as f:
            f.seek(self.__mcfile_after_header)
            # Raise appropriate error if one of the keyword args is not given.
            if not channel:
                raise TypeError("read_channel() missing required keyword"\
                        " argument: 'channel'")
            if not cachetime:
                raise TypeError("read_channel() missing required keyword"\
                        " argument: 'cachetime'")

            # Now continue with reading the file.
            if cachetype == "OneFile":  # For cachetype 'OneFile'.
                ticks = self.starttime
                while ticks <= self.endtime:  # Don't loop further then endtime.
                    blocktag = f.read(4).decode()
                    if blocktag and blocktag != "FOR4":
                        raise_runtime_error(
                                "'FOR4' (at beginning of time block)")
                    elif not blocktag:  # We hit the end of the file.
                        return None
                    blocksize = unpack(">l", f.read(4))[0]
                    bytes_read = 0
                    blocktag = f.read(4).decode()
                    bytes_read += 4
                    if blocktag != "MYCH":
                        raise_runtime_error("'MYCH'")
                    blocktag = f.read(4).decode()
                    bytes_read += 4
                    if blocktag != "TIME":
                        raise_runtime_error("'TIME'")
                    f.seek(4, 1)  # Skip, not needed.
                    bytes_read += 4
                    ticks = unpack(">l", f.read(4))[0]
                    bytes_read += 4
                    if ticks == cachetime:  # Time found.
                        while bytes_read < blocksize:
                            blocktag = f.read(4).decode()
                            bytes_read += 4
                            if blocktag != "CHNM":
                                raise_runtime_error("'CHNM'")
                            channelname_size = unpack(">l", f.read(4))[0]
                            bytes_read += 4
                            # The channelname is padded out to 32 bit
                            # boundaries. So we may need ot read more
                            # then channelname_size.
                            if channelname_size % 4 != 0:
                                bytes_to_read = channelname_size + (4 -
                                        (channelname_size % 4))
                            else:
                                bytes_to_read = channelname_size
                            channelname = f.read(
                                    channelname_size - 1).decode()
                            f.seek(bytes_to_read -
                                    (channelname_size - 1), 1)
                            bytes_read += bytes_to_read
                            if channelname != channel:
                                # Skip to the size of the datablock. So we can
                                # skip to the next channel.
                                f.seek(16, 1)
                                datasize = unpack(">l", f.read(4))[0]
                                f.seek(datasize, 1)
                                bytes_read += (16 + 4 + datasize)
                                continue
                            blocktag = f.read(4).decode()
                            bytes_read += 4
                            if blocktag != "SIZE":
                                raise_runtime_error("'SIZE'")
                            f.seek(4, 1)  # Skip, not needed.
                            bytes_read += 4
                            num_vertices = unpack(">l", f.read(4))[0]
                            bytes_read += 4
                            dataformat = f.read(4).decode()
                            bytes_read += 4
                            datasize = unpack(">l", f.read(4))[0]
                            bytes_read += 4
                            if dataformat == "FVCA":
                                # Do an extra check.
                                # num_vertices * 3 (x, y, z) * 4 (size of
                                # float) should be the same as datasize.
                                if not num_vertices * 3 * 4 == datasize:
                                    raise ValueError(
                                            "The datasize is not correct")
                                vertexarray = array('f')
                            elif dataformat == "DVCA":
                                # Do an extra check.
                                # num_vertices * 3 (x, y, z) * 8 (size of
                                # double) should be the same as datasize.
                                if not num_vertices * 3 * 8 == datasize:
                                    raise ValueError(
                                            "The datasize is not correct")
                                vertexarray = array('d')
                            else:
                                raise ValueError(
                                        "Wrong data format: {}".format(
                                                dataformat))
                            vertexarray.fromfile(f, num_vertices * 3)
                            if sys.byteorder == "little":
                                vertexarray.byteswap()
                            vertex_position_list = [i for i in grouper(
                                    3, vertexarray)]
                            return vertex_position_list
                    else:   # Go to the next time block.
                        # We already read 16 bytes, so we should skip to
                        # blocksize - 16 bytes.
                        f.seek((blocksize - 16), 1)
            else:       # The cachetype is 'OneFilePerFrame'
                pass    # Not implemented yet.

    def read_channels(self, **kwargs):
        """
        read_channels(**kwargs)

            channels=self.channels,
            starttime=self.starttime,
            endtime=self.endtime,

            Reads the channel(s) in the specified timerange.
            If no channels are given, it will read all channels. If no
            timerange is given it will use the timerange from the cache file.
            Returns a dictionary or None:
            {<time1>: {<channel1>: <vertexarray1>,
                       <channel2>: <vertexarray2>, ... etc.},
             <time2>: {channel1>: <vertexarray1>, ... etc.}
            }
        """

        channels = kwargs.get("channel", self.channels)
        starttime = kwargs.get("starttime", self.starttime)
        endtime = kwargs.get("endtime", self.endtime)
        cachetype = self.cachetype
        mc_filepath = self.__mc_filepath

        timedict = dict()

        # Only cachetype 'OneFile' supported for now.
        if not cachetype == "OneFile":
            raise TypeError("Only cachetype 'OneFile' supported for now...")

        with open(mc_filepath, "rb") as f:
            f.seek(self.__mcfile_after_header)

            # Now continue with reading the file.
            ticks = starttime
            while ticks <= endtime:  # Don't loop further then endtime.
                blocktag = f.read(4).decode()
                if blocktag and blocktag != "FOR4":
                    raise_runtime_error(
                            "'FOR4' (at beginning of time block)")
                elif not blocktag:  # We hit the end of the file.
                    return timedict
                blocksize = unpack(">l", f.read(4))[0]
                bytes_read = 0
                blocktag = f.read(4).decode()
                bytes_read += 4
                if blocktag != "MYCH":
                    raise_runtime_error("'MYCH'")
                blocktag = f.read(4).decode()
                bytes_read += 4
                if blocktag != "TIME":
                    raise_runtime_error("'TIME'")
                f.seek(4, 1)  # Skip, not needed.
                bytes_read += 4
                ticks = unpack(">l", f.read(4))[0]
                bytes_read += 4
                if starttime <= ticks <= endtime:  # Time in range.
                    channeldict = dict()
                    while bytes_read < blocksize:
                        blocktag = f.read(4).decode()
                        bytes_read += 4
                        if blocktag != "CHNM":
                            raise_runtime_error("'CHNM'")
                        channelname_size = unpack(">l", f.read(4))[0]
                        bytes_read += 4
                        # The channelname is padded out to 32 bit
                        # boundaries. So we may need to read more
                        # then channelname_size.
                        if channelname_size % 4 != 0:
                            bytes_to_read = channelname_size + (4 -
                                    (channelname_size % 4))
                        else:
                            bytes_to_read = channelname_size
                        channelname = f.read(channelname_size - 1).decode()
                        f.seek(bytes_to_read - (channelname_size - 1), 1)
                        bytes_read += bytes_to_read
                        if not channelname in channels:
                            # Skip the size of the datablock. So we reach the
                            # next channel.
                            f.seek(16, 1)
                            datasize = unpack(">l", f.read(4))[0]
                            f.seek(datasize, 1)
                            bytes_read += (16 + 4 + datasize)
                            continue
                        blocktag = f.read(4).decode()
                        bytes_read += 4
                        if blocktag != "SIZE":
                            raise_runtime_error("'SIZE'")
                        f.seek(4, 1)  # Skip, not needed.
                        bytes_read += 4
                        num_vertices = unpack(">l", f.read(4))[0]
                        bytes_read += 4
                        dataformat = f.read(4).decode()
                        bytes_read += 4
                        datasize = unpack(">l", f.read(4))[0]
                        bytes_read += 4
                        if dataformat == "FVCA":
                            # Do an extra check.
                            # num_vertices * 3 (x, y, z) * 4 (size of
                            # float) should be the same as datasize.
                            if num_vertices * 3 * 4 != datasize:
                                raise ValueError(
                                        "The datasize is not correct")
                            vertexarray = array('f')
                        elif dataformat == "DVCA":
                            # Do an extra check.
                            # num_vertices * 3 (x, y, z) * 8 (size of
                            # double) should be the same as datasize.
                            if num_vertices * 3 * 8 != datasize:
                                raise ValueError(
                                        "The datasize is not correct")
                            vertexarray = array('d')
                        else:
                            raise ValueError(
                                    "Wrong data format: {}".format(
                                            dataformat))
                        vertexarray.fromfile(f, num_vertices * 3)
                        bytes_read += datasize
                        if sys.byteorder == "little":
                            vertexarray.byteswap()
                        vertex_position_list = (i for i in grouper(
                                3, vertexarray))
                        channeldict[channelname] = vertex_position_list
                    else:   # Go to the next time block.
                        timedict[ticks] = channeldict

            return timedict


def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def raise_cachefile_error(errno, filepath,
        strerror="Maya Cache file not found"):
    raise OSError(errno, strerror, filepath)


def raise_runtime_error(tag):
    raise RuntimeError("The cachefile seems corrupt."\
            " {} tag not found".format(tag))


def match_channels(channels, objects):
    """
    match_channels(channels, objects)

        Try to find the matching objects for the channelnames.
        Returns the matches as a dictionary. Channels that could not be
        matched have a value of None.
    """

    objects_channels_match = dict()
    for ob in objects:
        for ch in channels:
            if ob.name in ch:
                objects_channels_match[ob] = ch

    return objects_channels_match


def load(operator, context, filepath, *args, **kwargs):
    """
    load(operator, context, filepath, *args, **kwargs)

        Called by the user interface or another script.
        This function checks and passes the file and sends the data off.
    """

    from time import time

    now = time()

    (base, ext) = os.path.splitext(filepath)
    if ext.lower() == ".xml":
        xml_filepath = filepath
    elif ext.lower() == ".mc":
        xml_filepath = "".join((base, ".xml"))
    else:
        raise_cachefile_error(5,
                "The file is not a valid Maya Cache file", filepath)
    if not os.path.isfile(xml_filepath):
            raise_cachefile_error(2, xml_filepath)
    mayacache = MayaCache(xml_filepath)
    scene_objects = [ob for ob in bpy.data.objects if ob.type == 'MESH']
    matchlist = match_channels(mayacache.channels, scene_objects)

    def updateMesh(ob, fr, **kwargs):
            vertex_positions = kwargs.get("vertex_positions")
            channel = kwargs.get("channel")
            # Insert new shape key.
            ob.shape_key_add('frame_%.4d' % fr)

            index = len(ob.data.shape_keys.key_blocks) - 1
            ob.active_shape_key_index = index

            shapeKeys = ob.data.shape_keys
            verts = shapeKeys.key_blocks[index].data

            pos = vertex_positions[mayacache._frames_to_ticks(fr)][channel]

            for v in verts:
                x, y, z = pos.__next__()
                v.co[:] = x, y, z

            # Insert keyframes
            shapeKeys.key_blocks[index].value = 0.0
            shapeKeys.key_blocks[index].keyframe_insert('value', frame=fr - 1)

            shapeKeys.key_blocks[index].value = 1.0
            shapeKeys.key_blocks[index].keyframe_insert('value', frame=fr)

            shapeKeys.key_blocks[index].value = 0.0
            shapeKeys.key_blocks[index].keyframe_insert('value', frame=fr + 1)

            ob.data.update()

    print("\nProcessing Maya Cache '{mc.name}'...\n"\
          "Framerange: {mc.startframe} - {mc.endframe}\n"\
          "Number of channels/objects: {len}".format(mc=mayacache,
                  len=len(mayacache.channels)))

    vertex_positions = mayacache.read_channels()
    for frame in range(mayacache.startframe, mayacache.endframe + 1):
        for ob in matchlist:
            bpy.context.scene.frame_current = frame
            if frame == mayacache.startframe:
                if not hasattr(ob.data.shape_keys, "key_blocks"):
                    ob.shape_key_add('Basis')
                    ob.data.update()
            bpy.context.scene.objects.active = ob
            updateMesh(ob, frame, vertex_positions=vertex_positions,
                    channel=matchlist[ob])

    posttime = time()

    processing_time = posttime - now
    print("\nProcessed in {:.2f} seconds".format(processing_time))

    bpy.context.scene.frame_start = mayacache.startframe
    bpy.context.scene.frame_end = mayacache.endframe
    bpy.context.scene.frame_current = mayacache.startframe

    return {'FINISHED'}
