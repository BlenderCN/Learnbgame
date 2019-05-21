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

bl_info = {
    "name": "MoMoSculpt",
    "author": "Domino Marama, Soraya Elcar, originally published by Machinimatrix",
    "version": (2, 0, 6),
    "blender": (2, 5, 7),
    "api": 36147,
    #"location": "View3D > Add",
    "description": "Adds support for Second Life primitives",
    "wiki_url": "https://github.com/sorayaelcar/MoMoSculpt/wiki",
    "tracker_url": "https://github.com/sorayaelcar/MoMoSculpt/issues",
    "category": "Learnbgame"
}

try:
    __import__('bpy')
    inblender = True
except(ImportError):
    inblender = False

if "bpy" in locals():
    import imp
    imp.reload(sculpty)
    imp.reload(add_mesh_uv_shape)
    imp.reload(properties_primitive)
    imp.reload(mesh_rasterize)
    imp.reload(object_bake)
    imp.reload(object_sculptify)
    imp.reload(library)
    imp.reload(uv_bounds)
    imp.reload(mesh_from_map)
    imp.reload(io_export_llsd)
    imp.reload(config)
elif inblender:
    from . import sculpty
    from . import add_mesh_uv_shape
    from . import properties_primitive
    from . import mesh_rasterize
    from . import object_bake
    from . import object_sculptify
    from . import library
    from . import uv_bounds
    from . import mesh_from_map
    from . import io_export_llsd
    from . import config
    import bpy


import os

if inblender:
    class INFO_MT_mesh_add_uvshape(bpy.types.Menu):
        bl_idname = "INFO_MT_mesh_add_uvshape"
        bl_label = "UVShape"

        def draw(self, context):
            layout = self.layout
            layout.operator_context = 'INVOKE_REGION_WIN'
            op = layout.operator("mesh.uv_shape_bricks_add",
                icon='MOD_BUILD', text='Bricks')
            op.subdivision_type = 'SIMPLE'
            op.subdivision = 1
            layout.operator("mesh.uv_shape_cone_add",
                icon='MESH_CONE', text='Cone')
            layout.operator("mesh.uv_shape_cylinder_add",
                icon='MESH_CYLINDER', text='Cylinder')
            layout.operator("mesh.uv_shape_hemisphere_add",
                icon='MESH_CIRCLE', text='Hemisphere')
            layout.operator("mesh.uv_shape_plane_add",
                icon='MESH_GRID', text='Plane')
            layout.operator("mesh.uv_shape_ring_add",
                icon='MESH_CYLINDER', text='Ring')
            layout.operator("mesh.uv_shape_sphere_add",
                icon='MESH_UVSPHERE', text='Sphere')
            op = layout.operator("mesh.uv_shape_star_add",
                icon='MOD_PARTICLES', text='Star')
            op.subdivision_type = 'SIMPLE'
            op = layout.operator("mesh.uv_shape_steps_add",
                icon='PARTICLEMODE', text='Steps')
            op.subdivision_type = 'SIMPLE'
            layout.operator("mesh.uv_shape_torus_add",
                icon='MESH_TORUS', text='Torus')


def menu_add_uvshape(self, context):
    self.layout.menu(INFO_MT_mesh_add_uvshape.bl_idname,
        text="UV Shape", icon='MESH_GRID')


def menu_render_lod(self, context):
    self.layout.operator(sculpty.ImageRenderLOD.bl_idname,
        text=sculpty.ImageRenderLOD.bl_label)


def menu_bake_sculpty(self, context):
    self.layout.operator(sculpty.ImageBakeSculpty.bl_idname,
        text=sculpty.ImageBakeSculpty.bl_label)


def menu_image_as_sculpty(self, context):
    self.layout.operator("image.import_sculpty")


def menu_rasterize(self, context):
    self.layout.operator(mesh_rasterize.MeshRasterizer.bl_idname,
        text="Rasterize")


def menu_import_sculpty(self, context):
    self.layout.operator("mesh.uv_shape_image_add",
        text='Sculpty (map image)')


def menu_object_bake(self, context):
    self.layout.operator("object.sculpty_bake",
        text='Bake Sculpt Maps...')


def menu_object_sculptify(self, context):
    self.layout.operator("object.sculptify",
        text='Sculptify')


def menu_update_from_map(self, context):
    self.layout.operator("object.update_from_sculpt_map")


def menu_uv_bounds(self, context):
    self.layout.operator("uv.to_bounds",
        text='Scale to bounds')


def menu_export_llsd(self, context):
    self.layout.operator("export.llsd")


def register():
    bpy.utils.register_module(__name__)
    library.register()
    config_path = bpy.utils.user_resource('CONFIG', 'momosculpt')
    if os.path.exists(config_path):
        print("do config")
    bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_rasterize)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(menu_rasterize)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(menu_update_from_map)
    bpy.types.INFO_MT_mesh_add.append(menu_add_uvshape)
    bpy.types.INFO_MT_mesh_add_uvshape.append(library.menu_library)
    bpy.types.Object.prim = bpy.props.PointerProperty(
        type=properties_primitive.PrimitiveSettings,
        name="Primitive",
        description="Primitive Settings")
    bpy.types.IMAGE_MT_image.append(menu_render_lod)
    bpy.types.IMAGE_MT_image.append(menu_bake_sculpty)
    bpy.types.IMAGE_MT_image.append(menu_image_as_sculpty)
    bpy.types.INFO_MT_file_import.append(menu_import_sculpty)
    bpy.types.INFO_MT_file_export.append(menu_export_llsd)
    bpy.types.VIEW3D_MT_object.append(menu_object_sculptify)
    bpy.types.VIEW3D_MT_object.append(menu_object_bake)
    bpy.types.IMAGE_MT_uvs_transform.append(menu_uv_bounds)


def unregister():
    bpy.utils.unregister_module(__name__)
    library.unregister()
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_rasterize)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(menu_rasterize)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(menu_update_from_map)
    bpy.types.INFO_MT_mesh_add_uvshape.remove(library.menu_library)
    bpy.types.INFO_MT_mesh_add.remove(menu_add_uvshape)
    bpy.types.IMAGE_MT_image.remove(menu_render_lod)
    bpy.types.IMAGE_MT_image.remove(menu_bake_sculpty)
    bpy.types.IMAGE_MT_image.remove(menu_image_as_sculpty)
    bpy.types.INFO_MT_file_import.remove(menu_import_sculpty)
    bpy.types.INFO_MT_file_export.append(menu_export_llsd)
    bpy.types.VIEW3D_MT_object.remove(menu_object_bake)
    bpy.types.VIEW3D_MT_object.remove(menu_object_sculptify)
    bpy.types.IMAGE_MT_uvs_transform.remove(menu_uv_bounds)


if __name__ == "__main__":
    register()
