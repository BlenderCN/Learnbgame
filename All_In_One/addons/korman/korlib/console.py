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

import bpy
import ctypes
import math
import sys

if sys.platform == "win32":
    class _Coord(ctypes.Structure):
        _fields_ = [("x", ctypes.c_short),
                    ("y", ctypes.c_short)]
    class _SmallRect(ctypes.Structure):
        _fields_ = [("Left", ctypes.c_short),
                    ("Top", ctypes.c_short),
                    ("Right", ctypes.c_short),
                    ("Bottom", ctypes.c_short),]
    class _ConsoleScreenBufferInfo(ctypes.Structure):
        _fields_ = [("dwSize", _Coord),
                    ("dwCursorPosition", _Coord),
                    ("wAttributes", ctypes.c_ushort),
                    ("srWindow", _SmallRect),
                    ("dwMaximumWindowSize", _Coord)]

    class _ConsoleCursor:
        def __init__(self):
            self._handle = ctypes.windll.kernel32.GetStdHandle(-11)
            self.position = _Coord(0, 0)

        @property
        def _screen_buffer_info(self):
            info = _ConsoleScreenBufferInfo()
            ctypes.windll.kernel32.GetConsoleScreenBufferInfo(self._handle, ctypes.pointer(info))
            return info

        def clear(self):
            info = self._screen_buffer_info
            curPos = info.dwCursorPosition
            num_cols = curPos.y - self.position.y
            num_rows = curPos.x - self.position.x
            num_chars = (info.dwSize.x * num_cols) + num_rows
            if num_chars:
                nWrite = ctypes.c_ulong()
                empty_char = ctypes.c_char(b' ')
                ctypes.windll.kernel32.FillConsoleOutputCharacterA(self._handle, empty_char,
                                                                   num_chars, self.position,
                                                                   ctypes.pointer(nWrite))

        def reset(self):
            ctypes.windll.kernel32.SetConsoleCursorPosition(self._handle, self.position)

        def update(self):
            info = _ConsoleScreenBufferInfo()
            ctypes.windll.kernel32.GetConsoleScreenBufferInfo(self._handle, ctypes.pointer(info))
            self.position = info.dwCursorPosition
else:
    class _ConsoleCursor:
        def clear(self):
            # Only clears the current line, unfortunately.
            sys.stdout.write("\x1B[K")

        def reset(self):
            # Forcibly clears the line after resetting, just in case more
            # than one junk line was printed from somewhere else.
            sys.stdout.write("\x1B[u\x1B[K")

        def update(self):
            sys.stdout.write("\x1B[s")


class ConsoleCursor(_ConsoleCursor):
    def __enter__(self):
        self.clear()
        self.reset()
        return self

    def __exit__(self, type, value, traceback):
        self.update()


class ConsoleToggler:
    _instance = None

    def __init__(self, want_console=None):
        if want_console is not None:
            self._console_wanted = want_console

    def __new__(cls, want_console=None):
        if cls._instance is None:
            assert want_console is not None
            cls._instance = object.__new__(cls)
            cls._instance._console_was_visible = cls.is_console_visible()
            cls._instance._console_wanted = want_console
            cls._instance._context_active = False
            cls._instance.keep_console = False
        return cls._instance

    def __enter__(self):
        if self._context_active:
            raise RuntimeError("ConsoleToggler context manager is not reentrant")
        self._console_visible = self.is_console_visible()
        self._context_active = True
        self.activate_console()
        return self

    def __exit__(self, type, value, traceback):
        if not self._console_was_visible and self._console_wanted:
            if self.keep_console:
                # Blender thinks the console is currently not visible. However, it actually is.
                # So, we will fire off the toggle operator to keep Blender's internal state valid
                bpy.ops.wm.console_toggle()
            else:
                self.hide_console()
        self._context_active = False
        self.keep_console = False
        return False

    def activate_console(self):
        if sys.platform == "win32":
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if self._console_wanted:
                ctypes.windll.user32.ShowWindow(hwnd, 1)
            if self._console_was_visible or self._console_wanted:
                ctypes.windll.user32.BringWindowToTop(hwnd)

    @staticmethod
    def hide_console():
        if sys.platform == "win32":
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            ctypes.windll.user32.ShowWindow(hwnd, 0)

    @staticmethod
    def is_console_visible():
        if sys.platform == "win32":
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            return bool(ctypes.windll.user32.IsWindowVisible(hwnd))

    @staticmethod
    def is_platform_supported():
        # If you read Blender's source code, GHOST_toggleConsole (the "Toggle System Console" menu
        # item) is only implemented on Windows. The majority of our audience is on Windows as well,
        # so I honestly don't see this as an issue...
        return sys.platform == "win32"
