import bpy
import json
import bmesh

# Blender convention dictates uppercase prefix
class ROR_UL_node_presets(bpy.types.UIList):
    # The draw_item function is called for each item of the collection that is visible in the list.
    #   data is the RNA object containing the collection,
    #   item is the current drawn item of the collection,
    #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
    #   have custom icons ID, which are not available as enum items).
    #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
    #   active item of the collection).
    #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
    #   index is index of the current item in the collection.
    #   flt_flag is the result of the filtering process for this item.
    #   Note: as index and flt_flag are optional arguments, you do not have to use/declare them here if you don't
    #         need them.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            # NOTE: layout.prop() param 'icon_value'
            #   -must not be None, otherwise list entries  are empty (no text)
            #   -value of 0 is OK
            layout.prop(item, "args_line", text="", emboss=False, icon_value=0)

        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


# Reference: https://docs.blender.org/api/blender2.8/bpy.types.Operator.html
class ROR_OT_node_presets(bpy.types.Operator):
    bl_idname = "mesh.ror_node_presets_op"
    bl_label = "Node presets manipulation"

    action = bpy.props.StringProperty() # {'SELECT', 'DESELECT', 'ASSIGN', 'REMOVE', 'CREATE', 'DELETE', 'SELECT_UNASSIGNED'} TODO: make enum

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        return active_object and active_object.type == 'MESH' and active_object.mode == 'EDIT' and active_object.ror_truck

    def execute(self, context):
        rig_def = context.object.ror_truck
        if self.action == 'CREATE':
            preset = context.object.ror_truck.node_presets.add()
            preset.args_line = 'set_node_defaults ' 
        else:
            mesh = context.object.data
            bm = bmesh.from_edit_mesh(mesh)
            bm.edges.ensure_lookup_table()
            presets_key = bm.verts.layers.int.get("presets")
            if (self.action == 'DELETE'):
                ror_truck.node_presets.remove(ror_truck.active_node_preset_index)
                for bv in bm.verts:
                    if bv[presets_key] == ror_truck.active_node_preset_index:
                        bv[presets_key] = -1 # not assigned
            elif (self.action == 'SELECT' or self.action == 'DESELECT'):
                bpy.ops.mesh.select_mode(type="VERT") # Reference: https://docs.blender.org/api/blender2.8/bpy.ops.mesh.html?highlight=select_mode#bpy.ops.mesh.select_mode
                for bv in bm.verts:
                    if bv[presets_key] == ror_truck.active_node_preset_index:
                        bv.select_set(self.action == 'SELECT')
            elif self.action == 'ASSIGN':
                for bv in bm.verts:
                    if bv.select:
                        bv[presets_key] = ror_truck.active_node_preset_index
            elif self.action == 'REMOVE':
                for bv in bm.verts:
                    if bv.select and bv[presets_key] == ror_truck.active_node_preset_index:
                        bv[presets_key] = -1 # not assigned
            elif self.action == 'SELECT_UNASSIGNED':
                bpy.ops.mesh.select_mode(type="VERT")
                for bv in bm.verts:
                    if bv[presets_key] == -1:
                        bv.select_set(True)
            bm.select_flush_mode()
            bmesh.update_edit_mesh(mesh, True)

        return {'FINISHED'}



class ROR_PT_node_presets(bpy.types.Panel):
    """ Add, assign on remove node presets (directive `set_node_defaults` in Truckfile) """
    bl_label = "Node Presets"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = bpy.context.active_object

        row = layout.row()
        row.template_list("ROR_UL_node_presets", "ror_node_presets",
            obj.ror_truck, "node_presets",              # context and property
            obj.ror_truck, "active_node_preset_index",  # context and property
            )

        row = layout.row()
        # HOWTO add UI button: https://docs.blender.org/api/blender2.8/bpy.types.UILayout.html#bpy.types.UILayout.operator
        op_props = row.operator("mesh.ror_node_presets_op", text="Select")
        op_props.action = 'SELECT'

        op_props = row.operator("mesh.ror_node_presets_op", text="Deselect")
        op_props.action = 'DESELECT'

        row = layout.row()
        op_props = row.operator("mesh.ror_node_presets_op", text="Assign")
        op_props.action = 'ASSIGN'

        op_props = row.operator("mesh.ror_node_presets_op", text="Remove")
        op_props.action = 'REMOVE'

        row = layout.row()
        op_props = row.operator("mesh.ror_node_presets_op", text="Create")
        op_props.action = 'CREATE'

        op_props = row.operator("mesh.ror_node_presets_op", text="Delete")
        op_props.action = 'DELETE'

        row = layout.row()
        op_props = row.operator("mesh.ror_node_presets_op", text="Select unassigned")
        op_props.action = 'SELECT_UNASSIGNED'

