import socket
import bpy


def queue_command(command, buffersize=None, port=None):
    """
    Add a command to commands queue of the command port. 
    This function can be used like executeDeferred in Maya: 
    * to run commands later, after current task or
    * to send command from a thread and evaluate in in the main thread of application safely.

    :param command: String with a command that will be executed
    :type command: unicode
    :param buffersize: Size of a socket buffer
    :type buffersize: int
    :param port: Port at which blender command port is working
    :type port: int
    """
    if port is None:
        port = bpy.Scene.bcp_port
    if buffersize is None:
        buffersize = bpy.Scene.bcp_buffersize

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(("127.0.0.1", port))

    soc.send(command.encode("utf8"))
    result_bytes = soc.recv(buffersize)
    result_string = result_bytes.decode("utf8")

    print("Result from server is {}".format(result_string))


def close_command_port():
    try:
        if not bpy.context.window_manager.keep_command_port_running:
            print("Port is not running")
            return False
        bpy.context.window_manager.keep_command_port_running = False
        print("Command port closed")
        return True
    except NameError:
        print("Port is not running. It was never initialized.")
        return False
