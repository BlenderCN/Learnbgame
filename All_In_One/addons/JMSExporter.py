# Author: Gurten






bl_info = {
    "name": "Halo 1 CE JMS Exporter for collision",
    "author": "Gurten",
    "version": ( 1, 0, 3 ),
    "blender": ( 2, 6, 3 ),
    "location": "File > Export > Halo 1 CE JMS Exporter collision (.jms)",
    "description": "Halo 1 CE JMS Exporter collision (.jms)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty

class ExportJMS(bpy.types.Operator, ExportHelper):
    bl_idname = "export.jms"
    bl_label = "Export"
    __doc__ = "Halo 1 CE JMS Exporter (.jms)"
    filename_ext = ".jms"
    filter_glob = StringProperty( default = "*.jms", options = {'HIDDEN'} )
    
    filepath = StringProperty( 
        name = "File Path",
        description = "File path used for exporting the JMS file",
        maxlen = 1024,
        default = "" )
            
    option_selection_only = BoolProperty(
        name = "Selection Only",
        description = "Exports selected mesh objects only",
        default = True )
    
    def draw( self, context ):
        layout = self.layout
        box = layout.box()
        box.prop( self, 'option_selection_only' )
    
    def serialise_model(self, context, obj, objs):
        #Single origin node for now.
        n_nodes = 1
        
        # header of JMS file. First two lines unknown, third line is the number of nodes.
        out = "8200\n3251\n%d\n" % (n_nodes)
        #write nodes
        for i in range(n_nodes):
            node_name = "default"
            node_next_sibling = -1
            node_first_child = -1
            node_rotation = (0,0,0,1) #i,j,k,w
            node_translation = (0,0,0) #x,y,z
            #flatten list and format to string
            node_vals = [[node_name, node_next_sibling, node_first_child], node_rotation, node_translation] 
            node_vals = [i for l in node_vals for i in l]
            out+= ("%s\n%d\n%d\n%f\t%f\t%f\t%f\n%f\t%f\t%f\n" % tuple(node_vals))
        
        # Materials
        materials_l = ['default'] # list maintains order thte materials were added.
        materials_d = {'default' : 0}
        for obj in objs:
            for mat in obj.data.materials:
                if mat.name not in materials_d:
                    materials_l.append(mat.name)
                    materials_d[mat.name] = len(materials_d)
        n_materials = len(materials_l)
        out += ("%d\n" % n_materials)
        
        #write materials
        for m in materials_l: # this is ordered by the order of insertion, not possible with a dict.
            material_name = m
            material_texture = "<none>"
            out += ("%s\n%s\n" % (material_name, material_texture))
        
        # Markers
        n_markers = 0
        out += ("%d\n" % n_markers)
        for i in range(n_markers):
            #
            None # format not known
        n_objs = 1
        out += "%d\n" % n_objs
        
        # Objects
 
        obj_name = obj.name
        n_verts = len(obj.data.vertices)
        out += "%s\n%d\n" % (obj_name, n_verts)
        for v in obj.data.vertices:
            node_idx = 0
            # apply transformations to object
            # scale by 100 to counteract H1CE Tool scale by 0.01. 
            vert_pos = obj.matrix_local * v.co * 100.0
            vert_normal = v.normal
            node1_idx = -1
            node1_weight = 0
            tex_coord = (0,0,0)
            #flatten list and write to string
            vert_vals = [[node_idx], vert_pos, vert_normal, [node1_idx, node1_weight], tex_coord]
            vert_vals = [item for sublist in vert_vals for item in sublist]
            out += ("%d\n%f\t%f\t%f\n%f\t%f\t%f\n%d\n%f\n%f\t%f\t%f\n" % tuple(vert_vals))
        n_faces = 0
        face_str = ""
        for f in obj.data.polygons:
            face_data = []
            face_vert_indices = [obj.data.loops[idx].vertex_index for idx in f.loop_indices]
            face_unknown = 0
            face_material_idx = f.material_index
            if len(obj.data.materials) is not 0: # Occurs when a face has a material assigned
                # get the global material list index
                face_material_idx = materials_d[obj.data.materials[face_material_idx].name]
            
            for i in range(len(face_vert_indices)-2):
                face_data.append([[face_unknown, face_material_idx], (face_vert_indices[0], face_vert_indices[i+1], face_vert_indices[i+2])]) 
                n_faces += 1
            
            for l in face_data:
                face_vals = [item for sublist in l for item in sublist]
                face_str += ("%d\n%d\n%d\t%d\t%d\n" % tuple(face_vals))
        out += ("%d\n" % n_faces)
        out += face_str
        return out

    def execute(self, context):
        n_objs_exported = 0
        if self.option_selection_only:
            objs = [o for o in context.selected_objects]
        else:
            objs = [o for o in context.selectable_objects]
        
        objs = list(filter(lambda x: x.type == "MESH", objs))
        if len(objs) == 0:
            raise Exception("No meshes to export.")
        
        fpath = self.filepath
        dir_path = fpath[:fpath.rfind('.')]
        os.mkdir(dir_path)
        fname = fpath[(fpath.rfind('\\')+1):].split(".jms")[0]
        stub_command = "tool collision-geometry %s/%s\n"
        bfile_collate = ""
        ext = ".model_collision_geometry"
        bfile_data = '''
:: This batch file was generated together with the directory: \'{0}\'
:: Place the parent directory: \'{0}\'
:: into \'<Halo 1 CE Tool directory>\\data\\\' and run this batch file.\ncd ../..\n'''.format(fname)
        
        for i,obj in enumerate(objs):
            ifname = ("%s%03d" % (fname, i))
            bfile_data += stub_command % (fname, ifname)
            bfile_collate += "copy \".\\tags\\{0}\\{1}\\{1}{2}\" \".\\data\\{0}\\{1}{2}\"\n".format(fname, ifname, ext)
            idir_path = ("%s\\%s" % (dir_path, ifname))
            idir_pathp = ("%s\\%s\\physics" % (dir_path, ifname))
            os.mkdir(idir_path)
            os.mkdir(idir_pathp)
            out = self.serialise_model(context, obj, objs)
            n_objs_exported += 1
            f = open(("%s\\%s.jms" % (idir_pathp, ifname)), "w")
            f.write(out)
            f.close()
        
        bfile_data += bfile_collate
        bfile_data += "pause"
        f = open(("%s\\generate.bat" % (dir_path)), "w")
        f.write(bfile_data)
        f.close()
        print("Successfully exported %d objects to \'%s\'." % (n_objs_exported, self.filepath))
        return {'FINISHED'}
        
        

# Blender register plugin 
def register():
    bpy.utils.register_class(ExportJMS)

def menu_func( self, context ):
    self.layout.operator( ExportJMS.bl_idname, text = "Halo 1 CE JMS Exporter collision (.jms)" )

def register():
    bpy.utils.register_class( ExportJMS )
    bpy.types.INFO_MT_file_export.append( menu_func )

def unregister():
    bpy.utils.unregister_class( ExportJMS )
    bpy.types.INFO_MT_file_export.remove( menu_func )

if __name__ == "__main__":
    register()