import argparse

from multiprocessing import Process, Pipe
from pythonosc import dispatcher, osc_server

#####################################
###Adds some arguments for starting the server
parser = argparse.ArgumentParser()
parser.add_argument(
    "--ip",
    default="127.0.0.1", 
    help="The ip to listen on",
    )
parser.add_argument(
    "--port",
    type=int, 
    default=5005, 
    help="The port to listen on",
    )
args = parser.parse_args()

#######################
###Some functions for the dispatcher later on
def print_volume_handler(unused_addr, args, volume):
  print("[{0}] ~ {1}".format(args[0], volume))

def print_compute_handler(unused_addr, args, volume):
  try:
    print("[{0}] ~ {1}".format(args[0], args[1](volume)))
  except ValueError: pass



###Sets up dispatcher as disp
disp = dispatcher.Dispatcher()
disp.map("/filter", print)

###################Classes########################
###Sets up listening server as osc_serv_target
class OscServer: #made with multiprocessing and magic <3
    #process name is "nimbus_osc_server".
    
    oscStatus = None
    osc_serv_target = None
    disp = None
    oscProcess = None
    
    def isUp(): #returns status of osc server
        """
        Checks the osc server is running.\n
        No arguments.\n
        Returns True or False.\n
        If osc_status is not initialised as a global,\n
        it will initialise it as None.
        """
        ####Some error handling
        if not oscStatus in globals():
            oscStatus = None
        try: #exception handler in case of bad token
            status = osc_serv_target.is_alive()    ###The real code <--
            return status
        except AttributeError:
            print(
                "OSC Server never / improperly "
                "linked to thr_osc_serv!"
                )
        
    def setProperties(address = [args.ip, args.port]): 
        """
        Sets defaults which are used the next time the server is started.
        usage: setProperties(address = [ip, port])
        Defaults to an ip of 127.0.0.1 and a port of 5505
        """
        global osc_serv_target
        global disp
        #creates token and assigns it to thr_osc_server
        osc_serv_target = osc_server.ThreadingOSCUDPServer(
            (address[0], address[1]), disp)
    
    def start():
        """
        This starts the OSC Server. It has no usable derivatives. \n
        It takes no arguments, and returns the server's status (bool),\n
        pid, and address.
        """
        
        def startServ():
            """
            Please don't call this.
            """
            global osc_serv_target
            global oscProcess
            osc_serv_target.serve_forever()

        oscProcess = Process(
            target = startServ,
            name = "nimbus_osc_server",
            daemon = True,
            )
        oscProcess.start()
    
    def stop():
        global oscProcess
        oscProcess.terminate()
        return isUp()

###################################
#enables standalone support
if __name__ == "__main__":
    import os
    import sys
    from os.path import dirname, join
    try:
        import bpy
        mainPackage = dirname(bpy.data.filepath)
    except ModuleNotFoundError:
        from os.path import abspath
        #This line changes based on where the meta package is
        mainPackage = dirname(dirname(abspath(__file__)))  
    if not mainPackage in sys.path:
        sys.path.append(mainPackage)
        print(mainPackage + " appended to sys path")
    library = join(mainPackage, "libs")
    if not library in sys.path:
        sys.path.append(library)
        print(library + " appended to sys path")
    os.chdir(mainPackage) ###THIS IS VERY IMPORTANT AND FIXES EVERYTHING
    ######    
    #extra file-specific stuff
    extr = join(mainPackage, "extranious")
    if not extr in sys.path:
        sys.path.append(extr)
        print(extr + " appended  to sys path")
        os.chdir(extr)
#################################