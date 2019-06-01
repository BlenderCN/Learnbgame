# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# Some of the code is from Michel Anders's script "Floor Generator"
# I couldn't figure by myself how to update the mesh :( Thanks to him !
 
bl_info = {
    "name": "Plancher",
    "author": "Cédric Brandin",
    "version": (0, 0, 31),
    "blender": (2, 72, 0),
	  "location": "",
    "description": "Create a floor board",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import math 
import bpy
import bmesh
from bpy.props import IntProperty, FloatProperty, BoolProperty, FloatVectorProperty, EnumProperty
from mathutils import Vector, Euler, Matrix
from random import random as rand, seed, uniform as randuni, randint

#############################################################
# COMPUTE THE LENGTH OF THE BOARD AFTER THE TILT
#############################################################
# The 'Tilt' is not a rotation.  
# It's a translation of the two first vertex on X axis (translatex)
# and a translation of the two ending vertex on the Y axis (translatey) 
# This will distord the board. So, to keep the end shape and the length
# I compute the end shape's opposite (1) then the hypotenuse (3) 
# using the width (2) and the angle (offsetx) from the Pythagoras Theorem (yeaah trigonometry !)
# Then, I compute the new length of the board (translatex)   
#     1
#   *---*-----------------------           |   *----*
#   |  /                                   |    \    \
# 2 | / 3                                  V     \    \
#   |/                                 translatey \    \
#   *---------------------------                   *----*  ---> translatex

def calculangle(left, end, tilt, start, width, lengthboard):

    opposite = width * math.tan(tilt)                                
    hyp = math.sqrt(width ** 2 + opposite ** 2)                        
    translatex = lengthboard * math.sin(tilt)                          
    translatey = math.sqrt((lengthboard ** 2) - (translatex ** 2))       
    
    return (hyp, translatex, translatey)

#############################################################
# BOARD 
#############################################################
# Mesh of the board.
# If the boards are tilt, we need to inverse the angle each time we call this function :
# /\/\/ -> So each board will be upside-down compared to each other
def board(start, left, right, end, tilt, translatex, hyp, herringbone, gapy, height, randheight):
    
    gapx = 0
    height = randheight * randuni(0, height)                              # Add randomness to the height of the boards  
    if not herringbone: gapy = 0
    
    if tilt > 0:                                                          # / / / -> 1 board, 3 board, 5 board...               
        shiftdown = translatex     
        shiftup = 0                
        if herringbone:            
            gapy = gapy / 2        
            gapx = 0               
            
    else:                                                                 #  \ \ \-> 2 board, 4 board, 6 board...
        shiftdown = 0              
        shiftup = -translatex      
        if herringbone:            
            gapy = gapy / 2        
            gapx = gapy * 2        
                                   
    dl = Vector((left + shiftdown + gapx, start - gapy, height))          # down left [0,0,0]
    dr = Vector((right + shiftdown + gapx, start - gapy, height))         # down right [1,0,0]
    ur = Vector((right - shiftup + gapx, end - gapy, height))             # up right [1,1,0]
    ul = Vector((left - shiftup + gapx, end - gapy, height))              # up left [0,1,0]

    if herringbone:
        if tilt > 0:                                                      # / / / -> 1 board, 3 board, 5 board... 
            ur[0] = ur[0] - (hyp / 2) 
            ur[1] = ur[1] + (hyp / 2) 
            dr[0] = dr[0] - (hyp / 2)
            dr[1] = dr[1] + (hyp / 2)
        else:                                                             #  \ \ \-> 2 board, 4 board, 6 board...
            dl[0] = dl[0] + (hyp / 2)
            dl[1] = dl[1] + (hyp / 2) 
            ul[0] = ul[0] + (hyp / 2) 
            ul[1] = ul[1] + (hyp / 2) 

    verts = (dl, ul, ur, dr)
   
    return (verts)

#############################################################
# TRANSVERSAL
#############################################################
# Creation of the boards in the interval.
# --    -> tilt > 0 : No translation on the x axis
# \\
#  --   -> tilt < 0 : Translation on the x axis to follow the tilted boards
# //

def transversal(left, right, start, tilt, translatex, gapy, gapx, gaptrans, randgaptrans, end, nbrtrans, verts, faces, locktrans, lengthtrans, height, randheight, borders, endfloor, shifty):
    gaptrans = gaptrans + (randgaptrans * randuni(0, gaptrans))           # Add randomness to the gap of the transversal of the boards
    if borders: nbrtrans = 1                                              # Constrain the transversal to 1 board if borders activate
    if gaptrans < (end-start)/(nbrtrans+1):                               # The gap can't be > to the width of the interval
        x = 0
        lengthint = 0
        if tilt > 0: translatex = 0                                       # Constrain the board to 0 on the x axis 
        width = ((end - start) - (gaptrans * (nbrtrans + 1))) * (1 / nbrtrans)# Width of 1 board in the interval
        startint = start + gaptrans                                       # Find the start of the first board
        while right > lengthint:                                          # While the transversal is < to the right edge of the floor (if unlock) or the board (if locked)
            if locktrans:                                                 # If the length of the transversal is unlock
                lengthint += lengthtrans                                  # Add the length 

            if not locktrans or (lengthint > right): lengthint = right    # Constrain the length of the transversal to th length of the board (locked) 

            while x < nbrtrans:                                           # Nbr of boards in the transversal
                x += 1 
                endtrans = startint + width                               # Find the end of the board

                # Create the boards in the interval
                nbvert = len(verts) 
                verts.extend(interval(left, lengthint, startint, translatex, gapy, endtrans, height, randheight, width, gapx, gaptrans, borders, endfloor, tilt, shifty))
                if shifty == 0 and borders and tilt == 0:
                    faces.append((nbvert, nbvert+1, nbvert+2, nbvert+3, nbvert+4, nbvert+5))
                else :
                    faces.append((nbvert, nbvert+1, nbvert+2, nbvert+3))
                startint = endtrans + gaptrans                            # Find the start of the next board

            #------------------------------------------------------------
            # Increment / initialize
            #------------------------------------------------------------
            if locktrans:
                left = lengthint + gaptrans
                lengthint += gaptrans
                x = 0
                endtrans = start + width
                startint = start + gaptrans
            
            # The boards can't be > to the length of the floor
            if left > right:
                lengthint = left


#############################################################
# INTERVAL
#############################################################
# Creation of 1 transversal 

def interval(left, right, start, translatex, gapy, end, height, randheight, width, gapx, gaptrans, borders, endfloor, tilt, shifty):
    height = randheight * randuni(0, height)                              # Add randomness to the height of the boards
    if gaptrans == gapx: bgap = 0
    else: bgap = gaptrans
    if shifty == 0 and borders and tilt == 0:
        tipleft = left-gapx/2+bgap
        tipright = right+gapx/2-bgap
        if tipleft < 0: tipleft = 0                                       # Constrain the first left tip to 0...
        elif tipleft > left: tipleft = left                               # ...and the other to the left of the board
        if tipright < right: tipright = right                             # Constrain the right tips to the right of the board.. 
        if endfloor > 0 : tipright = endfloor                             # ...and the last one to the last board of the floor
        dr = Vector((right, start, height))                               # Down right
        dl = Vector((left, start, height))                                # Down left
        tl = Vector((tipleft, start+(width/2), height))                   # Tip left
        ul = Vector((left, end, height))                                  # Up left
        ur = Vector((right, end, height))                                 # Up right
        tr = Vector((tipright, start+(width/2), height))                  # Tip right

        verts = (dr, dl, tl, ul, ur, tr)

    else:
        dr = Vector((right + translatex, start, height))                  # Down right
        dl = Vector((left + translatex, start, height))                   # Down left
        ul = Vector((left + translatex, end, height))                     # Up left
        ur = Vector((right + translatex, end, height))                    # Up right
        
        verts = (dl, ul, ur, dr)
        
    return verts

#############################################################
# BORDERS
#############################################################
# Creation of the borders 

def border(left, right, start, gapy, end, height, randheight, gaptrans, randgaptrans, lengthparquet, translatey):
    height = randheight * randuni(0, height)                              # Add randomness to the height of the boards
    gaptrans = gaptrans + (randgaptrans * randuni(0, gaptrans))
    tdogapy = gapy
    tupgapy = gapy
    if end+tupgapy > lengthparquet: tupgapy = (lengthparquet - end)
    tipdown = start-tdogapy/2+gaptrans
    tipup = end+tupgapy/2-gaptrans
    if tipup < end: tipup = end
    if tipdown < 0 : tipdown = 0
    elif tipdown > start: tipdown = start
    td = Vector(((left + right) /2, tipdown, height))                     # Tip down 
    tdl = Vector((left, start, height))                                   # Tip down left
    tup = Vector((left, end, height))                                     # Tip up left
    tu = Vector(((left + right) /2, tipup, height))                       # Tip up
    tur = Vector((right, end, height))                                    # Tip up right
    tdr = Vector((right, start, height))                                  # Tip down right        

    verts = (td, tdl, tup, tu, tur, tdr)
    
    return verts

#############################################################
# FLOOR BOARD
#############################################################
# Creation of a column of boards

def parquet(switch, nbrboards, height, randheight, width, randwith, gapx, lengthboard, gapy, shifty, nbrshift, tilt, herringbone, randoshifty, lengthparquet, trans, gaptrans, randgaptrans, glue, borders, lengthtrans, locktrans, nbrtrans):

    x = 0
    y = 0
    verts = []
    faces = []
    listinter = []
    start = 0
    left = 0
    bool_translatey = True                                                # shifty = 0                                                             
    end = lengthboard                                                                                                                              
    interleft = 0                                                                                                                                  
    interright = 0                                                                                                                                 
    if locktrans: 
        shifty = 0                                                        # No shift with unlock !
        glue = False
        borders = False
    if shifty: locktrans = False                                          # Can't have the boards shifted and the tranversal unlocked              
    if herringbone : switch = True                                        # Constrain the computation of the length using the boards if herringbone
    if randoshifty > 0:                                                   # If randomness in the shift of the boards
        randomshift = shifty * (1-randoshifty)                            # Compute the amount of randomness in the shift
    else:
        randomshift = shifty                                              # No randomness
        
    if shifty > 0: 
        tilt = 0
        herringbone = False

    if gapy == 0:                                                         # If no gap on the Y axis : the transversal is not possible
        trans = False

    if herringbone:                                                       # Constraints if herringbone is choose :
        shifty = 0                                                        # - no shift
        tilt = math.radians(45)                                           # - Tilt = 45°
        randwith = 0                                                      # - No random on the width
        trans = False                                                     # - No transversal
    
    # Compute the new length and width of the board if tilted
    hyp, translatex, translatey = calculangle(left, end, tilt, start, width, end)
    
    randwidth = hyp + (randwith * randuni(0, hyp))                        # Randomness in the width
    right = randwidth                                                     # Right = width of the board
    end = translatey - (translatey * randuni(randomshift, shifty))        # Randomness in the length

    if herringbone or switch:                                             # Compute the length of the floor based on the length of the boards
        lengthparquet = ((round(lengthparquet / (translatey + gapy))) * (translatey + gapy)) - gapy
    noglue = gapx           
    #------------------------------------------------------------
    # Loop for the boards on the X axis
    #------------------------------------------------------------
    while x < nbrboards:                                                  # X axis 
        x += 1   

        if glue and (x % nbrshift != 0): gapx = gaptrans
        else: gapx = noglue


        if (x % nbrshift != 0): bool_translatey = not bool_translatey     # Invert the shift 
        if end > lengthparquet :                                          # Cut the last board if it's > than the floor
            end = lengthparquet

        # Creation of the first board
        nbvert = len(verts)
        verts.extend(board(start, left, right, end, tilt, translatex, hyp, herringbone, gapy, height, randheight))
        faces.append((nbvert,nbvert+1, nbvert+2, nbvert+3))
        
        # Start a new column (Y)
        start2 = end + gapy
        end2 = start2 
        #------------------------------------------------------------
        # TRANSVERSAL
        #------------------------------------------------------------
        # listinter = List of the length (left) of the interval || x = nbr of the actual column || nbrshift = nbr of columns to shift || nbrboards = Total nbr of column 
        # The modulo (%) is here to determined if the actual interval as to be shift        
        listinter.append(left)                                            # Keep the length of the actual interval
        endfloor = 0
        if x == nbrboards: endfloor = right
        if trans and ((x % nbrshift == 0) or ((x % nbrshift != 0) and (x == nbrboards))) and (end < lengthparquet) and not locktrans:
            if start2 > lengthparquet: start2 = lengthparquet             # Cut the board if it's > than the floor
            transversal(listinter[0], right, end, tilt, translatex, gapy, noglue, gaptrans, randgaptrans, start2, nbrtrans, verts, faces, locktrans, lengthtrans, height, randheight, borders, endfloor, shifty)
        elif trans and (x == nbrboards) and locktrans:
            if start2 > lengthparquet: start2 = lengthparquet             # Cut the board if it's > than the floor
            transversal(listinter[0], right, end, tilt, translatex, gapy, noglue, gaptrans, randgaptrans, start2, nbrtrans, verts, faces, locktrans, lengthtrans, height, randheight, borders, endfloor, shifty)
            
        #------------------------------------------------------------
        # BORDERS
        #------------------------------------------------------------
        # Create the borders in the X gap if boards are glued
        if borders and glue and (x % nbrshift == 0) and translatex == 0 and (x != nbrboards) and (shifty == 0) and (gaptrans*2 < gapx): 
            nbvert = len(verts) 
            verts.extend(border(right+gaptrans, right+noglue-gaptrans, start, gapy, end, height, randheight, gaptrans, randgaptrans, lengthparquet, start2 + translatey))
            faces.append((nbvert, nbvert+1, nbvert+2, nbvert+3, nbvert+4, nbvert+5))

        #------------------------------------------------------------
        # Loop for the boards on the Y axis
        #------------------------------------------------------------
        while lengthparquet > end2 :                                      # Y axis
            end2 = start2 + translatey                                    # New column
            if end2 > lengthparquet :                                     # Cut the board if it's > than the floor
                end2 = lengthparquet

            if tilt < 0:                                                  # This part is used to inversed the tilt of the boards 
                tilt = tilt * (-1)                                         
            else:
                tilt = -tilt

            # Creation of the board
            nbvert = len(verts)
            verts.extend(board(start2, left, right, end2, tilt, translatex, hyp, herringbone, gapy, height, randheight))
            faces.append((nbvert,nbvert+1, nbvert+2, nbvert+3))

            #------------------------------------------------------------
            # BORDERS
            #------------------------------------------------------------
            # Create the borders in the X gap if boards are glued
            if borders and glue and (x % nbrshift == 0) and translatex == 0 and (x != nbrboards) and (shifty == 0) and (gaptrans*2 < gapx):  
                nbvert = len(verts) 
                verts.extend(border(right+gaptrans, right+noglue-gaptrans, start2, gapy, end2, height, randheight, gaptrans, randgaptrans, lengthparquet, start2 + translatey))
                faces.append((nbvert, nbvert+1, nbvert+2, nbvert+3, nbvert+4, nbvert+5))

            # New column 
            start2 += translatey + gapy
            
            #------------------------------------------------------------
            # TRANSVERSAL
            #------------------------------------------------------------
            # x = nbr of the actual column || nbrshift = nbr of columns to shift || nbrboards = Total nbr of column 
            # The modulo (%) is  here to determined if the actual interval as to be shift  
            endfloor = 0
            if x == nbrboards: endfloor = right            
            if trans and ((x % nbrshift == 0) or ((x % nbrshift != 0) and (x == nbrboards))) and (end2 < lengthparquet) and not locktrans:
                if start2 > lengthparquet: start2 = lengthparquet         # Cut the board if it's > than the floor
                transversal(listinter[0], right, end2, tilt, translatex, gapy, noglue, gaptrans, randgaptrans, start2, nbrtrans, verts, faces, locktrans, lengthtrans, height, randheight, borders, endfloor, shifty)

            elif trans and locktrans and (x == nbrboards) and (end2 < lengthparquet) :
                if start2 > lengthparquet: start2 = lengthparquet         # Cut the board if it's > than the floor
                transversal(listinter[0], right, end2, tilt, translatex, gapy, noglue, gaptrans, randgaptrans, start2, nbrtrans, verts, faces, locktrans, lengthtrans, height, randheight, borders, endfloor, shifty)

            end2 = start2                                                 # End of the loop on Y axis
        #------------------------------------------------------------#
                                                         
        #------------------------------------------------------------
        # Increment / initialize                                      
        #------------------------------------------------------------ 
        if (x % nbrshift == 0) and not locktrans: listinter = []          # Initialize the list of interval if the nbr of boards to shift is reaches        
        if not herringbone:                                               # If not herringbone 
            left += gapx                                                  #  Add the value of gapx to the left side of the boards 
            right += gapx                                                 #  Add the value of gapx to the right side of the boards
        else:                                                             # If herringbone, we don't use the gapx anymore in the panel  
            right += gapy * 2                                             #  used only the gapy                              
            left += gapy * 2                                              #  ""     ""      ""                               
        left += randwidth                                                 # Add randomness on the left side of the boards  
        randwidth = hyp + (randwith * randuni(0, hyp))                    # Compute the new randomness on the width (hyp)
        right += randwidth                                                # Add randomness on the right side of the boards 
        #------------------------------------------------------------#
        
        #------------------------------------------------------------
        # Shift on the Y axis
        #------------------------------------------------------------
        # bool_translatey is turn on and off at each new column to reverse the direction of the shift up or down.
        if (bool_translatey and shifty > 0):                              # If the columns are shifted
            if (x % nbrshift == 0 ):                                      # If the nbr of column to shift is reach 
                end = translatey * randuni(randomshift, shifty)           # Compute and add the randomness to the new end (translatey) shifted 
            bool_translatey = False                                       # Turn on the boolean, so it will be inverted for the next colmun
        else:
            if (x % nbrshift == 0 ):
                end = translatey - (translatey * randuni(randomshift, shifty)) # Compute and add the randomness to the new end (translatey) shifted
            bool_translatey = True                                        # Turn on the boolean, so it will be inverted for the next colmun
        #------------------------------------------------------------#

        #------------------------------------------------------------
        # Herringbone only
        #------------------------------------------------------------                
        # Invert the value of the tilted parameter
        if tilt < 0:                                                      # The tilted value is inverted at each column
           tilt = tilt * (-1)                                             # so the boards will be reverse
        #------------------------------------------------------------#

    #------------------------------------------------------------         # End of the loop on X axis
    return verts, faces

#############################################################
# PANEL PRINCIPAL
#############################################################
class PlancherPanel(bpy.types.Panel):
    bl_idname = "mesh.plancher"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Plancher"
    bl_label = "Plancher"

    #------------------------------------------------------------
    # PANEL 
    #------------------------------------------------------------
    def draw(self, context):
        layout = self.layout
        myObj = bpy.context.active_object
        col = layout.column()
        cobj = context.object
        if not myObj or myObj.name != 'Plancher' :
            layout.operator('mesh.ajout_primitive') 
        
        if bpy.context.mode == 'EDIT_MESH':
            col = layout.column()
            col = layout.column()      
            col.label(text="Vertex / UV")    
            col = layout.column(align=True)
            #Vertex Color
            if cobj.colphase == 0:
                row = col.row(align=True)
                row.prop(cobj, "colrand")
            if cobj.colrand > 0:
                row = col.row(align=True) 
                row.prop(cobj, "allrandom", text='All random', icon='BLANK1')
            #Phase Color
            if cobj.colrand == 0:
                row = col.row(align=True) 
                row.prop(cobj, "colphase")

            #Seed color
            row = col.row(align=True) 
            row.prop(cobj, "colseed")            
            #layout.label('Plancher only works in Object Mode.')
        elif myObj and myObj.name == 'Plancher'  :
            #-------------------------------------------------------------FLOOR
            col = layout.column(align=True)
            col.label(text="SURFACE")            
            row = col.row(align=True)
            row.prop(cobj, "switch", icon='BLANK1')
            row = col.row(align=True)
            row.prop(cobj, "nbrboards")
            row.prop(cobj, "lengthparquet")
            row = col.row(align=True)         
            row.prop(cobj, "height")
            row.prop(cobj, "randheight")   

            col = layout.column()
            col = layout.column(align=True)       

            #-------------------------------------------------------------BOARDS
            col.label(text="BOARD")
            row = col.row(align=True)
            row.prop(cobj, "lengthboard")
            row.prop(cobj, "width")
            row = col.row(align = True)
            row.prop(cobj, "randwith", text="Random", slider=True)
            
            col = layout.column()
            col = layout.column(align=True)    
            
            #-------------------------------------------------------------GAP 
            if cobj.herringbone == False:       
                col.label(text="GAP")                        
                row = col.row(align=True)                    
                row.prop(cobj, "gapx")                   
                row.prop(cobj, "gapy")                       
                if cobj.gapy > 0:                            
                                                      
            #-------------------------------------------------------------TRANSVERSAL     
                    row = col.row(align=True)
                    if not cobj.locktrans:
                        row.prop(cobj, "shifty")
                        row.prop(cobj, "randoshifty")
                        row = col.row(align=True)
                        row.prop(cobj, "nbrshift")

                    col = layout.column(align=True)  
                    col.label(text="INTERVAL")                        
                    col = layout.column(align=True)
                    row = col.row(align=True)
                    row.prop(cobj, "trans", text='Interval', icon='BLANK1')
                    if cobj.trans:
                        row.prop(cobj, "locktrans", text='Unlock', icon='BLANK1')
                        row = col.row(align=True)
                        if cobj.locktrans: row.prop(cobj, "lengthtrans")
                        else: row.prop(cobj, "nbrshift", text='Column')
                        row.prop(cobj, "nbrtrans", text='Row')
                    if (cobj.trans or cobj.glue):
                        row = col.row(align=True)
                        row.prop(cobj, "gaptrans")
                        row.prop(cobj, "randgaptrans")
                    row = col.row(align=True)
                    if not cobj.locktrans:
                        row.prop(cobj, "glue", text='Glue', icon='BLANK1')
                        if cobj.glue:
                            row.prop(cobj, "borders", text='Borders', icon='BLANK1')                    

            #-------------------------------------------------------------CHEVRON / HERRINGBONE
                                
            if cobj.shifty == 0 :
                if cobj.herringbone == False:
                    col = layout.column()
                    col = layout.column(align=True)      
                    col.label(text="CHEVRON")    
                    row = col.row(align=True)
                    row.prop(cobj, "tilt")             
                
                if cobj.herringbone == True: 
                    col = layout.column()
                    col = layout.column(align=True)              
                    row = col.row(align=True) 
                    row.prop(cobj, "gapy")
                    self.switch = True                            

                row = col.row(align=True) 
                row.prop(cobj, "herringbone", text='Herringbone', icon='BLANK1')
                
            #-------------------------------------------------------------SEED
            col = layout.column()   
            col = layout.column(align=True)
            col.label(text="SEED")    
            row = col.row(align=True)
            row.prop(cobj, "colseed")            

            #-------------------------------------------------------------UV / VERTEX
            # Warning, 'cause all the parameters are lost when going back to Object mode...
            # Have to do something with this. 
            col = layout.column()
            col = layout.column() 
            col = layout.column(align=True)     
            col.label(text="Go in edit mode for UV !")    
            col.label(text="Warning ! Any change here will reset the uv/color !")    

#############################################################
# FUNCTION PLANCHER
#############################################################
def create_plancher(self,context):
    bpy.context.user_preferences.edit.use_global_undo = False
    obj_mode = bpy.context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')  
    bpy.context.scene.unit_settings.system = 'METRIC'
    cobj = context.object
    verts, faces = parquet(cobj.switch,
                           cobj.nbrboards,
                           cobj.height,
                           cobj.randheight,
                           cobj.width,
                           cobj.randwith,
                           cobj.gapx,
                           cobj.lengthboard,
                           cobj.gapy,
                           cobj.shifty,
                           cobj.nbrshift,
                           cobj.tilt,
                           cobj.herringbone,
                           cobj.randoshifty,
                           cobj.lengthparquet,
                           cobj.trans,
                           cobj.gaptrans,
                           cobj.randgaptrans,
                           cobj.glue,
                           cobj.borders,
                           cobj.lengthtrans,
                           cobj.locktrans,
                           cobj.nbrtrans,)
    
    # Code from Michel Anders script Floor Generator
    # Create mesh & link object to scene
    emesh = cobj.data

    mesh = bpy.data.meshes.new("Plancher_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)

    for i in bpy.data.objects:
        if i.data == emesh:
            i.data = mesh
    
    name = emesh.name
    emesh.user_clear()
    bpy.data.meshes.remove(emesh)
    mesh.name = name

    #---------------------------------------------------------------------COLOR & UV 
    if obj_mode =='EDIT':                                                 # If we are in 'EDIT MODE'
        seed(cobj.colseed)                                            # New random distribution
        mesh.uv_textures.new("Txt_Plancher")                          # New UV map
        vertex_colors = mesh.vertex_colors.new().data                 # New vertex color
        rgb = []

        if cobj.colrand > 0:                                          # If random color
            for i in range(cobj.colrand):
                color = [round(rand(),1), round(rand(),1), round(rand(),1)] # Create as many random color as in the colrand variable
                rgb.append(color)                                     # Keep all the colors in the RGB variable

        elif cobj.colphase > 0:                                       # If phase color 
            for n in range(cobj.colphase):                              
                color = [round(rand(),1), round(rand(),1), round(rand(),1)] # Create as many random color as in the colphase variable  
                rgb.append(color)                                     # Keep all the colors in the RGB variable                 
                
    #---------------------------------------------------------------------VERTEX GROUP
        bpy.context.object.vertex_groups.clear()                      # Clear vertex group if exist
        if cobj.colrand == 0 and cobj.colphase == 0:                  # Create the first Vertex Group
            bpy.context.object.vertex_groups.new()
        elif cobj.colrand > 0:                                        # Create as many VG as random color
            for v in range(cobj.colrand): 
                bpy.context.object.vertex_groups.new()
        elif cobj.colphase > 0:                                       # Create as many VG as phase color
            for v in range(cobj.colphase): 
                bpy.context.object.vertex_groups.new()

    #---------------------------------------------------------------------VERTEX COLOR        
        phase = cobj.colphase
        color = {}
        for poly in mesh.polygons:                                    # For each polygon of the mesh

            if cobj.colrand == 0 and cobj.colphase == 0:              # If no color 
                color = [rand(), rand(), rand()]                      # Create at least one random color

            elif cobj.colrand > 0:                                    # If random color
            
                if cobj.allrandom:                                    # If all random choose
                    nbpoly = len(mesh.polygons.items())               # Number of boards
                    randvg = randint(0,cobj.colrand)                  # Random vertex group
                    for i in range(nbpoly):                           
                        color = [round(rand(),1), round(rand(),1), round(rand(),1)]     # Create as many random color as in the colrand variable
                        rgb.append(color)                             # Keep all the colors in the RGB variable

                else:
                    color = rgb[randint(0,cobj.colrand-1)]            # Take one color ramdomly from the RGB list
                

                for loop_index in poly.loop_indices:                  # For each vertice from this polygon
                    vertex_colors[loop_index].color = color           # Assign the same color
                    if cobj.allrandom:                                # If all random choose
                        vg = bpy.context.object.vertex_groups[randvg-1] # Assign a random vertex group
                    else: 
                        vg = bpy.context.object.vertex_groups[rgb.index(color)] # Else assign a vertex group by color index
                    vg.add([loop_index], 1, "ADD")                    # index, weight, operation

            elif cobj.colphase > 0:                                   # If phase color                          
                color = rgb[phase-1]                                  # Take the last color from the RGB list
                phase -= 1                                            # Substract 1 from the phase number
                if phase == 0: phase = cobj.colphase                  # When phase = 0, start again from the beginning to loop in the rgb list
                                                                      
                for loop_index in poly.loop_indices:                  # For each vertice from this polygon
                    vertex_colors[loop_index].color = color           # Assign the same color
                    vg = bpy.context.object.vertex_groups[rgb.index(color)]
                    vg.add([loop_index], 1, "ADD")                    # index, weight, operation
        color.clear()                                                 # Clear the color list

   
        #-----------------------------------------------------------------UV UNWRAP
        ob = bpy.context.object
        ob.select = True
        bpy.ops.object.mode_set(mode='EDIT') 
        bpy.ops.uv.unwrap(method='ANGLE_BASED', correct_aspect=True)       
        #-----------------------------------------------------------------UV LAYER
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        uv_lay = bm.loops.layers.uv.verify()
        
        #-----------------------------------------------------------------GROUP UV 
        # Group all the UV points at the origin point
        # Need more work, it's not working everytimes, don't know why...
        v = 0
        tpuvx = {}
        tpuvy = {}
        for face in bm.faces:                                             # For each polygon
            for loop in face.loops:                                       # For each loop
                luv = loop[uv_lay]
                v += 1
                uv = loop[uv_lay].uv                                      # Keep the coordinate of the uv point
                tpuvx[uv.x] = loop.index                                  # Keep the X coordinate of the uv point
                tpuvy[uv.y] = loop.index                                  # Keep the Y coordinate of the uv point
 
                if v > 3:                                                 # When the last uv point of this polygon is reached
                    minx = min(tpuvx.keys())                              # Keep the smallest value on the X axis from the 4 uv point 
                    miny = min(tpuvy.keys())                              # Keep the smallest value on the Y axis from the 4 uv point
                    for loop in face.loops:                               # A new loop in the loop ... really need more work 
                        loop[uv_lay].uv[0] -= minx                        # For each UV point, substract the value of the smallest X 
                        loop[uv_lay].uv[1] -= miny                        # For each UV point, substract the value of the smallest Y
                    v = 0                                                 # Initialize counter
            tpuvx.clear()                                                 # Clear the list
            tpuvy.clear()                                                 # Clear the list
            
        bmesh.update_edit_mesh(me)                                        # Update the mesh

    else:
        bpy.ops.object.mode_set(mode='OBJECT')                            # We are in 'OBJECT MODE' here, nothing to do
   
    #---------------------------------------------------------------------MODIFIERS
    nbop = len(cobj.modifiers)
    obj = context.active_object
    if nbop == 0:
        obj.modifiers.new('Solidify', 'SOLIDIFY')
        obj.modifiers.new('Bevel', 'BEVEL')
    cobj.modifiers['Solidify'].show_expanded = False
    cobj.modifiers['Solidify'].thickness = self.height
    cobj.modifiers['Bevel'].show_expanded = False
    cobj.modifiers['Bevel'].width = 0.001
    cobj.modifiers['Bevel'].use_clamp_overlap

    bpy.context.user_preferences.edit.use_global_undo = True

#############################################################
# PROPERTIES
#############################################################

    # Switch between length of the board and meters 
bpy.types.Object.switch = BoolProperty(
               name="Switch",
               description="Switch between length of the board and meters",
               default=False,            
               update=create_plancher)  

    # Length of the floor 
bpy.types.Object.lengthparquet = FloatProperty(
               name="Length",
               description="Length of the floor",
               min=0.01, max=10000000.0,
               default=4.0,
               precision=2,
               subtype='DISTANCE',
               update=create_plancher)

    # Number of row
bpy.types.Object.nbrboards = IntProperty(
            name="Count",
            description="Number of row",
            min=1, max=100,
            default=2,
            update=create_plancher)
              
    # Length of a board
bpy.types.Object.lengthboard = FloatProperty(
               name="Length",
               description="Length of a board",
               min=0.01, max=1000000000.0,
               default=2.0,
               precision=2,
               subtype='DISTANCE',
               update=create_plancher)

    # Height of the floor        
bpy.types.Object.height = FloatProperty(
              name="Height",
              description="Height of the floor",
              min=0.01, max=100,
              default=0.01,
              precision=2,
              subtype='DISTANCE',
              update=create_plancher)

    # Add random to the height
bpy.types.Object.randheight = FloatProperty(
               name="Random",
               description="Add random to the height",
               min=0, max=1,
               default=0,
               precision=2,
               subtype='PERCENTAGE',
               unit='NONE',
               step=0.1,
               update=create_plancher)                             
    # Width of a board
bpy.types.Object.width = FloatProperty(
              name="Width",
              description="Width of a board",
              min=0.01, max=100.0,
              default=0.18,
              precision=3,
              subtype='DISTANCE',
              update=create_plancher)

    # Add random to the width         
bpy.types.Object.randwith = FloatProperty(
               name="Random",
               description="Add random to the width",
               min=0, max=1,
               default=0,
               precision=2,
               subtype='PERCENTAGE',
               unit='NONE',
               step=0.1,
               update=create_plancher)

    # Add a gap between the columns (X)
bpy.types.Object.gapx = FloatProperty(
              name="Gap X",
              description="Add a gap between the columns (X)",  
              min=0.00, max=100.0,
              default=0.01,
              precision=2,
              subtype='DISTANCE',
              update=create_plancher)
              
    # Add a gap between the row (Y) (for the transversal's boards)
bpy.types.Object.gapy = FloatProperty(
              name="Gap Y",
              description="Add a gap between the row (Y)",
              min=0.00, max=100.0,
              default=0.01,
              precision=2,
              subtype='DISTANCE',          
              update=create_plancher)
                          
    # Shift the columns
bpy.types.Object.shifty = FloatProperty(
               name="Shift",
               description="Shift the columns",
               min=0, max=1,
               default=0,
               precision=2,
               subtype='PERCENTAGE',
               unit='NONE',
               step=0.1,
               update=create_plancher)

    # Add random to the shift          
bpy.types.Object.randoshifty = FloatProperty(
               name="Random",
               description="Add random to the shift",
               min=0, max=1,
               default=0,
               precision=2,
               subtype='PERCENTAGE',
               unit='NONE',
               step=0.1,
               update=create_plancher)
               
    # Number of column to shift
bpy.types.Object.nbrshift = IntProperty(
            name="Nbr Shift",
            description="Number of column to shift",
            min=1, max=100,
            default=1,
            update=create_plancher)

    # Fill in the gap between the row (transversal)
bpy.types.Object.trans = BoolProperty(
               name=" ",
               description="Fill in the gap between the row",
               default=False,           
               update=create_plancher) 

    # Unlock the length of the transversal
bpy.types.Object.locktrans = BoolProperty(
               name="Unlock",
               description="Unlock the length of the transversal",
               default=False,           
               update=create_plancher)
               
    # Length of the transversal
bpy.types.Object.lengthtrans = FloatProperty(
              name="Length",
              description="Length of the transversal",
              min=0.01, max=100,
              default=2,
              precision=2,
              subtype='DISTANCE',
              update=create_plancher)

    # Number of transversals in the interval
bpy.types.Object.nbrtrans = IntProperty(
            name="Count X",
            description="Number of transversals in the interval",
            min=1, max=100,
            default=1,
            update=create_plancher)

    # Gap between the transversals
bpy.types.Object.gaptrans = FloatProperty(
              name="Gap",
              description="Gap between the transversals",
              min=0.00, max=100,
              default=0.01,
              precision=2,
              subtype='DISTANCE',
              update=create_plancher)

    # Add random to the width         
bpy.types.Object.randgaptrans = FloatProperty(
               name="Random",
               description="Add random to the gap of the transversal",
               min=0, max=1,
               default=0,
               precision=2,
               subtype='PERCENTAGE',
               unit='NONE',
               step=0.1,
               update=create_plancher)
               
    # Glue the boards in the shift parameter 
bpy.types.Object.glue = BoolProperty(
               name="glue",
               description="Glue the boards in the shift parameter",
               default=False,           
               update=create_plancher)

    # Add borders 
bpy.types.Object.borders = BoolProperty(
               name="Borders",
               description="Add borders between the glued boards",
               default=False,           
               update=create_plancher)
                           
    # Tilt the columns
bpy.types.Object.tilt = FloatProperty(
               name="Tilt",
               description="Tilt the columns",
               min= math.radians(0), max= math.radians(70),
               default=0.00,
               precision=2,
               subtype='ANGLE',
               unit='ROTATION',
               step=1,
               update=create_plancher)

    # Floor type Herringbone
bpy.types.Object.herringbone = BoolProperty(
               name="Herringbone",
               description="Floor type Herringbone",
               default=False,            
               update=create_plancher)

    # Random color to the vertex group
bpy.types.Object.colrand = IntProperty(
               name="Random Color",
               description="Random color to the vertex group",
               min=0, max=100,
               default=0,
               update=create_plancher)

    # Orderly color to the vertex group
bpy.types.Object.colphase = IntProperty(
               name="Phase color",
               description="Orderly color to the vertex group",
               min=0, max=100,
               default=0,
               update=create_plancher)

    # New distribution for the random
bpy.types.Object.colseed = IntProperty(
               name="Seed",
               description="New distribution for the random",
               min=0, max=999999,
               default=0,
               update=create_plancher) 

    # Random color for each board
bpy.types.Object.allrandom = BoolProperty(
               name="allrandom",
               description="Make a random color for each board",
               default=False,            
               update=create_plancher)
                              
class AjoutPrimitive(bpy.types.Operator):
	bl_idname = "mesh.ajout_primitive"
	bl_label = "Add a new floor"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.mesh.primitive_cube_add()
		context.active_object.name = "Plancher"
		cobj = context.object
		cobj.nbrboards = 2
		return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)
    
def unregister():
    bpy.utils.unregister_module(__name__)
            
if __name__ == "__main__":
    register()
