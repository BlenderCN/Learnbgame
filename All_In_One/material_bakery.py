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
    "name": "Material Bakery",
    "author": "Nigel Munro",
    "version": (0, 9, 8),
    "blender": (2, 80, 0),
    "location": "Properties > Material > Material Bakery",
    "warning": "",
    "description": "Bake out Material Node graph into PBR texture maps",
    "wiki_url": ""
                "Scripts/Material/MaterialBakery",
    "category": "Learnbgame",
}


# TODO Move bake graph to proper location
# find node input/output by names instead of indexes?
# bake AO?

import bpy

from bpy.types import (
        Operator,
        Menu,
        Panel,
        PropertyGroup,
        AddonPreferences,
        )

from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        )

def findUVBakeNode(nodes, context):
    node_uv_map = None

    for node in nodes:
        if node_uv_map is None:
            if node.type == 'UVMAP' and node.uv_map == context.scene.bakery_out_uv:
                node_uv_map = node
        else:
            if node.type == 'UVMAP' and node.uv_map == context.scene.bakery_out_uv:
                #print("More than 1 UVMap node found")
                #self.report({'INFO'}, "More than 1 UVMap node found")
                return None
    return node_uv_map


def saveTexture(context, image, format, name, dir):
    ext = ""
    if format == 'PNG':
        ext=".png"
    else:
        ext=".jpg"
    filepath_raw = dir + name + ext
    image.filepath_raw = filepath_raw
    image.file_format = format
    image.save()
    

class MatBake_Panel(bpy.types.Panel):
    bl_label = "Material Bakery"
    bl_idname = "MATBAKE_PT_main"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Active Object: " + obj.name)

        row = layout.row()
        row.prop(context.scene, "bakery_resolution")
        
        row = layout.row()
        col = row.column()
        col.prop(context.scene, "bakery_col")
        col = row.column()
        col.prop(context.scene, "bakery_col_alpha")


        row = layout.row()
        col = row.column()
        col.prop(context.scene, "bakery_roughness")
        col = row.column()
        col.prop(context.scene, "bakery_normals")

        row = layout.row()
        row.prop(context.scene, "bakery_metallic")
        
        row = layout.row()
        row.prop_search(context.scene, "bakery_out_uv", obj.data, "uv_layers")

        row = layout.row()
        row.prop(context.scene, "bakery_tex_name")

        row = layout.row()
        row.prop(context.scene, "bakery_out_format")
        
        row = layout.row()
        row.prop(context.scene, "bakery_out_directory")
        
        #row = layout.row()
        #row.prop(context.scene, "uv_bake_alpha_color")
        
        op = layout.operator("material.mat_bake_create_maps", text="Create Maps")

        row = layout.row()
        col = row.column()
        col.prop(bpy.context.scene.cycles, "samples")
        col = row.column()
        col.prop(context.scene, "bakery_margin")

        op = layout.operator("material.mat_bake_bake_maps", text="Bake Maps")
        
        
        

class MatBake_CreateMaps(Operator):
    bl_idname = 'material.mat_bake_create_maps'
    bl_label = "Create Maps"
    bl_description = "Create texture maps"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return (ob and ob.type == 'MESH' and bpy.context.scene.bakery_out_uv != '')

    def draw(self, context):
        layout = self.layout
        
        # cleaning up
        terminate(global_undo)

        return{'FINISHED'}
    
    def execute(self, context):
        # initialise
        ob = bpy.context.active_object

        img_col = None
        img_rgh = None
        img_met = None
        img_nrm = None

        w = context.scene.bakery_resolution
        h = context.scene.bakery_resolution

        if context.scene.bakery_col:
            img_col = bpy.data.images.new(context.scene.bakery_tex_name + "_col", width=w, height=h, alpha=context.scene.bakery_col_alpha)
        if context.scene.bakery_roughness:
            img_rgh = bpy.data.images.new(context.scene.bakery_tex_name + "_rgh", width=w, height=h)
        if context.scene.bakery_metallic:
            img_met = bpy.data.images.new(context.scene.bakery_tex_name + "_met", width=w, height=h)
        if context.scene.bakery_normals:
            img_nrm = bpy.data.images.new(context.scene.bakery_tex_name + "_nrm", width=w, height=h)


        if len(ob.data.materials) > 0:
            # Get material
            for mat in ob.data.materials:
                mat.use_nodes=True

                nodes=mat.node_tree.nodes

                # Create node
                node_uv_map = nodes.new(type='ShaderNodeUVMap')
                node_uv_map.uv_map = context.scene.bakery_out_uv

                links = mat.node_tree.links

                if img_col:
                    col = nodes.new(type='ShaderNodeTexImage')
                    col.image = img_col
                    link = links.new(node_uv_map.outputs[0], col.inputs[0])
                
                if img_rgh:
                    rgh = nodes.new(type='ShaderNodeTexImage')
                    rgh.image = img_rgh
                    link = links.new(node_uv_map.outputs[0], rgh.inputs[0])
                
                if img_met:
                    met = nodes.new(type='ShaderNodeTexImage')
                    met.image = img_met
                    link = links.new(node_uv_map.outputs[0], met.inputs[0])

                if img_nrm:
                    nrm = nodes.new(type='ShaderNodeTexImage')
                    nrm.image = img_nrm
                    link = links.new(node_uv_map.outputs[0], nrm.inputs[0])

        else:
            self.report({'INFO'}, "No material attached to object")
            return {'CANCELLED'}

        return{'FINISHED'}


class MatBake_BakeMaps(Operator):
    bl_idname = 'material.mat_bake_bake_maps'
    bl_label = "Bake Maps(Cycles Only)"
    bl_description = "Bake out selected texture maps(Cycles Only)."


    @classmethod
    def poll(cls, context):
        #ob = context.active_object
        ob = bpy.context.active_object

        allUVNsFound = True
        for i in range(0, len(ob.data.materials)):
            mat = ob.data.materials[i]
            nodes=mat.node_tree.nodes

            node_uv_map = findUVBakeNode(nodes, context)
            if node_uv_map is None:
                allUVNsFound = False

        return (ob and ob.type == 'MESH' and context.scene.render.engine == 'CYCLES' and allUVNsFound and len(ob.data.materials) > 0) 

    def draw(self, context):
        layout = self.layout
        
        # cleaning up
        terminate(global_undo)

        return{'FINISHED'}
    
    def execute(self, context):
        # initialise

        ob = bpy.context.active_object

        cols = [None]*len(ob.data.materials)
        rghs = [None]*len(ob.data.materials)
        mets = [None]*len(ob.data.materials)
        nrms = [None]*len(ob.data.materials)

        if len(ob.data.materials) > 0:
            # Get material

            for i in range(0, len(ob.data.materials)):
                mat = ob.data.materials[i]
                mat.use_nodes=True
                links = mat.node_tree.links
                nodes=mat.node_tree.nodes

                nodes.active = None

                node_uv_map = findUVBakeNode(nodes, context)

                outLinks = len(node_uv_map.outputs[0].links)

                for link in node_uv_map.outputs[0].links:
                    node = link.to_node
                    if node.type == 'TEX_IMAGE' and node.image.name.endswith('_col'):
                        cols[i] = node
                        break
                        
                for link in node_uv_map.outputs[0].links:
                    node = link.to_node
                    if node.type == 'TEX_IMAGE' and node.image.name.endswith('_rgh'):
                        rghs[i] = node
                        break

                for link in node_uv_map.outputs[0].links:
                    node = link.to_node
                    if node.type == 'TEX_IMAGE' and node.image.name.endswith('_met'):
                        mets[i] = node
                        break

                for link in node_uv_map.outputs[0].links:
                    node = link.to_node
                    if node.type == 'TEX_IMAGE' and node.image.name.endswith('_nrm'):
                        nrms[i] = node
                        break

        else:
            self.report({'INFO'}, "No material attached to object")
            return {'CANCELLED'}

        #From here shader graph can be modified
        bpy.ops.ed.undo_push()

        bsdf_prins = [None]*len(ob.data.materials)
        bsdf_metvals = [0]*len(ob.data.materials)
        bsdf_metins = [None]*len(ob.data.materials)
        # Find principled shaders
        for i in range(0, len(ob.data.materials)):
            mat = ob.data.materials[i]

            links = mat.node_tree.links
            nodes=mat.node_tree.nodes

            bsdf_prin = None

            for n in nodes:
                if bsdf_prin == None:
                    if n.type == 'BSDF_PRINCIPLED':
                        bsdf_prin = n
                        bsdf_prins[i] = n
                        bsdf_metvals[i] = n.inputs[4].default_value
                        n.inputs[4].default_value = 0.0
                        if len(bsdf_prin.inputs[4].links) > 0:
                            bsdf_metins[i] = n.inputs[4].links[0].from_node
                            links.remove(bsdf_prin.inputs[4].links[0])

                else:
                    if bsdf_prin != None and n.type == 'BSDF_PRINCIPLED':
                        self.report({'INFO'}, "Found multiple BSDF Principled shaders in material graph")
                        return {'CANCELLED'}
        
        #Set bake settings
        bpy.context.scene.render.bake.use_pass_direct = False #TODO change to just context
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True

        
        allColsFound = True
        for i in range(0, len(ob.data.materials)):
            mat = ob.data.materials[i]
            nodes=mat.node_tree.nodes

            col=cols[i]
            if col:
                nodes.active = col
            else:
                allColsFound = False

        if allColsFound:
            bpy.ops.object.bake(type='DIFFUSE', margin=context.scene.bakery_margin)
            if context.scene.bakery_out_directory != "":
                img = cols[0].image
                saveTexture(context, img, context.scene.bakery_out_format, img.name, context.scene.bakery_out_directory)

        
        allRghsFound = True
        for i in range(0, len(ob.data.materials)):
            mat = ob.data.materials[i]
            nodes=mat.node_tree.nodes

            rgh=rghs[i]
            if rgh:
                nodes.active = rgh
            else:
                allRghsFound = False

        if allRghsFound:
            bpy.ops.object.bake(type='ROUGHNESS', margin=context.scene.bakery_margin)
            if context.scene.bakery_out_directory != "":
                img = rghs[0].image
                saveTexture(context, img, context.scene.bakery_out_format, img.name, context.scene.bakery_out_directory)


        for i in range(0, len(ob.data.materials)):
            mat = ob.data.materials[i]
            links = mat.node_tree.links
            nodes=mat.node_tree.nodes
            bsdf_prin = bsdf_prins[i]

            in_met = bsdf_metins[i]
            #in_from_sock = None

            #if bsdf_prin and len(bsdf_prin.inputs[4].links) > 0:
            #    in_met = bsdf_prin.inputs[4].links[0].from_node
            #    in_from_sock = bsdf_prin.inputs[4].links[0].from_socket

            if in_met is not None:
                    link = links.new(in_met.outputs[0], bsdf_prin.inputs[7]) #Maybe a bug here?
                #else:
                    #self.report({'INFO'}, "Could not find BSDF Principled Metalic input")
            elif bsdf_prin is not None:
                if len(bsdf_prin.inputs[7].links) > 0:
                    links.remove(bsdf_prin.inputs[7].links[0])
                bsdf_prin.inputs[7].default_value = bsdf_metvals[i]#bsdf_prin.inputs[4].default_value


        allMetsFound = True
        for i in range(0, len(ob.data.materials)):
            mat = ob.data.materials[i]
            nodes=mat.node_tree.nodes

            met=mets[i]
            if met:
                nodes.active = met
            else:
                allMetsFound = False

        if allMetsFound:
            bpy.ops.object.bake(type='ROUGHNESS', margin=context.scene.bakery_margin)
            if context.scene.bakery_out_directory != "":
                img = mets[0].image
                saveTexture(context, img, context.scene.bakery_out_format, img.name, context.scene.bakery_out_directory)


        for i in range(0, len(ob.data.materials)):
            mat = ob.data.materials[i]
            
            links = mat.node_tree.links
            nodes=mat.node_tree.nodes

            bsdf_prin = bsdf_prins[i]

            in_nrm_tex = None

            if bsdf_prin and len(bsdf_prin.inputs[17].links) > 0:
                in_nrm = None
                if bsdf_prin.inputs[17].links[0].from_node is not None:
                    in_nrm = bsdf_prin.inputs[17].links[0].from_node
                
                if in_nrm and in_nrm.type == 'NORMAL_MAP':
                    if len(bsdf_prin.inputs[17].links) > 0:
                        n = bsdf_prin.inputs[17].links[0].from_node
                        
                        if len(n.inputs[1].links) > 0:
                            n2 = n.inputs[1].links[0].from_node
                            if n2.type:
                                in_nrm_tex = n2

                if in_nrm_tex is not None:
                    link = links.new(in_nrm_tex.outputs[0], bsdf_prin.inputs[0])
                else:
                    self.report({'INFO'}, "Could not find BSDF Principled normal texture input")
            else:
                self.report({'INFO'}, "Could not find BSDF Principled normal input node")

        
        allNrmsFound = True
        for i in range(0, len(ob.data.materials)):
            mat = ob.data.materials[i]
            nodes=mat.node_tree.nodes

            nrm=nrms[i]
            if nrm:
                nodes.active = nrm
            else:
                allNrmsFound = False

        if allNrmsFound:
            bpy.ops.object.bake(type='DIFFUSE', margin=context.scene.bakery_margin)
            if context.scene.bakery_out_directory != "":
                img = nrms[0].image
                saveTexture(context, img, context.scene.bakery_out_format, img.name, context.scene.bakery_out_directory)
        else:
            self.report({'INFO'}, "Missing nrm output texture node. Skipping Normal bake")
        
        bpy.ops.ed.undo()

        

        return{'FINISHED'}

classes = (
    MatBake_CreateMaps,
    MatBake_BakeMaps,
    MatBake_Panel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.bakery_resolution = IntProperty(
        name="Resolution",
        description="resolution",
        default=1024,
        min=32,
        max=8192,
        )
    
    bpy.types.Scene.bakery_alpha_color = FloatVectorProperty(
        name="Alpha Color",
        description="Color to be used for transparency",
        subtype='COLOR',
        min=0.0,
        max=1.0)
        
    bpy.types.Scene.bakery_out_directory = StringProperty(
        name="Output(Optional)",
        description="Output Drectory for created map",
        subtype="DIR_PATH"
        )

    bpy.types.Scene.bakery_col = BoolProperty(
        name="Base Color",
        description="Bake Base Color",
        default=True
        )
        
    bpy.types.Scene.bakery_col_alpha = BoolProperty(
        name="Alpha Base Color",
        description="Add alpha channel to base color map",
        default=False
        )
    
    bpy.types.Scene.bakery_roughness = BoolProperty(
        name="Roughness",
        description="Bake Roughness",
        default=True
        )
    
    bpy.types.Scene.bakery_normals = BoolProperty(
        name="Normals",
        description="Bake Normals",
        default=True
        )

    bpy.types.Scene.bakery_metallic = BoolProperty(
        name="Metallic",
        description="Bake Metallic",
        default=False
        )
        
    bpy.types.Scene.bakery_out_uv = StringProperty(
        name="Output UV",
        description="Select the UV Map to be baked onto"
        )

    bpy.types.Scene.bakery_tex_name = StringProperty(
        name="Texture Name",
        description="Name of the baked texture maps",
        default="tex"
        )

    bpy.types.Scene.bakery_margin = IntProperty(
        name="Bake Margin",
        description="Bake Margin",
        default=16,
        min=0,
        max=8192,
        )
    
    bpy.types.Scene.bakery_out_format = EnumProperty(
        name="Out Format",
        items=(("PNG", "PNG", "PNG file format"),
              ("JPEG", "JPEG", "JPEG file format")),
        description="Output file format",
        default='PNG'
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.bakery_alpha_color
    del bpy.types.Scene.bakery_resolution
    del bpy.types.Scene.bakery_out_directory
    del bpy.types.Scene.bakery_col
    del bpy.types.Scene.bakery_col_alpha
    del bpy.types.Scene.bakery_roughness
    del bpy.types.Scene.bakery_normals
    del bpy.types.Scene.bakery_metallic
    del bpy.types.Scene.bakery_out_uv
    del bpy.types.Scene.bakery_tex_name
    del bpy.types.Scene.bakery_margin
    del bpy.types.Scene.bakery_out_format


if __name__ == "__main__":
    register()
