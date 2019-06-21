class UIDMap:
    def __init__(self):
        self._node_to_varname = {}
        self._uid_to_node = {}
        self._uid_to_varname = {}
        self._varname_to_node = {}
        self._removed_cells = []

    def _register(self, varname, uid, node):
        self._node_to_varname[node] = varname
        self._uid_to_node[uid] = node
        self._uid_to_varname[uid] = varname
        self._varname_to_node[varname] = node
        pass

    def remove_cell_from_tree(self, cell_varname):
        self._removed_cells.append(cell_varname)
        pass

    def is_removed(self, cell_varname):
        return cell_varname in self._removed_cells

    def get_varname_for_node(self, tree_node):
        return self._node_to_varname[tree_node]

    def get_node_for_varname(self, varname):
        return self._varname_to_node[varname]

    def _get_node_for_uid(self, uid):
        return self._uid_to_node[uid]

    def _get_varname_for_uid(self, uid):
        return self._uid_to_varname[uid]

    def _list_cell_names(self):
        return list(self._uid_to_varname.values())
    pass