###################################
#enables standalone support
if __name__ == "__main__":
    import os
    import sys
    from os.path import dirname, join, abspath, basename
    #Error handling if started from within blender's IDE
    try:
        main_package = dirname(abspath(__file__))
        print("main_package set!")
    except NameError:
        print("__file__ didn't work. trying bpy.")
        try:
            import bpy
            main_package = dirname(bpy.data.filepath)
            print("main_package set!")
        except:
            raise NameError("Can't hook blend file.")
    #
    #Iterates until it finds nimbus_vis or has run 10 times #10 subdirs max
    iter = 0
    #
    while basename(main_package) != "nimbus_vis" and iter in range(10):
        main_package = dirname(main_package)
        iter = iter + 1
    #
    if not main_package in sys.path:
        sys.path.append(main_package)
        print(main_package + " appended to sys path")
    #
    library = join(main_package, "libs")
    #
    if not library in sys.path:
        sys.path.append(library)
        print(library + " appended to sys path")
    #
    os.chdir(main_package) ###THIS IS VERY IMPORTANT AND FIXES EVERYTHING
#################################

import mido

##############VARS##############

input_list = None

################################


##############INIT##############

print("starting Nimbus MIDI....")
print("Starting mido, loading rtmidi backend...")
try: mido.Backend(load = True) #loads default backend, rt_midi
except ModuleNotFoundError:
    print("rtmidi not installed! This is a bug!!")
    raise Exception('LIB MISSING!!')
print("Backend loaded.")
print("Getting device list...")
print("...inputs...")

input_list = Input.getNames() ###Sets var with some defaults
print(input_list)

print("...outputs...")

output_list = Output.getNames) ###Sets var with some defaults
print(output_list()


print("Started!")

################################

##############DEFS##############

class DeviceInput():
    ##### MAKE PRIVATE Var
    target = None
    
    def getNames():
        return mido.get_input_names()
    
    def setDevice(name):
        if not name in getNames():
            target = None
            return None
        else: target = name
    
    def open(handler):
        if Input.target == None:
            raise Exception("Target Not Set!")
        mido.open_input(name = "")
        

class Output():