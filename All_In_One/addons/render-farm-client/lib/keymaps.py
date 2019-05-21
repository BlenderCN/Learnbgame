# Copyright (C) 2018 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
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

def addKeymaps(km):
    km.keymap_items.new("render_farm.render_frame_on_servers", 'F12', 'PRESS', alt=True)
    km.keymap_items.new("render_farm.render_animation_on_servers", 'F12', 'PRESS', alt=True, shift=True)
    km.keymap_items.new("render_farm.open_rendered_image", 'O', 'PRESS', shift=True)
    km.keymap_items.new("render_farm.open_rendered_animation", 'O', 'PRESS', alt=True, shift=True)
    km.keymap_items.new("render_farm.list_frames", 'M', 'PRESS', shift=True)
    km.keymap_items.new("render_farm.set_to_missing_frames", 'M', 'PRESS', alt=True, shift=True)
    km.keymap_items.new("render_farm.refresh_num_available_servers", 'R', 'PRESS', ctrl=True)
    km.keymap_items.new("render_farm.edit_servers_dict", 'E', 'PRESS', ctrl=True)
