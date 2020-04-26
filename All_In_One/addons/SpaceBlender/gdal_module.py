'''This class takes in a DEM image and a color mapping file in the form
   GdalModule(<input_dem> <color_text_file>)
   The script runs the gdaldem hillshade on the image, then runs gdaldem color_relief_map
   on the image. Once a hillshade and color_relief have been generated the hsv_merge script
   is called to merge the hillshade and color_relief together. This script produces 3 output
   images out_hillshade.tiff, out_color.tiff, and DTM_TEXTURE.tiff'''


import subprocess
import platform as _platform
import sys

class GDALDriver(object):
    def __init__(self, input_dem):
        self.input_dem = input_dem

    def gdal_hillshade(self, hill_shade):
    #  Run gdaldem hillshade on the input dem image
        if _platform.system() == "Windows":
            hill_sh = 'OSGeo4W gdaldem hillshade '+self.input_dem+' '+hill_shade
        else:
            hill_sh = 'gdaldem hillshade '+self.input_dem+' '+hill_shade
        print('Running Command: ', hill_sh)
        try:
            sub_proc1 = subprocess.Popen(hill_sh, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #   Print the progress of the GDAL operation to the console to give user feedback
            while sub_proc1.poll() is None:
                out = sub_proc1.stdout.read(1)
                if out != '':
                    outstr = str(out)
                    for char in outstr:
                        if char in " b'":
                            outstr = outstr.replace(char, '')
                    sys.stdout.write(outstr)
                    sys.stdout.flush()

        except subprocess.SubprocessError as e:
            print('Error: ' + e)
            print('\nFailed to spawn subprocess for gdal hill-shade')
            return sys.exit(1)
        print('\n'+'Hill-Shade created.')
        return 0

    def gdal_color_relief(self, color_file, color_relief):
    #   Run gdal color_relief on the input dem image using the color_txt_file supplied
        if _platform.system() == "Windows":
            col_rel = 'OSGeo4W gdaldem color-relief '+self.input_dem+' '+color_file+' '+color_relief
        else:
            col_rel = 'gdaldem color-relief '+self.input_dem+' '+color_file+' '+color_relief
        print('Running Command:', col_rel)
        try:
            sub_proc2 = subprocess.Popen(col_rel, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            #Print the progress of the GDAL operation to the console to give user feedback
            while sub_proc2.poll() is None:
                out = sub_proc2.stdout.read(1)
                if out != '':
                    outstr = str(out)
                    for char in outstr:
                        if char in " b'":
                            outstr = outstr.replace(char, '')
                    sys.stdout.write(outstr)
                    sys.stdout.flush()

        except subprocess.SubprocessError as e:
            print('Error: ' + e)
            print('\nFailed to spawn subprocess for gdal color-relief')
            return sys.exit(1)
        print('\n'+'Color-Relief created.')
        return 0

    def hsv_merge(self, merge_location, hill_shade, color_relief, texture_location):
    #   Merge the hillshade and color-relief using the hsv_merge script
        if _platform.system() == "Windows":
            merge = 'OSGeo4W python ' + merge_location+' '+color_relief+' '+hill_shade+' '+texture_location
        else:
            merge = 'python ' + merge_location+' '+color_relief+' '+hill_shade+' '+texture_location
        print('Running Command:', merge)
        print('This process takes a while. Please be patient...')
        try:
            sub_proc3 = subprocess.Popen(merge, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #   Print the progress of the hsv_merge operation to the console to give user feedback
            while sub_proc3.poll() is None:
                out = sub_proc3.stdout.read(1)
                if out != '':
                    outstr = str(out)
                    for char in outstr:
                        if char in " b'":
                            outstr = outstr.replace(char, '')
                    sys.stdout.write(outstr)
                    sys.stdout.flush()

        except subprocess.SubprocessError as e:
            print('Error' + e)
            print('\nFailed to spawn subprocess for hsv_merge.')
            return sys.exit(1)
        return 0

    def gdal_clean_up(self, hill_shade, color_relief):
        if _platform.system() == "Windows":
            clean = 'del '+hill_shade+' '+color_relief
            print('\nCleaning up Gdal temp images...')
            try:
                subprocess.Popen(clean, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except OSError as e:
                print('Error: ' + e)
                print('\nFailed to clean up GDAL temp images.')
                sys.exit(1)
        else:
            clean = 'rm '+hill_shade+' '+color_relief
            print('\nCleaning up Gdal temp images...')
            try:
                subprocess.Popen(clean, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except OSError as e:
                print('Error: ' + e)
                print('\nFailed to clean up GDAL temp images.')
                return sys.exit(1)
            return 0
