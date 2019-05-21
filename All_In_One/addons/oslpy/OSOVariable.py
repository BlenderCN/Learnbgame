import shlex 
class OSOVariable():
    def __init__(self, line):
        tokens = shlex.split(line)
        idx = 2
        if len(tokens) > 2:
            self.InitVar =  ""
            self.defaults = []
            self.varType = tokens[0]
            self.dataType = tokens[1]
            if self.dataType == 'closure' and tokens[2] == 'color':
                self.Type = 'closure color'
                idx = 3
            self.Name = tokens[idx]
            # if '[' in self.dataType:
            #    raise ValueError('Arrays are not supported')
            for id in range(idx + 1, len(tokens)):
                if tokens[id][0] is not '%':
                    self.defaults.extend([tokens[id]])

    def IsArray(self):
        return '[' in self.dataType

    def IsConst(self):
        return self.varType == 'const'

    def IsPointLike(self):
        return self.dataType in ['point', 'vector', 'normal', 'color']

    def IsColor(self):
        return self.dataType == 'color'

    def IsFloat(self):
        return self.dataType == 'float'

    def IsInt(self):
        return self.dataType == 'int'

    def IsNumeric(self):
        return self.IsFloat() or self.IsInt()

    def Name(self):
        return self.Name

    def InitVar(self):
        return self.InitVar


    def dataType(self):
        return self.dataType

    def defaults(self):
        return self.defaults

    def GetNodeType(self):
        if "oslpy_has" in self.Name:
            return "NodeSocketFloatFactor"
        if self.IsFloat():
            return "NodeSocketFloat"
        if self.IsInt():
            return "NodeSocketInt"
        if self.IsColor():
            return "NodeSocketColor"
        if self.IsPointLike():
            return "NodeSocketVector"
        return "**FIXME**"

    def __repr__(self):
        return "Variable: %s %s(%s)" % (self.varType, self.Name, self.defaults)
