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
    "name": "Blend Library",
    "author": "Vincent Gires",
    "description": "Asset Manager - Append or link materials/objects/groups/node groups of specific folder locations",
    "version": (0, 3, 3),
    "blender": (2, 7, 6),
    "location": "3D View > Tools || Node Editor > Tools",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Import-Export/Blend_Library",
    "category": "Learnbgame"
}

import bpy
import os.path


######### CALL BACK #########
#############################

def custom_paths_callback_node_groups(self, context):
    bpy.context.scene.node_groups_library_list_compositing.clear()
    bpy.context.scene.node_groups_library_list_shading.clear()
    bpy.context.scene.node_groups_library_list_texture.clear()
    
def custom_paths_callback_materials(self, context):
    bpy.context.scene.materials_library_list.clear()

def custom_paths_callback_objects(self, context):
    bpy.context.scene.objects_library_list.clear()
    
def custom_paths_callback_groups(self, context):
    bpy.context.scene.groups_library_list.clear()


######### ADDON PREFERENCES ##########
######################################


class library_addon_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    folderpath_nodegroups_compositing = bpy.props.StringProperty(
            name="Compositing Node Groups",
            subtype='DIR_PATH',
            )
    folderpath_nodegroups_shading = bpy.props.StringProperty(
            name="Shading Node Groups",
            subtype='DIR_PATH',
            )
    folderpath_nodegroups_texture = bpy.props.StringProperty(
            name="Texture Node Groups",
            subtype='DIR_PATH',
            )
    folderpath_materials = bpy.props.StringProperty(
            name="Materials",
            subtype='DIR_PATH',
            )
    folderpath_objects = bpy.props.StringProperty(
            name="Objects",
            subtype='DIR_PATH',
            )
    folderpath_groups = bpy.props.StringProperty(
            name="Groups",
            subtype='DIR_PATH',
            )
    
    list_display_filename = bpy.props.BoolProperty(
        name = "display filename",
        description = "Display the filename in library list",
        default = 1,
    )

    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "list_display_filename")
        
        layout.prop(self, "folderpath_nodegroups_compositing")
        layout.prop(self, "folderpath_nodegroups_shading")
        layout.prop(self, "folderpath_nodegroups_texture")
        layout.prop(self, "folderpath_materials")
        layout.prop(self, "folderpath_objects")
        layout.prop(self, "folderpath_groups")



######### PROPERTIES ##########
###############################


class blend_library_customPaths_properties(bpy.types.PropertyGroup):
    
    bpy.types.Scene.customFolderpath_nodegroups_compositing = bpy.props.StringProperty(
        name="Compositing Node Groups",
        subtype='DIR_PATH',
    )
    bpy.types.Scene.customFolderpath_nodegroups_shading = bpy.props.StringProperty(
        name="Shading Node Groups",
        subtype='DIR_PATH',
    )
    bpy.types.Scene.customFolderpath_nodegroups_texture = bpy.props.StringProperty(
        name="Texture Node Groups",
        subtype='DIR_PATH',
    )
    bpy.types.Scene.customFolderpath_materials = bpy.props.StringProperty(
        name="Materials",
        subtype='DIR_PATH',
    )
    bpy.types.Scene.customFolderpath_objects = bpy.props.StringProperty(
        name="Objects",
        subtype='DIR_PATH',
    )
    bpy.types.Scene.customFolderpath_groups = bpy.props.StringProperty(
        name="Groups",
        subtype='DIR_PATH',
    )


class property_node_groups_library_compositing(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="node name", default="Group")
    file = bpy.props.StringProperty(name="file", default="file.blend")
    
class property_node_groups_library_shading(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="node name", default="Group")
    file = bpy.props.StringProperty(name="file", default="file.blend")
    
class property_node_groups_library_texture(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="node name", default="Group")
    file = bpy.props.StringProperty(name="file", default="file.blend") 

class property_materials_library(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="material name", default="Material")
    file = bpy.props.StringProperty(name="file", default="file.blend")
    
class property_objects_library(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="object name", default="Object")
    file = bpy.props.StringProperty(name="file", default="file.blend")
    use = bpy.props.BoolProperty(name="use", description="Use this item when importing", default=False)
    
class property_groups_library(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="group name", default="Group")
    file = bpy.props.StringProperty(name="file", default="file.blend") 

class node_groups_library_properties(bpy.types.PropertyGroup):
    
    bpy.types.Scene.node_groups_library_compositing_index = bpy.props.IntProperty(
        name = "Index",
        default = 0,
        min = 0,
    )
    
    bpy.types.Scene.node_groups_library_shading_index = bpy.props.IntProperty(
        name = "Index",
        default = 0,
        min = 0,
    )
    
    bpy.types.Scene.node_groups_library_texture_index = bpy.props.IntProperty(
        name = "Index",
        default = 0,
        min = 0,
    )
    
    bpy.types.Scene.materials_library_index = bpy.props.IntProperty(
        name = "Index",
        default = 0,
        min = 0,
    )
    
    bpy.types.Scene.objects_library_index = bpy.props.IntProperty(
        name = "Index",
        default = 0,
        min = 0,
    )
    
    bpy.types.Scene.groups_library_index = bpy.props.IntProperty(
        name = "Index",
        default = 0,
        min = 0,
    )

    bpy.types.Scene.node_groups_library_addNode = bpy.props.BoolProperty(
        name = "Add node",
        description = "Add node in the node tree",
        default = 1,
    )
    
    bpy.types.Scene.node_groups_library_single = bpy.props.BoolProperty(
        name = "single-user",
        description = "Append node group only if this group is not in the node groups of the blend file",
        default = 0,
    )
    
    bpy.types.Scene.materials_library_assign = bpy.props.BoolProperty(
        name = "Assign",
        description = "Assign material to selected object",
        default = 1,
    )
    
    bpy.types.Scene.materials_library_replace = bpy.props.BoolProperty(
        name = "Replace",
        description = "Replace materials of the selected objects by the imported one",
        default = 0,
    )
    
    bpy.types.Scene.materials_library_single = bpy.props.BoolProperty(
        name = "single-user",
        description = "Append material only if this material is not in the blend file",
        default = 0,
    )
    
    bpy.types.Scene.view3d_library_useCursor = bpy.props.BoolProperty(
        name = "Use 3D Cursor",
        default = 0,
    )
    
    bpy.types.Scene.view3d_library_instanceGroup = bpy.props.BoolProperty(
        name = "Instance Group",
        default = 0,
    )
    
    bpy.types.Scene.library_customPaths_node_groups = bpy.props.BoolProperty(
        name = "Use custom paths",
        default = 0,
        update = custom_paths_callback_node_groups
    )
    
    bpy.types.Scene.library_customPaths_materials = bpy.props.BoolProperty(
        name = "Use custom paths",
        default = 0,
        update = custom_paths_callback_materials
    )
    
    bpy.types.Scene.library_customPaths_objects = bpy.props.BoolProperty(
        name = "Use custom paths",
        default = 0,
        update = custom_paths_callback_objects
    )
    
    bpy.types.Scene.library_customPaths_groups = bpy.props.BoolProperty(
        name = "Use custom paths",
        default = 0,
        update = custom_paths_callback_groups
    )
    
    bpy.types.Scene.nodegroups_library_import_type = bpy.props.EnumProperty(
        items = (
            ('append', 'Append', 'Append group to the blend file'),
            ('link', 'Link', 'Link group to the blend file'),
        ),
        name = "Import",
        description = "Append or Link",
        default = 'append',
    )
   
    bpy.types.Scene.materials_library_import_type = bpy.props.EnumProperty(
        items = (
            ('append', 'Append', 'Append material to the blend file'),
            ('link', 'Link', 'Link material to the blend file'),
        ),
        name = "Import",
        description = "Append or Link",
        default = 'append',
    )
    
    bpy.types.Scene.objects_library_import_type = bpy.props.EnumProperty(
        items = (
            ('append', 'Append', 'Append object to the blend file'),
            ('link', 'Link', 'Link object to the blend file'),
        ),
        name = "Import",
        description = "Append or Link",
        default = 'append',
    )

    bpy.types.Scene.groups_library_import_type = bpy.props.EnumProperty(
        items = (
            ('append', 'Append', 'Append group to the blend file'),
            ('link', 'Link', 'Link group to the blend file'),
        ),
        name = "Import",
        description = "Append or Link",
        default = 'append',
    )


######### FUNCTIONS ##########
##############################


def get_addon_preferences():
    #addon_preferences = bpy.context.user_preferences.addons['blend_library'].preferences # file name
    addon_preferences = bpy.context.user_preferences.addons[__name__].preferences
    return addon_preferences


def import_from_library(datablock, folderpath, file, selected, link, instance_group=False):
    
    folderpath = bpy.path.abspath(folderpath)
    
    if link:
        bpy.ops.wm.link(directory=os.path.join(folderpath, file, datablock), filename=selected)
        
    else:
        bpy.ops.wm.append(directory=os.path.join(folderpath, file, datablock), filename=selected, instance_groups=instance_group)
    

def scan_folder_nodes(folderpath, tree_type):
    
    folderpath = bpy.path.abspath(folderpath)
    
    for file in os.listdir(folderpath):
        if file.endswith(".blend"):
        
            filepath = folderpath+"\\"+file
        
            # look node_groups through file
            with bpy.data.libraries.load(filepath) as (data_from, data_to):
                
                for name in data_from.node_groups:
                
                    # add node_groups to list
                    if tree_type == "compositing":
                        my_item = bpy.context.scene.node_groups_library_list_compositing.add()
                    elif tree_type == "shading":
                        my_item = bpy.context.scene.node_groups_library_list_shading.add()
                    elif tree_type == "texture":
                        my_item = bpy.context.scene.node_groups_library_list_texture.add()
                    my_item.name = name
                    my_item.file = file


def scan_folder_files(folderpath, datablock):
    
    folderpath = bpy.path.abspath(folderpath)
    
    for file in os.listdir(folderpath):
        if file.endswith(".blend"):
            filepath = folderpath+"\\"+file
            with bpy.data.libraries.load(filepath) as (data_from, data_to):
                for name in eval("data_from."+datablock):
                    my_item = eval("bpy.context.scene."+datablock+"_library_list.add()")
                    my_item.name = name
                    my_item.file = file


def is_nodeGroup(nodegroup):
    if nodegroup in bpy.data.node_groups:
        return True
    else:
        return False
    
def is_material(material):
    if material in bpy.data.materials:
        return True
    else:
        return False

def list_blend_nodegroups():
    nodegroups_list = []
    for node in bpy.data.node_groups:
        nodegroups_list.append(node.name)
    return nodegroups_list

def list_blend_materials():
    materials_list = []
    for mat in bpy.data.materials:
        materials_list.append(mat.name)
    return materials_list

def add_node_group(nodegroup):
    
    tree_type = bpy.context.space_data.tree_type
    node_type = None
    
    if tree_type == "CompositorNodeTree":
        node_type = "CompositorNodeGroup"
    elif tree_type == "ShaderNodeTree":
        node_type = "ShaderNodeGroup"
    elif tree_type == "TextureNodeTree":
        node_type = "TextureNodeGroup"
        
    bpy.ops.node.add_node(use_transform=True, type=node_type, settings=[{"name":"node_tree", "value":"bpy.data.node_groups['"+nodegroup+"']"}])


def is_listChecked(list):
    for item in list:
        if item.use:
            return True



######### LIST TEMPLATE ##########
##################################


class node_groups_library_UL(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.alignment = 'EXPAND'
        layout.label(str(item.name))
        if get_addon_preferences().list_display_filename:
            layout.label(str(item.file))

class materials_library_UL(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.alignment = 'EXPAND'
        layout.label(str(item.name))
        if get_addon_preferences().list_display_filename:
            layout.label(str(item.file))
        
class objects_library_UL(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.alignment = 'EXPAND'
        layout.label(str(item.name))
        if get_addon_preferences().list_display_filename:
            layout.label(str(item.file))
        layout.prop(item, "use", text="")
        
class groups_library_UL(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.alignment = 'EXPAND'
        layout.label(str(item.name))
        if get_addon_preferences().list_display_filename:
            layout.label(str(item.file))



######### PANEL ##########
##########################

class node_groups_library_settings(bpy.types.Panel):
    bl_label = "Settings"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Library"
    
    @classmethod
    def poll(cls, context):
        tree_type = context.space_data.tree_type
        return tree_type == 'ShaderNodeTree' or tree_type == 'CompositorNodeTree' or tree_type == 'TextureNodeTree'
    
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label("Custom paths :")
        box.prop(context.scene, "customFolderpath_nodegroups_compositing")
        box.prop(context.scene, "customFolderpath_nodegroups_shading")
        box.prop(context.scene, "customFolderpath_nodegroups_texture")

class node_groups_library_UIListPanel(bpy.types.Panel):
    bl_label = "Node Groups"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Library"
    
    
    @classmethod
    def poll(cls, context):
        tree_type = context.space_data.tree_type
        return tree_type == 'ShaderNodeTree' or tree_type == 'CompositorNodeTree' or tree_type == 'TextureNodeTree'
    
    
    
    def draw(self, context):
        layout = self.layout
        
        addon_preferences = get_addon_preferences()
        
        layout.prop(context.scene, "library_customPaths_node_groups")
        
        if context.space_data.tree_type == "CompositorNodeTree":
            if (context.scene.library_customPaths_node_groups and context.scene.customFolderpath_nodegroups_compositing) or (addon_preferences.folderpath_nodegroups_compositing and not context.scene.library_customPaths_node_groups) :
                self.list_compositing(context)
                
            elif context.scene.library_customPaths_node_groups:
                layout.box().label("Set path in Settings panel", icon="QUESTION")
            else:
                layout.box().label("Set path in addon preferences", icon="QUESTION")
        
        elif context.space_data.tree_type == "ShaderNodeTree":
            if (context.scene.library_customPaths_node_groups and context.scene.customFolderpath_nodegroups_shading) or (addon_preferences.folderpath_nodegroups_shading and not context.scene.library_customPaths_node_groups) :
                self.list_shading(context)
            elif context.scene.library_customPaths_node_groups:
                layout.box().label("Set path in Settings panel", icon="QUESTION")
            else:
                layout.box().label("Set path in addon preferences", icon="QUESTION")
                
        elif context.space_data.tree_type == "TextureNodeTree":
            if (context.scene.library_customPaths_node_groups and context.scene.customFolderpath_nodegroups_texture) or (addon_preferences.folderpath_nodegroups_texture and not context.scene.library_customPaths_node_groups) :
                self.list_texture(context)
                
            elif context.scene.library_customPaths_node_groups:
                layout.box().label("Set path in Settings panel", icon="QUESTION")
            else:
                layout.box().label("Set path in addon preferences", icon="QUESTION")
            
    def buttons_append_link(self, context):
        layout = self.layout
        
        layout.prop(context.scene, "nodegroups_library_import_type", expand=True)
        
        if context.scene.nodegroups_library_import_type == "append":
            layout.operator("append_nodegroup.btn", text="Import", icon="APPEND_BLEND")
            row = layout.row(align=False)
            row.prop(context.scene, "node_groups_library_addNode")
            row.prop(context.scene, "node_groups_library_single")
        else:
            layout.operator("link_nodegroup.btn", text="Import", icon="LINK_BLEND")
    
    def list_compositing(self, context):
        layout = self.layout
        addon_preferences = get_addon_preferences()
        
        if context.space_data.tree_type == "CompositorNodeTree":
            if addon_preferences.folderpath_nodegroups_compositing:
                layout.operator("scan_folder_nodes.btn")
                layout.template_list("node_groups_library_UL", "", context.scene, "node_groups_library_list_compositing", context.scene, "node_groups_library_compositing_index")
                layout.prop(context.scene, "node_groups_library_list_compositing")
                
                if context.scene.node_groups_library_list_compositing:
                    self.buttons_append_link(context)

        
    def list_shading(self, context):
        layout = self.layout
        addon_preferences = get_addon_preferences()
        
        if context.space_data.tree_type == "ShaderNodeTree":
            if addon_preferences.folderpath_nodegroups_shading:
                layout.operator("scan_folder_nodes.btn")
                layout.template_list("node_groups_library_UL", "", context.scene, "node_groups_library_list_shading", context.scene, "node_groups_library_shading_index")
                layout.prop(context.scene, "node_groups_library_list_shading")
                
                if context.scene.node_groups_library_list_shading:
                    self.buttons_append_link(context)
                    
                    
    def list_texture(self, context):
        layout = self.layout
        addon_preferences = get_addon_preferences()
        
        if context.space_data.tree_type == "TextureNodeTree":
            if addon_preferences.folderpath_nodegroups_texture:
                layout.operator("scan_folder_nodes.btn")
                layout.template_list("node_groups_library_UL", "", context.scene, "node_groups_library_list_texture", context.scene, "node_groups_library_texture_index")
                layout.prop(context.scene, "node_groups_library_list_texture")
                
                if context.scene.node_groups_library_list_texture:
                    self.buttons_append_link(context)
            







class VIEW3D_library_settings(bpy.types.Panel):
    bl_label = "Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Library"
    bl_context = "objectmode"
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label("Custom paths :")
        box.prop(context.scene, "customFolderpath_materials")
        box.prop(context.scene, "customFolderpath_objects")
        box.prop(context.scene, "customFolderpath_groups")



class VIEW3D_materials_library(bpy.types.Panel):
    bl_label = "Materials"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Library"
    bl_context = "objectmode"
    
    
    def draw(self, context):
        layout = self.layout
        addon_preferences = get_addon_preferences()
        
        layout.prop(context.scene, "library_customPaths_materials")
        
        if context.scene.library_customPaths_materials and context.scene.customFolderpath_materials:
            self.list(context)
        elif addon_preferences.folderpath_materials and not context.scene.library_customPaths_materials:
            self.list(context)
        elif context.scene.library_customPaths_materials:
            layout.box().label("Set path in Settings panel", icon="QUESTION")
        else:
            layout.box().label("Set path in addon preferences", icon="QUESTION")
        
        
        
    def list(self, context):
        layout = self.layout
        layout.operator("scan_folder_materials.btn")
        layout.template_list("materials_library_UL", "", context.scene, "materials_library_list", context.scene, "materials_library_index")
        layout.prop(context.scene, "materials_library_list")
        
        if context.scene.materials_library_list:
            layout.prop(context.scene, "materials_library_import_type", expand=True)
            
            if context.scene.materials_library_import_type == "append":
                layout.operator("append_material.btn", text="Import", icon="APPEND_BLEND")
                row = layout.row(align=False)
                row.prop(context.scene, "materials_library_assign")
                row.prop(context.scene, "materials_library_replace")
                row.prop(context.scene, "materials_library_single")
            else:
                layout.operator("link_material.btn", text="Import", icon="LINK_BLEND")
        
        
        

class VIEW3D_objects_library(bpy.types.Panel):
    bl_label = "Objects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Library"
    bl_context = "objectmode"
    
    
    def draw(self, context):
        layout = self.layout
        addon_preferences = get_addon_preferences()
        
        layout.prop(context.scene, "library_customPaths_objects")
        
        if context.scene.library_customPaths_objects and context.scene.customFolderpath_objects:
            self.list(context)
        elif addon_preferences.folderpath_objects and not context.scene.library_customPaths_objects:
            self.list(context)
        elif context.scene.library_customPaths_objects:
            layout.box().label("Set path in Settings panel", icon="QUESTION")
        else:
            layout.box().label("Set path in addon preferences", icon="QUESTION")
        
        
        
    def list(self, context):
        layout = self.layout
        
        layout.operator("scan_folder_objects.btn")
        layout.template_list("objects_library_UL", "", context.scene, "objects_library_list", context.scene, "objects_library_index")
        layout.prop(context.scene, "objects_library_list")
        
        if context.scene.objects_library_list:
            layout.prop(context.scene, "objects_library_import_type", expand=True)
            row = layout.row(align=False)
            if context.scene.objects_library_import_type == "append":
                row.operator("import_object.btn", icon="APPEND_BLEND")
                row.prop(context.scene, "view3d_library_useCursor")
            else:
                row.operator("import_object.btn", icon="LINK_BLEND")
                


class VIEW3D_groups_library(bpy.types.Panel):
    bl_label = "Groups"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Library"
    bl_context = "objectmode"
    
    
    def draw(self, context):
        layout = self.layout
        
        addon_preferences = get_addon_preferences()
        
        layout.prop(context.scene, "library_customPaths_groups")
        
        if context.scene.library_customPaths_groups and context.scene.customFolderpath_groups:
            self.list(context)
        elif addon_preferences.folderpath_groups and not context.scene.library_customPaths_groups:
            self.list(context)
        elif context.scene.library_customPaths_groups:
            layout.box().label("Set path in Settings panel", icon="QUESTION")
        else:
            layout.box().label("Set path in addon preferences", icon="QUESTION")
        

    def list(self, context):
        layout = self.layout
        layout.operator("scan_folder_groups.btn")
        layout.template_list("groups_library_UL", "", context.scene, "groups_library_list", context.scene, "groups_library_index")
        layout.prop(context.scene, "materials_library_list")
        
        if context.scene.groups_library_list:
            layout.prop(context.scene, "groups_library_import_type", expand=True)
            row = layout.row(align=False)
            if context.scene.groups_library_import_type == "append":
                row.operator("append_group.btn", text="Import", icon="APPEND_BLEND")
                row.prop(context.scene, "view3d_library_instanceGroup")
            else:
                row.operator("link_group.btn", text="Import", icon="LINK_BLEND")
        
                

######### OPERATOR ##########
#############################



class node_groups_library_scan(bpy.types.Operator):
    bl_idname = "scan_folder_nodes.btn"
    bl_label = "Scan / Update"
    bl_description = "Scan files on the node groups folder"
    
    def execute(self, context):
        
        addon_preferences = get_addon_preferences()
        
        if context.space_data.tree_type == "CompositorNodeTree":
            if addon_preferences.folderpath_nodegroups_compositing:
                context.scene.node_groups_library_list_compositing.clear()
                context.scene.node_groups_library_compositing_index = 0
                if bpy.context.scene.library_customPaths_node_groups:
                    folderpath = context.scene.customFolderpath_nodegroups_compositing
                else:
                    folderpath = addon_preferences.folderpath_nodegroups_compositing
                if folderpath:
                    scan_folder_nodes(folderpath, "compositing")
                
        elif context.space_data.tree_type == "ShaderNodeTree":
            if addon_preferences.folderpath_nodegroups_shading:
                context.scene.node_groups_library_list_shading.clear()
                context.scene.node_groups_library_shading_index = 0
                if bpy.context.scene.library_customPaths_node_groups:
                    folderpath = context.scene.customFolderpath_nodegroups_shading
                else:
                    folderpath = addon_preferences.folderpath_nodegroups_shading
                if folderpath:
                    scan_folder_nodes(folderpath, "shading")
                    
        elif context.space_data.tree_type == "TextureNodeTree":
            if addon_preferences.folderpath_nodegroups_texture:
                context.scene.node_groups_library_list_texture.clear()
                context.scene.node_groups_library_texture_index = 0
                if bpy.context.scene.library_customPaths_node_groups:
                    folderpath = context.scene.customFolderpath_nodegroups_texture
                else:
                    folderpath = addon_preferences.folderpath_nodegroups_texture
                if folderpath:
                    scan_folder_nodes(folderpath, "texture")

                        
        return{'FINISHED'}


class materials_library_scan(bpy.types.Operator):
    bl_idname = "scan_folder_materials.btn"
    bl_label = "Scan / Update"
    bl_description = "Scan files on the materials folder"
    
    def execute(self, context):
        
        context.scene.materials_library_list.clear()
        context.scene.materials_library_index = 0
        
        if bpy.context.scene.library_customPaths_materials:
            if context.scene.customFolderpath_materials:
                scan_folder_files(context.scene.customFolderpath_materials, "materials")
        else:
            addon_preferences = get_addon_preferences()
            if addon_preferences.folderpath_materials:
                scan_folder_files(addon_preferences.folderpath_materials, "materials")
                
        return{'FINISHED'}

class objects_library_scan(bpy.types.Operator):
    bl_idname = "scan_folder_objects.btn"
    bl_label = "Scan / Update"
    bl_description = "Scan files on the objects folder"
    
    def execute(self, context):
        
        context.scene.objects_library_list.clear()
        context.scene.objects_library_index = 0
        
        if bpy.context.scene.library_customPaths_objects:
            if context.scene.customFolderpath_objects:
                scan_folder_files(context.scene.customFolderpath_objects, "objects")
        else:
            addon_preferences = get_addon_preferences()
            if addon_preferences.folderpath_objects:
                scan_folder_files(addon_preferences.folderpath_objects, "objects")
                
        return{'FINISHED'}


class groups_library_scan(bpy.types.Operator):
    bl_idname = "scan_folder_groups.btn"
    bl_label = "Scan / Update"
    bl_description = "Scan files on the materials folder"
    
    def execute(self, context):
        
        context.scene.groups_library_list.clear()
        context.scene.groups_library_index = 0
        
        if bpy.context.scene.library_customPaths_groups:
            if context.scene.customFolderpath_groups:
                scan_folder_files(context.scene.customFolderpath_groups, "groups")
        else:
            addon_preferences = get_addon_preferences()
            if addon_preferences.folderpath_groups:
                scan_folder_files(addon_preferences.folderpath_groups, "groups")
                
        return{'FINISHED'}



class node_groups_library_append(bpy.types.Operator):
    bl_idname = "append_nodegroup.btn"
    bl_label = "Append"
    bl_description = "Append node group to the blend file"
    
    def execute(self, context):
        
        addon_preferences = get_addon_preferences()
        
        nodegroups_list = list_blend_nodegroups()
        
        if context.space_data.tree_type == "CompositorNodeTree":
            index = context.scene.node_groups_library_compositing_index
            nodegroup_selected = context.scene.node_groups_library_list_compositing[index].name
            filename = context.scene.node_groups_library_list_compositing[index].file
            
            if context.scene.library_customPaths_node_groups:
                folderpath = bpy.context.scene.customFolderpath_nodegroups_compositing
            else:
                folderpath = addon_preferences.folderpath_nodegroups_compositing
            
            self.add_node_group_check_settings(context, nodegroup_selected, folderpath, filename, nodegroups_list)
            
        elif context.space_data.tree_type == "ShaderNodeTree":
            index = context.scene.node_groups_library_shading_index
            nodegroup_selected = context.scene.node_groups_library_list_shading[index].name
            filename = context.scene.node_groups_library_list_shading[index].file

            if context.scene.library_customPaths_node_groups:
                folderpath = bpy.context.scene.customFolderpath_nodegroups_shading
            else:
                folderpath = addon_preferences.folderpath_nodegroups_shading

            self.add_node_group_check_settings(context, nodegroup_selected, folderpath, filename, nodegroups_list)
            
        elif context.space_data.tree_type == "TextureNodeTree":
            index = context.scene.node_groups_library_texture_index
            nodegroup_selected = context.scene.node_groups_library_list_texture[index].name
            filename = context.scene.node_groups_library_list_texture[index].file
            
            if context.scene.library_customPaths_node_groups:
                folderpath = bpy.context.scene.customFolderpath_nodegroups_texture
            else:
                folderpath = addon_preferences.folderpath_nodegroups_texture
                
            self.add_node_group_check_settings(context, nodegroup_selected, folderpath, filename, nodegroups_list)

        
        return{'FINISHED'}



    def add_node_group_check_settings(self, context, nodegroup_selected, folderpath, filename, nodegroups_list):
        if not is_nodeGroup(nodegroup_selected) or context.scene.node_groups_library_single :
            import_from_library(datablock="NodeTree", folderpath=folderpath, file=filename, selected=nodegroup_selected, link=False)
        if context.scene.node_groups_library_addNode:
            if context.scene.node_groups_library_single:
                nodegroups_list_import = list_blend_nodegroups()
                nodegroup_created = "".join(set(nodegroups_list_import) - set(nodegroups_list))
                add_node_group(nodegroup_created)
            else:
                add_node_group(nodegroup_selected)
        
        
        

class node_groups_library_link(bpy.types.Operator):
    bl_idname = "link_nodegroup.btn"
    bl_label = "Link"
    bl_description = "Link node group to the blend file"
    
    def execute(self, context):
        
        addon_preferences = get_addon_preferences()
        
        if context.space_data.tree_type == "CompositorNodeTree":
            index = context.scene.node_groups_library_compositing_index
            nodegroup_selected = context.scene.node_groups_library_list_compositing[index].name
            filename = context.scene.node_groups_library_list_compositing[index].file
            
            if context.scene.library_customPaths_node_groups:
                folderpath = bpy.context.scene.customFolderpath_nodegroups_compositing
            else:
                folderpath = addon_preferences.folderpath_nodegroups_compositing
            
            import_from_library(datablock="NodeTree", folderpath=folderpath, file=filename, selected=nodegroup_selected, link=True)
            
        elif context.space_data.tree_type == "ShaderNodeTree":
            index = context.scene.node_groups_library_shading_index
            nodegroup_selected = context.scene.node_groups_library_list_shading[index].name
            filename = context.scene.node_groups_library_list_shading[index].file

            if context.scene.library_customPaths_node_groups:
                folderpath = bpy.context.scene.customFolderpath_nodegroups_shading
            else:
                folderpath = addon_preferences.folderpath_nodegroups_shading

            import_from_library(datablock="NodeTree", folderpath=folderpath, file=filename, selected=nodegroup_selected, link=True)
            
        elif context.space_data.tree_type == "TextureNodeTree":
            index = context.scene.node_groups_library_texture_index
            nodegroup_selected = context.scene.node_groups_library_list_texture[index].name
            filename = context.scene.node_groups_library_list_texture[index].file
            
            if context.scene.library_customPaths_node_groups:
                folderpath = bpy.context.scene.customFolderpath_nodegroups_texture
            else:
                folderpath = addon_preferences.folderpath_nodegroups_texture
                
            import_from_library(datablock="NodeTree", folderpath=folderpath, file=filename, selected=nodegroup_selected, link=True)
            
        
        return{'FINISHED'}


class materials_library_append(bpy.types.Operator):
    bl_idname = "append_material.btn"
    bl_label = "Append"
    bl_description = "Append material to the blend file"
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        
        materials_list = list_blend_materials()
        
        index = context.scene.materials_library_index
        material_selected = context.scene.materials_library_list[index].name
        filename = context.scene.materials_library_list[index].file
        if context.scene.library_customPaths_materials:
            folderpath = bpy.context.scene.customFolderpath_materials
        else:
            folderpath = addon_preferences.folderpath_materials
        
        
        selected_objects = context.selected_objects
        
        if not is_material(material_selected) or context.scene.materials_library_single :
            import_from_library(datablock="Material", folderpath=folderpath, file=filename, selected=material_selected, link=False)
        if context.scene.materials_library_assign:
            if context.scene.materials_library_single:
                materials_list_import = list_blend_materials()
                material_created = "".join(set(materials_list_import) - set(materials_list))
                
                for obj in selected_objects:
                    self.is_replace(context, obj)
                    obj.data.materials.append(bpy.data.materials[material_created])
            else:
                
                for obj in selected_objects:
                    self.is_replace(context, obj)
                    obj.data.materials.append(bpy.data.materials[material_selected])
        
        return{'FINISHED'}
    
    def is_replace(self, context, obj):
        if context.scene.materials_library_replace:
            obj.data.materials.clear()



class materials_library_link(bpy.types.Operator):
    bl_idname = "link_material.btn"
    bl_label = "Link"
    bl_description = "Link material to the blend file"
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        
        index = context.scene.materials_library_index
        material_selected = context.scene.materials_library_list[index].name
        filename = context.scene.materials_library_list[index].file
        if context.scene.library_customPaths_materials:
            folderpath = bpy.context.scene.customFolderpath_materials
        else:
            folderpath = addon_preferences.folderpath_materials
        
        import_from_library(datablock="Material", folderpath=folderpath, file=filename, selected=material_selected, link=True)
        
        return{'FINISHED'}

class objects_library_import(bpy.types.Operator):
    bl_idname = "import_object.btn"
    bl_label = "Import"
    bl_description = "Import object to the blend file"
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        list = context.scene.objects_library_list
        imported_objects = []
        
        if context.scene.library_customPaths_objects:
            folderpath = bpy.context.scene.customFolderpath_objects
        else:
            folderpath = addon_preferences.folderpath_objects
        
        if context.scene.objects_library_import_type == 'link':
            import_link = True
        else:
            import_link = False
        
        
        index = context.scene.objects_library_index
        object_selected = list[index].name
        filename = list[index].file
        
        
        if is_listChecked(list):
            for item in list:
                if item.use:
                    import_from_library(datablock="Object", folderpath=folderpath, file=item.file, selected=item.name, link=import_link)
                    imported_objects.append(context.selected_objects[-1])
                    
        else:
            index = context.scene.objects_library_index
            object_selected = list[index].name
            filename = list[index].file
            import_from_library(datablock="Object", folderpath=folderpath, file=filename, selected=object_selected, link=import_link)
            imported_objects.append(context.selected_objects[-1])
        
        
        if context.scene.view3d_library_useCursor and context.scene.objects_library_import_type == 'append':
            for obj in imported_objects:
                obj.location = context.space_data.cursor_location
        
        return{'FINISHED'}


class groups_library_append(bpy.types.Operator):
    bl_idname = "append_group.btn"
    bl_label = "Append"
    bl_description = "Append group to the blend file"
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        
        index = context.scene.groups_library_index
        group_selected = context.scene.groups_library_list[index].name
        filename = context.scene.groups_library_list[index].file
        if context.scene.library_customPaths_groups:
            folderpath = bpy.context.scene.customFolderpath_groups
        else:
            folderpath = addon_preferences.folderpath_groups
        
        instance_group = context.scene.view3d_library_instanceGroup
        import_from_library(datablock="Group", folderpath=folderpath, file=filename, selected=group_selected, link=False, instance_group=instance_group)
        
        return{'FINISHED'}

class groups_library_link(bpy.types.Operator):
    bl_idname = "link_group.btn"
    bl_label = "Link"
    bl_description = "Link group to the blend file"
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        
        index = context.scene.groups_library_index
        group_selected = context.scene.groups_library_list[index].name
        filename = context.scene.groups_library_list[index].file
        if context.scene.library_customPaths_groups:
            folderpath = bpy.context.scene.customFolderpath_groups
        else:
            folderpath = addon_preferences.folderpath_groups
        
        import_from_library(datablock="Group", folderpath=folderpath, file=filename, selected=group_selected, link=True)
        
        return{'FINISHED'}
    
    
######### REGISTRATION ##########
#################################


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.node_groups_library_list_compositing = \
        bpy.props.CollectionProperty(type=property_node_groups_library_compositing)
    bpy.types.Scene.node_groups_library_list_shading = \
        bpy.props.CollectionProperty(type=property_node_groups_library_shading)
    bpy.types.Scene.node_groups_library_list_texture = \
        bpy.props.CollectionProperty(type=property_node_groups_library_texture)
    bpy.types.Scene.materials_library_list = \
        bpy.props.CollectionProperty(type=property_materials_library)
    bpy.types.Scene.objects_library_list = \
        bpy.props.CollectionProperty(type=property_objects_library)
    bpy.types.Scene.groups_library_list = \
        bpy.props.CollectionProperty(type=property_groups_library)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.node_groups_library_list_compositing
    del bpy.types.Scene.node_groups_library_list_shading
    del bpy.types.Scene.node_groups_library_list_texture
    del bpy.types.Scene.materials_library_list
    del bpy.types.Scene.objects_library_list
    del bpy.types.Scene.groups_library_list

if __name__ == "__main__":
    register()


