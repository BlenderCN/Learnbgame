'''

  V-Ray/Blender

  http://vray.cgdo.ru

  Author: Andrey M. Izrantsev (aka bdancer)
  E-Mail: izrantsev@cgdo.ru

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.

'''


''' Python modules  '''
import filecmp
import math
import os
import platform
import random
import shutil
import string
import struct
import socket
import stat
import subprocess
import sys
import time
import tempfile
import getpass


''' Blender modules '''
import bpy
import mathutils

''' vb modules '''
import _vray_for_blender

from vb25.plugins import *

PLATFORM= sys.platform
HOSTNAME= socket.gethostname()

PURE_PROCEDURAL= (
	'TexDirt',
	'TexEdges',
	'TexFalloff',
)

COLOR_TABLE= {
	'22500': (0.3764,0.5432,1.0000),
	'34800': (0.3361,0.5095,1.0000),
	'8300': (0.7319,0.7938,1.0000),
	'10100': (0.5978,0.7069,1.0000),
	'7300': (0.8591,0.8704,1.0000),
	'15200': (0.4460,0.5982,1.0000),
	'21400': (0.3830,0.5486,1.0000),
	'28100': (0.3527,0.5235,1.0000),
	'8800': (0.6856,0.7645,1.0000),
	'39100': (0.3290,0.5033,1.0000),
	'8900': (0.6773,0.7593,1.0000),
	'19400': (0.3975,0.5603,1.0000),
	'32300': (0.3413,0.5139,1.0000),
	'12700': (0.4982,0.6371,1.0000),
	'10200': (0.5925,0.7033,1.0000),
	'24300': (0.3673,0.5357,1.0000),
	'22000': (0.3793,0.5456,1.0000),
	'1700': (1.0000,0.1912,0.0000),
	'13600': (0.4762,0.6209,1.0000),
	'5300': (1.0000,0.8167,0.6937),
	'27400': (0.3550,0.5255,1.0000),
	'19300': (0.3984,0.5610,1.0000),
	'10800': (0.5637,0.6836,1.0000),
	'30100': (0.3468,0.5186,1.0000),
	'21100': (0.3850,0.5502,1.0000),
	'8600': (0.7030,0.7757,1.0000),
	'39400': (0.3286,0.5030,1.0000),
	'36200': (0.3336,0.5073,1.0000),
	'16700': (0.4249,0.5819,1.0000),
	'15100': (0.4477,0.5994,1.0000),
	'28400': (0.3517,0.5227,1.0000),
	'30600': (0.3455,0.5174,1.0000),
	'24900': (0.3646,0.5335,1.0000),
	'27300': (0.3553,0.5257,1.0000),
	'1400': (1.0000,0.1303,0.0000),
	'5000': (1.0000,0.7792,0.6180),
	'13900': (0.4698,0.6161,1.0000),
	'34500': (0.3367,0.5100,1.0000),
	'10700': (0.5681,0.6866,1.0000),
	'31000': (0.3444,0.5166,1.0000),
	'27900': (0.3533,0.5241,1.0000),
	'15400': (0.4429,0.5958,1.0000),
	'18100': (0.4093,0.5697,1.0000),
	'16400': (0.4287,0.5848,1.0000),
	'7900': (0.7762,0.8211,1.0000),
	'21200': (0.3843,0.5496,1.0000),
	'35900': (0.3341,0.5077,1.0000),
	'11000': (0.5551,0.6776,1.0000),
	'7700': (0.8014,0.8363,1.0000),
	'6500': (1.0000,0.9445,0.9853),
	'36100': (0.3338,0.5074,1.0000),
	'31300': (0.3437,0.5159,1.0000),
	'3800': (1.0000,0.6028,0.3207),
	'4100': (1.0000,0.6511,0.3927),
	'1900': (1.0000,0.2272,0.0000),
	'38500': (0.3299,0.5041,1.0000),
	'13200': (0.4854,0.6277,1.0000),
	'5700': (1.0000,0.8630,0.7933),
	'27000': (0.3564,0.5266,1.0000),
	'37000': (0.3322,0.5061,1.0000),
	'22300': (0.3776,0.5441,1.0000),
	'6200': (1.0000,0.9156,0.9147),
	'25900': (0.3605,0.5300,1.0000),
	'32400': (0.3411,0.5137,1.0000),
	'16100': (0.4327,0.5879,1.0000),
	'33600': (0.3385,0.5115,1.0000),
	'6800': (0.9488,0.9219,1.0000),
	'25300': (0.3629,0.5321,1.0000),
	'20000': (0.3928,0.5565,1.0000),
	'7000': (0.9102,0.9000,1.0000),
	'37700': (0.3311,0.5052,1.0000),
	'3200': (1.0000,0.4970,0.1879),
	'23800': (0.3696,0.5376,1.0000),
	'32900': (0.3400,0.5128,1.0000),
	'25400': (0.3625,0.5317,1.0000),
	'18700': (0.4036,0.5652,1.0000),
	'33500': (0.3387,0.5117,1.0000),
	'35400': (0.3350,0.5085,1.0000),
	'13500': (0.4785,0.6226,1.0000),
	'26800': (0.3571,0.5272,1.0000),
	'29400': (0.3487,0.5202,1.0000),
	'11400': (0.5394,0.6666,1.0000),
	'6100': (1.0000,0.9055,0.8907),
	'34200': (0.3373,0.5105,1.0000),
	'17500': (0.4156,0.5746,1.0000),
	'20700': (0.3877,0.5524,1.0000),
	'23500': (0.3711,0.5389,1.0000),
	'19800': (0.3943,0.5577,1.0000),
	'4500': (1.0000,0.7111,0.4919),
	'3700': (1.0000,0.5860,0.2974),
	'30800': (0.3450,0.5170,1.0000),
	'38100': (0.3305,0.5046,1.0000),
	'14400': (0.4599,0.6087,1.0000),
	'21800': (0.3805,0.5466,1.0000),
	'29100': (0.3496,0.5209,1.0000),
	'31600': (0.3430,0.5153,1.0000),
	'26100': (0.3597,0.5294,1.0000),
	'23200': (0.3726,0.5401,1.0000),
	'1300': (1.0000,0.1085,0.0000),
	'9200': (0.6543,0.7444,1.0000),
	'35700': (0.3345,0.5080,1.0000),
	'11300': (0.5432,0.6693,1.0000),
	'17000': (0.4212,0.5791,1.0000),
	'12400': (0.5066,0.6432,1.0000),
	'2400': (1.0000,0.3364,0.0501),
	'36800': (0.3326,0.5064,1.0000),
	'14100': (0.4657,0.6131,1.0000),
	'35200': (0.3354,0.5088,1.0000),
	'20900': (0.3863,0.5513,1.0000),
	'26400': (0.3586,0.5284,1.0000),
	'29200': (0.3493,0.5207,1.0000),
	'9700': (0.6208,0.7224,1.0000),
	'18800': (0.4027,0.5644,1.0000),
	'9900': (0.6089,0.7144,1.0000),
	'39700': (0.3281,0.5026,1.0000),
	'11900': (0.5220,0.6542,1.0000),
	'12300': (0.5095,0.6453,1.0000),
	'33000': (0.3398,0.5126,1.0000),
	'24700': (0.3655,0.5342,1.0000),
	'36500': (0.3331,0.5068,1.0000),
	'2900': (1.0000,0.4394,0.1297),
	'19200': (0.3992,0.5616,1.0000),
	'37900': (0.3308,0.5049,1.0000),
	'12900': (0.4929,0.6332,1.0000),
	'39800': (0.3280,0.5025,1.0000),
	'17900': (0.4113,0.5713,1.0000),
	'14200': (0.4638,0.6116,1.0000),
	'22400': (0.3770,0.5437,1.0000),
	'3300': (1.0000,0.5155,0.2087),
	'21500': (0.3824,0.5481,1.0000),
	'2300': (1.0000,0.3149,0.0373),
	'34900': (0.3359,0.5093,1.0000),
	'31900': (0.3423,0.5147,1.0000),
	'19700': (0.3951,0.5584,1.0000),
	'39000': (0.3291,0.5035,1.0000),
	'36600': (0.3329,0.5067,1.0000),
	'30700': (0.3452,0.5172,1.0000),
	'24800': (0.3650,0.5338,1.0000),
	'8200': (0.7423,0.8002,1.0000),
	'24200': (0.3677,0.5361,1.0000),
	'22700': (0.3753,0.5423,1.0000),
	'32000': (0.3420,0.5145,1.0000),
	'27500': (0.3546,0.5252,1.0000),
	'5400': (1.0000,0.8286,0.7187),
	'12000': (0.5187,0.6519,1.0000),
	'28000': (0.3530,0.5238,1.0000),
	'17300': (0.4178,0.5763,1.0000),
	'30200': (0.3465,0.5183,1.0000),
	'10900': (0.5593,0.6806,1.0000),
	'1000': (1.0000,0.0401,0.0000),
	'8500': (0.7123,0.7815,1.0000),
	'10300': (0.5873,0.6998,1.0000),
	'15000': (0.4493,0.6007,1.0000),
	'21600': (0.3817,0.5476,1.0000),
	'28700': (0.3508,0.5219,1.0000),
	'16800': (0.4236,0.5809,1.0000),
	'36300': (0.3334,0.5071,1.0000),
	'39300': (0.3287,0.5031,1.0000),
	'1500': (1.0000,0.1515,0.0000),
	'9400': (0.6402,0.7352,1.0000),
	'10400': (0.5823,0.6964,1.0000),
	'22200': (0.3781,0.5446,1.0000),
	'22800': (0.3748,0.5419,1.0000),
	'21300': (0.3836,0.5491,1.0000),
	'5100': (1.0000,0.7919,0.6433),
	'34600': (0.3365,0.5098,1.0000),
	'13800': (0.4719,0.6177,1.0000),
	'19100': (0.4001,0.5623,1.0000),
	'35800': (0.3343,0.5079,1.0000),
	'7400': (0.8437,0.8614,1.0000),
	'3900': (1.0000,0.6193,0.3444),
	'15700': (0.4384,0.5923,1.0000),
	'32600': (0.3407,0.5133,1.0000),
	'16500': (0.4274,0.5838,1.0000),
	'23300': (0.3721,0.5397,1.0000),
	'30400': (0.3460,0.5179,1.0000),
	'37300': (0.3317,0.5057,1.0000),
	'27100': (0.3560,0.5263,1.0000),
	'4000': (1.0000,0.6354,0.3684),
	'14800': (0.4527,0.6033,1.0000),
	'32500': (0.3409,0.5135,1.0000),
	'5800': (1.0000,0.8740,0.8179),
	'13100': (0.4879,0.6295,1.0000),
	'16200': (0.4313,0.5869,1.0000),
	'25000': (0.3642,0.5331,1.0000),
	'18300': (0.4074,0.5681,1.0000),
	'7100': (0.8923,0.8897,1.0000),
	'33900': (0.3379,0.5110,1.0000),
	'23900': (0.3692,0.5372,1.0000),
	'20300': (0.3905,0.5547,1.0000),
	'29800': (0.3476,0.5192,1.0000),
	'37600': (0.3313,0.5053,1.0000),
	'4300': (1.0000,0.6817,0.4419),
	'15900': (0.4355,0.5901,1.0000),
	'21900': (0.3799,0.5461,1.0000),
	'34000': (0.3377,0.5108,1.0000),
	'13400': (0.4807,0.6243,1.0000),
	'27600': (0.3543,0.5249,1.0000),
	'25500': (0.3621,0.5314,1.0000),
	'5500': (1.0000,0.8403,0.7437),
	'6000': (1.0000,0.8952,0.8666),
	'4900': (1.0000,0.7661,0.5928),
	'26700': (0.3575,0.5275,1.0000),
	'34300': (0.3371,0.5103,1.0000),
	'11700': (0.5287,0.6590,1.0000),
	'29500': (0.3485,0.5200,1.0000),
	'31200': (0.3439,0.5161,1.0000),
	'20600': (0.3884,0.5529,1.0000),
	'23600': (0.3706,0.5384,1.0000),
	'2700': (1.0000,0.3992,0.0950),
	'28900': (0.3502,0.5214,1.0000),
	'3400': (1.0000,0.5336,0.2301),
	'37500': (0.3314,0.5054,1.0000),
	'38800': (0.3294,0.5037,1.0000),
	'30900': (0.3447,0.5168,1.0000),
	'17400': (0.4167,0.5755,1.0000),
	'14500': (0.4581,0.6073,1.0000),
	'4400': (1.0000,0.6966,0.4668),
	'31500': (0.3432,0.5155,1.0000),
	'26000': (0.3601,0.5297,1.0000),
	'29600': (0.3482,0.5197,1.0000),
	'38200': (0.3303,0.5045,1.0000),
	'35600': (0.3346,0.5082,1.0000),
	'11800': (0.5253,0.6566,1.0000),
	'11200': (0.5470,0.6720,1.0000),
	'17700': (0.4134,0.5729,1.0000),
	'6700': (0.9696,0.9336,1.0000),
	'20500': (0.3891,0.5535,1.0000),
	'9300': (0.6471,0.7397,1.0000),
	'12500': (0.5037,0.6411,1.0000),
	'24100': (0.3682,0.5365,1.0000),
	'36900': (0.3324,0.5063,1.0000),
	'18400': (0.4064,0.5674,1.0000),
	'33400': (0.3389,0.5119,1.0000),
	'19600': (0.3959,0.5590,1.0000),
	'38700': (0.3296,0.5038,1.0000),
	'9000': (0.6693,0.7541,1.0000),
	'14600': (0.4563,0.6060,1.0000),
	'39600': (0.3283,0.5027,1.0000),
	'29300': (0.3490,0.5204,1.0000),
	'26300': (0.3589,0.5288,1.0000),
	'33300': (0.3391,0.5120,1.0000),
	'25600': (0.3617,0.5310,1.0000),
	'24600': (0.3659,0.5346,1.0000),
	'18900': (0.4018,0.5637,1.0000),
	'19500': (0.3967,0.5596,1.0000),
	'37800': (0.3309,0.5050,1.0000),
	'17200': (0.4189,0.5772,1.0000),
	'30300': (0.3463,0.5181,1.0000),
	'22900': (0.3742,0.5414,1.0000),
	'14300': (0.4618,0.6102,1.0000),
	'3000': (1.0000,0.4589,0.1483),
	'2800': (1.0000,0.4195,0.1119),
	'2200': (1.0000,0.2930,0.0257),
	'31800': (0.3425,0.5149,1.0000),
	'39900': (0.3279,0.5024,1.0000),
	'8100': (0.7531,0.8069,1.0000),
	'30000': (0.3471,0.5188,1.0000),
	'9500': (0.6335,0.7308,1.0000),
	'32100': (0.3418,0.5143,1.0000),
	'28300': (0.3520,0.5230,1.0000),
	'12100': (0.5156,0.6497,1.0000),
	'24500': (0.3664,0.5349,1.0000),
	'36700': (0.3327,0.5066,1.0000),
	'23000': (0.3737,0.5410,1.0000),
	'1100': (1.0000,0.0631,0.0000),
	'35100': (0.3356,0.5090,1.0000),
	'2100': (1.0000,0.2709,0.0153),
	'20800': (0.3870,0.5518,1.0000),
	'10000': (0.6033,0.7106,1.0000),
	'22600': (0.3759,0.5428,1.0000),
	'21700': (0.3811,0.5471,1.0000),
	'8400': (0.7219,0.7875,1.0000),
	'36000': (0.3339,0.5076,1.0000),
	'16900': (0.4224,0.5800,1.0000),
	'39200': (0.3288,0.5032,1.0000),
	'7200': (0.8753,0.8799,1.0000),
	'15300': (0.4445,0.5970,1.0000),
	'28600': (0.3511,0.5222,1.0000),
	'22100': (0.3787,0.5451,1.0000),
	'14900': (0.4510,0.6020,1.0000),
	'32200': (0.3416,0.5141,1.0000),
	'5200': (1.0000,0.8044,0.6685),
	'34700': (0.3363,0.5096,1.0000),
	'12600': (0.5009,0.6391,1.0000),
	'10500': (0.5774,0.6930,1.0000),
	'1600': (1.0000,0.1718,0.0000),
	'13700': (0.4740,0.6193,1.0000),
	'7500': (0.8289,0.8527,1.0000),
	'19000': (0.4009,0.5630,1.0000),
	'15600': (0.4398,0.5935,1.0000),
	'32700': (0.3404,0.5132,1.0000),
	'16600': (0.4261,0.5829,1.0000),
	'21000': (0.3856,0.5507,1.0000),
	'38600': (0.3297,0.5040,1.0000),
	'28500': (0.3514,0.5225,1.0000),
	'27800': (0.3536,0.5243,1.0000),
	'39500': (0.3284,0.5028,1.0000),
	'4700': (1.0000,0.7392,0.5422),
	'40000': (0.3277,0.5022,1.0000),
	'5900': (1.0000,0.8847,0.8424),
	'13000': (0.4904,0.6314,1.0000),
	'30500': (0.3457,0.5177,1.0000),
	'27200': (0.3557,0.5260,1.0000),
	'37200': (0.3319,0.5058,1.0000),
	'7800': (0.7885,0.8285,1.0000),
	'34400': (0.3369,0.5101,1.0000),
	'33800': (0.3381,0.5112,1.0000),
	'16300': (0.4300,0.5859,1.0000),
	'15500': (0.4413,0.5946,1.0000),
	'18000': (0.4103,0.5705,1.0000),
	'25100': (0.3637,0.5328,1.0000),
	'20200': (0.3913,0.5553,1.0000),
	'17800': (0.4124,0.5721,1.0000),
	'11100': (0.5510,0.6748,1.0000),
	'7600': (0.8149,0.8443,1.0000),
	'29900': (0.3473,0.5190,1.0000),
	'8700': (0.6941,0.7700,1.0000),
	'37100': (0.3321,0.5060,1.0000),
	'34100': (0.3375,0.5106,1.0000),
	'31400': (0.3435,0.5157,1.0000),
	'27700': (0.3540,0.5246,1.0000),
	'5600': (1.0000,0.8518,0.7686),
	'25200': (0.3633,0.5324,1.0000),
	'6900': (0.9290,0.9107,1.0000),
	'4200': (1.0000,0.6666,0.4172),
	'4800': (1.0000,0.7528,0.5675),
	'26600': (0.3578,0.5278,1.0000),
	'38400': (0.3300,0.5042,1.0000),
	'13300': (0.4831,0.6260,1.0000),
	'10600': (0.5727,0.6898,1.0000),
	'31100': (0.3442,0.5164,1.0000),
	'11600': (0.5322,0.6615,1.0000),
	'25800': (0.3609,0.5304,1.0000),
	'6300': (1.0000,0.9254,0.9384),
	'2600': (1.0000,0.3786,0.0790),
	'28800': (0.3505,0.5217,1.0000),
	'23700': (0.3701,0.5380,1.0000),
	'20100': (0.3920,0.5559,1.0000),
	'32800': (0.3402,0.5130,1.0000),
	'3500': (1.0000,0.5515,0.2520),
	'37400': (0.3316,0.5056,1.0000),
	'38300': (0.3302,0.5044,1.0000),
	'26900': (0.3567,0.5269,1.0000),
	'33200': (0.3393,0.5122,1.0000),
	'18600': (0.4045,0.5659,1.0000),
	'25700': (0.3613,0.5307,1.0000),
	'38900': (0.3293,0.5036,1.0000),
	'6600': (0.9917,0.9458,1.0000),
	'20400': (0.3898,0.5541,1.0000),
	'23400': (0.3716,0.5393,1.0000),
	'35500': (0.3348,0.5084,1.0000),
	'24000': (0.3687,0.5368,1.0000),
	'11500': (0.5357,0.6640,1.0000),
	'29700': (0.3479,0.5195,1.0000),
	'18500': (0.4055,0.5666,1.0000),
	'16000': (0.4341,0.5890,1.0000),
	'33700': (0.3383,0.5113,1.0000),
	'15800': (0.4369,0.5912,1.0000),
	'3600': (1.0000,0.5689,0.2745),
	'17600': (0.4145,0.5738,1.0000),
	'14700': (0.4545,0.6046,1.0000),
	'19900': (0.3935,0.5571,1.0000),
	'4600': (1.0000,0.7253,0.5170),
	'29000': (0.3499,0.5212,1.0000),
	'31700': (0.3427,0.5151,1.0000),
	'26200': (0.3593,0.5291,1.0000),
	'1800': (1.0000,0.2097,0.0000),
	'38000': (0.3306,0.5048,1.0000),
	'17100': (0.4201,0.5781,1.0000),
	'23100': (0.3732,0.5405,1.0000),
	'1200': (1.0000,0.0860,0.0000),
	'9100': (0.6617,0.7492,1.0000),
	'3100': (1.0000,0.4781,0.1677),
	'2500': (1.0000,0.3577,0.0640),
	'9600': (0.6271,0.7265,1.0000),
	'14000': (0.4677,0.6146,1.0000),
	'35300': (0.3352,0.5087,1.0000),
	'18200': (0.4083,0.5689,1.0000),
	'12800': (0.4955,0.6351,1.0000),
	'26500': (0.3582,0.5281,1.0000),
	'8000': (0.7644,0.8139,1.0000),
	'6400': (1.0000,0.9351,0.9619),
	'33100': (0.3396,0.5124,1.0000),
	'36400': (0.3332,0.5070,1.0000),
	'24400': (0.3668,0.5353,1.0000),
	'9800': (0.6148,0.7183,1.0000),
	'35000': (0.3357,0.5091,1.0000),
	'2000': (1.0000,0.2484,0.0061),
	'12200': (0.5125,0.6474,1.0000),
	'28200': (0.3524,0.5232,1.0000),
}

ARCH= platform.architecture()[0]
TEX_TYPES=  {'IMAGE', 'VRAY'}
GEOM_TYPES= {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}

none_matrix= mathutils.Matrix(((0.0,0.0,0.0,0.0),(0.0,0.0,0.0,0.0),(0.0,0.0,0.0,0.0),(0.0,0.0,0.0,0.0)))


def get_username():
	if PLATFORM == 'win32':
		return "standalone"
	else:
		return getpass.getuser()


def copytree(src, dst, symlinks=False, ignore=None):
	if PLATFORM == 'win32':
		os.system('robocopy /E "%s" "%s"' % (src, dst))
	else:
		if not os.path.exists(dst):
			os.makedirs(dst)
		for item in os.listdir(src):
			s = os.path.join(src, item)
			d = os.path.join(dst, item)
			if os.path.isdir(s):
				shutil.copytree(s, d, symlinks, ignore)
			else:
				shutil.copy2(s, d)


# Get RAM directory
# Used for fast temp file access
def get_ram_basedir():
	if PLATFORM == 'linux':
		return "/dev/shm"
	return tempfile.gettempdir()


# Colorize sting on Linux
def color(text, color=None):
	if not color or not PLATFORM == 'linux':
		return text
	if color == 'green':
		return "\033[0;32m%s\033[0m" % text
	elif color == 'red':
		return "\033[0;31m%s\033[0m" % text
	elif color == 'yellow':
		return "\033[0;33m%s\033[0m" % text
	elif color == 'magenta':
		return "\033[0;35m%s\033[0m" % text
	else:
		return text


# Log message
def debug(scene, message, newline= True, cr= True, error= False):
	# sys.stdout.write("[%s] V-Ray/Blender: %s%s%s" % (
	# 	time.strftime("%Y/%b/%d|%H:%m:%S"),
	# 	color("Error! ", 'red') if error else '',
	# 	message,
	# 	'\n' if newline else '\r' if cr else '')
	# )
	sys.stdout.write("%s: %s%s%s" % (
		color("V-Ray/Blender", 'green'),
		color("Error! ", 'red') if error else '',
		message,
		'\n' if newline else '\r' if cr else '')
	)
	if not newline:
		sys.stdout.flush()


# Prints dictionary
def print_dict(scene, title, params, spacing= 2):
	debug(scene, "%s:" % title)
	for key in sorted(params.keys()):
		if type(params[key]) == dict:
			spacing*= 2
			print_dict(scene, key, params[key], spacing)
			spacing/= 2
		elif type(params[key]) in (list,tuple):
			debug(scene, "%s%s" % (''.join([' ']*int(spacing)), color(key, 'yellow')))
			for item in params[key]:
				debug(scene, ''.join([' ']*int(spacing)*2) + str(item))
		else:
			debug(scene, "%s%s: %s" % (''.join([' ']*int(spacing)), color(key, 'yellow'), params[key]))


# Property
def p(t):
	if type(t) is bool:
		return "%i"%(t)
	elif type(t) is int:
		return "%i"%(t)
	elif type(t) is float:
		return "%.6f"%(t)
	elif type(t) is mathutils.Vector:
		return "Vector(%.3f,%.3f,%.3f)"%(t.x,t.y,t.z)
	elif type(t) is mathutils.Color:
		return "Color(%.3f,%.3f,%.3f)"%(t.r,t.g,t.b)
	elif len(t) == 4 and type(t[0]) is float:
		return "AColor(%.3f,%.3f,%.3f,%.3f)"%(t[0],t[1],t[2],t[3])
	elif type(t) is str:
		if t == "True":
			return "1"
		elif t == "False":
			return "0"
		else:
			return t
	else:
		return "%s"%(t)


# Animated property
def a(scene, t):
	VRayScene    = scene.vray
	VRayExporter = VRayScene.exporter

	frame = scene.frame_current

	if VRayExporter.camera_loop:
		frame = VRayExporter.customFrame
	
	if VRayScene.RTEngine.enabled:
		return p(t)

	if VRayExporter.animation or VRayExporter.camera_loop or VRayExporter.use_still_motion_blur:
		return "interpolate((%i,%s))" % (frame, p(t))

	return p(t)


# Checks if object is animated
#
# TODO: cache results
#
def is_animated(ob):
	print("ob.name", ob.name)
	print("ob.animation_data",ob.animation_data)

	if ob.animation_data:
		return True

	if ob.type in GEOM_TYPES:
		# Check if material is animated
		if len(ob.material_slots):
			for slot in ob.material_slots:
				ma = slot.material
				if not ma:
					continue
				if ma.animation_data:
					return True
				# Check if texture is animated
				if len(ma.texture_slots):
					for tSlot in ma.texture_slots:
						if not tSlot:
							continue
						if not tSlot.texture:
							continue
						if tSlot.texture.animation_data:
							return True
	elif ob.type in {'LAMP'}:
		pass

	return False


# Checks if objects mesh is animated
def is_data_animated(ob):
	if not ob.data:
		return False

	print("ob.data.name", ob.name)
	print("ob.data.animation_data", ob.data.animation_data)

	if ob.data.animation_data:
		return True
	if ob.active_shape_key:
		return True
	return False


# Hex value format
def HexFormat(value):
    if type(value) is float:
        bytes= struct.pack('<f', value)
    else:
        bytes= struct.pack('<i', value)
    return ''.join(["%02X" % b for b in bytes])


# Transform matrix string
def transform(m):
	if hasattr(_vray_for_blender, 'getTransformHex'):
		return _vray_for_blender.getTransformHex(m.copy())
	return "Transform(Matrix(Vector(%f,%f,%f),Vector(%f,%f,%f),Vector(%f,%f,%f)),Vector(%f,%f,%f))" % (m[0][0], m[1][0], m[2][0], m[0][1], m[1][1], m[2][1], m[0][2], m[1][2], m[2][2], m[0][3], m[1][3], m[2][3])


# Clean string from forbidden chars
def clean_string(s):
	s= s.replace("+", "p")
	s= s.replace("-", "m")
	for i in range(len(s)):
		c= s[i]
		if not ((c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z') or (c >= '0' and c <= '9')):
			s= s.replace(c, "_")
	return s


# The most powerfull unique name generator =)
def get_random_string():
	return ''.join([random.choice(string.ascii_letters) for x in range(16)])


# Append to list only if item not already in list
def append_unique(array, item):
	if item in array:
		return False
	array.append(item)
	return True


# V-Ray uses UV indexes, Blender uses UV names
# Here we store UV name->index map
def get_uv_layer_id(uv_layers, uv_layer_name):
	if not uv_layer_name:
		return 1
	return uv_layers[uv_layer_name] if uv_layer_name in uv_layers else 1

def get_uv_layers_map(sce):
	uv_layers= {}
	uv_id= 1
	for ma in bpy.data.materials:
		for slot in ma.texture_slots:
			if slot and slot.texture:
				if slot.texture.vray.texture_coords == 'UV':
					if slot.uv_layer and slot.uv_layer not in uv_layers:
						uv_layers[slot.uv_layer]= uv_id
						uv_id+= 1

	if sce.vray.exporter.debug:
		for uv_layer in uv_layers:
			print_dict(sce, "UV layer name map", uv_layers)

	return uv_layers


# Generate visibility list for "Hide From View"
def get_visibility_lists(camera):
	VRayCamera= camera.data.vray

	visibility= {
		'all':     [],
		'camera':  [],
		'gi':      [],
		'reflect': [],
		'refract': [],
		'shadows': [],
	}

	if VRayCamera.hide_from_view:
		for hide_type in visibility:
			if getattr(VRayCamera, 'hf_%s' % hide_type):
				if getattr(VRayCamera, 'hf_%s_auto' % hide_type):
					visibility[hide_type]= generate_object_list(group_names_string= 'hf_%s' % camera.name)
				else:
					visibility[hide_type]= generate_object_list(getattr(VRayCamera, 'hf_%s_objects' % hide_type), getattr(VRayCamera, 'hf_%s_groups' % hide_type))

	return visibility


# Generate list objects from ';' separated object and group strings
def generate_object_list(object_names_string= None, group_names_string= None):
	object_list= []

	if object_names_string:
		ob_names= object_names_string.split(';')
		for ob_name in ob_names:
			if ob_name in bpy.data.objects:
				object_list.append(bpy.data.objects[ob_name])

	if group_names_string:
		gr_names= group_names_string.split(';')
		for gr_name in gr_names:
			if gr_name in bpy.data.groups:
				object_list.extend(bpy.data.groups[gr_name].objects)

	dupliGroup = []
	for ob in object_list:
		if ob.dupli_type == 'GROUP' and ob.dupli_group:
			dupliGroup.extend(ob.dupli_group.objects)
	object_list.extend(dupliGroup)

	return object_list


# Generate list of data from ';' separated string
#
def generateDataList(namesString, dataType):
	dataList = []

	dataPtr = getattr(bpy.data, dataType)

	dataNames = namesString.split(';')
	for dataName in dataNames:
		if dataName in dataPtr:
			dataList.append(dataPtr[dataName])

	return dataList


# Get object used as ORCO projection
def get_orco_object(scene, ob, VRayTexture):
	if VRayTexture.object:
		texture_object= get_data_by_name(scene, 'objects', VRayTexture.object)
		if texture_object:
			return texture_object
	return ob


# Naming
# def get_name(data, bus):
# 	name= data.name
# 	if bus['object']['particle'].get('name'):
# 		name= "%s_%s" % (bus['object']['particle']['name'], name)
# 	if bus['object']['dupli'].get('name'):
# 		name= "%s_%s" % (bus['object']['dupli']['name'], name)
# 	if issubclass(type(data), bpy.types.Lamp):
# 		name= 'LA'+name
# 	elif issubclass(type(data), bpy.types.Texture):
# 		name= 'TE'+name
# 	elif type(data) == bpy.types.Material:
# 		name= 'MA'+name
# 	else:
# 		name= 'OB'+name
# 	if data.library:
# 		name+= "%s%s" % ('LI', get_filename(data.library.filepath))
# 	return clean_string(name)
def get_name(ob, prefix= None):
	if not ob:
		return None
	name= ob.name
	if prefix:
		name= prefix+name
	if ob.library:
		name+= "%s%s" % ('LI', get_filename(ob.library.filepath).replace('.blend',''))
	return clean_string(name)


# Get node name
def get_node_name(node_tree, node):
	return "%s%s" % (get_name(node_tree, prefix='NT'),
					 clean_string(node.name))


# Find node connected to socket
def connected_node(node_tree, node_socket):
	for node in node_tree.links:
		if node.to_socket == node_socket:
			return node.from_node
	return None


# Get node_tree Output
def get_output_node(node_tree, output_node_name=None):
	for node in node_tree.nodes:
		if node.type == 'OUTPUT':
			if output_node_name is not None:
				if output_node_name == node.filepath:
					return node
			else:
				return node
	return None


# Get data by name
def get_data_by_name(sce, data_type, name):
	if data_type == 'objects':
		if name in sce.objects:
			return sce.objects[name]
	elif data_type in ('textures','materials','meshes'):
		data_ptr= getattr(bpy.data, data_type)
		if name in data_ptr:
			return data_ptr[name]
	return None


# Get file name
def get_filename(filepath):
	return os.path.basename(bpy.path.abspath(filepath))


def path_sep_to_unix(filepath):
	if PLATFORM != 'win32':
		filepath = filepath.replace('\\\\', '/')
		filepath = filepath.replace('\\', '/')
	return filepath


def get_path(filepath):
	return os.path.normpath(path_sep_to_unix(bpy.path.abspath(filepath)))


def Quotes(path):
	if PLATFORM != 'win32':
		return '"%s"' % (path)
	return path


# Create directory
def create_dir(directory, pathOnly=False):
	directory = path_sep_to_unix(directory)
	if not pathOnly and not os.path.exists(directory):
		debug(None, "Creating directory \"%s\"... " % directory, newline= False, cr= False)
		try:
			os.mkdir(directory)
			sys.stdout.write("%s\n" % (color("done", 'yellow')))
		except OSError:
			directory= tempfile.gettempdir()
			sys.stdout.write("%s\n" % (color("Fail!", 'red')))
			debug(None, "Using default exporting path: %s" % directory)
	return directory

def create_dir_from_filepath(filepath):
	file_path, file_name= os.path.split(bpy.path.abspath(filepath))
	file_path= create_dir(file_path)
	return os.path.join(file_path, file_name)


# Get full filepath
# Also copies file to DR shared folder
def get_full_filepath(bus, ob, filepath):
	def rel_path(filepath):
		if filepath[:2] == "//":
			return True
		else:
			return False

	scene= bus['scene']

	VRayDR          = scene.vray.VRayDR
	SettingsOptions = scene.vray.SettingsOptions

	# If object is linked and path is relative
	# we need to find correct absolute path
	if ob and ob.library and rel_path(filepath):
		lib_path= os.path.dirname(bpy.path.abspath(ob.library.filepath))
		filepath= os.path.normpath(os.path.join(lib_path,filepath[2:]))

	# Full absolute file path
	src_file = bpy.path.abspath(filepath)
	src_file = path_sep_to_unix(src_file)
	src_file = os.path.normpath(src_file)

	if VRayDR.on and VRayDR.transferAssets == '0':
		# File name
		src_filename= os.path.basename(src_file)

		# DR shared directory
		dest_path= bus['filenames']['DR']['dest_dir']

		# If shared directory is not set
		# just return absolute file path
		if not dest_path:
			return src_file

		file_type= os.path.splitext(src_file)[1]

		component_subdir= ""
		if file_type.lower() in ('ies','lens'):
			component_subdir= "misc"
		elif file_type.lower() == "vrmesh":
			component_subdir= "proxy"
		elif file_type.lower() == "vrmap":
			component_subdir= "lightmaps"
		else:
			component_subdir= "textures"

		if component_subdir:
			dest_path= create_dir(os.path.join(dest_path, component_subdir))

		# Copy file to the shared directory
		dest_file= os.path.join(dest_path, src_filename)

		if os.path.isfile(src_file):
			if os.path.exists(dest_file):
				# Copy only if the file was changed
				if not filecmp.cmp(dest_file, src_file):
					debug(scene, "Copying \"%s\" to \"%s\""% (color(src_filename, 'magenta'), dest_path))
					shutil.copyfile(src_file, dest_file)
				else:
					debug(scene, "File \"%s\" exists and not modified."% (color(src_filename, 'magenta')))
			else:
				debug(scene, "Copying \"%s\" to \"%s\"" % (color(src_filename, 'magenta'), dest_path))
				shutil.copyfile(src_file, dest_file)
		else:
			debug(scene, "\"%s\" is not a file!" % (src_file), error= True)
			return src_file

		if PLATFORM == 'win32':
			return "//%s/%s/%s/%s/%s"%(HOSTNAME,
									   VRayDR.share_name,
									   bus['filenames']['DR']['sub_dir'], component_subdir, src_filename)

		return bus['filenames']['DR']['prefix'] + os.sep + component_subdir + os.sep + src_filename
	else:
		return src_file


# True if object on active layer
def object_on_visible_layers(scene, ob):
	VRayScene    = scene.vray
	VRayExporter = VRayScene.exporter

	activeLayers = scene.layers

	if VRayExporter.activeLayers == 'ALL':
		return True
	elif VRayExporter.activeLayers == 'CUSTOM':
		activeLayers = VRayExporter.customRenderLayers

	for l in range(20):
		if ob.layers[l] and activeLayers[l]:
			return True
	return False


# True if object is visible
def object_visible(bus, ob):
	scene= bus['scene']

	VRayScene=       scene.vray
	VRayExporter=    VRayScene.exporter
	SettingsOptions= VRayScene.SettingsOptions

	if not object_on_visible_layers(scene,ob):
		if ob.type == 'LAMP':
			if not SettingsOptions.light_doHiddenLights:
				return False
		if not SettingsOptions.geom_doHidden:
			return False

	if ob.hide_render:
		if ob.type == 'LAMP':
			if not SettingsOptions.light_doHiddenLights:
				return False
		if not SettingsOptions.geom_doHidden:
			return False

	return True


# Distance between 2 objects
def get_distance(ob1, ob2):
	t1 = ob1.matrix_world.to_translation()
	t2 = ob2.matrix_world.to_translation()
	vec = t1 - t2
	return vec.length


# VRayProxy Creator call
def proxy_creator(hq_filepath, vrmesh_filepath, append= False):
	proxycreator_bin= "proxycreator"

	if PLATFORM == 'linux':
		proxycreator_bin += "_linux"
	elif PLATFORM == 'win32':
		proxycreator_bin += "_windows"
	else:
		proxycreator_bin += "_mac"

	if PLATFORM in ['linux', 'win32']:
		proxycreator_bin += "_"+ARCH[:-3]

	if PLATFORM == 'win32':
		proxycreator_bin += ".exe"

	vray_exporter_path= get_vray_exporter_path()
	if vray_exporter_path:
		proxycreator_bin= os.path.join(vray_exporter_path, "bin", proxycreator_bin)

		if os.path.exists(proxycreator_bin):
			debug(None, "Proxy Creator: %s" % (proxycreator_bin))

			mode = os.stat(proxycreator_bin).st_mode
			if not mode & stat.S_IXUSR:
				os.chmod(proxycreator_bin, mode | stat.S_IXUSR)

			cmd= []
			cmd.append(proxycreator_bin)
			if append:
				cmd.append('--append')
			cmd.append(hq_filepath)
			cmd.append(vrmesh_filepath)

			proc= subprocess.call(cmd)

		else:
			debug(None, "Proxy Creator not found!", error= True)


def GetUserConfigDir():
	userConfigDirpath = bpy.utils.user_resource('CONFIG')
	if not os.path.exists(userConfigDirpath):
		os.makedirs(userConfigDirpath)
	return userConfigDirpath


# Returns path to vb25 folder
def get_vray_exporter_path():
	for vb_path in bpy.utils.script_paths(os.path.join('addons','vb25')):
		if vb_path:
			return vb_path
	for vb_path in bpy.utils.script_paths(os.path.join('startup','vb25')):
		if vb_path:
			return vb_path
	return ""


def getColorMappingFilepath():
	return os.path.join(tempfile.gettempdir(), "colorMapping_%s.vrscene" % (get_username()))


# Detects V-Ray Standalone installation
def get_vray_standalone_path(sce):
	VRayExporter= sce.vray.exporter

	vray_bin= "vray"
	if PLATFORM == 'win32':
		vray_bin+= ".exe"

	def get_env_paths(var):
		split_char= ':'
		if PLATFORM == 'win32':
			split_char= ';'
		env_var= os.getenv(var)
		if env_var:
			return env_var.replace('\"','').split(split_char)
		return []

	def find_vray_std_osx_official():
		vrayPath = "/Applications/ChaosGroup/V-Ray/Standalone_for_snow_leopard_x86/bin/snow_leopard_x86/gcc-4.2/vray"
		if os.path.exists(vrayPath):
			return vrayPath
		return None

	def find_vray_std_osx():
		import glob
		instLogFilepath = "/var/log/chaos_installs"
		if not os.path.exists(instLogFilepath):
			return None
		instLog = open(instLogFilepath, 'r').readlines()
		for l in instLog:
			# Example path:
			#  /Applications/ChaosGroup/V-Ray/Standalone_for_snow_leopard_x86/uninstall/linuxinstaller.app/Contents
			#
			if 'V-Ray Standalone' in l and '[UN]' not in l:
				_tmp_, path = l.strip().split('=')

				# Going up to /Applications/ChaosGroup/V-Ray/Standalone_for_snow_leopard_x86/bin
				path = os.path.normpath(os.path.join(path.strip(), '..', '..', '..', "bin"))

				possiblePaths = glob.glob('%s/*/*/vray' % path)
				if len(possiblePaths):
					return possiblePaths[0]
				return None
		return None

	def find_vray_binary(paths):
		if paths:
			for p in paths:
				if p:
					vray_path= os.path.join(p,vray_bin)
					if os.path.exists(vray_path):
						if VRayExporter.debug:
							debug(sce, "V-Ray found in: %s" % (vray_path))
						return vray_path
		return None

	if not VRayExporter.detect_vray and VRayExporter.vray_binary:
		return bpy.path.abspath(VRayExporter.vray_binary)

	# Check 'VRAY_PATH' environment variable
	#
	vray_standalone_paths= get_env_paths('VRAY_PATH')
	if vray_standalone_paths:
		vray_standalone= find_vray_binary(vray_standalone_paths)
		if vray_standalone:
			return vray_standalone

	# On OS X check default path and install log
	#
	if PLATFORM in {'darwin'}:
		path = find_vray_std_osx_official()
		if path is not None:
			return path
		path = find_vray_std_osx()
		if path is not None:
			return path

	# Try to find Standalone in V-Ray For Maya
	#
	for var in os.environ:
		if var.startswith('VRAY_FOR_MAYA'):
			if var.find('MAIN') != -1:
				debug(sce, "Searching in: %s" % (var))
				vray_maya= find_vray_binary([os.path.join(path, 'bin') for path in get_env_paths(var)])
				if vray_maya:
					debug(sce, "V-Ray found in: %s" % (vray_maya))
					return vray_maya

	# Try to find vray binary in %PATH%
	debug(sce, "V-Ray not found! Trying to start \"%s\" command from $PATH..." % (vray_bin), True)

	return shutil.which(vray_bin)


# Inits directories / files
def init_files(bus):
	scene = bus['scene']

	VRayScene = scene.vray
	
	VRayExporter    = VRayScene.exporter
	VRayDR          = VRayScene.VRayDR
	SettingsOutput  = VRayScene.SettingsOutput
	SettingsOptions = VRayScene.SettingsOptions

	(blendfile_path, blendfile_name) = os.path.split(bpy.data.filepath)

	# Blend-file name without extension
	blendfile_name = os.path.basename(bpy.data.filepath)[:-6] if bpy.data.filepath else "default"

	# Default export directory is system's %TMP%
	default_dir = tempfile.gettempdir()

	# Export and output directory
	export_filepath = os.path.join(default_dir, "vrayblender_"+get_username())
	export_filename = "scene"
	output_filepath = default_dir

	if SettingsOutput.img_dir:
		img_dir = SettingsOutput.img_dir
		if img_dir.startswith("//") and not bpy.data.filepath:
			img_dir = default_dir
		output_filepath = bpy.path.abspath(img_dir)
		if '%C' in output_filepath: output_filepath = output_filepath.replace('%C', scene.camera.name)
		if '%S' in output_filepath: output_filepath = output_filepath.replace('%S', scene.name)
		if '%F' in output_filepath: output_filepath = output_filepath.replace('%F', clean_string(blendfile_name))

	if VRayExporter.output == 'USER':
		if VRayExporter.output_dir:
			export_filepath= bpy.path.abspath(VRayExporter.output_dir)

	elif VRayExporter.output == 'SCENE' and bpy.data.filepath:
		export_filepath= os.path.join(blendfile_path, "vrscene")

	if VRayExporter.output_unique:
		export_filename = blendfile_name

	if VRayExporter.output == 'USER':
		export_filepath = bpy.path.abspath(VRayExporter.output_dir)

	if VRayDR.on:
		export_filename = blendfile_name

	# Distributed rendering
	# filepath is relative = blend-file-name/filename
	if VRayDR.on and VRayDR.transferAssets == '0':
		abs_shared_dir  = os.path.normpath(bpy.path.abspath(VRayDR.shared_dir))
		export_filepath = os.path.normpath(os.path.join(abs_shared_dir, blendfile_name + os.sep))

		bus['filenames']['DR']               = {}
		bus['filenames']['DR']['shared_dir'] = abs_shared_dir
		bus['filenames']['DR']['sub_dir']    = blendfile_name
		bus['filenames']['DR']['dest_dir']   = export_filepath
		bus['filenames']['DR']['prefix']     = bus['filenames']['DR']['dest_dir']
		bus['filenames']['DR']['tex_dir']    = os.path.join(export_filepath, "textures")
		bus['filenames']['DR']['ies_dir']    = os.path.join(export_filepath, "IES")

	if bus['preview']:
		export_filename= "preview"
		if PLATFORM == 'linux':
			export_filepath = os.path.join("/dev/shm", "vrayblender_preview_"+get_username())
		else:
			export_filepath = os.path.join(tempfile.gettempdir(), "vrayblender_preview_"+get_username())

	export_directory = create_dir(export_filepath)

	# XXX: Ugly... If there were some error there could be some open files left
	#
	for key in bus['files']:
		f = bus['files']
		if f and not f.closed:
			f.close()

	for key in ('geometry', 'lights', 'materials', 'textures', 'nodes', 'camera', 'scene', 'environment'):
		if key == 'geometry':
			filepath = os.path.join(export_directory, "%s_geometry_00.vrscene" % (export_filename))
		else:
			if key == 'scene' and (VRayDR.on and VRayDR.transferAssets == '0'):
				# Scene file MUST be on top of scene directory
				filepath = os.path.normpath(os.path.join(export_directory, "..", "%s.vrscene" % (export_filename)))
			else:
				filepath = os.path.normpath(os.path.join(export_directory, "%s_%s.vrscene" % (export_filename, key)))
			bus['files'][key] = open(filepath, 'w')
		bus['filenames'][key] = filepath

	# Duplicate "Color mapping" setting to a separate file for correct preview
	#
	cmFilepath = getColorMappingFilepath()
	bus['filenames']['colorMapping'] = cmFilepath
	if not bus['preview']:
		bus['files']['colorMapping'] = open(cmFilepath, 'w')

	# Render output dir
	bus['filenames']['output'] = create_dir(output_filepath, pathOnly=not VRayExporter.auto_save_render)

	# Render output file name
	ext = SettingsOutput.img_format.lower()

	file_name = "render"
	if SettingsOutput.img_file:
		file_name = SettingsOutput.img_file
		if file_name.find("%C") != -1:
			file_name = file_name.replace("%C", scene.camera.name)
		if file_name.find("%S") != -1:
			file_name = file_name.replace("%S", scene.name)
		if file_name.find("%F") != -1:
			file_name = file_name.replace("%F", blendfile_name)
		file_name = clean_string(file_name)
		load_file_name = file_name
	bus['filenames']['output_filename'] = "%s.%s" % (file_name, ext)

	# Render output - load file name
	if SettingsOutput.img_file_needFrameNumber:
		load_file_name = "%s.%.4i" % (load_file_name, scene.frame_current)
	bus['filenames']['output_loadfile'] = "%s.%s" % (load_file_name, ext)

	# Lightmaps path
	# bus['filenames']['lightmaps']= create_dir(os.path.join(export_filepath, "lightmaps"))

	if VRayExporter.debug:
		debug(scene, "Files:")
		for key in sorted(bus['filenames'].keys()):
			debug(scene, "  {0:16}: {1}".format(key.capitalize(), bus['filenames'][key]))


# Converts kelvin temperature to color
def kelvin_to_rgb(temperature):
	return mathutils.Color(COLOR_TABLE[str(int(temperature / 100) * 100)])


# Load render result
def load_result(engine, w, h, filepath):
	if not os.path.exists(filepath):
		return

	if engine is None:
		return

	result = engine.begin_result(0, 0, w, h)
	layer = result.layers[0]
	try:
		layer.load_from_file(filepath)
	except:
		pass
	engine.end_result(result)


def GetStrSize(nBytes):
	BytesSuffix = (
		(1<<30, 'GB'),
		(1<<20, 'MB'),
		(1<<10, 'kB'),
		(1,     'bytes'),
	)
	for b,s in BytesSuffix:
		if nBytes > b:
			break
	return "%.2f %s" % (nBytes/b, s)


def TimeIt(label):
	def real_decorator(function):
		def wrapper(*args, **kwargs):
			ts = time.clock()
			function(*args, **kwargs)
			te = time.clock()
			debug(bpy.context.scene, "%s: %.2f\n" % (label, te-ts))
		return wrapper
	return real_decorator


def RelPath(filepath):
	path = filepath
	try:
		path = bpy.path.relpath(filepath)
	except ValueError:
		pass
	return path
