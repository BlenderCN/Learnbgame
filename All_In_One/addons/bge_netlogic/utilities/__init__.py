import bpy

class Color(object):

    _SPACE_RGBA = "RGBA"
    _SPACE_HSLA = "HSLA"

    @classmethod
    def RGBA(cls, r, g, b, a = 1.0):
        import numbers
        if r < 0: raise ValueError("RED component cannot be negative")
        if g < 0: raise ValueError("GREEN component cannot be negative")
        if b < 0: raise ValueError("BLUE component cannot be negative")
        if a < 0: raise ValueError("ALPHA component cannot be negative")
        if isinstance(r, numbers.Integral): r = float(r) / 255.0
        if isinstance(g, numbers.Integral): g = float(g) / 255.0
        if isinstance(b, numbers.Integral): b = float(b) / 255.0
        if isinstance(a, numbers.Integral): a = float(a) / 255.0
        return cls([r, g, b, a], cls._SPACE_RGBA)

    @classmethod
    def RGBA_TO_HSLA(cls, color):
        if color._space == cls._SPACE_HSLA:
            return cls(color._components, cls._SPACE_HSLA)
        rgba = color._components
        R = rgba[0]
        G = rgba[1]
        B = rgba[2]
        A = rgba[3]
        m = min(R, G, B)
        M = max(R, G, B)
        C = M - m
        H1 = 0
        if C != 0:
            if M == R: H1 = ((G - B) / C) % 6.0
            if M == G: H1 = ((B - R) / C) + 2.0
            if M == B: H1 = ((R - G) / C) + 4.0
        H = 60 * H1
        L = 0.5 * (M + m)
        S = 0
        if C != 0:
            S = (C / (1 - abs(2.0 * L - 1)))
        result = Color([0,0,0,0], Color._SPACE_HSLA)
        result._components[:] = [H,S,L,A]
        return result

    @classmethod
    def HSLA_TO_RGBA(cls, color):
        if color._space == cls._SPACE_RGBA:
            return cls(color._components, cls._SPACE_RGBA)
        hsla = color._components
        H = hsla[0]
        S = hsla[1]
        L = hsla[2]
        A = hsla[3]
        C = 1 - abs((2 * L) - 1) * S
        H1 = H / 60.0
        X = C * (1 - abs((H1 % 2) - 1))
        R1 = 0
        G1 = 0
        B1 = 0
        if (H >= 0 and H1 < 1):
            R1 = C
            G1 = H1
            B1 = 0
        if (H1 >= 1 and H1 < 2):
            R1 = X
            G1 = C
            B1 = 0
        elif (H1 >= 2 and H1 < 3):
            R1 = 0
            G1 = C
            B1 = X
        elif (H1 >= 3 and H1 < 4):
            R1 = 0
            G1 = X
            B1 = C
        elif (H1 >= 4 and H1 < 5):
            R1 = X
            G1 = 0
            B1 = C
        elif (H1 >= 5 and H1 < 6):
            R1 = C
            G1 = 0
            B1 = X
        else:
            raise ValueError("bug?")
        m = L - (0.5 * C)
        R = R1 + m
        G = G1 + m
        B = B1 + m
        result = Color((0,0,0), Color._SPACE_RGBA)
        result._components = [R, G, B, A]
        return result

    def __init__(node, color_components, space_type):
        node._components = color_components[:]
        node._space = space_type

    def __getitem__(node, item):
        return node._components[item]

    def __setitem__(node, key, value):
        node._components[key] = value

    def __len__(node):
        return len(node._components)

    def __repr__(node):
        return "Color{}({},{},{},{})".format(
            "RGBA" if node._space == Color._SPACE_RGBA else "HSLA",
            node._components[0],
            node._components[1],
            node._components[2],
            node._components[3]
        )

    def darker(node, lum_diff=0.1):
        source = node
        if source._space != Color._SPACE_HSLA:
            source = Color.RGBA_TO_HSLA(node)
        source._components[2] -= lum_diff
        if source._components[2] < 0.0: source._components[2] = 0.0
        if node._space == Color._SPACE_RGBA:
            source = Color.HSLA_TO_RGBA(source)
        return source

    def int_str(node):
        space = node._space
        a = int(node._components[0] * 255)
        b = int(node._components[1] * 255)
        c = int(node._components[2] * 255)
        d = int(node._components[3] * 255)
        if space == Color._SPACE_HSLA:
            a = int(node._components[0])
            b = int(100 * node._components[1])
            c = int(100 * node._components[2])
        return "Color{}({},{},{},{})".format(
            "RGBA" if node._space == Color._SPACE_RGBA else "HSLA",
            a,
            b,
            c,
            d
        )
    pass

def register_inputs(node, *data):
    assert isinstance(node, bpy.types.Node)
    i = 0
    while i < len(data):
        cls = data[i]
        lab = data[i+1]
        node.inputs.new(cls.bl_idname, lab)
        i += 2

def register_outputs(node, *data):
    assert isinstance(node, bpy.types.Node)
    i = 0
    while i < len(data):
        cls = data[i]
        lab = data[i + 1]
        node.outputs.new(cls.bl_idname, lab)
        i += 2

def _map_socket(input, node, socket, *names):
    assert isinstance(node, bpy.types.Node)
    assert isinstance(socket, bpy.types.NodeSocket)
    sockets = node.inputs
    if not input: sockets = node.outputs
    for i in range(0, len(sockets)):
        s = sockets[i]
        if s == socket: return names[i]
    assert False

def _map_value(input, node, socket, *fun):
    assert isinstance(node, bpy.types.Node)
    assert isinstance(socket, bpy.types.NodeSocket)
    sockets = node.inputs
    if not input: sockets = node.outputs
    for i in range(0, len(sockets)):
        s = sockets[i]
        if s == socket: return fun[i](s)
    assert False

def map_input_name(node, socket, *names):
    return _map_socket(True, node, socket, *names)

def map_input_value(node, socket, *fun):
    return _map_value(True, node, socket, *fun)

def map_output_name(node, socket, *names):
    return _map_socket(False, node, socket, *names)

def map_output_value(node, socket, *names):
    return _map_value(False, node, socket, *names)

def quoted(s):
    if s.startswith("'"): return s
    if s.startswith('"'): return s
    return '"{}"'.format(s)
quoted_string = quoted#alias

def strip_tree_name(name):
    buffer = ""
    valid_characters = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for c in name:
        if c in valid_characters: buffer += c
    return buffer

def py_module_name_for_tree(tree):
    tree_module_name = strip_tree_name(tree.name)
    return "NL" + tree_module_name

def py_module_name_for_stripped_tree_name(stripped_tree_name):
    return "NL" + stripped_tree_name

def py_module_filename_for_tree(tree):
    name = strip_tree_name(tree.name)
    return "NL{}.py".format(name)

def py_controller_module_string(py_module_name):
    return "bgelogic.{}.pulse_network".format(py_module_name)

def py_module_file_path_for_stripped_tree_name(stripped_tree_name):
    module_name = py_module_name_for_stripped_tree_name(stripped_tree_name)
    path = bpy.path.abspath("//bgelogic/{}".format(module_name))
    return path


def get_key_network_initial_status_for_tree_name(tree_name):
    return 'NL_{}_initial_status'.format(tree_name)

def get_key_network_initial_status_for_tree(nodetree):
    return get_key_network_initial_status_for_tree_name(nodetree.name)


def get_network_initial_status_for_object(ob, tree_name):
    status_key = get_key_network_initial_status_for_tree_name(tree_name)
    game_settings = ob.game
    game_properties = game_settings.properties
    for p in game_properties:
        if p.name == status_key:
            assert p.type == "BOOL"
            return p.value
    return None


def set_network_initial_status_key(ob, tree_name, initial_status_value, update_object_tree_item=True):
    current_active_object = bpy.context.scene.objects.active
    bpy.context.scene.objects.active = ob
    print("set_network_initial_status_key", ob, update_object_tree_item)
    status_key = get_key_network_initial_status_for_tree_name(tree_name)
    game_properties = ob.game.properties
    index = -1
    property_exists = False
    for p in game_properties:
        index += 1
        if p.name == status_key:
            assert p.type == "BOOL"
            p.value = initial_status_value
            property_exists = True
            break
    if not property_exists:
        bpy.ops.object.game_property_new(type="BOOL", name=status_key)
        game_property = game_properties[-1]
        game_property.value = initial_status_value
    if update_object_tree_item:
        print("also updating the tree_item...", ob)
        for tree_item in ob.bgelogic_treelist:
            print("looking at", tree_item.tree_name, "vs", tree_name)
            if tree_item.tree_name == tree_name:
                print("set initial status", ob.name, tree_name, initial_status_value)
                tree_item.tree_initial_status = initial_status_value
    bpy.context.scene.objects.active = current_active_object

def rename_initial_status_game_object_property(ob, old_tree_name, new_tree_name):
    old_key = get_key_network_initial_status_for_tree_name(old_tree_name)
    new_key = get_key_network_initial_status_for_tree_name(new_tree_name)
    for p in ob.game.properties:
        if p.name == old_key:
            p.name = new_key
            return
    raise RuntimeError("I can't find the property {} in the object {} to rename {}", old_key, ob.name, new_key)

def remove_network_initial_status_key(ob, tree_name):
    status_key = get_key_network_initial_status_for_tree_name(tree_name)
    game_properties = ob.game.properties
    index = -1
    for p in game_properties:
        index += 1
        if p.name == status_key:
            assert p.type == "BOOL"
            break
    if index >= 0:
        print("Utilities.remove_network_initial_status_key, removing from {} index {}", ob.name, index)
        bpy.ops.object.game_property_remove(index=index)


def remove_tree_item_from_object(ob, tree_name):
    index = -1
    for item in ob.bgelogic_treelist:
        index += 1
        if item.tree_name == tree_name: break
    if index >= 0:
        ob.bgelogic_treelist.remove(index)
    else:
        print("WARNING 18763 cannot remove item {} from object {} because no such item exists in that object".format(tree_name, ob.name))


def object_has_treeitem_for_treename(ob, treename):
    for item in ob.bgelogic_treelist:
        if item.tree_name == treename: return True
    return False



def compute_initial_status_of_tree(tree_name, objects):
    last_status = None
    for ob in objects:
        status = get_network_initial_status_for_object(ob, tree_name)
        if last_status is None: last_status = status
        elif last_status != status: return None#states are mixed in the list, return None
    return last_status#all states are the same