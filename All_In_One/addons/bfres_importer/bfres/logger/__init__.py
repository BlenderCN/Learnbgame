# This file is part of botwtools.
#
# botwtools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# botwtools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with botwtools.  If not, see <https://www.gnu.org/licenses/>.


# Sets up logging nicely to output to console with colours.
import logging
import os

log = logging.getLogger()
log.setLevel(logging.DEBUG)
_is_setup = False

def setup(appName):
    global _is_setup
    if _is_setup: return
    class MyFormatter(logging.Formatter):
        levels = {
            'CRITICAL': '\x1B[38;5;9mC', # red
            'ERROR':    '\x1B[38;5;9mE', # red
            'WARNING':  '\x1B[38;5;10mW', # yellow
            'INFO':     '\x1B[38;5;14mI', # cyan
            'DEBUG':    '\x1B[38;5;15mD', # white
        }
        def __init__(self, fmt=None, datefmt=None, style='%'):
            super().__init__(fmt, datefmt, style)

        def format(self, record):
            if record.levelname in self.levels:
                record.levelnamefmt = self.levels[record.levelname]
            else:
                record.levelnamefmt = record.levelname

            if record.threadName == 'MainThread':
                record.threadNameFmt = ''
            else:
                record.threadNameFmt = '\x1B[38;5;6m:' + record.threadName

            #record.pid = os.getpid()

            name = record.name.split('.')
            #if name[0] == appName: name[0] = ''
            record.nameshort = '.'.join(name)
            return super().format(record)

    formatter = MyFormatter(
        #'\x1B[38;5;7m%(asctime)s '
        '%(asctime)s.%(msecs)03d '
        '%(levelnamefmt)s'
        '\x1B[38;5;13m%(nameshort)s'
        '\x1B[38;5;9m:%(lineno)d'
        '%(threadNameFmt)s'
        #'\x1B[38;5;6m:%(pid)s'
        '\x1B[0m %(message)s',
        datefmt='\x1B[38;5;241m%H\x1B[38;5;246m%M\x1B[38;5;251m%S')
        #datefmt='%Y %m%d %H%M%S')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    # uncomment to output to debug.log too
    #fh = logging.FileHandler('fres-importer-debug.log', mode='wt')
    #fh.setLevel(logging.DEBUG)
    #fh.setFormatter(formatter)
    #log.addHandler(fh)
    _is_setup = True
