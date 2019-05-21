#################################################################
###Pipeline script to automate flyover creation #################
###Run script on command line with the following command:
###blender -b -P space_blend.py <your_image>.IMG
###For help with commands type:
###blender - b -P space_blend.py --h
#################################################################
import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper
from SpaceBlender import blender_module
from SpaceBlender import gdal_module
from SpaceBlender import flyover_module
import os
from sys import platform as _platform
import sys

class SpaceBlender(object):
    resolution = ['180p', '360p', '480p', '720p', '1080p']

    color_pattern = ['NoColorPattern',
                        'Rainbow_Saturated',
                        'Rainbow_Medium',
                        'Rainbow_Light',
                        'Blue_Steel',
                        'Earth',
                        'Diverging_BrownBlue',
                        'Diverging_RedGray',
                        'Diverging_BlueRed',
                        'Diverging_RedBrown',
                        'Diverging_RedBlue',
                        'Diverging_GreenRed',
                        'Sequential_Blue',
                        'Sequential_Green',
                        'Sequential_Red',
                        'Sequential_BlueGreen',
                        'Sequential_YellowBrown']

    flyover_pattern = ['noflyover', 'linear', 'circle', 'diamond']

    def __init__(self):



        #Set up the default options for the pipeline
        self.filepath = sys.argv[4]
        self.resolution = '1080p'
        self.flyover_pattern = 'LinearPattern'
        self.color_pattern = 'Rainbow_Saturated'
        self.animation = True
        self.stars = False
        self.mist = False
        #This section allows for the user to change options by added arguments on the command line
        #The arguments can be in any order and are case-insensitive can enter any number of arguments
        for arg in sys.argv:

            if arg in SpaceBlender.resolution:
                self.resolution = arg
                print("Video resolution set to:", self.resolution)

            for color in SpaceBlender.color_pattern:
                if arg.lower() == color.lower():
                    self.color_pattern = color
                    print("Color pattern set to:", self.color_pattern)

            for pattern in SpaceBlender.flyover_pattern:
                if arg.lower() == pattern.lower():
                    if arg.lower() == 'linear':
                        self.flyover_pattern = 'LinearPattern'
                        print("Flyover pattern set to:", self.flyover_pattern)
                    if arg.lower() == 'circle':
                        self.flyover_pattern = 'CirclePattern'
                        print("Flyover pattern set to:", self.flyover_pattern)

                    if arg.lower() == 'diamond':
                        self.flyover_pattern = 'DiamondPattern'
                        print("Flyover pattern set to:", self.flyover_pattern)
                    if arg.lower() == 'noflyover':
                        self.flyover_pattern = 'NoFlyover'
                        self.animation = False
                        print(self.flyover_pattern, "rendering still image")

            if arg.lower() == 'stars':
                self.stars = True
            if arg.lower() == 'mist':
                self.mist = True

    def display_help(self):
            print('To use the SpaceBlender Pipeline your command should look like:')
            print('blender -b -P space_blend.py test_dem.IMG\n')
            print('Default settings are: Linear Flyover, Saturated Rainbow color pattern, 1080p\n')
            print('You can add options in any order and they are case insensitive\n')
            print('Available options include flyover patterns, colors, resolution, stars, and mist\n')
            print('Here are the options:')
            print('Flyover patterns:', SpaceBlender.flyover_pattern)
            print('Available colors:', SpaceBlender.color_pattern)
            print('Resolutions:', SpaceBlender.resolution)

            print('A sample command with options could look like:')
            print('blender -b -P space_blend.py test_dem.IMG 480p Linear Stars Mist')
            print('blender -b -P space_blend.py test_dem.IMG circle 720p stars\n\n')


    def pipeline(self, context):
        input_DEM = self.filepath

        if input_DEM != bpy.path.ensure_ext(input_DEM, ".IMG"):
            return {'CANCELLED'}
        dtm_location = input_DEM

        texture_location = ''
        merge_location =''
        color_file = ''
        hill_shade = 'hillshade.tiff'
        color_relief = 'colorrelief.tiff'

        project_location = os.path.dirname(__file__)
        ################################################################################
        ## Use the GDAL tools to create hill-shade and color-relief and merge them with
        ## hsv_merge.py to use as a texture for the DTM. Creates DTM_TEXTURE.tiff
        ################################################################################
        if self.color_pattern == 'NoColorPattern':
            texture_location=None
            pass

        else:
            # If user selected a colr we are going to run the gdal and merge processes
            # We need to dtermine which OS is being used and set the location of color files
            # and the merge script accordingly
            if _platform == "linux" or _platform == "linux2":
            # linux
                    # Strip out the image name to set texture location and append color choice.
                texture_location = self.filepath.split('/')[-1:]
                texture_location = texture_location[0].split('.')[:1]
                texture_location = os.getcwd()+'/'+texture_location[0]+'_'+self.color_pattern+'.tiff'
                color_file = '/usr/share/blender/scripts/addons/SpaceBlender/color_maps/' + self.color_pattern + '.txt'
                merge_location = '/usr/share/blender/scripts/addons/SpaceBlender/hsv_merge.py'
            elif _platform == "darwin":
            # OS X
                        # Strip out the image name to set texture location and append color choice.
                texture_location = self.filepath.split('/')[-1:]
                texture_location = texture_location[0].split('.')[:1]
                texture_location = os.getcwd()+'/'+texture_location[0]+'_'+self.color_pattern+'.tiff'
                color_file = '/Applications/Blender/blender.app/Contents/MacOS/2.69/scripts/addons/SpaceBlender/color_maps/'\
                    + self.color_pattern + '.txt'
                merge_location = '/Applications/Blender/blender.app/Contents/MacOS/2.69/scripts/addons/SpaceBlender/hsv_merge.py'
            elif _platform == "win32":
            # Windows.
                # Strip out the image name to set texture location and append color choice.
                texture_location = self.filepath.split('\\')[-1:]
                texture_location = texture_location[0].split('.')[:1]
                texture_location = os.getcwd()+'\\'+texture_location[0]+'_'+self.color_pattern+'.tiff'
                color_file = '"'+'C:\\Program Files\\Blender Foundation\\Blender\\2.69\\scripts\\addons\\SpaceBlender\\color_maps\\'+self.color_pattern + '.txt'+'"'
                merge_location = '"'+'C:\\Program Files\\Blender Foundation\\Blender\\2.69\scripts\\addons\\SpaceBlender\\hsv_merge.py'+'"'

            gdal = gdal_module.GDALDriver(dtm_location)
            gdal.gdal_hillshade(hill_shade)
            gdal.gdal_color_relief(color_file, color_relief)
            gdal.hsv_merge(merge_location, hill_shade, color_relief, texture_location)

            print('\nSaving texture at: ' + texture_location)
            gdal.gdal_clean_up(hill_shade, color_relief)



        ################################################################################
        ####################Execute DEM Importer and Blender Module#####################
        blender_module.load(self, context,
                            filepath=input_DEM,
                            scale=0.01,
                            bin_mode='BIN12-FAST',
                            color_pattern=self.color_pattern,
                            flyover_pattern=self.flyover_pattern,
                            texture_location=texture_location,
                            cropVars=False,
                            resolution=self.resolution ,
                            stars=self.stars,
                            mist=self.mist,
                            render=True,
                            animation=self.animation)
        
        return {'FINISHED'}

if __name__ == "__main__":
    sp = SpaceBlender()
    if sys.argv[4] == '--h':
        sp.display_help()

    sp.pipeline(bpy.types.Operator)