import bpy
import bpy.props as prop

bl_info = {
    "name": "Quick Select set",
    "description": "Allows to temporally save a group of selected vertices",
    "author": "David Velasquez",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "Data",
    "category": "Learnbgame",
}


class QuickSelectSetListItem(bpy.types.PropertyGroup):
    """ Group of properties representing an item in the list """

    name = prop.StringProperty(
           name="Name",
           default="Group")

    vertices = prop.StringProperty(
            name="Vertices",
            default="")


class QuickSelectSetList(bpy.types.UIList):
    def draw_item(
            self, context, layout, data, item, icon, active_data,
            active_propname, index):

        custom_icon = 'GROUP_VERTEX'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                layout.prop(item, "name", text="", emboss=False,
                            icon=custom_icon)
            else:
                layout.label(text="", translate=False, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon=custom_icon)


class QuickSelectSetListNewItem(bpy.types.Operator):
    """ Add a new item to the list """
    bl_idname = "qss_list.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        context.object.qss_list.add()

        return{'FINISHED'}


class QuickSelectSetListDeleteItem(bpy.types.Operator):
    """ Delete the selected item from the list """
    bl_idname = "qss_list.delete_item"
    bl_label = "Deletes an item"

    @classmethod
    def poll(self, context):
        """ Enable if there's something in the list """
        return len(context.object.qss_list) > 0

    def execute(self, context):
        list = context.object.qss_list
        index = context.object.qss_active_index

        list.remove(index)

        if index > 0:
            index = index - 1

        return {'FINISHED'}


class QuickSelectSetAssign(bpy.types.Operator):
    """ Assign selected vertices to list item """
    bl_idname = "qss_list.assign_vertex"
    bl_label = "Assign the selected vertices to the active list"

    @classmethod
    def poll(self, context):
        return len(context.object.qss_list) > 0

    def execute(self, context):
        obj = context.object
        list = obj.qss_list
        index = obj.qss_active_index

        vertices = []

        mode = obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        selectedVerts = [v for v in obj.data.vertices if v.select]

        for v in selectedVerts:
            vertices.append(v.index)

        bpy.ops.object.mode_set(mode=mode)

        if len(vertices) > 0:
            list[index].vertices = ",".join(str(v) for v in vertices)

        return {'FINISHED'}


class QuickSelectSetSelect(bpy.types.Operator):
    """ Select vertices saved on group """
    bl_idname = "qss_list.select_vertex"
    bl_label = "Select all the vertices assigned to the selected vertex group"

    @classmethod
    def poll(self, context):
        return len(context.object.qss_list) > 0

    def execute(self, context):
        obj = context.object
        list = obj.qss_list
        index = obj.qss_active_index

        try:
            vertices = [int(v) for v in list[index].vertices.split(",")]

            mode = obj.mode
            bpy.ops.object.mode_set(mode='OBJECT')

            for index in vertices:
                obj.data.vertices[index].select = True

            bpy.ops.object.mode_set(mode=mode)
        except:
            pass

        return {'FINISHED'}


class QuickSelectSetPanel(bpy.types.Panel):
    """Creates a Panel for Quick Select Set in the Data properties window"""
    bl_label = "Quick Select Set"
    bl_idname = "DATA_PT_quick_select_set"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()

        rows = 2

        row.template_list("QuickSelectSetList", "", obj, "qss_list", obj,
                          "qss_active_index", rows=rows)

        col = row.column()
        col.operator("qss_list.new_item", icon='ZOOMIN', text="")
        col.operator("qss_list.delete_item", icon='ZOOMOUT', text="")

        if len(obj.qss_list) > 0 and obj.mode == 'EDIT':
            row = layout.row()

            sub = row.row(align=True)
            sub.operator("qss_list.assign_vertex", text="Assign")

            sub = row.row(align=True)
            sub.operator("qss_list.select_vertex", text="Select")
            # TODO: Adds deselect operator
            # sub.operator("qss_list.deselect_vertex", text="Deselect")


def register():
    bpy.utils.register_class(QuickSelectSetListItem)
    bpy.utils.register_class(QuickSelectSetList)

    bpy.utils.register_class(QuickSelectSetAssign)
    bpy.utils.register_class(QuickSelectSetSelect)

    bpy.utils.register_class(QuickSelectSetListNewItem)
    bpy.utils.register_class(QuickSelectSetListDeleteItem)

    bpy.utils.register_class(QuickSelectSetPanel)

    bpy.types.Object.qss_list = prop.CollectionProperty(
        type=QuickSelectSetListItem)
    bpy.types.Object.qss_active_index = prop.IntProperty(
        name="Index for qss_list",
        default=0)


def unregister():
    del bpy.types.Object.qss_list
    del bpy.types.Object.qss_active_index

    bpy.utils.unregister_class(QuickSelectSetListItem)
    bpy.utils.unregister_class(QuickSelectSetList)

    bpy.utils.unregister_class(QuickSelectSetAssign)
    bpy.utils.unregister_class(QuickSelectSetSelect)

    bpy.utils.unregister_class(QuickSelectSetListNewItem)
    bpy.utils.unregister_class(QuickSelectSetListDeleteItem)

    bpy.utils.unregister_class(QuickSelectSetPanel)


if __name__ == "__main__":
    register()
