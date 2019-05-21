'''
Copyright (C) 2018 SmugTomato

Created by SmugTomato

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


# Used to get human readable element identities
element_ids = {
    0x1C4AFC56: 'Blend Indices',
    0x5C4AFC5C: 'Blend Weights',
    0x7C4DEE82: 'Target Indices',
    0xCB6F3A6A: 'Normal Morph Deltas',
    0xCB7206A1: 'Colour',
    0xEB720693: 'Colour Deltas',
    0x3B83078B: 'Normals List',
    0x5B830781: 'Vertices',
    0xBB8307AB: 'UV Coordinates',
    0xDB830795: 'UV Coordinate Deltas',
    0x9BB38AFB: 'Binormals',
    0x3BD70105: 'Bone Weights',
    0xFBD70111: 'Bone Assignments',
    0x89D92BA0: 'Bump Map Normals',
    0x69D92B93: 'Bump Map Normal Deltas',
    0x5CF2CFE1: 'Morph Vertex Deltas',
    0xDCF2CFDC: 'Morph Vertex Map',
    0x114113C3: '(EP4) VertexID',
    0x114113CD: '(EP4) RegionMask'
}

# Used to check the identity of an element in code
class ElementID:
    BLEND_INDICES           = 0x1C4AFC56
    BLEND_WEIGHTS           = 0x5C4AFC5C
    TARGET_INDICES          = 0x7C4DEE82
    NORMAL_MORPH_DELTAS     = 0xCB6F3A6A
    COLOUR                  = 0xCB7206A1
    COLOUR_DELTAS           = 0xEB720693
    NORMALS_LIST            = 0x3B83078B
    VERTICES                = 0x5B830781
    UV_COORDINATES          = 0xBB8307AB
    UV_COORDINATE_DELTAS    = 0xDB830795
    BINORMALS               = 0x9BB38AFB
    BONE_WEIGHTS            = 0x3BD70105
    BONE_ASSIGNMENTS        = 0xFBD70111
    BUMP_MAP_NORMALS        = 0x89D92BA0
    BUMP_MAP_NORMAL_DELTAS  = 0x69D92B93
    MORPH_VERTEX_DELTAS     = 0x5CF2CFE1
    MORPH_VERTEX_MAP        = 0xDCF2CFDC
    EP4_VERTEX_ID           = 0x114113C3
    EP4_REGION_MASK         = 0x114113CD
