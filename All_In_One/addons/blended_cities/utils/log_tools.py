# an attempt to spare my fingers / avoid write the same lines again and again in my various scripts
# forked from script events code
# 
# v0.1 (user : blended cities)

import bpy
import time
from development_icon_get import create_icon_list_all

## directions
# instanciate per script
# save logs
# log levels for file, console and popup :
# usage at eof
# for GE too

# Logs collection
class LoggerLogs(bpy.types.PropertyGroup) :
    level = bpy.props.StringProperty()
    icon  = bpy.props.StringProperty()
    msg   = bpy.props.StringProperty()
    time  = bpy.props.StringProperty()        #subtype='TIME',unit='TIME')
    blendertime  = bpy.props.StringProperty() #subtype='TIME',unit='TIME')
                                              #(?) more reliable than float ? don't know how to use it
  
# popup report configuration
class LoggerPopup(bpy.types.PropertyGroup):
    buffer  = bpy.props.IntProperty(default=3)
    loglevel = bpy.props.IntProperty(default=4)
    lastlogfirst = bpy.props.BoolProperty(default=True)
    width = bpy.props.IntProperty(default=300,min=10,max=500)
    height = bpy.props.IntProperty(default=20,min=20,max=500)


# console report configuration
class LoggerConsole(bpy.types.PropertyGroup):
    loglevel = bpy.props.IntProperty(default=4)
    timestamp = bpy.props.BoolProperty(default=True)
    levelstamp = bpy.props.BoolProperty(default=True)
    linelength = bpy.props.IntProperty(default=0)

    def dprint(self ,msg ,level = 2,hms = time.strftime('%H:%M:%S',time.localtime())) :
        if level <= self.loglevel :
            header = hms + ' ' if self.timestamp else ''
            if self.levelstamp : header += bpy.types.Logger.levelnames[level] + ' ' 
            if header != '' : msg = header + ': ' + msg 
            if self.linelength > 0 and len(msg) > self.linelength :
                print( msg[0:min(len(msg)-1,int(self.linelength/2)-2)]  + '[...]' + msg[-int(self.linelength/2)+3:])
            else :
                print(msg)


# Logs configuration
class Logger(bpy.types.PropertyGroup):
    buffer  = bpy.props.IntProperty(default=10)
    loglevel = bpy.props.IntProperty(default=4)        
    levelnames = ['ERROR', 'WARN ', 'INFO ', 'MISC ']
    levelicons = ['CANCEL', 'ERROR', 'INFO', 'TRIA_RIGHT']
    bpy_instance_path = []
    icons = create_icon_list_all()

    def new(self,msg,level=2,icon='NONE',console=True,popup=True,logit=True) :

        logs = self.logs
        
        if icon == 'NONE' :
            i = min(level,len(self.levelicons)-1)
            icon = self.levelicons[i]
        
        i = min(level,len(self.levelnames)-1)
        levelname = self.levelnames[i]
        
        logtime = str(time.time())
        blendertime = str(time.clock())
        hms = time.strftime('%H:%M:%S',time.localtime())

        # time.strftime('%Y/%m/%d - %H:%M:%S',time.localtime())
        # to read from log : 
        # t = bpy.context.window_manager.logs[0].time
        # time.strftime('%Y/%m/%d - %H:%M:%S',time.localtime(t))
        
        if logit and level <= self.loglevel :
            log = logs.add()
            log.level = levelname
            log.icon  = icon
            log.msg   = msg
            log.time  = logtime
            log.blendertime = blendertime
            self.clamp()
        
        string = '%s %s : %s'%(hms, levelname ,msg)
        
        if console :
            self.console.dprint(msg,level,hms)
        
        if popup :
            #if logit :
            #    bpy.ops.wm.log_popup(invoked_from_logger = True)
            # else :
            #    bpy.ops.wm.msg_popup(invoked_from_logger = True)
            bpy.ops.wm.log_popup( icon = icon,
                                    msg = msg,
                                    level = level,
                                    invoked_from_logger = logit
                                    )

    def pop(self,msg,level=2,icon='NONE',console=True) :
        self.new(msg,level,icon,console,True,False)

    def prt(self,msg,level=2,icon='NONE',) :
        self.new(msg,level,icon,True,False,False)

    def clamp(self) :
        while len(self.logs) > self.buffer :
            logs.remove(0)
            
    def history(self) :
        logs = self.logs
        for log in logs :
            tm = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(float(log.time)))
            print( '%s %s : %s'%(tm,log.level,log.msg) )

    def clear(self) :
        logs = self.logs
        initAttribute(logs)

# ###################################
# User Interface ops and functions  #
# ###################################

# a logger
# event level ranges from 0 (max gravity) to infinite (misc) 
class OT_LoggerNew(bpy.types.Operator) :
    '''
    '''
    bl_idname = 'log.new'
    bl_label = 'log an event'
    
    msg = bpy.props.StringProperty()
    level = bpy.props.IntProperty(default=2)
    icon = bpy.props.StringProperty(default='NONE')
    console = bpy.props.BoolProperty(default=True)
    popup = bpy.props.BoolProperty(default=True)

    def execute(self, context):
        logger.new(self.msg,self.level,self.icon,self.console,self.popup)
        return {'FINISHED'}


# an ui report events panel, whatever self/context is
class OT_LoggerPopup(bpy.types.Operator) :
    '''bpy.context.window_manager.LoggerPopup
    buffer = 3
    lastlogfirst = True
    '''
    bl_idname = 'wm.log_popup'
    bl_label = 'Report logs in the gui'

    level = bpy.props.IntProperty(default=4)    
    icon = bpy.props.StringProperty(default='NONE')
    msg = bpy.props.StringProperty()
    invoked_from_logger = bpy.props.BoolProperty()

    def draw(self, context):
        layout = self.layout
        #print('invoked_from_logger : %s'%self.invoked_from_logger)
        if self.invoked_from_logger :

            logger = eval('bpy.context.%s'%(bpy.types.Logger.bpy_instance_path[0]))
            logs = logger.logs
            popup = logger.popup

            if popup.lastlogfirst == False :
                # previous logs first
                idx = popup.buffer
                while idx > 0 :
                    try :
                        log = logs[-idx]
                        if idx > 1 :
                            row = layout.row()#layout.row(align=True)
                        else :
                            if popup.buffer > 1 : box = layout.box()
                            row = layout.row()
                        row.label(icon = log.icon, text = log.msg)
                    except : pass
                    idx -= 1
                    
            else :    
                # last log first
                idx = 1
                while idx <= popup.buffer :
                    try :
                        log = logs[-idx]
                        if idx == 2 : box = layout.box()
                        row = layout.row()
                        row.label(icon = log.icon, text = log.msg)
                    except : idx = popup.buffer
                    idx += 1
        else :
                tm = str(time.time())
                msg = self.msg
                row = layout.row()
                row.label(icon = self.icon, text = msg)

    def execute(self, context):
        logger = eval('bpy.context.%s'%(bpy.types.Logger.bpy_instance_path[0]))
        logs = logger.logs
        popup = logger.popup
        if self.level <= popup.loglevel :
            if self.invoked_from_logger == False :
                #log = logs.add()
                #log.icon  = self.icon
                #log.msg   = self.msg
                #log.time  = str(time.time())
                txt = self.msg
            else :
                log = logs[len(logs)-1]
                txt = log.msg
            if self.icon not in logger.icons : self.icon = 'PANEL_CLOSE'
            return context.window_manager.invoke_popup(self, width = min(20 + len(txt) * 7,140, 20 + popup.width), height = popup.height)
        return {'CANCELLED'}


def register() :
    bpy.utils.register_class(Logger)
    bpy.utils.register_class(LoggerLogs)
    bpy.utils.register_class(LoggerConsole)
    bpy.utils.register_class(LoggerPopup)
    bpy.utils.register_class(OT_LoggerPopup)

    Logger.console = bpy.props.PointerProperty(type=LoggerConsole)
    Logger.popup = bpy.props.PointerProperty(type=LoggerPopup)
    Logger.logs = bpy.props.CollectionProperty(type=LoggerLogs)

    #bpy.utils.register_class(OT_LoggerNew)


    #bpy.types.WindowManager.logger = bpy.props.PointerProperty(type=Logger)


def unregister() :
    bpy.utils.unregister_class(LoggerLogs)
    bpy.utils.unregister_class(Logger)
    bpy.utils.unregister_class(LoggerPopup)
    bpy.utils.unregister_class(LoggerConsole)
    bpy.utils.unregister_class(OT_LoggerPopup)
    #bpy.utils.unregister_class(OT_LoggerNew)
    #del bpy.types.WindowManager.logger


if __name__ == "__main__" :
    register()
    
'''
bpy.types.Scene.myclass = bpy.props.PointerProperty(type=MyClass)

from log_tools import LoggerLogs, Logger, LoggerPopup, LoggerConsole
from log_tools import register as log_install, unregister as log_uninstall
log_install()
MyClass.log = bpy.props.PointerProperty(type=Logger)
bpy.types.Logger.bpy_instance_path.append('scene.myclass.log')


log.new('message') # add to logs, popup and print it if loglevel are ok
log.new(icon = 'QUESTION', msg='how goes it ?')
log.new(level = 0, msg="I'm bugged...")
log.pop('message') # popup and print it if loglevels are ok
log.prt('message') # print it if console loglevel is ok
log.history() # all logged messages

log.loglevel
log.popup.loglevel
log.console.loglevel # minimum error level of the message if greater, message is ignored

log.buffer = 30 # history length

log.console.timestamp = True # show hours
log.console.levelstamp = True # show errorlevel
log.console.linelength = 80 # cut in order the message can fit in one line (0 : disabled)

# maybe wont last :
logops = bpy.ops.log
logops.new(level=0, msg='POPO',icon='INFO')
logops.new(level=2, icon="NONE", msg="")
'''

