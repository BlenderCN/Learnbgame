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
"""
A module for printing messages to the console and optionally writing the messages to a log file.

@author: Demian Wright
"""

from . import const

# I've implemented this myself instead of using the standard logging because I needed a feature where the log file is only written if there were warnings logged.
# I could not figure out a way to do that with the standard logging library so it was just faster to write it myself.

__LOG_LINES = []
__WRITE_FILE = True
__ON_WARNINGS_ONLY = True
__HAS_WARNINGS = False


def configure(write_file, write_only_on_warnings):
    """Configures the logger with the specified options.

    Args:
        write_file (bool): Write log to a file?
        write_only_on_warnings (bool): Write log to a file but only if warnings were logged?
    """
    global __WRITE_FILE, __ON_WARNINGS_ONLY

    __WRITE_FILE = write_file
    __ON_WARNINGS_ONLY = write_only_on_warnings


def __log(log_type, code, message, is_warning, indents=0):
    """Prints the given message to the console and additionally to a log file if so specified at logger configuration.

    Args:
        log_type (string): Log type label.
        code (string): Unique code for the message.
        message (string): Log message.
        is_warning (bool): Is the message a warning?
        indents (int): The number of indents to add in front of the message. (Default: 0)
    """
    global __HAS_WARNINGS

    if log_type is None:
        message = "{}{}".format(const.LOG_INDENT * indents, message)
    else:
        message = "{}[{}:{}] {}".format(const.LOG_INDENT * indents, log_type, code, message)

    print(message)

    # If log will be written to a file, append the message to the sequence for writing later.
    if __WRITE_FILE:
        __LOG_LINES.append(message)

        if is_warning and not __HAS_WARNINGS:
            __HAS_WARNINGS = True


def info(message, indents=0):
    """Prints the given message to the console and additionally to a log file if so specified at logger configuration.

    Args:
        message (string): Log message.
        indents (int): The number of indents to add in front of the message. (Default: 0)
    """
    __log(None, None, message, False, indents)


def warning(code, message, indents=0):
    """Prefixes the message with '[WARNING:<code>] ', prints it to the console (and additionally to a log file if so specified at logger configuration), and logs the message as a warning.

    Args:
        code (string): Unique warning code.
        message (string): Log message.
        indents (int): The number of indents to add in front of the message. (Default: 0)
    """
    __log("WARNING", code, message, True, indents)


def error(code, message, indents=0):
    """Prefixes the message with '[ERROR:<code>] ', prints it to the console (and additionally to a log file if so specified at logger configuration), and logs the message as a warning.

    Args:
        code (string): Unique error code.
        message (string): Log message.
        indents (int): The number of indents to add in front of the message. (Default: 0)
    """
    __log("ERROR", code, message, True, indents)


def fatal(message):
    """Prefixes the message with '[FATAL:<code>] ', prints it to the console (and additionally to a log file if so specified at logger configuration), and logs the message as a warning.

    Args:
        message (string): The unique code followed by the log message after a space character.
    """
    space_pos = message.index(" ")
    __log("FATAL", message[:space_pos], message[space_pos + 1:], True, 0)


def build_countable_message(message_start, count, alternatives, message_end="", message_zero=None):
    """Builds a sentence with the correct message ending (i.e. singular or plural) based on the countable element.

    The function will append the start, the count, the singular or plural, and the end of the message one after the other without adding spaces in between.

    Args:
        message_start (string): The first part of message that will be the same for singular and plural messages.
        count (int): The countable element in the message that will determine if the message is singular or plural.
        alternatives (sequence of strings): A sequence of strings where:
                                                - the first element will be used if count is 1,
                                                - the second element will be used if count is greater than 1 or count is 0 and message_zero is not specified.
        message_end (string): An optional final part of the message.
        message_zero (string): An optional message to show instead if count is 0.

    Returns:
        A grammatically correct string.
    """
    # Determine which message to use from the end alternatives.
    if count == 0:
        if message_zero is not None:
            # If a zero count message was specified, use that instead.
            return message_zero
        else:
            # Else the count is 0 but no zero count message was specified, use the plural message.
            message_index = 1
    elif count == 1:
        # Index 0 contains the singular.
        message_index = 0
    else:
        # Index 1 contains the plural.
        message_index = 1

    return "{}{}{}{}".format(message_start, count, alternatives[message_index], message_end)


def clear_log():
    """Deletes all log lines and resets the warning flag"""
    global __LOG_LINES, __HAS_WARNINGS

    __LOG_LINES = []
    __HAS_WARNINGS = False


def write_log(logpath):
    """Writes a log file (if so configured) to the specified path.

    Args:
        logpath (string): A path to the log file to write, including the extension.
    """
    # Write a log file?
    # Anything to write?
    # Are we only writing a log if warnings were generated and warnings exist?
    # Are we writing a log regardless if warnings were generated?
    if (__WRITE_FILE and len(__LOG_LINES) > 0) and (__ON_WARNINGS_ONLY and __HAS_WARNINGS) or not __ON_WARNINGS_ONLY:
        print("Writing log to: {}".format(logpath))

        # Write the log file.
        with open(logpath, "w") as file:
            for line in __LOG_LINES:
                file.write("{}\n".format(line))
