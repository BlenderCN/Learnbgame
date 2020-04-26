import getpass, os, platform, re, subprocess, sys

from ..extensions_framework.util import filesystem_path

class PlatformInformation(object):
    '''
    Gather info about this machine for the <metadata> tag
    '''
    platform_id = None
    uname = None
    python = None
    user = None
    def __init__(self):
        self.platform_id = 'Unknown platform'
        if platform.system() == 'Linux':
            self.platform_id = ' '.join(platform.linux_distribution())
        elif platform.system() == 'Windows':
            self.platform_id = ' '.join(platform.win32_ver())
        elif platform.system() == 'Darwin':
            self.platform_id = ' '.join([' '.join(i) if type(i) is tuple else i for i in platform.mac_ver()])
        self.uname = ' '.join(platform.uname())
        self.python = sys.version
        self.user = getpass.getuser()
PlatformInformation = PlatformInformation()

def isLinux():
    return sys.platform[:5].lower() == 'linux'

def isMac():
    return sys.platform[:6].lower() == 'darwin'

def isWindows():
    return sys.platform[:3].lower() == 'win'

def getInstallPath(scene=None):
    # Can use scene.indigo_engine.exe_path as a hint, if available

    if scene != None:
        sip = filesystem_path(scene.indigo_engine.install_path)
        if sip != "" and os.path.exists(sip):
            if os.path.isdir(sip):
                return sip
            else:
                return os.path.dirname(sip)

    if isLinux():
        return "" # TODO

    if isMac():
        return "/Applications/Indigo Renderer/Indigo.app" # Assumption

    if isWindows():
        import winreg
        try:
            hKey = winreg.OpenKey (winreg.HKEY_CURRENT_USER, r"Software\Glare Technologies\Indigo Renderer")
            value = winreg.QueryValueEx (hKey, "InstallDirectory")[0]
        except:
            value = ""
        return value

    return ""

def getSettingsPath():
    if isLinux():
        return os.path.join(getInstallPath(), 'settings.xml')
    elif isMac():
        return os.path.expanduser('~/Library/Application Support/Indigo Renderer/settings.xml')
    elif isWindows():
        return os.path.join(os.getenv('APPDATA'), 'Indigo Renderer', 'settings.xml')
    
    return os.path.join(getInstallPath(), 'settings.xml')
    
def getResourcesPath(scene=None):
    if isLinux():
        return getInstallPath(scene)
    if isMac():
        return os.path.join(getInstallPath(scene), "Contents", "Resources")
    elif isWindows():
        return getInstallPath(scene)

def getGuiPath(scene=None):
    if isLinux():
        return os.path.join(getInstallPath(scene), "indigo")
    if isMac():
        #return os.path.join(getInstallPath(scene), "Contents", "MacOS", "Indigo")
        return getInstallPath(scene)
    elif isWindows():
        return os.path.join(getInstallPath(scene), "indigo.exe")

def getConsolePath(scene=None):
    if isLinux():
        return os.path.join(getInstallPath(scene), "indigo_console")
    if isMac():
        return os.path.join(getInstallPath(scene), "Contents", "MacOS", "IndigoConsole")
    elif isWindows():
        return os.path.join(getInstallPath(scene), "indigo_console.exe")

def getVersion(scene=None):
    try:
        version_str = subprocess.check_output([getConsolePath(scene), '-v'])
        if len(version_str) > 0:
            version_str = version_str.decode().splitlines()[0]
            grps = re.search(r'(\d+)\.(\d+)\.(\d+)', version_str).groups()
            if grps != None and len(grps) == 3:
                return tuple([int(n) for n in grps])
        raise Exception('Error getting Indigo version')
    except Exception:
        return (0,0,0)

def get_worldscale(scene):
    ws = 1.0

    scn_us = scene.unit_settings

    if scn_us.system in ['METRIC', 'IMPERIAL']:
        # The units used in modelling are for display only. behind
        # the scenes everything is in meters
        ws = scn_us.scale_length

    return ws

def count_contiguous(find, s):
    idx = s.find(find)

    if idx == -1:
        return 0
    else:
        count = 0
        while idx < len(s) and s[idx] == find:
            count += 1
            idx += 1

        return count
    
def getAddonDir():
    script_file = os.path.realpath(__file__)
    dir = os.path.dirname(script_file)
    return dir.split(os.path.sep)[-2]


class Borg(object):
    _shared_state = {}

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj.__dict__ = cls._shared_state
        return obj
    
class Counter(Borg):
    counter = 0
    def __init__(self):
        pass
    
    def getNewId(self):
        self.counter += 1
        return self.counter
    