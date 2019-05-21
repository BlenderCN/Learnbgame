# -*- coding: utf-8 -*-
 
# Copyright (c) 2010, Dan Eicher.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 
# <pep8 compliant>

bl_info = {
    "name": "Pie Library",
    "author": "Dan Eicher, Sean Olson, Patrick Moore",
    "version": (0, 1, 0),
    "blender": (2, 6, 4),
    "location": "",
    "description": "Library Used by Pie Menus",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}
 
import bpy
import os
import math
import time
import blf
import bgl
from mathutils import Vector, Matrix
import pie_menu_utils as pmu
import icon_util


class PiePropSlider(object):
    def __init__(self, id, data, property, width, height, x, y, rot = 0, scale = 1, rad = 5):
        self.type = "SLIDER"
        self.id = id
        self.data = data
        self.prop =  property
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.rot = rot
        self.scale = scale
        self.corner_radius = rad
        
        self.soft_min = data.bl_rna.properties[self.prop].soft_min
        self.soft_max = data.bl_rna.properties[self.prop].soft_max
        
        self.pctg = getattr(data, property, 0)/self.soft_max
        self.precision_pctg = self.pctg

        boxes = pmu.make_round_slider(-width/2, -height/2, width/2, height/2, self.pctg, self.corner_radius)
        self.left_box = boxes[0]
        self.right_box = boxes[1]
        self.cheap_box = pmu.make_quad(self.width, self.height, 0,0,0) #dont rotate this because mouse test happens locally..the whole slider is rotated already.
        
        #this will be update based on x,y, ang and scale only when self.update_local_to_screen
        #use these for drawing, but use self.calc to mouse test.  That way only the mouse coord
        #gets transformed for the test and you only have to recalc everything to draw when
        #position/loc/scale or menu changes.
        
        self.screen_left = []
        self.screen_right = []
        
        
    def push_to_prop(self):
        val = (self.pctg) * (self.soft_max)
        setattr(self.data, self.prop, val)
        #print("percentage in click...setattr to %f" % val)
        
    def pull_from_prop(self):
        self.pctg = getattr(self.data, self.prop)/self.soft_max
        
        boxes = pmu.make_round_slider(-self.width/2, -self.height/2, self.width/2, self.height/2, self.pctg, self.corner_radius)
        self.left_box = boxes[0]
        self.right_box = boxes[1]
    
    def update_local_to_screen(self):
        '''
        translate, rotates and scales the appropriate components of the slider
        '''
        self.pull_from_prop()
        
        j = len(self.right_box)  
        if j > 0:
            self.screen_right = [[0,1]]*j
            for i in range(0,j):
                vec = Vector((self.right_box[i][0],self.right_box[i][1]))
                vec = self.scale*vec
                vec = Matrix.Rotation(self.rot,2)*vec
                vec += Vector((self.x,self.y))
                self.screen_right[i] = vec
                
        j = len(self.left_box)  
        if j > 0:
            self.screen_left = [[0,1]]*j
            for i in range(0,j):
                vec = Vector((self.left_box[i][0],self.left_box[i][1]))
                vec = self.scale*vec
                vec = Matrix.Rotation(self.rot,2)*vec
                vec += Vector((self.x,self.y))
                self.screen_left[i] = vec

            
    def calc(self,mx,my,precision = False, push_now = False):
        '''
        args: mx,my screen coordinates of mouse
        return self or none
        '''
        #put the mouse coordinates in item space
        mx -= self.x
        my -= self.y
        mouse = Vector((mx,my))
        rmatrix = Matrix.Rotation(-1*self.rot,2)
        mouse = (1/self.scale)*(rmatrix*mouse)
        
        if pmu.point_inside_loop(self.cheap_box,mouse):
            pctg = mouse[0]/(self.width-2*self.corner_radius) + .5 #TODO may need to add scale here
            if pctg > 1:
                if not precision:
                    self.pctg = 1
            else:
                if not precision:
                    self.pctg = pctg
            
            if push_now:
                self.push_to_prop()   
            return True
        else: return False
        
class PiePropRadio(object):
    def __init__(self, id, data, property, x, y, rot = 0, scale = 1):
        self.type = "RADIO"
        self.id = id
        self.data = data
        self.prop =  property
        self.x = x
        self.y = y
        self.rot = rot
        self.scale = scale
        #self.corner_radius = rad
        self.calc_mode = "POLY_LOOP" #only optoin for radios
        self.layout = "PREDEF" #only option for radios
        self.close_menu = False #only option
        
        self.poly_bound = []
        self.cheap_box = [] #TODO: implement this for faster mouse testing
        self.on = False
        self.icon = "RADIOBUT_OFF"
        self.tex_coords = icon_util.icon_name_to_texture_coord(self.icon)
        self.icon_quad = []
        
        
        #this will be update based on x,y, ang and scale only when self.update_local_to_screen
        #use these for drawing, but use self.calc to mouse test.  That way only the mouse coord
        #gets transformed for the test and you only have to recalc everything to draw when
        #position/loc/scale or menu changes.
         
    def op(self,parent,context):
        val = self.on == False
        setattr(self.data, self.prop, val)
        self.on = val
        
        self.update_local_to_screen()
        print('did we do the damn thing?')
        #print("percentage in click...setattr to %f" % val)
        
    def pull_from_prop(self):
        self.on = getattr(self.data, self.prop)
    
    def update_local_to_screen(self):
        '''
        translate, rotates and scales the appropriate components of the slider
        '''
        self.pull_from_prop()
        if self.on:
            self.id = "On"
            self.icon = "RADIOBUT_ON"
        else:
            self.id = "Off"
            self.icon = "RADIOBUT_OFF"
            
        self.tex_coords = icon_util.icon_name_to_texture_coord(self.icon)
        
        j = len(self.icon_quad)  
        if j > 0:
            self.screen_icon_quad = [[0,1]]*j
            center = Vector((0,0))
            for i in range(0,j):
                center += Vector((self.icon_quad[i][0],self.icon_quad[i][1])) 
            center *= 1/j
            
            for i in range(0,j):
                vec = Vector((self.icon_quad[i][0],self.icon_quad[i][1]))-center #move the object to the MenuItem origin
                vec = self.scale*vec #scale it
                vec += self.scale*Matrix.Rotation(self.rot,2)*center #move it to a rotated scaled center in MenuItem space
                vec += Vector((self.x,self.y)) # Place it in Menu/Screen space
                self.screen_icon_quad[i] = vec
        
        j = len(self.poly_bound)  
        if j > 0:
            self.screen_poly_bound = [[0,1]]*j
            for i in range(0,j):
                vec = Vector((self.poly_bound[i][0],self.poly_bound[i][1]))
                vec = self.scale*vec
                vec = Matrix.Rotation(self.rot,2)*vec
                vec += Vector((self.x,self.y))
                self.screen_poly_bound[i] = vec
                
        #j = len(self.cheap_box)          
        #if j > 0:
            #self.cheap_box = [[0,1]]*j
            #for i in range(0,j):
                #vec = Vector((self.cheap_box[i][0],self.cheap_box[i][1]))
                #vec = self.scale*vec
                #vec = Matrix.Rotation(self.rot,2)*vec
                #vec += Vector((self.x,self.y))
                #self.cheap_box[i] = vec
            
    def calc(self,mx,my,push_now = False):
        '''
        args: mx,my screen coordinates of mouse
        return self or none
        '''
        #put the mouse coordinates in item space
        mx -= self.x
        my -= self.y
        mouse = Vector((mx,my))
        rmatrix = Matrix.Rotation(-1*self.rot,2)
        mouse = (1/self.scale)*(rmatrix*mouse)
        
        if pmu.point_inside_loop(self.poly_bound,mouse):  
            return True
        else: 
            return False
        
    def poll(self, context):
        return True
    
class MenuItem(object):
    def __init__(self, id, x=0, y=0, rot=0, scale = 1, angle = math.pi/12, icon = "", poly_bound = [], layout = "PIE", calc_mode = "ANGLE", close = True):
        
        self.type = "OP"
        self.id = id
        self.x = x
        self.y = y
        self.rot = rot
        self.scale = scale
        self.angle_cw = angle  #1/2 * 2*pi/n => pi/n typically in the symetric case
        self.angle_ccw = angle
        self.icon = icon
        self.tex_coords = (0,0)*4
        if self.icon:
            self.tex_coords = icon_util.icon_name_to_texture_coord(self.icon)
            
        self.icon_quad = []
        self.img = ""
        self.img_poly = []
        self.poly_bound = poly_bound
        self.calc_mode = calc_mode #ANGLE, ICON_QUAD, POLY_LOOP
        self.layout = layout  #PIE, PREDEF
        self.close_menu = close
        
        #this will be update based on x,y, ang and scale only when self.update_local_to_screen
        #use these for drawing, but use self.calc to mouse test.  That way only the mouse coord
        #gets transformed for the test and you only have to recalc everything to draw when
        #position/loc/scale or menu changes.
        self.screen_icon_quad = []
        self.screen_poly_bound = []
        self.screen_img_poly = []
        self.screen_pie = []
 
 
 
    def op(self, parent, context):
        raise NotImplementedError
 
    def poll(self, context):
        return True
        
    def calc(self, mx, my):
        '''
        args: mx,my screen coordinates of mouse
        return self or none
        '''
        #put the mouse coordinates in item space
        mx -= self.x
        my -= self.y
        mouse = Vector((mx,my))
        rmatrix = Matrix.Rotation(-1*self.rot,2)
        mouse = (1/self.scale)*(rmatrix*mouse)
        
        if self.calc_mode == "POLY_LOOP":
            if pmu.point_inside_loop(self.poly_bound,mouse):
                #print(self.id)
                return True
            else: return False

        if self.calc_mode == "ICON_QUAD": #TODO, make this actually test based on the icon quad
            if pmu.point_inside_loop(self.poly_bound,mouse):
                #print(self.id)
                return True
            else: return False
            
    def update_local_to_screen(self): #TODO Clean this up!
        '''
        translate, rotates and scales the appropriate components of the menu item
        icons don't get rotated.
        '''
        j = len(self.icon_quad)  
        if j > 0:
            self.screen_icon_quad = [[0,1]]*j
            center = Vector((0,0))
            for i in range(0,j):
                center += Vector((self.icon_quad[i][0],self.icon_quad[i][1])) 
            center *= 1/j
            
            for i in range(0,j):
                vec = Vector((self.icon_quad[i][0],self.icon_quad[i][1]))-center #move the object to the MenuItem origin
                vec = self.scale*vec #scale it
                vec += self.scale*Matrix.Rotation(self.rot,2)*center #move it to a rotated scaled center in MenuItem space
                vec += Vector((self.x,self.y)) # Place it in Menu/Screen space
                self.screen_icon_quad[i] = vec
        
        j = len(self.poly_bound)  
        if j > 0:
            self.screen_poly_bound = [[0,1]]*j
            for i in range(0,j):
                vec = Vector((self.poly_bound[i][0],self.poly_bound[i][1]))
                vec = self.scale*vec
                vec = Matrix.Rotation(self.rot,2)*vec
                vec += Vector((self.x,self.y))
                self.screen_poly_bound[i] = vec
                
        j = len(self.img_poly)  
        if j > 0:
            self.screen_img_poly = [[0,1]]*j
            for i in range(0,j):
                vec = Vector((self.img_poly[i][0],self.img_poly[i][1]))
                vec = self.scale*vec
                vec = Matrix.Rotation(self.rot,2)*vec
                vec += Vector((self.x,self.y))
                self.screen_poly_bound[i] = vec
    
    
    def icon_to_round(self):
        print('not implemented')
    
class PieMenu(object):
    
    def __init__(self, context, x, y, layout_radius, text_size,
                 text_dpi, center_radius_squared,
                 max_radius_squared, keybind,
                 corner_radius=5, icon = ""):
        
        
        settings = context.user_preferences.addons['piemenus'].preferences
        
        self.menu_x = x
        self.menu_y = y
        self.radius = layout_radius
        self.text_size = text_size
        self.text_dpi = text_dpi
        #self.center_radius = center_radius_squared  #use if each pie needs own inner radius setting
        #self.center_radius = 900
        self.center_radius = settings.pieInnerRadius**2
        #self.max_radius = max_radius_squared #use if each pie needs own outer radius setting
        self.max_radius = settings.pieOuterRadius**2  #TODO addon_prefs
        self.corner_radius = corner_radius
        self.angle = 0
        self.item_offset = 0
        self.menu_items = []
        self.sliders = []
        
        self.vec_cache = None
        
        self.biggest_dim_x = 0
        self.biggest_dim_y = 0
        self.dimension_radio = 0
        
        self.keybind = keybind
        self.init_time = time.time()
        self.mouse_drag = False
        
        self.precision = False
        self.precision_origin = x
        self.precision_item = None
        
        self.init_x = x
        self.init_y = y
        
        self.aspect = settings.pieSquish
        self.diamond = settings.pieDiamond
        self.theta_shift = settings.pieThetaShift

        ui=bpy.context.user_preferences.themes['Default'].user_interface #alias

        #inner color selected
        self.ris = ui.wcol_pulldown.inner_sel[0]
        self.gis = ui.wcol_pulldown.inner_sel[1]
        self.bis = ui.wcol_pulldown.inner_sel[2]
        self.ais = ui.wcol_pulldown.inner_sel[3]
    
        #inner color
        self.ri = ui.wcol_menu.inner[0]
        self.gi = ui.wcol_menu.inner[1]
        self.bi = ui.wcol_menu.inner[2]
        self.ai = ui.wcol_menu.inner[3]

        #outline color
        self.ro = ui.wcol_menu.outline[0]
        self.go = ui.wcol_menu.outline[1]
        self.bo = ui.wcol_menu.outline[2]

        #text color
        self.rt = ui.wcol_menu.text[0]
        self.gt = ui.wcol_menu.text[1]
        self.bt = ui.wcol_menu.text[2] 

        #slider item color (forground)
        self.rsItem = ui.wcol_numslider.item[0]
        self.gsItem = ui.wcol_numslider.item[1]
        self.bsItem = ui.wcol_numslider.item[2]

        #slider inner color (background)
        self.rsInner = ui.wcol_numslider.inner[0]
        self.gsInner = ui.wcol_numslider.inner[1]
        self.bsInner = ui.wcol_numslider.inner[2]

        #slider outline color
        self.rsOutline = ui.wcol_numslider.outline[0]
        self.gsOutline = ui.wcol_numslider.outline[1]
        self.bsOutline = ui.wcol_numslider.outline[2]

        #slider selected color (background)
        self.rsSelected = ui.wcol_numslider.inner_sel[0]
        self.gsSelected = ui.wcol_numslider.inner_sel[1]
        self.bsSelected = ui.wcol_numslider.inner_sel[2]
    
        self.pointerangle=0
        
        #image originally loaded into graphics mem at addon init
        #switching out of texture paint clears it. Other things might too...test
        
        img = bpy.data.images.get('blender_icons_x2.png')
        if not img:
            #this should never happen...except on first menu call
            #load the icon image into blend data.                
            addons_folder = os.path.dirname(__file__)
            icondir=os.path.join(addons_folder, 'icons','blender_icons')
            pmu.icons_to_blend_data(icondir)
            img = bpy.data.images['blender_icons_x2.png']
            
        bindcode = img.bindcode #will be 0 if not loaded
        if not bindcode:
            img.gl_load()
            settings.pieIconBindcode = img.bindcode
        
        #TODO addon_prefs
        scn = bpy.context.scene   
        if not len(scn.pie_settings):
            scn.piemenus.initSceneProperties()

             
    def distribute_slices(self):
        '''
        interpolate and distribute pie slices based on adjacent MenuItems
        should happen after MenuItem.x and y have  been set
        '''
        pie_items = [i for i in range(0,len(self.menu_items)) if self.menu_items[i].layout == "PIE"]
        thetas = [0]*len(pie_items)
        theta_dict = {}
        for i in pie_items:
            it = self.menu_items[i]
            theta = math.fmod(math.atan2(it.y-self.menu_y, it.x-self.menu_x) + 2*math.pi, 2*math.pi)
            theta_dict[theta] = i #a dictionary storing item index and angle
            thetas[i] = theta  #a list of angles to sort
        
        thetas.sort()        

        for i in range(0,len(thetas)):
            diff = math.fmod(thetas[i] - thetas[i-1]+2*math.pi , 2*math.pi)             
            self.menu_items[theta_dict[thetas[i]]].angle_cw = diff/2
            self.menu_items[theta_dict[thetas[i-1]]].angle_ccw = diff/2
  
    ## auto-layout menu items around the base circle
    def layout_even(self, radians):
        angle = self.angle #this is a limiting angle...eg, only a limited slice.  Will be used for spawing submenus.
        pie_items = [i for i in range(0,len(self.menu_items)) if self.menu_items[i].layout == "PIE"]
        n = len(pie_items)
        if angle:  # keep sub-menu items inside main slice
            step = radians / n
            angle -= (radians * 0.5)
        else:
            step = radians / n
        self.item_offset = step * 0.5
 
        # Calculate pie slice
        for i in pie_items:
            it = self.menu_items[i]
            it.rot = 0
            it.angle = self.item_offset  #To Do...self.item_offsst redundant each item has a width?
            # Rotate point around center with Fancy Math, set item x,y to screen
            it.x = self.radius * math.sin(angle) + self.menu_x
            it.y = self.radius * math.cos(angle) + self.menu_y
            it.update_local_to_screen()
            angle += step
            
        
        self.distribute_slices()
        
        for it_group in [self.menu_items, self.sliders]:        
            for it in it_group:
                it.update_local_to_screen()
            
    def layout_predefined(self, auto_slice = True):    
        #it = MenuItem  #used for PyDev autocompletion
        settings = bpy.context.user_preferences.addons['piemenus'].preferences
        for it_group in [self.menu_items, self.sliders]:
            for it in it_group:
                if settings.double_size:  #TODO: addon_prefs
                    it.scale = 2
                    it.x *= 2
                    it.y *= 2
                    
        
        self.border_patrol(bpy.context) #this shifts the menu instead of returning a value.
        
        for it_group in [self.menu_items, self.sliders]:
            for it in it_group:
                it.x += self.menu_x
                it.y += self.menu_y
                             
        if auto_slice:
            self.distribute_slices()
        
        for it_group in [self.menu_items, self.sliders]:  #need to do this in case we want to auto slice the pie            
            for it in it_group:
                it.update_local_to_screen()
            
        
        
              
    def layout_cardinal(self, rotate = False):
        settings = bpy.context.user_preferences.addons['piemenus'].preferences
        pie_items = [i for i in range(0,len(self.menu_items)) if self.menu_items[i].layout == "PIE"] #a list of indices
        
        #just for readability
        pi = math.pi
        shift = self.theta_shift
        aspect = 1 + self.aspect  #we will stretch the x coord and shrink y?
        diamond = self.diamond
        
        if settings.double_size:
            scale = 2
        else:
            scale = 1
        
        if len(pie_items)>8:
            self.layout_even(2*pi)
        else:
            l = len(pie_items)
            thetas = [pi, 0, - pi/2, pi/2 , 3*pi/4 + shift*pi/8, pi/4-shift*pi/8, -3*pi/4-shift*pi/8, -pi/4+shift*pi/8 ]
            
            #calculate the funky position of the off n,s,e,w locations   
            #height and width of menu
            A = self.radius
            B = self.radius * aspect
            
            #length of radius intersecting the diagonal between A and B
            #if menu were a diamond
            r = B*A/(math.sin(thetas[5])*B + math.cos(thetas[5])*A)
            R = self.radius - diamond*(self.radius - r)

            if l > 4 and l <= 6:
                #with 5 or 6 items, we bump east and west southward slightly to accomodate 3 * pi/4 items a NW, N, NE
                thetas[0] += pi/16  #bump down on left (west)
                thetas[1] -= pi/16  #bump down on right (east)
            
    
            for i in pie_items:
                it = self.menu_items[i]

                if i >3: #the non nsew
                    it.x = R * math.cos(thetas[i]) * scale * aspect
                    it.y = R * math.sin(thetas[i]) * scale
                else:
                    it.x = self.radius * math.cos(thetas[i]) * scale * aspect
                    it.y = self.radius * math.sin(thetas[i]) * scale
                
                it.scale = scale
                
                if rotate:
                    it.rot = thetas[i]
            
            self.border_patrol(bpy.context)
            
            #shift all in screen coords last        
            for it_group in [self.menu_items, self.sliders]:
                for it in it_group:
                    it.x += self.menu_x
                    it.y += self.menu_y
                    it.update_local_to_screen()
                    
            self.distribute_slices() #slices up the boundaries

                    
    ## fetch the item under the pointer
    def calc_by_angle(self, x, y):
        # mouse position converted from screen space to menu space
        x -= self.menu_x
        y -= self.menu_y
 
        # Cursor in inactive regions
        rad = pow(x, 2) + pow(y, 2)
        if rad < self.center_radius:
            return None
        if rad > self.max_radius:
            return -1
 
        angle = math.fmod(math.atan2(y, x) + 2*math.pi, 2*math.pi)
        #atan2 retunrs values in pi to -pi.  Adding 2pi and modding it with 2pi makes the number positive
        
        pie_items = [it for it in self.menu_items if it.calc_mode == 'ANGLE'] #here a list of items instead of indicies
        for it in pie_items:
            
            item_angle = math.fmod(math.atan2(it.y-self.menu_y, it.x-self.menu_x) + 2*math.pi, 2*math.pi)
           
            end = item_angle + it.angle_ccw
            start = item_angle - it.angle_cw
                     
            #the mouse angle falls nicely into the range specified by it.angle
            case_0 = (start < angle < end)
            if case_0:
                return it
            
            if start < 0:
                startr = math.fmod(start + 2*math.pi,2*math.pi) 
                if angle < end or angle > startr:
                    return it
               
            if end > 2*math.pi:
                endr = math.fmod(end + 2*math.pi,2*math.pi)
                if angle < endr or angle > start:
                    return it

        else:  # should never make it this far but you never know
            return None
    
    def calc_by_item(self, x, y):
        poly_items = [it for it in self.menu_items if it.calc_mode == 'POLY_LOOP']
        for it in poly_items:
            if it.calc(x,y):
                return it
        for slide in self.sliders:
            if slide.calc(x,y,precision = self.precision):
                return slide
    
    def calc_text(self):
        biggestdimensionX=biggestdimensionY=0
        settings = bpy.context.user_preferences.addons['piemenus'].preferences
        for it in self.menu_items:
            #find the biggest word in the menu and base the size of all buttons on that word
            
            blf.size(0, self.text_size, self.text_dpi)
            dimension = blf.dimensions(0, it.id)
    
            if dimension[0]>biggestdimensionX:
                biggestdimensionX = dimension[0]
            if dimension[1]>biggestdimensionY:
                biggestdimensionY = dimension[1]
                
        self.biggest_dim_x = biggestdimensionX
        self.biggest_dim_y = biggestdimensionY
        self.dimension_radio = blf.dimensions(0, "Off")[0]

        if settings.double_size: 
                self.text_size *= 2

        
    
    def border_patrol(self,context):
        region = context.region
        rv3d = context.space_data.region_3d

        width = region.width
        height = region.height
        
        #keep in mind, it.x and y have not been shifted to screen space yet.
        x_coords = [it.x for it in self.menu_items]
        y_coords = [it.y for it in self.menu_items]
        

        #presumes round box...so, need a more robust method that gets bound box of MenuItem searching all parts.
        #need to set a pixel safety threshold....perhaps in a "nitty gritty" user prefs
        menu_left  = self.menu_x + min(x_coords) - (self.biggest_dim_x/2 + 25) 
        menu_right = self.menu_x + max(x_coords) + self.biggest_dim_x/2 + 25
        
        menu_top = self.menu_y + max(y_coords) + self.biggest_dim_y/2 + 12
        menu_bot = self.menu_y + min(y_coords) - (self.biggest_dim_y/2 + 12)
        
        adjusted = False
        
        if menu_right > width:
            self.menu_x -= menu_right - width
            adjusted = True
        
        if menu_left < 0:
            self.menu_x += -1*menu_left
            adjusted = True
            
        if menu_top > height:
            self.menu_y -= menu_top - height
            adjusted = True
            
        if menu_bot  < 0:
            self.menu_y += -1*menu_bot
            adjusted = True
            
        return adjusted
     
    def calc_boxes(self):
        
        x = .5 * self.biggest_dim_x
        y = .5 * self.biggest_dim_y
        radio_x = self.dimension_radio
        
        op_box = pmu.make_round_box(-(x + 20), -(y + 5), x + 20, y + 5, self.corner_radius)
        radio_box = pmu.make_round_box(-(radio_x + 20), -(y + 5), radio_x + 5, y + 5, self.corner_radius)
        ic_quad = pmu.make_quad(16, 16, -(x+20)+11, 0, 0)
        ic_quad_radio = pmu.make_quad(16, 16, -(radio_x+20)+11, 0, 0)
        
        for it in self.menu_items:
            
            if not it.poly_bound:
                if it.type == "OP":
                    it.poly_bound = op_box
                elif it.type == "RADIO":
                    it.poly_bound = radio_box
                    it.cheap_box = pmu.make_quad(radio_x + 40, y + 10, 0, 0, 0)
                    
            if it.icon:
                if not it.icon_quad:
                    if it.type == "OP":
                        it.icon_quad = ic_quad
                    elif it.type == "RADIO":
                        it.icon_quad = ic_quad_radio
        
    # draw the menu
    def draw(self, parent, context):
        #get the addon settings/prefs
        settings = context.user_preferences.addons['piemenus'].preferences

        #grab the biggest text dimensions that we already calced previously        
        biggestdimensionX = self.biggest_dim_x
        biggestdimensionY = self.biggest_dim_y
        
        for it in self.sliders:
            #draw some text above it.
            blf.size(0, self.text_size, self.text_dpi)
            dimension = blf.dimensions(0, it.id)

            x = it.x - dimension[0]*.5
            y = it.y + (it.height + dimension[1])* 0.5 + 2
            # Draw text
            blf.enable(0, blf.SHADOW)
            blf.shadow_offset(0, 0, 0)
            blf.shadow(0, 5, 0.0, 0.0, 0.0, 1.0)
            bgl.glColor3f(self.rt, self.gt, self.bt)
            
            blf.position(0, x, y, 0)
            blf.draw(0, it.id)
            blf.disable(0, blf.SHADOW)
            
            

            #draw left side one color
            bgl.glColor4f(self.rsSelected,self.gsSelected, self.bsSelected,1.0)
            pmu.draw_outline_or_region(bgl.GL_TRIANGLE_FAN, it.screen_left)
            
            #draw the right side another color
            bgl.glColor4f(self.rsInner,self.gsInner, self.bsInner,1.0)
            pmu.draw_outline_or_region(bgl.GL_TRIANGLE_FAN, it.screen_right)
            
            #Draw box outline
            bgl.glColor4f(self.rsOutline,self.gsOutline, self.bsOutline,1.0)           
            pmu.draw_outline_or_region(bgl.GL_LINE_LOOP, it.screen_left)
            pmu.draw_outline_or_region(bgl.GL_LINE_LOOP, it.screen_right)
            
            #put the text on top
            blf.enable(0, blf.KERNING_DEFAULT)
            prop_text = str(getattr(it.data, it.prop, 0))[0:4]
            #prop_text = "Test"
            dimensions2 = blf.dimensions(0,prop_text)
            x2 =it.x - dimensions2[0] * 0.5
            y2 = it.y - dimensions2[1] * 0.5
            blf.position(0, x2, y2, 0)
            bgl.glColor4f(self.rt, self.gt, self.bt, 1.0)
            blf.draw(0, prop_text)
            blf.disable(0, blf.KERNING_DEFAULT)
                
        for it in self.menu_items:
            sel = it == parent.current
            it_poll = it.poll(context)
 
            # center item on the circle
            #x = (self.menu_x + it.x) - (dimension[0] * 0.5)
            #y = (self.menu_y + it.y) - (dimension[1] * 0.5)

            blf.size(0, self.text_size, self.text_dpi)
            dimension = blf.dimensions(0, it.id)

            #needed for box centering
            x = (it.x) - (biggestdimensionX * 0.5)
            y = (it.y) - (biggestdimensionY * 0.5)

            #needed offset for text centering
            blf.size(0, self.text_size, self.text_dpi)
            dimension = blf.dimensions(0, it.id)
            xt = ((biggestdimensionX-dimension[0]) * 0.5)
            yt = ((biggestdimensionY-dimension[1]) * 0.5)

            # Draw background buttons
            if sel and it_poll:
                bgl.glColor4f(self.ris, self.gis, self.bis, self.ais)
            else:
                bgl.glColor4f(self.ri, self.gi, self.bi, self.ai)
 
            #self.gl_pie_slice(bgl.GL_POLYGON, 8, it, x,y,30,90) #***
            #http://www.opengl.org/archives/resources/faq/technical/rasterization.htm#rast0120
            #self._round_box(bgl.GL_POLYGON, x - 20, y - 5, x + biggestdimensionX + 20, y + biggestdimensionY + 5)          
            
            if it.screen_poly_bound:
                shape = it.screen_poly_bound            
                pmu.draw_outline_or_region(bgl.GL_TRIANGLE_FAN, shape)
                bgl.glColor4f(self.ro, self.go, self.bo, 1.0)
                pmu.draw_outline_or_region(bgl.GL_LINE_LOOP, shape)
            
            bgl.glColor4f(self.ri, self.gi, self.bi, self.ai)
            #draw the circle
            if settings.clockBool:
                self._circle_(bgl.GL_TRIANGLE_FAN, (self.menu_x), (self.menu_y), 20)
            
                #draw the circle outline
                bgl.glColor4f(self.ro, self.go, self.bo, 1.0)
                self._circle_(bgl.GL_LINE_LOOP, (self.menu_x), (self.menu_y), 20)

                self._pointer_(bgl.GL_TRIANGLE_STRIP, (self.menu_x), (self.menu_y), self.pointerangle )
 
            # Draw text
            blf.enable(0, blf.SHADOW)
            blf.shadow_offset(0, 0, 0)
            blf.shadow(0, 5, 0.0, 0.0, 0.0, 1.0)
            if it_poll:
                bgl.glColor3f(self.rt, self.gt, self.bt)
            else:  # grayed out
                bgl.glColor3f(0.5, 0.5, 0.5)
            blf.position(0, x+xt, y+yt, 0)
            blf.draw(0, it.id)
            blf.disable(0, blf.SHADOW)
        
        
        #bind the named texure to GL_TEXTURE_2D
        #http://stackoverflow.com/questions/11217121/how-to-manage-memory-with-texture-in-opengl
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, settings.pieIconBindcode)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
        
        bgl.glEnable(bgl.GL_TEXTURE_2D)
        bgl.glEnable(bgl.GL_BLEND) 
        
        for it in self.menu_items:
            bgl.glColor4f(1, 1, 1, 1)
            if it.icon:
                #place the icon quad
                verts = it.screen_icon_quad
            
                bgl.glBegin(bgl.GL_QUADS)
            
                bgl.glTexCoord2f(it.tex_coords[0][0],it.tex_coords[0][1])
                bgl.glVertex2f(verts[0][0],verts[0][1])
                bgl.glTexCoord2f(it.tex_coords[1][0],it.tex_coords[1][1])
                bgl.glVertex2f(verts[1][0],verts[1][1])
                bgl.glTexCoord2f(it.tex_coords[2][0],it.tex_coords[2][1])
                bgl.glVertex2f(verts[2][0],verts[2][1])
                bgl.glTexCoord2f(it.tex_coords[3][0],it.tex_coords[3][1])
                bgl.glVertex2f(verts[3][0],verts[3][1])
            
                bgl.glEnd()
            
            #TODO
            #text value in center?
            #labe over top?    
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glDisable(bgl.GL_TEXTURE_2D)   
 
    ## nabbed from interface_draw.c
    def gl_pie_slice(self, mode, items, item, cx, cy, inner, outer): #***
        step = 360/items
        item -= 1
        bgl.glBegin(mode)
        for n in range(8):
            a = (item*360+180)/items+(n+8)*360/(items*15)
            x = math.sin(math.radians(a))
            y = math.cos(math.radians(a))
            bgl.glVertex2f(inner*x+cx,inner*y+cy)
        for n in range(16):
            a = ((item+1)*360+180)/items-n*360/(items*15)
            x = math.sin(math.radians(a))
            y = math.cos(math.radians(a))
            bgl.glVertex2f(outer*x+cx,outer*y+cy)
        for n in range(8):
            a = (item*360+180)/items+n*360/(items*15)
            x = math.sin(math.radians(a))
            y = math.cos(math.radians(a))
            bgl.glVertex2f(inner*x+cx,inner*y+cy)
        bgl.glEnd()

    def _circle_(self, mode, centerX, centerY, radius):
        bgl.glBegin(mode)
        for angle in range(0,20):
            angle = angle*2*math.pi/20 
            bgl.glVertex2f(centerX + (math.cos(angle) * radius), centerY + (math.sin(angle) * radius))
        bgl.glEnd()

    def _line_(self, mode, startX, startY, endX, endY):
        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(startX, startY)
        bgl.glVertex2f(endX, endY)
        bgl.glEnd()

    def _pointer_(self, mode, centerX, centerY, rotation):
        bgl.glBegin(mode);
        bgl.glColor4f(self.ris, self.gis, self.bis, self.ais)

        def draw_rotated(cos,sin, centerx, centery, x, y):
            nx = centerx + ((x * cos) - (y * sin))
            ny = centery + ((x * sin) + (y * cos))
            bgl.glVertex2f(nx,ny)

        sin = math.sin(rotation)
        cos = math.cos(rotation)

        draw_rotated(cos, sin, centerX, centerY, 0, 24)
        draw_rotated(cos, sin, centerX, centerY, -5, 14)
        draw_rotated(cos, sin, centerX, centerY, 5, 14)
        draw_rotated(cos, sin, centerX, centerY, -3, 10)
        draw_rotated(cos, sin, centerX, centerY, 3, 10)


        bgl.glPopMatrix()
        bgl.glEnd()


    def _round_box(self, mode, minx, miny, maxx, maxy):
       
        rad = self.corner_radius
        vec = [[0.195, 0.02],
               [0.383, 0.067],
               [0.55, 0.169],
               [0.707, 0.293],
               [0.831, 0.45],
               [0.924, 0.617],
               [0.98, 0.805]]
 
        # cache vec list to save 224 multiplications per 8 item menu redraw
        if self.vec_cache == None:
            self.vec_cache = [(point[0] * rad, point[1] * rad) for point in vec]
 
        bgl.glBegin(mode)
        #http://www.opengl.org/discussion_boards/showthread.php/164767-Newb-glVertex2fv(vertices-edges-i-1-)
        # start with corner right-bottom
        bgl.glVertex2f(maxx - rad, miny)
        bgl.glVertex2fv(bgl.Buffer(bgl.GL_FLOAT, [7,2],
                                   [(maxx - rad + point[0], miny + point[1]) for point in self.vec_cache]))
        bgl.glVertex2f(maxx, miny + rad)
 
        # corner right-top
        bgl.glVertex2f(maxx, maxy - rad)
        bgl.glVertex2fv(bgl.Buffer(bgl.GL_FLOAT, [7,2],
                                   [(maxx - point[1], maxy - rad + point[0]) for point in self.vec_cache]))
        bgl.glVertex2f(maxx - rad, maxy)
 
        # corner left-top
        bgl.glVertex2f(minx + rad, maxy)
        bgl.glVertex2fv(bgl.Buffer(bgl.GL_FLOAT, [7,2],
                                   [(minx + rad - point[0], maxy - point[1]) for point in self.vec_cache]))
        bgl.glVertex2f(minx, maxy - rad)
 
        # corner left-bottom
        bgl.glVertex2f(minx, miny + rad)
        bgl.glVertex2fv(bgl.Buffer(bgl.GL_FLOAT, [7,2],
                                   [(minx + point[1], miny + rad - point[0]) for point in self.vec_cache]))
        bgl.glVertex2f(minx + rad, miny)
 
        bgl.glEnd()



