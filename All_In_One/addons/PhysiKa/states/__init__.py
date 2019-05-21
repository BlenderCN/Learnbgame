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
import os,bpy
script_path = os.path.dirname(os.path.realpath(__file__))
state_names = [f.split('.')[0] for f in os.listdir(script_path) if f.endswith('_state')]

if "bpy" in locals():
    import importlib
    for module_name in state_names:
        if module_name in locals():
            importlib.reload(locals()[module_name])

for state in state_names:
    exec('from ..states import ' + state)


def register():
    for state in state_names:
        exec(state + '.register()')
        
def unregister():
    for state in state_names:
        exec(state + '.unregister()')
