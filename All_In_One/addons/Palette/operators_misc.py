import bpy
import os

from .addon_prefs import get_addon_preferences
from .files_functions import RemovePaletteFile, GetPrefPath, RefreshPaletteFromFile, SavePaletteFile, OpenFolder
from .node_functions import CreateNodeGroupFromPalette, RemoveNodeGroupFromPalette, UpdateAddNodeGroupColor, UpdateRemoveNodeGroupColor, PaletteNodeUpdate

# add palette
class PaletteCreatePalette(bpy.types.Operator):
    bl_idname = "palette.create_palette"
    bl_label = "Create Palette"
    bl_description = "Create a new Palette"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0

    def execute(self, context):
        prefs=get_addon_preferences()
        prop=bpy.data.window_managers['WinMan'].palette[0]
        new=prop.palettes.add()
        old_name=[]
        for p in prop.palettes:
            if "Palette_" in p.name:
                old_name.append(p.name.split('Palette_')[1])
        if len(old_name)!=0:
            old_name.sort()
            namenb=int(old_name[len(old_name)-1])+1
        else:
            namenb=1
        new.name='Palette_'+str(namenb)
        new.filepath=os.path.join(GetPrefPath(), new.name+".gpl")
        new.temp_name=new.name
        col1=new.colors.add()
        col1.name+="1"
        col1.color_value=prefs.col1
        col2=new.colors.add()
        col2.name+="2"
        col2.color_value=prefs.col2
        col3=new.colors.add()
        col3.name+="3"
        col3.color_value=prefs.col3
        col4=new.colors.add()
        col4.name+="4"
        col4.color_value=prefs.col4
        col5=new.colors.add()
        col5.name+="5"
        col5.color_value=prefs.col5
        CreateNodeGroupFromPalette(new)
        return {"FINISHED"}
    
# remove palette
class PaletteRemovePalette(bpy.types.Operator):
    bl_idname = "palette.remove_palette"
    bl_label = "Remove Palette"
    bl_description = "Remove the Palette"
    bl_options = {"REGISTER", "UNDO"}
    
    index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col=layout.column()
        col.label('Color Palette will be Permanently Removed', icon='ERROR')
        col.label('Click OK to continue')
        

    def execute(self, context):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        #delete palette file
        RemovePaletteFile(prop.palettes[self.index])
        #delete node group
        RemoveNodeGroupFromPalette(prop.palettes[self.index])
        prop.palettes.remove(self.index)
        if prop.manage_menu==True:
            prop.manage_menu=False
        return {"FINISHED"}
    
# remove all palette
class PaletteRemoveAllPalette(bpy.types.Operator):
    bl_idname = "palette.remove_all_palette"
    bl_label = "Remove All Palettes"
    bl_description = "Remove all the Palettes"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col=layout.column()
        col.label('All Color Palettes will be Permanently Removed', icon='ERROR')
        col.label('Click OK to continue')
        

    def execute(self, context):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        for p in prop.palettes:
            #delete palette file
            RemovePaletteFile(p)
            #delete node group
            RemoveNodeGroupFromPalette(p)
        prop.palettes.clear()
        return {"FINISHED"}
    
# add color to active palette
class PaletteAddColor(bpy.types.Operator):
    bl_idname = "palette.add_color"
    bl_label = "Add Color"
    bl_description = "Add Color to active Palette"
    bl_options = {"REGISTER"}

    index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0

    def execute(self, context):
        prefs=get_addon_preferences()
        prop=bpy.data.window_managers['WinMan'].palette[0]
        active=prop.palettes[self.index]
        new=active.colors.add()
        new.name+=str(len(active.colors))
        new.color_value=prefs.col3
        UpdateAddNodeGroupColor(active)
        PaletteNodeUpdate(self, context)
        SavePaletteFile(active)
        return {"FINISHED"}
    
# switch to management
class PaletteSwitchToManagement(bpy.types.Operator):
    bl_idname = "palette.switch_to_management"
    bl_label = "Manage"
    bl_description = "Switch to Management"
    bl_options = {"REGISTER"}

    index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0

    def execute(self, context):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        active=prop.palettes[self.index]
        prop.manage_menu=True
        prop.index=self.index
        for c in active.colors:
            c.temp_name=c.name
        active.temp_name=active.name
        return {"FINISHED"}
    
# remove color from active palette
class PaletteRemoveColor(bpy.types.Operator):
    bl_idname = "palette.remove_color"
    bl_label = "Remove Color"
    bl_description = "Remove Color from active Palette"
    bl_options = {"REGISTER"}
    
    index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0

    def execute(self, context):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        active=prop.palettes[prop.index]
        active.colors.remove(self.index)
        SavePaletteFile(active)
        UpdateRemoveNodeGroupColor(active)
        PaletteNodeUpdate(self, context)
        return {"FINISHED"}

# rename color from active palette
class PaletteRenameColor(bpy.types.Operator):
    bl_idname = "palette.rename_color"
    bl_label = "Rename Color"
    bl_description = "Rename Color from active Palette"
    bl_options = {"REGISTER"}
    
    index = bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0

    def execute(self, context):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        active=prop.palettes[prop.index]
        activecol=active.colors[self.index]
        temp=activecol.temp_name
        oname=[]
        ct=-1
        chk=0
        for c in active.colors:
            ct+=1
            if ct!=self.index:
                oname.append(c.name)
        for n in oname:
            if n==temp:
                chk=1
        if chk==0:
            activecol.name=temp
        else:
            nb=oname.count(temp)
            newname=temp+"_"+str(nb)
            for n in oname:
                if n==newname:
                    nb+=1
            activecol.name=temp+"_"+str(nb)
        activecol.temp_name=activecol.name
        return {"FINISHED"}
    
# rename palette
class PaletteRenamePalette(bpy.types.Operator):
    bl_idname = "palette.rename_palette"
    bl_label = "Rename Palette"
    bl_description = "Rename active Palette"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0

    def execute(self, context):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        palettes=prop.palettes
        active=prop.palettes[prop.index]
        temp=active.temp_name
        oname=[]
        ct=-1
        chk=0
        for c in palettes:
            ct+=1
            if ct!=prop.index:
                oname.append(c.name)
        for n in oname:
            if n==temp:
                chk=1
        if chk==0:
            active.name=temp
        else:
            nb=oname.count(temp)
            newname=temp+"_"+str(nb)
            for n in oname:
                if n==newname:
                    nb+=1
            active.name=temp+"_"+str(nb)
        active.temp_name=active.name
        return {"FINISHED"}

# palette zoom actions
class PaletteZoomActions(bpy.types.Operator):
    bl_idname = "palette.zoom_actions"
    bl_label = ""

    action = bpy.props.EnumProperty(
        items=(
            ('PLUS', "Plus", ""),
            ('MINUS', "Minus", ""),))
            
    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0

    def invoke(self, context, event):
        prop=bpy.data.window_managers['WinMan'].palette[0]
        if self.action == 'PLUS':
            prop.color_per_row-=1
        elif self.action == 'MINUS':
            prop.color_per_row+=1
        return {"FINISHED"}
    
# refresh palettes from filepath
class PaletteRefreshFromFIles(bpy.types.Operator):
    bl_idname = "palette.refresh_from_files"
    bl_label = "Refresh Palettes"
    bl_description = "Refresh Palettes from External Files"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0

    def execute(self, context):
        pallettes=bpy.data.window_managers['WinMan'].palette[0].palettes
        for i in range(len(pallettes)-1,-1,-1):
            pallettes.remove(i)
        RefreshPaletteFromFile()
        return {"FINISHED"}

# open folder
class PaletteOpenPaletteFolder(bpy.types.Operator):
    bl_idname = "palette.open_folder"
    bl_label = "Open"
    bl_description = "Open Palette Folder"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return len(bpy.data.window_managers['WinMan'].palette)!=0
    
    def execute(self, context):
        palette=bpy.data.window_managers['WinMan'].palette[0].palettes
        OpenFolder(GetPrefPath())
        return {"FINISHED"}