# Copyright (C) 2018 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
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

# system imports
import argparse

# Thanks to: http://stackoverflow.com/questions/6076690/verbose-level-with-argparse-and-multiple-v-options
class verbose_action(argparse.Action):
    def __call__(self, parser, args, values, options_string=None):
        if values == None:
            values = '1'
        try:
            values = int(values)
        except ValueError:
            values = values.count('v')+1
        setattr(args, self.dest, values)
