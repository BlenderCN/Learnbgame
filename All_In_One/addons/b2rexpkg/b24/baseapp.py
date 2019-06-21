import traceback

from .settings import ExportSettings
from .editor import EditorObject
from b2rexpkg.tools.siminfo import GridInfo
from b2rexpkg.tools.selectable import SelectablePack, SelectableRegion

from ogredotscene import Screen, HorizontalLayout
from ogredotscene import NumberView, Widget, CheckBox
from ogredotscene import VerticalLayout, Action, QuitButton, Button
from ogredotscene import StringButton, Label, Button, Box
from ogredotscene import SelectableLabel

import Blender

eventlet_present = False
try:
    import eventlet
    from b2rexpkg import simrt
    eventlet_present = True
except:
    pass

import logging
logger = logging.getLogger('b2rex.baseapp')

from b2rexpkg.baseapp import BaseApplication
from b2rexpkg import IMMEDIATE, OK, ERROR

class Base24Application(Screen, BaseApplication):
    def __init__(self, title="RealXtend"):
        Screen.__init__(self)
        self.exportSettings = ExportSettings()
        BaseApplication.__init__(self, title)
        self.initGui(title)
        self.addStatus("b2rex started")

    def initGui(self, title):
        """
        Initialize the interface system.
        """
        self.vLayout = VerticalLayout()
        self.buttonLayout = HorizontalLayout()
        self.addCallbackButton('Connect', self.buttonLayout, 'Connect to opensim server. Needed if you want to upload worlds directly.')
        #self.addButton('Export', self.buttonLayout, 'Export to disk')
        self.addButton('Quit', self.buttonLayout, 'Quit the exporter')
        self.vLayout.addWidget(self.buttonLayout, 'buttonPanel')
        self.screen.addWidget(Box(self.vLayout, title), "layout")

        settingsButton = CheckBox(self.ToggleSettingsAction(self),
			          self.settings_visible,
				  'Settings',
				  [100, 20],
				  tooltip='Show Settings')
        self.buttonLayout.addWidget(settingsButton, 'SettingsButton')

    def addSettingsButton(self, button_name, layout, tooltip=""):
        """
        Create a settings string button.
        """
        val = getattr(self.exportSettings, button_name)
        self.buttons[button_name] = StringButton(val,
                                                 self.ChangeSettingAction(self, button_name),
                                                 button_name+": ", [200, 20], tooltip)
        layout.addWidget(self.buttons[button_name], 'buttonPanelButton' + button_name)

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
            settingToggle = CheckBox(self.ToggleSettingAction(self, objtype),
				          getattr(self.exportSettings, keyName),
					  'Regen ' + objtype,
					  [100, 20],
					  tooltip='Regenerate uuids for ' + objtype)
            uuidControls.addWidget(settingToggle, keyName)

    def _draw(self):
        Screen._draw(self)
        if self.rt_on:
            self.processUpdates()
            Blender.Window.QAdd(Blender.Window.GetAreaID(),Blender.Draw.REDRAW,0,1)

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

    def addRtCheckBox(self):
        rtButton = CheckBox(self.CallbackAction(self.onToggleRt),
			          self.rt_on,
				  'RT',
				  [20, 20],
				  tooltip='Toggle real time connection')
        self.buttonLayout.addWidget(rtButton, 'RtButton')

    def queueRedraw(self, pars=None, immediate=False):
        if pars:
            Blender.Window.Redraw(Blender.Window.Types[pars])
        elif immediate:
            Blender.Window.QRedrawAll()
        else:
            info = Blender.Window.GetScreenInfo()
            for win in info:
                Blender.Window.QAdd(win['id'], Blender.Draw.REDRAW,0,1)

    def addCallbackButton(self, button_name, layout, tooltip=""):
        """
        Add a button to the interface. This function prelinks
        the button to a function in the class, called like
        "on" + button_name + "Action"
        """
        cb = getattr(self, 'on' + button_name.replace(" ", "") + 'Action')
        return layout.addWidget(Button(self.CallbackAction(cb),
                           button_name, [100, 20], tooltip),
                           button_name + 'Button')


    def addButton(self, button_name, layout, tooltip=""):
        """
        Add a button to the interface. This function prelinks
        the button to an action on this clss.
        """
        action = getattr(self, button_name + 'Action')
        return layout.addWidget(Button(action(self),
                           button_name, [100, 20], tooltip),
                           button_name + 'Button')

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
            self.app.exportSettings.save()

    class ToggleSettingsAction(Action):
        """
        Toggle the settings panel.
        """
        def __init__(self, app):
            self.app = app

        def execute(self):
            self.app.toggleSettings()

    class CallbackAction(Action):
        """
        Connect to the opensim server.
        """
        def __init__(self, cb):
            self.cb = cb

        def execute(self):
            try:
                self.cb()
	    except:
                traceback.print_exc()
                logger.error("Error: couldnt rum. Check your settings to see they are ok")
                return False

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

    def _processPosCommand(self, obj, objId, pos):
        self.apply_position(obj, pos)
        self.positions[str(objId)] = list(obj.getLocation())
        self.queueRedraw()

    def _processScaleCommand(self, obj, objId, scale):
        prev_scale = list(obj.getSize())
        if not prev_scale == scale:
            obj.setSize(*scale)
            self.scales[str(objId)] = list(obj.getSize())
            self.queueRedraw()

    def _processRotCommand(self, obj, objId, rot):
        self.apply_rotation(obj, rot)
        self.rotations[str(objId)] = list(obj.getEuler())
        self.queueRedraw()

    def getObjectProperties(self, obj):
        pos = list(obj.getLocation())
        rot = list(obj.getEuler())
        scale = list(obj.getSize())
        return pos, rot, scale



