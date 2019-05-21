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

import enum
from pathlib import Path
from PyHSPlasma import *
import time
import weakref

_HEADER_MAGICK = b"KTH\x00"
_INDEX_MAGICK = b"KTI\x00"
_DATA_MAGICK = b"KTC\x00"
_ENTRY_MAGICK = b"KTE\x00"
_IMAGE_MAGICK = b"KTT\x00"
_MIP_MAGICK = b"KTM\x00"

@enum.unique
class _HeaderBits(enum.IntEnum):
    last_export = 0
    index_pos = 1


@enum.unique
class _IndexBits(enum.IntEnum):
    image_count = 0


@enum.unique
class _EntryBits(enum.IntEnum):
    image_name = 0
    mip_levels = 1
    image_pos = 2
    compression = 3
    source_size = 4
    export_size = 5
    last_export = 6
    image_count = 7
    tag_string = 8


class _CachedImage:
    def __init__(self):
        self.name = None
        self.mip_levels = 1
        self.data_pos = None
        self.image_data = None
        self.source_size = None
        self.export_size = None
        self.compression = None
        self.export_time = None
        self.modify_time = None
        self.image_count = 1
        self.tag = None

    def __str__(self):
        return self.name


class ImageCache:
    def __init__(self, exporter):
        self._exporter = weakref.ref(exporter)
        self._images = {}
        self._read_stream = hsFileStream()
        self._stream_handles = 0

    def add_texture(self, texture, num_levels, export_size, compression, images):
        image, tag = texture.image, texture.tag
        image_name = str(texture)
        key = (image_name, tag, compression)
        ex_method, im_method = self._exporter().texcache_method, image.plasma_image.texcache_method
        method = set((ex_method, im_method))
        if texture.ephemeral or "skip" in method:
            self._images.pop(key, None)
            return
        elif im_method == "rebuild":
            image.plasma_image.texcache_method = "use"

        image = _CachedImage()
        image.name = image_name
        image.mip_levels = num_levels
        image.compression = compression
        image.source_size = texture.image.size
        image.export_size = export_size
        image.image_data = images
        image.image_count = len(images)
        image.tag = tag
        self._images[key] = image

    def _compact(self):
        for key, image in self._images.copy().items():
            if image.image_data is None:
                self._images.pop(key)

    def __enter__(self):
        if self._stream_handles == 0:
            path = self._exporter().texcache_path
            if Path(path).is_file():
                self._read_stream.open(path, fmRead)
        self._stream_handles += 1
        return self

    def __exit__(self, type, value, tb):
        self._stream_handles -= 1
        if self._stream_handles == 0:
            self._read_stream.close()

    def get_from_texture(self, texture, compression):
        bl_image, tag = texture.image, texture.tag

        # If the texture is ephemeral (eg a lightmap) or has been marked "rebuild" or "skip"
        # in the UI, we don't want anything from the cache. In the first two cases, we never
        # want to cache that crap. In the latter case, we just want to signal a recache is needed.
        ex_method, im_method = self._exporter().texcache_method, texture.image.plasma_image.texcache_method
        method = set((ex_method, im_method))
        if method != {"use"} or texture.ephemeral:
            return None

        key = (str(texture), tag, compression)
        cached_image = self._images.get(key)
        if cached_image is None:
            return None

        # ensure the texture key generally matches up with our copy of this image.
        # if not, a recache will likely be triggered implicitly.
        if tuple(bl_image.size) != cached_image.source_size:
            return None

        # if the image is on the disk, we can check the its modify time for changes
        if cached_image.modify_time is None:
            # if the image is packed, the filepath will be some garbage beginning with
            # the string "//". There isn't much we can do with that, unless the user
            # happens to have an unpacked copy lying around somewheres...
            path = Path(bl_image.filepath_from_user())
            if path.is_file():
                cached_image.modify_time = path.stat().st_mtime
                if cached_image.export_time and cached_image.export_time < cached_image.modify_time:
                    return None
            else:
                cached_image.modify_time = 0

        # ensure the data has been loaded from the cache
        if cached_image.image_data is None:
            try:
                cached_image.image_data = tuple(self._read_image_data(cached_image, self._read_stream))
            except AssertionError:
                self._report.warn("Cached copy of '{}' is corrupt and will be discarded", cached_image.name, indent=2)
                self._images.pop(key)
                return None
        return cached_image

    def load(self):
        if self._exporter().texcache_method == "skip":
            return
        try:
            with self:
                self._read(self._read_stream)
        except AssertionError:
            self._report.warn("Texture Cache is corrupt and will be regenerated")
            self._images.clear()

    def _read(self, stream):
        if stream.size == 0:
            return
        stream.seek(0)
        assert stream.read(4) == _HEADER_MAGICK

        # if we use a bit vector to define our header strcture, we can add
        # new fields without having to up the file version, trashing old
        # texture cache files... :)
        flags = hsBitVector()
        flags.read(stream)

        # ALWAYS ADD NEW FIELDS TO THE END OF THIS SECTION!!!!!!!
        if flags[_HeaderBits.last_export]:
            self.last_export = stream.readDouble()
        if flags[_HeaderBits.index_pos]:
            index_pos = stream.readInt()
            self._read_index(index_pos, stream)

    def _read_image_data(self, image, stream):
        if image.data_pos is None:
            return None

        assert stream.size > 0
        stream.seek(image.data_pos)
        assert stream.read(4) == _IMAGE_MAGICK

        # unused currently
        image_flags = hsBitVector()
        image_flags.read(stream)

        # given this is a generator, someone else might change our stream position
        # between iterations, so we'd best bookkeep the position
        pos = stream.pos

        def _read_image_mips():
            for _ in range(image.mip_levels):
                nonlocal pos
                if stream.pos != pos:
                    stream.seek(pos)
                assert stream.read(4) == _MIP_MAGICK

                # this should only ever be image data...
                # store your flags somewhere else!
                size = stream.readInt()
                data = stream.read(size)
                pos = stream.pos
                yield data

        for _ in range(image.image_count):
            if stream.pos != pos:
                stream.seek(pos)
            yield tuple(_read_image_mips())


    def _read_index(self, index_pos, stream):
        stream.seek(index_pos)
        assert stream.read(4) == _INDEX_MAGICK

        # See above, can change the index format easily...
        flags = hsBitVector()
        flags.read(stream)

        # ALWAYS ADD NEW FIELDS TO THE END OF THIS SECTION!!!!!!!
        image_count = stream.readInt() if flags[_IndexBits.image_count] else 0

        # Here begins the image map
        assert stream.read(4) == _DATA_MAGICK
        for i in range(image_count):
            self._read_index_entry(stream)

    def _read_index_entry(self, stream):
        assert stream.read(4) == _ENTRY_MAGICK
        image = _CachedImage()

        # See above, can change the entry format easily...
        flags = hsBitVector()
        flags.read(stream)

        # ALWAYS ADD NEW FIELDS TO THE END OF THIS SECTION!!!!!!!
        if flags[_EntryBits.image_name]:
            image.name = stream.readSafeWStr()
        if flags[_EntryBits.mip_levels]:
            image.mip_levels = stream.readByte()
        if flags[_EntryBits.image_pos]:
            image.data_pos = stream.readInt()
        if flags[_EntryBits.compression]:
            image.compression = stream.readByte()
        if flags[_EntryBits.source_size]:
            image.source_size = (stream.readInt(), stream.readInt())
        if flags[_EntryBits.export_size]:
            image.export_size = (stream.readInt(), stream.readInt())
        if flags[_EntryBits.last_export]:
            image.export_time = stream.readDouble()
        if flags[_EntryBits.image_count]:
            image.image_count = stream.readInt()
        if flags[_EntryBits.tag_string]:
            # tags should not contain user data, so we will use a latin_1 backed string
            image.tag = stream.readSafeStr()

        # do we need to check for duplicate images?
        self._images[(image.name, image.tag, image.compression)] = image

    @property
    def _report(self):
        return self._exporter().report

    def save(self):
        if self._exporter().texcache_method == "skip":
            return

        # TODO: add a way to preserve unused images for a brief period so we don't toss
        # already cached images that are only removed from the age temporarily...
        self._compact()

        # Assume all read operations are done (don't be within' my cache while you savin')
        assert self._stream_handles == 0

        with hsFileStream().open(self._exporter().texcache_path, fmWrite) as stream:
            self._write(stream)

    def _write(self, stream):
        flags = hsBitVector()
        flags[_HeaderBits.index_pos] = True

        stream.seek(0)
        stream.write(_HEADER_MAGICK)
        flags.write(stream)
        header_index_pos = stream.pos
        stream.writeInt(-1)

        for image in self._images.values():
            self._write_image_data(image, stream)

        # fix the index position
        index_pos = stream.pos
        self._write_index(stream)
        stream.seek(header_index_pos)
        stream.writeInt(index_pos)

    def _write_image_data(self, image, stream):
        # unused currently
        flags = hsBitVector()

        image.data_pos = stream.pos
        stream.write(_IMAGE_MAGICK)
        flags.write(stream)

        for i in image.image_data:
            for j in i:
                stream.write(_MIP_MAGICK)
                stream.writeInt(len(j))
                stream.write(j)

    def _write_index(self, stream):
        flags = hsBitVector()
        flags[_IndexBits.image_count] = True

        pos = stream.pos
        stream.write(_INDEX_MAGICK)
        flags.write(stream)
        stream.writeInt(len(self._images))

        stream.write(_DATA_MAGICK)
        for image in self._images.values():
            self._write_index_entry(image, stream)
        return pos

    def _write_index_entry(self, image, stream):
        flags = hsBitVector()
        flags[_EntryBits.image_name] = True
        flags[_EntryBits.mip_levels] = True
        flags[_EntryBits.image_pos] = True
        flags[_EntryBits.compression] = True
        flags[_EntryBits.source_size] = True
        flags[_EntryBits.export_size] = True
        flags[_EntryBits.last_export] = True
        flags[_EntryBits.image_count] = True
        flags[_EntryBits.tag_string] = image.tag is not None

        stream.write(_ENTRY_MAGICK)
        flags.write(stream)
        stream.writeSafeWStr(str(image))
        stream.writeByte(image.mip_levels)
        stream.writeInt(image.data_pos)
        stream.writeByte(image.compression)
        stream.writeInt(image.source_size[0])
        stream.writeInt(image.source_size[1])
        stream.writeInt(image.export_size[0])
        stream.writeInt(image.export_size[1])
        stream.writeDouble(time.time())
        stream.writeInt(image.image_count)
        if image.tag is not None:
            stream.writeSafeStr(image.tag)
