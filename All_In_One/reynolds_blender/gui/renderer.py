#------------------------------------------------------------------------------
# Reynolds-Blender | The Blender add-on for Reynolds, an OpenFoam toolbox.
#------------------------------------------------------------------------------
# Copyright|
#------------------------------------------------------------------------------
#     Deepak Surti       (dmsurti@gmail.com)
#     Prabhu R           (IIT Bombay, prabhu@aero.iitb.ac.in)
#     Shivasubramanian G (IIT Bombay, sgopalak@iitb.ac.in)
#------------------------------------------------------------------------------
# License
#
#     This file is part of reynolds-blender.
#
#     reynolds-blender is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     reynolds-blender is distributed in the hope that it will be useful, but
#     WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#     Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with reynolds-blender.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

# -----------
# bpy imports
# -----------
import bpy

# --------------
# python imports
# --------------
import yaml
import os

# ------------------------
# reynolds blender imports
# ------------------------
from .register import register_classes

class ReynoldsGUIRenderer(object):
    def __init__(self, scene, layout, gui_filename):
        self.scene = scene
        self.layout = layout

        current_dir = os.path.realpath(os.path.dirname(__file__))
        gui_file = os.path.join(current_dir, "../yaml", "panels",
                                gui_filename)

        self.gui_spec = []
        with open(gui_file) as f:
            self.gui_spec = yaml.load(f)

    def render(self):
        for gui_element in self.gui_spec['gui']:
            self._render_gui_element(gui_element, self.layout)

    def _render_gui_element(self, gui_element, parent):
        name = list(gui_element.keys())[0]
        metadata = gui_element[name]
        # print('Rendering gui elt ', name, ' with metadata ', metadata)

        if name == 'box':
            box = parent.box()
            for child in metadata:
                self._render_gui_element(child, box)

        if name == 'label':
            label = parent.label(text=metadata.get('text', ''))

        if name == 'row':
            row = parent.row()
            for child in metadata:
                self._render_gui_element(child, row)

        if name == 'col':
            col = parent.column()
            for child in metadata:
                self._render_gui_element(child, col)

        if name == 'prop':
            enabled = metadata.get('enabled', True)
            parent.enabled = enabled
            parent.prop(self.scene, metadata['scene_attr'])

        if name == 'group_prop':
            enabled = metadata.get('enabled', True)
            parent.enabled = enabled
            pointer_name = metadata['pointer']
            pointer = getattr(self.scene, pointer_name, None)
            if pointer:
                print('Rendering group prop ' + pointer_name)
                parent.prop(pointer, metadata['scene_attr'])

        if name == 'operator':
            action = metadata.get('action', False)
            if action:
                parent.operator(metadata['id'], icon=metadata['icon'],
                                text="").action = action
            else:
                parent.operator(metadata['id'], icon=metadata['icon'])

        if name == 'separator':
            for i in range(metadata['nums']):
                parent.separator()

        if name == 'template_list':
            parent.template_list('ReynoldsListItems', "", self.scene,
                                 metadata['coll_data_propname'], self.scene,
                                 metadata['coll_index_propname'])

