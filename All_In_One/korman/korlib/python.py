#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import generators # Python 2.2
import marshal
import os.path
import sys

_python_executables = {}

class PythonNotAvailableError(Exception):
    pass


def compyle(file_name, py_code, py_version, report=None, indent=0):
    # NOTE: Should never run under Python 2.x
    my_version = sys.version_info[:2]
    assert my_version == (2, 7) or my_version[0] > 2

    # Remember: Python 2.2 file, so no single line if statements...
    idx = file_name.find('.')
    if idx == -1:
        module_name = file_name
    else:
        module_name = file_name[:idx] 

    if report is not None:
        report.msg("Compyling {}", file_name, indent=indent)

    if my_version != py_version:
        import subprocess

        py_executable = _find_python(py_version)
        args = (py_executable, __file__, module_name)
        try:
            py_code = py_code.encode("utf-8")
        except UnicodeError:
            if report is not None:
                report.error("Could not encode '{}'", file_name, indent=indent+1)
            return (False, "Could not encode file")
        result = subprocess.run(args, input=py_code, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            try:
                error = result.stdout.decode("utf-8").replace('\r\n', '\n')
            except UnicodeError:
                error = result.stdout
            if report is not None:
                report.error("Compylation Error in '{}'\n{}", file_name, error, indent=indent+1)
        return (result.returncode == 0, result.stdout)
    else:
        raise NotImplementedError()

def _compyle(module_name, py_code):
    # Old python versions have major issues with Windows style newlines.
    # Also, bad things happen if there is no newline at the end.
    py_code += '\n' # sigh, this is slow on old Python...
    py_code = py_code.replace('\r\n', '\n')
    py_code = py_code.replace('\r', '\n')
    code_object = compile(py_code, module_name, "exec")

    # The difference between us and the py_compile module is twofold:
    # 1) py_compile compyles to a file. We might be exporting to memory, so that's
    #    not what we want.
    # 2) py_compile saves a *pyc format file containing information such as compyle
    #    time and marshal format version. These items are not included in Cyan's
    #    Python.pak format.
    # Therefore, we simply return the marshalled data as a string.
    return marshal.dumps(code_object)

def _find_python(py_version):
    def find_executable(py_version):
        # First, try to use Blender to find the Python executable
        try:
            import bpy
        except ImportError:
            pass
        else:
            userprefs = bpy.context.user_preferences.addons["korman"].preferences
            py_executable = getattr(userprefs, "python{}{}_executable".format(*py_version), None)
            if verify_python(py_version, py_executable):
                return py_executable

        # Second, try looking Python up in the registry.
        try:
            import winreg
        except ImportError:
            pass
        else:
            py_executable = _find_python_reg(winreg.HKEY_CURRENT_USER, py_version)
            if verify_python(py_version, py_executable):
                return py_executable
            py_executable = _find_python_reg(winreg.HKEY_LOCAL_MACHINE, py_version)
            if verify_python(py_version, py_executable):
                return py_executable

        # I give up, you win.
        return None

    py_executable = _python_executables.setdefault(py_version, find_executable(py_version))
    if py_executable:
        return py_executable
    else:
        raise PythonNotAvailableError("{}.{}".format(*py_version))

def _find_python_reg(reg_key, py_version):
    import winreg
    subkey_name = "Software\\Python\\PythonCore\\{}.{}\\InstallPath".format(*py_version)
    try:
        python_dir = winreg.QueryValue(reg_key, subkey_name)
    except FileNotFoundError:
        return None
    else:
        return os.path.join(python_dir, "python.exe")

def package_python(stream, pyc_objects):
    # Python.pak format:
    # uint32_t numFiles
    #     - safeStr filename
    #     - uint32_t offset
    # ~~~~~
    # uint32_t filesz
    # uint8_t data[filesz]
    if not pyc_objects:
        stream.writeInt(0)
        return

    # `stream` might be a plEncryptedStream, which doesn't seek very well at all.
    # Therefore, we will go ahead and calculate the size of the index block so
    # there is no need to seek around to write offset values
    base_offset = 4 # uint32_t numFiles
    data_offset = 0
    pyc_info = [] # sad, but makes life easier...
    for module_name, compyled_code in pyc_objects:
        pyc_info.append((module_name, data_offset, compyled_code))

        # index offset overall
        base_offset += 2 # writeSafeStr length
        # NOTE: This assumes that libHSPlasma's hsStream::writeSafeStr converts
        #       the Python unicode/string object to UTF-8. Currently, this is true.
        base_offset += len(module_name.encode("utf-8")) # writeSafeStr
        base_offset += 4

        # current file data offset
        data_offset += 4  # uint32_t filesz
        data_offset += len(compyled_code)

    stream.writeInt(len(pyc_info))
    for module_name, data_offset, compyled_code in pyc_info:
        stream.writeSafeStr(module_name)
        # offset of data == index size (base_offset) + offset to data blob (data_offset)
        stream.writeInt(base_offset + data_offset)
    for module_name, data_offset, compyled_code in pyc_info:
        stream.writeInt(len(compyled_code))
        stream.write(compyled_code)

def verify_python(py_version, py_exe):
    if not py_exe:
        return False

    import subprocess
    try:
        args = (py_exe, "-V")
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=5)
    except OSError:
        return False
    else:
        output = result.stdout.decode()
    try:
        py_str, py_check = output[:6], output[7:10]
    except IndexError:
        return False
    else:
        if py_str != "Python":
            return False
        return "{}.{}".format(*py_version) == py_check

if __name__ == "__main__":
    # Python tries to be "helpful" on Windows by converting \n to \r\n.
    # Therefore we must change the mode of stdout.
    if sys.platform == "win32":
        import os, msvcrt
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    try:
        module_name = sys.argv[1]
    except IndexError:
        module_name = "<string>"
    py_code_source = sys.stdin.read()
    py_code_object = _compyle(module_name, py_code_source)
    sys.stdout.write(py_code_object)
