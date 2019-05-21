# -*- coding: utf-8 -*-
"""LDR Importer GPLv2 license.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""


from datetime import datetime


class Console:

    @staticmethod
    def __makeMessage(msg, prefix=None):
        """Construct the message for displaying in the console.

        Formats, timestamps, and identifies the message
        as coming from this script.

        @param {Tuple} msg The message to be displayed.
        @param {String} prefix Any text to prefix to the message.
        @return {String} The constucted message.
        """
        msg = [str(text) for text in msg]

        # Prefix text if needed
        if prefix:
            msg.insert(0, str(prefix))

        return "\n[LDR Importer] ({0}) {1}".format(
            datetime.now().strftime("%H:%M:%S.%f")[:-4], " ".join(msg))

    @staticmethod
    def log(*msg):
        """Print logging messages to the console.

        @param {Tuple} msg The message to be displayed.
        """
        print(Console.__makeMessage(msg))

    @staticmethod
    def warn(*msg):
        """Print warning messages to the console.

        @param {Tuple} msg The message to be displayed.
        """
        print(Console.__makeMessage(msg, "Warning!"))
