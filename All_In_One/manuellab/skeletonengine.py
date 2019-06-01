#Manuel Bastioni Lab - Copyright (C) 2016 Manuel Bastioni
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.

#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bpy, os, json
import mathutils
from . import algorithms

import logging


#import faulthandler
#faulthandler.enable()

class SkeletonEngine:

    def __init__(self, obj_body, obj_armat, data_path):
        if obj_body and obj_armat:
            if bpy.data.objects[obj_armat.name].type == 'ARMATURE':
                self.armature_visibility = [x for x in obj_armat.layers]                
                self.armature_hide = obj_armat.hide
                self.armature_name = obj_armat.name
                self.body_name = obj_body.name
                self.joints_indices = {}
                self.bones_z_axis = {}
                self.joints_data_path = os.path.join(
                    data_path,
                    self.body_name,
                    "joints.json")
                self.jointsDatabase = self.load_joints_database(self.joints_data_path)
                self.store_bones_z_axis()
            else:
                logging.error("The object {0} is not an armature".format(obj_armat.name))
        else:
            logging.error("Body or armature (or both) not found ")

    def error_msg(self, path):
        logging.error("Database file not found or corrupted: {0}".format(algorithms.simple_path(path)))

    def store_armature_visibility(self, armature_object):
        logging.debug("Storing the armature visibility")
        self.armature_hide = armature_object.hide
        for n in range(len(armature_object.layers)):
            self.armature_visibility[n] = armature_object.layers[n]

    def restore_armature_visibility(self, armature_object):
        logging.debug("Restoring the armature visibility")
        armature_object.hide = self.armature_hide
        for n in range(len(armature_object.layers)):
            armature_object.layers[n] = self.armature_visibility[n]

    def force_visible_armature(self, armature_object):
        """
        Blender requires the armature is visible in order
        to handle it.
        """   
        logging.debug("Turn the armature visibility ON")     
        if armature_object.hide == True:
            armature_object.hide = False
        for n in range(len(armature_object.layers)):
            armature_object.layers[n] = True


    def get_body(self):
        logging.debug("Getting character body")
        if self.body_name in bpy.data.objects:
            return bpy.data.objects[self.body_name]
        else:
            logging.warning("Body {0} not found".format(self.body_name))
            return None

    def get_armature(self):   
        logging.debug("Getting character armature")     
        if self.armature_name in bpy.data.objects:
            if bpy.data.objects[self.armature_name].type == 'ARMATURE':                
                return bpy.data.objects[self.armature_name]
            else:
                logging.warning("Object {0} is not an armature".format(self.armature_name))
        else:
            logging.warning("Armature {0} not found".format(self.armature_name))
            return None

    def __bool__(self):
        armat = self.get_armature()
        body = self.get_body()
        if body and armat:
            return True
        else:
            return False

    def store_bones_z_axis(self):
        armat = self.get_armature()        
        if armat:
            self.store_armature_visibility(armat)
            self.force_visible_armature(armat)
            bpy.context.scene.objects.active = armat
            object_mode = bpy.context.object.mode
            bpy.ops.object.mode_set(mode='EDIT')

            for bone in armat.data.edit_bones:
                self.bones_z_axis[bone.name] = bone.z_axis.copy()
            bpy.ops.object.mode_set(mode=object_mode)
            self.restore_armature_visibility(armat)
        
        

    def load_joints_database(self, data_path):

        if os.path.isfile(data_path):
            database_file = open(data_path, "r")
            try:
                joint_data = json.load(database_file)
                return joint_data
            except:
                logging.error("Error decoding {0}".format(algorithms.simple_path(data_path)))
            database_file.close()

        else:
            self.error_msg(data_path)
            return None


    def fit_joints(self):

        armat = self.get_armature()
        body = self.get_body()

        if armat and body:
            self.store_armature_visibility(armat)
            self.force_visible_armature(armat)
            logging.debug("Fitting armature {0}".format(armat.name))
            if armat.data.use_mirror_x == True:
                armat.data.use_mirror_x = False

            # must be active in order to turn in edit mode.
            #if the armature is not in edit mode...
            #...armature.data.edit_bones is empty
            bpy.context.scene.objects.active = armat
            object_mode = bpy.context.object.mode
            bpy.ops.object.mode_set(mode='EDIT')

            for bone in armat.data.edit_bones:
                tail_name = "".join((bone.name, "_tail"))
                head_name = "".join((bone.name, "_head"))
                if tail_name in self.jointsDatabase:
                    tail_position = algorithms.centroid(
                        body,
                        self.jointsDatabase[tail_name])
                    bone.tail = tail_position
                if head_name in self.jointsDatabase:
                    head_position = algorithms.centroid(
                        body,
                        self.jointsDatabase[head_name])
                    bone.head = head_position                

                bone.align_roll(self.bones_z_axis[bone.name])
            bpy.ops.object.mode_set(mode=object_mode)
            bpy.context.scene.objects.active = body
            self.restore_armature_visibility(armat)


    def load_pose(self, data_path):

        armat = self.get_armature()
        if armat:
            if os.path.isfile(data_path):
                database_file = open(data_path, "r")
                try:
                    matrix_data = json.load(database_file)
                except:
                    logging.error("Error decoding {0}".format(algorithms.simple_path(data_path)))
                database_file.close()
            else:
                self.error_msg(data_path)
                return None

            self.store_armature_visibility(armat)
            self.force_visible_armature(armat)
            for bone in armat.pose.bones:
                if bone.name in matrix_data:
                    bone.rotation_quaternion = mathutils.Quaternion(matrix_data[bone.name])
            self.restore_armature_visibility(armat)
                    

    def reset_pose(self):

        armat = self.get_armature()
        if armat:
            self.store_armature_visibility(armat)
            self.force_visible_armature(armat)
            for bone in armat.pose.bones:
                bone.rotation_quaternion[0] = 1.0
                bone.rotation_quaternion[1] = 0.0
                bone.rotation_quaternion[2] = 0.0
                bone.rotation_quaternion[3] = 0.0
            self.restore_armature_visibility(armat)
