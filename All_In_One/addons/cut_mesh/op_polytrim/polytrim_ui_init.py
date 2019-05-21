'''
Created on Oct 11, 2015

@author: Patrick
'''

import time
import random

from bpy_extras import view3d_utils

from ..cookiecutter.cookiecutter import CookieCutter
from ..common import ui
from ..common.blender import show_error_message
from ..common.ui import Drawing

from .polytrim_datastructure import InputPoint, SplineSegment, CurveNode


class Polytrim_UI_Init():
    def ui_setup(self):
        self.instructions = {
            "add": "Left-click on the mesh to add a new point",
            "add (extend)": "Left-click to add new a point connected to the selected point. The green line will visualize the new segments created",
            "add (insert)": "Left-click on a segment to insert a new a point. The green line will visualize the new segments created",
            "close loop": "Left-click on the outer hover ring of existing point to close a boundary loop",
            "select": "Left-click on a point to select it",
            "sketch": "Hold Shift + left-click and drag to sketch in a series of points",
            "sketch extend": "Hover near an existing point, Shift + Left-click and drag to sketch in a series of points",
            "delete": "Right-click on a point to remove it",
            "delete (disconnect)": "Ctrl + right-click will remove a point and its connected segments",
            "tweak": "left click and drag a point to move it",
            "tweak confirm": "Release to place point at cursor's location",
            "paint": "Left-click to paint",
            "paint extend": "Left-click inside and then paint outward from an existing patch to extend it",
            "paint greedy": "Painting from one patch into another will remove area from 2nd patch and add it to 1st",
            "paint mergey": "Painting from one patch into another will merge the two patches",
            "paint remove": "Right-click and drag to delete area from patch",
            "seed add": "Left-click within a boundary to indicate it as patch segment",
            "segmentation" : "Left-click on a patch to select it, then use the segmentation buttons to apply changes"
        }

        def mode_getter():
            return self._state
        def mode_setter(m):
            self.fsm_change(m)
        def mode_change():
            nonlocal precut_container, segmentation_container, paint_radius
            m = self._state
            precut_container.visible = (m in {'spline', 'seed', 'region'})
            paint_radius.visible = (m in {'region'})
            no_options.visible = not (m in {'region'})
            segmentation_container.visible = (m in {'segmentation'})
        self.fsm_change_callback(mode_change)

        def radius_getter():
            return self.brush_radius
        def radius_setter(v):
            self.brush_radius = max(0.1, int(v*10)/10)
            if self.brush:
                self.brush.radius = self.brush_radius

        # def compute_cut():
        #     # should this be a state instead?
        #     self.network_cutter.knife_geometry4()
        #     self.network_cutter.find_perimeter_edges()
        #     for patch in self.network_cutter.face_patches:
        #         patch.grow_seed(self.input_net.bme, self.network_cutter.boundary_edges)
        #         patch.color_patch()
        #     self.net_ui_context.bme.to_mesh(self.net_ui_context.ob.data)
        #     self.fsm_change('segmentation')

        win_tools = self.wm.create_window('Polytrim Tools', {'pos':7, 'movable':True, 'bgcolor':(0.50, 0.50, 0.50, 0.90)})

        precut_container = win_tools.add(ui.UI_Container(rounded=1))

        precut_tools = precut_container.add(ui.UI_Frame('Pre Cut Tools', fontsize=16, spacer=0))
        precut_mode = precut_tools.add(ui.UI_Options(mode_getter, mode_setter, separation=0, rounded=1))
        precut_mode.add_option('Boundary Edit', value='spline', icon=ui.UI_Image('polyline.png', width=32, height=32))
        precut_mode.add_option('Boundary > Region', value='seed', icon=ui.UI_Image('seed.png', width=32, height=32))
        precut_mode.add_option('Region Paint', value='region', icon=ui.UI_Image('paint.png', width=32, height=32))

        container = precut_container.add(ui.UI_Frame('Cut Tools', fontsize=16, spacer=0))
        container.add(ui.UI_Button('Compute Cut', lambda:self.fsm_change('segmentation'), align=-1, icon=ui.UI_Image('divide32.png', width=32, height=32)))
        container.add(ui.UI_Button('Cancel', lambda:self.done(cancel=True), align=0))


        segmentation_container = win_tools.add(ui.UI_Container())
        segmentation_tools = segmentation_container.add(ui.UI_Frame('Segmentation Tools', fontsize=16, spacer=0))
        #segmentation_mode = segmentation_tools.add(ui.UI_Options(mode_getter, mode_setter))
        #segmentation_mode.add_option('Segmentation', value='segmentation', margin = 5)
        #seg_buttons = segmentation_tools.add(ui.UI_EqualContainer(margin=0,vertical=False))
        segmentation_tools.add(ui.UI_Button('Delete', self.delete_active_patch, tooltip='Delete the selected patch', align=-1, icon=ui.UI_Image('delete_patch32.png', width=32, height=32)))
        segmentation_tools.add(ui.UI_Button('Separate', self.separate_active_patch, tooltip='Separate the selected patch', align=-1, icon=ui.UI_Image('separate32.png', width=32, height=32)))
        segmentation_tools.add(ui.UI_Button('Duplicate', self.duplicate_active_patch, tooltip='Duplicate the selected patch', align=-1, icon=ui.UI_Image('duplicate32.png', width=32, height=32)))
        #seg_buttons.add(ui.UI_Button('Patch to VGroup', self.active_patch_to_vgroup, margin=5))

        container = segmentation_container.add(ui.UI_Frame('Cut Tools', fontsize=16, spacer=0))
        container.add(ui.UI_Button('Commit', self.done, align=0))
        container.add(ui.UI_Button('Cancel', lambda:self.done(cancel=True), align=0))


        info = self.wm.create_window('Polytrim Help', {'pos':9, 'movable':True, 'bgcolor':(0.30, 0.60, 0.30, 0.90)})
        #info.add(ui.UI_Label('Instructions', fontsize=16, align=0, margin=4))
        self.inst_paragraphs = [info.add(ui.UI_Markdown('', min_size=(200,10))) for i in range(7)]
        #for i in self.inst_paragraphs: i.visible = False
        #self.ui_instructions = info.add(ui.UI_Markdown('test', min_size=(200,200)))
        precut_options = info.add(ui.UI_Frame('Tool Options', fontsize=16, spacer=0))
        paint_radius = precut_options.add(ui.UI_Number("Paint radius", radius_getter, radius_setter))
        no_options = precut_options.add(ui.UI_Label('(none)', color=(1.00, 1.00, 1.00, 0.25)))
        
        
        self.set_ui_text_no_points()


    # XXX: Fine for now, but will likely be irrelevant in future
    def ui_text_update(self):
        '''
        updates the text in the info box
        '''
        if self._state == 'spline':
            if self.input_net.is_empty:
                self.set_ui_text_no_points()
            elif self.input_net.num_points == 1:
                self.set_ui_text_1_point()
            elif self.input_net.num_points > 1:
                self.set_ui_text_multiple_points()
            elif self.grabber and self.grabber.in_use:
                self.set_ui_text_grab_mode()

        elif self._state == 'region':
            self.set_ui_text_paint()
        elif self._state == 'seed':
            self.set_ui_text_seed_mode()

        elif self._state == 'segmentation':
            self.set_ui_text_segmetation_mode()

        else:
            self.reset_ui_text()

    # XXX: Fine for now, but will likely be irrelevant in future
    def set_ui_text_no_points(self):
        ''' sets the viewports text when no points are out '''
        self.reset_ui_text()
        self.inst_paragraphs[0].set_markdown('A) ' + self.instructions['add'])
        self.inst_paragraphs[1].set_markdown('B) ' + self.instructions['sketch'])

    def set_ui_text_1_point(self):
        ''' sets the viewports text when 1 point has been placed'''
        self.reset_ui_text()
        self.inst_paragraphs[0].set_markdown('A) ' + self.instructions['add (extend)'])
        self.inst_paragraphs[1].set_markdown('B) ' + self.instructions['delete'])
        self.inst_paragraphs[2].set_markdown('C) ' + self.instructions['sketch extend'])
        self.inst_paragraphs[3].set_markdown('C) ' + self.instructions['select'])
        self.inst_paragraphs[4].set_markdown('D) ' + self.instructions['tweak'])
        #self.inst_paragraphs[5].set_markdown('E) ' + self.instructions['add (disconnect)'])
        self.inst_paragraphs[6].set_markdown('F) ' + self.instructions['delete (disconnect)'])

        #self.inst_paragraphs[4].set_markdown('E) ' + self.instructions['add (disconnect)'])


    def set_ui_text_multiple_points(self):
        ''' sets the viewports text when there are multiple points '''
        self.reset_ui_text()
        self.inst_paragraphs[0].set_markdown('A) ' + self.instructions['add (extend)'])
        self.inst_paragraphs[1].set_markdown('B) ' + self.instructions['add (insert)'])
        self.inst_paragraphs[2].set_markdown('C) ' + self.instructions['delete'])
        self.inst_paragraphs[3].set_markdown('D) ' + self.instructions['delete (disconnect)'])
        self.inst_paragraphs[4].set_markdown('E) ' + self.instructions['sketch'])
        self.inst_paragraphs[5].set_markdown('F) ' + self.instructions['tweak'])
        self.inst_paragraphs[6].set_markdown('G) ' + self.instructions['close loop'])

    def set_ui_text_grab_mode(self):
        ''' sets the viewports text during general creation of line '''
        self.reset_ui_text()
        self.inst_paragraphs[0].set_markdown('A) ' + self.instructions['tweak confirm'])

    def set_ui_text_seed_mode(self):
        ''' sets the viewport text during seed selection'''
        self.reset_ui_text()
        self.inst_paragraphs[0].set_markdown('A) ' + self.instructions['seed add'])

    def set_ui_text_segmetation_mode(self):
        ''' sets the viewport text during seed selection'''
        self.reset_ui_text()
        self.inst_paragraphs[0].set_markdown('A) ' + self.instructions['segmentation'])

    def set_ui_text_paint(self):
        self.reset_ui_text()
        self.inst_paragraphs[0].set_markdown('A) ' + self.instructions['paint'])
        self.inst_paragraphs[1].set_markdown('B) ' + self.instructions['paint extend'])
        self.inst_paragraphs[2].set_markdown('C) ' + self.instructions['paint remove'])
        self.inst_paragraphs[3].set_markdown('D) ' + self.instructions['paint mergey'])

    def reset_ui_text(self):
        for inst_p in self.inst_paragraphs:
            inst_p.set_markdown('')
