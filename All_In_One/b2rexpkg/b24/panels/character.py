"""
Main b2rex character application class
"""

import os
import tempfile, shutil
import traceback
import b2rexpkg
from b2rexpkg.tools.selectable import SelectablePack, SelectableRegion

import Blender

from b2rexpkg.charexporter import CharacterExporter
from b2rexpkg.b24.charsettings import CharacterSettings

from ogredotscene import Screen, HorizontalLayout
from ogredotscene import NumberView, Widget, CheckBox
from ogredotscene import VerticalLayout, Action, QuitButton
from ogredotscene import StringButton, Label, Button, Box
from ogredotscene import Selectable, SelectableLabel

ERROR = 0
OK = 1
IMMEDIATE = 2

class RealxtendCharacterApplication(CharacterExporter):
    def __init__(self):
        CharacterExporter.__init__(self)
        self.buttons = {}
        self.screen = Screen()
        self.exportSettings = CharacterSettings()
        self.settings_visible = False
        self.region_uuid = ''
        self.regionLayout = None
        self.initGui()
        self.addStatus("b2rex started")

    def initGui(self):
        """
        Initialize the interface system.
        """
        self.vLayout = VerticalLayout()
        self.buttonLayout = HorizontalLayout()
        #self.addButton('Connect', self.buttonLayout, 'Connect to opensim server. Needed if you want to upload worlds directly.')
        self.addButton('Export', self.buttonLayout, 'Export to disk')
        self.addButton('Quit', self.buttonLayout, 'Quit the exporter')
        settingsButton = CheckBox(RealxtendCharacterApplication.ToggleSettingsAction(self),
			          self.settings_visible,
				  'Settings',
				  [100, 20],
				  tooltip='Show Settings')
        self.buttonLayout.addWidget(settingsButton, 'SettingsButton')
        self.vLayout.addWidget(self.buttonLayout, 'buttonPanel')
        self.screen.addWidget(Box(self.vLayout, 'realXtend character exporter'), "layout")

    def showSettings(self):
        """
        Create the settings widgets.
        """
        self.settingsLayout = VerticalLayout()
        self.vLayout.addWidget(self.settingsLayout, 'settingsLayout')
        #self.addSettingsButton('pack', self.settingsLayout, 'name for the main world files')
        self.addSettingsButton('path', self.settingsLayout, 'path to export to')
        #self.addSettingsButton('server_url', self.settingsLayout, 'server login url')
        properties = self.exportSettings.getProperties()
        for prop in properties.keys():
            self.addSettingsButton(prop, self.settingsLayout, properties[prop])
            #posControls = HorizontalLayout()
            #uuidControls = HorizontalLayout()
        #self.settingsLayout.addWidget(posControls, 'posControls')
        #self.settingsLayout.addWidget(uuidControls, 'uuidControls')
        #posControls.addWidget(NumberView('OffsetX:', self.exportSettings.locX, [100, 20], [Widget.INFINITY, 20], 
        #    tooltip='Additional offset on the x axis.'), 'locX')
        #posControls.addWidget(NumberView('OffsetY:', self.exportSettings.locY, [100, 20], [Widget.INFINITY, 20], 
        #    tooltip='Additional offset on the y axis.'), 'locY')
        #posControls.addWidget(NumberView('OffsetZ:', self.exportSettings.locZ, [100, 20], [Widget.INFINITY, 20], 
        #    tooltip='Additional offset on the z axis.'), 'locZ')
        #for objtype in ['Objects', 'Meshes', 'Materials', 'Textures']:
            #    keyName = 'regen' + objtype
            #settingToggle = CheckBox(RealxtendCharacterApplication.ToggleSettingAction(self, objtype),
            #		          getattr(self.exportSettings, keyName),
            #			  'Regen ' + objtype,
            #			  [100, 20],
            #			  tooltip='Regenerate uuids for ' + objtype)
            #uuidControls.addWidget(settingToggle, keyName)
 
    def toggleSettings(self):
        """
        Toggle the settings widget.
        """
        if self.settings_visible:
            self.vLayout.removeWidget('settingsLayout')
            self.settings_visible = False
        else:
            self.showSettings()
            self.settings_visible = True

    def setRegion(self, region_uuid):
        """
        Set the selected region.
        """
        if not self.region_uuid:
            # setting for the first time
            hLayout = HorizontalLayout()
            self.regionLayout.addWidget(hLayout, "regionButtons")
            self.addButton("ExportUpload", hLayout, 'Export scene and upload to opensim region')
            self.addButton("Upload", hLayout, 'Upload previously exported scene')
            self.addButton("Clear", hLayout, 'Clear the selected region in the opensim server')
        self.region_uuid = region_uuid
        self.addStatus("Region set to " + region_uuid)

    def addStatus(self, text, level = OK):
        """
        Add status information.
        """
        self.screen.addWidget(Box(Label(text), 'status'), 'b2rex initialized')
        if level in [ERROR, IMMEDIATE]:
            # Force a redraw
            Blender.Draw.Draw()
        else:
            Blender.Draw.Redraw(1)

    def addSettingsButton(self, button_name, layout, tooltip=""):
        """
        Create a settings string button.
        """
        val = getattr(self.exportSettings, button_name)
        self.buttons[button_name] = StringButton(val,
                                    RealxtendCharacterApplication.ChangeSettingAction(self,
                                                                                     button_name),
                                                 button_name+": ", [200, 20], tooltip)
        layout.addWidget(self.buttons[button_name], 'buttonPanelButton' + button_name)

    def addButton(self, button_name, layout, tooltip=""):
        """
        Add a button to the interface. This function prelinks
        the button to an action on this clss.
        """
        action = getattr(RealxtendCharacterApplication, button_name + 'Action')
        return layout.addWidget(Button(action(self),
                           button_name, [100, 20], tooltip),
                           button_name + 'Button')

    def go(self):
        """
        Start the ogre interface system
        """
        self.screen.activate()

    def packTo(self, from_path, to_zip):
        """
        Pack a directory to a file.
        """
        import zipfile
        zfile = zipfile.ZipFile(to_zip, "w", zipfile.ZIP_DEFLATED)
        for dirpath, dirnames, filenames in os.walk(from_path):
            for name in filenames:
                file_path = os.path.join(dirpath,  name)
                zfile.write(file_path, file_path[len(from_path+"/"):])
        zfile.close()

    def addRegionsPanel(self, regions, griddata):
        """
        Show available regions
        """
        vLayout = VerticalLayout()
        self.regionLayout = vLayout
        title = griddata['gridname'] + ' (' + griddata['mode'] + ')'
        vLayout.addWidget(Label(title), 'scene_key_title')
        self.screen.addWidget(Box(vLayout, griddata['gridnick']), "layout2")
        pack = SelectablePack()
        for key, region in regions.iteritems():
             selectable = SelectableRegion(0, region["id"], self, pack)
             label_text = region["name"] + " (" + str(region["x"]) + "," + str(region["y"]) + ")"
             vLayout.addWidget(SelectableLabel(selectable, region['name']),'region_'+key)
        return griddata

    def clearAction(self):
        """
        Clear Action
        """
        base_url = self.exportSettings.server_url
        pack_name = self.exportSettings.pack
        if not self.region_uuid:
            self.addStatus("No region selected ")
            return
        self.sim.sceneClear(self.region_uuid, pack_name)
        self.addStatus("Scene cleared " + self.region_uuid)

    def uploadAction(self):
        """
        Upload Action
        """
        base_url = self.exportSettings.server_url
        pack_name = self.exportSettings.pack
        if not self.region_uuid:
            self.addStatus("Error: No region selected ", ERROR)
            return
        self.addStatus("Uploading to " + base_url, IMMEDIATE)
        export_dir = self.getExportDir()
        res = self.sim.sceneUpload(self.region_uuid,
                                                           pack_name,
                                   os.path.join(export_dir, "world_pack.zip"))
        if res.has_key('success') and res['success'] == True:
            self.addStatus("Uploaded to " + base_url)
        else:
            self.addStatus("Error: Something went wrong uploading", ERROR)

    def connectAction(self):
        """
        Connect Action
        """
        base_url = self.exportSettings.server_url
        self.addStatus("Connecting to " + base_url, IMMEDIATE)
        self.connect(base_url)
        self.region_uuid = ''
        self.regionLayout = None
        try:
            regions = self.gridinfo.getRegions()
            griddata = self.gridinfo.getGridInfo()
        except:
            self.addStatus("Error: couldnt connect to " + base_url, ERROR)
            return
        self.addRegionsPanel(regions, griddata)
        # create the regions panel
        self.addStatus("Connected to " + griddata['gridnick'])

    def exportAction(self):
        """
        Export Action
        """
        tempfile.gettempdir()
        base_url = self.exportSettings.server_url
        pack_name = self.exportSettings.pack
        export_dir = self.getExportDir()

        self.addStatus("Exporting to " + export_dir, IMMEDIATE)

        destfolder = os.path.join(export_dir, 'b2rx_export')
        if not os.path.exists(destfolder):
            os.makedirs(destfolder)
        else:
            shutil.rmtree(destfolder)
            os.makedirs(destfolder)

        x = self.exportSettings.locX.getValue()
        y = self.exportSettings.locY.getValue()
        z = self.exportSettings.locZ.getValue()

        self.export(destfolder, pack_name, [x, y, z], self.exportSettings)
        dest_file = os.path.join(export_dir, "world_pack.zip")
        self.packTo(destfolder, dest_file)

        self.addStatus("Exported to " + dest_file)

    def getExportDir(self):
        export_dir = self.exportSettings.path
        if not export_dir:
            export_dir = tempfile.tempdir
        return export_dir

    class ChangeSettingAction(Action):
        """
        Change a setting from the application.
        """
        def __init__(self, app, name):
            self.app = app
            self.name = name
        def execute(self):
            setattr(self.app.exportSettings, self.name,
                    self.app.buttons[self.name].string.val)

    class QuitAction(Action):
        """
        Quit the application.
        """
        def __init__(self, app):
            self.settings = app.exportSettings
        def execute(self):
            import Blender
            self.settings.save()
            Blender.Draw.Exit()

    class ConnectAction(Action):
        """
        Connect to the opensim server.
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            try:
                self.app.connectAction()
	    except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt connect. Check your settings to see they are ok", ERROR)
                return False

    class ToggleSettingsAction(Action):
        """
        Toggle the settings panel.
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            self.app.toggleSettings()

    class ToggleSettingAction(Action):
        """
        Toggle a boolean setting.
        """
        def __init__(self, app, objtype):
            self.app = app
            self.objtype = objtype 

        def execute(self):
            keyName = 'regen' + self.objtype
            setattr(self.app.exportSettings, keyName, not getattr(self.app.exportSettings, keyName))


    class ExportUploadAction(Action):
        """
        Export and upload selected objects.
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            exportAction = RealxtendCharacterApplication.ExportAction(self.app)
            uploadAction = RealxtendCharacterApplication.UploadAction(self.app)
            if not exportAction.execute() == False:
                Blender.Draw.Draw()
                uploadAction.execute()

    class ExportAction(Action):
        """
        Export selected objects.
        """
        def __init__(self, app):
            self.app = app
            return

        def execute(self):
            try:
                self.app.exportAction()
            except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt export", ERROR)
                return False

    class UploadAction(Action):
        """
        Upload a previously exported world.
        """
        def __init__(self, exportSettings):
            self.app = exportSettings

        def execute(self):
            try:
                self.app.uploadAction()
            except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt upload", ERROR)
                return False

    class ClearAction(Action):
        """
        Clear the selected scene.
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            try:
                self.app.clearAction()
            except:
                traceback.print_exc()
                self.app.addStatus("Error: couldnt clear", ERROR)
                return False

