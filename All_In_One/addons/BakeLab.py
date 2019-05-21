bl_info = {
    "name":        "BakeLab",
    "description": "Bake Multiple Different Types Of Maps in One Click",
    "author":      "Shahzod Boyxonov",
    "version":     (1, 2, 0),
    "blender":     (2, 79, 0),
    "location":    "View3D > Tools Panel > BakeLab",
    "category":    "Render"
}

import bpy
import bgl
import blf

def BakeLab_DrawProgressBar(y_shift,progress,text):
    bgl.glColor4f(0,0,0,1.0)
    bgl.glBegin(bgl.GL_QUADS)
    bgl.glVertex2i(19,  y_shift-1)
    bgl.glVertex2i(161, y_shift-1)
    bgl.glVertex2i(161, y_shift+31)
    bgl.glVertex2i(19,  y_shift+31)
    bgl.glEnd()
    bgl.glColor4f(0.7,0.5,0.3, 1.0)
    bgl.glBegin(bgl.GL_QUADS)
    bgl.glVertex2i(20,  y_shift)
    bgl.glVertex2i(160, y_shift)
    bgl.glVertex2i(160, y_shift+30)
    bgl.glVertex2i(20,  y_shift+30)
    bgl.glEnd()
    bgl.glColor4f(0.05,0.1,0.15, 1.0)
    bgl.glBegin(bgl.GL_QUADS)
    bgl.glVertex2i(21,  y_shift+1)
    bgl.glVertex2i(159, y_shift+1)
    bgl.glVertex2i(159, y_shift+29)
    bgl.glVertex2i(21,  y_shift+29)
    bgl.glEnd()
    bgl.glColor4f(0.7,0.5,0.3, 1.0)
    bgl.glBegin(bgl.GL_QUADS)
    x_loc = (157-23)*progress+23
    bgl.glVertex2i(23,         y_shift+3)
    bgl.glVertex2i(int(x_loc), y_shift+3)
    bgl.glVertex2i(int(x_loc), y_shift+27)
    bgl.glVertex2i(23,         y_shift+27)
    bgl.glEnd()
    blf.position(0, 170, y_shift+10, 0)
    blf.draw(0, text)

def BakeLab_DrawCallback(self, context):
    props = context.scene.BakeLabProps
    ww = context.area.width
    wh = context.area.height
    
    bgl.glEnable(bgl.GL_BLEND)
    blf.enable(0,blf.SHADOW)
    blf.shadow(0,5,0,0.0,0.0,1)
    
    ######### Title {
    bgl.glBegin(bgl.GL_QUADS)
    bgl.glColor4f(0.88, 0.87, 0.85, 0.1)
    for i in range(0,20):
        bgl.glVertex2i(0,       wh)
        bgl.glVertex2i(120+i*3, wh)
        bgl.glVertex2i(120+i*3, wh-70)
        bgl.glVertex2i(0,       wh-70)
        
    bgl.glColor4f(0.7,0.1,0.3, 0.1)
    for i in range(0,20):
        bgl.glVertex2i(0,       wh-70)
        bgl.glVertex2i(140+i*3, wh-70)
        bgl.glVertex2i(140+i*3, wh-75)
        bgl.glVertex2i(0,       wh-75)
    bgl.glEnd()
    
    blf.size(0, 30, 72)
    bgl.glColor4f(0.7,0.1,0.3, 1.0)
    blf.position(0, 15, context.area.height-58, 0)
    blf.draw(0, 'BakeLab')
    ######### }
    
    ######### Progress {
    blf.size(0, 15, 72)
    y_shift = 15
    #######################################################################
    cur = self.bake_item_id
    max = len(context.scene.BakeLabMapColl)
    BakeLab_DrawProgressBar(y_shift,cur/max,'Map: '+ str(cur)+' of '+str(max))
    y_shift += 30
    #######################################################################
    if not props.s_to_a and not props.all_in_one:
        cur = self.bake_obj_id
        max = len(self.bake_objs)
        BakeLab_DrawProgressBar(y_shift,cur/max,'Object: '+ str(cur)+' of '+str(max))
        y_shift += 30
    #######################################################################
    if props.use_list:
        cur = self.ObjListIndex
        max = len(context.scene.BakeLabObjColl)
        BakeLab_DrawProgressBar(y_shift,cur/max,'List: '+ str(cur)+' of '+str(max))
        y_shift += 30
    #######################################################################
    ######### }
    
    
    blf.disable(0,blf.SHADOW)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

class baker:
    def __init__(self, type, image, item,
                engine = 'CYCLES', samples = 16):
        self.type = type
        self.image = image
        self.item = item
        self.engine = engine
        self.samples = samples
                
    def bake(self):
        if self.engine == 'CYCLES':
            ############################ CYCLES ###############################
            bpy.context.scene.cycles.samples = self.samples
            
            if bpy.ops.object.bake('INVOKE_DEFAULT',type = self.type)=={'CANCELLED'}:
                return False
        else:
            ############################ BI ###############################
            if bpy.context.scene.world:
                bpy.context.scene.world.light_settings.samples = self.samples
                    
            bpy.context.scene.render.bake_type = self.type
            if bpy.ops.object.bake_image('INVOKE_DEFAULT')=={'CANCELLED'}:
                return False
        
        return True
    
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################

class BakeLab(bpy.types.Operator):
    bl_idname = 'bakelab.bake'
    bl_label = 'BakeLab'
    bl_options = {'REGISTER','UNDO'}
    TMP_IMG_NODE_NAME = 'BAKELAB_IMAGE_NODE_TMP'
    TMP_COPY_MAT_NAME = 'BAKELAB_TMP_COPY_MAT_'
    
    def save_defaults(self,context):
        self.cur_engine        = bpy.context.scene.render.engine
        self.cycles_device     = bpy.context.scene.cycles.device
        self.s2a               = context.scene.render.use_bake_selected_to_active
        self.c_s2a             = context.scene.render.bake.use_selected_to_active
        self.b_bake_margin     = context.scene.render.bake_margin
        self.c_bake_margin     = context.scene.render.bake.margin
        self.bake_type         = context.scene.render.bake_type
        self.active_object     = context.scene.objects.active
        self.selected_objects  = [i for i in context.selected_objects]
        self.normalize         = context.scene.render.use_bake_normalize
        self.normal_space      = context.scene.render.bake_normal_space
        self.c_normal_space    = context.scene.render.bake.normal_space
        
        self.use_pass_direct   = context.scene.render.bake.use_pass_direct
        self.use_pass_indirect = context.scene.render.bake.use_pass_indirect
        self.use_pass_color    = context.scene.render.bake.use_pass_color
    
        self.use_pass_diffuse  = context.scene.render.bake.use_pass_diffuse
        self.use_pass_glossy   = context.scene.render.bake.use_pass_glossy
        self.use_pass_trans    = context.scene.render.bake.use_pass_transmission
        self.use_pass_sss      = context.scene.render.bake.use_pass_subsurface
        self.use_pass_ao       = context.scene.render.bake.use_pass_ambient_occlusion
        self.use_pass_emit     = context.scene.render.bake.use_pass_emit
    
        self.bake_distance     = context.scene.render.bake_distance
        self.use_cage          = context.scene.render.bake.use_cage
        self.cage_extrusion    = context.scene.render.bake.cage_extrusion
        self.cage_object       = context.scene.render.bake.cage_object
    
        if bpy.context.scene.world:
            self.bi_samples    = bpy.context.scene.world.light_settings.samples
        self.cy_samples        = bpy.context.scene.cycles.samples
        
    def restore_defaults(self,context):
        bpy.context.scene.render.engine                    = self.cur_engine
        bpy.context.scene.cycles.device                    = self.cycles_device
        context.scene.render.use_bake_selected_to_active   = self.s2a
        context.scene.render.bake.use_selected_to_active   = self.c_s2a
        context.scene.render.bake_margin                   = self.b_bake_margin
        context.scene.render.bake.margin                   = self.c_bake_margin
        context.scene.render.bake_type                     = self.bake_type
        context.scene.objects.active                       = self.active_object
        bpy.ops.object.select_all(action = 'DESELECT')
        for obj in self.selected_objects:
            obj.select = True
        context.scene.render.use_bake_normalize            = self.normalize
        context.scene.render.bake_normal_space             = self.normal_space
        context.scene.render.bake.normal_space             = self.c_normal_space
        
        context.scene.render.bake.use_pass_direct          = self.use_pass_direct
        context.scene.render.bake.use_pass_indirect        = self.use_pass_indirect
        context.scene.render.bake.use_pass_color           = self.use_pass_color
    
        context.scene.render.bake.use_pass_diffuse           = self.use_pass_diffuse
        context.scene.render.bake.use_pass_glossy            = self.use_pass_glossy
        context.scene.render.bake.use_pass_transmission      = self.use_pass_trans
        context.scene.render.bake.use_pass_subsurface        = self.use_pass_sss
        context.scene.render.bake.use_pass_ambient_occlusion = self.use_pass_ao
        context.scene.render.bake.use_pass_emit              = self.use_pass_emit
    
        context.scene.render.bake_distance                 = self.bake_distance
        context.scene.render.bake.use_cage                 = self.use_cage
        context.scene.render.bake.cage_extrusion           = self.cage_extrusion
        context.scene.render.bake.cage_object              = self.cage_object
    
        if bpy.context.scene.world:
            bpy.context.scene.world.light_settings.samples = self.bi_samples
        bpy.context.scene.cycles.samples                   = self.cy_samples
    
    def unwrap(self,props,obj):
        if props.newuv:
            obj.data.uv_textures.active = obj.data.uv_textures.new(name = 'UVMap_BAKELAB')
        elif obj.data.uv_textures.active:
            return
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        if   props.unwrap_mode == 'smart_uv':
            bpy.ops.uv.smart_project(angle_limit = props.smart_uv_angle,
                                    island_margin = props.smart_uv_margin)
        elif props.unwrap_mode == 'lightmap':
            bpy.ops.uv.lightmap_pack(PREF_BOX_DIV = props.lightmap_quality,
                                    PREF_MARGIN_DIV = props.lightmap_margin)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        
    def createTmpImageNodes(self,obj,image):
        for slot in obj.material_slots:
            mat = slot.material
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            for node in nodes:
                node.select = False
            if self.TMP_IMG_NODE_NAME in nodes:
                imgNode = nodes[self.TMP_IMG_NODE_NAME]
            else:
                imgNode = nodes.new(type = 'ShaderNodeTexImage')
                imgNode.name = self.TMP_IMG_NODE_NAME
            imgNode.select = True
            nodes.active = imgNode
            imgNode.image = image
            
    def removeTmpImageNodes(self,obj_list):
        for obj in obj_list:
            for slot in obj.material_slots:
                mat = slot.material
                if not mat: continue
                if not mat.node_tree: continue
                nodes = mat.node_tree.nodes
                if self.TMP_IMG_NODE_NAME in nodes:
                    nodes.remove(nodes[self.TMP_IMG_NODE_NAME])
        
    def add_empty_mat(self,obj):
        if len(obj.material_slots)==0:
            bpy.ops.object.material_slot_add()
         
        if not self.empty_mat:
            self.empty_mat = bpy.data.materials.new('BAKELAB_EMPTY_MAT')
            self.trash_mats.append(self.empty_mat)
        for slot in obj.material_slots:
            if slot.material is None:
                slot.material = self.empty_mat
                
    def passes_to_rgb(self,node,src_socket,nodes,links,passes,multiplier,addend):
        has_bsdf = False
        for input in node.inputs:
            if input.type == 'SHADER':
                has_bsdf = True
                if len(input.links):
                    self.passes_to_rgb(input.links[0].from_node,input,
                                    nodes,links,passes,multiplier,addend)
        
        if not has_bsdf:
            emit = nodes.new(type = 'ShaderNodeEmission')
            final_value = 0.0 * multiplier + addend
            emit.inputs[0].default_value = final_value,final_value,final_value,final_value
            links.new(emit.outputs[0],src_socket)
            ####### Find Pass Input Socket{
            pass_input = None
            for Pass in passes:
                pass_input = node.inputs.get(Pass)
                if pass_input: break
            ####### }
            if pass_input:
                if len(pass_input.links):
                    out_socket = pass_input.links[0].from_socket
                    mul = nodes.new(type = 'ShaderNodeMixRGB')
                    add = nodes.new(type = 'ShaderNodeMixRGB')
                    mul.inputs[0].default_value = 1
                    add.inputs[0].default_value = 1
                    mul.blend_type = 'MULTIPLY'
                    mul.inputs[2].default_value = multiplier,multiplier,multiplier,multiplier
                    if addend >= 0:
                        add.blend_type = 'ADD'
                        add.inputs[2].default_value = addend,addend,addend,addend
                    else:
                        add.blend_type = 'SUBTRACT'
                        add.inputs[2].default_value = -addend,-addend,-addend,-addend
                    
                    links.new(out_socket,     mul.inputs[1])
                    links.new(mul.outputs[0], add.inputs[1])
                    links.new(add.outputs[0], emit.inputs[0])
                else:
                    if   pass_input.type == 'RGBA':
                        emit.inputs[0].default_value[0] = pass_input.default_value[0] * multiplier + addend
                        emit.inputs[0].default_value[1] = pass_input.default_value[1] * multiplier + addend
                        emit.inputs[0].default_value[2] = pass_input.default_value[2] * multiplier + addend
                        emit.inputs[0].default_value[3] = pass_input.default_value[3] * multiplier + addend
                    elif pass_input.type == 'VECTOR':
                        emit.inputs[0].default_value[0] = pass_input.default_value[0] * multiplier + addend
                        emit.inputs[0].default_value[1] = pass_input.default_value[1] * multiplier + addend
                        emit.inputs[0].default_value[2] = pass_input.default_value[2] * multiplier + addend
                        emit.inputs[0].default_value[3] = 1
                    elif pass_input.type == 'VALUE':
                        emit.inputs[0].default_value[0] = pass_input.default_value * multiplier + addend
                        emit.inputs[0].default_value[1] = pass_input.default_value * multiplier + addend
                        emit.inputs[0].default_value[2] = pass_input.default_value * multiplier + addend
                        emit.inputs[0].default_value[3] = 1
                
    def passes_to_emit_node(self,obj,passes,multiplier,addend):
        for slot in obj.material_slots:
            nodes = slot.material.node_tree.nodes
            links = slot.material.node_tree.links
            
            ##### Find Output Node
            out = None
            for node in nodes:
                if node.type == 'OUTPUT_MATERIAL':
                    out = node
                    break
                
            if out:
            #### Modify Nodes
                self.passes_to_rgb(out,None,nodes,links,passes,multiplier,addend)
            else:
            #### Create Default Texture Nodes
                out = nodes.new(type = 'ShaderNodeOutputMaterial')
                emit = nodes.new(type = 'ShaderNodeEmission')
                final_value = 0.0 * multiplier + addend
                emit.inputs[0].default_value = final_value,final_value,final_value,final_value
                links.new(emit.outputs[0],out.inputs[0])
            
    def normal_to_rgb(self,node,src_socket,nodes,links,normal_socket):
        has_bsdf = False
        for input in node.inputs:
            if input.type == 'SHADER':
                has_bsdf = True
                if len(input.links):
                    self.normal_to_rgb(input.links[0].from_node,input,
                                    nodes,links,normal_socket)
                else:
                    emit = nodes.new(type = 'ShaderNodeEmission')
                    links.new(normal_socket,emit.inputs[0])
                    links.new(emit.outputs[0],input)
        
        if not has_bsdf:
            emit = nodes.new(type = 'ShaderNodeEmission')
            links.new(emit.outputs[0],src_socket)
            normal_input = node.inputs.get('Normal')
            if normal_input:
                if len(normal_input.links):
                    out_socket = normal_input.links[0].from_socket
                    add = nodes.new(type = 'ShaderNodeMixRGB')
                    div = nodes.new(type = 'ShaderNodeMixRGB')
                    add.blend_type = 'ADD'
                    div.blend_type = 'DIVIDE'
                    add.inputs[0].default_value = 1
                    div.inputs[0].default_value = 1
                    add.inputs[2].default_value = 1,1,1,1
                    div.inputs[2].default_value = 2,2,2,1
                    links.new(out_socket    ,add.inputs[1])
                    links.new(add.outputs[0],div.inputs[1])
                    links.new(div.outputs[0],emit.inputs[0])
                else:
                    links.new(normal_socket,emit.inputs[0])
            else:
                links.new(normal_socket,emit.inputs[0])
            
    def normals_to_emit_node(self,obj):
        for slot in obj.material_slots:
            nodes = slot.material.node_tree.nodes
            links = slot.material.node_tree.links
            
            ###### Create Default Normal Socket
            geo = nodes.new(type = 'ShaderNodeNewGeometry')
            add = nodes.new(type = 'ShaderNodeMixRGB')
            div = nodes.new(type = 'ShaderNodeMixRGB')
            add.blend_type = 'ADD'
            div.blend_type = 'DIVIDE'
            add.inputs[0].default_value = 1
            div.inputs[0].default_value = 1
            add.inputs[2].default_value = 1,1,1,1
            div.inputs[2].default_value = 2,2,2,1
            links.new(geo.outputs[1],add.inputs[1])
            links.new(add.outputs[0],div.inputs[1])
            normal_socket = div.outputs[0]
            
            ##### Find Output Node
            out = None
            for node in nodes:
                if node.type == 'OUTPUT_MATERIAL':
                    out = node
                    break
                
            if out:
            #### Modify Nodes
                self.normal_to_rgb(out,None,nodes,links,normal_socket)
            else:
            #### Create Default Normal Nodes
                out = nodes.new(type = 'ShaderNodeOutputMaterial')
                emit = nodes.new(type = 'ShaderNodeEmission')
                links.new(normal_socket,emit.inputs[0])
                links.new(emit.outputs[0],out.inputs[0])
            
            
    def create_normal_transfer_material(self,src_image,dst_image,normal_space):
        mat = bpy.data.materials.new('BAKELAB_NORMAL_TRANSFER_MAT')
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        src = nodes.new(type = 'ShaderNodeTexImage') # Source Image
        src.image = src_image
        mul = nodes.new(type = 'ShaderNodeMixRGB')
        sub = nodes.new(type = 'ShaderNodeMixRGB')
        mul.blend_type = 'MULTIPLY'
        sub.blend_type = 'SUBTRACT'
        mul.inputs[0].default_value = 1
        sub.inputs[0].default_value = 1
        mul.inputs[2].default_value = 2,2,2,1
        sub.inputs[2].default_value = 1,1,1,1
        links.new(src.outputs[0],mul.inputs[1])
        links.new(mul.outputs[0],sub.inputs[1])
        bump_normal = sub.outputs[0]
        
        if normal_space == 'TANGENT':
            geo = nodes.new(type = 'ShaderNodeNewGeometry')
            tan = nodes.new(type = 'ShaderNodeTangent')
            c_b = nodes.new(type = 'ShaderNodeVectorMath')
            tan.direction_type = 'UV_MAP'
            c_b.operation = 'CROSS_PRODUCT'
            normal = geo.outputs[1] # Normal
            tangent = tan.outputs[0] # Tangent
            binormal = c_b.outputs[0] # Binormal
            links.new(normal,c_b.inputs[0])
            links.new(tangent,c_b.inputs[1])
            
            d_t = nodes.new(type = 'ShaderNodeVectorMath')
            d_b = nodes.new(type = 'ShaderNodeVectorMath')
            d_n = nodes.new(type = 'ShaderNodeVectorMath')
            d_t.operation = 'DOT_PRODUCT'
            d_b.operation = 'DOT_PRODUCT'
            d_n.operation = 'DOT_PRODUCT'
            links.new(tangent, d_t.inputs[0])
            links.new(binormal,d_b.inputs[0])
            links.new(normal,  d_n.inputs[0])
            links.new(bump_normal,d_t.inputs[1])
            links.new(bump_normal,d_b.inputs[1])
            links.new(bump_normal,d_n.inputs[1])
            
            xyz = nodes.new(type = 'ShaderNodeCombineXYZ')
            links.new(d_t.outputs[1], xyz.inputs[0])
            links.new(d_b.outputs[1], xyz.inputs[1])
            links.new(d_n.outputs[1], xyz.inputs[2])
            final_normal_socket = xyz.outputs[0]
        else:
            w2o = nodes.new(type = 'ShaderNodeVectorTransform')
            w2o.vector_type  = 'NORMAL'
            w2o.convert_from = 'WORLD'
            w2o.convert_to   = 'OBJECT'
            links.new(bump_normal,w2o.inputs[0])
            final_normal_socket = w2o.outputs[0]
        add = nodes.new(type = 'ShaderNodeMixRGB')
        div = nodes.new(type = 'ShaderNodeMixRGB')
        gam = nodes.new(type = 'ShaderNodeGamma')
        emt = nodes.new(type = 'ShaderNodeEmission')
        out = nodes.new(type = 'ShaderNodeOutputMaterial')
        add.blend_type = 'ADD'
        div.blend_type = 'DIVIDE'
        add.inputs[0].default_value = 1
        div.inputs[0].default_value = 1
        add.inputs[2].default_value = 1,1,1,1
        div.inputs[2].default_value = 2,2,2,1
        gam.inputs[1].default_value = 2.2
        emt.inputs[1].default_value = 1
        links.new(final_normal_socket, add.inputs[1])
        links.new(add.outputs[0], div.inputs[1])
        links.new(div.outputs[0], gam.inputs[0])
        links.new(gam.outputs[0], emt.inputs[0])
        links.new(emt.outputs[0], out.inputs[0])
        
        dst = nodes.new(type = 'ShaderNodeTexImage') # Destination Image
        dst.image = dst_image
        for node in nodes:
            node.select = False
        dst.select = True
        nodes.active = dst
        
        return mat
        
    def generate_mat(self,name):
        new_mat = bpy.data.materials.new(name+'_BAKED')
        self.add_texs(name,new_mat)
        if bpy.context.scene.render.engine == 'CYCLES':
            new_mat.use_nodes = True
        else:
            new_mat.use_nodes = False
        return new_mat
        
    def add_texs(self,name,mat):
        #########################  BI materials  #####################################
        if self.BAKED_texture:
            slot = mat.texture_slots.add()
            slot.texture = bpy.data.textures.new(name+'_D',type = 'IMAGE')
            slot.texture.image = self.BAKED_texture.image
            slot.texture_coords = 'UV'
        if self.BAKED_normal:
            slot = mat.texture_slots.add()
            slot.texture = bpy.data.textures.new(name+'_N',type = 'IMAGE')
            slot.texture.image = self.BAKED_normal.image
            slot.texture.use_normal_map = True
            slot.use_map_color_diffuse = False
            slot.use_map_normal = True
            slot.normal_map_space = self.BAKED_normal.item.normal_space
            slot.texture_coords = 'UV'
        if self.BAKED_ambient:
            slot = mat.texture_slots.add()
            slot.texture = bpy.data.textures.new(name+'_AO',type = 'IMAGE')
            slot.texture.image = self.BAKED_ambient.image
            slot.blend_type = 'MULTIPLY'
            slot.texture_coords = 'UV'
        if self.BAKED_glossy:
            slot = mat.texture_slots.add()
            slot.texture = bpy.data.textures.new(name+'_S',type = 'IMAGE')
            slot.texture.image = self.BAKED_glossy.image
            slot.use_map_color_diffuse = False
            slot.use_map_color_spec = True
            slot.texture_coords = 'UV'
        if self.BAKED_full:
            for slot in mat.texture_slots:
                if slot:
                    slot.use = False
            slot = mat.texture_slots.add()
            slot.texture = bpy.data.textures.new(name+'_F',type = 'IMAGE')
            slot.texture.image = self.BAKED_full.image
            mat.use_shadeless = True
            slot.texture_coords = 'UV'
        if self.BAKED_alpha:
            slot = mat.texture_slots.add()
            slot.texture = bpy.data.textures.new(name+'_A',type = 'IMAGE')
            slot.texture.image = self.BAKED_alpha.image
            slot.use_map_color_diffuse = False
            slot.use_map_alpha = True
            mat.use_transparency = True
            mat.alpha = 0
            mat.specular_alpha = 0
            slot.texture_coords = 'UV'
        
        #########################  CYCLES materials  #################################
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        for node in nodes:
            nodes.remove(node)
        
        out = nodes.new(type = 'ShaderNodeOutputMaterial')
        out.location = 0,0
        pbr = nodes.new(type = 'ShaderNodeBsdfPrincipled')
        pbr.location = -200,400
        links.new(pbr.outputs[0],out.inputs[0])
        uvm = nodes.new(type = 'ShaderNodeTexCoord')
        uvm.location = -1500,400
        
        if self.BAKED_texture:
            imgNode = nodes.new(type = 'ShaderNodeTexImage')
            imgNode.location = -600,600
            imgNode.image = self.BAKED_texture.image
            links.new(imgNode.outputs[0],pbr.inputs[0])
            links.new(uvm.outputs[2],imgNode.inputs[0])
        if self.BAKED_normal:
            imgNode = nodes.new(type = 'ShaderNodeTexImage')
            imgNode.location = -600,-400
            imgNode.image = self.BAKED_normal.image
            imgNode.color_space = 'NONE'
            nmNode = nodes.new(type = 'ShaderNodeNormalMap')
            nmNode.location = -400,-200
            nmNode.space = self.BAKED_normal.item.normal_space
            if self.BAKED_normal.engine == 'BI' and self.BAKED_normal.item.normal_space == 'OBJECT':
                nmNode.space = 'BLENDER_OBJECT'
            links.new(imgNode.outputs[0],nmNode.inputs[1])
            links.new(nmNode.outputs[0],pbr.inputs[17])
            links.new(uvm.outputs[2],imgNode.inputs[0])
        if self.BAKED_ambient:
            imgNode = nodes.new(type = 'ShaderNodeTexImage')
            imgNode.location = -600,200
            imgNode.image = self.BAKED_ambient.image
            mul = nodes.new(type = 'ShaderNodeMixRGB')
            mul.location = -400,400
            mul.blend_type = 'MULTIPLY'
            mul.inputs[0].default_value = 1
            mul.inputs[1].default_value = 1,1,1,1
            mul.inputs[2].default_value = 1,1,1,1
            diff_socket = None
            if len(pbr.inputs[0].links):
                diff_socket = pbr.inputs[0].links[0].from_socket
            links.new(mul.outputs[0],pbr.inputs[0])
            links.new(imgNode.outputs[0],mul.inputs[2])
            links.new(uvm.outputs[2],imgNode.inputs[0])
            if diff_socket is not None:
                links.new(diff_socket,mul.inputs[1])
        if self.BAKED_glossy:
            imgNode = nodes.new(type = 'ShaderNodeTexImage')
            imgNode.location = -400,0
            imgNode.image = self.BAKED_glossy.image
            links.new(imgNode.outputs[0],pbr.inputs[5])
            links.new(uvm.outputs[2],imgNode.inputs[0])
        if self.BAKED_full:
            imgNode = nodes.new(type = 'ShaderNodeTexImage')
            imgNode.location = -600,1000
            imgNode.image = self.BAKED_full.image
            EmitNode = nodes.new(type = 'ShaderNodeEmission')
            EmitNode.location = -200,600
            links.new(imgNode.outputs[0],EmitNode.inputs[0])
            links.new(EmitNode.outputs[0],out.inputs[0])
            links.new(uvm.outputs[2],imgNode.inputs[0])
        if self.BAKED_alpha:
            if len(out.inputs[0].links):
                from_socket = out.inputs[0].links[0].from_socket
                transparent = nodes.new(type = 'ShaderNodeBsdfTransparent')
                transparent.location = -200, -100
                imgNode = nodes.new(type = 'ShaderNodeTexImage')
                imgNode.location = -200, -200
                imgNode.image = self.BAKED_alpha.image
                mix_shader = nodes.new(type = 'ShaderNodeMixShader')
                mix_shader.location = out.location[:]
                out.location[0] += 200
                links.new(imgNode.outputs[0],     mix_shader.inputs[0])
                links.new(transparent.outputs[0], mix_shader.inputs[1])
                links.new(from_socket,            mix_shader.inputs[2])
                links.new(mix_shader.outputs[0],  out.inputs[0])
                links.new(uvm.outputs[2],         imgNode.inputs[0])
                mat.game_settings.alpha_blend = 'ALPHA'
            
        ###### Custom Passes{
        node_y_shift = 500
        for baker in self.BAKED_passes:
            ####### Find Pass Input Socket{
            pass_input = None
            passes = baker.item.pass_name.split('|')
            for Pass in passes:
                pass_input = pbr.inputs.get(Pass)
                if pass_input: break
            if pass_input:
                if len(pass_input.links)==0:
                    node_x_shift = -800
                    pass_input_shift = pass_input
                    if baker.item.pass_multiplier != 1:
                        multiplier = baker.item.pass_multiplier
                        mul = nodes.new(type = 'ShaderNodeMixRGB')
                        mul.location = node_x_shift,node_y_shift
                        mul.inputs[0].default_value = 1
                        mul.blend_type = 'DIVIDE'
                        mul.inputs[2].default_value = multiplier,multiplier,multiplier,multiplier
                        links.new(mul.outputs[0],pass_input_shift)
                        pass_input_shift = mul.inputs[1]
                        node_x_shift -= 200
                    if baker.item.pass_addend != 0:
                        addend = baker.item.pass_addend
                        add = nodes.new(type = 'ShaderNodeMixRGB')
                        add.location = node_x_shift,node_y_shift
                        add.inputs[0].default_value = 1
                        if addend >= 0:
                            add.blend_type = 'SUBTRACT'
                            add.inputs[2].default_value = addend,addend,addend,addend
                        else:
                            add.blend_type = 'ADD'
                            add.inputs[2].default_value = -addend,-addend,-addend,-addend
                        links.new(add.outputs[0],pass_input_shift)
                        pass_input_shift = add.inputs[1]
                        node_x_shift -= 200
                    imgNode = nodes.new(type = 'ShaderNodeTexImage')
                    imgNode.location = node_x_shift,node_y_shift
                    imgNode.image = baker.image
                    links.new(imgNode.outputs[0],pass_input_shift)
                    links.new(uvm.outputs[2],imgNode.inputs[0])
                    node_y_shift -= 350
            ####### }
        ###### }
            
#######################################################################################

    def get_file_extension(self,format):
        extension = ''
        if format == 'PNG':
            extension = '.png'
        if format == 'JPEG':
            extension = '.jpg'
        if format == 'TARGA':
            extension = '.tar'
        if format == 'TIFF':
            extension = '.tiff'
        if format == 'BMP':
            extension = '.bmp'
        return extension

    def save_image(self,context,image,settings):
        if settings:
            img_settings = context.scene.render.image_settings
            img_settings.file_format = settings.format
            if settings.format == 'PNG':
                img_settings.color_mode  = settings.channels3
                img_settings.compression = settings.compression
                img_settings.color_depth = settings.c_depth
            if settings.format == 'JPEG':
                img_settings.color_mode = settings.channels2
                img_settings.quality    = settings.quality
            if settings.format == 'TARGA':
                img_settings.color_mode = settings.channels3
            if settings.format == 'TIFF':
                img_settings.color_mode  = settings.channels3
                img_settings.tiff_codec  = settings.tiff_codec
                img_settings.color_depth = settings.c_depth
        
        try:
            image.save()
            image.save_render(image.filepath,context.scene)
        except:
            self.report(type = {'ERROR'},
                    message = 'Could Not Save '+image.name+' to '+image.filepath)
            self.running = False

#######################################################################################
    def check_passes_enabled(self,settings,direct,indirect,color,combined):
        enabled = False
        if direct:
            if settings.use_pass_direct:
                enabled = True
        if indirect:
            if settings.use_pass_indirect:
                enabled = True
        if color:
            if settings.use_pass_color:
                enabled = True
        if not enabled:
            return False
        
        if combined:
            enabled = False
            if settings.use_pass_diffuse:
                enabled = True
            if settings.use_pass_glossy:
                enabled = True
            if settings.use_pass_transmission:
                enabled = True
            if settings.use_pass_subsurface:
                enabled = True
            if settings.use_pass_ambient_occlusion:
                enabled = True
            if settings.use_pass_emit:
                enabled = True
            if not enabled:
                return False
        return True
#######################################################################################
        
    def bake(self,context,obj_list,name,s_to_a):
        if self.bake_sub_step == 0 or self.bake_sub_step == 10:
            while True:
                if self.bake_item_id >= len(context.scene.BakeLabMapColl):
                    return True
                bake_item = context.scene.BakeLabMapColl[self.bake_item_id]
                if bake_item.enabled:
                    self.bake_sub_step = 1
                    break
                self.bake_item_id += 1
        else:
            bake_item = context.scene.BakeLabMapColl[self.bake_item_id]
            
        props = context.scene.BakeLabProps
        #### Final Variables{
        final_name = bake_item.img_name.replace('*',name)
        final_samples = bake_item.samples * self.sample_scale
        if self.override_image_size:
            final_image_width  = self.override_image_width * props.aa_samples
            final_image_height = self.override_image_height * props.aa_samples
        else:
            final_image_width  = bake_item.width  * self.image_scale * props.aa_samples
            final_image_height = bake_item.height * self.image_scale * props.aa_samples
        #### }
        if not self.img_cancelled and self.bake_sub_step >= 0:
            last_baked_image = self.current_image
            self.current_image = bpy.data.images.new(final_name,
                            width = final_image_width, height = final_image_height)
            self.current_image.filepath = props.out_path + \
                                self.current_image.name + \
                                self.get_file_extension(bake_item.format)
            self.current_image.file_format = bake_item.format
        
        ########################################################################
        if not self.img_cancelled:
            self.new_bake_sub_step = 0
            self.new_use_s_to_a = s_to_a
            if bake_item.engine == 'CYCLES':
                bpy.context.scene.render.engine = 'CYCLES'
                for obj in obj_list:
                    for slot in obj.material_slots:
                        mat = slot.material
                        if not mat: continue
                        mat.use_nodes = True
                if s_to_a:
                    active_obj = context.scene.objects.active
                    self.createTmpImageNodes(active_obj,self.current_image)
                else:
                    for obj in obj_list:
                        self.createTmpImageNodes(obj,self.current_image)
                
                bake_settings = context.scene.render.bake
                bake_settings.use_pass_direct   = bake_item.cycles_direct
                bake_settings.use_pass_indirect = bake_item.cycles_indirect
                bake_settings.use_pass_color    = bake_item.cycles_color
                        
                if   bake_item.type == 'Full':
                    bake_settings.use_pass_diffuse           = bake_item.cycles_diffuse
                    bake_settings.use_pass_glossy            = bake_item.cycles_glossy
                    bake_settings.use_pass_transmission      = bake_item.cycles_transmission
                    bake_settings.use_pass_subsurface        = bake_item.cycles_subsurface
                    bake_settings.use_pass_ambient_occlusion = bake_item.cycles_ambient_occlusion
                    bake_settings.use_pass_emit              = bake_item.cycles_emit
                    if not self.check_passes_enabled(bake_settings,True,True,False,True):
                        self.report(type = {'ERROR'},
                                message = 'Nothing to bake to '+final_name)
                        self.bake_sub_step = 0
                        self.bake_item_id += 1
                        return False
                    texture_type = 'COMBINED'
                elif bake_item.type == 'Diffuse':
                    if not self.check_passes_enabled(bake_settings,True,True,True,False):
                        self.report(type = {'ERROR'},
                                message = 'Nothing to bake to '+final_name)
                        self.bake_sub_step = 0
                        self.bake_item_id += 1
                        return False
                    texture_type = 'DIFFUSE'
                elif bake_item.type == 'Specular':
                    if not self.check_passes_enabled(bake_settings,True,True,True,False):
                        self.report(type = {'ERROR'},
                                message = 'Nothing to bake to '+final_name)
                        self.bake_sub_step = 0
                        self.bake_item_id += 1
                        return False
                    texture_type = 'GLOSSY'
                elif bake_item.type == 'Alpha':
                    if not self.check_passes_enabled(bake_settings,True,True,True,False):
                        self.report(type = {'ERROR'},
                                message = 'Nothing to bake to '+final_name)
                        self.bake_sub_step = 0
                        self.bake_item_id += 1
                        return False
                    texture_type = 'TRANSMISSION'
                elif bake_item.type == 'Subsurface':
                    if not self.check_passes_enabled(bake_settings,True,True,True,False):
                        self.report(type = {'ERROR'},
                                message = 'Nothing to bake to '+final_name)
                        self.bake_sub_step = 0
                        self.bake_item_id += 1
                        return False
                    texture_type = 'SUBSURFACE'
                elif bake_item.type == 'Emission':     texture_type = 'EMIT'
                elif bake_item.type == 'Ambient':      texture_type = 'AO'
                elif bake_item.type == 'Shadow':       texture_type = 'SHADOW'
                elif bake_item.type == 'UV':           texture_type = 'UV'
                elif bake_item.type == 'Environment':  texture_type = 'ENVIRONMENT'
                elif bake_item.type == 'Normal':
                    if bake_item.tricky:
                        texture_type = 'EMIT'
                        #################################################
                        if self.bake_sub_step == 1:
                            self.original_mats = []
                            self.old_active_render_uvs = []
                            self.current_image.name = 'TMP_WORLD_NORMAL_' + self.current_image.name
                            self.current_image.filepath = props.out_path + \
                                        self.current_image.name + \
                                        self.get_file_extension(bake_item.format)
                            for obj in obj_list:
                                if s_to_a:
                                    if obj == context.scene.objects.active:
                                        continue
                                active_render_uv = None
                                for uv in obj.data.uv_textures:
                                    if uv.active_render:
                                        active_render_uv = uv
                                self.old_active_render_uvs.append(active_render_uv)
                                for slot in obj.material_slots:
                                    self.original_mats.append(slot.material)
                                    slot.material = slot.material.copy()
                                    
                            for obj in obj_list:
                                if s_to_a:
                                    if obj == context.scene.objects.active:
                                        continue
                                self.normals_to_emit_node(obj)
                            self.new_bake_sub_step = 2
                        #################################################
                        elif self.bake_sub_step == 2:
                            self.trash_imgs.append(last_baked_image)
                            transfer_mat = self.create_normal_transfer_material(last_baked_image,
                                                    self.current_image,bake_item.normal_space)
                            if s_to_a:
                                self.new_use_s_to_a = False
                                active_obj = context.scene.objects.active
                                for obj in obj_list:
                                    if obj != active_obj:
                                        obj.select = False
                                active_obj.data.uv_textures.active.active_render = True
                                for slot in active_obj.material_slots:
                                    tmp_mat = slot.material
                                    slot.material = transfer_mat
                                    self.trash_mats.append(tmp_mat)
                            else:
                                for obj in obj_list:
                                    obj.data.uv_textures.active.active_render = True
                                    for slot in obj.material_slots:
                                        tmp_mat = slot.material
                                        slot.material = transfer_mat
                                        self.trash_mats.append(tmp_mat)
                            self.new_bake_sub_step = -1
                        #################################################
                        elif self.bake_sub_step == -1:
                            for uv in self.old_active_render_uvs:
                                if uv:
                                    uv.active_render = True
                            i = 0
                            for obj in obj_list:
                                obj.select = True
                                if s_to_a:
                                    if obj == context.scene.objects.active:
                                        continue
                                for slot in obj.material_slots:
                                    tmp_mat = slot.material
                                    slot.material = self.original_mats[i]
                                    self.trash_mats.append(tmp_mat)
                                    i += 1
                            self.new_bake_sub_step = 10
                    else:
                        context.scene.render.bake.normal_space = bake_item.normal_space
                        texture_type = 'NORMAL'
                elif bake_item.type in {'Texture','Passes'}:
                    texture_type = 'EMIT'
                    #################################################
                    if self.bake_sub_step == 1:
                        self.original_mats = []
                        for obj in obj_list:
                            if s_to_a:
                                if obj == context.scene.objects.active:
                                    continue
                            for slot in obj.material_slots:
                                self.original_mats.append(slot.material)
                                slot.material = slot.material.copy()
                                
                        for obj in obj_list:
                            if s_to_a:
                                if obj == context.scene.objects.active:
                                    continue
                            if bake_item.type == 'Texture':
                                self.passes_to_emit_node(obj,['Color','Base Color','Paint Color'],1,0)
                            else:
                                self.passes_to_emit_node(obj,bake_item.pass_name.split('|'),
                                                bake_item.pass_multiplier,bake_item.pass_addend)
                        self.new_bake_sub_step = -1
                    #################################################
                    elif self.bake_sub_step == -1:
                        i = 0
                        for obj in obj_list:
                            obj.select = True
                            if s_to_a:
                                if obj == context.scene.objects.active:
                                    continue
                            for slot in obj.material_slots:
                                tmp_mat = slot.material
                                slot.material = self.original_mats[i]
                                self.trash_mats.append(tmp_mat)
                                i += 1
                        self.new_bake_sub_step = 10
                else:
                    self.report(type = {'ERROR'},
                            message = 'Unknown Bake Type: '+bake_item.type)
                    self.bake_sub_step = 0
                    self.bake_item_id += 1
                    return False
            else:#####################################################################
                bpy.context.scene.render.engine = 'BLENDER_RENDER'
                for obj in obj_list:
                    for slot in obj.material_slots:
                        mat = slot.material
                        if not mat: continue
                        mat.use_nodes = False
                if s_to_a:
                    active_obj = context.scene.objects.active
                    for slot in active_obj.material_slots:
                        slot.material.use_nodes = False
                    for d in active_obj.data.uv_textures.active.data:
                        d.image = self.current_image
                else:
                    for obj in obj_list:
                        for slot in obj.material_slots:
                            slot.material.use_nodes = False
                        for d in obj.data.uv_textures.active.data:
                            d.image = self.current_image
                if   bake_item.type == 'Full':         texture_type = 'FULL'
                elif bake_item.type == 'Texture':      texture_type = 'TEXTURE'
                elif bake_item.type == 'Normal':
                    context.scene.render.bake_normal_space = bake_item.normal_space
                    texture_type = 'NORMALS'
                elif bake_item.type == 'Ambient':
                    if not context.scene.world:
                        self.report(type = {'ERROR'},message = 'No Active World')
                        self.bake_sub_step = 0
                        self.bake_item_id += 1
                        return False
                    context.scene.render.use_bake_normalize = bake_item.normalize
                    texture_type = 'AO'
                elif bake_item.type == 'Shadow':       texture_type = 'SHADOW'
                elif bake_item.type == 'Glossy':
                    if bake_item.gloss_type == 'SPECULAR':
                        if bake_item.gloss_data == 'INTENSITY':
                            texture_type = 'SPEC_INTENSITY'
                        else:
                            texture_type = 'SPEC_COLOR'
                    else:
                        if bake_item.gloss_data == 'INTENSITY':
                            texture_type = 'MIRROR_INTENSITY'
                        else:
                            texture_type = 'MIRROR_COLOR'
                elif bake_item.type == 'Emission':     texture_type = 'EMIT'
                elif bake_item.type == 'Alpha':        texture_type = 'ALPHA'
                elif bake_item.type == 'Displacement':
                    context.scene.render.use_bake_normalize = bake_item.normalize
                    texture_type = 'DISPLACEMENT'
                elif bake_item.type == 'Derivative':   texture_type = 'DERIVATIVE'
                elif bake_item.type == 'Vertex Col':   texture_type = 'VERTEX_COLORS'
                else:
                    self.report(type = {'ERROR'},
                            message = 'Unknown Bake Type: '+bake_item.type)
                    self.bake_sub_step = 0
                    self.bake_item_id += 1
                    return False
            ##############################################################################     
                
            if self.bake_sub_step >= 0:
                self.current_tex_baker = baker(texture_type, self.current_image, bake_item,
                                                          bake_item.engine, final_samples)
        if props.save_or_pack == 'SAVE':
            self.save_image(context,self.current_tex_baker.image,bake_item)
            if not self.running: return False
        else:
            self.current_tex_baker.image.pack(True)
        self.img_cancelled = False
        s_to_a = self.new_use_s_to_a
        
            
        if s_to_a:
            context.scene.render.use_bake_selected_to_active = True
            context.scene.render.bake.use_selected_to_active = True
        else:
            context.scene.render.use_bake_selected_to_active = False
            context.scene.render.bake.use_selected_to_active = False
            
        if self.bake_sub_step >= 0:
            if not self.current_tex_baker.bake():
                self.img_cancelled = True
                return False
        
        self.bake_sub_step = self.new_bake_sub_step
        if self.bake_sub_step == 0 or self.bake_sub_step == 10:
            self.bake_item_id += 1
        
        if   bake_item.type == 'Full':
            self.BAKED_full         = self.current_tex_baker
        if   bake_item.type == 'Texture':
            self.BAKED_texture      = self.current_tex_baker
        elif bake_item.type == 'Normal':
            self.BAKED_normal       = self.current_tex_baker
        elif bake_item.type == 'Ambient':
            self.BAKED_ambient      = self.current_tex_baker
        elif bake_item.type == 'Glossy':
            self.BAKED_glossy       = self.current_tex_baker
        elif bake_item.type == 'Alpha':
            self.BAKED_alpha        = self.current_tex_baker
        elif bake_item.type == 'Passes':
            self.BAKED_passes.append( self.current_tex_baker )
        
        return False
    
#######################################################################################

    def merge_objects(self,context,obj_list):
        merged_mesh = bpy.data.meshes.new('BAKELAB_MERGED_MESH_TMP')
        merged_obj  = bpy.data.objects.new('BAKELAB_MERGED_OBJ_TMP', merged_mesh)
        merged_obj.location = 0,0,0
        context.scene.objects.link(merged_obj)
        merged_mesh.update()
        
        for obj in obj_list:
            if obj.type != 'MESH':
                continue
            
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            context.scene.objects.active = obj
            bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
            obj_clone = context.scene.objects.active
            
            while len(obj_clone.vertex_groups):
                obj_clone.vertex_groups.remove(obj_clone.vertex_groups[0])
            v_group = obj_clone.vertex_groups.new(name = obj.name)
            v_group.add(list(range(len(obj_clone.data.vertices))),weight = 1,type = 'ADD')
            
            bpy.ops.object.select_all(action='DESELECT')
            merged_obj.select = True
            obj_clone.select  = True
            context.scene.objects.active = merged_obj
            clone_data = obj_clone.data
            bpy.ops.object.join()
            bpy.data.meshes.remove(clone_data)
        
        return merged_obj
    
    def separate_objects_and_merge_with_modifier(self,context,merged_obj,obj_list):
        new_merged_mesh = bpy.data.meshes.new('BAKELAB_NEW_MERGED_MESH_TMP')
        new_merged_obj  = bpy.data.objects.new('BAKELAB_NEW_MERGED_OBJ_TMP', new_merged_mesh)
        new_merged_obj.location = 0,0,0
        context.scene.objects.link(new_merged_obj)
        new_merged_mesh.update()
        
        for obj in obj_list:
            if obj.type != 'MESH':
                continue
            ##### Copy UV layers From Merged Object To Original Objects{
            if context.scene.BakeLabProps.newuv or not obj.data.uv_textures.active:
                bpy.ops.object.select_all(action='DESELECT')
                merged_obj.select = True
                context.scene.objects.active = merged_obj
                
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                merged_obj.vertex_groups.active_index = merged_obj.vertex_groups[obj.name].index
                bpy.ops.object.vertex_group_select()
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                
                for s_obj in context.selected_objects:
                    if s_obj != merged_obj:
                        separated_obj = s_obj
                
                bpy.ops.object.select_all(action='DESELECT')
                separated_obj.select = True
                obj.select           = True
                context.scene.objects.active = separated_obj
                new_uv = obj.data.uv_textures.new('UVMap_BAKELAB')
                obj.data.uv_textures.active = new_uv
                bpy.ops.object.join_uvs()
                obj.data.update()
                
                separated_data = separated_obj.data
                bpy.data.objects.remove(separated_obj)
                bpy.data.meshes.remove(separated_data)
            ##### }
            
            ##### Create New Merged Object{
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            context.scene.objects.active = obj
            bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
            obj_clone = context.scene.objects.active
            
            ########## Apply modifiers{
            for modifier in obj_clone.modifiers:
                if modifier.show_render:
                    if modifier.type == 'SUBSURF':
                        modifier.levels = modifier.render_levels
                    bpy.ops.object.modifier_apply(modifier = modifier.name)
            ########## }
            
            ########## Merge{
            bpy.ops.object.select_all(action='DESELECT')
            new_merged_obj.select = True
            obj_clone.select  = True
            context.scene.objects.active = new_merged_obj
            clone_data = obj_clone.data
            bpy.ops.object.join()
            bpy.data.meshes.remove(clone_data)
            ########## }
            ##### }
        
        ##################### Remove Merged Object
        merged_data = merged_obj.data
        bpy.data.objects.remove(merged_obj)
        bpy.data.meshes.remove(merged_data)
        return new_merged_obj
            
##############################################################################
    def prepare_next_object(self,context):
        self.BAKED_full = None
        self.BAKED_texture = None
        self.BAKED_normal = None
        self.BAKED_ambient = None
        self.BAKED_glossy = None
        self.BAKED_alpha = None
        self.BAKED_passes = []
        
        while True:
            if self.bake_obj_id>=len(self.bake_objs):
                self.next(context)
                return
            current_obj = self.bake_objs[self.bake_obj_id]
            self.bake_obj_id+=1
            if current_obj.type=='MESH':
                bpy.ops.object.select_all(action = 'DESELECT')
                current_obj.select = True
                context.scene.objects.active = current_obj
                self.unwrap(context.scene.BakeLabProps,current_obj)
                if self.check_uv_data(context):
                    break
                else:
                    self.report(type = {'WARNING'},message = 'Cound not unwrap '+current_obj.name)
        
        self.add_empty_mat(current_obj)
        self.tmp_use_nodes = [i.material.use_nodes for i in current_obj.material_slots]
        self.bake_item_id = 0
        self.current_image = None
        self.current_objs.clear()
        self.current_objs.append(current_obj)
        
##############################################################################
    
    def check_uv_data(self,context):
        object = context.scene.objects.active
        if not len(object.modifiers):
            if object.data.uv_textures.active:
                return True
            else:
                return False
            
        selected_objects = [obj for obj in context.selected_objects]
        bpy.ops.object.select_all(action='DESELECT')
        object.select = True
        context.scene.objects.active = object
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        obj_clone = context.scene.objects.active
        
        ########## Apply modifiers{
        for modifier in obj_clone.modifiers:
            if modifier.show_render:
                if modifier.type == 'SUBSURF':
                    modifier.levels = modifier.render_levels
                bpy.ops.object.modifier_apply(modifier = modifier.name)
        ########## }
        
        has_uv = obj_clone.data.uv_textures.active is not None
        
        bpy.ops.object.select_all(action='DESELECT')
        context.scene.objects.active = object
        for obj in selected_objects:
            obj.select = True
        clone_data = obj_clone.data
        bpy.data.objects.remove(obj_clone)
        bpy.data.meshes.remove(clone_data)
        return has_uv
        
##############################################################################
    def down_scale(self,img,val):
        if val == 1: return
        img.scale(img.size[0]/val,img.size[1]/val)
##############################################################################
    
    def manage_baking(self,context,event):
        scene = context.scene
        props = context.scene.BakeLabProps
        s_to_a = props.s_to_a
        
        if self.current_image:
            if not self.current_image.is_dirty:
                if not self.img_cancelled and \
                        self.bake_sub_step < 10:
                    return
            else:
                self.down_scale(self.current_image,props.aa_samples)
                if props.save_or_pack == 'SAVE':
                    self.save_image(context,self.current_image,None)
                    if not self.running: return
                else:
                    self.current_image.pack(True)
        
        if not s_to_a:
            if props.all_in_one:
                bake_cancel = False
                if not len(self.current_objs):
                    self.BAKED_full = None
                    self.BAKED_texture = None
                    self.BAKED_normal = None
                    self.BAKED_ambient = None
                    self.BAKED_glossy = None
                    self.BAKED_alpha = None
                    self.BAKED_passes = []
                    
                    self.merged_obj = self.merge_objects(context,self.bake_objs)
                    self.merged_obj.select = True
                    context.scene.objects.active = self.merged_obj
                    self.unwrap(context.scene.BakeLabProps,self.merged_obj)
                    self.merged_obj = self.separate_objects_and_merge_with_modifier(
                                                context,self.merged_obj,self.bake_objs)
                    scene.objects.active = self.merged_obj
                    self.merged_obj.select = True
                    bake_cancel = not self.check_uv_data(context)
                    
                    if not bake_cancel:
                        self.current_objs.clear()
                        self.tmp_use_nodes = []
                        for obj in self.bake_objs:
                            if obj.type != 'MESH': continue
                            bpy.ops.object.select_all(action = 'DESELECT')
                            obj.select = True
                            scene.objects.active = obj
                            
                            self.current_objs.append(obj)
                            self.add_empty_mat(obj)
                            for slot in obj.material_slots:
                                self.tmp_use_nodes.append(slot.material.use_nodes)
                                
                        bpy.ops.object.select_all(action = 'DESELECT')
                        scene.objects.active = self.merged_obj
                        self.merged_obj.select = True
                        while len(self.merged_obj.material_slots)>0:
                            bpy.ops.object.material_slot_remove()
                        self.add_empty_mat(self.merged_obj)
                        for obj in self.current_objs:
                            obj.select = True
                            
                        self.current_image = None
                        
                if bake_cancel: ##### Cancel
                    self.report(type = {'WARNING'},message = 'Cound not unwrap objects')
                    ##################### Remove Merged Object
                    if self.merged_obj:
                        merged_data = self.merged_obj.data
                        bpy.data.objects.remove(self.merged_obj)
                        bpy.data.meshes.remove(merged_data)
                    self.next(context)
                    return
                else: ##### Bake
                    if self.main_name: output_name = self.main_name
                    else:              output_name = props.general_name
                    
                    if self.bake(context,self.current_objs,output_name,True):
                        new_mat = None
                        if props.gen_mat:
                            new_mat = self.generate_mat(output_name)
                        i = 0
                        for obj in self.current_objs:
                            for slot in obj.material_slots:
                                slot.material.use_nodes = self.tmp_use_nodes[i]
                                i += 1
                            ##### Append Material{
                            if props.gen_mat and props.append_mat:
                                scene.objects.active = obj
                                bpy.ops.object.material_slot_add()
                                obj.material_slots[-1].material = new_mat
                            ##### }
                            
                        ##################### Remove Merged Object
                        if self.merged_obj:
                            merged_data = self.merged_obj.data
                            bpy.data.objects.remove(self.merged_obj)
                            bpy.data.meshes.remove(merged_data)
                        
                        self.next(context)
                        return
            else:
                if not len(self.current_objs):
                    self.prepare_next_object(context)
                    if not self.running: return
                if self.bake(context,self.current_objs,self.current_objs[0].name,False):
                    self.removeTmpImageNodes(self.current_objs)
                    for i in range(len(self.tmp_use_nodes)):
                        self.current_objs[0].material_slots[i].material.use_nodes = self.tmp_use_nodes[i]
                    
                    ##### Generate and Append Material{
                    if props.gen_mat:
                        new_mat = self.generate_mat(self.current_objs[0].name)
                        if props.append_mat:
                            bpy.ops.object.material_slot_add()
                            self.current_objs[0].material_slots[-1].material = new_mat
                    ##### }
                    self.prepare_next_object(context)
        else:
            bake_cancel = False
            if not len(self.current_objs):
                self.BAKED_full = None
                self.BAKED_texture = None
                self.BAKED_normal = None
                self.BAKED_ambient = None
                self.BAKED_glossy = None
                self.BAKED_alpha = None
                self.BAKED_passes = []
            
                active_obj = scene.objects.active
                self.unwrap(context.scene.BakeLabProps,active_obj)
                bake_cancel = not self.check_uv_data(context)
                
                if not bake_cancel:
                    self.current_objs.clear()
                    self.tmp_use_nodes = []
                    for obj in self.bake_objs:
                        if obj.type != 'MESH': continue
                        bpy.ops.object.select_all(action = 'DESELECT')
                        obj.select = True
                        scene.objects.active = obj
                        
                        self.current_objs.append(obj)
                        self.add_empty_mat(obj)
                        for slot in obj.material_slots:
                            self.tmp_use_nodes.append(slot.material.use_nodes)
                            
                    for obj in self.current_objs:
                        obj.select = True
                        
                    scene.objects.active = active_obj
                    self.current_image = None
                
            if bake_cancel:
                self.report(type = {'WARNING'},message = 'Cound not unwrap '+scene.objects.active.name)
                self.next(context)
                return
            else:
                if self.main_name: output_name = self.main_name
                else:              output_name = scene.objects.active.name
                
                if self.bake(context,self.current_objs,output_name,True):
                    i = 0
                    for obj in self.current_objs:
                        for slot in obj.material_slots:
                            slot.material.use_nodes = self.tmp_use_nodes[i]
                            i += 1
                            
                    ##### Generate and Append Material{
                    if props.gen_mat:
                        new_mat = self.generate_mat(output_name)
                        if props.append_mat:
                            bpy.ops.object.material_slot_add()
                            scene.objects.active.material_slots[-1].material = new_mat
                    ##### }
                    
                    self.next(context)
                    return
##############################################################################
                
    def modal(self,context,event):
        if not self.running:
            self.finish(context)
            return {'FINISHED'}
        
        if event.type in {'ESC'}:
            self.finish(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            self.manage_baking(context,event)

        return {'RUNNING_MODAL'}
        
    def init(self):
        self.current_image = None
        self.current_objs = []
        self.merged_obj = None
        self.bake_obj_id = 0
        self.bake_item_id = 0
        self.running = True
        self.img_cancelled = False
        self.bake_sub_step = 0
        
        self.main_name = None
        self.image_scale = 1.0
        self.override_image_size = False
        self.override_image_width = 1024
        self.override_image_height = 1024
        self.sample_scale = 1.0
        
    def manage_linked_datas(self,context,solution):
        if solution == 'MAKE_SINGLE_USER':
            for obj in context.selected_objects:
                if obj.type != 'MESH': continue
                if obj.data.users>1:
                    obj.data = obj.data.copy()
        elif solution == 'EXCLUDE':
            data_list = []
            active_obj = context.scene.objects.active
            if active_obj:
                if active_obj.type == 'MESH':
                    data_list.append(active_obj.data)
            for obj in context.selected_objects:
                if obj.type != 'MESH': continue
                if obj == active_obj: continue
                if obj.data.users>1:
                    if obj.data in data_list:
                        obj.select = False
                        continue
                data_list.append(obj.data)
        
    def execute(self,context):
        self.save_defaults(context)
        props = context.scene.BakeLabProps
        
        self.empty_mat = None
        self.trash_mats = []
        self.trash_imgs = []
        self.all_baked_objs = []
        self.init()
        if props.use_list:
            if not len(context.scene.BakeLabObjColl):
                self.report(type = {'WARNING'},message = 'Add Some Objects to List')
                return {'CANCELLED'}
            
            self.ObjListIndex = 0
            while True:
                if self.ObjListIndex>=len(context.scene.BakeLabObjColl):
                    self.report(type = {'WARNING'},message = 'No Objects Found')
                    return {'CANCELLED'}
                obj_list = context.scene.BakeLabObjColl[self.ObjListIndex]
                if obj_list.enabled:
                    bpy.ops.object.select_all(action='DESELECT')
                    for obj in obj_list.objects:
                        if obj.object:
                            if obj.object.type == 'MESH':
                                obj.object.select = True
                    context.scene.objects.active = obj_list.active
                    if obj_list.active:
                        obj_list.active.select = True
                    self.manage_linked_datas(context,props.linked_datas)
                    
                    #### Check Validity of the List{
                    if props.s_to_a:
                        if not obj_list.active:
                            self.ObjListIndex += 1
                            continue
                        if obj_list.active.type != 'MESH':
                            self.ObjListIndex += 1
                            continue
                        if len(context.selected_objects)<2:
                            self.ObjListIndex += 1
                            continue
                        
                        context.scene.render.bake.use_cage       = props.use_cage
                        context.scene.render.bake_distance       = props.cage_extrusion * obj_list.ray_scale
                        context.scene.render.bake.cage_extrusion = props.cage_extrusion * obj_list.ray_scale
                        context.scene.render.bake.cage_object    = ''
                    else:
                        if len(context.selected_objects)<1:
                            self.ObjListIndex += 1
                            continue
                        context.scene.render.bake.use_cage       = False
                        context.scene.render.bake_distance       = props.ray_limit * obj_list.ray_scale
                        context.scene.render.bake.cage_extrusion = props.ray_limit * obj_list.ray_scale
                    #### }
                    
                    self.main_name             = obj_list.name
                    self.image_scale           = obj_list.image_scale
                    self.override_image_size   = obj_list.override_size
                    self.override_image_width  = obj_list.width
                    self.override_image_height = obj_list.height
                    self.sample_scale          = obj_list.sample_scale
                
                    self.ObjListIndex += 1
                    break
                self.ObjListIndex += 1
        else:
            if len(context.selected_objects)==0:
                self.report(type = {'WARNING'},message = 'Nothing selected')
                return {'CANCELLED'}
            for obj in context.selected_objects:
                if obj.type != 'MESH':
                    obj.select = False
            if context.scene.objects.active:
                context.scene.objects.active.select = True
            self.manage_linked_datas(context,props.linked_datas)
            
            if props.s_to_a:
                if len(context.selected_objects)<2:
                    self.report(type = {'WARNING'},message = 'Select Two or More Mesh Objects')
                    return {'CANCELLED'}
                if not context.scene.objects.active:
                    self.report(type = {'WARNING'},message = 'Active Object Not Found')
                    return {'CANCELLED'}
                if context.scene.objects.active.type != 'MESH':
                    self.report(type = {'WARNING'},message = 'Active Object Is Not a Mesh')
                    return {'CANCELLED'}
                context.scene.render.bake.use_cage       = props.use_cage
                context.scene.render.bake_distance       = props.cage_extrusion
                context.scene.render.bake.cage_extrusion = props.cage_extrusion
                context.scene.render.bake.cage_object    = ''
            else:
                context.scene.render.bake.use_cage       = False
                context.scene.render.bake_distance       = props.ray_limit
                context.scene.render.bake.cage_extrusion = props.ray_limit
        self.bake_objs = [i for i in context.selected_objects]
        if props.s_to_a:
            self.all_baked_objs.append(context.scene.objects.active)
        else:
            self.all_baked_objs.extend(self.bake_objs)
        
        context.scene.cycles.device = props.compute_device
        context.scene.render.bake_margin = props.bake_margin
        context.scene.render.bake.margin = props.bake_margin
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, context.window)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
                                                    BakeLab_DrawCallback,(self,context),
                                                    'WINDOW','POST_PIXEL')
        wm.modal_handler_add(self)
    
        return {'RUNNING_MODAL'}
    
    def next(self,context):
        props = context.scene.BakeLabProps
        if props.use_list:
            while True:
                if self.ObjListIndex>=len(context.scene.BakeLabObjColl):
                    break
                obj_list = context.scene.BakeLabObjColl[self.ObjListIndex]
                if obj_list.enabled:
                    bpy.ops.object.select_all(action='DESELECT')
                    for obj in obj_list.objects:
                        if obj.object:
                            if obj.object.type == 'MESH':
                                obj.object.select = True
                    context.scene.objects.active = obj_list.active
                    if obj_list.active:
                        obj_list.active.select = True
                    self.manage_linked_datas(context,props.linked_datas)
                    
                    #### Check Validity of the List{
                    if props.s_to_a:
                        if not obj_list.active:
                            self.ObjListIndex += 1
                            continue
                        if obj_list.active.type != 'MESH':
                            self.ObjListIndex += 1
                            continue
                        if len(context.selected_objects)<2:
                            self.ObjListIndex += 1
                            continue
                        context.scene.render.bake.use_cage       = props.use_cage
                        context.scene.render.bake_distance       = props.cage_extrusion * obj_list.ray_scale
                        context.scene.render.bake.cage_extrusion = props.cage_extrusion * obj_list.ray_scale
                        context.scene.render.bake.cage_object    = ''
                    else:
                        if len(context.selected_objects)<1:
                            self.ObjListIndex += 1
                            continue
                        context.scene.render.bake.use_cage       = False
                        context.scene.render.bake_distance       = props.ray_limit * obj_list.ray_scale
                        context.scene.render.bake.cage_extrusion = props.ray_limit * obj_list.ray_scale
                    #### }
                    
                    self.init()
                    self.bake_objs = [i for i in context.selected_objects]
                    if props.s_to_a:
                        self.all_baked_objs.append(context.scene.objects.active)
                    else:
                        self.all_baked_objs.extend(self.bake_objs)
                    self.main_name             = obj_list.name
                    self.image_scale           = obj_list.image_scale
                    self.override_image_size   = obj_list.override_size
                    self.override_image_width  = obj_list.width
                    self.override_image_height = obj_list.height
                    self.sample_scale          = obj_list.sample_scale
                    self.ObjListIndex += 1
                    return
                self.ObjListIndex += 1
        self.running = False

    def finish(self, context):
        props = context.scene.BakeLabProps
        self.running = False
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        
        for obj in self.all_baked_objs:
            if not obj:            continue
            if obj.type != 'MESH': continue
        
            if props.gen_mat and props.append_mat:
                if obj.data.uv_textures.active:
                    obj.data.uv_textures.active.active_render = True
                ##############################  Remove Unused UV Layers{
                if props.deluvs:
                    curr_uv = 0
                    uv_texs = obj.data.uv_textures
                    uvs_len = len(uv_texs)
                    while curr_uv<uvs_len:
                        if uv_texs.active != uv_texs[curr_uv]:
                            uv_texs.remove(uv_texs[curr_uv])
                            uvs_len-=1
                        else:
                            curr_uv+=1
                #########}
            
            ##############################  Remove Unused Material Slots{
            if props.gen_mat and props.append_mat:
                context.scene.objects.active = obj
                obj.active_material_index = 0
                while len(obj.material_slots)>1:
                    bpy.ops.object.material_slot_remove()
            #######}
            
                
        self.restore_defaults(context)
        if props.gen_mat and props.append_mat:
            for obj in self.all_baked_objs:
                if obj.type != 'MESH': continue
                for slot in obj.material_slots:
                    if slot.material:
                        if bpy.context.scene.render.engine == 'CYCLES':
                            slot.material.use_nodes = True
                        else:
                            slot.material.use_nodes = False
                        
        ####### Clear Trashes{
        for mat in self.trash_mats:
            if mat:
                bpy.data.materials.remove(mat)
        for img in self.trash_imgs:
            if img:
                bpy.data.images.remove(img)
        ####### }
    
################################################################
################################################################

class BakeLabAddMapItem(bpy.types.Operator):
    """Add a new bake map"""
    bl_idname = "bakelab.newmapitem"
    bl_label = "Add bake map"
    bl_options = {'REGISTER','UNDO'}
    
    type = bpy.props.EnumProperty(
            name = 'Type',
            items =  (('Full',        'Full',''),
                      ('Texture',     'Texture',''),
                      ('Normal',      'Normal',''),
                      ('Ambient',     'Ambient',''),
                      ('Shadow',      'Shadow',''),
                      ('Glossy',      'Glossy',''),
                      ('Emission',    'Emission',''),
                      ('Alpha',       'Alpha/Transmission',''),
                      ('Displacement','Displacement (BI Only)',''),
                      ('Derivative',  'Derivative (BI Only)',''),
                      ('Vertex Col',  'Vertex Colors (BI Only)',''),
                      ('UV',          'UV (Cycles Only)',''),
                      ('Diffuse',     'Diffuse (Cycles Only)',''),
                      ('Environment', 'Environment (Cycles Only)',''),
                      ('Subsurface',  'Subsurface (Cycles Only)',''),
                      ('Passes',      'Custom Passes (Cycles Only)','')))
    width = bpy.props.IntProperty(name = 'Width',default = 1024,
                                    min = 1, soft_max = 16384)
    height = bpy.props.IntProperty(name = 'Height',default = 1024,
                                    min = 1, soft_max = 16384)
    format = bpy.props.EnumProperty(
            name = 'Format',
            items =  (('PNG','png',''),
                    ('JPEG','jpg',''),
                    ('TARGA','tar',''),
                    ('TIFF','tiff',''),
                    ('BMP','bmp','')))
                    
    def calcItemSettings(self,context,item):
        if context.scene.render.engine == 'CYCLES':
            item.engine = 'CYCLES'
        else:
            item.engine = 'BI'
            
        if self.type == 'Full':
            item.img_name = '*_f'
            if item.engine == 'CYCLES':
                item.samples  = 32
            else:
                item.samples  = 16
        if self.type == 'Texture':
            item.img_name = '*_t'
            item.samples  = 6
        if self.type == 'Normal':
            item.img_name = '*_n'
            item.samples  = 6
        if self.type == 'Ambient':
            item.img_name = '*_ao'
            item.normalize = True
            if item.engine == 'CYCLES':
                item.samples  = 32
            else:
                item.samples  = 16
        if self.type == 'Shadow':
            item.img_name = '*_sh'
            item.samples  = 12
        if self.type == 'Displacement':
            item.img_name = '*_h'
            item.normalize = False
        if self.type == 'Glossy':
            item.img_name = '*_s'
            item.samples  = 12
        if self.type == 'Diffuse':
            item.img_name = '*_d'
            item.samples  = 12
        if self.type == 'Emission':
            item.img_name = '*_e'
            item.samples  = 6
        if self.type == 'Alpha':
            item.img_name = '*_a'
            item.samples  = 8
        if self.type == 'Derivative':
            item.img_name = '*_dr'
        if self.type == 'Vertex Col':
            item.img_name = '*_vcol'
        if self.type == 'UV':
            item.img_name = '*_uv'
            item.samples  = 2
        if self.type == 'Environment':
            item.img_name = '*_env'
            item.samples  = 6
        if self.type == 'Subsurface':
            item.img_name = '*_sss'
            item.samples  = 32
        if self.type == 'Passes':
            item.img_name = '*_pass'
            item.samples  = 6
    
    def execute(self,context):
        context.area.tag_redraw()
        item = context.scene.BakeLabMapColl.add()
        item.type   = self.type
        item.width  = self.width
        item.height = self.height
        item.format = self.format
        self.calcItemSettings(context,item)
        context.scene.BakeLabMapListIndex=len(context.scene.BakeLabMapColl)-1
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
class BakeLabRemoveMapItem(bpy.types.Operator):
    """Remove selected bake map"""
    bl_idname = "bakelab.removemapitem"
    bl_label = "remove bake map"
    bl_options = {'REGISTER','UNDO'}
    
    @classmethod
    def poll(cls,context):
        return context.scene.BakeLabMapColl
    
    def execute(self,context):
        context.area.tag_redraw()
        context.scene.BakeLabMapColl.remove(context.scene.BakeLabMapListIndex)
        context.scene.BakeLabMapListIndex = max(context.scene.BakeLabMapListIndex - 1,0)
        context.scene.BakeLabMapListIndex = min(context.scene.BakeLabMapListIndex,len(context.scene.BakeLabMapColl))
        return {'FINISHED'}

################################################################

class BakeLabAddObjItem(bpy.types.Operator):
    """Add a new bake object list"""
    bl_idname = "bakelab.newobjitem"
    bl_label = "Add bake object list"
    bl_options = {'REGISTER','UNDO'}
    name = bpy.props.StringProperty(name = 'Group Name',default = 'Group')
    
    def execute(self,context):
        context.area.tag_redraw()
        item = context.scene.BakeLabObjColl.add()
        item.name   = self.name
        item.active = context.scene.objects.active
        for obj in context.selected_objects:
            item.objects.add().object = obj
        context.scene.BakeLabMapListIndex=len(context.scene.BakeLabMapColl)-1
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
class BakeLabRemoveObjItem(bpy.types.Operator):
    """Remove selected bake object list"""
    bl_idname = "bakelab.removeobjitem"
    bl_label = "remove bake object list"
    bl_options = {'REGISTER','UNDO'}
    
    @classmethod
    def poll(cls,context):
        return context.scene.BakeLabObjColl
    
    def execute(self,context):
        context.area.tag_redraw()
        context.scene.BakeLabObjColl.remove(context.scene.BakeLabObjListIndex)
        context.scene.BakeLabObjListIndex = max(context.scene.BakeLabObjListIndex - 1,0)
        context.scene.BakeLabObjListIndex = min(context.scene.BakeLabObjListIndex,len(context.scene.BakeLabObjColl))
        return {'FINISHED'}
    
class BakeLabSelectObjItem(bpy.types.Operator):
    """Select Objects"""
    bl_idname = "bakelab.selectobjitem"
    bl_label = "Select Objects"
    bl_options = {'REGISTER','UNDO'}
    
    @classmethod
    def poll(cls,context):
        return context.scene.BakeLabObjColl
    
    def execute(self,context):
        context.area.tag_redraw()
        bpy.ops.object.select_all(action='DESELECT')
        scene = context.scene
        item = scene.BakeLabObjColl[scene.BakeLabObjListIndex]
        for obj_col in item.objects:
            if obj_col.object:
                obj_col.object.select = True
        scene.objects.active = item.active
        return {'FINISHED'}
    
################################################################

class BakeLabShowPassPresets(bpy.types.Operator):
    """Show Presets"""
    bl_idname = "bakelab.pass_presets"
    bl_label = "BakeLab Show Pass Presets"
    pass_presets = bpy.props.EnumProperty(
            name   = 'Pass Presets',
            items  =  (('Color|Base Color|Paint Color',    'Color',''),
                      ('Metallic',     'Metallic',''),
                      ('Specular',     'Specular',''),
                      ('Roughness',    'Roughness',''),
                      ('Anisotropic',  'Anisotropic',''),
                      ('Sheen',        'Sheen',''),
                      ('Clearcoat',    'Clearcoat',''),
                      ('Transmission', 'Transmission ','')))
    
    def execute(self,context):
        context.area.tag_redraw()
        scene = context.scene
        if scene.BakeLabMapListIndex>=0 and scene.BakeLabMapColl:
            item = scene.BakeLabMapColl[scene.BakeLabMapListIndex]
            if item:
                item.pass_name = self.pass_presets
        return {'FINISHED'}

################################################################
    
class BakeLabProperties(bpy.types.PropertyGroup):
    use_list         = bpy.props.BoolProperty(name = 'Use Object Lists',
                    description = 'Use List of Objects Instead of Selected Objects',
                    default = False)
    obj_list_settings = bpy.props.BoolProperty(name = '',
                    description = 'Show Settings',
                    default = False)
                    
    s_to_a           = bpy.props.BoolProperty(name = 'Selected to Active',
                    description = 'Bake From Selected Objects to Active Object',
                    default = False)
    s_to_a_settings  = bpy.props.BoolProperty(name = '',
                    description = 'Show Settings',
                    default = False)
    use_cage         = bpy.props.BoolProperty(name = 'Use Cage Extrusion',
                    description = 'Extrude Object Along Normals Before Baking(Only Cycles)',
                    default = False)
    cage_extrusion   = bpy.props.FloatProperty(name = '',
                    default = 0.0,
                    min = 0)
                    
    all_in_one       = bpy.props.BoolProperty(name = 'All In One',
                    description = 'Bake Maps of All Objects Into One Image',
                    default = False)
    a_in_1_settings  = bpy.props.BoolProperty(name = '',
                       description = 'Show Settings',
                       default = False)
    general_name     = bpy.props.StringProperty(name = 'General Name',default = 'General_Objects')
    ray_limit      = bpy.props.FloatProperty(name = 'Ray Limit',
                    description = 'Ray Limit',
                    default = 0.01,
                    min = 0)
                    
    unwrap_mode      = bpy.props.EnumProperty(
            name = 'Unwrap mode',
            items =  (('smart_uv','Smart Project',''),
                      ('lightmap','LightMap Project','')))
    unwrap_settings  = bpy.props.BoolProperty(name = '',
                       description = 'Show Settings',
                       default = False)
                    
    smart_uv_angle   = bpy.props.FloatProperty(name = 'Angle',
                    description = 'Angle Limit',
                    default = 66,
                    min = 1,
                    max = 89)
    smart_uv_margin  = bpy.props.FloatProperty(name = 'Margin',
                    description = 'Island Margin',
                    default = 0.02,
                    min = 0,
                    max = 1)
                    
    lightmap_quality = bpy.props.IntProperty(name = 'Quality',
                    description = 'Pack Quality',
                    default = 12,
                    min = 1,
                    max = 48)
    lightmap_margin  = bpy.props.FloatProperty(name = 'Margin',
                    description = 'Margin',
                    default = 0.1,
                    min = 0,
                    max = 1)
    newuv  = bpy.props.BoolProperty(name = 'New UV layer',default = True)
    deluvs = bpy.props.BoolProperty(name = 'Remove Old UVs',default = False)
    compute_device   = bpy.props.EnumProperty(
            name = 'Device',
            description = 'Compute Device',
            items =  (('GPU','GPU (If Supported)',''),
                      ('CPU','CPU','')))
    linked_datas   = bpy.props.EnumProperty(
            name = 'Linked Datas',
            description = 'What to do with multi user data objects',
            items =  (('MAKE_SINGLE_USER','Make Single User',''),
                      ('EXCLUDE','Exclude Copies','')))
    aa_samples   = bpy.props.IntProperty(name = 'Anti-Aliasing',
                    default = 1,
                    min = 1,
                    soft_max = 8,
                    max = 64)
    bake_margin    = bpy.props.IntProperty(name = 'Bake Margin',
                    description = 'Extends the baked result as a post process filter',
                    default = 16,
                    min = 0,
                    max = 64)
    gen_mat  = bpy.props.BoolProperty(name = 'Generate Materials',
                    description = 'Generate New Materials Based On Baked Images',
                    default = True)
    append_mat  = bpy.props.BoolProperty(name = 'Append Materials',
                    description = 'Append Generated Materials to Objects',
                    default = True)
    save_or_pack = bpy.props.EnumProperty(
            items =  (('SAVE','Save Images',''),
                    ('PACK','Pack Images','')),
            default = 'SAVE')
    out_path     = bpy.props.StringProperty(
            default="C:\\",
            name="Output",
            subtype="FILE_PATH"
            )
            
class BakeLabObjectListCollection(bpy.types.PropertyGroup):
    object = bpy.props.PointerProperty(type = bpy.types.Object)
            
class BakeLabObjectCollection(bpy.types.PropertyGroup):
    enabled = bpy.props.BoolProperty(name = '',default = True)
    name = bpy.props.StringProperty(name = 'List Name',default = 'Group')
    objects = bpy.props.CollectionProperty(type = BakeLabObjectListCollection)
    active = bpy.props.PointerProperty(type = bpy.types.Object)
    image_scale = bpy.props.FloatProperty(name = 'Image Scale',
                    description = 'Scale of Image (Image Size * Scale)',
                    default = 1,
                    min = 0,
                    soft_max = 16)
    override_size = bpy.props.BoolProperty(name = 'Override Image Size',default = False)
    width = bpy.props.IntProperty(name = 'Width',default = 1024,
                                    min = 1, soft_max = 16384)
    height = bpy.props.IntProperty(name = 'Height',default = 1024,
                                    min = 1, soft_max = 16384)
    sample_scale = bpy.props.FloatProperty(name = 'Sample Scale',
                    description = 'Scale of Samples (Amount of Samples * Scale)',
                    default = 1,
                    min = 0,
                    soft_max = 64)
    ray_scale   = bpy.props.FloatProperty(name = '',
                    default = 1.0,
                    min = 0)
            
class BakeLabMapCollection(bpy.types.PropertyGroup):
    enabled = bpy.props.BoolProperty(name = '',default = True)
    engine = bpy.props.EnumProperty(
            name = 'Engine',
            items =  (('BI',    'Blender Internal',''),
                      ('CYCLES','Cycles','')))
    type = bpy.props.EnumProperty(
            name = 'Type',
            items =  (('Full',        'Full',''),
                      ('Texture',     'Texture',''),
                      ('Normal',      'Normal',''),
                      ('Ambient',     'Ambient',''),
                      ('Shadow',      'Shadow',''),
                      ('Glossy',      'Glossy',''),
                      ('Emission',    'Emission',''),
                      ('Alpha',       'Alpha/Transmission',''),
                      ('Displacement','Displacement (BI Only)',''),
                      ('Derivative',  'Derivative (BI Only)',''),
                      ('Vertex Col',  'Vertex Colors (BI Only)',''),
                      ('UV',          'UV (Cycles Only)',''),
                      ('Diffuse',     'Diffuse (Cycles Only)',''),
                      ('Environment', 'Environment (Cycles Only)',''),
                      ('Subsurface',  'Subsurface (Cycles Only)',''),
                      ('Passes',      'Custom Passes (Cycles Only)','')))
    pass_name = bpy.props.StringProperty(name = 'Pass Name',default = 'Color|Base Color|Paint Color')
    pass_multiplier = bpy.props.FloatProperty(name = 'Multiplier',
                    description = '(Pass Value * Multiplier) + Addend',
                    min = 0,
                    default = 1)
    pass_addend     = bpy.props.FloatProperty(name = 'Addend',
                    description = '(Pass Value * Multiplier) + Addend',
                    default = 0)
    img_name = bpy.props.StringProperty(name = 'Name',default = '*_d')
    width = bpy.props.IntProperty(name = 'Width',default = 1024,
                                    min = 1, soft_max = 16384)
    height = bpy.props.IntProperty(name = 'Height',default = 1024,
                                    min = 1, soft_max = 16384)
                                    
    format = bpy.props.EnumProperty(
            name = '',
            items =  (('PNG', 'png',''),
                      ('JPEG','jpg',''),
                      ('TARGA', 'tar',''),
                      ('TIFF','tiff',''),
                      ('BMP', 'bmp','')))
    channels3 = bpy.props.EnumProperty(
            name = '',
            items =  (('BW','BW',''),
                    ('RGB','RGB',''),
                    ('RGBA','RGBA','')),
            default = 'RGB')
    channels2 = bpy.props.EnumProperty(
            name = '',
            items =  (('BW','BW',''),
                    ('RGB','RGB','')),
            default = 'RGB')
    c_depth = bpy.props.EnumProperty(
            name = 'Depth',
            description = 'Color Depth',
            items =  (('8','8',''),
                    ('16','16','')),
            default = '8')
    compression = bpy.props.IntProperty(name = 'Compression',default = 15,
                                    description = 'Compression',
                                    min = 0, max = 100)
    quality = bpy.props.IntProperty(name = 'Quality',default = 90,
                                    description = 'Quality',
                                    min = 0, max = 100)
    tiff_codec = bpy.props.EnumProperty(
            name = 'Compression',
            items =  (('NONE','None',''),
                    ('DEFLATE','Deflate',''),
                    ('LZW','LZW',''),
                    ('PACKBITS','Pack Bits','')),
            default = 'DEFLATE')
            
    samples = bpy.props.IntProperty(name = 'Samples',default = 6,
                                    description = 'Amount of Samples (If Supported)',
                                    min = 1, soft_max = 128)
                                    
    normalize = bpy.props.BoolProperty(name = 'Normalize',default = False)
    normal_space = bpy.props.EnumProperty(
            name = 'Normal Space',
            items =  (('TANGENT','Tangent Space',''),
                      ('OBJECT', 'Object Space','')))
    tricky     = bpy.props.BoolProperty(
                name = "Include Material's Normals",
                description = 'Bake Also Bump Nodes Plugged Into BSDFs',
                default = True)
    gloss_type = bpy.props.EnumProperty(
            items =  (('SPECULAR','Specular','','',0),
                    ('MIRROR','Mirror','','',1)))
    gloss_data = bpy.props.EnumProperty(
            items =  (('INTENSITY','Intensity','','',0),
                    ('COLOR','Color','','',1)))
                    
    cycles_direct   = bpy.props.BoolProperty(name = 'Direct',   default = True)
    cycles_indirect = bpy.props.BoolProperty(name = 'Indirect', default = True)
    cycles_color    = bpy.props.BoolProperty(name = 'Color',    default = True)
    cycles_diffuse           = bpy.props.BoolProperty(name = 'Diffuse',      default = True)
    cycles_glossy            = bpy.props.BoolProperty(name = 'Glossy',       default = True)
    cycles_transmission      = bpy.props.BoolProperty(name = 'Transmission', default = True)
    cycles_subsurface        = bpy.props.BoolProperty(name = 'Subsurface',   default = True)
    cycles_ambient_occlusion = bpy.props.BoolProperty(name = 'AO',           default = True)
    cycles_emit              = bpy.props.BoolProperty(name = 'Emit',         default = True)

class BakeLabMapListUI(bpy.types.UIList):
    def draw_item(self,context,layout,data,item,icon,active_data,active_propname,index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.type == 'Passes':
                layout.label(item.pass_name,icon = 'NONE')
            else:
                layout.label(item.type,icon = 'NONE')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("",icon = 'TEXTURE')
        layout.prop(item,'enabled')
        
class BakeLabObjListUI(bpy.types.UIList):
    def draw_item(self,context,layout,data,item,icon,active_data,active_propname,index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(item.name,icon = 'OUTLINER_OB_GROUP_INSTANCE')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("",icon = 'OUTLINER_OB_GROUP_INSTANCE')
        layout.prop(item,'enabled')

class BakeLabUI(bpy.types.Panel):
    bl_label = 'BakeLab Tools'
    bl_idname = 'bakelab.ui'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "BakeLab"
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        
        col = layout.column()
        col.scale_y = 1.5
        col.operator('bakelab.bake','Bake',icon = 'RENDER_STILL')
        layout.prop(scene.BakeLabProps,'use_list')
        if scene.BakeLabProps.use_list:
            col = layout.column(align = True)
            row = col.split(align=True)
            row.operator("bakelab.newobjitem", icon='ZOOMIN', text="")
            row.operator("bakelab.removeobjitem", icon='ZOOMOUT', text="")
            row.operator("bakelab.selectobjitem", icon='RESTRICT_SELECT_OFF', text="")
            row.prop(scene.BakeLabProps,'obj_list_settings',icon = 'SCRIPTWIN',toggle = True)
            col.template_list("BakeLabObjListUI", "", scene,
                          "BakeLabObjColl", scene, "BakeLabObjListIndex", rows=2, maxrows=5)
            if scene.BakeLabProps.obj_list_settings:
                if scene.BakeLabObjListIndex>=0 and scene.BakeLabObjColl:
                    item = scene.BakeLabObjColl[scene.BakeLabObjListIndex]
                    box = col.box()
                    box.prop(item,'name')
                    box.prop(item,'override_size')
                    if item.override_size:
                        subcol = box.column(align=True)
                        subcol.prop(item,'width')
                        subcol.prop(item,'height')
                    else:
                        box.prop(item,'image_scale')
                    box.prop(item,'sample_scale')
                    if scene.BakeLabProps.s_to_a and scene.BakeLabProps.use_cage:
                        box.prop(item,'ray_scale',text = 'Cage Extrusion Scale')
                    else:
                        box.prop(item,'ray_scale',text = 'Ray Distance Scale')
                    col.separator()
                
        row = layout.row(align = True)
        row.prop(scene.BakeLabProps,'s_to_a',toggle = True)
        row.prop(scene.BakeLabProps,'s_to_a_settings',icon = 'SCRIPTWIN',toggle = True)
        if scene.BakeLabProps.s_to_a_settings:
            s2a_col = layout.column()
            s2a_col.prop(scene.BakeLabProps,'use_cage')
            if scene.BakeLabProps.use_cage:
                s2a_col.prop(scene.BakeLabProps,'cage_extrusion',text = 'Cage Extrusion')
            else:
                s2a_col.prop(scene.BakeLabProps,'cage_extrusion',text = 'Ray Distance')
            s2a_col.enabled = scene.BakeLabProps.s_to_a
                
        if not scene.BakeLabProps.s_to_a:
            row = layout.row(align = True)
            row.prop(scene.BakeLabProps,'all_in_one',toggle = True)
            if not scene.BakeLabProps.use_list:
                row.prop(scene.BakeLabProps,'a_in_1_settings',icon = 'SCRIPTWIN',toggle = True)
                if scene.BakeLabProps.a_in_1_settings:
                    a_in_1_col = layout.column()
                    a_in_1_col.prop(scene.BakeLabProps,'general_name')
                    a_in_1_col.prop(scene.BakeLabProps,'ray_limit')
                    a_in_1_col.enabled = scene.BakeLabProps.all_in_one
            
        row = layout.row(align = True)
        row.prop(scene.BakeLabProps,'unwrap_mode')
        row.prop(scene.BakeLabProps,'unwrap_settings',icon = 'SCRIPTWIN',toggle = True)
        
        if scene.BakeLabProps.unwrap_settings:
            row = layout.row(align = True)
            if   scene.BakeLabProps.unwrap_mode == 'smart_uv':
                row.prop(scene.BakeLabProps,'smart_uv_angle')
                row.prop(scene.BakeLabProps,'smart_uv_margin')
            elif scene.BakeLabProps.unwrap_mode == 'lightmap':
                row.prop(scene.BakeLabProps,'lightmap_quality')
                row.prop(scene.BakeLabProps,'lightmap_margin')
            row = layout.row()
            row.prop(scene.BakeLabProps,'newuv')
            row.prop(scene.BakeLabProps,'deluvs')
        
        layout.prop(scene.BakeLabProps,'compute_device')
        layout.prop(scene.BakeLabProps,'linked_datas')
        
        layout.prop(scene.BakeLabProps,'aa_samples')
        layout.prop(scene.BakeLabProps,'bake_margin')
            
        row = layout.row()
        row.prop(scene.BakeLabProps,'gen_mat')
        col = row.column()
        col.prop(scene.BakeLabProps,'append_mat')
        col.enabled = scene.BakeLabProps.gen_mat
        row = layout.row()
        row.prop(scene.BakeLabProps,'save_or_pack', expand = True)
        if scene.BakeLabProps.save_or_pack == 'SAVE':
            layout.prop(scene.BakeLabProps,'out_path')
        
        layout.separator()
        
        box = layout.box()
        col = box.column(align = True)
        row = col.split(align=True)
        row.operator("bakelab.newmapitem", icon='ZOOMIN', text="")
        row.operator("bakelab.removemapitem", icon='ZOOMOUT', text="")
        col.template_list("BakeLabMapListUI", "", scene,
                          "BakeLabMapColl", scene, "BakeLabMapListIndex", rows=2, maxrows=5)
                          
        ###################################################################
        
        if scene.BakeLabMapListIndex>=0 and scene.BakeLabMapColl:
            item = scene.BakeLabMapColl[scene.BakeLabMapListIndex]
            
            col = box.column()
            col.enabled = item.enabled
            
            col.prop(item,'type')
            col.prop(item,'img_name')
            subcol = col.column(align=True)
            subcol.prop(item,'width')
            subcol.prop(item,'height')
            
            if scene.BakeLabProps.save_or_pack == 'SAVE':
                row = col.row(align = True)
                row.prop(item,'format')
                if item.format in {'PNG','TARGA','TIFF'}:
                    row.prop(item,'channels3')
                elif item.format == 'JPEG':
                    row.prop(item,'channels2')
                    
                row = col.row()
                if item.format == 'PNG':
                    row.prop(item,'compression')
                if item.format == 'JPEG':
                    row.prop(item,'quality')
                if item.format == 'TIFF':
                    row.prop(item,'tiff_codec')
                if item.format in {'PNG','TIFF'}:
                    row.prop(item,'c_depth')
            
            col.separator()
            
            subcol = col.column()
            if item.type in {'Displacement','Derivative','Vertex Col'}:
                item.engine = 'BI'
                subcol.enabled = False
            elif item.type in {'UV','Diffuse','Environment','Subsurface','Passes'}:
                item.engine = 'CYCLES'
                subcol.enabled = False
                
            subcol.prop(item,'engine')
            col.prop(item,'samples')
            
            if item.engine == 'BI':
                if item.type in {'Ambient', 'Displacement'}:
                    box.prop(item,'normalize')
                if item.type in {'Glossy'}:
                    row = box.row()
                    row.prop(item,'gloss_type',expand = True)
                    row = box.row()
                    row.prop(item,'gloss_data',expand = True)
            if item.engine == 'CYCLES':
                if item.type in {'Full','Diffuse','Glossy','Alpha','Subsurface'}:
                    split = box.split(align = True)
                    split.prop(item,'cycles_direct',toggle = True)
                    split.prop(item,'cycles_indirect',toggle = True)
                    if item.type != 'Full':
                        split.prop(item,'cycles_color',toggle = True)
                    else:
                        row = box.row()
                        col = row.column()
                        col.prop(item,'cycles_diffuse')
                        col.prop(item,'cycles_glossy')
                        col.prop(item,'cycles_transmission')
                        col = row.column()
                        col.prop(item,'cycles_subsurface')
                        col.prop(item,'cycles_ambient_occlusion')
                        col.prop(item,'cycles_emit')
            if item.type in {'Normal'}:
                box.prop(item,'normal_space',expand = True)
                if item.engine == 'CYCLES':
                    box.prop(item,'tricky')
            if item.type in {'Passes'}:
                box.separator()
                row = box.row(align = True)
                row.prop(item,'pass_name')
                row.operator_menu_enum('bakelab.pass_presets','pass_presets',icon = 'COLLAPSEMENU',text = '')
                col = box.column(align = True)
                col.prop(item,'pass_multiplier')
                col.prop(item,'pass_addend')

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.BakeLabProps = bpy.props.PointerProperty(type = BakeLabProperties)
    bpy.types.Scene.BakeLabObjColl = bpy.props.CollectionProperty(type = BakeLabObjectCollection)
    bpy.types.Scene.BakeLabMapColl = bpy.props.CollectionProperty(type = BakeLabMapCollection)
    bpy.types.Scene.BakeLabMapListIndex = bpy.props.IntProperty(name = 'BakeLab Map List Index')
    bpy.types.Scene.BakeLabObjListIndex = bpy.props.IntProperty(name = 'BakeLab Object List Index')

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.BakeLabProps
    del bpy.types.Scene.BakeLabObjColl
    del bpy.types.Scene.BakeLabMapColl
    del bpy.types.Scene.BakeLabMapListIndex
    del bpy.types.Scene.BakeLabObjListIndex

if __name__ == "__main__":
    register()