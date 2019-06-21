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

""" handle export and import (potentially) to .csv """

if "bpy" in locals():
    import importlib
    importlib.reload(taskdna)
    importlib.reload(jsonode)
else:
    from . import taskdna
    from . import jsonode

import bpy

dependencies = 'dependencies'
task_seperator = '/'


def _get_dependencies(node):
    """ get dependencies of a node as a string """
    return task_seperator.join([
        link.from_node.name for inp in node.inputs for link in inp.links])


def _get_node_attr(node, attr):
    """ Get an attribute from a node """
    if attr == dependencies:
        return _get_dependencies(node)
    else:
        result = getattr(node, attr)
        if type(result) == str:
            return '"{}"'.format(result)
        elif type(result) == float and result > int(result):
            return '{0:.4f}'.format(result)
        else:
            return '{}'.format(result)


def _fields_from_node(node, fields):
    """ Return .csv fields from node attributes """
    return [_get_node_attr(node, field) for field in fields]


def export_csv(filepath, nodes, fields, seperator):
    """ Export nodes to a .csv file """
    with open(filepath, 'w') as csv_file:
        csv_file.write(seperator.join(['"{}"'.format(f) for f in fields]))
        csv_file.write('\n')
        for node in nodes:
            csv_file.write(seperator.join(_fields_from_node(node, fields)))
            csv_file.write('\n')


def _strip_quotes(field, text_seperator='"'):
    """ remove start and end quotes if needed """
    if field.startswith(text_seperator) and field.endswith(text_seperator):
        return field[1:-1]
    else:
        return field


def _sanitize(line, seperator):
    """ return sanitized version of a line """
    return line.replace('\n', '').replace('\r', '').split(seperator)


def import_csv(filepath, group, seperator):
    """ import nodes from a .csv file """
    # import lines from .csv as a task dictionary
    tasks = {}
    with open(filepath) as csv_file:
        fields = [
            _strip_quotes(f) for f in _sanitize(csv_file.readline(), seperator)]
        for line in csv_file:
            attrs = (_strip_quotes(i) for i in _sanitize(line, seperator))
            raw_dict = dict(zip(fields, attrs))
            try:
            	name = raw_dict.pop('name')
            except KeyError:
            	return 'error in csv'
            raw_dict['deps'] = raw_dict.pop(dependencies).split('/')
            for field in (
                    f for f in fields
                    if not f == 'name' and not f=='dependencies'):
                try:
                    raw_dict[field] = taskdna.Props.get_type(
                        field)(raw_dict[field])
                except:
                    print(field, 'not in taskdna')
                    raw_dict.pop(field)
            tasks[name] = raw_dict
    # merge task dictionary into tree
    print(tasks)
    jsonode.merge_tasks(tasks, group)
    
    

