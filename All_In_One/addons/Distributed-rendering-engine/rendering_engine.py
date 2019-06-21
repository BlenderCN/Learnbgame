import bpy
import dre
from dre.operators import GlobalData,ReceiveDataServiceThread
import socket
import time
import os

class DistributedRenderingEngine(bpy.types.RenderEngine):  # every rendering engine should inherit 'bpy.types.RenderEngine'
    bl_idname = 'DRE_RENDER'
    bl_label = "DRE"
    bl_use_preview = True

    def render(self, scene):
        MasterConfigs=scene.MasterConfigs
        scene.render.filepath=MasterConfigs.path
        if MasterConfigs.path == "":
            self.report({'ERROR'},'Enter Valid path')
        elif not GlobalData.RegisteredSlaves :
            self.report({'ERROR'},'No slaves registered')
        elif MasterConfigs.self_address=='[default]':
            self.report({'ERROR'},'No ip address specified !')
        else:
            bpy.ops.wm.save_as_mainfile(filepath=MasterConfigs.path+'/file.blend')

            start=scene.frame_start
            last=scene.frame_end
            n=len(GlobalData.RegisteredSlaves)
            number_of_frames = last - start + 1
            steps = int(number_of_frames / n )
            end=start+steps-1

            for i,val in enumerate(GlobalData.RegisteredSlaves):
                if i == n-1 :
                    self._send_job(val,start,last,scene)
                else:
                    self._send_job(val,start,end,scene)
                    start=end+1
                    end=start+steps-1

            self._start_receiving_service(scene,n)

    def _send_job(self,ip,start,end,scene):

        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        clientsocket.connect((ip,int(scene.MasterConfigs.port_no)))
        print('connected to '+ip+':'+scene.MasterConfigs.port_no)
        
        clientsocket.send(str(start).encode('ascii'))
        print(clientsocket.recv(1024).decode('ascii'))
        clientsocket.send(str(end).encode('ascii'))
        print(clientsocket.recv(1024).decode('ascii'))

        f = open(scene.MasterConfigs.path+'/file.blend','rb')
        print('sending file')
        l = f.read(1024)
        while (l):
            clientsocket.send(l)
            l = f.read(1024)
        f.close()
        print("Done Sending file")
        clientsocket.close()

    def _start_receiving_service(self,scene,num_of_slaves):
        MasterConfigs=scene.MasterConfigs

        directory=MasterConfigs.path+'DRE_output/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        ip = MasterConfigs.self_address

        port = int(MasterConfigs.port_no)+1
        
        server_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_socket.bind((ip, port))
        except socket.gaierror :
            self.report({'ERROR'},'Can not start service on '+MasterConfigs.self_address
                        +':'+str(port))
            return
        except OSError as e:
            self.report({'ERROR'},'Can not start service on '
                                +MasterConfigs.self_address
                                +'\n'+str(e))
            return

        server_socket.listen(10)                             
        t=ReceiveDataServiceThread(ip,port,server_socket,num_of_slaves,directory)
        t.start()
