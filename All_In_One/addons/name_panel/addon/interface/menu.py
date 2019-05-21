
# imports
import bpy
from bpy.types import Menu
from .buttons.menu import menu

class specials(Menu):
    '''
        Menu for name panel operators.
    '''
    bl_idname = 'VIEW3D_MT_name_panel_specials'
    bl_label = 'Operators'
    bl_description = 'Operators and settings.'

    def draw(self, context):
        '''
            Draw the menu body.
        '''

        menu(self, context)
