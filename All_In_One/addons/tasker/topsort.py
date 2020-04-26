# Copyright (c) 2014, Sunlight Labs

# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#    * Redistributions of source code must retain the above copyright notice, 
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the 
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of Sunlight Labs nor the names of its contributors may
#      be used to endorse or promote products derived from this software 
#      without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from collections import defaultdict
from itertools import chain


class CyclicGraphError(ValueError):
    """
    This exception is raised if the graph is Cyclic (or rather, when the
    sorting algorithm *knows* that the graph is Cyclic by hitting a snag
    in the top-sort)
    """
    pass


class Network(object):
    """
    This object (the `Network` object) handles keeping track of all the
    graph's nodes, and links between the nodes.

    The `Network' object is mostly used to topologically sort the nodes,
    to handle dependency resolution.
    """

    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(set)

    def add_node(self, node):
        """ Add a node to the graph (with no edges) """
        self.nodes.add(node)

    def add_edge(self, fro, to):
        """
        When doing topological sorting, the semantics of the edge mean that
        the depedency runs from the parent to the child - which is to say that
        the parent is required to be sorted *before* the child.

                  [ FROM ] ------> [ TO ]
        Committee on Finance -> Subcommittee of the Finance Committee on Budget
                            \-> Subcommittee of the Finance Committee on Roads
        """
        self.add_node(fro)
        self.add_node(to)
        self.edges[fro].add(to)

    def leaf_nodes(self):
        """
        Return an interable of nodes with no edges pointing at them. This is
        helpful to find all nodes without dependencies.
        """
        # Now contains all nodes that contain dependencies.
        deps = { item for sublist in self.edges.values() for item in sublist }
        # contains all nodes *without* any dependencies (leaf nodes)
        return self.nodes - deps

    def prune_node(self, node, remove_backrefs=False):
        """
        remove node `node` from the network (including any edges that may
        have been pointing at `node`).
        """
        if not remove_backrefs:
            for fro, connections in self.edges.items():
                if node in self.edges[fro]:
                    raise ValueError("""Attempting to remove a node with
                                     backrefs. You may consider setting
                                     `remove_backrefs` to true.""")

        # OK. Otherwise, let's do our removal.

        self.nodes.remove(node)
        if node in self.edges:
            # Remove add edges from this node if we're pruning it.
            self.edges.pop(node)

        for fro, connections in self.edges.items():
            # Remove any links to this node (if they exist)
            if node in self.edges[fro]:
                # If we should remove backrefs:
                self.edges[fro].remove(node)

    def sort(self):
        """
        Return an iterable of nodes, toplogically sorted to correctly import
        dependencies before leaf nodes.
        """
        while self.nodes:
            iterated = False
            for node in self.leaf_nodes():
                iterated = True
                self.prune_node(node)
                yield node
            if not iterated:
                raise CyclicGraphError("Sorting has found a cyclic graph.")

    def full_sort(self):
        """
        return a list of sets, topologically sorted in a tree to nicely space
        nodes in a graphical network
        """
        sorted_nodes = []
        while self.nodes:
            base = set()
            for node in self.leaf_nodes:
                base.add(node)
                self.prune_node(node)
            sorted_nodes.append(base)
            if not base:
                raise CyclicGraphError
        return sorted_nodes

    def dot(self):
        """
        Return a buffer that represents something dot(1) can render.
        """
        buff = "digraph graphname {"
        for fro in self.edges:
            for to in self.edges[fro]:
                buff += "%s -> %s;" % (fro, to)
        buff += "}"
        return buff

    def cycles(self):
        """
        Fairly expensive cycle detection algorithm. This method
        will return the shortest unique cycles that were detected.

        Debug usage may look something like:

        print("The following cycles were found:")
        for cycle in network.cycles():
            print("    ", " -> ".join(cycle))
        """

        def walk_node(node, seen):
            """
            Walk each top-level node we know about, and recurse
            along the graph.
            """
            if node in seen:
                yield (node,)
                return
            seen.add(node)
            for edge in self.edges[node]:
                for cycle in walk_node(edge, set(seen)):
                    yield (node,) + cycle

        # First, let's get a iterable of all known cycles.
        cycles = chain.from_iterable(
            (walk_node(node, set()) for node in self.nodes))

        shortest = set()
        # Now, let's go through and sift through the cycles, finding
        # the shortest unique cycle known, ignoring cycles which contain
        # already known cycles.
        for cycle in sorted(cycles, key=len):
            for el in shortest:
                if set(el).issubset(set(cycle)):
                    break
            else:
                shortest.add(cycle)
        # And return that unique list.
        return shortest
