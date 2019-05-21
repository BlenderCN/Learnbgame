bl_info = {
    "name": "Node Manager",
    "author": "Jonas Olesen",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Object Mode > Toolbar",
    "description": "Some operations to manage Shader Nodes",
    "category": "Learnbgame",
    }

import bpy
from bpy.props import *

#########################################  END PRE STUFF #####################################################

def delUnused(context,amount=0):

    matname = bpy.context.active_object.active_material.name
    tree = bpy.data.materials[matname].node_tree
    
    newamount = 0
    for node in tree.nodes:
        unused = True
        if len(node.outputs) == 0 :
            unused = False
        elif node.mute == True:
            unused = False
        else:
            for output in node.outputs:
                if len(output.links) >= 1:
                    unused = False
                    break
        if(unused):
            tree.nodes.remove(node)
            newamount += 1
        
    if newamount == 0:
        bpy.context.window_manager.popup_menu(deleteUnused.drawFin, title = str(amount) + " Nodes have been deleted!", icon='FILE_TICK')
        #Finished
    else:
        delUnused(context,amount+newamount)
        #New run


class deleteUnused(bpy.types.Operator):
    """Delete Unused Nodes"""
    bl_idname = "myops.add_deleteunusedid"
    bl_label = "Delete Unused"

    def execute(self,context):
        delUnused(context)
        return {'FINISHED'}
        

    def drawFin(self,context):
        self.layout.label(text = "Succesful run!")


##############################     END FUNCTIONALITY CLASS 1    #################################################################

def removeFromFlow(context, node):

    matname = bpy.context.active_object.active_material.name
    tree = bpy.data.materials[matname].node_tree
    
    InputtingRGBASockets = []
    OutputEndRGBASockets = []
    
    InputtingVALUESockets = []
    OutputEndVALUESockets = []
    
    InputtingVECTORSockets = []
    OutputEndVECTORSockets = []
    
    InputtingSHADERSockets = []
    OutputEndSHADERSockets = []
    
    for input in node.inputs:
        tempArr = []
        for link in input.links:
            tempArr.append(link.from_socket)
        if len(tempArr) > 0:
            if input.type == "RGBA":
                InputtingRGBASockets.append(tempArr[0])
            if input.type == "VALUE":
                InputtingVALUESockets.append(tempArr[0])
            if input.type == "VECTOR":
                InputtingVECTORSockets.append(tempArr[0])
            if input.type == "SHADER":
                InputtingSHADERSockets.append(tempArr[0])
            
    for output in node.outputs:
        tempArr = []
        for link in output.links:
            tempArr.append(link.to_socket)
        if len(tempArr) > 0:
            if output.type == "RGBA":
                OutputEndRGBASockets.append(tempArr)
            if output.type == "VALUE":
                OutputEndVALUESockets.append(tempArr)
            if output.type == "VECTOR":
                OutputEndVECTORSockets.append(tempArr)
            if output.type == "SHADER":
                OutputEndSHADERSockets.append(tempArr)
            
    #can only try to reconstruct as many outputs as inputs without randomly filling slots
    makeSameLength(InputtingRGBASockets,OutputEndRGBASockets)
    makeSameLength(InputtingVALUESockets,OutputEndVALUESockets)
    makeSameLength(InputtingVECTORSockets,OutputEndVECTORSockets)
    makeSameLength(InputtingSHADERSockets,OutputEndSHADERSockets)
    
    #Make Links
    if len(InputtingRGBASockets) > 0:
        for i in range(len(InputtingRGBASockets)):
            inp = InputtingRGBASockets[i]
            for socket in OutputEndRGBASockets[i]:
                tree.links.new(inp,socket)
                
    #Make Links
    if len(InputtingVALUESockets) > 0:
        for i in range(len(InputtingVALUESockets)):
            inp = InputtingVALUESockets[i]
            for socket in OutputEndVALUESockets[i]:
                tree.links.new(inp,socket)
                
    #Make Links
    if len(InputtingVECTORSockets) > 0:
        for i in range(len(InputtingVECTORSockets)):
            inp = InputtingVECTORSockets[i]
            for socket in OutputEndVECTORSockets[i]:
                tree.links.new(inp,socket)
                
    #Make Links
    if len(InputtingSHADERSockets) > 0:
        for i in range(len(InputtingSHADERSockets)):
            inp = InputtingSHADERSockets[i]
            for socket in OutputEndSHADERSockets[i]:
                tree.links.new(inp,socket)
            
    tree.nodes.remove(node)
            

def makeSameLength(a,b):
    while len(a) > len(b):
        del a[-1]
    while len(b) > len(a):
        del b[-1]

class FlowRemove(bpy.types.Operator):
    """Remove selected Nodes from Flow"""
    bl_idname = "myops.add_remfromflow"
    bl_label = "Remove from Flow"

    def execute(self,context):
        matname = bpy.context.active_object.active_material.name
        tree = bpy.data.materials[matname].node_tree
        nodes = [ n for n in tree.nodes if n.select ]
        for node in nodes:
            removeFromFlow(context, node)
        return {'FINISHED'}

##############################     END FUNCTIONALITY CLASS 2    #################################################################



class NodeManagerPanel(bpy.types.Panel):
    #creating Panel
    bl_label = "Node Manager"
    bl_idname = "NODEEDITOR_PT_NodeMan"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Node Manager"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        row = layout.row()
        row.operator("myops.add_deleteunusedid")
        row = layout.row()
        row.operator("myops.add_remfromflow")


###########################################    END UI-PANEL CLASS   ########################################################


classes = (
    deleteUnused,
    NodeManagerPanel,
    FlowRemove,
)


def register():

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():

    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)


if __name__ == '__main__':
    register()
