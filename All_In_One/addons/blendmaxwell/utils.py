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

import math
import sys
import os
import time
import datetime
import uuid

import bpy
from mathutils import Matrix, Vector

from .log import log, LogStyles


def color_temperature_to_rgb(kelvins):
    # http://www.vendian.org/mncharity/dir3/blackbody/
    # http://www.vendian.org/mncharity/dir3/blackbody/UnstableURLs/bbr_color.html
    # http://www.vendian.org/mncharity/dir3/blackbody/UnstableURLs/bbr_color.txt
    
    table = ((1000.0, (1.0, 0.0337, 0.0)), (1100.0, (1.0, 0.0592, 0.0)), (1200.0, (1.0, 0.0846, 0.0)), (1300.0, (1.0, 0.1096, 0.0)), (1400.0, (1.0, 0.1341, 0.0)),
             (1500.0, (1.0, 0.1578, 0.0)), (1600.0, (1.0, 0.1806, 0.0)), (1700.0, (1.0, 0.2025, 0.0)), (1800.0, (1.0, 0.2235, 0.0)), (1900.0, (1.0, 0.2434, 0.0)),
             (2000.0, (1.0, 0.2647, 0.0033)), (2100.0, (1.0, 0.2889, 0.012)), (2200.0, (1.0, 0.3126, 0.0219)), (2300.0, (1.0, 0.336, 0.0331)), (2400.0, (1.0, 0.3589, 0.0454)),
             (2500.0, (1.0, 0.3814, 0.0588)), (2600.0, (1.0, 0.4034, 0.0734)), (2700.0, (1.0, 0.425, 0.0889)), (2800.0, (1.0, 0.4461, 0.1054)), (2900.0, (1.0, 0.4668, 0.1229)),
             (3000.0, (1.0, 0.487, 0.1411)), (3100.0, (1.0, 0.5067, 0.1602)), (3200.0, (1.0, 0.5259, 0.18)), (3300.0, (1.0, 0.5447, 0.2005)), (3400.0, (1.0, 0.563, 0.2216)),
             (3500.0, (1.0, 0.5809, 0.2433)), (3600.0, (1.0, 0.5983, 0.2655)), (3700.0, (1.0, 0.6153, 0.2881)), (3800.0, (1.0, 0.6318, 0.3112)), (3900.0, (1.0, 0.648, 0.3346)),
             (4000.0, (1.0, 0.6636, 0.3583)), (4100.0, (1.0, 0.6789, 0.3823)), (4200.0, (1.0, 0.6938, 0.4066)), (4300.0, (1.0, 0.7083, 0.431)), (4400.0, (1.0, 0.7223, 0.4556)),
             (4500.0, (1.0, 0.736, 0.4803)), (4600.0, (1.0, 0.7494, 0.5051)), (4700.0, (1.0, 0.7623, 0.5299)), (4800.0, (1.0, 0.775, 0.5548)), (4900.0, (1.0, 0.7872, 0.5797)),
             (5000.0, (1.0, 0.7992, 0.6045)), (5100.0, (1.0, 0.8108, 0.6293)), (5200.0, (1.0, 0.8221, 0.6541)), (5300.0, (1.0, 0.833, 0.6787)), (5400.0, (1.0, 0.8437, 0.7032)),
             (5500.0, (1.0, 0.8541, 0.7277)), (5600.0, (1.0, 0.8642, 0.7519)), (5700.0, (1.0, 0.874, 0.776)), (5800.0, (1.0, 0.8836, 0.8)), (5900.0, (1.0, 0.8929, 0.8238)),
             (6000.0, (1.0, 0.9019, 0.8473)), (6100.0, (1.0, 0.9107, 0.8707)), (6200.0, (1.0, 0.9193, 0.8939)), (6300.0, (1.0, 0.9276, 0.9168)), (6400.0, (1.0, 0.9357, 0.9396)),
             (6500.0, (1.0, 0.9436, 0.9621)), (6600.0, (1.0, 0.9513, 0.9844)), (6700.0, (0.9937, 0.9526, 1.0)), (6800.0, (0.9726, 0.9395, 1.0)), (6900.0, (0.9526, 0.927, 1.0)),
             (7000.0, (0.9337, 0.915, 1.0)), (7100.0, (0.9157, 0.9035, 1.0)), (7200.0, (0.8986, 0.8925, 1.0)), (7300.0, (0.8823, 0.8819, 1.0)), (7400.0, (0.8668, 0.8718, 1.0)),
             (7500.0, (0.852, 0.8621, 1.0)), (7600.0, (0.8379, 0.8527, 1.0)), (7700.0, (0.8244, 0.8437, 1.0)), (7800.0, (0.8115, 0.8351, 1.0)), (7900.0, (0.7992, 0.8268, 1.0)),
             (8000.0, (0.7874, 0.8187, 1.0)), (8100.0, (0.7761, 0.811, 1.0)), (8200.0, (0.7652, 0.8035, 1.0)), (8300.0, (0.7548, 0.7963, 1.0)), (8400.0, (0.7449, 0.7894, 1.0)),
             (8500.0, (0.7353, 0.7827, 1.0)), (8600.0, (0.726, 0.7762, 1.0)), (8700.0, (0.7172, 0.7699, 1.0)), (8800.0, (0.7086, 0.7638, 1.0)), (8900.0, (0.7004, 0.7579, 1.0)),
             (9000.0, (0.6925, 0.7522, 1.0)), (9100.0, (0.6848, 0.7467, 1.0)), (9200.0, (0.6774, 0.7414, 1.0)), (9300.0, (0.6703, 0.7362, 1.0)), (9400.0, (0.6635, 0.7311, 1.0)),
             (9500.0, (0.6568, 0.7263, 1.0)), (9600.0, (0.6504, 0.7215, 1.0)), (9700.0, (0.6442, 0.7169, 1.0)), (9800.0, (0.6382, 0.7124, 1.0)), (9900.0, (0.6324, 0.7081, 1.0)),
             (10000.0, (0.6268, 0.7039, 1.0)), (10100.0, (0.6213, 0.6998, 1.0)), (10200.0, (0.6161, 0.6958, 1.0)), (10300.0, (0.6109, 0.6919, 1.0)), (10400.0, (0.606, 0.6881, 1.0)),
             (10500.0, (0.6012, 0.6844, 1.0)), (10600.0, (0.5965, 0.6808, 1.0)), (10700.0, (0.5919, 0.6773, 1.0)), (10800.0, (0.5875, 0.6739, 1.0)), (10900.0, (0.5833, 0.6706, 1.0)),
             (11000.0, (0.5791, 0.6674, 1.0)), (11100.0, (0.575, 0.6642, 1.0)), (11200.0, (0.5711, 0.6611, 1.0)), (11300.0, (0.5673, 0.6581, 1.0)), (11400.0, (0.5636, 0.6552, 1.0)),
             (11500.0, (0.5599, 0.6523, 1.0)), (11600.0, (0.5564, 0.6495, 1.0)), (11700.0, (0.553, 0.6468, 1.0)), (11800.0, (0.5496, 0.6441, 1.0)), (11900.0, (0.5463, 0.6415, 1.0)),
             (12000.0, (0.5431, 0.6389, 1.0)), (12100.0, (0.54, 0.6364, 1.0)), (12200.0, (0.537, 0.634, 1.0)), (12300.0, (0.534, 0.6316, 1.0)), (12400.0, (0.5312, 0.6293, 1.0)),
             (12500.0, (0.5283, 0.627, 1.0)), (12600.0, (0.5256, 0.6247, 1.0)), (12700.0, (0.5229, 0.6225, 1.0)), (12800.0, (0.5203, 0.6204, 1.0)), (12900.0, (0.5177, 0.6183, 1.0)),
             (13000.0, (0.5152, 0.6162, 1.0)), (13100.0, (0.5128, 0.6142, 1.0)), (13200.0, (0.5104, 0.6122, 1.0)), (13300.0, (0.508, 0.6103, 1.0)), (13400.0, (0.5057, 0.6084, 1.0)),
             (13500.0, (0.5035, 0.6065, 1.0)), (13600.0, (0.5013, 0.6047, 1.0)), (13700.0, (0.4991, 0.6029, 1.0)), (13800.0, (0.497, 0.6012, 1.0)), (13900.0, (0.495, 0.5994, 1.0)),
             (14000.0, (0.493, 0.5978, 1.0)), (14100.0, (0.491, 0.5961, 1.0)), (14200.0, (0.4891, 0.5945, 1.0)), (14300.0, (0.4872, 0.5929, 1.0)), (14400.0, (0.4853, 0.5913, 1.0)),
             (14500.0, (0.4835, 0.5898, 1.0)), (14600.0, (0.4817, 0.5882, 1.0)), (14700.0, (0.4799, 0.5868, 1.0)), (14800.0, (0.4782, 0.5853, 1.0)), (14900.0, (0.4765, 0.5839, 1.0)),
             (15000.0, (0.4749, 0.5824, 1.0)), (15100.0, (0.4733, 0.5811, 1.0)), (15200.0, (0.4717, 0.5797, 1.0)), (15300.0, (0.4701, 0.5784, 1.0)), (15400.0, (0.4686, 0.577, 1.0)),
             (15500.0, (0.4671, 0.5757, 1.0)), (15600.0, (0.4656, 0.5745, 1.0)), (15700.0, (0.4641, 0.5732, 1.0)), (15800.0, (0.4627, 0.572, 1.0)), (15900.0, (0.4613, 0.5708, 1.0)),
             (16000.0, (0.4599, 0.5696, 1.0)), (16100.0, (0.4586, 0.5684, 1.0)), (16200.0, (0.4572, 0.5673, 1.0)), (16300.0, (0.4559, 0.5661, 1.0)), (16400.0, (0.4546, 0.565, 1.0)),
             (16500.0, (0.4534, 0.5639, 1.0)), (16600.0, (0.4521, 0.5628, 1.0)), (16700.0, (0.4509, 0.5617, 1.0)), (16800.0, (0.4497, 0.5607, 1.0)), (16900.0, (0.4485, 0.5597, 1.0)),
             (17000.0, (0.4474, 0.5586, 1.0)), (17100.0, (0.4462, 0.5576, 1.0)), (17200.0, (0.4451, 0.5566, 1.0)), (17300.0, (0.444, 0.5557, 1.0)), (17400.0, (0.4429, 0.5547, 1.0)),
             (17500.0, (0.4418, 0.5538, 1.0)), (17600.0, (0.4408, 0.5528, 1.0)), (17700.0, (0.4397, 0.5519, 1.0)), (17800.0, (0.4387, 0.551, 1.0)), (17900.0, (0.4377, 0.5501, 1.0)),
             (18000.0, (0.4367, 0.5492, 1.0)), (18100.0, (0.4357, 0.5483, 1.0)), (18200.0, (0.4348, 0.5475, 1.0)), (18300.0, (0.4338, 0.5466, 1.0)), (18400.0, (0.4329, 0.5458, 1.0)),
             (18500.0, (0.4319, 0.545, 1.0)), (18600.0, (0.431, 0.5442, 1.0)), (18700.0, (0.4301, 0.5434, 1.0)), (18800.0, (0.4293, 0.5426, 1.0)), (18900.0, (0.4284, 0.5418, 1.0)),
             (19000.0, (0.4275, 0.541, 1.0)), (19100.0, (0.4267, 0.5403, 1.0)), (19200.0, (0.4258, 0.5395, 1.0)), (19300.0, (0.425, 0.5388, 1.0)), (19400.0, (0.4242, 0.5381, 1.0)),
             (19500.0, (0.4234, 0.5373, 1.0)), (19600.0, (0.4226, 0.5366, 1.0)), (19700.0, (0.4218, 0.5359, 1.0)), (19800.0, (0.4211, 0.5352, 1.0)), (19900.0, (0.4203, 0.5345, 1.0)),
             (20000.0, (0.4196, 0.5339, 1.0)), (20100.0, (0.4188, 0.5332, 1.0)), (20200.0, (0.4181, 0.5325, 1.0)), (20300.0, (0.4174, 0.5319, 1.0)), (20400.0, (0.4167, 0.5312, 1.0)),
             (20500.0, (0.416, 0.5306, 1.0)), (20600.0, (0.4153, 0.53, 1.0)), (20700.0, (0.4146, 0.5293, 1.0)), (20800.0, (0.4139, 0.5287, 1.0)), (20900.0, (0.4133, 0.5281, 1.0)),
             (21000.0, (0.4126, 0.5275, 1.0)), (21100.0, (0.4119, 0.5269, 1.0)), (21200.0, (0.4113, 0.5264, 1.0)), (21300.0, (0.4107, 0.5258, 1.0)), (21400.0, (0.41, 0.5252, 1.0)),
             (21500.0, (0.4094, 0.5246, 1.0)), (21600.0, (0.4088, 0.5241, 1.0)), (21700.0, (0.4082, 0.5235, 1.0)), (21800.0, (0.4076, 0.523, 1.0)), (21900.0, (0.407, 0.5224, 1.0)),
             (22000.0, (0.4064, 0.5219, 1.0)), (22100.0, (0.4059, 0.5214, 1.0)), (22200.0, (0.4053, 0.5209, 1.0)), (22300.0, (0.4047, 0.5203, 1.0)), (22400.0, (0.4042, 0.5198, 1.0)),
             (22500.0, (0.4036, 0.5193, 1.0)), (22600.0, (0.4031, 0.5188, 1.0)), (22700.0, (0.4026, 0.5183, 1.0)), (22800.0, (0.402, 0.5178, 1.0)), (22900.0, (0.4015, 0.5174, 1.0)),
             (23000.0, (0.401, 0.5169, 1.0)), (23100.0, (0.4005, 0.5164, 1.0)), (23200.0, (0.4, 0.5159, 1.0)), (23300.0, (0.3995, 0.5155, 1.0)), (23400.0, (0.399, 0.515, 1.0)),
             (23500.0, (0.3985, 0.5146, 1.0)), (23600.0, (0.398, 0.5141, 1.0)), (23700.0, (0.3975, 0.5137, 1.0)), (23800.0, (0.397, 0.5132, 1.0)), (23900.0, (0.3966, 0.5128, 1.0)),
             (24000.0, (0.3961, 0.5123, 1.0)), (24100.0, (0.3956, 0.5119, 1.0)), (24200.0, (0.3952, 0.5115, 1.0)), (24300.0, (0.3947, 0.5111, 1.0)), (24400.0, (0.3943, 0.5107, 1.0)),
             (24500.0, (0.3938, 0.5103, 1.0)), (24600.0, (0.3934, 0.5098, 1.0)), (24700.0, (0.393, 0.5094, 1.0)), (24800.0, (0.3925, 0.509, 1.0)), (24900.0, (0.3921, 0.5086, 1.0)),
             (25000.0, (0.3917, 0.5083, 1.0)), (25100.0, (0.3913, 0.5079, 1.0)), (25200.0, (0.3909, 0.5075, 1.0)), (25300.0, (0.3905, 0.5071, 1.0)), (25400.0, (0.3901, 0.5067, 1.0)),
             (25500.0, (0.3897, 0.5064, 1.0)), (25600.0, (0.3893, 0.506, 1.0)), (25700.0, (0.3889, 0.5056, 1.0)), (25800.0, (0.3885, 0.5053, 1.0)), (25900.0, (0.3881, 0.5049, 1.0)),
             (26000.0, (0.3877, 0.5045, 1.0)), (26100.0, (0.3874, 0.5042, 1.0)), (26200.0, (0.387, 0.5038, 1.0)), (26300.0, (0.3866, 0.5035, 1.0)), (26400.0, (0.3863, 0.5032, 1.0)),
             (26500.0, (0.3859, 0.5028, 1.0)), (26600.0, (0.3855, 0.5025, 1.0)), (26700.0, (0.3852, 0.5021, 1.0)), (26800.0, (0.3848, 0.5018, 1.0)), (26900.0, (0.3845, 0.5015, 1.0)),
             (27000.0, (0.3841, 0.5012, 1.0)), (27100.0, (0.3838, 0.5008, 1.0)), (27200.0, (0.3835, 0.5005, 1.0)), (27300.0, (0.3831, 0.5002, 1.0)), (27400.0, (0.3828, 0.4999, 1.0)),
             (27500.0, (0.3825, 0.4996, 1.0)), (27600.0, (0.3821, 0.4993, 1.0)), (27700.0, (0.3818, 0.499, 1.0)), (27800.0, (0.3815, 0.4987, 1.0)), (27900.0, (0.3812, 0.4984, 1.0)),
             (28000.0, (0.3809, 0.4981, 1.0)), (28100.0, (0.3805, 0.4978, 1.0)), (28200.0, (0.3802, 0.4975, 1.0)), (28300.0, (0.3799, 0.4972, 1.0)), (28400.0, (0.3796, 0.4969, 1.0)),
             (28500.0, (0.3793, 0.4966, 1.0)), (28600.0, (0.379, 0.4963, 1.0)), (28700.0, (0.3787, 0.496, 1.0)), (28800.0, (0.3784, 0.4958, 1.0)), (28900.0, (0.3781, 0.4955, 1.0)),
             (29000.0, (0.3779, 0.4952, 1.0)), (29100.0, (0.3776, 0.4949, 1.0)), (29200.0, (0.3773, 0.4947, 1.0)), (29300.0, (0.377, 0.4944, 1.0)), (29400.0, (0.3767, 0.4941, 1.0)),
             (29500.0, (0.3764, 0.4939, 1.0)), (29600.0, (0.3762, 0.4936, 1.0)), (29700.0, (0.3759, 0.4934, 1.0)), (29800.0, (0.3756, 0.4931, 1.0)), (29900.0, (0.3754, 0.4928, 1.0)),
             (30000.0, (0.3751, 0.4926, 1.0)), (30100.0, (0.3748, 0.4923, 1.0)), (30200.0, (0.3746, 0.4921, 1.0)), (30300.0, (0.3743, 0.4918, 1.0)), (30400.0, (0.3741, 0.4916, 1.0)),
             (30500.0, (0.3738, 0.4914, 1.0)), (30600.0, (0.3735, 0.4911, 1.0)), (30700.0, (0.3733, 0.4909, 1.0)), (30800.0, (0.373, 0.4906, 1.0)), (30900.0, (0.3728, 0.4904, 1.0)),
             (31000.0, (0.3726, 0.4902, 1.0)), (31100.0, (0.3723, 0.4899, 1.0)), (31200.0, (0.3721, 0.4897, 1.0)), (31300.0, (0.3718, 0.4895, 1.0)), (31400.0, (0.3716, 0.4893, 1.0)),
             (31500.0, (0.3714, 0.489, 1.0)), (31600.0, (0.3711, 0.4888, 1.0)), (31700.0, (0.3709, 0.4886, 1.0)), (31800.0, (0.3707, 0.4884, 1.0)), (31900.0, (0.3704, 0.4881, 1.0)),
             (32000.0, (0.3702, 0.4879, 1.0)), (32100.0, (0.37, 0.4877, 1.0)), (32200.0, (0.3698, 0.4875, 1.0)), (32300.0, (0.3695, 0.4873, 1.0)), (32400.0, (0.3693, 0.4871, 1.0)),
             (32500.0, (0.3691, 0.4869, 1.0)), (32600.0, (0.3689, 0.4867, 1.0)), (32700.0, (0.3687, 0.4864, 1.0)), (32800.0, (0.3684, 0.4862, 1.0)), (32900.0, (0.3682, 0.486, 1.0)),
             (33000.0, (0.368, 0.4858, 1.0)), (33100.0, (0.3678, 0.4856, 1.0)), (33200.0, (0.3676, 0.4854, 1.0)), (33300.0, (0.3674, 0.4852, 1.0)), (33400.0, (0.3672, 0.485, 1.0)),
             (33500.0, (0.367, 0.4848, 1.0)), (33600.0, (0.3668, 0.4847, 1.0)), (33700.0, (0.3666, 0.4845, 1.0)), (33800.0, (0.3664, 0.4843, 1.0)), (33900.0, (0.3662, 0.4841, 1.0)),
             (34000.0, (0.366, 0.4839, 1.0)), (34100.0, (0.3658, 0.4837, 1.0)), (34200.0, (0.3656, 0.4835, 1.0)), (34300.0, (0.3654, 0.4833, 1.0)), (34400.0, (0.3652, 0.4831, 1.0)),
             (34500.0, (0.365, 0.483, 1.0)), (34600.0, (0.3649, 0.4828, 1.0)), (34700.0, (0.3647, 0.4826, 1.0)), (34800.0, (0.3645, 0.4824, 1.0)), (34900.0, (0.3643, 0.4822, 1.0)),
             (35000.0, (0.3641, 0.4821, 1.0)), (35100.0, (0.3639, 0.4819, 1.0)), (35200.0, (0.3638, 0.4817, 1.0)), (35300.0, (0.3636, 0.4815, 1.0)), (35400.0, (0.3634, 0.4814, 1.0)),
             (35500.0, (0.3632, 0.4812, 1.0)), (35600.0, (0.363, 0.481, 1.0)), (35700.0, (0.3629, 0.4809, 1.0)), (35800.0, (0.3627, 0.4807, 1.0)), (35900.0, (0.3625, 0.4805, 1.0)),
             (36000.0, (0.3624, 0.4804, 1.0)), (36100.0, (0.3622, 0.4802, 1.0)), (36200.0, (0.362, 0.48, 1.0)), (36300.0, (0.3619, 0.4799, 1.0)), (36400.0, (0.3617, 0.4797, 1.0)),
             (36500.0, (0.3615, 0.4796, 1.0)), (36600.0, (0.3614, 0.4794, 1.0)), (36700.0, (0.3612, 0.4792, 1.0)), (36800.0, (0.361, 0.4791, 1.0)), (36900.0, (0.3609, 0.4789, 1.0)),
             (37000.0, (0.3607, 0.4788, 1.0)), (37100.0, (0.3605, 0.4786, 1.0)), (37200.0, (0.3604, 0.4785, 1.0)), (37300.0, (0.3602, 0.4783, 1.0)), (37400.0, (0.3601, 0.4782, 1.0)),
             (37500.0, (0.3599, 0.478, 1.0)), (37600.0, (0.3598, 0.4779, 1.0)), (37700.0, (0.3596, 0.4777, 1.0)), (37800.0, (0.3595, 0.4776, 1.0)), (37900.0, (0.3593, 0.4774, 1.0)),
             (38000.0, (0.3592, 0.4773, 1.0)), (38100.0, (0.359, 0.4771, 1.0)), (38200.0, (0.3589, 0.477, 1.0)), (38300.0, (0.3587, 0.4768, 1.0)), (38400.0, (0.3586, 0.4767, 1.0)),
             (38500.0, (0.3584, 0.4766, 1.0)), (38600.0, (0.3583, 0.4764, 1.0)), (38700.0, (0.3581, 0.4763, 1.0)), (38800.0, (0.358, 0.4761, 1.0)), (38900.0, (0.3579, 0.476, 1.0)),
             (39000.0, (0.3577, 0.4759, 1.0)), (39100.0, (0.3576, 0.4757, 1.0)), (39200.0, (0.3574, 0.4756, 1.0)), (39300.0, (0.3573, 0.4755, 1.0)), (39400.0, (0.3572, 0.4753, 1.0)),
             (39500.0, (0.357, 0.4752, 1.0)), (39600.0, (0.3569, 0.4751, 1.0)), (39700.0, (0.3567, 0.4749, 1.0)), (39800.0, (0.3566, 0.4748, 1.0)), (39900.0, (0.3565, 0.4747, 1.0)),
             (40000.0, (0.3563, 0.4745, 1.0)), )
    
    if(kelvins <= 1000.0):
        return table[0][1]
    elif(kelvins >= 40000.0):
        return table[len(table) - 1][1]
    else:
        r = round(kelvins / 100) * 100
        i = int(r / 100) - 10
        return table[i][1]


def get_addon_bl_info():
    a = os.path.split(os.path.split(os.path.realpath(__file__))[0])[1]
    m = sys.modules[a]
    return m.bl_info


def get_plugin_id():
    bli = get_addon_bl_info()
    n = bli.get('name', "")
    d = bli.get('description', "")
    v = bli.get('version', (0, 0, 0, ))
    v = ".".join([str(i) for i in v])
    r = ""
    if(n != ""):
        r = "{} ({}), version: {}".format(n, d, v)
    return r


def add_object(name, data):
    """Fastest way of adding new objects.
    All existing objects gets deselected, then new one is added, selected and made active.
    
    name - Name of the new object
    data - Data of the new object, Empty objects can be added by passing None.
    Returns newly created object.
    
    About 40% faster than object_utils.object_data_add and with Empty support.
    """
    
    so = bpy.context.scene.objects
    for i in so:
        i.select = False
    o = bpy.data.objects.new(name, data)
    so.link(o)
    o.select = True
    if(so.active is None or so.active.mode == 'OBJECT'):
        so.active = o
    return o


def add_object2(name, data, ):
    # skip select / active part..
    o = bpy.data.objects.new(name, data, )
    s = bpy.context.scene
    s.objects.link(o)
    return o


def wipe_out_object(ob, and_data=True):
    # http://blenderartists.org/forum/showthread.php?222667-Remove-object-and-clear-from-memory&p=1888116&viewfull=1#post1888116
    
    data = bpy.data.objects[ob.name].data
    # never wipe data before unlink the ex-user object of the scene else crash (2.58 3 770 2)
    # so if there's more than one user for this data, never wipeOutData. will be done with the last user
    # if in the list
    if(data is not None):
        # change: if wiping empty, data in None and following will raise exception
        if(data.users > 1):
            and_data = False
    else:
        and_data = False
    
    # odd:
    ob = bpy.data.objects[ob.name]
    # if the ob (board) argument comes from bpy.data.groups['aGroup'].objects,
    #  bpy.data.groups['board'].objects['board'].users_scene
    
    for sc in ob.users_scene:
        sc.objects.unlink(ob)
    
    try:
        bpy.data.objects.remove(ob)
    except:
        log('data.objects.remove issue with %s' % ob.name, style=LogStyles.ERROR, )
    
    # never wipe data before unlink the ex-user object of the scene else crash (2.58 3 770 2)
    if(and_data):
        wipe_out_data(data)


def wipe_out_data(data):
    # http://blenderartists.org/forum/showthread.php?222667-Remove-object-and-clear-from-memory&p=1888116&viewfull=1#post1888116
    
    if(data.users == 0):
        try:
            data.user_clear()
            if type(data) == bpy.types.Mesh:
                bpy.data.meshes.remove(data)
            elif type(data) == bpy.types.PointLamp:
                bpy.data.lamps.remove(data)
            elif type(data) == bpy.types.Camera:
                bpy.data.cameras.remove(data)
            elif type(data) in [bpy.types.Curve, bpy.types.TextCurve]:
                bpy.data.curves.remove(data)
            elif type(data) == bpy.types.MetaBall:
                bpy.data.metaballs.remove(data)
            elif type(data) == bpy.types.Lattice:
                bpy.data.lattices.remove(data)
            elif type(data) == bpy.types.Armature:
                bpy.data.armatures.remove(data)
            else:
                log('data still here : forgot %s' % type(data), style=LogStyles.ERROR, )
        except:
            log('%s has no user_clear attribute.' % data.name, style=LogStyles.ERROR, )
    else:
        log('%s has %s user(s) !' % (data.name, data.users), style=LogStyles.ERROR, )


class InstanceMeshGenerator():
    """base instance mesh generator class"""
    def __init__(self):
        self.def_verts, self.def_edges, self.def_faces = self.generate()
        self.exponent_v = len(self.def_verts)
        self.exponent_e = len(self.def_edges)
        self.exponent_f = len(self.def_faces)
    
    def generate(self):
        dv = []
        de = []
        df = []
        # -------------------------------------------
        
        dv.append((0, 0, 0))
        
        # -------------------------------------------
        return dv, de, df


class CylinderMeshGenerator(InstanceMeshGenerator):
    def __init__(self, height=1, radius=0.5, sides=6, z_translation=0, z_rotation=0, z_scale=1, ngon_fill=True, inverse=False, enhanced=False, hed=-1, ):
        if(height <= 0):
            log("height is (or less than) 0, which is ridiculous. setting to 0.001..", 1)
            height = 0.001
        self.height = height
        
        if(radius <= 0):
            log("radius is (or less than) 0, which is ridiculous. setting to 0.001..", 1)
            radius = 0.001
        self.radius = radius
        
        if(sides < 3):
            log("sides are less than 3 which is ridiculous. setting to 3..", 1)
            sides = 3
        self.sides = sides
        
        self.z_translation = z_translation
        self.z_rotation = z_rotation
        if(z_scale <= 0):
            log("z scale is (or less than) 0, which is ridiculous. setting to 0.001..", 1)
            z_scale = 0.001
        self.z_scale = z_scale
        
        self.ngon_fill = ngon_fill
        self.inverse = inverse
        
        self.enhanced = enhanced
        if(self.enhanced):
            if(self.radius < self.height):
                if(hed == -1):
                    # default
                    hed = self.radius / 8
                elif(hed <= 0):
                    log("got ridiculous holding edge distance (smaller or equal to 0).. setting to radius/8", 1)
                    hed = self.radius / 8
                elif(hed >= self.radius):
                    log("got ridiculous holding edge distance (higher or equal to radius).. setting to radius/8", 1)
                    hed = self.radius / 8
            else:
                if(hed == -1):
                    # default
                    hed = self.height / 8
                elif(hed <= 0):
                    log("got ridiculous holding edge distance (smaller or equal to 0).. setting to height/8", 1)
                    hed = self.height / 8
                elif(hed >= self.height):
                    log("got ridiculous holding edge distance (higher or equal to height).. setting to height/8", 1)
                    hed = self.height / 8
        self.hed = hed
        
        super(CylinderMeshGenerator, self).__init__()
    
    def generate(self):
        dv = []
        de = []
        df = []
        # -------------------------------------------
        
        zt = Matrix.Translation(Vector((0, 0, self.z_translation)))
        zr = Matrix.Rotation(math.radians(self.z_rotation), 4, (0.0, 0.0, 1.0))
        zs = Matrix.Scale(self.z_scale, 4, (0.0, 0.0, 1.0))
        inv = 0
        if(self.inverse):
            inv = 180
        ri = Matrix.Rotation(math.radians(inv), 4, (0.0, 1.0, 0.0))
        mat = zt * zr * zs * ri
        
        def circle2d_coords(radius, steps, offset, ox, oy):
            r = []
            angstep = 2 * math.pi / steps
            for i in range(steps):
                x = math.sin(i * angstep + offset) * radius + ox
                y = math.cos(i * angstep + offset) * radius + oy
                r.append((x, y))
            return r
        
        def do_quads(o, s, q, cw):
            r = []
            for i in range(s):
                a = o + ((s * q) + i)
                b = o + ((s * q) + i + 1)
                if(b == o + ((s * q) + s)):
                    b = o + (s * q)
                c = o + ((s * q) + i + s)
                d = o + ((s * q) + i + s + 1)
                if(d == o + ((s * q) + s + s)):
                    d = o + ((s * q) + s)
                # debug
                # print(a, b, c, d)
                # production
                # print(a, c, d, b)
                # if(cw):
                #     df.append((a, b, d, c))
                # else:
                #     df.append((a, c, d, b))
                
                if(cw):
                    r.append((a, b, d, c))
                else:
                    r.append((a, c, d, b))
            return r
        
        def do_tris(o, s, c, cw):
            r = []
            for i in range(s):
                a = o + i
                b = o + i + 1
                if(b == o + s):
                    b = o
                # debug
                # print(a, b, c)
                # production
                # print(b, a, c)
                # if(cw):
                #     df.append((a, b, c))
                # else:
                #     df.append((b, a, c))
                if(cw):
                    r.append((a, b, c))
                else:
                    r.append((b, a, c))
            return r
        
        l = self.height
        r = self.radius
        s = self.sides
        h = self.hed
        z = 0.0
        
        if(self.enhanced):
            cvv = []
            
            # holding edge
            c = circle2d_coords(r - h, s, 0, 0, 0)
            for i in c:
                cvv.append(Vector((i[0], i[1], z)))
            
            # bottom circle
            c = circle2d_coords(r, s, 0, 0, 0)
            for i in c:
                cvv.append(Vector((i[0], i[1], z)))
            
            # holding edge
            c = circle2d_coords(r, s, 0, 0, 0)
            for i in c:
                cvv.append(Vector((i[0], i[1], h)))
            
            # holding edge
            c = circle2d_coords(r, s, 0, 0, 0)
            for i in c:
                cvv.append(Vector((i[0], i[1], l - h)))
            
            # bottom circle
            c = circle2d_coords(r, s, 0, 0, 0)
            for i in c:
                cvv.append(Vector((i[0], i[1], l)))
            
            # holding edge
            c = circle2d_coords(r - h, s, 0, 0, 0)
            for i in c:
                cvv.append(Vector((i[0], i[1], l)))
            
            if(self.ngon_fill is False):
                # bottom nad top center vertex
                cvv.append(Vector((z, z, z)))
                cvv.append(Vector((z, z, l)))
            
            for i, v in enumerate(cvv):
                # cvv[i] = v * mat
                cvv[i] = mat * v
            for v in cvv:
                dv.append(v.to_tuple())
            
            qr = 5
            for q in range(qr):
                df.extend(do_quads(0, s, q, False))
            
            if(self.ngon_fill):
                ng = []
                for i in range(s):
                    ng.append(i)
                df.append(tuple(ng))
                ng = []
                for i in range(len(dv) - s, len(dv)):
                    ng.append(i)
                df.append(tuple(reversed(ng)))
                
            else:
                df.extend(do_tris(0, s, len(dv) - 2, True))
                df.extend(do_tris(len(dv) - 2 - s, s, len(dv) - 1, False))
            
        else:
            cvv = []
            c = circle2d_coords(r, s, 0, 0, 0)
            for i in c:
                cvv.append(Vector((i[0], i[1], z)))
            c = circle2d_coords(r, s, 0, 0, 0)
            for i in c:
                cvv.append(Vector((i[0], i[1], l)))
            
            if(self.ngon_fill is False):
                cvv.append(Vector((0, 0, 0)))
                cvv.append(Vector((0, 0, l)))
            
            for i, v in enumerate(cvv):
                # cvv[i] = v * mat
                cvv[i] = mat * v
            for v in cvv:
                dv.append(v.to_tuple())
            
            if(self.ngon_fill):
                df.extend(do_quads(0, s, 0, False))
                
                ng = []
                for i in range(s):
                    ng.append(i)
                df.append(tuple(ng))
                ng = []
                for i in range(len(dv) - s, len(dv)):
                    ng.append(i)
                df.append(tuple(reversed(ng)))
                
            else:
                df.extend(do_quads(0, s, 0, False))
                df.extend(do_tris(0, s, len(dv) - 2, True))
                df.extend(do_tris(len(dv) - 2 - s, s, len(dv) - 1, False))
        
        # -------------------------------------------
        return dv, de, df


def benchmark(t=None):
    if(t is None):
        return time.time()
    d = datetime.timedelta(seconds=time.time() - t)
    log("benchmark: {} {}".format(d, '-' * 50), 0, LogStyles.MESSAGE)
    return time.time()


def tmp_dir(purpose=None, uid=None, use_blend_name=False, custom_name=None, override_path=None, ):
    """create temp directory, look into preferences where to create it, build its name, create and return its absolute path
    naming pattern: 'tmp-PURPOSE-UUID', without purpose 'tmp-UUID', when use_blend_name is True, 'BLEND_NAME-tmp_dir-PURPOSE-UUID' or 'BLEND_NAME-tmp_dir-UUID'
    purpose:        string, something descriptive, such as 'material_preview' or so
    uid:            to prevent overwriting what is already there, add uuid to directory name. probability that someone is using such names and probability for the identical name is sufficiently infinitesimal i guess
    use_blend_name: blend name as directory prefix
    custom_name:    the same like use_blend_name but you can set whatever you want, use_blend_name should be False
    override_path:  path is set outside, so use this one. only create if needed..
    return          absolute path string
    """
    def prefs():
        a = os.path.split(os.path.split(os.path.realpath(__file__))[0])[1]
        p = bpy.context.user_preferences.addons[a].preferences
        return p
    
    if(override_path is not None):
        if(os.path.exists(override_path) is False):
            os.makedirs(override_path)
        return override_path
    
    blend = os.path.realpath(bpy.path.abspath(bpy.data.filepath))
    _, blend_file = os.path.split(blend)
    blend_name, _ = os.path.splitext(blend_file)
    
    if(purpose is None):
        purpose = ""
    
    if(uid is None or uid == ""):
        uid = uuid.uuid1()
    
    if(custom_name is None):
        custom_name = ""
    
    root = os.path.realpath(bpy.path.abspath("//"))
    if(prefs().tmp_dir_use == 'SPECIFIC_DIRECTORY'):
        tmpsd = os.path.realpath(bpy.path.abspath(prefs().tmp_dir_path))
        if(os.path.exists(tmpsd)):
            if(os.path.isdir(tmpsd)):
                if(os.access(tmpsd, os.W_OK)):
                    root = tmpsd
                else:
                    log("specific temp directory ('{}') is not writeable, using default".format(tmpsd), 1, LogStyles.WARNING)
            else:
                log("specific temp directory ('{}') is not a directory, using default".format(tmpsd), 1, LogStyles.WARNING)
        else:
            log("specific temp directory ('{}') does not exist, using default".format(tmpsd), 1, LogStyles.WARNING)
    else:
        # tmp_dir_use == 'BLEND_DIRECTORY' ie '//'
        pass
    
    if(purpose == ""):
        if(use_blend_name):
            # BLEND_NAME-tmp-UUID
            tmp_dir = os.path.join(root, "{}-tmp-{}".format(blend_name, uid))
        else:
            if(custom_name != ""):
                # CUSTOM_NAME-tmp-UUID
                tmp_dir = os.path.join(root, "{}-tmp-{}".format(custom_name, uid))
            else:
                # tmp-UUID
                tmp_dir = os.path.join(root, "tmp-{}".format(uid))
    else:
        if(use_blend_name):
            # BLEND_NAME-tmp-PURPOSE-UUID
            tmp_dir = os.path.join(root, "{}-tmp-{}-{}".format(blend_name, purpose, uid))
        else:
            if(custom_name != ""):
                # CUSTOM_NAME-tmp-PURPOSE-UUID
                tmp_dir = os.path.join(root, "{}-tmp-{}-{}".format(custom_name, purpose, uid))
            else:
                # tmp-PURPOSE-UUID
                tmp_dir = os.path.join(root, "tmp-{}-{}".format(purpose, uid))
    
    if(os.path.exists(tmp_dir) is False):
        os.makedirs(tmp_dir)
    
    log("using temp directory at '{}'".format(tmp_dir), 1, LogStyles.MESSAGE, )
    return tmp_dir
