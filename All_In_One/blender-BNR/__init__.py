bl_info = {
    "name": "Bone Name Rangler (BNR)",
    "author": "birdd",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Properties > Bone Name Rangler",
    "description": "Set of tools for quickly renaming bones.",
    "warning": "",
    "wiki_url": "https://github.com/birddiq/blender-BNR",
    "tracker_url": "https://github.com/birddiq/blender-BNR/issues",
    "category": "Learnbgame",
    }

##TODO: Add a way to detect child bone chains by defining which axis it faces via xml
##      ie. Would make it so you could rename and chain and its children from say "Pelvis" to "Head" Z+, "WristL" X+, and "WristR" X- with one click
##TODO: Add a preset selector, instead of importing every time. Importing should add to presets.
##TODO: Make the bone list editing better, user shouldn't have to manually construct xml

#pylint: disable=import-error
import bpy 
import bgl
import blf
from bpy_extras import view3d_utils
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
#pylint: enable=import-error
from math import *
import xml.etree.ElementTree as ET

import os
xml_preset_path = os.path.join(bpy.utils.script_paths()[2], "presets", "blender-BNR")

def xml_preset_load(self, context):
    opt = bpy.context.scene.bnr_xml_list_enum
    print(opt)
    if opt == "CLEAR":
        context.scene.BNR_bone_list.clear()
        bpy.types.Scene.BNR_bone_order.clear()
    else:
        BNR_import_list(context, os.path.join(xml_preset_path, opt), True)

def rebuild_xml_presets():
    tmp = [("CLEAR", "Clear", "")]
    for f in os.listdir(xml_preset_path):
        print(f)
        tmp.append(
            (f, f, '')
        )
    bpy.types.Scene.bnr_xml_list_enum = EnumProperty(items=tmp, name="Select Preset", default="CLEAR", update=xml_preset_load)

def BNR_import_list(context, filepath, opt_clear):
    if opt_clear:
        context.scene.BNR_bone_list.clear()
        bpy.types.Scene.BNR_bone_order.clear()

    bpy.types.Scene.BNR_bone_list = ET.parse(filepath).getroot()

    for bone in bpy.types.Scene.BNR_bone_list.iter('bone'):
        bpy.types.Scene.BNR_bone_order.append(bone.get('name'))

    return {'FINISHED'}

class BoneRenameImportList(Operator, ImportHelper):
    """Opens a .txt file containing a list of bones separated by new lines"""
    bl_idname = "bnr.import_list" 
    bl_label = "Import Bone List"
    bl_options = {'PRESET'}

    # ImportHelper mixin class uses this
    filename_ext = ".xml"

    filter_glob = StringProperty(
            default="*.xml",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    opt_clear = BoolProperty(
            name="Clear Bone List",
            description="Clear the current list of bones on import",
            default=True,
            )

    """type = EnumProperty(
            name="Example Enum",
            description="Choose between two items",
            items=(('OPT_A', "First Option", "Description one"),
                   ('OPT_B', "Second Option", "Description two")),
            default='OPT_A',
            )"""

    def execute(self, context):
        return BNR_import_list(context, self.filepath, self.opt_clear)

def rename_bone(bone, bone_name):
    context = bpy.context
    #TODO: Clean this
    if bone:
        if context.scene.BNR_replaceDuplicate:
            duplicate_bone = None
            for b in context.object.data.bones:
                if b.name == bone_name:
                    duplicate_bone = b
                    break
            if duplicate_bone:
                duplicate_bone.name = bone_name + ".replaced"
                bone.name = bone_name
            else:
                bone.name = bone_name
        else:
            bone.name = bone_name
    else:
        print("BNR::__init__::rename_bone: Could not rename bone, must've been None Type")

def get_selected_bone(index=0):
    #TODO: Fix this hack
    ##  Bone should be returned depending on object.mode instead of 
    context = bpy.context
    arm = context.object.data
    selected_edit_bones = context.selected_bones    
    if selected_edit_bones is not None:
        if index >= len(selected_edit_bones):
            return None
        return selected_edit_bones[index]

    selected_pose_bones = context.selected_pose_bones
    if selected_pose_bones is not None:
        if index >= len(selected_pose_bones):
            return None
        return arm.bones[selected_pose_bones[index].name]

    return None

def get_next_bone():
    current_bone = get_selected_bone()
    next_bone = current_bone.children
    if next_bone:
        return next_bone[0]
    return None

##TODO: FIX THIS
class BNR_AddBoneName(bpy.types.Operator):
    """Add a name to the bone list below"""
    bl_idname = "bone_rename.addname"
    bl_label = "Add Bone Name"
    
    def execute(self, context):
        print("self.user_inputted_value:", context.scene.BNR_addBoneString)
        bpy.types.Scene.BNR_bone_list.append(context.scene.BNR_addBoneString)
        return {"FINISHED"}

class BNR_ClearList(bpy.types.Operator):
    """Clears the bone list"""
    bl_idname = "bone_rename.clearlist"
    bl_label = "Clear List"
    bl_icon = "ERROR"
    bl_options = {"UNDO"}

    def execute(self, context):
        context.scene.BNR_bone_list.clear()
        context.scene.BNR_bone_order.clear()
        return {"FINISHED"}

class BNR_Connect(bpy.types.Operator):
    """Moves tail end of parent bone to a child bone's head"""
    bl_idname = "bnr.connect"
    bl_label = "Connect"
    bl_icon = "CONSTRAINT_BONE"
    bl_options = {"UNDO"}

    @classmethod
    def poll(self, context):
        first_bone = get_selected_bone()
        if first_bone == None:
            return False
        elif len(first_bone.children) > 0:
            if first_bone.children[0].use_connect == False:
                return True

        second_bone = get_selected_bone(1)
        if second_bone == None:
            return False

        if second_bone.parent != first_bone:
            return False

        if second_bone.use_connect:
            return False
        return True

    def execute(self, context):
        #TODO: Add pie chain selecting
        #   NOTE: Set object to edit mode or else edit_bones list aren't built?
        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode="EDIT")
        #Get bones
        bone = context.object.data.edit_bones[get_selected_bone().name]
        #Test if second bone is selected or not and make adjustments
        child_bone = get_selected_bone(1)
        if child_bone == None:
            child_bone = bone.children[0]
        else:
            #Get edit_bone
            child_bone = context.object.data.edit_bones[child_bone.name]
        #Move bone tail to child bone head
        bone.tail = child_bone.head
        child_bone.use_connect = True
        #Recalculate bone roll
        if context.scene.BNR_recalculateRoll:
            #Get axis direction to recalculate
            direction = ""
            #X+
            if bone.head[0] < child_bone.head[0]:
                direction = "GLOBAL_POS_X"
            #X-
            if bone.head[0] < child_bone.head[0]:
                direction = "GLOBAL_NEG_X"
            #Execute recalculate
            bpy.ops.armature.calculate_roll(type=direction)
        #Select next bone in chain if option set to true
        if context.scene.BNR_followChainBool:
            bone.select = False
            child_bone.select = True
        #Change mode back
        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}

######### PIE CHILD SELECTOR ###########
class BNR_PieChainMenu(bpy.types.Operator):

    bl_idname = "bnr.pie_chain_menu"
    bl_label = "Add Quick Node"
    
    bone_name = bpy.props.StringProperty()
    @classmethod
    def poll(cls, context):
        if get_selected_bone():
            return True
        return False
        
    def execute(self, context):
        #TODO: Optimize this, and getting current bone
        context.object.data.bones[get_selected_bone().name].select = False
        context.object.data.bones[self.bone_name].select = True
        return {'FINISHED'}
    
class BNR_piechain_template(bpy.types.Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Select Bone"
    
    @classmethod
    def poll(cls, context):
        if get_selected_bone():
            return True
        return False
    
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()        
        bones = get_selected_bone().children
        for b in bones:
            pie.operator("bnr.pie_chain_menu", b.name).bone_name = b.name
########################################

class BNR_RenameBone(bpy.types.Operator):
    """Rename bone to current button's name"""
    bl_idname = "bone_rename.renamebone"
    bl_label = "Rename Bone"
    bl_options = {"UNDO"}
    
    bone_name = bpy.props.StringProperty(name="Bone")
    
    @classmethod
    def poll(self, context):
        if get_selected_bone() == None:
            return False
        if context.object.mode == "EDIT":
            if len(context.selected_bones) > 1:
                return False
        if context.object.mode == "POSE":
            if len(context.selected_pose_bones) > 1:
                return False
        return True

    def execute(self, context):
        #Save mode and switch to edit mode
        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode="EDIT")
        
        rename_bone(get_selected_bone(), self.bone_name)

        #Goto next bone
        next_bone = get_next_bone()
        if next_bone and context.scene.BNR_followChainBool == True:
            get_selected_bone().select = False
            next_bone.select = True
        
        bpy.ops.object.mode_set(mode=current_mode)
        return {"FINISHED"}

class BNR_RenameBoneConfirmOperator(bpy.types.Operator):
    """TEST QUOTES"""
    bl_idname = "bnr.rename_panel"
    bl_label = "Rename Bone"
    bl_options = {"UNDO"}
    
    type = StringProperty(default="", options={'SKIP_SAVE'})
    #bpy.types.Scene.BNR_addBoneString = bpy.props.StringProperty(default="Bone")
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        rename_bone(get_selected_bone(), self.type)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        bone = get_selected_bone()
        if bone:
            self.bone_name = bone.name
            return context.window_manager.invoke_props_dialog(self, width=400)
        
    def draw(self, context):
        self.layout.prop(self, "type", text="")
#TODO: Add bone selecting pie menu if pie option is enabled
class BNR_RenameChain(bpy.types.Operator):
    """Rename a chain of bones up to when the chain forks based on bone list structure"""
    bl_idname = "bnr.rename_chain"
    bl_label = "Rename Chain"
    bl_options = {"UNDO"}
    
    @classmethod
    def poll(self, context):
        #Check if first and second bone are selected, if second is not, then check if first bone has children
        first_bone = get_selected_bone()
        if first_bone == None:
            return False
        second_bone = get_selected_bone(1)
        if second_bone == None:
            if len(first_bone.children) < 1:
                return False
        #Length of selected bones
        if context.object.mode == "EDIT":
            if len(context.selected_bones) > 2:
                return False
        if context.object.mode == "POSE":
            if len(context.selected_pose_bones) > 2:
                return False

        return True
        
    ##TODO: Add "replace old" check and replace old if true
    def execute(self, context):
        #Store current object mode
        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode="EDIT")
        
        bones = context.selected_bones
        if bones:
            #TODO: Rename chain FROM TO selected bones
            if len(bones) == 2:
                index = -1
                cur_bone = bones[0]
                #Find index of bone name to start at
                for count in range(0, len(context.scene.BNR_bone_order)):
                    bone_list_name = context.scene.BNR_bone_order[count]
                    if cur_bone.name == bone_list_name:
                        index = count
                        break
                if index < 0:
                    bpy.ops.object.mode_set(mode=current_mode)
                    return {"CANCELLED"}
                #Get count of bone chain from second bone parent > parent > etc.
                tmp_bone = bones[1]
                rename_list = []
                found = False
                while found == False and len(rename_list) < 1024 and tmp_bone.parent != None:
                    rename_list.append(tmp_bone)
                    tmp_bone = tmp_bone.parent
                    if cur_bone.name == tmp_bone.name:
                        found = True

                if found == False:
                    #TODO: Add exception here for user
                    print("Selected bone 2 is not in a child chain of selected bone 1")
                    bpy.ops.object.mode_set(mode=current_mode)
                    return {"CANCELLED"}
                count = 1
                rename_list.reverse()
                for b in rename_list:
                    rename_bone(b, context.scene.BNR_bone_order[index + count])
                    count +=1
            #Rename bone chain from to first child split/not found
            elif len(bones) == 1:
                index = -1
                cur_bone = bones[0]
                #Find index of bone name to start at
                for count in range(0, len(context.scene.BNR_bone_order)):
                    bone_list_name = context.scene.BNR_bone_order[count]
                    if cur_bone.name == bone_list_name:
                        index = count
                        break
                if index > -1:
                    count = 1
                    #Check for no children, or if children branch out
                    if len(cur_bone.children) == 1:
                        bones = cur_bone
                        #Same as above, but looping until that condition is met / goes above length of bone list names
                        while len(bones.children) == 1 and index + count < len(context.scene.BNR_bone_order):
                            #Select next bone in chain
                            bones = bones.children[0]
                            bones.select = False
                            #Rename bone
                            rename_bone(bones, context.scene.BNR_bone_order[index + count])
                            count += 1
                        #Select last bone and de-select first in chain
                        if context.scene.BNR_followChainBool:
                            cur_bone.select = False
                            bones.select = True
                
                
        bpy.ops.object.mode_set(mode=current_mode)
        return {"FINISHED"}

###############DRAWING NAMES#################
def draw_text_3d(font_id, color, pos, width, height, msg):

    blf.position(font_id, pos[0] + 10, pos[1], 0)
    blf.size(font_id, width, height)

    bgl.glEnable(bgl.GL_BLEND)
        
    bgl.glColor4f(color[0], color[1], color[2], color[3])
    blf.draw(font_id, msg)    
        
    #Set gl back to defaults
    
    bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
    
    bgl.glEnd()
    
def draw_text_outline_3d(font_id, color, outline_color, pos, width, height, msg):
    #Outline
    draw_text_3d(font_id, outline_color, [pos[0]-1, pos[1]-1], width, height, msg)
    draw_text_3d(font_id, outline_color, [pos[0]-1, pos[1]+1], width, height, msg)
    draw_text_3d(font_id, outline_color, [pos[0]+1, pos[1]+1], width, height, msg)
    draw_text_3d(font_id, outline_color, [pos[0]+1, pos[1]-1], width, height, msg)
    #Fill
    draw_text_3d(font_id, color, pos, width, height, msg)
    
#Draw bone names
def bnr_draw_names_callback():
    if bpy.context.object == None:
        return
    #Get bone
    bone = get_selected_bone()
    
    ###Variable setup
    font_id = 0
    #Name colors for each type of bone
    selected_color = (1.0, 1.0, 1.0, 1.0)
    selected_outline_color = (0.0, 0.0, 0.0, 1.0)
    unselected_color = (0.0, 0.0, 0.0, 1.0)
    parent_color = (1.0, 0.75, 0.75, 1.0)
    child_color = (0.75, 1.0, 0.75, 1.0)
    ##outline_color = (1.0, 1.0, 1.0, 1.0)
    not_in_list_color = (0.25, 0.0, 0.0, 1.0)
    #Size, 28
    width = 28
    height = 28

    #Draw just black names if no bone is selected
    #TODO: make red appear for unmatched bones
    if bone is None:
        for b in bpy.context.object.data.bones:
                #Add the location of the armature's position with the head's position relative to armature
                #Then add local bone center position
                pos = 0
                #Fix edit mode moving bone text
                if bpy.context.object.mode == "EDIT":
                    tmp = bpy.context.object.data.edit_bones[b.name]
                    pos = bpy.context.object.location + tmp.head + ((tmp.tail - tmp.head) / 2)
                elif bpy.context.object.mode == "POSE":
                    tmp = bpy.context.object.pose.bones[b.name]
                    pos = bpy.context.object.location + tmp.head + ((tmp.tail - tmp.head) / 2)
                else:
                    pos = bpy.context.object.location + b.head_local + ((b.tail_local - b.head_local) / 2)
                ##Translate 3d position to 2d position on viewport
                pos = view3d_utils.location_3d_to_region_2d(
                        bpy.context.region, 
                        bpy.context.space_data.region_3d, 
                        pos, 
                        [-10, -500]
                )
                draw_text_3d(font_id,
                             unselected_color,
                             pos,
                             width,
                             height,
                             b.name
                )
        return
    
    #Get child bone names
    child_names = []
    for child in bone.children:
        child_names.append(child.name)
        
    parent_name = None
    if bone.parent:
        parent_name = bone.parent.name

    for b in bpy.context.object.data.bones:
        #Add the location of the armature's position with the head's position relative to armature
        #Then add local bone center position
        pos = 0
        #Fix edit mode moving bone text
        if bpy.context.object.mode == "EDIT":
            tmp = bpy.context.object.data.edit_bones[b.name]
            pos = bpy.context.object.location + tmp.head + ((tmp.tail - tmp.head) / 2)
        elif bpy.context.object.mode == "POSE":
            tmp = bpy.context.object.pose.bones[b.name]
            pos = bpy.context.object.location + tmp.head + ((tmp.tail - tmp.head) / 2)
        else:
            pos = bpy.context.object.location + b.head_local + ((b.tail_local - b.head_local) / 2)

        
        ##Translate 3d position to 2d position on viewport
        pos = view3d_utils.location_3d_to_region_2d(
                bpy.context.region, 
                bpy.context.space_data.region_3d, 
                pos, 
                [-10, -500]
        )    

        ##Draw text                
        if b.name == bone.name:
            #fill
            draw_text_outline_3d(font_id, 
                                 selected_color, 
                                 selected_outline_color, 
                                 pos, 
                                 width, 
                                 height, 
                                 b.name
            )
                    
        elif b.name in child_names:
            #Child
            draw_text_outline_3d(font_id,
                                     child_color,
                                     selected_outline_color,
                                     pos,
                                     width,
                                     height,
                                     b.name
                )
        elif parent_name == b.name:
            #Parent
            draw_text_outline_3d(font_id,
                                 parent_color,
                                 selected_outline_color,
                                 pos,
                                 width,
                                 height,
                                 b.name
            )
        elif len(bpy.context.scene.BNR_bone_order) > 0 and b.name not in bpy.context.scene.BNR_bone_order:
            #Not in list
            draw_text_3d(font_id,
                                 not_in_list_color,
                                 pos,
                                 width,
                                 height,
                                 b.name
            )
        else:
            #Unselected
            draw_text_3d(font_id,
                                 unselected_color,
                                 pos,
                                 width,
                                 height,
                                 b.name
            )

bpy.types.Scene.bnr_widgets = {}

##Non-Registered class
class BNR_DrawNames:
    def __init__(self):
        self.handle_3d_names = bpy.types.SpaceView3D.draw_handler_add(bnr_draw_names_callback, (), 'WINDOW', 'POST_PIXEL')
    
    def cleanup(self):
        if self.handle_3d_names:
            bpy.types.SpaceView3D.draw_handler_remove(self.handle_3d_names, 'WINDOW')

#Function to call when toggling "Draw Names" checkbox
def bnr_draw_names(self, context):
    b = bpy.context.scene.BNR_drawNames
    if b:
        bpy.types.Scene.bnr_widgets["draw_names"] = BNR_DrawNames()
    else:
        if bpy.types.Scene.bnr_widgets["draw_names"]:
            bpy.types.Scene.bnr_widgets["draw_names"].cleanup()
            del bpy.types.Scene.bnr_widgets["draw_names"]

###############END Drawing Names###############

#"Bone Name Rangler" panel class, the gui
class BonePanel(bpy.types.Panel):
    bl_idname      = "DATA_PT_bone_rangler"
    bl_label       = "Bone Name Rangler"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context     = "data"
    bpy.types.Scene.BNR_addBoneString    = StringProperty(default="Bone")
    bpy.types.Scene.BNR_followChainBool  = BoolProperty(default=True)
    bpy.types.Scene.BNR_hideMatching     = BoolProperty(default=True)
    bpy.types.Scene.BNR_replaceDuplicate = BoolProperty(default=False)
    bpy.types.Scene.BNR_drawNames        = BoolProperty(default=False, update=bnr_draw_names)
    bpy.types.Scene.BNR_recalculateRoll  = BoolProperty(default=True)
    bpy.types.Scene.BNR_bone_list = {}
    bpy.types.Scene.BNR_bone_order = []
    
    #TODO: Clean up names used for layout here
    def draw(self, context):
        if context.object == None:
            return
        if context.object.mode in { 'POSE', 'EDIT' }:
            layout = self.layout
            bone = get_selected_bone()

            #region     #/ TEMP /#
            layout.operator("wm.call_menu_pie", "BNR_piechain_template").name = "BNR_piechain_template"
            #endregion  #/ TEMP /#
            #region     #/ Bone List Manipulation /#
            if bone is not None:
                layout.prop(bone, "name", "", icon="BONE_DATA")
            else:
                layout.label("No bone selected")            

            ##TODO:// Fix adding bones
            """
            add_name_row = layout.row()
            add_name_row.prop(context.scene, "BNR_addBoneString", "")
            add_name_row.alignment = "RIGHT"
            add_name_row.operator("bone_rename.addname", "Add Name")
            """
            t = layout.row(align=True)
            t.prop_menu_enum(context.scene, 'bnr_xml_list_enum', text=context.scene.bnr_xml_list_enum)
            t.operator("bnr.import_list", icon="FILE", text="")
            #endregion  #/ Bone List Manipulation /#
            #region     #/ Armature Options /#
            option_col = layout.column(align=True)
            t = option_col.row()
            t.alignment = "CENTER"
            t.label("Armature Options")
            option_armature_col = option_col.column()
            #LAYERS
            t = option_armature_col.column()
            t.prop(context.object.data, "layers", "")
            
            option_armature_row = option_armature_col.row()
            #LEFT
            t = option_armature_row.column()
            t.prop(context.scene, "BNR_drawNames", "Draw Names")
            #RIGHT
            t = option_armature_row.column()
            t.prop(context.object, "show_x_ray")            
            #endregion  #/ Armature Options /#
            #region     #/ BNR Options #/
            t = option_col.row()
            t.alignment = "CENTER"
            t.label("Bone Name Replacement Options")
            
            option_row = option_col.row()
            t = option_row.column()
            t.prop(context.scene, "BNR_followChainBool", "Follow Chain")
            t.prop(context.scene, "BNR_replaceDuplicate", "Replace Old")
            
            t = option_row.column()
            t.prop(context.scene, "BNR_hideMatching", "Hide Matching")
            
            bl_col = layout.column()
            bl_inner_col = bl_col.column()
            #endregion  #/ BNR Options #/
            #region     #/ Connect Stuff /#
            
            option_col.operator("bnr.connect", "Connect (Tail > Head)")
            ##
            connect_row = option_col.row()
            t = connect_row.column()
            t.prop(context.scene, "BNR_recalculateRoll", "Calculate Roll")
            #endregion  #/ Connect Stuff /#
            #region     #/ Bone List /#
            if len(bpy.types.Scene.BNR_bone_order) > 0:
                
                t = option_col.row()
                t.operator("bnr.rename_chain")
                
                qbl_row = bl_inner_col.row()
                qbl_row.label("Quick Bone List:")
                qbl_row.alignment = "RIGHT"
                qbl_row.operator("bone_rename.clearlist", "Clear List", icon="X")
                qbl_row.alignment = "EXPAND"

                
                ####Begin drawing defined bone list buttons
                #Build armature bone name list
                a_bone_list = []
                if context.scene.BNR_hideMatching == True:
                    armature_bones = context.object.data.bones
                    for b in armature_bones:
                        a_bone_list.append(b.name)
                    
                hidden_count = 0
                bone_count = 0
                
                child_names = []
                parent_name = None
                #Check if bone even selected to get children/parent
                if bone:
                    for child in bone.children:
                        child_names.append(child.name)    
                    if bone.parent:
                        parent_name = bone.parent.name
                
                ##Iterate over BNR list and do shit to figure out what to add to list in that moment
                for b in bpy.types.Scene.BNR_bone_order:
                    bl_row = bl_col.row()
                    if context.scene.BNR_hideMatching == True:
                        if b not in a_bone_list:
                            bl_row.operator("bone_rename.renamebone", b).bone_name = b
                        else:
                            hidden_count += 1
                    elif bone is None:
                        bl_row.operator("bone_rename.renamebone", b).bone_name = b
                    else:
                        if bone.name == b:
                            bl_row.operator("bone_rename.renamebone", b, icon="BONE_DATA").bone_name = b
                        elif parent_name == b:
                            bl_row.operator("bone_rename.renamebone", b, icon="KEYTYPE_EXTREME_VEC").bone_name = b
                        elif b in child_names:
                            bl_row.operator("bone_rename.renamebone", b, icon="KEYTYPE_JITTER_VEC").bone_name = b                            
                        else:
                            bl_row.operator("bone_rename.renamebone", b).bone_name = b
                    
                    

                    bone_count += 1
                if context.scene.BNR_hideMatching == True:
                    bl_inner_col.label("({0}/{1} Hidden due to matching)".format(hidden_count, bone_count))
            #endregion  #/ Bone List /#

bnr_class_list = [
    BNR_RenameChain,
    BNR_ClearList,
    BNR_Connect,
    BoneRenameImportList,
    BNR_RenameBone,
    BNR_RenameBoneConfirmOperator,
    BNR_AddBoneName,
    BNR_PieChainMenu,
    BNR_piechain_template,
    BonePanel
]

addon_keymaps = []

def register():
    print("Registering BNR")
    
    if not os.path.exists(xml_preset_path):
        os.mkdir(xml_preset_path)
    files = os.listdir(xml_preset_path)
    bpy.types.Scene.bnr_xml_list = files
    print(bpy.types.Scene.bnr_xml_list)
    rebuild_xml_presets()
    ##Check for keymaps
    """
    wm = bpy.context.window_manager  
    km = wm.keyconfigs.addon.keymaps.new(name='Bone Name Rangler', space_type='EMPTY')
    
    kmi = km.keymap_items.new(BNR_RenameBoneConfirmOperator.bl_idname,
                              value='PRESS',
                              type='E',
                              ctrl=True,
                              alt=False,
                              shift=False,
                              oskey=False
    )
    addon_keymaps.append((km, kmi))
    """
    #bpy.data.window_managers[0].keyconfigs.active.keymaps['Pose'].keymap_items.new('bnr.rename_panel',value='PRESS',type='E',ctrl=True,alt=False,shift=False,oskey=False)     
    for c in bnr_class_list:
        bpy.utils.register_class(c)
            
def unregister():
    for widget in bpy.types.Scene.bnr_widgets:
        w = bpy.types.Scene.bnr_widgets[widget]
        print(w)
        if w:
            w.cleanup()
        
    for c in bnr_class_list:
        bpy.utils.unregister_class(c)
        
    #Clear keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.bnr_xml_list_enum
        
if __name__ == "__main__":
    register()   