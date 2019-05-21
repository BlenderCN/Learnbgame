import bpy
import serial
import time
import os
from math import degrees

bl_info = {
    "name": "ServoControl",
    "author": "<author>",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}

class Servos:
    servo_list = []
    def build(mode): 
        if (mode == "man"):
            Servos.arm_bones = bpy.context.scene.objects['Armature'].pose.bones
            Servos.rig = 'Armature'
            
            Servos.servo_count = 6 
            #                    ^^ Set to how many servos you plan to run
            # Define your servos here (copy or delete these lines as you need)        Reverse
            Servos.servo_list.append(Servo('neck', 2, False, 90))
            #                                   name of bone^^^^   Axis of rotation^          ^^ Home position
            Servos.servo_list.append(Servo('neck', 0, True, 90))
            #...for every servo
            Servos.servo_list.append(Servo('eye_top', 0, False, 90))
            Servos.servo_list.append(Servo('eye', 2, False, 90))
            Servos.servo_list.append(Servo('eye', 0, False, 90))
            Servos.servo_list.append(Servo('eye_bottom', 0, False, 90))
						
        else: 
            # attempt to read external file first
            if (os.path.exists(mode)): 
                mode_file = open(mode, "r")
                bpy.context.scene.robot_servo_data = mode_file.read()
                mode_file.close()
            
            # set global info, chop off first armature line
            servo_config_lines = bpy.context.scene.robot_servo_data.split("\n")
            Servos.rig = servo_config_lines[0]
            Servos.arm_bones = bpy.context.scene.objects[servo_config_lines[0]].pose.bones
            servo_config_lines = servo_config_lines[1:-1]
            Servos.servo_count = len(servo_config_lines)
            
            if (StoresStuff.debug): 
                print("DEBUG: Servo build: config file")
                print(servo_config_lines)
            
            # add servos to the class
            for line in servo_config_lines: 
                servo_props = line.split(" ")
                Servos.servo_list.append(Servo( \
                    servo_props[0], \
                    int(servo_props[1]), \
                    bool(servo_props[2]), \
                    int(servo_props[3])))
    
    def update():
        for servo in Servos.servo_list:
            servo.source = \
                Servos.arm_bones[servo.source_bone].rotation_euler[servo.source_axis]
    
    def export(filepath):
        export_file = bpy.context.scene.robot_global_source + "\n"
        
        for servo in Servos.servo_list:
            export_file += \
                str(servo.source_bone) + " " + \
                str(servo.source_axis) + " " + \
                str(servo.reversed) + " " + \
                str(servo.home) + "\n"           
                
            if (StoresStuff.debug): print("DEBUG: export data\n" + export_file) 
            if (filepath == ""): bpy.context.scene.robot_servo_data = export_file
            elif (os.path.exists(filepath)): 
                filewriter = open(filepath, "w")
                filewriter.write(export_file)
                filewriter.close()
            else: print("EXPORT SERVOS: invalid string input")
        

class ServoInterface:
    def set_rig():
        Servos.arm_bones = \
            bpy.context.scene.objects[bpy.context.scene.robot_global_source].pose.bones
    # makes sure Servos.servo_count and the acutal servo list match up  
    def fit_servos():
        while (Servos.servo_count != len(Servos.servo_list)):
            if (Servos.servo_count > len(Servos.servo_list)):
                Servos.servo_list.append(Servo('', 0, False, 90))
                if (StoresStuff.debug): print("DEBUG: fit: added servos\n")
            if (Servos.servo_count < len(Servos.servo_list)):
                del Servos.servo_list[-1]
                if (StoresStuff.debug): print("DEBUG: fit: removed servos\n")
    def get_servo_data(channel):
        try:
            servo = Servos.servo_list[channel]
            return [
                servo.source_bone, 
                str(servo.home), 
                str(servo.reversed), 
                str(servo.source_axis)]
        except IndexError:
            return ['']
    
    def set_servo_source(channel, src): 
        Servos.servo_list[channel].source_bone = src
    
    def set_servo_home(channel, home_pos):
        Servos.servo_list[channel].home = home_pos
    
    def set_servo_reverse(channel, reverse):
        Servos.servo_list[channel].reversed = reverse
        
    def set_servo_axis(channel, ax):
        Servos.servo_list[channel].source_axis = ax
    
    
class Servo:
    def __init__(self, src, src_xyz, rev, hm):
        #self.source = src
        self.source_bone = src
        self.source_axis = src_xyz
        self.reversed = rev
        self.home = hm
        self.position = self.home
    

#Draws GUI, defines Blender Props
class RobotPanel(bpy.types.Panel):
    bl_label = "Servo Control"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        self.layout.operator("robot.animate", text='Play Animation')
        
        col = self.layout.column(align = True)        
        col.prop(context.scene, "robot_debug")
        col.label(text = bpy.context.scene.robot_message)
        col.prop(context.scene, "robot_port")
        col.prop(context.scene, "robot_port_rate")
        col.operator("robot.connect", text='(Dis)Connect')
        
        row = self.layout.row()        
        
        col2 = self.layout.column(align = True)        
        col2.label(text = "Source Armature")
        col2.prop(context.scene, "robot_global_source")
        col2.label(text = "Channel Config")
        col2.prop(context.scene, "robot_channel_count")
        col2.prop(context.scene, "robot_channel")
        
        row2 = self.layout.row()
        row2.operator("robot.read_servo", text = "Read")
        row2.operator("robot.write_servo", text = "Write")
        
        col3 = self.layout.column(align = True)
        col3.prop(context.scene, "robot_channel_source")
        col3.prop(context.scene, "robot_channel_home")
        col3.prop(context.scene, "robot_channel_axis")
        col3.prop(context.scene, "robot_channel_reverse")

    def register():
        bpy.types.Scene.robot_servo_data = bpy.props.StringProperty()
        bpy.types.Scene.robot_debug = bpy.props.BoolProperty \
            (
                name = "Debug",
                description = "dump to terminal instead of sending serial data",
                default = False
            )
        bpy.types.Scene.robot_channel = bpy.props.IntProperty \
            ( 
                name = "Edit",
                description = "set the servo channel you want to edit here",
                default = 1
            )
        bpy.types.Scene.robot_channel_count = bpy.props.IntProperty \
            ( 
                name = "Channels",
                description = "total amount of servo channels",
                default = 1
            )     
        bpy.types.Scene.robot_channel_axis = bpy.props.IntProperty \
            ( 
                name = "Axis",
                description = "axis of rotation (0-X, 1-Y, 2-Z)",
                default = 0
            )       
        bpy.types.Scene.robot_channel_reverse = bpy.props.BoolProperty \
            (
                name = "Reversed",
                description = "check if servo moves backwards of what's expected",
                default = False
            )
        bpy.types.Scene.robot_channel_home = bpy.props.IntProperty \
            (
                name = "HomePos",
                description = "Degrees added to frame bone position",
                default = 90
            )
        bpy.types.Scene.robot_channel_source = bpy.props.StringProperty \
            (
                name = "SourceBone",
                default = "bone"
            )
        bpy.types.Scene.robot_global_source = bpy.props.StringProperty \
            (
                name = "Source",
                default = "Armature"
            )
        bpy.types.Scene.robot_connected = bpy.props.BoolProperty \
            (
                name = "ConnectionStatus",
                default = 0
            )
        bpy.types.Scene.robot_message = bpy.props.StringProperty \
            (
                name = "Message",
                default = ""
            )
        bpy.types.Scene.robot_port_rate = bpy.props.IntProperty \
            (
                name = "PortRate",
                description = "Set the Serial port Speed (baudrate) here",
                default = 38400
            )
        bpy.types.Scene.robot_port = bpy.props.StringProperty \
            (
               name = "Port",
               description = "Set the Serial Port to access the robot here",
               default = "/dev/ttyUSB0"
            )
            

class StoresStuff:
    debug = False # bpy.context.scene.robot_debug 
    
    def print_connected(): 
        bpy.context.scene.robot_message = "Connected"
        bpy.context.scene.robot_connected = 1

    def print_disconnected(fail):
        if (fail): bpy.context.scene.robot_message = "Connect Failure"
        else: bpy.context.scene.robot_message = "Disconnected"
        bpy.context.scene.robot_connected = 0
    

class PlaysAnimation:
    # stops servo movement
    @classmethod
    def cancel(self): 
        cancel_str = ''
        for sv in range(0, Servos.servo_count):
            cancel_str += '-1 0 '
        if (StoresStuff.debug): print((cancel_str + '\n'))
        else: StoresStuff.ser.write((cancel_str + '\n').encode())
    
    # gets per-servo data for given frame, formats and commits to arduino   
    @classmethod
    def update_frame(self, frame, fps):      
        send_str = ''
        new_servo_pos = []
        Servos.update()
        
        for sv in range(0, Servos.servo_count):
            curr_servo = Servos.servo_list[sv]
            new_servo_pos.append(curr_servo.home + degrees(curr_servo.source))
            send_str += self.gen_servo_args(
                curr_servo.position, 
                new_servo_pos[sv], 
                curr_servo.reversed, 
                fps) + ' '
            curr_servo.position = new_servo_pos[sv]
        
        if (StoresStuff.debug): print (send_str + '\n')
        else: StoresStuff.ser.write((send_str + '\n').encode())
    
    # plays entire animation on arduino 
    # note this holds up the thread (time.sleep()) so the UI goes unresponsive
    @classmethod
    def play(self, fps):
        for frame in range(StoresStuff.start, StoresStuff.end):
            bpy.context.scene.frame_set(frame)
          
            if (not bpy.context.scene.robot_connected and not StoresStuff.debug):
                bpy.context.scene.robot_message = "No Connection!"
                return
              
            print ('frame ' + str(frame) + '\n')
            
              
            if (frame == StoresStuff.end - 1):
                self.cancel()
                return
              
            self.update_frame(frame, StoresStuff.fps)
            time.sleep(1 / StoresStuff.fps)
            
    # converts a servo position for current and last frame into velocity/direction string
    @classmethod
    def gen_servo_args(self, start_pos, end_pos, reverse, fps): #todo: add revese
        print("start_pos: " + str(start_pos))
        print("end_pos: " + str(end_pos))
        deg_sec = (end_pos - start_pos) * fps
        print("deg_sec" + str(deg_sec))
        if (deg_sec == 0): return '-1 0'
        if ((deg_sec < 0 and not reverse)): 
            return str(int(deg_sec * -1)) + ' 1'
        elif ((deg_sec > 0 and reverse)):
            return str(int(deg_sec)) + ' 1'
        elif ((deg_sec < 0 and reverse)):
            return str(int(deg_sec * -1)) + ' 0'
        else: return str(int(deg_sec)) + ' 0'

# Following classes are input handlers
class ConnectButton(bpy.types.Operator):
    bl_idname = "robot.connect"
    bl_label = "Connect"
    def execute(self, context):
    
        if (bpy.context.scene.robot_connected):
            try: 
                StoresStuff.print_disconnected(False)
                StoresStuff.ser.close()

                return{'FINISHED'}
            except: 
                bpy.context.scene.robot_message = "Disconnect Failure"

                return{'FINISHED'}
        try: 
            StoresStuff.ser = serial.Serial(bpy.context.scene.robot_port, 
                bpy.context.scene.robot_port_rate)
            StoresStuff.print_connected()                   
            
            return{'FINISHED'}
        except: 
            StoresStuff.print_disconnected(True)
            
            return{'FINISHED'}  
     

class PlayAnimButton(bpy.types.Operator):
    bl_idname = "robot.animate"
    bl_label = "Play"  
	
    def execute(self, context): 
        Servos.build("") # in order to remember servo config after re-opening blender 
        StoresStuff.fps = bpy.context.scene.render.fps
        StoresStuff.start = bpy.context.scene.frame_start
        StoresStuff.end = bpy.context.scene.frame_end
        PlaysAnimation.play(StoresStuff.fps)
        return{'FINISHED'}
        

class ReadServoButton(bpy.types.Operator):
    bl_idname = "robot.read_servo"
    bl_label = "Read Servo"
    
    def execute(self, context):
        # Builds servo data if it hasn't already been done
        try:
            bpy.context.scene.robot_channel_count = Servos.servo_count
        except AttributeError:
            Servos.build("")
            bpy.context.scene.robot_channel_count = Servos.servo_count
        
        sv_data = ServoInterface.get_servo_data(bpy.context.scene.robot_channel - 1)
        if (StoresStuff.debug): print ("DEBUG: Servo data read: " + str(sv_data) + "\n")
        bpy.context.scene.robot_channel_source = sv_data[0]
        bpy.context.scene.robot_channel_home = int(sv_data[1])
        bpy.context.scene.robot_channel_reverse = (sv_data[2] == "True")
        bpy.context.scene.robot_channel_axis = int(sv_data[3])
        
        return{'FINISHED'}
   
      
class WriteServoButton(bpy.types.Operator):
    bl_idname = "robot.write_servo"
    bl_label = "Write Servo"
    
    def execute(self, context):
        Servos.servo_count = bpy.context.scene.robot_channel_count 
        ServoInterface.fit_servos()
        ServoInterface.set_rig()
        
        ServoInterface.set_servo_source \
            (bpy.context.scene.robot_channel - 1, bpy.context.scene.robot_channel_source)
        ServoInterface.set_servo_home \
            (bpy.context.scene.robot_channel - 1, bpy.context.scene.robot_channel_home)
        ServoInterface.set_servo_reverse \
            (bpy.context.scene.robot_channel - 1, bpy.context.scene.robot_channel_reverse)
        ServoInterface.set_servo_axis \
            (bpy.context.scene.robot_channel - 1, bpy.context.scene.robot_channel_axis)
            
        Servos.export("");
             
        return{'FINISHED'}

classes = (
    ReadServoButton,
    WriteServoButton,
    RobotPanel,
    ConnectButton,
    PlayAnimButton,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
if __name__ == "__main__":
    register()