'''
Created on Jan 21, 2013

@author: Patrick
'''
import bpy
import math
import time

import pie_menu_utils as pmu
import pie_menu

#slider, noclick border modal
def slider_modal(self, context, event):
    settings = context.user_preferences.addons['piemenus'].preferences
    now = time.time()
    if now - self.menu.init_time < settings.pieBorderDelay:
        #calculate apparent position of mouse
        app_x = event.mouse_region_x + (self.menu.menu_x - self.menu.init_x)
        app_y = event.mouse_region_y + (self.menu.menu_y - self.menu.init_y)
    else:
        app_x = event.mouse_region_x
        app_y = event.mouse_region_y
        
    if event.type == 'MOUSEMOVE':
        #make sure we keep the mouse over or slider highlit
        if self.menu.precision_item:
            self.current = self.menu.precision_item
        else:
            #first identify what item we have the mouse over
            self.current = self.menu.calc_by_item(app_x, app_y)
            if not self.current:
                self.current = self.menu.calc_by_angle(app_x, app_y)
                    
        # pointer of center circle points at the mouse
        self.menu.pointerangle=-math.atan2(app_x-self.menu.menu_x, app_y-self.menu.menu_y)   #changed this to radians and y = 0 axis theta  0     
        
        if self.current in self.menu.sliders and self.menu.mouse_drag:
            if self.menu.precision:
                width = context.region.width
                delta = .5 * (event.mouse_region_x-self.menu.precision_origin)/width
                self.current.pctg = self.current.precision_pctg + delta
                
            else:
                self.current.calc(app_x, app_y)
                
            self.current.push_to_prop()
            self.current.update_local_to_screen()
    
    elif event.type in {'LEFT_SHIFT','RIGHT_SHIFT'}:
        if event.value == 'PRESS':
            self.menu.precision = True
        if event.value == 'RELEASE':
            self.menu.precision = False
            if self.menu.precision_item:
                self.menu.precision_item.precision_pctg = self.menu.precision_item.pctg
                self.menu.precision_item = None
            
    elif event.type == 'LEFTMOUSE':
    
        if self.menu.precision_item:
            self.current = self.menu.precision_item
        else:
            #first identify what item we have the mouse over
            self.current = self.menu.calc_by_item(app_x, app_y)
            if not self.current:
                self.current = self.menu.calc_by_angle(app_x, app_y)
            
             
        #three things could be happening here
        #clicking a slider or clicking a menu item, or precision sliding beyond
        if event.value == 'PRESS':
            if not self.menu.mouse_drag:
                self.menu.mouse_drag = True
                self.menu.precision_origin = event.mouse_region_x
                self.menu.precision_item = self.current
            
            self.menu.precision = event.shift
            #development declaration for properties and autocomlete
            #self.current = pie_menu.PiePropSlider
            
            if self.current in self.menu.sliders:
                if self.menu.precision:
                    width = context.region.width
                    delta = .5 * (event.mouse_region_x-self.menu.precision_origin)/width
                    self.current.pctg = self.current.precision_pctg + delta
                else: #keep the valuse synced..perhaps should be happening on item level
                    self.current.precision_pctg = self.current.pctg    
                self.current.push_to_prop()
                self.current.update_local_to_screen()
                return {'RUNNING_MODAL'}
            
            else:    
                do_exec = self.current and self.current.poll(context)
                if do_exec:
                    self.current.op(self, context)
            
                if self.current is None or (do_exec and self.current.close_menu):
                    pmu.callback_cleanup(self, context)
                    return {'FINISHED'}
                else:
                    return {'RUNNING_MODAL'}
        
        if event.value == 'RELEASE':
            self.menu.mouse_drag = False
            self.menu.precision_item = None
            
            if self.current in self.menu.sliders:
                if self.menu.precision:
                    width = context.region.width
                    delta = .5 * (event.mouse_region_x-self.menu.precision_origin)/width
                    self.current.pctg = self.current.precision_pctg + delta
                
                self.current.precision_pctg = self.current.pctg
                    
                self.current.push_to_prop()
                self.current.update_local_to_screen()
            
            return {'RUNNING_MODAL'}
        
        
    elif event.type == self.menu.keybind and event.value == "RELEASE":
        
        do_exec = False
        if self.current not in self.menu.sliders:
            do_exec = self.current and self.current.poll(context)
        if do_exec and self.current.close_menu:
            self.current.op(self, context)
            pmu.callback_cleanup(self,context)
            
            return {'FINISHED'}
    
        elif self.current is None: #the mouse is still in the circle
            return {'RUNNING_MODAL'}
    
        else:
            return {'RUNNING_MODAL'}
        
        
    if self.current == -1 or event.type in ('RIGHTMOUSE', 'ESC'):
        pmu.callback_cleanup(self,context)
        return {'CANCELLED'}
    
    return {'RUNNING_MODAL'}