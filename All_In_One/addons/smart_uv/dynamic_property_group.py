import bpy

class _DPGVars:
    uid = 0
    instances = {}

    @staticmethod
    def get(item):
        if not item.name:
            _DPGVars.uid += 1
            item.name = str(_DPGVars.uid)

        if item.name not in _DPGVars.instances:
            _DPGVars.instances[item.name] = _DPGVars()

        return _DPGVars.instances[item.name]


class DynamicPropertyGroup(bpy.types.PropertyGroup):

    def delvar(self, var):
        dpgvars = _DPGVars.get(self)
        del dpgvars[var]

    def getvar(self, var):
        dpgvars = _DPGVars.get(self)
        return getattr(dpgvars, var)

    def hasvar(self, var):
        if not self.name or self.name not in _DPGVars.instances:
            return False
        dpgvars = _DPGVars.get(self)
        return hasattr(dpgvars, var)

    def setvar(self, var, value):
        dpgvars = _DPGVars.get(self)
        setattr(dpgvars, var, value)
        return getattr(dpgvars, var)
