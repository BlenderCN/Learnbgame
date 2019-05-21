# Blender FLIP Fluid Add-on
# Copyright (C) 2018 Ryan L. Guy
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bpy, os
from bpy.props import (
        BoolProperty,
        StringProperty,
        PointerProperty
        )



class PhysiKaProperties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.physika = PointerProperty(
                name="PhysiKa Properties",
                description="",
                type=cls,
                )

        # cls.custom_icons = bpy.utils.previews.new()
        cls.physika_object_name = StringProperty(default="")
        

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.physika
        
    def get_physika_object(self):
        obj = bpy.data.objects.get(self.physika_object_name)
        return obj


def scene_update_post(scene):
    scene.physika.scene_update_post(scene)


def register():
    bpy.utils.register_class(PhysiKaProperties)

def unregister():
    bpy.utils.unregister_class(PhysiKaProperties)


