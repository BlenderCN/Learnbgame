import socket
import sys


def send_command(command):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('localhost', int(sys.argv[2])))
    clientsocket.sendall(command.encode())
    while True:
        res = clientsocket.recv(4096)
        if not res:
            break
        print(res.decode())
    clientsocket.close()

send_command("""exec(compile(open("{}", "rb").read(), filename, 'exec'), globals, locals)""".format(sys.argv[1]))
