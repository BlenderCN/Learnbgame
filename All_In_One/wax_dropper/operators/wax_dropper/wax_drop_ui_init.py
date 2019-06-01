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

# System imports
import time
import random

# Blender imports
from bpy_extras import view3d_utils

# Addon imports
from .wax_drop_datastructure import InputPoint, SplineSegment, CurveNode
from ...addon_common.cookiecutter.cookiecutter import CookieCutter
from ...addon_common.common import ui
from ...addon_common.common.blender import show_error_message
from ...addon_common.common.ui import Drawing


class WaxDrop_UI_Init():
    def ui_setup(self):
        # UI Box functionality
        def get_blobsize(): return self.wax_opts["blob_size"]
        def get_blobsize_print(): return "%0.3f" % self.wax_opts["blob_size"]
        def set_blobsize(v): self.wax_opts["blob_size"] = min(max(0.001, float(v)),8.0)

        # def get_radius(): return self.wax_opts["paint_radius"]
        # def get_radius_print(): return "%0.3f" % self.wax_opts["paint_radius"]
        # def set_radius(v):
        #     self.wax_opts["paint_radius"] = max(0.1, int(v*10)/10)
        #     if self.brush:
        #         print("setting bursh radius")
        #         self.brush.radius = self.wax_opts["paint_radius"]
        #         self.brush_density()

        def get_resolution(): return self.wax_opts["resolution"]
        def get_resolution_print(): return "%0.3f" % self.wax_opts["resolution"]
        def set_resolution(v):
            self.wax_opts["resolution"] = round(min(max(0.05, float(v)), 2.0), 5)
            self.meta_obj.data.resolution = self.wax_opts["resolution"]

        def get_depth_offset(): return self.wax_opts["depth_offset"]
        def get_depth_offset_print(): return "%0.3f" % self.wax_opts["depth_offset"]
        def set_depth_offset(v): self.wax_opts["depth_offset"] = round(min(max(-1.0, float(v)), 1.0), 5)

        def get_action(): return self.wax_opts["action"]
        def set_action(v): self.wax_opts["action"] = v

        def get_surface_target(): return self.wax_opts["surface_target"]
        def set_surface_target(v): self.wax_opts["surface_target"] = v

        # instructions
        self.instructions = {
            "place wax": "Left-click on the mesh to add a new wax ball",
            "change state": "Press 'ALT' to toggle between states",
            "sketch": "In sketch state, hold left-click and drag to sketch a series of wax balls",
            "paint": "In paint state, hold left-click and drag to paint a group of wax balls",
            "remove wax": "Shift + left-click on the mesh to remove a wax ball",
            # "remove wax series": "Shift + Right-click on the mesh to remove a series of connected wax balls",
        }

        def mode_getter(): return self._state
        def mode_setter(m): self.fsm_change(m)

        def radius_getter(): return self.wax_opts["paint_radius"]
        def radius_setter(v):
            self.wax_opts["paint_radius"] = max(0.1, int(v*10)/10)
            if self.brush:
                self.brush.radius = self.wax_opts["paint_radius"]

        #UPPER LEFT WINDOW, Sketch/Paint Mode
        #COMMIT/COMMIT and CONTINUE/COMMIT
        self.tools_panel = self.wm.create_window('Wax Dropper Tools', {'pos':7, 'movable':True, 'bgcolor':(0.50, 0.50, 0.50, 0.90)})

        precut_container = self.tools_panel.add(ui.UI_Container()) # TODO: make this rounded

        self.mode_frame = precut_container.add(ui.UI_Frame('Wax Drop Mode'))
        self.mode_options = self.mode_frame.add(ui.UI_Options(mode_getter, mode_setter, separation=0))
        self.mode_options.add_option('Sketch', value='sketch wait')
        self.mode_options.add_option('Paint', value='paint wait')

        segmentation_container = self.tools_panel.add(ui.UI_Container())
        self.finish_frame = segmentation_container.add(ui.UI_Frame('Finish Tools'))
        self.fuse_and_continue_button = self.finish_frame.add(ui.UI_Button('Fuse and Continue', self.fuse_and_continue, align=0))
        self.commit_button = self.finish_frame.add(ui.UI_Button('Commit', self.done, align=0))
        self.cancel_button = self.finish_frame.add(ui.UI_Button('Cancel', lambda:self.done(cancel=True), align=0))

        #####################################
        ### Collapsible Help and Options   ##
        #####################################
        self.info_panel = self.wm.create_window('Wax Dropper Help',
                                                {'pos':9,
                                                 'movable':True,
                                                 'bgcolor':(0.50, 0.50, 0.50, 0.90)})#, 'bgcolor':(0.30, 0.60, 0.30, 0.90)})

        collapse_container = self.info_panel.add(ui.UI_Collapsible('Instructions     ', collapsed=False))
        self.inst_paragraphs = [collapse_container.add(ui.UI_Markdown('', min_size=(100,10), max_size=(250, 20))) for i in range(5)]
        self.set_ui_text()
        #for i in self.inst_paragraphs: i.visible = False
        #self.ui_instructions = info.add(ui.UI_Markdown('test', min_size=(200,200)))
        self.options_frame = self.info_panel.add(ui.UI_Frame('Tool Options'))
        self.options_frame.add(ui.UI_Number("Size", get_blobsize, set_blobsize, fn_get_print_value=get_blobsize_print, fn_set_print_value=set_blobsize))
        # opts.add(ui.UI_Number("Paint Radius", get_radius, set_radius, fn_get_print_value=get_radius_print, fn_set_print_value=set_radius))
        self.options_frame.add(ui.UI_Number("Resolution", get_resolution, set_resolution, fn_get_print_value=get_resolution_print, fn_set_print_value=set_resolution, update_func=self.push_meta_to_wax, update_multiplier=0.05))
        self.options_frame.add(ui.UI_Number("Depth Offset", get_depth_offset, set_depth_offset, update_multiplier=0.05))
        self.wax_action_options = self.options_frame.add(ui.UI_Options(get_action, set_action, label="Action: ", vertical=True))
        self.wax_action_options.add_option("add")
        self.wax_action_options.add_option("subtract")
        self.wax_action_options.add_option("none")

        self.wax_surface_options = self.options_frame.add(ui.UI_Options(get_surface_target, set_surface_target, label="Surface: ", vertical=True))
        self.wax_surface_options.add_option("object")
        self.wax_surface_options.add_option("wax on wax")
        self.wax_surface_options.add_option("scene")

    def set_ui_text(self):
        ''' sets the viewports text '''
        self.reset_ui_text()
        for i,val in enumerate(['place wax', 'change state', 'sketch', 'paint', 'remove wax']):
            self.inst_paragraphs[i].set_markdown("-" + self.instructions[val])

    def reset_ui_text(self):
        for inst_p in self.inst_paragraphs:
            inst_p.set_markdown('')
