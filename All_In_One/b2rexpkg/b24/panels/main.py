"""
Main b2rex application class
"""

import os
import tempfile, shutil
import b2rexpkg

import Blender

from b2rexpkg.exporter import Exporter
from b2rexpkg.importer import Importer
from b2rexpkg.b24.settings import ExportSettings

from ogredotscene import Screen, HorizontalLayout
from ogredotscene import NumberView, Widget, CheckBox
from ogredotscene import VerticalLayout, Action, QuitButton
from ogredotscene import StringButton, Label, Button, Box

ERROR = 0
OK = 1
IMMEDIATE = 2

from b2rexpkg.compatibility import BaseApplication

class RealxtendExporterApplication(BaseApplication):
    def __init__(self):
        self.region_uuid = ''
        self.regionLayout = None
        BaseApplication.__init__(self)
        self.addStatus("b2rex started")

    def initGui(self, title=None):
        """
        Initialize the interface system.
        """
        if not title:
            title = 'realXtend exporter'
        self.vLayout = VerticalLayout()
        self.buttonLayout = HorizontalLayout()
        self.addCallbackButton('Connect', self.buttonLayout, 'Connect to opensim server. Needed if you want to upload worlds directly.')
        self.addCallbackButton('Export', self.buttonLayout, 'Export to disk')
        self.addButton('Quit', self.buttonLayout, 'Quit the exporter')
        settingsButton = CheckBox(RealxtendExporterApplication.ToggleSettingsAction(self),
			          self.settings_visible,
				  'Settings',
				  [100, 20],
				  tooltip='Show Settings')
        self.buttonLayout.addWidget(settingsButton, 'SettingsButton')
        self.vLayout.addWidget(self.buttonLayout, 'buttonPanel')
        self.screen.addWidget(Box(self.vLayout, 'realXtend exporter'), "layout")

    def showSettings(self):
        """
        Create the settings widgets.
        """
        self.settingsLayout = VerticalLayout()
        self.vLayout.addWidget(self.settingsLayout, 'settingsLayout')
        self.addSettingsButton('pack', self.settingsLayout, 'name for the main world files')
        self.addSettingsButton('path', self.settingsLayout, 'path to export to')
        self.addSettingsButton('server_url', self.settingsLayout, 'server login url')
        self.addSettingsButton('username', self.settingsLayout, 'server login username')
        self.addSettingsButton('password', self.settingsLayout, 'server login password')
        posControls = HorizontalLayout()
        uuidControls = HorizontalLayout()
        self.settingsLayout.addWidget(posControls, 'posControls')
        self.settingsLayout.addWidget(uuidControls, 'uuidControls')
        posControls.addWidget(NumberView('OffsetX:', self.exportSettings.locX, [100, 20], [Widget.INFINITY, 20], 
            tooltip='Additional offset on the x axis.'), 'locX')
        posControls.addWidget(NumberView('OffsetY:', self.exportSettings.locY, [100, 20], [Widget.INFINITY, 20], 
            tooltip='Additional offset on the y axis.'), 'locY')
        posControls.addWidget(NumberView('OffsetZ:', self.exportSettings.locZ, [100, 20], [Widget.INFINITY, 20], 
            tooltip='Additional offset on the z axis.'), 'locZ')
        for objtype in ['Objects', 'Meshes', 'Materials', 'Textures']:
            keyName = 'regen' + objtype
            settingToggle = CheckBox(RealxtendExporterApplication.ToggleSettingAction(self, objtype),
				          getattr(self.exportSettings, keyName),
					  'Regen ' + objtype,
					  [100, 20],
					  tooltip='Regenerate uuids for ' + objtype)
            uuidControls.addWidget(settingToggle, keyName)
 
    def setRegion(self, region_uuid):
        """
        Set the selected region.
        """
        if not self.region_uuid:
            # setting for the first time
            hLayout = HorizontalLayout()
            self.regionLayout.addWidget(hLayout, "regionButtons")
            self.addButton("ExportUpload", hLayout, 'Export scene and upload to opensim region')
            self.addCallbackButton("Upload", hLayout, 'Upload previously exported scene')
            self.addCallbackButton("Clear", hLayout, 'Clear the selected region in the opensim server')
            self.addCallbackButton("Check", hLayout, 'Check blend file against region contents')
            self.addCallbackButton("Sync", hLayout, 'Sync blend file objects from region')
            self.addCallbackButton("Import", hLayout, 'Import all objects from current region')
        self.region_uuid = region_uuid
        self.addStatus("Region set to " + region_uuid)
        self.regionInfoLayout = VerticalLayout()
        self.regionLayout.addWidget(self.regionInfoLayout, "regionInfoLayout")
        self.regionInfoLayout.addWidget(Label(" \n"),
                                        "regionInfoSpace")
        self.regionInfoLayout.addWidget(Label("\n"+region_uuid), "regionInfo")

    def onCheckAction(self):
        """
        Check region contents against server.
        """
        text = self.check_region(self.region_uuid)
        self.regionInfoLayout = VerticalLayout()
        self.regionLayout.addWidget(self.regionInfoLayout, "regionInfoLayout")
        for idx, line in enumerate(text):
            self.regionInfoLayout.addWidget(Label(line),
                                        "regionInfoSpace"+str(idx))
        Blender.Draw.Draw()

    def onSyncAction(self):
        """
        Sync selected region contents against server.
        """
        text = self.sync_region(self.region_uuid)
        Blender.Draw.Draw()

    def onImportAction(self):
        """
        Import region from OpenSim.
        """
        text = self.import_region(self.region_uuid)
        self.addStatus("Scene imported " + self.region_uuid)
        Blender.Draw.Draw()

    def onClearAction(self):
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

    def onUploadAction(self):
        """
        Upload Action
        """
        self.doUpload()

    def onExportAction(self):
        """
        Export Action
        """
        x = self.exportSettings.locX.getValue()
        y = self.exportSettings.locY.getValue()
        z = self.exportSettings.locZ.getValue()

        self.doExport(self.exportSettings, [x, y, z])

    class ExportUploadAction(Action):
        """
        Export and upload selected objects.
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            if not self.app.onExportAction() == False:
                Blender.Draw.Draw()
                self.app.onUploadAction()


