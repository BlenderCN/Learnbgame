import time
import bpy
import bgl
import blf
from . ui_tools import *

########
## PANEL
########

class ImageTools_panel(bpy.types.Panel) :
    bl_label = 'Tools'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_idname = 'imagetools'

    @classmethod
    def poll(self,context) :
        for area in bpy.context.window.screen.areas :
            if area.type == 'IMAGE_EDITOR' :
                return True
                img = area.spaces[0].image
                if type(img) == bpy.types.Image : return True
        return False

    def draw(self, context) :
        imtool = bpy.context.window_manager.imagetools
        for area in bpy.context.window.screen.areas :
            if area.type == 'IMAGE_EDITOR' :
                img = area.spaces[0].image
                if type(img) == bpy.types.Image :
                    if imtool.showcrop :
                        rev_id = max(0, img.tempid() + 1)
                    else :
                        rev_id = max(0, img.tempid())
                    rev = img.revision(rev_id)
                    prev_rev = img.revision(rev.source)

        layout  = self.layout
        state = False if imtool.showcrop else True
        if type(img) == bpy.types.Image :
            
            ## options
            box = layout.box()
            split = box.split(0.4)
            col = split.column()
            col.label(text='History :',icon="TIME")
            col.label(text='Update :',icon="FILE_REFRESH")

            col = split.column()
            # revision navigation
            row = col.row(align=True)
            row.enabled = state
            if img.tempid() >= 0 :
                row.operator('image.previous',text='',icon='TRIA_LEFT')
                rowid = row.row(align=True)
                rowid.alignment = 'CENTER'
                rowid.label( text='  %s '%img.tempid() )
            else :
                rowid = row.row(align=True)
                rowid.alignment = 'LEFT'
                rowid.label( text='source' )
            if rev.outdated :
                row.prop(imtool,'refresh',icon='FILE_REFRESH',icon_only=True)
            if (img.tempid() >= 0 and img.revision_count() == rev.id + 1) :
                row.prop(imtool,'rev_del',icon='PANEL_CLOSE',icon_only=True)
                icon = 'NEW'
            else : icon = 'TRIA_RIGHT'
            row.operator('image.next',text='',icon=icon)
            # update buttons
            row = col.row(align=True)
            row.enabled = state
            row.prop(imtool,'updatenow',text = 'now', toggle=True)
            row.prop(imtool,'autoupdate',text = 'auto')

            ## colours
            box = drawExpand(layout,'Colours','window_manager.imagetools.tempset[%s].expand_colours'%rev_id,True)
            if box :

                split = box.split(0.4)

                col = split.column(align=True)
                col.label(text='Brightness :',icon="LAMP_SUN")
                col.label(text='Contrast :',icon="COLOR")
                col.label(text='Levels :',icon="IMAGE_ALPHA")
                col.label(text='Balance :',icon="MANIPUL")
                col.label(text='Colors Number :',icon="COLOR")

                col = split.column(align=True)
                col.enabled = state
                # brightness
                col.prop(rev,'brightness', slider=True)
                # contrast
                if rev.autocontrast :
                    col.prop(rev,'autocontrast',toggle=True, slider=True)
                else :
                    row = col.row(align=True)
                    row.prop(rev,'contrast')
                    row.prop(rev,'autocontrast',toggle=True)
                # levels
                if rev.autolevels :
                    col.prop(rev,'autolevels',toggle=True)
                else :
                    row = col.row(align=True)
                    row.prop(rev,'level_b')
                    row.prop(rev,'level_w')
                    row.prop(rev,'autolevels',toggle=True)
                # balance
                #if rev.autolevels :
                #    col.prop(rev,'autolevels',toggle=True)
                #else :
                row = col.row(align=True)
                row.prop(rev,'balance_r')
                row.prop(rev,'balance_g')
                row.prop(rev,'balance_b')

                # colors number
                col.prop(rev,'colors_nb')

            ## transformations
            box = drawExpand(layout,'Transformations','window_manager.imagetools.tempset[%s].expand_transfs'%rev_id,True)
            if box :
                split = box.split(0.4)
                col = split.column(align=True)

                col.label(text='Crop :',icon="MESH_GRID")
                if rev.canvas_area != 'off' :
                    col.label(text='')
                col.label(text='Resize :',icon="VIEWZOOM")
                col.label(text='Flip :',icon="ARROW_LEFTRIGHT")
                col.label(text='Rotate :',icon="FILE_REFRESH")
                #col.label(text='Mirror :',icon="MOD_MIRROR")

                col = split.column(align=True)
                # crop
                row = col.row(align=True)
                row.prop(rev,'canvas_area',text='')
                if rev.canvas_area != 'off' :
                    if rev.canvas_area == 'offset' :
                        row.prop(rev,'offset_x')
                        row.prop(rev,'offset_y')
                    else :
                        row.prop(rev,'canvas_percent',toggle=True)
                    row = col.row(align=True)
                    if imtool.has_helpers : row.prop(imtool,'showcrop',toggle=True,text ='Show')
                    row.prop(rev,'width')
                    row.prop(rev,'height')

                # resize
                row = col.row(align=True)
                row.enabled = state
                row.prop(rev,'resize_x')
                row.prop(rev,'resize_y')
                row.prop(rev,'resize_percent',toggle=True)

                # flip
                row = col.row(align=True)
                row.enabled = state
                row.prop(rev,'vflip',text='X',toggle=True)
                row.prop(rev,'hflip',text='Y',toggle=True)
                #row.prop(rev,'exif',text='exif')

                # rotate
                row = col.row(align=True)
                row.enabled = state
                row.prop(rev,'degrees')
                row.prop(rev,'smoothrot',toggle=True)
                # mirror
                #row = col.row(align=True)
                #row.operator('image.mirror',text='horizontal')
                #row.operator('image.mirror',text='vertical').dir = 'Y'

            ## FX
            box = drawExpand(layout,'FX','window_manager.imagetools.tempset[%s].expand_fx'%rev_id,True)
            if box :
                split = box.split(0.4)
                col = split.column(align=True)
                col.label(text='Blur :',icon="MOD_FLUIDSIM")
                col.label(text='sharpen :',icon="PMARKER")
                col.label(text='Noise :',icon="IMAGE_RGB")
                col.label(text='Emboss :',icon="CLIPUV_DEHLT")
                col.label(text='Oilify :',icon="MOD_FLUIDSIM")

                col = split.column(align=True)
                col.enabled = state
                # blur
                col.prop(rev,'blur', slider=True)
                # sharpen
                col.prop(rev,'sharpen', slider=True)
                # noise
                row = col.row(align=True)
                #row.prop_menu_enum(rev,'noise',icon="MESH_GRID")
                row.prop(rev,'noise',text='')
                if rev.noise not in ['off','reduce'] :
                    row.prop(rev,'noise_value', slider=True)
                # emboss
                row = col.row(align=True)
                row.prop_enum(rev,'emboss','off')
                row.prop_enum(rev,'emboss','emboss')
                row.prop_enum(rev,'emboss','embossmore')
                # oilify
                col.prop(rev,'oil', slider=True)

            box = layout.box()
            split = box.split(0.4)
            col = split.column()
            col.label(text='xnNerds :',icon="SCRIPTWIN")
            col = split.column()
            col.enabled = state
            # command
            col.prop(rev,'cmd')
        row = layout.box().row()
        row.enabled = state
        row.operator('image.clipboard',text='import clipboard as new')


class ImageTools_helpers(bpy.types.PropertyGroup) :
    drag = bpy.props.BoolProperty()
    mouse_xo = bpy.props.IntProperty()
    mouse_yo = bpy.props.IntProperty()

    last_over_act =  bpy.props.StringProperty(default='')

    def start_crop(self) :
        mdl = bpy.context.window_manager.imagetools.modal
        mdl.func = 'bpy.context.window_manager.imagetools.helpers.console(context,event,verbose=1)'
        mdl.timer = True
        mdl.timer_refresh = 0.03
        mdl.hud = True
        mdl.area = 'IMAGE_EDITOR'
        mdl.hudfunc = 'bpy.context.window_manager.imagetools.helpers.hud'
        mdl.loglevel = 1
        mdl.status = True

    def stop(self) :
        mdl = bpy.context.window_manager.imagetools.modal
        mdl.status = False

    def console(self,context,event,verbose=1) :
        mdl = bpy.context.window_manager.imagetools.modal
        if event.type not in ['TIMER','MOUSEMOVE'] :
            global f
            #if f != bpy.context.scene.frame_current :
            #    f = bpy.context.scene.frame_current
            #    print('.modal_example : frame is now %s'%f)
            if verbose == 2 :
                print('. modal_example events :')
                for i in dir(event) :
                    if i not in ['__doc__','__module__','__slots__','ascii','bl_rna','rna_type'] :
                        val = eval('event.%s'%i)
                        print('   .%s : %s'%(i,val))
            elif verbose == 4 :
                #print('.modal_example :\n events : %s %s\nlogs : %s \n%s'%(event.type,event.value,dir(event),dir(context)))
                print('\narea : %s \nregion : %s'%(bpy.context.area.type,bpy.context.region.type))
                print('area : %s \nregion : %s'%(context.area.type,context.region.type))
    
    # HUD
    def hud(dummy, self, context) :
        #if getattr(self,'type') :
        if 'type' in dir(self) :
            imtool = bpy.context.window_manager.imagetools
            mdl = imtool.modal
            bpy.ops.image.view_all()
            img = active()
            # something to do when fullscreened.. test should be here
            if 2==2 :
                rev = img.revision()
                if rev.canvas_area != 'off' :
                    #if len(self.lastlog) >= 2 : self.log = self.lastlog.pop(0)
                    #else : self.log = self.lastlog[0]
                    evt = self#.event
                    #print(dir(self.event))
                    imtool = bpy.context.window_manager.imagetools

                    # mouse can be outside of our area so don't use context
                    #area,region = findArea('IMAGE_EDITOR','WINDOW')
                    area = context.area
                    region = context.region
                    area_sx = region.width
                    area_sy = region.height 

                    #image_ed, img_ui  = getArea('IMAGE_EDITOR','UI')
                    #img_win  = getRegion(image_ed)
                    #img_prev  = getRegion(image_ed,'PREVIEW')

                    zoom_x = area.spaces[0].zoom[0]
                    zoom_y = area.spaces[0].zoom[1]
                    
                    #print('log : %s last(%s)'%(self.log,self.lastlog))
                    #print('evt : %s  %s'%(evt.type,evt.value))
                    #print(self.lastlog)
                    #print(context.space_data.type)
                    #print(dir(evt))

                    #
                    #if area.type == context.area.type and region.type == context.region.type :
                    x_min,x,x_max = self._regions
                    y_min,y_max = self._regionsy

                    if x < self.mouse_x < x_max and y_min < self.mouse_y < y_max :
                        mouse_x = self.mouse_x - x
                        mouse_y = self.mouse_y - y_min
                    else :
                        mouse_x = False
                        mouse_y = False

                    img_sx, img_sy = img.size
                    img_sx = int( img_sx * zoom_x)
                    img_sy = int( img_sy * zoom_y)
                    
                    img_x0 = int( (area_sx - img_sx) * 0.5 )
                    img_y0 = int( (area_sy - img_sy) * 0.5 )

                    offset_x = int( rev.offset_x * zoom_x)
                    offset_y = int( rev.offset_y * zoom_y)

                    width = int( rev.width * zoom_x)
                    height = int( rev.height * zoom_y)

                    blf.size(0, 11, 72)

                    # enable action zones in crop selection box
                    drag = up = down = right = left = False

                    if rev.canvas_area == 'offset' :
                        crop_x = img_x0 + min(offset_x,img_sx)
                        crop_sx = max( 0 , min(img_sx - offset_x, width) )

                        crop_sy = min(img_sy,height)
                        crop_y = max(img_y0 - crop_sy, img_y0 + img_sy - crop_sy - offset_y)
                        if crop_y - img_y0 < 0 :
                            crop_sy += crop_y - img_y0
                            crop_y = img_y0

                        txt_offx = offset_x
                        txt_offx_x = crop_x
                        txt_offx_y = crop_y + crop_sy

                        x,y = blf.dimensions(0, '%s'%(offset_y))
                        txt_offy = offset_y
                        txt_offy_x = txt_offx_x - x
                        txt_offy_y = txt_offx_y - y

                        txt_sizx = '%s'%rev.width
                        txt_sizy = '%s'%rev.height

                        drag = up = down = right = left = True

                    else :
                        
                        drag = False
                        
                        txt_offx = ''
                        txt_offy = ''
                        txt_offx_x = 0
                        txt_offx_y = 0
                        txt_offy_x = 0
                        txt_offy_y = 0
                        if rev.canvas_percent :
                            crop_sx = int( min( (rev.width * 0.01) * img_sx ,img_sx) ) + 1
                            crop_sy = int( min( (rev.height * 0.01) * img_sy ,img_sy) ) + 1
                            txt_sizx = '%s%s'%(rev.width,'%')
                            txt_sizy = '%s%s'%(rev.height,'%')
                        else :
                            crop_sx = min(img_sx,width)
                            crop_sy = min(img_sy,height)
                            txt_sizx = '%s'%rev.width
                            txt_sizy = '%s'%rev.height

                        if rev.canvas_area == 'top-left' :
                            crop_x = img_x0
                            crop_y = img_y0 + img_sy - crop_sy
                            down = right = True
                    
                        elif rev.canvas_area == 'top-center' :
                            crop_x = img_x0 + int( (img_sx - crop_sx) * 0.5 )
                            crop_y = img_y0 + img_sy - crop_sy
                            down = right = left = True

                        elif rev.canvas_area == 'top-right' :
                            crop_x = img_x0 + img_sx - crop_sx
                            crop_y = img_y0 + img_sy - crop_sy
                            down = left = True

                        elif rev.canvas_area == 'center-left' :
                            crop_x = img_x0
                            crop_y = img_y0 + int( (img_sy - crop_sy) * 0.5 )
                            up = down = right = True

                        elif rev.canvas_area == 'center' :
                            crop_x = img_x0 + int( (img_sx - crop_sx) * 0.5 )
                            crop_y = img_y0 + int( (img_sy - crop_sy) * 0.5 )
                            up = down = right = left = True
                        
                        elif rev.canvas_area == 'center-right' :
                            crop_x = img_x0 + img_sx - crop_sx
                            crop_y = img_y0 + int( (img_sy - crop_sy) * 0.5 )
                            up = down = left = True
                            
                        elif rev.canvas_area == 'bottom-left' :
                            crop_x = img_x0
                            crop_y = img_y0
                            up = right = True
                            
                        elif rev.canvas_area == 'bottom-center' :
                            crop_x = img_x0 + int( (img_sx - crop_sx) * 0.5 )
                            crop_y = img_y0
                            up = right = left = True
                        
                        elif rev.canvas_area == 'bottom-right' :
                            crop_x = img_x0 + img_sx - crop_sx
                            crop_y = img_y0
                            up = left = True
                    
                    #print(crop_x - img_x0, crop_y - img_y0, crop_sx, crop_sy)

                    x,y = blf.dimensions(0,txt_sizx)
                    txt_sizx_x = crop_x + int((crop_sx - x)* 0.5)
                    txt_sizx_y = crop_y -11

                    x,y = blf.dimensions(0,txt_sizy)
                    txt_sizy_x = crop_x + crop_sx
                    txt_sizy_y = crop_y + int((crop_sy - y) * 0.5)

                    bgl.glColor4f(0.4, 0.4, 0.4, 0.5)

                    # event
                    blf.position(0, 35, 50, 0) 
                    blf.size(0, 13, 72)
                    blf.draw(0, "%s"%(self.log))

                    # timer
                    if mdl.timer :
                        if evt.type == 'TIMER' : self.idx = (self.idx + 1)%4
                        blf.size(0, 11, 72)
                        blf.position(0, 35, 35, 0)
                        blf.draw(0, "timer %1.3f : %s"%( mdl.timer_refresh, ('|/-\\')[self.idx]) )

                    # is over ?
                    overcrop = False
                    bgl.glColor4f(0.3, 0.7, 0.3, 0.3)
                    if mouse_x :
                        blf.position(0, 35, 20, 0)
                        blf.size(0, 11, 72)
                        blf.draw(0, 'Mx: %s My: %s %s'%(mouse_x, mouse_y,self._regions))
                        if (crop_x < mouse_x < crop_x + crop_sx and crop_y < mouse_y < crop_y + crop_sy) :
                            overcrop = True
                            bgl.glColor4f(0.5, 0.7, 0.5, 0.5)

                    # crop selection box
                    bgl.glEnable(bgl.GL_BLEND)
                    bgl.glBegin(bgl.GL_QUADS)
                    drawRectangle(crop_x , crop_y , crop_sx , crop_sy, 0 )
                    bgl.glEnd()

                    bgl.glColor4f(1.0, 1.0, 1.0, 1.0)

                    if evt.type in [ 'MOUSEMOVE', 'TIMER' ] :
                        if self.log != self.lastlog :
                            self.evttime = time.clock()
                        self.log = self.lastlog
                    else :
                        self.log = self.lastlog = '%s %s'%(evt.type,evt.value)
                        self.evttime = time.clock()

                    #if time.clock() - self.evttime > 1 :
                    #    self.log = self.lastlog = ''

                    # drag status change ?
                    if dummy.drag == False and overcrop and self.log == 'LEFTMOUSE PRESS' :
                        dummy.drag = True
                        dummy.mouse_xo = mouse_x
                        dummy.mouse_yo = mouse_y

                    elif dummy.drag  and self.log == 'LEFTMOUSE RELEASE' :
                        dummy.drag = False
                        dummy.last_over_act = ''

                    # define over action
                    stretch = 8
                    over_act = ''
                    if dummy.drag :

                        if rev.canvas_percent and  rev.canvas_area != 'offset' : 
                            percent_x = 100.0 / img_sx
                            percent_y = 100.0 / img_sy
                        else : percent_x = percent_y = 1

                        st_y = False
                        if down and ('down' in dummy.last_over_act or mouse_y - crop_y < stretch) :
                            rev.height  = int( ( ( crop_sy - mouse_y + dummy.mouse_yo ) * percent_y ) / zoom_y )
                            st_y = True
                            over_act = 'resize down'

                        elif up and ('up' in dummy.last_over_act or mouse_y > crop_y + crop_sy - stretch) :
                            rev.offset_y  = int( ( offset_y - mouse_y + dummy.mouse_yo ) / zoom_y )
                            rev.height  = int( ( ( crop_sy + mouse_y - dummy.mouse_yo ) * percent_y ) / zoom_y )
                            st_y = True
                            over_act = 'resize up'


                        st_x = False
                        if right and ('right' in dummy.last_over_act or mouse_x > crop_x + crop_sx - stretch) :
                            rev.width  = int( ( ( crop_sx + mouse_x - dummy.mouse_xo ) * percent_x )  / zoom_x )
                            st_x = True
                            if over_act == '' : over_act = 'resize right' 
                            else : over_act += '/right'
                            
                        elif left and ('left' in dummy.last_over_act or mouse_x - crop_x < stretch) :
                            #rev.width  = int( ( ( crop_sx * percent_x ) + ( mouse_x - dummy.mouse_xo ) ) / zoom_x )
                            rev.width  = int( ( ( crop_sx - mouse_x + dummy.mouse_xo ) * percent_x )  / zoom_x )
                            rev.offset_x  = int( ( offset_x + mouse_x - dummy.mouse_xo ) / zoom_x )
                            st_x = True
                            if over_act == '' : over_act = 'resize left'
                            else : over_act += '/left'

                        if drag and ('drag'== dummy.last_over_act  or ( st_x == False and st_y == False )) :
                            rev.offset_x  = int( ( offset_x + ( mouse_x - dummy.mouse_xo ) ) / zoom_x )
                            rev.offset_y  = int( ( offset_y - ( mouse_y - dummy.mouse_yo ) ) / zoom_y )
                            over_act = 'drag'
                        
                        dummy.mouse_xo = mouse_x
                        dummy.mouse_yo = mouse_y
                        blf.position(0, 35, 70, 0)
                        blf.draw(0, over_act)
                        dummy.last_over_act = over_act
                        #print(rev.width, crop_sx,percent_x,zoom_x,mouse_x - dummy.mouse_xo )

                    # box selection areas
                    #print(overcrop,over_act)
                    if overcrop or over_act != '' :
                        bgl.glEnable(bgl.GL_BLEND)
                        bgl.glBegin(bgl.GL_LINES)
                        bgl.glLineWidth(5)
                        if up : drawLinef(crop_x, crop_y + crop_sy - stretch, crop_x + crop_sx, crop_y + crop_sy - stretch)
                        if down : drawLinef(crop_x, crop_y + stretch, crop_x + crop_sx, crop_y + stretch)
                        if left : drawLinef(crop_x + stretch, crop_y, crop_x + stretch, crop_y + crop_sy)
                        if right : drawLinef(crop_x + crop_sx - stretch, crop_y, crop_x + crop_sx - stretch, crop_y + crop_sy)
                        bgl.glEnd()

                    # crop info
                    if txt_offx != '' :
                        blf.position(0, txt_offx_x, txt_offx_y, 0)
                        blf.draw(0, '%s'%(txt_offx))
                        blf.position(0, txt_offy_x, txt_offy_y, 0)
                        blf.draw(0, '%s'%(txt_offy))
                    blf.position(0, txt_sizx_x, txt_sizx_y, 0)
                    blf.draw(0, '%s'%(txt_sizx))
                    blf.position(0, txt_sizy_x, txt_sizy_y, 0)
                    blf.draw(0, '%s'%(txt_sizy))

                else :
                    imtool.showcrop = False

# 0 : error, abort
# 5 : routines, func internals
def dprint(string,lvl=5) :
    if lvl < 4 :
        print(string)


def active(verbose=False) :    
    img, imged_id = checkUVpanels(verbose)
    return img


def checkUVpanels(verbose=False):
    images = []
    locations=[]
    screens={}
    imged_id = -1
    active_screen = bpy.context.window.screen.name

    for screen in bpy.data.screens :
        dprint(screen.name,5)
        if screen.show_fullscreen == False :
            for id, area in enumerate(screen.areas) :
                dprint('    %s : %s'%(id,area.type),5)
                if area.type == 'IMAGE_EDITOR' :
                    locations.append(' .screen %s'%(screen.name))
                    img = area.spaces[0].image
                    if type(img) == bpy.types.Image :
                        locations[-1] += ' :\n  '+img.name
                        dprint('    >> '+img.name)
                        images.append(img)
                        screens[screen.name] = id
                    else :
                        locations[-1] += ' :\n  <nothing>'
                        dprint('    >> <nothing>')
    if len(images) == 0 :
        dprint('no active image found.',0)
        img = None
    elif len(images) > 1 :
        img = images[0]
        for im in images[1:] :
            if im != img :
                dprint('%s Image editors are opened with different active images :'%len(images),0)
                for loc in locations : dprint(loc,0)
                dprint('either close them excepted one or load the same image in each.',0)
                img = None
                break
    else : img = images[0]
    
    # to refresh uv editor panel if visible : returns the panel tag for later use
    if type(img) == bpy.types.Image :
        if active_screen in screens : imged_id = screens[active_screen]
        dprint('selected %s (%s)'%(img.name,imged_id))

    return img, imged_id

def getArea(area_name='3D_VIEW',region_name=False):
    screen = bpy.context.window.screen
    for id, area in enumerate(screen.areas) :
        if area.type == area_name :
            if region_name == False : return area
            return area, getRegion(area,region_name)
    return False

def getRegion(area,region_name='WINDOW') :
    for ri, region in enumerate(area.regions) :
        if region.type == region_name :
            return region
    return False



def drawLinef(from_x, from_y, to_x, to_y):
    #bgl.glLineWidth(5)
    bgl.glVertex2f(from_x, from_y)
    bgl.glVertex2f(to_x, to_y)

def drawRectangle (ox, oy, ow, oh, padding=0):

    x = ox - 2 * padding
    y = oy - padding
    w = ow + 4 * padding
    h = oh + 2 * padding

    drawLinef(x,   y,   x+w, y)
    drawLinef(x+w, y,   x+w, y+h)
    drawLinef(x+w, y+h, x  , y+h)
    drawLinef(x  , y+h, x  ,   y)
