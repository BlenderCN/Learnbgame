import shlex

class OSOInstruction():
    def __init__(self, line, tag):
        tokens = shlex.split(line)
        tokens = [word for word in tokens if not word.startswith('%meta')]
        self.Opcode = tokens[0]
        self.Tag = tag
        self.Hints = []
        self.Parameters = []
        for id in range(1, len(tokens)):
            if tokens[id][0] is '%':
                self.Hints.extend([tokens[id]])
            else:
                self.Parameters.extend([tokens[id]])

    def Opcode(self):
        return self.Opcode

    def Tag(self):
        return self.Tag

    def Hints(self):
        return self.Hints

    def Parameters(self):
        return self.Parameters

    def __repr__(self):
        return "Instruction: %s(%s)" % (self.Opcode, self.Parameters)
