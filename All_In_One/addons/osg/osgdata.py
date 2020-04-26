# -*- python-indent: 4; mode: python -*-
# -*- coding: UTF-8 -*-
#
# Copyright (C) 2008-2012 Cedric Pinson
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#  Cedric Pinson <cedric@plopbyte.com>
#  Jeremy Moles <jeremy@emperorlinux.com>

import bpy
import mathutils
import json
import math
import os
import shutil
import subprocess

import osg
from collections import OrderedDict
from . import osglog
from . import osgconf
from .osgutils import *
from .osgconf import DEBUG
from . import osgbake
from . import osgobject
from .osgobject import *
osgobject.VERSION = osg.__version__

Euler = mathutils.Euler
Matrix = mathutils.Matrix
Vector = mathutils.Vector
Quaternion = mathutils.Quaternion
Log = osglog.log


def createAnimationUpdate(blender_object, callback, rotation_mode, prefix="", zero=False):
    has_location_keys = False
    has_scale_keys = False
    has_rotation_keys = False
    has_constraints = hasSolidConstraints(blender_object)
    has_nla = hasNLATracks(blender_object)

    # Use local transform matrix at t=0 to initialize stacked transforms.
    scene = bpy.context.scene
    backup_frame = scene.frame_current
    scene.frame_set(0)
    blender_object.update_tag(refresh={'OBJECT'})
    scene.update()

    lcl_transform = blender_object.matrix_local.copy()

    scene.frame_set(backup_frame)
    scene.update()

    if blender_object.animation_data:
        action = blender_object.animation_data.action

        if action:
            for curve in action.fcurves:
                datapath = curve.data_path[len(prefix):]
                Log("curve.data_path {} {} {}".format(curve.data_path, curve.array_index, datapath))
                if datapath == "location":
                    has_location_keys = True

                if datapath.startswith("rotation"):
                    has_rotation_keys = True

                if datapath == "scale":
                    has_scale_keys = True

    if not (has_location_keys or has_scale_keys or has_rotation_keys) and not has_constraints and not has_nla:
        return None

    if zero:
        if has_location_keys:
            tr = StackedTranslateElement()
            tr.translate = Vector()
            callback.stacked_transforms.append(tr)

            if has_rotation_keys:
                if rotation_mode in ["XYZ", "XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX"]:
                    rotation_keys = [StackedRotateAxisElement(name="euler_x", axis=Vector((1, 0, 0)), angle=0),
                                     StackedRotateAxisElement(name="euler_y", axis=Vector((0, 1, 0)), angle=0),
                                     StackedRotateAxisElement(name="euler_z", axis=Vector((0, 0, 1)), angle=0)]

                    callback.stacked_transforms.append(rotation_keys[ord(blender_object.rotation_mode[2]) - ord('X')])
                    callback.stacked_transforms.append(rotation_keys[ord(blender_object.rotation_mode[1]) - ord('X')])
                    callback.stacked_transforms.append(rotation_keys[ord(blender_object.rotation_mode[0]) - ord('X')])

                if rotation_mode == "QUATERNION":
                    q = StackedQuaternionElement()
                    q.quaternion = Quaternion()
                    callback.stacked_transforms.append(q)

                if rotation_mode == "AXIS_ANGLE":
                    callback.stacked_transforms.append(StackedRotateAxisElement(name="axis_angle",
                                                                                axis=Vector((1, 0, 0)),
                                                                                angle=0))
        if has_scale_keys:
            sc = StackedScaleElement()
            sc.scale = Vector(blender_object.scale)
            callback.stacked_transforms.append(sc)

    else:
        tr = StackedTranslateElement()
        tr.translate = Vector(lcl_transform.to_translation())
        callback.stacked_transforms.append(tr)

        if rotation_mode in ["XYZ", "XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX"]:
            lcl_rotation = lcl_transform.to_euler()
            rotation_keys = [StackedRotateAxisElement(name="euler_x", axis=Vector((1, 0, 0)),
                                                      angle=lcl_rotation[0]),
                             StackedRotateAxisElement(name="euler_y", axis=Vector((0, 1, 0)),
                                                      angle=lcl_rotation[1]),
                             StackedRotateAxisElement(name="euler_z", axis=Vector((0, 0, 1)),
                                                      angle=lcl_rotation[2])]

            callback.stacked_transforms.append(rotation_keys[ord(blender_object.rotation_mode[2]) - ord('X')])
            callback.stacked_transforms.append(rotation_keys[ord(blender_object.rotation_mode[1]) - ord('X')])
            callback.stacked_transforms.append(rotation_keys[ord(blender_object.rotation_mode[0]) - ord('X')])

        if rotation_mode == "QUATERNION":
            q = StackedQuaternionElement()
            q.quaternion = lcl_transform.to_quaternion()
            callback.stacked_transforms.append(q)

        if rotation_mode == "AXIS_ANGLE":
            lcl_axis_angle = lcl_transform.to_quaternion().to_axis_angle()
            callback.stacked_transforms.append(StackedRotateAxisElement(name="axis_angle",
                                                                        axis=lcl_axis_angle[0],
                                                                        angle=lcl_axis_angle[1]))

        sc = StackedScaleElement()
        sc.scale = Vector(lcl_transform.to_scale())
        callback.stacked_transforms.append(sc)

    return callback


def createAnimationMaterialAndSetCallback(osg_node, blender_object, config, unique_objects):
    Log("Warning: [[blender]] Update material animations are not yet supported")
    return None
    # return createAnimationsObject(osg_node, blender_object, config, UpdateMaterial(), uniq_anims)


class UniqueObject(object):
    def __init__(self):
        self.statesets = {}
        self.textures = {}
        self.objects = {}

    def hasObject(self, obj):
        return obj in self.objects

    def getObject(self, obj):
        if self.hasObject(obj):
            return self.objects[obj]
        return None

    def registerObject(self, obj, reg):
        self.objects[obj] = reg

    def hasTexture(self, obj):
        return obj in self.textures

    def getTexture(self, obj):
        if self.hasTexture(obj):
            return self.textures[obj]
        return None

    def registerTexture(self, obj, reg):
        self.textures[obj] = reg

    def hasStateSet(self, obj):
        return obj in self.statesets

    def getStateSet(self, obj):
        if self.hasStateSet(obj):
            return self.statesets[obj]
        return None

    def registerStateSet(self, obj, reg):
        self.statesets[obj] = reg


class Export(object):
    def __init__(self, config=None):
        object.__init__(self)
        self.items = []
        self.config = config
        if self.config is None:
            self.config = osgconf.Config()
            self.config.defaultattr('scene', bpy.context.scene)
        self.rest_armatures = []
        self.animations = []
        self.baked_actions = []
        self.current_animation = None
        self.images = set()
        self.lights = {}
        self.root = None
        self.unique_objects = UniqueObject()
        self.parse_all_actions = False  # if only one object and several actions

    def clean_generated_actions(self):
        for action in self.baked_actions:
            if action.users != 0:
                Log('Warning: The exporter generated actions that are still attached to objects. Cleaning users')
                action.user_clear()
            try:
                bpy.data.actions.remove(action)
            except:
                Log('Can''t remove generated action')

    def isExcluded(self, blender_object):
        return blender_object.name in self.config.exclude_objects

    def setArmatureInRestMode(self):
        self.rest_armatures = setArmaturesPosePosition(self.config.scene, 'REST')

    def restoreArmaturePoseMode(self):
        setArmaturesPosePosition(self.config.scene, 'POSE', self.rest_armatures)
        self.rest_armatures = []

    def exportItemAndChildren(self, blender_object):
        item = self.exportChildrenRecursively(blender_object, None, None)
        if item is not None:
            self.items.append(item)

    def evaluateGroup(self, blender_object, item, rootItem):
        if blender_object.dupli_group is None or len(blender_object.dupli_group.objects) == 0:
            return

        Log("resolving {} for {} offset {}".format(blender_object.dupli_group.name,
                                                   blender_object.name,
                                                   blender_object.dupli_group.dupli_offset))

        group = MatrixTransform()
        group.matrix = Matrix.Translation(-blender_object.dupli_group.dupli_offset)
        item.children.append(group)

        # for group we disable the only visible
        config_visible = self.config.only_visible
        self.config.only_visible = False
        for o in blender_object.dupli_group.objects:
            Log("object {}".format(o))
            self.exportChildrenRecursively(o, group, rootItem)
        self.config.only_visible = config_visible
        # and restore it after processing group

    def getName(self, blender_object):
        if hasattr(blender_object, "name"):
            return blender_object.name
        return "no name"

    def isObjectVisible(self, blender_object):
        return blender_object.is_visible(self.config.scene) or not self.config.only_visible

    def createAnimationsObject(self,
                               osg_object,
                               blender_object,
                               config,
                               update_callback,
                               unique_objects,
                               parse_all_actions=False):

        if not config.export_anim or len(bpy.data.actions) == 0:
            return None

        has_action = blender_object.animation_data and hasAction(blender_object)
        has_constraints = hasSolidConstraints(blender_object) or hasExternalBoneConstraints(blender_object)
        has_morph = hasShapeKeysAnimation(blender_object)

        if blender_object.type != 'ARMATURE' and not has_morph and not update_callback:
            return None

        if not has_action and not has_constraints and not has_morph and not hasNLATracks(blender_object):
            return None

        if parse_all_actions and not has_action and not has_morph and not hasNLATracks(blender_object):
            return None

        if has_constraints and (blender_object.parent and blender_object.parent.type == 'ARMATURE'):
            return None

        action2animation = BlenderAnimationToAnimation(object=blender_object,
                                                       config=config,
                                                       unique_objects=unique_objects,
                                                       has_action=has_action,
                                                       has_constraints=has_constraints,
                                                       has_morph=has_morph)

        if parse_all_actions:
            self.animations = action2animation.parseAllActions()
        else:
            # must have only one animation here
            if not self.current_animation:
                self.current_animation = Animation()
                self.current_animation.setName('Take 01')
                self.animations.append(self.current_animation)
            action2animation.handleAnimationBaking()
            action2animation.addActionDataToAnimation(self.current_animation)

            if has_morph:
                # Bake morph animation
                action2animation.handleMorphAnimationBaking()
                action2animation.addActionDataToAnimation(self.current_animation, morph=True)

        # Remove actions created by the exporter for baking
        self.baked_actions.extend(action2animation.get_generated_actions())
        if update_callback:
            if blender_object.type == 'ARMATURE':
                osg_object.update_callbacks = []
            osg_object.update_callbacks.append(update_callback)

    def exportChildrenRecursively(self, blender_object, parent, osg_root):
        def parseArmature(blender_armature):
            osg_object = self.createSkeleton(blender_object)
            self.createAnimationsObject(osg_object, blender_object, self.config,
                                        createAnimationUpdate(blender_object,
                                                              UpdateMatrixTransform(name=osg_object.name),
                                                              rotation_mode),
                                        self.unique_objects,
                                        self.parse_all_actions)
            return osg_object

        def parseLight(blender_light):
            matrix = getDeltaMatrixFrom(blender_object.parent, blender_object)
            osg_object = MatrixTransform()
            osg_object.setName(blender_object.name)
            osg_object.matrix = matrix
            lightItem = self.createLight(blender_object)
            self.createAnimationsObject(osg_object, blender_object, self.config,
                                        createAnimationUpdate(blender_object,
                                                              UpdateMatrixTransform(name=osg_object.name),
                                                              rotation_mode),
                                        self.unique_objects,
                                        self.parse_all_actions)
            osg_object.children.append(lightItem)
            return osg_object

        # Mesh, Camera and Empty objects
        def parseBlenderObject(blender_object, is_visible):
            # because it blender can insert inverse matrix, we have to recompute the parent child
            # matrix for our use.
            matrix = getDeltaMatrixFrom(blender_object.parent, blender_object)
            osg_object = MatrixTransform()
            osg_object.setName(blender_object.name)

            osg_object.matrix = matrix.copy()
            if self.config.zero_translations and parent is None:
                if bpy.app.version[0] >= 2 and bpy.app.version[1] >= 62:
                    print("zero_translations option has not been converted to blender 2.62")
                else:
                    osg_object.matrix[3].xyz = Vector()

            self.createAnimationsObject(osg_object, blender_object, self.config,
                                        createAnimationUpdate(blender_object,
                                                              UpdateMatrixTransform(name=osg_object.name),
                                                              rotation_mode),
                                        self.unique_objects,
                                        self.parse_all_actions)

            if is_visible:
                if blender_object.type == "MESH":
                    osg_geode = self.createGeodeFromObject(blender_object)
                    osg_object.children.append(osg_geode)
                else:
                    self.evaluateGroup(blender_object, osg_object, osg_root)
            return osg_object

        def handleBoneChild(blender_object, osg_object):
            bone = findBoneInHierarchy(osg_root, spaceSafe(blender_object.parent_bone + '_' +
                                                           str(blender_object.parent.name)))
            if bone is None:
                Log("Warning: [[blender]] {} not found".format(blender_object.parent_bone))
            else:
                armature = blender_object.parent
                original_pose_position = armature.data.pose_position
                armature.data.pose_position = 'REST'

                boneInWorldSpace = armature.matrix_world \
                    * armature.pose.bones[blender_object.parent_bone].matrix

                matrix = getDeltaMatrixFromMatrix(boneInWorldSpace, blender_object.matrix_world)

                osg_object.matrix = matrix
                bone.children.append(osg_object)

                armature.data.pose_position = original_pose_position

        # We skip the object if it is in the excluded objects list
        if self.isExcluded(blender_object):
            return None

        # Check if the object is visible. The visibility will be used for meshes and lights
        # to determine if we keep it or not. Other objects have to be taken into account even if they
        # are not visible as they can be used as modifiers (avoiding some crashs during the export)
        is_visible = self.isObjectVisible(blender_object)
        Log("")

        osg_object = None
        rotation_mode = 'QUATERNION' if self.config.use_quaternions else blender_object.rotation_mode

        if self.unique_objects.hasObject(blender_object):
            Log("{} '{}' has already been parsed, reuse osg_object".format(blender_object.type, blender_object.name))
            osg_object = self.unique_objects.getObject(blender_object)
        else:
            Log("Parsing object '{}' of type {}".format(blender_object.name, blender_object.type))
            if blender_object.type == "ARMATURE":
                osg_object = parseArmature(blender_object)
            elif blender_object.type == "LAMP" and is_visible:
                osg_object = parseLight(blender_object)
            elif blender_object.type in ['MESH', 'EMPTY', 'CAMERA']:
                osg_object = parseBlenderObject(blender_object, is_visible)
            else:
                Log("Warning: [[blender]] Skipping object {} (objects {} are not exported)"
                    .format(blender_object.name, blender_object.type))
                return None

            self.unique_objects.registerObject(blender_object, osg_object)

        if osg_root is None:
            osg_root = osg_object

        # Handle parenting
        if blender_object.parent_type == "BONE":
            handleBoneChild(blender_object, osg_object)
        elif parent:
            parent.children.append(osg_object)

        children = getChildrenOf(self.config.scene, blender_object)
        for child in children:
            self.exportChildrenRecursively(child, osg_object, osg_root)
        return osg_object

    def createSkeleton(self, blender_object):
        Log("processing Armature {}".format(blender_object.name))
        # if no animation, set it in pose mode to bake it
        use_pose = not (hasAction(blender_object) or hasNLATracks(blender_object)) and not \
            (hasExternalBoneConstraints(blender_object)) and not self.config.arm_rest

        if use_pose and blender_object in self.rest_armatures:
            setArmaturesPosePosition(self.config.scene, 'POSE', [blender_object])

        roots = getRootBonesList(blender_object.data)

        matrix = getDeltaMatrixFrom(blender_object.parent, blender_object)
        skeleton = Skeleton(blender_object.name, matrix)
        for bone in roots:
            b = Bone(blender_object, bone)
            b.buildBoneChildren(use_pose=use_pose)
            skeleton.children.append(b)
        skeleton.collectBones()

        if use_pose and blender_object in self.rest_armatures:
            setArmaturesPosePosition(self.config.scene, 'REST', [blender_object])
        return skeleton

    def preProcess(self):
        def lookForAnimatedObjects():
            scene = self.config.scene
            nb_animated_objects = 0
            for obj in scene.objects:
                # FIXME not sure about the constraint check here
                if hasAction(obj) or \
                   hasSolidConstraints(obj) or \
                   hasExternalBoneConstraints(obj) or \
                   hasNLATracks(obj) or \
                   hasShapeKeysAnimation(obj):
                    nb_animated_objects += 1

            self.parse_all_actions = nb_animated_objects == 1

        def checkNameEncoding(elements, label, renamed_count):
            for element in elements:
                try:
                    element.name
                except UnicodeDecodeError:
                    element.name = 'renamed_{}_{}'.format(label, renamed_count)
                    renamed_count += 1

        def resolveMisencodedNames(scene):
            ''' Replace misencoded object names to avoid errors '''
            scene = bpy.context.scene
            renamed_count = 0

            renamed_count = checkNameEncoding(scene.objects, 'object', renamed_count)
            for obj in scene.objects:
                renamed_count = checkNameEncoding(obj.modifiers, 'modifier', renamed_count)
                renamed_count = checkNameEncoding(obj.vertex_groups, 'vertex_group', renamed_count)

            renamed_count = checkNameEncoding(bpy.data.armatures, 'armature', renamed_count)
            for arm in bpy.data.armatures:
                renamed_count = checkNameEncoding(arm.bones, 'bone', renamed_count)

            renamed_count = checkNameEncoding(bpy.data.materials, 'material', renamed_count)
            renamed_count = checkNameEncoding(bpy.data.textures, 'texture', renamed_count)
            renamed_count = checkNameEncoding(bpy.data.images, 'image', renamed_count)
            renamed_count = checkNameEncoding(bpy.data.curves, 'curve', renamed_count)
            renamed_count = checkNameEncoding(bpy.data.cameras, 'camera', renamed_count)
            renamed_count = checkNameEncoding(bpy.data.lamps, 'lamp', renamed_count)
            renamed_count = checkNameEncoding(bpy.data.metaballs, 'metaball', renamed_count)

            if renamed_count:
                print('Warning: [[blender]] {} entities having misencoded names were renamed'.format(renamed_count))

        def make_dupliverts_real(scene):
            ''' Duplicates vertex instances and makes them real'''
            unselectAllObjects()
            # Select all objects that use dupli_vertex mode
            selectObjects([obj for obj in scene.objects if obj.dupli_type == 'VERTS' and obj.children])

            # Duplicate all instances into real objects
            if bpy.context.selected_objects:
                bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True)
                print('Warning: [[blender]] Some instances (duplication at vertex) were duplicated as real objects')
                # Clear selection
                unselectAllObjects()

        # The following process may alter object selection, so
        # we need to save it
        backup_selection = bpy.context.selected_objects

        make_dupliverts_real(self.config.scene)
        resolveMisencodedNames(self.config.scene)
        lookForAnimatedObjects()

        # restore the user's selection
        unselectAllObjects()
        selectObjects(backup_selection)

    def process(self):
        self.preProcess()

        # Object.resetWriter()
        self.scene_name = self.config.scene.name
        Log("current scene {}".format(self.scene_name))
        if self.config.validFilename() is False:
            self.config.filename += self.scene_name
        self.config.createLogfile()

        self.setArmatureInRestMode()
        try:
            if self.config.object_selected is not None:
                o = bpy.data.objects[self.config.object_selected]
                try:
                    self.config.scene.objects.active = o
                    self.config.scene.objects.selected = [o]
                except ValueError:
                    Log("Error, problem happens when assigning object {} to scene {}"
                        .format(o.name, self.config.scene.name))
                    raise

            for obj in self.config.scene.objects:
                Log("obj {}".format(obj.name))
                if (self.config.selected == "SELECTED_ONLY_WITH_CHILDREN" and obj.select) or \
                   (self.config.selected == "ALL" and obj.parent is None):
                    self.exportItemAndChildren(obj)
        finally:
            self.restoreArmaturePoseMode()
            self.clean_generated_actions()

        self.postProcess()

    # OSG requires that rig geometry be a child of the skeleton,
    # but Blender does not.  Move any meshes that are modified by
    # an armature to be under the armature.
    def reparentRiggedGeodes(self, item, parent):
        if isinstance(item, MatrixTransform) \
           and len(item.children) == 1 \
           and isinstance(item.children[0], Geode) \
           and not isinstance(parent, Skeleton):
            geode = item.children[0]
            Log("geode {}".format(geode.name))

            # some blend files has a armature_modifier but a None object
            # so we have to test armature_modifier and armature_modifier.object
            if geode.armature_modifier is not None and geode.armature_modifier.object:
                parent.children.remove(item)
                modifier_object = item.children[0].armature_modifier.object

                arm = self.unique_objects.getObject(modifier_object)
                for (k, v) in self.unique_objects.objects.items():
                    if v == item:
                        meshobj = k

                item.matrix = getDeltaMatrixFromMatrix(item.children[0].armature_modifier.object.matrix_world,
                                                       meshobj.matrix_world)

                arm.children.append(item)
                Log("NOTICE: Reparenting {} to {}".format(geode.name, arm.name))
        if hasattr(item, "children"):
            for c in list(item.children):
                self.reparentRiggedGeodes(c, item)

    def postProcess(self):
        # set only one root to the scene
        self.root = None
        self.root = Group()
        self.root.setName("Root")
        self.root.children = self.items
        self.root.getOrCreateUserData().append(StringValueObject("source", "blender"))
        if len(self.animations) > 0:
            animation_manager = BasicAnimationManager()
            animation_manager.animations = self.animations
            self.root.update_callbacks.append(animation_manager)

        self.reparentRiggedGeodes(self.root, None)

        # index light num for opengl use and enable them in a stateset
        if len(self.lights) > 0:
            st = StateSet()
            self.root.stateset = st
            if len(self.lights) > 8:
                Log("Warning: [[blender]] The model has more than 8 lights")

            # retrieve world to global ambient
            lm = LightModel()
            lm.ambient = (1.0, 1.0, 1.0, 1.0)
            if self.config.scene.world is not None:
                amb = self.config.scene.world.ambient_color
                lm.ambient = (amb[0], amb[1], amb[2], 1.0)

            st.attributes.append(lm)

            # add by default
            st.attributes.append(Material())

            light_num = 0
            for name, ls in self.lights.items():
                ls.light.light_num = light_num
                key = "GL_LIGHT{}".format(light_num)
                st.modes[key] = "ON"
                light_num += 1

        for key in self.unique_objects.statesets.keys():
            stateset = self.unique_objects.statesets[key]
            if stateset is not None:  # register images to unpack them at the end
                images = getImageFilesFromStateSet(stateset)
                for i in images:
                    self.images.add(i)

    def write(self):
        if len(self.items) == 0:
            if self.config.log_file is not None:
                self.config.closeLogfile()
            return

        filename = self.config.getFullName("osgt")
        Log("write file to {}".format(filename))
        with open(filename, "wb") as sfile:
            # sfile.write(str(self.root).encode('utf-8'))
            self.root.writeFile(sfile)

        nativePath = os.path.join(os.path.abspath(self.config.getFullPath()), self.config.texture_prefix)
        # blenderPath = bpy.path.relpath(nativePath)
        if len(self.images) > 0:
            try:
                if not os.path.exists(nativePath):
                    os.mkdir(nativePath)
            except:
                Log("can't create textures directory {}".format(nativePath))
                raise

        copied_images = []
        for i in self.images:
            if i is not None:
                imagename = bpy.path.basename(createImageFilename("", i))
                try:
                    if i.packed_file:
                        original_filepath = i.filepath_raw
                        try:
                            if len(imagename.split('.')) == 1:
                                imagename += ".png"
                            filename = os.path.join(nativePath, imagename)
                            if not os.path.exists(filename):
                                # record which images that were newly copied and can be safely
                                # cleaned up
                                copied_images.append(filename)
                            i.filepath_raw = filename
                            Log("packed file, save it to {}"
                                .format(os.path.abspath(bpy.path.abspath(filename))))
                            i.save()
                        except:
                            Log("failed to save file {} to {}".format(imagename, nativePath))
                        i.filepath_raw = original_filepath
                    else:
                        filepath = os.path.abspath(bpy.path.abspath(i.filepath))
                        texturePath = os.path.join(nativePath, imagename)
                        if os.path.exists(filepath):
                            if not os.path.exists(texturePath):
                                # record which images that were newly copied and can be safely
                                # cleaned up
                                copied_images.append(texturePath)
                            shutil.copy(filepath, texturePath)
                            Log("copy file {} to {}".format(filepath, texturePath))
                        else:
                            Log("file {} not available".format(filepath))
                except Exception as e:
                    Log("error while trying to copy file {} to {}: {}".format(imagename, nativePath, e))

        filetoview = self.config.getFullName("osgt")
        if self.config.osgconv_to_ive:
            if self.config.osgconv_embed_textures:
                r = [self.config.osgconv_path, "-O", "includeImageFileInIVEFile",
                     self.config.getFullName("osgt"), self.config.getFullName("ive")]
            else:
                r = [self.config.osgconv_path, "-O", "noTexturesInIVEFile",
                     self.config.getFullName("osgt"), self.config.getFullName("ive")]
            try:
                if subprocess.call(r) == 0:
                    filetoview = self.config.getFullName("ive")
                    if self.config.osgconv_cleanup:
                        os.unlink(self.config.getFullName("osgt"))
                        if self.config.osgconv_embed_textures:
                            for i in copied_images:
                                os.unlink(i)
            except Exception as e:
                print("Error running {}".format(r))
                print(repr(e))

        if self.config.run_viewer:
            r = [self.config.viewer_path, filetoview]
            try:
                subprocess.Popen(r)
            except Exception as e:
                print("Error running {}".format(r))
                print(repr(e))

        if self.config.log_file is not None:
            self.config.closeLogfile()

    def createGeodeFromObject(self, mesh, skeleton=None):
        Log("exporting object {}".format(mesh.name))

        # check if the mesh has a armature modifier
        # if no we don't write influence
        exportInfluence = False

        armature_modifier = None
        has_non_armature_modifiers = False

        for mod in mesh.modifiers:
            if mod.type == "ARMATURE":
                armature_modifier = mod
            else:
                has_non_armature_modifiers = True

        # Consider a mesh child of armature as rigged only if it has no parent_bone. To get both bone parenting
        # and riggin effect, an armature modifier has to be applied
        if armature_modifier is not None or mesh.parent and mesh.parent.type == 'ARMATURE' and not mesh.parent_bone:
            exportInfluence = True

        # converting to mesh skips shape keys
        if self.config.apply_modifiers and has_non_armature_modifiers and not hasShapeKeys(mesh):
            mesh_object = mesh.to_mesh(self.config.scene, True, 'PREVIEW')
        else:
            mesh_object = mesh.data

        Log("mesh_object is {}".format(mesh_object.name))

        if self.unique_objects.hasObject(mesh_object):
            return self.unique_objects.getObject(mesh_object)

        hasVertexGroup = False

        for vertex in mesh_object.vertices:
            if len(vertex.groups) > 0:
                hasVertexGroup = True
                break

        geometries = []
        converter = BlenderObjectToGeometry(object=mesh,
                                            mesh=mesh_object,
                                            config=self.config,
                                            unique_objects=self.unique_objects)
        sources_geometries = converter.convert()

        Log("vertex groups {} {} ".format(exportInfluence, hasVertexGroup))
        if exportInfluence and hasVertexGroup:
            for geom in sources_geometries:
                rig_geom = RigGeometry()
                rig_geom.sourcegeometry = geom
                rig_geom.copyFrom(geom)
                rig_geom.groups = geom.groups
                geometries.append(rig_geom)
        else:
            geometries = sources_geometries

        geode = Geode()
        geode.setName(mesh_object.name)
        geode.armature_modifier = armature_modifier

        updateMorphs = {}
        # Geometries are the result of splitting Blender multi-material mesh.
        # We assume that we have as much geometries as the number of materials
        # the original Blender mesh has. This mapping is used when renaming geometry
        # targets in animation parsing code.
        if len(geometries) > 0:
            # Rename geometries to ensure that the order is kept bewteen MorphGeometry and UpdateMorphs
            # Note: renaming geometries should not be a problem here since armature deform/animation doesn't use
            # rig/source geometry names and solid animation is applied to geode (or upper osg node)
            # The name of the morphGeometry is used for UpdateMorph callback, that is created after
            # that so the link is not broken
            for index, geom in enumerate(geometries):
                geom.name = "{}_{}".format(geom.name, index)

                if geom.className() == 'MorphGeometry':
                    updateMorphs.setdefault(geom.name, []).extend(map(lambda x: x.name, geom.morphTargets))

                if geom.className() == 'RigGeometry' and geom.sourcegeometry.className() == 'MorphGeometry':
                    geom.sourcegeometry.name = "{}_{}".format(geom.sourcegeometry.name, index)
                    updateMorphs.setdefault(geom.name, []).extend(map(lambda x: x.name,
                                                                      geom.sourcegeometry.morphTargets))

                geode.drawables.append(geom)

            # Material animations is not yet supported
            # for name in converter.material_animations.keys():
            #     self.animations.append(converter.material_animations[name])

            if updateMorphs:
                # Important: to keep the same order in updateMorph than in drawables
                names = [geom.name for geom in geometries]
                update = None
                for morphname in names:
                    callback = UpdateMorph()
                    callback.setName(morphname)
                    callback.targetNames.extend(updateMorphs[morphname])
                    if not update:
                        update = callback
                    else:
                        update.addNestedCallback(callback)

                geode.update_callbacks.append(update)
        self.unique_objects.registerObject(mesh_object, geode)
        return geode

    def createLight(self, obj):
        converter = BlenderLightToLightSource(lamp=obj)
        lightsource = converter.convert()
        self.lights[lightsource.name] = lightsource  # will be used to index lightnum at the end
        return lightsource


class BlenderLightToLightSource(object):
    def __init__(self, *args, **kwargs):
        self.object = kwargs["lamp"]
        self.lamp = self.object.data

    def convert(self):
        ls = LightSource()
        ls.setName(self.object.name)
        light = ls.light
        energy = self.lamp.energy
        light.ambient = (1.0, 1.0, 1.0, 1.0)

        if self.lamp.use_diffuse:
            light.diffuse = (self.lamp.color[0] * energy,
                             self.lamp.color[1] * energy,
                             self.lamp.color[2] * energy,
                             1.0)
        else:
            light.diffuse = (0, 0, 0, 1.0)

        if self.lamp.use_specular:
            light.specular = (energy, energy, energy, 1.0)  # light.diffuse
        else:
            light.specular = (0, 0, 0, 1.0)

        light.getOrCreateUserData().append(StringValueObject("source", "blender"))
        light.getOrCreateUserData().append(StringValueObject("Energy", str(energy)))
        light.getOrCreateUserData().append(StringValueObject("Color", "[{}, {}, {}]".format(self.lamp.color[0],
                                                                                            self.lamp.color[1],
                                                                                            self.lamp.color[2])))

        if self.lamp.use_diffuse:
            light.getOrCreateUserData().append(StringValueObject("UseDiffuse", "true"))
        else:
            light.getOrCreateUserData().append(StringValueObject("UseDiffuse", "false"))

        if self.lamp.use_specular:
            light.getOrCreateUserData().append(StringValueObject("UseSpecular", "true"))
        else:
            light.getOrCreateUserData().append(StringValueObject("UseSpecular", "false"))

        light.getOrCreateUserData().append(StringValueObject("Distance", str(self.lamp.distance)))
        if self.lamp.type == 'POINT' or self.lamp.type == "SPOT":
            light.getOrCreateUserData().append(StringValueObject("FalloffType", str(self.lamp.falloff_type)))
            light.getOrCreateUserData().append(StringValueObject("UseSphere", str(self.lamp.use_sphere).lower()))

        light.getOrCreateUserData().append(StringValueObject("Type", str(self.lamp.type)))

        # Lamp', 'Sun', 'Spot', 'Hemi', 'Area', or 'Photon
        if self.lamp.type == 'POINT' or self.lamp.type == 'SPOT':
            # position light
            # Note DW - the distance may not be necessary anymore (blender 2.5)
            light.position = (0, 0, 0, 1)  # put light to vec3(0) it will inherit the position from parent transform
            light.linear_attenuation = self.lamp.linear_attenuation / self.lamp.distance
            light.quadratic_attenuation = self.lamp.quadratic_attenuation / self.lamp.distance

            if self.lamp.falloff_type == 'CONSTANT':
                light.quadratic_attenuation = 0
                light.linear_attenuation = 0

            if self.lamp.falloff_type == 'INVERSE_SQUARE':
                light.constant_attenuation = 0
                light.linear_attenuation = 0

            if self.lamp.falloff_type == 'INVERSE_LINEAR':
                light.constant_attenuation = 0
                light.quadratic_attenuation = 0

        elif self.lamp.type == 'SUN':
            light.position = (0, 0, 1, 0)  # put light to 0 it will inherit the position from parent transform

        if self.lamp.type == 'SPOT':
            light.spot_cutoff = math.degrees(self.lamp.spot_size * .5)
            if light.spot_cutoff > 90:
                light.spot_cutoff = 180
            light.spot_exponent = 128.0 * self.lamp.spot_blend

            light.getOrCreateUserData().append(StringValueObject("SpotSize", str(self.lamp.spot_size)))
            light.getOrCreateUserData().append(StringValueObject("SpotBlend", str(self.lamp.spot_blend)))

        return ls


class BlenderObjectToGeometry(object):
    def __init__(self, *args, **kwargs):
        self.object = kwargs["object"]
        self.config = kwargs.get("config", osgconf.Config())
        self.unique_objects = kwargs.get("unique_objects", UniqueObject())
        self.geom_type = Geometry
        self.mesh = kwargs.get("mesh", None)

        # if self.config.apply_modifiers is False:
        #     self.mesh = self.object.data
        # else:
        #     self.mesh = self.object.to_mesh(self.config.scene, True, 'PREVIEW')
        self.material_animations = {}

    def createTexture2D(self, mtex):
        image_object = None
        try:
            image_object = mtex.texture.image
        except:
            image_object = None
        if image_object is None:
            Log("Warning: [[blender]] The texture {} is skipped since it has no Image".format(mtex.name))
            return None

        if self.unique_objects.hasTexture(mtex.texture):
            return self.unique_objects.getTexture(mtex.texture)

        texture = Texture2D()
        texture.name = mtex.texture.name

        # reference texture relative to export path
        filename = createImageFilename(self.config.texture_prefix, image_object)
        texture.file = filename
        texture.source_image = image_object
        self.unique_objects.registerTexture(mtex.texture, texture)
        return texture

    def createTexture2DFromNode(self, node):
        image_object = None
        try:
            image_object = node.image
        except:
            image_object = None
        if image_object is None:
            Log("Warning: [[blender]] The texture node {} is skipped since it has no Image".format(node))
            return None

        if self.unique_objects.hasTexture(node):
            return self.unique_objects.getTexture(node)

        texture = Texture2D()
        texture.name = node.image.name

        # reference texture relative to export path
        filename = createImageFilename(self.config.texture_prefix, image_object)
        texture.file = filename
        texture.source_image = image_object
        self.unique_objects.registerTexture(node, texture)
        return texture

    def adjustUVLayerFromMaterial(self, geom, material, mesh_uv_textures):

        uvs = geom.uvs
        if DEBUG:
            Log("geometry uvs {}".format(uvs))
        geom.uvs = OrderedDict()

        texture_list = material.texture_slots
        if DEBUG:
            Log("texture list {} - {}".format(len(texture_list), texture_list))

        # find a default channel if exist uv
        default_uv = None
        default_uv_key = None
        if len(mesh_uv_textures) > 0:
            default_uv_key = mesh_uv_textures[0].name
            default_uv = uvs[default_uv_key]

        if DEBUG:
            Log("default uv key {}".format(default_uv_key))

        for texture_id, texture_slot in enumerate(texture_list):
            if texture_slot is not None:
                uv_layer = texture_slot.uv_layer

                if DEBUG:
                    Log("uv layer {}".format(uv_layer))

                if len(uv_layer) > 0 and uv_layer not in uvs.keys():
                    Log("Warning: [[blender]] The material '{}' with texture '{}'\
use an uv layer '{}' that does not exist on the mesh '{}'; using the first uv channel as fallback"
                        .format(material.name, texture_slot, uv_layer, geom.name))
                if len(uv_layer) > 0 and uv_layer in uvs.keys():
                    if DEBUG:
                        Log("texture {} use uv layer {}".format(i, uv_layer))
                    geom.uvs[texture_id] = TexCoordArray()
                    geom.uvs[texture_id].array = uvs[uv_layer].array
                    geom.uvs[texture_id].index = texture_id
                elif default_uv:
                    if DEBUG:
                        Log("texture {} use default uv layer {}".format(i, default_uv_key))
                    geom.uvs[texture_id] = TexCoordArray()
                    geom.uvs[texture_id].index = texture_id
                    geom.uvs[texture_id].array = default_uv.array

        # adjust uvs channels if no textures assigned
        if len(geom.uvs.keys()) == 0:
            if DEBUG:
                Log("no texture set, adjust uvs channels, in arbitrary order")
            for index, k in enumerate(uvs.keys()):
                uvs[k].index = index
            geom.uvs = uvs
        return

    def createStateSet(self, index_material, mesh):
        if len(mesh.materials) == 0:
            return None

        mat_source = mesh.materials[index_material]
        if self.unique_objects.hasStateSet(mat_source):
            return self.unique_objects.getStateSet(mat_source)

        if mat_source is None:
            return None

        stateset = StateSet()
        self.unique_objects.registerStateSet(mat_source, stateset)
        material = Material()
        stateset.attributes.append(material)

        # Setting dataVariance to Static since material animation is not supported
        for osg_object in (stateset, material):
            osg_object.dataVariance = "STATIC"
            osg_object.setName(mat_source.name)
            osg_object.getOrCreateUserData().append(StringValueObject("source", "blender"))

        if mat_source.use_nodes is True:
            self.createStateSetShaderNode(mat_source, stateset, material)
        else:
            self.createStateSetMaterial(mat_source, stateset, material)

        return stateset

    def createStateSetShaderNode(self, mat_source, stateset, material):
        """
        Reads a shadernode to an osg stateset/material
        """
        if self.config.json_shaders:
            self.createStateSetShaderNodeJSON(mat_source, stateset, material)
        else:
            self.createStateSetShaderNodeUserData(mat_source, material)

    def createStateSetShaderNodeJSON(self, mat_source, stateset, material):
        """
         Serializes a blender shadernode into a JSON object
        """
        source_tree = mat_source.node_tree

        def createSocket(source_socket):
            socket = {
                "name": source_socket.name,
                "type": source_socket.type,
                "enabled": source_socket.enabled,
                "links": []
            }
            for source_link in source_socket.links:
                socket['links'].append({
                    "from_node": source_link.from_node.name,
                    "from_socket": source_link.from_socket.name,
                    "to_node": source_link.to_node.name,
                    "to_socket": source_link.to_socket.name
                })

            if hasattr(source_socket, 'default_value'):
                value = source_socket.default_value
                if isinstance(value, Vector) or str(type(value)) \
                   in ["<class 'bpy_prop_array'>", "<class 'mathutils.Color'>"]:
                    socket['default_value'] = [v for v in value]
                else:
                    socket['default_value'] = value

            return socket

        tree = {
            "nodes": {}
        }
        texture_slot_id = 0
        for source_node in source_tree.nodes:
            node = {
                "name": source_node.name,
                "type": source_node.type,
                "inputs": [createSocket(source_input) for source_input in source_node.inputs],
                "outputs": [createSocket(source_output) for source_output in source_node.outputs]
            }

            if source_node.type == "TEX_IMAGE" and source_node.image is not None:
                node["texture_mapping"] = {
                    "mapping": source_node.texture_mapping.mapping
                }
                node["image"] = {
                    "filepath_raw": source_node.image.filepath_raw,
                    "use_alpha": source_node.image.use_alpha,
                    "colorspace": source_node.image.colorspace_settings.name,
                    "channels": source_node.image.channels
                }
                node["texture_slot"] = texture_slot_id

                texture = self.createTexture2DFromNode(source_node)
                stateset.texture_attributes.setdefault(texture_slot_id, []).append(texture)
                texture_slot_id += 1

            tree['nodes'][source_node.name] = node

        # safely delete unused nodes
        nodes = tree['nodes']
        for name in list(nodes.keys()):
            node = nodes[name]
            if all(map(lambda socket: len(socket['links']) == 0, node['inputs'])) and \
               all(map(lambda socket: len(socket['links']) == 0, node['outputs'])):
                del nodes[name]

        material.getOrCreateUserData().append(StringValueObject("NodeTree", json.dumps(tree)))

    def createStateSetShaderNodeUserData(self, mat_source, material):
        """
        reads a shadernode to a basic material
        """
        userData = material.getOrCreateUserData()
        for node in mat_source.node_tree.nodes:
            if node.type == "BSDF_DIFFUSE":
                if not node.inputs["Color"].is_linked:
                    value = node.inputs["Color"].default_value
                    userData.append(StringValueObject("DiffuseColor",
                                                      "[{}, {}, {}]".format(value[0],
                                                                            value[1],
                                                                            value[2])))
            elif node.type == "BSDF_GLOSSY":
                if not node.inputs["Color"].is_linked:
                    value = node.inputs["Color"].default_value
                    userData.append(StringValueObject("SpecularColor",
                                                      "[{}, {}, {}]".format(value[0],
                                                                            value[1],
                                                                            value[2])))

    def createStateSetMaterial(self, mat_source, stateset, material):
        """
        Reads a blender material into an osg stateset/material
        """
        anim = createAnimationMaterialAndSetCallback(material, mat_source, self.config, self.unique_objects)
        if anim:
            self.material_animations[anim.name] = anim

        if mat_source.use_shadeless:
            stateset.modes["GL_LIGHTING"] = "OFF"

        alpha = 1.0
        if mat_source.use_transparency:
            alpha = 1.0 - mat_source.alpha

        refl = mat_source.diffuse_intensity
        # we premultiply color with intensity to have rendering near blender for opengl fixed pipeline
        material.diffuse = (mat_source.diffuse_color[0] * refl,
                            mat_source.diffuse_color[1] * refl,
                            mat_source.diffuse_color[2] * refl,
                            alpha)

        # if alpha not 1 then we set the blending mode on
        if DEBUG:
            Log("state material alpha {}".format(alpha))
        if alpha != 1.0:
            stateset.modes["GL_BLEND"] = "ON"

        ambient_factor = mat_source.ambient
        if bpy.context.scene.world:
            material.ambient = ((bpy.context.scene.world.ambient_color[0]) * ambient_factor,
                                (bpy.context.scene.world.ambient_color[1]) * ambient_factor,
                                (bpy.context.scene.world.ambient_color[2]) * ambient_factor,
                                1.0)
        else:
            material.ambient = (0, 0, 0, 1.0)

        # we premultiply color with intensity to have rendering near blender for opengl fixed pipeline
        spec = mat_source.specular_intensity
        material.specular = (mat_source.specular_color[0] * spec,
                             mat_source.specular_color[1] * spec,
                             mat_source.specular_color[2] * spec,
                             1)

        emissive_factor = mat_source.emit
        material.emission = (mat_source.diffuse_color[0] * emissive_factor,
                             mat_source.diffuse_color[1] * emissive_factor,
                             mat_source.diffuse_color[2] * emissive_factor,
                             1)
        material.shininess = (mat_source.specular_hardness / 512.0) * 128.0

        material_data = self.createStateSetMaterialData(mat_source, stateset)

        if self.config.json_materials:
            self.createStateSetMaterialJson(material_data, stateset)
        else:
            self.createStateSetMaterialUserData(material_data, stateset, material)

        return stateset

    def createStateSetMaterialData(self, mat_source, stateset):
        """
        Reads a blender material into an osg stateset/material json userdata
        """
        def premultAlpha(slot, data):
            if slot.texture and slot.texture.image:
                data["UsePremultiplyAlpha"] = slot.texture.image.alpha_mode == 'PREMULT'

        def useAlpha(slot, data):
            if slot.texture and slot.texture.use_alpha:
                data["UseAlpha"] = True

        data = {}

        data["DiffuseIntensity"] = mat_source.diffuse_intensity
        data["DiffuseColor"] = [mat_source.diffuse_color[0],
                                mat_source.diffuse_color[1],
                                mat_source.diffuse_color[2]]

        data["SpecularIntensity"] = mat_source.specular_intensity
        data["SpecularColor"] = [mat_source.specular_color[0],
                                 mat_source.specular_color[1],
                                 mat_source.specular_color[2]]

        data["SpecularHardness"] = mat_source.specular_hardness

        if mat_source.use_shadeless:
            data["Shadeless"] = True
        else:
            data["Emit"] = mat_source.emit
            data["Ambient"] = mat_source.ambient
        data["Translucency"] = mat_source.translucency
        data["DiffuseShader"] = mat_source.diffuse_shader
        data["SpecularShader"] = mat_source.specular_shader
        if mat_source.use_transparency:
            data["Transparency"] = True
            data["TransparencyMethod"] = mat_source.transparency_method

        if mat_source.diffuse_shader == "TOON":
            data["DiffuseToonSize"] = mat_source.diffuse_toon_size
            data["DiffuseToonSmooth"] = mat_source.diffuse_toon_smooth

        if mat_source.diffuse_shader == "OREN_NAYAR":
            data["Roughness"] = mat_source.roughness

        if mat_source.diffuse_shader == "MINNAERT":
            data["Darkness"] = mat_source.roughness

        if mat_source.diffuse_shader == "FRESNEL":
            data["DiffuseFresnel"] = mat_source.diffuse_fresnel
            data["DiffuseFresnelFactor"] = mat_source.diffuse_fresnel_factor

        # specular
        if mat_source.specular_shader == "TOON":
            data["SpecularToonSize"] = mat_source.specular_toon_size
            data["SpecularToonSmooth"] = mat_source.specular_toon_smooth

        if mat_source.specular_shader == "WARDISO":
            data["SpecularSlope"] = mat_source.specular_slope

        if mat_source.specular_shader == "BLINN":
            data["SpecularIor"] = mat_source.specular_ior

        data["TextureSlots"] = {}
        texture_list = mat_source.texture_slots
        if DEBUG:
            Log("texture list {}".format(texture_list))

        for i, texture_slot in enumerate(texture_list):
            if texture_slot is None:
                continue

            texture = self.createTexture2D(texture_slot)
            if DEBUG:
                Log("texture {} {}".format(i, texture_slot))
            if texture is None:
                continue

            data_texture_slot = data["TextureSlots"].setdefault(i, {})

            for (use_map, name, factor) in (('use_map_diffuse', 'DiffuseIntensity', 'diffuse_factor'),
                                            ('use_map_color_diffuse', 'DiffuseColor', 'diffuse_color_factor'),
                                            ('use_map_alpha', 'Alpha', 'alpha_factor'),
                                            ('use_map_translucency', 'Translucency', 'translucency_factor'),
                                            ('use_map_specular', 'SpecularIntensity', 'specular_factor'),
                                            ('use_map_color_spec', 'SpecularColor', 'specular_color_factor'),
                                            ('use_map_mirror', 'Mirror', 'mirror_factor'),
                                            ('use_map_normal', 'Normal', 'normal_factor'),
                                            ('use_map_ambient', 'Ambient', 'ambient_factor'),
                                            ('use_map_emit', 'Emit', 'emit_factor')):
                if getattr(texture_slot, use_map):
                    premultAlpha(texture_slot, data_texture_slot)
                    useAlpha(texture_slot, data_texture_slot)
                    data_texture_slot[name] = getattr(texture_slot, factor)

            # use blend
            data_texture_slot["BlendType"] = texture_slot.blend_type

            stateset.texture_attributes.setdefault(i, []).append(texture)

            try:
                if t.source_image.getDepth() > 24:  # there is an alpha
                    stateset.modes["GL_BLEND"] = "ON"
            except:
                pass

        return data

    def createStateSetMaterialJson(self, data, stateset):
        """
        Serialize blender material data into stateset as a JSON user data
        """
        stateset.getOrCreateUserData().append(StringValueObject("BlenderMaterial",
                                                                json.dumps(data)))

    def createStateSetMaterialUserData(self, data, stateset, material):
        """
        Serialize blender material data into material as a collection of string user data
        """
        def toUserData(value):
            # dict-like values are *not* serialized
            if isinstance(value, (list, tuple)):
                return "[{}]".format(", ".join(toUserData(x) for x in value))
            elif isinstance(value, (int, float, bool)):
                return json.dumps(value)
            elif isinstance(value, str):
                return value
            return None

        userData = material.getOrCreateUserData()

        for key, value in data.items():
            userdata = toUserData(value)
            if userdata is not None:
                userData.append(StringValueObject(key, userdata))

        slot_name = lambda index, label: "{:02}_{}".format(index, label)

        userData = stateset.getOrCreateUserData()
        for index, slot in data["TextureSlots"].items():
            for key, value in slot.items():
                userData.append(StringValueObject(slot_name(index, key), toUserData(value)))

    def parseMorphTargets(self, obj, geometry, morph_vertex_map, material_index):
        ''' Create morph targets '''
        # Absolute shape keys are converted during baking. The data is parsed
        # in the same way for both absolute and relative keyframes
        for key in obj.data.shape_keys.key_blocks:
            if key.relative_key == key:
                continue

            target = Geometry()
            target.name = spaceSafe('{}_{}_{}'.format(obj.name, material_index, key.name))

            osg_vertexes = VertexArray()
            for i in range(len(morph_vertex_map)):
                osg_vertexes.getArray().append([key.data[morph_vertex_map[i]].co[0],
                                                key.data[morph_vertex_map[i]].co[1],
                                                key.data[morph_vertex_map[i]].co[2]])

            target.vertexes = osg_vertexes
            # FIXME we don't currently generate normals, so osganimationviewer will crash
            target.primitives = geometry.primitives
            geometry.morphTargets.append(target)
            target.factor = key.value

    def createGeometryForMaterialIndex(self, material_index, mesh):
        if hasShapeKeys(self.object):
            geom = MorphGeometry()
        else:
            geom = Geometry()

        geom.groups = {}
        if bpy.app.version[0] >= 2 and bpy.app.version[1] >= 63:
            faces = mesh.tessfaces
            uv_textures = mesh.tessface_uv_textures
            vertex_colors = mesh.tessface_vertex_colors.active
        else:
            faces = mesh.faces
            uv_textures = mesh.uv_textures
        if (len(faces) == 0):
            Log("object {} has no faces, so no materials".format(self.object.name))
            return None
        if len(mesh.materials) and mesh.materials[material_index] is not None:
            material_name = mesh.materials[material_index].name
            title = "mesh {} with material {}".format(self.object.name, material_name)
        else:
            title = "mesh {} without material".format(self.object.name)
        Log(title)

        arm_modifiers = [mod for mod in self.object.modifiers if mod.type == 'ARMATURE' and mod.object]
        armature_name = ('_' + str(arm_modifiers[-1].object.name)) if arm_modifiers else ''
        if self.object.vertex_groups and self.object.parent \
           and self.object.parent.type == 'ARMATURE' \
           and not self.object.parent_bone:
            armature_name = '_' + str(self.object.parent.name)

        collected_faces = []
        morph_map = []
        osg_vertexes = VertexArray()
        osg_normals = NormalArray()
        osg_colors = ColorArray()

        osg_uvs = OrderedDict()
        lines = DrawElements()
        lines.type = "GL_LINES"
        triangles = DrawElements()
        triangles.type = "GL_TRIANGLES"
        quads = DrawElements()
        quads.type = "GL_QUADS"
        primitives = []
        nquad = 0
        nlin = 0
        ntri = 0
        vgroups = {}
        # index remapping
        vertex_index_map = {}

        def get_vertex_key(faceindex, facevertexindex):
            if face.use_smooth:
                normal = list(mesh.vertices[face.vertices[facevertexindex]].normal)
            else:
                normal = list(face.normal)

            if vertex_colors:
                vcolors = tuple(getattr(vertex_colors.data[faceindex], 'color{}'.format(facevertexindex + 1)))
            else:
                vcolors = tuple()

            texcoords = [tuple(truncateVector(list(uv.data[faceindex].uv[facevertexindex])))
                         for uv in mesh.tessface_uv_textures]
            return (face.vertices[facevertexindex], tuple(truncateVector(normal)), tuple(texcoords), vcolors)

        for face in faces:
            if face.material_index != material_index:
                continue

            for facevertexindex, vert_index in enumerate(face.vertices):
                # Uvs and colors are per face and not per vertexes, so need to deduplicate
                # this here using keys.
                # A key is build as (vertexIndex, normal, texcoords={},vertex_colors)
                key = get_vertex_key(face.index, facevertexindex)
                if key not in vertex_index_map:
                    newindex = len(osg_vertexes.getArray())
                    vertex_index_map[key] = newindex
                    morph_map.append(vert_index)
                    uvs = []

                    for uv in mesh.tessface_uv_textures:
                        uvs.append(uv.data[face.index].uv[facevertexindex])

                    if self.object.vertex_groups:
                        for vertex_group in mesh.vertices[vert_index].groups:
                            influence = [self.object.vertex_groups[vertex_group.group].name, vertex_group.weight]
                            # try:getBoneByName(influence[0])  # check bone existence
                            if influence[0] != "" and influence[1] > 0.0001:
                                if influence[0] not in vgroups:
                                    vg = VertexGroup()
                                    vg.targetGroupName = spaceSafe(influence[0] + armature_name)
                                    vg.vertexes.append((newindex, influence[1]))
                                    vgroups[influence[0]] = vg
                                else:
                                    vgroups[influence[0]].vertexes.append((newindex, vertex_group.weight))

                    osg_normals.getArray().append(key[1])
                    osg_vertexes.getArray().append(list(mesh.vertices[vert_index].co))
                    # beware this enumerate, order can be different ?
                    for idx, uv in enumerate(mesh.tessface_uv_textures):
                        osg_uvs.setdefault(uv.name, TexCoordArray()).getArray().append(key[2][idx])

                    if vertex_colors:
                        col = key[len(key) - 1]
                        osg_colors.getArray().append([col[0], col[1], col[2]])

            # facelength test : crawl primitives
            facelength = len(face.vertices)
            if facelength == 2:
                nlin = nlin + 1

                lines.indexes.append(vertex_index_map[get_vertex_key(face.index, 0)])
                lines.indexes.append(vertex_index_map[get_vertex_key(face.index, 1)])
            elif facelength == 3:
                ntri = ntri + 1
                triangles.indexes.append(vertex_index_map[get_vertex_key(face.index, 0)])
                triangles.indexes.append(vertex_index_map[get_vertex_key(face.index, 1)])
                triangles.indexes.append(vertex_index_map[get_vertex_key(face.index, 2)])

            elif facelength == 4:
                nquad = nquad + 1
                quads.indexes.append(vertex_index_map[get_vertex_key(face.index, 0)])
                quads.indexes.append(vertex_index_map[get_vertex_key(face.index, 1)])
                quads.indexes.append(vertex_index_map[get_vertex_key(face.index, 2)])
                quads.indexes.append(vertex_index_map[get_vertex_key(face.index, 3)])

            else:
                osglog.log("WARNING can't manage faces with {} vertices".format(nv))

            collected_faces.append(face)

        if (len(collected_faces) == 0):
            Log("object {} has no faces for sub material slot {}".format(self.object.name, material_index))
            end_title = '-' * len(title)
            Log(end_title)
            return None

        if len(lines.indexes) != 0:
            primitives.append(lines)
        if len(triangles.indexes) != 0:
            primitives.append(triangles)
        if len(quads.indexes) != 0:
            primitives.append(quads)

        geom.uvs = osg_uvs
        geom.groups = vgroups
        if mesh.vertex_colors:
            geom.colors = osg_colors

        geom.vertexes = osg_vertexes
        geom.normals = osg_normals
        geom.primitives = primitives
        geom.setName(self.object.name)
        stateset = self.createStateSet(material_index, mesh)
        if stateset is not None:
            geom.stateset = stateset

        if len(mesh.materials) > 0 and mesh.materials[material_index] is not None:
            self.adjustUVLayerFromMaterial(geom, mesh.materials[material_index], uv_textures)

        end_title = '-' * len(title)
        Log(end_title)

        if geom.className() == "MorphGeometry":
            self.parseMorphTargets(self.object, geom, morph_map, material_index)

        return geom

    def process(self, mesh):
        if bpy.app.version[0] >= 2 and bpy.app.version[1] >= 63:
            mesh.update(calc_tessface=True)  # Generates faces of 3 or 4 vertices

        geometry_list = []
        material_index = 0
        if len(mesh.materials) == 0:
            geom = self.createGeometryForMaterialIndex(0, mesh)
            if geom is not None:
                geometry_list.append(geom)
        else:
            for material in mesh.materials:
                # Blender has an operator to split mesh by material (bpy.ops.mesh.separate(type='MATERIAL'))
                geom = self.createGeometryForMaterialIndex(material_index, mesh)
                if geom is not None:
                    geometry_list.append(geom)
                material_index += 1
        return geometry_list

    def convert(self):
        # looks like this was dropped
        # if self.mesh.vertexUV:
        #     Log("Warning: [[blender]] mesh %s use sticky UV and it's not supported" % self.object.name)

        return self.process(self.mesh)


class BlenderAnimationToAnimation(object):
    def __init__(self, *args, **kwargs):
        self.config = kwargs["config"]
        self.object = kwargs.get("object", None)
        self.unique_objects = kwargs.get("unique_objects", UniqueObject())
        self.animations = None
        self.current_action = None
        self.baked_actions = []
        self.action_name = None
        self.has_action = kwargs.get("has_action", False)
        self.has_constraints = kwargs.get("has_constraints", False)
        self.has_morph = kwargs.get("has_morph", False)
        self.channel_index = 0
        if self.object:
            self.target = self.object.name
        else:
            Log("Warning: animation with no target")
            self.target = 'unknown target'
        # Set action as current action
        if self.has_action:
            self.current_action = self.object.animation_data.action
            self.action_name = self.current_action.name
        if self.has_morph:
            if hasAction(self.object.data.shape_keys):
                self.current_action = self.object.data.shape_keys.animation_data.action
            else:
                self.current_action = self.object.animation_data.action
            self.action_name = self.current_action.name

    def needBake(self, blender_object):
        if self.has_constraints and self.config.bake_constraints:
            Log("Baking constraints " + str(self.object.constraints))
            return True
        else:
            if self.has_action:
                for fcu in self.current_action.fcurves:
                    for kf in fcu.keyframe_points:
                        if kf.interpolation != 'LINEAR':
                            return True
        return False

    def handleMorphAnimationBaking(self, is_multi_animation=False):
        Log("Exporting morph animation on object {}".format(self.object.name))
        # We always bake if shape_keys are absolute as they need to be converted to relative
        if not self.has_morph or \
           (self.object.data.shape_keys.use_relative and not self.config.bake_animations):
            return

        if is_multi_animation:
            # Bake animation using current action frame_range
            if self.object.data.shape_keys.animation_data and self.object.data.shape_keys.animation_data.action:
                start, end = self.object.data.shape_keys.animation_data.action.frame_range
            else:
                start, end = self.object.animation_data.action.frame_range
        else:
            start, end = getWidestActionDuration(self.config.scene)

        self.current_action = osgbake.bakeMorphTargets(int(start), int(end), self.object)

    def handleAnimationBaking(self, is_multi_animation=False):
        Log("Exporting animation on object {}".format(self.object.name))
        if self.has_action and not self.current_action:
            self.current_action = self.object.animation_data.action

        if self.config.bake_animations or self.needBake(self.object):
            # all scene actions will be baked and merged together into a single
            # osg animation, so define start and end frames with the wider duration
            start = self.config.scene.frame_start
            end = self.config.scene.frame_end

            if is_multi_animation:
                # Bake animation using current action frame_range
                start, end = self.object.animation_data.action.frame_range
            else:
                # Bake using widest time range to have short animations looping
                start, end = getWidestActionDuration(self.config.scene)

            print('BAKING animation for action')
            self.current_action = osgbake.bakeAnimation(self.config.scene,
                                                        int(start),
                                                        int(end),
                                                        self.config.bake_frame_step,
                                                        self.object,
                                                        use_quaternions=self.config.use_quaternions,
                                                        has_action=self.has_action)
            self.baked_actions.append(self.current_action)
        self.action_name = self.object.animation_data.action.name if self.has_action else 'Action_baked'

    def parseAllActions(self):
        def parseSolidRigAction():
            if hasAction(self.object):
                backup_action = self.object.animation_data.action
                # The object is animated so we always have animation_data not None here
                try:
                    self.object.animation_data.action = action
                except AttributeError:
                    Log("Warning: Can't set action '{}' to object {} (read-only)"
                        .format(action.name, self.object.name))
                    return
                self.handleAnimationBaking(is_multi_animation=True)
                self.addActionDataToAnimation(anim, morph=False)
                self.object.animation_data.action = backup_action
                anims.append(anim)
                if backup_action:
                    self.object.animation_data.action = backup_action

        def parseMorphAction():
            anim_object = self.object if isObjectMorphAction(action) else self.object.data.shape_keys
            need_clear = False
            backup_action = None
            if hasAction(anim_object):
                backup_action = anim_object.animation_data.action
            if not anim_object.animation_data:
                anim_object.animation_data_create()
                need_clear = True
            anim_object.animation_data.action = action
            self.handleMorphAnimationBaking(is_multi_animation=True)
            self.addActionDataToAnimation(anim, morph=True)
            anims.append(anim)
            if backup_action:
                anim_object.animation_data.action = backup_action
            if need_clear:
                anim_object.animation_data_clear()

        anims = []
        if not self.has_action and not self.has_morph and not hasNLATracks(self.object):
            Log("Warning: osgdata::parseAllActions object has no action")
            return anims
        actions_dict = dict(bpy.data.actions)
        actions = {key: actions_dict[key] for key in actions_dict if actions_dict[key].users > 0}
        for action_key in actions:
            # TODO handle morph here
            print("parseAllActions: parsing {} ".format(action_key))
            anim = Animation()
            action = bpy.data.actions[action_key]
            self.current_action = action
            anim.setName(action.name)
            if isSolidOrRigAction(action):
                if not (self.object.type != 'ARMATURE' and isRigAction(action)):
                    parseSolidRigAction()
            elif hasShapeKeys(self.object):
                parseMorphAction()

        return anims

    def addActionDataToAnimation(self, animation, morph=False):
        if not self.current_action:
            return
        Log('adding data from action {} to animation {}'.format(self.current_action.name, animation))
        if self.current_action is None:
            return
        if self.object.type == "ARMATURE":
            for bone in self.object.data.bones:
                bname = bone.name
                osg_target = spaceSafe('{}_{}'.format(bone.name, self.object.name))
                Log("{} processing channels for bone {}".format(self.action_name, bname))
                self.appendChannelsToAnimation(bname, animation, self.current_action,
                                               prefix=('pose.bones["{}"].'.format(bname)), osg_targetname=osg_target)
            # Append channels for armature solid animation
            self.appendChannelsToAnimation(self.object.name, animation, self.current_action)
        elif morph:
            # need to create as many animation as we generate osg geometries for the object
            # (that correspond to the number of materials of the object)
            for i in range(len(self.object.data.materials) if self.object.data.materials else 1):
                self.channel_index = 0
                for key in self.object.data.shape_keys.key_blocks:
                    osg_target = spaceSafe('{}_{}_{}'.format(self.object.name, i, key.name))
                    self.appendChannelsToAnimation(key.name, animation, self.current_action,
                                                   prefix=('key_blocks["{}"].'.format(key.name)),
                                                   osg_targetname=osg_target)
        else:
            self.appendChannelsToAnimation(self.target, animation, self.current_action)

    def appendChannelsToAnimation(self, target, anim, action, prefix="", osg_targetname=''):
        channels = self.exportActionsToKeyframeSplitRotationTranslationScale(target,
                                                                             action,
                                                                             self.config.anim_fps,
                                                                             prefix,
                                                                             osg_targetname=osg_targetname)
        for channel in channels:
            anim.channels.append(channel)

    def get_generated_actions(self):
        return self.baked_actions

    def getChannel(self, target, action, fps, data_path, array_indexes, osg_targetname):
        times = []
        duration = 0
        fcurves = []

        for array_index in array_indexes:
            for fcurve in action.fcurves:
                # Log("fcurves {} {} matches {} {} ".format(fcurve.data_path,
                #                                                  fcurve.array_index,
                #                                                  data_path,
                #                                                  array_index))
                if fcurve.data_path == data_path and fcurve.array_index == array_index:
                    fcurves.append(fcurve)
                    # Log("yes")

        if len(fcurves) == 0:
            return None

        for fcurve in fcurves:
            for keyframe in fcurve.keyframe_points:
                if times.count(keyframe.co[0]) == 0:
                    times.append(keyframe.co[0])

        if len(times) == 0:
            return None

        channel = Channel()
        channel.target = osg_targetname if osg_targetname else target

        if len(array_indexes) == 1:
            channel.type = "FloatLinearChannel"
        if len(array_indexes) == 3:
            channel.type = "Vec3LinearChannel"
        if len(array_indexes) == 4:
            channel.type = "QuatSphericalLinearChannel"

        times.sort()

        for time in times:
            realtime = (time) / fps
            # Log("time {} {} {}".format(time, realtime, fps))

            # realtime = time
            if realtime > duration:
                duration = realtime

            value = [realtime]
            for fcurve in fcurves:
                value.append(fcurve.evaluate(time))
            channel.keys.append(value)

        return channel

    # as for blender 2.49
    def exportActionsToKeyframeSplitRotationTranslationScale(self, target, action, fps, prefix, osg_targetname=''):
        channels = []

        translate = self.getChannel(target, action, fps, prefix + "location", [0, 1, 2], osg_targetname)
        if translate:
            translate.setName("translate")
            channels.append(translate)

        eulerName = ["euler_x", "euler_y", "euler_z"]
        for i in range(0, 3):
            c = self.getChannel(target, action, fps, prefix + "rotation_euler", [i], osg_targetname)
            if c:
                c.setName(eulerName[i])
                channels.append(c)

        quaternion = self.getChannel(target, action, fps, prefix + "rotation_quaternion", [1, 2, 3, 0], osg_targetname)
        if quaternion:
            quaternion.setName("quaternion")
            channels.append(quaternion)

        axis_angle = self.getChannel(target, action, fps, prefix + "rotation_axis_angle", [1, 2, 3, 0], osg_targetname)
        if axis_angle:
            axis_angle.setName("axis_angle")
            channels.append(axis_angle)

        scale = self.getChannel(target, action, fps, prefix + "scale", [0, 1, 2], osg_targetname)
        if scale:
            scale.setName("scale")
            channels.append(scale)

        morph_factor = self.getChannel(target, action, fps, prefix + "value", [0], osg_targetname)
        if morph_factor:
            morph_factor.setName('\"' + str(self.channel_index) + '\"')
            self.channel_index += 1
            channels.append(morph_factor)

        return channels
