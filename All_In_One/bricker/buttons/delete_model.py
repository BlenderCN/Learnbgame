# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# system imports
import time
import sys

# Blender imports
import bpy
import bmesh
from mathutils import Vector, Euler
props = bpy.props

# Addon imports
from ..functions import *
from .cache import *
from ..lib.background_processing.classes.JobManager import JobManager


def getModelType(cm):
    """ return 'MODEL' if modelCreated, 'ANIMATION' if animated """
    if cm.animated:
        modelType = "ANIMATION"
    elif cm.modelCreated:
        modelType = "MODEL"
    else:
        raise AttributeError("Brick object is in unexpected state")
    return modelType


class BRICKER_OT_delete_model(bpy.types.Operator):
    """Delete brickified model (restores original source object)"""
    bl_idname = "bricker.delete_model"
    bl_label = "Delete Brickified model from Blender"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        """ ensures operator can execute (if not, returns false) """
        scn = bpy.context.scene
        if scn.cmlist_index == -1:
            return False
        return True

    def execute(self, context):
        wm = bpy.context.window_manager
        wm.Bricker_runningBlockingOperation = True
        try:
            cm = getActiveContextInfo()[1]
            self.undo_stack.iterateStates(cm)
            self.runFullDelete()
        except:
            bricker_handle_exception()
        wm.Bricker_runningBlockingOperation = False

        return{"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        cm = getActiveContextInfo()[1]
        # push to undo stack
        self.undo_stack = UndoStack.get_instance()
        self.undo_stack.undo_push('delete', affected_ids=[cm.id])

    #############################################
    # class methods

    @classmethod
    def cleanUp(cls, modelType, cm=None, skipSource=False, skipDupes=False, skipParents=False, skipBricks=False, skipTransAndAnimData=True, preservedFrames=None, source_name=None):
        """ externally callable cleanup function for bricks, source, dupes, and parents """
        # set up variables
        scn, cm, n = getActiveContextInfo(cm=cm)
        source = bpy.data.objects.get(source_name or n)

        if not b280():
            # set all layers active temporarily
            curLayers = list(scn.layers)
            setLayers([True]*20)
            # match source layers to brick layers
            bGroup = bpy_collections().get("Bricker_%(n)s_bricks" % locals())
            if bGroup is not None and len(bGroup.objects) > 0:
                brick = bGroup.objects[0]
                source.layers = brick.layers

        # clean up 'Bricker_[source name]' collection
        if not skipSource:
            cls.cleanSource(cm, n, source, modelType)

        # clean up source model duplicates
        if not skipDupes:
            cls.cleanDupes(cm, n, preservedFrames, modelType)

        if not skipParents:
            brickLoc, brickRot, brickScl = cls.cleanParents(cm, n, preservedFrames, modelType)
        else:
            brickLoc, brickRot, brickScl = None, None, None

        # initialize variables for cursor status updates
        wm = bpy.context.window_manager
        wm.progress_begin(0, 100)
        print()

        if not skipBricks:
            bricker_trans_and_anim_data = cls.cleanBricks(scn, cm, n, preservedFrames, modelType, skipTransAndAnimData)
        else:
            bricker_trans_and_anim_data = []

        if not b280():
            # set scene layers back to original layers
            setLayers(curLayers)

        return source, brickLoc, brickRot, brickScl, bricker_trans_and_anim_data

    @classmethod
    def runFullDelete(cls, cm=None):
        """ externally callable cleanup function for full delete action (clears everything from memory) """
        scn, cm, n = getActiveContextInfo(cm=cm)
        modelType = getModelType(cm)
        origFrame = scn.frame_current
        scn.frame_set(cm.modelCreatedOnFrame)
        bricks = getBricks()
        # store pivot point for model
        if cm.lastSplitModel or cm.animated:
            pivot_point = cm.parent_obj.matrix_world.to_translation()
        else:
            pivot_obj = bricks[0] if len(bricks) > 0 else cm.source_obj
            pivot_point = pivot_obj.matrix_world.to_translation()

        if cm.brickifyingInBackground:
            curJobManager = JobManager.get_instance(cm.id)
            curJobManager.kill_all()

        source, brickLoc, brickRot, brickScl, _ = cls.cleanUp(modelType, cm=cm, skipSource=cm.source_obj is None)

        # select source
        if source is None:
            print("[Bricker] Source object for model could not be found")
        else:
            select(source, active=True)

            # apply transformation to source
            if not cm.armature and len(bricks) > 0 and ((modelType == "MODEL" and (cm.applyToSourceObject or not cm.lastSplitModel)) or (modelType == "ANIMATION" and cm.applyToSourceObject)):
                l, r, s = getTransformData(cm)
                if modelType == "MODEL":
                    loc = strToTuple(cm.lastSourceMid, float)
                    if brickLoc is not None:
                        source.location = source.location + brickLoc - Vector(loc)
                    else:
                        source.location = Vector(l)# - Vector(loc)
                else:
                    source.location = Vector(l)
                source.scale = (source.scale[0] * s[0], source.scale[1] * s[1], source.scale[2] * s[2])
                # set rotation mode
                lastMode = source.rotation_mode
                source.rotation_mode = "XYZ"
                # create vert to track original source origin
                if len(source.data.vertices) == 0: source.data.vertices.add(1)
                last_co = source.data.vertices[0].co.to_tuple()
                source.data.vertices[0].co = (0, 0, 0)
                # set source origin to rotation point for transformed brick object
                scn.update()
                setObjOrigin(source, pivot_point)
                # rotate source
                if cm.useLocalOrient and not cm.useAnimation:
                    source.rotation_euler = brickRot or Euler(tuple(r))
                else:
                    rotateBy = Euler(tuple(r))
                    # if source.parent is not None:
                    #     # TODO: convert rotateBy to local with respect to source's parent
                    source.rotation_euler.rotate(rotateBy)
                # set source origin back to original point (tracked by last vert)
                scn.update()
                setObjOrigin(source, mathutils_mult(source.matrix_world, source.data.vertices[0].co))
                source.data.vertices[0].co = last_co
                source.rotation_mode = lastMode
            # adjust source loc to account for local_orient_offset applied in BRICKER_OT_brickify.transformBricks
            if cm.useLocalOrient and not cm.useAnimation:
                try:
                    source.location -= Vector(source["local_orient_offset"])
                except KeyError:
                    pass

        BRICKER_OT_clear_cache.clearCache(cm, brick_mesh=False)

        # Scale brick height according to scale value applied to source
        cm.brickHeight = cm.brickHeight * cm.transformScale

        # reset default values for select items in cmlist
        cls.resetCmlistAttrs()

        clearTransformData(cm)

        # reset frame (for proper update), update scene and redraw 3D view
        scn.frame_set(origFrame)
        scn.update()
        tag_redraw_areas("VIEW_3D")

    @classmethod
    def cleanSource(cls, cm, n, source, modelType):
        scn = bpy.context.scene
        if b280():
            # link source to all collections containing Bricker model
            brickColl = cm.collection
            brickCollUsers = [cn for cn in bpy.data.collections if brickColl.name in cn.children] if brickColl is not None else [item.collection for item in source.stored_parents]
        else:
            # set source layers to brick layers
            frame = cm.lastStartFrame
            bGroup = bpy_collections().get("Bricker_%(n)s_bricks" % locals() + ("_f_%(frame)s" % locals() if modelType == "ANIMATION" else ""))
            if bGroup and len(bGroup.objects) > 0:
                source.layers = list(bGroup.objects[0].layers)
            brickCollUsers = []
        safeLink(source, collections=brickCollUsers)
        # reset source properties
        source.cmlist_id = -1

    @classmethod
    def cleanDupes(cls, cm, n, preservedFrames, modelType):
        scn = bpy.context.scene
        if modelType == "ANIMATION":
            dupe_name = "Bricker_%(n)s_f_" % locals()
            dObjects = [bpy.data.objects.get(dupe_name + str(fn)) for fn in range(cm.lastStartFrame, cm.lastStopFrame + 1)]
        else:
            dObjects = [bpy.data.objects.get("%(n)s__dup__" % locals())]
        # # if preserve frames, remove those objects from dObjects
        # objsToRemove = []
        # if modelType == "ANIMATION" and preservedFrames is not None:
        #     for obj in dObjects:
        #         if obj is None:
        #             continue
        #         frameNumIdx = obj.name.rfind("_") + 1
        #         curFrameNum = int(obj.name[frameNumIdx:])
        #         if curFrameNum >= preservedFrames[0] and curFrameNum <= preservedFrames[1]:
        #             objsToRemove.append(obj)
        #     for obj in objsToRemove:
        #         dObjects.remove(obj)
        if len(dObjects) > 0:
            delete(dObjects)

    @classmethod
    def cleanParents(cls, cm, n, preservedFrames, modelType):
        scn = bpy.context.scene
        brickLoc, brickRot, brickScl = None, None, None
        p = cm.parent_obj
        if p is None:
            return brickLoc, brickRot, brickScl
        if preservedFrames is None:
            if modelType == "ANIMATION" or cm.lastSplitModel:
                # store transform data of transformation parent object
                try:
                    loc_diff = p["loc_diff"]
                except KeyError:
                    loc_diff = None
                storeTransformData(cm, p, offsetBy=loc_diff)
            if not cm.lastSplitModel and cm.collection is not None:
                bricks = getBricks()
                if len(bricks) > 0:
                    b = bricks[0]
                    scn.update()
                    brickLoc = b.matrix_world.to_translation().copy()
                    brickRot = b.matrix_world.to_euler().copy()
                    brickScl = b.matrix_world.to_scale().copy()  # currently unused
        # clean up Bricker_parent objects
        parents = [p] + (list(p.children) if modelType == "ANIMATION" else [])
        for parent in parents:
            if parent is None:
                continue
            # if preserve frames, skip those parents
            if modelType == "ANIMATION" and preservedFrames is not None:
                frameNumIdx = parent.name.rfind("_") + 1
                try:
                    curFrameNum = int(parent.name[frameNumIdx:])
                    if curFrameNum >= preservedFrames[0] and curFrameNum <= preservedFrames[1]:
                        continue
                except ValueError:
                    continue
            bpy.data.objects.remove(parent, do_unlink=True)
        return brickLoc, brickRot, brickScl

    def updateAnimationData(objs, bricker_trans_and_anim_data):
        """ add anim data for objs to 'bricker_trans_and_anim_data' """
        for obj in objs:
            obj.rotation_mode = "XYZ"
            bricker_trans_and_anim_data.append({"name":obj.name, "loc":obj.location.to_tuple(), "rot":tuple(obj.rotation_euler), "scale":obj.scale.to_tuple(), "action":obj.animation_data.action.copy() if obj.animation_data and obj.animation_data.action else None})

    @classmethod
    def cleanBricks(cls, scn, cm, n, preservedFrames, modelType, skipTransAndAnimData):
        bricker_trans_and_anim_data = []
        wm = bpy.context.window_manager
        if modelType == "MODEL":
            # clean up bricks collection
            sys.stdout.write("\rDeleting...")
            sys.stdout.flush()
            if cm.collection is not None:
                bricks = getBricks()
                if not cm.lastSplitModel:
                    if len(bricks) > 0:
                        storeTransformData(cm, bricks[0])
                if not skipTransAndAnimData:
                    cls.updateAnimationData(bricks, bricker_trans_and_anim_data)
                last_percent = 0
                # remove objects
                delete(bricks)
                bpy_collections().remove(cm.collection, do_unlink=True)
            cm.modelCreated = False
        elif modelType == "ANIMATION":
            # clean up bricks collection
            for i in range(cm.lastStartFrame, cm.lastStopFrame + 1):
                if preservedFrames is not None and i >= preservedFrames[0] and i <= preservedFrames[1]:
                    continue
                percent = (i - cm.lastStartFrame + 1)/(cm.lastStopFrame - cm.lastStartFrame + 1)
                if percent < 1:
                    update_progress("Deleting", percent)
                    wm.progress_update(percent*100)
                brickColl = bpy_collections().get("Bricker_{n}_bricks_f_{i}".format(n=n, i=str(i)))
                if brickColl:
                    bricks = list(brickColl.objects)
                    if not skipTransAndAnimData:
                        cls.updateAnimationData(bricks, bricker_trans_and_anim_data)
                    if len(bricks) > 0:
                        delete(bricks)
                    bpy_collections().remove(brickColl, do_unlink=True)
            if preservedFrames is None:
                bpy_collections().remove(cm.collection, do_unlink=True)
                cm.animated = False
        # finish status update
        update_progress("Deleting", 1)
        wm.progress_end()
        return bricker_trans_and_anim_data

    def resetCmlistAttrs():
        scn, cm, n = getActiveContextInfo()
        cm.modelLoc = "-1,-1,-1"
        cm.modelRot = "-1,-1,-1"
        cm.modelScale = "-1,-1,-1"
        cm.transformScale = 1
        cm.modelCreatedOnFrame = -1
        cm.lastSourceMid = "-1,-1,-1"
        cm.lastLogoType = "NONE"
        cm.lastSplitModel = False
        cm.lastBrickType = "NONE"
        cm.lastLegalBricksOnly = True
        cm.lastMatrixSettings = "NONE"
        cm.lastMaterialType = "NONE"
        cm.lastIsSmoke = False
        cm.animIsDirty = True
        cm.materialIsDirty = True
        cm.modelIsDirty = True
        cm.buildIsDirty = False
        cm.matrixIsDirty = True
        cm.bricksAreDirty = True
        cm.armature = False
        cm.rigid_body = False
        cm.soft_body = False
        cm.exposeParent = False
        cm.version = bpy.props.bricker_version
        cm.activeKey = (-1, -1, -1)
        cm.firstKey = ""
        cm.isSmoke = False
        cm.hasCustomObj1 = False
        cm.hasCustomObj2 = False
        cm.hasCustomObj3 = False
