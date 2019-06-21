#!/usr/bin/env python3

import unittest
import util

from collections import namedtuple

from .helper_classes import Vector

class TestUtilMethods(unittest.TestCase):

    def test_patch_infos(self):
        colors = [(0.0, 0.0, 0.0, 1.0) for i in range(8)]
        l = util.create_tile_infos(250, 120, 10, 50, colors)
        self.assertEqual(100, l[7].x1)
        self.assertEqual(149, l[7].x2)
        self.assertEqual(50, l[7].y1)
        self.assertEqual(99, l[7].y2)

        with self.assertRaises(ValueError):
            util.create_tile_infos(220, 120, 10, 50, colors)


    def test_paint_patch(self):
        colors = [(0.0, 0.0, 0.0, 0.0) for i in range(10)]
        color = (0.0, 0.0, 0.0 , 1.0 )
        colors[7] = color
        width, height = 260, 120
        pixels = [0.0 for i in range(width * height * 4)]
        tile_infos = util.create_tile_infos(
                width=width,
                height=height,
                num_tiles=10,
                tile_size=50,
                colors=colors
            )
        pixels = util.paint_patch(tile_infos=tile_infos, pixels=pixels, width=width)
        x1, y1  = 100, 50
        x2, y2  = 149, 99
        offset = (x1 + y1 * width) * 4
        self.assertEqual(1.0, pixels[offset + 3])
        self.assertEqual(0.0, pixels[offset + 4])
        self.assertEqual(0.0, pixels[offset - 1])

        offset = (x2 + y1 * width) * 4
        self.assertEqual(1.0, pixels[offset + 3])
        self.assertEqual(0.0, pixels[offset + 6])

        offset = (x2 + y2 * width) * 4
        self.assertEqual(1.0, pixels[offset + 3])
        self.assertEqual(0.0, pixels[offset + 6])

        offset = (x1 + y2 * width) * 4
        self.assertEqual(1.0, pixels[offset + 3])
        offset = (x1 + (y2 + 1) * width) * 4
        self.assertEqual(0.0, pixels[offset + 3])


    def test_translate_uvs(self):
        uvs = [
            Vector((10.0, 10.0)),
            Vector((65.0, 12.0)),
            Vector((60.0, 80.0))
        ]
        colors = [(0.0, 0.0, 0.0, 1.0) for i in range(8)]
        tile_infos = util.create_tile_infos(250, 120, 10, 50, colors)

        uvs = util.translate_uvs(tile_infos[7], uvs)

        self.assertGreater(uvs[0].x, 100)

if __name__ == '__main__':
    unittest.main()
