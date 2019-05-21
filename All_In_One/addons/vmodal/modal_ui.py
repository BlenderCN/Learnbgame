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

import bpy

## property update functions
#called from the self.props dialog below (misc.)
def toggleConsole(self,context='') :
    if self.csl :
        bpy.ops.wm.console_toggle()

def debugConsole(self,context='') :
    mdl = bpy.context.window_manager.modal
    if self.debugcsl : mdl.loglevel = 2
    else : mdl.loglevel = -1

def restoreModalDefaults(self,context='') :
    modal = bpy.context.window_manager.modal
    modal.defaults()

## modal config panel
class ModalConfig(bpy.types.Operator):
    '''see bpy.ops.wm.modal for info'''
    bl_idname = "wm.modal_config"
    bl_label = "Modal Config"
    bl_options = {'REGISTER'}

    csl   = bpy.props.BoolProperty(          # toggle console from the popup
            default = True,
            description = 'show console',
            update  = toggleConsole)

    debugcsl = bpy.props.BoolProperty(       # show log in the console
               default = False,
               description = 'show addon debug',
               update  = debugConsole)

    restore  = bpy.props.BoolProperty(       # restore modal default
               default = False,
               description = 'restore default configuration',
               update = restoreModalDefaults)

    # could be useful if one need to confirm the updates.
    # see execute copy_props_values() and replace mdl 
    # more cool to see the changes directly here

    #func = bpy.props.StringProperty(
    #        description = 'your function name.')
    #        #update = checkFunctionField
    #        #)
    #hudfunc = bpy.props.StringProperty(
    #        description = "your HUD function name. do NOT add arguments/brackets ! ") # user modal function
    
    #hud = bpy.props.BoolProperty(
    #        description = 'display the HUD when running.'
    #        )
    #
    #timer = bpy.props.BoolProperty(
    #        description = 'enable timer event'
    #        )
    #
    #timer_refresh   = bpy.props.FloatProperty(
    #        min = 0.01,
    #        max = 60.0,
    #        description = 'event timer latency'
    #        )

    def draw(self, context) :
        scene = bpy.context.scene
        mdl = bpy.context.window_manager.modal
        inst_status = [ 'LAYER_USED', 'LAYER_ACTIVE' ]
        ops = bpy.ops.wm

        layout = self.layout

        # 1st line
        row = layout.row()
        row.prop(mdl,'status',toggle = False) #,text='enabled' if mdl.status else 'disabled')
        row.prop(mdl,'func')                  # dialog/popup are not redraw so the kind of
                                              # code above commented above don't work (?)
        # instance status useless, it does not refresh in popup
        #row = layout.row()
        #row.label( icon = inst_status[ mdl._inst[0] ] )
        #row.label( icon = inst_status[ mdl._inst[1] ] )

        # 1st checkboxes column
        row = layout.split(0.05)
        col = row.column()
        col.prop(mdl,'timer')
        col.prop(mdl,'hud')
        col.label('')
        col.prop(self,'debugcsl')
        col.prop(self,'restore',toggle = True)

        # 2nd option names column
        col = row.column()
        col.label('timer event interval')
        col.label('hud function')
        col.label('hud area')
        col.label('debug')
        col.label('restore default value')

        # 3rd column
        col = row.column()
        col.prop(mdl,'timer_refresh')
        col.prop(mdl,'hudfunc')
        col.prop(mdl,'area',text='')
        col.label('')

        # goodies bottom-right
        split = col.split(0.85)
        col0 = split.row(align=True)
        col0.label('')
        subrow = split.column()
        subrow.prop(self,'csl',toggle = True, icon='CONSOLE')

        # (?) calls to operators (modal_start for example) will work only one time
        # in a popup or dialog op ?
        #row = layout.row()
        #row.operator('wm.modal_start',text = 'Start')
        #row.operator('wm.modal_stop',text = 'Stop')

    def execute(self, context):
        mdl = bpy.context.window_manager.modal
        #self.func = mdl.func
        #self.hudfunc = mdl.hudfunc
        return {'FINISHED'}

    def invoke(self, context, event):
        mdl = bpy.context.window_manager.modal
        #copy_props_values(mdl,self)
        if mdl.loglevel != -1 : self.debugcsl = True
        #self.func = mdl.func
        #self.hudfunc = mdl.hudfunc
        wm = context.window_manager
        #return wm.invoke_props_dialog(self)
        return wm.invoke_props_popup(self,event)

def register_ui() :
    bpy.utils.register_class(ModalConfig)

def unregister_ui() :
    bpy.utils.unregister_class(ModalConfig)

if __name__ == "__main__" :
    register()