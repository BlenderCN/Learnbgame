# base code file to copy to mdworkdir
# from PythonQt import QtCore, QtGui, MarvelousDesignerAPI
# from PythonQt.MarvelousDesignerAPI import *
import MarvelousDesigner
# from MarvelousDesigner import *

import sys

# mdsa = MarvelousDesigner.MarvelousDesigner()
import __main__
mdsa = __main__.mdsa
basedir = "C:/mdwork_temp/"
def autosim(mdsa):
    mdsa.clear_console() 
    mdsa.initialize() 
    mdsa.set_open_option("m", 5) 
    mdsa.set_save_option("m", 5, False)
    mdsa.set_garment_file_path(basedir + "garment.zpac") 
    # mdsa.set_avatar_file_path(basedir + "animation.abc")
    mdsa.set_animation_file_path(basedir + "animation.abc") 
    mdsa.set_simulation_options(0, 0, 0) 
    mdsa.set_save_file_path(basedir + "result.obj")
    # mdsa.set_save_folder_path(mydir+"result", "obj")
    mdsa.process(False) 

    # mdsa.clear_console() 
    # mdsa.initialize() 
    # mdsa.set_open_option("m", 5) 
    # mdsa.set_save_option("m", 5, False)
    # mdsa.set_simulation_options(0, 0, 0) 
    # mdsa.set_save_file_path(basedir + "result.obj")
    # mdsa.single_process(open_garment_path = basedir + "garment.zpac",
    #                     open_avatar_path = basedir + "animation.abc",
    #                     open_animation_path = basedir + "animation.abc",
    #                     save_file_path = basedir + "result.obj", obj_type = 0, simulation_delay_time = 0, simulation_quality = 0, simulation = True, auto_save_project_file = False, with_xml_data = False)

autosim(mdsa)
# sys.exit()
