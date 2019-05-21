# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
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

# Author: Ulteq (https://github.com/ulteq)

import bpy
import bmesh
from bpy_extras.io_utils import ImportHelper

def import_menu_func(self, context):
    self.layout.operator(ROR_OT_truck_import.bl_idname, text="Truck (.truck)")

class ROR_OT_truck_import(bpy.types.Operator, ImportHelper):
    bl_idname = "import_truck.truck"
    bl_label = "Import RoR Truck"
    filename_ext = ""
    filter_glob: bpy.props.StringProperty(
            default="*.truck;*.trailer;*.load;*.car;*.boat;*.airplane;*.train;*.machine;*.fixed",
            options={'HIDDEN'},
            )
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        truckfile = []
        node_idx = 0
        nodes = []
        beam_idx = 0
        beams = []
        cab_idx = 0
        cabs = []

        with open(self.filepath, 'r') as f:
            node_defaults = ''
            beam_defaults = ''
            mode = 'name' # 'name', 'nodes', 'beams', 'cab', 'ignore'
            groups = []
            truck_name = ''
            for line in f:
                line = line.strip()
                if not line or line[0] == ';':
                    if mode == 'name':
                        truck_name = line;
                        mode = 'ignore'
                    elif mode == 'nodes' and line[:5] == ';grp:':
                        groups = [g.strip() for g in line[5:].split(',')]
                    elif mode == 'beams' and line[:5] == ';grp:':
                        pass
                    else:
                        truckfile.append(line)
                    continue

                args = line.replace(',', ' ').split()
                if not args or "set_" in args[0]:
                    if args and mode == 'nodes' and "set_n" in args[0]:
                        node_defaults = line
                    if args and mode == 'beams' and "set_b" in args[0]:
                        beam_defaults = line
                    else:
                        truckfile.append(line)
                    continue

                if args[0] == 'nodes':
                    mode = 'nodes'
                    node_defaults = ''
                    node_idx = len(truckfile)
                    continue
                elif args[0] == 'beams':
                    mode = 'beams'
                    beam_defaults = ''
                    beam_idx = len(truckfile)
                    continue
                elif args[0] == 'cab':
                    mode = 'cab'
                    cab_idx = len(truckfile)
                    continue
                elif not args[0].isdigit() or mode == 'ignore':
                    truckfile.append(line)
                    mode = 'ignore'

                if mode == 'nodes':
                    nodes.append([node_defaults] + [groups] + args[1:])
                elif mode == 'beams':
                    beams.append([beam_defaults] + args)
                elif mode == 'cab':
                    cabs.append(args)

        mesh = bpy.data.meshes.new(truck_name)
        obj  = bpy.data.objects.new(truck_name, mesh)

        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        if (beam_idx < node_idx):
            beam_idx = len(truckfile)
        if (cab_idx < beam_idx):
            cab_idx = len(truckfile)
            
        obj.ror_truck.truckfile_path = self.filepath        
        obj.ror_truck.truckfile_nodes_pos = node_idx
        obj.ror_truck.truckfile_beams_pos = beam_idx
        obj.ror_truck.truckfile_cab_pos = cab_idx    

        mesh = bpy.context.object.data
        bm   = bmesh.new()
        dl   = bm.verts.layers.deform.verify()

        presets_key = bm.verts.layers.int.new("presets") # indices to 'RoR_Truck.node_presets'
        options_key = bm.verts.layers.string.new("options")
        node_presets = []
        for n in nodes:
            try:
                v = bm.verts.new((float(n[4]), float(n[2]), float(n[3])))
                bm.verts.ensure_lookup_table()
                bm.verts.index_update()
                # options
                bm.verts[-1][options_key] = ' '.join(n[5:]).encode()
                # presets
                if len(node_presets) == 0 or n[0] != node_presets[-1]:
                    if n[0] != "":
                        node_presets.append(n[0])
                        print("----ROR import: adding node preset: ", n[0])
                bm.verts[-1][presets_key] = len(node_presets) - 1 # -1 means 'no preset'
                # vertex groups
                for g in n[1]:
                    vg = obj.vertex_groups.get(g)
                    if not vg:
                        vg = obj.vertex_groups.new(g)
                    v[dl][vg.index] = 1.0
            except:
                print ("Failed to add vertex:", n)

        presets_key = bm.edges.layers.int.new("presets") # indices to 'RoR_Truck.beam_presets'
        options_key = bm.edges.layers.string.new("options")
        beam_presets = []
        for b in beams:
            try:
                bm.edges.new((bm.verts[int(i)] for i in b[1:3]))
                bm.edges.ensure_lookup_table()
                # Process options
                bm.edges[-1][options_key] = ' '.join(b[3:]).encode()
                # Process presets
                if len(beam_presets) == 0 or b[0] != beam_presets[-1]:
                    if b[0] != "":
                        beam_presets.append(b[0])
                        print("----ROR import: adding beam preset: ", b[0])
                bm.edges[-1][presets_key] = len(beam_presets) - 1 # -1 means 'no preset'
            except:
                print ("Failed to add edge:", b)

        options_key = bm.faces.layers.string.new("options")
        for c in cabs:
            try:
                bm.faces.new((bm.verts[int(i)] for i in c[:3]))
                bm.faces.ensure_lookup_table()
                bm.faces[-1][options_key] = ' '.join(c[3:]).encode()
            except:
                print ("Failed to add face:", c)

        bm.to_mesh(mesh)
        bm.free()

        # Beam presets
        obj = bpy.context.active_object
        for line in beam_presets:
            preset = obj.ror_truck.beam_presets.add()
            preset.args_line = line

        # Node presets
        for line in node_presets:
            preset = obj.ror_truck.node_presets.add()
            preset.args_line = line
            
        # Lines
        for line in truckfile:
            tl = obj.ror_truck.truckfile_lines.add()
            tl.line = line 

        return {'FINISHED'}
