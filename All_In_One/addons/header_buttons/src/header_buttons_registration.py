#----------------------------------------------------------------------
# header_buttons_registration.py
#----------------------------------------------------------------------
# This file contains the generated register methods
# for the header buttons.
# Each button is handled with by it's own add_to_header_space_id method
# as there is already a different button for every space  
#----------------------------------------------------------------------
# File generated on 2017-12-26 00:29:13
#----------------------------------------------------------------------

import bpy
from . import header_buttons 

def register():
# PrintHello registration per space
    bpy.types.VIEW3D_HT_header.append(header_buttons.add_to_header_1)
    bpy.types.TIME_HT_header.append(header_buttons.add_to_header_2)
    bpy.types.GRAPH_HT_header.append(header_buttons.add_to_header_3)
    bpy.types.DOPESHEET_HT_header.append(header_buttons.add_to_header_4)
    bpy.types.NLA_HT_header.append(header_buttons.add_to_header_5)
    bpy.types.IMAGE_HT_header.append(header_buttons.add_to_header_6)
    bpy.types.SEQUENCER_HT_header.append(header_buttons.add_to_header_7)
    bpy.types.CLIP_HT_header.append(header_buttons.add_to_header_8)
    bpy.types.TEXT_HT_header.append(header_buttons.add_to_header_9)
    bpy.types.NODE_HT_header.append(header_buttons.add_to_header_10)
    bpy.types.LOGIC_HT_header.append(header_buttons.add_to_header_11)
    bpy.types.PROPERTIES_HT_header.append(header_buttons.add_to_header_12)
    bpy.types.OUTLINER_HT_header.append(header_buttons.add_to_header_13)
    bpy.types.USERPREF_HT_header.append(header_buttons.add_to_header_14)
    bpy.types.INFO_HT_header.append(header_buttons.add_to_header_15)
    bpy.types.FILEBROWSER_HT_header.append(header_buttons.add_to_header_16)
    bpy.types.CONSOLE_HT_header.append(header_buttons.add_to_header_17)

def unregister():
# PrintHello registration per space
    bpy.types.VIEW3D_HT_header.remove(header_buttons.add_to_header_1)
    bpy.types.TIME_HT_header.remove(header_buttons.add_to_header_2)
    bpy.types.GRAPH_HT_header.remove(header_buttons.add_to_header_3)
    bpy.types.DOPESHEET_HT_header.remove(header_buttons.add_to_header_4)
    bpy.types.NLA_HT_header.remove(header_buttons.add_to_header_5)
    bpy.types.IMAGE_HT_header.remove(header_buttons.add_to_header_6)
    bpy.types.SEQUENCER_HT_header.remove(header_buttons.add_to_header_7)
    bpy.types.CLIP_HT_header.remove(header_buttons.add_to_header_8)
    bpy.types.TEXT_HT_header.remove(header_buttons.add_to_header_9)
    bpy.types.NODE_HT_header.remove(header_buttons.add_to_header_10)
    bpy.types.LOGIC_HT_header.remove(header_buttons.add_to_header_11)
    bpy.types.PROPERTIES_HT_header.remove(header_buttons.add_to_header_12)
    bpy.types.OUTLINER_HT_header.remove(header_buttons.add_to_header_13)
    bpy.types.USERPREF_HT_header.remove(header_buttons.add_to_header_14)
    bpy.types.INFO_HT_header.remove(header_buttons.add_to_header_15)
    bpy.types.FILEBROWSER_HT_header.remove(header_buttons.add_to_header_16)
    bpy.types.CONSOLE_HT_header.remove(header_buttons.add_to_header_17)


