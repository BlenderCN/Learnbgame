# ##### BEGIN MIT LICENSE BLOCK #####
#
# Copyright (c) 2015 - 2017 Pixar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#
# ##### END MIT LICENSE BLOCK #####

import json
import time
import datetime
import shutil
import glob
import os.path
import sys
import subprocess
import re
import xml.dom.minidom as mx
import filecmp
import distutils.version as dv
from collections import OrderedDict
from . import vstruct as vstruct


# use a global to store the last read json file to be able to read from it
# without having to load it again.
#
__lastJson = None

# debugging utilities
#
__loglevel = 0


##
# @brief      flatten nested sequence into a single sequence
#
# @param      l       input sequence
# @param      ltypes  type of sequence
#
# @return     the flattened sequence
#
def flatten(l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)


##
# @brief      Builds a space-delimited list of values string. The array will be
#             flattened first.
#
# @param      l     the list containing the values. We support nested lists.
#
# @return      string containing space-delimited values.
#
def buildRibArrayValues(l):
    av = str(flatten(l)).replace(',', '')[1:-1]
    return av


##
# @brief      Set the log level.
#
# @param      level  The logging level. See logLevels() for details.
#
# @return     None
#
def setLogLevel(level):
    global __loglevel
    __loglevel = level


##
# @brief      Prints the supported log levels to std out.
#             0 : silent
#             1 : warnings only
#             2 : external files processing
#             3 : vstruct debugging
#
# @return     None
#
def logLevels():
    global __loglevel
    print('rmanAssets log levels:')
    print('   0 : silent')
    print('   1 : warnings only')
    print('   2 : external files processing')
    print('   3 : vstruct debugging')
    print('   current log level : %d' % __loglevel)


##
# @brief      Returns the log level.
#
# @return     an int
#
def logLevel():
    global __loglevel
    return __loglevel


##
# @brief      Logs a warning. it won't be printed if the log level is too low.
#
# @param      msg   The msg
#
# @return     None
#
def logWarning(msg):
    global __loglevel
    if __loglevel > 0:
        print('rmanAssets Warning: %s' % msg)


##
# @brief      log an external file message. it won't be printed if the log
#             level is too low.
#
# @param      msg   The msg
#
# @return     None
#
def logExternalFiles(msg):
    global __loglevel
    if __loglevel == 2:
        print('%s' % msg)


##
# @brief      Returns a Windows-only object to make sure tasks launched through
#             subprocess don't open a cmd window.
#
# @return     A startupinfo object on windows, None on other OSes.
#
def startupInfo():
    startupinfo = None
    if os.name is 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return startupinfo


##
# @brief      Adds an exe suffix to app names on windows-based OSes.
#
# @param      name  The executable's name
#
# @return     The correct execuatble name for that platform.
#
def app(name):
    if os.name is 'nt':
        return (name + '.exe')
    return name


##
# @brief      Convert a path to posix format, which is our internal
#             representation.
#
# @param      path  a file path
#
# @return     a posix file path
#
def internalPath(path):
    ipath = path
    if os.sep is not '/':
        ipath = path.replace(os.sep, '/')
    # print 'internalPath( %s ) = %s' % (path, repr(ipath))
    return ipath


##
# @brief      Convert our internal posix path to a platform specific format.
#
# @param      path  posix path
#
# @return     platform-specific path
#
def externalPath(path):
    # print 'externalPath( %s ) = %s' % (path, repr(os.path.normpath(path)))
    return r'%s' % os.path.normpath(path)


##
# @brief      A class used to query environment variables. It can be overriden
#             by a client app, like Maya, who may have a slightly different
#             environment.
#
class DefaultEnv:

    def Exists(self, key):
        # print '>>>> DefaultEnv::Exists %s' % key
        if key in os.environ:
            return True
        else:
            return False

    def GetValue(self, key):
        # print '>>>> DefaultEnv::GetValue %s' % key
        try:
            val = os.environ[key]
        except:
            raise RmanAssetError('%s is not an registered environment ' +
                                 'variable !' % key)
        # print 'DefaultEnv.GetValue( %s ) = %s' % (key, repr(val))
        return os.path.expandvars(val)


# a global that can be set by the client via setEnvClass().
#
g_env = DefaultEnv()


# a few utility functions to avoid referencing globals everywhere.

##
# @brief      Returns the value of an environment variable. This function calls
#             an object that has been registered through setEnvClass(). This
#             allows a client to use/pass its own environment.
#
# @param      key   the environment variable name
#
# @return     value as a string. If the variable doesn't exist or is an empty
#             string, an exception will be raised by the registered object. Any
#             environment variable in the result will be expanded.
#
def envGet(key):
    global g_env
    return g_env.GetValue(key)


##
# @brief      Checks if an environment variable is defined and not an empty
#             string.
#
# @param      key   the environment variable name
#
# @return     True or False
#
def envExists(key):
    global g_env
    return g_env.Exists(key)


##
# @brief      Set the env class.
#
# @param      obj   An object passed by the client. The client's class MUST
#                   implement two methods : GetValue(key) and Exists(key). See
#                   DefaultEnv class above for a reference implementation.
#
# @return     None
#
def setEnvClass(obj):
    global g_env
    g_env = obj


##
# @brief      Helper to get the last exception message string.
#
# @return     system error message string
#
def sysErr():
    return sys.exc_info()[0]


# Simplistic image type detection based on file extension.
#
__imgExtensions = ['.tif', '.exr', '.jpg', '.sgi', '.tga',
                   '.iff', '.dpx', '.bmp', '.png']
__texExtensions = ['.tex', '.tx']
__hdrExtensions = ['.exr', '.hdr']


def isImage(filename):
    global __imgExtensions
    return (os.path.splitext(filename)[1] in __imgExtensions)


def isTexture(filename):
    global __texExtensions
    return (os.path.splitext(filename)[1] in __texExtensions)


def isHDRI(filename):
    global __hdrExtensions
    return (os.path.splitext(filename)[1] in __hdrExtensions)


##
# @brief      Exception reporting class
#
class RmanAssetError(Exception):
    def __init__(self, value):
        self.value = 'RmanAsset Error: %s' % value

    def __str__(self):
        return repr(self.value)


##
# @brief      Specify transformation space : world or object
#
class TrSpace:
    k_world = 0
    k_object = 1


##
# @brief      How are transformation values specified ? Could be a 4x4 matrix
#             or Translate + Rotate + scale
#
class TrStorage:
    k_matrix = 0    # 16 floats expected
    k_TRS = 1       # 3+3+3 floats expected


##
# @brief      Tranformations could be flat or hierarchical.
#
class TrMode:
    k_flat = 0
    k_hierarchical = 1


##
# @brief      Transformations could be output as a separate named coordinate
#             system or as a transformation of the node.
#
class TrType:
    k_coordsys = 0
    k_nodeTransform = 1


# a dict of parsed shading node objects.
# These are stored lazily to avoid re-parsing every time the user creates
# a new asset.
g_rmanShadingNodeCache = {}

# the path to all args files.
g_rmanShadingNodePaths = []
g_rmanShadingNodePathsInit = False

# debug : store which files have been found
g_rmanShadingNodeIniFiles = []


##
# @brief      A class that reads node descriptions from args files.
#
class RmanShadingNode:

    ##
    # @brief      Takes a shading node name, like 'PxrExposure', finds the
    #             relevant args file and stores the results in a global dict to
    #             amortize repeated lookups.
    #
    # @param      self             none
    # @param      shadingNodeType  node type, i.e. 'PxrDomeLight'.
    # @param      osoPath          Optional oso file path
    #
    def __init__(self, shadingNodeType, osoPath=None):
        global g_rmanShadingNodeCache
        self.name = shadingNodeType
        # self.oso  = osoPath
        if shadingNodeType not in g_rmanShadingNodeCache:
            self.__registerNodePaths(osoPath)
            self.__parseNode()

    ##
    # @brief      private method to discover paths to args files on system. The
    #             paths found will be stored (in posix format) in the
    #             g_rmanShadingNodePaths globals variable to amortize repeated
    #             lookups.
    #
    # @param      self  none
    #
    # @return     none
    #
    def __registerNodePaths(self, thisPath=None):
        global g_rmanShadingNodePaths
        global g_rmanShadingNodePathsInit

        if thisPath is not None:
            if thisPath not in g_rmanShadingNodePaths:
                if os.path.exists(thisPath):
                    g_rmanShadingNodePaths.append(thisPath)
                else:
                    err = ("__registerNodePaths: path doesn't exist: %s"
                           % thisPath)
                    raise RmanAssetError(err)
        # don't go through the whole thing if it has already been done.
        if g_rmanShadingNodePathsInit:
            return
        # standard rendermn.ini file
        try:
            rmantree = internalPath(envGet('RMANTREE'))
        except:
            raise RmanAssetError('RmanShadingNode: RMANTREE is not defined !')
        std_ini = os.path.join(rmantree, 'etc', 'rendermn.ini')
        self.__readIniPaths(std_ini)
        # user rendermn.ini file
        user_ini = os.path.join(os.path.expanduser('~'), 'rendermn.ini')
        self.__readIniPaths(user_ini)

        # rms args files path if RMS is installed
        #if envExists('RMSTREE'):
        #    rmstree = internalPath(envGet('RMSTREE'))
        #    rms_args_path = os.path.join(rmstree, 'lib', 'rfm', 'ris',
        #                                 'mayaNodes')
        #    if os.path.exists(rms_args_path):
        #        g_rmanShadingNodePaths.append(rms_args_path)

        # print g_rmanShadingNodePaths
        if len(g_rmanShadingNodePaths) < 1:
            raise RmanAssetError('Could not find rix plugin path !')

        g_rmanShadingNodePathsInit = True

    ##
    # @brief      Opens a rendermn.ini file to find '/standardrixpluginpath',
    #             get the paths to rix plugins and store them in the
    #             g_rmanShadingNodePaths global var.
    #
    # @param      self      none
    # @param      ini_file  full path to the rendermn.ini file
    #
    # @return     none. The result is directly saved in g_rmanShadingNodePaths.
    #
    def __readIniPaths(self, ini_file):
        global g_rmanShadingNodePaths
        global g_rmanShadingNodeIniFiles
        if os.path.exists(ini_file):
            g_rmanShadingNodeIniFiles.append(ini_file)
            # read ini file
            fh = open(externalPath(ini_file), 'r')
            ini = fh.read()
            fh.close()
            # find the relevant paths
            ini_keys = ['standardrixpluginpath',  # c++ plugins
                        'standardshaderpath']     # osl shaders
            for key in ini_keys:
                m = re.search('/' + key + '\s+(.+)', ini)
                if m:
                    # print '0: "%s"' % m.group(0)
                    # print 'match 1: %s' % repr(m.group(1))
                    paths = m.group(1).split(':')
                    for p in paths:
                        # print 'ini path as read: %s' % p
                        thispath = os.path.expandvars(p)
                        # print ' > expanded path: %s' % thispath
                        argspath = os.path.join(thispath, 'Args')
                        if os.path.exists(argspath):
                            g_rmanShadingNodePaths.append(argspath)
                        else:
                            g_rmanShadingNodePaths.append(thispath)
                
                else:
                    print('RmanShadingNode: Could not find '
                          'standardrixpluginpath in rendermn.ini !')

    ##
    # @brief      Parse an args file and stores results for later retrieval.
    #
    # @param      self      none
    # @param      nodename  for example 'PxrLMSubsurface'
    #
    # @return     none. results are stored in the g_rmanShadingNodeCache dict.
    #
    def __parseNode(self):
        global g_rmanShadingNodePaths
        global g_rmanShadingNodeCache
        global g_rmanShadingNodeIniFiles
        xml = None
        oso = None
        for path in g_rmanShadingNodePaths:
            # try to open the file in each path...
            #
            xmlfile = externalPath(os.path.join(path, self.name + '.args'))
            try:
                xml = mx.parse(xmlfile)
            except:
                # print '%s not in %s' % (self.name, xmlfile)
                xml = None
                oso = externalPath(os.path.join(path, self.name + '.oso'))
                if not os.path.exists(oso):
                    # print '%s not in %s' % (self.name, oso)
                    oso = None
                    continue
            # the file has been found and parsed, let get down to business...
            #
            if xml is not None:
                # print 'Parse Args for %s' % self.name
                self.__parseArgsXml(xml)
                break
            elif oso is not None:
                # print 'Parse oso for %s' % self.name
                self.__parseOsoFile(oso)
                break

        if xml is None and oso is None:
            yesno = ['No', 'Yes']
            print('Diagnostic ------------------------------------------------')
            print('Failed to find: "%s.args" or "%s.oso"' % (self.name,
                                                             self.name))
            print('Found ini files : %s' % g_rmanShadingNodeIniFiles)
            print('Searched paths:')
            for path in g_rmanShadingNodePaths:
                print(' + %s' % path)
                exists = os.path.exists(path)
                print('   Path exists: %s' % (yesno[exists]))
                if exists:
                    files = os.listdir(externalPath(path))
                    print('   Number of files: %d' % (len(files)))
                    for f in files:
                        print('   > %s' % f)
            print('-----------------------------------------------------------')
            raise RmanAssetError('Could not parse %s ! '
                                 'Is it a RenderMan node ?' % self.name)
        # else:
        #     print '%s' % g_rmanShadingNodeCache[self.name]

    ##
    # @brief      Parse the xml contents of an args file.
    #
    # @param      self  object ref
    # @param      xml   The xml document
    #
    # @return     None
    #
    def __parseArgsXml(self, xml):
        global g_rmanShadingNodeCache
        # get the node type (bxdf, pattern, etc)
        # we expected only one shaderType element containing a single
        # tag element. Anything else will make this code explode.
        #
        shaderTypes = xml.getElementsByTagName('shaderType')
        if len(shaderTypes) == 0:
            # some args files use 'typeTag'... which one is correct ?
            shaderTypes = xml.getElementsByTagName('typeTag')
        if len(shaderTypes):
            tags = shaderTypes.item(0).getElementsByTagName('tag')
            if len(tags):
                nodetype = tags.item(0).getAttribute('value')
            else:
                err = 'No "tag" element in "shaderType" ! : %s' % xmlfile
                raise RmanAssetError(err)
        else:
            err = 'No "shaderType" element in args file ! : %s' % xmlfile
            raise RmanAssetError(err)
        # in RIS, displacement should translate to displace
        if nodetype == 'displacement':
            nodetype = 'displace'

        # is this a metashader, i.e. an args file referencing a node
        # with a different name ?
        rmanNode = self.name
        metashader = xml.getElementsByTagName('metashader')
        if len(metashader):
            rmanNode = metashader.item(0).getAttribute('shader')

        # get the node parameters
        #
        params = xml.getElementsByTagName('param')
        # print 'Got %d params' % len(params)
        g_rmanShadingNodeCache[self.name] = {'nodeType': nodetype,
                                             'rmanNode': rmanNode,
                                             'params': []}
        thisNode = g_rmanShadingNodeCache[self.name]
        for p in params:
            # param type
            ptype = p.getAttribute('type')
            if p.hasAttribute('isDynamicArray'):
                if p.getAttribute('isDynamicArray') != '0':
                    ptype += '[]'
                elif p.hasAttribute('arraySize'):
                    size = p.getAttribute('arraySize')
                    ptype += '[%d]' % int(size)
            elif p.hasAttribute('arraySize'):
                size = p.getAttribute('arraySize')
                ptype += '[%d]' % int(size)
            # param name
            pname = p.getAttribute('name')
            # param default
            pdefault = p.getAttribute('default')
            if 'string' not in ptype:
                try:
                    pdefault = eval(pdefault)
                except:
                    try:
                        pdefault = eval(pdefault.replace(' ', ','))
                    except:
                        # mmmm....
                        pass
            # add the base description
            thisNode['params'].append({'type': ptype, 'name': pname,
                                       'default': pdefault})
            thisParam = thisNode['params'][-1]
            # vstructs
            if p.hasAttribute('vstructmember'):
                thisParam['vstructmember'] = p.getAttribute('vstructmember')

            # store input vstruct
            tag = p.getElementsByTagName('tag')
            if tag.length > 0:
                tagValue = tag[0].getAttribute('value')
                if tagValue == 'vstruct':
                    thisParam['type'] = 'vstruct'

    ##
    # @brief      Parse an OSL object file with the help of oslinfo
    #
    # @param      self  object ref
    # @param      oso   the file path to the *.oso
    #
    # @return     None
    #
    def __parseOsoFile(self, oso):
        global g_rmanShadingNodeCache
        # use oslinfo to read parameter list
        # print ' + oslinfo -v %s' % oso
        rmantree = internalPath(envGet('RMANTREE'))
        oslinfo = os.path.join(rmantree, 'bin', app('oslinfo'))
        cmd = [externalPath(oslinfo), '-v', externalPath(oso)]
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             startupinfo=startupInfo(),
                             bufsize=-1)
        out, err = p.communicate()
        # make sure we use the os' favorite end-of-line sequence.
        out = out.decode('utf-8')
        lines = out.split(os.linesep)
        rmanNode = lines[0].split()[1].replace('"', '')
        g_rmanShadingNodeCache[self.name] = {'params': [],
                                             'rmanNode': rmanNode,
                                             'nodeType': 'pattern'}
        thisNode = g_rmanShadingNodeCache[self.name]
        thisParam = None

        for l in lines:
            # split the line on whitespace
            toks = l.split()

            if len(toks) < 1:
                continue

            # skip anything not looking like an input param
            if toks[0][0] == '"':
                # parameter : 0:name 1:type
                thisNode['params'].append({})
                thisParam = thisNode['params'][-1]
                for t in range(len(toks)):
                    toks[t] = toks[t].replace('"', '')
                if toks[1] == 'output':
                    thisParam['type'] = toks[1] + ' ' + toks[2]
                    thisParam['name'] = toks[0]
                else:
                    thisParam['type'] = toks[1]
                    thisParam['name'] = toks[0]
            elif toks[0] == 'Default':
                # default value
                default = ''
                if len(toks) > 3:
                    # this is not a single value default.
                    # turn list of tokens into string, like so:
                    # ['[', '0.0', '0.0', '0.0', ']'] -> '(0.0, 0.0, 0.0)'
                    default = '(%s)' % (', '.join(toks[1:-1]))
                else:
                    default = toks[2]
                thisParam['default'] = default
            elif toks[0] == 'metadata:':
                # metadata
                meta = ' '.join(toks[4:])
                meta = meta.replace('"', '')
                if toks[2] == 'vstructmember':
                    thisParam['vstructmember'] = meta
                elif toks[2] == 'vstructConditionalExpr':
                    thisParam['vstructConditionalExpr'] = meta
                elif toks[2] == 'tag' and meta == 'vstruct':
                        thisParam['type'] = 'vstruct'

    ##
    # @brief      Returns the params array.
    #
    # @param      self  none
    #
    # @return     an array of dicts containing all params. The array looks
    #             like so : [{'type': 'float[]', 'name': 'IORs'}, {...}, ...]
    #
    def params(self):
        global g_rmanShadingNodeCache
        return g_rmanShadingNodeCache[self.name]['params']

    ##
    # @brief      Return the node's type : bxdf, pattern, light, etc
    #
    # @param      self  none
    #
    # @return     string result
    #
    def nodeType(self):
        global g_rmanShadingNodeCache
        return g_rmanShadingNodeCache[self.name]['nodeType']

    ##
    # @brief      Return the nodename, which may be different than the name if
    #             we are dealing with a metashader.
    #
    # @param      self  none
    #
    # @return     string result
    #
    def rmanNode(self):
        global g_rmanShadingNodeCache
        return g_rmanShadingNodeCache[self.name]['rmanNode']

    ##
    # @brief      debugging method
    #
    # @param      self  none
    #
    # @return     a human-readable dump of the node
    #
    def __str__(self):
        global g_rmanShadingNodeCache
        s = '%s ----------\n' % self.name
        s += 'type: %s\n' % g_rmanShadingNodeCache[self.name]['nodeType']
        s += 'rman node: %s\n' % g_rmanShadingNodeCache[self.name]['rmanNode']
        for p in g_rmanShadingNodeCache[self.name]['params']:
            for k, v in sorted(p.items()):
                s += '  %s:"%s"' % (k, v)
            s += '\n'
        s += '-' * 80
        return s


class vstructAssets:

    ##
    # @brief      constructor
    #
    # @param      self      The object
    # @param      dstNode   The dst node name
    # @param      dstType   The dst parameter type
    # @param      dstParam  The dst param name
    # @param      src       The src RmanAssetNode
    #
    def __init__(self, dstNode, dstType, dstParam, src, srcParam):
        self.action = None
        self.actionValue = None
        self.fallback = None
        self.fallbackValue = None
        self.dstNode = dstNode
        self.dstParam = dstParam
        self.srcNode = src.name()
        self.srcParam = srcParam
        self.params = src._data['params']
        # print ('%s.%s -> %s.%s' % (self.srcNode, self.srcParam,
        #                            self.dstNode, self.dstParam))

    def paramGetValue(self, param):
        if param in self.params:
            value = self.params[param]['value']
            if 'vstructmember' in self.params[param]:
                # this value can be overriden if this node's master vstruct
                # param is connected. We then need to recursively evaluate
                # the expressions.
                pass
            if isinstance(value, bool):
                value = int(value)
            vstruct.logTrace('Client paramGetValue :'.rjust(45) +
                             ' param = %s' % self.params[param])
            return value
        else:
            print('=' * 80)
            print('%s.%s -> %s.%s' % (self.srcNode, self.srcParam,
                                       self.dstNode, self.dstParam))
            print(vstruct.getLastTrace())
            raise RmanAssetError('ERROR: vstructAssets:paramGetValue : '
                                 '%s not in param list of %s ! : %s'
                                 % (param, self.srcNode, self.params.keys()))

    # def paramSetValue(self, param, value):
    #     print '++ paramSetValue: %s = %s' % (param, value)

    def paramIsConnected(self, param):
        # print '++ paramIsConnected: %s' % (param)
        if param in self.params:
            return ('reference ' in self.params[param]['type'])
        else:
            print('=' * 80)
            print ('%s.%s -> %s.%s' % (self.srcNode, self.srcParam,
                                       self.dstNode, self.dstParam))
            print(vstruct.getLastTrace())
            raise RmanAssetError('ERROR: vstructAssets:paramIsConnected : '
                                 '%s not in param list of %s !'
                                 % (param, self.srcNode))

    def actionSet(self, action):
        if self.action is None:
            self.action = action
        else:
            self.fallback = action
        vstruct.logTrace('Client actionSet :'.rjust(45) +
                         ' action = %s  fallback = %s'
                         % (self.action, self.fallback))

    def actionChoose(self, which):
        if which == 'action':
            self.fallback = None
        else:
            self.action = None

    def actionGet(self):
        if self.action is not None:
            return self.action
        else:
            return self.fallback

    def valueSet(self, value):
        if self.action is not None and self.actionValue is None:
            self.actionValue = value
        else:
            self.fallbackValue = value
        vstruct.logTrace('Client valueSet :'.rjust(45) +
                         ' actionValue = %s  fallbackValue = %s'
                         % (self.actionValue, self.fallbackValue))

    def valueGet(self):
        if self.action is not None:
            return self.actionValue
        else:
            return self.fallbackValue


class RmanAssetNodeConnection:
    def __init__(self, paramdict):
        self._data = paramdict

    def srcNode(self):
        return self._data['src']['node']

    def srcNodeHandle(self):
        # RIB-compatible name (':' is reserved for connections)
        return self.srcNode().replace(':', '_')

    def srcParam(self):
        return self._data['src']['param']

    def srcNodeParam(self):
        return ('%s.%s' % (self._data['src']['node'],
                           self._data['src']['param']))

    def dstNode(self):
        return self._data['dst']['node']

    def dstNodeHandle(self):
        # RIB-compatible name (':' is reserved for connections)
        return self.dstNode().replace(':', '_')

    def dstParam(self):
        return self._data['dst']['param']

    def dstNodeParam(self):
        return ('%s.%s' % (self._data['dst']['node'],
                           self._data['dst']['param']))


class RmanAssetNodeParam:
    def __init__(self, name, paramdict):
        self._name = name
        self._data = paramdict

    def name(self):
        return self._name

    def type(self):
        return self._data['type']

    def value(self):
        try:
            # output parameters don't have a value
            return self._data['value']
        except:
            return None

    ##
    # @brief      Generate RIB for this parameter.
    #
    # @param      self            The object
    # @param      nodename        The node's name
    # @param      connectObjDict  The connect obj dict
    # @param      nodeDict        All graph nodes as nodeName: RmanAssetNode
    #
    # @return     RIB string
    #
    def getRIB(self, nodename, connectObjDict, nodeDict):

        # skip 'output' parameters
        if 'output ' in self.type():
            return None
        if self.type() == 'vstruct':
            return None

        rib = ''

        # vstruct check
        if 'vstructmember' in self._data:
            # print '%s: %s is a vstructmember' % (nodename, self.name())
            # this param belongs to a vstruct
            masterAttr, attr = self._data['vstructmember'].split('.')
            if masterAttr in connectObjDict:
                # get the node the master param is connected to...
                cnode, cattr = connectObjDict[masterAttr].split(':')
                # this param belongs to a vstruct
                vstructSrcParam = '%s_%s' % (cattr, attr)
                # print ' > upstream : %s.%s' % (cnode, vstructSrcParam)
                rib = nodeDict[cnode].vstructEval(nodename,
                                                  self.type(),
                                                  self.name(),
                                                  vstructSrcParam,
                                                  nodeDict)
                if rib is not None:
                    return rib

        # regular output starts with param type and name...
        val = self.value()
        rib = '''"%s %s" [''' % (self.type(), self.name())

        # detect a connected param : they start by 'reference' and have a value
        # of None
        if 'reference ' in self.type() and val is None:
            if 'vstruct' in self.type():
                # this is a vstruct connection : do not output to RIB
                return None
            if self.name() in connectObjDict:
                rib += '''"%s" ''' % (connectObjDict[self.name()])
        elif isinstance(val, list):
            # this is a list, i.e. some kind of array or tuple
            rib += buildRibArrayValues(val)
        else:
            if isinstance(val, float):
                rib += '%g ' % val
            elif isinstance(val, str) or isinstance(val, bytes):
                rib += '"%s" ' % val
            else:
                try:
                    rib += '%d ' % int(val)
                except:
                    RmanAssetError('getRIB: failed: %s = %s' %
                                   (self.name(), val))
        rib = rib.rstrip() + '] '
        return rib


class RmanAssetNode:
    def __init__(self, name, nodedict):
        self._name = name
        self._handle = name.replace(':', '_')
        self._data = OrderedDict(nodedict)

    def name(self):
        return self._name

    def handle(self):
        return self._handle

    def type(self):
        return self._data['type']

    def rmanNode(self):
        return self._data['rmanNode']

    def nodeClass(self):
        return self._data['nodeClass']

    def externalOSL(self):
        try:
            return self._data['externalOSL']
        except:
            return False

    def paramsDict(self):
        paramList = []
        for (name, data) in self._data['params'].items():
            paramList.append(RmanAssetNodeParam(name, data))
        return paramList

    def params(self):
        return self._data['params']

    def transforms(self):
        if 'transforms' not in self._data.keys():
            return None, None, None
        tr = []
        fmt = self._data['transforms']['format']
        try:
            ttype = self._data['transforms']['type']
        except:
            ttype = None
        if fmt[1] is TrSpace.k_world and fmt[2] is TrMode.k_flat:
            tr = self._data['transforms']['values']
        else:
            raise RmanAssetError('We only support world-space flat '
                                 'transforms !')
        return fmt, tr, ttype

    def __str__(self):
        return ('RmanAssetNode: class=%s rman=%s name=%s data=%s' %
                (self.nodeClass(), self.rmanNode(), self.name(), self._data))

    def __repr__(self):
        return self.__str__()

    ##
    # @brief      Evaluate a vstruct conditional expression for a downstream
    #             param.
    #
    # @param      self      The object
    # @param      dstNode   The destination node
    # @param      dstType   The destination parameter type
    # @param      dstParam  The destination param
    # @param      srcParam  The source param
    # @param      nodeDict  A dict containing all RmanAssetNode(s) by name
    #
    # @return     None
    #
    def vstructEval(self, dstNode, dstType, dstParam, srcParam, nodeDict):
        if srcParam in self._data['params']:
            # print self._data['params'][srcParam]
            try:
                expr = self._data['params'][srcParam]['vstructConditionalExpr']
            except:
                return ''
            obj = vstructAssets(dstNode, dstType, dstParam, self, srcParam)
            result = vstruct.evalExpr(expr, obj)

            # DEBUG ---------------------------------------
            if logLevel() == 3:
                print('=' * 80)
                print("EVAL: '%s' for %s" % (expr, dstParam))
                print(vstruct.getLastTrace())
                print ('result = %s   action = %s   value = %s' %
                       (repr(result), obj.actionGet(), obj.valueGet()))
            # ---------------------------------------------

            action = obj.actionGet()
            if action is not None:
                # the vstruct conditional expressions need to be recursively
                # parsed and evaluated, i.e. an expression can require the
                # value of a parameter that is itself a member of another
                # vstruct and whose value depend on another upstream expres-
                # sion.
                # Given that we evaluate nodes from leaf to root, any value
                # modified by an expression is written back in place to be
                # re-used by downstream nodes without further evaluation.
                #
                # dstParamDict is a pointer to the destination parameter that
                # may have its value modified.
                #
                dstParamDict = nodeDict[dstNode]._data['params'][dstParam]
                if action == 'connect':
                    rib = '"reference %s %s" ["%s:%s"]' % (dstType, dstParam,
                                                           self.name(),
                                                           srcParam)
                    # save to dst param
                    dstParamDict['type'] = 'reference %s' % dstType
                    dstParamDict['value'] = None
                elif action == 'copyParam':
                    pvalue = self._data['params'][obj.valueGet()]['value']
                    rib = '"%s %s" [%s]' % (dstType, dstParam, pvalue)
                    # save to dst param
                    dstParamDict['value'] = pvalue
                elif action == 'setNumber':
                    rib = '"%s %s" [%s]' % (dstType, dstParam, obj.valueGet())
                    # save to dst param
                    dstParamDict['value'] = obj.valueGet()
                elif action == 'setString':
                    rib = '"%s %s" [%s]' % (dstType, dstParam, obj.valueGet())
                    # save to dst param
                    dstParamDict['value'] = obj.valueGet()
                elif action == 'ignore':
                    rib = None

                if logLevel() == 3:
                    print('RIB: %s\n\n' % repr(rib))
                return rib
            else:
                if logLevel() == 3:
                    print('\n\n')
                return None
        else:
            err = ('RmanAssetNode::vstructEval : Unknown param of %s (%s) : %s'
                   % (self.name(), self.rmanNode(), srcParam))
            logWarning(err)
            return None

    ##
    # @brief      Generate RIB for this RmanAssetNode in the shading graph.
    #
    # @param      self            The object
    # @param      connectObjDict  The connect obj dict
    #
    # @return     RIB as a string
    #
    def getRIB(self, connectObjDict, nodeDict):
        rib = ''
        if self.nodeClass() == 'root':
            # output an empty string
            pass
        else:
            fmt, vals, trtype = self.transforms()
            hasTransform = (fmt is not None and vals is not None)
            if hasTransform:
                if fmt[2] is TrMode.k_flat:
                    rib += 'TransformBegin\n'
                    if fmt[0] is TrStorage.k_matrix:
                        rib += '  ConcatTransform %s\n' \
                               % str(vals).replace(',', '')
                    else:
                        rib += '  Scale %f %f %f\n' % (vals[6], vals[7],
                                                       vals[8])
                        rib += '  Rotate %f 1 0 0\n' % (vals[3])
                        rib += '  Rotate %f 0 1 0\n' % (vals[4])
                        rib += '  Rotate %f 0 0 1\n' % (vals[5])
                        rib += '  Translate %f %f %f\n' % (vals[0],
                                                           vals[1],
                                                           vals[2])
                else:
                    raise RmanAssetError('Unsupported transform RIB gen !'
                                         ' (hierarchical)')
            if self.nodeClass() == 'CoordinateSystem':
                # output a scoped coordinate system
                rib += '  ScopedCoordinateSystem "%s"\n' % self.name()
                rib += 'TransformEnd\n'
            elif trtype == TrType.k_coordsys:
                rib += '  ScopedCoordinateSystem "%s"\n' % self.name()
                rib += 'TransformEnd\n'

            # TODO: need to transfer this value instead of hard-coding it !
            if self.nodeClass().lower() == 'displace':
                # FIX ME !
                rib += ('Attribute "displacementbound" '
                        '"float sphere" [0.1]\n')

            rib += '''%s "%s" "%s"\n''' % (self.nodeClass().capitalize(),
                                           self.rmanNode(), self.handle())

            for (name, data) in self._data["params"].items():
                p = RmanAssetNodeParam(name, data)
                prib = p.getRIB(self.name(), connectObjDict, nodeDict)
                # prib == None for skipped params like vstruct inputs.
                if prib is not None:
                    rib += '    ' + prib + '\n'
            rib += '    "__instanceid" ["%s_0"]\n' % self.handle()
            if hasTransform and trtype is TrType.k_nodeTransform:
                rib += 'TransformEnd\n'
        return rib


class RmanAsset:

    ##
    # @brief      Constructor
    #
    # @param      self
    # @param      assetType  optional: the asset type ("nodeGraph" or "envMap"
    #                        )
    # @param      label      The asset's user-friendly label.
    #
    def __init__(self, assetType='', label='untitled'):
        '''lightweight constructor. If assetType is defined, the json skeleton
        will be constructed.'''

        self._json = {'RenderManAsset':
                      {'version': 1.0, 'label': label, 'asset': {}}}
        # file path in posix format
        self._jsonFilePath = ''
        self._version = 1.0
        self._validTypes = ['nodeGraph', 'envMap']
        self._label = label
        self._type = assetType
        self._meta = None
        self._asset = self._json['RenderManAsset']['asset']
        self._assetData = None
        self._externalFiles = []
        self._txmakeQueue = []
        self._convertToTex = False
        self._imageExts = ['.tif', '.exr', '.jpg', '.sgi', '.tga', '.iff',
                           '.dpx', '.bmp', '.hdr', '.png', '.env', '.gif',
                           '.ppm', '.xpm', '.z']
        self._textureExts = ['.tex', '.tx', '.ptx']
        if assetType != '':
            self.addAsset(assetType)
            # save standard metadata: time stamp
            ts = time.time()
            tformat = '%Y-%m-%d %H:%M:%S'
            st = datetime.datetime.fromtimestamp(ts).strftime(tformat)
            self._meta['created'] = st

    ##
    # @brief      Updates references to parts of the json data structure. This
    #             is called in addAsset() and Load().
    #
    # @param      self  This object.
    #
    def __updateAliases(self):
        self._asset = self._json['RenderManAsset']['asset']
        self._assetData = self._json['RenderManAsset']['asset'][self._type]
        self._meta = self._asset[self._type]['metadata']

    ##
    # @brief      Returns the asset's type : "nodeGraph" or "envMap"
    #
    # @param      self
    #
    # @return     The asset type (string)
    #
    def type(self):
        atype = self._type
        return atype

    ##
    # @brief      Returns the asset protocol's version
    #
    # @param      self
    #
    # @return     The version (float)
    #
    def version(self):
        avers = self._version
        return avers

    ##
    # @brief      Returns the label
    #
    # @param      self
    #
    # @return     The label (string)
    #
    def label(self):
        return self._label

    ##
    # @brief      Sets the asset's label
    #
    # @param      self
    # @param      label  The new label
    #
    # @return     none
    #
    def setLabel(self, label):
        self._label = label
        self._json['RenderManAsset']['label'] = label

    def creationTime(self):
        try:
            created = self._meta['created']
        except:
            created = '----/--/-- --:--:--'
        return created

    def addMetadata(self, key, val):
        self._meta[key] = val

    def getMetadata(self, key):
        try:
            val = self._meta[key]
        except:
            val = None
        return val

    ##
    # @brief      Returns the path to the asset's json file in posix format
    #
    # @param      self
    #
    # @return     none
    #
    def jsonFilePath(self):
        return self._jsonFilePath

    def path(self):
        return os.path.dirname(self.jsonFilePath())

    ##
    # @brief      Adds an asset to the skeleton and initialises it.
    #
    # @param      self
    # @param      atype  asset type : "nodeGraph" or "envMap"
    #
    # @return     none
    #
    def addAsset(self, atype):
        '''Inserts the relevant asset structure in the dictionnary'''
        if atype in self._validTypes:
            self.type = atype
            self._asset[atype] = {'metadata': {}, 'dependencies': []}
            # add compatibility data
            cdata = {'host': {'name': None, 'version': None},
                     'renderer': {'version': None},
                     'hostNodeTypes': []}
            self._asset[atype]['compatibility'] = cdata
            if atype == 'nodeGraph':
                self._asset[atype]['nodeList'] = {}
                self._asset[atype]['connectionList'] = []
            elif atype == 'envMap':
                self._asset[atype]['specs'] = {}
            self.__updateAliases()
        else:
            raise RmanAssetError('Unknown asset type : %s' % atype)

    ##
    # @brief      Adds a connection to a connectionList
    #
    # @param      self
    # @param      src   the source node and parameter, maya-style : node.attr
    # @param      dst   the destination node and parameter, maya-style :
    #                   node.attr
    #
    # @return     none
    #
    def addConnection(self, src, dst):
        if 'connectionList' not in self._assetData.keys():
            self._assetData['connectionList'] = []
        s = src.split('.')
        d = dst.split('.')
        con = {'src': {'node': s[0], 'param': s[1]},
               'dst': {'node': d[0], 'param': d[1]}}
        self._assetData['connectionList'].append(con)

    ##
    # @brief      Add a node to a nodeList
    #
    # @param      self      The object
    # @param      nid       node id / name
    # @param      ntype     node type
    # @param      nclass    bxdf, pattern, etc
    # @param      rmannode  The name of the corresponding RenderMan node.
    #
    # @return     none
    #
    def addNode(self, nid, ntype, nclass, rmannode, externalosl=False):
        if 'nodeList' not in self._assetData.keys():
            self._assetData['nodeList'] = OrderedDict()
        node = {'type': ntype, 'nodeClass': nclass, 'rmanNode': rmannode,
                'params': OrderedDict()}
        if externalosl:
            node['externalOSL'] = True
        # print 'addNode: %s' % node
        self._assetData['nodeList'][nid] = node

    ##
    # @brief      Add a tranform to a node in the nodeList.
    #
    # @param      self         none
    # @param      nid          the node's name
    # @param      floatValues  16 or 9 float values to specify the transform
    # @param      trStorage    storage type: default to matrix, i.e. 16 floats.
    # @param      trSpace      transform space: default to world.
    # @param      trType       transform type: default to flat, i.e. not
    #                          hierarchical.
    #
    # @return     none
    #
    def addNodeTransform(self, nid, floatValues, trNames=None,
                         trStorage=TrStorage.k_matrix,
                         trSpace=TrSpace.k_world,
                         trMode=TrMode.k_flat,
                         trType=TrType.k_coordsys):
        if floatValues is None:
            print('addNodeTransform: "%s"' % nid)
            print(str(self._json).replace(',', ',\n'))
            raise RmanAssetError('Bad float values in addNodeTransform')
        if 'transform' not in self._assetData['nodeList'][nid]:
            self._assetData['nodeList'][nid]['transforms'] = {}

        Tnode = self._assetData['nodeList'][nid]['transforms']

        # error checking
        if trSpace != TrSpace.k_world:
            raise RmanAssetError(
                'World-space only ! Other spaces not implemented yet...')
        if trMode != TrMode.k_flat:
            raise RmanAssetError(
                'Flat tranform only ! Other modes not implemented yet...')

        # store configuration
        Tnode['format'] = (trStorage, trSpace, trMode)

        if trMode == TrMode.k_flat:
            # In k_flat mode, we store all the values as a single array of
            # floats. For k_matrix, we get 16 values, for k_TRS we get 9
            # values.
            if trSpace != TrSpace.k_world:
                raise RmanAssetError('Values MUST be in world space '
                                     'for flat storage !')

            numValues = len(floatValues)
            if trStorage == TrStorage.k_matrix and numValues != 16:
                    raise RmanAssetError('Need 16 floats in matrix modes :'
                                         ' %d passed !' % numValues)
            elif trStorage == TrStorage.k_TRS and numValues != 9:
                    raise RmanAssetError('Need 9 floats in TRS modes :'
                                         ' %d passed !' % numValues)

            Tnode['values'] = floatValues

        elif trMode is TrMode.k_hierarchical:

            if trSpace is not TrSpace.k_object:
                raise RmanAssetError('Values MUST be in object space for '
                                     'hierarchical storage !')

            # In k_hierarchical mode, we store an array of tuples. Each tuple
            # decribes a transform. They are ordered bottom to top.
            # in that case, we expect floatValues to be an array of float
            # arrays and trNames to be an array of transform names.
            Tnode['values'] = []
            for name, vals in trNames, floatValues:
                Tnode['values'].append(name, vals)
        else:
            raise RmanAssetError('Unknown transform mode : %d' % trMode)

        Tnode['type'] = trType

    ##
    # @brief      Add a param to a node in a nodelist.
    #
    # @param      self   The object
    # @param      nid    node id / name
    # @param      param  name of the parameter.
    # @param      pdict  dict containing param data
    #
    # @return     none
    #
    def addParam(self, nid, param, pdict):
        # print '+ addParam %s.%s  = %s' % (nid, param, pdict)
        theNode = self._assetData['nodeList'][nid]
        # we don't want to store all specs of output parameters.
        if 'output ' in pdict['type']:
            d = pdict
            unwanted = ['value', 'default']
            for k in unwanted:
                if k in d:
                    del d[k]
            theNode['params'][param] = d
            return
        # any external file path should be localized
        if pdict['type'] == 'string':
            pdict['value'] = self.processExternalFile(pdict['value'])
        # add the parameter to the list
        theNode['params'][param] = pdict

    ##
    # @brief      Save the asset as a json file
    #
    # @param      self
    # @param      filepath  Absolute path to the json file
    # @param      compact   Don't prettify the json. Defaults to False.
    #
    # @return     none
    #
    def save(self, filepath, compact=False):
        self.registerUsedNodeTypes()
        try:
            fh = open(filepath, 'w')
        except:
            RmanAssetError('Could not create file : %s', filepath)
        if compact:
            json.dump(self._json, fh)
        else:
            json.dump(self._json, fh, sort_keys=False, indent=4,
                      separators=(',', ': '))
        fh.close()
        self._jsonFilePath = internalPath(filepath)
        self.txmake()
        self.gatherExternalFiles()

    ##
    # @brief      Load a json asset file, checks its version and store the type
    #             and label
    #
    # @param      self
    # @param      filepath  The json file's absolute path in posix format
    #
    # @return     none
    #
    def load(self, filepath, localizeFilePaths=False):
        try:
            fh = open(externalPath(filepath), 'r')
        except:
            err = 'Could not open file : %s : %s' % (externalPath(filepath),
                                                     sysErr())
            raise RmanAssetError(err)
        try:
            self._json = json.load(fh)
        except:
            err = 'Failed to parse: %s : %s' % (externalPath(filepath),
                                                sysErr())
            raise RmanAssetError(err)
        fh.close()

        if float(self.version()) > 1.0:
            raise RmanAssetError('Can not read file version > %f' %
                                 self.version())

        self._type = list(self._json['RenderManAsset']['asset'].keys())[0]
        # print 'load type: %s' % self._type
        self._label = self._json['RenderManAsset']['label']
        self._jsonFilePath = internalPath(filepath)
        self.__updateAliases()
        if 'dependencies' in self._assetData:
            self._externalFiles = self._assetData['dependencies']
        if localizeFilePaths:
            self.localizeExternalFiles()

    ##
    # @brief      Outputs the json dict as a pretty string
    #
    # @param      self
    # @return     string
    #
    def __str__(self):
        return json.dumps(self._json, sort_keys=False, indent=4,
                          separators=(',', ': '))

    ##
    # @brief      Return the nodeList as a list of RmanAssetNode objects.
    #
    # @param      self
    #
    # @return     a list of RmanAssetNode objects.
    #
    def nodeList(self):
        if self._type != 'nodeGraph':
            raise RmanAssetError('%s asset types do not have ',
                                 'a node list !' % self._type)
        nodes = []
        for (name, data) in self._assetData['nodeList'].items():
            nodes.append(RmanAssetNode(name, data))
        return nodes

    ##
    # @brief      Return the connectionList as a list of
    #             RmanAssetNodeConnection objects.
    #
    # @param      self
    #
    # @return     A list of RmanAssetNodeConnection objects
    #
    def connectionList(self):
        if self._type != 'nodeGraph':
            raise RmanAssetError('%s asset types do not have a ',
                                 'connection list !' % self._type)
        clist = []
        for c in self._assetData['connectionList']:
            clist.append(RmanAssetNodeConnection(c))
        return clist

    ##
    # @brief      Create standard metadata fields : 'created', 'author',
    #             'version'. Note: this is the asset's version, not the
    #             protocol's version, which is at the top of the scope.
    #
    # @param      self
    #
    # @return     none
    #
    def stdMetadata(self):
        infos = {'created': self.creationTime()}
        try:
            infos['author'] = self._meta['author']
        except:
            infos['author'] = '-'
        try:
            infos['version'] = self._meta['version']
        except:
            infos['version'] = '1'
        return infos

    ##
    # @brief      Convert images files to textures.
    #
    # @param      self  none
    #
    # @return     none
    #
    def txmake(self):
        assetdir = os.path.dirname(self.jsonFilePath())
        rmantree = internalPath(envGet('RMANTREE'))
        txmake = externalPath(os.path.join(rmantree, 'bin', app('txmake')))
        cmd = [txmake]
        # print 'txmake for %s' % self._type
        if self._type == 'envMap':
            cmd += ['-envlatl',
                    '-filter', 'box',
                    '-format', 'openexr',
                    '-compression', 'pxr24',
                    '-newer',
                    'src', 'dst']
        else:
            cmd += ['-resize', 'round-',
                    '-mode', 'periodic',
                    '-format', 'pixar',
                    '-compression', 'lossless',
                    '-newer',
                    'src', 'dst']
        for img in self._txmakeQueue:
            cmd[-2] = externalPath(img)
            dirname, filename = os.path.split(img)
            cmd[-1] = externalPath(os.path.join(assetdir,
                                   os.path.splitext(filename)[0] + '.tex'))
            print ('> Converting to texture :\n    %s -> %s' %
                   (cmd[-2], cmd[-1]))
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 startupinfo=startupInfo())
            p.wait()

    ##
    # @brief      identify and process external files like textures.
    #
    # @param      self
    # @param      stringvalue  The parameter value, potentialy a file path.
    #
    # @return     a relative filepath.
    #
    def processExternalFile(self, stringvalue):
        logExternalFiles('>> processExternalFile: %s' % stringvalue)
        if os.path.isfile(stringvalue):
            # single file
            logExternalFiles('  > it is a file')
            texturefile = stringvalue
            path, filename = os.path.split(stringvalue)
            fname, ext = os.path.splitext(filename)
            if ext.lower() in self._imageExts:
                logExternalFiles('  > this is an image and needs to be txmade')
                texturefile = fname + '.tex'
                # This is an image : add the file to our txmake queue
                if ext not in self._textureExts:
                    logExternalFiles('  > added to txmake queue')
                    self._txmakeQueue.append(stringvalue)
                else:
                    logExternalFiles('  > already in txmake queue')
                # add to the list of files we may need to copy to the
                # asset dir.
                self._externalFiles.append(texturefile)
                logExternalFiles('  > add to list of files to copy: %s'
                                 % texturefile)
                # register the path in the dependency list.
                self._assetData['dependencies'].append(texturefile)
                logExternalFiles('  > add to dependencies: %s'
                                 % texturefile)
                return texturefile
            else:
                # add to the list of files we may need to copy to the
                # asset dir.
                self._externalFiles.append(stringvalue)
                logExternalFiles('  > add to list of files to copy: %s'
                                 % stringvalue)
                # register the path in the dependency list.
                self._assetData['dependencies'].append(filename)
                logExternalFiles('  > add to dependencies: %s'
                                 % filename)
                return filename
        elif '__MAPID__' in stringvalue:
                logExternalFiles('  > it is a texture atlas')
                # texture atlas : we don't txmake them for now.
                path, filename = os.path.split(stringvalue)
                # add to the list of files we may need to copy to the
                # asset dir.
                fileglob = replace(stringvalue, '__MAPID__', '*')
                self._externalFiles.append(fileglob)
                logExternalFiles('  > add to list of files to copy: %s'
                                 % fileglob)
                # register the path in the dependency list.
                self._assetData['dependencies'].append(filename)
                logExternalFiles('  > add to dependencies: %s'
                                 % filename)
                return filename
        else:
            logExternalFiles('  > not a file : only escape...')
            return str(stringvalue).encode('unicode_escape').decode('utf-8')

    ##
    # @brief      Copies all referenced files (textures) to the asset
    #             directory.
    #
    # @param      self
    #
    # @return     None
    #
    def gatherExternalFiles(self):
        # print 'external files: %s' % self._externalFiles
        if len(self._externalFiles):
            root = os.path.split(self._jsonFilePath)[0]
            for dep in self._externalFiles:
                # print dep
                src = []
                if os.path.isfile(dep):
                    src.append(dep)
                elif '*' in dep:
                    src = glob.glob(dep)
                for s in src:
                    srcp = s
                    dstp = os.path.join(root, os.path.basename(s))
                    print('> copy external file : %s -> %s' % (srcp, dstp))
                    try:
                        shutil.copy(externalPath(srcp), externalPath(dstp))
                    except:
                        # is the file already there ?
                        this_is_wrong = True
                        if os.path.exists(dstp):
                            # is it the exact same file ?
                            if filecmp.cmp(externalPath(dstp),
                                           externalPath(srcp)):
                                # this is the same file : nothing to do
                                this_is_wrong = False
                        if this_is_wrong:
                            print('Could not copy: %s to %s' % (srcp, dstp))
                            print('>> Unexpected error:', sys.exc_info()[0])
                            raise
        else:
            print('> no external file to copy')

    ##
    # @brief      modifies the texture paths to point to the asset directory
    #
    # @param      self
    #
    # @return     None
    #
    def localizeExternalFiles(self):
        if 'nodeList' not in self._assetData:
            return

        root = os.path.dirname(self._jsonFilePath)

        for (nk, nv) in self._assetData['nodeList'].items():
            # print ('nk=%s' % nk)
            for (pk, pv) in nv['params'].items():
                # print ('+ pk=%s pv=%s' % (pk,pv))
                Pnode = self._assetData['nodeList'][nk]['params'][pk]
                if 'string' not in pv['type']:
                    continue
                if '[' in pv['type']:
                    for i in range(len(pv['value'])):
                        if pv['value'][i] not in self._externalFiles:
                            continue
                        Pnode['value'][i] = os.path.join(root, pv['value'][i])
                else:
                    if pv['value'] in self._externalFiles:
                        Pnode['value'] = os.path.join(root, pv['value'])

    ##
    # @brief      Gets the path to a dependency file (*.tex, *.oso, etc).
    #
    # @param      self           The object
    # @param      shortFileName  The short file name, i.e. 'diffmap.tex'
    #
    # @return     The fully qualified dependency path.
    #
    def getDependencyPath(self, shortFileName):
        root = os.path.dirname(self._jsonFilePath)
        depfile = os.path.join(root, shortFileName)
        # print 'depfile = %s' % depfile
        if os.path.exists(depfile):
            # print 'depfile exists'
            return depfile
        else:
            # print 'depfile missing'
            return None

    ##
    # @brief      topological sort of our shading graph
    #
    # @param      self            none
    # @param      graph_unsorted  A dict describing all edges of each node. It
    #                             should look like this:
    #                             {0:[8,2], 1:[12,15], 2:[6], 3:[12,11], ...}
    #
    # @return     A sorted version of the input graph.
    #
    def topo_sort(self, graph_unsorted):
        graph_sorted = []
        graph_unsorted = dict(graph_unsorted)

        while graph_unsorted:
            acyclic = False
            for node, edges in list(graph_unsorted.items()):
                for edge in edges:
                    if edge in graph_unsorted:
                        break
                else:
                    acyclic = True
                    del graph_unsorted[node]
                    graph_sorted.append((node, edges))
            if not acyclic:
                raise RmanAssetError('Cyclic dependency detected !')

        return graph_sorted

    ##
    # @brief      Output RIB for this asset. First, we build an unordered graph
    #             and sort it, to be able to output the RIB statements in the
    #             right order.
    #
    # @param      self  this object
    #
    # @return     a RIB string
    #
    def getRIB(self):
        nodes = self.nodeList()
        conns = self.connectionList()

        # build a nodename to idx dict
        namedict = {}
        for i in range(len(nodes)):
            namedict[nodes[i].name()] = i

        # build a dependency list / unordered graph
        deps = {}
        for i in range(len(nodes)):
            deps[i] = []
            for c in conns:
                if c.dstNode() == nodes[i].name():
                    deps[i].append(namedict[c.srcNode()])
        # print deps

        # sort the graph, leaf to root
        sortedgraph = self.topo_sort(deps)
        # print sortedgraph

        # pass a node dict to simplify vstruct lookups
        nodeDict = {}
        for n in nodes:
            nodeDict[n.name()] = n

        rib = ''
        for g in sortedgraph:
            #  build a paramname:'srcnode:srcparam' dict for connections
            cnx = {}
            thisnode = nodes[g[0]]
            for i in g[1]:
                for c in conns:
                    if c.dstNode() == thisnode.name():
                        # make sure the node handle doesn't contain a ':' !
                        cnx[c.dstParam()] = '%s:%s' % (c.srcNodeHandle(),
                                                       c.srcParam())
            # print '\ncnx: %s -> %s' % (thisnode.name(), cnx)
            rib += thisnode.getRIB(cnx, nodeDict)
        # print '-'*70
        # print rib
        # print '-'*70
        return rib

    ##
    # @brief      Gather infos from an image's header. We use sho for now, but
    #             hopefuly we will switch to OpenImage IO in the future.
    #
    # @param      self  this object
    # @param      img   Full path to the image file
    #
    # @return     The spec dictionnary stored in the json file.
    #
    def getTextureHeader(self, img):
        specs = {}
        if os.path.exists(img):
            rmantree = internalPath(envGet('RMANTREE'))
            sho = os.path.join(rmantree, 'bin', app('sho'))
            cmd = [externalPath(sho), '-info', externalPath(img)]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 startupinfo=startupInfo(),
                                 bufsize=-1)
            out, err = p.communicate()
            # print out
            # print err
            toks = err.split('\n')
            for tok in toks:
                tok = re.sub('\s{2,50}', '\t', tok)
                kv = tok.split('\t')
                if len(kv) < 2:
                    continue
                try:
                    specs[kv[0]] = eval(kv[1])
                except:
                    if '(' in kv[1]:
                        kv[1] = re.sub('\s', ',', kv[1])
                    try:
                        specs[kv[0]] = eval(kv[1])
                    except:
                        specs[kv[0]] = kv[1]
        else:
            err = 'Invalid image path : %s' % img
            raise RmanAssetError(err)
        return specs

    ##
    # @brief      Build the spec dict and stores it in the json struct.
    #
    # @param      self  this object
    # @param      img   full path to the image file.
    #
    def addTextureInfos(self, img):
        # which format is it ?
        fspecs = self.getTextureHeader(img)
        specFields = {'Original File Format': 'originalFormat',
                      'Original Size': 'originalSize',
                      'Original Bits Per Sample': 'originalBitDepth',
                      'Image Description': 'description',
                      'Display Window Origin': 'displayWindowOrigin',
                      'Display Window Size': 'displayWindowSize'}
        for k, v in specFields.items():
            try:
                val = fspecs[k]
            except:
                raise RmanAssetError('Could not read %s !' % k)
            self._assetData["specs"][v] = val
        tex = self.processExternalFile(img)
        self._assetData["specs"]['filename'] = tex

    ##
    # @brief      Returns the name of the environment map
    #
    # @param      self  this object
    #
    # @return     the name as a string
    #
    def envMapName(self):
        if self._type != 'envMap':
            raise RmanAssetError('This is not an envMap asset !')
        name = self._assetData["specs"]['filename']
        # print 'envMapName: %s' % name
        return name

    ##
    # @brief      Returns the full path to the assets's environment texture
    #             file.
    #
    # @param      self  this object
    #
    # @return     the path as a string
    #
    def envMapPath(self):
        if self._type != 'envMap':
            print(self)
            raise RmanAssetError('%s is not an envMap asset !' % self._label)
        fpath = os.path.dirname(self._jsonFilePath)
        # print 'envMapPath: %s' % fpath
        fpath = os.path.join(fpath, self.envMapName())
        # print 'envMapPath: %s' % fpath
        return fpath

    ##
    # @brief      Allows an asset exporter to register host-specific node
    #             types. They will be saved in the json file so another
    #             importer may decide if they can safely rebuild this asset.
    #
    # @param      self      this object
    # @param      nodetype  The node type to register. It will only be added if
    #                       not already in the list.
    #
    def registerHostNode(self, nodetype):
        cdata = self._assetData['compatibility']
        if nodetype not in cdata['hostNodeTypes']:
            cdata['hostNodeTypes'].append(nodetype)

    ##
    # @brief      Set the values of the compatibility dict
    #
    # @param      self             this object
    # @param      hostName         The application in which that asset was
    #                              created (Maya, Katana, Houdini, Blender,
    #                              etc)
    # @param      hostVersion      The host app's version string. The version
    #                              string should be compatible with python's
    #                              distutils.version module for comparison
    #                              purposes. Should contain at least one dot.
    #                              If not, add '.0' to your version string.
    # @param      rendererVersion  The current version of the renderer. Should
    #                              contain at least one dot. If not, add '.0'
    #                              to your version string.
    #
    def setCompatibility(self, hostName=None, hostVersion=None,
                         rendererVersion=None):
        cdata = self._assetData['compatibility']
        if hostName is not None:
            cdata['host']['name'] = hostName
        if hostVersion is not None:
            cdata['host']['version'] = hostVersion
        if rendererVersion is not None:
            cdata['renderer']['version'] = rendererVersion

    ##
    # @brief      Called by importers to check if this asset can be safely
    #             imported. Potential incompatibilities will trigger a message.
    #             We only return False if the asset contains host-specific
    #             nodes for which we have no replacement. To support foreign
    #             host-specific nodes, an importer can implement an equivalent
    #             node with the same name and inputs/outputs and make sure they
    #             appear in the validNodeTypes list.
    #
    # @param      self             this object
    # @param      hostName         The importer's host
    # @param      hostVersion      The importer's host version. Should contain
    #                              at least one dot. If not, add '.0' to your
    #                              version string.
    # @param      rendererVersion  The current renderer version. Should contain
    #                              at least one dot. If not, add '.0' to your
    #                              version string.
    # @param      validNodeTypes   A list of node types the importer can safely
    #                              handle.
    #
    # @return     True if compatible, False otherwise.
    #
    def IsCompatible(self, hostName=None, hostVersion=None,
                     rendererVersion=None, validNodeTypes=[]):
        try:
            cdata = self._assetData['compatibility']
        except:
            # if the compatibility data is missing, we are dealing with an
            # old file.
            print('Warning: compatibility data is missing')
            return True

        sameHostOK = False
        if hostName is not None:
            if cdata['host']['name'] == hostName:
                sameHostOK = True

        if hostVersion is not None:
            try:
                assetVersion = dv.StrictVersion(cdata['host']['version'])
                thisVersion = dv.StrictVersion(hostVersion)
            except:
                assetVersion = dv.LooseVersion(cdata['host']['version'])
                thisVersion = dv.LooseVersion(hostVersion)
            if assetVersion <= thisVersion:
                pass
            else:
                if len(cdata['hostNodeTypes']) > 0:
                    print ('This asset contains %s %s nodes and may not '
                           'be compatible' % (cdata['host']['name'],
                                              cdata['host']['version']))

        if rendererVersion is not None:
            try:
                assetVersion = dv.StrictVersion(cdata['renderer']['version'])
                thisVersion = dv.StrictVersion(rendererVersion)
            except:
                assetVersion = dv.LooseVersion(cdata['renderer']['version'])
                thisVersion = dv.LooseVersion(rendererVersion)
            if assetVersion <= thisVersion:
                pass
            else:
                print ('This asset was created for RenderMan %s and may not '
                       'be compatible' % (cdata['renderer']['version']))

        if not sameHostOK:
            # Are there any host-specific nodes in that asset ?
            # If not, we consider this asset compatible.
            pass
            # if len(cdata['hostNodeTypes']) > 0:
            #     # if the validNodeTypes list has been passed, check if we have
            #     # all required nodes...
            #     allHostNodesAreAvailable = False
            #     if len(validNodeTypes):
            #         allHostNodesAreAvailable = True
            #         for n in cdata['hostNodeTypes']:
            #             if n not in validNodeTypes:
            #                 allHostNodesAreAvailable = False
            #                 break
            #     if not allHostNodesAreAvailable:
            #         print(cdata['renderer']['version'], cdata['hostNodeTypes'])
            #         #print ('This asset was created with %s %s and is not '
            #         #       'compatible' % (cdata['renderer']['version']))
            #         #print('Missing node types : %s' % cdata['hostNodeTypes'])
            #     return False

        return True

    def registerUsedNodeTypes(self):
        nodetypes = []
        if self._type is 'nodeGraph':
            for k, v in self._assetData['nodeList'].items():
                nodetypes.append(v['rmanNode'])
        self._json['RenderManAsset']['usedNodeTypes'] = nodetypes

    def getUsedNodeTypes(self, asString=False):
        unt = ['no data']
        try:
            unt = self._json['RenderManAsset']['usedNodeTypes']
        except:
            # compatibility mode - to be removed soon.
            # print '%s: trying old usedNodeTypes' % self.label()
            try:
                unt = self._json['usedNodeTypes']
            except:
                # print '%s: no usedNodeTypes' % self.label()
                pass
        if asString:
            return ' '.join(unt)
        else:
            return unt


#
# These functions are meant to be called from non-python scripts, namely MEL.
#


def read(jsonfile):
    global __lastJson
    try:
        jf = open(jsonfile, 'r')
    except:
        return
    __lastJson = json.load(jf)
    jf.close()


def assetType(jo=None):
    global __lastJson
    if jo is None:
        jo = __lastJson
    return list(jo['RenderManAsset']['asset'])[0]
