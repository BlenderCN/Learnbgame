'''------------------------------------------------------------------

    Description

Create Panel
    add checkboxes and callback functions
    draw properties to panel

------------------------------------------------------------------'''
import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty

# global variables---------------------------------

hW = []
l  = []

obj_string1 = "Dimensional"
obj_string2 = "Lumber"

# this file and vertCollections need all the global variables
# perhaps they should be put in __init__
# how do i pass the variable back and forth

# width
width = .75
wthq =  .375   # nominal 1 inch (.75")
wfq  =  .625   # five quarter inches (1.25")
wt   =  .75    # nominal 2 inches (1.5")
wf   = 1.75    # nominal 4 inches (3.5")

# height
height = 1.75
htxf  = 1.75
htxs  = 2.75
htxe  = 3.75
htxt  = 4.75
htxtw = 5.75

# length
length = 4
le  = 4
lt  = 5
ltw = 6
lft = 7
lst = 8


# define Panel-------------------------------------------------------------

class DimensionalLumberPanel(bpy.types.Panel):
    """Creates a Panel in Toolbar that adds dimensional lumber"""
    bl_label = "Dimensional Lumber"
    bl_idname = "OBJECT_PT_dimensionalLumber"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category= "Lumber"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object

        # Height & Width Section-----
        row = layout.row()
        row.label(text="Select width")

        i = 0
        for string in hW:
            row = layout.row()
            row.prop(scene, string)
            i += 1

        # Length Section-----
        row = layout.row()
        row.label(text="Select length")

        n = 0
        for stringTwo in l:
            row = layout.row()
            row.prop(scene, stringTwo)
            n += 1

        # Button section (last)-----
        row = layout.row()
        row.label(text="Add Dimensional Lumber") #icon='WORLD' (and icon can be the third argument)

        row = layout.row()
        row.operator("mesh.add_object")

        row = layout.row()
        row.operator("get.board_lengths")


# Checkbox management-----------------------------------------------


def checkbox_Callback0(self, context):

    if self.twoXFour_prop:
        if self.twoXSix_prop:
            self.twoXSix_prop = False
        if self.twoXEight_prop:
            self.twoXEight_prop = False
        if self.twoXTen_prop:
            self.twoXTen_prop = False
        if self.twoXTwelve_prop:
            self.twoXTwelve_prop = False
        global width
        width = wt
        global height
        height = htxf
        global obj_string1
        obj_string1 = "2x4"

        # console feedback
        dimensions = [width * 2, height * 2]
        for value in dimensions:
            print(value)

def checkbox_Callback1(self, context):

    if self.twoXSix_prop:
        if self.twoXFour_prop:
            self.twoXFour_prop = False
        if self.twoXEight_prop:
            self.twoXEight_prop = False
        if self.twoXTen_prop:
            self.twoXTen_prop = False
        if self.twoXTwelve_prop:
            self.twoXTwelve_prop = False
        global width # these two lines in all callbacks needs to -->
        width = wt   # change vertCollections variables
        global  height
        height = htxs
        global obj_string1
        obj_string1 = "2x6"

        # console feedback
        dimensions = [width * 2, height * 2]
        for value in dimensions:
            print(value)

def checkbox_Callback2(self, context):

    if self.twoXEight_prop:
        if self.twoXFour_prop:
            self.twoXFour_prop = False
        if self.twoXSix_prop:
            self.twoXSix_prop = False
        if self.twoXTen_prop:
            self.twoXTen_prop = False
        if self.twoXTwelve_prop:
            self.twoXTwelve_prop = False
        global width
        width = wt
        global height
        height = htxe
        global obj_string1
        obj_string1 = "2x8"

        # console feedback
        dimensions = [width * 2, height * 2]
        for value in dimensions:
            print(value)

def checkbox_Callback3(self, context):

    if self.twoXTen_prop:
        if self.twoXFour_prop:
            self.twoXFour_prop = False
        if self.twoXSix_prop:
            self.twoXSix_prop = False
        if self.twoXEight_prop:
            self.twoXEight_prop = False
        if self.twoXTwelve_prop:
            self.twoXTwelve_prop = False
        global width
        width = wt
        global height
        height = htxt
        global obj_string1
        obj_string1 = "2x10"

        # console feedback
        dimensions = [width * 2, height * 2]
        for value in dimensions:
            print(value)

def checkbox_Callback4(self, context):

    if self.twoXTwelve_prop:
        if self.twoXFour_prop:
            self.twoXFour_prop = False
        if self.twoXSix_prop:
            self.twoXSix_prop = False
        if self.twoXEight_prop:
            self.twoXEight_prop = False
        if self.twoXTen_prop:
            self.twoXTen_prop = False
        global width
        width = wt
        global height
        height = htxtw
        global obj_string1
        obj_string1 = "2x12"

        # console feedback
        dimensions = [width * 2, height * 2]
        for value in dimensions:
            print(value)

#--------------------------------------

def checkbox_Callback5(self, context):

    if self.eight_prop:
        if self.ten_prop:
            self.ten_prop = False
        if self.twelve_prop:
            self.twelve_prop = False
        if self.fourteen_prop:
            self.fourteen_prop = False
        if self.sixteen_prop:
            self.sixteen_prop = False
        global length
        length = le
        global obj_string2
        obj_string2 = "x8"

        # console feedback
        print(length * 2)

def checkbox_Callback6(self, context):

    if self.ten_prop:
        if self.eight_prop:
            self.eight_prop = False
        if self.twelve_prop:
            self.twelve_prop = False
        if self.fourteen_prop:
            self.fourteen_prop = False
        if self.sixteen_prop:
            self.sixteen_prop = False
        global length
        length = lt
        global obj_string2
        obj_string2 = "x10"

        # console feedback
        print(length * 2)

def checkbox_Callback7(self, context):

    if self.twelve_prop:
        if self.eight_prop:
            self.eight_prop = False
        if self.ten_prop:
            self.ten_prop = False
        if self.fourteen_prop:
            self.fourteen_prop = False
        if self.sixteen_prop:
            self.sixteen_prop = False
        global length
        length = ltw
        global obj_string2
        obj_string2 = "x12"

        # console feedback
        print(length * 2)

def checkbox_Callback8(self, context):

    if self.fourteen_prop:
        if self.eight_prop:
            self.eight_prop = False
        if self.ten_prop:
            self.ten_prop = False
        if self.twelve_prop:
            self.twelve_prop = False
        if self.sixteen_prop:
            self.sixteen_prop = False
        global length
        length = lft
        global obj_string2
        obj_string2 = "x14"

        # console feedback
        print(length * 2)

def checkbox_Callback9(self, context):

    if self.sixteen_prop:
        if self.eight_prop:
            self.eight_prop = False
        if self.ten_prop:
            self.ten_prop = False
        if self.twelve_prop:
            self.twelve_prop = False
        if self.fourteen_prop:
            self.fourteen_prop = False
        global length
        length = lst
        global obj_string2
        obj_string2 = "x16"

        # console feedback
        print(length * 2)


# properties (checkboxes)--------------------------------------------------------

class MyProperties(PropertyGroup):

    #put in an array
    hW.extend (["twoXFour_prop", "twoXSix_prop", "twoXEight_prop", "twoXTen_prop", "twoXTwelve_prop"])
    #can the below be single variables
    bpy.types.Scene.twoXFour_prop   = BoolProperty(name="2x4", description="Select for 2x4", default = False, update = checkbox_Callback0)
    bpy.types.Scene.twoXSix_prop    = BoolProperty(name="2x6", description="Select for 2x6", default = False, update = checkbox_Callback1)
    bpy.types.Scene.twoXEight_prop  = BoolProperty(name="2x8", description="Select for 2x8", default = False, update = checkbox_Callback2)
    bpy.types.Scene.twoXTen_prop    = BoolProperty(name="2x10",description="Select for 2x10",default = False, update = checkbox_Callback3)
    bpy.types.Scene.twoXTwelve_prop = BoolProperty(name="2x12",description="Select for 2x12",default = False, update = checkbox_Callback4)

    #put in an array
    l.extend (["eight_prop", "ten_prop", "twelve_prop", "fourteen_prop", "sixteen_prop"])
    bpy.types.Scene.eight_prop    = BoolProperty(name="8", description="Select for 8' length", default = False, update = checkbox_Callback5)
    bpy.types.Scene.ten_prop      = BoolProperty(name="10",description="Select for 10' lenght",default = False, update = checkbox_Callback6)
    bpy.types.Scene.twelve_prop   = BoolProperty(name="12",description="Select for 12' length",default = False, update = checkbox_Callback7)
    bpy.types.Scene.fourteen_prop = BoolProperty(name="14",description="Select for 14' length",default = False, update = checkbox_Callback8)
    bpy.types.Scene.sixteen_prop  = BoolProperty(name="16",description="Select for 16' length",default = False, update = checkbox_Callback9)
