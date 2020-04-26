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

def collision(modifier, layout, context):
    layout.prop(modifier, "bounds")
    layout.separator()

    split = layout.split()
    col = split.column()
    col.prop(modifier, "avatar_blocker")
    col.prop(modifier, "camera_blocker")
    col.prop(modifier, "terrain")

    col = split.column()
    col.prop(modifier, "friction")
    col.prop(modifier, "restitution")
    layout.separator()

    split = layout.split()
    col = split.column()
    col.prop(modifier, "dynamic")
    row = col.row()
    row.active = modifier.dynamic
    row.prop(modifier, "start_asleep")

    col = split.column()
    col.active = modifier.dynamic
    col.prop(modifier, "mass")

def subworld_def(modifier, layout, context):
    layout.prop(modifier, "sub_type")
    if modifier.sub_type != "dynamicav":
        layout.prop(modifier, "gravity")
