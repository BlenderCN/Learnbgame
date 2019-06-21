### BEGIN GPL LICENSE BLOCK #####
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

# <pep8 compliant>


class Symbol():
    def __init__(self, name, scope, typedesc, value=None):
        # XXX valid value types depend on the converter system
        """
        from bpy.types import NodeSocket
        if typedesc.basetype == 'string':
            pass
        else:
            try:
                assert(isinstance(value, NodeSocket))
            except:
                raise Exception("Expected NodeSocket value, got %r" % value)
        """
        self.name = name
        self.scope = scope
        self.typedesc = typedesc
        self.value = value

    def __repr__(self):
        return "<Symbol at %s, name=%r, scope=%r, typedesc=%r, value=%r>" % (hex(id(self)), self.name, self.scope, self.typedesc, self.value)

    def copy_assign(self, value):
        symbol = Symbol(self.name, self.scope, self.typedesc, value)
        return symbol
