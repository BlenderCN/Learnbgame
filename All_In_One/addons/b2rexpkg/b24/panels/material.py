"""
Material browser application.
"""

import os
import tempfile, shutil
import traceback
import b2rexpkg
from b2rexpkg.tools.selectable import SelectablePack, SelectableRegion

import Blender

from b2rexpkg.exporter import Exporter
from b2rexpkg.b24.settings import ExportSettings

from b2rexpkg.b24.material import RexMaterialExporter

from ogredotscene import Screen, HorizontalLayout
from ogredotscene import NumberView, Widget, CheckBox
from ogredotscene import VerticalLayout, Action, QuitButton
from ogredotscene import StringButton, Label, Button, Box
from ogredotscene import Selectable, SelectableLabel

try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO

ERROR = 0
OK = 1
IMMEDIATE = 2

class RealxtendMaterialBrowser(object):
    def __init__(self):
 #       Exporter.__init__(self)
        self.buttons = {}
        self.screen = Screen()
        self.exportSettings = ExportSettings()
        self.shader_visible = False
        self.region_uuid = ''
        self.regionLayout = None
        self.initGui()
        self.addStatus("b2rex started")

    def createMaterialButtons(self, layout, materialExporter):
        self.matButtonLayout = HorizontalLayout()
        if materialExporter.material:
		autodetect = self.getAutodetect()
                AutodetectButton = CheckBox(RealxtendMaterialBrowser.ToggleAutodetectAction(self),
			          autodetect,
				  'Autodetect',
				  [100, 20],
				  tooltip='Autodetect shader')
		self.matButtonLayout.addWidget(AutodetectButton, 'autodetect_button')
		if not autodetect:
			self.shaderButton = self.addStringButton(materialExporter.getShader() ,'Shader', self.matButtonLayout, 'Shader to use for this material')
		shaderButton = CheckBox(RealxtendMaterialBrowser.ToggleShaderVisibleAction(self),
					  self.shader_visible,
					  'Show Shader',
					  [100, 20],
					  tooltip='Show Shader text')
		self.matButtonLayout.addWidget(shaderButton, 'ShaderButton')

        layout.addWidget(self.matButtonLayout, 'matButtonLayout')

    def parseSelected(self):
        all_selected = Blender.Object.GetSelected()
        if all_selected:
		shaderLayoutBox = VerticalLayout()
		self.shaderLayoutBox = shaderLayoutBox
                colouredAmbient = False
                mesh = all_selected[0].getData(0, True)
		face = mesh.faces[0]
                materialExporter = RexMaterialExporter(self, mesh, face, colouredAmbient)
		self.createMaterialButtons(shaderLayoutBox, materialExporter)
		self.shaderLayout.addWidget(Box(shaderLayoutBox, materialExporter._createName()), 'shaderBox')
		lineWidget = Label("")
		shaderLayoutBox.addWidget(lineWidget, 'lineShader3')
		lineWidget = Label("Shader: "+materialExporter.shader)
		shaderLayoutBox.addWidget(lineWidget, 'lineShader')
		if self.shader_visible:
			self.showShader()

                Blender.Draw.Draw()

    def registerTextureImage(self, bimage):
	# to fake the texture manager
	return os.path.basename(bimage.filename)

    def initGui(self):
        """
        Initialize the interface system.
        """
        self.vLayout = VerticalLayout()
        self.shaderLayout = VerticalLayout()
        self.buttonLayout = HorizontalLayout()
        #self.addButton('Connect', self.buttonLayout, 'Connect to opensim server. Needed if you want to upload worlds directly.')
        self.addButton('Refresh', self.buttonLayout, 'Export to disk')
        self.addButton('Quit', self.buttonLayout, 'Quit the exporter')
        self.vLayout.addWidget(self.buttonLayout, 'buttonPanel')
        self.screen.addWidget(Box(self.vLayout, 'b2rex material browser'), "layout")
        self.screen.addWidget(self.shaderLayout, "shaderLayout")

    def showShader(self):
        """
        Show the shader text
	"""
        materialExporter = self.getMaterialExporter()
	shaderText = VerticalLayout()
	lineWidget = Label("")
	shaderText.addWidget(lineWidget, 'lineShader2')
	f = StringIO()
	materialExporter.writeTechniques(f)
	rexMaterial = f.getvalue()
	for idx, line in enumerate(rexMaterial.split('\n')):
		color = [0,0,0]
		if "program_ref" in line:
		    color = [0.2, 0.2, 0.8]
		if "texture_unit" in line:
		    color = [0.2, 0.5, 0.2]
		lineWidget = Label(line, 'small', color)
		shaderText.addWidget(lineWidget, 'line'+str(idx))
	
	self.shaderLayoutBox.addWidget(shaderText, 'shaderText')

    def setShader(self, value):
	materialExporter = self.getMaterialExporter()
	materialExporter.setShader(value)
	self.parseSelected()

    def toggleAutodetect(self):
	materialExporter = self.getMaterialExporter()
	materialExporter.toggleAutodetect()
	# XXX update interface
	self.parseSelected()
	#self.createMaterialButtons(self.shaderLayoutBox, materialExporter)

    def getAutodetect(self):
	materialExporter = self.getMaterialExporter()
	return materialExporter.getAutodetect()

    def getMaterialExporter(self, obj=None):
	if not obj:
		obj = self.getSelected()
	if not obj:
		return
	mesh = obj.getData(0, True)
	face = mesh.faces[0]
	colouredAmbient = False
        materialExporter = RexMaterialExporter(self, mesh, face, colouredAmbient)
	return materialExporter

    def getSelected(self):
        objs = Blender.Object.GetSelected()
	if not objs:
		return
        obj = objs[0]
        return obj

    def toggleShaderVisible(self):
        """
        Toggle the settings widget.
        """
        if self.shader_visible:
            self.shaderLayoutBox.removeWidget('shaderText')
            self.shader_visible = False
        else:
            self.showShader()
            self.shader_visible = True

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

    def addStringButton(self, value, button_name, layout, tooltip=""):
        """
        Add a button to the interface. This function prelinks
        the button to an action on this clss.
        """
        action = getattr(RealxtendMaterialBrowser, button_name + 'Action')
        button = StringButton(value, action(self),
			button_name+": ", [100, 20], tooltip)
        layout.addWidget(button, button_name + 'Button')
	return button

    def addButton(self, button_name, layout, tooltip=""):
        """
        Add a button to the interface. This function prelinks
        the button to an action on this clss.
        """
        action = getattr(RealxtendMaterialBrowser, button_name + 'Action')
        return layout.addWidget(Button(action(self),
                           button_name, [100, 20], tooltip),
                           button_name + 'Button')

    def go(self):
        """
        Start the ogre interface system
        """
        self.screen.activate()

    class RefreshAction(Action):
        """
        Refresh the material view
        """
        def __init__(self, app):
            self.app = app
        def execute(self):
            import Blender
 #           self.app.settings.save()
	    self.app.parseSelected()

    class ToggleAutodetectAction(Action):
        """
        Refresh the material view
        """
        def __init__(self, app):
            self.app = app
        def execute(self):
            import Blender
 #           self.app.settings.save()
	    self.app.toggleAutodetect()

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

    class ToggleShaderVisibleAction(Action):
        """
        Toggle the shader text
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            self.app.toggleShaderVisible()

    class ShaderAction(Action):
        """
        Change the shader on the material
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            button = self.app.shaderButton
	    self.app.setShader(button.string.val)


