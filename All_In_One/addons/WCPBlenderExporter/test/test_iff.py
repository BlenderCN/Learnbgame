#!/usr/bin/env python3
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
# -*- coding: utf8 -*-

import unittest


class TestIFFFormAndChunk(unittest.TestCase):

    def setUp(self):
        import iff
        self.ifff = iff.IffForm("FONG")
        self.iffc_frst = iff.IffChunk("FRST")
        self.iffc_frst.add_member(12.25)
        self.iffc_frst.add_member(12345)
        self.iffc_frst.add_member("I am poncho man")
        self.ifff.add_member(self.iffc_frst)
        self.iffc_scnd = iff.IffChunk("SCND")
        self.iffc_scnd.add_member(12.25)
        self.iffc_scnd.add_member(12345)
        self.iffc_scnd.add_member("I am poncho man!")
        self.ifff.add_member(self.iffc_scnd)
        self.iffc_gone = iff.IffChunk("GONE")
        self.iffc_gone.add_member(42)
        self.ifff.add_member(self.iffc_gone)
        self.ifff_empty = iff.IffForm("EMPT")
        self.ifff.add_member(self.ifff_empty)

    def test_iff_form(self):
        """Ensure IffForm constructs, adds members, and raises appropriate
        errors properly."""
        import iff
        self.assertIsNotNone(iff.IffForm("BABY"), 'Cannot create Form BABY!')
        self.assertEqual("IffForm 'BOOK'", str(iff.IffForm("BOOK")),
                         "IffForm isn't converting to a string properly!")

        good_members = [iff.IffForm("EMPT"), iff.IffChunk("VOID")]
        bad_members = [192, 2.25, "abc"]

        test_form = iff.IffForm("TEST", good_members)
        self.assertIs(good_members, test_form._members,
                      "IffForm isn't using the members parameter correctly!")

        # Exception testing.
        # Invalid Form ID
        self.assertRaises(ValueError, iff.IffForm, ("\x02Aéâ"))
        # Invalid member types
        self.assertRaises(TypeError, iff.IffForm, "DETA", bad_members)

    def test_iff_chunk(self):
        """Ensure IffChunk constructs, adds members, and raises appropriate
        errors properly."""
        import iff
        self.assertIsNotNone(iff.IffChunk("DOCK"), 'Cannot create chunk DOCK!')
        self.assertEqual("IffChunk 'SOCK'", str(iff.IffChunk("SOCK")),
                         "IffChunk isn't converting to a string properly!")

        good_members = [192, 2.25, "abc"]
        bad_members = [iff.IffForm("EMPT"), iff.IffChunk("VOID")]
        test_chunk = iff.IffChunk("TEST", good_members)

        self.assertIs(good_members, test_chunk._members,
                      "IffChunk isn't using the members parameter correctly!")

        # Exception testing.
        # Invalid Chunk ID
        self.assertRaises(ValueError, iff.IffChunk, ("\x02Aé\xFF"))
        # Invalid member types
        self.assertRaises(TypeError, iff.IffChunk, "META",
                          [iff.IffChunk("SETA"), iff.IffForm("ZETA")])

    def test_chunk(self):
        "Check chunk length and content"
        import iff

        self.assertEqual(24, self.iffc_frst.get_length(),
                         'Chunk FRST is wrong length!')
        self.assertEqual(25, self.iffc_scnd.get_length(),
                         'Chunk SCND is wrong length!')
        self.assertEqual(4, self.iffc_gone.get_length(),
                         'Chunk GONE is wrong length!')
        self.assertEqual(
            b'GONE\x00\x00\x00\x04*\x00\x00\x00', self.iffc_gone.to_bytes(),
            'chunk GONE is outputting incorrectly')
        self.assertEqual(
            b'FRST\x00\x00\x00\x18\x00\x00DA90\x00\x00I am poncho man\x00',
            self.iffc_frst.to_bytes(), 'chunk FRST is outputting incorrectly')
        self.assertEqual(
            b'SCND\x00\x00\x00\x19\x00\x00DA90\x00\x00I am poncho man!\x00',
            self.iffc_scnd.to_bytes(), 'chunk SCND is outputting incorrectly')

        # Test clear_members method of IffChunk
        void_chnk = iff.IffChunk("VOID")
        void_chnk.add_member(42)
        void_chnk.clear_members()

        self.assertEqual(
            0, void_chnk.get_length(),
            'chunk VOID is wrong length after clearing its members!')
        self.assertEqual(b"VOID\x00\x00\x00\x00", void_chnk.to_bytes(),
                         'chunk VOID is outputting incorrectly!')

    def test_form(self):
        "Check root form length and content"
        self.assertEqual(
            94, self.ifff.get_length(), 'Form FONG is wrong length!')
        self.assertEqual(
            b'FORM\x00\x00\x00^FONGFRST\x00\x00\x00\x18\x00\x00DA90\x00\x00I '
            b'am poncho man\x00SCND\x00\x00\x00\x19\x00\x00DA90\x00\x00I am '
            b'poncho man!\x00\x00GONE\x00\x00\x00\x04*\x00\x00\x00FORM\x00'
            b'\x00\x00\x04EMPT',
            self.ifff.to_bytes(), 'Form FONG is outputting incorrectly!')


class TestIFFFile(unittest.TestCase):

    def setUp(self):
        import iff
        self.iffl = iff.IffFile("TEST")
        iffc_fib = iff.IffChunk("FIB")
        iffc_fib.add_member(1)
        iffc_fib.add_member(1)
        iffc_fib.add_member(2)
        iffc_fib.add_member(3)
        iffc_fib.add_member(5)
        iffc_fib.add_member(8)
        iffc_fib.add_member(13)
        self.iffl.get_root_form().add_member(iffc_fib)
        self.iffl.set_comment("The FIB chunk represents the first 7 numbers "
                              "of a fibonacci sequence, as little-endian "
                              "32-bit integers.")

    def test_bytes(self):
        "IffFile.to_bytes() works as it should"
        self.assertEqual(
            b'FORM\x00\x00\x00(TESTFIB \x00\x00\x00\x1C\x01\x00\x00\x00'
            b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x05\x00\x00\x00'
            b'\x08\x00\x00\x00\x0D\x00\x00\x00The FIB chunk represents the '
            b'first 7 numbers of a fibonacci sequence, as little-endian '
            b'32-bit integers.', self.iffl.to_bytes(),
            'The IFF is outputting incorrectly!')


class TestIFFReader(unittest.TestCase):

    def setUp(self):
        import iff
        iffl = iff.IffForm("TEST")

        iffc_desc = iff.IffChunk("DESC")
        iffc_desc.add_member("Fibonacci sequence")
        iffl.add_member(iffc_desc)

        ifff_fib = iff.IffForm("FIB")

        iffc_num = iff.IffChunk("NUM")
        iffc_num.add_member(7)
        ifff_fib.add_member(iffc_num)

        iffc_fib = iff.IffChunk("FIB")
        iffc_fib.add_member(1)
        iffc_fib.add_member(1)
        iffc_fib.add_member(2)
        iffc_fib.add_member(3)
        iffc_fib.add_member(5)
        iffc_fib.add_member(8)
        iffc_fib.add_member(13)
        ifff_fib.add_member(iffc_fib)
        iffl.add_member(ifff_fib)

        self.iff_data = iffl.to_bytes()

    def test_can_read(self):
        "IffReader can read from bytes or bytearray objects."
        import iff_read
        self.assertIsNotNone(
            iff_read.IffReader(self.iff_data),
            'IffReader is unable to read from bytes or bytearrays!')

    def test_skip(self):
        "IffReader skips CHUNKs and FORMs properly."
        import iff_read
        iffr = iff_read.IffReader(self.iff_data)
        self.assertEqual(0, iffr._iff_file.tell(),
                         'IffReader does not start at the beginning of the '
                         'file/bytes!')
        self.assertIsNone(iffr.skip_data(), 'skip_data() returned something!')
        # First 12 bytes are the header for the TEST (root) form.
        self.assertEqual(12, iffr._iff_file.tell(), 'IffReader does not skip'
                         'FORM headers properly!')
        self.assertIsNone(iffr.skip_data(), 'skip_data() returned something!')
        self.assertEqual(40, iffr._iff_file.tell(), 'IffReader does not skip '
                         'odd-length CHUNKs properly!')


class TestIFFMetadata(unittest.TestCase):

    def setUp(self):
        import iff_mesh
        self.sphere = iff_mesh.Sphere(100, 0, 50, 30)
        self.hardpoint = iff_mesh.Hardpoint(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1]], [0, -0.5, 3], "fgun01")

    def test_chunks(self):
        self.assertEqual(
            b"SPHR\x00\x00\x00\x10\x00\x00\xC8B\x00\x00\x00\x00"
            b"\x00\x00HB\x00\x00\xF0A",
            self.sphere.to_collsphr_chunk().to_bytes(),
            'Sphere is not being converted to a chunk correctly!')

        self.assertEqual(
            b"HARD\x00\x00\x007\x00\x00\x80?\x00\x00\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80?"
            b"\x00\x00\x00\x00\x00\x00\x00\xBF\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\x00\x00\x80?\x00\x00@@fgun01\x00",
            self.hardpoint.to_chunk().to_bytes(),
            'Hardpoint is not being converted to a chunk correctly!')


class TestIFFMesh(unittest.TestCase):

    def setUp(self):
        import iff_mesh
        self.cube_mesh = iff_mesh.ModelIff("box", True)

        cube_lod = iff_mesh.MeshLODForm(0)
        empty_lod = iff_mesh.EmptyLODForm(1)

        cube_lod.set_name("testcube")

        cube_lod.add_vertex(1.0, 1.0, 1.0)
        cube_lod.add_vertex(-1.0, 1.0, 1.0)
        cube_lod.add_vertex(1.0, 1.0, -1.0)
        cube_lod.add_vertex(-1.0, 1.0, -1.0)
        cube_lod.add_vertex(1.0, -1.0, 1.0)
        cube_lod.add_vertex(-1.0, -1.0, 1.0)
        cube_lod.add_vertex(1.0, -1.0, -1.0)
        cube_lod.add_vertex(-1.0, -1.0, -1.0)

        cube_lod.add_normal()

        cube_lod.add_fvrt(0, 0, 0.0, 0.0)
        cube_lod.add_fvrt(1, 1, 1.0, 0.0)
        cube_lod.add_fvrt(2, 2, 0.0, 1.0)
        cube_lod.add_fvrt(3, 3, 1.0, 1.0)

        self.cube_mesh.add_lod(cube_lod, 0)
        self.cube_mesh.add_lod(empty_lod, 1000)


if __name__ == '__main__':
    unittest.main()
