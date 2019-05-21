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




##################################################
################# N O T   D O N E #########################
##################################################






import argparse

from threading import Thread
#for client
from pythonosc import dispatcher, udp_client

#################################

#thread name is "nimbus_osc_client".

#################################


########DECLARATIONS########
a_parser = argparse.ArgumentParser()
disp = dispatcher.Dispatcher()
############################


############ARGS############
a_parser.add_argument(
    "--ip",
    default = "127.0.0.1",
    help = "The ip the server listens on.",
    )
a_parser.add_argument(
    "--port",
    type = int,
    default = 5505,
    help = "The port the server listens on.",
    )
args = a_parser.parse_args()
############################


############VARS############
up_address = [None, None] #[next_address[0], next_address[1]]
next_address = [None, None]
server = None
thread = None
killer_client = None
############################


########DISPATCHER##########
#Sets up dispatcher, which is used to map commands.
class Dispatch():    
    def printAll(unused_addr, text):
        print(text)
    def shutdown(unused_addr, code):
        
        stop_code_def = StopCode.getStopCodeDef(code)
        print(
            
            """
            Shutdown requested with stop code {0}.\n
            Code {0}: {1}\n
            Terminating...
            """.format(code, StopCode.getStopCodeDef(code))
            )

class StopCode():
    
    code_dict = { #Use this to set up mapings
        
        "0" : "Closed normally."
        
        }
    
    def getStopCodeDef(stop_code):
        stop_code = str(stop_code)
        try:
            return StopCode.code_dict[stop_code]
        except KeyError:
            return "Stop code does not exist."
        
#mapping happens here
#disp.map("/nimbus", Dispatch.printAll)#placeholder

####################
###DON"T CHANGE THIS EVER
disp.map("/nimbus/server/stop", Dispatch.shutdown)
############################


###########CLASSES##########

class Address():

    def set(ip = "", port = ""): 
        """
        Sets defaults which are used the next time the server is started.\n
        usage: set(ip (str), port (int))\n
        if None is entered, it defaults to\n
        an ip of '127.0.0.1' and a port of 5505.\n
        if one or both of the arguments is left blank,\n
        that parameter will remain unchanged. 
        """
        
        global next_address

        try:
            port = int(port)
        except ValueError:
            pass
        
        
        if ip == None:
            next_address[0] = args.ip
        if port == None:
            next_address[1] = args.port
        if ip == "":
            pass
        if port == "":
            pass
        if ip != None and ip != "":
            next_address[0] = ip
        if port != None and port != "":
            next_address[1] = port
        
    def getNext(call):
        """
        Gets the next address
        that will be used to start the server.
        Args can be 'ip' and / or 'port'.\n
        Returns None if server is not online.
        """
        global next_address

        call = str(call)
        call = call.lower()
        print(call)
        output = []

        if "ip" in call:
            output.append(next_address[0])
        if "port" in (call):
            output.append(next_address[1])
        if not "ip" or "port" in call:
            print(
                """
                No valid address selector listed!\n
                Args can be 'ip' and / or 'port'.
                """,
                )
            return None
        return output
    def getCurrent(call):
        """
        Gets the address of the running server, if anything.
        Args can be 'ip' and / or 'port'.\n
        Returns None if server is not online.
        """
        global up_address
        
        call = str(call)
        call = call.lower()
        print(call)
        output = []
        
        if isUp() == True:
            if "ip" in call:
                output.append(address[0])
            if "port" in (call):
                output.append(address[1])
            if not "ip" or "port" in call:
                print(
                    """
                    No valid address selector listed!\n
                    Args can be 'ip' and or 'port'.
                    """,
                    )
            return output
            
        if isUp() != True:
            print("Server not running!")
            return None

    def get(text = ""):
        """
        Shortener function for getCurrent()
        """
        return Address.getCurrent(text)

############################


#########FUNCTIONS##########

def isUp():
    global thread
    try:
        up_status = thread.is_alive()
        return up_status
    except AttributeError:
        print("thread doesn't point to anything! Is the server initialised?")

def start():
    """
    This starts the OSC Server. It has no usable derivatives. \n
    Can not be run if server is already up, will return False.\n
    Takes no arguments.\n
    Returns, as a list:\n
    ---The server's status as a boolean\n
    ---The ip and port as a nested list
    """
    global server
    global disp
    global next_address
    global thread
    global up_port
    global up_address

    temp_up_status = isUp()
    if temp_up_status != True:   
        if next_address[0] == None:
            next_address[0] = args.ip #antiquated, but can protect in case of bad things
        if next_address[1] == None:
            next_address[1] = args.port #antiquated, but can protect in case of bad things

        server = None
        thread = None
        server = osc_server.ThreadingOSCUDPServer(
            (next_address[0], next_address[1]),
            disp,
            )
        
        thread = Thread(
            #Calling it this way forces it to either work, or throw an exception.
            target = server.serve_forever, #No maybe!
            name = "nimbus_osc_server",
            daemon = True,
            )
        print("Starting Server!")
        thread.start()

        print("Binding current ip and port to up_address[0,1]")
        up_address[0] = next_address[0]
        up_address[1] = next_address[1]
        return [isUp(), up_address]
    elif isUp() == True:
        print("Server already running!")
    
def stop(stop_code = 0):
    """
    Used to kill the running server.\n
    Usage: stop(stop_code = 0)
    """
    global up_address
    
    if server != None:
        if isUp() == True:
            killer_client = udp_client.SimpleUDPClient(up_address[0], up_address[1])
            print("Sending Kill Signal...")
            killer_client.send_message("/nimbus/server/stop", str(stop_code))
        elif isUp() == False:
            print("Server is already stopped.")
        return isUp()
    elif server == None:
        print("Server has never been started!")

############################
