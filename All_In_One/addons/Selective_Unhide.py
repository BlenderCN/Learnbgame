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

import bpy


bl_info = {
    "name": "Selective Unhide",
    "description": "Selectively unhide objects instead of unhiding all objects at once",
    "author": "Ray Mairlot",
    "version": (1, 3),
    "blender": (2, 76, 0),
    "location": "3D View> Alt + H",
    "category": "Learnbgame",
}



def getHiddenMeshElements(type=""):
    
    object = bpy.context.active_object                
        
    object.update_from_editmode()
    
    hiddenVertices = [vertex for vertex in object.data.vertices if vertex.hide]

    if type == "":

        hiddenEdges = [edge for edge in object.data.edges if edge.hide]

        hiddenFaces = [face for face in object.data.polygons if face.hide]
        
        return hiddenVertices + hiddenEdges + hiddenFaces
    
    elif type == "vertices":
        
        return hiddenVertices



def getHiddenVertexGroups():
            
    object = bpy.context.active_object                
                
    hiddenVertexGroups = []
                    
    for hiddenVertex in getHiddenMeshElements("vertices"):
        
        for vertexGroup in hiddenVertex.groups:
            
            if object.vertex_groups[vertexGroup.group] not in hiddenVertexGroups:
                
                hiddenVertexGroups.append(object.vertex_groups[vertexGroup.group])
                    
    return hiddenVertexGroups



def getHiddenBones(boneType):
    
    if boneType == "EDIT_ARMATURE":
        
        boneList = bpy.context.active_object.data.edit_bones
        
    elif boneType == "POSE":
        
        boneList = bpy.context.active_object.data.bones
    
    return [bone for bone in boneList if bone.hide] 



def getHiddenBoneGroups(boneType):
        
    hiddenBoneGroups = []
    
    armature = bpy.context.active_object
    
    for boneGroup in armature.pose.bone_groups:
        
        for hiddenBone in getHiddenBones(boneType):
            
            if armature.pose.bones[hiddenBone.name].bone_group == boneGroup and boneGroup not in hiddenBoneGroups:
                
                hiddenBoneGroups.append(boneGroup)        
    
    return hiddenBoneGroups            



def getHiddenObjects():
    
    return [object for object in bpy.context.scene.objects if object.hide]



def getHiddenGroups():
    
    #Possible, but not very readable
    #hiddenGroups = [group.name for hiddenObject in hiddenObjects if hiddenObject.name in group.objects and group.name not in hiddenGroups]
    
    hiddenObjects = getHiddenObjects()
    
    hiddenGroups = []
                    
    for group in bpy.data.groups:
        
        for hiddenObject in hiddenObjects:

            if hiddenObject.name in group.objects and group not in hiddenGroups:
                
                hiddenGroups.append(group)
                
    return hiddenGroups
    


def getHiddenItems(scene, context):
    
    if bpy.context.mode == "OBJECT":
        
        hiddenGroups = [(item.name, item.name, "Group") for item in getHiddenGroups()]
        
        hiddenObjects = [(item.name, item.name, "Object") for item in getHiddenObjects()]

    elif bpy.context.mode in ["EDIT_ARMATURE", "POSE"]:
                
        hiddenGroups = [(item.name, item.name, bpy.context.mode+" Bone Group") for item in getHiddenBoneGroups(bpy.context.mode)]
        
        hiddenObjects = [(item.name, item.name, bpy.context.mode+" Bone") for item in getHiddenBones(bpy.context.mode)]
        
    elif bpy.context.mode == "EDIT_MESH":
        
        hiddenGroups = [(item.name, item.name, bpy.context.mode+" Group") for item in getHiddenVertexGroups()]
        
        hiddenObjects = []

    return hiddenObjects + hiddenGroups



class UnhideSearch(bpy.types.Operator):
    """Search through a list of hidden items"""
    bl_idname = "object.unhide_search"
    bl_label = "Hidden Items"
    bl_property = "hiddenItems"

    hiddenItems = bpy.props.EnumProperty(name="Hidden Items", description="Holds a list of the hidden items", items=getHiddenItems)

    def execute(self, context):
        
        allHiddenItems = getHiddenItems(context.scene, context)
        
        for item in allHiddenItems:
            
            if item[0] == self.hiddenItems:
                
                itemType = item[2]
                                                  
        if bpy.context.mode == "OBJECT":
                
            bpy.ops.object.show(type=itemType, itemName=self.hiddenItems)
            
        elif bpy.context.mode in ["EDIT_ARMATURE", "POSE", "EDIT_MESH"]:
                        
            bpy.ops.object.show(type=itemType, itemName=self.hiddenItems, object=bpy.context.active_object.name)        
            
        return {'FINISHED'}


    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}



class UnhideObject(bpy.types.Operator):
    """Unhide the item or group of items"""
    bl_idname = "object.show"
    bl_label = "Show a specific item or group"
    bl_options = {"INTERNAL"}

    itemName = bpy.props.StringProperty()
    type = bpy.props.StringProperty()
    unHideAll = bpy.props.BoolProperty(default=False)
    object = bpy.props.StringProperty()

    def execute(self, context):
        
        if self.type == "Object" and not self.unHideAll:
            
            bpy.data.objects[self.itemName].hide = False
            bpy.data.objects[self.itemName].select = True
            bpy.context.scene.objects.active = bpy.data.objects[self.itemName]
        
        elif self.unHideAll:
            
            for object in getHiddenObjects():
                                
                if object.type == self.itemName:
                    
                    object.hide = False
                    object.select = True
                    bpy.context.scene.objects.active = object
            
        elif self.type == "Group":
            
            for object in bpy.data.groups[self.itemName].objects:
                
                if object.hide:
                
                    object.hide = False
                    object.select = True
                    
        elif self.type == "EDIT_ARMATURE Bone":
            
            armature = bpy.data.objects[self.object].data
            armature.edit_bones[self.itemName].hide = False
            armature.edit_bones[self.itemName].select = True
            armature.edit_bones.active = armature.edit_bones[self.itemName]
                 
        elif self.type == "EDIT_ARMATURE Bone Group":
            
            armature = bpy.data.objects[self.object]
                        
            for bone in getHiddenBones("EDIT_ARMATURE"):
            
                if armature.pose.bones[bone.name].bone_group:
            
                    if armature.pose.bones[bone.name].bone_group.name == self.itemName:
                    
                        bone.hide = False
                        bone.select = True
                    
        elif self.type == "POSE Bone":
            
            armature = bpy.data.objects[self.object].data
            armature.bones[self.itemName].hide = False
            armature.bones[self.itemName].select = True
            armature.bones.active = armature.bones[self.itemName]
            
        elif self.type == "POSE Bone Group":
            
            armature = bpy.data.objects[self.object]
                        
            for bone in getHiddenBones("POSE"):
            
                if armature.pose.bones[bone.name].bone_group:
            
                    if armature.pose.bones[bone.name].bone_group.name == self.itemName:
                    
                        bone.hide = False
                        bone.select = True            
        
        elif self.type == "EDIT_MESH Group":
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
            object = bpy.data.objects[self.object]
                                                        
            for hiddenVertex in getHiddenMeshElements("vertices"):
                
                for vertexGroup in hiddenVertex.groups:
                    
                    if object.vertex_groups[self.itemName].index == vertexGroup.group:
                        
                        hiddenVertex.hide = False
                        
                        break
                                        
            for edge in object.data.edges:
                
                vertex1 = edge.vertices[0]
                vertex2 = edge.vertices[1]
                    
                if not object.data.vertices[vertex1].hide and not object.data.vertices[vertex2].hide:
                    
                    edge.hide = False
                    
            for face in object.data.polygons:
                
                hidden = False
                
                for vertex in face.vertices:
                    
                    if object.data.vertices[vertex].hide:
                        
                         hidden = True
                         
                         break
                     
                if not hidden:
                    
                    face.hide = False
                                    
            bpy.ops.object.mode_set(mode = 'EDIT')
                    
                    
        return {'FINISHED'}



class UnhideAllByTypeMenu(bpy.types.Menu):
    bl_label = "Unhide all by type"
    bl_idname = "view3d.unhide_all_by_type_menu"

    def draw(self, context):
        layout = self.layout

        objectTypes = []
            
        for object in getHiddenObjects():
                            
            if object.type not in objectTypes:
                
                row = layout.row()
                operator = row.operator("object.show", text=object.type.lower().capitalize(), icon="OUTLINER_OB_"+object.type)
                operator.itemName = object.type
                operator.unHideAll = True 
                
                objectTypes.append(object.type)
        
        

class UnhideByTypeMenu(bpy.types.Menu):
    bl_label = "Unhide by type"
    bl_idname = "view3d.unhide_by_type_menu"

    def draw(self, context):
        layout = self.layout
        split = layout.split()
        
        col = split.column()
        
        if bpy.context.mode == "OBJECT":
        
            for hiddenObject in getHiddenObjects():
            
                if hiddenObject.type == context.object.type:
                    row = col.row()                        
                    operator = row.operator("object.show", text=hiddenObject.name)
                    operator.itemName = hiddenObject.name
                    operator.type = "Object"
                    
        elif bpy.context.mode in ["EDIT_ARMATURE", "POSE"]:
                
            for hiddenBone in getHiddenBones(bpy.context.mode):
                
                row = col.row()
                operator = row.operator("object.show", text=hiddenBone.name)
                operator.itemName = hiddenBone.name
                operator.type = bpy.context.mode+" Bone"
                operator.object = bpy.context.active_object.name

                
        
class UnhideMenu(bpy.types.Menu):
    bl_label = "Unhide"
    bl_idname = "view3d.unhide_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        split = layout.split()
                        
        col = split.column()
        
        hiddenVertices = []
        
        if bpy.context.mode == "OBJECT":
                                
            hiddenObjects = getHiddenObjects()
            hiddenGroups = getHiddenGroups()     
            
        elif bpy.context.mode in ["EDIT_ARMATURE", "POSE"]:
            
            hiddenObjects = getHiddenBones(bpy.context.mode)
            hiddenGroups = getHiddenBoneGroups(bpy.context.mode)
            
        elif bpy.context.mode == "EDIT_MESH":
            
            hiddenGroups = getHiddenVertexGroups()
            hiddenObjects = [] #Edit mdoe doesn't have hidden objects
            hiddenVertices = getHiddenMeshElements()
                                                   
                        
        row = col.row()
        if len(hiddenObjects) > 0 or len(hiddenVertices) > 0:

            if bpy.context.mode == "OBJECT":
                
                row.operator("object.hide_view_clear", text="Unhide all objects", icon="RESTRICT_VIEW_OFF")
                row = col.row()
                row.menu(UnhideAllByTypeMenu.bl_idname, text="Unhide all by type", icon="FILTER")
                row = col.row()
                operator = row.operator("object.unhide_search", text="Search", icon="VIEWZOOM")
            
            elif bpy.context.mode == "EDIT_ARMATURE":
                
                row.operator("armature.reveal", text="Unhide all bones", icon="RESTRICT_VIEW_OFF")
                row = col.row()
                operator = row.operator("object.unhide_search", text="Search", icon="VIEWZOOM")    
                
            elif bpy.context.mode == "POSE":
                
                row.operator("pose.reveal", text="Unhide all bones", icon="RESTRICT_VIEW_OFF")
                row = col.row()
                operator = row.operator("object.unhide_search", text="Search", icon="VIEWZOOM")   
                
            elif bpy.context.mode == "EDIT_MESH":
                
                row.operator("mesh.reveal", text="Unhide all", icon="RESTRICT_VIEW_OFF")
                
                if len(hiddenGroups) > 0:
                
                    row = col.row()
                    operator = row.operator("object.unhide_search", text="Search", icon="VIEWZOOM")     
                        
        else:
            
            if bpy.context.mode == "OBJECT":
            
                row.label(text="No hidden objects or groups")
            
            elif bpy.context.mode in ["EDIT_ARMATURE", "POSE"]:
                
                row.label(text="No hidden bones or bone groups")
                
            elif bpy.context.mode == "EDIT_MESH":
                
                row.label(text="No hidden vertices, edges or faces")
                
                            
        if len(hiddenGroups) > 0:

            col.separator()            
            row = col.row()

            #This should change depending on mode, e.g. hidden vertex groups
            row.label(text="Hidden groups:")
            
        else:
            
            if bpy.context.mode == "EDIT_MESH":
                
                if len(hiddenVertices) > 0:
                    
                    col.separator()            
                    row = col.row()
                    row.label(text="No hidden groups")
                    
            elif len(hiddenObjects) > 0:
                
                col.separator()            
                row = col.row()
                row.label(text="No hidden groups")  
            

        for hiddenGroup in hiddenGroups:
                
            row = col.row()
                        
            if bpy.context.mode == "OBJECT":
                
                operator = row.operator("object.show", text=hiddenGroup.name, icon="GROUP")
                operator.itemName = hiddenGroup.name    
                operator.type = "Group"
                
            elif bpy.context.mode in ["EDIT_ARMATURE", "POSE"]:
            
                operator = row.operator("object.show", text=hiddenGroup.name, icon="GROUP_BONE")
                operator.itemName = hiddenGroup.name    
                operator.type = bpy.context.mode+" Bone Group"
                operator.object = bpy.context.active_object.name
                
            elif bpy.context.mode == "EDIT_MESH":
                
                operator = row.operator("object.show", text=hiddenGroup.name, icon="GROUP_VERTEX")
                operator.itemName = hiddenGroup.name    
                operator.type = bpy.context.mode+" Group"
                operator.object = bpy.context.active_object.name
                
              
        if len(hiddenObjects) > 0:
            col.separator()
            row = col.row()
            row.label(text="Hidden objects by type:")
        
            if bpy.context.mode == "OBJECT":

                objectTypes = []
                
                for object in hiddenObjects:
                                    
                    if object.type not in objectTypes:
                                        
                        row = layout.row()
                        row.context_pointer_set("object", object)    
                        row.menu(UnhideByTypeMenu.bl_idname, text=object.type.lower().capitalize(), icon="OUTLINER_OB_"+object.type)      

                        objectTypes.append(object.type)
                        
            elif bpy.context.mode in ["EDIT_ARMATURE", "POSE"]:
                    
                row = layout.row()
                row.menu(UnhideByTypeMenu.bl_idname, text="Bone", icon="BONE_DATA")
                
            

keymaps = []
                  
def register():
        
    bpy.utils.register_module(__name__)    
                
    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'H', 'PRESS', alt=True)
    kmi.properties.name = 'view3d.unhide_menu'
    keymaps.append((km, kmi))
    
    km = wm.keyconfigs.addon.keymaps.new(name='Armature', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'H', 'PRESS', alt=True)
    kmi.properties.name = 'view3d.unhide_menu'
    keymaps.append((km, kmi))
    
    km = wm.keyconfigs.addon.keymaps.new(name='Pose', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'H', 'PRESS', alt=True)
    kmi.properties.name = 'view3d.unhide_menu'
    keymaps.append((km, kmi))
    
    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.call_menu', 'H', 'PRESS', alt=True)
    kmi.properties.name = 'view3d.unhide_menu'
    keymaps.append((km, kmi))    
        


def unregister():
    bpy.utils.unregister_module(__name__)        
        
    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()
    


if __name__ == "__main__":
    register()

             