from __future__ import with_statement

import os
import re
import sys
import stat
import shutil
import pickle as cPickle
import datetime

from . import valve
from .perforce import _p4fast, P4Change, p4run, DEFAULT_CHANGE, toDepotAndDiskPaths

# try to import the windows api - this may fail if we're not running on windows
try:
    import win32con, win32api
except ImportError:
    pass

# set the pickle protocol to use
PICKLE_PROTOCOL = 2

# set some variables for separators
NICE_SEPARATOR = '/'
NASTY_SEPARATOR = '\\'
NATIVE_SEPARATOR = (NICE_SEPARATOR, NASTY_SEPARATOR)[os.name == 'nt']
PATH_SEPARATOR = '/'  # (NICE_SEPARATOR, NASTY_SEPARATOR)[ os.name == 'nt' ]
OTHER_SEPARATOR = '\\'  # (NASTY_SEPARATOR, NICE_SEPARATOR)[ os.name == 'nt' ]
UNC_PREFIX = PATH_SEPARATOR * 2


def cleanPath(pathString):
    '''
    will clean out all nasty crap that gets into pathnames from various sources.
    maya will often put double, sometimes triple slashes, different slash types etc
    '''
    path = str(pathString).strip().replace(OTHER_SEPARATOR, PATH_SEPARATOR)
    isUNC = path.startswith(UNC_PREFIX)
    while path.find(UNC_PREFIX) != -1:
        path = path.replace(UNC_PREFIX, PATH_SEPARATOR)

    if isUNC:
        path = PATH_SEPARATOR + path

    return path


ENV_REGEX = re.compile("\%[^%]+\%")
findall = re.findall


def RealPath(path):
    try:
        import win32api

        return win32api.GetLongPathName(win32api.GetShortPathName(str(path)))
    except:
        return path


class PathError(Exception):
    '''
    Exception to handle errors in path values.
    '''

    def __init__(self, msg, errno=None):
        # Exception.__init__( self, message )
        self.errno = errno
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

    def __repr__(self):
        return str(self.msg)


def resolveAndSplit(path, envDict=None, raiseOnMissing=False):
    '''
    recursively expands all environment variables and '..' tokens in a pathname
    '''
    if envDict is None:
        envDict = os.environ

    path = str(path)

    # first resolve any env variables
    missingVars = set()
    if '%' in path:  # performing this check is faster than doing the regex
        matches = findall(ENV_REGEX, path)
        while matches:
            for match in matches:
                try:
                    path = path.replace(match, envDict[match[1:-1]])
                except KeyError:
                    if raiseOnMissing:
                        raise PathError(
                            'Attempted to resolve a Path using an environment variable that does not exist.', 1)
                    missingVars.add(match)

            matches = set(findall(ENV_REGEX, path))

            # remove any variables that have been found to be missing...
            for missing in missingVars:
                matches.remove(missing)

    # now resolve any subpath navigation
    if OTHER_SEPARATOR in path:  # believe it or not, checking this first is faster
        path = path.replace(OTHER_SEPARATOR, PATH_SEPARATOR)

    # is the path a UNC path?
    isUNC = path[:2] == UNC_PREFIX
    if isUNC:
        path = path[2:]

    # remove duplicate separators
    duplicateSeparator = UNC_PREFIX
    while duplicateSeparator in path:
        path = path.replace(duplicateSeparator, PATH_SEPARATOR)

    pathToks = path.split(PATH_SEPARATOR)
    pathsToUse = []
    pathsToUseAppend = pathsToUse.append
    for n, tok in enumerate(pathToks):
        # resolve a .. unless the previous token is a missing envar
        if tok == "..":
            if n > 0 and (pathToks[n - 1] in missingVars):
                raise PathError(
                    'Attempted to resolve a Path with ".." into the directory of environment variable "{0}" that does not exist.'.format(
                        pathToks[n - 1]), 2)
            try:
                pathsToUse.pop()
            except IndexError:
                if raiseOnMissing:
                    raise

                pathsToUse = pathToks[n:]
                break
        else:
            pathsToUseAppend(tok)

    # finally convert it back into a path string and pop out the last token if its empty
    path = PATH_SEPARATOR.join(pathsToUse)
    try:
        if not pathsToUse[-1]:
            pathsToUse.pop()
    except IndexError:
        raise PathError('Attempted to resolve a Path with "{0}", which is not a valid path string.'.format(path))

    path = RealPath(path)

    # if its a UNC path, stick the UNC prefix
    if isUNC:
        return UNC_PREFIX + path, pathsToUse, True

    return path, pathsToUse, isUNC


def resolve(path, envDict=None, raiseOnMissing=False):
    return resolveAndSplit(path, envDict, raiseOnMissing)[0]


resolvePath = resolve

sz_BYTES = 0
sz_KILOBYTES = 1
sz_MEGABYTES = 2
sz_GIGABYTES = 3


class Path(str):
    __CASE_MATTERS = os.name != 'nt'

    @classmethod
    def DoP4(cls):
        return P4File.USE_P4

    def asP4(self):
        '''
        returns self as a P4File instance - the instance is cached so repeated calls to this
        method will result in the same P4File instance being returned.

        NOTE: the caching is done within the method, it doesn't rely on the cache decorators
        used elsewhere in this class, so it won't get blown away on cache flush
        '''
        try:
            return self.p4
        except AttributeError:
            self.p4 = P4File(self)
            return self.p4

    @classmethod
    def SetCaseMatter(cls, state):
        cls.__CASE_MATTERS = state

    @classmethod
    def DoesCaseMatter(cls):
        return cls.__CASE_MATTERS

    @classmethod
    def Join(cls, *toks, **kw):
        return cls('/'.join(toks), **kw)

    def __new__(cls, path='', caseMatters=None, envDict=None):
        '''
        if case doesn't matter for the path instance you're creating, setting caseMatters
        to False will do things like caseless equality testing, caseless hash generation
        '''

        # early out if we've been given a Path instance - paths are immutable so there is no reason not to just return what was passed in
        if type(path) == cls:
            return path

        # set to an empty string if we've been init'd with None
        if path is None:
            path = ''

        resolvedPath, pathTokens, isUnc = resolveAndSplit(path, envDict)
        new = str.__new__(cls, resolvedPath)
        new.isUNC = isUnc
        new.hasTrailing = resolvedPath.endswith(PATH_SEPARATOR)
        new._splits = tuple(pathTokens)
        new._passed = path

        # case sensitivity, if not specified, defaults to system behaviour
        if caseMatters is not None:
            new.__CASE_MATTERS = caseMatters

        return new

    @classmethod
    def Temp(cls):
        '''
        returns a temporary filepath - the file should be unique (i think) but certainly the file is guaranteed
        to not exist
        '''
        import datetime, random
        def generateRandomPathName():
            now = datetime.datetime.now()
            rnd = '%06d' % (abs(random.gauss(0.5, 0.5) * 10 ** 6))
            return '%TEMP%' + PATH_SEPARATOR + 'TMP_FILE_%s%s%s%s%s%s%s%s' % (
                now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond, rnd)

        randomPathName = cls(generateRandomPathName())
        while randomPathName.exists:
            randomPathName = cls(generateRandomPathName())

        return randomPathName

    def __nonzero__(self):
        '''
        a Path instance is "non-zero" if its not '' or '/'  (although I guess '/' is actually a valid path on *nix)
        '''
        selfStripped = self.strip()
        if selfStripped == '':
            return False

        if selfStripped == PATH_SEPARATOR:
            return False

        return True

    def __add__(self, other):
        return self.__class__('%s%s%s' % (self, PATH_SEPARATOR, other), self.__CASE_MATTERS)

    # the / or + operator both concatenate path tokens
    __div__ = __add__
    __truediv__ = __add__



    def __radd__(self, other):
        return self.__class__(other, self.__CASE_MATTERS) + self

    __rdiv__ = __radd__

    def __getitem__(self, item):
        return self._splits[item]

    def __getslice__(self, a, b):
        isUNC = self.isUNC
        if a:
            isUNC = False

        return self._toksToPath(self._splits[a:b], isUNC, self.hasTrailing)

    def __len__(self):

        return len(self._splits)

    def __contains__(self, item):
        if not self.__CASE_MATTERS:
            return item.lower() in [s.lower() for s in self._splits]

        return item in list(self._splits)

    def __hash__(self):
        '''
        the hash for two paths that are identical should match - the most reliable way to do this
        is to use a tuple from self.split to generate the hash from
        '''
        if not self.__CASE_MATTERS:
            return hash(tuple([s.lower() for s in self._splits]))

        return hash(tuple(self._splits))

    def _toksToPath(self, toks, isUNC=False, hasTrailing=False):
        '''
        given a bunch of path tokens, deals with prepending and appending path
        separators for unc paths and paths with trailing separators
        '''
        toks = list(toks)
        if isUNC:
            toks = ['', ''] + toks

        if hasTrailing:
            toks.append('')

        return self.__class__(PATH_SEPARATOR.join(toks), self.__CASE_MATTERS)

    def resolve(self, envDict=None, raiseOnMissing=False):
        '''
        will re-resolve the path given a new envDict
        '''
        if envDict is None:
            return self
        else:
            return Path(self._passed, self.__CASE_MATTERS, envDict)

    def unresolved(self):
        '''
        returns the un-resolved path - this is the exact string that the path was instantiated with
        '''
        return self._passed

    def isEqual(self, other):
        '''
        compares two paths after all variables have been resolved, and case sensitivity has been
        taken into account - the idea being that two paths are only equal if they refer to the
        same ValveFileSystem object.  NOTE: this doesn't take into account any sort of linking on *nix
        systems...
        '''
        if isinstance(other, Path):
            # Convert Paths to strings
            otherStr = str(other.asFile())
        elif other:
            # Convert non-empty strings to Paths
            otherStr = Path(other, self.__CASE_MATTERS)
        else:
            # Leave empty strings and convert non-strings
            otherStr = str(other)

        selfStr = str(self.asFile())

        if not self.__CASE_MATTERS:
            selfStr = selfStr.lower()
            otherStr = otherStr.lower()

        return selfStr == otherStr

    __eq__ = isEqual

    def __ne__(self, other):
        return not self.isEqual(other)

    def doesCaseMatter(self):
        return self.__CASE_MATTERS

    @classmethod
    def getcwd(cls):
        '''
        returns the current working directory as a path object
        '''
        return cls(os.getcwd())

    @classmethod
    def setcwd(cls, path):
        '''
        simply sets the current working directory - NOTE: this is a class method so it can be called
        without first constructing a path object
        '''
        newPath = cls(path)
        try:
            os.chdir(newPath)
        except WindowsError:
            return None

        return newPath

    putcwd = setcwd

    def getStat(self):
        try:
            return os.stat(self)
        except:
            # return a null stat_result object
            return os.stat_result([0 for n in range(os.stat_result.n_sequence_fields)])

    stat = property(getStat)

    def getModifiedDate(self):
        '''
        Return the last modified date in seconds.
        '''
        return self.stat[8]

    modifiedDate = property(getModifiedDate, doc="Return the last modified date in seconds.")

    def isAbs(self):
        try:
            return os.path.isabs(str(self))
        except:
            return False

    def abs(self):
        '''
        returns the absolute path as is reported by os.path.abspath
        '''
        return self.__class__(os.path.abspath(str(self)))

    def split(self, sep=None, maxsplit=None):
        '''
        Returns the splits tuple - ie. the path tokens
        The additional arguments only included for class compatibility.
        '''
        assert (sep == None) or (sep == '\\') or (
                sep == '/'), "Path objects can only be split by path separators, ie. '/'."
        return list(self._splits)

    def asDir(self):
        '''
        makes sure there is a trailing / on the end of a path
        '''
        if self.hasTrailing:
            return self

        return self.__class__('%s%s' % (self._passed, PATH_SEPARATOR), self.__CASE_MATTERS)

    asdir = asDir

    def asFile(self):
        '''
        makes sure there is no trailing path separators
        '''
        if not self.hasTrailing:
            return self

        # Don't remove single slash Paths
        if len(self) == 1:
            return self

        return self.__class__(str(self)[:-1], self.__CASE_MATTERS)

    asfile = asFile

    def isDir(self):
        '''
        bool indicating whether the path object points to an existing directory or not.  NOTE: a
        path object can still represent a file that refers to a file not yet in existence and this
        method will return False
        '''
        return os.path.isdir(self)

    isdir = isDir

    def isFile(self):
        '''
        see isdir notes
        '''
        return os.path.isfile(self)

    isfile = isFile

    def getReadable(self):
        '''
        returns whether the current instance's file is readable or not.  if the file
        doesn't exist False is returned
        '''
        try:
            s = os.stat(self)
            return s.st_mode & stat.S_IREAD
        except:
            # i think this only happens if the file doesn't exist
            return False

    def isReadable(self):
        return bool(self.getReadable())

    def setWritable(self, state=True):
        '''
        sets the writeable flag (ie: !readonly)
        '''
        try:
            setTo = stat.S_IREAD
            if state:
                setTo = stat.S_IWRITE

            os.chmod(self, setTo)
        except:
            pass

    def getWritable(self):
        '''
        returns whether the current instance's file is writeable or not.  if the file
        doesn't exist True is returned
        '''
        try:
            s = os.stat(self)
            return s.st_mode & stat.S_IWRITE
        except:
            # i think this only happens if the file doesn't exist - so return true
            return True

    def isWriteable(self):
        return bool(self.getWritable())

    def getExtension(self):
        '''
        returns the extension of the path object - an extension is defined as the string after a
        period (.) character in the final path token
        '''
        try:
            endTok = self[-1]
        except IndexError:
            return ''

        idx = endTok.rfind('.')
        if idx == -1:
            return ''

        return endTok[idx + 1:]  # add one to skip the period

    def setExtension(self, xtn=None, renameOnDisk=False):
        '''
        sets the extension the path object.  deals with making sure there is only
        one period etc...

        if the renameOnDisk arg is true, the file on disk (if there is one) is
        renamed with the new extension
        '''
        if xtn is None:
            xtn = ''

        # make sure there is are no start periods
        while xtn.startswith('.'):
            xtn = xtn[1:]

        toks = list(self.split())
        try:
            endTok = toks.pop()
        except IndexError:
            endTok = ''

        idx = endTok.rfind('.')
        name = endTok
        if idx >= 0:
            name = endTok[:idx]

        if xtn:
            newEndTok = '%s.%s' % (name, xtn)
        else:
            newEndTok = name

        if renameOnDisk:
            self.rename(newEndTok, True)
        else:
            toks.append(newEndTok)

        return self._toksToPath(toks, self.isUNC, self.hasTrailing)

    extension = property(getExtension, setExtension)

    def hasExtension(self, extension):
        '''
        returns whether the extension is of a certain value or not
        '''
        ext = self.getExtension()
        if not self.__CASE_MATTERS:
            ext = ext.lower()
            extension = extension.lower()

        return ext == extension

    isExtension = hasExtension

    def name(self, stripExtension=True, stripAllExtensions=False):
        '''
        returns the filename by itself - by default it also strips the extension, as the actual filename can
        be easily obtained using self[-1], while extension stripping is either a multi line operation or a
        lengthy expression
        '''
        try:
            name = self[-1]
        except IndexError:
            return ''

        if stripExtension:
            pIdx = -1
            if stripAllExtensions:
                pIdx = name.find('.')
            else:
                pIdx = name.rfind('.')

            if pIdx != -1:
                return name[:pIdx]

        return name

    @property
    def filename(self):
        '''
        Returns the filename with extension.
        '''
        return self.name(stripExtension=False)

    def up(self, levels=1):
        '''
        returns a new path object with <levels> path tokens removed from the tail.
        ie: Path("a/b/c/d").up(2) returns Path("a/b")
        '''
        if not levels:
            return self

        toks = list(self._splits)
        levels = max(min(levels, len(toks) - 1), 1)
        toksToJoin = toks[:-levels]
        if self.hasTrailing:
            toksToJoin.append('')

        return self._toksToPath(toksToJoin, self.isUNC, self.hasTrailing)

    def replace(self, search, replace='', caseMatters=None):
        '''
        A simple search replace method - works on path tokens.
        If caseMatters is None, then the system default case sensitivity is used.
        If the string is not found, the original Path is returned.
        '''
        try:
            idx = self.find(search, caseMatters)
        except ValueError:
            # If no match is found, return original Path
            return self
        if idx == -1:
            # string not found, return the original object
            return self
        elif search in ('\\', '/'):
            # Use base class method if the search string is a path sep and return a str. If we don't
            # return a str, the path replacement would have no effect as the Path.__str__
            # representation always presents a path with forward slashes.
            return super(self.__class__, self).replace(search, replace)

        toks = list(self.split())
        toks[idx] = replace

        return self._toksToPath(toks, self.isUNC, self.hasTrailing)

    def find(self, search, caseMatters=None):
        '''
        Returns the index of the given path token.
        Returns -1 if the token is not found.
        '''
        if search in ('\\', '/'):
            # Use base class method if the search string is a path sep
            return super(self.__class__, self).find(search)

        if caseMatters is None:
            # in this case assume system case sensitivity - ie sensitive only on *nix platforms
            caseMatters = self.__CASE_MATTERS

        if not caseMatters:
            toks = [s.lower() for s in self.split()]
            search = search.lower()
        else:
            toks = self.split()

        try:
            idx = toks.index(search)
        except ValueError:
            return -1

        return idx

    index = find

    def doesExist(self):
        '''
        returns whether the file exists on disk or not
        '''
        try:
            return os.path.exists(self)
        except IndexError:
            return False

    exists = property(doesExist)

    def matchCase(self):
        '''
        If running under an env where file case doesn't matter, this method will return a Path instance
        whose case matches the file on disk.  It assumes the file exists
        '''
        if self.doesCaseMatter():
            return self

        for f in self.up().files():
            if f == self:
                return f

    def getSize(self, units=sz_MEGABYTES):
        '''
        returns the size of the file in mega-bytes
        '''
        div = float(1024 ** units)
        return os.path.getsize(self) / div

    def create(self):
        '''
        if the directory doesn't exist - create it
        '''
        if not self.exists:
            os.makedirs(str(self))

    def _delete(self):
        '''
        WindowsError is raised if the file cannot be deleted
        '''
        if self.isfile():
            try:
                os.remove(self)
            except WindowsError as e:
                win32api.SetFileAttributes(self, win32con.FILE_ATTRIBUTE_NORMAL)
                os.remove(self)
        elif self.isdir():
            for f in self.files(recursive=True):
                f.delete()

            win32api.SetFileAttributes(self, win32con.FILE_ATTRIBUTE_NORMAL)
            shutil.rmtree(str(self.asDir()), True)

    def delete(self, doP4=True):
        '''
        Delete the file. For P4 operations, return the result.
        '''
        if doP4 and P4File.DoP4():
            try:
                asP4 = P4File(self)
                if asP4.managed():
                    if asP4.action is None:
                        result = asP4.delete()
                        if not self.exists:
                            return result
                    else:
                        asP4.revert()
                        result = asP4.delete()

                        # only return if the file doesn't exist anymore - it may have been open for add in
                        # which case we still need to do a normal delete...
                        if not self.exists:
                            return result
            except Exception as e:
                pass

        return self._delete()

    remove = delete

    def _rename(self, newName, nameIsLeaf=False):
        '''
        it is assumed newPath is a fullpath to the new dir OR file.  if nameIsLeaf is True then
        newName is taken to be a filename, not a filepath.  the fullpath to the renamed file is
        returned
        '''
        newPath = Path(newName)
        if nameIsLeaf:
            newPath = self.up() / newName

        if self.isfile():
            if newPath != self:
                if newPath.exists:
                    newPath.delete()

            # Now perform the rename
            os.rename(self, newPath)
        elif self.isdir():
            raise NotImplementedError('dir renaming not implemented yet...')

        return newPath

    def rename(self, newName, nameIsLeaf=False, doP4=True):
        '''
        it is assumed newPath is a fullpath to the new dir OR file.  if nameIsLeaf is True then
        newName is taken to be a filename, not a filepath.  the instance is modified in place.
        if the file is in perforce, then a p4 rename (integrate/delete) is performed
        '''

        newPath = Path(newName)
        if nameIsLeaf:
            newPath = self.up() / newName

        if self.isfile():
            tgtExists = newPath.exists
            if doP4 and P4File.DoP4():
                reAdd = False
                change = None
                asP4 = P4File(self)

                # if its open for add, revert - we're going to rename the file...
                if asP4.action == 'add':
                    asP4.revert()
                    change = asP4.getChange()
                    reAdd = True

                # so if we're managed by p4 - try a p4 rename, and return on success.  if it
                # fails however, then just do a normal rename...
                if asP4.managed():
                    asP4.rename(newPath)
                    return newPath

                # if the target exists and is managed by p4, make sure its open for edit
                if tgtExists and asP4.managed(newPath):
                    _p4fast('edit', newPath)

                # now perform the rename
                ret = self._rename(newName, nameIsLeaf)

                if reAdd:
                    _p4fast('add', newPath)
                    asP4.setChange(change, newPath)

                return ret
        elif self.isdir():
            raise NotImplementedError('dir renaming not implemented yet...')

        return self._rename(newName, nameIsLeaf)

    move = rename

    def _copy(self, target, nameIsLeaf=False):
        '''
        same as rename - except for copying.  returns the new target name
        '''
        if self.isfile():
            target = Path(target)
            if nameIsLeaf:
                asPath = self.up() / target
                target = asPath

            if self == target:
                return target

            shutil.copy2(str(self), str(target))

            return target
        elif self.isdir():
            raise NotImplementedError('dir copying not implemented yet...')

    # shutil.copytree( str(self), str(target) )
    def copy(self, target, nameIsLeaf=False, doP4=True):
        '''
        Same as rename - except for copying. Returns the new target name
        '''
        if self.isfile():
            target = Path(target)
            if nameIsLeaf:
                target = self.up() / target

            if doP4 and P4File.DoP4():
                try:
                    asP4 = P4File(self)
                    tgtAsP4 = P4File(target)
                    if asP4.managed() and tgtAsP4.isUnderClient():
                        # so if we're managed by p4 - try a p4 rename, and return on success.  if it
                        # fails however, then just do a normal rename...
                        result = asP4.copy(target)

                        return target
                except:
                    pass

        return self._copy(target, nameIsLeaf)

    def read(self, strip=True):
        '''
        returns a list of lines contained in the file. NOTE: newlines are stripped from the end but whitespace
        at the head of each line is preserved unless strip=False
        '''
        if self.exists and self.isfile():
            fileId = open(self)
            if strip:
                lines = [line.rstrip() for line in fileId.readlines()]
            else:
                lines = fileId.read()
            fileId.close()

            return lines

    def _write(self, contentsStr):
        '''
        writes a given string to the file defined by self
        '''

        # make sure the directory to we're writing the file to exists
        self.up().create()

        with open(self, 'w') as f:
            f.write(str(contentsStr))

    def write(self, contentsStr, doP4=True):
        '''
        Wraps Path.write:  if doP4 is true, the file will be either checked out of p4 before writing or
        add to perforce after writing if its not managed already.
        '''
        assert isinstance(self, Path)
        if doP4 and self.DoP4():

            hasBeenHandled = False

            isUnderClient = self.asP4().isUnderClient()
            if self.exists:
                # Assume if its writeable that its open for edit already
                if not self.getWritable():
                    _p4fast('edit', self)
                    if not self.getWritable():
                        self.setWritable()

                    hasBeenHandled = True

            ret = self._write(contentsStr)

            if isUnderClient and not hasBeenHandled:
                _p4fast('add', self)

            return ret
        else:
            return self._write(contentsStr)

    def _pickle(self, toPickle):
        '''
        similar to the write method but pickles the file
        '''
        if self.up():
            # Only create if there is a parent dir
            self.up().create()

        with open(self, 'w') as f:
            cPickle.dump(toPickle, f, PICKLE_PROTOCOL)

    def pickle(self, toPickle, doP4=True):
        assert isinstance(self, Path)
        if doP4 and P4File.DoP4():

            hasBeenHandled = False

            isUnderClient = P4File().isUnderClient(self)
            if self.exists:
                if not self.getWritable():
                    _p4fast('edit', self)
                    if not self.getWritable():
                        self.setWritable()

                    hasBeenHandled = True

            ret = self._pickle(toPickle)

            if isUnderClient and not hasBeenHandled:
                # need to explicitly add pickled files as binary type files, otherwise p4 mangles them
                _p4fast('add -t binary', self)

            return ret

        return self._pickle(toPickle)

    def unpickle(self):
        '''
        unpickles the file
        '''
        fileId = open(self, 'rb')
        data = cPickle.load(fileId)
        fileId.close()

        return data

    def relativeTo(self, other):
        '''
        returns self as a path relative to another
        '''

        path = self
        other = Path(other)

        pathToks = path.split()
        otherToks = other.split()

        caseMatters = self.__CASE_MATTERS
        if not caseMatters:
            pathToks = [t.lower() for t in pathToks]
            otherToks = [t.lower() for t in otherToks]

        # if the first path token is different, early out - one is not a subset of the other in any fashion
        if otherToks[0] != pathToks[0]:
            return None

        lenPath, lenOther = len(path), len(other)
        if lenPath < lenOther:
            return None

        newPathToks = []
        pathsToDiscard = lenOther
        for pathN, otherN in zip(pathToks[1:], otherToks[1:]):
            if pathN == otherN:
                continue
            else:
                newPathToks.append('..')
                pathsToDiscard -= 1

        newPathToks.extend(path[pathsToDiscard:])
        path = Path(PATH_SEPARATOR.join(newPathToks), self.__CASE_MATTERS)

        return path

    __sub__ = relativeTo

    def __rsub__(self, other):
        return self.__class__(other, self.__CASE_MATTERS).relativeTo(self)

    def inject(self, other, envDict=None):
        '''
        injects an env variable into the path - if the env variable doesn't
        resolve to tokens that exist in the path, a path string with the same
        value as self is returned...

        NOTE: a string is returned, not a Path instance - as Path instances are
        always resolved

        NOTE: this method is alias'd by __lshift__ and so can be accessed using the << operator:
        d:/main/content/mod/models/someModel.ma << '%VCONTENT%' results in %VCONTENT%/mod/models/someModel.ma
        '''

        toks = toksLower = self._splits
        otherToks = Path(other, self.__CASE_MATTERS, envDict=envDict).split()
        newToks = []
        n = 0
        if not self.__CASE_MATTERS:
            toksLower = [t.lower() for t in toks]
            otherToks = [t.lower() for t in otherToks]

        while n < len(toks):
            tok, tokLower = toks[n], toksLower[n]
            if tokLower == otherToks[0]:
                allMatch = True
                for tok, otherTok in zip(toksLower[n + 1:], otherToks[1:]):
                    if tok != otherTok:
                        allMatch = False
                        break

                if allMatch:
                    newToks.append(other)
                    n += len(otherToks) - 1
                else:
                    newToks.append(toks[n])
            else:
                newToks.append(tok)
            n += 1

        return PATH_SEPARATOR.join(newToks)

    __lshift__ = inject

    def findNearest(self):
        '''
        returns the longest path that exists on disk
        '''
        path = self
        while not path.exists and len(path) > 1:
            path = path.up()

        if not path.exists:
            return None
        return path

    getClosestExisting = findNearest
    nearest = findNearest

    def asNative(self):
        '''
        returns a string with system native path separators
        '''
        return str(self).replace(PATH_SEPARATOR, NATIVE_SEPARATOR)

    def startswith(self, other):
        '''
        returns whether the current instance begins with a given path fragment.  ie:
        Path('d:/temp/someDir/').startswith('d:/temp') returns True
        '''
        if not isinstance(other, type(self)):
            other = Path(other, self.__CASE_MATTERS)

        otherToks = other.split()
        selfToks = self.split()
        if not self.__CASE_MATTERS:
            otherToks = [t.lower() for t in otherToks]
            selfToks = [t.lower() for t in selfToks]

        if len(otherToks) > len(selfToks):
            return False

        for tokOther, tokSelf in zip(otherToks, selfToks):
            if tokOther != tokSelf: return False

        return True

    isUnder = startswith

    def endswith(self, other):
        '''
        determines whether self ends with the given path - it can be a string
        '''
        # copies of these objects NEED to be made, as the results from them are often cached - hence modification to them
        # would screw up the cache, causing really hard to track down bugs...  not sure what the best answer to this is,
        # but this is clearly not it...  the caching decorator could always return copies of mutable objects, but that
        # sounds wasteful...  for now, this is a workaround
        otherToks = list(Path(other).split())
        selfToks = list(self._splits)
        otherToks.reverse()
        selfToks.reverse()
        if not self.__CASE_MATTERS:
            otherToks = [t.lower() for t in otherToks]
            selfToks = [t.lower() for t in selfToks]

        for tokOther, tokSelf in zip(otherToks, selfToks):
            if tokOther != tokSelf:
                return False

        return True

    def _list_filesystem_items(self, itemtest, namesOnly=False, recursive=False):
        '''
        does all the listing work - itemtest can generally only be one of os.path.isfile or
        os.path.isdir.  if anything else is passed in, the arg given is the full path as a
        string to the ValveFileSystem item
        '''
        if not self.exists:
            return

        if recursive:
            walker = os.walk(self)
            for path, subs, files in walker:
                path = Path(path, self.__CASE_MATTERS)

                for sub in subs:
                    p = path / sub
                    if itemtest(p):
                        if namesOnly:
                            p = p.name()

                        yield p
                    else:
                        break  # if this doesn't match, none of the other subs will

                for item in files:
                    p = path / item
                    if itemtest(p):
                        if namesOnly:
                            p = p.name()

                        yield p
                    else:
                        break  # if this doesn't match, none of the other items will
        else:
            for item in os.listdir(self):
                p = self / item
                if itemtest(p):
                    if namesOnly:
                        p = p.name()

                    yield p

    def dirs(self, namesOnly=False, recursive=False):
        '''
        returns a generator that lists all sub-directories.  If namesOnly is True, then only directory
        names (relative to the current dir) are returned
        '''
        return self._list_filesystem_items(os.path.isdir, namesOnly, recursive)

    def files(self, namesOnly=False, recursive=False):
        '''
        returns a generator that lists all files under the path (assuming its a directory).  If namesOnly
        is True, then only directory names (relative to the current dir) are returned
        '''
        return self._list_filesystem_items(os.path.isfile, namesOnly, recursive)

    ########### VALVE SPECIFIC PATH METHODS ###########

    def expandAsGame(self, gameInfo, extension=None, mustExist=True):
        '''
        expands a given "mod" relative path to a real path under the game tree.  if an extension is not given, it is
        assumed the path already contains an extension.  ie:  models/player/scout.vmt would get expanded to:
        <gameRoot>/<mod found under>/models/player/scout.vmt - where the mod found under is the actual mod the file
        exists under on the user's system

        The mustExistFlag was added due to a bug with how a mod's pre-existing assets were being determined.
        If the files did not exist it would default to the parent mod, and then delete those files as part of a
        clean up step so in the pre-compiled check we set mustExist to be False.
        '''
        thePath = self
        if extension is not None:
            thePath = self.setExtension(extension)

        searchPaths = gameInfo.getSearchPaths()
        for path in searchPaths:
            tmp = os.path.join(path, thePath)
            if not mustExist or os.path.exists(tmp):
                return tmp

        return None

    def expandAsContent(self, gameInfo, extension=None):
        '''
        as for expandAsGame except for content rooted paths
        '''
        thePath = self
        if extension is not None:
            thePath = self.setExtension(extension)

        for mod in gameInfo.getSearchMods():
            underMod = '%VCONTENT%' + (mod + thePath)
            if underMod.exists:
                return underMod

        return None

    def expandAsGameAddon(self, gameInfo, addon, extension=None, mustExist=False):
        '''
        Given an addon name, expand a relative Path to an absolute game Path.
        E.g. passing 'pudge_battle' and a Path of 'maps/pudge_battle.bsp', this would expand to:
        '<VGAME>/dota/dota_addons/pudge_battle/maps/pudge_battle.bsp'
        '''
        addonPath = '%VGAME%' + self.expandAsAddonBasePath(addon)
        if extension is not None:
            addonPath = self.setExtension(extension)
        if (not mustExist) or (os.path.exists(addonPath)):
            return addonPath

    def expandAsContentAddon(self, gameinfo, addon, extension=None, mustExist=False):
        '''
        Given an addon name, expand a relative Path to an abosolute game Path.
        E.g. passing 'pudge_battle' and a Path of 'maps/pudge_battle.bsp', this would expand to:
        '<VCONTENT>/dota/dota_addons/pudge_battle/maps/pudge_battle.bsp'
        '''
        addonPath = '%VCONTENT%' + self.expandAsAddonBasePath(addon)
        if extension is not None:
            addonPath = self.setExtension(extension)
        if (not mustExist) or (os.path.exists(addonPath)):
            return addonPath

    def expandAsAddonBasePath(self, addon):
        '''
        Given an addon name, expand as an addon-relative Path for the mod.
        E.g. passing 'pudge_battle' and a Path of 'maps/pudge_battle.bsp', this would expand to:
        'dota_addons/pudge_battle/maps/pudge_battle.bsp'
        '''
        return Path('{0}_addons\\{1}\\').format(valve.mod(), addon) + self

    def belongsToContent(self, gameInfo):
        for mod in gameInfo.getSearchMods():
            if self.isUnder(valve.content() / mod):
                return True

        return False

    def belongsToGame(self, gameInfo):
        for mod in gameInfo.getSearchMods():
            if self.isUnder(valve.game() / mod):
                return True
        return False

    def belongsToMod(self):
        '''
        Return True if Path belongs under *content* of the current mod
        '''
        if self.isUnder(valve.content() / valve.mod()):
            return True
        return False

    def asRelative(self):
        '''
        returns the path relative to either VCONTENT or VGAME.
        If the path isn't under either of these directories, None is returned.
        '''
        c = valve.content()
        g = valve.game()
        if self.isUnder(c):
            return self - c
        elif self.isUnder(g):
            return self - g
        return None

    def asRelativeFuzzy(self):
        '''
        Returns the path relative to either VCONTENT or VGAME if there is an exact match.
        If the path isn't under either of these directories, try looking for a pattern match using 'content' or 'game'
        in the path and matching any of the mods in gameinfo Search Paths.
        If still no matches, return None
        '''
        # Try direct match first
        rel = self.asRelative()
        if rel is not None:
            return rel

        # No direct matches found, continue
        mods = valve.gameInfo.getSearchMods()
        toks = self.split()
        toks_lower = [s.lower() for s in toks]

        # Step up through tokens looking for a case-insensitive match
        for modName in mods:
            if modName in toks:
                if 'content' in toks_lower:
                    for i in range(len(toks) - 1, 1, -1):
                        # Look for set of tokens that are 'content' followed by the mod name
                        if (toks_lower[i] == modName) and (toks_lower[i - 1] == 'content'):
                            return Path('\\'.join(toks[i:]))
                elif 'game' in toks_lower:
                    for i in range(len(toks) - 1, 1, -1):
                        # Look for set of tokens that are 'game' followed by the mod name
                        if (toks_lower[i] == modName) and (toks_lower[i - 1] == 'game'):
                            return Path('\\'.join(toks[i:]))
        return None

    def asModRelative(self):
        '''
        Returns a Path instance that is relative to the mod.
        If the path doesn't match the game or content, the original filepath is returned.
        '''
        relPath = self.asRelative()
        if not relPath: return self
        return relPath[1:]

    def asContentModRelative(self):
        '''
        Returns a path instance that is relative to the mod if the path is under the content tree.
        If the path doesn't match the content tree, the original filepath is returned.
        '''
        # Make sure the path starts with content before stripping it away
        if self.startswith(valve.content()):
            return self.asRelative()[1:]
        else:
            return self

    def asContentModRelativePathFuzzy(self):
        '''
        Returns a path instance that is relative to the mod if the path is under the content tree.
        if an automatic match cannot be found, look for the content and mod strings using gameinfo file.
        '''
        # Get content-relative path first
        relPath = self.asRelativeFuzzy()

        if relPath is not None:
            # Make sure the path starts with a mod in search mods before stripping it away
            for modName in valve.gameInfo.getSearchMods():
                if relPath.startswith(modName):
                    return relPath[1:]
            # Mod name must already be stripped
            return relPath
        else:
            # Couldn't find a relative path, return original
            return self

    def asGameModRelative(self):
        '''
        Returns a path instance that is relative to the mod if the path is under the game tree.
        If the path doesn't match the game tree, the original filepath is returned.
        '''
        # Make sure the path starts with content before stripping it away
        if self.startswith(valve.game()):
            return self.asRelative()[1:]
        else:
            return self

    def asAddonRelative(self):
        '''
        Takes an absolute Path and returns a path instance that is relative to the addon, either
        in VCONTENT or VGAME. If the path isn't under either of these directories, None is returned.
        '''
        relPath = self.asRelative()
        if (relPath) and (relPath.isAddon) and (len(relPath) > 2):
            return relPath[2:]
        return None

    def asAddonRelativeFuzzy(self):
        '''
        Returns the addon-relative path under either VCONTENT or VGAME if there is an exact match.
        If the path isn't under either of these directories, try looking for a pattern match using 'content' or 'game'
        in the addon path and matching any of the mods in gameinfo Search Paths.
        If still no matches, return None
        '''
        # Try direct match first
        rel = self.asAddonRelative()
        if rel is not None:
            return rel

        # No direct matches found, continue
        addonModNames = ['{0}_addons'.format(m.lower()) for m in valve.gameInfo.getSearchMods()]
        toks = self.split()
        toks_lower = [s.lower() for s in toks]

        # Step up through tokens looking for a case-insensitive match
        for addonModName in addonModNames:
            if addonModName in toks:
                if 'content' in toks_lower:
                    for i in range(len(toks) - 1, 1, -1):
                        # Look for set of tokens that are 'content' followed by the mod name
                        if (toks_lower[i] == addonModName) and (toks_lower[i - 1] == 'content'):
                            addonRelPath = Path('\\'.join(toks[i:]))
                            # Return path with mod_addons and addon name removed
                            return addonRelPath[2:]
                elif 'game' in toks_lower:
                    for i in range(len(toks) - 1, 1, -1):
                        # Look for set of tokens that are 'game' followed by the mod name
                        if (toks_lower[i] == addonModName) and (toks_lower[i - 1] == 'game'):
                            addonRelPath = Path('\\'.join(toks[i:]))
                            # Return path with mod_addons and addon name removed
                            return addonRelPath[2:]
        return None

    def asAddonRelativeGamePath(self):
        '''
        Takes an absolute VGAME Path and returns a path instance that is relative to the addon.
        If the path isn't under VGAME, None is returned.
        '''
        if self.isUnder(valve.game()):
            return self.asAddonRelative()
        return None

    def asAddonRelativeContentPath(self):
        '''
        Takes an absolute VCONTENT Path and returns a path instance that is relative to the addon.
        If the path isn't under VCONTENT, None is returned.
        '''
        if self.isUnder(valve.content()):
            return self.asAddonRelative()
        return None

    def asMdl(self, isAddon=False):
        '''
        Returns as .mdl path relative to the models directory.
        Passing the isAddon argument as True will force it look for an addon directory to strip from the base of the path.
        '''
        p = self.asModRelative()
        assert p != '', 'mdl cannot be determined from empty path!'

        if self.isAddon or isAddon == True:
            # Remove the addon base path if it is present
            if p.startswith(p.addonBaseDir):
                p = p[1:]
            # For addons, models dir is under the addon name.
            assert p[1] == 'models', 'path not under addon models directory!'
            mdl = p[2:].setExtension('mdl')
        else:
            assert p[0] == 'models', 'path not under models directory!'
            mdl = p[1:].setExtension('mdl')

        return mdl

    def asVMdl(self, isAddon=False):
        '''
        Returns as .vmdl path relative to the models directory.
        Passing the isAddon argument as True will force it look for an addon directory to strip from the base of the path.
        '''
        p = self.asModRelative()
        assert p != '', 'vmdl cannot be determined from empty path!'

        if self.isAddon or isAddon == True:
            # Remove the addon base path if it is present
            if (len(p) > 1) and (p.addonBaseDir):
                p = p[1:]
            # For addons, models dir is under the addon name.
            assert p[1] == 'models', 'path not under addon models directory!'
            vmdl = p[2:].setExtension('vmdl')

        else:
            assert p[0] == 'models', 'path not under models directory!'
            vmdl = p[1:].setExtension('vmdl')

        return vmdl

    @property
    def addonName(self):
        '''
        Returns the addon name, if found, or None.
        Note that this is somewhat strict, as the _addons base directory must be directly under game or content,
        or in the case of a relative path, at the start of the path.
        '''
        for base in valve.gameInfo.getAddonRoots():

            if (self.startswith(base)) and (len(self) > 1):
                # The path is already relative, starting with addons dir
                return self[1]

            # Get a relative path
            relPath = self.asRelative()
            if (relPath) and (relPath.startswith(base)) and (len(relPath) > 1):
                return relPath[1]

        return None

    @property
    def isAddon(self):
        '''
        Returns True is the path is an Addon path.
        Note that this is somewhat strict, as the <mod>_addons must be directly under game or content, or at the start of the path.
        '''
        return (self.addonName is not None)

    @property
    def addonBaseDir(self):
        '''
        Returns the addons base directory name found in the Path (e.g. 'dota_addons' ) or None.
        '''
        for base in valve.getAddonBasePaths(asContent=self.isUnder(valve.content())):
            if self.isUnder(base):
                return base.name()
        return None

    ########### Perforce Integration ###########

    def edit(self):
        '''
        if the file exists and is in perforce, this will open it for edit - if the file isn't in perforce
        AND exists then this will open the file for add, otherwise it does nothing.
        '''
        if self.exists:
            return self.asP4().editoradd()

        return False

    editoradd = edit

    def add(self, type=None):
        return self.asP4().add()

    def revert(self):
        return self.asP4().revert()

    def asDepot(self):
        '''
        returns this instance as a perforce depot path
        '''
        return self.asP4().toDepotPath()

    def isEdit(self):
        '''
        returns true if the file is open for edit
        '''
        return self.asP4().isEdit()

    def setChange(self, change):
        '''
        move to the specified change
        '''
        self.asP4().setChange(change)


class P4File(Path):
    '''
    provides a more convenient way of interfacing with perforce.  NOTE: where appropriate all actions
    are added to the changelist with the description DEFAULT_CHANGE
    '''
    USE_P4 = True

    __CASE_MATTERS = os.name != 'nt'

    # the default change description for instances
    DEFAULT_CHANGE = DEFAULT_CHANGE

    BINARY = 'binary'
    XBINARY = 'xbinary'

    TIMEOUT_PERIOD = 5

    # def __init__( self, *args, **kwargs ):
    # super( self.__class__, self ).__init__( *args, **kwargs )

    # if not self.isFile():
    # raise TypeError( 'Class P4File must refer to a file, not a directory!' )

    def run(self, *args, **kwargs):
        return p4run(*args, **kwargs)

    def getFile(self, f=None):
        if f is None:
            return self

        return Path(f)

    def getFileStr(self, f=None, allowMultiple=False, verifyExistence=True):
        if f is None:
            return '"%s"' % self

        if isinstance(f, (list, tuple)):
            if verifyExistence:
                return '"%s"' % '" "'.join([anF for anF in f if Path(anF).exists])
            else:
                return '"%s"' % '" "'.join(f)

        return '"%s"' % Path(f)

    def getStatus(self, f=None):
        '''
        returns the status dictionary for the instance.  if the file isn't managed by perforce,
        None is returned
        '''
        if not self.USE_P4:
            return None

        f = self.getFile(f)
        try:
            return self.run('fstat', f)
        except Exception:
            return None

    def isManaged(self, f=None):
        '''
        returns True if the file is managed by perforce, otherwise False
        '''
        if not self.USE_P4:
            return False

        f = self.getFile(f)
        stat = self.getStatus(f)
        if stat:
            # if the file IS managed - only return true if the head action isn't delete - which effectively means the file
            # ISN'T managed...
            try:
                return stat['headAction'] != 'delete'
            except KeyError:
                # this can happen if the file is a new file and is opened for add
                return True
        return False

    managed = isManaged

    def isUnderClient(self, f=None):
        '''
        returns whether the file is in the client's root
        '''
        if not self.USE_P4:
            return False

        f = self.getFile(f)
        results = self.getStatus()
        if not results:
            try:
                errors = results.errors
            except AttributeError:
                return False
            else:
                phrases = ["not in client view", "not under client's root"]

                for e in results.errors:
                    for ph in phrases:
                        if ph in e: return False

        return True

    def getAction(self, f=None):
        '''
        returns the head "action" of the file - if the file isn't in perforce None is returned...
        '''
        if not self.USE_P4:
            return None

        f = self.getFile(f)
        data = self.getStatus(f)

        try:
            return data.get('action', None)
        except AttributeError:
            return None

    action = property(getAction)

    def getHaveHead(self, f=None):
        if not self.USE_P4:
            return False

        f = self.getFile(f)
        data = self.getStatus(f)

        try:
            return data['haveRev'], data['headRev']
        except (AttributeError, TypeError, KeyError):
            return None, None

    def isEdit(self, f=None):
        if not self.USE_P4:
            return False

        editActions = ['add', 'edit']
        action = self.getAction(f)

        # if the action is none, the file may not be managed - check
        if action is None:
            if not self.getStatus(f):
                return None

        return action in editActions

    def isLatest(self, f=None):
        '''
        returns True if the user has the latest version of the file, otherwise False
        '''

        # if no p4 integration, always say everything is the latest to prevent complaints from tools
        if not self.USE_P4:
            return True

        status = self.getStatus(f)
        if not status:
            return None

        # if there is any action on the file then always return True
        if 'action' in status:
            return True

        # otherwise check revision numbers
        try:
            headRev, haveRev = status['headRev'], status['haveRev']

            return headRev == haveRev
        except KeyError:
            return False

    def isDeleteAtHead(self, f=None):
        '''
        Returns True if the file will be deleted at the head revision
        '''
        # if no p4 integration, always say everything is not deleted to prevent complaints from tools
        if not self.USE_P4:
            return False
        status = self.getStatus(f)
        if not status:
            return None

        # if there is any action on the file then always return True
        if ('headAction' in status) and (status['headAction'] == 'delete'):
            return True
        else:
            return False

    def add(self, f=None, type=None):
        if not self.USE_P4:
            return False

        try:
            args = ['add', '-c', self.getOrCreateChange()]
        except:
            return False

        # if the type has been specified, add it to the add args
        if type is not None:
            args += ['-t', type]

        args.append(self.getFile(f))

        ret = p4run(*args)
        if (ret.errors) or (ret == {}):
            return False

        return True

    def edit(self, f=None):
        f = self.getFile(f)
        if not self.USE_P4:

            # if p4 is disabled but the file is read-only, set it to be writeable...
            if not f.getWritable():
                f.setWritable()

            return False

        # if the file is already writeable, assume its checked out already
        if f.getWritable():
            return True

        try:
            ret = p4run('edit', '-c', self.getOrCreateChange(), self.getFile(f))
        except:
            return False

        if (ret.errors) or (ret == {}):
            return False

        return True

    def editoradd(self, f=None):
        if self.edit(f):
            return True

        if self.add(f):
            return True

        return False

    def revert(self, f=None):
        if not self.USE_P4:
            return False

        return self.run('revert', self.getFile(f))

    def sync(self, f=None, force=False, rev=None, change=None):
        '''
        rev can be a negative number - if it is, it works as previous revisions - so rev=-1 syncs to
        the version prior to the headRev.  you can also specify the change number using the change arg.
        if both a rev and a change are specified, the rev is used
        '''
        if not self.USE_P4:
            return False

        f = self.getFile(f)

        # if file is a directory, then we want to sync to the dir
        f = str(f.asfile())
        if not f.startswith(
                '//'):  # depot paths start with // - but windows will try to poll the network for a computer with the name, so if it starts with //, assume its a depot path
            if os.path.isdir(f):
                f = '%s/...' % f

        if rev is not None:
            if rev == 0:
                f += '#none'
            elif rev < 0:
                status = self.getStatus()
                headRev = status['headRev']
                rev += int(headRev)
                if rev <= 0: rev = 'none'
                f += '#%s' % rev
            else:
                f += '#%s' % rev
        elif change is not None:
            f += '@%s' % change

        if force:
            return self.run('sync', '-f', f)
        else:
            return self.run('sync', f)

    def delete(self, f=None):
        if not self.USE_P4:
            return False

        f = self.getFile(f)
        action = self.getAction(f)
        if action is None and self.managed(f):
            return self.run('delete', '-c', self.getOrCreateChange(), f)

    def remove(self, f=None):
        if not self.USE_P4:
            return False

        self.sync(f, rev=0)

    def rename(self, newName, f=None):
        if not self.USE_P4:
            return False

        f = self.getFile(f)

        try:
            action = self.getAction(f)
            if action is None and self.managed(f):
                self.run('integrate', '-c', self.getOrCreateChange(), f, str(newName))
                return self.run('delete', '-c', self.getOrCreateChange(), f)
        except Exception:
            pass
        return False

    def copy(self, newName, f=None):
        if not self.USE_P4:
            return False

        f = self.getFile(f)
        newName = self.getFile(newName)
        action = self.getAction(f)

        if self.managed(f):
            return self.run('integrate', '-c', self.getOrCreateChange(), f, newName)

        return False

    def submit(self, change=None):
        if not self.USE_P4:
            return

        if change is None:
            change = self.getChange().change

        self.run('submit', '-c', change)

    def getChange(self, f=None):
        if not self.USE_P4:
            return P4Change.CHANGE_NUM_INVALID

        f = self.getFile(f)
        stat = self.getStatus(f)
        try:
            return stat.get('change', P4Change.CHANGE_NUM_DEFAULT)
        except (AttributeError, ValueError):
            return P4Change.CHANGE_NUM_DEFAULT

    def setChange(self, newChange=None, f=None):
        '''
        sets the changelist the file belongs to. the changelist can be specified as either a changelist
        number, a P4Change object, or a description. if a description is given, the existing pending
        changelists are searched for a matching description.  use 0 for the default changelist.  if
        None is passed, then the changelist as described by self.DEFAULT_CHANGE is used
        '''
        if not self.USE_P4:
            return

        if isinstance(newChange, int):
            change = newChange
        elif isinstance(newChange, P4Change):
            change = newChange.change
        else:
            change = P4Change.FetchByDescription(newChange, True).change

        f = self.getFile(f)
        self.run('reopen', '-c', change, f)

    def getOtherOpen(self, f=None):
        f = self.getFile(f)
        statusDict = self.getStatus(f)
        try:
            return statusDict['otherOpen']
        except (KeyError, TypeError):
            return []

    def getOrCreateChange(self, f=None):
        '''
        if the file isn't already in a changelist, this will create one.  returns the change number
        '''
        if not self.USE_P4:
            return P4Change.CHANGE_NUM_INVALID

        f = self.getFile(f)
        ch = self.getChange(f)
        if ch == P4Change.CHANGE_NUM_DEFAULT:
            return P4Change.FetchByDescription(self.DEFAULT_CHANGE, True).change

        return ch

    def getChangeNumFromDesc(self, description=None, createIfNotFound=True):
        if description is None:
            description = self.DEFAULT_CHANGE

        return P4Change.FetchByDescription(description, createIfNotFound).change

    def allPaths(self, f=None):
        '''
        returns all perforce paths for the file (depot path, workspace path and disk path)
        '''
        if not self.USE_P4:
            return None

        f = self.getFile(f)

        return toDepotAndDiskPaths([f])[0]

    def toDepotPath(self, f=None):
        '''
        returns the depot path to the file
        '''
        if not self.USE_P4:
            return None

        return self.allPaths(f)[0]

    def toDiskPath(self, f=None):
        '''
        returns the disk path to a depot file
        '''
        if not self.USE_P4:
            return None

        return self.allPaths(f)[1]


P4Data = P4File  # userd to be called P4Data - this is just for any legacy references...


def findInPyPath(filename):
    '''
    given a filename or path fragment, will return the full path to the first matching file found in
    the sys.path variable
    '''
    for p in map(Path, sys.path):
        loc = p / filename
        if loc.exists:
            return loc

    return None


def findInPath(filename):
    '''
    given a filename or path fragment, will return the full path to the first matching file found in
    the PATH env variable
    '''
    for p in map(Path, os.environ['PATH'].split(';')):
        loc = p / filename
        if loc.exists:
            return loc

    return None

# end
