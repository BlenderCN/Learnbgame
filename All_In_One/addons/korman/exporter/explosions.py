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

class NonfatalExportError(Exception):
    def __init__(self, *args, **kwargs):
        assert args
        if len(args) > 1:
            super(Exception, self).__init__(args[0].format(*args[1:], **kwargs))
        else:
            super(Exception, self).__init__(args[0])


class ExportError(Exception):
    def __init__(self, value="Undefined Export Error"):
        super(Exception, self).__init__(value)


class BlenderOptionNotSupportedError(ExportError):
    def __init__(self, opt):
        super(ExportError, self).__init__("Unsupported Blender Option: '{}'".format(opt))


class ExportAssertionError(ExportError):
    def __init__(self):
        super(ExportError, self).__init__("Assertion failed")


class TooManyUVChannelsError(ExportError):
    def __init__(self, obj, mat, numUVTexs, maxUVTexCount=8):
        msg = "There are too many UV Textures on the material '{}' associated with object '{}'. You can have at most {} (there are {})".format(
           mat.name, obj.name, maxUVTexCount, numUVTexs)
        super(ExportError, self).__init__(msg)


class TooManyVerticesError(ExportError):
    def __init__(self, mesh, matname, vertcount):
        msg = "There are too many vertices ({}) on the mesh data '{}' associated with material '{}'".format(
           vertcount, mesh, matname
        )
        super(ExportError, self).__init__(msg)


class UndefinedPageError(ExportError):
    mistakes = {}

    def __init__(self):
        super(ExportError, self).__init__("You have objects in pages that do not exist!")

    def add(self, page, obj):
        if page not in self.mistakes:
            self.mistakes[page] = [obj,]
        else:
            self.mistakes[page].append(obj)

    def raise_if_error(self):
        if self.mistakes:
            # Better give them some idea of what happened...
            print(repr(self.mistakes))
            raise self


class UnsupportedTextureError(ExportError):
    def __init__(self, texture, material):
        super(ExportError, self).__init__("Cannot export texture '{}' on material '{}' -- unsupported type '{}'".format(texture.name, material.name, texture.type))
