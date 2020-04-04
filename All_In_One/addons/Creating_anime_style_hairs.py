# Anime Hair Generator
# Copyright © 2019 Mateusz Dera

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

bl_info = {
    'name': 'Creating anime style hairs',
    "author": "Mateusz Dera",
    "category": "Learnbgame",
}

import bpy
import math
from bpy import * #context, data, ops
from mathutils import Euler, Matrix, Quaternion, Vector

class X1(bpy.types.PropertyGroup):

    my_bool = bpy.props.BoolProperty(
        name="Front",
        description="Additional front hairs",
        default = False
        )
class X2(bpy.types.PropertyGroup):
            
    my_bool2 = bpy.props.BoolProperty(
        name="Style 1",
        description="Style 1",
        default = True
        )
class X3(bpy.types.PropertyGroup):
            
    my_bool3 = bpy.props.BoolProperty(
        name="Style 2",
        description="Style 2",
        default = False
        )
        
class ToggleOperator(bpy.types.Operator):
    bl_idname = "view3d.toggle_mybool"
    bl_label = "Toggle My Bool"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):  
        context.scene.my_tool.my_bool = not context.scene.my_tool.my_bool
        context.area.tag_redraw()
        return {'FINISHED'}
    
class ToggleOperator2(bpy.types.Operator):
    bl_idname = "view3d.toggle_mybool"
    bl_label = "Toggle My Bool2"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):  
        context.scene.my_tool2.my_bool2 = not context.scene.my_tool2.my_bool2
        context.area.tag_redraw()
        return {'FINISHED'}

class ToggleOperator3(bpy.types.Operator):
    bl_idname = "view3d.toggle_mybool"
    bl_label = "Toggle My Bool3"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):  
        context.scene.my_tool3.my_bool3 = not context.scene.my_tool3.my_bool3
        context.area.tag_redraw()
        return {'FINISHED'}

class generate(bpy.types.Operator):
    bl_idname = 'mesh.generate_hairs'
    bl_label = 'Generate Hairs'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        def basic_closed_curve(name, p0, p1, p2, p3):
            # Create curve and cache reference.
            ops.curve.primitive_bezier_circle_add(enter_editmode=False)
            curve = context.active_object
            curve.name = 'Basic Closed Curve' + name
            bez_points = curve.data.splines[0].bezier_points

            # Set handles to desired handle type.
            for bez_point in bez_points:
                bez_point.handle_left_type = 'FREE'
                bez_point.handle_right_type = 'FREE'   

            # Left point.
            bez_points[0].co = p0[1]
            bez_points[0].handle_left = p0[0]
            bez_points[0].handle_right = p0[2]

            # Top-middle point.
            bez_points[1].co = p1[1]
            bez_points[1].handle_left = p1[0]
            bez_points[1].handle_right = p1[2]

            # Right point.
            bez_points[2].co = p2[1]
            bez_points[2].handle_left = p2[0]
            bez_points[2].handle_right = p2[2]

            # Bottom point.
            bez_points[3].co = p3[1]
            bez_points[3].handle_left = p3[0]
            bez_points[3].handle_right = p3[2]
            
            return curve.name

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        def basic_simple_curve(name, p0, p1):
            ops.curve.primitive_bezier_curve_add(enter_editmode=False)
            curve = context.active_object
            curve.name = 'Basic Simple Curve' + name
            bez_points = curve.data.splines[0].bezier_points

            # Set handles to desired handle type.
            for bez_point in bez_points:
                bez_point.handle_left_type = 'FREE'
                bez_point.handle_right_type = 'FREE'   

            # First point.
            bez_points[0].co = p0[1]
            bez_points[0].handle_left = p0[0]
            bez_points[0].handle_right = p0[2]

            # Second point.
            bez_points[1].co = p1[1]
            bez_points[1].handle_left = p1[0]
            bez_points[1].handle_right = p1[2]
            
            return curve.name

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        def single_hair(closed, simple, p0, p1, p3):
            ops.curve.primitive_bezier_curve_add(enter_editmode=False)
            curve = context.active_object
            curve.name = 'First Type'
            bez_points = curve.data.splines[0].bezier_points

            # Set handles to desired handle type.
            for bez_point in bez_points:
                bez_point.handle_left_type = 'FREE'
                bez_point.handle_right_type = 'FREE'   

            mat = bpy.data.materials.new("PKHG")
            mat.diffuse_color = (float(.5),0.0,1.0)
            curve.active_material = mat

            # First point.
            bez_points[0].co = p0[1]
            bez_points[0].handle_left = p0[0]
            bez_points[0].handle_right = p0[2]

            # Second point.
            bez_points[1].co = p1[1]
            bez_points[1].handle_left = p1[0]
            bez_points[1].handle_right = p1[2]
            
            # Shape
            curve.data.bevel_object = bpy.data.objects[closed]
            curve.data.taper_object = bpy.data.objects[simple]
            
            # Transform
            bpy.context.scene.objects.active.scale = p3[0]
            bpy.context.scene.objects.active.rotation_euler = p3[1]
            bpy.context.scene.objects.active.location = p3[2]
            
        # Front
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p0 = []
        p0.append(Vector((-0.5500, -0.4500, 0.0000)))
        p0.append(Vector((0.0000, -0.4500, 0.0000)))
        p0.append(Vector((0.5500, -0.4500, 0.0000)))

        p1 = []
        p1.append(Vector((1.0000, -0.1800, 0.0000)))
        p1.append(Vector((1.0000, 0.0000, 0.0000)))
        p1.append(Vector((0.8198, 0.2332, 0.0000)))

        p2 = []
        p2.append(Vector((0.6908, 0.6175, 0.0000)))
        p2.append(Vector((-0.0639, 0.5629, 0.0000)))
        p2.append(Vector((-0.2992, 0.5264, 0.0000)))

        p3 = []
        p3.append(Vector((-0.9409, 0.2253, 0.0000)))
        p3.append(Vector((-1.0000, 0.0000, 0.0000)))
        p3.append(Vector((-1.0000, -0.1800, 0.000)))

        first_closed = basic_closed_curve('01', p0, p1, p2, p3)

        p4 = []
        p4.append(Vector((1.6000, -0.3400, 0.0000)))
        p4.append(Vector((-1.0000, 0.0000, 0.0000)))
        p4.append(Vector((-0.5000, 0.2800, 0.0000)))

        p5 = []
        p5.append(Vector((0.3500, 0.3500, 0.0000)))
        p5.append(Vector((1.0000, 0.0000, 0.0000)))
        p5.append(Vector((1.9900, -0.1700, 0.0000)))

        first_simple = basic_simple_curve('01', p4, p5)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p6 = []
        p6.append(Vector((-0.5500, 0.0082, -0.0174)))
        p6.append(Vector((0.0000, 0.0082, -0.0174)))
        p6.append(Vector((0.5500, 0.0082, -0.0174)))

        p7 = []
        p7.append(Vector((1.0000, -0.1800, -0.0174)))
        p7.append(Vector((1.0000, 0.0000, -0.0174)))
        p7.append(Vector((0.8455, 0.3240, -0.0174)))

        p8 = []
        p8.append(Vector((0.0944, 0.5268, -0.0174)))
        p8.append(Vector((-0.0902, 0.4995, -0.0174)))
        p8.append(Vector((-0.3255, 0.4631, -0.0174)))

        p9 = []
        p9.append(Vector((-0.8818, 0.0084, -0.0174)))
        p9.append(Vector((-1.0000, -0.2153, -0.0174)))
        p9.append(Vector((-1.0000, -0.3953, -0.0174)))

        second_closed = basic_closed_curve('02', p6, p7, p8, p9)

        p10 = []
        p10.append(Vector((1.6000, -0.3400, 0.0000)))
        p10.append(Vector((-1.0000, 0.0000, 0.0000)))
        p10.append(Vector((-0.5000, 0.2800, 0.0000)))

        p11 = []
        p11.append(Vector((0.5389, 1.4427, 0.0000)))
        p11.append(Vector((1.0000, 0.0000, 0.0000)))
        p11.append(Vector((1.9900, -0.1700, 0.0000)))

        second_simple = basic_simple_curve('02', p10, p11)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p12 = []
        p12.append(Vector((0.1245, 0.2037, 0.0916)))
        p12.append(Vector((0.0124, 0.1637, -0.0280)))
        p12.append(Vector((0.2630, -0.8983, 0.3541)))

        p13 = []
        p13.append(Vector((0.1858, -2.2267, -0.9604)))
        p13.append(Vector((1.0884, -2.2705, -3.0047)))
        p13.append(Vector((0.4267, -1.6870, -1.9636)))

        p14 = []
        p14.append(Vector((0.7346, -0.3922, -0.3078)))
        p14.append(Vector((math.radians(27.5962), math.radians(142.589), math.radians(-224.597))))
        p14.append(Vector((-0.0715, -1.0689, 2.4231)))

        single_hair(first_closed, first_simple, p12, p13, p14)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p16 = []
        p16.append(Vector((0.0474, 0.0234, -0.0433)))
        p16.append(Vector((0.0211, 0.0141, -0.0278)))
        p16.append(Vector((-0.4961, -1.8625, 0.3345)))

        p17 = []
        p17.append(Vector((0.6021, -2.3578, -1.2558)))
        p17.append(Vector((-0.1304, -3.3095, -2.2563)))
        p17.append(Vector((-0.3387, -0.2077, -0.1034)))

        p18 = []
        p18.append(Vector((-0.5161, -0.3922, -0.3078)))
        p18.append(Vector((math.radians(43.0794), math.radians(175.762), math.radians(-204.492))))
        p18.append(Vector((-0.0382, -1.0437, 2.4477)))


        single_hair(first_closed, first_simple, p16, p17, p18)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p19 = []
        p19.append(Vector((0.0605, 0.0819, -0.0501)))
        p19.append(Vector((0.0378, 0.0843, -0.0516)))
        p19.append(Vector((-0.1054, -0.1891, 0.2761)))

        p20 = []
        p20.append(Vector((0.1418, -2.4546, 0.2383)))
        p20.append(Vector((0.4127, -3.3218, -1.6458)))
        p20.append(Vector((0.0087, 0.0489, 0.0797)))

        p21 = []
        p21.append(Vector((0.3078, 0.3078, 0.3078)))
        p21.append(Vector((math.radians(-135.427), math.radians(181.645), math.radians(-173.21))))
        p21.append(Vector((-0.0269, -1.0361, 2.4331)))

        single_hair(first_closed, first_simple, p19, p20, p21)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p22 = []
        p22.append(Vector((0.0474, 0.0234, -0.0433)))
        p22.append(Vector((0.0211, 0.0141, -0.0278)))
        p22.append(Vector((0.1448, -0.4429, 0.4276)))

        p23 = []
        p23.append(Vector((-0.2247, -2.3724, 0.0233)))
        p23.append(Vector((0.6031, -2.8554, -2.2048)))
        p23.append(Vector((0.1264, 0.4731, -0.5563)))

        p24 = []
        p24.append(Vector((0.5161, 0.3922, 0.3078)))
        p24.append(Vector((math.radians(-136.921), math.radians(184.238), math.radians(-155.508))))
        p24.append(Vector((-0.0223, -1.0437, 2.4477)))

        single_hair(first_closed, first_simple, p22, p23, p24)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p25 = []
        p25.append(Vector((0.2900, -0.0027, -0.2220)))
        p25.append(Vector((0.1142, 0.0905, -0.1349)))
        p25.append(Vector((0.3759, -0.3174, 0.6216)))

        p26 = []
        p26.append(Vector((-3.9942, -2.1316, -0.3099)))
        p26.append(Vector((0.6691, -4.0723, -2.7557)))
        p26.append(Vector((-3.7605, -0.7307, -0.2524)))

        p27 = []
        p27.append(Vector((0.1846, 0.3067, 0.3074)))
        p27.append(Vector((math.radians(-148.388), math.radians(180.073), math.radians(-103.587))))
        p27.append(Vector((-0.0174, -1.0428, 2.4287)))

        single_hair(first_closed, first_simple, p25, p26, p27)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p28 = []
        p28.append(Vector((0.1997, 0.1810, 0.1567)))
        p28.append(Vector((0.0876, 0.1410, 0.0372)))
        p28.append(Vector((-0.0521, -1.2464, 0.2709)))

        p29 = []
        p29.append(Vector((0.6762, -1.8978, -0.4249)))
        p29.append(Vector((0.6527, -2.6536, -3.4344)))
        p29.append(Vector((-0.0091, -2.0702, -2.3932)))

        p30 = []
        p30.append(Vector((-0.7346, 0.3922, 0.3078)))
        p30.append(Vector((math.radians(27.5962), math.radians(-37.4106), math.radians(-315.403))))
        p30.append(Vector((0.0628, -1.0177, 2.4495)))


        single_hair(first_closed, first_simple, p28, p29, p30)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p31 = []
        p31.append(Vector((0.1578, -1.2012, 0.4306)))
        p31.append(Vector((0.2201, 0.4303, -0.4083)))
        p31.append(Vector((-0.4468, -1.0094, 1.4471)))

        p32 = []
        p32.append(Vector((1.0629, -3.4865, -1.7192)))
        p32.append(Vector((-0.0290, -3.8182, -3.8705)))
        p32.append(Vector((0.6691, -2.8950, -1.7503)))

        p33 = []
        p33.append(Vector((-0.5161, 0.3922, 0.3078)))
        p33.append(Vector((math.radians(48.489), math.radians(-21.9885), math.radians(-311.352))))
        p33.append(Vector((0.2155, -1.0767, 2.4368)))


        single_hair(first_closed, first_simple, p31, p32, p33)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p34 = []
        p34.append(Vector((-0.0413, -0.5441, -0.0555)))
        p34.append(Vector((0.2038, 0.3199, -0.3361)))
        p34.append(Vector((-0.4124, -1.1984, 0.8252)))

        p35 = []
        p35.append(Vector((-0.1608, -2.5737, -2.0292)))
        p35.append(Vector((0.9169, -3.7260, -2.9079)))
        p35.append(Vector((0.2441, -1.7120, 0.3762)))

        p36 = []
        p36.append(Vector((0.5161, -0.3922, -0.3078)))
        p36.append(Vector((math.radians(48.489), math.radians(158.011), math.radians(-217.571))))
        p36.append(Vector((-0.2381, -1.1318, 2.4473)))

        single_hair(first_closed, first_simple, p34, p35, p36)

        # Left
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p37 = []
        p37.append(Vector((0.0667, 0.4420, 0.0200)))
        p37.append(Vector((-0.0455, 0.4020, -0.0995)))
        p37.append(Vector((-0.0238, -1.2097, 1.2622)))

        p38 = []
        p38.append(Vector((0.4460, -2.6228, -1.5982)))
        p38.append(Vector((1.3015, -1.7020, -2.4903)))
        p38.append(Vector((1.7387, -1.7911, -2.2080)))

        p39 = []
        p39.append(Vector((0.9777, -0.4192, -0.3946)))
        p39.append(Vector((math.radians(19.3876), math.radians(136.488), math.radians(447.84))))
        p39.append(Vector((-0.2130, -1.0463, 2.3889)))

        single_hair(first_closed, first_simple, p37, p38, p39)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p40 = []
        p40.append(Vector((0.2298, 0.7032, 0.4218)))
        p40.append(Vector((0.1375, 0.5391, 0.3184)))
        p40.append(Vector((-0.2850, -1.2560, 0.3807)))

        p41 = []
        p41.append(Vector((0.5712, -2.2586, -1.7462)))
        p41.append(Vector((0.9980, -2.2803, -2.1546)))
        p41.append(Vector((1.3912, -1.4322, -2.3540)))

        p42 = []
        p42.append(Vector((0.6926, -0.3673, -0.3712)))
        p42.append(Vector((math.radians(32.9117), math.radians(152.807), math.radians(457.159))))
        p42.append(Vector((-0.5528, -0.8084, 2.3493)))

        single_hair(first_closed, first_simple, p40, p41, p42)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
        p43 = []
        p43.append(Vector((0.2607, 0.8334, 0.2688)))
        p43.append(Vector((0.1351, 0.8216, 0.1329)))
        p43.append(Vector((-0.4874, -0.6006, 0.9036)))

        p44 = []
        p44.append(Vector((0.6244, -1.9791, -1.0514)))
        p44.append(Vector((1.2673, -1.7254, -2.2090)))
        p44.append(Vector((1.7044, -1.8145, -1.9267)))

        p45 = []
        p45.append(Vector((0.7509, -0.4244, -0.3047)))
        p45.append(Vector((math.radians(43.8763), math.radians(147.565), math.radians(439.213))))
        p45.append(Vector((-0.6615, -0.6697, 2.3049)))

        single_hair(first_closed, first_simple, p43, p44, p45)

        # Right
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p46 = []
        p46.append(Vector((0.4553, -1.1703, 0.7381)))
        p46.append(Vector((0.1929, 0.2913, -0.3907)))
        p46.append(Vector((-0.4481, -1.0763, 1.5393)))

        p47 = []
        p47.append(Vector((0.9868, -3.3524, -1.5548)))
        p47.append(Vector((0.1581, -3.6720, -3.9506)))
        p47.append(Vector((1.8143, -4.7249, -3.4023)))

        p48 = []
        p48.append(Vector((-0.7099, 0.3922, 0.3078)))
        p48.append(Vector((math.radians(39.6701), math.radians(-25.9542), math.radians(-285.447))))
        p48.append(Vector((0.2067, -1.0104, 2.4838)))

        single_hair(first_closed, first_simple, p46, p47, p48)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p49 = []
        p49.append(Vector((-0.0669, 0.1261, 0.0898)))
        p49.append(Vector((-0.0842, 0.0216, 0.0722)))
        p49.append(Vector((-0.2187, -1.1696, 0.5329)))

        p50 = []
        p50.append(Vector((0.6511, -1.9113, -1.2389)))
        p50.append(Vector((0.7624, -2.0067, -4.6478)))
        p50.append(Vector((-0.2565, -1.4577, -1.6127)))

        p51 = []
        p51.append(Vector((-0.5161, -0.3922, -0.3078)))
        p51.append(Vector((math.radians(2.87559), math.radians(200.923), math.radians(-64.2996))))
        p51.append(Vector((0.2406, -1.0540, 2.4172)))


        single_hair(first_closed, first_simple, p49, p50, p51)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p52 = []
        p52.append(Vector((-0.0847, 0.1773, 0.0175)))
        p52.append(Vector((-0.1021, 0.0728, -0.0001)))
        p52.append(Vector((-0.1426, -0.5277, 0.0627)))

        p53 = []
        p53.append(Vector((0.9169, -1.3514, -0.5460)))
        p53.append(Vector((1.1228, -1.0250, -4.8204)))
        p53.append(Vector((-0.1897, -1.7864, -2.3303)))

        p54 = []
        p54.append(Vector((-0.5161, -0.3922, -0.3078)))
        p54.append(Vector((math.radians(-9.95378), math.radians(203.561), math.radians(-47.7315))))
        p54.append(Vector((0.4077, -0.9401, 2.4521)))

        single_hair(first_closed, first_simple, p52, p53, p54)

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p55 = []
        p55.append(Vector((0.3173, 0.6770, 0.2944)))
        p55.append(Vector((0.1916, 0.6651, 0.1586)))
        p55.append(Vector((-0.3146, 0.2161, 0.7578)))

        p56 = []
        p56.append(Vector((0.1294, -1.9445, -1.1856)))
        p56.append(Vector((0.8276, -1.7547, -3.6173)))
        p56.append(Vector((1.2648, -1.8438, -3.3350)))

        p57 = []
        p57.append(Vector((-0.7509, 0.4244, 0.3047)))
        p57.append(Vector((math.radians(30.8204), math.radians(-27.536), math.radians(446.541))))
        p57.append(Vector((0.6088, -0.6529, 2.3272)))


        single_hair(first_closed, first_simple, p55, p56, p57)

        # Top
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p58 = []
        p58.append(Vector((0.0001, 0.5690, -0.0156)))
        p58.append(Vector((0.0001, 0.0690, -0.0156)))
        p58.append(Vector((0.1037, -0.3440, 0.1191)))

        p59 = []
        p59.append(Vector((-0.2372, -1.2894, -0.6000)))
        p59.append(Vector((0.0223, -1.7789, -1.4055)))
        p59.append(Vector((-0.0179, -2.7299, -1.5019)))

        p60 = []
        p60.append(Vector((-0.6184, -0.6184, -0.6184)))
        p60.append(Vector((math.radians(135.929), math.radians(52.26), math.radians(-31.0181))))
        p60.append(Vector((0.6155, 0.1559, 2.2849)))

        single_hair(second_closed, second_simple, p58, p59, p60)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p61 = []
        p61.append(Vector((0.0187, 0.4834, -0.0038)))
        p61.append(Vector((0.0187, -0.0166, -0.0038)))
        p61.append(Vector((-0.1589, -0.6596, -0.0170)))

        p62 = []
        p62.append(Vector((-0.0286, -1.2223, -0.5865)))
        p62.append(Vector((0.7650, -0.9313, -0.8792)))
        p62.append(Vector((-0.7827, -0.8605, -0.2023)))

        p63 = []
        p63.append(Vector((1.0000, 1.0000, 1.0000)))
        p63.append(Vector((math.radians(-230.898), math.radians(165.367), math.radians(-233.108))))
        p63.append(Vector((0.6252, 0.2029, 2.2595)))

        single_hair(first_closed, first_simple, p61, p62, p63)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p64 = []
        p64.append(Vector((-0.0806, 0.5038, -0.0003)))
        p64.append(Vector((-0.0806, 0.0038, -0.0003)))
        p64.append(Vector((0.0849, -0.4426, 0.1688)))

        p65 = []
        p65.append(Vector((-0.1305, -1.4913, -0.4922)))
        p65.append(Vector((-0.0059, -1.7926, -1.3982)))
        p65.append(Vector((-0.0059, -2.7926, -1.3982)))

        p66 = []
        p66.append(Vector((0.6184, 0.6184, 0.6184)))
        p66.append(Vector((math.radians(-44.0714), math.radians(-52.26), math.radians(31.0181))))
        p66.append(Vector((-0.6491, 0.1508, 2.2602)))


        single_hair(second_closed, second_simple, p64, p65, p66)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p67 = []
        p67.append(Vector((-0.0710, 0.5483, -0.0462)))
        p67.append(Vector((-0.0710, 0.0483, -0.0462)))
        p67.append(Vector((-0.0281, -0.4413, 0.2166)))

        p68 = []
        p68.append(Vector((-0.1959, -1.4251, -0.5101)))
        p68.append(Vector((-0.3912, -1.3697, -0.6346)))
        p68.append(Vector((-0.3912, -2.3697, -0.6346)))

        p69 = []
        p69.append(Vector((0.6907, 0.6907, 0.6907)))
        p69.append(Vector((math.radians(125.594), math.radians(-163.046), math.radians(236.241))))
        p69.append(Vector((-0.6592, 0.1737, 2.2339)))

        single_hair(first_closed, first_simple, p67, p68, p69)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p70 = []
        p70.append(Vector((0.0399, 0.5721, 0.0016)))
        p70.append(Vector((0.0399, 0.0721, 0.0016)))
        p70.append(Vector((-0.0757, -0.3066, -0.1541)))

        p71 = []
        p71.append(Vector((-0.4069, -1.3559, -0.2237)))
        p71.append(Vector((0.5583, -1.4849, -0.9043)))
        p71.append(Vector((0.5583, -2.4849, -0.9043)))

        p72 = []
        p72.append(Vector((0.6378, 0.6378, 0.6378)))
        p72.append(Vector((math.radians(127.693), math.radians(176.433), math.radians(118.042))))
        p72.append(Vector((0.5857, 0.1845, 2.3160)))

        single_hair(first_closed, first_simple, p70, p71, p72)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p73 = []
        p73.append(Vector((-0.0584, 0.5504, -0.0016)))
        p73.append(Vector((-0.0584, 0.0504, -0.0016)))
        p73.append(Vector((0.0382, -0.5043, -0.0233)))

        p74 = []
        p74.append(Vector((-0.0158, -0.8657, -0.0351)))
        p74.append(Vector((-0.4274, -1.1583, -0.4047)))
        p74.append(Vector((1.3194, -1.4521, 0.2662)))

        p75 = []
        p75.append(Vector((0.7418, 0.7418, 0.7418)))
        p75.append(Vector((math.radians(-52.3081), math.radians(-4.86421), math.radians(61.23))))
        p75.append(Vector((-0.6343, 0.1727, 2.2655)))

        single_hair(first_closed, first_simple, p73, p74, p75)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p76 = []
        p76.append(Vector((0.0179, 0.7227, -0.0060)))
        p76.append(Vector((0.0179, 0.2227, -0.0060)))
        p76.append(Vector((0.0179, -0.2773, -0.0060)))

        p77 = []
        p77.append(Vector((0.5621, -1.3456, -0.1422)))
        p77.append(Vector((1.3271, -1.0938, -0.6422)))
        p77.append(Vector((1.3271, -2.0938, -0.6422)))

        p78 = []
        p78.append(Vector((0.4744, 0.4744, 0.4744)))
        p78.append(Vector((math.radians(-28.6909), math.radians(-25.7711), math.radians(-77.1393))))
        p78.append(Vector((0.3204, 0.2343, 2.4867)))

        single_hair(first_closed, first_simple, p76, p77, p78)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p79 = []
        p79.append(Vector((0.2477, 0.5931, 0.1384)))
        p79.append(Vector((0.2477, 0.0931, 0.1384)))
        p79.append(Vector((0.1650, -0.5895, 0.1585)))

        p80 = []
        p80.append(Vector((0.6707, -1.0410, 0.1259)))
        p80.append(Vector((1.3271, -1.0938, -0.6422)))
        p80.append(Vector((1.3271, -2.0938, -0.6422)))

        p81 = []
        p81.append(Vector((0.3589, 0.3589, 0.2752)))
        p81.append(Vector((math.radians(-28.6909), math.radians(-25.7711), math.radians(-77.1393))))
        p81.append(Vector((0.1076, 0.2602, 2.4742)))

        single_hair(first_closed, first_simple, p79, p80, p81)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p82 = []
        p82.append(Vector((-0.0169, 0.7968, 0.0394)))
        p82.append(Vector((-0.0169, 0.2968, 0.0394)))
        p82.append(Vector((-0.0450, -0.2655, 0.0333)))

        p83 = []
        p83.append(Vector((0.0680, -1.0651, -0.3358)))
        p83.append(Vector((-0.2387, -1.7746, -0.2253)))
        p83.append(Vector((-0.3576, -2.9463, -0.3042)))

        p84 = []
        p84.append(Vector((0.3639, 0.3639, 0.3639)))
        p84.append(Vector((math.radians(-41.7185), math.radians(-6.19113), math.radians(2.36108))))
        p84.append(Vector((-0.1130, 0.4707, 2.3673)))


        single_hair(second_closed, second_simple, p82, p83, p84)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p85 = []
        p85.append(Vector((0.2515, 0.3951, 0.0131)))
        p85.append(Vector((0.2515, -0.1049, 0.0131)))
        p85.append(Vector((-0.0841, -0.1831, 0.0262)))

        p86 = []
        p86.append(Vector((-0.6717, -1.1148, 0.1115)))
        p86.append(Vector((0.3786, -1.3403, -0.5713)))
        p86.append(Vector((0.3786, -2.3403, -0.5713)))

        p87 = []
        p87.append(Vector((0.4816, 0.4816, 0.4816)))
        p87.append(Vector((math.radians(-29.9292), math.radians(50.0279), math.radians(-238.884))))
        p87.append(Vector((-0.5941, 0.0395, 2.3116)))

        single_hair(first_closed, first_simple, p85, p86, p87)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p88 = []
        p88.append(Vector((-0.1736, 0.6661, 0.1286)))
        p88.append(Vector((-0.1736, 0.1661, 0.1286)))
        p88.append(Vector((0.2300, 0.0189, 0.1193)))

        p89 = []
        p89.append(Vector((-0.0230, -1.0143, 0.2591)))
        p89.append(Vector((-0.7577, -1.2598, -0.1616)))
        p89.append(Vector((-0.7577, -2.2598, -0.1616)))

        p90 = []
        p90.append(Vector((0.3959, 0.3959, 0.3959)))
        p90.append(Vector((math.radians(6.36155), math.radians(-31.6429), math.radians(-114.103))))
        p90.append(Vector((0.1421, 0.1915, 2.5316)))

        single_hair(first_closed, first_simple, p88, p89, p90)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p91 = []
        p91.append(Vector((0.0615, 0.5667, 0.0008)))
        p91.append(Vector((0.0615, 0.0667, 0.0008)))
        p91.append(Vector((-0.2007, -0.2789, -0.1055)))

        p92 = []
        p92.append(Vector((-0.5017, -1.2215, -0.0277)))
        p92.append(Vector((0.5345, -1.2462, -0.5975)))
        p92.append(Vector((0.5345, -2.2462, -0.5975)))

        p93 = []
        p93.append(Vector((0.4816, 0.4816, 0.4816)))
        p93.append(Vector((math.radians(-29.9292), math.radians(50.0279), math.radians(-238.884))))
        p93.append(Vector((-0.6607, 0.1426, 2.2492)))

        single_hair(first_closed, first_simple, p91, p92, p93)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p94 = []
        p94.append(Vector((-0.1531, 0.7610, -0.0070)))
        p94.append(Vector((-0.1531, 0.2610, -0.0070)))
        p94.append(Vector((0.1182, -0.1815, 0.2609)))

        p95 = []
        p95.append(Vector((-0.2966, -1.0732, 0.0871)))
        p95.append(Vector((-0.8517, -1.3029, -0.2766)))
        p95.append(Vector((-0.8517, -2.3029, -0.2766)))

        p96 = []
        p96.append(Vector((0.3959, 0.3959, 0.3959)))
        p96.append(Vector((math.radians(6.36155), math.radians(-31.6429), math.radians(-114.103))))
        p96.append(Vector((0.1909, 0.2390, 2.5163)))

        single_hair(first_closed, first_simple, p94, p95, p96)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p97 = []
        p97.append(Vector((-0.1201, 0.4703, 0.0028)))
        p97.append(Vector((-0.1201, -0.0297, 0.0028)))
        p97.append(Vector((-0.0266, -1.0782, -0.1937)))

        p98 = []
        p98.append(Vector((-0.9290, -2.0856, -0.4948)))
        p98.append(Vector((-1.6136, -0.9386, -1.5717)))
        p98.append(Vector((-5.7472, -3.0651, -0.1708)))

        p99 = []
        p99.append(Vector((0.4437, 0.4437, 0.4437)))
        p99.append(Vector((math.radians(-52.8239), math.radians(-22.8763), math.radians(-84.4569))))
        p99.append(Vector((0.6686, 0.1220, 2.2496)))

        single_hair(first_closed, first_simple, p97, p98, p99)

        # Back right
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p101 = []
        p101.append(Vector((0.0271, 0.5293, -0.0573)))
        p101.append(Vector((0.0271, 0.0293, -0.0573)))
        p101.append(Vector((-0.0563, -0.6468, 0.0728)))

        p102 = []
        p102.append(Vector((-0.1209, -1.3892, -0.1598)))
        p102.append(Vector((-0.3842, -2.1772, -0.7909)))
        p102.append(Vector((-0.3842, -3.1772, -0.7909)))

        p103 = []
        p103.append(Vector((-0.7272, -0.4593, -0.5404)))
        p103.append(Vector((math.radians(-214.872), math.radians(59.2613), math.radians(-20.1133))))
        p103.append(Vector((0.6479, 0.1917, 2.2666)))

        single_hair(first_closed, first_simple, p101, p102, p103)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p104 = []
        p104.append(Vector((0.0188, 0.5111, -0.0453)))
        p104.append(Vector((0.0188, 0.0111, -0.0453)))
        p104.append(Vector((-0.0645, -0.6650, 0.0848)))

        p105 = []
        p105.append(Vector((-0.1277, -1.4113, -0.1295)))
        p105.append(Vector((-0.4092, -2.2100, -0.7169)))
        p105.append(Vector((-0.4092, -3.2100, -0.7169)))

        p106 = []
        p106.append(Vector((-0.6489, -0.4099, -0.4822)))
        p106.append(Vector((math.radians(-188.568), math.radians(66.54), math.radians(-348.9))))
        p106.append(Vector((0.6479, 0.1917, 2.2666)))

        single_hair(first_closed, first_simple, p104, p105, p106)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p107 = []
        p107.append(Vector((0.0188, 0.5111, -0.0453)))
        p107.append(Vector((0.0188, 0.0111, -0.0453)))
        p107.append(Vector((-0.0645, -0.6650, 0.0848)))

        p108 = []
        p108.append(Vector((-0.1587, -1.4075, -0.1862)))
        p108.append(Vector((-0.4401, -2.2062, -0.7736)))
        p108.append(Vector((-0.4401, -3.2062, -0.7736)))

        p109 = []
        p109.append(Vector((-0.7609, -0.4099, -0.4822)))
        p109.append(Vector((math.radians(-162.072), math.radians(61.5077), math.radians(-320.593))))
        p109.append(Vector((0.6479, 0.1917, 2.2666)))

        single_hair(first_closed, first_simple, p107, p108, p109)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p110 = []
        p110.append(Vector((0.0000, 0.5000, 0.0000)))
        p110.append(Vector((0.0000, 0.0000, 0.0000)))
        p110.append(Vector((-0.2271, -0.6299, 0.1434)))

        p111 = []
        p111.append(Vector((0.1426, -1.2316, -0.1622)))
        p111.append(Vector((-0.4527, -2.1513, -0.8559)))
        p111.append(Vector((-0.4527, -3.1513, -0.8559)))

        p112 = []
        p112.append(Vector((-0.5825, -0.5825, -0.5825)))
        p112.append(Vector((math.radians(-303.22), math.radians(133.817), math.radians(-96.2162))))
        p112.append(Vector((0.6207, 0.1853, 2.2795)))

        single_hair(first_closed, first_simple, p110, p111, p112)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p113 = []
        p113.append(Vector((0.2015, 0.3595, -0.0181)))
        p113.append(Vector((0.2015, -0.1405, -0.0181)))
        p113.append(Vector((-0.3121, -1.0408, -0.0157)))

        p114 = []
        p114.append(Vector((0.4206, -1.9544, -1.1306)))
        p114.append(Vector((0.0685, -1.5726, -1.1710)))
        p114.append(Vector((-0.3684, -0.7984, -1.0950)))

        p115 = []
        p115.append(Vector((-0.5879, -0.5194, -0.5279)))
        p115.append(Vector((math.radians(47.1674), math.radians(-212.421), math.radians(-84.787))))
        p115.append(Vector((0.5662, 0.3122, 2.2689)))

        single_hair(first_closed, first_simple, p113, p114, p115)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p116 = []
        p116.append(Vector((0.0770, 0.4525, -0.0348)))
        p116.append(Vector((0.0770, -0.0475, -0.0348)))
        p116.append(Vector((0.6716, -0.5717, -0.1215)))

        p117 = []
        p117.append(Vector((-0.4190, -0.7572, -0.5550)))
        p117.append(Vector((0.4346, -1.2668, -1.0000)))
        p117.append(Vector((10.9781, 5.2940, -14.3218)))

        p118 = []
        p118.append(Vector((0.8951, 0.8951, 0.8951)))
        p118.append(Vector((math.radians(-310.035), math.radians(18.4344), math.radians(100.412))))
        p118.append(Vector((0.6239, 0.1323, 2.3552)))


        single_hair(first_closed, first_simple, p116, p117, p118)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p119 = []
        p119.append(Vector((-0.9452, 0.2600, -0.3112)))
        p119.append(Vector((0.1250, -0.1273, -0.0112)))
        p119.append(Vector((0.8745, -0.2881, -0.0271)))

        p120 = []
        p120.append(Vector((0.1562, -0.9987, -0.7864)))
        p120.append(Vector((0.5462, -1.1581, -1.0067)))
        p120.append(Vector((-8.0963, 41.2850, -13.9451)))

        p121 = []
        p121.append(Vector((0.8951, 0.8951, 0.8951)))
        p121.append(Vector((math.radians(-315.056), math.radians(15.257), math.radians(96.7963))))
        p121.append(Vector((0.5566, 0.0782, 2.3976)))

        single_hair(first_closed, first_simple, p119, p120, p121)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p122 = []
        p122.append(Vector((-1.1233, 0.3495, -0.3047)))
        p122.append(Vector((-0.0531, -0.0379, -0.0047)))
        p122.append(Vector((0.7517, -0.1389, 0.1370)))

        p123 = []
        p123.append(Vector((0.4577, -0.6591, -0.4163)))
        p123.append(Vector((0.6297, -1.1172, -0.7693)))
        p123.append(Vector((-8.0128, 41.3258, -13.7077)))

        p124 = []
        p124.append(Vector((0.8951, 0.7366, 0.8951)))
        p124.append(Vector((math.radians(-310.035), math.radians(18.4344), math.radians(100.412))))
        p124.append(Vector((0.5896, 0.2154, 2.2944)))

        single_hair(first_closed, first_simple, p122, p123, p124)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p125 = []
        p125.append(Vector((-1.1779, 0.3219, -0.3197)))
        p125.append(Vector((-0.1077, -0.0655, -0.0197)))
        p125.append(Vector((0.7833, 0.3214, 0.0989)))

        p126 = []
        p126.append(Vector((0.6906, -0.5736, -0.4778)))
        p126.append(Vector((0.8869, -0.8584, -1.1703)))
        p126.append(Vector((-7.7556, 41.5846, -14.1086)))

        p127 = []
        p127.append(Vector((0.8871, 0.7602, 0.7422)))
        p127.append(Vector((math.radians(-310.035), math.radians(18.4344), math.radians(100.412))))
        p127.append(Vector((0.5896, 0.2154, 2.2944)))

        single_hair(first_closed, first_simple, p125, p126, p127)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p128 = []
        p128.append(Vector((0.6115, 1.1673, -0.3411)))
        p128.append(Vector((-0.0588, 0.0069, -0.0027)))
        p128.append(Vector((-0.3502, -0.4498, -0.0507)))

        p129 = []
        p129.append(Vector((-0.3943, -0.8327, -0.2463)))
        p129.append(Vector((-1.0837, -0.0602, -0.8994)))
        p129.append(Vector((-2.4244, -2.3810, -0.2225)))

        p130 = []
        p130.append(Vector((1.0000, 1.0000, 1.0000)))
        p130.append(Vector((math.radians(-32.463), math.radians(-43.6753), math.radians(247.942))))
        p130.append(Vector((0.5959, 0.1431, 2.3270)))

        single_hair(first_closed, first_simple, p128, p129, p130)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p131 = []
        p131.append(Vector((-0.0593, 0.4556, 0.0030)))
        p131.append(Vector((-0.0593, -0.0444, 0.0030)))
        p131.append(Vector((0.3236, -1.3809, -0.0297)))

        p132 = []
        p132.append(Vector((-0.6261, -0.6120, -1.0340)))
        p132.append(Vector((-1.0458, -0.5055, -1.1922)))
        p132.append(Vector((-2.0136, -3.3859, -0.4393)))

        p133 = []
        p133.append(Vector((0.8909, 0.8909, 0.8909)))
        p133.append(Vector((math.radians(-14.3799), math.radians(-51.0298), math.radians(-136.727))))
        p133.append(Vector((0.6121, 0.1260, 2.3174)))

        single_hair(first_closed, first_simple, p131, p132, p133)

        # Back left
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p134 = []
        p134.append(Vector((0.0064, 0.5077, -0.0299)))
        p134.append(Vector((0.0064, 0.0077, -0.0299)))
        p134.append(Vector((-0.0770, -0.6685, 0.1001)))

        p135 = []
        p135.append(Vector((-0.4191, -1.3637, -0.6201)))
        p135.append(Vector((-0.4274, -1.7620, -1.3090)))
        p135.append(Vector((-0.4274, -2.7620, -1.3090)))

        p136 = []
        p136.append(Vector((0.7272, 0.4593, 0.5404)))
        p136.append(Vector((math.radians(-426.918), math.radians(-46.4359), math.radians(40.2805))))
        p136.append(Vector((-0.6974, 0.1334, 2.2337)))

        single_hair(first_closed, first_simple, p134, p135, p136)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p137 = []
        p137.append(Vector((0.0000, 0.5000, 0.0000)))
        p137.append(Vector((0.0000, 0.0000, 0.0000)))
        p137.append(Vector((-0.0833, -0.6761, 0.1301)))

        p138 = []
        p138.append(Vector((-0.1360, -1.3982, -0.1236)))
        p138.append(Vector((-0.3842, -2.1772, -0.7909)))
        p138.append(Vector((-0.3842, -3.1772, -0.7909)))

        p139 = []
        p139.append(Vector((0.7272, 0.4593, 0.5404)))
        p139.append(Vector((math.radians(-370.541), math.radians(-62.9769), math.radians(-6.2589))))
        p139.append(Vector((-0.6833, 0.1269, 2.2337)))

        single_hair(first_closed, first_simple, p137, p138, p139)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p140 = []
        p140.append(Vector((-0.0069, 0.5219, 0.0075)))
        p140.append(Vector((-0.0069, 0.0219, 0.0075)))
        p140.append(Vector((-0.0902, -0.6542, 0.1376)))

        p141 = []
        p141.append(Vector((-0.1093, -1.7260, -0.2722)))
        p141.append(Vector((-0.4919, -2.4882, -0.8762)))
        p141.append(Vector((-0.4919, -3.4882, -0.8762)))

        p142 = []
        p142.append(Vector((0.6897, 0.4356, 0.5126)))
        p142.append(Vector((math.radians(-325.327), math.radians(-61.0986), math.radians(-60.0009))))
        p142.append(Vector((-0.6634, 0.1334, 2.2337)))

        single_hair(first_closed, first_simple, p140, p141, p142)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p143 = []
        p143.append(Vector((-0.0089, 0.5156, -0.0126)))
        p143.append(Vector((-0.0089, 0.0156, -0.0126)))
        p143.append(Vector((-0.0922, -0.6605, 0.1174)))

        p144 = []
        p144.append(Vector((-0.0753, -1.2845, -0.1790)))
        p144.append(Vector((-0.4527, -2.1513, -0.8559)))
        p144.append(Vector((-0.4527, -3.1513, -0.8559)))

        p145 = []
        p145.append(Vector((0.5825, 0.5825, 0.5825)))
        p145.append(Vector((math.radians(-303.22), math.radians(-46.1825), math.radians(-83.7838))))
        p145.append(Vector((-0.6763, 0.1347, 2.2357)))

        single_hair(first_closed, first_simple, p143, p144, p145)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p146 = []
        p146.append(Vector((0.1949, 0.3598, -0.0276)))
        p146.append(Vector((0.1949, -0.1402, -0.0276)))
        p146.append(Vector((-0.0998, -1.1095, 0.0644)))

        p147 = []
        p147.append(Vector((0.4229, -1.7067, -1.1636)))
        p147.append(Vector((-0.0574, -1.4227, -1.2145)))
        p147.append(Vector((0.0698, -2.3635, -1.0603)))

        p148 = []
        p148.append(Vector((0.5879, 0.5194, 0.5279)))
        p148.append(Vector((math.radians(47.1674), math.radians(-392.421), math.radians(-95.213))))
        p148.append(Vector((-0.6218, 0.2616, 2.2251)))

        single_hair(first_closed, first_simple, p146, p147, p148)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p149 = []
        p149.append(Vector((0.0795, 0.4626, -0.0456)))
        p149.append(Vector((0.0795, -0.0374, -0.0456)))
        p149.append(Vector((0.6483, -0.3678, -0.0759)))

        p150 = []
        p150.append(Vector((-0.1681, -0.6361, -0.3667)))
        p150.append(Vector((0.3276, -1.0642, -0.9238)))
        p150.append(Vector((10.8711, 5.4966, -14.2456)))

        p151 = []
        p151.append(Vector((-0.8951, -0.8951, -0.8951)))
        p151.append(Vector((math.radians(-310.035), math.radians(-161.566), math.radians(79.5881))))
        p151.append(Vector((-0.6840, 0.0593, 2.3200)))

        single_hair(first_closed, first_simple, p149, p150, p151)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p152 = []
        p152.append(Vector((-0.9482, 0.2468, -0.3127)))
        p152.append(Vector((0.1220, -0.1406, -0.0127)))
        p152.append(Vector((0.8474, -0.3475, -0.0227)))

        p153 = []
        p153.append(Vector((0.2448, -0.7827, -0.5470)))
        p153.append(Vector((0.5139, -1.1123, -0.9120)))
        p153.append(Vector((-8.1285, 41.3308, -13.8504)))

        p154 = []
        p154.append(Vector((-0.8951, -0.8951, -0.8951)))
        p154.append(Vector((math.radians(-312.48), math.radians(-164.088), math.radians(82.4942))))
        p154.append(Vector((-0.6093, 0.0489, 2.3571)))

        single_hair(first_closed, first_simple, p152, p153, p154)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p155 = []
        p155.append(Vector((-1.1313, -0.1668, -0.3173)))
        p155.append(Vector((-0.0611, -0.5541, -0.0173)))
        p155.append(Vector((0.8978, -0.0798, -0.0138)))

        p156 = []
        p156.append(Vector((0.2990, -1.9929, -0.8967)))
        p156.append(Vector((0.6606, -2.0583, -1.1252)))
        p156.append(Vector((-11.4108, 36.3486, -15.5021)))

        p157 = []
        p157.append(Vector((-0.8904, -0.4703, -0.7315)))
        p157.append(Vector((math.radians(-312.48), math.radians(-164.088), math.radians(82.4942))))
        p157.append(Vector((-0.5012, 0.1800, 2.4095)))

        single_hair(first_closed, first_simple, p155, p156, p157)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        p158 = []
        p158.append(Vector((0.0366, 0.5602, -0.0023)))
        p158.append(Vector((0.0366, 0.0602, -0.0023)))
        p158.append(Vector((-0.4511, -0.8720, 0.0319)))

        p159 = []
        p159.append(Vector((0.8289, -0.6120, -0.8296)))
        p159.append(Vector((0.9804, -0.4977, -0.9051)))
        p159.append(Vector((3.4816, -9.6984, 1.4162)))

        p160 = []
        p160.append(Vector((0.9243, 0.9243, 0.9243)))
        p160.append(Vector((math.radians(188.473), math.radians(-235.744), math.radians(-11.7521))))
        p160.append(Vector((-0.6541, 0.1730, 2.2412)))

        single_hair(first_closed, first_simple, p158, p159, p160)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
        
        # Additional front
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
        if bpy.data.scenes["Scene"].my_tool.my_bool == True:
            
            p161 = []
            p161.append(Vector((0.3169, 0.0025, -0.0872)))
            p161.append(Vector((0.1410, 0.0586, -0.0603)))
            p161.append(Vector((-0.2409, -0.4803, 0.5225)))

            p162 = []
            p162.append(Vector((-0.4390, -2.1399, 0.0453)))
            p162.append(Vector((1.0113, -2.4868, -1.8770)))
            p162.append(Vector((0.0931, 0.6328, 0.0821)))

            p163 = []
            p163.append(Vector((0.1846, 0.3067, 0.3074)))
            p163.append(Vector((math.radians(-163.656), math.radians(161.232), math.radians(-219.988))))
            p163.append(Vector((-0.0343, -1.0126, 2.4249)))
            
            single_hair(first_closed, first_simple, p161, p162, p163)
            
            #
        
            p164 = []
            p164.append(Vector((0.3169, 0.0025, -0.0872)))
            p164.append(Vector((0.1410, 0.0586, -0.0603)))
            p164.append(Vector((-0.0022, -0.2148, 0.2673)))

            p165 = []
            p165.append(Vector((-0.7367, -2.2122, 0.1985)))
            p165.append(Vector((0.4327, -2.7988, -1.7309)))
            p165.append(Vector((0.0287, 0.5718, -0.0055)))

            p166 = []
            p166.append(Vector((0.1846, 0.3067, 0.3074)))
            p166.append(Vector((math.radians(-148.388), math.radians(180.073), math.radians(-173.015))))
            p166.append(Vector((-0.0599, -1.0274, 2.4372)))

            single_hair(first_closed, first_simple, p164, p165, p166)
            
            #
            
            p167 = []
            p167.append(Vector((0.2491, -0.0080, 0.0340)))
            p167.append(Vector((0.0732, 0.0481, 0.0609)))
            p167.append(Vector((-0.3642, -0.8414, 0.3606)))

            p168 = []
            p168.append(Vector((-0.8876, -1.8752, -0.8799)))
            p168.append(Vector((-0.0104, -1.7644, -2.9284)))
            p168.append(Vector((-0.9286, 1.3553, -0.9692)))

            p169 = []
            p169.append(Vector((0.1846, 0.3067, 0.3074)))
            p169.append(Vector((math.radians(-188.614), math.radians(173.54), math.radians(-73.7553))))
            p169.append(Vector((0.2352, -1.0153, 2.4356)))

            single_hair(first_closed, first_simple, p167, p168, p169)
            
        if bpy.data.scenes["Scene"].my_tool2.my_bool2 == True:
            
            p170 = []
            p170.append(Vector((-0.9231, 0.2994, -0.4048)))
            p170.append(Vector((0.1471, -0.0879, -0.1048)))
            p170.append(Vector((0.2081, -0.1190, 0.4254)))

            p171 = []
            p171.append(Vector((0.4735, -0.8781, -0.1278)))
            p171.append(Vector((0.8635, -1.0375, -0.3481)))
            p171.append(Vector((-7.7790, 41.4056, -13.2865)))

            p172 = []
            p172.append(Vector((1.5166, 0.8951, 0.8951)))
            p172.append(Vector((math.radians(-315.056), math.radians(15.257), math.radians(96.7963))))
            p172.append(Vector((0.5566, 0.0782, 2.3976)))

            single_hair(first_closed, first_simple, p170, p171, p172)
            #
            
            p173 = []
            p173.append(Vector((-0.9231, 0.2994, -0.4048)))
            p173.append(Vector((0.1471, -0.0879, -0.1048)))
            p173.append(Vector((0.2081, -0.1190, 0.4254)))

            p174 = []
            p174.append(Vector((0.4735, -0.8781, -0.1278)))
            p174.append(Vector((0.8635, -1.0375, -0.3481)))
            p174.append(Vector((-7.7790, 41.4056, -13.2865)))

            p175 = []
            p175.append(Vector((-1.5166, -0.8951, -0.8951)))
            p175.append(Vector((math.radians(-315.056), math.radians(-164.743), math.radians(83.2037))))
            p175.append(Vector((-0.6381, -0.0512, 2.3923)))

            single_hair(first_closed, first_simple, p173, p174, p175)     
            
        if bpy.data.scenes["Scene"].my_tool3.my_bool3 == True:
            
            p176 = []
            p176.append(Vector((-0.9164, 0.2838, -0.4204)))
            p176.append(Vector((0.1538, -0.1035, -0.1204)))
            p176.append(Vector((0.1894, -0.0284, 0.8390)))

            p177 = []
            p177.append(Vector((0.1879, -1.4542, -0.6031)))
            p177.append(Vector((1.4584, -2.0513, -1.3051)))
            p177.append(Vector((-9.9344, 19.5093, -25.8692)))

            p178 = []
            p178.append(Vector((-1.0091, -1.1157, -1.1157)))
            p178.append(Vector((math.radians(-315.056), math.radians(-164.743), math.radians(83.2037))))
            p178.append(Vector((-0.6218, 0.0085, 2.3546)))
            
            single_hair(first_closed, first_simple, p176, p177, p178)  
                    
            #        
            
            p179 = []
            p179.append(Vector((-0.9164, 0.2838, -0.4204)))
            p179.append(Vector((0.1538, -0.1035, -0.1204)))
            p179.append(Vector((0.4550, -0.0032, 0.9063)))

            p180 = []
            p180.append(Vector((-0.0484, -1.6420, -0.5022)))
            p180.append(Vector((1.4584, -2.0513, -1.3051)))
            p180.append(Vector((-9.9344, 19.5093, -25.8692)))

            p181 = []
            p181.append(Vector((1.1874, 1.3128, 1.3128)))
            p181.append(Vector((math.radians(-315.056), math.radians(15.257), math.radians(96.7963))))
            p181.append(Vector((0.5566, -0.0489, 2.3976)))

            single_hair(first_closed, first_simple, p179, p180, p181)  

                   
        return {'FINISHED'}

class panel1(bpy.types.Panel):
    bl_idname = "panel.panel1"
    bl_label = "Anime Hair"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_category = "Anime Hair"

    def draw(self, context):
        scene = context.scene
        my_tool = scene.my_tool
        my_tool2 = scene.my_tool2
        my_tool3 = scene.my_tool3
        self.layout.prop(my_tool, "my_bool")
        self.layout.prop(my_tool2, "my_bool2")
        self.layout.prop(my_tool3, "my_bool3")
        self.layout.operator(generate.bl_idname, icon='MESH_CUBE', text="Generate")

addon_keymaps = []

def register() :
    bpy.utils.register_class(generate)
    bpy.utils.register_class(panel1)
    bpy.utils.register_class(X1)
    bpy.utils.register_class(X2)
    bpy.utils.register_class(X3)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=X1)
    bpy.types.Scene.my_tool2 = bpy.props.PointerProperty(type=X2)
    bpy.types.Scene.my_tool3 = bpy.props.PointerProperty(type=X3)
   
def unregister() :
    bpy.utils.unregister_class(generate)
    bpy.utils.unregister_class(panel1)
    bpy.utils.register_class(X1)
    bpy.utils.register_class(X2)
    bpy.utils.register_class(X3)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=X1)
    bpy.types.Scene.my_tool2 = bpy.props.PointerProperty(type=X2)
    bpy.types.Scene.my_tool3 = bpy.props.PointerProperty(type=X3)
   
if __name__ == "__main__" :
    register()
