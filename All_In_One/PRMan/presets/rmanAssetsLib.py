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

from . import rmanAssets as ra
import os
import os.path
import shutil
import re
import sys
import subprocess
import time
import tempfile
import multiprocessing

from .rmanAssets import internalPath, externalPath, app

# the path to our library
#
__rmanLibraryPath = ''


# debug utilities

__debugPreview = False


##
# @brief      Enables preview debugging. For now, it just saves the material
#             RIB if a rendering error was detected.
#
# @param      state  True or False
#
# @return     None
#
def setDebugPreview(state):
    global __debugPreview
    __debugPreview = state


##
# @brief      Returns the debug state
#
# @return     boolean value
#
def debugPreview():
    global __debugPreview
    return __debugPreview


##
# @brief      Helper to get the last exception message string.
#
# @return     system error message string
#
def sysErr():
    if len(sys.exc_info()) > 1 and isinstance(sys.exc_info()[1], Exception):
        return sys.exc_info()[1][1]
    return sys.exc_info()[0]


##
# @brief      Exception class to tell the world about our miserable failings.
#
class RmanAssetLibError(Exception):

    def __init__(self, value):
        self.value = "RmanAssetLib Error: %s" % value

    def __str__(self):
        return repr(self.value)


##
# @brief      Builds a filename from the asset label string
#
# @param      label  User-friendly label
#
# @return     the asset file name
#
def assetNameFromLabel(label):
    assetDir = re.sub('[^\w]', '', re.sub(' ', '_', label)) + '.rma'
    return assetDir


##
# @brief      Returns a valid path to a RenderManAssetLibrary directory. If
#             the directory doesn't exist, it will be created.
#
# @param      path  full path to the RenderManAssetLibrary directory.
#
# @return     valid path
#
def validateLibraryRoot(path):
    if not os.path.exists(path):
        raise RmanAssetLibError('Invalid path: %s' % path)
    rootname = 'RenderManAssetLibrary'
    libroot = path
    # we always create a RenderManAssetLibrary directory to store our assets.
    if rootname not in path:
        libroot = os.path.join(path, rootname)
        if not os.path.exists(libroot):
            os.mkdir(libroot)
    else:
        if os.path.basename(libroot) != rootname:
            # we are inside the library, make sure we are at the root
            while os.path.basename(libroot) != rootname:
                libroot = os.path.dirname(libroot)
    return libroot


##
# @brief      Creates the default catgories in a brand new library, if they
#             don't exist yet.
#
# @param      path  Location of the new library
#
# @return     none
#
def initLibrary(path):
    libroot = validateLibraryRoot(path)
    # now, we initialize the minimal directory structure.
    defaultCategories = {'Materials', 'LightRigs', 'EnvironmentMaps'}
    depth = 0
    for root, dirs, files in os.walk(libroot):
        if depth == 0 and len(dirs) == 0:
            for cat in defaultCategories:
                dirpath = os.path.join(root, cat)
                if not os.path.exists(dirpath):
                    os.mkdir(dirpath)
        depth += 1
        # we only create top categories for now.
        if depth > 0:
            break
    return libroot


##
# @brief      Returns the path to the asset library's root directory, in
#             os.path/posix format. If the library can not return a valid path,
#             we raise an exception to allow the caller to choose a default or
#             ask the user for guidance.
#
# @return     path as a string
#
def getLibraryPath():
    global __rmanLibraryPath
    root = ''

    if __rmanLibraryPath != '':
        root = __rmanLibraryPath

    elif ra.envExists('RMAN_ASSET_LIBRARY'):
        #  If not, we check the RMAN_ASSET_LIBRARY environment variable. If
        #  available, we store the path in out optionVar and return it.
        root = internalPath(ra.envGet('RMAN_ASSET_LIBRARY'))
        if not os.path.exists(root):
            err = "Invalid Library path in RMAN_ASSET_LIBRARY: '%s'" % root
            raise RmanAssetLibError(err)
    elif root == '':
        # The standard library installed with RPS will be used as the default,
        # if found.
        root = internalPath(ra.envGet('RMANTREE'))
        root = os.path.join(root, 'lib', 'RenderManAssetLibrary')
        if not os.path.exists(root):
            root = ''
    elif root == '':
        raise RmanAssetLibError('RenderMan Asset Library path undefined !!')

    # print 'Library path: %s' % root
    root = initLibrary(root)
    __rmanLibraryPath = root
    return root


##
# @brief      Set the library path. The path is stored in a global.
#
# @param      path  A fully validated path that should end with
#                   'RenderManAssetLibrary'. We don't validate this path.
#
def setLibraryPath(path):
    global __rmanLibraryPath
    __rmanLibraryPath = validateLibraryRoot(path)


##
# @brief      Add a category as a relative path, i.e. 'Materials/Metals'
#
# @param      relpath  A relative path to the new category folder
#
# @return     none
#
def createCategory(relpath):
    root = getLibraryPath()
    fullpath = os.path.join(root, relpath)
    if not os.path.exists(fullpath):
        os.mkdir(fullpath)
    else:
        print('Skipped: Category already exists : %s' % relpath)


##
# @brief      Delete a category and its contents
#
# @param      relpath  A relative path to the library folder
#
# @return     none
#
def deleteCategory(relpath):
    root = getLibraryPath()
    fullpath = os.path.join(root, relpath)
    if os.path.exists(fullpath):
        try:
            shutil.rmtree(fullpath)
        except:
            err = 'deleteCategory %s failed: %s' % (fullpath, sysErr())
            raise RmanAssetLibError(err)
    else:
        print('''Warning: Category doesn't exists : %s''' % relpath)


##
# @brief      Return the parent category when passed a relative category path
#
# @param      relpath  relative path to category
#
# @return     string
#
def parentCategory(relpath):
    return (os.path.basename(relpath))


##
# @brief      Returns a fully qualified path to the category
#
# @param      relpath  relative path to the category, i.e. "lights/env"
#
# @return     absolute path (string)
#
def getAbsCategoryPath(relpath):
    root = getLibraryPath()
    fullpath = os.path.join(root, relpath)
    if not os.path.exists(fullpath):
        raise RmanAssetLibError("Invalid category: %s" % relpath)
    return internalPath(fullpath)


##
# @brief      Return all categories as relative paths.
#
# @return     list of categories as relative paths (string).
#
def getAllCategories():
    lib = getLibraryPath()
    liblen = len(lib) + 1
    categories = []
    for root, dirs, files in os.walk(lib):
        for d in dirs:
            if d[-4:] == ".rma":
                continue
            if "DS_Store" in d:
                continue
            categories.append(internalPath(os.path.join(root[liblen:], d)))
    return categories


##
# @brief      Returns all asset names for a given category.
#
# @param      relpath  relative path to the category.
#
# @return     list of assets as relative paths (string).
#
def getAssetList(relpath):
    lib = getLibraryPath()
    liblen = len(lib) + 1
    assets = []
    for root, dirs, files in os.walk(os.path.join(lib, relpath)):
        for d in dirs:
            if d[-4:] == ".rma":
                assets.append(internalPath(os.path.join(root[liblen:], d)))
    return assets


##
# @brief      Move an asset to another category.
#
# @param      srcPath   full path to the asset directory
# @param      category  relative category path
#
# @return     none
#
def moveAsset(srcPath, category):
    dst = os.path.join(getLibraryPath(), category)
    # print 'moving %s to %s' % (srcPath, dst)
    try:
        shutil.move(srcPath, dst)
    except:
        msg = 'moving %s to %s\n' % (srcPath, dst)
        msg += 'Could not move asset to new location : %s' % sysErr()
        raise RmanAssetLibError(msg)


##
# @brief      Class used by renderAssetPreview to report progress back to the
#             host application. If no object is passed, this class just prints
#             out progress messages to std out.
#
class DefaultProgress:
    def Start(self):
        print('Rendering asset preview...')

    def Update(self, val, msg=None):
        if msg is None:
            print(' %d...' % val)
        else:
            print(' %d : %s...' % (val, msg))

    def End(self):
        print('Render finished.')


##
# @brief      Class used by renderAssetPreview to resize the original render to
#             make a smaller preview image. The input and output images are in
#             PNG format.
#
class DefaultResizer:
    def __init__(self):
        self.cmd = None
        candidates = [['oiiotool', '-v'], ['convert', '-version']]
        cmd = {'convert':
               'convert|%(src)s|-resize|%(size)dx%(size)d|%(dst)s',
               'oiiotool':
               'oiiotool|%(src)s|--resize|%(size)dx%(size)d|-o|%(dst)s'}

        # if some utilities have only been installed on the current profile,
        # '/usr/local/bin' may be missing from the environment.
        #
        self.paths = os.environ['PATH']
        if os.name == 'posix' and '/usr/local/bin' not in self.paths:
            self.paths += ':/usr/local/bin'

        for c in candidates:
            rt = 1
            p = None

            try:
                p = subprocess.Popen(c,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     env={'PATH': self.paths},
                                     startupinfo=ra.startupInfo())
            except:
                # print 'no: %s : %s' % (c, sysErr())
                continue

            rt = p.wait()
            if rt == 0:
                self.cmd = cmd[c[0]]
                break
            else:
                print('no: %s : return code = %d' % (c, rt))
        # print 'cmd is %s' % self.cmd

    def Resize(self, size, srcfile, dstfile):
        if self.cmd is None:
            return

        cmd = self.cmd % {'size': int(size),
                          'src': str(srcfile),
                          'dst': str(dstfile)}
        cmdlist = cmd.split('|')
        # print " ".join(cmdlist)
        p = subprocess.Popen(cmdlist,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env={'PATH': self.paths},
                             startupinfo=ra.startupInfo())
        retcode = p.wait()
        if retcode != 0:
            print('return code: %d' % retcode)
        elapsed = 0
        while not os.path.exists(dstfile):
            if elapsed >= 2.0:
                print ("Warning: small preview still missing after 2 sec : %s"
                       % dstfile)
                break
            elapsed += 0.5
            time.sleep(0.5)
        # print 'resize done: %d wait' % elapsed


##
# @brief      Render preview png images for a given asset.
#
# @param      Asset     The asset used to generate the preview images.
# @param      progress  An object used to report progress back to the host. It
#                       must implements 3 methods : Start(),
#                       Update(progressValue) and End()
# @param      resize    An object used to resize the initial render. It must
#                       implement the following method : Resize(size, srcfile,
#                       dstfile)
#
# @return     none
#
def renderAssetPreview(Asset, progress=None, resize=None):

    rmstree = internalPath(ra.envGet('RMAN_ASSET_LIBRARY'))
    rmantree = internalPath(ra.envGet('RMANTREE'))

    progressReporter = progress
    if progress is None:
        progressReporter = DefaultProgress()
    resizer = resize
    if resize is None:
        resizer = DefaultResizer()

    # start progress report
    #
    assetName = Asset.label()
    progressReporter.Start()
    progressReporter.Update(0, 'Setting up render : %s' % assetName)

    # get the main RIB file
    #
    ribroot = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RenderManAssets')
    if not os.path.exists(ribroot):
        progressReporter.End()
        raise RmanAssetLibError('BAD ROOT PATH: %s' % ribroot)
    # print(" - renderAssetPreview: rib root = %s" % ribroot)

    # copy all necessary files to a tmp dir : some users may not have write
    # permission in the install directory
    tmpdir = os.path.join(internalPath(tempfile.gettempdir()),
                          'RenderManAssets')
    # print "tmp: %s" % repr(tmpdir)

    # make sure it's clean
    try:
        shutil.rmtree(externalPath(tmpdir))
    except:
        pass

    if not os.path.exists(tmpdir):
        try:
            shutil.copytree(ribroot, externalPath(tmpdir))
        except:
            progressReporter.End()
            RmanAssetLibError('Could not copytree: %s' % sysErr())

    # get the main RIB file
    ribfile = os.path.join(tmpdir, 'materialSample_v1.rib')
    if not os.path.exists(ribfile):
        progressReporter.End()
        raise RmanAssetLibError('BAD RIB PATH: %s' % ribfile)
    # print(" - renderAssetPreview: rib file = %s" % repr(ribfile))

    # build a material rib
    #
    af = internalPath(Asset.jsonFilePath())
    matdir = internalPath(os.path.dirname(af))
    # print(" - renderAssetPreview: matdir = %s" % repr(matdir))
    matribfile = os.path.join(matdir, 'm_shading.rib')
    if Asset._type == 'envMap':
        # use preset material
        envMapMaterial = os.path.join(tmpdir, 'm_shadingEnvMap.rib')
        if not os.path.exists(envMapMaterial):
            progressReporter.End()
            raise RmanAssetLibError('missing rib file: %s' % envMapMaterial)
        shutil.copy(externalPath(envMapMaterial), externalPath(matribfile))
    else:
        mr = open(externalPath(matribfile), 'w')
        mr.write(Asset.getRIB())
        mr.close()
    if not os.path.exists(matribfile):
        progressReporter.End()
        raise RmanAssetLibError('MISSING MAT RIB : %s' % matribfile)
    # print(" - renderAssetPreview: mat rib = %s" % repr(matribfile))

    # define the light rig
    #
    lightrig = 'winter'
    if Asset._type == 'envMap':
        lribfile = os.path.join(tmpdir, 'm_lightrig_envMap.rib')
        # read template
        fh = open(externalPath(lribfile), 'r')
        rib = fh.read()
        fh.close()
        # fill in env map path
        rib = rib % (internalPath(Asset.envMapPath()))
        # print '-'*80
        # print rib
        # print '-'*80
        # write out file
        fh = open(externalPath(lribfile), 'w')
        fh.write(rib)
        fh.close()
        lightrig = 'envMap'

    # build a config file
    # The config file needs to be in the tmp dir.
    #
    configfile = os.path.join(tmpdir, 'm_config.rib')
    conf = '''IfBegin "!defined(RMSPROJ_FROM_ENV)"
  Option "user" "string RMSPROJ" ["."]
IfEnd
IfBegin "!defined(RMSTREE)"
  Option "user" "string RMSTREE" ["%s"]
IfEnd
IfBegin "!defined(MATDIR)"
  Option "user" "string MATDIR" ["%s"]
IfEnd
  Option "user" "string lightrig" ["%s"]''' % (rmstree, matdir, lightrig)
    fh = open(externalPath(configfile), 'w')
    fh.write(conf)
    fh.close()
    if not os.path.exists(configfile):
        progressReporter.End()
        raise RmanAssetLibError('BAD CONFIG PATH: %s' % configfile)
    # print(" - renderAssetPreview: config rib = %s" % repr(configfile))

    # get executable path
    #
    rmanbin = internalPath(os.path.join(rmantree, 'bin'))
    if not os.path.exists(rmanbin):
        progressReporter.End()
        raise RmanAssetLibError('BAD RMANBIN PATH: %s' % repr(rmanbin))
    prman = os.path.join(rmanbin, app('prman'))
    if not os.path.exists(prman):
        progressReporter.End()
        raise RmanAssetLibError('BAD PRMAN PATH: %s' % repr(prman))
    sho = os.path.join(rmanbin, app('sho'))
    if not os.path.exists(sho):
        progressReporter.End()
        raise RmanAssetLibError('BAD SHO PATH: %s' % repr(sho))
    # setup is done
    progressReporter.End()

    # build command
    ncpu = multiprocessing.cpu_count()
    cmd = [externalPath(prman), '-t:%d' % (ncpu - 1), '-Progress',
           '-cwd', externalPath(tmpdir), externalPath(ribfile)]
    # print(" - renderAssetPreview: cmd = %s" % (' '.join(cmd)))

    # the progress strings have different end-of-line sequences...
    strIn = -6
    strOut = -3
    onWindows = (os.name is 'nt')
    if onWindows:
        strIn = -7
        strOut = -4

    # we don't want the command window to open on Windows...
    startupinfo = ra.startupInfo()

    # if we detect an error during the render, we will cancel intermediate
    # files cleanup for debugging.
    cancelCleanup = False
    debug = debugPreview()

    useShell = False
    if useShell:
        cmd = ' '.join(cmd)

    # launch command
    progressReporter.Start()
    progressReporter.Update(0, 'Rendering Preview : %s' % assetName)
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, bufsize=1, shell=useShell,
                             startupinfo=startupinfo)
    except:
        progressReporter.End()
        print(p.stderr.read())
        print(p.stdout.read())
        progressReporter.End()
        raise RmanAssetLibError(">> Unexpected error: %s" % sysErr())

    l = p.stderr.readline().decode('utf-8')
    while l:
        # l = errdata
        if 'R90000' in l:
            # progress messages update the progress bar
            # print repr(l)
            val = int(l[strIn:strOut])
            progressReporter.Update(val)
        else:
            # detect crash - desperate measure... :(
            if 'SIGSEGV' in l:
                print(p.poll())
                print(l.rstrip())
                print('The renderer has crashed !')
                cancelCleanup = (debug and True)
                break
            # print any other output
            print(l.rstrip())
            if debug and 'ERROR' in l or 'Invalid' in l:
                cancelCleanup = True
        # in practice, this isn't working because prman is a child process of
        # p. we would need the psutil module to find out if the child process
        # is actually running, but it is not available.
        status = p.poll()
        if status is None:
            l = p.stderr.readline().decode('utf-8')
        else:
            if status < 0:
                print('The renderer has crashed ! (%d)' % status)
            break
    progressReporter.End()

    progressReporter.Start()
    progressReporter.Update(0, 'Post-processing previews : %s' % assetName)

    # convert tiff to png
    # The render comes at 128x128 in tif format.
    # We need a 128x128 png and a 64x64 png for the browser.
    tif100 = os.path.join(matdir, 'asset_100.tif')
    png100 = os.path.join(matdir, 'asset_100.png')
    png50 = os.path.join(matdir, 'asset_50.png')

    if not os.path.exists(tif100):
        progressReporter.End()
        raise RmanAssetLibError("No render : %s" % tif100)

    # maya can not read our tiff file... sigh
    #
    icmd = [externalPath(sho), '-dspy', 'png', '-dspyfile',
            externalPath(png100), externalPath(tif100)]
    progressReporter.Update(33)
    p = subprocess.Popen(icmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         startupinfo=startupinfo)
    p.wait()

    # make a half-size version of the preview, if possible
    #
    progressReporter.Update(66)
    resizer.Resize(64, externalPath(png100), externalPath(png50))
    progressReporter.End()

    # delete temporary files
    #
    progressReporter.Start()
    progressReporter.Update(0, 'clean-up : %s' % assetName)
    if not cancelCleanup:
        for f in [tif100, matribfile]:
            try:
                # print "cleanup: %s" % f
                os.remove(externalPath(f))
            except:
                progressReporter.End()
                raise RmanAssetLibError("Could not cleanup : %s" % f)

        try:
            shutil.rmtree(externalPath(tmpdir))
        except:
            print('failed to cleanup temporary directory')
    else:
        print("              cmd: %s" % (' '.join(cmd)))
        print('    main rib file: %s' % externalPath(ribfile))
        print('material rib file: %s' % externalPath(matribfile))

    progressReporter.End()
