bl_info = {
    "name": "World C Plugin",
    'author': 'Justin Meiners',
    "location": "Many",
    "category": "Games"
}

if "bpy" in locals():
    import imp
    imp.reload(world_export)
else:
    import bpy
    from bpy.props import *
    from . import (export_level)
    from . import (export_mesh)
    from . import (export_skmesh)
    from . import (export_skanim)
    from . import (export_nav)

class LevelExport(bpy.types.Operator):
    bl_idname = "export_mesh.level"
    bl_label = bl_info['name']

    filepath = StringProperty(name="File Path", description="Filepath used for exporting", maxlen=1024, default= "")

    def execute(self, context):
        export_level.export(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".lvl")
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class BinaryMeshExport(bpy.types.Operator):
    bl_idname = "export_mesh.bmesh"
    bl_label = bl_info['name']

    filepath = StringProperty(name="File Path", description="Filepath used for exporting", maxlen=1024, default="")

    def execute(self, context):
        selection = bpy.context.selected_objects

        b_mesh = None
        for selected in selection:
            if selected.type == "MESH":
                b_mesh = selected

        if b_mesh is None:
            print("fail")
            return {'CANCELLED'}

        export_mesh.export_binary(b_mesh, self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".bmesh")
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MeshExport(bpy.types.Operator):
    bl_idname = "export_mesh.mesh"
    bl_label = bl_info['name']

    filepath = StringProperty(name="File Path", description="Filepath used for exporting", maxlen=1024, default="")

    def execute(self, context):
        selection = bpy.context.selected_objects

        b_mesh = None
        for selected in selection:
            if selected.type == "MESH":
                b_mesh = selected

        if b_mesh is None:
            print("fail")
            return {'CANCELLED'}

        export_mesh.export(b_mesh, self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".mesh")
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class SkMeshExport(bpy.types.Operator):
    bl_idname = "export_mesh.skmesh"
    bl_label = bl_info['name']

    filepath = StringProperty(name="File Path", description="Filepath used for exporting", maxlen=1024, default="")

    def execute(self, context):
        selection = bpy.context.selected_objects
        scene = bpy.context.scene

        b_mesh = None
        b_armature = None
        b_attach_points = []

        for selected in selection:
            if selected.type == "MESH":
                b_mesh = selected
            elif selected.type == "ARMATURE":
                b_armature = selected
            elif selected.type == "EMPTY" and selected.parent_type == "BONE":
                b_attach_points.append(selected)

        if b_mesh is None or b_armature is None:
            return {'CANCELLED'}

        export_skmesh.export(b_mesh, b_armature, b_attach_points, self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".skmesh")
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class SkAnimExport(bpy.types.Operator):
    bl_idname = "export_anim.skanim"
    bl_label = bl_info['name']

    filepath = StringProperty(name="File Path", description="Filepath used for exporting", maxlen=1024, default= "")

    def execute(self, context):
        selection = bpy.context.selected_objects

        b_armature = None
        for selected in selection:
            if selected.type == "ARMATURE":
                b_armature = selected

        if b_armature is None:
            return {'CANCELLED'}

        export_skanim.export(b_armature, self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".skanim")
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class NavExport(bpy.types.Operator):
    bl_idname = "export_nav.nav"
    bl_label = bl_info['name']

    filepath = StringProperty(name="File Path", description="Filepath used for exporting", maxlen=1024, default= "")

    def execute(self, context):
        selection = bpy.context.selected_objects
        if not len(selection) == 1:
            return {'CANCELLED'}

        b_nav = selection[0]

        export_nav.export(b_nav, self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".nav")
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class EventItem(bpy.types.PropertyGroup):
    event = bpy.props.StringProperty(name="Event", default="DEFAULT")
    target = bpy.props.StringProperty(name="Target", default="")
    action = bpy.props.StringProperty(name="Action", default="")
    data = bpy.props.IntProperty(name="Data", default=-1)

class AddEvent(bpy.types.Operator):
    bl_idname = "object.add_event"
    bl_label = "Add Event"

    event = bpy.props.StringProperty(name="Event", default="DEFAULT")
    target = bpy.props.StringProperty(name="Target", default="")
    action = bpy.props.StringProperty(name="Action", default="")
    data = bpy.props.IntProperty(name="Data", default=-1)

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self, width=300)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        event_obj = bpy.context.object.events.add()
        event_obj.event = self.event
        event_obj.target = self.target
        event_obj.action = self.action
        event_obj.data = self.data
        return {'FINISHED'}

class RemoveEvent(bpy.types.Operator):
    bl_idname = "object.remove_event"
    bl_label = "Remove Event"

    def invoke(self, context, event):
        obj = bpy.context.object

        if obj.event_index >= 0:
            obj.events.remove(obj.event_index)
            obj.event_index -= 1

        return {'FINISHED'}

class EventList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.event, translate=False, icon_value=icon)
        layout.prop_search(item, "target", context.scene, "objects")
        layout.prop(item, "action")
        layout.prop(item, "data")

class ObjectPropPanel(bpy.types.Panel):
    bl_label = "Level_Edit"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        obj = context.object
        if not obj:
            return
        layout = self.layout

        layout.label(text="Events")
        split = layout.split()
        row = split.row()
        row.template_list("EventList", "", obj, 'events', obj, 'event_index')
        col = row.column(align=True)
        col.operator('object.add_event', text="", icon="ZOOMIN")
        col.operator('object.remove_event', text="", icon="ZOOMOUT")

def menu_level_export(self, context):
    self.layout.operator(LevelExport.bl_idname, text="Level (.lvl)")

def menu_bmesh_export(self, context):
    self.layout.operator(BinaryMeshExport.bl_idname, text="Mesh (.bmesh)")

def menu_mesh_export(self, context):
    self.layout.operator(MeshExport.bl_idname, text="Mesh (.mesh)")

def menu_skmesh_export(self, context):
    self.layout.operator(SkMeshExport.bl_idname, text="Skel Mesh (.skmesh)")

def menu_skanim_export(self, context):
    self.layout.operator(SkAnimExport.bl_idname, text="Skel Anim (.skanim)")

def menu_nav_export(self, context):
    self.layout.operator(NavExport.bl_idname, text="Nav (.nav)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_level_export)
    bpy.types.INFO_MT_file_export.append(menu_mesh_export)
    bpy.types.INFO_MT_file_export.append(menu_bmesh_export)
    bpy.types.INFO_MT_file_export.append(menu_skmesh_export)
    bpy.types.INFO_MT_file_export.append(menu_skanim_export)
    bpy.types.INFO_MT_file_export.append(menu_nav_export)

    bpy.types.Scene.atlas = bpy.props.StringProperty(name="Atlas")
    bpy.types.Scene.data_path = bpy.props.StringProperty(name="Data Path")

    bpy.types.Object.events = bpy.props.CollectionProperty(type=EventItem)
    bpy.types.Object.event_index = bpy.props.IntProperty(min=0, default=0)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_level_export)
    bpy.types.INFO_MT_file_export.remove(menu_mesh_export)
    bpy.types.INFO_MT_file_export.remove(menu_bmesh_export)
    bpy.types.INFO_MT_file_export.remove(menu_skmesh_export)
    bpy.types.INFO_MT_file_export.remove(menu_skanim_export)
    bpy.types.INFO_MT_file_export.remove(menu_nav_export)

if __name__ == "__main__":
    register()
