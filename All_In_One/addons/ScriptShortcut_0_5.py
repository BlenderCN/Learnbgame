#Todo:
#   Add the ability to have multiple buttons/labels per row - figure out how
#   Maybe add ability to make panel presets conditional? would this be possible?
#   Maybe add ability to add in any properties
#   Functions to implement:
#       Sequencer - Cut selected at cursor, move strip back to original start position, and move cursor to clip start position
#
#Changes:
#   0.3
#       Initial Release
#   0.4
#       Added popup menu with the shortcut ctrl-shift-space that pops up the current panel for an area
#       Added a change script button to the button editor dialog
#       Implemented stored panel presets through a drop-down menu
#   0.5
#       Made panel settings into addon preferences, they no longer clog up the window view menu with a settings menu
#       Resolved error messages when loading script

import bpy
import os
import sys
from bpy_extras.io_utils import ImportHelper


bl_info = {
    "name": "Script Shortcut",
    "description": "Allows easily running of python scripts by adding a configurable shortcut panel to the Properties shelf of most areas.  Pressing a script button will execute commands directly in the script, and will run the 'register()' function if it exists.",
    "author": "Hudson Barkley (Snu)",
    "version": (0, 5, 0),
    "blender": (2, 76, 0),
    "location": "Properties shelf in most areas, View menu in same areas, Ctrl-Shift-Space shortcut in most areas",
    "wiki_url": "none",
    "category": "User Interface"
}

addon_keymaps = []


def return_panel(scene, panel):
    #This function will return the panel data for the given panel name
    if panel == 'VIEW_3D': return [scene.scriptshortcuts.VIEW_3Dedit, scene.scriptshortcuts.VIEW_3D, scene.scriptshortcuts.VIEW_3Dpresets]
    if panel == 'GRAPH_EDITOR': return [scene.scriptshortcuts.GRAPH_EDITORedit, scene.scriptshortcuts.GRAPH_EDITOR, scene.scriptshortcuts.GRAPH_EDITORpresets]
    if panel == 'NLA_EDITOR': return [scene.scriptshortcuts.NLA_EDITORedit, scene.scriptshortcuts.NLA_EDITOR, scene.scriptshortcuts.NLA_EDITORpresets]
    if panel == 'IMAGE_EDITOR': return [scene.scriptshortcuts.IMAGE_EDITORedit, scene.scriptshortcuts.IMAGE_EDITOR, scene.scriptshortcuts.IMAGE_EDITORpresets]
    if panel == 'SEQUENCE_EDITOR': return [scene.scriptshortcuts.SEQUENCE_EDITORedit, scene.scriptshortcuts.SEQUENCE_EDITOR, scene.scriptshortcuts.SEQUENCE_EDITORpresets]
    if panel == 'CLIP_EDITOR': return [scene.scriptshortcuts.CLIP_EDITORedit, scene.scriptshortcuts.CLIP_EDITOR, scene.scriptshortcuts.CLIP_EDITORpresets]
    if panel == 'TEXT_EDITOR': return [scene.scriptshortcuts.TEXT_EDITORedit, scene.scriptshortcuts.TEXT_EDITOR, scene.scriptshortcuts.TEXT_EDITORpresets]
    if panel == 'NODE_EDITOR': return [scene.scriptshortcuts.NODE_EDITORedit, scene.scriptshortcuts.NODE_EDITOR, scene.scriptshortcuts.NODE_EDITORpresets]
    if panel == 'LOGIC_EDITOR': return [scene.scriptshortcuts.LOGIC_EDITORedit, scene.scriptshortcuts.LOGIC_EDITOR, scene.scriptshortcuts.LOGIC_EDITORpresets]
    else: return [False, [], []]


class ScriptShortcutPanelButton(bpy.types.PropertyGroup):
    #This class stores the data for a panel element
    
    #The button name
    title = bpy.props.StringProperty(
        name = "Button Title",
        default = "Button")
    #The script that will be run when the button is activated
    script = bpy.props.StringProperty(
        name = "Script File",
        default = "")
    #Determine if this button is conditional or not
    conditional = bpy.props.BoolProperty(
        name = "Conditional Enabled",
        description = "Make This Button A Conditional Button",
        default = False)
    #A string that contains the conditional check statement for this button
    requirement = bpy.props.StringProperty(
        name = "Conditional Requirement",
        default = "")


class ScriptShortcutPanel(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty("")
    panel = bpy.props.CollectionProperty(type = ScriptShortcutPanelButton)


class ScriptShortcutPanels(bpy.types.PropertyGroup):
    #Class that stores the data for all the panel elements
    VIEW_3D = bpy.props.CollectionProperty(type = ScriptShortcutPanelButton)
    VIEW_3Dpresets = bpy.props.CollectionProperty(type = ScriptShortcutPanel)
    VIEW_3Dedit = bpy.props.BoolProperty(default=False)
    GRAPH_EDITOR = bpy.props.CollectionProperty(type = ScriptShortcutPanelButton)
    GRAPH_EDITORpresets = bpy.props.CollectionProperty(type = ScriptShortcutPanel)
    GRAPH_EDITORedit = bpy.props.BoolProperty(default=False)
    NLA_EDITOR = bpy.props.CollectionProperty(type = ScriptShortcutPanelButton)
    NLA_EDITORpresets = bpy.props.CollectionProperty(type = ScriptShortcutPanel)
    NLA_EDITORedit = bpy.props.BoolProperty(default=False)
    IMAGE_EDITOR = bpy.props.CollectionProperty(type = ScriptShortcutPanelButton)
    IMAGE_EDITORpresets = bpy.props.CollectionProperty(type = ScriptShortcutPanel)
    IMAGE_EDITORedit = bpy.props.BoolProperty(default=False)
    SEQUENCE_EDITOR = bpy.props.CollectionProperty(type = ScriptShortcutPanelButton)
    SEQUENCE_EDITORpresets = bpy.props.CollectionProperty(type = ScriptShortcutPanel)
    SEQUENCE_EDITORedit = bpy.props.BoolProperty(default=False)
    CLIP_EDITOR = bpy.props.CollectionProperty(type = ScriptShortcutPanelButton)
    CLIP_EDITORpresets = bpy.props.CollectionProperty(type = ScriptShortcutPanel)
    CLIP_EDITORedit = bpy.props.BoolProperty(default=False)
    TEXT_EDITOR = bpy.props.CollectionProperty(type = ScriptShortcutPanelButton)
    TEXT_EDITORpresets = bpy.props.CollectionProperty(type = ScriptShortcutPanel)
    TEXT_EDITORedit = bpy.props.BoolProperty(default=False)
    NODE_EDITOR = bpy.props.CollectionProperty(type = ScriptShortcutPanelButton)
    NODE_EDITORpresets = bpy.props.CollectionProperty(type = ScriptShortcutPanel)
    NODE_EDITORedit = bpy.props.BoolProperty(default=False)
    LOGIC_EDITOR = bpy.props.CollectionProperty(type = ScriptShortcutPanelButton)
    LOGIC_EDITORpresets = bpy.props.CollectionProperty(type = ScriptShortcutPanel)
    LOGIC_EDITORedit = bpy.props.BoolProperty(default=False)


class ScriptShortcutSave(bpy.types.Operator, ImportHelper):
    #This is an operator to save a current panel layout to an external file
    #The panel variable must be set
    
    bl_idname = "scriptshortcut.save"
    bl_label = "Save Layout"
    bl_description = "Save this layout"
    
    panel = bpy.props.StringProperty()    
    title = bpy.props.StringProperty(name='Title')
    filepath = bpy.props.StringProperty()
    
    def execute(self, context):
        #Get the panel data
        self.data = return_panel(context.scene, self.panel)[1]
        try:
            file = open(self.filepath, 'w')
            for button in self.data:
                file.write(button.title+'\n')
                file.write(str(button.conditional)+'\n')
                file.write(button.script+'\n')
            file.close()
            self.report({'INFO'}, "Saved file to: "+self.filepath)
        except:
            self.report({'WARNING'}, "Unable to save file: "+self.filepath)
        return {'FINISHED'}


class ScriptShortcutLoad(bpy.types.Operator, ImportHelper):
    #This is an operator to load a layout file
    bl_idname = "scriptshortcut.load"
    bl_label = "Load Layout"
    bl_description = "Load this layout"
    
    panel = bpy.props.StringProperty()    
    title = bpy.props.StringProperty(name='Title')
    filepath = bpy.props.StringProperty()
    
    def execute(self, context):
        try:
            file = open(self.filepath, "r")
            data = file.readlines()
            file.close()
            if len(data) > 1:
                oldpanel = return_panel(context.scene, self.panel)[1]
                oldpanel.clear()
                element = 'title'
                title = ""
                conditional = False
                for line in data:
                    if len(line.replace('\n', '')) > 0:
                        if element == 'title':
                            title = line.replace('\n', '')
                            element = 'conditional'
                        elif element == 'conditional':
                            if line.replace('\n', '') == 'True':
                                conditional = True
                            element = 'script'
                        elif element == 'script':
                            button = oldpanel.add()
                            button.title = title
                            button.conditional = conditional
                            button.script = line.replace('\n', '')
                            try:
                                file = open(button.script, 'r')
                                requirement = file.readline().strip("\n\r")
                                file.close()
                                if requirement[0] == "#":
                                    button.requirement = requirement[1:]
                            except:
                                pass
                            element = 'title'
                            
                self.report({'INFO'}, "Loaded layout from file: "+self.filepath)
            else:
                raise Exception("")
        except:
            self.report({'WARNING'}, "Unable to open file: "+self.filepath)
        return {'FINISHED'}


class ScriptShortcutClear(bpy.types.Operator):
    #This operator will remove all elements from a panel
    bl_idname = "scriptshortcut.clear"
    bl_label = "Clear Layout"
    bl_description = "Clear this layout"
    
    panel = bpy.props.StringProperty()    
    
    def execute(self, context):
        self.data = return_panel(context.scene, self.panel)[1]
        self.data.clear()
        return {'FINISHED'}


class ScriptShortcutMove(bpy.types.Operator):
    #This operator will move an element up or down in the list
    bl_idname = "scriptshortcut.move"
    bl_label = "Move Shortcut"
    bl_description = "Move this item"
    
    argument = bpy.props.StringProperty()
    
    def execute(self, context):
        panel = self.argument.split(',')[0]
        buttonindex = int(self.argument.split(',')[1])
        direction = self.argument.split(',')[2]
        buttons = return_panel(context.scene, panel)[1]
        if direction == 'up':
            move = -1
        else:
            move = 1
        buttons.move(buttonindex, buttonindex+move)
        return {'FINISHED'}


class ScriptShortcutRun(bpy.types.Operator):
    #This operator will run an external python script
    bl_idname = "scriptshortcut.run"
    bl_label = "Run Script"
    bl_description = "Run a python script"

    path = bpy.props.StringProperty()

    def execute(self, context):
        try:
            folder = os.path.split(self.path)[0]
            file = os.path.splitext(os.path.split(self.path)[1])[0]
            sys.path.insert(0, folder)
            script = __import__(file)

            try:
                script.register()

            except:
                pass

            sys.path.remove(folder)
            del sys.modules[file]
            del script

        except:
            pass

        return {'FINISHED'}


class ScriptShortcutRename(bpy.types.Operator):
    #This operator will rename an element in a shortcut panel
    bl_idname = "scriptshortcut.rename"
    bl_label = "Rename Button Or Label"
    bl_description = "Rename this item"

    argument = bpy.props.StringProperty()
    title = bpy.props.StringProperty(name='Title')
    script = bpy.props.StringProperty()
    index = bpy.props.IntProperty(0)

    def invoke(self, context, event):
        self.index = int(self.argument.split(',')[1])
        buttons = return_panel(context.scene, self.argument.split(',')[0])[1]
        self.button = buttons[self.index]
        self.title = self.button.title
        self.script = self.button.script
        return context.window_manager.invoke_props_dialog(self, width=600, height=200)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'title')
        if self.script != '_':
            row = layout.row()
            row.operator("scriptshortcut.changescript", text="Select Script").argument = self.argument

    def execute(self, context):
        self.button.title = self.title
        return {'FINISHED'}


class ScriptShortcutChangeScript(bpy.types.Operator, ImportHelper):
    #This operator will open a file select dialog to select an external script for a panel element
    bl_idname = "scriptshortcut.changescript"
    bl_label = "Select A Script For Script Shortcut"

    argument = bpy.props.StringProperty()
    index = bpy.props.IntProperty()
    panel = bpy.props.StringProperty()
    filename_ext = ".py"

    filter_glob = bpy.props.StringProperty(
            default="*.py",
            options={'HIDDEN'})
    directory = bpy.props.StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        self.index = int(self.argument.split(',')[1])
        self.panel = self.argument.split(',')[0]
        buttons = return_panel(context.scene, self.panel)[1]
        button = buttons[self.index]
        button.script = self.filepath
        file = open(self.filepath, 'r')
        requirement = file.readline().strip("\n\r")
        file.close()
        if requirement[0] == "#":
            button.requirement = requirement[1:]
        return {'FINISHED'}


class ScriptShortcutAdd(bpy.types.Operator):
    #This operator will add a new element to a shortcut panel
    bl_idname = "scriptshortcut.new"
    bl_label = "Add New Script Shortcut"
    bl_description = "Add a new item"

    argument = bpy.props.StringProperty()
    title = bpy.props.StringProperty(name='Title')
    type = bpy.props.StringProperty()
    panel = bpy.props.StringProperty()

    def invoke(self, context, event):
        self.type = self.argument.split(',')[1]
        self.panel = self.argument.split(',')[0]
        buttons = return_panel(context.scene, self.panel)[1]
        if self.type == "button":
            self.title = "Button "+str(len(buttons)+1)
            return context.window_manager.invoke_props_dialog(self, width=600, height=200)
        elif self.type == "label":
            self.title = "Label "+str(len(buttons)+1)
            return context.window_manager.invoke_props_dialog(self, width=600, height=200)
        else:
            button = buttons.add()
            button.title = '_'
            button.script = '_'
            return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'title')

    def execute(self, context):
        if self.type == "button":
            bpy.ops.scriptshortcut.selectscript('INVOKE_DEFAULT', title=self.title, panel=self.argument.split(',')[0])
        else:
            buttons = return_panel(context.scene, self.panel)[1]
            button = buttons.add()
            button.title = self.title
            button.script = '_'
        return {'FINISHED'}


class ScriptShortcutSelectScript(bpy.types.Operator, ImportHelper):
    #This operator will open a file select dialog to select an external script for a panel element, then create a button
    bl_idname = "scriptshortcut.selectscript"
    bl_label = "Select A Script For Script Shortcut"

    title = bpy.props.StringProperty(name='Title')
    panel = bpy.props.StringProperty(name='Panel')
    filename_ext = ".py"

    filter_glob = bpy.props.StringProperty(
            default="*.py",
            options={'HIDDEN'})
    directory = bpy.props.StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        buttons = return_panel(context.scene, self.panel)[1]
        button = buttons.add()
        button.title = self.title
        button.script = self.filepath
        file = open(self.filepath, 'r')
        requirement = file.readline().strip("\n\r")
        file.close()
        if requirement[0] == "#":
            button.requirement = requirement[1:]
        return {'FINISHED'}


class ScriptShortcutRemove(bpy.types.Operator):
    #This operator will remove an item from the shortcut list
    bl_idname = "scriptshortcut.remove"
    bl_label = "Remove A Script Shortcut"
    bl_description = "Remove this item"

    argument = bpy.props.StringProperty()

    def execute(self, context):
        buttons = return_panel(context.scene, self.argument.split(',')[0])[1]
        button = int(self.argument.split(',')[1])
        buttons.remove(button)
        return {'FINISHED'}


class ScriptShortcutPopup(bpy.types.Menu):
    #This will show the current panel for the area as a popup
    bl_idname = "scriptshortcut.popup"
    bl_label = "Script Shortcut"

    @classmethod
    def poll(self, context):
        area_type = context.area.type
        prefs = context.user_preferences.addons[__name__].preferences
        if hasattr(prefs, area_type):
            panelon = eval("prefs."+area_type)
            return panelon
        else:
            return False
    
    def draw(self, context):
        layout = self.layout
        area_type = context.area.type
        panel = return_panel(context.scene, area_type)[1]

        for index, button in enumerate(panel):
            #Iterate through the elements and draw each one
            row = layout.row()
            if button.script == '_':
                #This element is a label or spacer
                if button.title == '_':
                    #This element is a spacer
                    row.label("")
                else:
                    #This element is a label
                    row.label(button.title)

            else:
                #This element is a button
                row.operator("scriptshortcut.run", text=button.title).path = button.script
                
                #Check if this button is conditional and should be disabled
                if button.conditional and len(button.requirement) > 0:
                    #This button is in conditional mode
                    try:
                        condition = eval(button.requirement)
                        if condition == False:
                            row.enabled = False
                    except:
                        row.enabled = False


class ScriptShortcutSettings(bpy.types.AddonPreferences):
    bl_idname = __name__
    VIEW_3D = bpy.props.BoolProperty(
        name="Enable 3d View Panel",
        default=True)
    GRAPH_EDITOR = bpy.props.BoolProperty(
        name="Enable Graph Editor Panel",
        default=True)
    NLA_EDITOR = bpy.props.BoolProperty(
        name="Enable NLA Editor Panel",
        default=True)
    IMAGE_EDITOR = bpy.props.BoolProperty(
        name="Enable Image Editor Panel",
        default=True)
    SEQUENCE_EDITOR = bpy.props.BoolProperty(
        name="Enable Sequence Editor Panel",
        default=True)
    CLIP_EDITOR = bpy.props.BoolProperty(
        name="Enable Clip Editor Panel",
        default=True)
    TEXT_EDITOR = bpy.props.BoolProperty(
        name="Enable Text Editor Panel",
        default=True)
    NODE_EDITOR = bpy.props.BoolProperty(
        name="Enable Node Editor Panel",
        default=True)
    LOGIC_EDITOR = bpy.props.BoolProperty(
        name="Enable Logic Editor Panel",
        default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "VIEW_3D")
        layout.prop(self, "GRAPH_EDITOR")
        layout.prop(self, "NLA_EDITOR")
        layout.prop(self, "IMAGE_EDITOR")
        layout.prop(self, "SEQUENCE_EDITOR")
        layout.prop(self, "CLIP_EDITOR")
        layout.prop(self, "TEXT_EDITOR")
        layout.prop(self, "NODE_EDITOR")
        layout.prop(self, "LOGIC_EDITOR")


class ScriptShortcutPresetsMenu(bpy.types.Menu):
    bl_idname = 'scriptshortcut.presetmenu'
    bl_label = 'List of saved presets'
    
    def draw(self, context):
        layout = self.layout
        area_type = context.area.type
        paneldata = return_panel(context.scene, area_type)
        presets = paneldata[2]

        for index, preset in enumerate(presets):
            layout.operator("scriptshortcut.presetactivate", text=preset.name).argument = str(index)+','+area_type


class ScriptShortcutPresetActivate(bpy.types.Operator):
    #This operator will copy a preset into the current panel
    bl_idname = "scriptshortcut.presetactivate"
    bl_label = "Select A Preset"
    bl_description = "Select this preset"

    argument = bpy.props.StringProperty()

    def execute(self, context):
        panel = self.argument.split(',',1)[1]
        index = int(self.argument.split(',')[0])
        paneldata = return_panel(context.scene, panel)
        presets = paneldata[2]
        preset = presets[index].panel
        buttons = paneldata[1]
        buttons.clear()
        for button in preset:
            newelement = buttons.add()
            newelement.title = button.title
            newelement.script = button.script
            newelement.conditional = button.conditional
            newelement.requirement = button.requirement
        return {'FINISHED'}


class ScriptShortcutPresetsMenuEdit(bpy.types.Menu):
    bl_idname = 'scriptshortcut.presetmenuedit'
    bl_label = 'List of saved presets'
    
    def draw(self, context):
        #Sorry about this code... menus are just a pain to get two columns in tho
        layout = self.layout
        area_type = context.area.type
        paneldata = return_panel(context.scene, area_type)
        presets = paneldata[2]
        
        layout.label("Click A Preset To Rename")
        split = layout.split()
        column = split.column()
        for index, preset in enumerate(presets):
            column.operator("scriptshortcut.presetrename", text=preset.name).argument = str(index)+','+area_type
        column.operator("scriptshortcut.presetadd", text="Add Current As Preset").panel = area_type
        
        column = split.column()
        for index, preset in enumerate(presets):
            column.operator("scriptshortcut.presetremove", text="", icon="X").argument = str(index)+','+area_type


class ScriptShortcutPresetAdd(bpy.types.Operator):
    bl_idname = 'scriptshortcut.presetadd'
    bl_label = 'Add a new shortcut panel preset'
    
    panel = bpy.props.StringProperty()
    name = bpy.props.StringProperty()
    
    def invoke(self, context, event):
        self.name = "New Preset"
        return context.window_manager.invoke_props_dialog(self, width=600, height=200)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'name')

    def execute(self, context):
        self.paneldata = return_panel(context.scene, self.panel)
        self.presets = self.paneldata[2]
        self.newpreset = self.presets.add()
        currentpanel = self.paneldata[1]
        for button in currentpanel:
            newelement = self.newpreset.panel.add()
            newelement.title = button.title
            newelement.script = button.script
            newelement.conditional = button.conditional
            newelement.requirement = button.requirement
        self.newpreset.name = self.name
        return {'FINISHED'}


class ScriptShortcutPresetRemove(bpy.types.Operator):
    #This operator will remove a shortcut panel preset
    bl_idname = "scriptshortcut.presetremove"
    bl_label = "Remove A Panel Preset"
    bl_description = "Remove this preset"

    argument = bpy.props.StringProperty()

    def execute(self, context):
        panel = self.argument.split(',',1)[1]
        index = int(self.argument.split(',')[0])
        paneldata = return_panel(context.scene, panel)
        presets = paneldata[2]
        presets.remove(index)
        return {'FINISHED'}


class ScriptShortcutPresetRename(bpy.types.Operator):
    #This operator will rename a shortcut panel preset
    bl_idname = "scriptshortcut.presetrename"
    bl_label = "Rename Preset"
    bl_description = "Rename this item"

    argument = bpy.props.StringProperty()
    title = bpy.props.StringProperty(name='Title')
    panel = bpy.props.StringProperty()
    index = bpy.props.IntProperty(0)

    def invoke(self, context, event):
        self.index = int(self.argument.split(',')[0])
        self.panel = self.argument.split(',',1)[1]
        self.paneldata = return_panel(context.scene, self.panel)
        self.presets = self.paneldata[2]
        self.title = self.presets[self.index].name
        return context.window_manager.invoke_props_dialog(self, width=600, height=200)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'title')

    def execute(self, context):
        self.presets[self.index].name = self.title
        return {'FINISHED'}


class ScriptShortcutPanelTemplate():
    #This class is the template for all panels
    bl_label = "Script Shortcuts"
    #bl_space_type = "EMPTY"
    #bl_region_type = "TEMPORARY"
    
    @classmethod
    def poll(self, context):
        prefs = context.user_preferences.addons[__name__].preferences
        if hasattr(prefs, self.bl_space_type):
            panelon = eval("prefs."+self.bl_space_type)
            return panelon
        else:
            return False

    def draw(self, context):
        panel = self.bl_space_type
        layout = self.layout
        
        #Get the panel data thats stored in the scene properties
        paneldata = return_panel(context.scene, panel)
        buttons = paneldata[1]
        editmode = paneldata[0]
        presets = paneldata[2]
        
        if editmode:
            #Draw the panel in edit mode
            row = layout.row()
            row.menu('scriptshortcut.presetmenuedit', text='Panel Presets')
            
            for index, button in enumerate(buttons):
                #Iterate through the elements and draw each one
                row = layout.row()
                split = row.split(percentage=.6, align=True)
                if button.script == '_' and button.title == '_':
                    #This element is a spacer
                    split.label("<Spacer>")
                else:
                    #This element is a label or button
                    split.operator("scriptshortcut.rename", text=button.title).argument = panel+','+str(index)

                #Move up button
                split.operator("scriptshortcut.move", text="", icon="TRIA_UP").argument = panel+','+str(index)+','+'up'
                #Move down button
                split.operator("scriptshortcut.move", text="", icon="TRIA_DOWN").argument = panel+','+str(index)+','+'down'
                #Remove element button
                split.operator("scriptshortcut.remove", text="", icon="X").argument = panel+','+str(index)
                    
                if button.script == '_':
                    #Spacer area to keep layout over the conditional property
                    split.label(text="")
                else:
                    #Conditional mode checkbox property
                    split.prop(button, 'conditional')

            row = layout.row()
            split = row.split(align = True)
            #Create a new button
            split.operator("scriptshortcut.new", text="Button", icon="PLUS").argument = panel+','+"button"
            #Create a new spacer
            split.operator("scriptshortcut.new", text="Spacer", icon="PLUS").argument = panel+','+"spacer"
            #Create a new label
            split.operator("scriptshortcut.new", text="Label", icon="PLUS").argument = panel+','+"label"
            row = layout.row()
            split = row.split()
            #Save layout button
            split.operator("scriptshortcut.save", text="Save", icon="DISK_DRIVE").panel = panel
            #Load layout button
            split.operator("scriptshortcut.load", text="Load", icon="FILESEL").panel = panel
            #Clear layout button
            split.operator("scriptshortcut.clear", text="Clear").panel = panel

        else:
            #Draw the panel in normal display mode
            if len(presets) > 0:
                row = layout.row()
                row.menu('scriptshortcut.presetmenu', text='Panel Presets')
            for index, button in enumerate(buttons):
                #Iterate through the elements and draw each one
                row = layout.row()
                if button.script == '_':
                    #This element is a label or spacer
                    if button.title == '_':
                        #This element is a spacer
                        row.label("")
                    else:
                        #This element is a label
                        row.label(button.title)

                else:
                    #This element is a button
                    row.operator("scriptshortcut.run", text=button.title).path = button.script
                    
                    #Check if this button is conditional and should be disabled
                    if button.conditional and len(button.requirement) > 0:
                        #This button is in conditional mode
                        try:
                            condition = eval(button.requirement)
                            if condition == False:
                                row.enabled = False
                        except:
                            row.enabled = False
        
        row = layout.row()
        #Edit mode toggle button
        row.prop(context.scene.scriptshortcuts, panel+'edit', text='Edit')


#The following classes are definitions for each panel
class ScriptShortcutPanelView3d(ScriptShortcutPanelTemplate,bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

class ScriptShortcutPanelGraphEditor(ScriptShortcutPanelTemplate,bpy.types.Panel):
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"

class ScriptShortcutPanelNLAEditor(ScriptShortcutPanelTemplate,bpy.types.Panel):
    bl_space_type = "NLA_EDITOR"
    bl_region_type = "UI"

class ScriptShortcutPanelImageEditor(ScriptShortcutPanelTemplate,bpy.types.Panel):
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"

class ScriptShortcutPanelSequenceEditor(ScriptShortcutPanelTemplate,bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"

class ScriptShortcutPanelClipEditor(ScriptShortcutPanelTemplate,bpy.types.Panel):
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "UI"

class ScriptShortcutPanelTextEditor(ScriptShortcutPanelTemplate,bpy.types.Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

class ScriptShortcutPanelNodeEditor(ScriptShortcutPanelTemplate,bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

class ScriptShortcutPanelLogicEditor(ScriptShortcutPanelTemplate,bpy.types.Panel):
    bl_space_type = "LOGIC_EDITOR"
    bl_region_type = "UI"


def register():
    bpy.utils.register_class(ScriptShortcutSettings)
    bpy.utils.register_class(ScriptShortcutPanelButton)
    bpy.utils.register_class(ScriptShortcutPanel)
    bpy.utils.register_class(ScriptShortcutPanels)
    bpy.utils.register_class(ScriptShortcutSave)
    bpy.utils.register_class(ScriptShortcutLoad)
    bpy.utils.register_class(ScriptShortcutClear)
    bpy.utils.register_class(ScriptShortcutMove)
    bpy.utils.register_class(ScriptShortcutRun)
    bpy.utils.register_class(ScriptShortcutRename)
    bpy.utils.register_class(ScriptShortcutChangeScript)
    bpy.utils.register_class(ScriptShortcutAdd)
    bpy.utils.register_class(ScriptShortcutSelectScript)
    bpy.utils.register_class(ScriptShortcutRemove)
    bpy.utils.register_class(ScriptShortcutPopup)
    bpy.utils.register_class(ScriptShortcutPresetsMenu)
    bpy.utils.register_class(ScriptShortcutPresetActivate)
    bpy.utils.register_class(ScriptShortcutPresetsMenuEdit)
    bpy.utils.register_class(ScriptShortcutPresetAdd)
    bpy.utils.register_class(ScriptShortcutPresetRemove)
    bpy.utils.register_class(ScriptShortcutPresetRename)
    #bpy.utils.register_class(ScriptShortcutPanelTemplate)
    bpy.utils.register_class(ScriptShortcutPanelView3d)
    bpy.utils.register_class(ScriptShortcutPanelGraphEditor)
    bpy.utils.register_class(ScriptShortcutPanelNLAEditor)
    bpy.utils.register_class(ScriptShortcutPanelImageEditor)
    bpy.utils.register_class(ScriptShortcutPanelSequenceEditor)
    bpy.utils.register_class(ScriptShortcutPanelClipEditor)
    bpy.utils.register_class(ScriptShortcutPanelTextEditor)
    bpy.utils.register_class(ScriptShortcutPanelNodeEditor)
    bpy.utils.register_class(ScriptShortcutPanelLogicEditor)
    
    keymaps = bpy.context.window_manager.keyconfigs.addon.keymaps
    keymap = keymaps.new(name='Window', region_type='WINDOW', space_type='EMPTY')
    addon_keymaps.append(keymap)
    keymapitem = keymap.keymap_items.new('wm.call_menu', 'SPACE', 'PRESS', ctrl=True, shift=True)
    keymapitem.properties.name = 'scriptshortcut.popup'

    bpy.types.Scene.scriptshortcuts = bpy.props.PointerProperty(type=ScriptShortcutPanels)


def unregister():
    bpy.utils.unregister_class(ScriptShortcutSettings)
    bpy.utils.unregister_class(ScriptShortcutPanelButton)
    bpy.utils.unregister_class(ScriptShortcutPanel)
    bpy.utils.unregister_class(ScriptShortcutPanels)
    bpy.utils.unregister_class(ScriptShortcutSave)
    bpy.utils.unregister_class(ScriptShortcutLoad)
    bpy.utils.unregister_class(ScriptShortcutClear)
    bpy.utils.unregister_class(ScriptShortcutMove)
    bpy.utils.unregister_class(ScriptShortcutRun)
    bpy.utils.unregister_class(ScriptShortcutRename)
    bpy.utils.unregister_class(ScriptShortcutChangeScript)
    bpy.utils.unregister_class(ScriptShortcutAdd)
    bpy.utils.unregister_class(ScriptShortcutSelectScript)
    bpy.utils.unregister_class(ScriptShortcutRemove)
    bpy.utils.unregister_class(ScriptShortcutPopup)
    bpy.utils.unregister_class(ScriptShortcutPresetsMenu)
    bpy.utils.unregister_class(ScriptShortcutPresetActivate)
    bpy.utils.unregister_class(ScriptShortcutPresetsMenuEdit)
    bpy.utils.unregister_class(ScriptShortcutPresetAdd)
    bpy.utils.unregister_class(ScriptShortcutPresetRemove)
    bpy.utils.unregister_class(ScriptShortcutPresetRename)
    #bpy.utils.unregister_class(ScriptShortcutPanelTemplate)
    bpy.utils.unregister_class(ScriptShortcutPanelView3d)
    bpy.utils.unregister_class(ScriptShortcutPanelGraphEditor)
    bpy.utils.unregister_class(ScriptShortcutPanelNLAEditor)
    bpy.utils.unregister_class(ScriptShortcutPanelImageEditor)
    bpy.utils.unregister_class(ScriptShortcutPanelSequenceEditor)
    bpy.utils.unregister_class(ScriptShortcutPanelClipEditor)
    bpy.utils.unregister_class(ScriptShortcutPanelTextEditor)
    bpy.utils.unregister_class(ScriptShortcutPanelNodeEditor)
    bpy.utils.unregister_class(ScriptShortcutPanelLogicEditor)

    for keymap in addon_keymaps:
        bpy.context.window_manager.keyconfigs.addon.keymaps.remove(keymap)

if __name__ == "__main__":
    register()
