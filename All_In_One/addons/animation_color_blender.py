'''
BEGIN GPL LICENSE BLOCK

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

END GPL LICENCE BLOCK
'''

bl_info = {
    "name": "Color Blender",
    "author": "Scott Wood (aka 'crazycourier'",
    "version": (0, 2, ),
    "blender": (2, 5, 7),
    "api": 36373,
    "location": "View3D > Tools",
    "description": "Set a keyframe for the material diffuse color spaced out over a specified number of frames within the timeline.",
    "warning": "Still under development, bug reports appreciated",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
   }

'''
Simple script to set a keyframe for the material diffuse color spaced out over a
specified number of frames within the timeline.

To use select your object(s) and then select a color palette. The palette colors can
be modified. Choose the number frames between each keyframe and click
Run Color Blender

'''


import bpy
from bpy.props import *

class mmProps(bpy.types.PropertyGroup):
    enabled = bpy.props.IntProperty(default=0)
    
    # Material custom Properties properties
    mmColors = bpy.props.EnumProperty(
        items=(("RANDOM", "Random", "Use random colors"),
                ("CUSTOM", "Custom", "Use custom colors"),
                ("BW", "Black/White", "Use Black and White"),
                ("BRIGHT", "Bright Colors", "Use Bright colors"),
                ("EARTH", "Earth", "Use Earth colors"),
                ("GREENBLUE", "Green to Blue", "Use Green to Blue colors")),
        description="Choose which type of colors the materials uses",
        default="BRIGHT",
        name="Define a color palette")
    
    # Custom property for how many keyframes to skip
    mmSkip = bpy.props.IntProperty(name="frames", min=1, max=500, default=20, description="Number of frames between each keyframes")
    
    # Custom property to enable/disable random order for the 
    mmBoolRandom = bpy.props.BoolProperty(name="Random Order", default=False, description="Randomize the order of the colors")
    
    # Custom Color properties
    mmColor1 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.8, 0.8, 0.8), description="Custom Color 1", subtype="COLOR")
    mmColor2 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.8, 0.8, 0.3), description="Custom Color 2", subtype="COLOR")
    mmColor3 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.8, 0.5, 0.6), description="Custom Color 3", subtype="COLOR")
    mmColor4 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.2, 0.8, 0.289), description="Custom Color 4", subtype="COLOR")
    mmColor5 = bpy.props.FloatVectorProperty(min=0, max=1, default=(1.0, 0.348, 0.8), description="Custom Color 5", subtype="COLOR")
    mmColor6 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.4, 0.67, 0.8), description="Custom Color 6", subtype="COLOR")
    mmColor7 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.66, 0.88, 0.8), description="Custom Color 7", subtype="COLOR")
    mmColor8 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.8, 0.38, 0.22), description="Custom Color 8", subtype="COLOR")

    # BW Color properties
    bwColor1 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.0,0.0,0.0), description="Black/White Color 1", subtype="COLOR")
    bwColor2 = bpy.props.FloatVectorProperty(min=0, max=1, default=(1.0,1.0,1.0), description="Black/White Color 2", subtype="COLOR")
    
    # Bright Color properties
    brightColor1 = bpy.props.FloatVectorProperty(min=0, max=1, default=(1.0, 0.0, 0.75), description="Bright Color 1", subtype="COLOR")
    brightColor2 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.0,1.0,1.0), description="Bright Color 2", subtype="COLOR")
    brightColor3 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.0,1.0,0.0), description="Bright Color 3", subtype="COLOR")
    brightColor4 = bpy.props.FloatVectorProperty(min=0, max=1, default=(1.0,1.0,0.0), description="Bright Color 4", subtype="COLOR")
    
    # Earth Color Properties
    earthColor1 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.068, 0.019, 0.014), description="Earth Color 1", subtype="COLOR")
    earthColor2 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.089, 0.060, 0.047), description="Earth Color 2", subtype="COLOR")
    earthColor3 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.188, 0.168, 0.066), description="Earth Color 3", subtype="COLOR")
    earthColor4 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.445, 0.296, 0.065), description="Earth Color 4", subtype="COLOR")
    earthColor5 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.745, 0.332, 0.065), description="Earth Color 5", subtype="COLOR")
    
    # Green to Blue Color properties
    greenblueColor1 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.296, 0.445, 0.074), description="Green/Blue Color 1", subtype="COLOR")
    greenblueColor2 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.651, 1.0, 0.223), description="Green/Blue Color 2", subtype="COLOR")
    greenblueColor3 = bpy.props.FloatVectorProperty(min=0, max=1, default=(0.037, 0.047, 0.084), description="Green/Blue Color 3", subtype="COLOR")
    
# Draw Material changer panel in Toolbar
class mmPanel(bpy.types.Panel):
    bl_label = "Color Blender"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        objects = bpy.context.selected_objects
        colorProp = bpy.context.window_manager.colorblender
        
        # Don't show menu if no objects are selected
        if not objects:
            box = self.layout.box()
            box.label(text='No object(s) selected', icon='COLOR')
            return
        
        # Box for Color Blender
        layout.label("Color palette")
        layout.prop(colorProp, 'mmColors')
        # Show Custom Colors if selected
        if colorProp.mmColors == 'CUSTOM':
            row = layout.row(align=True)
            row.prop(colorProp, 'mmColor1')
            row.prop(colorProp, 'mmColor2')
            row.prop(colorProp, 'mmColor3')
            row.prop(colorProp, 'mmColor4')
            row.prop(colorProp, 'mmColor5')
            row.prop(colorProp, 'mmColor6')
            row.prop(colorProp, 'mmColor7')
            row.prop(colorProp, 'mmColor8')
        # Show Earth Colors
        elif colorProp.mmColors == 'BW':
            row = layout.row(align=True)
            row.prop(colorProp, 'bwColor1')
            row.prop(colorProp, 'bwColor2')
        # Show Earth Colors
        elif colorProp.mmColors == 'BRIGHT':
            row = layout.row(align=True)
            row.prop(colorProp, 'brightColor1')
            row.prop(colorProp, 'brightColor2')
            row.prop(colorProp, 'brightColor3')
            row.prop(colorProp, 'brightColor4')
        # Show Earth Colors
        elif colorProp.mmColors == 'EARTH':
            row = layout.row(align=True)
            row.prop(colorProp, 'earthColor1')
            row.prop(colorProp, 'earthColor2')
            row.prop(colorProp, 'earthColor3')
            row.prop(colorProp, 'earthColor4')
            row.prop(colorProp, 'earthColor5')
        # Show Earth Colors
        elif colorProp.mmColors == 'GREENBLUE':
            row = layout.row(align=True)
            row.prop(colorProp, 'greenblueColor1')
            row.prop(colorProp, 'greenblueColor2')
            row.prop(colorProp, 'greenblueColor3')
        elif colorProp.mmColors == 'RANDOM':
            row = layout.row()
        # Show rest of menu
        col = layout.column()
        col.label('Keyframe every')
        col.prop(colorProp, 'mmSkip')
        row = layout.row()
        row = layout.row()
        # layout.prop(colorProp, 'mmBoolRandom')
        col = layout.column(align=True)
        col.operator("object.colorblender", text="Run Color Blender", icon="COLOR")
        col.operator("object.colorblenderclear", text="Reset Keyframes", icon="KEY_DEHLT")


# This is the magical material changer!
class OBJECT_OT_materialChango(bpy.types.Operator):
    bl_idname = 'object.colorblender'
    bl_label = 'Color Blender'
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        
        import bpy, random
        colorProp = bpy.context.window_manager.colorblender # properties panel
        colorObjects = bpy.context.selected_objects
        
        # Set color lists
        brightColors  = [colorProp.brightColor1, colorProp.brightColor2, colorProp.brightColor3, colorProp.brightColor4]
        bwColors = [colorProp.bwColor1, colorProp.bwColor2]
        customColors = [colorProp.mmColor1, colorProp.mmColor2, colorProp.mmColor3, colorProp.mmColor4, colorProp.mmColor5, colorProp.mmColor6, colorProp.mmColor7, colorProp.mmColor8]
        earthColors = [colorProp.earthColor1, colorProp.earthColor2, colorProp.earthColor3, colorProp.earthColor4, colorProp.earthColor5]
        greenblueColors = [colorProp.greenblueColor1, colorProp.greenblueColor2, colorProp.greenblueColor3]
        
        colorList = colorProp.mmColors
        
        # Go through each selected object and run the operator
        for i in colorObjects:
            theObj = i
            # Check to see if object has materials
            checkMaterials = len(theObj.data.materials)
            if checkMaterials == 0:
                # Add a material
                print('No materials, adding one now.')
                materialName = "colorblendMaterial"
                madMat = bpy.data.materials.new(materialName)
                theObj.data.materials.append(madMat)
            else:                
                pass # pass since we have what we need
                
            # assign the first material of the object to "mat"
            mat = theObj.data.materials[0] 

            # Numbers of frames to skip between keyframes
            skip = colorProp.mmSkip

            # Random material function
            def colorblenderRandom():
                for crazyNumber in range(3):
                    mat.diffuse_color[crazyNumber] = random.random()
            
            def colorblenderCustom():
                mat.diffuse_color = random.choice(customColors)
                
            # Black and white color        
            def colorblenderBW():
                mat.diffuse_color = random.choice(bwColors)
            
            # Bright colors
            def colorblenderBright():
                mat.diffuse_color = random.choice(brightColors)
                
            # Earth Tones
            def colorblenderEarth():
                mat.diffuse_color = random.choice(earthColors)
                
            # Green to Blue Tones
            def colorblenderGreenBlue():
                mat.diffuse_color = random.choice(greenblueColors)
             
            # define frame start/end variables
            scn = bpy.context.scene       
            start = scn.frame_start
            end = scn.frame_end           
            # Go to each frame in iteration and add material
            while start<=(end+(skip-1)):
               
                bpy.ops.anim.change_frame(frame=start)
                
                # Check what colors setting is checked and run the appropriate function
                if colorProp.mmColors=='RANDOM':
                    colorblenderRandom()
                elif colorProp.mmColors=='CUSTOM':
                    colorblenderCustom()
                elif colorProp.mmColors=='BW':
                    colorblenderBW()
                elif colorProp.mmColors=='BRIGHT':
                    colorblenderBright()
                elif colorProp.mmColors=='EARTH':
                    colorblenderEarth()
                elif colorProp.mmColors=='GREENBLUE':
                    colorblenderGreenBlue()
                else:
                    pass
                
                # Add keyframe to material
                mat.keyframe_insert('diffuse_color')
                
                # Increase frame number
                start += skip
        return{'FINISHED'}
    
###### This clears the keyframes ######
class OBJECT_OT_clearColorblender(bpy.types.Operator):
    bl_idname = 'object.colorblenderclear'
    bl_label = 'Clear colorblendness'
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        
        import bpy, random
        mcolorblend = context.window_manager.colorblender_operator # properties panel
        colorObjects = bpy.context.selected_objects
        
        # Go through each selected object and run the operator
        for i in colorObjects:
            theObj = i    
            # assign the first material of the object to "mat"
            matCl = theObj.data.materials[0] 
            
            # define frame start/end variables
            scn = bpy.context.scene       
            start = scn.frame_start
            end = scn.frame_end

            # Remove all keyframes from diffuse_color, super sloppy need to find better way
            while start<=(end*2):
                bpy.ops.anim.change_frame(frame=start)
                matCl.keyframe_delete('diffuse_color')
                start += 1
            
        return{'FINISHED'} 
 
classes = [OBJECT_OT_materialChango, 
                OBJECT_OT_clearColorblender,
                mmPanel, 
                mmProps]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.colorblender = bpy.props.PointerProperty(type=mmProps)
    bpy.types.WindowManager.colorblender_operator = bpy.props.PointerProperty(type=mmProps)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.WindowManager.colorblender
    del bpy.types.WindowManager.colorblender_operator
    
if __name__ == "__main__":
    register()