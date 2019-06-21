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

# System imports
# NONE!

# Blender imports
import bpy
from bpy.types import Operator
from bpy.props import *

# Addon imports
from ..lib.bricksDict import *
from ..functions import *
from ..buttons.customize.functions import *
from ..buttons.customize.undo_stack import *
from ..buttons.delete_model import BRICKER_OT_delete_model
from ..lib.Brick import Bricks
from ..lib.bricksDict.functions import getDictKey


class OBJECT_OT_delete_override(Operator):
    """OK?"""
    bl_idname = "object.delete"
    bl_label = "Delete"
    bl_options = {'REGISTER'}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(self, context):
        # return context.active_object is not None
        return True

    def execute(self, context):
        try:
            self.runDelete(context)
        except:
            bricker_handle_exception()
        return {'FINISHED'}

    def invoke(self, context, event):
        # Run confirmation popup for delete action
        # TODO: support 'self.confirm'
        return context.window_manager.invoke_confirm(self, event)

    ################################################
    # initialization method

    def __init__(self):
        self.undo_stack = UndoStack.get_instance()
        self.iteratedStatesAtLeastOnce = False
        self.objsToDelete = bpy.context.selected_objects
        self.warnInitialize = False
        self.undo_pushed = False

    ###################################################
    # class variables

    use_global = BoolProperty(default=False)
    update_model = BoolProperty(default=True)
    undo = BoolProperty(default=True)
    confirm = BoolProperty(default=True)

    ################################################
    # class methods

    def runDelete(self, context):
        if bpy.props.bricker_initialized:
            for obj in self.objsToDelete:
                if obj.isBrick:
                    self.undo_stack.undo_push('delete_override')
                    self.undo_pushed = True
                    break
        else:
            # initialize objNamesD (key:cm_id, val:list of brick objects)
            objNamesD = createObjNamesD(self.objsToDelete)
            # remove brick type objects from selection
            for obj_names_list in objNamesD.values():
                if len(obj_names_list) > 0:
                    for obj_name in obj_names_list:
                        self.objsToDelete.remove(bpy.data.objects.get(obj_name))
                    if not self.warnInitialize:
                        self.report({"WARNING"}, "Please initialize the Bricker [shift+i] before attempting to delete bricks")
                        self.warnInitialize = True
        # run deleteUnprotected
        protected = self.deleteUnprotected(context, self.use_global, self.update_model)
        # alert user of protected objects
        if len(protected) > 0:
            self.report({"WARNING"}, "Bricker is using the following object(s): " + str(protected)[1:-1])
        # push delete action to undo stack
        if self.undo:
            bpy.ops.ed.undo_push(message="Delete")
        tag_redraw_areas("VIEW_3D")

    def deleteUnprotected(self, context, use_global=False, update_model=True):
        scn = context.scene
        protected = []
        objNamesToDelete = [obj.name for obj in self.objsToDelete]

        # initialize objNamesD (key:cm_id, val:list of brick objects)
        objNamesD = createObjNamesD(self.objsToDelete)

        # update matrix
        for i, cm_id in enumerate(objNamesD.keys()):
            cm = getItemByID(scn.cmlist, cm_id)
            if createdWithUnsupportedVersion(cm):
                continue
            lastBlenderState = cm.blender_undo_state
            # get bricksDict from cache
            bricksDict = getBricksDict(cm)
            if not update_model:
                continue
            if bricksDict is None:
                self.report({"WARNING"}, "Adjacent bricks in model '" + cm.name + "' could not be updated (matrix not cached)")
                continue
            keysToUpdate = []
            cm.customized = True

            for obj_name in objNamesD[cm_id]:
                # get dict key details of current obj
                dictKey = getDictKey(obj_name)
                x0, y0, z0 = getDictLoc(bricksDict, dictKey)
                # get size of current brick (e.g. [2, 4, 1])
                objSize = bricksDict[dictKey]["size"]

                # for all locations in bricksDict covered by current obj
                for x in range(x0, x0 + objSize[0]):
                    for y in range(y0, y0 + objSize[1]):
                        for z in range(z0, z0 + (objSize[2] // cm.zStep)):
                            curKey = listToStr((x, y, z))
                            # make adjustments to adjacent bricks
                            if cm.autoUpdateOnDelete and cm.lastSplitModel:
                                self.updateAdjBricksDicts(bricksDict, cm.zStep, curKey, [x, y, z], keysToUpdate)
                            # reset bricksDict values
                            bricksDict[curKey]["draw"] = False
                            bricksDict[curKey]["val"] = 0
                            bricksDict[curKey]["parent"] = None
                            bricksDict[curKey]["created_from"] = None
                            bricksDict[curKey]["flipped"] = False
                            bricksDict[curKey]["rotated"] = False
                            bricksDict[curKey]["top_exposed"] = False
                            bricksDict[curKey]["bot_exposed"] = False
            # dirtyBuild if it wasn't already
            lastBuildIsDirty = cm.buildIsDirty
            if not lastBuildIsDirty:
                cm.buildIsDirty = True
            # merge and draw modified bricks
            if len(keysToUpdate) > 0:
                # split up bricks before drawUpdatedBricks calls attemptMerge
                keysToUpdate = uniquify1(keysToUpdate)
                for k0 in keysToUpdate.copy():
                    keysToUpdate += Bricks.split(bricksDict, k0, cm.zStep, cm.brickType)
                keysToUpdate = uniquify1(keysToUpdate)
                # remove duplicate keys from the list and delete those objects
                for k2 in keysToUpdate:
                    brick = bpy.data.objects.get(bricksDict[k2]["name"])
                    delete(brick)
                # create new bricks at all keysToUpdate locations (attempts merge as well)
                drawUpdatedBricks(cm, bricksDict, keysToUpdate, selectCreated=False)
                iteratedStates = True
            if not lastBuildIsDirty:
                cm.buildIsDirty = False
            # if undo states not iterated above
            if lastBlenderState == cm.blender_undo_state:
                # iterate undo states
                self.undo_stack.iterateStates(cm)
            self.iteratedStatesAtLeastOnce = True

        # if nothing was done worth undoing but state was pushed
        if not self.iteratedStatesAtLeastOnce and self.undo_pushed:
            # pop pushed value from undo stack
            self.undo_stack.undo_pop_clean()

        # delete bricks
        for obj_name in objNamesToDelete:
            obj = bpy.data.objects.get(obj_name)
            if obj is None:
                continue
            if obj.isBrickifiedObject or obj.isBrick:
                self.deleteBrickObject(obj, update_model, use_global)
            elif not obj.protected:
                obj_users_scene = len(obj.users_scene)
                if use_global or obj_users_scene == 1:
                    bpy.data.objects.remove(obj, do_unlink=True)
            else:
                print(obj.name + ' is protected')
                protected.append(obj.name)

        tag_redraw_areas("VIEW_3D")

        return protected

    @staticmethod
    def updateAdjBricksDicts(bricksDict, zStep, curKey, curLoc, keysToUpdate):
        x, y, z = curLoc
        newBricks = []
        adjKeys = getAdjKeysAndBrickVals(bricksDict, key=curKey)[0]
        # set adjacent bricks to shell if deleted brick was on shell
        for k0 in adjKeys:
            if bricksDict[k0]["val"] != 0:  # if adjacent brick not outside
                bricksDict[k0]["val"] = 1
                if not bricksDict[k0]["draw"]:
                    bricksDict[k0]["draw"] = True
                    bricksDict[k0]["size"] = [1, 1, zStep]
                    bricksDict[k0]["parent"] = "self"
                    bricksDict[k0]["type"] = bricksDict[curKey]["type"]
                    bricksDict[k0]["flipped"] = bricksDict[curKey]["flipped"]
                    bricksDict[k0]["rotated"] = bricksDict[curKey]["rotated"]
                    bricksDict[k0]["mat_name"] = bricksDict[curKey]["mat_name"]
                    bricksDict[k0]["near_face"] = bricksDict[curKey]["near_face"]
                    ni = bricksDict[curKey]["near_intersection"]
                    bricksDict[k0]["near_intersection"] = tuple(ni) if type(ni) in [list, tuple] else ni
                    # add key to list for drawing
                    keysToUpdate.append(k0)
                    newBricks.append(k0)
        # top of bricks below are now exposed
        k0 = listToStr((x, y, z - 1))
        if k0 in bricksDict and bricksDict[k0]["draw"]:
            k1 = k0 if bricksDict[k0]["parent"] == "self" else bricksDict[k0]["parent"]
            if not bricksDict[k1]["top_exposed"]:
                bricksDict[k1]["top_exposed"] = True
                # add key to list for drawing
                keysToUpdate.append(k1)
        # bottom of bricks above are now exposed
        k0 = listToStr((x, y, z + 1))
        if k0 in bricksDict and bricksDict[k0]["draw"]:
            k1 = k0 if bricksDict[k0]["parent"] == "self" else bricksDict[k0]["parent"]
            if not bricksDict[k1]["bot_exposed"]:
                bricksDict[k1]["bot_exposed"] = True
                # add key to list for drawing
                keysToUpdate.append(k1)
        return keysToUpdate, newBricks

    def deleteBrickObject(self, obj, update_model=True, use_global=False):
        scn = bpy.context.scene
        cm = None
        for cmCur in scn.cmlist:
            n = getSourceName(cmCur)
            if not obj.name.startswith("Bricker_%(n)s_brick" % locals()):
                continue
            if obj.isBrickifiedObject:
                cm = cmCur
                break
            elif obj.isBrick:
                curBricks = cmCur.collection
                if curBricks is not None and len(curBricks.objects) < 2:
                    cm = cmCur
                    break
        if cm and update_model:
            BRICKER_OT_delete_model.runFullDelete(cm=cm)
            deselect(bpy.context.active_object)
        else:
            obj_users_scene = len(obj.users_scene)
            if use_global or obj_users_scene == 1:
                bpy.data.objects.remove(obj, do_unlink=True)

    ################################################
