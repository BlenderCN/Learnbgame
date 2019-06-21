from bge import logic as gl
from .evertims import Evertims

IP_EVERT = 'localhost' # EVERTims client IP address
PORT_W = 3858 # port used by EVERTims client to read data sent by the BGE
IP_LOCAL = 'localhost' # local host (this computer) IP address, running the BGE
PORT_R = 3862 # port used by the BGE to read data sent by the EVERTims client
DEBUG = True # enable / disable console log
MOVE_UPDATE_THRESHOLD_VALUE_LOC = 1.0 # minimum value a listener / source must move to be updated on EVERTims client (m)
MOVE_UPDATE_THRESHOLD_VALUE_ROT = 5.0 # minimum value a listener / source must rotate to be updated on EVERTims client (deg)

def init(cont):

    # get main evertims module
    gl.evertims = Evertims()

    # set debug mode
    gl.evertims.setDebugMode(DEBUG)

    # define EVERTs elements: room, listener and source
    scene = gl.getCurrentScene()
    gl.evertims.addRoom(scene.objects['Room'])
    gl.evertims.addSource(scene.objects['source'])
    gl.evertims.addListener(scene.objects['listener_1'])

    # limit listener / source position updates in EVERTims Client
    gl.evertims.setMovementUpdateThreshold(MOVE_UPDATE_THRESHOLD_VALUE_LOC, MOVE_UPDATE_THRESHOLD_VALUE_ROT)

    # init newtork connections
    gl.evertims.initConnection_write(IP_EVERT, PORT_W)
    gl.evertims.initConnection_read(IP_LOCAL, PORT_R)

    # activate raytracing
    gl.evertims.activateRayTracingFeedback(True)

    # check if evertims module is ready to start
    if gl.evertims.isReady():
        # start EVERTims client
        gl.evertims.startClientSimulation()

    else:
        print ('\n###### EVERTims SIMULATION ABORTED ###### \nYou should create at least 1 room, 1 listener, 1 source, \nand define EVERTims client parameters.\n')
        gl.endGame() # quit game


