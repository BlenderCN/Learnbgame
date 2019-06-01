"""Data model module"""

import pickle

import bpy
import bpy_extras
import mathutils
import numpy
import json
import zipfile
import tempfile

from . import layer
from . import kernel
from . import mesh

"""Contains all the connection results. The structure for this list is:
list of mapping sets -> 
    dict: 'c' for connections:
        2D array with connection indices (int)
    'd' for distances:
        2D array with distances (float)
    's' for synapse:
        2D array of mathutils.Vector (2D) for synapse position on the synapse uv layer
"""
CONNECTION_RESULTS = []

"""The currently active model. Should be an object of the Model-class"""
MODEL = None

"""A list containing all mapping exceptions that occured during calculation"""
CONNECTION_ERRORS = []

MAPPING_NAMES = ['MAP_euclid', 'MAP_normal', 'MAP_random', 'MAP_top', 'MAP_uv', 'MAP_mask3D']
DISTANCE_NAMES = ['DIS_euclid', 'DIS_euclidUV', 'DIS_jumpUV', 'DIS_UVjump', 'DIS_normalUV', 'DIS_UVnormal']

class Connection():
    """Represents a Connection with multiple layers"""
    def __init__(self, layers, slayer, mappings):
        """Initialize the connection
        :param layers: a list of the layers in the connection
        :type layers: list of layer.Layer2D
        :param slayer: The index of the synaptic layer in your connection. 
        This should correspond to the index layer.SynpaseLayer object in layers
        :type slayer: int
        :param mappings: The mapping and distance functions for this connection
        :type mappings: list of tuples, each tuple containing 2 integers correspondig 
        to a mapping function and a distance function
        """
        self._layers = layers
        self._synaptic_layer_index = slayer
        self._mappings = mappings

    @property
    def layers(self):
        return self._layers

    @property
    def mappings(self):
        return self._mappings

    @property
    def mapping_connections(self):
        return [m[0] for m in self._mappings]
    
    @property
    def mapping_distances(self):
        return [m[1] for m in self._mappings]
        
    @property
    def pre_layer(self):
        return self.layers[0]

    @property
    def post_layer(self):
        return self.layers[-1]
    
    @property
    def synaptic_layer(self):
        return self.layers[self._synaptic_layer_index]
    
    @property
    def synaptic_layer_index(self):
        return self._synaptic_layer_index
    
    @property
    def pre_intermediate_layers(self):
        return self.layers[1:self._synaptic_layer_index]
    
    @property
    def post_intermediate_layers(self):
        return self.layers[self._synaptic_layer_index + 1:-1]

    def __str__(self):
        return " -> ".join(["|" + self.pre_layer.name + "|"] + [l.name for l in self.pre_intermediate_layers] + ["|" + self.synaptic_layer.name + "|"] + [l.name for l in self.post_intermediate_layers] + ["|"  + self.post_layer.name + "|"])

    def __repr__(self):
        rep = "Connection from " + self.pre_layer.name + " to " + self.post_layer.name + "\n"
        rep += "\tLayers:            " + " -> ".join(["|" + self.pre_layer.name + "| (Pre layer)"] + [l.name for l in self.pre_intermediate_layers] + ["|" + self.synaptic_layer.name + "| (Synaptic Layer)"] + [l.name for l in self.post_intermediate_layers] + ["|"  + self.post_layer.name + "| (Post Layer)\n"])
        rep += "\tMapping functions: " + ", ".join([MAPPING_NAMES[m[0]] for m in self.mappings]) + "\n"
        rep += "\tMapping distances: " + ", ".join([DISTANCE_NAMES[m[1]] for m in self.mappings]) + "\n"
        rep += "Kernel functions:\n"
        rep += "\tPre kernel:  " + self.pre_layer.kernel.name + "(" + ", ".join([str(x) + '=' + str(y) for x, y in self.pre_layer.kernel.get_args().items()]) + ")\n"
        rep += "\tPost kernel: " + self.post_layer.kernel.name + "(" + ", ".join([str(x) + '=' + str(y) for x, y in self.post_layer.kernel.get_args().items()]) + ")\n"
        rep += "Neurons:\n"
        rep += "\tPre:      " + str(self.pre_layer.neuron_count) + "\n"
        rep += "\tPost:     " + str(self.post_layer.neuron_count) + "\n"
        rep += "\tSynapses: " + str(self.synaptic_layer.no_synapses)
        rep += "\n"

        return rep

    def __eq__(self, con):
        if len(self.layers) != len(con.layers):
            return False
        for i in range(len(self.layers)):
            if self.layers[i] != con.layers[i]:
                return False
        if self.synaptic_layer_index != con.synaptic_layer_index:
            return False
        if len(self.layers) - 1 > len(con.mappings):
            return False 
        for i in range(len(self.layers) - 1):
            if self.mappings[i][0] != con.mappings[i][0] or self.mappings[i][1] != con.mappings[i][1]:
                return False
        return True

    def __ne__(self, con):
        return not self.__eq__(con)

    def toDict(self):
        """Returns a dictionary of the values of this class for json encoding"""
        conDict = {}
        conDict['layers'] = [l.name for l in self.layers]
        conDict['ng_pre'] = self.pre_layer.neuronset_name
        conDict['ng_post'] = self.post_layer.neuronset_name
        conDict['synaptic_layer_index'] = self.synaptic_layer_index
        conDict['mappings'] = [(MAPPING_NAMES[m[0]], DISTANCE_NAMES[m[1]]) for m in self.mappings]
        conDict['pre_kernel'] = {'name': self.pre_layer.kernel.name, 'args': self.pre_layer.kernel.get_args()}
        conDict['post_kernel'] = {'name': self.post_layer.kernel.name, 'args': self.post_layer.kernel.get_args()}
        conDict['no_synapses'] = self.synaptic_layer.no_synapses
        return conDict

    def toList(self):
        """Returns this class in a list format compatible with the old pam files"""
        conList = []
        conList.append([l.name for l in self.layers])
        conList.append(self.pre_layer.neuronset_name)
        conList.append(self.post_layer.neuronset_name)
        conList.append(self.synaptic_layer_index)
        conList.append([MAPPING_NAMES[m[0]] for m in self.mappings])
        conList.append([DISTANCE_NAMES[m[1]] for m in self.mappings])
        conList.append(self.pre_layer.kernel.name)
        conList.append(self.pre_layer.kernel.get_args())
        conList.append(self.post_layer.kernel.name)
        conList.append(self.post_layer.kernel.get_args())
        conList.append(self.synaptic_layer.no_synapses)
        return conList

class Model():
    """Represents a model with its connections and settings"""
    def __init__(self, ng_list = None, ng_dict = None, connections = None, connection_indices = None):
        """Create a new model
        
        :param ng_list: A list of used neuron groups
        :type ng_list: A list of tuple with 3 elements: (ng_name, psystem_name, neuron_count)
        :param ng_dict: A dictionary of used neuron groups (similar to ng_list, but the object names are the keys)
        See pam.returnNeuronGroups() for more info
        :type ng_dict: dictionary of dictionaries
        :param connections: A list of connections for this model
        :type connections: List of model.Connection
        :param connection_indices: A list of lists, containing 3 integers, that correspond to (connection_id, source_ng_id, target_ng_id)
        :type connection_indices: list
        """
        self.ng_list = ng_list or []
        self.ng_dict = ng_dict or {}
        self.connections = connections or []
        self.connection_indices = connection_indices or []

    def addConnection(self, connection):
        self.connections.append(connection)

    def __eq__(self, other):
        return self.ng_list == other.ng_list \
            and self.ng_dict == other.ng_dict \
            and self.connections == other.connections \
            and self.connection_indices == other.connection_indices

    def __ne__(self, other):
        return not self.__eq__(other)


class ModelJsonEncoder(json.JSONEncoder):
    """Encodes a model to the json format"""
    def default(self, model):
        if isinstance(model, Model):
            modelJson = {}
            modelJson['NEURON_GROUP_LIST'] = model.ng_list
            modelJson['NEURON_GROUP_DICT'] = model.ng_dict
            modelJson['CONNECTION_INDICES'] = model.connection_indices

            conJson = []
            con = model.connections
            enc = ConnectionJsonEncoder()
            for c in con:
                conJson.append(enc.default(c))
            modelJson['CONNECTIONS'] = conJson
            return modelJson
        else:
            return super().default(model)

class ConnectionJsonEncoder(json.JSONEncoder):
    """Encodes a Connection object to json"""
    def default(self, connection):
        return connection.toDict()

def decodeJSONModel(m):
    """Decode a JSON dict to a model object
    :param m: The model dict
    :type m: dict
    :retruns: A model object generated from the dict
    :rtype: model.Model"""
    model = Model()
    model.ng_list = m['NEURON_GROUP_LIST']
    model.ng_dict = m['NEURON_GROUP_DICT']
    model.connection_indices = m['CONNECTION_INDICES']
    connections = []
    for c in m['CONNECTIONS']:
        connections.append(connectionFromDict(c))
    model.connections = connections
    return model

def connectionFromDict(c):
    """Decode a JSON dict to a connection
    :param c: The connection dict
    :type c: dict
    :return: A Connection object generated from the dict
    :rtype: model.Connection"""
    kernel_pre = kernel.get_kernel(c['pre_kernel']['name'], c['pre_kernel']['args'])
    kernel_post = kernel.get_kernel(c['post_kernel']['name'], c['post_kernel']['args'])

    layer_names = c['layers']
    layers = []
    for i, l in enumerate(layer_names):
        obj = bpy.data.objects[l]
        if i == 0:
            layers.append(layer.NeuronLayer(l, obj, c['ng_pre'], obj.particle_systems[c['ng_pre']].particles, kernel_pre))
        elif i == len(layer_names)-1:
            layers.append(layer.NeuronLayer(l, obj, c['ng_post'], obj.particle_systems[c['ng_post']].particles, kernel_post))
        elif i == c['synaptic_layer_index']:
            layers.append(layer.SynapticLayer(l, obj, c['no_synapses']))
        else:
            layers.append(layer.Layer2d(l, obj))
    return Connection(layers, c['synaptic_layer_index'], [(MAPPING_NAMES.index(m[0]), DISTANCE_NAMES.index(m[1])) for m in c['mappings']])

def connectionFromList(c):
    """Create a connection instance from the old list format

    :param c: The connection dictionary
    :type c: dict
    
    :return: The created connection instance
    :rtype: model.Connection"""
    layers = []
    for i, l in enumerate(c[0]):
        if i == 0:
            layers.append(layer.NeuronLayer(l, bpy.data.objects[l], c[1], bpy.data.objects[l].particle_systems[c[1]].particles, kernel.get_kernel(c[6], c[7])))
        elif i == len(c[0])-1:
            layers.append(layer.NeuronLayer(l, bpy.data.objects[l], c[2], bpy.data.objects[l].particle_systems[c[2]].particles, kernel.get_kernel(c[8], c[9])))
        elif i == c[3]:
            layers.append(layer.SynapticLayer(l, bpy.data.objects[l], c[10]))
        else:
            layers.append(layer.Layer2d(l, bpy.data.objects[l]))
    return Connection(layers, c[3], [(c[4][i], c[5][i]) for i in range(len(c[4]))])

def saveModelToJson(model, path):
    """Save a model to a json file
    :param model: The model to save
    :type model: model.Model
    :param path: The filepath to save the model to
    :type path: string
    """
    with open(bpy.path.abspath(path), 'w+') as f:
        json.dump(model, f, cls = ModelJsonEncoder, sort_keys=True,
            indent = 4, separators=(',', ': '))

def loadModelFromJson(path):
    """Load a model from a JSON file
    :param path: The path to the JSON file
    :type path: string
    :return: The model
    :rtype: model.Model
    """
    with open(bpy.path.abspath(path), 'r') as f:
        m = decodeJSONModel(json.load(f))
    return m

def getPreIndicesOfPostIndex(c_index, post_index ):
    """ returns for a given connection-index c_index and a given post-synaptic
    neuron post_index the row-indices (index of the pre-synaptic neurons) and the
    column-index (for identifying the synapse """
    pre_indices, synapses = numpy.where(numpy.array(CONNECTION_RESULTS[c_index]['c']) == post_index)
    return pre_indices, synapses

def convertObject2String(connection):
    """Takes a CONNECTION-struct and converts `bpy.objects` to
    string names and returns a list of strings
    Note: This function is only to be used with the legacy 
    connection structures, not with a Connection object

    :param connection: The connection struct
    :type connection: list
    :return: A list of the names of the objects in the connection struct
    :rtype: list of strings
    """
    return [o.name for o in connection[0]]


def convertString2Object(connection):
    """Takes a CONNECTION-struct and converts string names to
    `bpy.objects` and returns a list of `bpy.objects`
    Note: This function is only to be used with the legacy 
    connection structures, not with a Connection object

    :param connection: A connection struct (with object names only)
    :type connection: list
    :return: A list of objects
    :rtype: list of bpy.types.Object

    """
    return [bpy.data.objects[name] for name in connection[0]]


def Connection2Pickle(connections):
    """Converts a Connection struct into a format that can be used by pickle

    :param connection: A connection struct
    :type connection: list
    :return: A new connection struct with all bpy-objects replaced with strings
    :rtype: list

    """
    result = []
    for c in connections:
        new_c = [convertObject2String(c)]
        new_c = new_c + list(c[1:])
        result.append(new_c)
    return result


def Pickle2Connection(connections):
    """Convert a conection struct from a Pickle-ready format to its normal form

    :param connection: The connection struct
    :type connection: list
    :return: A new connection struct with all object names replaced by the corresponding blender object
    :rtype: list

    """
    result = []
    for c in connections:
        if hasattr(c[6], 'name'):
            c[6] = c[6].name
        if hasattr(c[8], 'name'):
            c[8] = c[8].name
        new_c = connectionFromList(c)
        result.append(new_c)
    return result


def convertVector2Array(connection_results):
    """Takes a CONNECTION_RESULTS-struct and converts `mathutils.Vector`
    to `numpy.Array`

    :param connection_results: The connection results list
    :type connection_results: list
    :return: A new array with the Vectors replaced with arrays
    :rtype: list

    """
    result = []
    for c in connection_results:
        temp = []
        for r in c['s']:
            temp.append(numpy.array(r))
        result.append({'c': c['c'], 'd': c['d'], 's': temp})
    return result


# TODO(SK): Fill in docstring parameter/return values
def convertArray2Vector(connection_results):
    """Takes a CONNECTION_RESULTS-struct and converts `numpy.array`
    to `mathutils.Vector`

    :param connection_results: The connection results list
    :type connection_results: list
    :return: A new array with the arrays replaced with blender vectors
    :rtype: list

    """
    result = []
    for c in connection_results:
        temp = []
        for r in c['s']:
            if r.size > 0:
                temp.append([mathutils.Vector(v) for v in r])
            else:
                temp.append([[] for i in range(r.shape[0])])
        result.append({'c': c['c'], 'd': c['d'], 's': temp})
    return result


class ModelSnapshot(object):
    """Represents a snapshot of the current model"""
    def __init__(self):
        self.NG_LIST = MODEL.ng_list
        self.NG_DICT = MODEL.ng_dict
        self.CONNECTION_INDICES = MODEL.connection_indices
        self.CONNECTIONS = [c.toList() for c in MODEL.connections]
        self.CONNECTION_RESULTS = convertVector2Array(CONNECTION_RESULTS)

    def __eq__(self, other):
        return str(self.__dict__) == str(other.__dict__)


def savePickle(path):
    """Save current model via pickle to given path

    :param str path: filepath

    """
    snapshot = ModelSnapshot()
    pickle.dump(snapshot, open(path, "wb"))


def loadPickle(path):
    """Load model via pickle from given path

    :param str path: filepath

    """
    snapshot = pickle.load(open(path, "rb"))

    global CONNECTION_RESULTS
    global CONNECTION_ERRORS
    global MODEL
    NG_LIST = snapshot.NG_LIST
    NG_DICT = snapshot.NG_DICT
    CONNECTION_INDICES = snapshot.CONNECTION_INDICES
    CONNECTIONS = Pickle2Connection(snapshot.CONNECTIONS)
    CONNECTION_RESULTS = convertArray2Vector(snapshot.CONNECTION_RESULTS)
    CONNECTION_ERRORS = []
    MODEL = Model(NG_LIST, NG_DICT, CONNECTIONS, CONNECTION_INDICES)


def comparePickle(path1, path2):
    """Compare two models with each other

    :param str path1: a path
    :param str path2: another path

    """
    m1 = loadPickle(path1)
    m2 = loadPickle(path2)
    return m1 == m2


def reset():
    """Reset most important variables"""
    global MODEL
    global CONNECTION_RESULTS
    MODEL = Model()
    CONNECTION_RESULTS = []

def clearQuadtreeCache():
    """Clears the quadtree cache. 
    Has to be called each time a uv-map has changed."""
    mesh.QUADTREE_CACHE = {}

def saveZip(path, model = None, connection_results = None):
    """Saves a model and the connection results to a zip file using JSON encoding
    :param path: The path where the zip file should be saved
    :type path: string
    :param model: The model to save. If None, the currently active model is used
    :type model: model.Model
    :param connection_results: The connection results. If None, the currently active CONNECTION_RESULTS is used)
    :type connection_results: list (See CONNECTION_RESULTS for details)
    """
    if model is None:
        model = MODEL
    if connection_results is None:
        connection_results = CONNECTION_RESULTS

    connection_results_dict = {}
    for i, con in enumerate(connection_results):
        connection_results_dict['connection_result_' + str(i) + '_c'] = con['c']
        connection_results_dict['connection_result_' + str(i) + '_d'] = con['d']

        # Synapses have to be copied manually because numpy can't handle vector objects
        s = numpy.zeros((len(con['s']), len(con['c'][0]), 2))
        for s_i in range(s.shape[0]):
            for s_j in range(s.shape[1]):
                if len(con['s'][s_i][s_j]) == 2:
                    for s_k in range(s.shape[2]):
                        s[s_i][s_j][s_k] = con['s'][s_i][s_j][s_k]
        connection_results_dict['connection_result_' + str(i) + '_s'] = s

    # Write connection results using numpy npy files and compress them
    with open(path, 'wb') as f:
        numpy.savez_compressed(f, **connection_results_dict)
    
    # Open zipfile again and add the json model data to it
    with zipfile.ZipFile(path, mode = 'a') as zf:
        json_data = json.dumps(model, cls = ModelJsonEncoder, sort_keys=True,
                indent = 4, separators=(',', ': '))
        zf.writestr('model.json', json_data)

def loadZip(path):
    """Load model and connection results from a zip file and save it as the active model

    :param path: The path to the zip file
    :type path: string"""
    with zipfile.ZipFile(path, mode = 'r') as zf:
        model_file = zf.open('model.json', 'r')
        m = decodeJSONModel(json.loads(model_file.read().decode('UTF-8')))
        global MODEL
        MODEL = m
        model_file.close()

    f = numpy.load(path)
    global CONNECTION_RESULTS
    CONNECTION_RESULTS = []
    for i in range(len(m.connections)):
        dist_name = 'connection_result_' + str(i) + '_d.npy'
        con_name = 'connection_result_' + str(i) + '_c.npy'
        syn_name = 'connection_result_' + str(i) + '_s.npy'
        con = {'c': f[con_name], 'd': f[dist_name], 's': f[syn_name]}
        CONNECTION_RESULTS.append(con)
    # CONNECTION_RESULTS = convertArray2Vector(CONNECTION_RESULTS)

class PAMModelLoad(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a model and the connection results"""

    bl_idname = "pam.model_load"
    bl_label = "Load model data"
    bl_description = "Load model data"

    load_type = bpy.props.EnumProperty(items = [
        ('auto', 'Auto', 'Detect load type by file extension', '', 1),
        ('zip', 'ZIP', 'Load from compressed zip file', '', 2),
        ('pam', 'Pickle', 'Load using Pickle serialization', '', 3)],
        name = 'File format', description = 'The type of serilization for the data', default = 'auto')

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'load_type')

    def execute(self, context):
        if self.load_type == 'auto':
            if self.filepath.endswith('.zip'):
                loadZip(self.filepath)
            else:
                loadPickle(self.filepath)
        elif self.load_type == 'pam':
            loadPickle(self.filepath)
        elif self.load_type == 'zip':
            loadZip(self.filepath)

        return {'FINISHED'}


class PAMModelSave(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Save current model with the connection results"""

    bl_idname = "pam.model_save"
    bl_label = "Save model data"
    bl_description = "Save model data"

    filename_ext = ".zip"

    save_type = bpy.props.EnumProperty(items = [
        ('zip', 'ZIP', 'Save as compressed zip file', '', 1),
        ('pam', 'Pickle', 'Save using Pickle serialization', '', 2)],
        name = 'File format', description = 'The type of serilization for the data', default = 'zip')

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'save_type')

    @classmethod
    def poll(cls, context):
        return any(MODEL.connections)

    def execute(self, context):
        if self.save_type == 'zip':
            saveZip(self.filepath)
        elif self.save_type == 'pam':
            savePickle(self.filepath)

        return {'FINISHED'}

class PAMModelJSONLoad(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a model"""

    bl_idname = "pam.model_load_json"
    bl_label = "Load model data from JSON"
    bl_description = "Load model data from JSON"

    def execute(self, context):
        m = loadModelFromJson(self.filepath)
        global MODEL
        MODEL = m

        return {'FINISHED'}

class PAMModelJSONSave(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Save current model"""

    bl_idname = "pam.model_save_json"
    bl_label = "Save model data to JSON"
    bl_description = "Save model data to JSON"

    filename_ext = ".json"

    @classmethod
    def poll(cls, context):
        return True # any(MODEL.connections)

    def execute(self, context):
        saveModelToJson(MODEL, self.filepath)

        return {'FINISHED'}

if MODEL == None:
    MODEL = Model()