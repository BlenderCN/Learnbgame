bl_info = {
    'name': 'Edge Groups',
    'author': 'Antti Elonen',
    'version': (0,0,1),
    'blender': (2, 79, 0),
    'location': 'Object data',
    'description': 'Edge groups',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Object'
}

import bpy, bmesh

def init():
    global dic
    dic = {}
    bpy.types.Object.edge_groups = bpy.props.CollectionProperty(type=EdgeGroup)
    bpy.types.Object.active_edge_group_index = bpy.props.IntProperty(name="Active Edge Group Index")
    bpy.app.handlers.scene_update_post.append(edit_object_change_handler)

dic = {}

class EdgeGroupPanel(bpy.types.Panel):
    """A panel listing edge groups and buttons to manipulate them.
    """
    bl_label = "Edge groups"
    bl_idname = "edge_group_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"


    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type in {'MESH', 'LATTICE'})


    def draw(self, context):
        layout = self.layout

        obj = context.object
        me = context.mesh

        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "edge_groups", obj, "edge_groups", obj, "active_edge_group_index")

        col = row.column(align=True)
        col.operator("object.edge_group_add", icon='ZOOMIN', text="")
        col.operator("object.edge_group_delete", icon='ZOOMOUT', text="")
        if obj.edge_groups:
            col.separator()
            col.operator("object.edge_group_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("object.edge_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if obj.edge_groups and obj.mode == 'EDIT':
            row = layout.row()

            sub = row.row(align=True)
            sub.operator("object.edge_group_assign", text="Assign")
            sub.operator("object.edge_group_remove", text="Remove")

            sub = row.row(align=True)
            sub.operator("object.edge_group_select", text="Select")
            sub.operator("object.edge_group_deselect", text="Deselect")


class EdgeGroupAdd(bpy.types.Operator):
    """Add an edge group to an object
    """
    bl_idname = "object.edge_group_add"
    bl_label = "add"
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        t = bpy.context.object.edge_groups.add()
        t.name = "new_edge_group"
        return {'FINISHED'}

class EdgeGroupDelete(bpy.types.Operator):
    """Delete an edge group from an object
    """
    bl_idname = "object.edge_group_delete"
    bl_label = "delete"
    @classmethod
    def poll(cls, context):
        return True
    def execute(self, context):
        obj = context.object
        obj.edge_groups.remove(obj.active_edge_group_index)
        return {'FINISHED'}

class EdgeGroupMove(bpy.types.Operator):
    """Move an edge group
    """
    bl_idname = "object.edge_group_move"
    bl_label = "move"
    direction = bpy.props.StringProperty(name="direction", default="UP")
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        pass #TODO
        return {'FINISHED'}


class EdgeGroupSelect(bpy.types.Operator):
    """Select edges of an edge group
    """
    bl_idname = "object.edge_group_select"
    bl_label = "select"
    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type in {'MESH', 'LATTICE'})
    def execute(self, context):
        eo = context.edit_object
        bm = dic.setdefault(eo.name, bmesh.from_edit_mesh(eo.data))
        egl = bm.edges.layers.int.get("edge_groups")
        edges = []
        for e in bm.edges:
            if e[egl] is 1:
                e.select = 1
        bpy.context.scene.objects.active = bpy.context.scene.objects.active
        return {'FINISHED'}

class EdgeGroupDeselect(bpy.types.Operator):
    """Deselect edges of an edge group
    """
    bl_idname = "object.edge_group_deselect"
    bl_label = "deselect"
    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type in {'MESH', 'LATTICE'})
    def execute(self, context):
        eo = context.edit_object
        bm = dic.setdefault(eo.name, bmesh.from_edit_mesh(eo.data))
        egl = bm.edges.layers.int.get("edge_groups")
        edges = []
        for e in bm.edges:
            if e[egl] is 1:
                e.select = 0
        bpy.context.scene.objects.active = bpy.context.scene.objects.active
        return {'FINISHED'}

class EdgeGroupAssign(bpy.types.Operator):
    """Assign edges of an edge group
    """
    """Tooltip"""
    bl_idname = "object.edge_group_assign"
    bl_label = "assign"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type in {'MESH', 'LATTICE'})

    def execute(self, context):
        eo = context.edit_object
        bm = dic.setdefault(eo.name, bmesh.from_edit_mesh(eo.data))
        egl = bm.edges.layers.int.get("edge_groups")
        edges = []
        for e in bm.edges:
            if e.select:
                e[egl] = 1

        # trigger viewport update
        bpy.context.scene.objects.active = bpy.context.scene.objects.active
        return {'FINISHED'}

class EdgeGroupRemove(bpy.types.Operator):
    """Remove an edge group
    """
    bl_idname = "object.edge_group_remove"
    bl_label = "remove"
    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type in {'MESH', 'LATTICE'})
    def execute(self, context):
        eo = context.edit_object
        bm = dic.setdefault(eo.name, bmesh.from_edit_mesh(eo.data))
        egl = bm.edges.layers.int.get("edge_groups")
        edges = []
        for e in bm.edges:
            if e.select:
                e[egl] = 0
        return {'FINISHED'}

class EdgeGroup(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Group Name", default="Unknown")

class ActiveEdgeGroupIndex(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Group Name", default="Unknown")

def edit_object_change_handler(scene):
    obj = scene.objects.active
    if obj is None:
        return None
    # add one instance of edit bmesh to global dic
    if obj.mode == 'EDIT' and obj.type == 'MESH':
        bm = dic.setdefault(obj.name, bmesh.from_edit_mesh(obj.data))
        if bm.edges.layers.int.get("edge_groups") is None:
            edge_groups_layer = bm.edges.layers.int.new("edge_groups")
        return None

    dic.clear()
    return None

def register():
    bpy.utils.register_class(EdgeGroup)
    bpy.utils.register_class(EdgeGroupAdd)
    bpy.utils.register_class(EdgeGroupDelete)
    bpy.utils.register_class(EdgeGroupMove)
    bpy.utils.register_class(EdgeGroupAssign)
    bpy.utils.register_class(EdgeGroupRemove)
    bpy.utils.register_class(EdgeGroupSelect)
    bpy.utils.register_class(EdgeGroupDeselect)
    bpy.utils.register_class(EdgeGroupPanel)
    init()


def unregister():
    bpy.utils.unregister_class(EdgeGroup)
    bpy.utils.unregister_class(EdgeGroupAdd)
    bpy.utils.unregister_class(EdgeGroupDelete)
    bpy.utils.unregister_class(EdgeGroupMove)
    bpy.utils.unregister_class(EdgeGroupAssign)
    bpy.utils.unregister_class(EdgeGroupRemove)
    bpy.utils.unregister_class(EdgeGroupSelect)
    bpy.utils.unregister_class(EdgeGroupDeselect)
    bpy.utils.unregister_class(EdgeGroupPanel)


if __name__ == "__main__":
    register()
