import bpy
import bmesh

bl_info = {
    "name": "Render Bevel",
    "description": "Render Bevel",
    "author": "Bartosz Styperek",
    "version": (0, 2, 0),
    "blender": (2, 80, 0),
    "location": "SideBar(N) -> Tools tab -> Render Bevel panel",
    "warning": "",
    "wiki_url": "",
    "category": "Object"}


class RB_OP_EditRenderBevelPanel(bpy.types.Panel):
    bl_idname = "render_bevel_edit"
    bl_label = "Render Bevel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("object.render_bevel_vcolor")
        # row.operator("object.bevel_vcolor_node")


# FOR CURVE EDIT MODE
class RB_OT_ObjectRenderBevelPanel(bpy.types.Panel):
    bl_idname = "render_bevel"
    bl_label = "Render Bevel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tools"
    bl_context = "objectmode"

    def draw(self, context):
        RB_OP_EditRenderBevelPanel.draw(self, context)


class RB_OT_SetBevelVerColor(bpy.types.Operator):
    bl_label = "Render bevel size"
    bl_idname = "object.render_bevel_vcolor"
    bl_description = "Set render bevel size from vertex color (use F6 to change bevel size prop)"
    bl_options = {"REGISTER", "UNDO"}

    bevel: bpy.props.FloatProperty(name = "Bevel size", description = "Bevel size", default = 0.5, min = 0, max = 1, subtype = 'FACTOR')

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        activeObj = context.active_object
        mesh = activeObj.data
        wasVColCreated = False
        if not mesh.vertex_colors or "Bevel" not in mesh.vertex_colors.keys():
            mesh.vertex_colors.new(name="Bevel")
            wasVColCreated =True

        me = activeObj.data
        bevelCol = 3 * [self.bevel] + [1]
        if context.object.mode == "EDIT":
            bm = bmesh.from_edit_mesh(me)  # load mesh
            # bm.verts.ensure_lookup_table()
            color_layer = bm.loops.layers.color["Bevel"]
            if wasVColCreated:
                for vert in bm.verts:  # island faces
                    for loop in vert.link_loops:
                        loop[color_layer] = [0,0,0,1]
            selVerts = [vert for vert in bm.verts if vert.select]
            for vert in selVerts:  # island faces
                for loop in vert.link_loops:
                    loop[color_layer] = bevelCol
            bmesh.update_edit_mesh(mesh)
        else:
            bm = bmesh.new()  # load mesh
            bm.from_mesh(me)
            # bm.verts.ensure_lookup_table()
            color_layer = bm.loops.layers.color["Bevel"]
            if wasVColCreated:
                for vert in bm.verts:  # island faces
                    for loop in vert.link_loops:
                        loop[color_layer] = [0, 0, 0, 1]
            for vert in bm.verts:  # island faces
                for loop in vert.link_loops:
                    loop[color_layer] = bevelCol
            bm.to_mesh(me)
            bm.free()
        if activeObj.type == "MESH" and (len(activeObj.material_slots) == 0 or activeObj.material_slots[0].material is None):
            bpy.ops.object.bevel_vcolor_node()
        else:
            matNodeTree = activeObj.active_material.node_tree
            if 'RenderBevel' not in matNodeTree.nodes.keys():
                bpy.ops.object.bevel_vcolor_node()
        return {"FINISHED"}


class RB_OT_AdBevelVColNode(bpy.types.Operator):
    bl_label = "Add bevel node"
    bl_idname = "object.bevel_vcolor_node"
    bl_description = "Add bevel node to material"
    bl_options = {"REGISTER", "UNDO"}

    def attachCyclesmaterial(self, obj):
        mat = bpy.data.materials.get("BevelMat")
        if mat is None:
            # create material
            mat = bpy.data.materials.new(name="EmptyMat")
            mat.diffuse_color = (0.7, 0.7, 0.7, 1)
        obj.data.materials.append(mat)
        if bpy.context.scene.render.engine == 'CYCLES':
            obj.data.materials[0].use_nodes = True

    def execute(self, context):
        activeObj = context.active_object
        mesh = activeObj.data
        if not mesh.vertex_colors or "Bevel" not in mesh.vertex_colors.keys():
            self.report({'INFO'}, 'No bevel vertex color detected!')
            return {"CANCELLED"}
        if context.scene.render.engine == 'CYCLES':
            if activeObj.type == "MESH" and (len(activeObj.material_slots) == 0 or activeObj.material_slots[0].material is None):
                self.attachCyclesmaterial(activeObj)
            activeObj.active_material.use_nodes = True
            # activeObj.material_slots[0].material.use_nodes = True
            matNodeTree = activeObj.active_material.node_tree
        else:
            self.report({'INFO'}, 'Works only in cycles!')
            return {"CANCELLED"}
        links = matNodeTree.links
        nodes = matNodeTree.nodes
        if 'RenderBevel' in nodes.keys():
            return
        if "BevelGroup" not in bpy.data.node_groups.keys():
            BevelGroup = bpy.data.node_groups.new('BevelGroup', 'ShaderNodeTree')

            # create group inputs
            group_inputs = BevelGroup.nodes.new('NodeGroupInput')
            group_inputs.location = (-350, 0)
            BevelGroup.inputs.new('NodeSocketVectorXYZ', 'Normal')

            # create group outputs
            group_outputs = BevelGroup.nodes.new('NodeGroupOutput')
            group_outputs.location = (800, 0)
            BevelGroup.outputs.new('NodeSocketVectorXYZ', 'Normal')


            vCol = BevelGroup.nodes.new('ShaderNodeAttribute')
            vCol.attribute_name = "Bevel"
            vCol.location = (0, 100)

            mathPower = BevelGroup.nodes.new('ShaderNodeMath')
            mathPower.location = (200, 100)
            mathPower.operation = 'POWER'
            mathPower.inputs[1].default_value = 0.4545
            BevelGroup.links.new(vCol.outputs['Color'], mathPower.inputs[0])


            mathMul = BevelGroup.nodes.new('ShaderNodeMath')
            mathMul.location = (400, 100)
            mathMul.operation = 'MULTIPLY'
            mathMul.inputs[1].default_value = 0.1
            BevelGroup.links.new(mathPower.outputs[0], mathMul.inputs[0])


            bevel = BevelGroup.nodes.new('ShaderNodeBevel')
            bevel.location = (600, 100)

            BevelGroup.links.new(mathMul.outputs[0], bevel.inputs['Radius'])
            BevelGroup.links.new(bevel.outputs[0], group_outputs.inputs[0])
            BevelGroup.links.new(bevel.inputs['Normal'],group_inputs.outputs['Normal'])

        BevelGroup = nodes.new('ShaderNodeGroup')
        BevelGroup.name = 'RenderBevel'
        BevelGroup.node_tree = bpy.data.node_groups['BevelGroup']
        BevelGroup.location = (-300, 0)
        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED' and len(node.inputs['Normal'].links)==0:
                links.new(BevelGroup.outputs['Normal'], node.inputs['Normal'])
        # Add a diffuse shader and set its location:
        return {"FINISHED"}


classes = (
    RB_OP_EditRenderBevelPanel,
    RB_OT_ObjectRenderBevelPanel,
    RB_OT_SetBevelVerColor,
    RB_OT_AdBevelVColNode,
)
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
