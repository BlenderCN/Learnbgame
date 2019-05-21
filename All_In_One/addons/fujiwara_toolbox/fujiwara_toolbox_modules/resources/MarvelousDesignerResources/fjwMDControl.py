# exec("from fjwMDControl import *;run(mdsa)",globals(), locals())

from PythonQt import QtCore, QtGui, MarvelousDesignerAPI
from PythonQt.MarvelousDesignerAPI import *
import sys

def log(line):
    sys.stdout.write(line+"\n")
    sys.stdout.flush()

def logfile(text):
    f = open(r"C:\fjwmdtemp\log.txt", "a")
    f.write(text + "\n")
    f.close

class MD():
    def __init__(self, mdsa):
        self.mdsa = mdsa

    def initialize(self):
        mdsa = self.mdsa
   
        # mdsa.clear_console()
        mdsa.initialize() 
        # unit = "none", fps = 30
        mdsa.set_open_option("m", 30) 
        # unit = "none", fps = 30, unified = False, thin = True, weld = False
        mdsa.set_save_option("m", 30, False)

        mdsa.set_alembic_format_type(True)

        mdsa.on_export_garment_only()

    def simulate(self, abc_path, cloth_path, output_path):
        mdsa = self.mdsa

        mdsa.set_garment_file_path(cloth_path)
        mdsa.set_avatar_file_path(abc_path)
        mdsa.set_animation_file_path(abc_path)
        # obj_type = 0, simulation_quality = 0, simulation_delay_time = 5000, process_simulation = True
        mdsa.set_simulation_options(0, 1, 50) 
        mdsa.set_save_file_path(output_path)
        mdsa.set_auto_save(True)

    def process(self):
        mdsa = self.mdsa
        mdsa.process()

def run(mdsa):
    mddata = MD(mdsa)
    # mddata.simulate(r"C:\Users\Public\Documents\fjwmdtemp\q87d4ptw.abc", r"C:\Users\Public\Documents\fjwmdtemp\q87d4ptw.zpac", r"C:\Users\Public\Documents\fjwmdtemp\q87d4ptw.obj")
    f = open(r"C:\fjwmdtemp\mdcode.py", "r")
    lines = f.readlines()
    f.close

    mddata = MD(mdsa)
    mddata.initialize()
    for line in lines:
        line = line.replace("\n", "")
        if line == "":
            continue
        data = line.split(",")
        avatar_path = data[0]
        cloth_path = data[1]
        output_path = data[2]
        mddata.simulate(avatar_path, cloth_path, output_path)
    mddata.process()

    # clear cue
    f = open(r"C:\fjwmdtemp\mdcode.py", "w")
    f.close


