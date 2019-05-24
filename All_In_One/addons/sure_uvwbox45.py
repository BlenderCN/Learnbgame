bl_info = {
    "name": "Sure UVW Map v.0.45",
    "author": "Alexander Milovsky (www.3dmaster.ru)",
    "version": (0, 45),
    "blender": (2, 6, 3),
    "api": 45093,
    "location": "Properties > Object Data (below UV Maps), parameters in Tool Properties",
    "description": "Box / Best Planar UVW Map (Make Material With Raster Texture First!)",
    "warning": "",
    "wiki_url": "http://blenderartists.org/forum/showthread.php?236631-Addon-Simple-Box-UVW-Map-Modifier",
    "tracker_url": "https://projects.blender.org/tracker/index.php",
    "category": "Learnbgame",
}

import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty, FloatVectorProperty
from math import sin, cos, pi
from mathutils import Vector

# globals for Box Mapping
all_scale_def = 1
x_offset_def = 0
y_offset_def = 0
z_offset_def = 0
x_rot_def = 0
y_rot_def = 0
z_rot_def = 0


# globals for Best Planar Mapping
xoffset_def = 0
yoffset_def = 0
zrot_def = 0

# Preview flag
preview_flag = True

def show_texture():
    obj = bpy.context.active_object
    mesh = obj.data
    is_editmode = (obj.mode == 'EDIT')
    # if in EDIT Mode switch to OBJECT
    if is_editmode:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # if no UVtex - create it
    if not mesh.uv_textures:
        uvtex = bpy.ops.mesh.uv_texture_add()
    uvtex = mesh.uv_textures.active
    uvtex.active_render = True

    img = None    
    aspect = 1.0
    mat = obj.active_material

    try:
        if mat:
            img = mat.active_texture
            for f in mesh.polygons:  
                if not is_editmode or f.select:
                    uvtex.data[f.index].image = img.image
        else:
            img = None        
    except:
        pass
    # Back to EDIT Mode
    if is_editmode:
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)


def box_map():    
    #print('** Boxmap **')
    global all_scale_def,x_offset_def,y_offset_def,z_offset_def,x_rot_def,y_rot_def,z_rot_def
    obj = bpy.context.active_object
    mesh = obj.data

    is_editmode = (obj.mode == 'EDIT')

    # if in EDIT Mode switch to OBJECT
    if is_editmode:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # if no UVtex - create it
    if not mesh.uv_textures:
        uvtex = bpy.ops.mesh.uv_texture_add()
    uvtex = mesh.uv_textures.active
    #uvtex.active_render = True
    
    img = None    
    aspect = 1.0
    mat = obj.active_material
    try:
        if mat:
            img = mat.active_texture
            aspect = img.image.size[0]/img.image.size[1]
    except:
        pass

                
    
    #
    # Main action
    #
    if all_scale_def:
        sc = 1.0/all_scale_def
    else:
        sc = 1.0   

    sx = 1 * sc
    sy = 1 * sc
    sz = 1 * sc
    ofx = x_offset_def
    ofy = y_offset_def
    ofz = z_offset_def
    rx = x_rot_def / 180 * pi
    ry = y_rot_def / 180 * pi
    rz = z_rot_def / 180 * pi
    
    crx = cos(rx)
    srx = sin(rx)
    cry = cos(ry)
    sry = sin(ry)
    crz = cos(rz)
    srz = sin(rz)
    ofycrx = ofy * crx
    ofzsrx = ofz * srx
    
    ofysrx = ofy * srx
    ofzcrx = ofz * crx
    
    ofxcry = ofx * cry
    ofzsry = ofz * sry
    
    ofxsry = ofx * sry
    ofzcry = ofz * cry
    
    ofxcry = ofx * cry
    ofzsry = ofz * sry
    
    ofxsry = ofx * sry
    ofzcry = ofz * cry
    
    ofxcrz = ofx * crz
    ofysrz = ofy * srz
    
    ofxsrz = ofx * srz
    ofycrz = ofy * crz
    
    #uvs = mesh.uv_loop_layers[mesh.uv_loop_layers.active_index].data
    uvs = mesh.uv_loop_layers.active.data
    for i, pol in enumerate(mesh.polygons):
        if not is_editmode or mesh.polygons[i].select:
            for j, loop in enumerate(mesh.polygons[i].loops):
                v_idx = mesh.loops[loop].vertex_index
                #print('before[%s]:' % v_idx)
                #print(uvs[loop].uv)
                n = mesh.polygons[i].normal
                co = mesh.vertices[v_idx].co
                x = co.x * sx
                y = co.y * sy
                z = co.z * sz
                if abs(n[0]) > abs(n[1]) and abs(n[0]) > abs(n[2]):
                    # X
                    if n[0] >= 0:
                        uvs[loop].uv[0] =  y * crx + z * srx                    - ofycrx - ofzsrx
                        uvs[loop].uv[1] = -y * aspect * srx + z * aspect * crx  + ofysrx - ofzcrx
                    else:
                        uvs[loop].uv[0] = -y * crx + z * srx                    + ofycrx - ofzsrx
                        uvs[loop].uv[1] =  y * aspect * srx + z * aspect * crx  - ofysrx - ofzcrx
                elif abs(n[1]) > abs(n[0]) and abs(n[1]) > abs(n[2]):
                    # Y
                    if n[1] >= 0:
                        uvs[loop].uv[0] =  -x * cry + z * sry                   + ofxcry - ofzsry
                        uvs[loop].uv[1] =   x * aspect * sry + z * aspect * cry - ofxsry - ofzcry
                    else:
                        uvs[loop].uv[0] =   x * cry + z * sry                   - ofxcry - ofzsry
                        uvs[loop].uv[1] =  -x * aspect * sry + z * aspect * cry + ofxsry - ofzcry
                else:
                    # Z
                    if n[2] >= 0:
                        uvs[loop].uv[0] =   x * crz + y * srz +                 - ofxcrz - ofysrz
                        uvs[loop].uv[1] =  -x * aspect * srz + y * aspect * crz + ofxsrz - ofycrz
                    else:
                        uvs[loop].uv[0] =  -y * srz - x * crz                   + ofxcrz - ofysrz
                        uvs[loop].uv[1] =   y * aspect * crz - x * aspect * srz - ofxsrz - ofycrz
    
    # Back to EDIT Mode
    if is_editmode:
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

# Best Planar Mapping
def best_planar_map():
    global all_scale_def,xoffset_def,yoffset_def,zrot_def
    
    obj = bpy.context.active_object
    mesh = obj.data

    is_editmode = (obj.mode == 'EDIT')

    # if in EDIT Mode switch to OBJECT
    if is_editmode:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # if no UVtex - create it
    if not mesh.uv_textures:
        uvtex = bpy.ops.mesh.uv_texture_add()
    uvtex = mesh.uv_textures.active
    #uvtex.active_render = True
    
    img = None    
    aspect = 1.0
    mat = obj.active_material
    try:
        if mat:
            img = mat.active_texture
            aspect = img.image.size[0]/img.image.size[1]
    except:
        pass

                
    
    #
    # Main action
    #
    if all_scale_def:
        sc = 1.0/all_scale_def
    else:
        sc = 1.0   

    # Calculate Average Normal
    v = Vector((0,0,0))
    cnt = 0
    for f in mesh.polygons:  
        if f.select:
            cnt += 1
            v = v + f.normal
    
    zv = Vector((0,0,1))
    q = v.rotation_difference(zv)
            

    sx = 1 * sc
    sy = 1 * sc
    sz = 1 * sc
    ofx = xoffset_def
    ofy = yoffset_def
    rz = zrot_def / 180 * pi

    cosrz = cos(rz)
    sinrz = sin(rz)

    #uvs = mesh.uv_loop_layers[mesh.uv_loop_layers.active_index].data
    uvs = mesh.uv_loop_layers.active.data
    for i, pol in enumerate(mesh.polygons):
        if not is_editmode or mesh.polygons[i].select:
            for j, loop in enumerate(mesh.polygons[i].loops):
                v_idx = mesh.loops[loop].vertex_index

                n = pol.normal
                co = q * mesh.vertices[v_idx].co
                x = co.x * sx
                y = co.y * sy
                z = co.z * sz
                uvs[loop].uv[0] =  x * cosrz - y * sinrz + xoffset_def
                uvs[loop].uv[1] =  aspect*(- x * sinrz - y * cosrz) + yoffset_def



    # Back to EDIT Mode
    if is_editmode:
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)


class SureUVWOperator(bpy.types.Operator):
    bl_idname = "object.sureuvw_operator"
    bl_label = "Sure UVW Map"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    bl_options = {'REGISTER', 'UNDO'}

    
    action = StringProperty()  

    size = FloatProperty(name="Size", default=1.0)
    rot = FloatVectorProperty(name="XYZ Rotation")
    offset = FloatVectorProperty(name="XYZ offset")

    zrot = FloatProperty(name="Z rotation", default=0.0)
    xoffset = FloatProperty(name="X offset", default=0.0)
    yoffset = FloatProperty(name="Y offset", default=0.0)

    flag90 = BoolProperty()
    flag90ccw = BoolProperty()


    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')

    def execute(self, context):
        #print('** execute **')
        #print(self.action)
        global all_scale_def,x_offset_def,y_offset_def,z_offset_def,x_rot_def,y_rot_def,z_rot_def, xoffset_def, yoffset_def, zrot_def
                
        all_scale_def = self.size
        x_offset_def = self.offset[0]
        y_offset_def = self.offset[1]
        z_offset_def = self.offset[2]
        x_rot_def = self.rot[0]
        y_rot_def = self.rot[1]
        z_rot_def = self.rot[2]

        xoffset_def = self.xoffset
        yoffset_def = self.yoffset
        zrot_def = self.zrot

        
        if self.flag90:
          self.zrot += 90
          zrot_def += 90
          self.flag90 = False

        if self.flag90ccw:
          self.zrot += -90
          zrot_def += -90
          self.flag90ccw = False

        
        if self.action == 'bestplanar':
            best_planar_map()
        elif self.action == 'box':
            box_map()
        elif self.action == 'showtex':
            show_texture()
        elif self.action == 'doneplanar':
            best_planar_map()
        elif self.action == 'donebox':
            box_map()
        
        #print('finish execute')
        return {'FINISHED'}

    def invoke(self, context, event):
        #print('** invoke **')
        #print(self.action)
        global all_scale_def,x_offset_def,y_offset_def,z_offset_def,x_rot_def,y_rot_def,z_rot_def, xoffset_def, yoffset_def, zrot_def

        self.size = all_scale_def
        self.offset[0] = x_offset_def
        self.offset[1] = y_offset_def
        self.offset[2] = z_offset_def
        self.rot[0] = x_rot_def
        self.rot[1] = y_rot_def
        self.rot[2] = z_rot_def

        
        self.xoffset = xoffset_def
        self.yoffset = yoffset_def
        self.zrot = zrot_def
        
            

        if self.action == 'bestplanar':
            best_planar_map()
        elif self.action == 'box':
            box_map()
        elif self.action == 'showtex':
            show_texture()
        elif self.action == 'doneplanar':
            best_planar_map()
        elif self.action == 'donebox':
            box_map()
            
        #print('finish invoke')
        return {'FINISHED'}


    def draw(self, context):
        if self.action == 'bestplanar' or self.action == 'rotatecw' or self.action == 'rotateccw':
            self.action = 'bestplanar'
            layout = self.layout
            layout.label("Size - "+self.action)
            layout.prop(self,'size',text="")
            layout.label("Z rotation")
            col = layout.column()
            col.prop(self,'zrot',text="")
            row = layout.row()
            row.prop(self,'flag90ccw',text="-90 (CCW)")
            row.prop(self,'flag90',text="+90 (CW)")
            layout.label("XY offset")
            col = layout.column()
            col.prop(self,'xoffset', text="")
            col.prop(self,'yoffset', text="")

            #layout.prop(self,'preview_flag', text="Interactive Preview")
            #layout.operator("object.sureuvw_operator",text="Done").action='doneplanar'
            
        elif self.action == 'box':          
            layout = self.layout
            layout.label("Size")
            layout.prop(self,'size',text="")
            layout.label("XYZ rotation")
            col = layout.column()
            col.prop(self,'rot', text="")
            layout.label("XYZ offset")
            col = layout.column()
            col.prop(self,'offset', text="")

            #layout.prop(self,'preview_flag', text="Interactive Preview")        
            #layout.operator("object.sureuvw_operator",text="Done").action='donebox'
             

class SureUVWPanel(bpy.types.Panel):
    bl_label = "Sure UVW Mapping v.0.4"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    #bl_space_type = "VIEW_3D"
    #bl_region_type = "TOOLS"
    #bl_region_type = "TOOL_PROPS"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')

    def draw(self, context):
        self.layout.label("Press this button first:")
        self.layout.operator("object.sureuvw_operator",text="Show active texture on object").action='showtex'
        self.layout.label("UVW Mapping:")
        self.layout.operator("object.sureuvw_operator",text="UVW Box Map").action='box'
        self.layout.operator("object.sureuvw_operator",text="Best Planar Map").action='bestplanar'
        self.layout.label("1. Make Material With Raster Texture!")
        self.layout.label("2. Texture Mapping Coords: UV!")
        self.layout.label("3. Use Addon buttons")

#
# Registration
#

def register():
    bpy.utils.register_class(SureUVWOperator)
    bpy.utils.register_class(SureUVWPanel)


def unregister():
    bpy.utils.unregister_class(SureUVWOperator)
    bpy.utils.unregister_class(SureUVWPanel)


if __name__ == "__main__":
    register()
