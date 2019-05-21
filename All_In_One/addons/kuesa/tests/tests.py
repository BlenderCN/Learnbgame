# tests.py
#
# This file is part of Kuesa.
#
# Copyright (C) 2018 Klarälvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Paul Lemire <paul.lemire@kdab.com>
#
# Licensees holding valid proprietary KDAB Kuesa licenses may use this file in
# accordance with the Kuesa Enterprise License Agreement provided with the Software in the
# LICENSE.KUESA.ENTERPRISE file.
#
# Contact info@kdab.com if any conditions of this licensing are not clear to you.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import os
import json
import unittest
import bpy
# Blender's Python interpreter doesn't use PYTHONPATH and doesn't look for packages/modules
# in the current repository
# We therefore need to resolve our module's path manually
dir = os.path.dirname(sys.argv[sys.argv.index("--") + 1])
sys.path.append(dir) # Kuesa plugin path
from kuesa.Layers.layermanager import LayerManager
import kuesa
import kuesa_exporter

class TestLayerManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        kuesa.register()
        # Remove any blender data previously created
        bpy.ops.wm.read_factory_settings(use_empty=True)

    @classmethod
    def tearDownClass(cls):
        kuesa.unregister()

    def test_has_kuesa_layer_property(self):
        # GIVEN
        obj = {}
        layer_manager = LayerManager(bpy.context)
        res = layer_manager.has_kuesa_layers_property(obj)

        # THEN
        self.assertFalse(res)

        # WHEN
        obj_data = bpy.data.meshes.new("tst_has_kuesa_layer_property_mesh")
        obj = bpy.data.objects.new(name="tst_has_kuesa_layer_property", object_data=obj_data)
        bpy.context.scene.objects.link(obj)
        res = layer_manager.has_kuesa_layers_property(obj)

        # THEN
        self.assertFalse(res)

        # WHEN
        obj.kuesa.__init__()
        obj.kuesa.layers.add()
        res = layer_manager.has_kuesa_layers_property(obj)
        print(obj.keys())
        print(obj.kuesa.keys())

        # THEN
        self.assertTrue(res)

    def test_gather_layer_names(self):
        # GIVEN
        layer_manager = LayerManager(bpy.context)
        obj_data = bpy.data.meshes.new("test_gather_layer_names_mesh")
        obj = bpy.data.objects.new(name="test_gather_layer_names", object_data=obj_data)

        # WHEN
        names = layer_manager.gather_layer_names(obj)

        # THEN
        self.assertEqual(len(names), 0)

        # WHEN
        layer_manager.add(["layer1"], obj)
        names = layer_manager.gather_layer_names(obj)

        # THEN
        self.assertEqual(len(names), 1)
        self.assertIn("layer1", names)

        # WHEN
        layer_manager.add(["layer2"], obj)
        names = layer_manager.gather_layer_names(obj)

        # THEN
        self.assertEqual(len(names), 2)
        self.assertIn("layer1", names)
        self.assertIn("layer2", names)

    def test_add_layer(self):
        # GIVEN
        layer_manager = LayerManager(bpy.context)
        obj_data = bpy.data.meshes.new("test_add_layer_mesh")
        obj = bpy.data.objects.new(name="test_add_layer", object_data=obj_data)
        bpy.context.scene.objects.link(obj)
        obj.select = False

        # WHEN
        layer_manager.add(["layer_add"])

        # THEN
        self.assertEqual(len(layer_manager.gather_layer_names(obj)), 0)

        # WHEN
        obj.select = True
        layer_manager.add(["layer_add"])

        # THEN
        self.assertEqual(len(obj.kuesa.layers), 1)
        self.assertEqual(obj.kuesa.layers[0].name, "layer_add")

        # WHEN
        layer_manager.add(["layer_add"])

        # THEN
        self.assertEqual(len(obj.kuesa.layers), 1)


    def test_sub_layer(self):
        # GIVEN
        layer_manager = LayerManager(bpy.context)
        obj_data = bpy.data.meshes.new("test_sub_layer_mesh")
        obj = bpy.data.objects.new(name="test_sub_layer", object_data=obj_data)
        bpy.context.scene.objects.link(obj)
        obj.select = True

        # WHEN
        layer_manager.add(["layer_sub_1", "layer_sub_2", "layer_sub_3"])

        # THEN
        self.assertEqual(len(obj.kuesa.layers), 3)

        # WHEN
        layer_manager.sub(["layer_sub_2", "layer_sub_3"])

        # THEN
        self.assertEqual(len(obj.kuesa.layers), 1)
        self.assertEqual(obj.kuesa.layers[0].name, "layer_sub_1")

        # WHEN
        layer_manager.sub(["layer_sub_1"])

        # THEN
        self.assertEqual(len(obj.kuesa.layers), 0)


    def test_rename_layer(self):
        # GIVEN
        layer_manager = LayerManager(bpy.context)
        obj_data = bpy.data.meshes.new("test_rename_layer_mesh")
        obj1 = bpy.data.objects.new(name="test_rename_layer_1", object_data=obj_data)
        obj2 = bpy.data.objects.new(name="test_rename_layer_2", object_data=obj_data)
        bpy.context.scene.objects.link(obj1)
        bpy.context.scene.objects.link(obj2)
        obj1.select = True
        obj2.select = True

        # WHEN
        layer_manager.add(["layer_rename"])

        # THEN
        self.assertEqual(len(obj1.kuesa.layers), 1)
        self.assertEqual(len(obj2.kuesa.layers), 1)
        self.assertEqual(obj1.kuesa.layers[0].name, "layer_rename")
        self.assertEqual(obj2.kuesa.layers[0].name, "layer_rename")

        # WHEN
        layer_manager.rename("layer_rename", "layer_renamed_1")

        # THEN
        self.assertEqual(len(obj1.kuesa.layers), 1)
        self.assertEqual(len(obj2.kuesa.layers), 1)
        self.assertEqual(obj1.kuesa.layers[0].name, "layer_renamed_1")
        self.assertEqual(obj2.kuesa.layers[0].name, "layer_renamed_1")

        # WHEN
        obj1.select = False
        layer_manager.rename("layer_renamed_1", "layer_renamed_2")

        # THEN
        self.assertEqual(len(obj1.kuesa.layers), 1)
        self.assertEqual(len(obj2.kuesa.layers), 1)
        self.assertEqual(obj1.kuesa.layers[0].name, "layer_renamed_2")
        self.assertEqual(obj2.kuesa.layers[0].name, "layer_renamed_2")

    def test_meets_union(self):
        # Union as in at least one object contains a layer
        # GIVEN
        layer_manager = LayerManager(bpy.context)
        obj_data = bpy.data.meshes.new("test_meets_union_mesh")
        obj = bpy.data.objects.new(name="test_meets_union", object_data=obj_data)
        bpy.context.scene.objects.link(obj)
        obj.select = True

        # WHEN
        layer_manager.add(["layer_meets_union_1", "layer_meets_union_2", "layer_meets_union_3"])

        # THEN
        self.assertEqual(len(obj.kuesa.layers), 3)

        # WHEN
        check = layer_manager.meets_union("layer_meets_union_1")

        # THEN
        self.assertTrue(check)

        # WHEN
        check = layer_manager.meets_union("layer_meets_union_2")

        # THEN
        self.assertTrue(check)

        # WHEN
        check = layer_manager.meets_union("layer_meets_union_3")

        # THEN
        self.assertTrue(check)

        # WHEN
        check = layer_manager.meets_union("layer_meets_union_4")

        # THEN
        self.assertFalse(check)

    def test_meets_intersect(self):
        # Intersect as in a layer must be defined in each objects

        # GIVEN
        layer_manager = LayerManager(bpy.context)
        obj_data = bpy.data.meshes.new("test_meets_intersect_mesh")
        obj1 = bpy.data.objects.new(name="test_meets_intersect_1", object_data=obj_data)
        obj2 = bpy.data.objects.new(name="test_meets_intersect_2", object_data=obj_data)
        bpy.context.scene.objects.link(obj1)
        bpy.context.scene.objects.link(obj2)
        bpy.ops.object.select_all(action='DESELECT')

        # THEN
        self.assertEqual(len(bpy.context.selected_objects), 0)

        # WHEN
        obj1.select = True
        obj2.select = False
        layer_manager.add(["layer_meets_intersect_1", "layer_meets_intersect_2"])

        obj2.select = True
        obj1.select = False
        layer_manager.add(["layer_meets_intersect_1", "layer_meets_intersect_3"])

        # THEN
        self.assertEqual(len(obj1.kuesa.layers), 2)
        self.assertEqual(len(obj2.kuesa.layers), 2)

        # WHEN
        obj1.select = True
        obj2.select = True
        check = layer_manager.meets_intersect("layer_meets_intersect_1")

        # THEN
        self.assertTrue(check)

        # WHEN
        check = layer_manager.meets_intersect("layer_meets_intersect_2")

        # THEN
        self.assertFalse(check)

        # WHEN
        check = layer_manager.meets_intersect("layer_meets_intersect_3")

        # THEN
        self.assertFalse(check)

        # WHEN
        obj1.select = False
        check = layer_manager.meets_intersect("layer_meets_intersect_3")

        # THEN
        self.assertTrue(check)


    def test_select_match_one(self):
        # GIVEN
        layer_manager = LayerManager(bpy.context)
        obj_data = bpy.data.meshes.new("test_select_match_one_mesh")
        obj1 = bpy.data.objects.new(name="test_select_match_one_1", object_data=obj_data)
        obj2 = bpy.data.objects.new(name="test_select_match_one_2", object_data=obj_data)
        bpy.context.scene.objects.link(obj1)
        bpy.context.scene.objects.link(obj2)
        bpy.ops.object.select_all(action='DESELECT')

        # THEN
        self.assertEqual(len(bpy.context.selected_objects), 0)

        # WHEN
        obj1.select = True
        obj2.select = False
        layer_manager.add(["layer_select_match_one_1", "layer_select_match_one_2"])

        obj2.select = True
        obj1.select = False
        layer_manager.add(["layer_select_match_one_1", "layer_select_match_one_3"])

        # THEN
        self.assertEqual(len(obj1.kuesa.layers), 2)
        self.assertEqual(len(obj2.kuesa.layers), 2)

        # WHEN
        obj1.select = False
        obj2.select = False
        layer_manager.select_match_one(["layer_select_match_one_1"])

        # THEN
        self.assertTrue(obj1.select)
        self.assertTrue(obj2.select)

        # WHEN
        obj1.select = False
        obj2.select = False
        layer_manager.select_match_one(["layer_select_match_one_2"])

        # THEN
        self.assertTrue(obj1.select)
        self.assertFalse(obj2.select)

        # WHEN
        obj1.select = False
        obj2.select = False
        layer_manager.select_match_one(["layer_select_match_one_3"])

        # THEN
        self.assertTrue(obj2.select)
        self.assertFalse(obj1.select)

        # WHEN
        obj1.select = False
        obj2.select = False
        layer_manager.select_match_one(["layer_select_match_one_2", "layer_select_match_one_3"])

        # THEN
        self.assertTrue(obj1.select)
        self.assertTrue(obj2.select)

    def test_select_match_all(self):
        # GIVEN
        layer_manager = LayerManager(bpy.context)
        obj_data = bpy.data.meshes.new("test_select_match_all_mesh")
        obj1 = bpy.data.objects.new(name="test_select_match_all_1", object_data=obj_data)
        obj2 = bpy.data.objects.new(name="test_select_match_all_2", object_data=obj_data)
        bpy.context.scene.objects.link(obj1)
        bpy.context.scene.objects.link(obj2)
        bpy.ops.object.select_all(action='DESELECT')

        # THEN
        self.assertEqual(len(bpy.context.selected_objects), 0)

        # WHEN
        obj1.select = True
        obj2.select = False
        layer_manager.add(["layer_select_match_all_1", "layer_select_match_all_2"])

        obj2.select = True
        obj1.select = False
        layer_manager.add(["layer_select_match_all_1", "layer_select_match_all_3"])

        # THEN
        self.assertEqual(len(obj1.kuesa.layers), 2)
        self.assertEqual(len(obj2.kuesa.layers), 2)

        # WHEN
        obj1.select = False
        obj2.select = False
        layer_manager.select_match_all(["layer_select_match_all_1"])

        # THEN
        self.assertTrue(obj1.select)
        self.assertTrue(obj2.select)

        # WHEN
        obj1.select = False
        obj2.select = False
        layer_manager.select_match_all(["layer_select_match_all_2"])

        # THEN
        self.assertTrue(obj1.select)
        self.assertFalse(obj2.select)

        # WHEN
        obj1.select = False
        obj2.select = False
        layer_manager.select_match_all(["layer_select_match_all_3"])

        # THEN
        self.assertTrue(obj2.select)
        self.assertFalse(obj1.select)

        # WHEN
        obj1.select = False
        obj2.select = False
        layer_manager.select_match_all(["layer_select_match_all_2", "layer_select_match_all_3"])

        # THEN
        self.assertFalse(obj1.select)
        self.assertFalse(obj2.select)


class TestLayerAndGLTFExport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Register GLTF Exporter
        kuesa_exporter.register()
        # Register Kuesa Plugin
        kuesa.register()
        # Remove any blender data previously created
        bpy.ops.wm.read_factory_settings(use_empty=True)

    @classmethod
    def tearDownClass(cls):
        # Unregister GLTF Exporter
        kuesa_exporter.unregister()
        # Unregister Kuesa Plugin
        kuesa.unregister()


    def test_gltf_with_layer_export(self):

        # GIVEN
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.object

        # WHEN
        bpy.context.scene.kuesa_layers.current_layer_name = "layer_gltf_with_layer_export"
        bpy.ops.kuesa_layers.new_layer()

        # THEN
        self.assertEqual(len(bpy.context.scene.kuesa_layers.layer_names_list), 1)
        self.assertEqual(bpy.context.scene.kuesa_layers.layer_names_list[0].name, "layer_gltf_with_layer_export")
        self.assertEqual(len(obj.kuesa.layers), 1)
        self.assertEqual(obj.kuesa.layers[0].name, "layer_gltf_with_layer_export")

        # WHEN
        gltf_file_name = "./test_gltf_with_layer_export.gltf"
        buffer_file_name = "./test_gltf_with_layer_export.bin"
        bpy.ops.export_scene.gltf(filepath=gltf_file_name, export_selected=True)
        gltf = open(gltf_file_name, 'r')

        # THEN
        self.assertFalse(gltf.closed)

        # WHEN
        gltf_json = json.load(gltf)

        # Cleanup
        gltf.close()
        os.remove(gltf_file_name)
        os.remove(buffer_file_name)

        # THEN
        self.assertTrue("extensions" in gltf_json)
        extension_json = gltf_json["extensions"]
        self.assertTrue("KDAB_Kuesa_Layers" in extension_json)
        self.assertTrue("layers" in extension_json["KDAB_Kuesa_Layers"])
        exporter_layers = extension_json["KDAB_Kuesa_Layers"]["layers"]
        self.assertEqual(len(exporter_layers), 1)
        self.assertEqual(exporter_layers[0], "layer_gltf_with_layer_export")

        self.assertTrue("nodes" in gltf_json)
        nodes = gltf_json["nodes"]
        self.assertEqual(len(nodes), 1)
        exported_obj = nodes[0]
        self.assertTrue("extensions" in exported_obj)
        self.assertTrue("KDAB_Kuesa_Layers" in exported_obj["extensions"])
        self.assertTrue("layers" in exported_obj["extensions"]["KDAB_Kuesa_Layers"])
        exported_node_layers = exported_obj["extensions"]["KDAB_Kuesa_Layers"]["layers"]
        self.assertEqual(len(exported_node_layers), 1)
        self.assertEqual(exported_node_layers[0], 0)

class TestTriangleGLTFExport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Register GLTF Exporter
        kuesa_exporter.register()
        # Register Kuesa Plugin
        kuesa.register()
        # Remove any blender data previously created
        bpy.ops.wm.read_factory_settings(use_empty=True)

    @classmethod
    def tearDownClass(cls):
        # Unregister GLTF Exporter
        kuesa_exporter.unregister()
        # Unregister Kuesa Plugin
        kuesa.unregister()

    def test_wireframe_export(self):
        # GIVEN
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.object

        # WHEN
        gltf_file_name = "./test_gltf_triangle_export.gltf"
        buffer_file_name = "./test_gltf_triangle_export.bin"
        bpy.ops.export_scene.gltf(filepath=gltf_file_name, export_selected=True)
        gltf = open(gltf_file_name, 'r')

        # THEN
        self.assertFalse(gltf.closed)

        # WHEN
        gltf_json = json.load(gltf)

        # Cleanup
        gltf.close()
        os.remove(gltf_file_name)
        os.remove(buffer_file_name)

        # THEN
        self.assertTrue("meshes" in gltf_json)
        self.assertTrue("bufferViews" in gltf_json)

        self.assertEqual(len(gltf_json["meshes"]), 1)
        mesh = gltf_json["meshes"][0]
        self.assertEqual(len(mesh["primitives"]), 1);
        primitive = mesh["primitives"][0]

        # check we are using GL_TRIANGLES
        if "mode" in primitive:
            self.assertEqual(primitive["mode"], 4)

        # check number of entries in index buffer matches lines
        indexBufferIndex = primitive["indices"]
        self.assertTrue(indexBufferIndex < len(gltf_json["accessors"]))
        indexAccessor = gltf_json["accessors"][indexBufferIndex]
        # 6 faces of 2 triangles, a triangle is 3 indices
        self.assertEqual(indexAccessor["count"], 6 * 2 * 3)

class TestWireframeGLTFExport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Register GLTF Exporter
        kuesa_exporter.register()
        # Register Kuesa Plugin
        kuesa.register()
        # Remove any blender data previously created
        bpy.ops.wm.read_factory_settings(use_empty=True)
        # Enable wireframe export property to False
        bpy.types.settings_KDAB_Kuesa_FaceWireframe.export_face_wireframe = True

    @classmethod
    def tearDownClass(cls):
        # Unregister GLTF Exporter
        kuesa_exporter.unregister()
        # Unregister Kuesa Plugin
        kuesa.unregister()
        # Restore wireframe export property to False
        bpy.types.settings_KDAB_Kuesa_FaceWireframe.export_face_wireframe = False

    def test_wireframe_export(self):

        # GIVEN
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.object

        # WHEN
        gltf_file_name = "./test_gltf_wireframe_export.gltf"
        buffer_file_name = "./test_gltf_wireframe_export.bin"
        bpy.ops.export_scene.gltf(filepath=gltf_file_name, export_selected=True)
        gltf = open(gltf_file_name, 'r')

        # THEN
        self.assertFalse(gltf.closed)

        # WHEN
        gltf_json = json.load(gltf)

        # Cleanup
        gltf.close()
        os.remove(gltf_file_name)
        os.remove(buffer_file_name)

        # THEN
        self.assertTrue("meshes" in gltf_json)
        self.assertTrue("bufferViews" in gltf_json)

        self.assertEqual(len(gltf_json["meshes"]), 1)
        mesh = gltf_json["meshes"][0]
        self.assertEqual(len(mesh["primitives"]), 1);
        primitive = mesh["primitives"][0]

        # check we are using GL_LINES
        self.assertEqual(primitive["mode"], 1)

        # check number of entries in index buffer matches lines
        indexBufferIndex = primitive["indices"]
        self.assertTrue(indexBufferIndex < len(gltf_json["accessors"]))
        indexAccessor = gltf_json["accessors"][indexBufferIndex]
        # 6 faces of 4 lines, a line is two indices
        self.assertEqual(indexAccessor["count"], 6 * 4 * 2)

class TestAnimationExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Register GLTF Exporter
        kuesa_exporter.register()
        # Register Kuesa Plugin
        kuesa.register()
        # Remove any blender data previously created
        bpy.ops.wm.read_factory_settings(use_empty=True)

    @classmethod
    def tearDownClass(cls):
        # Unregister GLTF Exporter
        kuesa_exporter.unregister()
        # Unregister Kuesa Plugin
        kuesa.unregister()

    def test_no_animation_export(self):
        # GIVEN
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.object

        # Create animation
        obj_do = bpy.data.objects[obj.name]
        bpy.ops.screen.frame_jump(end=False)
        bpy.context.scene.frame_set(1)
        obj_do.location = (0, 0, 0)
        obj_do.keyframe_insert(data_path="location", index=-1)
        bpy.context.scene.frame_set(100)
        obj_do.location = (10, 10, 10)
        obj_do.keyframe_insert(data_path="location", index=-1)
        bpy.ops.screen.frame_jump(end=False)

        # WHEN
        gltf_file_name = "./test_gltf_animation_export.gltf"
        buffer_file_name = "./test_gltf_animation_export.bin"
        bpy.ops.export_scene.gltf(filepath=gltf_file_name, export_selected=True, export_animations=False)
        gltf = open(gltf_file_name, 'r')

        # THEN
        self.assertFalse(gltf.closed)

        # WHEN
        gltf_json = json.load(gltf)

        # Cleanup
        gltf.close()
        os.remove(gltf_file_name)
        os.remove(buffer_file_name)

        # THEN
        self.assertTrue(not "animations" in gltf_json)

    def test_animation_export(self):
        # GIVEN
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.object

        # Create animation
        obj_do = bpy.data.objects[obj.name]
        bpy.ops.screen.frame_jump(end=False)
        bpy.context.scene.frame_set(1)
        obj_do.location = (0, 0, 0)
        obj_do.keyframe_insert(data_path="location", index=-1)
        bpy.context.scene.frame_set(100)
        obj_do.location = (10, 10, 10)
        obj_do.keyframe_insert(data_path="location", index=-1)
        bpy.ops.screen.frame_jump(end=False)

        # WHEN
        gltf_file_name = "./test_gltf_animation_export.gltf"
        buffer_file_name = "./test_gltf_animation_export.bin"
        bpy.ops.export_scene.gltf(filepath=gltf_file_name, export_selected=True, export_animations=True)
        gltf = open(gltf_file_name, 'r')

        # THEN
        self.assertFalse(gltf.closed)

        # WHEN
        gltf_json = json.load(gltf)

        # Cleanup
        gltf.close()
        os.remove(gltf_file_name)
        os.remove(buffer_file_name)

        # THEN
        self.assertTrue("animations" in gltf_json)


# We must only send the sys args forwarded by blender
unittest.main(argv=sys.argv[sys.argv.index("--") + 1:], verbosity=2)
