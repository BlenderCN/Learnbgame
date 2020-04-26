"""Export Module"""

import csv
import io
import logging
import zipfile

import bpy
import bpy_extras

from .. import model
from .. import pam

logger = logging.getLogger(__package__)


def getUVs(object, particle_system):
    """ returns a numpy-array of uv - coordinates for a given particle-system 
    on a given object """
    locations = [p.location for p in object.particle_systems[particle_system].particles]
    uvs = [pam.map3dPointToUV(object, object, loc) for loc in locations]
    return np.array(uvs)

def saveUVs(filename, object, particle_system):
    """ saves the uv-coordinates of all particles for a given object and a given
    particle_system id """
    uvs = getUVs(object, particle_system)
    f = open(filename, 'w')
    writer = csv.writer(f, delimiter=";")
    for uv in uvs:
        writer.writerow([uv[0], uv[1]])
        
    f.close()


def export_connections(filepath):
    """Export connection and distance-informations

    :param str filepath: export filename

    .. note::
        * cmatrices: list of connection matrices
        * dmatrices: list of distance matrices
        * nglist: list of neural groups
        * connection_list: list of layer-based connections

    """
    cmatrices = []
    dmatrices = []
    for c in model.CONNECTION_RESULTS:
        cmatrices.append(c['c'])
        dmatrices.append(c['d'])

    mapping_names = get_mapping_names()

    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as file:
        csv_write_matrices(file, "c", cmatrices)
        csv_write_matrices(file, "d", dmatrices)
        csv_write_matrix(file, "names", mapping_names)
        csv_write_matrix(file, "connections", model.MODEL.connection_indices)
        csv_write_matrix(file, "neurongroups", model.MODEL.ng_list)


# TODO(SK): Fill in docstring parameters/return values
def export_UVfactors(filepath, uv_matrices, layer_names):
    """Export UV-matrices, including the length of a real edge an its
    UV-distance

    :param str filename: export filename
    :param numpy.Array uv_matrices:
    :param list layer_names:

    .. note::
        * uv_matrices: list of uv-matrices
        * layer_names: list of layer-names, the order corresponds to the
          list-order in uv_matrices
    """
    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as file:
        for i, matrix in enumerate(uv_matrices):
            csv_write_matrix(file, layer_names[i], [matrix])


def csv_write_matrix(file, name, matrix):
    """Write matrix to csv file

    :param file file: open file
    :param str name: name of file
    :param numpy.Array matrix: a matrix

    """
    output = io.StringIO()
    writer = csv.writer(
        output,
        delimiter=";",
        quoting=csv.QUOTE_NONNUMERIC
    )
    for row in matrix:
        writer.writerow(row)
    file.writestr("%s.csv" % (name), output.getvalue())


def csv_write_matrices(file, suffix, matrices):
    """Write matrices to csv file

    :param file file: open file
    :param str suffix: suffix for filename
    :param list matrices: a list of matrices

    """
    for i, matrix in enumerate(matrices):
        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter=";",
            quoting=csv.QUOTE_NONNUMERIC
        )
        for row in matrix:
            writer.writerow(row)
        file.writestr("%i_%s.csv" % (i, suffix), output.getvalue())


def get_mapping_names():
    """Return names of mappings

    :return: names of mappings
    :rtype: list

    """
    m = bpy.context.scene.pam_mapping
    return [s.name for s in m.sets]


class PAMModelExportCSV(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export model to csv"""

    bl_idname = "pam.model_export_csv"
    bl_label = "Export model to csv"
    bl_description = "Export model to csv"

    filename_ext = ".zip"

    @classmethod
    def poll(cls, context):
        return any(model.MODEL.connections)

    def execute(self, context):
        export_connections(self.filepath)

        return {'FINISHED'}


def register():
    """Call upon module register"""
    bpy.utils.register_class(PAMModelExportCSV)


def unregister():
    """Call upon module unregister"""
    pass