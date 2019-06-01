# -*- coding: utf8 -*-
# Blender WCP IFF mesh import/export script by Kevin Caccamo
# Copyright © 2013-2016 Kevin Caccamo
# E-mail: kevin@ciinet.org
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# <pep8-80 compliant>

# Classes for IFF data structures
# See the EA IFF 85 specification here:
# https://github.com/1fish2/IFF/tree/master/IFF docs with Commodore revisions/
from struct import pack
from io import StringIO


class IffForm:
    # A FORM is an IFF data structure that can hold CHUNKs or other FORMs
    def __init__(self, name, members=None):
        name = name.strip()
        if len(name) == 4:  # The name of the FORM must be 4 letters long
            self._name = name.upper()
        elif len(name) > 4:
            self._name = name[:4].upper()
        elif len(name) < 4:
            self._name = name.upper().ljust(4)

        for idchar in self._name:
            if ord(idchar) < 0x20 or ord(idchar) > 0x7E:
                raise ValueError(
                    "Invalid name for this " + type(self).__name__)

        if members is not None:
            if not isinstance(members, list):
                raise TypeError(
                    "members must be a list of valid members for an %s!" %
                    (type(self).__name__)
                )

            for member in members:
                if self.is_member_valid(member) == 0:
                    raise TypeError(
                        "Member %r is of an invalid type for an %s!" %
                        (member, type(self).__name__)
                    )

        # Make a slice copy of the member list so that every FORM can have
        # different members. If this is not done, all IffForm objects will have
        # the same members
        self._members = [] if members is None else members

    def __str__(self):
        return "{} {!r}".format(type(self).__name__, self._name)

    def is_member_valid(self, member):
        if (isinstance(member, IffForm) or
                isinstance(member, IffChunk)):
            return 1
        else:
            return 0

    def add_member(self, member_to_add):
        """Add a member to this FORM

        Only CHUNKs or other FORMs may be added to a FORM
        """
        # Only add a member if it is a CHUNK or a FORM
        if self.is_member_valid(member_to_add):
            self._members.append(member_to_add)
        else:
            raise TypeError

    def insert_member(self, member_to_add, pos):
        if self.is_member_valid(member_to_add):
            self._members.insert(pos, member_to_add)
        else:
            raise TypeError

    def remove_member(self, member_to_remove):
        """Remove a member from this FORM"""
        self._members.remove(member_to_remove)

    def replace_member(self, member_to_replace, new_member):
        """Replace a member in this FORM with another one."""
        if (isinstance(member_to_replace, int) and
                member_to_replace < len(self._members)):
            membidx = member_to_replace
        else:
            membidx = self._members.index(member_to_replace)
        self._members[membidx] = new_member

    def to_xmf(self):
        """Convert this FORM to an XMF (IFF Source) string"""
        xmf_string = StringIO()
        xmf_string.write('\nFORM "%s"\n{\n' % self._name)
        for x in self._members:
            xmf_string.write(x.to_xmf())  # All members of a FORM are CHUNKs.
        xmf_string.write("\n}\n")
        return xmf_string.getvalue()

    def to_bytes(self):
        iffbytes = bytearray()
        form_length = 4  # Account for form header/name
        for x in self._members:
            iffbytes.extend(x.to_bytes())
            form_length += 8 + x.get_length()
            # If the chunk contains an odd number of bytes,
            # add an extra 0-byte for padding.
            if form_length % 2 == 1:
                iffbytes.append(0)
                form_length += 1

        iffbytes = (b"FORM" + pack(">l", form_length) +
                    self._name.encode("ascii", "replace") +
                    iffbytes)
        return iffbytes

    def get_num_members(self):
        return len(self._members)

    def has_members(self):
        return len(self._members) > 0

    def clear_members(self):
        """Remove all members from this FORM"""
        self._members = []
        self._length = 4

    def get_length(self):
        form_length = 4
        for x in self._members:
            form_length += 8 + x.get_length()
            # If the chunk contains an odd number of bytes,
            # add an extra 0-byte for padding.
            if form_length % 2 == 1:
                form_length += 1
        return form_length


class IffChunk(IffForm):
    # A CHUNK is an IFF data structure that holds binary data,
    # such as integers, floats, or strings.

    def __init__(self, name, members=None):
        super().__init__(name, members)
        memblength = 0
        if members is not None and len(members) > 0:
            for m in members:
                membtype = self.is_member_valid(m)
                if membtype == 1:
                    memblength += 4  # Number
                elif membtype == 2:
                    memblength += len(m)  # String
        self._length = memblength

    def is_member_valid(self, member):
        if (isinstance(member, int) or
                isinstance(member, float)):
            return 1
        elif isinstance(member, str):
            return 2
        else:
            return 0

    def add_member(self, member_to_add):
        """Add a member to this CHUNK

        Only ints, floats, and strings can be added to a CHUNK.
        """
        membtype = self.is_member_valid(member_to_add)
        if membtype > 0:
            self._members.append(member_to_add)
            if membtype == 1:  # Numeric (int/float)
                self._length += 4
            elif membtype == 2:  # String
                self._length += len(member_to_add) + 1  # Null-terminated
        else:
            raise TypeError("Tried to add an invalid piece of data!")

    def insert_member(self, member_to_add, pos):
        membtype = self.is_member_valid(member_to_add)
        omembtype = (
            self.is_member_valid(self._members[pos - 1]) if pos > 0 else 0)
        if membtype > 0:
            self._members.insert(pos, member_to_add)
            if membtype == 1:
                if omembtype == 2:
                    self._length += 1
                self._length += 4
            elif membtype == 2:
                self._length += len(member_to_add)
        else:
            raise TypeError

    def remove_member(self, member_to_remove):
        """Remove a member from this FORM"""
        if (isinstance(member_to_remove, int) or
                isinstance(member_to_remove, float)):
            self._length -= 4
        else:
            self._length -= len(member_to_remove)
        self._members.remove(member_to_remove)

    def replace_member(self, member_to_replace, new_member):
        if member_to_replace > len(self._members):
            raise ValueError("Member index cannot be larger than the internal"
                             "member list length!")

        new_member_type = self.is_member_valid(new_member)
        if new_member_type == 1:
            new_member_length = 4
        elif new_member_type == 2:
            new_member_length = len(new_member) + 1
        else:
            raise TypeError("Member is of an invalid type for an IffChunk!")

        old_member_type = self.is_member_valid(
            self._members[member_to_replace])
        if old_member_type == 1:
            old_member_length = 4
        elif old_member_type == 2:
            old_member_length = len(self._members[member_to_replace]) + 1

        self._length += (new_member_length - old_member_length)
        self._members[member_to_replace] = new_member

    def clear_members(self):
        """Remove all members from this FORM"""
        self._members = []
        self._length = 0

    def to_xmf(self):
        """
        Returns an XMF string.
        """
        xmf_string = StringIO()
        xmf_string.write('CHUNK "%s"\n{\n' % self._name)
        for x in self._members:
            if isinstance(x, int):
                xmf_string.write("long %i" % x)
            if isinstance(x, float):
                xmf_string.write("float %f" % x)
            if isinstance(x, str):
                xmf_string.write('cstring "%s"' % x)
            xmf_string.write("\n")
        xmf_string.write("}")
        return xmf_string.getvalue()

    def to_bytes(self):
        iffbytes = bytearray()
        for x in self._members:
            if isinstance(x, int):
                iffbytes.extend(pack("<l", x))
            if isinstance(x, float):
                iffbytes.extend(pack("<f", x))
            if isinstance(x, str):
                iffbytes.extend(x.encode("ascii", "replace"))
                iffbytes.append(0)

        iffbytes = (self._name.encode("ascii", "replace") +
                    pack(">l", self._length) + iffbytes)
        return iffbytes

    def get_length(self):
        return self._length


class IffFile:
    def __init__(self, root_form=IffForm("NONE"),
                 filename="untitled"):
        if isinstance(root_form, IffForm):
            self.root_form = root_form
        elif isinstance(root_form, str):
            self.root_form = IffForm(root_form)
        else:
            raise TypeError(
                "Root FORM must be a string (which will be made "
                "into a FORM object with the given name) or a FORM object."
            )
        if isinstance(filename, str):
            self.filename = filename
        else:
            raise TypeError("Filename must be a string")

        self.comment = b""

    def to_xmf(self):
        xmf_string = StringIO()
        xmf_string.write('IFF "')
        xmf_string.write(self.filename)
        xmf_string.write('"\n{')
        xmf_string.write(self.root_form.to_xmf())
        xmf_string.write("}\n")
        return xmf_string.getvalue()

    def to_bytes(self):
        return self.root_form.to_bytes() + self.comment

    def set_root_form(self, root_form):
        if isinstance(root_form, IffForm):
            self.root_form = root_form

    def get_root_form(self):
        return self.root_form

    def set_comment(self, comment):
        if not isinstance(comment, str) and not isinstance(comment, bytes):
            raise TypeError("Comment must be a string or a byte string!")

        self.comment = comment
        if isinstance(self.comment, str):
            self.comment = self.comment.encode()

    def write_file_xmf(self):
        fname = self.filename + ".xmf"
        try:
            fd = open(fname, "x")
            fd.close()
        except FileExistsError:
            print("File already exists! Overwriting...")
        fd = open(fname, "w")
        fd.write(self.to_xmf())
        fd.close()

    def write_file_bin(self):
        fname = self.filename + ".iff"
        try:
            fd = open(fname, "x")
            fd.close()
        except FileExistsError:
            print("File already exists! Overwriting...")
        fd = open(fname, "wb")
        fd.write(self.to_bytes())
        fd.close()
