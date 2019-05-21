# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Delicode NI mate Tools",
    "description": "Receives OSC and live feed data from the Delicode NI mate program",
    "author": "Janne Karhu (jahka)",
    "version": (1, 1),
    "blender": (2, 65, 0),
    "location": "View3D > Toolbar > NI mate Receiver & Game Engine",
    "category": "Animation",
    'wiki_url': '',
    'tracker_url': ''
    }

from mathutils import Vector
from mathutils import Matrix
from mathutils import Quaternion

import math
import struct
import socket
import subprocess, os
import mmap

try:
    import bge
    GE = True
except ImportError:
    GE = False
    import bpy
    from bpy.props import *

add_rotations = False
reset_locrot = False

def set_GE_location(objects, ob_name, vec, originals):
    ob = objects.get(ob_name)
    
    if ob != None:
        ob.localPosition = 10*vec

def set_GE_rotation(objects, ob_name, quat, originals):
    ob = objects.get(ob_name)
    
    if ob != None:
        if ob_name not in originals.keys():
            originals[ob_name] = ob.localOrientation.to_quaternion()

        if add_rotations:
            ob.localOrientation = quat * originals[ob_name]
        else:
            ob.localOrientation = quat

def set_location(objects, ob_name, vec, originals):
    if ob_name in objects.keys():
        if ob_name not in originals.keys():
            originals[ob_name] = objects[ob_name].location.copy()

        objects[ob_name].location = 10*vec
        
        if(bpy.context.scene.tool_settings.use_keyframe_insert_auto):
            objects[ob_name].keyframe_insert(data_path="location")

    elif bpy.context.scene.delicode_ni_mate_create != 'NONE':
        ob_type = bpy.context.scene.delicode_ni_mate_create
        if(ob_type == 'EMPTIES'):
            bpy.ops.object.add()
        elif(ob_type == 'SPHERES'):
            bpy.ops.mesh.primitive_ico_sphere_add()
        elif(ob_type == 'CUBES'):
            bpy.ops.mesh.primitive_cube_add()

        ob = bpy.context.object
        ob.name = ob_name
        ob.location = 10*vec

        if(bpy.context.scene.tool_settings.use_keyframe_insert_auto):
            objects[ob_name].keyframe_insert(data_path="location")

def set_rotation(objects, ob_name, quat, originals):
    if ob_name in objects.keys():
        objects[ob_name].rotation_mode = 'QUATERNION'

        if ob_name not in originals.keys():
            originals[ob_name] = objects[ob_name].rotation_quaternion.copy()

        if add_rotations:
            objects[ob_name].rotation_quaternion = quat * originals[ob_name]
        else:
            objects[ob_name].rotation_quaternion = quat
        
        if(bpy.context.scene.tool_settings.use_keyframe_insert_auto):
            objects[ob_name].keyframe_insert(data_path="rotation_quaternion")

def rotation_from_matrix(m00, m01, m02, m10, m11, m12, m20, m21, m22):
    mat = Matrix()
    mat[0][0] = m00
    mat[0][1] = m01
    mat[0][2] = m02
    mat[1][0] = m10
    mat[1][1] = m11
    mat[1][2] = m12
    mat[2][0] = m20
    mat[2][1] = m21
    mat[2][2] = m22

    return mat.to_quaternion()
            
class OSC():
    def readByte(data):
        length   = data.find(b'\x00')
        nextData = int(math.ceil((length+1) / 4.0) * 4)
        return (data[0:length], data[nextData:])

    
    def readString(data):
        length   = str(data).find("\0")
        nextData = int(math.ceil((length+1) / 4.0) * 4)
        return (data[0:length], data[nextData:])
    
    
    def readBlob(data):
        length   = struct.unpack(">i", data[0:4])[0]
        nextData = int(math.ceil((length) / 4.0) * 4) + 4
        return (data[4:length+4], data[nextData:])
    
    
    def readInt(data):
        if(len(data)<4):
            print("Error: too few bytes for int", data, len(data))
            rest = data
            integer = 0
        else:
            integer = struct.unpack(">i", data[0:4])[0]
            rest    = data[4:]
    
        return (integer, rest)
    
    
    def readLong(data):
        """Tries to interpret the next 8 bytes of the data
        as a 64-bit signed integer."""
        high, low = struct.unpack(">ll", data[0:8])
        big = (long(high) << 32) + low
        rest = data[8:]
        return (big, rest)
    
    
    def readDouble(data):
        """Tries to interpret the next 8 bytes of the data
        as a 64-bit double float."""
        floater = struct.unpack(">d", data[0:8])
        big = float(floater[0])
        rest = data[8:]
        return (big, rest)
    
    
    
    def readFloat(data):
        if(len(data)<4):
            print("Error: too few bytes for float", data, len(data))
            rest = data
            float = 0
        else:
            float = struct.unpack(">f", data[0:4])[0]
            rest  = data[4:]
    
        return (float, rest)
    
    def decodeOSC(data):
        table = { "i" : OSC.readInt, "f" : OSC.readFloat, "s" : OSC.readString, "b" : OSC.readBlob, "d" : OSC.readDouble }
        decoded = []
        address,  rest = OSC.readByte(data)
        typetags = ""
        
        if address == "#bundle":
            time, rest = readLong(rest)
            decoded.append(address)
            decoded.append(time)
            while len(rest)>0:
                length, rest = OSC.readInt(rest)
                decoded.append(OSC.decodeOSC(rest[:length]))
                rest = rest[length:]
    
        elif len(rest) > 0:
            typetags, rest = OSC.readByte(rest)
            decoded.append(address)
            decoded.append(typetags)
            
            if len(typetags) > 0:        
                if typetags[0] == ord(','):
                    for tag in typetags[1:]:
                        value, rest = table[chr(tag)](rest)
                        decoded.append(value)
                else:
                    print("Oops, typetag lacks the magic")
    
        return decoded

 
class NImateReceiver():
    original_rotations = {}
    original_locations = {}
    quit_port = None
    message_port = None
    profile_path = None

    def run(self, objects, set_location_func, set_rotation_func):
        location_dict = {}
        rotation_dict = {}
        
        try:
            data = self.sock.recv( 1024 )
        except:
            return {'PASS_THROUGH'}
        
        trash = data
        while(True):
            data = trash
            
            decoded = OSC.decodeOSC(data)
            ob_name = str(decoded[0], "utf-8")

            if len(decoded) == 5: #location
                location_dict[ob_name] = Vector([decoded[2], -decoded[4], decoded[3]])
            elif len(decoded) == 6: #quaternion
                rotation_dict[ob_name] = Quaternion((-decoded[2], decoded[3], -decoded[5], decoded[4]))
            elif len(decoded) == 9: #location & quaternion
                location_dict[ob_name] = Vector([decoded[2], -decoded[4], decoded[3]])
                rotation_dict[ob_name] = Quaternion((-decoded[5], decoded[6], -decoded[8], decoded[7]))
            elif len(decoded) == 11: #matrix
                rotation_dict[ob_name] = rotation_from_matrix(decoded[2], decoded[3], decoded[4], decoded[5], decoded[6], decoded[7], decoded[8], decoded[9], decoded[10])
            elif len(decoded) == 14: #location & matrix
                location_dict[ob_name] = Vector([decoded[2], -decoded[4], decoded[3]])
                quat = rotation_from_matrix(decoded[5], decoded[6], decoded[7], decoded[8], decoded[9], decoded[10], decoded[11], decoded[12], decoded[13])
                rotation_dict[ob_name] = Quaternion((quat.w, quat.x, -quat.z, quat.y))
            
            try:
                trash = self.sock.recv(1024)
            except:
                break
            
        for key, value in location_dict.items():
            set_location_func(objects, key, value, self.original_locations)
            
        for key, value in rotation_dict.items():
            set_rotation_func(objects, key, value, self.original_rotations)



    def __init__(self, UDP_PORT, QUIT_PORT, MESSAGE_PORT, PROFILE_PATH):
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(0)
        self.sock.bind( ("localhost", UDP_PORT) )

        self.quit_port = QUIT_PORT
        self.message_port = MESSAGE_PORT
        self.profile_path = PROFILE_PATH

        self.original_rotations = {}
        self.original_locations = {}
        
        print("Delicode NI mate Tools started listening to OSC on port " + str(UDP_PORT))
        
    def __del__(self):
        self.sock.close()
        print("Delicode NI mate Tools stopped listening to OSC")

        if self.quit_port != None:
            if self.quit_port >= 0:
                try:
                    quit_sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
                    quit_sock.sendto(b'/NI mate\x00\x00\x00\x00,s\x00\x00quit\x00\x00\x00\x00', ("127.0.0.1", self.quit_port) )

                    print("Quitting NI mate")
                except Exception as e:
                    print("Couldn't quit NI mate: %s" % e)
                    pass
        else:
            global reset_locrot
            if reset_locrot:
                for key, value in self.original_locations.items():
                    bpy.data.objects[key].location = value.copy()

                for key, value in self.original_rotations.items():
                    bpy.data.objects[key].rotation_quaternion = value.copy()

        if self.profile_path != None:
            try:
                with open(self.profile_path) as profile:
                   profile.close()
                   os.remove(self.profile_path)
            except IOError:
               pass # no file to delete

class DelicodeNImateFeed():
    image_texture = None
    file_map = None

    def run(self):
        if self.file_map != None:
            self.file_map.seek(0)
            buf = self.file_map.read(640*480*4)
            self.image_texture.source.load(buf, 640, 480)
            self.image_texture.refresh(True)

    def __init__(self, image_name, feed_2):
        import sys
        import bge
        from bge import texture
        import tempfile

        cont = bge.logic.getCurrentController()
        own = cont.owner

        try:
            matID = texture.materialID(own, image_name)
        except:
            print("Delicode NI mate Tools Error: No texture with name: " + image_name)
            pass
        
        try:
            self.image_texture = texture.Texture(own, matID)

            if feed_2:
                filename = "NI_mate_shared_map2.data"
            else:
                filename = "NI_mate_shared_map1.data"
        
            file = open(tempfile.gettempdir() + "/" + filename, "rb")
            if sys.platform.startswith('darwin') or sys.platform.startswith('Linux'):
                self.file_map = mmap.mmap(file.fileno(), 0, mmap.PROT_READ, mmap.ACCESS_READ)
            else:
                self.file_map = mmap.mmap(file.fileno(), 0, None, mmap.ACCESS_READ)
            file.close()

            self.file_map.seek(0)
            buf = self.file_map.read(640*480*4)

            self.image_texture.source = texture.ImageBuff()
            self.image_texture.source.filter = texture.FilterRGBA32()
            self.image_texture.source.load(buf, 640, 480)

            if feed_2:
                print("Delicode NI mate Tools replacing " + image_name + " with live feed 2")
            else:
                print("Delicode NI mate Tools replacing " + image_name + " with live feed 1")
        except Exception as e:
            print("Delicode NI mate Tools Error: Couldn't open NI mate feed " + tempfile.gettempdir() + "/" + filename)
            print("Reason: %s" % e)
            self.file_map = None
            pass

if not GE:
    class DelicodeNImateFeedPlaneCreate(bpy.types.Operator):
        bl_idname = "wm.delicode_ni_mate_feed_plane_create"
        bl_label = "Create feed plane"
        bl_description = "Create a new plane for NI mate live feed"
        bl_options = {'REGISTER'}
        
        def execute(self, context):
            bpy.ops.mesh.primitive_plane_add()
            plane = context.object
            plane.scale = Vector((4.0/3.0, 1.0, 1.0))

            if(context.scene.delicode_ni_mate_feed == 'FEED1'):
                feed_prefix = "NImateFeed1"
            else:
                feed_prefix = "NImateFeed2"

            plane.name = feed_prefix + "_Plane"
            
            if (feed_prefix + "_Image") not in bpy.data.images:
                bpy.ops.image.new(name=feed_prefix + "_Image", width=640, height=480, generated_type='UV_GRID')
            
            bpy.ops.mesh.uv_texture_add()
            plane.data.uv_textures[0].data[0].image = bpy.data.images[feed_prefix + "_Image"]

            mat = bpy.data.materials.new(feed_prefix + "_Material")
            mat.use_shadeless = True
            mat.use_transparency = True
            mat.alpha = 0.0

            tex = bpy.data.textures.new(feed_prefix + "_Texture", type = 'IMAGE')
            tex.image = bpy.data.images[feed_prefix + "_Image"]

            mtex = mat.texture_slots.add()
            mtex.texture = tex
            mtex.texture_coords = 'UV'
            mtex.use_map_alpha = True

            plane.data.materials.append(mat)
            
            bpy.ops.logic.sensor_add(name='SNImateFeed')
            plane.game.sensors['SNImateFeed'].use_pulse_true_level = True
            
            bpy.ops.logic.controller_add(name='CNImateFeed', type='PYTHON')
            plane.game.controllers['CNImateFeed'].mode = 'MODULE'
            plane.game.controllers['CNImateFeed'].module = 'animation_delicode_ni_mate_tools.updateFeed'
            plane.game.sensors['SNImateFeed'].link(plane.game.controllers['CNImateFeed'])
            
            bpy.ops.object.game_property_new(type='STRING', name='NImateFeedImage')
            plane.game.properties['NImateFeedImage'].value = feed_prefix + "_Image"
            context.scene.delicode_ni_mate_feed_image = feed_prefix + "_Image"
            
            bpy.ops.object.game_property_new(type='BOOL', name='NImateUseFeed2')
            plane.game.properties['NImateUseFeed2'].value = (context.scene.delicode_ni_mate_feed == 'FEED2')
            
            return {'FINISHED'}
        
    class DelicodeNImateFeedLogicCreate(bpy.types.Operator):
        bl_idname = "wm.delicode_ni_mate_feed_logic_create"
        bl_label = "Create game logic"
        bl_description = "Create or update game logic to replace an image with NI mate live feed for the selected object"
        bl_options = {'REGISTER'}

        @classmethod
        def poll(self, context):
            return context.object != None
        
        def execute(self, context):
            ob = context.object

            if 'SNImateFeed' not in ob.game.sensors:
                bpy.ops.logic.sensor_add(name='SNImateFeed')
            ob.game.sensors['SNImateFeed'].use_pulse_true_level = True
            
            if 'CNImateFeed' not in ob.game.controllers:
                bpy.ops.logic.controller_add(name='CNImateFeed', type='PYTHON')
            ob.game.controllers['CNImateFeed'].mode = 'MODULE'
            ob.game.controllers['CNImateFeed'].module = 'animation_delicode_ni_mate_tools.updateFeed'

            ob.game.sensors['SNImateFeed'].link(ob.game.controllers['CNImateFeed'])
            
            if 'NImateFeedImage' not in ob.game.properties:
                bpy.ops.object.game_property_new(type='STRING', name='NImateFeedImage')
            ob.game.properties['NImateFeedImage'].type = 'STRING'
            ob.game.properties['NImateFeedImage'].value = context.scene.delicode_ni_mate_feed_image
            
            if 'NImateUseFeed2' not in ob.game.properties:
                bpy.ops.object.game_property_new(type='BOOL', name='NImateUseFeed2')
            ob.game.properties['NImateUseFeed2'].type = 'BOOL'
            ob.game.properties['NImateUseFeed2'].value = (context.scene.delicode_ni_mate_feed == 'FEED2')
 
            return {'FINISHED'}

    class DelicodeNImateMessageLogicCreate(bpy.types.Operator):
        bl_idname = "wm.delicode_ni_mate_message_logic_create"
        bl_label = "Create game logic"
        bl_description = "Create or update game logic for sending an OSC message to NI mate. You can connect the resulting controller to any sensor."
        bl_options = {'REGISTER'}

        @classmethod
        def poll(self, context):
            return context.object != None

        def execute(self, context):
            ob = context.object

            if 'CNImateMessage' not in ob.game.controllers:
                bpy.ops.logic.controller_add(name='CNImateMessage', type='PYTHON')
            ob.game.controllers['CNImateMessage'].mode = 'MODULE'
            ob.game.controllers['CNImateMessage'].module = 'animation_delicode_ni_mate_tools.sendMessage'

            if 'NImateMessage' not in ob.game.properties:
                bpy.ops.object.game_property_new(type='STRING', name='NImateMessage')
            ob.game.properties['NImateMessage'].type = 'STRING'
            ob.game.properties['NImateMessage'].value = context.scene.delicode_ni_mate_current_message

            return {'FINISHED'}

    class DelicodeNImateReceiverLogicCreate(bpy.types.Operator):
        bl_idname = "wm.delicode_ni_mate_receiver_logic_create"
        bl_label = "Create game logic"
        bl_description = "Create or update game logic for NI mate receiver for the selected object"
        bl_options = {'REGISTER'}

        @classmethod
        def poll(self, context):
            return context.object != None
        
        def execute(self, context):
            ob = context.object

            if 'SNImateReceiver' not in ob.game.sensors:
                bpy.ops.logic.sensor_add(name='SNImateReceiver')
            ob.game.sensors['SNImateReceiver'].use_pulse_true_level = True
            
            if 'CNImateReceiver' not in ob.game.controllers:
                bpy.ops.logic.controller_add(name='CNImateReceiver', type='PYTHON')
            ob.game.controllers['CNImateReceiver'].mode = 'MODULE'
            ob.game.controllers['CNImateReceiver'].module = 'animation_delicode_ni_mate_tools.updateGE'

            ob.game.sensors['SNImateReceiver'].link(ob.game.controllers['CNImateReceiver'])
            
            if 'NImatePort' not in ob.game.properties:
                bpy.ops.object.game_property_new(type='INT', name='NImatePort')
            ob.game.properties['NImatePort'].type = 'INT'
            ob.game.properties['NImatePort'].value = context.scene.delicode_ni_mate_GE_port

            if 'NImateStart' not in ob.game.properties:
                bpy.ops.object.game_property_new(type='BOOL', name='NImateStart')
            ob.game.properties['NImateStart'].type = 'BOOL'
            ob.game.properties['NImateStart'].value = context.scene.delicode_ni_mate_start

            if 'CNImateProfile' not in ob.game.controllers:
                bpy.ops.logic.controller_add(name='CNImateProfile', type='PYTHON')
            ob.game.controllers['CNImateProfile'].mode = 'SCRIPT'
            ob.game.controllers['CNImateProfile'].text = bpy.data.texts[context.scene.delicode_ni_mate_start_profile]

            if 'NImateQuit' not in ob.game.properties:
                bpy.ops.object.game_property_new(type='BOOL', name='NImateQuit')
            ob.game.properties['NImateQuit'].type = 'BOOL'
            ob.game.properties['NImateQuit'].value = context.scene.delicode_ni_mate_quit

            if 'NImateQuitPort' not in ob.game.properties:
                bpy.ops.object.game_property_new(type='INT', name='NImateQuitPort')
            ob.game.properties['NImateQuitPort'].type = 'INT'
            ob.game.properties['NImateQuitPort'].value = context.scene.delicode_ni_mate_GE_quit_port

            if 'NImateMessages' not in ob.game.properties:
                bpy.ops.object.game_property_new(type='BOOL', name='NImateMessages')
            ob.game.properties['NImateMessages'].type = 'BOOL'
            ob.game.properties['NImateMessages'].value = context.scene.delicode_ni_mate_messages

            if 'NImateMessagePort' not in ob.game.properties:
                bpy.ops.object.game_property_new(type='INT', name='NImateMessagePort')
            ob.game.properties['NImateMessagePort'].type = 'INT'
            ob.game.properties['NImateMessagePort'].value = context.scene.delicode_ni_mate_GE_message_port

            if 'NImateAddRotations' not in ob.game.properties:
                bpy.ops.object.game_property_new(type='BOOL', name='NImateAddRotations')
            ob.game.properties['NImateAddRotations'].type = 'BOOL'
            ob.game.properties['NImateAddRotations'].value = context.scene.delicode_ni_mate_GE_add_rotations
 
            return {'FINISHED'}

    class DelicodeNImate(bpy.types.Operator):
        bl_idname = "wm.delicode_ni_mate_start"
        bl_label = "Delicode NI mate Start"
        bl_description = "Start receiving data from NI mate"
        bl_options = {'REGISTER'}
        
        enabled = False
        receiver = None
        timer = None
        
        def modal(self, context, event):
            if event.type == 'ESC' or not __class__.enabled:
                return self.cancel(context)
            
            if event.type == 'TIMER':
                self.receiver.run(bpy.data.objects, set_location, set_rotation)
            
            return {'PASS_THROUGH'}     

        def execute(self, context):
            __class__.enabled = True
            global add_rotations
            global reset_locrot
            add_rotations = bpy.context.scene.delicode_ni_mate_add_rotations
            reset_locrot = bpy.context.scene.delicode_ni_mate_reset
            self.receiver = NImateReceiver(context.scene.delicode_ni_mate_port, None, None, None)
            
            context.window_manager.modal_handler_add(self)
            self.timer = context.window_manager.event_timer_add(1/context.scene.render.fps, context.window)
            return {'RUNNING_MODAL'}
        
        def cancel(self, context):
            __class__.enabled = False
            context.window_manager.event_timer_remove(self.timer)
            
            del self.receiver
            
            return {'CANCELLED'}
        
        @classmethod
        def disable(cls):
            if cls.enabled:
                cls.enabled = False
                
    class DelicodeNImateStop(bpy.types.Operator):
        bl_idname = "wm.delicode_ni_mate_stop"
        bl_label = "Delicode NI mate Stop"
        bl_description = "Stop receiving data from NI mate"
        bl_options = {'REGISTER'}
        
        def execute(self, context):
            DelicodeNImate.disable()
            return {'FINISHED'}
        
    class VIEW3D_PT_DelicodeNImatePanel(bpy.types.Panel):
        bl_space_type = "VIEW_3D"
        bl_region_type = "TOOLS"
        bl_label = "NI mate Receiver"
        
        def draw(self, context):
            layout = self.layout
            
            scene = context.scene
            
            col = layout.column()
            col.enabled = not DelicodeNImate.enabled
            col.prop(scene, "delicode_ni_mate_port")
            col.label("Create:")
            row = col.row()
            row.prop(scene, "delicode_ni_mate_create", expand=True);
            row = col.row()
            row.prop(scene, "delicode_ni_mate_add_rotations")
            row.prop(scene, "delicode_ni_mate_reset")
            
            if(DelicodeNImate.enabled):
                layout.operator("wm.delicode_ni_mate_stop", text="Stop", icon='ARMATURE_DATA')
            else:
                layout.operator("wm.delicode_ni_mate_start", text="Start", icon='POSE_DATA')

    class VIEW3D_PT_DelicodeNImateGEPanel(bpy.types.Panel):
        bl_space_type = "VIEW_3D"
        bl_region_type = "TOOLS"
        bl_label = "NI mate Game Engine"
        
        def draw(self, context):
            layout = self.layout

            scene = context.scene

            layout.label("Receiver:")
            layout.prop(scene, "delicode_ni_mate_GE_port")

            row = layout.row(align=True)
            row.prop(scene, "delicode_ni_mate_start", toggle=True)
            col = row.column()
            col.enabled = scene.delicode_ni_mate_start
            col.prop_search(scene, "delicode_ni_mate_start_profile", bpy.data, "texts", text="")

            row = layout.row(align=True)
            row.prop(scene, "delicode_ni_mate_quit", toggle=True)
            col = row.column()
            col.enabled = scene.delicode_ni_mate_quit
            col.prop(scene, "delicode_ni_mate_GE_quit_port", text="Port")

            row = layout.row(align=True)
            row.prop(scene, "delicode_ni_mate_messages", toggle=True)
            col = row.column()
            col.enabled = scene.delicode_ni_mate_messages
            col.prop(scene, "delicode_ni_mate_GE_message_port", text="Port")

            layout.prop(scene, "delicode_ni_mate_GE_add_rotations")
            col = layout.column()
            if context.object != None and "CNImateReceiver" in context.object.game.controllers:
                col.operator("wm.delicode_ni_mate_receiver_logic_create", icon='FILE_REFRESH', text="Update game logic")
            else:
                col.operator("wm.delicode_ni_mate_receiver_logic_create", icon='GAME')
            
            layout.label("")

            row = layout.row()
            row.label("Live feed:")
            row.prop(scene, "delicode_ni_mate_feed", expand=True)
            layout.operator("wm.delicode_ni_mate_feed_plane_create", icon="TEXTURE")
            layout.prop_search(scene, "delicode_ni_mate_feed_image", bpy.data, "images", text="Or replace")
            col = layout.column()
            if context.object != None and "CNImateFeed" in context.object.game.controllers:
                col.operator("wm.delicode_ni_mate_feed_logic_create", icon='FILE_REFRESH', text="Update game logic")
            else:
                col.operator("wm.delicode_ni_mate_feed_logic_create", icon='GAME')

            layout.label("")

            row = layout.row()
            row.label("Messaging:")
            layout.prop(scene, "delicode_ni_mate_current_message")
            col = layout.column()
            if context.object != None and "CNImateMessage" in context.object.game.controllers:
                col.operator("wm.delicode_ni_mate_message_logic_create", icon='FILE_REFRESH', text="Update game logic")
            else:
                col.operator("wm.delicode_ni_mate_message_logic_create", icon='GAME')



    def quitPortChanged(self, context):
        scene = context.scene

        if scene.delicode_ni_mate_GE_message_port != scene.delicode_ni_mate_GE_quit_port:
            scene.delicode_ni_mate_GE_message_port = scene.delicode_ni_mate_GE_quit_port

    def messagePortChanged(self, context):
        scene = context.scene

        if scene.delicode_ni_mate_GE_quit_port != scene.delicode_ni_mate_GE_message_port:
            scene.delicode_ni_mate_GE_quit_port = scene.delicode_ni_mate_GE_message_port

    def init_properties():
        scene = bpy.types.Scene
        
        scene.delicode_ni_mate_port = bpy.props.IntProperty(
            name="Port",
            description="Receive OSC on this port, must match the Full Skeleton port in NI mate!",
            default = 7000,
            min = 0,
            max = 65535)

        scene.delicode_ni_mate_GE_port = bpy.props.IntProperty(
            name="Port",
            description="Receive OSC on this port, must match the Full Skeleton port in NI mate!",
            default = 7000,
            min = 0,
            max = 65535)

        scene.delicode_ni_mate_GE_quit_port = bpy.props.IntProperty(
            name="Quit Port",
            description="NI mate will receive the quit OSC message on this port, must match the OSC input port in NI mate preferences!",
            default = 7001,
            min = 0,
            max = 65535,
            update = quitPortChanged)

        scene.delicode_ni_mate_GE_message_port = bpy.props.IntProperty(
            name="Message Port",
            description="NI mate will receive OSC messages on this port, must match the OSC input port in NI mate preferences!",
            default = 7001,
            min = 0,
            max = 65535,
            update = messagePortChanged)

        scene.delicode_ni_mate_add_rotations = bpy.props.BoolProperty(
            name="Add Rotations",
            description="Add received rotation data to original rotations")

        scene.delicode_ni_mate_reset = bpy.props.BoolProperty(
            name="Reset",
            description="Reset original object locations and rotations after receiving is stopped",
            default=True)
        
        scene.delicode_ni_mate_create = bpy.props.EnumProperty(
            name="Create",
            items = [('NONE', 'Nothing', "Don't create objects based on received data"),
                    ('EMPTIES', 'Empties', 'Create empties based on received data'),
                    ('SPHERES', 'Spheres', 'Create spheres based on received data'),
                    ('CUBES', 'Cubes', 'Create cubes based on received data')])

        scene.delicode_ni_mate_feed_image = bpy.props.StringProperty(
            name="Image",
            description="Replace this image with the feed")
        
        scene.delicode_ni_mate_feed = bpy.props.EnumProperty(
            items = [('FEED1', '1', 'Feed 1'), ('FEED2', '2', 'Feed 2')],
            name="Feed")

        scene.delicode_ni_mate_start = bpy.props.BoolProperty(
            name="Start NI mate",
            description="Start NI mate when the game engine is started")

        scene.delicode_ni_mate_start_profile = bpy.props.StringProperty(
            name="NI mate profile",
            description="The profile text used to start NI mate (the first and last lines of the text must be triple-quotes \"\"\" as otherwise the text is interpreted as an invalid python script)")

        scene.delicode_ni_mate_quit = bpy.props.BoolProperty(
            name="Quit NI mate",
            description="Quit NI mate when the game engine quits"
            )

        scene.delicode_ni_mate_messages = bpy.props.BoolProperty(
            name="Enable messages",
            description="Enable sending of OSC messages back to NI mate"
            )

        scene.delicode_ni_mate_GE_add_rotations = bpy.props.BoolProperty(
            name="Add Rotations",
            description="Add received rotation data to original rotations")

        scene.delicode_ni_mate_current_message = bpy.props.StringProperty(
            name="Send",
            description="The OSC message to send to NI mate"
            )
            
    def clear_properties():
        scene = bpy.types.Scene
        
        del scene.delicode_ni_mate_port
        del scene.delicode_ni_mate_GE_port
        del scene.delicode_ni_mate_GE_quit_port
        del scene.delicode_ni_mate_GE_message_port

        del scene.delicode_ni_mate_quit
        del scene.delicode_ni_mate_messages
        del scene.delicode_ni_mate_start

        del scene.delicode_ni_mate_add_rotations
        del scene.delicode_ni_mate_reset
        del scene.delicode_ni_mate_GE_add_rotations
        del scene.delicode_ni_mate_create

        del scene.delicode_ni_mate_feed_image
        del scene.delicode_ni_mate_feed

        del scene.delicode_ni_mate_current_message
                
    def register():
            
        init_properties()
        bpy.utils.register_module(__name__)

    def unregister():
        bpy.utils.unregister_module(__name__)
        clear_properties()
        
    if __name__ == "__main__":
        register()



def setupGE(own):
    import bge
    import sys

    port = own.get('NImatePort', "")
    global add_rotations
    add_rotations = own.get('NImateAddRotations', False)

    profile_path = None
    
    if own.get('NImateStart', False) and 'CNImateProfile' in own.controllers:

        profile_text = own.controllers['CNImateProfile'].script

        profile_path = bge.logic.expandPath('//BlenderGameEngine.nimate')

        profile = open(profile_path, 'w')
        try:
            profile.truncate()
            profile.write(profile_text)
        finally:
            profile.close()

        try:
            if sys.platform.startswith('darwin') or sys.platform.startswith('Linux'):
                subprocess.call(('open', profile_path))
            elif os.name == 'nt':
                os.startfile(bge.logic.expandPath(profile_path))

            print("Starting NI mate with profile: " + str(profile_path))
        except Exception as e:
            print("Tried to start NI mate with profile: " + str(profile_path))
            print("...but couldn't because: %s" % e)
            pass

    quit_port = -1

    if own.get('NImateQuit', False):
        quit_port = own.get('NImateQuitPort', -1)

    message_port = -1;

    if own.get('NImateMessages', False):
        message_port = own.get('NImateMessagePort', -1)

    bge.logic.DelicodeNImate = NImateReceiver(port, quit_port, message_port, profile_path)
    
def sendMessage(controller):
    import bge

    print("sending message")
    
    if controller.owner.get('NImateMessage', False):
        msg = controller.owner.get('NImateMessage')

        print("message is" + msg)
        
        nulls = 4 - (len(msg) % 4)
        
        port = -1
        
        if hasattr(bge.logic, 'DelicodeNImate'):
            port = bge.logic.DelicodeNImate.message_port

        print("port is" + str(port))
        
        if port is not None and port > 0:
            sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
            sock.sendto(b'/NI mate\x00\x00\x00\x00,s\x00\x00' + str.encode(msg) + b'\x00' * nulls, ("127.0.0.1", port) )

def updateGE(controller):
    import bge

    if hasattr(bge.logic, 'DelicodeNImate') == False:
        setupGE(controller.owner)

    bge.logic.DelicodeNImate.run(bge.logic.getCurrentScene().objects, set_GE_location, set_GE_rotation)

def setupFeed(own):
    import bge

    feed_2 = own.get('NImateUseFeed2', False)
    feed_image = own.get('NImateFeedImage', 0)
    
    if isinstance(feed_image, str) == False:
        print("Delicode NI mate Tools Error: no image name defined with String property 'NImateFeedImage'!")
        return

    if feed_2:
        bge.logic.DelicodeNImateFeed2 = DelicodeNImateFeed("IM" + feed_image, True)
    else:
        bge.logic.DelicodeNImateFeed1 = DelicodeNImateFeed("IM" + feed_image, False)

def updateFeed(controller):
    import bge

    own = controller.owner

    feed_2 = own.get('NImateUseFeed2', False)

    if feed_2:
        if hasattr(bge.logic, 'DelicodeNImateFeed2') == False:
            setupFeed(own)
        else:
            bge.logic.DelicodeNImateFeed2.run()
    else:
        if hasattr(bge.logic, 'DelicodeNImateFeed1') == False:
            setupFeed(own)
        else:
            bge.logic.DelicodeNImateFeed1.run()