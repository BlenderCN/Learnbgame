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

from ..korlib import ConsoleCursor, ConsoleToggler
from .explosions import NonfatalExportError
from pathlib import Path
import threading
import time

_HEADING_SIZE = 60
_MAX_ELIPSES = 3
_MAX_TIME_UNTIL_ELIPSES = 2.0

class _ExportLogger:
    def __init__(self, print_logs, age_path=None):
        self._errors = []
        self._porting = []
        self._warnings = []
        self._age_path = Path(age_path) if age_path is not None else None
        self._file = None
        self._print_logs = print_logs
        self._time_start_overall = 0

    def __enter__(self):
        assert self._age_path is not None

        # Make the log file name from the age file path -- this ensures we're not trying to write
        # the log file to the same directory Blender.exe is in, which might be a permission error
        my_path = self._age_path.with_name("{}_export".format(self._age_path.stem)).with_suffix(".log")
        self._file = open(str(my_path), "w")
        return self

    def __exit__(self, type, value, traceback):
        if value is not None:
            ConsoleToggler().keep_console = not isinstance(value, NonfatalExportError)
        self._file.close()
        return False

    def error(self, *args, **kwargs):
        assert args
        indent = kwargs.get("indent", 0)
        msg = "{}ERROR: {}".format("    " * indent, args[0])
        if len(args) > 1:
            msg = msg.format(*args[1:], **kwargs)
        if self._file is not None:
            self._file.writelines((msg, "\n"))
        if self._print_logs:
            print(msg)
        cache = args[0] if len(args) == 1 else args[0].format(*args[1:])
        self._errors.append(cache)

    def msg(self, *args, **kwargs):
        assert args
        indent = kwargs.get("indent", 0)
        msg = "{}{}".format("    " * indent, args[0])
        if len(args) > 1:
            msg = msg.format(*args[1:], **kwargs)
        if self._file is not None:
            self._file.writelines((msg, "\n"))
        if self._print_logs:
            print(msg)

    def port(self, *args, **kwargs):
        assert args
        indent = kwargs.get("indent", 0)
        msg = "{}PORTING: {}".format("    " * indent, args[0])
        if len(args) > 1:
            msg = msg.format(*args[1:], **kwargs)
        if self._file is not None:
            self._file.writelines((msg, "\n"))
        if self._print_logs:
            print(msg)
        cache = args[0] if len(args) == 1 else args[0].format(*args[1:])
        self._porting.append(cache)


    def progress_add_step(self, name):
        pass

    def progress_advance(self):
        pass

    def progress_complete_step(self):
        pass

    def progress_end(self):
        if self._age_path is not None:
            export_time = time.perf_counter() - self._time_start_overall
            self.msg("\nExported '{}' in {:.2f}s", self._age_path.name, export_time)

    def progress_increment(self):
        pass

    def progress_start(self, action):
        if self._age_path is not None:
            self.msg("Exporting '{}'", self._age_path.name)
        self._time_start_overall = time.perf_counter()

    def raise_errors(self):
        num_errors = len(self._errors)
        if num_errors == 1:
            raise NonfatalExportError(self._errors[0])
        elif num_errors:
            raise NonfatalExportError("""{} errors were encountered during export. Check the export log for more details:
                                         {}""", num_errors, self._file.name)

    def save(self):
        # TODO
        pass

    def warn(self, *args, **kwargs):
        assert args
        indent = kwargs.get("indent", 0)
        msg = "{}WARNING: {}".format("    " * indent, args[0])
        if len(args) > 1:
            msg = msg.format(*args[1:], **kwargs)
        if self._file is not None:
            self._file.writelines((msg, "\n"))
        if self._print_logs:
            print(msg)
        cache = args[0] if len(args) == 1 else args[0].format(*args[1:])
        self._warnings.append(cache)


class ExportProgressLogger(_ExportLogger):
    def __init__(self, age_path=None):
        super().__init__(False, age_path)

        # Long running operations like the Blender bake_image call make it seem like we've hung
        # because it is difficult to inspect the progress of Blender's internal operators. The best
        # solution here is to move printing into a thread that can detect long-running ops and display
        # something visible such as a moving elipsis
        self._cursor = ConsoleCursor()
        self._thread = threading.Thread(target=self._progress_thread)
        self._queued_lines = []
        self._print_condition = threading.Condition()
        self._volatile_line = ""

        # Progress manager
        self._progress_alive = False
        self._progress_steps = []
        self._step_id = -1
        self._step_max = 0
        self._step_progress = 0
        self._time_start_step = 0

    def __exit__(self, type, value, traceback):
        if value is not None:
            export_time = time.perf_counter() - self._time_start_overall
            with self._print_condition:
                self._progress_print_step(done=(self._step_progress == self._step_max), error=True)
                self._progress_print_line("\nABORTED AFTER {:.2f}s".format(export_time))
                self._progress_print_heading("ERROR")
                self._progress_print_line(str(value))
                self._progress_print_heading()
                self._progress_alive = False
        return super().__exit__(type, value, traceback)

    def progress_add_step(self, name):
        assert self._step_id == -1
        self._progress_steps.append(name)

    def progress_advance(self):
        """Advances the progress bar to the next step"""
        if self._step_id != -1:
            self._progress_print_step(done=True)
        assert self._step_id < len(self._progress_steps)

        self._step_id += 1
        self._step_max = 0
        self._step_progress = 0
        self._time_start_step = time.perf_counter()
        self._progress_print_step()

    def progress_complete_step(self):
        """Manually completes the current step"""
        assert self._step_id != -1
        self._progress_print_step(done=True)

    def progress_end(self):
        self._progress_print_step(done=True)
        assert self._step_id+1 == len(self._progress_steps)

        export_time = time.perf_counter() - self._time_start_overall
        with self._print_condition:
            if self._age_path is not None:
                self.msg("\nExported '{}' in {:.2f}s", self._age_path.name, export_time)
                self._progress_print_line("\nEXPORTED '{}' IN {:.2f}s".format(self._age_path.name, export_time))
            else:
                self._progress_print_line("\nCOMPLETED IN {:.2f}s".format(export_time))
            self._progress_print_heading()
            self._progress_print_line("")
            self._progress_alive = False

        # Ensure the got dawg thread goes good-bye
        self._thread.join(timeout=5.0)
        assert not self._thread.is_alive()

    def progress_increment(self):
        """Increments the progress of the current step"""
        assert self._step_id != -1
        self._step_progress += 1
        if self._step_max != 0:
            self._progress_print_step()

    def _progress_print_line(self, line):
        with self._print_condition:
            self._queued_lines.append(line)
            self._print_condition.notify()

    def _progress_print_volatile(self, line):
        with self._print_condition:
            self._volatile_line = line
            self._print_condition.notify()

    def _progress_print_heading(self, text=None):
        if text:
            num_chars = len(text)
            border = "-" * int((_HEADING_SIZE - (num_chars + 2)) / 2)
            pad = " " if num_chars % 2 == 1 else ""
            line = "{border} {pad}{text} {border}".format(border=border, pad=pad, text=text)
            self._progress_print_line(line)
        else:
            self._progress_print_line("-" * _HEADING_SIZE)

    def _progress_print_step(self, done=False, error=False):
        with self._print_condition:
            if done:
                stage = "DONE IN {:.2f}s".format(time.perf_counter() - self._time_start_step)
                print_func = self._progress_print_line
                self._progress_print_volatile("")
            else:
                if self._step_max != 0 and self._step_progress != 0:
                    stage = "{} of {}".format(self._step_progress, self._step_max)
                else:
                    stage = ""
                print_func = self._progress_print_line if error else self._progress_print_volatile

            # ALLLLL ABOARD!!!!! HAHAHAHA
            step_name = self._progress_steps[self._step_id]
            whitespace = ' ' * (self._step_spacing - len(step_name))
            num_steps = len(self._progress_steps)
            step_id = self._step_id + 1
            stage_max_whitespace = len(str(num_steps)) * 2
            stage_space_used = len(str(step_id)) + len(str(num_steps))
            stage_whitespace = ' ' * (stage_max_whitespace - stage_space_used + 1)
            # f-strings would be nice here...
            line = "{step_name}{step_whitespace}(step {step_id}/{num_steps}):{stage_whitespace}{stage}".format(
                step_name=step_name, step_whitespace=whitespace, step_id=step_id, num_steps=num_steps,
                stage_whitespace=stage_whitespace, stage=stage)
            print_func(line)

    def _progress_get_max(self):
        return self._step_max
    def _progress_set_max(self, value):
        assert self._step_id != -1
        self._step_max = value
        self._progress_print_step()
    progress_range = property(_progress_get_max, _progress_set_max)

    def progress_start(self, action):
        super().progress_start(action)

        # Need to know the spacing for this junk
        self._step_spacing = max((len(i) for i in self._progress_steps)) + 4

        # Begin displaying the progress console
        self._progress_print_heading("Korman")
        self._progress_print_heading(action)
        self._progress_alive = True
        self._thread.start()

    def _progress_thread(self):
        num_dots = 0
        self._cursor.update()

        while self._progress_alive:
            with self._print_condition:
                signalled = self._print_condition.wait(timeout=1.0)
                print(end='\r')

                # First, we need to print out any queued whole lines.
                # NOTE: no need to lock anything here as Blender uses CPython (GIL)
                with self._cursor:
                    if self._queued_lines:
                        print(*self._queued_lines, sep='\n')
                        self._queued_lines.clear()

                # Now, we need to print out the current volatile line, if any.
                if self._volatile_line:
                    # On Windows, if we clear the line, the volatile line is nuked as well.
                    # Probably a race condition in the Win32 console host.
                    self._cursor.reset()
                    print(self._volatile_line, end="")

                    # If the proc is long running, let us display some elipses so as to not alarm the user
                    if self._time_start_step != 0:
                        if (time.perf_counter() - self._time_start_step) > _MAX_TIME_UNTIL_ELIPSES:
                            num_dots = 0 if signalled or num_dots == _MAX_ELIPSES else num_dots + 1
                        else:
                            num_dots = 0
                    print('.' * num_dots, end=" " * (_MAX_ELIPSES - num_dots))
                    self._cursor.update()

    def _progress_get_current(self):
        return self._step_progress
    def _progress_set_current(self, value):
        assert self._step_id != -1
        self._step_progress = value
        if self._step_max != 0:
            self._progress_print_step()
    progress_value = property(_progress_get_current, _progress_set_current)


class ExportVerboseLogger(_ExportLogger):
    def __init__(self, age_path=None):
        super().__init__(True, age_path)
        self.progress_range = 0
        self.progress_value = 0

    def __exit__(self, type, value, traceback):
        if value is not None:
            export_time = time.perf_counter() - self._time_start_overall
            self.msg("\nAborted after {:.2f}s", export_time)
            self.msg("Error: {}", value)
        return super().__exit__(type, value, traceback)
