# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import os
import re
import platform


LOG_FILE_PATH = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log.txt'))
LOG_CONVERT = re.compile("\033\[[0-9;]+m")
NUMBER_OF_WARNINGS = 0


def clear_log():
    global NUMBER_OF_WARNINGS
    NUMBER_OF_WARNINGS = 0
    with open(LOG_FILE_PATH, mode='w', encoding='utf-8', ):
        # clear log file..
        pass


clear_log()


def copy_paste_log(log_file_path):
    import shutil
    shutil.copyfile(LOG_FILE_PATH, log_file_path)


class LogStyles:
    NORMAL = "\033[40m\033[32m"
    HEADER = "\033[46m\033[30m"
    MESSAGE = "\033[42m\033[30m"
    WARNING = "\033[43m\033[1;30mWARNING: "
    ERROR = "\033[41m\033[1;30mERROR: "
    END = "\033[0m"
    EOL = "\n"


if(platform.system() == 'Windows'):
    # no pretty logging for windows
    LogStyles.NORMAL = ""
    LogStyles.HEADER = ""
    LogStyles.MESSAGE = ""
    LogStyles.WARNING = "WARNING: "
    LogStyles.ERROR = "ERROR: "
    LogStyles.END = ""


def log(msg="", indent=0, style=LogStyles.NORMAL, instance=None, prefix="> ", ):
    global NUMBER_OF_WARNINGS
    if(style == LogStyles.WARNING):
        NUMBER_OF_WARNINGS += 1
    
    if(instance is None):
        inst = ""
    else:
        cn = instance.__class__.__name__
        cl = cn.split(".")
        inst = "{0}: ".format(cl[-1])
    
    m = "{0}{1}{2}{3}{4}{5}".format("    " * indent, style, prefix, inst, msg, LogStyles.END)
    
    print(m)
    with open(LOG_FILE_PATH, mode='a', encoding='utf-8', ) as f:
        f.write("{}{}".format(re.sub(LOG_CONVERT, '', m), LogStyles.EOL))


def log_args(locals, self, header="arguments: ", indent=1, style=LogStyles.NORMAL, prefix="> ", ):
    import inspect
    l = dict([(k, v) for k, v in locals.items() if v != self and k != '__class__'])
    f = [i for i in inspect.getfullargspec(self.__init__).args if i != 'self']
    t = "    "
    s = " "
    hl = 0
    for i in f:
        if(len(i) > hl):
            hl = len(i)
    # hl += 1
    vs = ["{0}: {1}".format(i.ljust(hl, s), l[i]) for i in f]
    for i, v in enumerate(vs):
        if(i == 0):
            vs[i] = "{0}{1}\n".format(header, v)
        elif(i == len(vs) - 1):
            vs[i] = "{0}{1}{2}{3}".format(t * indent, s * len(prefix), s * len(header), v)
        else:
            vs[i] = "{0}{1}{2}{3}\n".format(t * indent, s * len(prefix), s * len(header), v)
    log("".join(vs), indent, style, None, prefix, )
