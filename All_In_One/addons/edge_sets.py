import bpy
import bmesh


bl_info = {
    "name": "Edge Sets",
    "author": "Isaac Weaver",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "Properties > Mesh > Edge Sets",
    "description": "Create edge sets to easily manage edge creases and bevel weights.",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}


# ------------------
# --- Utilities ----
# ------------------
class create_bmesh(object):
    def __init__(self, mesh):
        self.bm = bmesh.new()
        self.mesh = mesh

    def __enter__(self):
        self.bm.from_mesh(self.mesh)
        return self.bm

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bm.to_mesh(self.mesh)
        self.bm.free()


class create_edit_bmesh(object):
    def __init__(self, mesh):
        self.bm = None
        self.mesh = mesh

    def __enter__(self):
        self.bm = bmesh.from_edit_mesh(self.mesh)
        return self.bm

    def __exit__(self, exc_type, exc_val, exc_tb):
        bmesh.update_edit_mesh(self.mesh)


def create_general_bmesh(context, mesh):
    if context.mode == 'EDIT_MESH':
        return create_edit_bmesh(mesh)
    else:
        return create_bmesh(mesh)


# ------------------
# --- Properties ---
# ------------------
def crease_update_callback(self, context):
    mesh = self.id_data
    index = mesh.edge_sets.values().index(self)

    with create_general_bmesh(context, mesh) as bm:
        name = 'edge_set'
        if name in bm.edges.layers.int:
            if len(bm.edges.layers.crease) > 0:
                crease = bm.edges.layers.crease[0]
            else:
                crease = bm.edges.layers.crease.new()
            edge_set = bm.edges.layers.int[name]

            for edge in bm.edges:
                if edge[edge_set] - 1 == index:
                    edge[crease] = self.crease


def bevel_update_callback(self, context):
    mesh = self.id_data
    index = mesh.edge_sets.values().index(self)

    with create_general_bmesh(context, mesh) as bm:
        name = 'edge_set'
        if name in bm.edges.layers.int:
            if len(bm.edges.layers.bevel_weight) > 0:
                bevel = bm.edges.layers.bevel_weight[0]
            else:
                bevel = bm.edges.layers.bevel_weight.new()
            edge_set = bm.edges.layers.int[name]

            for edge in bm.edges:
                if edge[edge_set] - 1 == index:
                    edge[bevel] = self.bevel


class EdgeSetItem(bpy.types.PropertyGroup):
    crease = bpy.props.FloatProperty(
        name="Crease",
        subtype='FACTOR',
        min=0, max=1,
        update=crease_update_callback)

    bevel = bpy.props.FloatProperty(
        name="Bevel Weight",
        subtype='FACTOR',
        min=0, max=1,
        update=bevel_update_callback)


# ------------------
# --- Operators ----
# ------------------
class AddEdgeSetOperator(bpy.types.Operator):
    """Add an edge set to the active mesh"""
    bl_idname = "mesh.edge_set_add"
    bl_label = "Add Edge Set"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == "MESH"

    def execute(self, context):
        mesh = context.object.data
        mesh.edge_sets.add().name = "Edge Set"
        mesh.active_edge_set_index = len(mesh.edge_sets) - 1
        return {"FINISHED"}


class RemoveEdgeSetOperator(bpy.types.Operator):
    """Remove an edge set from the active mesh"""
    bl_idname = "mesh.edge_set_remove"
    bl_label = "Remove Edge Set"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == "MESH"

    def execute(self, context):
        mesh = context.object.data
        mesh.edge_sets.remove(mesh.active_edge_set_index)

        if mesh.active_edge_set_index > 0:
            mesh.active_edge_set_index -= 1

        return {"FINISHED"}


class AssignEdgeSetOperator(bpy.types.Operator):
    """Assign the selected edges to the active edge set"""
    bl_idname = "mesh.edge_set_assign"
    bl_label = "Assign"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == "MESH" and context.mode == "EDIT_MESH"

    def execute(self, context):
        mesh = context.object.data
        name = 'edge_set'

        with create_edit_bmesh(mesh) as bm:
            if name not in bm.edges.layers.int:
                edge_set = bm.edges.layers.int.new(name)
            else:
                edge_set = bm.edges.layers.int[name]

            for edge in bm.edges:
                if edge.select:
                    edge[edge_set] = mesh.active_edge_set_index + 1

        return {"FINISHED"}


class RemoveFromEdgeSetOperator(bpy.types.Operator):
    """Remove the selected edges from the active edge set"""
    bl_idname = "mesh.edge_set_remove_from"
    bl_label = "Remove"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == "MESH" and context.mode == "EDIT_MESH"

    def execute(self, context):
        mesh = context.object.data
        name = "edge_set"

        with create_edit_bmesh(mesh) as bm:
            if name in bm.edges.layers.int:
                edge_set = bm.edges.layers.int[name]

                for edge in bm.edges:
                    if edge.select:
                        edge[edge_set] = 0
        return {"FINISHED"}


class SelectEdgeSetOperator(bpy.types.Operator):
    """Select the edges in the edge set"""
    bl_idname = "mesh.edge_set_select"
    bl_label = "Select"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == "MESH" and context.mode == "EDIT_MESH"

    def execute(self, context):
        mesh = context.object.data
        name = "edge_set"

        with create_edit_bmesh(mesh) as bm:
            if name in bm.edges.layers.int:
                edge_set = bm.edges.layers.int[name]

                for edge in bm.edges:
                    if edge[edge_set] - 1 == mesh.active_edge_set_index:
                        edge.select = True
                bm.select_flush_mode()
        return {"FINISHED"}


class DeselectEdgeSetOperator(bpy.types.Operator):
    """Deselect the edges in the edge set"""
    bl_idname = "mesh.edge_set_deselect"
    bl_label = "Deselect"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == "MESH" and context.mode == "EDIT_MESH"

    def execute(self, context):
        mesh = context.object.data
        name = "edge_set"

        with create_edit_bmesh(mesh) as bm:
            if name in bm.edges.layers.int:
                edge_set = bm.edges.layers.int[name]

                for edge in bm.edges:
                    if edge[edge_set] - 1 == mesh.active_edge_set_index:
                        edge.select = False
                bm.select_flush_mode()
        return {"FINISHED"}


# ------------------
# ------ UI --------
# ------------------
class OBJECT_UL_edge_sets(bpy.types.UIList):
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
        edge_set = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            col = row.column()

            col.prop(edge_set, "name", text="", emboss=False, icon_value=icon)

            col = row.column(align=True)
            col.prop(edge_set, "crease", emboss=False)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


# And now we can use this list everywhere in Blender. Here is a small example panel.
class EdgeSetsPanel(bpy.types.Panel):
    """Object mesh edges sets panel"""
    bl_label = "Edge Sets"
    bl_idname = "OBJECT_PT_ui_edge_sets"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return (context.object is not None) and (context.object.type == "MESH")

    def draw(self, context):
        layout = self.layout
        mesh = context.object.data

        row = layout.row()
        col = row.column()

        col.template_list("OBJECT_UL_edge_sets", "", mesh, "edge_sets", mesh, "active_edge_set_index", rows=1)

        col = row.column(align=True)
        col.operator("mesh.edge_set_add", icon='ZOOMIN', text="")
        col.operator("mesh.edge_set_remove", icon='ZOOMOUT', text="")

        row = layout.row()
        row.prop(mesh.edge_sets[mesh.active_edge_set_index], 'crease')
        row = layout.row()
        row.prop(mesh.edge_sets[mesh.active_edge_set_index], 'bevel')

        if context.mode == "EDIT_MESH" and len(mesh.edge_sets) > 0:
            row = layout.row()

            sub = row.row(align=True)
            sub.operator("mesh.edge_set_assign", text="Assign")
            sub.operator("mesh.edge_set_remove_from", text="Remove")

            sub = row.row(align=True)
            sub.operator("mesh.edge_set_select", text="Select")
            sub.operator("mesh.edge_set_deselect", text="Deselect")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.Mesh.edge_sets = bpy.props.CollectionProperty(type=EdgeSetItem)
    bpy.types.Mesh.active_edge_set_index = bpy.props.IntProperty()


def unregister():
    del bpy.types.Mesh.edge_sets
    del bpy.types.Mesh.active_edge_set_index

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
