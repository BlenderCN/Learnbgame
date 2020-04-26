"""
 Base class for editsync modules.
"""

import bpy

class SyncModule(object):
    _expand = False
    def __init__(self, parent):
        self._parent = parent
    def getName(self):
        """
        Return the name under which this handler should be registered.
        """
        return self.__class__.__name__.replace("Module", "")

    def getPanelName(self):
        """
        Return the name under which this handlers panel should be registered.
        """
        return self.getName()

    def register_property(self, origcls, prop, destcls):
        """
        Register a property with an editor model
        """
        setattr(origcls, prop, bpy.props.PointerProperty(type=destcls))

    def unregister_property(self, origcls, prop):
        """
        Unregister a property from an editor model
        """
        delattr(origcls, prop)

    def setProperties(self, props):
        """
        Called when setting the module properties
        """
        self._props = props
    def onToggleRt(self, enabled):
        """
        Called when agent is enabled or disabled.
        """
        self._props = self._parent.exportSettings
        if enabled:
            self.simrt = self._parent.simrt
            self.workpool = self._parent.workpool
        else:
            self.simrt = None
            self.workpool = None
    def register(self, parent):
        """
        Called when the module is registered with the system.
        """
        pass
    def unregister(self, parent):
        """
        Called when the module is unregistered from the system:
        """
        pass
    def expand(self, box, icons=['TRIA_DOWN', 'TRIA_RIGHT'], title=None):
        if not title:
            title = self.getPanelName()
        if self._expand:
            icon=icons[0]
            box.operator('b2rex.section', icon=icon,
                         text=title,
                     emboss=True).section = self.getName()
        else:
            icon=icons[1]
            box.operator("b2rex.section", icon=icon,
                         text=title,
                     emboss=True).section = self.getName()
        return self._expand

    """
    The following can be defined for getting called in specific
    moments.

    def draw(self, layout, editor, props):
    def draw_object(self, layout, editor, obj):
    def check(self, starttime, budget):
    """

