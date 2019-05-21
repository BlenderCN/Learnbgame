bl_info = {
    "name": "Print to Python Interactive Console",
    "category": "Development",
}
import bpy
import os
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                        )
from enum import Enum
# double dot means up one level
from ..models.context_data import ContextData

class Strategy(Enum):
    ALL = 0
    CURRENT_SCREEN = 1
    FIRST_CONSOLE_IN_CURRENT_SCREEN = 2

# ---- start of Console capturing ------
def get_consoles(strategy):
    ''' Get all the opened consoles '''
    consoleContextList = []

    console_areas = get_areas(strategy, 'CONSOLE')

    for area in console_areas:

        space = get_space(area, 'CONSOLE')

        contextData = ContextData(area, space)
        consoleContextList.extend([contextData])

    return consoleContextList

def get_areas(strategy, area_name):
    areas = []
    if (strategy == Strategy.ALL):
        for screen in bpy.data.screens:
            areas.extend([area for area in screen.areas if area.type == area_name])
    else:
        areas.extend([area for area in bpy.context.screen.areas if area.type == area_name])
    return areas

def get_space(area, space_name):
    spaces = [space for space in area.spaces if space.type == space_name]

    if spaces == None:
        return None
    # only one space for a single area could be found with the area_name
    elif len(spaces) > 1:
        print("Unhandled situation: multiple spaces with the name " + space_name + " where found for the area " + area.type)

    elif (len(spaces) == 1):
        return spaces[0]

    else:
        # unreachable
        return None
# ------ end of Console capturing -----------

# ---- start of Console writing ------
def console_write(text):
    strategy = Strategy.ALL
    # Note: we can't use a global list as a new console editor could be added any time
    #       thus we need to recapture the list before every write (performance penalty)!
    consoleContextList = get_consoles(strategy)
    for consoleContext in consoleContextList:
        area = consoleContext.area
        space = consoleContext.space

        if space is None:
            return

        context = bpy.context.copy()
        context.update(dict(
            space=space,
            area=area,
        ))
        for line in text.split("\n"):
            bpy.ops.console.scrollback_append(context, text=line, type='OUTPUT')
        if (strategy == Strategy.FIRST_CONSOLE_IN_CURRENT_SCREEN):
            # we will only print once
            return
# ------ end of Console writing -----------


