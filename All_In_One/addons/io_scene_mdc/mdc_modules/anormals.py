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

# Module: anormals.py
# Description: builds 256 normals according to the compression method.

# TODO
# - could not figure out a way to pack this into MDCXyznCompressed and from
# there call it once upon class creation, so it is here separately for now.

import math

LAT_SCALE = 180 / 16
SIGMA_WIDTH_DELTA = 4
SIGMA_WIDTH_MAX = 32

class ANormal:

    def buildNormals():

        # build table containing rho-ranges and their medians
        table = []

        # lat=[90, 180]
        curSigmaWidth = SIGMA_WIDTH_MAX
        for i in range(7, 14):

            lowerBound = LAT_SCALE * i + (1/2) * LAT_SCALE
            upperBound = LAT_SCALE * (i + 1) + (1/2) * LAT_SCALE
            median = LAT_SCALE * (i + 1)
            sigmaWidth = curSigmaWidth

            table.append((lowerBound, upperBound, median, sigmaWidth))

            curSigmaWidth = curSigmaWidth - SIGMA_WIDTH_DELTA

        i = 14
        lowerBound = LAT_SCALE * i + (1/2) * LAT_SCALE
        upperBound = 180
        median = LAT_SCALE * (i + 1)
        sigmaWidth = curSigmaWidth

        table.append((lowerBound, upperBound, median, sigmaWidth))

        curSigmaWidth = curSigmaWidth - SIGMA_WIDTH_DELTA

        # lat=(90, 0]
        curSigmaWidth = SIGMA_WIDTH_MAX - SIGMA_WIDTH_DELTA
        for i in range(6, 0, -1):

            lowerBound = LAT_SCALE * i + (1/2) * LAT_SCALE
            upperBound = LAT_SCALE * (i + 1) + (1/2) * LAT_SCALE
            median = LAT_SCALE * (i + 1)
            sigmaWidth = curSigmaWidth

            table.append((lowerBound, upperBound, median, sigmaWidth))

            curSigmaWidth = curSigmaWidth - SIGMA_WIDTH_DELTA

        i = 0
        lowerBound = 0
        upperBound = LAT_SCALE * (i + 1) + (1/2) * LAT_SCALE
        median = LAT_SCALE * (i + 1)
        sigmaWidth = curSigmaWidth

        table.append((lowerBound, upperBound, median, sigmaWidth))

        curSigmaWidth = curSigmaWidth - SIGMA_WIDTH_DELTA

        # from table build normals
        latLon = []

        for i in range(0, len(table)):

            median = table[i][2]
            sigmaWidth = table[i][3]

            lat = median
            for j in range(0, sigmaWidth):
                lon = (360/sigmaWidth) * j
                latLon.append((lat, lon))

        normals = []

        for i in range(0, len(latLon)):

            lat = math.radians(latLon[i][0])
            lon = math.radians(latLon[i][1])

            x = math.cos(lon) *  math.sin(lat)
            y = math.sin(lon) *  math.sin(lat)
            z = math.cos(lat)

            normals.append((x, y, z))

        return normals
