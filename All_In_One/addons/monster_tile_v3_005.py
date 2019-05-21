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

bl_info = {
    'name': 'Monster Tile Renderer',
    'author': 'Dealga McArdle (zeffii) <digitalaphasia.com>',
    'version': (0, 3, 3),
    'blender': (2, 6, 3),
    'location': 'Render > Monster Tile Renderer',
    'description': 'you give it CM / INCH, it spits out tiled renders.',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Render'}

import bpy
from bpy.props import *
from bpy import path
import math

# updated 2 July 2012

''' C O N S T A N T S   ( S T R I N G S   A N D   V A L U E S )'''


MAX_PERCENT = 32767     # @1k px thats, 327kpx max per side. that's a lot.
CMINCH = 0.393700787    # 1 centimeter = 0.393700787 inch 
DEFAULTLINE = ""

input_descr1 = "format: 01_01, 02_02, 04_02, 26_22 "
input_descr2 = "(comma+space separated, order doesn't matter)"
description_full = input_descr1 + input_descr2


''' W O R K L O A D   F U N C T I O N S'''


def get_pixels(context):
    
    '''
    Takes realworld width, height and DPI to produce raster equivalent

    arguments   :   Description
    ------------------------------------------------------------
    mode        :   (string) ['NONE', 'METRIC', 'IMPERIAL'], mode
                    
    width       :   (float) or int value for the real world measurement
    height      :   (float) or int value for the real world measurement
    DPI         :   (int) to declare what DPI you are aiming for.

    returns     :   by valid input:
                    cells_wide, cells_high, total_px_width, total_px_height

                    by invalid input: returns None
    '''
    
    print("="*60)
    
    # from context
    scn = context.scene
    mode = scn.unit_settings.system
    width = scn.MyDimW
    height = scn.MyDimH
    DPI = scn.MyDPIsetting
    scn.MyShowSwitch = True

    # or whatever your machine can handle comfortably
    largest_tile_dimension_wide = scn.MyMaxTileWidth 
    largest_tile_dimension_high = scn.MyMaxTileHeight
     
    if mode == 'METRIC':
        width_in_inches = width*CMINCH
        height_in_inches = height*CMINCH
    elif mode == 'IMPERIAL':
        width_in_inches = width
        height_in_inches = height
        
    if mode != 'NONE':
        print("width", width, "x height", height, mode, "| DPI", DPI)
        if mode == 'METRIC':
            print("width", width_in_inches,"(inches)")
            print("height", height_in_inches, "(inches)")
            
        print("\nat", DPI, "DPI that gives: ")
    
        w_in_px = width_in_inches*DPI
        h_in_px = height_in_inches*DPI
        w_in_px = math.floor(w_in_px)   
        h_in_px = math.floor(h_in_px)
        
        print("Width", w_in_px,"px. Height", h_in_px, "px")
    else:
        w_in_px = scn.MyPXwide
        h_in_px = scn.MyPXhigh
    
    # determine number of tiles wide / high
    cells_wide = math.ceil(w_in_px / largest_tile_dimension_wide)
    cells_high = math.ceil(h_in_px / largest_tile_dimension_high)
    
    square_tiles = max(cells_wide, cells_high)
    
    px_wide_per_tile = math.floor(w_in_px / square_tiles)
    px_high_per_tile = math.floor(h_in_px / square_tiles)
    
    out1 = str(square_tiles)+" tiles wide, at "+str(px_wide_per_tile)+"px wide"
    out2 = str(square_tiles)+" tiles high, at "+str(px_high_per_tile)+"px high"
  
    scn.MyTilesWidth = square_tiles
    scn.MyTilesHeight = square_tiles
    
    percent1 = int(w_in_px / px_wide_per_tile)*100
    percent2 = int(h_in_px / px_high_per_tile)*100
    scn.MyEnlargePercentage = max(percent1, percent2)
    
    out3 = "percentage scale :" + str(scn.MyEnlargePercentage)+" %"
    scn.MyOutput1 = out1
    scn.MyOutput2 = out2
    scn.MyOutput3 = out3
            
    return px_wide_per_tile, px_high_per_tile
    


def do_render_job(scn):

    n = scn.MyTilesWidth # n tiles wide (x)
    m = scn.MyTilesHeight # m tiles high (y)

    usedir = scn.MyFilePath
    filename = scn.MyFileName
    filetype = scn.render.file_extension
    
    if usedir == "":
        print("select a directory to render into")
        return

    # slice unit size
    wslice = 1/n
    hslice = 1/m

    # consumables
    name_list = []
    subset_list = []
    
    for j in range(m):
        for i in range(n):
            left_side = str(i+1).zfill(2)
            right_side = str(j+1).zfill(2) 
            name_list.append(left_side+"_"+right_side)

    # prevent accidental duplicates, whitespaces
    if scn.MyTileSelection == True:
        subset_list = list(set(scn.MySubset.split(", ")))
        for element in subset_list:
            element = element.strip()
    print("current subset list", subset_list)

    # use border and crop, set resolution percentage
    scn.render.use_border = True
    scn.render.use_crop_to_border = True

    divider = "="*20 + " New Job " + "="*20
    print(divider)
    print("destination folder", usedir)
    
    for cell in name_list:

        # to perform only subset rendering
        if (scn.MyTileSelection == True) and (subset_list != []):
            if cell in subset_list: 
                print("cell ", cell)
            else:
                continue    # skip this cell.

        wdiv, hdiv = cell.split("_")
        bmin_x = float((int(wdiv)-1)*wslice)
        bmax_x = float(int(wdiv)*wslice)
        bmin_y = 1.0 - (float(int(hdiv)*hslice))
        bmax_y = 1.0 - (float((int(hdiv)-1)*hslice))

        str_borders = ("bmin_x="+str(bmin_x),
                       "bmax_x="+str(bmax_x),
                       "bmin_y="+str(bmin_y),
                       "bmax_y="+str(bmax_y))

        # set border for this tile
        scn.render.border_min_x = bmin_x
        scn.render.border_max_x = bmax_x
        scn.render.border_min_y = bmin_y
        scn.render.border_max_y = bmax_y 

        # this is candidate for setting up a progress tracker
        bpy.ops.render.render()

        RR = "Render Result"
        mypath = usedir+filename+"_"+cell+filetype
        bpy.data.images[RR].save_render(mypath)
        print("rendered", cell+filetype)

    # reset border and crop modes
    bpy.context.scene.render.use_border = False
    bpy.context.scene.render.use_crop_to_border = False
    print("completed")


''' P A N E L   D E F I N I T O N'''


class RENDER_PT_SetupTiles(bpy.types.Panel):
    bl_label = "Monster Tile Renderer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    bts = bpy.types.Scene

    bts.MyFilePath = StringProperty(
        name='path to file',
        subtype='DIR_PATH')   

    # looks at current blend and uses it as a basename, the way i like it.
    # [TODO] update with new file name, without restart blender.
    # bpy.context.scene.update()
    mfilepath = bpy.data.filepath
    this_blend = path.display_name_from_filepath(mfilepath)

    bts.MyFileName = StringProperty(
        name='file name',
        description='file name will be suffixed by cell name',
        default=this_blend)
        
    bts.MyDPIsetting = IntProperty(
        name = 'DPI',
        description='set some reasonable value here, 150/300/600/1200',
        min=10, max=1200, default=300)
        
    # arbitrary value 10meters, if you need something that big contact me.
    # i'd love to see it :)
    bts.MyDimW = FloatProperty(
        description="real width in cm/inch",
        min=5.0, max=1000.0, default=100.0)
    bts.MyDimH = FloatProperty(
        description="real height in cm/inch",
        min=5.0, max=1000.0, default=100.0)

    bts.MyPXwide = IntProperty(
        description="px width",
        min=1000, max=327670, default=1920)
    bts.MyPXhigh = IntProperty(
        description="px height",
        min=1000, max=327670, default=1080)

    bts.MyMaxTileWidth = IntProperty(
        description="max px width",
        min=500, max=10000, default=1000)
    bts.MyMaxTileHeight = IntProperty(
        description="max px height",
        min=500, max=10000, default=1000)
    
    bts.MyTilesWidth = IntProperty()
    bts.MyTilesHeight = IntProperty()
    bts.MyEnlargePercentage = IntProperty()
    bts.MyShowSwitch = BoolProperty(default=False)
    
    bts.MyTileSelection = BoolProperty(
        name="Render subset of tiles",
        default=False)
    
    bts.MySubset = StringProperty(
        name = "Subset",
        description = description_full)

    bts.MyRenderResX = IntProperty()
    bts.MyRenderResY = IntProperty()

    # using the panel to display currently calculated settings
    bts.MyOutput1 = StringProperty(default=DEFAULTLINE)
    bts.MyOutput2 = StringProperty(default=DEFAULTLINE)
    bts.MyOutput3 = StringProperty(default=DEFAULTLINE)
    
    
    def draw(self, context):

        layout = self.layout
        scn = context.scene
        unit = scn.unit_settings

        row1 = layout.row(align=True)
        row2 = layout.row(align=True)
        row3 = layout.row(align=True)
        row4 = layout.row(align=True)
        row5 = layout.row(align=True)
        row6 = layout.row(align=True)

        row1.prop(scn, "MyFilePath")
        row2.prop(scn, "MyFileName")

        # side by side
        row3.label("file type")
        # row3.prop(scn.render, "file_format", text="")
        row3.prop(scn.render.image_settings, "file_format", text="")  #update for 2.6
 
        if unit.system in ('METRIC','IMPERIAL'):
            row3.prop(scn, "MyDPIsetting")
            
        row4.prop(unit, "system", expand=True)

        # discriminate
        if unit.system in ('METRIC','IMPERIAL'):
            unittype = "cm"
            if unit.system == 'IMPERIAL':
                unittype = "Inch"
                
            row5.label("W * H in " + unittype)
            row5.prop(scn, "MyDimW")
            row5.prop(scn, "MyDimH")
        else:
            row5.label("Pixels X * Y")
            row5.prop(scn, "MyPXwide")
            row5.prop(scn, "MyPXhigh")

        # choices     
        row6.label("tile size limits")
        row6.prop(scn, "MyMaxTileWidth")
        row6.prop(scn, "MyMaxTileHeight")
        
        row7 = layout.row(align=True)
        row7.operator("object.calculate")
        
        if scn.MyShowSwitch != False:
            row8 = layout.row(align=True)
            row8.label(scn.MyOutput1)
            row9 = layout.row(align=True)
            row9.label(scn.MyOutput2)
            row10 = layout.row(align=True)
            row10.label(scn.MyOutput3)
            row11 = layout.row(align=True)
            row11.operator("object.setvalues")

   
        row12 = layout.row(align=True)
        row12.prop(scn, "MyTileSelection")
        
        row13 = layout.row(align=True)
        row13.prop(scn, "MySubset")

        if scn.MyTileSelection == True:
            row13.active = True
            row13.enabled = True

            temp_subset_list = list(set(scn.MySubset.split(", ")))
            if temp_subset_list != ['']:
                num_subset = len(temp_subset_list)

        else:
            row13.active = False
            row13.enabled = False
            num_subset = 0
        
    
        # a few lines to indicate the number of subset tiles.
        row14 = layout.row(align=True)
        num_tiles = str(scn.MyTilesWidth * scn.MyTilesHeight)
        button_title = "render job! "+ num_tiles + " Tiles"
        if scn.MyTileSelection == True:
            subset_str = " subset: "+str(num_subset)
            button_title += subset_str
        row14.operator( "object.starttilejob", text=button_title, icon="MESH_GRID")


''' B U T T O N  D E F I N I T I O N S'''


class OBJECT_OT_Calculate(bpy.types.Operator):
    bl_idname = "object.calculate"
    bl_label = "Perform Calculations"
    bl_description = "gets stats for rendering"

    def execute(self, context):
        xres, yres = get_pixels(context)
        context.scene.MyRenderResX = xres
        context.scene.MyRenderResY = yres
        return {'FINISHED'}


class OBJECT_OT_ApplySettings(bpy.types.Operator):
    bl_idname = "object.setvalues"
    bl_label = "Apply Settings"
    bl_description = "set stats for rendering"

    def execute(self, context):
        scn = context.scene                
        scn.render.resolution_percentage = scn.MyEnlargePercentage
        scn.render.resolution_x = scn.MyRenderResX
        scn.render.resolution_y = scn.MyRenderResY
        return {'FINISHED'}


class OBJECT_OT_StartTileJob(bpy.types.Operator):
    bl_idname = "object.starttilejob"
    bl_label = "Start Tile Job"
    bl_description = "Start Render Job using defined tile numbers"

    def execute(self, context):
        if len(bpy.data.cameras) > 0:
            do_render_job(context.scene)
        else:
            print('nope, add a camera first')
        return {'FINISHED'}


''' B O I L E R P L A T E '''


reg_list = [    OBJECT_OT_StartTileJob,  
                RENDER_PT_SetupTiles,
                OBJECT_OT_Calculate,
                OBJECT_OT_ApplySettings]

def register():
    for classname in reg_list:
        bpy.utils.register_class(classname)

def unregister():
    for classname in reg_list:
        bpy.utils.unregister_class(classname)

if __name__ == "__main__":
    register()