# #############################################################################
# AUTHOR BLOCK:
# #############################################################################
#
# RIB Mosaic RenderMan(R) IDE, see <http://sourceforge.net/projects/ribmosaic>
# by Eric Nathen Back aka WHiTeRaBBiT, 01-24-2010
# This script is protected by the GPL: Gnu Public License
# GPL - http://www.gnu.org/copyleft/gpl.html
#
# #############################################################################
# GPL LICENSE BLOCK:
# #############################################################################
#
# Script Copyright (C) Eric Nathen Back
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# #############################################################################
# COPYRIGHT BLOCK:
# #############################################################################
#
# The RenderMan(R) Interface Procedures and Protocol are:
# Copyright 1988, 1989, 2000, 2005 Pixar
# All Rights Reserved
# RenderMan(R) is a registered trademark of Pixar
#
# #############################################################################
# COMMENT BLOCK:
# #############################################################################
#
# Error handling module.
#
# This script is PEP 8 compliant
#
# Search TODO for incomplete code
# Search FIXME for improper code
# Search XXX for broken code
#
# #############################################################################
# END BLOCKS
# #############################################################################

import os
import traceback


# #### Global variables

MODULE = os.path.dirname(__file__).split(os.sep)[-1]
exec("import " + MODULE + " as rm")


# #############################################################################
# ERROR HANDLER CLASS
# #############################################################################

# #### Define the global error handler class

class RibmosaicError(Exception):
    """UI and console error messages"""

    # ### Private attributes

    _message = ""  # Message to report
    _exc_info = None  # Execution info and traceback object to print

    def __init__(self, message, exc_info=None):
        self._message = message
        self._exc_info = exc_info

    def __str__(self):
        return self._message

    def ReportError(self, operator=None):
        print(rm.ENGINE + " Error: " + self._message)
        traceback.print_exc()

        if self._exc_info:
            traceback.print_tb(self._exc_info[2])
            for t in self._exc_info[:2]:
                print(t)

        if operator:
            operator.report({'ERROR'}, self._message)
