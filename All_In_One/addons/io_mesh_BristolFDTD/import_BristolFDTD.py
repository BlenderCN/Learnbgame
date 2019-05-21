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

# <pep8 compliant>

bl_info = {
    'name': 'Import Bristol FDTD format (.geo,.inp,.in)',
    'author': 'Mike Taverne',
    'version': (0, 0, 1),
    "blender": (2, 5, 7),
    "api": 36079,
    'location': 'File > Import > Import Bristol FDTD (.geo,.inp,.in)',
    'description': 'Import files in the Bristol FDTD format (.geo,.inp,.in)',
    'warning': 'only a part of Bristol FDTD specification is supported: Work in Progress',
    'wiki_url': '',
    'tracker_url': '',
    'support': 'UNOFFICIAL',
    'category': 'Import-Export',
    }

import re
import struct


class element_spec(object):
    __slots__ = ("name",
                 "count",
                 "properties",
                 )

    def __init__(self, name, count):
        self.name = name
        self.count = count
        self.properties = []

    def load(self, format, stream):
        if format == b'ascii':
            stream = re.split(b'\s+', stream.readline())
        return [x.load(format, stream) for x in self.properties]

    def index(self, name):
        for i, p in enumerate(self.properties):
            if p.name == name:
                return i
        return -1


class property_spec(object):
    __slots__ = ("name",
                 "list_type",
                 "numeric_type",
                 )

    def __init__(self, name, list_type, numeric_type):
        self.name = name
        self.list_type = list_type
        self.numeric_type = numeric_type

    def read_format(self, format, count, num_type, stream):
        if format == b'ascii':
            if num_type == 's':
                ans = []
                for i in range(count):
                    s = stream[i]
                    if len(s) < 2 or s[0] != '"' or s[-1] != '"':
                        print('Invalid string', s)
                        print('Note: BristolFDTD_import.py does not handle whitespace in strings')
                        return None
                    ans.append(s[1:-1])
                stream[:count] = []
                return ans
            if num_type == 'f' or num_type == 'd':
                mapper = float
            else:
                mapper = int
            ans = [mapper(x) for x in stream[:count]]
            stream[:count] = []
            return ans
        else:
            if num_type == 's':
                ans = []
                for i in range(count):
                    fmt = format + 'i'
                    data = stream.read(struct.calcsize(fmt))
                    length = struct.unpack(fmt, data)[0]
                    fmt = '%s%is' % (format, length)
                    data = stream.read(struct.calcsize(fmt))
                    s = struct.unpack(fmt, data)[0]
                    ans.append(s[:-1])  # strip the NULL
                return ans
            else:
                fmt = '%s%i%s' % (format, count, num_type)
                data = stream.read(struct.calcsize(fmt))
                return struct.unpack(fmt, data)

    def load(self, format, stream):
        if self.list_type is not None:
            count = int(self.read_format(format, 1, self.list_type, stream)[0])
            return self.read_format(format, count, self.numeric_type, stream)
        else:
            return self.read_format(format, 1, self.numeric_type, stream)[0]


class object_spec(object):
    __slots__ = ("specs",
                )
    'A list of element_specs'
    def __init__(self):
        self.specs = []

    def load(self, format, stream):
        return dict([(i.name, [i.load(format, stream) for j in range(i.count)]) for i in self.specs])

        '''
        # Longhand for above LC
        answer = {}
        for i in self.specs:
            answer[i.name] = []
            for j in range(i.count):
                if not j % 100 and meshtools.show_progress:
                    Blender.Window.DrawProgressBar(float(j) / i.count, 'Loading ' + i.name)
                answer[i.name].append(i.load(format, stream))
        return answer
            '''


def read(filepath):
    format = b''
    version = b'1.0'
    format_specs = {b'binary_little_endian': '<',
                    b'binary_big_endian': '>',
                    b'ascii': b'ascii'}
    type_specs = {b'char': 'b',
                  b'uchar': 'B',
                  b'int8': 'b',
                  b'uint8': 'B',
                  b'int16': 'h',
                  b'uint16': 'H',
                  b'ushort': 'H',
                  b'int': 'i',
                  b'int32': 'i',
                  b'uint': 'I',
                  b'uint32': 'I',
                  b'float': 'f',
                  b'float32': 'f',
                  b'float64': 'd',
                  b'double': 'd',
                  b'string': 's'}
    obj_spec = object_spec()

    file = open(filepath, 'rb')  # Only for parsing the header, not binary data
    signature = file.readline()

    if not signature.startswith(b'BristolFDTD'):
        print('Signature line was invalid')
        return None

    while 1:
        tokens = re.split(br'[ \r\n]+', file.readline())

        if len(tokens) == 0:
            continue
        if tokens[0] == b'end_header':
            break
        elif tokens[0] == b'comment' or tokens[0] == b'obj_info':
            continue
        elif tokens[0] == b'format':
            if len(tokens) < 3:
                print('Invalid format line')
                return None
            if tokens[1] not in format_specs:  # .keys(): # keys is implicit
                print('Unknown format', tokens[1])
                return None
            if tokens[2] != version:
                print('Unknown version', tokens[2])
                return None
            format = tokens[1]
        elif tokens[0] == b'element':
            if len(tokens) < 3:
                print(b'Invalid element line')
                return None
            obj_spec.specs.append(element_spec(tokens[1], int(tokens[2])))
        elif tokens[0] == b'property':
            if not len(obj_spec.specs):
                print('Property without element')
                return None
            if tokens[1] == b'list':
                obj_spec.specs[-1].properties.append(property_spec(tokens[4], type_specs[tokens[2]], type_specs[tokens[3]]))
            else:
                obj_spec.specs[-1].properties.append(property_spec(tokens[2], None, type_specs[tokens[1]]))

    if format != b'ascii':
        file.close()  # was ascii, now binary
        file = open(filepath, 'rb')

        # skip the header...
        while not file.readline().startswith(b'end_header'):
            pass

    obj = obj_spec.load(format_specs[format], file)

    file.close()

    return obj_spec, obj


import bpy


def load_BristolFDTD(filepath):
    import time
    from bpy_extras.io_utils import unpack_list, unpack_face_list
    from bpy_extras.image_utils import load_image

    t = time.time()
    print('filepath = ',filepath)
    return
    
    obj_spec, obj = read(filepath)
    if obj is None:
        print('Invalid file')
        return

    uvindices = colindices = None
    colmultiply = None

    # noindices = None # Ignore normals

    for el in obj_spec.specs:
        if el.name == b'vertex':
            vindices = vindices_x, vindices_y, vindices_z = el.index(b'x'), el.index(b'y'), el.index(b'z')
            # noindices = (el.index('nx'), el.index('ny'), el.index('nz'))
            # if -1 in noindices: noindices = None
            uvindices = (el.index(b's'), el.index(b't'))
            if -1 in uvindices:
                uvindices = None
            colindices = el.index(b'red'), el.index(b'green'), el.index(b'blue')
            if -1 in colindices:
                colindices = None
            else:  # if not a float assume uchar
                colmultiply = [1.0 if el.properties[i].numeric_type in ('f', 'd') else (1.0 / 256.0) for i in colindices]

        elif el.name == b'face':
            findex = el.index(b'vertex_indices')

    mesh_faces = []
    mesh_uvs = []
    mesh_colors = []

    def add_face(vertices, indices, uvindices, colindices):
        mesh_faces.append(indices)
        if uvindices:
            mesh_uvs.append([(vertices[index][uvindices[0]], 1.0 - vertices[index][uvindices[1]]) for index in indices])
        if colindices:
            mesh_colors.append([(vertices[index][colindices[0]] * colmultiply[0],
                                 vertices[index][colindices[1]] * colmultiply[1],
                                 vertices[index][colindices[2]] * colmultiply[2],
                                 ) for index in indices])

    if uvindices or colindices:
        # If we have Cols or UVs then we need to check the face order.
        add_face_simple = add_face

        # EVIL EEKADOODLE - face order annoyance.
        def add_face(vertices, indices, uvindices, colindices):
            if len(indices) == 4:
                if indices[2] == 0 or indices[3] == 0:
                    indices = indices[2], indices[3], indices[0], indices[1]
            elif len(indices) == 3:
                if indices[2] == 0:
                    indices = indices[1], indices[2], indices[0]

            add_face_simple(vertices, indices, uvindices, colindices)

    verts = obj[b'vertex']

    if b'face' in obj:
        for f in obj[b'face']:
            ind = f[findex]
            len_ind = len(ind)
            if len_ind <= 4:
                add_face(verts, ind, uvindices, colindices)
            else:
                # Fan fill the face
                for j in range(len_ind - 2):
                    add_face(verts, (ind[0], ind[j + 1], ind[j + 2]), uvindices, colindices)

    BristolFDTD_name = bpy.path.display_name_from_filepath(filepath)

    mesh = bpy.data.meshes.new(name=BristolFDTD_name)

    mesh.vertices.add(len(obj[b'vertex']))

    mesh.vertices.foreach_set("co", [a for v in obj[b'vertex'] for a in (v[vindices_x], v[vindices_y], v[vindices_z])])

    if mesh_faces:
        mesh.faces.add(len(mesh_faces))
        mesh.faces.foreach_set("vertices_raw", unpack_face_list(mesh_faces))

        if uvindices or colindices:
            if uvindices:
                uvlay = mesh.uv_textures.new()
            if colindices:
                vcol_lay = mesh.vertex_colors.new()

            if uvindices:
                for i, f in enumerate(uvlay.data):
                    BristolFDTD_uv = mesh_uvs[i]
                    for j, uv in enumerate(f.uv):
                        uv[0], uv[1] = BristolFDTD_uv[j]

            if colindices:
                for i, f in enumerate(vcol_lay.data):
                    # XXX, colors dont come in right, needs further investigation.
                    BristolFDTD_col = mesh_colors[i]
                    if len(BristolFDTD_col) == 4:
                        f_col = f.color1, f.color2, f.color3, f.color4
                    else:
                        f_col = f.color1, f.color2, f.color3

                    for j, col in enumerate(f_col):
                        col.r, col.g, col.b = BristolFDTD_col[j]

    mesh.validate()
    mesh.update()

    scn = bpy.context.scene
    #scn.objects.selected = [] # XXX25

    obj = bpy.data.objects.new(BristolFDTD_name, mesh)
    scn.objects.link(obj)
    scn.objects.active = obj
    obj.select = True

    print('\nSuccessfully imported %r in %.3f sec' % (filepath, time.time() - t))


def load(operator, context, filepath=""):
    load_BristolFDTD(filepath)
    return {'FINISHED'}

###############################
# MAIN FUNCTION
###############################
def main():
  ''' MAIN FUNCTION '''
  print('sys.argv=' + str(sys.argv))
  print('len(sys.argv)=' + str(len(sys.argv)))
  
  # arg[0]='blender'
  # arg[1]='-P'
  # arg[2]='scriptname'
  # arg[3]='--'
  
  if len(sys.argv)>4:
      for i in range(len(sys.argv)- 4):
          print('Importing ' + sys.argv[4+i])
          importBristolFDTD(sys.argv[4+i]);
  else:
      ###################
      # load import path
      ###################
      # print('tempdir=',Blender.Get('tempdir'))
      # print('soundsdir=',Blender.Get('soundsdir'))
  
      # default_path = Blender.Get('tempdir');
      # if not default_path:
          # default_path = os.getenv('DATADIR');
          
      default_path = os.getenv('DATADIR')
      print('cfgfile = ', cfgfile)
  
      if os.path.isfile(cfgfile) and os.path.getsize(cfgfile) > 0:
          #with open(, 'r') as FILE:
               #= pickle.load(FILE);
        with open(cfgfile, 'rb') as f:
          # The protocol version used is detected automatically, so we do not
          # have to specify it.
          default_path = pickle.load(f)
      ###################
  
      ###################
      # import file
      ###################
      Blender.Window.FileSelector(importBristolFDTD, "Import Bristol FDTD file...", default_path);
      # TestObjects();

class IMPORT_OT_autocad_dxf(bpy.types.Operator):
    '''Import from BFDTD file format (.geo,.inp,.in)'''
    bl_idname = "import_scene.BFDTD"
    bl_description = 'Import from BFDTD file format (.geo,.inp,.in)'
    bl_label = "Import BFDTD" +' v.'+ __version__
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filepath = StringProperty(name="File Path", description="Filepath used for importing the BFDTD file", maxlen= 1024, default= "", subtype='FILE_PATH')

    new_scene = BoolProperty(name="Replace scene", description="Replace scene", default=toggle&T_NewScene)
    #new_scene = BoolProperty(name="New scene", description="Create new scene", default=toggle&T_NewScene)
    curves = BoolProperty(name="Draw curves", description="Draw entities as curves", default=toggle&T_Curves)
    thic_on = BoolProperty(name="Thic ON", description="Support THICKNESS", default=toggle&T_ThicON)

    merge = BoolProperty(name="Remove doubles", description="Merge coincident vertices", default=toggle&T_Merge)
    mergeLimit = FloatProperty(name="Limit", description="Merge limit", default = theMergeLimit*1e4,min=1.0, soft_min=1.0, max=100.0, soft_max=100.0)

    draw_one = BoolProperty(name="Merge all", description="Draw all into one mesh-object", default=toggle&T_DrawOne)
    circleResolution = IntProperty(name="Circle resolution", description="Circle/Arc are aproximated will this factor", default = theCircleRes,
                min=4, soft_min=4, max=360, soft_max=360)
    codecs = tripleList(['iso-8859-15', 'utf-8', 'ascii'])
    codec = EnumProperty(name="Codec", description="Codec",  items=codecs, default = 'ascii')

    debug = BoolProperty(name="Debug", description="Unknown DXF-codes generate errors", default=toggle&T_Debug)
    verbose = BoolProperty(name="Verbose", description="Print debug info", default=toggle&T_Verbose)

    ##### DRAW #####
    def draw(self, context):
        layout0 = self.layout
        #layout0.enabled = False

        #col = layout0.column_flow(2,align=True)
        layout = layout0.box()
        col = layout.column()
        #col.prop(self, 'KnotType') waits for more knottypes
        #col.label(text="import Parameters")
        #col.prop(self, 'replace')
        col.prop(self, 'new_scene')
        
        row = layout.row(align=True)
        row.prop(self, 'curves')
        row.prop(self, 'circleResolution')

        row = layout.row(align=True)
        row.prop(self, 'merge')
        if self.merge:
            row.prop(self, 'mergeLimit')
 
        row = layout.row(align=True)
        #row.label('na')
        row.prop(self, 'draw_one')
        row.prop(self, 'thic_on')

        col = layout.column()
        col.prop(self, 'codec')
 
        row = layout.row(align=True)
        row.prop(self, 'debug')
        if self.debug:
            row.prop(self, 'verbose')
         
    def execute(self, context):
        global toggle, theMergeLimit, theCodec, theCircleRes
        O_Merge = T_Merge if self.merge else 0
        #O_Replace = T_Replace if self.replace else 0
        O_NewScene = T_NewScene if self.new_scene else 0
        O_Curves = T_Curves if self.curves else 0
        O_ThicON = T_ThicON if self.thic_on else 0
        O_DrawOne = T_DrawOne if self.draw_one else 0
        O_Debug = T_Debug if self.debug else 0
        O_Verbose = T_Verbose if self.verbose else 0

        toggle =  O_Merge | O_DrawOne | O_NewScene | O_Curves | O_ThicON | O_Debug | O_Verbose
        theMergeLimit = self.mergeLimit*1e-4
        theCircleRes = self.circleResolution
        theCodec = self.codec

        readAndBuildDxfFile(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_func(self, context):
    self.layout.operator(IMPORT_OT_autocad_dxf.bl_idname, text="MOMOMOMOMO (.dxf)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func)

 
def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()
