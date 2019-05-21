import bpy
from bpy.types import Menu, Operator

DEFAULT_ATTRIBUTE_GROUP = None

vertexAttributes = [("POSITION", "Position", "" , "MAN_TRANS", 0 ),
                      ("NORMAL", "Normal", "", "MANIPUL", 1),
                      ("TANGENT", "Tangent", "", "OUTLINER_OB_EMPTY", 2),
                      ("BITANGENT", "Bitangent", "", "EMPTY_DATA", 3),
                      ("TEXTURE", "Texture Coordinates", "", "GROUP_UVS", 4),
                      ("GROUPS", "Vertex Groups", "", "GROUP_VERTEX", 5),                                            
                      ("COLOR", "Vertex Color", "", "GROUP_VCOL", 6)]
#!BPY

# Copyright (c) <2013> Daniel Peterson
# License: MIT Software License <www.mini3d.org/license>


vertexAttributeDict = {i[0]: [i[1], i[3]] for i in vertexAttributes}

class AttributeProperty(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Name", default="new attribute")
    type = bpy.props.EnumProperty(
                name="Attribute Type",
                items=vertexAttributes,
                )

class AttributePropertyGroup(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Name", default="new vertex attributes")
    index = bpy.props.IntProperty()
    attributes = bpy.props.CollectionProperty(type=AttributeProperty)

def findGroup(name):
    settings = getMini3dScene()
    return settings.attribute_groups.get(name)
    
def getMini3dScene():
    mini3dScene = bpy.data.scenes.get("Mini3d Settings")
    
    if mini3dScene:
        return mini3dScene
    else:
        return bpy.data.scenes.new("Mini3d Settings")

def makeUniqueName(name):
    settings = getMini3dScene()
    index = 1
    while settings.attribute_groups.find(name) >= 0:
        name = "Attribute Group." + str(index)
        index += 1

    return name
    
class AddAttributeGroupOperator(bpy.types.Operator):
    bl_idname = "mesh.attribute_group_add"
    bl_label = "Add Vertex Attribute Group"

    def invoke(self, context, event):
        name = makeUniqueName("Attribute Group")
        new_group = getMini3dScene().attribute_groups.add()
        bpy.context.object.data.attribute_group = new_group.name = name
        return{"FINISHED"}

class RemoveAttributeGroupOperator(bpy.types.Operator):
    bl_idname = "mesh.attribute_group_remove"
    bl_label = "Remove Vertex Attribute Group"

    def invoke(self, context, event):

        settings = getMini3dScene()
        mesh = bpy.context.object.data
        
        index = 0
        for group in settings.attribute_groups:
            if group.name == mesh.attribute_group:
                settings.attribute_groups.remove(index)
                break
            
            index += 1
            
        mesh.attribute_group = ""
        return{"FINISHED"}    

        
class AddAttributeOperator(bpy.types.Operator):
    bl_idname = "mesh.attribute_add"
    bl_label = "Add Vertex Attribute"

    def invoke(self, context, event):
        mesh = bpy.context.object.data
        group = findGroup(mesh.attribute_group)
        
        if group:
            group.attributes.add()
            group.index = len(group.attributes) - 1
            
        return{"FINISHED"}

class RemoveAttributeOperator(bpy.types.Operator):
    bl_idname = "mesh.attribute_remove"
    bl_label = "Remove Vertex Attribute"

    def invoke(self, context, event):
        mesh = bpy.context.object.data
        group = findGroup(mesh.attribute_group)
        
        if group:
            index = group.index
            
            if index >= 0 and index < len(group.attributes):
                group.attributes.remove(index)
                group.index -= 1

        return{"FINISHED"}    

class MoveAttributeOperator(bpy.types.Operator):
    bl_idname = "mesh.attribute_move"
    bl_label = "Move Vertex Attribute"
    
    direction = bpy.props.EnumProperty(
                        name="direction",
                        items=(("UP", "Up", ""),
                              ("DOWN", "Down", ""))
                        )
    
    def invoke(self, context, event):

        mesh = bpy.context.object.data
        group = findGroup(mesh.attribute_group)
        
        if group:
            index = group.index
        
            if self.direction == 'DOWN' and index < len(group.attributes) - 1:
                group.attributes.move(index, index + 1)
                group.index += 1
            elif self.direction == 'UP' and index > 0:
                group.attributes.move(index, index - 1)
                group.index -= 1
        
        return{"FINISHED"}    

class RenameGroupOperator(bpy.types.Operator):
    bl_idname = "mesh.rename_group"
    bl_label = "Rename Vertex Attribute Group"

    group = bpy.props.StringProperty()
    old_name = None
    
    def execute(self, context):
        if self.group == self.old_name:
            return {'FINISHED'}
        
        gp = findGroup(self.old_name)
        gp.name = makeUniqueName(self.group)
            
        for mesh in bpy.data.meshes:
            if mesh.attribute_group == self.old_name:
                mesh.attribute_group = gp.name

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)                 
        return {'FINISHED'}

    def invoke(self, context, event):
        self.old_name = self.group
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
class DoNotiongOperator(bpy.types.Operator):
    bl_idname = "mesh.do_nothing"
    bl_label = "Rename Vertex Attribute Group"

    def invoke(self, context, event):
        return{"FINISHED"}
        
class MeshAttributeGroupSet(bpy.types.Operator):
    bl_idname = "mesh.attribute_group_set"
    bl_label = "Set Vertex Attribute Group"

    group = bpy.props.StringProperty()

    def execute(self, context):
        print("set: ", self.group)
        bpy.context.object.data.attribute_group = self.group
        return {'FINISHED'}

class MeshAttributeGroupsMenu(bpy.types.Menu):
    bl_idname = "mesh.attribute_group_menu"
    bl_label = "Vertex Attribute Group"

    def draw(self, context):
        
        settings = getMini3dScene()
    
        for group in settings.attribute_groups:
            self.layout.operator("mesh.attribute_group_set", text=group.name).group = group.name
        
class ATTRIBUTE_UL_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, translate=False, icon_value=icon)
            layout.label(text=vertexAttributeDict[item.type][0], translate=False, icon=vertexAttributeDict[item.type][1])
            
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class MeshPanel(bpy.types.Panel):
    bl_label = "Mini3d Export"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    def draw(self, context):
     
        if context.object.type == 'MESH':
            
            settings = getMini3dScene()
            
            layout = self.layout
            mesh = bpy.context.object.data

            group = findGroup(mesh.attribute_group)
            label = ""

            if group:
                label = group.name
        
            #parent attribute mesh
            layout.label(text="Share Attributes:", translate=False)
            
            row = layout.row(align=True)
            
            row.menu("mesh.attribute_group_menu", icon='TRIA_UP', text="")
            if group:
                row.operator("mesh.rename_group", text=group.name).group = group.name
            else:
                row.operator("mesh.do_nothing", text=" ")
                
            row.operator("mesh.attribute_group_add", icon='ZOOMIN', text="")
            row.operator("mesh.attribute_group_remove", icon='ZOOMOUT', text="")
        
            row = layout.row()

            if group:
                collection = group.attributes
                size = len(collection)
                index = group.index

                #separator
                layout.label(text="Vertex Attributes:", translate=False)
                col = layout.column()
                row = col.row()
                row.template_list('ATTRIBUTE_UL_list', 'attribute_list', group, "attributes", group, "index")

                # Attribute list buttons
                col = row.column(align=True)
                col.operator("mesh.attribute_add", icon='ZOOMIN', text="")
                col.operator("mesh.attribute_remove", icon='ZOOMOUT', text="")
                
                attribute = None
                if size > 0 and index < size:
                    attribute = collection[index]

                if attribute:
                    col.separator()
                    col.operator("mesh.attribute_move", icon='TRIA_UP', text="").direction = 'UP'
                    col.operator("mesh.attribute_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

                    row = layout.row()
                    row.prop(attribute, "name")
                    row = layout.row()
                    row.prop(attribute, "type")
                    
       