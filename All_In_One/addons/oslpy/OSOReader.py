import shlex
from .OSOVariable import OSOVariable
from .OSOInstruction import OSOInstruction
from enum import Enum
from .Opcodes import *


class ParserState(Enum):
    WaitVersion = 1
    WaitVariablesAndCode = 2
    WaitCode = 3


class OSOReader():
    def __init__(self, filename):
        self.FileName = filename
        self.ParserState = ParserState.WaitVersion
        self.Variables = []
        self.Instructions = []
        self.CurrentTag = ""
        self.ShaderName = "Unknown"
        # all indexes are 1 based, so add a nop to line everything up nicely
        inst = OSOInstruction("nop", self.CurrentTag)
        self.Instructions.append(inst)

    def HandleVersion(self, line):
        tokens = shlex.split(line)
        if tokens[0] == 'OpenShadingLanguage':
            self.Version = tokens[1]
            self.ParserState = ParserState.WaitVariablesAndCode
            return True
        return False

    def HandleCode(self, line):
        tokens = shlex.split(line)
        tokens = [word for word in tokens if not word.startswith('%meta')]

        if tokens[0] == 'code':
            self.CurrentTag = tokens[1]
        else:
            inst = OSOInstruction(line, self.CurrentTag)
            self.Instructions.append(inst)
        return True

    def HandleVariablesAndCode(self, line):
        tokens = shlex.split(line)
        tokens = [word for word in tokens if not word.startswith('%meta')]

        if tokens[0] == 'code':
            self.ParserState = ParserState.WaitCode
            return self.HandleCode(line)

        if tokens[0] == 'shader':
            if len(tokens) == 2:
                self.ShaderName = tokens[1]
                return True
            else:
                return False

        filterWords = ['param', 'oparam', 'global', 'local', 'const', 'temp']
        if tokens[0] in filterWords:
            var = OSOVariable(line)
            self.Variables.append(var)
            return True

        return False

    def HandleLine(self, line):
        if self.ParserState is ParserState.WaitVersion:
            return self.HandleVersion(line)
        elif self.ParserState is ParserState.WaitVariablesAndCode:
            return self.HandleVariablesAndCode(line)
        elif self.ParserState is ParserState.WaitCode:
            return self.HandleCode(line)
        return True

    def Load(self):
        file = open(self.FileName, 'r')
        for line in file:
            if line[0] is not '#':
                if self.HandleLine(line) is False:
                    return False
        return True

    def GetVariable(self, name):
        for var in self.Variables:
            if var.Name == name:
                return var
        return None

    def MakeOpcode(self, index):
        className = "Opcode_" + self.Instructions[index].Opcode
        if (className in globals()):
            classType = globals()[className]
            instance = classType(self, index)
            return instance
        else:
            raise ValueError(str('Unsupported opcode %s' %
                                 self.Instructions[index].Opcode))

    def __repr__(self):
        return "OSO> Shader:%s instructions:%s variables:%s" % (
            self.ShaderName,
            len(self.Instructions),
            len(self.Variables))
