import bpy
from socket import *
import sys
from math import degrees
import time
from math import sqrt


class CheckPath(bpy.types.Operator):
    bl_idname = "object.checking_data"
    bl_label = "Check"
    bl_description = "Check path data"
    bl_options = {"REGISTER"}
    '''
    @classmethod
    def poll(cls, context):
        return True
    '''
    def execute(self, context):
        print('\n')
        print('NEW CYCLE !!!!!!!!!!!!!!!!!')
        print('\n')
        
        data = bpy.data
        scene = context.scene
        
        fps = scene.render.fps
        frame_current = scene.frame_current
        frame_start = scene.frame_start
        frame_end = scene.frame_end
        frame_range = frame_end - frame_start
        
        send_data_frame_range = str(frame_range)
        send_data_fps = str(fps)
        
        obj = context.object
        #obj_loc = obj.matrix_world.translation
        obj_loc = obj.location
        #obj_loc = [round(obj_loc[0],4),round(obj_loc[1],4),round(obj_loc[2],4)]
        obj_rot = obj.rotation_euler
        #obj_rot = [round(obj_rot[0],4),round(obj_rot[1],4),round(obj_rot[2],4)]
        
        separator = ','
        
        def measure(first, second):
            locx = second[0] - first[0]
            locy = second[1] - first[1]
            locz = second[2] - first[2]
            distance = sqrt((locx)**2 + (locy)**2 + (locz)**2) 
            #print('distance', distance) # Debug
            return distance
        
        obj_matrix = obj.matrix_world.translation
        link5_matrix = scene.objects['KUKA_6'].matrix_world.translation
        
        
        if scene.sendData:
            # SOCKET:
            host = 'localhost'
            port = 5000
            addr = (host,port)
            udp = socket(AF_INET, SOCK_DGRAM)
            udp.bind(('',5001))
            udp.connect(addr)
            
####UDP#### METHOD
            udp.send(str.encode('1'))
            time.sleep(0.001)
            
####UDP#### FRAME RANGE
            udp.send(str.encode(send_data_frame_range))
            time.sleep(0.001)
            
####UDP#### FPS
            udp.send(str.encode(send_data_fps))
            time.sleep(0.001)
            
        if scene.printSendData:
            print(send_data_frame_range) # Debug
            print(send_data_fps) # Debug
        
        for frame in range(frame_start,frame_end):
            scene.frame_set(frame)
            send_data = ''
            send_data = send_data + str(context.object.matrix_world.translation[0])
            send_data = send_data + separator + str(context.object.matrix_world.translation[1])
            send_data = send_data + separator + str(context.object.matrix_world.translation[2])
            
            send_data = send_data + separator + str(degrees(context.object.matrix_world.to_euler('XYZ')[0])) # B axis
            send_data = send_data + separator + str(degrees(context.object.matrix_world.to_euler('XYZ')[1])) # C axis
            send_data = send_data + separator + str(degrees(context.object.matrix_world.to_euler('XYZ')[2])) # A axis
            
            if measure(obj_matrix, link5_matrix) > 0.001:
                scene.checkResult = "ERROR at " + str(frame) + " frame!"
                #print("NO NO NO NO NO NO NO") # Debug
                scene.frame_set(frame-1)
                bpy.data.scenes[scene.name].timeline_markers.new('error', frame)
                break
            else:
                scene.checkResult = "PATH IS OK!"
                #print("YES YES YES") # Debug
        
            
            if scene.printSendData:
                print('SEND: ', frame, ' ', send_data) # Debug
            
            if scene.sendData:
                send_data = str.encode(send_data)
                udp.send(send_data)
                time.sleep(0.001)
            
            #distance = sqrt((locx)**2 + (locy)**2 + (locz)**2) 
            
        # RECEIVE
        if scene.recieveData:
            receive = udp.recv(1024)
            scene.checkResult = bytes.decode(receive) # DECODE !!!
            print(receive) # Debug
            udp.close()
        elif scene.sendData:
            udp.close()
        
        return {"FINISHED"}

class CheckA1_to_A6(bpy.types.Operator):
    bl_idname = "object.check_a1_to_a6"
    bl_label = "Check A..."
    bl_description = ""
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        scene = context.scene
        
        fps = scene.render.fps
        frame_current = scene.frame_current
        
        if scene.currentFrame:
            frame_start = frame_current
            frame_end = frame_current + 1
        else:
            frame_start = scene.frame_start
            frame_end = scene.frame_end
        
        frame_range = frame_end - frame_start
        
        send_data_frame_range = str(frame_range)
        send_data_fps = str(fps)
        '''
        # LIMITATION
        a1_limit = 360
        a2_limit = 300
        a3_limit = 360
        a4_limit = 381
        a5_limit = 388
        a6_limit = 615
        '''    
        '''
        def set_A12346(a1,a2,a3,a4,a5,a6):
            a1 = round(degrees(scene.objects['A1'].matrix_world.to_euler('XYZ')[2]),4) # 0
            a6 = round(degrees(scene.objects['A6'].matrix_world.to_euler('XYZ')[2]),4) # 0
            a6 = a6 - a1
            
            a2 = round(degrees(scene.objects['A2'].matrix_world.to_euler('XYZ')[1]),4) # -90
            a3 = round(degrees(scene.objects['A3'].matrix_world.to_euler('XYZ')[1]) - degrees(scene.objects['a2_constr'].matrix_world.to_euler('XYZ')[1]), 4)
            a5 = round(degrees(scene.objects['A5'].matrix_world.to_euler('XYZ')[1]),4) # 90
            a5 = a5-a3-a2
            
            a4 = round(degrees(scene.objects['A4'].matrix_world.to_euler('XYZ')[0]),4) # 0
            
            #A3 = round(degrees(scene.objects['A3'].matrix_world.to_euler('XYZ')[1]),4) # 90
            return [A1,A2,A3,A4,A5,A6]
        '''
        ####################################################################
        def check_limitation(FPS,FRAME, current_array):
            limits = (360, 300, 360, 381, 388, 615)
            bpy.context.scene.frame_set(FRAME + 1)
            
            a1next = round(degrees(scene.objects['A1'].matrix_world.to_euler('XYZ')[2]),4) # 0
            a6next = round(degrees(scene.objects['A6'].matrix_world.to_euler('XYZ')[2]),4) # 0
            a6next = a6next - a1next
            
            a2next = round(degrees(scene.objects['A2'].matrix_world.to_euler('XYZ')[1]),4) # -90
            a3next = round(degrees(scene.objects['A3'].matrix_world.to_euler('XYZ')[1]),4) - 90 - A2
            a5next = round(degrees(scene.objects['A5'].matrix_world.to_euler('XYZ')[1]),4) # 90
            a5next = a5next-a3next-a2next
            
            a4next = round(degrees(scene.objects['A4'].matrix_world.to_euler('XYZ')[0]),4) # 0
            
            
            next_array = [a1next,a2next,a3next,a4next,a5next,a6next] # set_A12346(a1next,a2next,a3next,a4next,a5next,a6next) # 
            for a in range(len(current_array)):
                print('\nA' + str(a+1) + ':')
                print('current = ', current_array[a])
#                print('next = ', next_array[a])
#                print('limit = ', limits[a])
                
                if current_array[a] < next_array[a]:
                    print(abs((current_array[a] - next_array[a])*FPS))
                    if (abs((current_array[a] - next_array[a])*FPS)) > limits[a]:
                        print('ERROR!!!\n')
                        return False
                    else:
                        print('1 < 2 \n')
                
                if next_array[a] < current_array[a]:
                    print(abs((next_array[a] - current_array[a])*FPS))
                    if abs((next_array[a] - current_array[a])*FPS) > limits[a]:
                        print('ERROR!!!\n')
                        return False
                    else:
                        print('1 > 2 \n')
                        
            bpy.context.scene.frame_set(FRAME)
            return True
            
        ########################################################
        
        if scene.sendData:
            # SOCKET:
            host = 'localhost'
            port = 5000
            addr = (host,port)
            udp = socket(AF_INET, SOCK_DGRAM)
            udp.bind(('',5001))
            udp.connect(addr)
            
####UDP#### METHOD
            udp.send(str.encode('2'))
            time.sleep(0.001)
            
####UDP#### FRAME RANGE
            udp.send(str.encode(send_data_frame_range))
            time.sleep(0.001)
            
####UDP#### FPS
            udp.send(str.encode(send_data_fps))
            time.sleep(0.001)
        
        
        for frame in range(frame_start,frame_end):
            scene.frame_set(frame)
            
            A1 = -round(degrees(scene.objects['A1'].matrix_world.to_euler('XYZ')[2]),4) # 0
            A6 = round(degrees(scene.objects['A6'].matrix_world.to_euler('XYZ')[2]),4) # 0
            A6 = A6 - A1
            
            A2 = round(degrees(scene.objects['A2'].matrix_world.to_euler('XYZ')[1]),4) # -90
            A3 = round(degrees(scene.objects['A3'].matrix_world.to_euler('XYZ')[1]),4) - 90 - A2
            A5 = round(degrees(scene.objects['A5'].matrix_world.to_euler('XYZ')[1]),4) # 90
            A5 = A5-A3-A2
            
            A4 = round(degrees(scene.objects['A4'].matrix_world.to_euler('XYZ')[0]),4) # 0
            
            #A3 = round(degrees(scene.objects['A3'].matrix_world.to_euler('XYZ')[1]),4) # 90
            
            a1_to_6 = [A1,A2,A3,A4,A5,A6] # set_A12346(A1,A2,A3,A4,A5,A6)
            
            scene.A_1 = A1
            scene.A_2 = A2
            scene.A_3 = A3
            scene.A_4 = A4
            scene.A_5 = A5
            scene.A_6 = A6
            
            if scene.checkLimit:
                check_limitation(fps, frame, a1_to_6) # CHECK LIMIT ! ! !
            
                if check_limitation(fps, frame, a1_to_6):
                    scene.checkResult = "PATH IS OK!"
                    print("YES YES YES") # Debug
                else:
                    scene.checkResult = "ERROR at " + str(frame) + " frame!"
                    print("NO NO NO NO NO NO NO") # Debug
                    scene.frame_set(frame-1)
                    bpy.data.scenes[scene.name].timeline_markers.new('speed error', frame)
                    break
            
            send_data = ''
            sep = ','
            send_data = send_data + str(A1)
            send_data = send_data + sep + str(A2)
            send_data = send_data + sep + str(A3)
            send_data = send_data + sep + str(A4)
            send_data = send_data + sep + str(A5)
            send_data = send_data + sep + str(A6)
            
            if scene.printSendData: # Debug
                print('\nFrame = ', frame)
                #print('\n', 'A1 = ',A1,'\n', 'A2 = ',A2,'\n', 'A3 = ',A3,'\n', 'A4 = ',A4,'\n', 'A5 = ',A5,'\n', 'A6 = ',A6,'\n', )
                print(send_data)
                print('\n','\n')
            
            if scene.sendData:
                send_data = str.encode(send_data)
                udp.send(send_data)
                time.sleep(0.001)
            
        # RECEIVE
        if scene.recieveData:
            receive = udp.recv(1024)
            scene.checkResult = bytes.decode(receive) # DECODE !!!
            print(receive) # Debug
            udp.close()
        elif scene.sendData:
            udp.close()
        return {"FINISHED"}
    
class RT_PrintToUI(bpy.types.Operator):
    bl_idname = "object.rt_print_to_ui"
    bl_label = "Rt Print To Ui"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    
    
    @classmethod
    def poll(cls, context):
        return True
        
    def modal(self, context, event):
        scene = context.scene
        print(scene.frame_current) # Debug
        
####### SET A1 TO A6
        A1 = -round(degrees(scene.objects['A1'].matrix_world.to_euler('XYZ')[2]),4) # 0
        A6 = round(degrees(scene.objects['A6'].matrix_world.to_euler('XYZ')[2]),4) # 0
        A6 = A6 - round(degrees(scene.objects['A1'].matrix_world.to_euler('XYZ')[2]),4)
        
        A2 = round(degrees(scene.objects['A2'].matrix_world.to_euler('XYZ')[1]),4) # -90
        A3 = round(degrees(scene.objects['A3'].matrix_world.to_euler('XYZ')[1]),4) - 90 - A2 # -90
        #A3 = round(degrees(scene.objects['A3'].matrix_world.to_euler('XYZ')[1]) - degrees(scene.objects['a2_constr'].matrix_world.to_euler('XYZ')[1]), 4)
        A5 = round(degrees(scene.objects['A5'].matrix_world.to_euler('XYZ')[1]),4) # 90
        A5 = A5-A3-A2
        A4 = round(degrees(scene.objects['A4'].matrix_world.to_euler('XYZ')[0]),4) # 0
                    
        scene.A_1 = A1
        scene.A_2 = A2
        scene.A_3 = A3
        scene.A_4 = A4
        scene.A_5 = A5
        scene.A_6 = A6
        # SET A1 TO A6 #############################
        a1_to_6 = [A1,A2,A3,A4,A5,A6] # set_A12346(A1,A2,A3,A4,A5,A6)    
        
        fps = scene.render.fps
        frame_current = scene.frame_current
        
        if check_limitation(fps, frame_current, a1_to_6):
            scene.modalErrors = '=)'
        else:
            scene.modalErrors = '=('
            
####### UPDATE UI
        context.area.tag_redraw()
        
        if scene.modalPrint:
            print('RUNNING')
        else:
            return {"CANCELLED"}
        
        if event.type in {"RIGHTMOUSE", "ESC"}:
            return {"CANCELLED"}
            
        return {"RUNNING_MODAL"}
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        
        #set up timer to window manager
        #self.timer = context.window_manager.event_timer_add(1/60, context.window)
        
        print('RUN')
        return {"RUNNING_MODAL"}
        
        
#def axiesUpdate():
#    scene = bpy.context.scene
#    scene.A_1 = 666#round(degrees(scene.objects['A1'].matrix_world.to_euler('XYZ')[2]),4)
#    context.area.tag_redraw()

####################################################################

def check_limitation(FPS,FRAME, current_array):
    scene = bpy.context.scene
    limits = (360, 300, 360, 381, 388, 615)
    bpy.context.scene.frame_set(FRAME + 1)
            
    a1next = round(degrees(scene.objects['A1'].matrix_world.to_euler('XYZ')[2]),4) # 0
    a6next = round(degrees(scene.objects['A6'].matrix_world.to_euler('XYZ')[2]),4) # 0
    a6next = a6next - a1next
            
    a2next = round(degrees(scene.objects['A2'].matrix_world.to_euler('XYZ')[1]),4) # -90
    a3next = round(degrees(scene.objects['A3'].matrix_world.to_euler('XYZ')[1]) - degrees(scene.objects['a2_constr'].matrix_world.to_euler('XYZ')[1]), 4)
    a5next = round(degrees(scene.objects['A5'].matrix_world.to_euler('XYZ')[1]),4) # 90
    a5next = a5next-a3next-a2next
            
    a4next = round(degrees(scene.objects['A4'].matrix_world.to_euler('XYZ')[0]),4) # 0
            
            
    next_array = [a1next,a2next,a3next,a4next,a5next,a6next] # set_A12346(a1next,a2next,a3next,a4next,a5next,a6next) # 
    for a in range(len(current_array)):
        print('\nA' + str(a+1) + ':')
        print('current = ', current_array[a])
                
        if current_array[a] < next_array[a]:
            print(abs((current_array[a] - next_array[a])*FPS))
            if (abs((current_array[a] - next_array[a])*FPS)) > limits[a]:
                print('ERROR!!!\n')
                return False
            else:
                print('1 < 2 \n')
                
        if next_array[a] < current_array[a]:
            print(abs((next_array[a] - current_array[a])*FPS))
            if abs((next_array[a] - current_array[a])*FPS) > limits[a]:
                print('ERROR!!!\n')
                return False
            else:
                print('1 > 2 \n')
                        
        bpy.context.scene.frame_set(FRAME)
    return True
            
        ########################################################
       