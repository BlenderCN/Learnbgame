import os

try:
    import _winreg
except:
    _winreg = None

_application_paths = {}
_binary_paths = ["/usr/bin", "/usr/local/bin"]
_extra_binary_paths = []
_win_pypaths = ["C:\\Python27","C:\\Python26"]

def add_binary_path(path):
    _binary_paths.add(path)
    # remove applications we didnt find from the cache since
    # they might be found in the new path
    for name, _path in _application_paths.items():
        if not _path:
            _application_paths.pop(name)

def find_application(name, user_paths=[], reset=False):
    if name in _application_paths and not reset:
        return _application_paths[name]
    # look for command with same name
    for path in _binary_paths + _extra_binary_paths + user_paths:
        app_path = os.path.join(path, name)
        if os.path.exists(app_path):
            _application_paths[name] = app_path
            return app_path
    # now look for .exe
    for path in _extra_binary_paths + user_paths:
        app_path = os.path.join(path, name+'.exe')
        if os.path.exists(app_path):
            _application_paths[name] = app_path
            return app_path
    # save the miss so we don't have to search next time
    _application_paths[name] = None

def find_python2(user_paths=[]):
    path = find_application('python', user_paths + _win_pypaths)
    if path:
        return path
    if _winreg:
        for pyversion in ["2.7", "2.6"]:
            regpath = "SOFTWARE\\Python\\Pythoncore\\"+pyversion+"\\"
            installpath = ""
            try:
                reg = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, regpath)
                installpath = _winreg.QueryValue(reg, 'InstallPath')
                _winreg.CloseKey(reg)
            except EnvironmentError:
                pass
            if installpath:
                apppath = os.path.join(installpath, 'python.exe')
                if os.path.exists(apppath):
                    _application_paths['python'] = apppath
                return apppath
