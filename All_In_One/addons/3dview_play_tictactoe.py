# ##### BEGIN GPL LICENSE BLOCK #####
#
#  3dview_play_tictactoe.py
#  Play tic-tac-toe in the viewport!
#  Copyright (C) 2015 Quentin Wenger
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



bl_info = {"name": "Play Tic-Tac-Toe",
           "description": "Play tic-tac-toe in the viewport!",
           "author": "Quentin Wenger (Matpi)",
           "version": (1, 0),
           "blender": (2, 75, 0),
           "location": "Custom Render Engine -> Play Tic-Tac-Toe, then "\
                       "'Start' in the menu.",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "3D View"
           }



import bpy
import bgl
import blf
from collections import deque
from random import choice
from mathutils import Matrix

# global parameters (ugly, but it works...)
handle = []
end = [False]
game = [None]
init = [False]


class TicTacToePlay(bpy.types.RenderEngine):
    bl_idname = 'tictactoe_renderer'
    bl_label = 'Play Tic-Tac-Toe!'
    #bl_use_preview = True

    def view_draw(self, context):
        if game[0]:
            game[0].next(context)
            game[0].render(context)
        elif (context.space_data.type == 'VIEW_3D'
              and context.region.type == 'WINDOW'):
            game[0] = TicTacToeGame()
            """if not init[0]:
                bpy.app.handlers.scene_update_post.append(addBootstrap)"""
            
        
    def view_update(self, context):
        pass
        
    def render(self, scene):
        pass

class TicTacToeOperator(bpy.types.Operator):
    bl_idname = "view3d.modal_operator_tictactoe"
    bl_label = "Tic Tac Toe Operator"
    bl_options = {'INTERNAL'}

    def modal(self, context, event):
        if end[0]:
            return {'FINISHED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if game[0] and not game[0].mouse_coords:
                game[0].mouse_coords = (event.mouse_region_x,
                                        event.mouse_region_y)
        context.region_data.update()
        context.region.tag_redraw()
        return {'PASS_THROUGH'}
        
    def invoke(self, context, event):
        #if context.space_data.type == 'VIEW_3D':
        context.space_data.viewport_shade = 'RENDERED'
        context.window_manager.modal_handler_add(self)
        init[0] = True
        return {'RUNNING_MODAL'}
        """
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}
        """
    
class TicTacToeOperator(bpy.types.Operator):
    bl_idname = "view3d.modal_operator_tictactoe_restart"
    bl_label = "Tic Tac Toe Operator Restart"
    bl_options = {'INTERNAL'}
        
    def execute(self, context):
        if game[0]:
            game[0].start()
        return {'FINISHED'}

class TicTacToeGame(object):

    NONE = 0
    
    PLAYER = 1
    COMPUTER = 2

    # filling factor for drawing items into cells
    FACTOR = 0.8
    EMPTY_FACTOR = (1.0 - FACTOR)/2.0

    # scale factor for the board into the viewport
    BOARD_FACTOR = 0.8

    COLOR_BOARD = (1.0, 1.0, 1.0)
    COLOR_FONT = (1.0, 1.0, 1.0)
    COLOR_X = (1.0, 0.0, 0.0)
    COLOR_O = (0.0, 0.0, 1.0)

    LINES = [
        [0, 0, 1, 0, 2, 0],
        [0, 1, 1, 1, 2, 1],
        [0, 2, 1, 2, 2, 2],
        [0, 0, 0, 1, 0, 2],
        [1, 0, 1, 1, 1, 2],
        [2, 0, 2, 1, 2, 2],
        [0, 0, 1, 1, 2, 2],
        [0, 2, 1, 1, 2, 0]]

    def __init__(self):
        self.region_id = 0
        self.mouse_coords = None
        self.start()

    def start(self):
        self.region_id = bpy.context.region.id
        self.mouse_coords = None
        self.round = choice((self.PLAYER, self.COMPUTER))
        self.computer_has_x = choice((True, False))
        self.board = [[self.NONE for i in range(3)] for i in range(3)]
        self.index = 0
        self.winner = self.NONE

    def next(self, context):
        # needed??
        if context.region.id == self.region_id:
            if self.round == self.PLAYER:
                if self.mouse_coords:
                    x, y = self.mouse_coords
                    
                    w = context.region.width
                    h = context.region.height

                    i, j = self.coordsToCell(x, y, w, h)

                    if i != -1:
                        self.playPlayer(i, j)


            elif self.round == self.COMPUTER:
                self.playComputer()
                self.mouse_coords = None
                    
            self.checkWins()

            if self.winner != self.NONE:
                self.round = self.NONE
            elif self.index == 9:
                self.round = self.NONE

    def finish(self):
        end[0] = True

    def render(self, context):
        # needed???
        if context.region.id == self.region_id:
            # just hide the cursor...
            context.space_data.cursor_location = [0.0, 0.0, 10.0]
            context.space_data.region_3d.view_matrix = Matrix.Identity(4)
            
            w = context.region.width
            h = context.region.height
            
            x1, x2, x3, x4, y1, y2, y3, y4 = self.grid(w, h)
                       
            bgl.glMatrixMode(bgl.GL_PROJECTION)
            bgl.glLoadIdentity()
            bgl.gluOrtho2D(0, w, 0, h)
            bgl.glMatrixMode(bgl.GL_MODELVIEW)
            bgl.glLoadIdentity()
            
            bgl.glColor3f(*self.COLOR_BOARD)
            bgl.glLineWidth(2.0)
            bgl.glBegin(bgl.GL_LINES)
            for x in (x1, x2, x3, x4):
                bgl.glVertex3f(x, y1, 0.0)
                bgl.glVertex3f(x, y4, 0.0)
            for y in (y1, y2, y3, y4):
                bgl.glVertex3f(x1, y, 0.0)
                bgl.glVertex3f(x4, y, 0.0)
            bgl.glEnd()

            xs = (x1, x2, x3, x4)
            ys = (y1, y2, y3, y4)
            
            bgl.glLineWidth(8.0)
            bgl.glBegin(bgl.GL_LINES)
            for i in range(3):
                for j in range(3):
                    c = self.board[i][j]
                    xa = xs[i]
                    xb = xs[i + 1]
                    ya = ys[j]
                    yb = ys[j + 1]

                    if c == self.PLAYER:
                        if self.computer_has_x:
                            self.drawO(xa, xb, ya, yb)
                        else:
                            self.drawX(xa, xb, ya, yb)
                    elif c == self.COMPUTER:
                        if self.computer_has_x:
                            self.drawX(xa, xb, ya, yb)
                        else:
                            self.drawO(xa, xb, ya, yb)
            bgl.glEnd()

            bgl.glLineWidth(1.0)
            bgl.glColor3f(*self.COLOR_FONT)

            xp, yp = self.fontPosition(w, h)
            blf.position(0, xp, yp, 0)
            blf.size(0, 50, 72)

            if self.winner == self.COMPUTER:
                blf.draw(0, "You loose!")

            elif self.winner == self.PLAYER:
                blf.draw(0, "You win!")

            elif self.round == self.NONE:
                blf.draw(0, "Draw.")

    def drawO(self, xa, xb, ya, yb):
        bgl.glColor3f(*self.COLOR_O)
        r = xb - xa
        bgl.glVertex3f(xa + r*self.EMPTY_FACTOR, (ya + yb)/2.0, 0.0)
        bgl.glVertex3f((xa + xb)/2.0, yb - r*self.EMPTY_FACTOR, 0.0)
        bgl.glVertex3f((xa + xb)/2.0, yb - r*self.EMPTY_FACTOR, 0.0)
        bgl.glVertex3f(xb - r*self.EMPTY_FACTOR, (ya + yb)/2.0, 0.0)
        bgl.glVertex3f(xb - r*self.EMPTY_FACTOR, (ya + yb)/2.0, 0.0)
        bgl.glVertex3f((xa + xb)/2.0, ya + r*self.EMPTY_FACTOR, 0.0)
        bgl.glVertex3f((xa + xb)/2.0, ya + r*self.EMPTY_FACTOR, 0.0)
        bgl.glVertex3f(xa + r*self.EMPTY_FACTOR, (ya + yb)/2.0, 0.0)

    def drawX(self, xa, xb, ya, yb):
        bgl.glColor3f(*self.COLOR_X)
        r = xb - xa
        bgl.glVertex3f(xa + r*self.EMPTY_FACTOR, ya + r*self.EMPTY_FACTOR, 0.0)
        bgl.glVertex3f(xb - r*self.EMPTY_FACTOR, yb - r*self.EMPTY_FACTOR, 0.0)
        bgl.glVertex3f(xa + r*self.EMPTY_FACTOR, yb - r*self.EMPTY_FACTOR, 0.0)
        bgl.glVertex3f(xb - r*self.EMPTY_FACTOR, ya + r*self.EMPTY_FACTOR, 0.0)

    def coordsToCell(self, x, y, w, h):
        x1, x2, x3, x4, y1, y2, y3, y4 = self.grid(w, h)

        for i0, x0 in enumerate((x1, x2, x3, x4)):
            if x <= x0:
                i = i0 - 1
                break
        else:
            i = -1
            
        for j0, y0 in enumerate((y1, y2, y3, y4)):
            if y <= y0:
                j = j0 - 1
                break
        else:
            j = -1

        if i == -1 or j == -1:
            i = -1
            j = -1
        
        return i, j

    def grid(self, w, h):
        wh_min = min(w, h)

        cx = w/2.0
        cy = h/2.0
        r = wh_min/2.0

        x1 = cx - r*self.BOARD_FACTOR
        x4 = cx + r*self.BOARD_FACTOR

        y1 = cy - r*self.BOARD_FACTOR
        y4 = cy + r*self.BOARD_FACTOR

        x2 = x1 + (x4 - x1)/3.0
        y2 = y1 + (y4 - y1)/3.0
        x3 = x4 + (x1 - x4)/3.0
        y3 = y4 + (y1 - y4)/3.0

        return x1, x2, x3, x4, y1, y2, y3, y4

    def fontPosition(self, w, h):
        wh_min = min(w, h)

        cx = w/2.0
        cy = h/2.0
        r = wh_min*self.BOARD_FACTOR/2.0

        x = cx - r
        y = (cy - r)/3.0

        return x, y

    def playPlayer(self, i, j):
        if self.board[i][j] == self.NONE:
            self.board[i][j] = self.PLAYER
            self.round = self.COMPUTER
            self.index += 1
        else:
            self.mouse_coords = None

    def playComputer(self):
        """
        ### XXX TEMP
        found = False
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == self.NONE:
                    self.board[i][j] = self.COMPUTER
                    found = True
                    break
            if found:
                break

        self.round = self.PLAYER
        self.index += 1"""

        x = -1
        y = -1

        for x1, y1, x2, y2, x3, y3 in self.LINES:
            if (self.board[x1][y1]
                == self.board[x2][y2]
                == self.COMPUTER
                and self.board[x3][y3]
                == self.NONE):
                x = x3
                y = y3
                break
            elif (self.board[x1][y1]
                == self.board[x3][y3]
                == self.COMPUTER
                and self.board[x2][y2]
                == self.NONE):
                x = x2
                y = y2
                break
            elif (self.board[x3][y3]
                == self.board[x2][y2]
                == self.COMPUTER
                and self.board[x1][y1]
                == self.NONE):
                x = x1
                y = y1
                break

        else:
            for x1, y1, x2, y2, x3, y3 in self.LINES:
                if (self.board[x1][y1]
                    == self.board[x2][y2]
                    == self.PLAYER
                    and self.board[x3][y3]
                    == self.NONE):
                    x = x3
                    y = y3
                    break
                elif (self.board[x1][y1]
                    == self.board[x3][y3]
                    == self.PLAYER
                    and self.board[x2][y2]
                    == self.NONE):
                    x = x2
                    y = y2
                    break
                elif (self.board[x3][y3]
                    == self.board[x2][y2]
                    == self.PLAYER
                    and self.board[x1][y1]
                    == self.NONE):
                    x = x1
                    y = y1
                    break

        if x == -1:
            while x == -1:
                i = choice(range(3))
                j = choice(range(3))
                if self.board[i][j] == self.NONE:
                    x = i
                    y = j

        self.board[x][y] = self.COMPUTER
        self.round = self.PLAYER
        self.index += 1

    def checkWins(self):
        # we could check only changed items
        # would probably be more complicated, this check is not that hard...
        for x1, y1, x2, y2, x3, y3 in self.LINES:
            if (self.board[x1][y1]
                == self.board[x2][y2]
                == self.board[x3][y3]
                != self.NONE):
                self.winner = self.board[x1][y1]
                break

"""
class TicTacToeBootstrapOperator(bpy.types.Operator):
    bl_idname = "view3d.modal_operator_tictactoe_bootstrap"
    bl_label = "Tic Tac Toe Bootstrap Operator"
    bl_options = {'INTERNAL'}

    def modal(self, context, event):
        if event.type == 'TIMER' and game[0]:
            print()
            print(context.region)
            if context.space_data and context.space_data.type == 'VIEW_3D':
                print(context.region.id)
                if context.region.id == game.region_id:
                    bpy.ops.view3d.modal_operator_tictactoe('INVOKE_DEFAULT')
                    return {'FINISHED'}
        return {'PASS_THROUGH'}
        
    def invoke(self, context, event):
        context.window_manager.event_timer_add(0.1, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}"""
"""
def addBootstrap(dummy):
    if not init[0]:
        init[0] = True
        bpy.ops.view3d.modal_operator_tictactoe('INVOKE_REGION_WIN')#_bootstrap
        # strange... doesn't seem to work...
        #so use silly init[0] security...
        if addBootstrap in bpy.app.handlers.scene_update_pre:
            bpy.app.handlers.scene_update_pre.remove(addBootstrap)
"""



def displayTicTacToeOps(self, context):
    layout = self.layout

    if context.scene.render.engine == TicTacToePlay.bl_idname:
        if init[0]:
            layout.operator("view3d.modal_operator_tictactoe_restart", icon='FILE_REFRESH', text="Restart")
        else:
            layout.operator("view3d.modal_operator_tictactoe", icon='PLAY', text="Start")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_HT_header.prepend(displayTicTacToeOps)
    
    
def unregister():
    if game[0]:
        game[0].finish()
    bpy.types.VIEW3D_HT_header.remove(displayTicTacToeOps)
    bpy.utils.unregister_module(__name__)
    

if __name__ == "__main__":
    register()
