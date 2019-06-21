

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
    "name": "Oscurart Action Offset",
    "author": "Oscurart",
    "version": (1,1),
    "blender": (2, 6, 7),
    "api": 48000,
    "location": "Tools > Action Offset",
    "description": "Oscurart Offset Action",
    "warning": "",
    "wiki_url": "oscurart.blogspot.com",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy

bpy.types.Scene.nla_offset_action = bpy.props.StringProperty(default="Empty")

#------------------------------- PANEL

class OscPanelNlaOffset(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Action Offset"

    def draw(self, context):
        active_obj = context.active_object
        layout = self.layout
        col = layout.column(align=1)
        col.operator("nla.create_offset_cp", icon="LINENUMBERS_ON", text="Set Order")  
        col.operator("nla.create_action_cp", icon="POSE_DATA", text="Set Action Object!") 
        col.label(text="Active Action: %s" % (bpy.context.scene.nla_offset_action))
            
        col = layout.column(align=0)   
        row = col.row(align=0)
        row.operator("nla.strip_offset", icon="NLA")
        row.operator("constraint.offset_action_cns", icon="CONSTRAINT")   
           

# -------------------- APPLY OFFSET

def funcOffsetNla(context, OFFSET, CONT, CONTROOT):
    
    TIMEOFF = 0    
    ACTIVEOBJECT = bpy.context.active_object
    ACTIVEACTION = bpy.context.object.animation_data.action    
    SELOSC = eval(bpy.context.scene["NLA_OFFSET_CP"])
    SELOSC.pop(-1)        

    if CONTROOT:       
            NULLROOT = bpy.data.objects.new("%s_Root" % (ACTIVEOBJECT.name) , None)
            bpy.context.scene.objects.link(NULLROOT)
            NULLROOT.location = (0,0,0)
    
    for OBJ in SELOSC:  
        OBJ.animation_data_clear() 
                
        if CONT:
            NULL = bpy.data.objects.new("%s_Container" % (ACTIVEOBJECT.name) , None)
            bpy.context.scene.objects.link(NULL)
            NULL.location = OBJ.location
            NULL.rotation_euler = OBJ.rotation_euler
                           
        OBJ.animation_data_create()         
        TRK = OBJ.animation_data.nla_tracks.new()
        OBJ.animation_data.action = None
        
        if CONTROOT:
            if CONT:
                OBJ.parent = NULL
                NULL.parent = NULLROOT  
            else:
                OBJ.parent = NULLROOT  
        else:
            if CONT:
                OBJ.parent = NULL
                OBJ.location = (0,0,0)
                OBJ.rotation_euler = (0,0,0)  
                OBJ.scale = (0,0,0)      
        
        ST = TRK.strips.new(OBJ.name, start=TIMEOFF, action=bpy.data.actions[bpy.context.scene.nla_offset_action])          
             
        TIMEOFF+=OFFSET

class OperatorOffsetNla(bpy.types.Operator):
    bl_idname = "nla.strip_offset"
    bl_label = "Nla"
    bl_options = {"REGISTER", "UNDO"}

    offset = bpy.props.FloatProperty(default=1, name="Strip Offset")    

    cont = bpy.props.BoolProperty(default=False, name="Offset Container")
  
    controot = bpy.props.BoolProperty(default=False, name="Root Container")
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        funcOffsetNla(context, self.offset, self.cont, self.controot)
        return {'FINISHED'}

## --------------- ACTION CONSTRAINT   
def funcOffsetAction(context, OFFSET,  MN, MX, ST, EN, INC):

    ACTIVEOBJECT = bpy.context.active_object
    ACTIVEACTION = bpy.context.object.animation_data.action
    SELOSC = eval(bpy.context.scene["NLA_OFFSET_CP"])

    for OBJ in SELOSC:  
        OBJ.animation_data_clear() 
                           
        OBJ.animation_data_create()         
        TRK = OBJ.animation_data.nla_tracks.new()
        OBJ.animation_data.action = None

    CNSDRIVER = bpy.data.objects.new("%s_Action_Driver" % (ACTIVEOBJECT.name) , None)
    bpy.context.scene.objects.link(CNSDRIVER)  
    CNSDRIVER.location = (0,0,0)                   
                
    FADE = (MX-MN)/INC 
    for STEP,OBJ in enumerate(SELOSC):
        if len(OBJ.constraints) > 0:
            OBJ.constraints.remove(OBJ.constraints[-1])
        CNS = OBJ.constraints.new("ACTION")
        CNS.target = CNSDRIVER
        CNS.action = bpy.data.actions[bpy.context.scene.nla_offset_action]
        CNS.frame_start = ST
        CNS.frame_end = EN
        CNS.min = MN-(FADE*STEP+1)+OFFSET
        CNS.max = MX-(FADE*STEP+1)+OFFSET
        MN,MX = (MX,MX+(MX-MN))


class OperatorOffsetAction(bpy.types.Operator):
    bl_idname = "constraint.offset_action_cns"
    bl_label = "Action Cns"
    bl_options = {"REGISTER", "UNDO"}

    min = bpy.props.FloatProperty(default=0, name="Min")  
    max = bpy.props.FloatProperty(default=1, name="Max")  
    start = bpy.props.IntProperty(default=1, name="Start")  
    end = bpy.props.IntProperty(default=10, name="End")  
    offset = bpy.props.FloatProperty(default=0, name="Cns Offset")  
    inc  = bpy.props.FloatProperty(default=1, min=.01, name="Fade")   

    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        funcOffsetAction(context, self.offset, self.min, self.max, self.start, self.end, self.inc)
        return {'FINISHED'}


    
#----------------------------- SET CP

class OperatorOffsetNlaCreate(bpy.types.Operator):
    bl_idname = "nla.create_offset_cp"
    bl_label = "Set Order"
    bl_options = {"REGISTER", "UNDO"}

 
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.context.scene["NLA_OFFSET_CP"] = str(bpy.selection_osc[:])
        return {'FINISHED'}
    
#----------------------------- SET ACTION

class OperatorOffsetNlaCreate(bpy.types.Operator):
    bl_idname = "nla.create_action_cp"
    bl_label = "Set Action Nla Offset"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.context.scene.nla_offset_action = str(bpy.context.object.animation_data.action.name)
        return {'FINISHED'}    

def register():
    bpy.utils.register_module(__name__)
def unregister():
    bpy.utils.unregister_module(__name__)



if __name__ == "__main__":
    register()