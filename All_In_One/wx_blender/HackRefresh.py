#!/usr/bin/env python

from bpy import ops

def HackRefresh():
    """
    When moving/sizing the wxFrame, It smears across the blender GUI,
    making it look ugly.

    What is being attempted here is a refresh,
    so to clear the ugliness from the screen.
    """
    ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
