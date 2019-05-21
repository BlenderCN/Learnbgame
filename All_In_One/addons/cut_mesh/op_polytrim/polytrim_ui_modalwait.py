'''
Created on Oct 11, 2015

@author: Patrick
'''
from ..common.blender import show_error_message, show_blender_popup
from .polytrim_datastructure import PolyLineKnife

class Polytrim_UI_ModalWait():

    def modal_wait(self,context,eventd):
        # general navigation
        nmode = self.modal_nav(context, eventd)
        if nmode != '':
            print("nmode")
            return nmode  #stop here and tell parent modal to 'PASS_THROUGH'

        # test code that will break operator :)
        #if eventd['press'] == 'F9': bad = 3.14 / 0
        #if eventd['press'] == 'F10': assert False

        #after navigation filter, these are relevant events in this state
        if eventd['press'] == 'G':
            if self.plm.current.grab_initiate():
                self.plm.current.grab_mouse_move(context,self.mouse)
                context.area.header_text_set("'MoveMouse'and 'LeftClick' to adjust node location, Right Click to cancel the grab")
                return 'grab'
            return 'main'

        if  eventd['type'] == 'MOUSEMOVE':
            self.mouse = eventd['mouse']
            self.hover(context)
            self.ui_text_update(context)
            return 'main'

        if  eventd['press'] == 'LEFTMOUSE':
            self.plm.current.click_add_point(context, self.mouse)  #Send the 2D coordinates to Knife Class
            if (self.plm.current.ui_type == 'DENSE_POLY' and self.plm.current.hovered[0] == 'POINT') or self.plm.current.num_points == 1:
                self.sketch = [self.mouse]
                return 'sketch'
            return 'main'

        if eventd['press'] == 'RIGHTMOUSE':
            if self.plm.current.start_edge and self.plm.current.hovered[1] == 0 and self.plm.current.num_points > 1:
                show_error_message('Can not delete the first point for this kind of cut.', "Don't do this!")
                return 'main'
            self.plm.current.click_delete_point(mode = 'mouse')
            self.hover(context) ## this fixed index out range error in draw function after deleteing last point.
            return 'main'

        if eventd['press'] == 'A':
            if self.plm.current.num_points > 1:
                context.window.cursor_modal_set('DEFAULT')
                context.area.header_text_set("LEFT-CLICK: select, RIGHT-CLICK: delete, PRESS-N: new, ESC: cancel")
                self.plm.initiate_select_mode(context)
                return 'select'
            else: show_error_message("You must have 2 or more points out before you can ")
            return 'main'

        if eventd['press'] == 'C':
            if self.plm.current.start_edge != None and self.plm.current.end_edge == None:
                show_error_message('Cut starts on non manifold boundary of mesh and must end on non manifold boundary')
            elif self.plm.current.start_edge == None and not self.plm.current.cyclic:
                show_error_message('Cut starts within mesh.  Cut must be closed loop.  Click the first point to close the loop')
            else:
                self.plm.current.make_cut()
                context.area.header_text_set("Red segments have cut failures, modify polyline to fix.  When ready press 'S' to set seed point")

            return 'main'

        if eventd['press'] == 'K':
            if self.plm.current.split and self.plm.current.face_seed and self.plm.current.ed_cross_map.is_used:
                self.plm.current.split_geometry(eventd['context'], mode = 'KNIFE')
                self.plm.polylines.pop(self.plm.polylines.index(self.plm.current))
                if len(self.plm.polylines):
                    self.plm.current = self.plm.polylines[-1]
                    return 'main'
                return 'finish'

        if eventd['press'] == 'P':
            if self.plm.current.split and self.plm.current.face_seed and self.plm.current.ed_cross_map.is_used:
                self.plm.current.split_geometry(eventd['context'], mode = 'SEPARATE')
                self.plm.polylines.pop(self.plm.polylines.index(self.plm.current))
                if len(self.plm.polylines):
                    self.plm.current = self.plm.polylines[-1]
                    return 'main'
                return 'finish'

        if eventd['press'] == 'X':
            if self.plm.current.split and self.plm.current.face_seed and self.plm.current.ed_cross_map.is_used:
                self.plm.current.split_geometry(eventd['context'], mode = 'DELETE')
                self.plm.polylines.pop(self.plm.polylines.index(self.plm.current))
                if len(self.plm.polylines):
                    self.plm.current = self.plm.polylines[-1]
                    return 'main'
                return 'finish'

        if eventd['press'] == 'SHIFT+D':
            if self.plm.current.split and self.plm.current.face_seed and self.plm.current.ed_cross_map.is_used:
                self.plm.current.split_geometry(eventd['context'], mode = 'DUPLICATE')
                self.plm.polylines.pop(self.plm.polylines.index(self.plm.current))
                if len(self.plm.polylines):
                    self.plm.current = self.plm.polylines[-1]
                    return 'main'
                return 'finish'

        if eventd['press'] == 'S':
            if len(self.plm.current.bad_segments) != 0:
                show_error_message('Cut has failed segments shown in red.  Move the red segment slightly or add cut nodes to avoid bad part of mesh')
                return 'main'

            if self.plm.current.start_edge == None and not self.plm.current.cyclic:
                show_error_message('Finish closing cut boundary loop')
                return 'main'

            elif self.plm.current.start_edge != None and self.plm.current.end_edge == None:
                show_error_message('Finish cutting to another non-manifold boundary/edge of the object')
                return 'main'

            elif not self.plm.current.ed_cross_map.is_used:
                show_error_message('Press "C" to preview the cut success before setting the seed')
                return 'main'

            context.window.cursor_modal_set('EYEDROPPER')
            context.area.header_text_set("Left Click Region to select area to cut")
            return 'inner'

        if eventd['press'] == 'RET' :
            self.plm.current.confirm_cut_to_mesh()
            return 'finish'

        elif eventd['press'] == 'ESC':
            return 'cancel'

        return 'main'

    def modal_grab(self,context,eventd):
        # no navigation in grab mode
        
        if eventd['press'] == 'LEFTMOUSE':
            #confirm location
            self.plm.current.grab_confirm(context)
            if self.plm.current.ed_cross_map.is_used:
                self.plm.current.make_cut()
            self.ui_text_update(context)
            return 'main'

        elif eventd['press'] in {'RIGHTMOUSE', 'ESC'}:
            #put it back!
            self.plm.current.grab_cancel()
            self.ui_text_update(context)
            return 'main'

        elif eventd['type'] == 'MOUSEMOVE':
            #update the b_pt location
            self.mouse = eventd['mouse']
            self.plm.current.grab_mouse_move(context, self.mouse)
            return 'grab'

    def modal_sketch(self,context,eventd):
        if eventd['type'] == 'MOUSEMOVE':
            self.mouse = eventd['mouse']
            if not len(self.sketch):
                return 'main'
            ## Manipulating sketch data
            (lx, ly) = self.sketch[-1]
            ss0,ss1 = self.stroke_smoothing ,1-self.stroke_smoothing  #First data manipulation
            self.sketch += [(lx*ss0+self.mouse[0]*ss1, ly*ss0+self.mouse[1]*ss1)]
            return 'sketch'

        elif eventd['release'] == 'LEFTMOUSE':
            is_sketch = self.sketch_confirm(context, eventd)
            if self.plm.current.ed_cross_map.is_used and is_sketch:
                self.plm.current.make_cut()
            self.ui_text_update(context)
            self.sketch = []
            return 'main'

    def modal_select(self, context, eventd):
        # no navigation in select mode
        if eventd['type'] == 'MOUSEMOVE':
            self.mouse = eventd['mouse']
            self.plm.hover(context, self.mouse)
            return 'select'

        elif eventd['press'] == 'LEFTMOUSE':
            if self.plm.hovered:
                self.plm.select(context)
                self.set_ui_text_main(context)
                context.window.cursor_modal_set('CROSSHAIR')
                return 'main'
            return 'select'

        elif eventd['press'] == 'RIGHTMOUSE':
            if self.plm.hovered and self.plm.num_polylines > 1:
                self.plm.delete(context)
            return 'select'

        elif eventd['press'] == 'N':
            self.plm.start_new_polyline(context)
            context.window.cursor_modal_set('CROSSHAIR')
            self.set_ui_text_main(context)
            return 'main'

        elif eventd['press'] in {'ESC', 'A'}:
            self.plm.terminate_select_mode()
            context.window.cursor_modal_set('CROSSHAIR')
            self.set_ui_text_main(context)
            return 'main'

    def modal_inner(self,context,eventd):

        if eventd['press'] == 'LEFTMOUSE':
            self.mouse = eventd['mouse']

            result = self.plm.current.click_seed_select(context, self.mouse)
            # found a good face
            if result == 1:
                context.window.cursor_modal_set('CROSSHAIR')
                if self.plm.current.ed_cross_map.is_used and not self.plm.current.bad_segments and not self.plm.current.split:
                    self.plm.current.confirm_cut_to_mesh_no_ops()
                    context.area.header_text_set("X:delete, P:separate, SHIFT+D:duplicate, K:knife")
                return 'main'
            # found a bad face
            elif result == -1:
                show_error_message('Seed is too close to cut boundary, try again more interior to the cut')
                return 'inner'
            # face not found
            else:
                show_error_message('Seed not found, try again')
                return 'inner'

        if eventd['press'] in {'RET', 'ESC'}:
            return 'main'