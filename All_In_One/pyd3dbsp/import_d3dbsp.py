import gc
import math
import os
import struct

import bpy
import bpy.ops
import bpy.props
import bmesh

from . import read_d3dbsp

class D3DBSPImporter(bpy.types.Operator):
    bl_idname = 'pyd3dbsp.d3dbsp_importer'
    bl_label = 'CoD2 D3DBSP (.d3dbsp)'
    bl_options = {'UNDO'}


    filepath = bpy.props.StringProperty(subtype = 'FILE_PATH')
    filename_ext = '.d3dbsp'
    filter_glob = bpy.props.StringProperty(default="*.d3dbsp", options={'HIDDEN'})

    materialPath = bpy.props.StringProperty(
        name = 'Material Path',
        description = 'Directory path containing the materials.',
        default = '',
        #subtype = 'DIR_PATH'
    )

    texturePath = bpy.props.StringProperty(
        name = 'Texture Path',
        description = 'Directory path containing the textures.',
        default = '',
        #subtype = 'DIR_PATH'
    )

    xmodelPath = bpy.props.StringProperty(
        name = 'Models Path',
        description = 'Directory path containing map entities.',
        default = '',
        #subtype = 'DIR_PATH'
    )

    def execute(self, context):
        #todo
        result_import_d3dbsp = self.import_d3dbsp(context)
        #result_import_entities = import_entities()


        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def import_d3dbsp(self, context):
        # will need to clean up this mess once i got the whole stuff working
        d3dbsp = read_d3dbsp.D3DBSP()
        if(d3dbsp.load_d3dbsp(self.filepath)):
            
            for i in range (0, len(d3dbsp.trianglesoups)):
                mesh = bpy.data.meshes.new('mapgeo_' + str(i) )
                obj = bpy.data.objects.new('mapgeo_' + str(i), mesh)

                bpy.context.scene.objects.link(obj)
                bpy.context.scene.objects.active = obj
                obj.select = True

                mesh = bpy.context.object.data
                bm = bmesh.new()

                curr_soup = d3dbsp.trianglesoups[i]
                curr_soup_tricount = (int) (curr_soup.triangle_length / 3)

                uv_data_list = []
                vertexcolor_data_list = []

                for j in range (0, curr_soup_tricount):
                    curr_triangle = d3dbsp.triangles[(int) (curr_soup.triangle_offset / 3 + j)]

                    vertex1 = d3dbsp.vertices[(int) (curr_soup.vertex_offset + curr_triangle.v1)]
                    vertex2 = d3dbsp.vertices[(int) (curr_soup.vertex_offset + curr_triangle.v2)]
                    vertex3 = d3dbsp.vertices[(int) (curr_soup.vertex_offset + curr_triangle.v3)]

                    v1 = bm.verts.new((vertex1.pos_x, vertex1.pos_y, vertex1.pos_z))
                    v2 = bm.verts.new((vertex2.pos_x, vertex2.pos_y, vertex2.pos_z))
                    v3 = bm.verts.new((vertex3.pos_x, vertex3.pos_y, vertex3.pos_z))

                    uv_face_list = []
                    vertexcolor_face_list = []

                    uv_face_list.append((vertex1.uv_u, vertex1.uv_v))
                    uv_face_list.append((vertex2.uv_u, vertex2.uv_v))
                    uv_face_list.append((vertex3.uv_u, vertex3.uv_v))

                    vertexcolor_face_list.append((vertex1.clr_r / 255, vertex1.clr_g / 255, vertex1.clr_b / 255))
                    vertexcolor_face_list.append((vertex2.clr_r / 255, vertex2.clr_g / 255, vertex2.clr_b / 255))
                    vertexcolor_face_list.append((vertex3.clr_r / 255, vertex3.clr_g / 255, vertex3.clr_b / 255))

                    uv_data_list.append(uv_face_list)
                    vertexcolor_data_list.append(vertexcolor_face_list)

                    bm.verts.ensure_lookup_table()
                    bm.verts.index_update()

                    bm.faces.new((v1, v2, v3))
                    bm.faces.ensure_lookup_table()
                    bm.faces.index_update()

                uv_layer = bm.loops.layers.uv.new()
                vertexcolor_layer = bm.loops.layers.color.new()

                for face, uv_face_data, vertexcolor_face_data in zip(bm.faces, uv_data_list, vertexcolor_data_list):
                    for loop, uv_data, vertexcolor_data in zip(face.loops, uv_face_data, vertexcolor_face_data):
                        loop[uv_layer].uv = uv_data
                        loop[vertexcolor_layer] = vertexcolor_data

                bm.to_mesh(mesh)
                bm.free()
            
            return True
        else:
            return False
    
    def import_entities(self, context):
        pass
    
    def import_materials(self, materials):
        pass

