########### VALVE FILESYSTEM INTEGRATION ###########

from ValveFileSystem.path import Path, PathError

import os
import sys
import re
import shlex

### Platform
WIN_32_SUFFIX = 'win32'
WIN_64_SUFFIX = 'win64'

# The mail server used to send mail
MAIL_SERVER = 'exchange'
DEFAULT_AUTHOR = 'python@valvesoftware.com'

# Make sure there is a HOME var...
try:
    os.environ['HOME'] = os.environ['USERPROFILE']
except KeyError:
    os.environ['HOME'] = str(Path('%HOMEDRIVE%/%HOMEPATH%'))

_MOD = None


def mod():
    '''
    returns the mod name of the current project
    '''
    global _MOD
    try:
        _MOD = Path(os.environ['VPROJECT']).name()
        return _MOD
    except KeyError:
        raise KeyError('%VPROJECT% not defined')


_GAME = None


def game():
    '''
    returns a Path instance representing the %VGAME% path - path construction this way is super easy:
    somePropPath = game() / mod() / 'models/props/some_prop.dmx'
    '''
    global _GAME
    try:
        _GAME = Path.Join(os.environ['VPROJECT'], '..')
        return _GAME
    except KeyError:
        raise KeyError('%VPROJECT% not defined.')
    except PathError:
        raise PathError('%VPROJECT% is defined with an invalid path.')


_CONTENT = None


def content():
    '''
    returns a Path instance representing the %VCONTENT% path - path construction this way is super easy:
    somePropPath = content() / 'ep3/models/characters/alyx/maya/alyx_model.ma'
    '''
    global _CONTENT

    try:
        return Path(os.environ['VCONTENT'])
    except KeyError:
        try:
            _CONTENT = Path.Join(os.environ['VPROJECT'], '../../content')
            return _CONTENT
        except KeyError:
            KeyError('%VPROJECT% not defined')


_PROJECT = None


def project():
    '''
    returns a Path instance representing the %VPROJECT% path - path construction this way is super easy:
    somePropPath = project() / 'models/props/some_prop.mdl'
    '''
    global _PROJECT
    try:
        _PROJECT = Path(os.environ['VPROJECT'])
        return _PROJECT
    except KeyError:
        raise KeyError('%VPROJECT% not defined')


_TOOLS = None


def tools(engine='Source 2'):
    '''
    returns the location of our tools.
    '''
    global _TOOLS

    if engine == 'Source':
        if _TOOLS is None:
            try:
                _TOOLS = Path(os.environ['VTOOLS'])
            except KeyError:
                try:
                    _TOOLS = Path.Join(os.environ['VGAME'], '/../../tools')

                except KeyError:
                    try:
                        _TOOLS = Path.Join(os.environ['VPROJECT'], '/../../../tools')
                    except KeyError:
                        raise KeyError('%VGAME% or %VPROJECT% not defined - cannot determine tools path')
    else:
        if _TOOLS is None:
            try:
                _TOOLS = Path(os.environ['VTOOLS'])
            except KeyError:
                try:
                    _TOOLS = Path.Join(os.environ['VGAME'], '/sdktools')
                except KeyError:
                    try:
                        _TOOLS = Path.Join(os.environ['VPROJECT'], '../sdktools')
                    except KeyError:
                        raise KeyError('%VGAME% or %VPROJECT% not defined - cannot determine tools path')

    return _TOOLS


_PLATFORM = WIN_32_SUFFIX


def platform():
    '''
    Returns the platform of the current environment, defaults to win32
    '''
    global _PLATFORM

    try:
        _PLATFORM = os.environ['VPLATFORM']
    except KeyError:
        try:
            # next try to determine platform by looking for win64 bin directory in the path
            bin64Dir = r'{0}\bin\{1}'.format(os.environ['VGAME'], WIN_64_SUFFIX)
            if bin64Dir in os.environ['PATH']:
                _PLATFORM = WIN_64_SUFFIX
        except (KeyError, PathError):
            pass
    return _PLATFORM


def addon():
    '''
    Returns the addon of the current environment or None if no addon is set
    '''
    try:
        sAddon = os.environ['VADDON']
        return sAddon
    except KeyError:
        return None


def iterContentDirectories():
    for m in gameInfo.getSearchMods():
        yield content() / m


def iterGameDirectories():
    for m in gameInfo.getSearchMods():
        yield game() / m


def getAddonFromFullPath(sFullPath):
    '''
    Returns the name of the addon determined by examining the specified path
    Returns None if the specified file is not under an addon for the current
    game()/content() tree, calls getModAndAddonTupleFromFullPath() and returns
    2nd component
    '''
    fullPath = Path(sFullPath)
    return fullPath.addonName


def setAddonFromFullPath(sFullPath):
    '''
    Sets the addon from the specified path
    '''
    fullPath = Path(sFullPath)
    setAddon(fullPath.addonName)


def resolveValvePath(valvePath, basePath=content()):
    '''
    A "Valve Path" is one that is relative to a mod - in either the game or content tree.

    Ie: if you have a project with the content dir: d:/content and the game dir: d:/game
    a "Valve Path" looks like this:  models/awesomeProps/coolThing.vmdl

    To resolve this path one must look under each mod the current project inherits from.
    So a project "test" which inherits from "another" would result in the following searches:
        d:/content/test/models/awesomeProps/coolThing.vmdl
        d:/content/another/models/awesomeProps/coolThing.vmdl

    Similarly for the game tree.

    If the path cannot be resolved to a real file, None is returned.
    '''
    for mod in gameInfo.getSearchMods():
        p = basePath / mod / valvePath
        if p.exists:
            return p


##-----------------------------------------------------------------------------
##
##-----------------------------------------------------------------------------
def FullPathToRelativePath(path, basePath=content()):
    '''
    Converts a full path to a relative path based on the current gameinfo and the
    specified base directory.  Directory defaults to content, call with game() to
    search the game directory.  If the path cannot be converted to a relative path
    it's returned exactly as it was passed in, otherwise the relative path is returned
    '''

    sFullPath = os.path.normpath(str(path))
    sBasePath = os.path.normpath(str(basePath))

    for sMod in gameInfo.getSearchMods():
        sMod = str(sMod)
        sTmpDir = os.path.normpath(os.path.join(sBasePath, sMod))
        try:
            sTmpRelPath = os.path.relpath(sFullPath, sTmpDir)
        except ValueError:
            continue
        if not sTmpRelPath.startswith('..'):
            return sTmpRelPath

    # Not found, return what was passed
    return path


##-----------------------------------------------------------------------------
##
##-----------------------------------------------------------------------------
def RelativePathToFullPath(path, basePath=content(), exist=True, includeAddons=None):
    '''
    Converts a relative path to a full path based on the current gameinfo and
    specified base directory.  If exist is True then the file must already exist
    and if it cannot be found, nothing is returned.  if exist is False any file
    that matches on the search path will be preferentially returned but if not
    a path based on the current mod will be returned
    '''

    sRelPath = os.path.normpath(str(path))
    sBasePath = os.path.normpath(str(basePath))

    for sMod in gameInfo.getSearchMods(includeAddons=includeAddons):
        sMod = str(sMod)
        sTmpDir = os.path.normpath(os.path.join(sBasePath, sMod))
        sTmpFullPath = os.path.join(sTmpDir, sRelPath)
        if os.path.exists(sTmpFullPath):
            return sTmpFullPath

    # if we don't care if it exists, return basePath/mod/relPath
    if not exist:
        return os.path.normpath(os.path.join(os.path.join(sBasePath, mod()), sRelPath))

    # Not found, must exist, return None
    return None


##-----------------------------------------------------------------------------
##
##-----------------------------------------------------------------------------
def FixSlashes(path, pathSep='/'):
    try:
        return path.replace('\\', pathSep).replace('/', pathSep)
    except:
        return path


def encode_quotes(string):
    '''
    Return a string with single and double quotes escaped, keyvalues style
    '''
    return string.replace('"', '\\"').replace("'", "\\'")


def decode_quotes(string):
    '''
    Return a string with escaped single and double quotes without escape characters.
    '''
    return string.replace('\\"', '"').replace("\\'", "'")


def setMod(newMod):
    '''
    sets the current mod to something else.  makes sure to update VPROJECT, VMOD and re-parses global gameInfo for
    the new mod so that calls to gamePath and contentPath return correctly
    '''
    global gameInfo
    os.environ['VMOD'] = str(newMod)
    os.environ['VPROJECT'] = (game() / newMod).asNative()
    gameInfo = GameInfoFile()


def setAddon(newAddon):
    '''
    sets the current addon to something else.  Mod needs to be set ahead of time
    Pass None or the empty string to unset the current addon
    '''
    if newAddon:
        os.environ['VADDON'] = str(newAddon)
    elif 'VADDON' in os.environ:
        del os.environ['VADDON']


def reportUsageToAuthor(author=None, payloadCB=None):
    '''
    when called, this method will fire of a useage report email to whoever has marked themselves as the __author__ of the tool
    the call was made from.  if no author is found then an email is sent to the DEFAULT_AUTHOR
    '''
    # additionalMsg = ''
    # try:
    # additionalMsg = payloadCB()
    # except: pass

    # try:
    # fr = inspect.currentframe()
    # frameInfos = inspect.getouterframes( fr, 0 )

    # dataToSend = []
    # if author is None:
    ##set the default - in case we can't find an __author__ variable up the tree...
    # author = DEFAULT_AUTHOR

    ##in this case, walk up the caller tree and find the top most __author__ variable definition
    # for frameInfo in frameInfos:
    # frame = frameInfo[0]
    # dataToSend.append( '%s:  %s' % (Path( frameInfo[1] ) - '%VTOOLS%', frameInfo[3]) )

    # if author is None:
    # try:
    # author = frame.f_globals['__author__']
    # except KeyError: pass

    # try:
    # author = frame.f_locals['__author__']
    # except KeyError: pass

    # import smtplib
    # envDump = '\ncontent: %s\nproject: %s\n' % (content(), project())
    # subject = '[using] %s' % str( Path( frameInfos[1][1] ).name() )
    # msg = u'Subject: %s\n\n%s\n\n%s\n\n%s' % (subject, '\n'.join( map(str, dataToSend) ), envDump, additionalMsg)

    # def sendMail():
    # try:
    # svr = smtplib.SMTP( MAIL_SERVER )
    # svr.sendmail( '%s@valvesoftware.com' % os.environ[ 'USERNAME' ], author, msg )
    # except: pass

    ##throw the mail sending into a separate thread in case the mail server is being tardy - if it succeeds, great, if something happens, meh...
    # threading.Thread( target=sendMail ).start()
    ##NOTE: this method should never ever throw an exception...  its purely a useage tracking tool and if it fails, it should fail invisibly...
    # except: pass

    pass


def asRelative(filepath):
    '''
    '''
    return str(Path(filepath).asRelative())


def contentModRelativePath(filepath):
    '''
    Returns a path instance that is relative to the mod if the path is under the content tree
    '''
    return filepath.asContentModRelative()


def addonRelativeContentPath(filepath):
    '''
    Returns a path instance that is relative to the addon if the path is under the content tree
    '''
    # Make sure the path starts with content before stripping it away
    return filepath.asAddonRelativeContentPath()


def contentModRelativePathFuzzy(filepath):
    '''
    returns a path instance that is relative to the mod if the path is under the content tree
    if an automatic match cannot be found, look for the content and mod strings using gameinfo file.
    '''
    return filepath.asContentModRelativePathFuzzy()


def projectRelativePath(filepath):
    '''
    returns a path instance that is relative to vproject().  this method is provided purely for symmetry - its pretty trivial
    '''
    return filepath - project()


def makeSourceAbsolutePath(filepath):
    '''
    Returns a Path instance as a "source" relative filepath.
    If the filepath doesn't exist under the project tree, the original filepath is returned.
    '''
    return filepath.asModRelative()


def makeSource1TexturePath(filepath):
    '''
    returns the path as if it were a source1 texture/material path - ie the path is relative to the
    materials, or materialsrc directory.  if the materials or materialsrc directory can't be found
    in the path, the original path is returned
    '''
    if not isinstance(filepath, Path):
        filepath = Path(filepath)

    try:
        idx = filepath.index('materials')
    except ValueError:
        try:
            idx = filepath.index('materialsrc')
        except ValueError:
            return filepath

    return filepath[idx + 1:]


########### DEPENDENCY CHECKING ###########

_VALIDATE_LOCATION_IMPORT_HOOK = None


def EnableValidDependencyCheck():
    '''
    sets up an import hook that ensures all imported modules live under the game directory
    '''
    global _VALIDATE_LOCATION_IMPORT_HOOK

    validPaths = [game()]

    class Importer(object):
        def find_module(self, fullname, path=None):
            lastName = fullname.rsplit('.', 1)[-1]
            scriptName = lastName + '.py'

            if path is None:
                path = []

            # not sure if there is a better way of asking python where it would look for a script/module - but I think this encapsulates the logic...
            # at least under 2.6.  I think > 3 works differently?
            for d in (path + sys.path):
                pyFilepath = Path(d) / scriptName
                pyModulePath = Path(d) / lastName / '__init__.py'
                if pyFilepath.exists or pyModulePath.exists:
                    for validPath in validPaths:
                        if pyFilepath.isUnder(validPath):
                            return None

                    print("### importing a script outside of game!", pyFilepath)
                    return None

            return None

    _VALIDATE_LOCATION_IMPORT_HOOK = Importer()
    sys.meta_path.append(_VALIDATE_LOCATION_IMPORT_HOOK)


def DisableValidDependencyCheck():
    '''
    disables the location validation import hook
    '''
    global _VALIDATE_LOCATION_IMPORT_HOOK

    if _VALIDATE_LOCATION_IMPORT_HOOK is None:
        return

    sys.meta_path.remove(_VALIDATE_LOCATION_IMPORT_HOOK)

    _VALIDATE_LOCATION_IMPORT_HOOK = None


try:
    enableHook = os.environ['ENSURE_PYTHON_CONTAINED']
    if enableHook: EnableValidDependencyCheck()
except KeyError:
    pass


########### VALVE KEYVALUES PARSER ###########

def removeLineComments(lines):
    '''
    removes all line comments from a list of lines
    '''
    newLines = []
    for line in lines:
        commentStart = line.find('//')
        if commentStart != -1:
            line = line[:commentStart]
            if not line: continue
            # strip trailing whitespace and tabs
            line = line.rstrip(' \t')
        newLines.append(line)

    return newLines


def removeBlockComments(lines):
    '''
    removes all block comments from a list of lines
    '''
    newLines = []
    end = len(lines)
    n = 0
    while n < end:
        blockCommentStart = lines[n].find('/*')
        newLines.append(lines[n])
        contFlag = 0
        if blockCommentStart != -1:
            newLines[-1] = lines[n][:blockCommentStart]
            while n < end:
                blockCommentEnd = lines[n].find('*/')
                if blockCommentEnd != -1:
                    newLines[-1] += lines[n][blockCommentEnd + 2:]
                    n += 1
                    contFlag = 1
                    break

                n += 1

        if contFlag:
            continue

        n += 1
    return newLines


def stripcomments(lines):
    '''
    Strips all C++ style block and line comments from a list of lines using RegEx
    '''

    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return ""
        else:
            return s

    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    outLines = []
    for l in lines:
        l = re.sub(pattern, replacer, l).strip()
        outLines.append(l)

    return outLines


class Chunk(object):
    '''
    a chunk creates a reasonably convenient way to hold and access key value pairs, as well as a way to access
    a chunk's parent.  the value attribute can contain either a string or a list containing other Chunk instances
    '''

    def __init__(self, key, value=None, parent=None, append=False, quoteCompoundKeys=True):
        self.key = key
        self.value = value
        self.parent = parent
        self.quoteCompoundKeys = quoteCompoundKeys
        if append:
            parent.append(self)

    def __getitem__(self, item):
        return self.value[item]

    def __getattr__(self, attr):
        if self.hasLen:
            for val in self.value:
                if val.key == attr:
                    return val

        raise AttributeError("has no attribute called %s" % attr)

    def __len__(self):
        if self.hasLen: return len(self.value)
        return None

    def _hasLen(self):
        return isinstance(self.value, list)

    hasLen = property(_hasLen)

    def __iter__(self):
        if self.hasLen:
            return iter(self.value)
        raise TypeError("non-compound value is not iterable")

    def __repr__(self, depth=0):
        strLines = []

        compoundLine = '{0}{1}\n'
        if self.quoteCompoundKeys:
            compoundLine = '{0}"{1}"\n'

        if isinstance(self.value, list) and not isinstance(self.value[0],int):
            strLines.append(compoundLine.format('\t' * depth, self.key))
            strLines.append('\t' * depth + '{\n')
            for val in self.value: strLines.append(val.__repr__(depth + 1))
            strLines.append('\t' * depth + '}\n')
        else:
            v = self.value

            strLines.append('%s"%s" "%s"\n' % ('\t' * depth, self.key, v))

        return ''.join(strLines)

    __str__ = __repr__

    def __hash__(self):
        return id(self)

    def iterChildren(self):
        '''
        '''
        if self.hasLen:
            for chunk in self:
                if chunk.hasLen:
                    for subChunk in chunk.iterChildren():
                        yield subChunk
                else:
                    yield chunk

    def asDict(self, parentDict):
        if isinstance(self.value, list):
            parentDict[self.key] = subDict = {}
            for c in self.value:
                c.asDict(subDict)
        else:
            parentDict[self.key] = self.value

    def append(self, new):
        '''
        Append a chunk to the end of the list.
        '''
        if not isinstance(self.value, list):
            self.value = []

        self.value.append(new)

        # set the parent of the new Chunk to this instance
        new.parent = self

    def insert(self, index, new):
        '''
        Insert a new chunk at a particular index.
        '''
        if not isinstance(self.value, list):
            self.value = []

        self.value.insert(index, new)

        # Set the parent of the new Chunk to this instance
        new.parent = self

    def remove(self, chunk):
        '''
        Remove given chunk from this chunk.
        '''
        for c in self.value:
            if c == chunk:
                self.value.remove(c)
                return

    def removeByKey(self, key):
        '''
        Remove any chunks with the given key from this chunk. Does not recursively search all children.
        '''
        for c in self.value:
            if c.key == key:
                self.value.remove(c)

    def findKey(self, key):
        '''
        recursively searches this chunk and its children and returns a list of chunks with the given key
        '''
        matches = []
        if self.key == key:
            matches.append(self)
        if self.hasLen:
            for val in self.value:
                matches.extend(val.findKey(key))

        return matches

    def findValue(self, value):
        '''
        recursively searches this chunk and its children and returns a list of chunks with the given value
        '''
        matches = []
        if self.hasLen:
            for val in self.value:
                matches.extend(val.findValue(value))
        elif self.value == value:
            matches.append(self)

        return matches

    def findKeyValue(self, key, value, recursive=True):
        '''
        recursively searches this chunk and its children and returns a list of chunks with the given key AND value
        '''
        keyLower = key.lower()

        matches = []
        if self.hasLen:
            for val in self.value:
                if val.key.lower() == keyLower and val.value == value:
                    matches.append(val)

                if recursive:
                    matches.extend(val.findKeyValue(key, value))

        return matches

    def testOnValues(self, valueTest):
        matches = []
        if self.hasLen:
            for val in self.value:
                matches.extend(val.testOnValues(valueTest))
        elif valueTest(self.value):
            matches.append(self)

        return matches

    def listAttr(self):
        # lists all the "attributes" - an attribute is just as a named key.  NOTE: only Chunks with length have attributes
        attrs = []
        for attr in self:
            attrs.append(attr.key)

        return attrs

    def hasAttr(self, attr):
        attrs = self.listAttr()
        return attr in attrs

    def getFileObject(self):
        '''
        walks up the chunk hierarchy to find the top chunk
        '''
        parent = self.parent
        lastParent = parent
        safety = 1000
        while parent is not None and safety:
            lastParent = parent
            parent = parent.parent
            safety -= 1

        return lastParent

    def duplicate(self, skipNullChunks=False):
        '''
        makes a deep copy of this chunk
        '''
        chunkType = type(self)

        def copyChunk(chunk):
            chunkCopy = chunkType(chunk.key)

            # recurse if nessecary
            if chunk.hasLen:
                chunkCopy.value = []

                for childChunk in chunk.__iter__(skipNullChunks):
                    childChunkCopy = copyChunk(childChunk)
                    chunkCopy.append(childChunkCopy)
            else:
                chunkCopy.value = chunk.value

            return chunkCopy

        return copyChunk(self)

    def delete(self):
        '''
        deletes this chunk
        '''
        parentChunk = self.parent
        if parentChunk:

            # the chunk will definitely be in the _rawValue list so remove it from there
            parentChunk._rawValue.remove(self)

            # the chunk MAY also be in the value list, so try to remove it from there, but if its not, ignore the exception.  NULL chunks don't get put into this list
            try:
                parentChunk.value.remove(self)
            except ValueError:
                pass


def parseLine(line):
    '''
    Line parser that extracts key value pairs from a line and returns a list of the tokens with escaped quotes.
    '''
    # Fix any trailing slashes that are escaping quotes
    if line.endswith('\\"'):
        l = line.rsplit('\\"', 1)
        line = '\\\\"'.join(l)
    elif line.endswith("\\'"):
        l = line.rsplit("\\'", 1)
        line = "\\\\'".join(l)

    lex = shlex.shlex(line, posix=True)
    lex.escapedquotes = '\"\''
    lex.whitespace = ' \n\t='
    lex.wordchars += '|.:/\\+*%$'  # Do not split on these chars
    # Escape all quotes in result
    toks = [encode_quotes(token) for token in lex]

    if len(toks) == 1:
        # Key with no value gets empty string as value
        toks.append('')
    elif len(toks) > 2:
        # Multiple value tokens, invalid
        raise TypeError
    vals = toks[1].split(" ")
    if vals and len(vals)>1:
        a = [val.isnumeric() for val in vals]
        if all(a):
            toks[1] = list(map(int,vals))
    return toks


class KeyValueFile(object):
    '''
    A class for working with KeyValues2 format files.
    self.data contains a list which holds all the top level Chunk objects
    '''

    def __init__(self, filepath=None, lineParser=parseLine, chunkClass=Chunk, readCallback=None, supportsComments=True,initial_data = None,string_buffer = None):
        '''
        lineParser needs to return key,value
        '''
        self.filepath = Path(filepath)
        self.data = self.value = []
        if initial_data is not None:
            self.data.append(initial_data)
        self.key = None
        self.parent = None
        self.lineParser = lineParser
        self.chunkClass = chunkClass
        self.callback = readCallback
        self.supportsComments = supportsComments

        def nullCallback(*args):
            pass

        self.nullCallback = nullCallback

        # if no callback is defined, create a dummy one
        if self.callback is None:
            self.callback = nullCallback

        # if no line parser was given, then use a default one
        if self.lineParser is None:
            def simpleLineParse(line):
                toks = line.split()
                if len(toks) == 1:
                    return toks[0], []
                else:
                    return toks[0], toks[1]

            self.lineParser = simpleLineParse

        # if a filepath exists, then read it
        if (filepath) and (os.path.exists(filepath)):
            self.read()
        if string_buffer:
            self.parseLines(string_buffer)

    def getFilepath(self):
        return self._filepath

    def setFilepath(self, newFilepath):
        '''
        this wrapper is here so to ensure the _filepath attribute is a Path instance
        '''
        self._filepath = Path(newFilepath)

    filepath = property(getFilepath, setFilepath)

    def read(self, filepath=None):
        '''
        reads the actual file, and passes the data read over to the parseLines method
        '''
        if filepath == None:
            filepath = self.filepath
        else:
            filepath = Path(filepath)

        self.parseLines(filepath.read())

    def parseLines(self, lines):
        '''
        this method does the actual parsing/data creation.  deals with comments, passing off data to the lineParser,
        firing off the read callback, all that juicy stuff...
        '''
        lines = [l.strip() for l in lines]

        # remove comments
        if self.supportsComments:
            lines = stripcomments(lines)
        # lines = removeLineComments(lines)
        # lines = removeBlockComments(lines)

        numLines = len(lines)

        # hold a list representation of the current spot in the hierarchy
        parentList = [self]
        parentListEnd = self
        callback = self.callback
        lineParser = self.lineParser
        n = 0
        for n,line in enumerate(lines):
            # run the callback - if there are any problems, replace the callback with the nullCallback
            try:
                callback(n, numLines)
            except:
                callback = self.nullCallback

            if line == '':
                pass
            elif line == '{':
                curParent = parentList[-1][-1]
                parentList.append(curParent)
                parentListEnd = curParent
            elif line == '}':
                parentList.pop()
                parentListEnd = parentList[-1]
            else:
                try:
                    key, value = lineParser(line)
                except (TypeError, ValueError):
                    print(line)
                    raise TypeError(
                        'Malformed keyvalue found in file near line {0} in {1}. Check for misplaced quotes'.format(
                            n + 1, self.filepath))
                parentListEnd.append(self.chunkClass(key, value, parentListEnd))
            n += 1

    def __getitem__(self, *args):
        '''
        provides an index based way of accessing file data - self[0,1,2] accesses the third child of
        the second child of the first root element in self
        '''
        args = args[0]
        if not isinstance(args, tuple):
            data = self.data[args]
        else:
            data = self.data[args[0]]
            if len(args) > 1:
                for arg in args[1:]:
                    data = data[arg]

        return data

    def __len__(self):
        '''
        lists the number of root elements in the file
        '''
        return len(self.data)

    def __repr__(self):
        '''
        this string representation of the file is almost identical to the formatting of a vmf file written
        directly out of hammer
        '''
        strList = []
        for chunk in self.data:
            a = str(chunk)
            strList.append(a)
            b = 8
        return ''.join(strList)

    __str__ = __repr__
    serialize = __repr__

    def unserialize(self, theString):
        '''
        '''
        theStringLines = theString.split('\n')
        self.parseLines(theStringLines)

    @property
    def hasLen(self):
        try:
            self.data[0]
            return True
        except IndexError:
            return False

    def asDict(self):
        '''
        returns a dictionary representing the key value file - this isn't always possible as it is valid for
        a keyValueFile to have mutiple keys with the same key name within the same level - which obviously
        isn't possible with a dictionary - so beware!
        '''
        asDict = {}
        for chunk in self.data:
            chunk.asDict(asDict)

        return asDict

    def append(self, chunk):
        '''
        appends data to the root level of this file - provided to make the vmf file object appear
        more like a chunk object
        '''
        self.data.append(chunk)

    def findKey(self, key):
        '''
        returns a list of all chunks that contain the exact key given
        :rtype: List[Chunk]
        '''
        matches = []
        for item in self.data:
            matches.extend(item.findKey(key))

        return matches

    def hasKey(self, key):
        '''
        returns true if the exact named key exists
        '''
        for item in self.data:
            if item.hasAttr(key):
                return True
        return False

    def findValue(self, value):
        '''
        returns a list of all chunks that contain the exact value given
        '''
        matches = []
        for item in self.data:
            matches.extend(item.findValue(value))

        return matches

    def findKeyValue(self, key, value):
        '''
        returns a list of all chunks that have the exact key and value given
        '''
        matches = []
        for item in self.data:
            matches.extend(item.findKeyValue(key, value))

        return matches

    def getRootChunk(self):
        '''
        Return the base chunk for the file.
        '''
        try:
            return self.value[0]
        except IndexError:
            return None

    rootChunk = property(getRootChunk, doc="The base chunk for the file.")

    def testOnValues(self, valueTest):
        '''
        returns a list of chunks that return true to the method given - the method should take as its
        first argument the value of the chunk it is testing against.  can be useful for finding values
        containing substrings, or all compound chunks etc...
        '''
        matches = []
        for item in self.data:
            matches.extend(item.testOnValues(valueTest))

        return matches

    def write(self, filepath=None, doP4=True):
        '''
        writes the instance back to disk - optionally to a different location from that which it was
        loaded.  NOTE: deals with perforce should the file be managed by p4
        '''
        if filepath is None:
            filepath = self.filepath
        else:
            filepath = Path(filepath)

        filepath.write(str(self), doP4=doP4)

    def resetCache(self):
        pass


class GameInfoFile(KeyValueFile):
    '''
    Provides an interface to gameinfo relevant operations - querying search paths, game root, game title etc...
    Passing startEmpty=True creates an empty object. Otherwise the current VPROJECT will be used to fetch the gameinfo.
    The parselines method can be passed a list of strings to fill an empty GameInfoFile object.
    '''

    def __init__(self, filepath=None, chunkClass=Chunk, readCallback=None, modname=None, startEmpty=False):

        try:
            project()
        except:
            return

        self.modname = modname

        if (filepath is None) and (not startEmpty):
            filepath = Path(os.path.join(str(project()), 'gameinfo.gi'))
            # look for a gameinfo.txt instead, pick a gameinfo.gi as default if it doesn't exist.
            if not filepath.exists:
                filepath = Path(os.path.join(str(project()), 'gameinfo.txt'))
            if not filepath.exists:
                filepath = Path(os.path.join(str(project()), 'gameinfo.gi'))

        if filepath:
            # Get filename and mod name from path
            self.filename = os.path.split(str(filepath))[1]
            if not self.modname:
                self.modname = os.path.split(os.path.dirname(str(filepath)))[1]
        else:
            self.filename = None

        KeyValueFile.__init__(self, filepath, parseLine, chunkClass, readCallback, True)

    def __getattr__(self, attr):
        try:
            return getattr(self[0], attr)
        except IndexError:
            raise AttributeError("attribute '%s' not found" % attr)

    def getSearchPaths(self):
        return [str(Path.Join('%VPROJECT%/../', modEntry)) for modEntry in self.getSearchMods()]

    def getSearchMods(self, includeAddons=None):
        '''
        Get a list of mod names listed in the SearchPaths

        includeAddons, depending if a global addon is set via the setAddon() function,
        and depending if includeAddons is explicitly set versus left as the default the
        following behaviors occur, example assumes AddonRoot of 'foo_addons' and addon of 'bar'


                       | includeAddons     | includeAddons     | includeAddons     |
                       | Default(None)     | True              | False             |
        ---------------+-------------------+-------------------+-------------------+
         addon() None  | No addon          | AddonRoot         | No addon          |
                       |                   | prepended         |                   |
                       |                   |                   |                   |
         e.g.          |                   | 'foo_addons'      |                   |
        ---------------+-------------------+-------------------+-------------------+
         addon() 'bar' | AddonRoot/addon() | AddonRoot/addon() | No addon          |
                       | prepended         | prepended         |                   |
                       |                   |                   |                   |
         e.g.          | 'foo_addons/bar'  | 'foo_addons/bar'  |                   |
        ---------------+-------------------+-------------------+-------------------+

        '''
        # always has the base mod in it...
        searchMods = [self.modname]
        # See if a global addon is set
        sAddon = addon()
        # if the user has explicitly set includeAddons to True or the user has set a global
        # addon and hasn't explicitly set includeAddons to False then include addons
        bIncludeAddons = includeAddons or ((sAddon) and (includeAddons is None))

        gi = '|gameinfo_path|'
        sp = '|all_source_engine_paths|'
        for chunk in self.FileSystem.SearchPaths:
            bAddon = ('addonroot' in chunk.key.lower())
            if (bAddon) and (not bIncludeAddons):
                continue
            pos = chunk.value.find(gi)
            if pos != -1: continue

            sPath = chunk.value.replace(sp, '')
            if not sPath: continue
            if bAddon:
                sAddon = addon()
                if sAddon:
                    sPath = sPath + '/' + sAddon
            if sPath not in searchMods:
                if bAddon:
                    searchMods.insert(0, sPath)
                else:
                    searchMods.append(sPath)
        return searchMods

    def getAddonRoots(self):
        '''
        Return a list of addon root names in the SearchPaths
        '''
        addonNames = []
        for chunk in self.FileSystem.SearchPaths:
            if 'addonroot' in chunk.key.lower():
                if chunk.value not in addonNames:
                    addonNames.append(chunk.value)
        return addonNames

    def getTitle(self):
        try:
            return self[0].title.value
        except AttributeError:
            try:
                return self[0].game.value
            except:
                return None

    title = property(getTitle)

    def getEngine(self):
        try:
            return self[0].ToolsEnvironment.Engine.value
        except AttributeError:
            try:
                return self[0].engine.value
            except:
                return None

    engine = property(getEngine)

    def getToolsDir(self):
        try:
            return self[0].ToolsEnvironment.ToolsDir.value
        except AttributeError:
            try:
                return self[0].ToolsDir.value
            except:
                return None

    toolsDir = property(getToolsDir)

    def __get_useVPLATFORM(self):
        try:
            return self[0].ToolsEnvironment.UseVPLATFORM.value
        except AttributeError:
            try:
                return self[0].UseVPLATFORM.value
            except:
                return None

    useVPLATFORM = property(__get_useVPLATFORM)

    def __getPythonVersion(self):
        try:
            return self[0].ToolsEnvironment.PythonVersion.value
        except AttributeError:
            try:
                return self[0].PythonVersion.value
            except:
                return None

    pythonVersion = property(__getPythonVersion)

    def __get_PythonHomeDisable(self):
        try:
            return self[0].ToolsEnvironment.PythonHomeDisable.value
        except AttributeError:
            try:
                return self[0].PythonHomeDisable.value
            except:
                raise

    pythonHomeDisable = property(__get_PythonHomeDisable)

    def __get_PythonDir(self):
        try:
            return self[0].ToolsEnvironment.PythonDir.value
        except AttributeError:
            try:
                return self[0].PythonDir.value
            except:
                return None

    pythonDir = property(__get_PythonDir)

    def writeDefaultFile(self):
        '''
        Creates a default GameInfo file with basic structure
        '''
        self.filepath.write('''"GameInfo"\n{\n\tgame "tmp"\n\tFileSystem\n\t{\n\t\tSearchPaths\n'+
		'\t\t{\n\t\t\tGame |gameinfo_path|.\n\t\t}\n\t}\n}''')

    def simpleValidate(self):
        '''
        Checks to see if the file has some basic keyvalues
        '''
        try:
            getattr(self[0], 'game')
            getattr(self[0], 'SearchPaths')
            return True
        except AttributeError:
            raise GameInfoException('Not a valid gameinfo file.')

        # Read the current gameinfo


gameInfo = GameInfoFile()


class GameInfoException(Exception):
    def __init__(self, message, errno=None):
        Exception.__init__(self, message)
        self.errno = None
        self.strerror = message


def getAddonBasePaths(asContent=False):
    '''
    Returns a list of Paths for the addon base directories for the current mod (eg. 'dota_addons')
    Returns content-based Paths instead of game-based Paths if asContent is set to True.
    '''
    if asContent:
        basePath = content()
    else:
        basePath = game()

    return [(basePath + addon) for addon in gameInfo.getAddonRoots()]


def getAddonPaths(asContent=False):
    '''
    Returns a list of addons Paths for the current mod.
    Returns content-based Paths instead of game-based Paths if asContent is set to True.
    '''
    addonPaths = []
    for base in getAddonBasePaths(asContent):
        addonPaths.extend(base.dirs())
    return addonPaths


def getAddonNames():
    '''
    Returns a list of addon names for the current mod.
    '''
    return [d.addonName for d in getAddonPaths()]


def lsGamePath(path, recursive=False):
    '''
    lists all files under a given 'valve path' - ie a game or content relative path.  this method needs to iterate
    over all known search mods as defined in a project's gameInfo script
    '''
    path = Path(path)
    files = []

    for modPath in [Path(os.path.join(base, path.asNative())) for base in gameInfo.getSearchPaths()]:
        files += list(modPath.files(recursive=recursive))

    return files


def lsContentPath(path, recursive=False):
    '''
    similar to lsGamePath except that it lists files under the content tree, not the game tree
    '''
    path = Path(path)
    c = content()
    files = []

    for modPath in [c / mod / path for mod in gameInfo.getSearchMods()]:
        files += list(modPath.files(recursive=recursive))

    return files


def contentPath(modRelativeContentPath):
    '''allows you do specify a path using mod relative syntax instead of a fullpath
    example:
       assuming vproject is set to d:/main/game/tf_movies
       contentPath( 'models/player/soldier/parts/maya/soldier_reference.ma' )

       returns: d:/main/content/tf/models/player/soldier/parts/maya/soldier_reference.ma

    NOTE: None is returned in the file can't be found in the mod hierarchy
    '''
    return Path(modRelativeContentPath).expandAsContent(gameInfo)


def gamePath(modRelativeContentPath):
    '''allows you do specify a path using mod relative syntax instead of a fullpath
    example:
       assuming vproject is set to d:/main/game/tf
       gamePath( 'models/player/soldier.mdl' )

       returns: d:/main/game/tf/models/player/soldier.mdl

    NOTE: None is returned in the file can't be found in the mod hierarchy
    '''
    return Path(modRelativeContentPath).expandAsGame(gameInfo)


def textureAsGameTexture(texturePath):
    '''
    returns a resolved game texture filepath given some sort of texture path
    '''
    if not isinstance(texturePath, Path):
        texturePath = Path(texturePath)

    if texturePath.isAbs():
        if texturePath.isUnder(content()):
            relPath = texturePath - content()
        else:
            relPath = texturePath - game()
        relPath = relPath[2:]
    else:
        relPath = texturePath
        if relPath.startswith('materials') or relPath.startswith('materialsrc'):
            relPath = relPath[1:]

    relPath = Path(Path('materials') + relPath).setExtension('vtf')
    relPath = relPath.expandAsGame(gameInfo)

    return relPath


def textureAsContentTexture(texturePath):
    '''
    returns a resolved content texture filepath for some sort of texture path.  it looks for psd
    first, and then for tga.  if neither are found None is returned
    '''
    if not isinstance(texturePath, Path):
        texturePath = Path(texturePath)

    xtns = ['psd', 'tga']
    if texturePath.isAbs():
        if texturePath.isUnder(content()):
            relPath = texturePath - content()
        else:
            relPath = texturePath - game()
        relPath = relPath[2:]
    else:
        relPath = texturePath
        if relPath.startswith('materials') or relPath.startswith('materialsrc'):
            relPath = relPath[1:]

    contentPath = 'materialsrc' / relPath
    for xtn in xtns:
        tmp = contentPath.expandAsContent(gameInfo, xtn)
        if tmp is None: continue

        return tmp

    return None


def resolveMaterialPath(materialPath):
    '''
    returns a resolved material path given some sort of material path
    '''
    if not isinstance(materialPath, Path):
        materialPath = Path(materialPath)

    if materialPath.isAbs():
        if materialPath.isUnder(content()):
            relPath = materialPath - content()
        else:
            relPath = materialPath - game()
        relPath = relPath[2:]
    else:
        relPath = materialPath
        if relPath.startswith('materials') or relPath.startswith('materialsrc'):
            relPath = relPath[1:]

    relPath = ('materials' + relPath).setExtension('vmt')
    relPath = relPath.expandAsGame(gameInfo)

    return relPath

# end
