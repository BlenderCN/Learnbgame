from itertools import chain
from collections import defaultdict, namedtuple
from . utils.nodes import iter_compute_node_trees, iter_base_nodes_in_tree

class TreeInfo:
    def __init__(self, node_tree):
        self.nodes = dict(node_tree.nodes)
        self.links = list(node_tree.links)

        self._create_nodes_data()
        self._create_links_data()
        self._find_data_connections()

    def _create_nodes_data(self):
        self.reroutes = set()
        self.node_by_socket = dict()
        self.nodes_by_type = defaultdict(list)

        for node in self.nodes.values():
            if node.bl_idname == "NodeReroute":
                self.reroutes.add(name)

            for socket in chain(node.inputs, node.outputs):
                self.node_by_socket[socket] = node

            self.nodes_by_type[node.bl_idname].append(node)

    def _create_links_data(self):
        self.direct_origin = defaultdict(lambda: None)
        self.direct_targets = defaultdict(list)

        for link in self.links:
            origin = link.from_socket
            target = link.to_socket

            self.direct_origin[target] = origin
            self.direct_targets[origin].append(target)

    def _find_data_connections(self):
        self.data_origin = defaultdict(lambda: None)
        self.data_targets = defaultdict(list)

        for target, origin in self.direct_origin.items():
            if target in self.reroutes:
                continue

            real_origin = self._find_real_data_origin(target, set())
            if real_origin is not None:
                self.data_origin[target] = real_origin
                self.data_targets[real_origin].append(target)

    def _find_real_data_origin(self, target, visited_reroutes):
        direct_origin = self.direct_origin[target]
        if direct_origin is None:
            return None

        if direct_origin in visited_reroutes:
            print("Reroute recursion detected")
            return None
        elif direct_origin in self.reroutes:
            visited_reroutes.add(direct_origin)
            return self._find_real_data_origin(direct_origin, visited_reroutes)
        else:
            return direct_origin


tree_info_by_hash = dict()
updated_trees = set()

def tag_update(tree):
    updated_trees.add(hash(tree))

def update_if_necessary():
    new_tree_info_by_hash = dict()
    for tree in iter_compute_node_trees():
        tree_hash = hash(tree)
        if tree_hash not in tree_info_by_hash or tree_hash in updated_trees:
            new_tree_info_by_hash[tree_hash] = TreeInfo(tree)
            updated_trees.discard(tree_hash)
        else:
            new_tree_info_by_hash[tree_hash] = tree_info_by_hash[tree_hash]

    tree_info_by_hash.clear()
    tree_info_by_hash.update(new_tree_info_by_hash)




# Access tree info utilities

def iter_all_unlinked_inputs(tree):
    for node in iter_base_nodes_in_tree(tree):
        for socket in iter_unlinked_inputs(node):
            yield node, socket

def iter_unlinked_inputs(node):
    info = tree_info_by_hash[hash(node.id_data)]
    for socket in node.inputs:
        if info.data_origin[socket] is None:
            yield socket

def iter_linked_inputs(node):
    info = tree_info_by_hash[hash(node.id_data)]
    for socket in node.inputs:
        if info.data_origin[socket] is not None:
            yield socket

def get_data_origin_socket(socket):
    info = tree_info_by_hash[hash(socket.id_data)]
    return info.data_origin[socket]

def get_nodes_by_type(tree, idname):
    info = tree_info_by_hash[hash(tree)]
    return info.nodes_by_type[idname]

def get_node_by_socket(socket):
    info = tree_info_by_hash[hash(socket.id_data)]
    return info.node_by_socket[socket]
