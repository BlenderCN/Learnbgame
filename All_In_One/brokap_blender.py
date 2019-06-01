bl_info = {
    "name": "Brokap",
    "description": "Receives motion capture data from the xbox 360 kinect",
    "author": "Werner Mendizabal (nonameentername)",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "View3D > Toolbar > Brokap Receiver",
    "category": "Learnbgame",
    'wiki_url': '',
    'tracker_url': ''
}

import bpy
import json
import socket
from bgl import *
from mathutils import Matrix


def set_bone_location(armature, name, location):
    x, y, z = location
    armature.data.edit_bones[name].head.xyz = (x, y, z)
    armature.data.edit_bones[name].tail.xyz = (x, y + 1, z)

def get_bone_location(armature, name):
    return armature.data.edit_bones[name].head.xyz

class BrokapUI(bpy.types.Panel):
    bl_label = "Brokap Receiver"
    bl_idname = "brokapui"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Brokap"
    bl_context = "objectmode"

    def __init__(self):
        super(BrokapUI, self).__init__()

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Brokap panel", icon="CAMERA_DATA")

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        split = row.split(percentage=0.5)
        colL = split.column()
        colR = split.column()

        colL.operator('brokapui.create', text='create', icon='ARMATURE_DATA')

        row = layout.row()
        split = row.split(percentage=0.5)

        colL = split.column()
        colR = split.column()

        colL.operator('brokapui.start', text='start', icon='PLAY') #PAUSE
        colR.operator('brokapui.stop', text='stop', icon='PAUSE')

class BrokapUI_create(bpy.types.Operator):
    bl_label = "Brokap create armature"
    bl_idname = 'brokapui.create'
    bl_description = 'Create armature bones'

    def __init__(self):
        super(BrokapUI_create, self).__init__()
        self.ITEMS = [
            'Head',
            'Neck',
            'Torso',
            'Left_Shoulder',
            'Left_Elbow',
            'Left_Hand',
            'Right_Shoulder',
            'Right_Elbow',
            'Right_Hand',
            'Left_Hip',
            'Left_Knee',
            'Left_Foot',
            'Right_Hip',
            'Right_Knee',
            'Right_Foot'
        ]

    def invoke(self, context, event):
        self.report({'INFO'}, 'create trackers')
        for name in self.ITEMS:
            bpy.ops.object.empty_add()
            bpy.context.active_object.name = name
        return {'FINISHED'}


class BrokapUI_start(bpy.types.Operator):
    bl_label = "Brokap start"
    bl_idname = 'brokapui.start'
    bl_description = 'Start kinect tracking'

    _timer = None

    def __init__(self):
        UDP_PORT = 7000
        self.sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(0)
        self.sock.bind( ("127.0.0.1", UDP_PORT) )

    def __del__(self):
        pass

    def modal(self, context, event):
        if not bpy.types.brokapui.active:
            context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}
        elif event.type == 'ESC':
            context.window_manager.event_timer_remove(self._timer)
            return {'CANCELLED'}
        elif event.type == 'TIMER':
            receive = True

            try:
                data = json.loads(self.sock.recv( 1024 ))
            except:
                data = None
                receive = False

            while receive:
                print ('running')
                name = data['name']
                position = data['position']
                rotation = data['rotation']
                bpy.data.objects[name].location = position
                bpy.data.objects[name].rotation_quaternion = Matrix(rotation).to_quaternion()

                try:
                    data = json.loads(self.sock.recv( 1024 ))
                except:
                    break

        return {'PASS_THROUGH'}

    def execute(self, context):
        bpy.types.brokapui.active = True

        context.window_manager.modal_handler_add(self)
        self.report({'INFO'}, 'start kinect tracking')
        self._timer = context.window_manager.event_timer_add(0.1, context.window)
        return {'RUNNING_MODAL'}


class BrokapUI_stop(bpy.types.Operator):
    bl_label = "Brokap stop"
    bl_idname = 'brokapui.stop'
    bl_description = 'Stop kinect tracking'

    def invoke(self, context, event):
        self.report({'INFO'}, 'stop kinect tracking')
        bpy.types.brokapui.active = False
        return {'FINISHED'}

def register():
    bpy.utils.register_class(BrokapUI)
    bpy.utils.register_class(BrokapUI_create)
    bpy.utils.register_class(BrokapUI_start)
    bpy.utils.register_class(BrokapUI_stop)


def unregister():
    bpy.utils.unregister_class(BrokapUI)
    bpy.utils.unregister_class(BrokapUI_create)
    bpy.utils.unregister_class(BrokapUI_start)
    bpy.utils.unregister_class(BrokapUI_stop)


if __name__ == "__main__":
    register()
