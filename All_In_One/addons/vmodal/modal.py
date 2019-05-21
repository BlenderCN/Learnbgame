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

# TODO :
# provide support for multiple instance allowing several addons to hook to this module


bl_info = {
    "name": "versatile modal",
    "description": "a modal helper ready to use from your addons as a module. enable only to enable a demo.",
    "author": "Jerome Mahieux (Littleneo)",
    "version": (0, 5),
    "blender": (2, 5, 8),
    "api": 37702,
    "location": "View3D > Space > Modal ( Config, Start, Stop ) ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "System"
    }

if "bpy" in locals():
    import imp
    imp.reload(modal_ui)

else:
    import bpy
    from .modal_ui import *

import bpy
import time


def findArea(area_name='3D_VIEW',region_name=False):
    screen = bpy.context.window.screen
    for id, area in enumerate(screen.areas) :
        if area.type == area_name :
            if region_name == False : return area
            for ri, region in enumerate(area.regions) :
                if region.type == region_name :
                    return area, region
            return area, False
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
            description = "your HUD function name. do NOT add arguments/brackets ! ") # user modal function

    hud = bpy.props.BoolProperty(           # HUD True/False
            default=True,
            description = 'display a HUD when running.',
            update=modalStatusRestart)

    area = bpy.props.EnumProperty(
            name="hud area",
            default='VIEW_3D',
            items=(('VIEW_3D', "3D View", ""),
                   ('IMAGE_EDITOR', "Image Editor", "")
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
        dprint("modal default restored",1)

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
class WM_OT_modal(bpy.types.Operator):
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
    bl_idname = "wm.modal"
    bl_label = "Modal"

    _timer        = None
    _hud_callback = None
    _inst = 0
    _count = 0

    def __init__(self) :
        dprint("modal __init__",3)
        #mdl = bpy.context.window_manager.modal
        #if mdl.laststatus == mdl.status :
        #    dprint("init run")
        #    mdl.status = True

    def __del__(self):
        dprint("modal __del__",3)
        #dprint(self._hud_callback,type(self._hud_callback))
        #if self._hud_callback != None :
        #    self.ctx.callback_remove(self._hud_callback)
        #    self._hud_callback = None
        #if self._timer != None :
        #    context.window_manager.event_timer_remove(self._timer)
        #    self._timer = None
        #    self.log = ''


    def modal(self, context, event):
        # this to pass events to hud
        self.event = event

        scene = bpy.context.scene
        mdl =  bpy_instance()
        #mdl = bpy.context.window_manager.modal
        dprint("modal intance %s cycle %s"%(self._inst,self._count),3)
        context.area.tag_redraw()

        # go idle flag, disable hud and modal timer if running
        if mdl._inst[self._inst] == False :
            return self.cancel(context)

        # this because the hud has not enough time to see some events
        # like LEFTMOUSE RELEASE
        if event.type not in ['MOUSEMOVE','TIMER'] :
            self.lastlog = '%s %s'%(event.type,event.value)

        # user function call
        try : exec(mdl.func)
        except :
            dprint("wrong path or buggy function.",0)
            mdl.status = False
        self._count += 1
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        dprint("modal invoke",3)
        mdl = bpy.context.window_manager.modal
        mdl.status = not(mdl.status)
        return {'FINISHED'}

    def execute(self, context):
        dprint("modal execute",3)
        mdl =  bpy_instance()
        dprint(mdl._inst,3)
        if mdl.status == True :

            if mdl._inst[0] or mdl._inst[1] : 
                startmsg = "modal restarted"
                popup = False
            else :
                startmsg = "modal enabled"
                popup = True

            if mdl._inst[0] == False :
                mdl._inst[0] = True
                mdl._inst[1] = False
                self._inst = 0
            else :
                mdl._inst[0] = False
                mdl._inst[1] = True
                self._inst = 1

            context.window_manager.modal_handler_add(self)
            
            #print('ctx area : %s'%context.area.type,3)
            #if context.area.type == 'VIEW_3D' and mdl.hud :
            area, region = findArea(mdl.area,'WINDOW')
            #print('area : %s'%area)
            if area and region and mdl.hud :
                self.ctx = region
                
                # (?) don't know how to prevent a crash
                # if the hud callback function does not exists
                # tried checkFunctionField() line 229 before.
                try :
                    self._hud_callback = self.ctx.callback_add(eval(mdl.hudfunc), (self, context), 'POST_PIXEL')
                except :
                    mdl._inst[0] = False
                    mdl._inst[1] = False
                    dprint("your hud function name is wrong, and you will die now.",0)
                    return {'CANCELLED'}

            if mdl.timer :
                self._timer = context.window_manager.event_timer_add(mdl.timer_refresh, context.window)

            self.log = ''
            self.lastlog = ''
            self.idx = 0
            self.evttime = time.clock()
            self.event = ''
            dprint(startmsg,2)

            return {'RUNNING_MODAL'}

        else :
            mdl._inst[0] = False
            mdl._inst[1] = False
            dprint("modal disabled",2)
            return {'CANCELLED'}

    def cancel(self, context) :
        dprint('modal cancel %s'%self._inst,3)
        mdl =  bpy_instance()
        if self._hud_callback != None :
            area, region = findArea(mdl.area,'WINDOW')
            region.callback_remove(self._hud_callback)
            self._hud_callback = None
        if self._timer != None :
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
            self.log = ''

        dprint("modal instance %s ended after %s cycles"%(self._inst,self._count),2)

        return{'CANCELLED'}

## operators
class ModalStart(bpy.types.Operator):
    '''see bpy.ops.wm.modal for info'''
    bl_idname = "wm.modal_start"
    bl_label = "Modal Start"

    def execute(self,context) :
        mdl =  bpy_instance()
        mdl.status = True
        return {'FINISHED'}


class ModalStop(bpy.types.Operator):
    '''see bpy.ops.wm.modal for info'''
    bl_idname = "wm.modal_stop"
    bl_label = "Modal Stop"

    def execute(self,context) :
        mdl =  bpy_instance()
        mdl.status = False
        return {'FINISHED'}


class ModalStatus(bpy.types.Operator):
    '''see bpy.ops.wm.modal for info'''

    bl_idname = "wm.modal_status"
    bl_label = "Modal Report"

    def execute(self, context):
        mdl =  bpy_instance()
        sta = 'enabled'if mdl.status else 'disabled' 
        dprint("modal is %s"%sta,2)
        return {'FINISHED'}


class ModalDefaults(bpy.types.Operator):
    '''see bpy.ops.wm.modal for info'''
    bl_idname = "wm.modal_defaults"
    bl_label = "Modal Default Values"

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
    mdl =  bpy_instance()
    if mdl.status :
        mdl.status = False
        return "shutting down the modal first, please disable it again."
    unregister_modal()
    unregister_ui()
    del bpy.types.WindowManager.modal


if __name__ == "__main__" :
    register_modal()