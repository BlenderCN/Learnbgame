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

class PlasmaImage(bpy.types.PropertyGroup):
    texcache_method = EnumProperty(name="Texture Cache",
                                   description="Texture Cache Settings",
                                   items=[("skip", "Don't Cache Image", "This image is never cached."),
                                          ("use", "Use Image Cache", "This image should be cached."),
                                          ("rebuild", "Refresh Image Cache", "Forces this image to be recached on the next export.")],
                                   default="use",
                                   options=set())
