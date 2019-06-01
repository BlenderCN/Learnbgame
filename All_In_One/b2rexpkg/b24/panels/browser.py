"""
Region asset browser.
"""

from b2rexpkg.compatibility import BaseApplication
from b2rexpkg.baseapp import HorizontalLayout, Box, Label, VerticalLayout
from b2rexpkg.baseapp import IMMEDIATE

from b2rexpkg.tools.simconnection import SimConnection
from b2rexpkg.importer import Importer

import Blender

class RealxtendBrowserApplication(BaseApplication):
    def __init__(self):
        BaseApplication.__init__(self, "RealXtend Browser")
        self.addStatus("b2rex started")

    def setRegion(self, regionuuid):
        """
        Region set from the interface.
        """
        self.region_uuid = regionuuid
        hLayout = HorizontalLayout()
        vLayout = VerticalLayout()
        vLayout.addWidget(hLayout, "browser_vertical")
        #self.regionLayout = vLayout
        #title = griddata['gridname'] + ' (' + griddata['mode'] + ')'
        #vLayout.addWidget(Label(title), 'scene_key_title')
        self.screen.addWidget(Box(vLayout, "Browser"), "browser")
        self.addCallbackButton('Previous', hLayout, 'Previous object.')
        self.addCallbackButton('Next', hLayout, 'Next object.')
        vLayout.addWidget(Label('-'), "browser_spacing")
        vLayout.addWidget(Label("press next to start"), "browser_info")
        self.setScene()
        self.browserButtonsLayout = hLayout
        self.browserButtonsLayout.addWidget(Label(" 0/?"), "browser-counter")
        self.browserLayout = vLayout
        self.browserInitialized = False

    def setScene(self):
        """
        Go to the browser scene, and create it if necessary.
        """
        try:
            self.scene = Blender.Scene.Get("b2rexbrowser")
        except:
            self.scene = Blender.Scene.New("b2rexbrowser")
        self.scene.makeCurrent()

    def clearScene(self):
        """
        Clear the browser scene.
        """
        for obj in list(self.scene.objects):
            self.scene.unlink(obj)

    def initializeBrowser(self):
        """
        Initialize the browser for a region.
        """
        self.importer = Importer(self.gridinfo)
        con = SimConnection()
        con.connect(self.gridinfo._url)
        region_id = self.region_uuid
        scenedata = con._con.ogrescene_list({"RegionID":region_id})
        self.scenedata = scenedata['res']
        self.browserkeys = self.scenedata.keys()
        self.browserIdx = -1
        self.browserInitialized = True

    def loadGroup(self, name, group, load_materials=False):
        """
        Load a group for viewing.
        """
        self.setScene()
        self.clearScene()
        outLayout = VerticalLayout()
        outLayout.addWidget(Label("uuid: " + str(name)), "browser_lineX")
        for idx, key in enumerate(["name", "owner", "asset",
                                   "materials"]):
            outLayout.addWidget(Label(key + ": " + str(group[key])), "browser_line"+str(idx))
        self.addCallbackButton('Load Material', self.browserButtonsLayout, 'Next object.')
        self.browserLayout.addWidget(outLayout, "browser_info")
        self.importer.init_structures()
        obj = self.importer.import_group(name, group, 10,
                                         load_materials=load_materials)
        if obj:
           obj.setLocation(0.0,0.0,0.0)
           obj.select(True)

    def onLoadMaterialAction(self):
        """
        Load the material for current object.
        """
        self.loadGroupIdx("texture", True)

    def onNextAction(self):
        """
        Load the next object in the region.
        """
        if not self.browserInitialized:
            self.initializeBrowser()
        self.browserIdx += 1
        self.loadGroupIdx("previous")

    def onPreviousAction(self):
        """
        Load the previous object in the region.
        """
        if not self.browserInitialized:
            self.initializeBrowser()
        self.browserIdx -= 1
        self.loadGroupIdx("next")

    def loadGroupIdx(self, comment, load_materials=False):
        """
        Load the current object from the region.
        """
        self.browserIdx = self.browserIdx % len(self.browserkeys)
        name = self.browserkeys[self.browserIdx]
        group = self.scenedata[name]
        self.browserButtonsLayout.addWidget(Label(" %s/%s "%(self.browserIdx+1,
                                                           len(self.browserkeys))),
                                           "browser-counter")
        self.addStatus("loading "+comment, IMMEDIATE)
        try:
            self.loadGroup(name, group, load_materials)
            self.addStatus("loaded "+comment)
        except Exception as e:
            self.addStatus("error loading "+comment+": "+str(e))


