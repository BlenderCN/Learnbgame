# Copyright 2015 Bassam Kurdali / urchn.org
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

""" Converts tasks from json to blender nodes and back """

if "bpy" in locals():
    import importlib
    importlib.reload(topsort)
    importlib.reload(taskdna)
else:
    from . import topsort
    from . import taskdna

import bpy
import json


def _load_json_tasks(filename):
    """ load tasks from json file """
    return json.loads(open(filename).read())


def _set_node_attrs(node, data):
    """ set a task node's data or update it """
    for prop in data:
        if prop in taskdna.Props.get_list():
            setattr(node, prop, data[prop])    


def _create_node(name, data, group):
    """ create a single task node and set it's data """
    tasknode = group.nodes.new(type='TaskNode')    
    tasknode.name = tasknode.label = name
    _set_node_attrs(tasknode, data)


def _create_nodes(tasks, group):
    """ create task nodes """
    for task in tasks:
        _create_node(task, tasks[task], group)


def _create_node_link(tasknode, dep, group):
    """ create a dependency link in the first empty input """
    for inp in tasknode.inputs:
        if inp.links:
            continue
        else:
            nodelink = group.links.new(inp, group.nodes[dep].outputs[0])
            return nodelink


def _create_links(tasks, group):
    """ create dependency links aka noodles """
    for task in tasks:
        for i, dep in enumerate(tasks[task]['deps']):
            nodelink = _create_link(group.links.new(
                group.nodes[task].inputs['depend_{}'.format(i)],
                group.nodes[dep].outputs[0]))


def _sort_nodes(group):
    """ Make nodes look pretty(er) """
    # sort the node network
    network = topsort.Network()
    for node in group.nodes:
        network.add_node(node)
    for link in group.links:
        network.add_edge(link.from_node, link.to_node)
    sorted_nodes = reversed([node for node in network.sort()])
    next_x = next_y = 2000
    # scale and transform nodes
    for node in sorted_nodes:
        node.location.x = next_x
        node.location.y = next_y
        node.width = 400
        for input in node.inputs:
            input.hide = True
        node.outputs[0].hide = True
        if not node.outputs[0].links:
            next_y -= 400
        else:
            node.location.x -= 400
            next_x = node.location.x
            base = node.outputs[0].links[0].to_node.location.y
            offset = int(node.outputs[0].links[0].to_socket.name[-1])
            node.location.y = base - 400 * offset
            next_y = node.location.y -400


def to_nodetree(filename, group):
    """ Convert JSON task descriptor file to nodetree """
    tasks = _load_json_tasks(filename)
    _create_nodes(tasks, group)
    _create_links(tasks, group)
    _sort_nodes(group)


def merge_tasks(tasks, group):
    """ Merge a tasks dictionary into an existing nodetree """
    nodes = group.nodes
    for task in tasks:
        if task in nodes:
            print('task in nodes:', task)
            _set_node_attrs(nodes[task], tasks[task])
        else:
            print('node not in tasks:', task)
            _create_node(task, tasks[task], group)
    old_links = [(link.from_node, link.to_node) for link in group.links]
    for task in tasks:
        for i, dep in enumerate(tasks[task]['deps']):
            if not (task, dep) in old_links:
                print(task, dep, "not in")
                #_create_node_link(group.nodes[task], dep, group)
            else:
                print(task, dep, "in")


def into_nodetree(filename, group):
    """ Merge JSON task descriptor file into an existing nodetree """
    tasks = _load_json_tasks(filename)
    merge_tasks(tasks, group)


def _tree_to_tasks(group, selected=False):
    """ return a tasks data structure from our nodes """
    tasks = {}
    all_tasks = not selected
    for node in group.nodes:
        if all_tasks or node.select:
            tasks[node.name] = {
                itm: getattr(node, itm) for itm in taskdna.Props.get_list()}
            tasks[node.name]["deps"] = [
                dep.links[0].from_node.name for dep in node.inputs if dep.links]
    return tasks

        
def _save_json_tasks(filename, tasks):
    """ save out tasks to a JSON file """
    with open(filename, mode='w') as json_file:
        json_file.write(
            json.dumps(tasks, sort_keys=True, indent=4))


def to_json(filename, group, selected=False):
    """ convert nodetree to JSON file """
    tasks = _tree_to_tasks(group, selected)
    _save_json_tasks(filename, tasks)

if __name__ == "__main__":
    group = bpy.data.node_groups['Tasks']
    filename = '/home/bassam/projects/hamp/tube/scenes/edit/tasks.json'
    to_nodetree(filename, group)
    #to_json(filename, group)

