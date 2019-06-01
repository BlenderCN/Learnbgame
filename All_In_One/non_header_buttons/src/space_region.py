#----------------------------------------------------------------------
# space_region.py
#----------------------------------------------------------------------
# This file contains the generated register methods
# for the header buttons.
# Each button is handled with by it's own add_to_header_space_id method
# as there is already a different button for every space  
#----------------------------------------------------------------------
# File generated on 2017-12-26 00:29:18
#----------------------------------------------------------------------

import bpy
import os
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                        )

#----------------------------------------------------
# Use console_writing in case its addon is installed
#          Otherwise print to the terminal
#----------------------------------------------------
try:
    from console_scripts.utils import console_writer
    console_script_is_installed=True
except ImportError:
    print("console_scripts addon wasn't found, ensure correct name of the addon if it's registered!")
    console_script_is_installed=False

def custom_print(str):
    if "console_write_operator" in dir(bpy.ops.console)
        # the exposed Blender operator
        # case of console_scripts registered
        bpy.ops.console.console_write_operator(myString=str)
    elif console_script_is_installed==True:
        # the python method
        # case of console_scripts existent but not registered
        # or console_scripts has just been removed
        console_writer.console_write(str)
    else:
        print(str)



class PrintHello_EMPTY_WINDOW(Operator):
    bl_idname = "wm.printhello0_0"
    bl_label = "Print Hello EMPTY_WINDOW"

    def execute(self, context):
        custom_print("{space: EMPTY, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_EMPTY_WINDOW(Panel):
    bl_idname = "HelloPanel_EMPTY_WINDOW"
    bl_label = "My Panel EMPTY_WINDOW"
    bl_space_type = "EMPTY"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello0_0")

        
class PrintHello_EMPTY_HEADER(Operator):
    bl_idname = "wm.printhello0_1"
    bl_label = "Print Hello EMPTY_HEADER"

    def execute(self, context):
        custom_print("{space: EMPTY, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_EMPTY_HEADER(Panel):
    bl_idname = "HelloPanel_EMPTY_HEADER"
    bl_label = "My Panel EMPTY_HEADER"
    bl_space_type = "EMPTY"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello0_1")

        
class PrintHello_EMPTY_CHANNELS(Operator):
    bl_idname = "wm.printhello0_2"
    bl_label = "Print Hello EMPTY_CHANNELS"

    def execute(self, context):
        custom_print("{space: EMPTY, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_EMPTY_CHANNELS(Panel):
    bl_idname = "HelloPanel_EMPTY_CHANNELS"
    bl_label = "My Panel EMPTY_CHANNELS"
    bl_space_type = "EMPTY"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello0_2")

        
class PrintHello_EMPTY_TEMPORARY(Operator):
    bl_idname = "wm.printhello0_3"
    bl_label = "Print Hello EMPTY_TEMPORARY"

    def execute(self, context):
        custom_print("{space: EMPTY, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_EMPTY_TEMPORARY(Panel):
    bl_idname = "HelloPanel_EMPTY_TEMPORARY"
    bl_label = "My Panel EMPTY_TEMPORARY"
    bl_space_type = "EMPTY"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello0_3")

        
class PrintHello_EMPTY_UI(Operator):
    bl_idname = "wm.printhello0_4"
    bl_label = "Print Hello EMPTY_UI"

    def execute(self, context):
        custom_print("{space: EMPTY, region: UI}")
        return {'FINISHED'}

class HelloPanel_EMPTY_UI(Panel):
    bl_idname = "HelloPanel_EMPTY_UI"
    bl_label = "My Panel EMPTY_UI"
    bl_space_type = "EMPTY"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello0_4")

        
class PrintHello_EMPTY_TOOLS(Operator):
    bl_idname = "wm.printhello0_5"
    bl_label = "Print Hello EMPTY_TOOLS"

    def execute(self, context):
        custom_print("{space: EMPTY, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_EMPTY_TOOLS(Panel):
    bl_idname = "HelloPanel_EMPTY_TOOLS"
    bl_label = "My Panel EMPTY_TOOLS"
    bl_space_type = "EMPTY"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello0_5")

        
class PrintHello_EMPTY_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello0_6"
    bl_label = "Print Hello EMPTY_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: EMPTY, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_EMPTY_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_EMPTY_TOOL_PROPS"
    bl_label = "My Panel EMPTY_TOOL_PROPS"
    bl_space_type = "EMPTY"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello0_6")

        
class PrintHello_EMPTY_PREVIEW(Operator):
    bl_idname = "wm.printhello0_7"
    bl_label = "Print Hello EMPTY_PREVIEW"

    def execute(self, context):
        custom_print("{space: EMPTY, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_EMPTY_PREVIEW(Panel):
    bl_idname = "HelloPanel_EMPTY_PREVIEW"
    bl_label = "My Panel EMPTY_PREVIEW"
    bl_space_type = "EMPTY"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello0_7")

        
class PrintHello_VIEW_3D_WINDOW(Operator):
    bl_idname = "wm.printhello1_0"
    bl_label = "Print Hello VIEW_3D_WINDOW"

    def execute(self, context):
        custom_print("{space: VIEW_3D, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_VIEW_3D_WINDOW(Panel):
    bl_idname = "HelloPanel_VIEW_3D_WINDOW"
    bl_label = "My Panel VIEW_3D_WINDOW"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello1_0")

        
class PrintHello_VIEW_3D_HEADER(Operator):
    bl_idname = "wm.printhello1_1"
    bl_label = "Print Hello VIEW_3D_HEADER"

    def execute(self, context):
        custom_print("{space: VIEW_3D, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_VIEW_3D_HEADER(Panel):
    bl_idname = "HelloPanel_VIEW_3D_HEADER"
    bl_label = "My Panel VIEW_3D_HEADER"
    bl_space_type = "VIEW_3D"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello1_1")

        
class PrintHello_VIEW_3D_CHANNELS(Operator):
    bl_idname = "wm.printhello1_2"
    bl_label = "Print Hello VIEW_3D_CHANNELS"

    def execute(self, context):
        custom_print("{space: VIEW_3D, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_VIEW_3D_CHANNELS(Panel):
    bl_idname = "HelloPanel_VIEW_3D_CHANNELS"
    bl_label = "My Panel VIEW_3D_CHANNELS"
    bl_space_type = "VIEW_3D"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello1_2")

        
class PrintHello_VIEW_3D_TEMPORARY(Operator):
    bl_idname = "wm.printhello1_3"
    bl_label = "Print Hello VIEW_3D_TEMPORARY"

    def execute(self, context):
        custom_print("{space: VIEW_3D, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_VIEW_3D_TEMPORARY(Panel):
    bl_idname = "HelloPanel_VIEW_3D_TEMPORARY"
    bl_label = "My Panel VIEW_3D_TEMPORARY"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello1_3")

        
class PrintHello_VIEW_3D_UI(Operator):
    bl_idname = "wm.printhello1_4"
    bl_label = "Print Hello VIEW_3D_UI"

    def execute(self, context):
        custom_print("{space: VIEW_3D, region: UI}")
        return {'FINISHED'}

class HelloPanel_VIEW_3D_UI(Panel):
    bl_idname = "HelloPanel_VIEW_3D_UI"
    bl_label = "My Panel VIEW_3D_UI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello1_4")

        
class PrintHello_VIEW_3D_TOOLS(Operator):
    bl_idname = "wm.printhello1_5"
    bl_label = "Print Hello VIEW_3D_TOOLS"

    def execute(self, context):
        custom_print("{space: VIEW_3D, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_VIEW_3D_TOOLS(Panel):
    bl_idname = "HelloPanel_VIEW_3D_TOOLS"
    bl_label = "My Panel VIEW_3D_TOOLS"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello1_5")

        
class PrintHello_VIEW_3D_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello1_6"
    bl_label = "Print Hello VIEW_3D_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: VIEW_3D, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_VIEW_3D_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_VIEW_3D_TOOL_PROPS"
    bl_label = "My Panel VIEW_3D_TOOL_PROPS"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello1_6")

        
class PrintHello_VIEW_3D_PREVIEW(Operator):
    bl_idname = "wm.printhello1_7"
    bl_label = "Print Hello VIEW_3D_PREVIEW"

    def execute(self, context):
        custom_print("{space: VIEW_3D, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_VIEW_3D_PREVIEW(Panel):
    bl_idname = "HelloPanel_VIEW_3D_PREVIEW"
    bl_label = "My Panel VIEW_3D_PREVIEW"
    bl_space_type = "VIEW_3D"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello1_7")

        
class PrintHello_TIMELINE_WINDOW(Operator):
    bl_idname = "wm.printhello2_0"
    bl_label = "Print Hello TIMELINE_WINDOW"

    def execute(self, context):
        custom_print("{space: TIMELINE, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_TIMELINE_WINDOW(Panel):
    bl_idname = "HelloPanel_TIMELINE_WINDOW"
    bl_label = "My Panel TIMELINE_WINDOW"
    bl_space_type = "TIMELINE"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello2_0")

        
class PrintHello_TIMELINE_HEADER(Operator):
    bl_idname = "wm.printhello2_1"
    bl_label = "Print Hello TIMELINE_HEADER"

    def execute(self, context):
        custom_print("{space: TIMELINE, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_TIMELINE_HEADER(Panel):
    bl_idname = "HelloPanel_TIMELINE_HEADER"
    bl_label = "My Panel TIMELINE_HEADER"
    bl_space_type = "TIMELINE"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello2_1")

        
class PrintHello_TIMELINE_CHANNELS(Operator):
    bl_idname = "wm.printhello2_2"
    bl_label = "Print Hello TIMELINE_CHANNELS"

    def execute(self, context):
        custom_print("{space: TIMELINE, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_TIMELINE_CHANNELS(Panel):
    bl_idname = "HelloPanel_TIMELINE_CHANNELS"
    bl_label = "My Panel TIMELINE_CHANNELS"
    bl_space_type = "TIMELINE"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello2_2")

        
class PrintHello_TIMELINE_TEMPORARY(Operator):
    bl_idname = "wm.printhello2_3"
    bl_label = "Print Hello TIMELINE_TEMPORARY"

    def execute(self, context):
        custom_print("{space: TIMELINE, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_TIMELINE_TEMPORARY(Panel):
    bl_idname = "HelloPanel_TIMELINE_TEMPORARY"
    bl_label = "My Panel TIMELINE_TEMPORARY"
    bl_space_type = "TIMELINE"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello2_3")

        
class PrintHello_TIMELINE_UI(Operator):
    bl_idname = "wm.printhello2_4"
    bl_label = "Print Hello TIMELINE_UI"

    def execute(self, context):
        custom_print("{space: TIMELINE, region: UI}")
        return {'FINISHED'}

class HelloPanel_TIMELINE_UI(Panel):
    bl_idname = "HelloPanel_TIMELINE_UI"
    bl_label = "My Panel TIMELINE_UI"
    bl_space_type = "TIMELINE"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello2_4")

        
class PrintHello_TIMELINE_TOOLS(Operator):
    bl_idname = "wm.printhello2_5"
    bl_label = "Print Hello TIMELINE_TOOLS"

    def execute(self, context):
        custom_print("{space: TIMELINE, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_TIMELINE_TOOLS(Panel):
    bl_idname = "HelloPanel_TIMELINE_TOOLS"
    bl_label = "My Panel TIMELINE_TOOLS"
    bl_space_type = "TIMELINE"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello2_5")

        
class PrintHello_TIMELINE_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello2_6"
    bl_label = "Print Hello TIMELINE_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: TIMELINE, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_TIMELINE_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_TIMELINE_TOOL_PROPS"
    bl_label = "My Panel TIMELINE_TOOL_PROPS"
    bl_space_type = "TIMELINE"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello2_6")

        
class PrintHello_TIMELINE_PREVIEW(Operator):
    bl_idname = "wm.printhello2_7"
    bl_label = "Print Hello TIMELINE_PREVIEW"

    def execute(self, context):
        custom_print("{space: TIMELINE, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_TIMELINE_PREVIEW(Panel):
    bl_idname = "HelloPanel_TIMELINE_PREVIEW"
    bl_label = "My Panel TIMELINE_PREVIEW"
    bl_space_type = "TIMELINE"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello2_7")

        
class PrintHello_GRAPH_EDITOR_WINDOW(Operator):
    bl_idname = "wm.printhello3_0"
    bl_label = "Print Hello GRAPH_EDITOR_WINDOW"

    def execute(self, context):
        custom_print("{space: GRAPH_EDITOR, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_GRAPH_EDITOR_WINDOW(Panel):
    bl_idname = "HelloPanel_GRAPH_EDITOR_WINDOW"
    bl_label = "My Panel GRAPH_EDITOR_WINDOW"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello3_0")

        
class PrintHello_GRAPH_EDITOR_HEADER(Operator):
    bl_idname = "wm.printhello3_1"
    bl_label = "Print Hello GRAPH_EDITOR_HEADER"

    def execute(self, context):
        custom_print("{space: GRAPH_EDITOR, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_GRAPH_EDITOR_HEADER(Panel):
    bl_idname = "HelloPanel_GRAPH_EDITOR_HEADER"
    bl_label = "My Panel GRAPH_EDITOR_HEADER"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello3_1")

        
class PrintHello_GRAPH_EDITOR_CHANNELS(Operator):
    bl_idname = "wm.printhello3_2"
    bl_label = "Print Hello GRAPH_EDITOR_CHANNELS"

    def execute(self, context):
        custom_print("{space: GRAPH_EDITOR, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_GRAPH_EDITOR_CHANNELS(Panel):
    bl_idname = "HelloPanel_GRAPH_EDITOR_CHANNELS"
    bl_label = "My Panel GRAPH_EDITOR_CHANNELS"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello3_2")

        
class PrintHello_GRAPH_EDITOR_TEMPORARY(Operator):
    bl_idname = "wm.printhello3_3"
    bl_label = "Print Hello GRAPH_EDITOR_TEMPORARY"

    def execute(self, context):
        custom_print("{space: GRAPH_EDITOR, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_GRAPH_EDITOR_TEMPORARY(Panel):
    bl_idname = "HelloPanel_GRAPH_EDITOR_TEMPORARY"
    bl_label = "My Panel GRAPH_EDITOR_TEMPORARY"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello3_3")

        
class PrintHello_GRAPH_EDITOR_UI(Operator):
    bl_idname = "wm.printhello3_4"
    bl_label = "Print Hello GRAPH_EDITOR_UI"

    def execute(self, context):
        custom_print("{space: GRAPH_EDITOR, region: UI}")
        return {'FINISHED'}

class HelloPanel_GRAPH_EDITOR_UI(Panel):
    bl_idname = "HelloPanel_GRAPH_EDITOR_UI"
    bl_label = "My Panel GRAPH_EDITOR_UI"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello3_4")

        
class PrintHello_GRAPH_EDITOR_TOOLS(Operator):
    bl_idname = "wm.printhello3_5"
    bl_label = "Print Hello GRAPH_EDITOR_TOOLS"

    def execute(self, context):
        custom_print("{space: GRAPH_EDITOR, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_GRAPH_EDITOR_TOOLS(Panel):
    bl_idname = "HelloPanel_GRAPH_EDITOR_TOOLS"
    bl_label = "My Panel GRAPH_EDITOR_TOOLS"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello3_5")

        
class PrintHello_GRAPH_EDITOR_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello3_6"
    bl_label = "Print Hello GRAPH_EDITOR_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: GRAPH_EDITOR, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_GRAPH_EDITOR_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_GRAPH_EDITOR_TOOL_PROPS"
    bl_label = "My Panel GRAPH_EDITOR_TOOL_PROPS"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello3_6")

        
class PrintHello_GRAPH_EDITOR_PREVIEW(Operator):
    bl_idname = "wm.printhello3_7"
    bl_label = "Print Hello GRAPH_EDITOR_PREVIEW"

    def execute(self, context):
        custom_print("{space: GRAPH_EDITOR, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_GRAPH_EDITOR_PREVIEW(Panel):
    bl_idname = "HelloPanel_GRAPH_EDITOR_PREVIEW"
    bl_label = "My Panel GRAPH_EDITOR_PREVIEW"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello3_7")

        
class PrintHello_DOPESHEET_EDITOR_WINDOW(Operator):
    bl_idname = "wm.printhello4_0"
    bl_label = "Print Hello DOPESHEET_EDITOR_WINDOW"

    def execute(self, context):
        custom_print("{space: DOPESHEET_EDITOR, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_DOPESHEET_EDITOR_WINDOW(Panel):
    bl_idname = "HelloPanel_DOPESHEET_EDITOR_WINDOW"
    bl_label = "My Panel DOPESHEET_EDITOR_WINDOW"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello4_0")

        
class PrintHello_DOPESHEET_EDITOR_HEADER(Operator):
    bl_idname = "wm.printhello4_1"
    bl_label = "Print Hello DOPESHEET_EDITOR_HEADER"

    def execute(self, context):
        custom_print("{space: DOPESHEET_EDITOR, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_DOPESHEET_EDITOR_HEADER(Panel):
    bl_idname = "HelloPanel_DOPESHEET_EDITOR_HEADER"
    bl_label = "My Panel DOPESHEET_EDITOR_HEADER"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello4_1")

        
class PrintHello_DOPESHEET_EDITOR_CHANNELS(Operator):
    bl_idname = "wm.printhello4_2"
    bl_label = "Print Hello DOPESHEET_EDITOR_CHANNELS"

    def execute(self, context):
        custom_print("{space: DOPESHEET_EDITOR, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_DOPESHEET_EDITOR_CHANNELS(Panel):
    bl_idname = "HelloPanel_DOPESHEET_EDITOR_CHANNELS"
    bl_label = "My Panel DOPESHEET_EDITOR_CHANNELS"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello4_2")

        
class PrintHello_DOPESHEET_EDITOR_TEMPORARY(Operator):
    bl_idname = "wm.printhello4_3"
    bl_label = "Print Hello DOPESHEET_EDITOR_TEMPORARY"

    def execute(self, context):
        custom_print("{space: DOPESHEET_EDITOR, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_DOPESHEET_EDITOR_TEMPORARY(Panel):
    bl_idname = "HelloPanel_DOPESHEET_EDITOR_TEMPORARY"
    bl_label = "My Panel DOPESHEET_EDITOR_TEMPORARY"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello4_3")

        
class PrintHello_DOPESHEET_EDITOR_UI(Operator):
    bl_idname = "wm.printhello4_4"
    bl_label = "Print Hello DOPESHEET_EDITOR_UI"

    def execute(self, context):
        custom_print("{space: DOPESHEET_EDITOR, region: UI}")
        return {'FINISHED'}

class HelloPanel_DOPESHEET_EDITOR_UI(Panel):
    bl_idname = "HelloPanel_DOPESHEET_EDITOR_UI"
    bl_label = "My Panel DOPESHEET_EDITOR_UI"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello4_4")

        
class PrintHello_DOPESHEET_EDITOR_TOOLS(Operator):
    bl_idname = "wm.printhello4_5"
    bl_label = "Print Hello DOPESHEET_EDITOR_TOOLS"

    def execute(self, context):
        custom_print("{space: DOPESHEET_EDITOR, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_DOPESHEET_EDITOR_TOOLS(Panel):
    bl_idname = "HelloPanel_DOPESHEET_EDITOR_TOOLS"
    bl_label = "My Panel DOPESHEET_EDITOR_TOOLS"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello4_5")

        
class PrintHello_DOPESHEET_EDITOR_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello4_6"
    bl_label = "Print Hello DOPESHEET_EDITOR_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: DOPESHEET_EDITOR, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_DOPESHEET_EDITOR_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_DOPESHEET_EDITOR_TOOL_PROPS"
    bl_label = "My Panel DOPESHEET_EDITOR_TOOL_PROPS"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello4_6")

        
class PrintHello_DOPESHEET_EDITOR_PREVIEW(Operator):
    bl_idname = "wm.printhello4_7"
    bl_label = "Print Hello DOPESHEET_EDITOR_PREVIEW"

    def execute(self, context):
        custom_print("{space: DOPESHEET_EDITOR, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_DOPESHEET_EDITOR_PREVIEW(Panel):
    bl_idname = "HelloPanel_DOPESHEET_EDITOR_PREVIEW"
    bl_label = "My Panel DOPESHEET_EDITOR_PREVIEW"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello4_7")

        
class PrintHello_NLA_EDITOR_WINDOW(Operator):
    bl_idname = "wm.printhello5_0"
    bl_label = "Print Hello NLA_EDITOR_WINDOW"

    def execute(self, context):
        custom_print("{space: NLA_EDITOR, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_NLA_EDITOR_WINDOW(Panel):
    bl_idname = "HelloPanel_NLA_EDITOR_WINDOW"
    bl_label = "My Panel NLA_EDITOR_WINDOW"
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello5_0")

        
class PrintHello_NLA_EDITOR_HEADER(Operator):
    bl_idname = "wm.printhello5_1"
    bl_label = "Print Hello NLA_EDITOR_HEADER"

    def execute(self, context):
        custom_print("{space: NLA_EDITOR, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_NLA_EDITOR_HEADER(Panel):
    bl_idname = "HelloPanel_NLA_EDITOR_HEADER"
    bl_label = "My Panel NLA_EDITOR_HEADER"
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello5_1")

        
class PrintHello_NLA_EDITOR_CHANNELS(Operator):
    bl_idname = "wm.printhello5_2"
    bl_label = "Print Hello NLA_EDITOR_CHANNELS"

    def execute(self, context):
        custom_print("{space: NLA_EDITOR, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_NLA_EDITOR_CHANNELS(Panel):
    bl_idname = "HelloPanel_NLA_EDITOR_CHANNELS"
    bl_label = "My Panel NLA_EDITOR_CHANNELS"
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello5_2")

        
class PrintHello_NLA_EDITOR_TEMPORARY(Operator):
    bl_idname = "wm.printhello5_3"
    bl_label = "Print Hello NLA_EDITOR_TEMPORARY"

    def execute(self, context):
        custom_print("{space: NLA_EDITOR, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_NLA_EDITOR_TEMPORARY(Panel):
    bl_idname = "HelloPanel_NLA_EDITOR_TEMPORARY"
    bl_label = "My Panel NLA_EDITOR_TEMPORARY"
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello5_3")

        
class PrintHello_NLA_EDITOR_UI(Operator):
    bl_idname = "wm.printhello5_4"
    bl_label = "Print Hello NLA_EDITOR_UI"

    def execute(self, context):
        custom_print("{space: NLA_EDITOR, region: UI}")
        return {'FINISHED'}

class HelloPanel_NLA_EDITOR_UI(Panel):
    bl_idname = "HelloPanel_NLA_EDITOR_UI"
    bl_label = "My Panel NLA_EDITOR_UI"
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello5_4")

        
class PrintHello_NLA_EDITOR_TOOLS(Operator):
    bl_idname = "wm.printhello5_5"
    bl_label = "Print Hello NLA_EDITOR_TOOLS"

    def execute(self, context):
        custom_print("{space: NLA_EDITOR, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_NLA_EDITOR_TOOLS(Panel):
    bl_idname = "HelloPanel_NLA_EDITOR_TOOLS"
    bl_label = "My Panel NLA_EDITOR_TOOLS"
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello5_5")

        
class PrintHello_NLA_EDITOR_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello5_6"
    bl_label = "Print Hello NLA_EDITOR_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: NLA_EDITOR, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_NLA_EDITOR_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_NLA_EDITOR_TOOL_PROPS"
    bl_label = "My Panel NLA_EDITOR_TOOL_PROPS"
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello5_6")

        
class PrintHello_NLA_EDITOR_PREVIEW(Operator):
    bl_idname = "wm.printhello5_7"
    bl_label = "Print Hello NLA_EDITOR_PREVIEW"

    def execute(self, context):
        custom_print("{space: NLA_EDITOR, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_NLA_EDITOR_PREVIEW(Panel):
    bl_idname = "HelloPanel_NLA_EDITOR_PREVIEW"
    bl_label = "My Panel NLA_EDITOR_PREVIEW"
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello5_7")

        
class PrintHello_IMAGE_EDITOR_WINDOW(Operator):
    bl_idname = "wm.printhello6_0"
    bl_label = "Print Hello IMAGE_EDITOR_WINDOW"

    def execute(self, context):
        custom_print("{space: IMAGE_EDITOR, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_IMAGE_EDITOR_WINDOW(Panel):
    bl_idname = "HelloPanel_IMAGE_EDITOR_WINDOW"
    bl_label = "My Panel IMAGE_EDITOR_WINDOW"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello6_0")

        
class PrintHello_IMAGE_EDITOR_HEADER(Operator):
    bl_idname = "wm.printhello6_1"
    bl_label = "Print Hello IMAGE_EDITOR_HEADER"

    def execute(self, context):
        custom_print("{space: IMAGE_EDITOR, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_IMAGE_EDITOR_HEADER(Panel):
    bl_idname = "HelloPanel_IMAGE_EDITOR_HEADER"
    bl_label = "My Panel IMAGE_EDITOR_HEADER"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello6_1")

        
class PrintHello_IMAGE_EDITOR_CHANNELS(Operator):
    bl_idname = "wm.printhello6_2"
    bl_label = "Print Hello IMAGE_EDITOR_CHANNELS"

    def execute(self, context):
        custom_print("{space: IMAGE_EDITOR, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_IMAGE_EDITOR_CHANNELS(Panel):
    bl_idname = "HelloPanel_IMAGE_EDITOR_CHANNELS"
    bl_label = "My Panel IMAGE_EDITOR_CHANNELS"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello6_2")

        
class PrintHello_IMAGE_EDITOR_TEMPORARY(Operator):
    bl_idname = "wm.printhello6_3"
    bl_label = "Print Hello IMAGE_EDITOR_TEMPORARY"

    def execute(self, context):
        custom_print("{space: IMAGE_EDITOR, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_IMAGE_EDITOR_TEMPORARY(Panel):
    bl_idname = "HelloPanel_IMAGE_EDITOR_TEMPORARY"
    bl_label = "My Panel IMAGE_EDITOR_TEMPORARY"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello6_3")

        
class PrintHello_IMAGE_EDITOR_UI(Operator):
    bl_idname = "wm.printhello6_4"
    bl_label = "Print Hello IMAGE_EDITOR_UI"

    def execute(self, context):
        custom_print("{space: IMAGE_EDITOR, region: UI}")
        return {'FINISHED'}

class HelloPanel_IMAGE_EDITOR_UI(Panel):
    bl_idname = "HelloPanel_IMAGE_EDITOR_UI"
    bl_label = "My Panel IMAGE_EDITOR_UI"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello6_4")

        
class PrintHello_IMAGE_EDITOR_TOOLS(Operator):
    bl_idname = "wm.printhello6_5"
    bl_label = "Print Hello IMAGE_EDITOR_TOOLS"

    def execute(self, context):
        custom_print("{space: IMAGE_EDITOR, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_IMAGE_EDITOR_TOOLS(Panel):
    bl_idname = "HelloPanel_IMAGE_EDITOR_TOOLS"
    bl_label = "My Panel IMAGE_EDITOR_TOOLS"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello6_5")

        
class PrintHello_IMAGE_EDITOR_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello6_6"
    bl_label = "Print Hello IMAGE_EDITOR_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: IMAGE_EDITOR, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_IMAGE_EDITOR_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_IMAGE_EDITOR_TOOL_PROPS"
    bl_label = "My Panel IMAGE_EDITOR_TOOL_PROPS"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello6_6")

        
class PrintHello_IMAGE_EDITOR_PREVIEW(Operator):
    bl_idname = "wm.printhello6_7"
    bl_label = "Print Hello IMAGE_EDITOR_PREVIEW"

    def execute(self, context):
        custom_print("{space: IMAGE_EDITOR, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_IMAGE_EDITOR_PREVIEW(Panel):
    bl_idname = "HelloPanel_IMAGE_EDITOR_PREVIEW"
    bl_label = "My Panel IMAGE_EDITOR_PREVIEW"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello6_7")

        
class PrintHello_SEQUENCE_EDITOR_WINDOW(Operator):
    bl_idname = "wm.printhello7_0"
    bl_label = "Print Hello SEQUENCE_EDITOR_WINDOW"

    def execute(self, context):
        custom_print("{space: SEQUENCE_EDITOR, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_SEQUENCE_EDITOR_WINDOW(Panel):
    bl_idname = "HelloPanel_SEQUENCE_EDITOR_WINDOW"
    bl_label = "My Panel SEQUENCE_EDITOR_WINDOW"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello7_0")

        
class PrintHello_SEQUENCE_EDITOR_HEADER(Operator):
    bl_idname = "wm.printhello7_1"
    bl_label = "Print Hello SEQUENCE_EDITOR_HEADER"

    def execute(self, context):
        custom_print("{space: SEQUENCE_EDITOR, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_SEQUENCE_EDITOR_HEADER(Panel):
    bl_idname = "HelloPanel_SEQUENCE_EDITOR_HEADER"
    bl_label = "My Panel SEQUENCE_EDITOR_HEADER"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello7_1")

        
class PrintHello_SEQUENCE_EDITOR_CHANNELS(Operator):
    bl_idname = "wm.printhello7_2"
    bl_label = "Print Hello SEQUENCE_EDITOR_CHANNELS"

    def execute(self, context):
        custom_print("{space: SEQUENCE_EDITOR, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_SEQUENCE_EDITOR_CHANNELS(Panel):
    bl_idname = "HelloPanel_SEQUENCE_EDITOR_CHANNELS"
    bl_label = "My Panel SEQUENCE_EDITOR_CHANNELS"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello7_2")

        
class PrintHello_SEQUENCE_EDITOR_TEMPORARY(Operator):
    bl_idname = "wm.printhello7_3"
    bl_label = "Print Hello SEQUENCE_EDITOR_TEMPORARY"

    def execute(self, context):
        custom_print("{space: SEQUENCE_EDITOR, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_SEQUENCE_EDITOR_TEMPORARY(Panel):
    bl_idname = "HelloPanel_SEQUENCE_EDITOR_TEMPORARY"
    bl_label = "My Panel SEQUENCE_EDITOR_TEMPORARY"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello7_3")

        
class PrintHello_SEQUENCE_EDITOR_UI(Operator):
    bl_idname = "wm.printhello7_4"
    bl_label = "Print Hello SEQUENCE_EDITOR_UI"

    def execute(self, context):
        custom_print("{space: SEQUENCE_EDITOR, region: UI}")
        return {'FINISHED'}

class HelloPanel_SEQUENCE_EDITOR_UI(Panel):
    bl_idname = "HelloPanel_SEQUENCE_EDITOR_UI"
    bl_label = "My Panel SEQUENCE_EDITOR_UI"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello7_4")

        
class PrintHello_SEQUENCE_EDITOR_TOOLS(Operator):
    bl_idname = "wm.printhello7_5"
    bl_label = "Print Hello SEQUENCE_EDITOR_TOOLS"

    def execute(self, context):
        custom_print("{space: SEQUENCE_EDITOR, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_SEQUENCE_EDITOR_TOOLS(Panel):
    bl_idname = "HelloPanel_SEQUENCE_EDITOR_TOOLS"
    bl_label = "My Panel SEQUENCE_EDITOR_TOOLS"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello7_5")

        
class PrintHello_SEQUENCE_EDITOR_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello7_6"
    bl_label = "Print Hello SEQUENCE_EDITOR_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: SEQUENCE_EDITOR, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_SEQUENCE_EDITOR_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_SEQUENCE_EDITOR_TOOL_PROPS"
    bl_label = "My Panel SEQUENCE_EDITOR_TOOL_PROPS"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello7_6")

        
class PrintHello_SEQUENCE_EDITOR_PREVIEW(Operator):
    bl_idname = "wm.printhello7_7"
    bl_label = "Print Hello SEQUENCE_EDITOR_PREVIEW"

    def execute(self, context):
        custom_print("{space: SEQUENCE_EDITOR, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_SEQUENCE_EDITOR_PREVIEW(Panel):
    bl_idname = "HelloPanel_SEQUENCE_EDITOR_PREVIEW"
    bl_label = "My Panel SEQUENCE_EDITOR_PREVIEW"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello7_7")

        
class PrintHello_CLIP_EDITOR_WINDOW(Operator):
    bl_idname = "wm.printhello8_0"
    bl_label = "Print Hello CLIP_EDITOR_WINDOW"

    def execute(self, context):
        custom_print("{space: CLIP_EDITOR, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_CLIP_EDITOR_WINDOW(Panel):
    bl_idname = "HelloPanel_CLIP_EDITOR_WINDOW"
    bl_label = "My Panel CLIP_EDITOR_WINDOW"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello8_0")

        
class PrintHello_CLIP_EDITOR_HEADER(Operator):
    bl_idname = "wm.printhello8_1"
    bl_label = "Print Hello CLIP_EDITOR_HEADER"

    def execute(self, context):
        custom_print("{space: CLIP_EDITOR, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_CLIP_EDITOR_HEADER(Panel):
    bl_idname = "HelloPanel_CLIP_EDITOR_HEADER"
    bl_label = "My Panel CLIP_EDITOR_HEADER"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello8_1")

        
class PrintHello_CLIP_EDITOR_CHANNELS(Operator):
    bl_idname = "wm.printhello8_2"
    bl_label = "Print Hello CLIP_EDITOR_CHANNELS"

    def execute(self, context):
        custom_print("{space: CLIP_EDITOR, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_CLIP_EDITOR_CHANNELS(Panel):
    bl_idname = "HelloPanel_CLIP_EDITOR_CHANNELS"
    bl_label = "My Panel CLIP_EDITOR_CHANNELS"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello8_2")

        
class PrintHello_CLIP_EDITOR_TEMPORARY(Operator):
    bl_idname = "wm.printhello8_3"
    bl_label = "Print Hello CLIP_EDITOR_TEMPORARY"

    def execute(self, context):
        custom_print("{space: CLIP_EDITOR, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_CLIP_EDITOR_TEMPORARY(Panel):
    bl_idname = "HelloPanel_CLIP_EDITOR_TEMPORARY"
    bl_label = "My Panel CLIP_EDITOR_TEMPORARY"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello8_3")

        
class PrintHello_CLIP_EDITOR_UI(Operator):
    bl_idname = "wm.printhello8_4"
    bl_label = "Print Hello CLIP_EDITOR_UI"

    def execute(self, context):
        custom_print("{space: CLIP_EDITOR, region: UI}")
        return {'FINISHED'}

class HelloPanel_CLIP_EDITOR_UI(Panel):
    bl_idname = "HelloPanel_CLIP_EDITOR_UI"
    bl_label = "My Panel CLIP_EDITOR_UI"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello8_4")

        
class PrintHello_CLIP_EDITOR_TOOLS(Operator):
    bl_idname = "wm.printhello8_5"
    bl_label = "Print Hello CLIP_EDITOR_TOOLS"

    def execute(self, context):
        custom_print("{space: CLIP_EDITOR, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_CLIP_EDITOR_TOOLS(Panel):
    bl_idname = "HelloPanel_CLIP_EDITOR_TOOLS"
    bl_label = "My Panel CLIP_EDITOR_TOOLS"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello8_5")

        
class PrintHello_CLIP_EDITOR_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello8_6"
    bl_label = "Print Hello CLIP_EDITOR_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: CLIP_EDITOR, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_CLIP_EDITOR_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_CLIP_EDITOR_TOOL_PROPS"
    bl_label = "My Panel CLIP_EDITOR_TOOL_PROPS"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello8_6")

        
class PrintHello_CLIP_EDITOR_PREVIEW(Operator):
    bl_idname = "wm.printhello8_7"
    bl_label = "Print Hello CLIP_EDITOR_PREVIEW"

    def execute(self, context):
        custom_print("{space: CLIP_EDITOR, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_CLIP_EDITOR_PREVIEW(Panel):
    bl_idname = "HelloPanel_CLIP_EDITOR_PREVIEW"
    bl_label = "My Panel CLIP_EDITOR_PREVIEW"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello8_7")

        
class PrintHello_TEXT_EDITOR_WINDOW(Operator):
    bl_idname = "wm.printhello9_0"
    bl_label = "Print Hello TEXT_EDITOR_WINDOW"

    def execute(self, context):
        custom_print("{space: TEXT_EDITOR, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_TEXT_EDITOR_WINDOW(Panel):
    bl_idname = "HelloPanel_TEXT_EDITOR_WINDOW"
    bl_label = "My Panel TEXT_EDITOR_WINDOW"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello9_0")

        
class PrintHello_TEXT_EDITOR_HEADER(Operator):
    bl_idname = "wm.printhello9_1"
    bl_label = "Print Hello TEXT_EDITOR_HEADER"

    def execute(self, context):
        custom_print("{space: TEXT_EDITOR, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_TEXT_EDITOR_HEADER(Panel):
    bl_idname = "HelloPanel_TEXT_EDITOR_HEADER"
    bl_label = "My Panel TEXT_EDITOR_HEADER"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello9_1")

        
class PrintHello_TEXT_EDITOR_CHANNELS(Operator):
    bl_idname = "wm.printhello9_2"
    bl_label = "Print Hello TEXT_EDITOR_CHANNELS"

    def execute(self, context):
        custom_print("{space: TEXT_EDITOR, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_TEXT_EDITOR_CHANNELS(Panel):
    bl_idname = "HelloPanel_TEXT_EDITOR_CHANNELS"
    bl_label = "My Panel TEXT_EDITOR_CHANNELS"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello9_2")

        
class PrintHello_TEXT_EDITOR_TEMPORARY(Operator):
    bl_idname = "wm.printhello9_3"
    bl_label = "Print Hello TEXT_EDITOR_TEMPORARY"

    def execute(self, context):
        custom_print("{space: TEXT_EDITOR, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_TEXT_EDITOR_TEMPORARY(Panel):
    bl_idname = "HelloPanel_TEXT_EDITOR_TEMPORARY"
    bl_label = "My Panel TEXT_EDITOR_TEMPORARY"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello9_3")

        
class PrintHello_TEXT_EDITOR_UI(Operator):
    bl_idname = "wm.printhello9_4"
    bl_label = "Print Hello TEXT_EDITOR_UI"

    def execute(self, context):
        custom_print("{space: TEXT_EDITOR, region: UI}")
        return {'FINISHED'}

class HelloPanel_TEXT_EDITOR_UI(Panel):
    bl_idname = "HelloPanel_TEXT_EDITOR_UI"
    bl_label = "My Panel TEXT_EDITOR_UI"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello9_4")

        
class PrintHello_TEXT_EDITOR_TOOLS(Operator):
    bl_idname = "wm.printhello9_5"
    bl_label = "Print Hello TEXT_EDITOR_TOOLS"

    def execute(self, context):
        custom_print("{space: TEXT_EDITOR, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_TEXT_EDITOR_TOOLS(Panel):
    bl_idname = "HelloPanel_TEXT_EDITOR_TOOLS"
    bl_label = "My Panel TEXT_EDITOR_TOOLS"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello9_5")

        
class PrintHello_TEXT_EDITOR_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello9_6"
    bl_label = "Print Hello TEXT_EDITOR_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: TEXT_EDITOR, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_TEXT_EDITOR_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_TEXT_EDITOR_TOOL_PROPS"
    bl_label = "My Panel TEXT_EDITOR_TOOL_PROPS"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello9_6")

        
class PrintHello_TEXT_EDITOR_PREVIEW(Operator):
    bl_idname = "wm.printhello9_7"
    bl_label = "Print Hello TEXT_EDITOR_PREVIEW"

    def execute(self, context):
        custom_print("{space: TEXT_EDITOR, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_TEXT_EDITOR_PREVIEW(Panel):
    bl_idname = "HelloPanel_TEXT_EDITOR_PREVIEW"
    bl_label = "My Panel TEXT_EDITOR_PREVIEW"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello9_7")

        
class PrintHello_NODE_EDITOR_WINDOW(Operator):
    bl_idname = "wm.printhello10_0"
    bl_label = "Print Hello NODE_EDITOR_WINDOW"

    def execute(self, context):
        custom_print("{space: NODE_EDITOR, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_NODE_EDITOR_WINDOW(Panel):
    bl_idname = "HelloPanel_NODE_EDITOR_WINDOW"
    bl_label = "My Panel NODE_EDITOR_WINDOW"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello10_0")

        
class PrintHello_NODE_EDITOR_HEADER(Operator):
    bl_idname = "wm.printhello10_1"
    bl_label = "Print Hello NODE_EDITOR_HEADER"

    def execute(self, context):
        custom_print("{space: NODE_EDITOR, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_NODE_EDITOR_HEADER(Panel):
    bl_idname = "HelloPanel_NODE_EDITOR_HEADER"
    bl_label = "My Panel NODE_EDITOR_HEADER"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello10_1")

        
class PrintHello_NODE_EDITOR_CHANNELS(Operator):
    bl_idname = "wm.printhello10_2"
    bl_label = "Print Hello NODE_EDITOR_CHANNELS"

    def execute(self, context):
        custom_print("{space: NODE_EDITOR, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_NODE_EDITOR_CHANNELS(Panel):
    bl_idname = "HelloPanel_NODE_EDITOR_CHANNELS"
    bl_label = "My Panel NODE_EDITOR_CHANNELS"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello10_2")

        
class PrintHello_NODE_EDITOR_TEMPORARY(Operator):
    bl_idname = "wm.printhello10_3"
    bl_label = "Print Hello NODE_EDITOR_TEMPORARY"

    def execute(self, context):
        custom_print("{space: NODE_EDITOR, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_NODE_EDITOR_TEMPORARY(Panel):
    bl_idname = "HelloPanel_NODE_EDITOR_TEMPORARY"
    bl_label = "My Panel NODE_EDITOR_TEMPORARY"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello10_3")

        
class PrintHello_NODE_EDITOR_UI(Operator):
    bl_idname = "wm.printhello10_4"
    bl_label = "Print Hello NODE_EDITOR_UI"

    def execute(self, context):
        custom_print("{space: NODE_EDITOR, region: UI}")
        return {'FINISHED'}

class HelloPanel_NODE_EDITOR_UI(Panel):
    bl_idname = "HelloPanel_NODE_EDITOR_UI"
    bl_label = "My Panel NODE_EDITOR_UI"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello10_4")

        
class PrintHello_NODE_EDITOR_TOOLS(Operator):
    bl_idname = "wm.printhello10_5"
    bl_label = "Print Hello NODE_EDITOR_TOOLS"

    def execute(self, context):
        custom_print("{space: NODE_EDITOR, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_NODE_EDITOR_TOOLS(Panel):
    bl_idname = "HelloPanel_NODE_EDITOR_TOOLS"
    bl_label = "My Panel NODE_EDITOR_TOOLS"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello10_5")

        
class PrintHello_NODE_EDITOR_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello10_6"
    bl_label = "Print Hello NODE_EDITOR_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: NODE_EDITOR, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_NODE_EDITOR_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_NODE_EDITOR_TOOL_PROPS"
    bl_label = "My Panel NODE_EDITOR_TOOL_PROPS"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello10_6")

        
class PrintHello_NODE_EDITOR_PREVIEW(Operator):
    bl_idname = "wm.printhello10_7"
    bl_label = "Print Hello NODE_EDITOR_PREVIEW"

    def execute(self, context):
        custom_print("{space: NODE_EDITOR, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_NODE_EDITOR_PREVIEW(Panel):
    bl_idname = "HelloPanel_NODE_EDITOR_PREVIEW"
    bl_label = "My Panel NODE_EDITOR_PREVIEW"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello10_7")

        
class PrintHello_LOGIC_EDITOR_WINDOW(Operator):
    bl_idname = "wm.printhello11_0"
    bl_label = "Print Hello LOGIC_EDITOR_WINDOW"

    def execute(self, context):
        custom_print("{space: LOGIC_EDITOR, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_LOGIC_EDITOR_WINDOW(Panel):
    bl_idname = "HelloPanel_LOGIC_EDITOR_WINDOW"
    bl_label = "My Panel LOGIC_EDITOR_WINDOW"
    bl_space_type = "LOGIC_EDITOR"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello11_0")

        
class PrintHello_LOGIC_EDITOR_HEADER(Operator):
    bl_idname = "wm.printhello11_1"
    bl_label = "Print Hello LOGIC_EDITOR_HEADER"

    def execute(self, context):
        custom_print("{space: LOGIC_EDITOR, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_LOGIC_EDITOR_HEADER(Panel):
    bl_idname = "HelloPanel_LOGIC_EDITOR_HEADER"
    bl_label = "My Panel LOGIC_EDITOR_HEADER"
    bl_space_type = "LOGIC_EDITOR"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello11_1")

        
class PrintHello_LOGIC_EDITOR_CHANNELS(Operator):
    bl_idname = "wm.printhello11_2"
    bl_label = "Print Hello LOGIC_EDITOR_CHANNELS"

    def execute(self, context):
        custom_print("{space: LOGIC_EDITOR, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_LOGIC_EDITOR_CHANNELS(Panel):
    bl_idname = "HelloPanel_LOGIC_EDITOR_CHANNELS"
    bl_label = "My Panel LOGIC_EDITOR_CHANNELS"
    bl_space_type = "LOGIC_EDITOR"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello11_2")

        
class PrintHello_LOGIC_EDITOR_TEMPORARY(Operator):
    bl_idname = "wm.printhello11_3"
    bl_label = "Print Hello LOGIC_EDITOR_TEMPORARY"

    def execute(self, context):
        custom_print("{space: LOGIC_EDITOR, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_LOGIC_EDITOR_TEMPORARY(Panel):
    bl_idname = "HelloPanel_LOGIC_EDITOR_TEMPORARY"
    bl_label = "My Panel LOGIC_EDITOR_TEMPORARY"
    bl_space_type = "LOGIC_EDITOR"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello11_3")

        
class PrintHello_LOGIC_EDITOR_UI(Operator):
    bl_idname = "wm.printhello11_4"
    bl_label = "Print Hello LOGIC_EDITOR_UI"

    def execute(self, context):
        custom_print("{space: LOGIC_EDITOR, region: UI}")
        return {'FINISHED'}

class HelloPanel_LOGIC_EDITOR_UI(Panel):
    bl_idname = "HelloPanel_LOGIC_EDITOR_UI"
    bl_label = "My Panel LOGIC_EDITOR_UI"
    bl_space_type = "LOGIC_EDITOR"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello11_4")

        
class PrintHello_LOGIC_EDITOR_TOOLS(Operator):
    bl_idname = "wm.printhello11_5"
    bl_label = "Print Hello LOGIC_EDITOR_TOOLS"

    def execute(self, context):
        custom_print("{space: LOGIC_EDITOR, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_LOGIC_EDITOR_TOOLS(Panel):
    bl_idname = "HelloPanel_LOGIC_EDITOR_TOOLS"
    bl_label = "My Panel LOGIC_EDITOR_TOOLS"
    bl_space_type = "LOGIC_EDITOR"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello11_5")

        
class PrintHello_LOGIC_EDITOR_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello11_6"
    bl_label = "Print Hello LOGIC_EDITOR_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: LOGIC_EDITOR, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_LOGIC_EDITOR_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_LOGIC_EDITOR_TOOL_PROPS"
    bl_label = "My Panel LOGIC_EDITOR_TOOL_PROPS"
    bl_space_type = "LOGIC_EDITOR"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello11_6")

        
class PrintHello_LOGIC_EDITOR_PREVIEW(Operator):
    bl_idname = "wm.printhello11_7"
    bl_label = "Print Hello LOGIC_EDITOR_PREVIEW"

    def execute(self, context):
        custom_print("{space: LOGIC_EDITOR, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_LOGIC_EDITOR_PREVIEW(Panel):
    bl_idname = "HelloPanel_LOGIC_EDITOR_PREVIEW"
    bl_label = "My Panel LOGIC_EDITOR_PREVIEW"
    bl_space_type = "LOGIC_EDITOR"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello11_7")

        
class PrintHello_PROPERTIES_WINDOW(Operator):
    bl_idname = "wm.printhello12_0"
    bl_label = "Print Hello PROPERTIES_WINDOW"

    def execute(self, context):
        custom_print("{space: PROPERTIES, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_PROPERTIES_WINDOW(Panel):
    bl_idname = "HelloPanel_PROPERTIES_WINDOW"
    bl_label = "My Panel PROPERTIES_WINDOW"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello12_0")

        
class PrintHello_PROPERTIES_HEADER(Operator):
    bl_idname = "wm.printhello12_1"
    bl_label = "Print Hello PROPERTIES_HEADER"

    def execute(self, context):
        custom_print("{space: PROPERTIES, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_PROPERTIES_HEADER(Panel):
    bl_idname = "HelloPanel_PROPERTIES_HEADER"
    bl_label = "My Panel PROPERTIES_HEADER"
    bl_space_type = "PROPERTIES"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello12_1")

        
class PrintHello_PROPERTIES_CHANNELS(Operator):
    bl_idname = "wm.printhello12_2"
    bl_label = "Print Hello PROPERTIES_CHANNELS"

    def execute(self, context):
        custom_print("{space: PROPERTIES, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_PROPERTIES_CHANNELS(Panel):
    bl_idname = "HelloPanel_PROPERTIES_CHANNELS"
    bl_label = "My Panel PROPERTIES_CHANNELS"
    bl_space_type = "PROPERTIES"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello12_2")

        
class PrintHello_PROPERTIES_TEMPORARY(Operator):
    bl_idname = "wm.printhello12_3"
    bl_label = "Print Hello PROPERTIES_TEMPORARY"

    def execute(self, context):
        custom_print("{space: PROPERTIES, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_PROPERTIES_TEMPORARY(Panel):
    bl_idname = "HelloPanel_PROPERTIES_TEMPORARY"
    bl_label = "My Panel PROPERTIES_TEMPORARY"
    bl_space_type = "PROPERTIES"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello12_3")

        
class PrintHello_PROPERTIES_UI(Operator):
    bl_idname = "wm.printhello12_4"
    bl_label = "Print Hello PROPERTIES_UI"

    def execute(self, context):
        custom_print("{space: PROPERTIES, region: UI}")
        return {'FINISHED'}

class HelloPanel_PROPERTIES_UI(Panel):
    bl_idname = "HelloPanel_PROPERTIES_UI"
    bl_label = "My Panel PROPERTIES_UI"
    bl_space_type = "PROPERTIES"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello12_4")

        
class PrintHello_PROPERTIES_TOOLS(Operator):
    bl_idname = "wm.printhello12_5"
    bl_label = "Print Hello PROPERTIES_TOOLS"

    def execute(self, context):
        custom_print("{space: PROPERTIES, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_PROPERTIES_TOOLS(Panel):
    bl_idname = "HelloPanel_PROPERTIES_TOOLS"
    bl_label = "My Panel PROPERTIES_TOOLS"
    bl_space_type = "PROPERTIES"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello12_5")

        
class PrintHello_PROPERTIES_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello12_6"
    bl_label = "Print Hello PROPERTIES_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: PROPERTIES, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_PROPERTIES_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_PROPERTIES_TOOL_PROPS"
    bl_label = "My Panel PROPERTIES_TOOL_PROPS"
    bl_space_type = "PROPERTIES"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello12_6")

        
class PrintHello_PROPERTIES_PREVIEW(Operator):
    bl_idname = "wm.printhello12_7"
    bl_label = "Print Hello PROPERTIES_PREVIEW"

    def execute(self, context):
        custom_print("{space: PROPERTIES, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_PROPERTIES_PREVIEW(Panel):
    bl_idname = "HelloPanel_PROPERTIES_PREVIEW"
    bl_label = "My Panel PROPERTIES_PREVIEW"
    bl_space_type = "PROPERTIES"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello12_7")

        
class PrintHello_OUTLINER_WINDOW(Operator):
    bl_idname = "wm.printhello13_0"
    bl_label = "Print Hello OUTLINER_WINDOW"

    def execute(self, context):
        custom_print("{space: OUTLINER, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_OUTLINER_WINDOW(Panel):
    bl_idname = "HelloPanel_OUTLINER_WINDOW"
    bl_label = "My Panel OUTLINER_WINDOW"
    bl_space_type = "OUTLINER"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello13_0")

        
class PrintHello_OUTLINER_HEADER(Operator):
    bl_idname = "wm.printhello13_1"
    bl_label = "Print Hello OUTLINER_HEADER"

    def execute(self, context):
        custom_print("{space: OUTLINER, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_OUTLINER_HEADER(Panel):
    bl_idname = "HelloPanel_OUTLINER_HEADER"
    bl_label = "My Panel OUTLINER_HEADER"
    bl_space_type = "OUTLINER"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello13_1")

        
class PrintHello_OUTLINER_CHANNELS(Operator):
    bl_idname = "wm.printhello13_2"
    bl_label = "Print Hello OUTLINER_CHANNELS"

    def execute(self, context):
        custom_print("{space: OUTLINER, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_OUTLINER_CHANNELS(Panel):
    bl_idname = "HelloPanel_OUTLINER_CHANNELS"
    bl_label = "My Panel OUTLINER_CHANNELS"
    bl_space_type = "OUTLINER"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello13_2")

        
class PrintHello_OUTLINER_TEMPORARY(Operator):
    bl_idname = "wm.printhello13_3"
    bl_label = "Print Hello OUTLINER_TEMPORARY"

    def execute(self, context):
        custom_print("{space: OUTLINER, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_OUTLINER_TEMPORARY(Panel):
    bl_idname = "HelloPanel_OUTLINER_TEMPORARY"
    bl_label = "My Panel OUTLINER_TEMPORARY"
    bl_space_type = "OUTLINER"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello13_3")

        
class PrintHello_OUTLINER_UI(Operator):
    bl_idname = "wm.printhello13_4"
    bl_label = "Print Hello OUTLINER_UI"

    def execute(self, context):
        custom_print("{space: OUTLINER, region: UI}")
        return {'FINISHED'}

class HelloPanel_OUTLINER_UI(Panel):
    bl_idname = "HelloPanel_OUTLINER_UI"
    bl_label = "My Panel OUTLINER_UI"
    bl_space_type = "OUTLINER"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello13_4")

        
class PrintHello_OUTLINER_TOOLS(Operator):
    bl_idname = "wm.printhello13_5"
    bl_label = "Print Hello OUTLINER_TOOLS"

    def execute(self, context):
        custom_print("{space: OUTLINER, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_OUTLINER_TOOLS(Panel):
    bl_idname = "HelloPanel_OUTLINER_TOOLS"
    bl_label = "My Panel OUTLINER_TOOLS"
    bl_space_type = "OUTLINER"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello13_5")

        
class PrintHello_OUTLINER_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello13_6"
    bl_label = "Print Hello OUTLINER_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: OUTLINER, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_OUTLINER_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_OUTLINER_TOOL_PROPS"
    bl_label = "My Panel OUTLINER_TOOL_PROPS"
    bl_space_type = "OUTLINER"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello13_6")

        
class PrintHello_OUTLINER_PREVIEW(Operator):
    bl_idname = "wm.printhello13_7"
    bl_label = "Print Hello OUTLINER_PREVIEW"

    def execute(self, context):
        custom_print("{space: OUTLINER, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_OUTLINER_PREVIEW(Panel):
    bl_idname = "HelloPanel_OUTLINER_PREVIEW"
    bl_label = "My Panel OUTLINER_PREVIEW"
    bl_space_type = "OUTLINER"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello13_7")

        
class PrintHello_USER_PREFERENCES_WINDOW(Operator):
    bl_idname = "wm.printhello14_0"
    bl_label = "Print Hello USER_PREFERENCES_WINDOW"

    def execute(self, context):
        custom_print("{space: USER_PREFERENCES, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_USER_PREFERENCES_WINDOW(Panel):
    bl_idname = "HelloPanel_USER_PREFERENCES_WINDOW"
    bl_label = "My Panel USER_PREFERENCES_WINDOW"
    bl_space_type = "USER_PREFERENCES"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello14_0")

        
class PrintHello_USER_PREFERENCES_HEADER(Operator):
    bl_idname = "wm.printhello14_1"
    bl_label = "Print Hello USER_PREFERENCES_HEADER"

    def execute(self, context):
        custom_print("{space: USER_PREFERENCES, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_USER_PREFERENCES_HEADER(Panel):
    bl_idname = "HelloPanel_USER_PREFERENCES_HEADER"
    bl_label = "My Panel USER_PREFERENCES_HEADER"
    bl_space_type = "USER_PREFERENCES"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello14_1")

        
class PrintHello_USER_PREFERENCES_CHANNELS(Operator):
    bl_idname = "wm.printhello14_2"
    bl_label = "Print Hello USER_PREFERENCES_CHANNELS"

    def execute(self, context):
        custom_print("{space: USER_PREFERENCES, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_USER_PREFERENCES_CHANNELS(Panel):
    bl_idname = "HelloPanel_USER_PREFERENCES_CHANNELS"
    bl_label = "My Panel USER_PREFERENCES_CHANNELS"
    bl_space_type = "USER_PREFERENCES"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello14_2")

        
class PrintHello_USER_PREFERENCES_TEMPORARY(Operator):
    bl_idname = "wm.printhello14_3"
    bl_label = "Print Hello USER_PREFERENCES_TEMPORARY"

    def execute(self, context):
        custom_print("{space: USER_PREFERENCES, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_USER_PREFERENCES_TEMPORARY(Panel):
    bl_idname = "HelloPanel_USER_PREFERENCES_TEMPORARY"
    bl_label = "My Panel USER_PREFERENCES_TEMPORARY"
    bl_space_type = "USER_PREFERENCES"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello14_3")

        
class PrintHello_USER_PREFERENCES_UI(Operator):
    bl_idname = "wm.printhello14_4"
    bl_label = "Print Hello USER_PREFERENCES_UI"

    def execute(self, context):
        custom_print("{space: USER_PREFERENCES, region: UI}")
        return {'FINISHED'}

class HelloPanel_USER_PREFERENCES_UI(Panel):
    bl_idname = "HelloPanel_USER_PREFERENCES_UI"
    bl_label = "My Panel USER_PREFERENCES_UI"
    bl_space_type = "USER_PREFERENCES"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello14_4")

        
class PrintHello_USER_PREFERENCES_TOOLS(Operator):
    bl_idname = "wm.printhello14_5"
    bl_label = "Print Hello USER_PREFERENCES_TOOLS"

    def execute(self, context):
        custom_print("{space: USER_PREFERENCES, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_USER_PREFERENCES_TOOLS(Panel):
    bl_idname = "HelloPanel_USER_PREFERENCES_TOOLS"
    bl_label = "My Panel USER_PREFERENCES_TOOLS"
    bl_space_type = "USER_PREFERENCES"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello14_5")

        
class PrintHello_USER_PREFERENCES_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello14_6"
    bl_label = "Print Hello USER_PREFERENCES_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: USER_PREFERENCES, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_USER_PREFERENCES_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_USER_PREFERENCES_TOOL_PROPS"
    bl_label = "My Panel USER_PREFERENCES_TOOL_PROPS"
    bl_space_type = "USER_PREFERENCES"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello14_6")

        
class PrintHello_USER_PREFERENCES_PREVIEW(Operator):
    bl_idname = "wm.printhello14_7"
    bl_label = "Print Hello USER_PREFERENCES_PREVIEW"

    def execute(self, context):
        custom_print("{space: USER_PREFERENCES, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_USER_PREFERENCES_PREVIEW(Panel):
    bl_idname = "HelloPanel_USER_PREFERENCES_PREVIEW"
    bl_label = "My Panel USER_PREFERENCES_PREVIEW"
    bl_space_type = "USER_PREFERENCES"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello14_7")

        
class PrintHello_INFO_WINDOW(Operator):
    bl_idname = "wm.printhello15_0"
    bl_label = "Print Hello INFO_WINDOW"

    def execute(self, context):
        custom_print("{space: INFO, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_INFO_WINDOW(Panel):
    bl_idname = "HelloPanel_INFO_WINDOW"
    bl_label = "My Panel INFO_WINDOW"
    bl_space_type = "INFO"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello15_0")

        
class PrintHello_INFO_HEADER(Operator):
    bl_idname = "wm.printhello15_1"
    bl_label = "Print Hello INFO_HEADER"

    def execute(self, context):
        custom_print("{space: INFO, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_INFO_HEADER(Panel):
    bl_idname = "HelloPanel_INFO_HEADER"
    bl_label = "My Panel INFO_HEADER"
    bl_space_type = "INFO"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello15_1")

        
class PrintHello_INFO_CHANNELS(Operator):
    bl_idname = "wm.printhello15_2"
    bl_label = "Print Hello INFO_CHANNELS"

    def execute(self, context):
        custom_print("{space: INFO, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_INFO_CHANNELS(Panel):
    bl_idname = "HelloPanel_INFO_CHANNELS"
    bl_label = "My Panel INFO_CHANNELS"
    bl_space_type = "INFO"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello15_2")

        
class PrintHello_INFO_TEMPORARY(Operator):
    bl_idname = "wm.printhello15_3"
    bl_label = "Print Hello INFO_TEMPORARY"

    def execute(self, context):
        custom_print("{space: INFO, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_INFO_TEMPORARY(Panel):
    bl_idname = "HelloPanel_INFO_TEMPORARY"
    bl_label = "My Panel INFO_TEMPORARY"
    bl_space_type = "INFO"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello15_3")

        
class PrintHello_INFO_UI(Operator):
    bl_idname = "wm.printhello15_4"
    bl_label = "Print Hello INFO_UI"

    def execute(self, context):
        custom_print("{space: INFO, region: UI}")
        return {'FINISHED'}

class HelloPanel_INFO_UI(Panel):
    bl_idname = "HelloPanel_INFO_UI"
    bl_label = "My Panel INFO_UI"
    bl_space_type = "INFO"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello15_4")

        
class PrintHello_INFO_TOOLS(Operator):
    bl_idname = "wm.printhello15_5"
    bl_label = "Print Hello INFO_TOOLS"

    def execute(self, context):
        custom_print("{space: INFO, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_INFO_TOOLS(Panel):
    bl_idname = "HelloPanel_INFO_TOOLS"
    bl_label = "My Panel INFO_TOOLS"
    bl_space_type = "INFO"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello15_5")

        
class PrintHello_INFO_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello15_6"
    bl_label = "Print Hello INFO_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: INFO, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_INFO_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_INFO_TOOL_PROPS"
    bl_label = "My Panel INFO_TOOL_PROPS"
    bl_space_type = "INFO"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello15_6")

        
class PrintHello_INFO_PREVIEW(Operator):
    bl_idname = "wm.printhello15_7"
    bl_label = "Print Hello INFO_PREVIEW"

    def execute(self, context):
        custom_print("{space: INFO, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_INFO_PREVIEW(Panel):
    bl_idname = "HelloPanel_INFO_PREVIEW"
    bl_label = "My Panel INFO_PREVIEW"
    bl_space_type = "INFO"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello15_7")

        
class PrintHello_FILE_BROWSER_WINDOW(Operator):
    bl_idname = "wm.printhello16_0"
    bl_label = "Print Hello FILE_BROWSER_WINDOW"

    def execute(self, context):
        custom_print("{space: FILE_BROWSER, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_FILE_BROWSER_WINDOW(Panel):
    bl_idname = "HelloPanel_FILE_BROWSER_WINDOW"
    bl_label = "My Panel FILE_BROWSER_WINDOW"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello16_0")

        
class PrintHello_FILE_BROWSER_HEADER(Operator):
    bl_idname = "wm.printhello16_1"
    bl_label = "Print Hello FILE_BROWSER_HEADER"

    def execute(self, context):
        custom_print("{space: FILE_BROWSER, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_FILE_BROWSER_HEADER(Panel):
    bl_idname = "HelloPanel_FILE_BROWSER_HEADER"
    bl_label = "My Panel FILE_BROWSER_HEADER"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello16_1")

        
class PrintHello_FILE_BROWSER_CHANNELS(Operator):
    bl_idname = "wm.printhello16_2"
    bl_label = "Print Hello FILE_BROWSER_CHANNELS"

    def execute(self, context):
        custom_print("{space: FILE_BROWSER, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_FILE_BROWSER_CHANNELS(Panel):
    bl_idname = "HelloPanel_FILE_BROWSER_CHANNELS"
    bl_label = "My Panel FILE_BROWSER_CHANNELS"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello16_2")

        
class PrintHello_FILE_BROWSER_TEMPORARY(Operator):
    bl_idname = "wm.printhello16_3"
    bl_label = "Print Hello FILE_BROWSER_TEMPORARY"

    def execute(self, context):
        custom_print("{space: FILE_BROWSER, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_FILE_BROWSER_TEMPORARY(Panel):
    bl_idname = "HelloPanel_FILE_BROWSER_TEMPORARY"
    bl_label = "My Panel FILE_BROWSER_TEMPORARY"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello16_3")

        
class PrintHello_FILE_BROWSER_UI(Operator):
    bl_idname = "wm.printhello16_4"
    bl_label = "Print Hello FILE_BROWSER_UI"

    def execute(self, context):
        custom_print("{space: FILE_BROWSER, region: UI}")
        return {'FINISHED'}

class HelloPanel_FILE_BROWSER_UI(Panel):
    bl_idname = "HelloPanel_FILE_BROWSER_UI"
    bl_label = "My Panel FILE_BROWSER_UI"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello16_4")

        
class PrintHello_FILE_BROWSER_TOOLS(Operator):
    bl_idname = "wm.printhello16_5"
    bl_label = "Print Hello FILE_BROWSER_TOOLS"

    def execute(self, context):
        custom_print("{space: FILE_BROWSER, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_FILE_BROWSER_TOOLS(Panel):
    bl_idname = "HelloPanel_FILE_BROWSER_TOOLS"
    bl_label = "My Panel FILE_BROWSER_TOOLS"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello16_5")

        
class PrintHello_FILE_BROWSER_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello16_6"
    bl_label = "Print Hello FILE_BROWSER_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: FILE_BROWSER, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_FILE_BROWSER_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_FILE_BROWSER_TOOL_PROPS"
    bl_label = "My Panel FILE_BROWSER_TOOL_PROPS"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello16_6")

        
class PrintHello_FILE_BROWSER_PREVIEW(Operator):
    bl_idname = "wm.printhello16_7"
    bl_label = "Print Hello FILE_BROWSER_PREVIEW"

    def execute(self, context):
        custom_print("{space: FILE_BROWSER, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_FILE_BROWSER_PREVIEW(Panel):
    bl_idname = "HelloPanel_FILE_BROWSER_PREVIEW"
    bl_label = "My Panel FILE_BROWSER_PREVIEW"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello16_7")

        
class PrintHello_CONSOLE_WINDOW(Operator):
    bl_idname = "wm.printhello17_0"
    bl_label = "Print Hello CONSOLE_WINDOW"

    def execute(self, context):
        custom_print("{space: CONSOLE, region: WINDOW}")
        return {'FINISHED'}

class HelloPanel_CONSOLE_WINDOW(Panel):
    bl_idname = "HelloPanel_CONSOLE_WINDOW"
    bl_label = "My Panel CONSOLE_WINDOW"
    bl_space_type = "CONSOLE"
    bl_region_type = "WINDOW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello17_0")

        
class PrintHello_CONSOLE_HEADER(Operator):
    bl_idname = "wm.printhello17_1"
    bl_label = "Print Hello CONSOLE_HEADER"

    def execute(self, context):
        custom_print("{space: CONSOLE, region: HEADER}")
        return {'FINISHED'}

class HelloPanel_CONSOLE_HEADER(Panel):
    bl_idname = "HelloPanel_CONSOLE_HEADER"
    bl_label = "My Panel CONSOLE_HEADER"
    bl_space_type = "CONSOLE"
    bl_region_type = "HEADER"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello17_1")

        
class PrintHello_CONSOLE_CHANNELS(Operator):
    bl_idname = "wm.printhello17_2"
    bl_label = "Print Hello CONSOLE_CHANNELS"

    def execute(self, context):
        custom_print("{space: CONSOLE, region: CHANNELS}")
        return {'FINISHED'}

class HelloPanel_CONSOLE_CHANNELS(Panel):
    bl_idname = "HelloPanel_CONSOLE_CHANNELS"
    bl_label = "My Panel CONSOLE_CHANNELS"
    bl_space_type = "CONSOLE"
    bl_region_type = "CHANNELS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello17_2")

        
class PrintHello_CONSOLE_TEMPORARY(Operator):
    bl_idname = "wm.printhello17_3"
    bl_label = "Print Hello CONSOLE_TEMPORARY"

    def execute(self, context):
        custom_print("{space: CONSOLE, region: TEMPORARY}")
        return {'FINISHED'}

class HelloPanel_CONSOLE_TEMPORARY(Panel):
    bl_idname = "HelloPanel_CONSOLE_TEMPORARY"
    bl_label = "My Panel CONSOLE_TEMPORARY"
    bl_space_type = "CONSOLE"
    bl_region_type = "TEMPORARY"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello17_3")

        
class PrintHello_CONSOLE_UI(Operator):
    bl_idname = "wm.printhello17_4"
    bl_label = "Print Hello CONSOLE_UI"

    def execute(self, context):
        custom_print("{space: CONSOLE, region: UI}")
        return {'FINISHED'}

class HelloPanel_CONSOLE_UI(Panel):
    bl_idname = "HelloPanel_CONSOLE_UI"
    bl_label = "My Panel CONSOLE_UI"
    bl_space_type = "CONSOLE"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello17_4")

        
class PrintHello_CONSOLE_TOOLS(Operator):
    bl_idname = "wm.printhello17_5"
    bl_label = "Print Hello CONSOLE_TOOLS"

    def execute(self, context):
        custom_print("{space: CONSOLE, region: TOOLS}")
        return {'FINISHED'}

class HelloPanel_CONSOLE_TOOLS(Panel):
    bl_idname = "HelloPanel_CONSOLE_TOOLS"
    bl_label = "My Panel CONSOLE_TOOLS"
    bl_space_type = "CONSOLE"
    bl_region_type = "TOOLS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello17_5")

        
class PrintHello_CONSOLE_TOOL_PROPS(Operator):
    bl_idname = "wm.printhello17_6"
    bl_label = "Print Hello CONSOLE_TOOL_PROPS"

    def execute(self, context):
        custom_print("{space: CONSOLE, region: TOOL_PROPS}")
        return {'FINISHED'}

class HelloPanel_CONSOLE_TOOL_PROPS(Panel):
    bl_idname = "HelloPanel_CONSOLE_TOOL_PROPS"
    bl_label = "My Panel CONSOLE_TOOL_PROPS"
    bl_space_type = "CONSOLE"
    bl_region_type = "TOOL_PROPS"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello17_6")

        
class PrintHello_CONSOLE_PREVIEW(Operator):
    bl_idname = "wm.printhello17_7"
    bl_label = "Print Hello CONSOLE_PREVIEW"

    def execute(self, context):
        custom_print("{space: CONSOLE, region: PREVIEW}")
        return {'FINISHED'}

class HelloPanel_CONSOLE_PREVIEW(Panel):
    bl_idname = "HelloPanel_CONSOLE_PREVIEW"
    bl_label = "My Panel CONSOLE_PREVIEW"
    bl_space_type = "CONSOLE"
    bl_region_type = "PREVIEW"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("wm.printhello17_7")

        

