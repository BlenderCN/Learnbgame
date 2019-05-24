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

# <pep8 compliant>


bl_info = {
    "name": "BreakPoint",
    "description": "Breakpoint allows you to pause script execution and display variables values.",
    "author": "Christopher Barrett  (www.goodspiritgraphics.com)",
    "version": (1,0),
    "blender": (2, 5, 9),
    "api": 39307,
    "location": "Text Editor > Properties",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"
                "Scripts/Development/BreakPoint",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"
                   "func=detail&aid=28802",
    "category": "Learnbgame",
}


import bpy
import code
import traceback
from collections import OrderedDict
from bpy.props import BoolProperty
from bpy.props import EnumProperty


class BreakPoint_Class:
    """ this class contains all variables concerning BreakPoint """

    def __init__(self):

        # gui modes (Run, Stop)
        bpy.types.Scene.gsg1_mode = EnumProperty(attr='mode', name='bp_mode', items=(\
        ('enable', 'Enable', 'Enable all BreakPoint statements.'),\
        ('disable', 'Disable', 'Disable all BreakPoint statements.'),\
        ('help', 'Help' , 'Display BreakPoint instructions.')), default='enable')

        bpy.types.Scene.gsg1_console_print = BoolProperty(name= "Print to Console" ,description = "Select to allow printing 'BreakPoint' commands to the 'Console' window." , default = True)
        bpy.types.Scene.gsg1_panel_print = BoolProperty(name= "Print to Panel" ,description = "Select to allow printing 'BreakPoint' commands to the 'BreakPoint' panel." , default = True)
        bpy.types.Scene.gsg1_ignore_pause = BoolProperty(name= "Ignore Pause" ,description = "Select to ignore all 'Pause' args in the 'BreakPoint' commands." , default = False)
        bpy.types.Scene.gsg1_update_panel = BoolProperty(name= "Update Panel" ,description = "Select to force Blender to update the 'BreakPoint' panel.  Slow, but it guarantees valid display of variable values." , default = True)

        #Create list type for variables.
        bpy.types.Scene.gsg1_variables = []


# Create the instance class for global variables.
gsg1bp = BreakPoint_Class()



class bp(bpy.types.Panel):
    bl_label = "BreakPoint"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_context = "WINDOW"


    def draw(self, context):
        scn = bpy.context.scene
        
        layout = self.layout; 
        row = layout.row(align = True)
        row.prop(context.scene , "gsg1_mode", expand = True)
        row = layout.row()
        row = layout.row()
        row.prop(context.scene , "gsg1_console_print")
        row.prop(context.scene , "gsg1_panel_print")
        row = layout.row()
        row.prop(context.scene , "gsg1_ignore_pause")
        row.prop(context.scene , "gsg1_update_panel")
        row = layout.row()

        if scn.gsg1_mode == 'help':
            pic = 'QUESTION'
            box = layout.box()
            box.label(" 'BreakPoint' Instructions:", icon=pic)

            box.label("To use 'BreakPoint', put the following line,")
            box.label("without the quotes, at the top of your script:")
            box.label("'breakpoint = bpy.types.bp.bp'")
            box.label("To set a breakpoint, insert the line:")
            box.label("'breakpoint(DICTIONARY)'")
            box.label("where you want to stop script execution,")
            box.label("and display variable values.")
            box.label("Replace the word 'DICTIONARY' above with: ")
            box.label("'locals()' to display the local variables;")
            box.label("'globals()' to display the global variables;")
            box.label("or with any other dictionary object.")
            box.label("BreakPoint can take two additional boolean")
            box.label("args after the dictionary object.")
            box.label("The first arg, 'pause' is used to stop script")
            box.label("execution.  Default = 'True'")
            box.label("The second arg, 'prnt' is used to print the")
            box.label("dictionary object.  Default = 'True'")
            box.label("Example: 'breakpoint(locals(), False)")
            box.label("This will print all the local variables within")
            box.label("the function without pausing.")
            box.label("")

        elif scn.gsg1_mode == 'enable':
            pic = 'CONSOLE'

            box = layout.box()

            if bpy.types.Scene.gsg1_variables == []:
                box.label(text=" Output:", icon=pic)
                for i in range(1, 3):
                    box.label("")
            else:
                done_once = False
                for i in bpy.types.Scene.gsg1_variables:
                    if not done_once:
                        box.label(text=" " + str(i), icon=pic)
                        done_once = True
                    else:
                        box.label(str(i))

                box.label("")

        else:
            # 'Stop'
            pic = 'CANCEL'

            box = layout.box()
            box.label(text=" BreakPoint Disabled.", icon=pic)
            
            for i in range(1, 3):
                box.label("")



    def bp(dictionary={}, pause = True, prnt = True):
        scn = bpy.context.scene
        if scn.gsg1_mode == 'disable':
            #User has disabled BreakPoint.
            #print("Stopped")
            return

        s = traceback.extract_stack()
        s = s[len(s)-2]
        strng = str(s)
        scrptPos = strng.rfind("\\")
        scrpt = strng[scrptPos + 1 : len(strng) - 1]
        lst = scrpt.split(",")
        scrpt = str(lst[0])
        scrpt = scrpt[0 : len(scrpt) - 1]


        #Clear the list.
        bpy.types.Scene.gsg1_variables = []

        #Print the line, object, and file from which 'Breakpoint' was called.
        if prnt and scn.gsg1_panel_print:
            text = "Breakpoint>>  Line: " + str(s[1]) + "  In: '" + str(s[2]) + "'  File: '" + scrpt + "'"
            bpy.types.Scene.gsg1_variables.append(text)

        if prnt and scn.gsg1_console_print:
            text = "\n\n\nBreakpoint>>  Line: " + str(s[1]) + "  In: '" + str(s[2]) + "'  File: '" + scrpt + "'\n"
            print_to_console(text)



        if dictionary == {}:
            #Empty dictionary passed, so return globals as default, and pause.
            text = "\nEnter 'CTRL-Z' to exit the console.  With Unix, use 'CTRL-D'\n\n"
            print_to_console(text)

            d = globals().copy()
            code.interact(local=d)
            return
        else:
            d = dictionary


        if prnt:
            #Alphabetize by key.
            d_sorted_by_value = OrderedDict(sorted(d.items(), key=lambda x: x[0]))

            text = "Variables:\n"
            print_to_console(text)

            for items in d_sorted_by_value.keys():
                text = str(items) + " = " + str(d_sorted_by_value[items])
                print_to_console(text)

                if scn.gsg1_panel_print:
                    bpy.types.Scene.gsg1_variables.append(text)

            #Necessary here to guarantee that the panel is updated after last variable.
            if scn.gsg1_panel_print:
                force_redraw()

        if pause and not(scn.gsg1_ignore_pause):
            text = "\n\nEnter 'CTRL-Z' to exit the console.  With Unix, use 'CTRL-D'\n"
            print_to_console(text)

#            if scn.gsg1_panel_print:
#                #This updates the panel even if a script still has control of Blender.
#                force_redraw()

            code.interact(local=d)

        return



def print_to_console(text):
    if bpy.context.scene.gsg1_console_print:
        print(text)


def force_redraw():
    if bpy.context.scene.gsg1_update_panel:
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)


#registration is necessary for the script to appear in the GUI
def register():
    bpy.utils.register_class(bp)


def unregister():
    bpy.utils.unregister_class(bp)


if __name__ == '__main__':
    register()
