bl_info = {
    "name": "KinectToPin mocap", 
    "author": "Nick Fox-Gieg",
    "description": "Import and export K2P xml format",
    "category": "Animation"
}

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import (BoolProperty, FloatProperty, StringProperty, IntProperty, PointerProperty, EnumProperty)
from bpy_extras.io_utils import (ImportHelper, ExportHelper)
import xml.dom.minidom as xd
import xml.etree.ElementTree as etree

# ~ ~ ~ 

def select(target=None):
    if not target:
        target=bpy.context.selected_objects;
    print("selected " + str(target))
    return target

def ss():
	returns = select()
	if (len(returns) > 0):
	    return returns[0]
	else:
		return None

s = select

def deselect():
    bpy.ops.object.select_all(action='DESELECT')

def refresh():
    bpy.context.scene.update()

def addLocator(target=None, draw_size=0.1):
    if not target:
        target = ss()
    empty = bpy.data.objects.new("Empty", None)
    empty.empty_draw_size = draw_size
    bpy.context.scene.objects.link(empty)
    bpy.context.scene.update()
    if (target != None):
        empty.location = target.location
    return empty

def rename(target=None, name="Untitled"):
    if not target:
        target = ss()
    target.name = name
    return target.name

def goToFrame(_index):
    origFrame = bpy.context.scene.frame_current
    bpy.context.scene.frame_current = _index
    bpy.context.scene.frame_set(_index)
    refresh()
    print("Moved from timeline frame " + str(origFrame) + " to " + str(_index))
    return bpy.context.scene.frame_current

def currentFrame(target=None):
    if not target:
        return bpy.context.scene.frame_current
    else:
        goToFrame(target)

def getStartEnd(pad=True):
    start = bpy.context.scene.frame_start
    end = None
    if (pad==True):
        end = bpy.context.scene.frame_end + 1
    else:
        end = bpy.context.scene.frame_end
    return start, end

def keyTransform(_obj, _frame):
    _obj.keyframe_insert(data_path="location", frame=_frame) 
    _obj.keyframe_insert(data_path="rotation_euler", frame=_frame) 
    _obj.keyframe_insert(data_path="scale", frame=_frame)

# ~ ~ ~ 

def readKinectToPin(filepath=None, resizeTimeline=True, drawSize=0.1):
    joints = ["l_foot","l_knee","l_hip","r_foot","r_knee","r_hip","l_hand","l_elbow","l_shoulder","r_hand","r_elbow","r_shoulder","torso","neck","head"]
    globalScale = (1, -1, 1)

    xmlFile = xd.parse(filepath)

    for joint in joints:    
        deselect()
        frames = xmlFile.getElementsByTagName(joint)
        loc = addLocator(target=None, draw_size=drawSize)
        rename(loc, joint)

        for i, frame in enumerate(frames):
            x = float(frame.getAttribute("x")) * globalScale[0]
            y = float(frame.getAttribute("y")) * globalScale[1]
            z = float(frame.getAttribute("z")) * globalScale[2]
            
            goToFrame(i)
            loc.location = (x, z, y)
            keyTransform(loc, currentFrame())

def writeKinectToPin(filepath=None, bake=False):
    start, end = getStartEnd()

    openniNames = ["head", "neck", "torso", "l_shoulder", "l_elbow", "l_hand", "r_shoulder", "r_elbow", "r_hand", "l_hip", "l_knee", "l_foot", "r_hip", "r_knee", "r_foot"]
    openniNames_jnt = ["head_jnt", "neck_jnt", "torso_jnt", "l_shoulder_jnt", "l_elbow_jnt", "l_hand_jnt", "r_shoulder_jnt", "r_elbow_jnt", "r_hand_jnt", "l_hip_jnt", "l_knee_jnt", "l_foot_jnt", "r_hip_jnt", "r_knee_jnt", "r_foot_jnt"]
    cmuNames = ["Head", "Neck1", "Spine", "LeftArm", "LeftForeArm", "LeftFingerBase", "RightArm", "RightForeArm", "RightFingerBase", "LeftUpLeg", "LeftLeg", "LeftToeBase", "RightUpLeg", "RightLeg", "RightToeBase"]
    mobuNames = ["Head", "Neck", "Spine", "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand", "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot"]

    doc = xd.Document()

    root_node = doc.createElement("MotionCapture")
    doc.appendChild(root_node)
    root_node.setAttribute("width", "640")
    root_node.setAttribute("height", "480")
    root_node.setAttribute("depth", "200")
    root_node.setAttribute("dialogueFile", "none")
    root_node.setAttribute("fps", "24")
    root_node.setAttribute("numFrames", str(end))

    for i in range(start, end):
        goToFrame(i)
        frame_node = doc.createElement("MocapFrame")
        root_node.appendChild(frame_node)
        frame_node.setAttribute("index",str(i-1))

        skel_node = doc.createElement("Skeleton")
        frame_node.appendChild(skel_node)
        skel_node.setAttribute("id","0")

        joint_node = doc.createElement("Joints")
        skel_node.appendChild(joint_node)

        joints = None
        target = s()
        if (len(target) == 1): # assume root joint selected
            joints = getChildren(target)
            joints.append(target)
        elif (len(target) > 1): # assume all joints at same level
            joints = target
        else:
            return

        for j in range(0,len(joints)):
            try:
                theJointName = joints[j].name
                for k in range(0,len(openniNames)):
                    if (theJointName==cmuNames[k] or theJointName==mobuNames[k] or theJointName==openniNames_jnt[k]):
                        theJointName=openniNames[k]
                    if (theJointName==openniNames[k]):
                        k_node = doc.createElement(theJointName)
                        joint_node.appendChild(k_node)

                        p = joints[j].location
                        k_node.setAttribute("x", str(p[0]))
                        k_node.setAttribute("y", str(-p[2]))
                        k_node.setAttribute("z", str(p[1]))
            except:
                pass

    with open(filepath, "w") as f:
        f.write(doc.toprettyxml())
        f.closed

# ~ ~ ~ 

class ImportK2P(bpy.types.Operator, ImportHelper):
    """Load a KinectToPin xml File"""
    resizeTimeline = BoolProperty(name="Resize Timeline", description="Set in and out points", default=True)
    drawSize = FloatProperty(name="Empty Draw Size", description="Size of the empty objects", default=0.1)

    bl_idname = "import_scene.k2p"
    bl_label = "Import K2P"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".xml"
    filter_glob = StringProperty(
            default="*.xml",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import kinect_to_pin as k2p
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
        #~
        keywords["resizeTimeline"] = self.resizeTimeline
        keywords["drawSize"] = self.drawSize
        k2p.readKinectToPin(**keywords)
        return {'FINISHED'}

class ExportK2P(bpy.types.Operator, ExportHelper): # TODO combine into one class
    """Save a KinectToPin xml File"""

    bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=False)

    bl_idname = "export_scene.k2p"
    bl_label = 'Export K2P'
    bl_options = {'PRESET'}

    filename_ext = ".xml"

    filter_glob = StringProperty(
            default="*.xml",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import kinect_to_pin as k2p
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake"))
        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
        #~
        keywords["bake"] = self.bake
        #~
        k2p.writeKinectToPin(**keywords)
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportK2P.bl_idname, text="KinectToPin mocap (.xml)")

def menu_func_export(self, context):
    self.layout.operator(ExportK2P.bl_idname, text="KinectToPin mocap (.xml)")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
