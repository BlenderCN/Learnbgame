#! /usr/bin/env python3
"""
Functions relating to the import of v_sim ascii files
"""

import re 
from collections import namedtuple
from mathutils import Vector

class Mode(namedtuple('Mode', 'freq qpt vectors')):
    """
    Collection of vibrational mode data imported from a v_sim ascii file

    :param freq: Vibrational frequency
    :type freq: float
    :param qpt: **q**-point of mode
    :type qpt: 3-list of reciprocal space coordinates
    :param vectors: Eigenvectors
    :type vectors: Nested list; 3-lists of complex numbers corresponding to atoms
    """
    pass

def import_vsim(filename):
    """
    Import data from v_sim ascii file, including lattice vectors, atomic positions and phonon modes

    :param filename: Path to .ascii file

    :returns: cell_vsim, positions, symbols, vibs

    :return cell_vsim: Lattice vectors in v_sim format
    :rtype: 2x3 nested lists of floats
    :return positions: Atomic positions
    :rtype: list of 3-Vectors
    :return symbols:   Symbols corresponding to atomic positions
    :rtype: list of strings
    :return vibs:      Vibrations
    :rtype: list of "Mode" namedtuples

    """
    with open(filename,'r') as f:
        f.readline() # Skip header
        # Read in lattice vectors (2-row format) and cast as floats
        cell_vsim = [[float(x) for x in f.readline().split()],
                     [float(x) for x in f.readline().split()]]
        # Read in all remaining non-commented lines as positions/symbols, commented lines to new array
        positions, symbols, commentlines = [], [], []
        for line in f:
            if line[0] != '#' and line[0] != '\!':
                line = line.split()
                position = [float(x) for x in line[0:3]]
                symbol = line[3]
                positions.append(Vector(position))
                symbols.append(symbol)
            else:
                commentlines.append(line.strip())

    # remove comment characters and implement linebreaks (linebreak character \)

    for index, line in enumerate(commentlines):
        while line[-1] == '\\':
            line = line[:-1] + commentlines.pop(index+1)[1:]
        commentlines[index] = line[1:]

    # Import data from commentlines
    vibs = []
    for line in commentlines:
        vector_txt = re.search('qpt=\[(.+)\]',line)
        if vector_txt:
            mode_data = vector_txt.group(1).split(';')
            qpt = [float(x) for x in mode_data[0:3]]
            freq = float(mode_data[3])
            vector_list = [float(x) for x in mode_data[4:]]
            vector_set = [vector_list[6*i:6*i+6] for i in range(len(positions))]
            complex_vectors = [[complex(x[0],x[3]),
                               complex(x[1],x[4]),
                                       complex(x[2],x[5])] for x in vector_set]
            vibs.append(Mode(freq, qpt, complex_vectors))

    if _check_if_reduced(filename):
        positions = _reduced_to_cartesian(positions, cell_vsim)
            
    return (cell_vsim, positions, symbols, vibs)

def _check_if_reduced(filename):
    """
    Scan a .ascii file for the "reduced" keyword

    :params filename: v_sim .ascii file to check
    :type filename: float

    :returns: Boolean
    """
    with open(filename,'r') as f:
        f.readline() # Skip header
        for line in f:
            if 'reduced' in line:
                return True
        else:
            return False

def _reduced_to_cartesian(positions, cell_vsim):
    """
    Convert a set of atomic positions in lattice vector units to Cartesian coordinates

    :param positions: Atomic positions in reduced coordinates
    :type positions: List of 3-tuples/lists/Vectors
    :param cell_vsim: Lattice vectors in v_sim (6-value) format
    :format cell_vsim: 2x3 nested lists

    :returns: Atomic positions in Cartesian coordinates
    :rtype: List of 3-Vectors
    """
    lattice_vectors = cell_vsim_to_vectors(cell_vsim)
    cartesian_positions = []
    for position in positions:
        cartesian_position = Vector((0.,0.,0.))
        for position_i, vector in zip(position, lattice_vectors):
            cartesian_position += position_i * vector
        cartesian_positions.append(cartesian_position)
    return cartesian_positions

def cell_vsim_to_vectors(cell_vsim):
    """
    Convert between v_sim 6-value lattice vector format (`ref <http://inac.cea.fr/L_Sim/V_Sim/sample.html>`_) and set of three Cartesian vectors

    :param cell_vsim: Lattice vectors in v_sim format
    :type cell_vsim: 2x3 nested lists

    :returns: Cartesian lattice vectors
    :rtype: 3-list of 3-Vectors
    """
    dxx, dyx, dyy = cell_vsim[0]
    dzx, dzy, dzz = cell_vsim[1]
    return [Vector([dxx, 0., 0.]),
            Vector([dyx, dyy, 0.]),
            Vector([dzx, dzy, dzz])]

if __name__ == "__main__":
    cell, positions, symbols, vibs = import_vsim('gamma_vibs.ascii')

    print(vibs)
    print(cell_vsim_to_vectors(cell))
    print(symbols)
