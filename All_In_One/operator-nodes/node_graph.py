from itertools import chain
from collections import defaultdict

class NodeGraph:
    def __init__(self):
        self._nodes_by_idname = defaultdict(set)
        self._linked_sockets = defaultdict(set)
        self._node_by_socket = dict()

    @classmethod
    def from_node_tree(cls, node_tree):
        graph = cls()
        for node in node_tree.nodes:
            graph.add_node(node)
        for link in node_tree.links:
            graph.add_link(link)
        return graph

    def add_node(self, node):
        self._nodes_by_idname[node.bl_idname].add(node)
        for socket in chain(node.inputs, node.outputs):
            self._node_by_socket[socket] = node

    def add_link(self, link):
        self._linked_sockets[link.from_socket].add(link.to_socket)
        self._linked_sockets[link.to_socket].add(link.from_socket)

    def iter_nodes(self):
        for nodes in self._nodes_by_idname.values():
            yield from nodes

    def count_idname(self, idname):
        return len(self._nodes_by_idname[idname])

    def get_nodes_by_idname(self, idname):
        return list(self._nodes_by_idname[idname])

    def get_dependency_nodes(self, node):
        dependencies = set()
        for socket in node.inputs:
            for origin_socket in self._linked_sockets[socket]:
                dependencies.add(self._node_by_socket[origin_socket])
        return dependencies

    def iter_existing_idnames(self):
        yield from self._nodes_by_idname.keys()

    def get_node_by_socket(self, socket):
        return self._node_by_socket[socket]

    def get_linked_socket(self, socket):
        linked_sockets = self._linked_sockets[socket]
        if len(linked_sockets) == 1:
            return next(iter(linked_sockets))
        else:
            raise Exception("expected one connected socket, but found: {}".format(len(linked_sockets)))

    def get_linked_sockets(self, socket):
        return self._linked_sockets[socket]


