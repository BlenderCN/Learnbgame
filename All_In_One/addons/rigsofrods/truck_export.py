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
from bpy_extras.io_utils import ExportHelper

def export_menu_func(self, context):
    self.layout.operator(ROR_OT_truck_export.bl_idname, text="Truck (.truck)")

class ROR_OT_truck_export(bpy.types.Operator, ExportHelper):
    bl_idname = "export_truck.truck"
    bl_label = "Export RoR Truck"
    filename_ext = ""
    filter_glob: bpy.props.StringProperty(
            default="*.truck;*.trailer;*.load;*.car;*.boat;*.airplane;*.train;*.machine;*.fixed",
            options={'HIDDEN'},
            )
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        nodes = []
        beams = []
        cabs = []

        for obj in context.selected_objects[:1]:
            if obj.type != 'MESH':
                continue

            current_mode = bpy.context.object.mode
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.mode_set(mode="EDIT")
            bm = bmesh.from_edit_mesh(obj.data)

            group_names = {group.index : group.name for group in obj.vertex_groups}
            node_digits = len(str(len(obj.data.vertices) - 1))

            format_string = '{:'+str(node_digits)+'d}, {: 8.3f}, {: 8.3f}, {: 8.3f}'
            presets_key = bm.verts.layers.int.get("presets")
            options_key = bm.verts.layers.string.get("options")
            bm.verts.ensure_lookup_table()
            for v, bv in zip(obj.data.vertices, bm.verts):
                preset_idx = -1
                if presets_key:
                    preset_idx = bv[presets_key];
                options = ''
                if options_key:
                    options = bv[options_key].decode()
                if not options:
                    options = 'n'
                groups = [group_names[g.group] for g in v.groups]
                nodes.append([format_string.format(v.index, v.co[1], v.co[2], v.co[0]), options, groups, preset_idx])

            format_string = '{:'+str(node_digits)+'d}, {:'+str(node_digits)+'d}'
            presets_key = bm.edges.layers.int.get("presets")
            options_key = bm.edges.layers.string.get("options")
            bm.edges.ensure_lookup_table()
            for e, be in zip(obj.data.edges, bm.edges):
                preset_idx = -1
                if presets_key:
                    preset_idx = be[presets_key]
                options = ''
                if options_key:
                    options = be[options_key].decode()
                if not options:
                    options = 'v'
                ids = sorted([[g.group for g in obj.data.vertices[e.vertices[i]].groups] for i in [0, 1]])
                vg1, vg2 = [[group_names[g] for g in ids[i]] for i in [0, 1]]
                groups = vg1 if vg1 == vg2 else [', '.join(vg1)] + [">"] + [', '.join(vg2)]
                beams.append([ids, groups, format_string.format(e.vertices[0], e.vertices[1]), options, preset_idx])

            format_string = '{:'+str(node_digits)+'d}, {:'+str(node_digits)+'d}, {:'+str(node_digits)+'d}'
            options_key = bm.faces.layers.string.get("options")
            bm.faces.ensure_lookup_table()
            for p, bp in zip(obj.data.polygons, bm.faces):
                if len(p.vertices) == 3:
                    options = ''
                    if options_key:
                        options = bp[options_key].decode()
                    if not options:
                        options = 'c'
                    cabs.append([format_string.format(p.vertices[0], p.vertices[1], p.vertices[2]), options])

            bpy.ops.object.mode_set(mode=current_mode)
            bm.free()

        truckfile = []
        indices = [0, 0, 0]
        truck = bpy.context.active_object.ror_truck
        truckfile = []
        for entry in truck.truckfile_lines:
            truckfile.append(entry.line)

        with open(self.filepath, 'w') as f:
            for line in truckfile[:truck.truckfile_nodes_pos]:
                print (line, file=f)

            print("nodes", file=f)
            node_preset_idx = -1 # -1 means 'not set'
            vertex_groups = []
            for n in sorted(nodes):
                if n[-1] != node_preset_idx:
                    node_preset_idx = n[-1]
                    if node_preset_idx == -1:
                        print('set_node_defaults -1, -1, -1, -1', file=f) # reset all to builtin values
                    else:
                        print (truck.node_presets[node_preset_idx].args_line, file=f)
                if n[-2] != vertex_groups:
                    vertex_groups = n[-2]
                    print (";grp:", ', '.join(vertex_groups), file=f)
                print (*n[:-2], sep=', ', file=f)

            lines = truckfile[truck.truckfile_nodes_pos:truck.truckfile_beams_pos]
            if not lines:
                lines = ['']
            for line in lines:
                print (line, file=f)

            print("beams", file=f)
            beam_preset_idx = -1
            edge_groups = []
            for b in sorted(beams):
                if b[-1] != beam_preset_idx:
                    beam_preset_idx = b[-1]
                    if beam_preset_idx == -1:
                        print('set_beam_defaults -1, -1, -1, -1', file=f) # reset all to builtin values
                    else:
                        print (truck.beam_presets[beam_preset_idx].args_line, file=f)
                if b[1] != edge_groups:
                    edge_groups = b[1]
                    print (";grp:", *edge_groups, file=f)
                print (*b[2:-1], sep=', ', file=f)

            lines = truckfile[truck.truckfile_beams_pos:truck.truckfile_cab_pos]
            if not lines:
                lines = ['']
            for line in lines:
                print (line, file=f)

            if cabs:
                print ("cab", file=f)
                for c in cabs:
                    print (*c, sep=', ', file=f)

            for line in truckfile[truck.truckfile_cab_pos:]:
                print (line, file=f)

        return {'FINISHED'}
