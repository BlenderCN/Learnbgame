import bpy
import bmesh

def LiberSplintWeightDef(self, context):


    bpy.ops.object.mode_set(mode = 'OBJECT')

    bpy.ops.object.duplicate()

    bpy.context.object.name = "ObjSplint"

    # Seleciona área interesse

    # Which group to find?
    groupName = 'Group'


    # Use the active object
    obj = bpy.context.active_object

    # Make sure you're in edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Deselect all verts
    bpy.ops.mesh.select_all(action='DESELECT')

    # Make sure the active group is the one we want
    bpy.ops.object.vertex_group_set_active(group=groupName)

    # Select the verts
    bpy.ops.object.vertex_group_select()

    # Store the mesh
    mesh = obj.data

    # Get the selected verts
    selVerts = [v for v in mesh.vertices if v.select]

    # Inverte seleção
    bpy.ops.mesh.select_all(action='INVERT')

    # Zera weight
    bpy.context.scene.tool_settings.vertex_group_weight = 0

    bpy.ops.object.vertex_group_assign()

    # SELECIONA 1

    minWeight = .99
    maxWeight = 1
    vertexGroupIndex = 0 # Index 0

    bpy.ops.object.mode_set(mode = 'EDIT') 
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT') # Switch to Object to get selection

    obj = bpy.context.active_object 
    verts = [v for v in obj.data.vertices]
    for v in verts:
      weight = v.groups[vertexGroupIndex].weight
      if weight <= maxWeight and weight >= minWeight:
        v.select = True
    bpy.ops.object.mode_set(mode = 'EDIT')

    # Duplica objetos

    bpy.ops.mesh.duplicate()
    bpy.ops.mesh.separate(type='SELECTED')

    bpy.ops.object.mode_set(mode = 'OBJECT') 

    obj_copiado = bpy.data.objects[str(bpy.context.active_object.name)+'.001'] 
    bpy.ops.object.select_all(action='DESELECT')   
    obj_copiado.select = True
    bpy.context.scene.objects.active = obj_copiado

    # Cria o volume

    bpy.ops.object.metaball_add(type='BALL', radius=1)
    bpy.context.object.name = "SplintFinal"

    bpy.ops.object.select_all(action='DESELECT')   
    obj_copiado.select = True
    bpy.context.scene.objects.active = obj_copiado

    bpy.ops.object.particle_system_add()
    bpy.data.particles["ParticleSettings"].type = 'HAIR'
    bpy.data.particles["ParticleSettings"].render_type = 'OBJECT'
    bpy.data.particles["ParticleSettings"].count = 2000
    bpy.data.particles["ParticleSettings"].dupli_object = bpy.data.objects["SplintFinal"]
    bpy.data.particles["ParticleSettings"].particle_size = 0.22
    bpy.data.particles["ParticleSettings"].name = "DELETE" # Senão não funciona, pois usa o nome anterior

    MetaSplint = bpy.data.objects['SplintFinal']


    bpy.ops.object.select_all(action='DESELECT')
    MetaSplint.select = True
    bpy.context.scene.objects.active = MetaSplint
        
    bpy.ops.object.convert(target='MESH')
        
    bpy.ops.object.modifier_add(type='SMOOTH')
    bpy.context.object.modifiers["Smooth"].factor = 1
    bpy.context.object.modifiers["Smooth"].iterations = 20

    bpy.ops.object.convert(target='MESH')

    bpy.ops.object.modifier_add(type='SMOOTH')
    bpy.context.object.modifiers["Smooth"].factor = 1
    bpy.context.object.modifiers["Smooth"].iterations = 20

    bpy.ops.object.convert(target='MESH')

    bpy.ops.object.modifier_add(type='REMESH')
    bpy.context.object.modifiers["Remesh"].use_remove_disconnected = True
    bpy.context.object.modifiers["Remesh"].mode = 'SMOOTH'
    bpy.context.object.modifiers["Remesh"].octree_depth = 7

    bpy.ops.object.convert(target='MESH')

    # Apaga original

    bpy.ops.object.select_all(action='DESELECT')   
    obj_copiado.select = True
    bpy.context.scene.objects.active = obj_copiado
    bpy.ops.object.delete(use_global=False)

    # Boolean

    bpy.ops.object.select_all(action='DESELECT')
    BoolA = bpy.data.objects['ObjSplint']
    BoolB = bpy.data.objects['SplintFinal.001']
    BoolA.select = True
    BoolB.select = True
    bpy.context.scene.objects.active = BoolB
    bpy.ops.btool.direct_difference()

    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

class LiberSplintWeight(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.liber_splint_weight"
    bl_label = "Liber Splint Weight"

    def execute(self, context):
        LiberSplintWeightDef(self, context)
        return {'FINISHED'}

def LiberWeight1Def(self, context):
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.data.brushes["Draw"].vertex_tool = 'MIX'
    bpy.ops.brush.curve_preset(shape='MAX')
    bpy.context.scene.tool_settings.unified_paint_settings.weight = 1

class LiberWeight1(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.liber_weight_1"
    bl_label = "Liber Change Weight"

    def execute(self, context):
        LiberWeight1Def(self, context)
        return {'FINISHED'}

def LiberWeight0Def(self, context):
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.data.brushes["Draw"].vertex_tool = 'MIX'
    bpy.ops.brush.curve_preset(shape='MAX')
    bpy.context.scene.tool_settings.unified_paint_settings.weight = 0

class LiberWeight0(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.liber_weight_0"
    bl_label = "Liber Change Weight"

    def execute(self, context):
        LiberWeight0Def(self, context)
        return {'FINISHED'}

