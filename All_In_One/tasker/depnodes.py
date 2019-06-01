# Copyright 2015 Bassam Kurdali / urchn.org
# Modified from custom nodes template
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

""" Custom Nodes that represent project tasks """

if "bpy" in locals():
    import importlib
    importlib.reload(taskdna)
    importlib.reload(jsonode)
    importlib.reload(csvnode)
else:
    from . import taskdna
    from . import jsonode
    from . import csvnode

import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy_extras.io_utils import ExportHelper, ImportHelper

# preview images for task nodes
preview_collections = {}


class TaskTree(NodeTree):
    """ Task Nodes Tree Type """
    bl_idname = 'TaskTree'
    bl_label = 'Task Node Tree'
    bl_icon = 'NODETREE'


# Custom socket type
class TaskSocket(NodeSocket):
    """ Task node socket type """
    bl_idname = 'TaskSocket'
    bl_label = 'Task Socket'

    DepProperty = bpy.props.StringProperty(
        name="taskdep", description="dependency")

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)


class DepNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'TaskTree'


# Derived from the Node base type.
class TaskNode(Node, DepNode):
    """ Single Dependency Node """
    bl_idname = 'TaskNode'
    bl_label = 'Task Node'
    bl_icon = 'SOUND'

    preview_image = None
    preview_filepath = bpy.props.StringProperty(default="", subtype="FILE_PATH")

    def init(self, context):
        for i in range(10):
            self.inputs.new('TaskSocket', "depend_{}".format(i))
        self.outputs.new('TaskSocket', "Output")
        
    def draw_buttons(self, context, layout):
        if self.preview_filepath:
            row = layout.row()
            row.scale_y =2
            row.template_icon_view(self, "preview_image")
        row = layout.row()
        row.prop(self, "preview_filepath")
        for prop in taskdna.Props.get_list():
            row = layout.row()
            row.prop(self, prop, expand=True)

for prop, proptype in taskdna.Props.get_bpy_types():
    setattr(TaskNode, prop, proptype())

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem


class DepNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'TaskTree'

node_categories = [
    DepNodeCategory("DEPNODES", "Dependency Nodes", items=[
        # our basic node
        NodeItem("TaskNode"),
        ]),
    ]


class CreateTask(bpy.types.Operator):
    """ Create a new Task """
    bl_label = "Create New Task"
    bl_idname = 'node.create_task'

    def execute(self, context):
        group = context.area.spaces[0].node_tree
        scene = context.scene
        deps = [dep for dep in group.task_deps if not dep == group.task_name]
        # create the nodes
        tasknode = group.nodes.new(type='TaskNode')
        tasknode.name = tasknode.label = group.task_name
        for attr in taskdna.Props.get_list():
            setattr(tasknode, attr, getattr(group, "task_{}".format(attr)))
        # initial location choice
        area = context.area
        space = area.spaces[0]
        space.cursor_location_from_region(
            area.x + area.width / 2,
            area.y + area.height / 2)
        max_x = space.cursor_location[0]
        max_y = space.cursor_location[1]

        # create the links
        for i, dep in enumerate(deps):
            taskdep = group.links.new(
                tasknode.inputs['depend_{}'.format(i)],
                group.nodes[dep].outputs[0])
            group.nodes[dep].outputs[0].hide = False
            max_x = group.nodes[dep].location.x + 400
            max_y = group.nodes[dep].location.y
        # place node
        tasknode.width = 400
        tasknode.location.x = max_x
        tasknode.location.y = max_y

        return {'FINISHED'}


class TasksExport(bpy.types.Operator, ExportHelper):
    """ Export Tasks """
    bl_label = "Tasks Export to JSON"
    bl_idname = 'node.tasks_export'

    filename_ext = ".json"

    filter_glob = bpy.props.StringProperty(
            default="*.json",
            options={'HIDDEN'},
            )

    export_selected = bpy.props.BoolProperty(
            default=False,
            name="Export Selected",
            description="Only Export Selected Tasks")

    @classmethod
    def poll(cls, context):
        space = context.area.spaces[0]
        return space and 'node_tree' in dir(space) and \
            space.node_tree.bl_idname == 'TaskTree' and \
            space.node_tree.nodes

    def execute(self, context):
        group = context.area.spaces[0].node_tree
        scene = context.scene
        jsonode.to_json(self.filepath, group, self.properties.export_selected)
        return {'FINISHED'}


class Restrict():
    """ Helper Task for CSV export columns """

props = ['name']
props.extend(taskdna.Props.get_list())
props.append('dependencies')
restrictions = [tuple([prop] * 3) for prop in props]
restrictions.append(tuple(['none']*3))
for index, prop in enumerate(props):
    setattr(
        Restrict,
        'column_{}'.format(index),
        bpy.props.EnumProperty(
            items=restrictions, default=restrictions[index][0]))


class TasksExportCSV(bpy.types.Operator, ExportHelper, Restrict):
    """ Export Tasks to CSV"""
    bl_label = "Tasks Export to CSV"
    bl_idname = 'node.tasks_export_csv'

    filename_ext = ".csv"

    filter_glob = bpy.props.StringProperty(
            default="*.csv",
            options={'HIDDEN'},
            )

    export_selected = bpy.props.BoolProperty(
            default=False,
            name="Export Selected",
            description="Only Export Selected Tasks")

    export_blocked = bpy.props.BoolProperty(
            default=True,
            name="Export Blocked",
            description="Export Tasks that are blocked by other tasks")

    seperator = bpy.props.StringProperty(default='~')

    @classmethod
    def poll(cls, context):
        space = context.area.spaces[0]
        return space and 'node_tree' in dir(space) and \
            space.node_tree.bl_idname == 'TaskTree' and \
            space.node_tree.nodes

    def execute(self, context):
        group = context.area.spaces[0].node_tree
        scene = context.scene
        props = self.properties
        seperator = props.seperator
        columns = sorted([
            col for col in dir(props) if col.startswith('column_') and
            getattr(props, col) != 'none'])
        if not props.export_blocked:
            columns = columns[:-1]
        fields = [getattr(props, col) for col in columns]
        nodes = (
            node for node in group.nodes if
            (node.select or not props.export_selected) and
            (props.export_blocked or
            any(not inp.links for inp in node.inputs)))
        csvnode.export_csv(props.filepath, nodes, fields, seperator)
        return {'FINISHED'}

    def draw(self, context):
        props = self.properties
        layout = self.layout
        row = layout.row()
        row.prop(props, 'export_selected')
        row.prop(props, 'export_blocked')
        columns = sorted([
            prop for prop in dir(props) if prop.startswith('column_')])
        for prop in columns[:len(columns) if props.export_blocked else -1]:
            row = layout.row()
            row.prop(props, prop)
        row = layout.row()
        row.prop(props, 'seperator')


class TasksImportCSV(bpy.types.Operator, ImportHelper):
    """ Import Tasks from CSV"""
    bl_label = "Tasks Import from CSV"
    bl_idname = 'node.tasks_import_csv'

    filename_ext = ".csv"

    filter_glob = bpy.props.StringProperty(
            default="*.csv",
            options={'HIDDEN'},
            )


    seperator = bpy.props.StringProperty(default='~')

    @classmethod
    def poll(cls, context):
        space = context.area.spaces[0]
        return space and 'node_tree' in dir(space) and \
            space.node_tree.bl_idname == 'TaskTree'

    def execute(self, context):
        props = self.properties
        if csvnode.import_csv(
            	props.filepath, context.area.spaces[0].node_tree, props.seperator):
            self.report({'ERROR'}, "CSV Invalid, check file or csv seperator")
            return {'CANCELLED'}
        return {'FINISHED'}

   
class TasksImport(bpy.types.Operator, ImportHelper):
    """ Import Tasks """
    bl_label = "Tasks Import"
    bl_idname = 'node.tasks_import'

    filename_ext = ".json"

    filter_glob = bpy.props.StringProperty(
            default="*.json",
            options={'HIDDEN'},
            )

    @classmethod
    def poll(cls, context):
        space = context.area.spaces[0]
        return space and 'node_tree' in dir(space) and \
            space.node_tree.bl_idname == 'TaskTree' and \
            not space.node_tree.nodes

    def execute(self, context):
        group = context.area.spaces[0].node_tree
        scene = context.scene
        jsonode.to_nodetree(self.filepath, group)
        return {'FINISHED'}


class TaskCreatePanel(bpy.types.Panel):
    """ Task Creation Panel """
    bl_label = 'Create Task'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = 'Dependency Nodes'

    def draw(self, context):
        layout = self.layout
        group = context.area.spaces[0].node_tree
        layout.prop(group, 'task_name', text='identifier')
        for prop in taskdna.Props.get_list():
            layout.prop(group, 'task_{}'.format(prop), text=prop, expand=True)
        layout.prop_menu_enum(group, 'task_deps', text='dependencies')
        op = layout.operator('node.create_task', text='Create Task')


class TaskIOPanel(bpy.types.Panel):
    """ Task Import and Export Panel """
    bl_label = 'Import/Export'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = 'Dependency Nodes'

    def draw(self, context):
        layout = self.layout
        group = context.area.spaces[0].node_tree
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator('node.tasks_import', text='Import JSON')
        layout.operator('node.tasks_export', text='Export JSON')
        layout.operator('node.tasks_export_csv', text='Export csv')
        layout.operator('node.tasks_import_csv', text='Import csv')


class Proper():
    """ Proper """

for prop, bpy_type in taskdna.Props.get_bpy_types():
    print(prop, bpy_type)
    setattr(
        Proper,
        "search_{}".format(prop),
        bpy.props.BoolProperty(default=False))
    setattr(
        Proper,
        "data_{}".format(prop),
        bpy_type())


class SearchOperator(bpy.types.Operator, Proper):
    """ Search and select Nodes """
    bl_label = 'Select by Property'
    bl_idname = 'node.select_by_property'

    exclusive = bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        space = context.area.spaces[0]
        return space and 'node_tree' in dir(space) and \
            space.node_tree.bl_idname == 'TaskTree' and \
            space.node_tree.nodes

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, 250)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        group = context.area.spaces[0].node_tree
        props = self.properties
        searches = (
            attr for attr in dir(props) if attr.startswith('search_')
            and getattr(self, attr))
        for search in searches:
            data = getattr(props, search.replace('search_','data_'))
            prop = search.replace('search_','')
            for node in group.nodes:
                node.select = node.select and not props.exclusive or getattr(node, prop) == data
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        props = self.properties
        searches = (
            attr for attr in dir(props) if attr.startswith('search_'))
        for search in searches:
            row = layout.row()
            base = search.replace('search_','')

            row.prop(props, search, text=base)
            row.prop(props, "data_{}".format(base), text='')
        row = layout.row()
        row.prop(props, "exclusive")


def nicetime(days):
    years = days // 365
    months = days % 365 // 30
    return "{} years, {} months".format(years, months)


class SearchPanel(bpy.types.Panel):
    """ Search and Select Tools """
    bl_label = 'Search and Select'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = 'Dependency Nodes'

    def draw(self, context):
        layout = self.layout
        nodes = context.area.spaces[0].node_tree.nodes
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator('node.select_by_property', 'Select by Property')


def _report_format(prefix, nodes):
    """ Format a report for a given number of nodes """
    total = sum(
        node.time for node in nodes
        if node.bl_idname == 'TaskNode' if not node.completed)
    report = "{0:.2f} days".format(total) if total < 30 else nicetime(days=total)
    return "{} takes {}".format(prefix, report)


def _get_deps(old_deps):
    """ get all dependent nodes of a node """
    new_deps = []
    for tasknode in old_deps:
        for inp in tasknode.inputs:
            for link in inp.links:
                new_deps.append(link.from_node)
    if new_deps:
        return new_deps + _get_deps(new_deps)
    else:
        return []
         
    
class StatsPanel(bpy.types.Panel):
    """ Statistics and reports"""
    bl_label = 'Stats and Reports'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = 'Dependency Nodes'

    def draw(self, context):
        layout = self.layout
        nodes = context.area.spaces[0].node_tree.nodes
        selected = [node for node in nodes if node.select]
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.label(_report_format('project', nodes))
        if selected:
            selected.extend(_get_deps(selected))
            layout.label(_report_format('selected', set(selected)))


def register():
    import os
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    preview_collections["orgnodes"] = pcoll

    def get_preview(self, context):
        """ return just this node's preview images """
        prefix = "PRV_{}__{}".format(self.name, "{}")
        path = bpy.path.abspath(self.preview_filepath)
        if not prefix.format(path) in preview_collections["orgnodes"]:
            pcoll = preview_collections["orgnodes"]
            pcoll.load(prefix.format(path), path, 'IMAGE')
        return [
            tuple([prefix.format(i),] * 3 + [preview[1].icon_id, i])
            for i, preview in enumerate(
                preview_collections["orgnodes"].items()
                )
            if preview[0].startswith(prefix.format(""))
            ]

    TaskNode.preview_image = bpy.props.EnumProperty(items=get_preview)

    bpy.utils.register_class(TaskTree)

    for prop, proptype in taskdna.Props.get_bpy_types():
        setattr(TaskTree, 'task_{}'.format(prop), proptype())
    TaskTree.task_name = bpy.props.StringProperty()
    def get_nodes(self, context):
        too_many = len(self.nodes) >= 32
        return [
            tuple([node.name] * 3) for node in self.nodes
            if node.select or not too_many]
    TaskTree.task_deps = bpy.props.EnumProperty(
        items=get_nodes,options={'ENUM_FLAG'})
    for bpy_class in (TaskSocket, TaskNode):
        bpy.utils.register_class(bpy_class)
    nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)
    for bpy_class in (
            CreateTask, TasksImport, TasksExport, TasksExportCSV,
            TasksImportCSV, TaskCreatePanel,
            TaskIOPanel, SearchOperator, SearchPanel, StatsPanel): 
        bpy.utils.register_class(bpy_class)


def unregister():
    for bpy_class in (
            StatsPanel, TaskCreatePanel, TaskIOPanel, CreateTask, TasksExport,
            TasksImport, TasksExportCSV, TasksImportCSV,
            SearchPanel, SearchOperator):
        bpy.utils.unregister_class(bpy_class)
    nodeitems_utils.unregister_node_categories("CUSTOM_NODES")
    for bpy_class in (
            TaskTree, TaskSocket, TaskNode):
        bpy.utils.unregister_class(bpy_class)
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

if __name__ == "__main__":
    register()
