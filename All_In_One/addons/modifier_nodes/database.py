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

# <pep8 compliant>

import bpy
from bpy.app.handlers import persistent
from generator import NodeTreeCompiler

_database = {}
_update_keys = set()

def tag_update(data):
    key = data.as_pointer()
    _update_keys.add(key)

def clear_tags():
    _update_keys.clear()


def _data_deps(data):
    from mod_node import ModifierNodeTree
    from nodes.group import ModifierNode_group

    if isinstance(data, ModifierNodeTree):
        for node in data.nodes:
            if isinstance(node, ModifierNode_group) and node.nodetree is not None:
                yield node.nodetree

def _data_all():
    from mod_node import ModifierNodeTree

    for nodetree in bpy.data.node_groups:
        if isinstance(nodetree, ModifierNodeTree):
            yield nodetree

def _flush_tags():
    # recursive tagging
    visited = set()

    def flush_recursive(data):
        key = data.as_pointer()

        if data not in visited:
            visited.add(data)
            for dep in _data_deps(data):
                if flush_recursive(dep):
                    _update_keys.add(key)
                    return True

        return (key in _update_keys)

    for data in _data_all():
        flush_recursive(data)

def _do_sync_nodetree(nodetree):
    key = nodetree.as_pointer()
    if key not in _update_keys:
        generator = _database.get(key, None)
        if generator:
            return generator

    comp = NodeTreeCompiler()
    generator = comp.compile(nodetree)
    _database[key] = generator
    return generator

def _do_sync_object(ob, force=False):
    nodetree = ob.modifier_node_tree
    if nodetree:
        key = nodetree.as_pointer()
        if force or key in _update_keys:
            generator = _do_sync_nodetree(nodetree)
            if generator:
                kwargs = {} # XXX TODO
                generator.evaluate(ob, **kwargs)

def sync_nodetree(nodetree):
    _flush_tags()
    return _do_sync_nodetree(nodetree)

def sync_object(ob, force=False):
    _flush_tags()
    _do_sync_object(ob, force)

def sync(scene):
    if not _update_keys:
        return

    _flush_tags()
    print("sync scene: %r" % ", ".join("%d" % key for key in _update_keys))
    used = set()

    for ob in scene.objects:
        _do_sync_object(ob)

        nodetree = ob.modifier_node_tree
        if nodetree:
            key = nodetree.as_pointer()
            used.add(key)

    clear_tags()
    for key in _database.keys():
        if key not in used:
            del _database[key]

@persistent
def sync_handler(scene):
    sync(scene)


def register():
    bpy.app.handlers.scene_update_pre.append(sync_handler)

def unregister():
    for handler in bpy.app.handlers.scene_update_pre:
        if handler is sync_handler:
            bpy.app.handlers.load_post.remove(handler)
