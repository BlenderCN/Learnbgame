import bpy
import threading,socket,subprocess
from bpy.props import *
from bpy.types import CollectionProperty
from dre.configs import *    

class GlobalData:
    MasterServiceThread=None
    SlaveServiceThread=None
    Slave_isRegistered=False
    RegisteredSlaves=set()

class StartMasterService_operator(bpy.types.Operator):
    bl_idname = "action.start_service"
    bl_label = "Start Master"

    def execute(self, context):
        MasterConfigs=context.scene.MasterConfigs

        ip = MasterConfigs.self_address  
        if ip=='[default]':
            self.report({'ERROR'},'No ip address specified !')
            return {'CANCELLED'} 

        port = int(MasterConfigs.port_no)
        
        server_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_socket.bind((ip, port))
        except socket.gaierror :
            self.report({'ERROR'},'Can not start service on '+MasterConfigs.self_address)
            return {'CANCELLED'}
        except OSError as e:
            self.report({'ERROR'},'Can not start service on '
                                +MasterConfigs.self_address
                                +'\n'+str(e))
            return {'CANCELLED'}

        server_socket.listen(5)                             
        t=MasterServiceThread(ip,port,server_socket)
        t.start()
        GlobalData.MasterServiceThread=t

        return{'FINISHED'}

class StopMasterService_operator(bpy.types.Operator):
    bl_idname = "action.stop_service"
    bl_label = "Stop Master"

    def execute(self, context):
        GlobalData.MasterServiceThread=None

        MasterConfigs=context.scene.MasterConfigs

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        ip=MasterConfigs.self_address
        port=int(MasterConfigs.port_no)
        sock.connect((ip,port))
        sock.send('STOP SERVICE'.encode('ascii'))
        sock.close()

        return{'FINISHED'}
        
class RegisterSlave_operator(bpy.types.Operator):
    bl_idname = "action.register_with_master"
    bl_label = 'Register with Master'

    def execute(self,context):
        SlaveConfigs=context.scene.SlaveConfigs

        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        ip=SlaveConfigs.master_address
        port=int(SlaveConfigs.port_no)

        try:
            clientsocket.connect((ip,port))
            print("....connected to master")
        except socket.gaierror:
            self.report({'ERROR'},'No master running at '+ip+':'+str(port))
            return {'CANCELLED'}
        except ConnectionRefusedError as e:
            self.report({'ERROR'},str(e))
            return {'CANCELLED'}
        except OSError as e:
            self.report({'ERROR'},str(e))
            return {'CANCELLED'}

        clientsocket.send('REGISTER'.encode('ascii'))
        response=clientsocket.recv(1024).decode('ascii')
        print('...... message from master : ',response)
        if response=='REGISTERED SUCCESS':
            GlobalData.Slave_isRegistered=True
            SlaveConfigs=context.scene.SlaveConfigs

            ip = SlaveConfigs.self_address  
            if ip=='[default]':
                self.report({'ERROR'},'No ip address specified !')
                return {'CANCELLED'} 

            port = int(SlaveConfigs.port_no)
            
            server_socket = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)
            try:
                server_socket.bind((ip, port))
            except socket.gaierror :
                self.report({'ERROR'},'Can not start service on '+ip)
                return {'CANCELLED'}
            except OSError as e:
                self.report({'ERROR'},'Can not start service on '
                                    +ip
                                    +'\n'+str(e))
                return {'CANCELLED'}

            server_socket.listen(5)                             
            t=SlaveServiceThread(ip,port,server_socket,SlaveConfigs)
            t.start()
            GlobalData.SlaveServiceThread=t

            clientsocket.close()
            return{'FINISHED'}

        else:
            self.report({'ERROR'},'Slave Registration failed')
            clientsocket.close()
            return {'CANCELLED'}

        clientsocket.close()
        return {'FINISHED'}

class UnRegisterSlave_operator(bpy.types.Operator):
    bl_idname = "action.unregister_with_master"
    bl_label = 'Un-Register with Master'

    def execute(self,context):
        SlaveConfigs=context.scene.SlaveConfigs

        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        ip=SlaveConfigs.master_address
        port=int(SlaveConfigs.port_no)

        try:
            clientsocket.connect((ip,port))
            print("....connected to master")
        except socket.gaierror:
            self.report({'ERROR'},'No master running at '+ip+':'+str(port))
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'},str(e))
            return {'CANCELLED'}

        clientsocket.send('UNREGISTER'.encode('ascii'))
        response=clientsocket.recv(1024).decode('ascii')
        print('....message from server : ',response)
        if response=='UNREGISTERED SUCCESS':
            GlobalData.Slave_isRegistered=False

            GlobalData.SlaveServiceThread=None

            SlaveConfigs=context.scene.SlaveConfigs

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            ip=SlaveConfigs.self_address
            port=int(SlaveConfigs.port_no)
            sock.connect((ip,port))
            sock.send('STOP SERVICE'.encode('ascii'))
            sock.close()
        else:
            self.report({'ERROR'},'Un Register Failed')
            clientsocket.close()
            return {'CANCELLED'}

        return {'FINISHED'}

class PrintRegisteredSlaves_operator(bpy.types.Operator):
    """docstring for PrintRegisteredSlaves_operator"""
    bl_idname = "action.print_registered_slaves"
    bl_label = 'Print slaves on terminal'

    def execute(self,context):
        print(GlobalData.RegisteredSlaves)
        return {'FINISHED'}      

class MasterServiceThread(threading.Thread):
    """docstring for MasterServiceThread"""
    def __init__(self,ip,port,socket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        print("[+] Master Service Started on "+ip+":"+str(port))

    def run(self):
        while True:
            # establish a connection
            clientsocket,addr = self.socket.accept()      

            response=clientsocket.recv(1024).decode('ascii')
            print("[+] message form "+str(addr[0])+" : ",response)
            if response=='REGISTER':
                GlobalData.RegisteredSlaves.add(addr[0])
                print(GlobalData.RegisteredSlaves)
                print('\tslave registered')
                clientsocket.send('REGISTERED SUCCESS'.encode('ascii'))

            elif response=='UNREGISTER':
                GlobalData.RegisteredSlaves.remove(str(addr[0]))
                clientsocket.send('UNREGISTERED SUCCESS'.encode('ascii'))
                print(GlobalData.RegisteredSlaves)

            elif response=='STOP SERVICE':
                clientsocket.close()
                break

            else:
                clientsocket.send('INVALID REQUEST'.encode('ascii'))

            clientsocket.close()

        print('[+] Master Service Stopped')

class SlaveServiceThread(threading.Thread):
    """docstring for MasterServiceThread"""
    def __init__(self,ip,port,socket,SlaveConfigs):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        self.SlaveConfigs=SlaveConfigs
        print("[+] Slave Service Started on "+ip+":"+str(port))

    def run(self):
        clientsocket,addr = self.socket.accept()      

        self.start_frame=clientsocket.recv(1024).decode('ascii')
        print('start ',self.start_frame)
        clientsocket.send('OK'.encode('ascii'))
        self.end_frame=clientsocket.recv(1024).decode('ascii')
        print('end' ,self.end_frame)
        clientsocket.send('OK 2'.encode('ascii'))

        f = open(self.SlaveConfigs.path+'slavefile.blend','wb')
        l = clientsocket.recv(1024)
        print("Receiving file...")
        while (l):
            f.write(l)
            l = clientsocket.recv(1024)
        f.close()
        print("Done Receiving")

        clientsocket.close()

        print("[+] Slave Service Stopped for "+self.ip+":"+str(self.port))  

        self._render()

        self._send_output()

    def _render(self):
        blender_path = os.getcwd() + '/blender'
        file_path = self.SlaveConfigs.path + 'slavefile.blend'
        start_frame = self.start_frame
        end_frame = self.end_frame

        subprocess.call([blender_path, "-b",file_path,'-E','CYCLES','-o',
                    self.SlaveConfigs.path + 'output/',
                    '-s',start_frame,'-e',end_frame,'-a'])

    def _send_output(self):
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        clientsocket.connect((self.SlaveConfigs.master_address,
                            int(self.SlaveConfigs.port_no)+1))

        clientsocket.send('FILE'.encode('ascii'))

        path=self.SlaveConfigs.path+'output/'

        filesList=os.listdir(path)
        for file in filesList:
            print(clientsocket.recv(1024).decode('ascii'))
            clientsocket.send(file.encode('ascii'))
            print(clientsocket.recv(1024).decode('ascii'))

            f = open(path+file,'rb')
            print('sending file',file)
            l = f.read(1024)
            while (l):
                clientsocket.send(l)
                l = f.read(1024)
            f.close()
            print(file,'sent')
            print(clientsocket.recv(1024).decode('ascii'))
            if file == filesList[-1]:
                clientsocket.send('NO'.encode('ascii'))
            else:
                clientsocket.send('YES'.encode('ascii'))
            
        clientsocket.close()

class ReceiveDataServiceThread(threading.Thread):
    """docstring for MasterServiceThread"""
    def __init__(self,ip,port,socket,num_of_slaves,output_path):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        self.num_of_slaves=num_of_slaves
        self.output_path=output_path
        print("[+] Data receiving Service Started on "+ip+":"+str(port))

    def run(self):
        while self.num_of_slaves != 0:
            # establish a connection
            clientsocket,addr = self.socket.accept() 

            clientsocket.settimeout(5)  

            response=clientsocket.recv(1024).decode('ascii')
            print('msg from slave : ',response)
            if response == 'FILE':
                while True:
                    clientsocket.send('SEND FILE NAME'.encode('ascii'))
                    file_name=clientsocket.recv(1024).decode('ascii')
                    print("Receiving file : ",file_name)
                    clientsocket.send('OK'.encode('ascii'))

                    f = open(self.output_path+file_name,'wb')
                    l = clientsocket.recv(1024)
                    
                    while (l):
                        f.write(l)
                        try:
                            l = clientsocket.recv(1024)
                        except socket.timeout:
                            break
                    f.close()
                    print("Done Receiving",file_name)
                    clientsocket.send('MORE'.encode('ascii'))
                    response=clientsocket.recv(1024).decode('ascii')
                    if response == 'NO':
                        break

                self.num_of_slaves -= 1
            elif response == 'STOP SERVICE':
                print('ll')
                self.num_of_slaves=0
            else:
                clientsocket.send('INVALID MESSAGE'.encode('ascii'))


            clientsocket.close()



        print('[+] Data receiving Service Stopped')

class StopDataReceivingService_operator(bpy.types.Operator):
    bl_idname = "action.stop_data_receiving_service"
    bl_label = "Stop Data Receiving Service"

    def execute(self, context):

        MasterConfigs=context.scene.MasterConfigs

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        sock.settimeout(1)
        ip=MasterConfigs.self_address
        port=int(MasterConfigs.port_no)+1
        sock.connect((ip,port))
        sock.send('STOP SERVICE'.encode('ascii'))
        sock.close()

        return{'FINISHED'}





