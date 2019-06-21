# Scene parser ===================================================================================

TABSIZE = 4

def lineIndentTabs(l):
    count = 0
    for c in l:
        if c == ' ':
            count += 1
        else:
            break
    if (count % TABSIZE) != 0:
        return 0
    return count / TABSIZE

def indentBy(l, levels):
    idt = ""
    for i in range(TABSIZE * levels):
        idt += " "
    return idt + l

# A block is a collection of lines part of a logical block,
# for example in MakeNamedMaterial or in AttributeBegin
class SceneBlock():

    def __init__(self, lines):
        self.lines = lines

    # Returns the string representation for writing to file
    # There is no trailing \n
    def toString(self):
        return "\n".join(self.lines)

    # Returns None if this type of block is not recognized
    def getBlockType(self):
        if len(self.lines) == 0:
            return None
        first = self.lines[0]
        splt = first.split(" ")
        if len(splt) != 0:
            return splt[0]
        else:
            return None

    # Replaces a line content
    # if the line is at the specified <level> of indentation
    # and if it starts with <startMatch>
    def replaceLine(self, level, startMatch, newStr):
        for i in range(len(self.lines)):
            l = self.lines[i]
            if lineIndentTabs(l) == level:
                rawLine = l[(TABSIZE * level):]
                if rawLine.startswith(startMatch):
                    transformedLine = indentBy(newStr, level)
                    self.lines[i] = transformedLine

    # Matching function
    def contains(self, level, startMatch):
        for i in range(len(self.lines)):
            l = self.lines[i]
            if lineIndentTabs(l) == level:
                rawLine = l[(TABSIZE * level):]
                if rawLine.startswith(startMatch):
                    return True
        return False

    def findLine(self, level, startMatch):
        for i in range(len(self.lines)):
            l = self.lines[i]
            if lineIndentTabs(l) == level:
                rawLine = l[(TABSIZE * level):]
                if rawLine.startswith(startMatch):
                    return rawLine
        return None

    # Finds AttributeBegin->AreaLightSource blocks
    def isAreaLightSource(self):
        return (self.getBlockType() == "AttributeBegin") and (self.contains(1, "AreaLightSource"))

    def isMakeNamedMaterial(self):
        return self.getBlockType() == "MakeNamedMaterial"

    def getMaterialDefinitionName(self):
        first = self.lines[0].rstrip()
        splt = first.split(" ")
        return " ".join(splt[1:]).replace('"', '')

    def clearBody(self):
        if len(self.lines) >= 1:
            self.lines = self.lines[0:1]
    
    def clearAll(self):
        self.lines = []

    def getAssignedMaterial(self):
        if self.getBlockType() == "AttributeBegin":
            line = self.findLine(1, "NamedMaterial")
            splt = line.split(" ")
            if len(splt) > 0:
                selection = splt[1:]
                return " ".join(selection).replace('"', '')
            else:
                return None
        else:
            return None

    def appendLine(self, level, content):
        self.lines.append(indentBy(content, level))

    def addBeginning(self, level, content):
        newLine = indentBy(content, level)
        self.lines = [newLine] + self.lines

# Represents the entire parsed scenefile
class SceneDocument():

    def __init__(self):
        self.blocks = []

    def parse(self, filepath):
        f = open(filepath, "r")

        sceneBlocks = []
        currentBlock = []

        for line in f:
            line = line[:-1]
            if lineIndentTabs(line) > 0:
                currentBlock.append(line)
            else:
                # Collect previous block
                if len(currentBlock) > 0:
                    sceneBlocks.append(SceneBlock(currentBlock))
                # Start a new block
                currentBlock = []
                currentBlock.append(line)

        # Collect last block
        if len(currentBlock) > 0:
            sceneBlocks.append(SceneBlock(currentBlock))

        f.close()

        self.blocks = sceneBlocks

    def getBlocks(self):
        return self.blocks

    def write(self, outPath):
        outFile = open(outPath, 'w')
        for block in self.blocks:
            outFile.write("{}\n".format(block.toString()))
        outFile.close()

    def addBlocksBeginning(self, newBlocks):
        self.blocks = newBlocks + self.blocks

    def addBlocksEnd(self, newBlocks):
        self.blocks = self.blocks + newBlocks

# Scene parser end =============================================================

# Main =========================================================================
def mainTest():
    doc = SceneDocument()
    doc.parse("tmp/sceneOriginal.pbrt")

    # Find block with arealightsource
    blocks = doc.getBlocks()
    for b in blocks:
        if b.isAreaLightSource():
            print("Found the Area light source")
            print(b.toString())
            print(b.getAssignedMaterial())
            print("Replacing...")
            b.replaceLine(3, '"rgb L"', '"rgb L" [ 99 99 99 ]')
            print(b.toString())
        if b.isMakeNamedMaterial():
            print("Found named material [{}]".format(b.getMaterialDefinitionName()))
            b.clearBody()
            b.appendLine(2, "yoyuo")
            print(b.toString())
    doc.write("tmp/sceneTrans.pbrt")
