bl_info = {
    "name": "Export GM:Studio BLMod",
    "description": "Exporter for GameMaker:Studio with customizable vertex format",
    "author": "Bart Teunis",
    "version": (0, 8, 1),
    "blender": (2, 79, 0),
    "location": "File > Export",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/bartteunis/blender-gms-vbx/wiki",
    "category": "Learnbgame"
}

# Required imports
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Object, Operator, PropertyGroup
import bpy
import shutil                       # for image file copy
import json
from os import path, makedirs
from os.path import splitext, split
from struct import pack, calcsize

### Export Function Definitions ###
def fetch_attribs(desc,node,ba,byte_pos,frame):
    """"Fetch the attribute values from the given node and place in ba at byte_pos"""
    id = node.bl_rna.identifier
    if id in desc:
        for prop, occurrences in desc[id].items():                   # Property name and occurrences in bytedata
            for offset, attr_blen, fmt, index, func in occurrences:  # Each occurrence's data (tuple assignment!)
                ind = byte_pos+offset
                val = getattr(node,prop)
                if func != None: val = func(val)
                val_bin = pack(fmt,val) if len(fmt) == 1 else pack(fmt,*val)
                ba[frame-index][ind:ind+attr_blen] = val_bin

def write_object_ba(scene,obj,desc,ba,frame,reverse_loop,apply_transforms):
    """Traverse the object's mesh data at the given frame and write to the appropriate bytearray in ba using the description data structure provided"""
    desc, vertex_format_bytesize = desc
    
    mod_tri = obj.modifiers.new('triangulate_for_export','TRIANGULATE')
    m = obj.to_mesh(bpy.context.scene,True,'RENDER')
    obj.modifiers.remove(mod_tri)
    if apply_transforms:
        m.transform(obj.matrix_world)
    
    ba_pos = 0
    for p in m.polygons:
        # Loop through vertices
        # TODO Speed this up!
        iter = reversed(p.loop_indices) if reverse_loop else p.loop_indices
        for li in iter:
            fetch_attribs(desc,scene,ba,ba_pos,frame)
            fetch_attribs(desc,obj,ba,ba_pos,frame)
            
            fetch_attribs(desc,p,ba,ba_pos,frame)
            
            mat = m.materials[p.material_index]
            if not mat.use_nodes:
                fetch_attribs(desc,mat,ba,ba_pos,frame)
            
            loop = m.loops[li]
            fetch_attribs(desc,loop,ba,ba_pos,frame)
            
            if not mat.use_nodes:
                uvs = m.uv_layers.active.data
                uv = uvs[loop.index]                                # Use active uv layer
                fetch_attribs(desc,uv,ba,ba_pos,frame)
            
            vertex = m.vertices[loop.vertex_index]
            fetch_attribs(desc,vertex,ba,ba_pos,frame)
            
            # We wrote a full vertex, so we can now increment the bytearray position by the vertex format size
            ba_pos += vertex_format_bytesize
    
    bpy.data.meshes.remove(m)

def construct_ds(obj,attr):
    """Construct the data structure required to move through the attributes of a given object"""
    desc, offset = {}, 0
    
    for a in attr:
        ident, atn, format, fo, func = a
        
        if ident not in desc:
            desc[ident] = {}
        dct_obj = desc[ident]
        
        if atn not in dct_obj:
            dct_obj[atn] = []
        lst_attr = dct_obj[atn]
        
        prop_rna = getattr(bpy.types,ident).bl_rna.properties[atn]
        attrib_bytesize = calcsize(format)
        
        lst_attr.append((offset,attrib_bytesize,format,fo,func))
        offset += attrib_bytesize
        
    return (desc, offset)

def construct_ba(obj,desc,frame_count):
    """Construct the required bytearrays to store vertex data for the given object for the given number of frames"""
    mod_tri = obj.modifiers.new('triangulate_for_export','TRIANGULATE')
    m = obj.to_mesh(bpy.context.scene,True,'RENDER')
    obj.modifiers.remove(mod_tri)
    no_verts = len(m.polygons) * 3
    bpy.data.meshes.remove(m)                                   # Any easier way to get number of vertices??
    desc, vertex_format_bytesize = desc
    ba = [bytearray([0] * no_verts * vertex_format_bytesize) for i in range(0,frame_count)]
    return ba, no_verts

### End of Export Function Definitions ###

# Conversion functions (go into the globals() dictionary for now...)
def float_to_byte(val):
    """Convert value in range [0,1] to an integer value in range [0,255]"""
    return int(val*255)

def vec_to_bytes(val):
    """Convert a list of values in range [0,1] to a list of integer values in range [0,255]"""
    return [int(x*255) for x in val]

def invert_v(val):
    """Invert the v coordinate of a (u,v) pair"""
    return [val[0],1-val[1]]

def invert_y(val):
    """Invert the y coordinate of a vector"""
    return [val[0],-val[1],val[2]]

def vertex_group_ids_to_bitmask(vertex):
    """Return a bitmask containing the vertex groups a vertex belongs to"""
    list = [x.group for x in vertex.groups]
    masked = 0
    for group in list:
        masked |= 1 << group
    return masked

def mat_name_to_index(val):
    """Return the index of the material with the given name in bpy.data.materials"""
    return bpy.data.materials.find(val)

def object_get_texture_name(obj):
    """Returns the name of the texture image if the object has one defined"""
    tex_name = ""
    for ms in obj.material_slots:
        mat = ms.material
        if mat != None:
            ts = mat.texture_slots[0]
            if (ts != None):
                tex = ts.texture
                tex_name = tex.image.name
    return tex_name

def object_get_diffuse_color(obj):
    if (len(obj.material_slots) > 0):
        return obj.material_slots[0].material.diffuse_color[:]
    else:
        return (1.0,1.0,1.0)

# Custom type to be used in collection
class AttributeType(bpy.types.PropertyGroup):
    # Getter and setter functions
    def fill_attr_cb(self,context):
        if self.type == None: return self.attr_items
        props = getattr(bpy.types,self.type).bl_rna.properties
        items = [(p.identifier,p.name,p.description) for p in props]
        return items
    
    # Currently supported attribute sources, maintained manually at the moment
    supported_sources = {'MeshVertex','MeshLoop','MeshUVLoop','ShapeKeyPoint','VertexGroupElement','Material','MeshLoopColor','MeshPolygon','Scene','Object'}
    source_items, attr_items = [], []
    for src in supported_sources:
        rna = getattr(bpy.types,src).bl_rna
        source_items.append((rna.identifier,rna.name,rna.description))
        props = rna.properties
        items = [(p.identifier,p.name,p.description) for p in props]
        attr_items.extend(items)
    
    # Actual properties
    type = bpy.props.EnumProperty(name="Source", description="Where to get the data from", items=source_items,default=None,update=fill_attr_cb)
    attr = bpy.props.EnumProperty(name="Attribute", description="Which attribute to get", items=attr_items)
    fmt  = bpy.props.StringProperty(name="Format", description="The format string to be used for the binary data", default="fff")
    int  = bpy.props.IntProperty(name="Int", description="Interpolation offset, i.e. 0 means value at current frame, 1 means value at next frame", default=0, min=0, max=1)

# Operators to get the vertex format customization add/remove to work
# See https://blender.stackexchange.com/questions/57545/can-i-make-a-ui-button-that-makes-buttons-in-a-panel
class AddAttributeOperator(Operator):
    """Add a new attribute to the vertex format"""
    bl_idname = "export_scene.add_attribute_operator"
    bl_label = "Add Vertex Attribute"
    
    def execute(self, context):
        # context.active_operator refers to ExportGMSVertexBuffer instance
        context.active_operator.vertex_format.add()
        return {'FINISHED'}

class RemoveAttributeOperator(Operator):
    """Remove the selected attribute from the vertex format"""
    bl_idname = "export_scene.remove_attribute_operator"
    bl_label = "Remove Vertex Attribute"
    
    id = bpy.props.IntProperty()
    
    def execute(self, context):
        # context.active_operator refers to ExportGMSVertexBuffer instance
        context.active_operator.vertex_format.remove(self.id)
        return {'FINISHED'}

# Register these here already
bpy.utils.register_class(AttributeType)
bpy.utils.register_class(AddAttributeOperator)
bpy.utils.register_class(RemoveAttributeOperator)

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
class ExportGMSVertexBuffer(Operator, ExportHelper):
    """Export (parts of) the current scene to a vertex buffer, including textures and a description file in JSON format"""
    bl_idname = "export_scene.gms_blmod" # important since its how bpy.ops.export_scene.gms_blmod is constructed
    bl_label = "Export GM:Studio BLMod"
    bl_options = {'PRESET'}              # Allow presets of exporter configurations
    
    def __init__(self):
        # Blender Python trickery: dynamic addition of an index variable to the class
        bpy.types.Object.batch_index = bpy.props.IntProperty(name="Batch Index")    # Each instance now has a batch index!
    
    # ExportHelper mixin class uses this
    filename_ext = ".json"
    
    filter_glob = StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    ### Property Definitions ###
    selection_only = BoolProperty(
        name="Selection Only",
        default=True,
        description="Only export objects that are currently selected",
    )
    
    reverse_loop = BoolProperty(
        name="Reverse Loop",
        default=False,
        description="Reverse looping through triangle indices",
    )
    
    frame_option = EnumProperty(
        name="Frame",
        description="Which frames to export",
        items=(('cur',"Current","Export current frame only"),
               ('all',"All","Export all frames in range"),
        )
    )
    
    batch_mode = EnumProperty(
        name="Batch Mode",
        description="How to split individual object data over files",
        items=(('one',"Single File", "Batch all into a single file"),
               ('perobj',"Per Object", "Create a file for each object in the selection"),
               ('perfra',"Per Frame", "Create a file for each frame"),
               ('objfra',"Per Object Then Frame", "Create a directory for each object with a file for each frame"),
               ('fraobj',"Per Frame Then Object", "Create a directory for each frame with a file for each object"),
        )
    )
    
    handedness = EnumProperty(
        name="Handedness",
        description="Handedness of the coordinate system to be used",
        items=(('rh',"Right handed",""),
               ('lh',"Left handed",""),
        )
    )
    
    export_mesh_data = BoolProperty(
        name="Export Mesh Data",
        default=False,
        description="Whether to export mesh data to a separate, binary file (.vbx)",
    )
    
    export_json_data = BoolProperty(
        name="Export Object Data",
        default = True,
        description="Whether to export blender data (bpy.data) in JSON format",
    )
    
    object_types_to_export = EnumProperty(
        name="Object Types",
        description="Which types of object data to export",
        options = {'ENUM_FLAG'},
        items=(('cameras',"Cameras","Export cameras"),
               ('lamps',"Lamps","Export lamps"),
               ('speakers',"Speakers","Export speakers"),
               ('armatures',"Armatures","Export armatures"),
               ('materials',"Materials","Export materials"),
               ('textures',"Textures","Export textures"),
               ('actions',"Actions","Export actions"),
               ('curves',"Curves","Export curves"),
               ('groups',"Groups","Export groups"),
        )
    )
    
    export_json_filter = BoolProperty(
        name="Filter Selection",
        default = True,
        description="Whether to filter data in bpy.data based on selection",
    )
    
    apply_transforms = BoolProperty(
        name="Apply Transforms",
        default=True,
        description="Whether to apply object transforms to mesh data",
    )
    
    vertex_format = CollectionProperty(
        name="Vertex Format",
        type=bpy.types.AttributeType,
    )
    
    join_into_active = BoolProperty(
        name="Join Into Active",
        default=False,
        description="Whether to join the selection into the active object",
    )
    
    split_by_material = BoolProperty(
        name="Split By Material",
        default=False,
        description="Whether to split joined mesh by material after joining",
    )
    
    export_textures = BoolProperty(
        name="Export Textures",
        default=True,
        description="Export texture images to same directory as result file",
    )
    ### End of Property Definitions ###
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        
        box.label("General:")
        
        box.prop(self,'selection_only')
        box.prop(self,'frame_option')
        box.prop(self,'batch_mode')
        
        box = layout.box()
        
        box.label("Mesh Data:")
        box.prop(self,"export_mesh_data")
        
        if self.export_mesh_data == True:
            box.label("Vertex Format:")
            
            box.operator("export_scene.add_attribute_operator",text="Add")
            
            for index, item in enumerate(self.vertex_format):
                row = box.row()
                row.prop(item,'type')
                row.prop(item,'attr')
                row.prop(item,'fmt')
                row.prop(item,'func')
                row.prop(item,'int')
                opt_remove = row.operator("export_scene.remove_attribute_operator",text="Remove")
                opt_remove.id = index
        
        box = layout.box()
        
        box.label("Object Data:")
        box.prop(self,"export_json_data")
        
        if self.export_json_data == True:
            box.prop(self,"export_json_filter")
            box.prop(self,"object_types_to_export")
        
        box = layout.box()
        
        box.label("Transforms:")
        
        box.prop(self,"apply_transforms")
        box.prop(self,'handedness')
        box.prop(self,'reverse_loop')
        
        box = layout.box()
        
        box.label("Extras:")
        
        box.prop(self,'join_into_active')
        box.prop(self,'split_by_material')
        box.prop(self,'export_textures')

    def execute(self, context):
        # Prepare a bit
        root, ext = splitext(self.filepath)
        base, fname = split(self.filepath)
        s = context.scene
        
        # Join step
        if self.join_into_active:
            bpy.ops.object.join()
        
        # TODO: transformation and axes step
        
        # Split by material
        if self.split_by_material:
            bpy.ops.mesh.separate(type='MATERIAL')
        
        # Get objects
        mesh_selection = [obj for obj in context.selected_objects if obj.type == 'MESH']
        for i, obj in enumerate(mesh_selection): obj.batch_index = i   # Guarantee a predictable batch index
        
        # Attribs
        attribs = [(i.type,i.attr,i.fmt,i.int,None if i.func == "" else globals()[i.func]) for i in self.vertex_format]
        #print(attribs)
        
        # << Prepare a structure to map vertex attributes to the actual contents >>
        frame_count = s.frame_end-s.frame_start+1 if self.frame_option == 'all' else 1
        
        ba_per_object = {}
        no_verts_per_object = {}
        desc_per_object = {}
        for obj in mesh_selection:
            desc_per_object[obj] = construct_ds(obj,attribs)
            ba_per_object[obj], no_verts_per_object[obj] = construct_ba(obj,desc_per_object[obj],frame_count)
        
        # << End of preparation of structure >>
        
        # << Now execute >>
        
        # Loop through scene frames
        for i in range(frame_count):
            # First set the current frame
            s.frame_set(s.frame_start+i)
            
            # Now add frame vertex data for the current object
            for obj in mesh_selection:
                write_object_ba(s,obj,desc_per_object[obj],ba_per_object[obj],i,self.reverse_loop,self.apply_transforms)
        
        # Final step: write all bytearrays to one or more file(s) in one or more directories
        fn, ext = splitext(fname)
        batch_path = root + ".vbx"
        f = open(batch_path,"wb")
        
        offset = {}
        for obj in mesh_selection:
            ba = ba_per_object[obj]
            offset[obj] = f.tell()
            for b in ba:
                f.write(b)
        
        f.close()
        
        
        
        # Create JSON description file
        ctx, data = {}, {}
        json_data = {
            "bpy":{
                "context":ctx,
                "data":data
            }
        }
        
        def object_to_json(obj):
            """Returns the data of the object in a json-compatible form"""
            result = {}
            rna = obj.bl_rna
            for prop in rna.properties:
                prop_id = prop.identifier
                prop_ins = getattr(obj,prop_id)
                prop_rna = rna.properties[prop_id]
                type = rna.properties[prop_id].type
                #print(prop_id,prop_ins,type)
                if type == 'STRING':
                    result[prop_id] = prop_ins
                elif type == 'ENUM':
                    result[prop_id] = [flag for flag in prop_ins] if prop_rna.is_enum_flag else prop_ins
                elif type == 'POINTER':
                    result[prop_id] = getattr(prop_ins,'name','') if prop_ins != None else ''
                elif type == 'COLLECTION':
                    # Enter collections up to encountering a PointerProperty
                    result[prop_id] = [object_to_json(prop_item) for prop_item in prop_ins if prop_item != None]
                    pass
                else:
                    # 'Simple' attribute types: int, float, boolean
                    if prop_rna.is_array:
                        # Sometimes the bl_rna indicates a number of array items, but the actual number is less
                        # That's because items are stored in an additional object, e.g. a matrix consists of 4 vectors
                        len_expected, len_actual = prop_rna.array_length, len(prop_ins)
                        if len_expected > len_actual:
                            result[prop_id] = []
                            for item in prop_ins: result[prop_id].extend(item[:])
                        else:
                            result[prop_id] = prop_ins[:]
                    else:
                        result[prop_id] = prop_ins
            #print(result)
            return result
        
        # Export bpy.context
        ctx["selected_objects"] = [object_to_json(obj) for obj in bpy.context.selected_objects]
        ctx["scene"] = {"render":{"layers":[{layer.name:[i for i in layer.layers]} for layer in context.scene.render.layers]}}
        
        # Export bpy.data
        #data_to_export = ['cameras','lamps','speakers','armatures','materials','textures','actions','curves','groups']
        data_to_export = self.object_types_to_export
        for datatype in data_to_export:
            #data[datatype] = [object_to_json(obj) for obj in getattr(bpy.data,datatype)]
            data[datatype] = {obj.name:object_to_json(obj) for obj in getattr(bpy.data,datatype)}
        
        # Export additional info that might be useful
        json_data["blmod"] = {
            "mesh_data":{
                "location":fn + ".vbx",
                "format":[{"type":x.type,"attr":x.attr,"fmt":x.fmt} for x in self.vertex_format],
                "ranges":{obj.name:{"no_verts":no_verts_per_object[obj],"offset":offset[obj]} for obj in mesh_selection},
            },
            "settings":{"apply_transforms":self.apply_transforms},
            "no_frames":frame_count,
            "blender_version":bpy.app.version[:],
            "version":bl_info["version"],
        }
        
        # Save textures (TODO: clean this up!)
        if self.export_textures:
            for obj in mesh_selection:                              # Only mesh objects have texture slots
                tex_slot = None
                for ms in obj.material_slots:
                    mat = ms.material
                    if not mat.use_nodes:
                        tex_slot = mat.texture_slots[0]
                if tex_slot != None:
                    image = tex_slot.texture.image
                    image.save_render(base + '/' + image.name,context.scene)
        
        # Write to file
        f_desc = open(root + ".json","w")
        
        json.dump(json_data,f_desc)
        
        f_desc.close()
        
        # Cleanup: remove dynamic property from class
        del bpy.types.Object.batch_index
        
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportGMSVertexBuffer.bl_idname, text="GM:Studio BLMod (*.json + *.vbx)")


def register():
    bpy.utils.register_class(ExportGMSVertexBuffer)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportGMSVertexBuffer)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()