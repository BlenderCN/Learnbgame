# Python application for detailed neuronal morphometric analysis (Aguiar, Sousa & Szucs, Neuroinformatics 2013 - Submitted)
# Author: Paulo de Castro Aguiar	
# Date: Apr 2013
# email: pauloaguiar@fc.up.pt

"""py3DN main() function"""

import sys

# CHANGE THIS LINE FOR YOUR INSTALATION DIRECTORY
#sys.path.append('C:\\py3DN')

import DataContainers
import NeuroLucidaXMLParser
import InterpolateFun


# global variables are defined in the myconfig.py file
import myconfig
from mytools import *


# define the function MAIN()
def main():
    

    if len( sys.argv ) < 2:
        NO_BLENDER = 0
    else:
        NO_BLENDER = 1


    """Gateway"""

    if NO_BLENDER == 1: # use this to import all neuron data into an interactive python shell

        # parameters that otherwise would be obtained from gui

        filename             = sys.argv[1]
        minimal_diam         = 0.17
        remove_points        = True
        contours_detail      = 1
        interpolation_degree = 0

        
        NeuroLucidaXMLParser.Load_Neuron( filename, minimal_diam, remove_points ) 
        InterpolateFun.Interpolate_Objects( myconfig.neuron[0], myconfig.morphology[0], contours_detail, interpolation_degree, minimal_diam )
        
        print('\nAll done! Waiting for your commands.')
        
    else:

        import GUI


    return




# All ready! Start the engine!
if __name__ == '__main__':
    main()
