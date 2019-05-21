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
    "description": "a modal operator ready to use from your addons as a module. enable only to see how it works.",
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
    imp.reload(modal)

else:
    import bpy
    import vmodal.modal

import bpy
import blf
import time

# a class must be created with your modal
class ModalExample(bpy.types.PropertyGroup) :

    def modal_init(self) :
        mdl = self.modal
        mdl.func = 'window_manager.my_addon.console'
        mdl.hudfunc = 'window_manager.my_addon.hud'
        mdl.check_function_calls()

    # default user modal function
    #try : f = bpy.context.scene.frame_current
    #except : f=1 #if addons enabled at startup, bpy is not quite ready

    # some info in the console
    def console(this, self,context,event,verbose=1) :
        mdl = bpy.context.window_manager.modal
        if event.type not in ['TIMER','MOUSEMOVE'] :
            global f
            if f != bpy.context.scene.frame_current :
                f = bpy.context.scene.frame_current
                print('.modal_example : frame is now %s'%f)
            if verbose == 2 :
                print('. modal_example events :')
                for i in dir(event) :
                    if i not in ['__doc__','__module__','__slots__','ascii','bl_rna','rna_type'] :
                        val = eval('event.%s'%i)
                        print('   .%s : %s'%(i,val))
            elif verbose == 1 :
                print('.modal_example events : %s %s'%(event.type,event.value))


    # a HUD in the 3D view
    def hud(this, self, context) :
        mdl = bpy.context.window_manager.modal

        if type(self.event) != str :
            
            evt = self.event

            if mdl.timer :
                #print(self.idx)
                if evt.type == 'TIMER' : self.idx = (self.idx + 1)%4
                blf.size(0, 11, 72)
                blf.position(0, 35, 30, 0)
                blf.draw(0, "timer %1.3f : %s"%( mdl.timer_refresh, ('|/-\\')[self.idx]) )

            if evt.type in [ 'MOUSEMOVE', 'TIMER' ] :
                if self.log != self.lastlog :
                    self.evttime = time.clock()
                self.log = self.lastlog
            else :
                self.log = self.lastlog = '%s %s'%(evt.type,evt.value)
                self.evttime = time.clock()

            if time.clock() - self.evttime > 1 :
                self.log = self.lastlog = ''

            blf.position(0, 35, 60, 0)
            blf.size(0, 13, 72)
            blf.draw(0, "%s"%(self.log))

            blf.position(0, 35, 45, 0)
            blf.size(0, 11, 72)
            blf.draw(0, 'Mx: %s My: %s'%(evt.mouse_region_x, evt.mouse_region_y))


# to use the provided example. see example.py for sample code
def register() :
    # registration of the example
    bpy.utils.register_class(ModalExample)
    bpy.types.WindowManager.myaddon = bpy.props.PointerProperty(type=ModalExample)

    # registration of vmodal
    vmodal.register_modal()
    bpy.types.WindowManager.myaddon.modal = bpy.props.PointerProperty(type=vmodal.ModalState)
    bpy.types.ModalState.bpy_instance_path.append('window_manager.myaddon.modal')


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