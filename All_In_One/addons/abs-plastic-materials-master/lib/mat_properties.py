# Copyright (C) 2019 Christopher Gearhart
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

# LDR code reference: https://www.ldraw.org/article/547.html

"""

ABS_Dialectric defaults:
    Diffuse Color: (1, 1, 1, 1)
    Boost Value: 0.0
    Random: 0.02
    Rough 1: 0.005
    Rough 2: 0.15
    Metallic: 0.01
    Speckle: 0.0
    Fingerprints: 0.25
    SSS Color: (1, 1, 1, 1)
    SSS Amount: 0.0
    SSS Default: 0.0

ABS_Transparent defaults:
    Color: (1, 1, 1, 1)
    Boost Value: 0
    Random: 0.02
    Rough 1: 0.005
    Rough 2: 0.15
    Rough Mix: 0.0
    Reflection: 0.01
    Fingerprints: 0.25
    Absorption: -1.0

"""

mat_properties = {
  'ABS Plastic Black':{
      'Diffuse Color':[0.0185, 0.01764, 0.01681, 1.0],
      # Other properties (not node inputs)
      'LDR Code':0,
  },
  'ABS Plastic Blue':{
      'Diffuse Color':[0.0, 0.12214, 0.46778, 1.0],
      # Other properties (not node inputs)
      'LDR Code':1,
  },
  'ABS Plastic Bright Green':{
      'Diffuse Color':[0.00605, 0.29614, 0.04667, 1.0],
      'SSS Color':[0.0, 1.0, 0.02956, 1.0],
      'SSS Amount':0.17,
      'SSS Default':0.17,
      # Other properties (not node inputs)
      'LDR Code':10,
  },
  'ABS Plastic Bright Light Orange':{
      'Diffuse Color':[0.98225, 0.4452, 0.0, 1.0],
      'Boost Value':0.1,
      'SSS Color':[1.0, 0.30499, 0.0, 1.0],
      'SSS Amount':0.12,
      'SSS Default':0.12,
      # Other properties (not node inputs)
      'LDR Code':366,
  },
  'ABS Plastic Bright Pink':{
      'Diffuse Color':[0.86316, 0.08228, 0.23455, 1.0],
      'SSS Color':[0.98225, 0.0, 0.0999, 1.0],
      'SSS Amount':0.04,
      'SSS Default':0.04,
      # Other properties (not node inputs)
      'LDR Code':5,
  },
  'ABS Plastic Brown':{
      'Diffuse Color':[0.16513, 0.04817, 0.02416, 1.0],
      # Other properties (not node inputs)
      'LDR Code':6,
  },
  'ABS Plastic Cool Yellow':{
      'Diffuse Color':[1.0, 0.83077, 0.20508, 1.0],
      # TODO: UPDATE SUBSURFACE SCATTERING COLOR
      # Other properties (not node inputs)
      'LDR Code':266,
  },
  'ABS Plastic Dark Azur':{
      'Diffuse Color':[0.16203, 0.40724, 0.65837, 1.0],
      'SSS Color':[0.0003, 0.33245, 1.0, 1.0],
      'SSS Amount':0.12,
      'SSS Default':0.12,
      # Other properties (not node inputs)
      'LDR Code':321,
  },
  'ABS Plastic Dark Blue':{
      'Diffuse Color':[0.01161, 0.0382, 0.08866, 1.0],
      # Other properties (not node inputs)
      'LDR Code':272,
  },
  'ABS Plastic Dark Brown':{
      'Diffuse Color':[0.06848, 0.0331, 0.02519, 1.0],
      # Other properties (not node inputs)
      'LDR Code':308,
  },
  'ABS Plastic Dark Green':{
      'Diffuse Color':[0.0075, 0.0648, 0.0356, 1.0],
      'SSS Color':[0.0075, 0.0648, 0.0356, 1.0],
      'SSS Amount':0.03,
      'SSS Default':0.03,
      # Other properties (not node inputs)
      'LDR Code':288,
  },
  'ABS Plastic Dark Grey':{
      'Diffuse Color':[0.07819, 0.0999, 0.09306, 1.0],
      # Other properties (not node inputs)
      'LDR Code':8,
  },
  'ABS Plastic Dark Purple':{
      'Diffuse Color':[0.09306, 0.05127, 0.25818, 1.0],
      # TODO: UPDATE SUBSURFACE SCATTERING COLOR
      # Other properties (not node inputs)
      'LDR Code':85,
  },
  'ABS Plastic Dark Red':{
      'Diffuse Color':[0.21953, 0.02029, 0.02217, 1.0],
      'SSS Color':[1.0, 0.0, 0.0, 1.0],
      'SSS Amount':0.1,
      'SSS Default':0.1,
      # Other properties (not node inputs)
      'LDR Code':320,
  },
  'ABS Plastic Dark Tan':{
      'Diffuse Color':[0.32778, 0.23074, 0.12744, 1.0],
      'SSS Color':[0.40724, 0.10702, 0.01681, 1.0],
      'SSS Amount':0.14,
      'SSS Default':0.14,
      # Other properties (not node inputs)
      'LDR Code':28,
  },
  'ABS Plastic Gold':{
      'Diffuse Color':[0.38333, 0.2021, 0.05824, 1.0],
      'Rough 1':0.25,
      'Rough 2':0.33,
      'Metallic':0.85,
      'Speckle':0.35,
      'Fingerprints':0.03125,
      'SSS Color':[1.0, 0.16827, 0.0, 1.0],
      'SSS Amount':0.05,
      'SSS Default':0.05,
      # Other properties (not node inputs)
      'LDR Code':334,
  },
  'ABS Plastic Green':{
      'Diffuse Color':[0.0, 0.21586, 0.04971, 1.0],
      'SSS Color':[0.0, 0.4452, 0.04667, 1.0],
      'SSS Amount':0.04,
      'SSS Default':0.04,
      # Other properties (not node inputs)
      'LDR Code':2,
  },
  'ABS Plastic Lavender':{
      'Diffuse Color':[0.48515, 0.39676, 0.67954, 1.0],
      # TODO: UPDATE SUBSURFACE SCATTERING COLOR
      # Other properties (not node inputs)
      'LDR Code':31,
  },
  'ABS Plastic Light Blue':{
      'Diffuse Color':[0.05951, 0.32314, 0.60383, 1.0],
      # TODO: UPDATE SUBSURFACE SCATTERING COLOR
      # Other properties (not node inputs)
      'LDR Code':9,
  },
  'ABS Plastic Light Flesh':{
      'Diffuse Color':[0.93011, 0.55834, 0.39676, 1.0],
      # TODO: UPDATE SUBSURFACE SCATTERING COLOR
      # Other properties (not node inputs)
      'LDR Code':78,
  },
  'ABS Plastic Light Grey':{
      'Diffuse Color':[0.3467, 0.37626, 0.38643, 1.0],
      'SSS Color':[0.3467, 0.37626, 0.38643, 1.0],
      'SSS Amount':0.01,
      'SSS Default':0.01,
      # Other properties (not node inputs)
      'LDR Code':503,
  },
  'ABS Plastic Light Pink':{
      'Diffuse Color':[0.92158, 0.40724, 0.7011, 1.0],
      'SSS Color':[0.98225, 0.01797, 0.15952, 1.0],
      'SSS Amount':0.04,
      'SSS Default':0.04,
      # Other properties (not node inputs)
      'LDR Code':13,
  },
  'ABS Plastic Lime':{
      'Diffuse Color':[0.36625, 0.49102, 0.00304, 1.0],
      'SSS Color':[0.43966, 0.95597, 0.0, 1.0],
      'SSS Amount':0.1,
      'SSS Default':0.1,
      # Other properties (not node inputs)
      'LDR Code':27,
  },
  'ABS Plastic Magenta':{
      'Diffuse Color':[0.39157, 0.0185, 0.14996, 1.0],
      # TODO: UPDATE SUBSURFACE SCATTERING COLOR
      # Other properties (not node inputs)
      'LDR Code':26,
  },
  'ABS Plastic Medium Dark Flesh':{
      'Diffuse Color':[0.42327, 0.17465, 0.0648, 1.0],
      # TODO: UPDATE SUBSURFACE SCATTERING COLOR
      # Other properties (not node inputs)
      'LDR Code':84,
  },
  'ABS Plastic Medium Lavender':{
      'Diffuse Color':[0.36131, 0.17789, 0.47932, 1.0],
      # TODO: UPDATE SUBSURFACE SCATTERING COLOR
      # Other properties (not node inputs)
      'LDR Code':30,
  },
  'ABS Plastic Orange':{
      'Diffuse Color':[1.0, 0.20864, 0.00605, 1.0],
      'SSS Color':[1.0, 0.02956, 0.0, 1.0],
      'SSS Amount':0.14,
      'SSS Default':0.14,
      # Other properties (not node inputs)
      'LDR Code':25,
  },
  'ABS Plastic Purple':{
      'Diffuse Color':[0.2462, 0.02217, 0.14703, 1.0],
      'SSS Color':[0.87962, 0.0, 0.06848, 1.0],
      'SSS Amount':0.04,
      'SSS Default':0.04,
      # Other properties (not node inputs)
      'LDR Code':5,
  },
  'ABS Plastic Red':{
      'Diffuse Color':[0.50289, 0.01161, 0.01521, 1.0],
      'SSS Color':[1.0, 0.0, 0.0, 1.0],
      'SSS Amount':0.14,
      'SSS Default':0.14,
      # Other properties (not node inputs)
      'LDR Code':4,
  },
  'ABS Plastic Sand Blue':{
      'Diffuse Color':[0.15593, 0.23455, 0.30054, 1.0],
      'SSS Color':[0.15593, 0.23455, 0.30054, 1.0],
      'SSS Amount':0.01,
      'SSS Default':0.01,
      # Other properties (not node inputs)
      'LDR Code':379,
  },
  'ABS Plastic Sand Green':{
      'Diffuse Color':[0.16513, 0.29614, 0.20156, 1.0],
      'SSS Color':[0.16513, 0.29614, 0.20156, 1.0],
      'SSS Amount':0.05,
      'SSS Default':0.05,
      # Other properties (not node inputs)
      'LDR Code':378,
  },
  'ABS Plastic Silver':{
      'Diffuse Color':[0.30963, 0.30963, 0.30963, 1.0],
      'Rough 1':0.25,
      'Rough 2':0.33,
      'Metallic':0.9,
      'Speckle':0.35,
      'Fingerprints':0.03125,
      # Other properties (not node inputs)
      'LDR Code':383,
  },
  'ABS Plastic Tan':{
      'Diffuse Color':[0.71569, 0.53948, 0.30054, 1.0],
      'SSS Color':[1.0, 0.67244, 0.06125, 1.0],
      'SSS Amount':0.14,
      'SSS Default':0.14,
      # Other properties (not node inputs)
      'LDR Code':19,
  },
  'ABS Plastic Teal':{
      'Diffuse Color':[0.0, 0.29177, 0.28315, 1.0],
      # TODO: UPDATE SUBSURFACE SCATTERING COLOR
      # Other properties (not node inputs)
      'LDR Code':3,
  },
  'ABS Plastic Trans-Blue':{
      'Color':[0.0, 0.42327, 0.7454, 0.75],
      # Other properties (not node inputs)
      'LDR Code':41,
  },
  'ABS Plastic Trans-Bright Orange':{
      'Color':[1.0, 0.31399, 0.0, 0.75],
      'Boost Value':0.33,
      # Other properties (not node inputs)
      'LDR Code':38,
  },
  'ABS Plastic Trans-Brown':{
      'Color':[0.116, 0.085, 0.0484, 0.75],
      'Boost Value':0.33,
      # Other properties (not node inputs)
      'LDR Code':40,
  },
  'ABS Plastic Trans-Clear':{
      'Color':[1.0, 0.98225, 0.94731, 0.65],
      # Other properties (not node inputs)
      'LDR Code':47,
  },
  'ABS Plastic Trans-Green':{
      'Color':[0.0, 0.53328, 0.08438, 0.75],
      # Other properties (not node inputs)
      'LDR Code':34,
  },
  'ABS Plastic Trans-Light Blue':{
      'Color':[0.38643, 0.85499, 1.0, 0.75],
      # Other properties (not node inputs)
      'LDR Code':43,
  },
  'ABS Plastic Trans-Light Green':{
      'Color':[0.88792, 1.0, 0.01229, 0.75],
      # Other properties (not node inputs)
      'LDR Code':42,
  },
  'ABS Plastic Trans-Orange':{
      'Color':[1.0, 0.47353, 0.12214, 0.75],
      # Other properties (not node inputs)
      'LDR Code':57,
  },
  'ABS Plastic Trans-Red':{
      'Color':[0.95597, 0.0, 0.0, 0.75],
      # Other properties (not node inputs)
      'LDR Code':36,
  },
  'ABS Plastic Trans-Yellow':{
      'Color':[1.0, 0.89627, 0.01681, 0.75],
      # Other properties (not node inputs)
      'LDR Code':46,
  },
  'ABS Plastic Trans-Yellowish Clear':{
      'Color':[0.87962, 0.8388, 0.73046, 0.7],
      'Rough 1':0.015,
      # Other properties (not node inputs)
      'LDR Code':47,
  },
  'ABS Plastic White':{
      'Diffuse Color':[0.94731, 0.89627, 0.81485, 1.0],
      'SSS Color':[1.0, 0.67244, 0.06125, 1.0],
      'SSS Amount':0.14,
      'SSS Default':0.14,
      # Other properties (not node inputs)
      'LDR Code':15,
  },
  'ABS Plastic Yellow':{
      'Diffuse Color':[0.97345, 0.58408, 0.0, 1.0],
      'SSS Color':[1.0, 0.30499, 0.0, 1.0],
      'SSS Amount':0.14,
      'SSS Default':0.14,
      # Other properties (not node inputs)
      'LDR Code':14,
  },
}
