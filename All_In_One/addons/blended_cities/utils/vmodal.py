# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# pep8 compliant maybe one day>

# see init() for a quick function reference
import bpy
import time


def getArea(area_name='3D_VIEW',region_name=False):
    screen = bpy.context.window.screen
    for id, area in enumerate(screen.areas) :
        if area.type == area_name :
            if region_name == False : return area
            return area, getRegion(area,region_name)
    return False

def getRegion(area,region_name='WINDOW') :
    for ri, region in enumerate(area.regions) :
        #print(region.type)
        if region.type == region_name :
            return region
    return False

# basic print() with debuglevel
def dprint(str,level=1) :
    mdl = bpy_instance()
    loglevel = mdl.loglevel
    if level <= loglevel :
        print(str)


# MAIN property update function called by modal.status
def modalStatusChanged(self,context='') :
    dprint('MODAL status value changed to %s (instance states are %s)'%(self.status,self._inst),3)
    bpy.ops.wm.modal()


def modalStatusRestart(self,context='') :
    dprint('modalStatusRestart check',3)
    mdl = bpy_instance()
    if mdl.status == True :
        bpy.ops.wm.modal_start()

###########################
## modal configuration and state
###########################
def bpy_instance(id=0) :
    return eval('bpy.context.%s'%(bpy.types.ModalState.bpy_instance_path[id]))

class ModalState(bpy.types.PropertyGroup):
    '''
    Versatile modal addon properties. (vmodal.py addon)
        (status, func, hudfunc, hud, timer, timer_refresh)
        all these properties are read / write.

        status
            (boolean)
            returns True if running else False.
            set it to True to start the modal or False to stop it.
        func
            (string)
            returns the current function called by the modal
            set your function name and arguments here.
            it should have (self, context, event) as arguments.
            the function can be changed while running.
        hudfunc
            (string)
            returns the current function used by the modal
            to display info in the viewport.
            set your hudfunction name. DO NOT TYPE BRACKETS !
            event are available from the function with self.event :
            def my_hud(self,context):
                evt = self.event
                if evt.type == 'ESC' : ...
            you need to restart the modal to see the changes.
        hud
            (boolean)
            returns True if the hud is displayed else False
            set it to True to display the hud defined by hudfunc
            or false to hide it.
        area
            (string in 'VIEW_3D', 'IMAGE_EDITOR')
            area to attach the hud to. default 'VIEW_3D'
        timer
            (boolean)
            True if a timer event is running, else False.
            you need to restart the modal when you change that value.
        timer_refresh
            (float)
            timer event idle time in seconds.
            you need to restart the modal when you change that value

        see also :
            print(bpy.ops.wm.modal.__doc__)
    '''
    
    status       = bpy.props.BoolProperty(update=modalStatusChanged)   # True : start / False : stop

    func = bpy.props.StringProperty(        # user modal function
            default = 'modal_example(self,context,event,verbose=1)',
            description = 'your function name.')

    hudfunc = bpy.props.StringProperty(     # HUD function
            default = 'default_hud',
            description = 'your HUD function name. do NOT add arguments/brackets ! ') # user modal function

    hud = bpy.props.BoolProperty(           # HUD True/False
            default=True,
            description = 'display a HUD when running.',
            update=modalStatusRestart)

    area = bpy.props.EnumProperty(
            name='hud area',
            default='VIEW_3D',
            items=(('VIEW_3D', '3D View', ''),
                   ('IMAGE_EDITOR', 'Image Editor', '')
                )
        )

    timer = bpy.props.BoolProperty(         # event timer True/False
            default=True,
            description = 'enable timer event',
            update=modalStatusRestart)

    timer_refresh   = bpy.props.FloatProperty(
            min = 0.01,
            max = 60.0,                     # timer idle interval
            default=0.25,
            description = 'event timer latency',
            update=modalStatusRestart)

    loglevel = bpy.props.IntProperty(       # console log level
               default = 1,
               description = 'console log level')

    _inst = [False,False]
    bpy_instance_path = []

    def defaults(self) :
        self.func = bpy.types.ModalState.func[1]['default']
        self.hudfunc = bpy.types.ModalState.hudfunc[1]['default']
        self.hud = bpy.types.ModalState.hud[1]['default']
        self.area = bpy.types.ModalState.area[1]['default']
        self.timer = bpy.types.ModalState.timer[1]['default']
        self.timer_refresh = bpy.types.ModalState.timer_refresh[1]['default']
        self.loglevel = bpy.types.ModalState.loglevel[1]['default']
        dprint('modal default restored',1)

    def check_function_calls(self) :
        mdl = self
        if 'bpy.context.' not in mdl.func  : mdl.func  = 'bpy.context.' + mdl.func
        if '(' not in mdl.func  : mdl.func += '(context,event)'
        if '.' in mdl.func : 
            e = mdl.func.rindex('.')
            fe = mdl.func.rindex('(')
            addon = mdl.func[0:e]
            func = mdl.func[e+1:fe]
            try : test = hasattr(eval(addon),func)
            except : test = False
            if test :
                print('modal function found :\n%s'%(mdl.func))
            else :
                print('modal function not found :\nremoved')
        else :
            print('modal function need to be registered in bpy :\nremoved')
            mdl.func = ''

        if mdl.hud :
            if '.' in mdl.hudfunc : 
                if 'bpy.context.' not in mdl.hudfunc  : mdl.hudfunc  = 'bpy.context.' + mdl.hudfunc
                if '(' in mdl.hudfunc : mdl.hudfunc = mdl.hudfunc[0:mdl.hudfunc.rindex('(')]
                e = mdl.hudfunc.rindex('.')
                addon = mdl.hudfunc[0:e]
                func = mdl.hudfunc[e+1:]
                try : test = hasattr(eval(addon),func)
                except : test = False
                if test :
                    print('modal hud function found :\n%s'%(mdl.hudfunc))
                else :
                    print('modal hud function not found :\nremoved')
                    mdl.hudfunc = ''
            else :
                print('modal hud function need to be registered in bpy :\nremoved')
                mdl.hudfunc = ''

# check user function names
# (?) can't work since I don't know
# how to know the namespace of the user script
'''
def checkHudFunctionField(self,context='') :
# ...
def checkFunctionField(self,context='') :
    mdl = bpy.context.window_manager.modal
    f = self.func
    if '(' in f : f = f[0:f.index('(')]
    if hasattr(__name__,f) :
        mdl.func = self.func
        print('updated to %s'%mdl.func)
        return
    print('not found')
'''

###########
## the modal
###########
'''
Versatile modal addon properties.

bpy.ops.wm.modal()
    switch the state of the modal start or stop.
    will work only from viewport.
    (space bar > Modal from the viewport)
bpy.ops.wm.modal_start()
    start the modal
    (space bar > Modal Start)
bpy.ops.wm.modal_stop()
    you get it
    (space bar > Modal Stop)
bpy.ops.wm.modal_config()
    display a property dialog when invoked from the wiewport.
    (space bar > Modal Config)
bpy.ops.wm.modal_report()
    returns the modal status in the console or the viewport.
    (space bar > Modal Report)
see also :
    print(bpy.context.window_manager.modal.__doc__)
'''

modalinst = "class WM_OT_modal(bpy.types.Operator):\n\
    bl_idname = 'wm.modal'\n\
    bl_label = 'Modal'\n\
    bl_option = {'GRAB_POINTER'}\n\
    exclusive = bpy.props.BoolProperty()\n\
    _timer        = None\n\
    _hud_callback = None\n\
    _inst = 0\n\
    _count = 0\n\
    _regions = 0\n\
    _regionsy = 0\n\
    _overcrop = 0\n\
\n\
    def __init__(self) :\n\
        dprint('modal __init__',3)\n\
\n\
    def __del__(self):\n\
        dprint('modal __del__',3)\n\
\n\
    def modal(self, context, event):\n\
\n\
        if self._count == 0 :\n\
            x0 = event.mouse_prev_x - event.mouse_region_x\n\
            #image_ed, img_ui  = getArea('IMAGE_EDITOR','UI')\n\
            image_ed, img_ui  = getArea('VIEW_3D','TOOLS')\n\
            img_win  = getRegion(image_ed)\n\
            x1 = x0 + img_ui.width\n\
            x2 = x1 + img_win.width\n\
            self._regions = [x0,x1,x2]\n\
            ymin = event.mouse_prev_y - event.mouse_region_y\n\
            ymax = ymin + img_win.height\n\
            self._regionsy = [ymin,ymax]\n\
\n\
        self.alt = event.alt\n\
        self.ctrl = event.ctrl\n\
        self.mouse_prev_x = event.mouse_prev_x\n\
        self.mouse_prev_y = event.mouse_prev_y\n\
        self.mouse_region_x = event.mouse_region_x\n\
        self.mouse_region_y = event.mouse_region_y\n\
        self.mouse_x = event.mouse_x\n\
        self.mouse_y = event.mouse_y\n\
        self.oskey = event.oskey\n\
        self.shift = event.shift\n\
        self.type = event.type\n\
        self.value = event.value\n\
\n\
        mdl =  bpy_instance()\n\
        #dprint('modal intance %s cycle %s'%(self._inst,self._count),3)\n\
        context.area.tag_redraw()\n\
\n\
        if mdl._inst[self._inst] == False :\n\
            return self.cancel(context)\n\
\n\
        if event.type not in ['MOUSEMOVE','TIMER'] :\n\
            self.lastlog = '%s %s'%(event.type,event.value)\n\
\n\
        try : exec(mdl.func)\n\
        except :\n\
            dprint('wrong path or buggy function.',0)\n\
            mdl.status = False\n\
        self._count += 1\n\
\n\
        if self.exclusive == False and event.mouse_x > self._regions[1] and event.type == 'LEFTMOUSE' and event.value == 'PRESS' and context.area.type == 'IMAGE_EDITOR' :\n\
            self.exclusive = True\n\
\n\
        elif self.exclusive and event.type == 'LEFTMOUSE' and event.value == 'RELEASE' :\n\
            self.exclusive = False\n\
\n\
        return {'RUNNING_MODAL'} if self.exclusive else {'PASS_THROUGH'}\n\
\n\
    def invoke(self, context, event):\n\
        dprint('modal invoke',0)\n\
        mdl = bpy.context.window_manager.modal\n\
        mdl.status = not(mdl.status)\n\
        return {'FINISHED'}\n\
\n\
    def execute(self, context):\n\
        dprint('modal execute',0)\n\
        mdl =  bpy_instance()\n\
        dprint(mdl._inst,3)\n\
        if mdl.status == True :\n\
            if mdl._inst[0] or mdl._inst[1] : \n\
                startmsg = 'modal restarted'\n\
                popup = False\n\
            else :\n\
                startmsg = 'modal enabled'\n\
                popup = True\n\
\n\
            if mdl._inst[0] == False :\n\
                mdl._inst[0] = True\n\
                mdl._inst[1] = False\n\
                self._inst = 0\n\
            else :\n\
                mdl._inst[0] = False\n\
                mdl._inst[1] = True\n\
                self._inst = 1\n\
\n\
            context.window_manager.modal_handler_add(self)\n\
\n\
            area, region = getArea(mdl.area,'WINDOW')\n\
            #print('area : %s'%area)\n\
            if area and region and mdl.hud :\n\
                self.ctx = region\n\
\n\
                # (?) don't know how to prevent a crash\n\
                # if the hud callback function does not exists\n\
                # tried checkFunctionField() line 229 before.\n\
                try :\n\
                    self._hud_callback = region.callback_add(eval(mdl.hudfunc), (self, context), 'POST_PIXEL')\n\
                except :\n\
                    mdl._inst[0] = False\n\
                    mdl._inst[1] = False\n\
                    dprint('your hud function name is wrong, and you will die now.',0)\n\
                    return {'CANCELLED'}\n\
\n\
            if mdl.timer :\n\
                self._timer = context.window_manager.event_timer_add(mdl.timer_refresh, context.window)\n\
\n\
            self.log = ''\n\
            self.lastlog = ''\n\
            self.idx = 0\n\
            self.evttime = time.clock()\n\
            self.event = ''\n\
            dprint(startmsg,2)\n\
\n\
            return {'RUNNING_MODAL'}\n\
\n\
        else :\n\
            mdl._inst[0] = False\n\
            mdl._inst[1] = False\n\
            dprint('modal disabled',2)\n\
            return {'CANCELLED'}\n\
\n\
    def cancel(self, context) :\n\
        dprint('modal cancel %s'%self._inst,3)\n\
        mdl =  bpy_instance()\n\
        if self._hud_callback != None :\n\
            area, region = getArea(mdl.area,'WINDOW')\n\
            region.callback_remove(self._hud_callback)\n\
            self._hud_callback = None\n\
        if self._timer != None :\n\
            context.window_manager.event_timer_remove(self._timer)\n\
            self._timer = None\n\
            self.log = ''\n\
\n\
        dprint('modal instance %s ended after %s cycles'%(self._inst,self._count),2)\n\
\n\
        return{'CANCELLED'}\n\
"
exec(modalinst)

## operators
class ModalStart(bpy.types.Operator):
    '''see bpy.ops.wm.modal for info'''
    bl_idname = 'wm.modal_start'
    bl_label = 'Modal Start'

    def execute(self,context) :
        mdl =  bpy_instance()
        mdl.status = True
        return {'FINISHED'}


class ModalStop(bpy.types.Operator):
    '''see bpy.ops.wm.modal for info'''
    bl_idname = 'wm.modal_stop'
    bl_label = 'Modal Stop'

    def execute(self,context) :
        mdl =  bpy_instance()
        mdl.status = False
        return {'FINISHED'}


class ModalStatus(bpy.types.Operator):
    '''see bpy.ops.wm.modal for info'''

    bl_idname = 'wm.modal_status'
    bl_label = 'Modal Report'

    def execute(self, context):
        mdl =  bpy_instance()
        sta = 'enabled'if mdl.status else 'disabled' 
        dprint('modal is %s'%sta,2)
        return {'FINISHED'}


class ModalDefaults(bpy.types.Operator):
    '''see bpy.ops.wm.modal for info'''
    bl_idname = 'wm.modal_defaults'
    bl_label = 'Modal Default Values'

    def execute(self, context):
        mdl = bpy_instance()
        mdl.defaults()
        return {'FINISHED'}


## registers
# use (un)register_modal to use if from your work 
# no need to enable the addon, see example.py for sample code
def register_modal() :
    bpy.utils.register_class(WM_OT_modal)
    bpy.utils.register_class(ModalStart)
    bpy.utils.register_class(ModalStop)
    bpy.utils.register_class(ModalStatus)
    bpy.utils.register_class(ModalDefaults)
    bpy.utils.register_class(ModalState)


def unregister_modal() :
    mdl =  bpy_instance()
    if mdl.status :
        mdl.status = False
        return 'shutting down the modal first, please disable it again.'
    else :
        bpy.utils.unregister_class(ModalStart)
        bpy.utils.unregister_class(ModalStop)
        bpy.utils.unregister_class(ModalStatus)
        bpy.utils.unregister_class(ModalDefaults)
        bpy.utils.unregister_class(ModalState)
        bpy.utils.unregister_class(WM_OT_modal)

# to use the provided example. see example.py for sample code
def register() :
    register_modal()
    bpy.types.WindowManager.modal = bpy.props.PointerProperty(type=ModalState)
    bpy.types.ModalState.bpy_instance_path.append('window_manager.imagetools.modal')
    register_ui()


def unregister() :
    ret = unregister_modal()
    if typr(ret) == str :
        return False, 'shutting down the modal first, please disable it again.'
    unregister_ui()
    del bpy.types.WindowManager.modal

if __name__ == '__main__' :
    register_modal()
