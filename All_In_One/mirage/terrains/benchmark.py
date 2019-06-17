'''
Copyright (C) 2015 Diego Gangl
<diego@sinestesia.co>

Created by Diego Gangl. This file is part of Mirage.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import time
from datetime import timedelta

start_time = None


def start():
    """ Start the timer """
    
    global start_time
    start_time = time.time()


def stop():
    """ Stop, calculate and reset the benchmark """

    global start_time

    # Calculate and format as HH:MM:SS.UU
    final_time = time.time() - start_time
    formatted = str(timedelta(seconds=final_time))
    formatted = formatted[:10]

    return formatted


def reset():
    """ Convenience for resetting the benchmark """

    start_time = None
