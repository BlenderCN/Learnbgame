#
# @file    tools/plugin/blender/Shadow/mDevice.py
# @author  Luke Tokheim, luke@motionshadow.com
# @version 2.5
#
# (C) Copyright Motion Workshop 2017. All rights reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Motion Workshop, which is protected by
# US federal copyright law and by international treaties.
#
# The Data may not be disclosed or distributed to third parties, in whole
# or in part, without the prior written consent of Motion Workshop.
#
# The Data is provided "as is" without express or implied warranty, and
# with no claim as to its suitability for any purpose.
#

import copy
import os
import threading
from xml.etree.ElementTree import XML

import bpy
from mathutils import Quaternion, Vector
from . import MotionSDK as SDK


#
# Motion SDK I/O thread. Blocks while reading samples over data stream.
#
class mDevice(threading.Thread):
    def __init__(self):
        # Must construct the Thread base class.
        super().__init__()

        # Recursive mutex. Protect the data and quit flag members.
        self.__lock = threading.RLock()
        self.__condition = threading.Condition(self.__lock)
        self.__data = {}
        self.__xml = ""
        self.__quit = False

    def __del__(self):
        self.close()

        if self.is_alive():
            self.join()

    def run(self):
        """
        Thread function. Read data over the Motion Service stream as quickly as
        possible. Save the most recent sample received for access from other
        threads. Throw away older samples assuming that we are previewing.
        """
        client = SDK.Client("127.0.0.1", 32076)

        # Request the channels we are interested in from the Motion
        # Configurable data service. Only get every other frame (~50 Hz) and
        # request inactive dummy nodes as well.
        #   [Local quaternion, positional constraint]
        xml = (
            b"<configurable stride=\"2\" inactive=\"1\">"
            b"<Lq/><c/></configurable>"
        )
        client.writeData(xml)

        while True:
            data = client.readData()
            if data is None:
                # Empty message. Could be a time out.
                continue

            if data.startswith(b"<?xml"):
                with self.__lock:
                    # XML message.
                    self.__xml = data.decode()
                continue

            with self.__lock:
                if self.__quit:
                    break

                # Probably not necessary to make the deep copy but be clear on
                # the intent.
                self.__data = copy.deepcopy(data)

                # Notify any consumers blocking on some data.
                self.__condition.notify_all()

        client.close()

    def close(self):
        """
        Set the quit flag. Next iteration in the thread loop will stop
        exection of the thread. Can be called from any thread.
        """
        with self.__lock:
            self.__quit = True

    def get_data(self):
        data = {}
        xml = ""
        with self.__lock:
            data = copy.deepcopy(self.__data)
            xml = copy.deepcopy(self.__xml)

        return (data, xml)

    def get_data_block(self):
        with self.__lock:
            while 0 == len(self.__data):
                self.__condition.wait()

            return self.get_data()

#
# END class mDevice
#


#
# As per Blender API docs. Update the scene on a fixed window timer event.
# Catch the ESC key press to cancel the updates.
#
# [2.6x API docs ...]/bpy.types.Operator.html#modal-execution
#
class ModalOperator(bpy.types.Operator):
    """
    Use the Blender Operator base class to copy the most recent input data from
    the mDevice sampler into the Blender scene. Use Modal Execution as per the
    Blender docs to create an operator that remains running, processing events,
    until the operator says it wants to stop.
    """
    bl_idname = "mdevice.start"
    bl_label = "mDevice: Start Device"
    bl_description = "Start streaming data from the from the device server"

    __xml = ""
    __name_map = {}
    __device = None
    __timer = None
    __debug = False
    __cancel_event = ['ESC']

    def __init__(self):
        # Mac is hanging when you close the Blender window. Stop the sampling
        # thread when the window leaves the foreground.
        if 'nt' != os.name:
            self.__cancel_event.append('WINDOW_DEACTIVATE')

        self.__device = mDevice()
        self.__device.start()

        if self.__debug:
            print("START")

    def __del__(self):
        if self.__device is not None:
            self.__device.close()
            self.__device = None

        if self.__debug:
            print("END")

    def execute(self, context):
        """
        Run as a regular command. Read a single frame of data, copy the results
        into the scene, and then return.
        """
        if self.__debug:
            print("execute")

        data, xml = self.__device.get_data_block()

        self.__parse_data(context, data, xml)

        return {'FINISHED'}

    def invoke(self, context, event):
        """
        Run as a modal command. Remains in scope until the modal event handler
        returns CANCELLED or FINISHED.
        """
        if self.__debug:
            print("invoke")

        context.window_manager.modal_handler_add(self)
        self.__timer = context.window_manager.event_timer_add(0.02,
                                                              context.window)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        """
        Modal command event handler. The invoke method sets up a timer for us
        so that the modal event handler can update the scene at a regular
        interval.
        """
        if self.__debug:
            print("modal: %s" % event.type)

        if event.type in self.__cancel_event:
            return self.cancel(context)

        if 'TIMER' == event.type:
            data, xml = self.__device.get_data()

            self.__parse_data(context, data, xml)

        return {'PASS_THROUGH'}

    def cancel(self, context):
        if self.__debug:
            print("cancel")

        if self.__timer is not None:
            context.window_manager.event_timer_remove(self.__timer)
            self.__timer = None

        return {'CANCELLED'}

    def __parse_data(self, context, data, xml):
        """
        Parse an incoming message from the Configurable data service. Also,
        optionally update the node name map from an XML message. Copy the most
        recent frame into the scene.
        """

        # Check for changes in the XML channel name definition.
        if xml != self.__xml:
            self.__parse_xml(xml)

        obj = None
        armature = None

        # Create a map of data for each connected node. Use the channel name
        # mapping to look up objects in the Blender scene to apply rotation and
        # translation data.
        list = SDK.Format.Configurable(data)
        for key, item in list.items():
            name = self.__name_map.get(key)
            if name is None:
                continue

            # "Body" is the container node for a single skeleton.
            if name.startswith("Body"):
                # Either work with independent objects or an armature with
                # named bones.
                obj = context.scene.objects.get(name)
                if obj is not None and 'ARMATURE' == obj.type:
                    armature = obj
                else:
                    armature = None
            else:
                if armature is None:
                    obj = context.scene.objects.get(name)
                else:
                    obj = armature.pose.bones.get(name)

            # Rotate.
            q = Quaternion((item.value(0),
                            item.value(3), item.value(1), item.value(2)))

            # Translate.
            t = Vector((item.value(7), item.value(5), item.value(6)))

            if obj is not None:
                if 'QUATERNION' == obj.rotation_mode:
                    obj.rotation_quaternion = q
                else:
                    obj.rotation_euler = q.to_euler(obj.rotation_mode)

                if armature is None or name.startswith("Hips"):
                    obj.location = t
            elif self.__debug:
                print("Missing object named %s" % name)

            # World space marker. Joint position point cloud with weights.
            obj = context.scene.objects.get("_".join([name, "Marker"]))
            if obj is not None:
                obj.location = t

                weight = item.value(4)
                if weight < 0:
                    weight = 0
                elif weight > 1:
                    weight = 1

                obj.scale.x = obj.scale.y = obj.scale.z = weight + 1

    def __parse_xml(self, xml):
        self.__name_map.clear()

        tree = XML(xml)

        # <node key="N" id="Name"> ... </node>
        list = tree.findall(".//node")
        for itr in list:
            self.__name_map[int(itr.get("key"))] = itr.get("id")

        self.__xml = xml

#
# END class ModalOperator
#
