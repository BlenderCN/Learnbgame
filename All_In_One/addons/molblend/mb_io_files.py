# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


if "logging" in locals():
    import importlib
    importlib.reload(mb_utils)
else:
    from molblend import mb_utils

import re
import os
import math
import itertools
import logging
import numpy as np
import json

from mathutils import Vector, Matrix

from molblend.elements_default import ELEMENTS

logger = logging.getLogger(__name__)
A_per_Bohr = 0.529177249

# These three classes mirror the property structure of mb_molecule. If
# something goes wrong during import, it is much easier to just discard these
# instances, than to delete already read mode vectors from the molecule.

class MB_Mode_Displacement():
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

class MB_Mode():
    def __init__(self, freq=""):
        self.freq = freq
        self.evecs = []

class MB_QMode():
    def __init__(self, iqpt, qvec):
        self.iqpt = iqpt # starts at 1
        self.qvec = qvec
        self.qvecs_format = ""
        self.modes = []
    
    def lines_iter(self, fmt='9.6f'):
        
        qvec_fmt = ",".join(['{{0[{0}]:{1}}}'.format(i,fmt) for i in range(3)])
        real_fmt = ",".join(['{{real[{0}]:{1}}}'.format(i,fmt) for i in range(3)])
        imag_fmt = ",".join(['{{imag[{0}]:{1}}}'.format(i,fmt) for i in range(3)])
        
        vec_fmt = "[[{0}], [{1}]]".format(real_fmt, imag_fmt)
        
        nevecs = len(self.modes[0].evecs)
        
        qpt_fmt =      '{{{{"qvec": [{}], "iqpt": {{iq}},\n'.format(qvec_fmt)
        mode_line =    ' "modes": [\n'
        freq_fmt  =    ' {{"freq": "{}", "imode": {},\n'
        disp_line =    '  "displacements": \n'
        vec_fmts    = ['   {},\n'.format(vec_fmt)]*nevecs
        vec_fmts[0]  = '  [{},\n'.format(vec_fmt)
        vec_fmts[-1] = '   {}]\n'.format(vec_fmt)
        end_disp_line= '  },\n'
        last_disp_line='  }\n'
        last_qpt_line= ']}\n'
        
        yield qpt_fmt.format(self.qvec, iq=self.iqpt)
        yield mode_line
        for nm, mode in enumerate(self.modes):
            yield freq_fmt.format(mode.freq, nm+1)
            yield disp_line
            for n, disp in enumerate(mode.evecs):
                yield vec_fmts[n].format(real=disp.real, imag=disp.imag)
            if nm == len(self.modes) - 1:
                yield last_disp_line
            else:
                yield end_disp_line
        yield last_qpt_line
    
class MB_Modes(list):
    
    @property
    def nqpt(self):
        return len(self)
    
    def get_qmode(self, qvec):
        for qmode in self:
            if np.isclose(qmode.qvec, qvec).all():
                return qmode
        else:
            return None
    
    def lines_iter(self, fmt='9.6f'):
        
        qvec_fmt = ",".join(['{{0[{0}]:{1}}}'.format(i,fmt) for i in range(3)])
        real_fmt = ",".join(['{{real[{0}]:{1}}}'.format(i,fmt) for i in range(3)])
        imag_fmt = ",".join(['{{imag[{0}]:{1}}}'.format(i,fmt) for i in range(3)])
        
        vec_fmt = "[[{0}], [{1}]]".format(real_fmt, imag_fmt)
        
        nevecs = len(self[0].modes[0].evecs)
        
        start_line =   '[\n'
        qpt_fmt =      '{{{{"qvec": [{}], "iqpt": {{iq}},\n'.format(qvec_fmt)
        mode_line =    ' "modes": [\n'
        freq_fmt  =    ' {{"freq": "{}", "imode": {},\n'
        disp_line =    '  "displacements": \n'
        vec_fmts    = ['   {},\n'.format(vec_fmt)]*nevecs
        vec_fmts[0]  = '  [{},\n'.format(vec_fmt)
        vec_fmts[-1] = '   {}]\n'.format(vec_fmt)
        end_disp_line= '  },\n'
        last_disp_line='  }\n'
        end_qpt_line = ']},\n'
        last_qpt_line= ']}\n'
        end_line =     ']'
        
        yield start_line
        for nq, qmode in enumerate(self):
            yield qpt_fmt.format(qmode.qvec, iq=qmode.iqpt)
            yield mode_line
            for nm, mode in enumerate(qmode.modes):
                yield freq_fmt.format(mode.freq, nm+1)
                yield disp_line
                for n, disp in enumerate(mode.evecs):
                    yield vec_fmts[n].format(real=disp.real, imag=disp.imag)
                if nm == len(qmode.modes) - 1:
                    yield last_disp_line
                else:
                    yield end_disp_line
            if nq == len(self)-1:
                yield last_qpt_line
            else:
                yield end_qpt_line
        yield end_line
    
    @classmethod
    def from_file(cls, modefilepath, file_format):
        """
        Read vibrational modes from file.
        
        Currently implemented file formats:
        - qe_dynmat: Quantum espresso (dynmat/matdyn format)
        - simple: xyz style file with Nx3 (real) or Nx6 (complex) floats
        """
        
        # Also need to add entry in mb_utils.enums.mode_file_format
        read_modes_funcs = {
            "ANADDB": cls._read_anaddb_out,
            "QE_DYNMAT": cls._read_qe_dynmat_out,
            "XYZ": cls._read_simple_modes,
            "PHONOPY": cls._read_phonopy_ascii,
        }
        if not file_format in read_modes_funcs:
            msg = "ERROR: File format {}".format(file_format)
            msg += " not implemented yet."
            logger.error(msg)
        
        return read_modes_funcs[file_format](modefilepath)
    
    @classmethod
    def _read_phonopy_ascii(cls, modefilepath):
        
        all_qpts = cls()
        with open(modefilepath, 'r') as fin:
            q_count = 0
            for line in fin:
                if "metaData:" in line and "qpt" in line:
                    qstr = line.strip()
                    while not "]" in line:
                        line = next(fin)
                        qstr += line.strip()
                    qstr = qstr.split("[")[-1].split("]")[0]
                    qstr = re.sub(r"\\|#|!", "", qstr)
                    qlst = list(map(float, qstr.split(";")))
                    qvec = np.array(qlst[:3])
                    freq = str(qlst[3])
                    all_disps = np.array(qlst[4:]).reshape((-1,6))
                    
                    qmode = all_qpts.get_qmode(qvec)
                    if not qmode:
                        q_count += 1
                        qmode = MB_QMode(q_count, qvec)
                        all_qpts.append(qmode)
                    #qmode.qvecs_format = "QE"
                    qmode.modes.append(MB_Mode(freq=freq))
                    
                    for disp in all_disps:
                        qmode.modes[-1].evecs.append(
                            MB_Mode_Displacement(disp[:3], disp[3:]))
                    
        return all_qpts
    
    @classmethod
    def _read_simple_modes(cls, modefilepath):
        """
        xyz-style format
        (i.e. real_modes.xyz:
            2
            freq = 10 cm^-1
            C  0.1  0.2  0.1
            O  0.1  0.9  0.1
            
            2
            freq = 0.1 THz
            C -0.3  0.2  0.1
            O  0.2 -0.1  0.2
            
            etc.
        )
        complex colums: ELEMENT Re_x Im_x Re_y Im_y Re_z Im_z
        The first column is completely ignored!
        This format doesn't allow separate q-points.
        """
        
        # This is a custom file format similar to the xyz file format.
        # It can only contain one q-point.
        qmode = MB_QMode(1, (0,0,0))
        
        with open(modefilepath, "r") as fin:
            number_atoms = -1
            for line in fin:
                
                # Simply ignore empty lines
                if line == "":
                    continue
                
                # Read until I find the number of atoms
                split_line = line.rsplit()
                if len(split_line) == 1:
                    try:
                        number_atoms = int(split_line[0])
                    except ValueError:
                        pass
                
                # Read as many lines as there are atoms (plus one comment line)
                # and repeat the procedure for additional frames
                if number_atoms > 0:
                    # comment line might contain frequency, search for float
                    line = fin.readline()
                    m = re.search("[-+]?[0-9]*\.[0-9]+([eEdD][-+]?[0-9]+)?", line)
                    if m:
                        freq = m.group(0)
                    else:
                        freq = ""
                    new_mode = MB_Mode(freq)
                    
                    for i in range(number_atoms):
                        split_line = fin.readline().strip().split()
                        disp = list(map(float, split_line[:]))
                        if len(disp) == 3:
                            real = disp
                            imag = (0., 0., 0.)
                        elif len(disp) == 6:
                            real = disp[::2]
                            imag = disp[1::2]
                            #real = disp[:3]
                            #imag = disp[3:6]
                        try:
                            new_mode.evecs.append(
                                MB_Mode_Displacement(real, imag))
                        except:
                            print(len(disp))
                            raise
                    qmode.modes.append(new_mode)
                    number_atoms = -1
        return cls([qmode])

    @classmethod
    def _read_qe_dynmat_out(cls, filepath):
        # read mode file, modes need to be in same order as atoms in input file
        # currently only supports dynmat.out
        
        all_qpts = cls()
        with open(filepath, 'r') as fin:
            line = next(fin)
            q_count = 0
            for line in fin:
                if 'q =' in line:
                    q_count += 1
                    q = [c*1. for c in (map(float, line.split()[-3:]))]
                    qmode = MB_QMode(q_count, q)
                    qmode.qvecs_format = "QE"
                    
                    line = next(fin) # stars
                    
                    for line in fin:
                        lstrip = line.strip()
                        
                        # new mode
                        if lstrip.startswith('omega(') or lstrip.startswith('freq ('):
                            m = re.search(
                                '(omega|freq )\(([ 0-9*]+)\).+ ([-.0-9]+)(?= \[cm-1\])', 
                                lstrip)
                            qmode.modes.append(MB_Mode(m.group(3)))
                        
                        elif lstrip.startswith('('):
                            lsplit = lstrip[1:-1].split()
                            
                            disp = list(map(float, lsplit))
                            qmode.modes[-1].evecs.append(
                                MB_Mode_Displacement(disp[::2], disp[1::2]))
                        
                        elif '**********' in line:
                            all_qpts.append(qmode)
                            break
        return all_qpts

    @classmethod
    def _read_anaddb_out(cls, filepath):
        # read mode file, modes need to be in same order as atoms in input file
        
        all_qpts = cls()
        with open(filepath, 'r') as fin:
            q_count = 0
            for line in fin:
                if 'Phonon wavevector' in line:
                    q_count += 1
                    q = [c*1. for c in list(map(float, line.split()[-3:]))]
                    qmode = MB_QMode(q_count, q)
                    qmode.qvecs_format = "anaddb"
                    #msg = "Reading q-point {}: {:7.4f} {:7.4f} {:7.4f}"
                    #logger.debug(msg.format(q_count, *q))
                    while not "Phonon frequencies in cm-1" in line:
                        line = next(fin)
                    nmodes = 0
                    line = next(fin)
                    while line[0] == "-":
                        nmodes += len(line[1:].strip().split())
                        line = next(fin)
                    if nmodes%3:
                        raise ValueError("Number of modes is not divisible by 3.")
                    nat = int(nmodes/3)
                    #logger.debug("found {} frequencies in {}".format(nmodes, filepath))
                    while not "Eigendisplacements" in line:
                        line = next(fin)
                    
                    for nm in range(nmodes):
                        while not "Mode number" in line:
                            line = next(fin)
                        
                        freq = "{:6.2f} cm^-1".format(float(line.split()[-1]) * 219474.6) # Ha to cm-1
                        qmode.modes.append(MB_Mode(freq))
                        line = next(fin)
                        while line[0] != "-" and line[0] != ";":
                            line = next(fin)
                        for na in range(nat):
                        #while line[0] == "-" or line[0] == ";":
                            real = [c*1. for c in list(map(float, line.split()[-3:]))]
                            line = next(fin)
                            imag = [c*1. for c in list(map(float, line.split()[-3:]))]
                            qmode.modes[-1].evecs.append(MB_Mode_Displacement(real, imag))
                            line = next(fin)
                    all_qpts.append(qmode)
        return all_qpts

class MB_Structure():
    """
    This is a class for reading and importing structure files. It handles
    unit conversions and bond guessing.
    
    Variables:
    nframes:        Number of frames. Each atom must have nframes coordinates,
                    and if axes are present, there must be nframes of them.
    all_atoms:      dictionary of all atoms that contains element, name
                    coordinates, id, and the supercell the atom is in
    atom_unit:      unit of atom coordinates at read time
    bonds:          bond information contained in file, and after guessing
    axes:           unit cell axes of structure if present
    axes_unit:      unit of axes at read time
    origin:         where the origin of the unit cell sits 
                    (in units of axes_unit)
    """
    def __init__(self):
        self.nframes = 0
        self.all_atoms = {}
        self.atom_unit = ""
        self.bonds = {}
        self.axes = []
        self.axes_unit = ""
        self.origin = [.0, .0, .0]
    
    def guess_bonds(self, tol=0.2):
        '''
        loops through all atoms and adds list of bonds to structure in the 
        format {index1: [index2, index3], index2: [index4, index5], ...}
        If bond argument is given, only additional bonds are added
        TODO for now, this only checks in the unit of Angstroms!
        TODO use numpy, probably faster
        '''
        
        for index1, atom1 in self.all_atoms.items():
            for index2, atom2 in self.all_atoms.items():
                if (index1 < index2 and not
                        (index1 in self.bonds
                         and index2 in self.bonds[index1])):
                    distance = (atom1["coords"][0] - atom2["coords"][0]).length
                    try:
                        cov1 = ELEMENTS[atom1["element"]]['covalent']
                    except KeyError:
                        cov1 = 1
                    try:
                        cov2 = ELEMENTS[atom1["element"]]['covalent']
                    except KeyError:
                        cov2 = 1
                    # the bond length should just be the sum of covalent radii 
                    # (plus some extra just to make sure)
                    max_dist = cov1 + cov2 + tol
                    if distance < max_dist:
                        try:
                            self.bonds[index1].add(index2)
                        except KeyError:
                            self.bonds[index1] = set((index2,))
        if not self.bonds:
            logger.warning("guess_bonds: No bonds found.")
    
    def create_supercell(self, supercell):
        if self.axes:
            max_atom_index = max(self.all_atoms.keys()) + 1
            print(max_atom_index)
            n_unit_cell = 0
            iter_3d = itertools.product(range(supercell[0]),
                                        range(supercell[1]),
                                        range(supercell[2]))
            single_cell = list(self.all_atoms.items())
            for i, j, k in iter_3d:
                for index, atom in single_cell:
                    sc_coords = []
                    for loc, uc in zip(atom["coords"], self.axes):
                        sc_coords.append(
                            loc.copy() + i*uc[0] + j*uc[1] + k*uc[2]
                            )
                    #d = [element, atom_name, location, mode_vec]
                    new_index = index + max_atom_index*n_unit_cell
                    self.all_atoms[new_index] = {
                        "element": atom["element"],
                        "name": atom["name"],
                        "coords": sc_coords,
                        "id": index, # keep old index for reference
                        "supercell": (i, j, k),
                        }
                n_unit_cell += 1
        else:
            logger.error("Supercell requested, but no unit cell vectors read")
    
    def get_center_of_mass(self):
        origin = Vector((0.0,0.0,0.0))
        coords = [atom["coords"][0] for atom in self.all_atoms.values()]
        center_of_mass = sum(coords, origin) / len(coords)
        return center_of_mass
    
    def apply_mask(self, mask_planes, mask_flip=False):
        delete = set()
        for index, atom in self.all_atoms.items():
            if not mb_utils.is_inside_of_planes(mask_planes, 
                                                atom["coords"][0],
                                                flip=mask_flip):
                delete.add(index)
        for index in delete:
            del self.all_atoms[index]
            if index in self.bonds:
                del self.bonds[index]
        for index1 in self.bonds:
            self.bonds[index1] = self.bonds[index1] - delete
        
    
    @classmethod
    def from_file(cls, filepath,
                  auto_unit=True,
                  unit_fac=1.0):
        read_funcs = {
            "xyz": cls._read_xyz_file,
            "pdb": cls._read_pdb_file,
            "POSCAR": cls._read_POSCAR_file,
            "vasp": cls._read_POSCAR_file,
            "ascii": cls._read_phonopy_ascii,
            "cube": cls._read_cube_file,
            "abinit": cls._read_abinit_output_file,
            "qe_input": cls._read_qe_input_file,
            "qe_output": cls._read_qe_rlx_output_file
            }
        
        fmt = os.path.basename(filepath).rsplit('.')[-1]
        # Determine file format
        if not fmt in read_funcs:
            # read first lines of file to determine file format
            with open(filepath, 'r') as fin:
                lines = fin.read()
                if "ABINIT" in lines:
                    fmt = "abinit"
                if "&control" in lines.lower():
                    fmt = "qe_input"
                elif "BFGS Geometry Optimization" in lines:
                    fmt = "qe_output"
        logger.debug("Reading {} as {} file.".format(filepath, fmt))
        structure = read_funcs[fmt](filepath)
        
        if structure.axes and not len(structure.axes) == structure.nframes:
            raise IOError(("Number of unit vectors ({}) and frames ({})"
                            " does not match").format(len(structure.axes), 
                                                      structure.nframes))
        # now convert all numbers
        unit = {
            "angstrom": 1.0,
            "bohr": A_per_Bohr
            }
        if len(structure.axes):
            try:
                fac = unit[structure.axes_unit]
            except KeyError:
                msg = "Axes unit '{}' unknown. This is probably a bug in {}"
                msg = msg.format(structure.axes_unit, read_funcs[fmt].__name__)
                raise KeyError(msg)
            for i in range(len(structure.axes)):
                structure.axes[i] = fac * Matrix(structure.axes[i])
            structure.origin = Vector(structure.origin) * fac
        
        if structure.atom_unit == "crystal":
            if not auto_unit:
                msg = "It looks like atom coordinates are in crystal units,"
                msg += " while user requested '{}'.".format(unit_fac)
                logger.warning(msg)
                cell_mats = [unit_fac] * structure.nframes
            else:
                if not structure.axes:
                    msg = "Atom unit in crystal, but no axes present. "
                    msg += "Probably a bug in {}".format(read_funcs[fmt].__name__)
                    raise IOError(msg)
                cell_mats = [Matrix(ax).transposed() for ax in structure.axes]
        else:
            # override automatic unit here if user chose to
            fac = unit[structure.atom_unit] if auto_unit else unit_fac
            cell_mats = [fac] * structure.nframes
        
        for atom in structure.all_atoms.values():
            if not len(cell_mats) == len(atom['coords']):
                msg = "List of conversion factors has wrong length ({}) "
                msg += "compared to number of coordinates ({}). "
                msg += "This should not have happened..."
                raise ValueError(msg.format(len(cell_mats),
                                            len(atom['coords'])))
            for n, (m, c) in enumerate(zip(cell_mats, atom['coords'])):
                atom['coords'][n] = m * Vector(c)
        
        return structure
    
    @classmethod
    def _read_cube_file(cls, filepath):
        """
        Reading Gaussian cube file format.
        This code is assuming that either all units are in Bohr (positive 
        numbers of voxels in lines 4-6) or Angstrom (negative numbers), 
        including the atomic coordinates. The Gaussian documentation is
        slightly vague on that.
        """
        strc = cls()
        strc.nframes = 1
        element_by_number = dict(
            [(ELEMENTS[element]["atomic number"], element) for element in ELEMENTS]
            )
        with open(filepath, "r") as fin:
            next(fin)
            next(fin)
            ls = next(fin).split()
            nat = abs(int(ls[0]))
            origin = Vector(list(map(float, ls[1:4])))
            nvoxel = np.zeros(3, dtype=int)
            voxel_vec = np.zeros((3,3))
            for i in range(3):
                n, x, y, z = next(fin).split()
                nvoxel[i] = int(n)
                voxel_vec[i,:] = list(map(float, (x, y, z)))
            
            if (nvoxel<0).all():
                strc.axes_unit = "angstrom"
            elif (nvoxel<0).any():
                msg = (
                    "{} ".format(filepath) +
                    "seems to contain mixed units (+/- mixed in lines 4-6). "
                    "Please make sure either all units are in Bohr (+) or "
                    "Angstrom (-)."
                    )
                report({'ERROR'}, msg)
                return False
            else:
                strc.axes_unit = "bohr"
            
            unit_cell = voxel_vec * nvoxel[:,np.newaxis]
            strc.axes = [[Vector(c) for c in unit_cell]]
            
            strc.origin = origin
            
            for n in range(nat):
                nel, _, x, y, z = list(map(float, next(fin).split()))
                element = element_by_number[nel]
                
                strc.all_atoms[n] = {
                        "element": element,
                        "name": element,
                        "coords": [Vector((x, y, z))], # always in Bohr!
                        "id": n}
        strc.atom_unit = "bohr"
        return strc
    
    @classmethod
    def _read_phonopy_ascii(cls, filepath):
        strc = cls()
        keywords = []
        nat = 0
        with open(filepath, "r") as fin:
            next(fin) # dump
            dxx, dyx, dyy = list(map(float, next(fin).split()))
            dzx, dzy, dzz = list(map(float, next(fin).split()))
            for line in fin:
                if line.startswith("#keyword"):
                    keywords.extend(re.findall('[a-zA-Z0-9]+', line)[1:])
                    logger.debug("found keywords: {}".format(",".join(keywords)))
                elif line.startswith("#") or line.startswith("!"):
                    pass
                else:
                    ls = line.split()
                    strc.all_atoms[nat] = {
                        "element": ls[3],
                        "name": ls[-1],
                        "coords": [list(map(float, ls[:3]))],
                        "id": nat}
                    nat += 1
        # postprocess based on keywords
        if 'angdeg' in keywords:
            alpha, beta, gamma = np.deg2rad((bc, ac, ab))
            a, b, c = dxx, dyx, dyy
            avec = np.array((a, 0., 0.))
            bvec = np.array((b*np.cos(gamma), b*np.sin(gamma), 0.))
            cx = c*np.cos(beta)
            cy = c*(np.cos(alpha) - np.cos(beta)*np.cos(gamma))
            cz = np.sqrt(c*c - cx*cx - cy*cy)
            cvec = np.array((cx,cy,cz))
            return np.array((avec, bvec, cvec))
        else:
            x = Vector((dxx, 0, 0))
            y = Vector((dyx, dyy, 0))
            z = Vector((dzx, dzy, dzz))
            strc.axes = [[x, y, z]]
        
        if "reduced" in keywords:
            strc.atom_unit = "crystal"
        for s in ("bohr", "bohrd0", "atomic", "atomicd0"):
            if s in keywords:
                strc.axes_unit = "bohr"
                strc.atom_unit = strc.atom_unit or "bohr"
        strc.axes_unit = strc.axes_unit or "angstrom"
        strc.atom_unit = strc.atom_unit or "angstrom"
        if "freeBC" in keywords:
            # unit cell for 0D system doesn't make sense and might be
            # zero anyway, leading to all kinds of problems
            strc.axes = []
        strc.nframes = 1
        return strc
        
    @classmethod
    def _read_POSCAR_file(cls, filepath_vasp):
        
        strc = cls()
        
        with open(filepath_vasp, "r") as fin:
            # first line is name or comment
            next(fin)
            scale = float(next(fin))
            # if scale is negative, it is the total volume of the cell
            volume = None
            if scale < 0.0:
                volume = -1.*scale
                scale = 1.0
            # lattice vectors
            for i in range(3):
                line = next(fin)
                coords = list(map(float, line.split()))
                strc.axes.append(Vector(coords) * scale)
            if volume:
                avec, bvec, cvec = strc.axes
                scale = V/np.absolute(np.dot(avec, np.cross(bvec, cvec)))
                strc.axes = [vec * scale for vec in strc.axes]
            # probably elements
            elements_list = next(fin).split()
            try:
                # in the old POSCAR the atom types were not specified.
                n_atoms = map(int, elements_list)
                elements = ["Default"] * sum(n_atoms)
            except ValueError:
                n_atoms = map(int, next(fin).split())
                elements = [elements_list[i] for i, n in enumerate(n_atoms)
                            for j in range(n)]
            line = next(fin).strip()
            # dynamical switch that is ignored here
            if line[0] in "Ss":
                line = next(fin).strip()
            # The next character determines format of coordinates.
            # - in cartesian coordinates
            if line[0] in "CcKk":
                strc.atom_unit = "angstrom"
            # - fractional coordinates
            elif line[0] in "Dd":
                strc.atom_unit = "crystal"
            for i, element in enumerate(elements):
                line = next(fin)
                coords = list(map(float, line.split()[:3]))
                atom_name = "{}{}".format(element.capitalize(), i)
                strc.all_atoms[i] = {"element": element,
                                     "name": atom_name,
                                     "coords": [coords],
                                     "id": i}
        strc.axes = [strc.axes]
        strc.axes_unit = "angstrom"
        strc.nframes += 1
        return strc
    
    @classmethod
    def _read_xyz_file(cls, filepath_xyz):
        
        strc = cls()
        # assume that this is in angstrom
        strc.atom_unit = "angstrom"
        
        all_frames = []
        
        element_by_number = dict(
            [(ELEMENTS[element]["atomic number"], element) for element in ELEMENTS]
            )
        
        # XYZ is not a well defined file format. This is an attempt to be very
        # flexible. about it.
        with open(filepath_xyz, "r") as fin:
            number_atoms = -1
            for line in fin:
                # Simply ignore empty lines
                if line == "":
                    continue
                
                # Read until I find the number of atoms
                split_line = line.rsplit()
                if len(split_line) == 1:
                    try:
                        number_atoms = int(split_line[0])
                    except ValueError:
                        pass
                
                # Read as many lines as there are atoms (plus one comment line)
                # and repeat the procedure for additional frames
                if number_atoms > 0:
                    # dump comment line
                    line = next(fin)
                    all_atoms = []
                    for i in range(number_atoms):
                        
                        split_line = next(fin).strip().split()
                        coords = list(map(float, split_line[1:4]))
                        location = Vector(coords)
                        
                        element = split_line[0]
                        # Apparently some formats use atomic numbers instead of
                        # element names
                        try:
                            element = element_by_number[int(element)]
                        except:
                            pass
                        atom_name = "{}{}".format(element.capitalize(), i)
                        # If element is an 'X' then it is a vacancy.
                        if "X" in element:
                            element = "Vac"
                            atom_name = "Vacancy"
                        
                        all_atoms.append([element, atom_name, location, i])
                    
                    all_frames.append(all_atoms)
                    strc.nframes += 1
                    number_atoms = -1
        
        for element, atom_name, location, i in all_frames[0]:
            strc.all_atoms[i] = {"element": element,
                                 "name": atom_name,
                                 "coords": [location],
                                 "id": i}
        # Add other frames to coordinate lists
        for frame in all_frames[1:]:
            for el, an, loc, i in frame:
                if strc.all_atoms[i]["element"] == el:
                    strc.all_atoms[i]["coords"].append(loc)
                else:
                    raise ValueError(
                        "ERROR: Mismatch across frames in file {}.\n".format(
                            filepath_pdb
                            )
                        + "atom {}: {} (frame 0)".format(
                            i, strc.all_atoms[i]["element"]
                            )
                        + "vs {} (frame {})".format(el, nf+1),
                        level=0
                        )
        return strc
    
    @classmethod
    def _read_abinit_output_file(cls, filepath_abi):
        '''
        read abinit output file
        '''
        
        strc = cls()
        
        # some default variables
        optcell = 0
        ionmov = 0
        
        with open(filepath_abi, "r") as fin:
            for line in fin:
                if "ionmov" in line and re.search("ionmov +[0-9]+", line):
                    ionmov = int(line.split()[-1])
                elif ("acell" in line
                      and re.search("acell +( [ .0-9E+-]+){3}.*", line)):
                    acell_split = line.split()
                    acell = Vector([float(f) for f in acell_split[1:4]])
                    acell_unit = "bohr"
                    if len(acell_split) == 5:
                        if acell_split[-1].startswith("Ang"):
                            acell_unit = "angstrom"
                        elif acell_split[-1] == "Bohr":
                            acell_unit = "bohr"
                        else:
                            msg = ("WARNING: Didn't understand acell unit in "
                                   + "{} ({})".format(filepath_abi,
                                                      acell_split[-1]))
                            logger.warning(msg)
                            acell_unit = "angstrom"
                    strc.axes_unit = acell_unit
                elif "natom" in line and re.search("natom +[0-9]+", line):
                    natom = int(line.split()[-1])
                elif "ndtset" in line and re.search("ndtset +[0-9]+", line):
                    ndtset = int(line.split()[-1])
                    if ndtset > 1:
                        logger.warning(
                            "WARNING: More than one dataset present. "
                            "Will probably result in unwanted behavior.")
                elif "optcell" in line and re.search("optcell +[0-9]+", line):
                    optcell = int(line.split()[-1])
                elif ("rprim" in line
                      and re.search("rprim +( [ .0-9E+-]+){3} *", line)):
                    rprim = []
                    ls = line.split()
                    rprim.append(acell[0]*Vector([float(f) for f in ls[1:4]]))
                    rprim.append(acell[1]*Vector([float(f)
                                                  for f in next(fin).split()]))
                    rprim.append(acell[2]*Vector([float(f)
                                                  for f in next(fin).split()]))
                    strc.axes.append(rprim)
                
                elif ("typat" in line
                      and re.search(" typat +( [0-9]+)+ *", line)):
                    try:
                        typat = []
                        ls = line.split()
                        typat.extend([int(i) for i in ls[1:]])
                        while len(typat) < natom:
                            typat.extend([int(i) for i in next(fin).split()])
                    except NameError as e:
                        msg = "ERROR: natom should be defined before typat"
                        logger.error(msg)
                        logger.error(e)
                elif ("xcart" in line
                      and re.search("xcart +( [ .0-9E+-]+){3} *", line)):
                    try:
                        xcart = []
                        ls = line.split()
                        strc.atom_unit = "bohr"
                        xcart.append(Vector([float(f) for f in ls[1:4]]))
                        while len(xcart) < natom:
                            xcart.append(Vector([float(f) 
                                                  for f in next(fin).split()]))
                    except NameError:
                        msg = "ERROR: natom should be defined before xcart"
                        logger.error(msg)
                        logger.error(e)
                elif "znucl" in line and re.search("znucl +( [.0-9]+)+", line):
                    znucl = [int(i.split('.')[0]) for i in line.split()[1:]]
                    znucl_str = [""] * len(znucl)
                    for el, vals in ELEMENTS.items():
                        if vals["atomic number"] in znucl:
                            znucl_str[znucl.index(vals["atomic number"])] = el
                    elements = [znucl_str[i-1] for i in typat]
                
                elif "== DATASET" in line:
                    # compile all information
                    strc.nframes += 1
                    for i, (el, location) in enumerate(zip(elements, xcart)):
                        atom_name = "{}{}".format(el.capitalize(), i)
                        strc.all_atoms[i] = {"element": el,
                                             "name": atom_name,
                                             "coords": [location],
                                             "id": i}
                    break
            if ionmov > 0:
                for line in fin:
                    if "Iteration" in line:
                        try:
                            while "---OUTPUT" not in line:
                                line = next(fin)
                        except StopIteration:
                            msg = "File {} ended prematurely"
                            logger.warning(msg.format(filepath_abi))
                            break
                        next(fin)
                        next(fin)
                        for i in range(natom):
                            ls = next(fin).split()
                            coord = Vector([float(f) for f in ls])
                            strc.all_atoms[i]["coords"].append(coord)
                        
                        # now find cell
                        if optcell > 0:
                            stop = "Real space primitive translations (rprimd)"
                            try:
                                while stop not in line:
                                    line = next(fin)
                            except StopIteration:
                                msg = "File {} ended prematurely"
                                logger.warning(msg.format(filepath_abi))
                                break
                            pattern = "\(rprimd\) \[([a-z]+)\]"
                            unit = re.search(pattern, line).group(1)
                            if unit.lower()[:3] == strc.axes_unit[:3]:
                                fac = 1.0
                            elif (unit.lower().startswith("ang")
                                  and strc.axes == "bohr"):
                                fac = 1.0/A_per_Bohr
                            elif (unit.lower() == "bohr"
                                  and strc.axes == "angstrom"):
                                fac = A_per_Bohr
                            else:
                                msg = ("WARNING: Scale of Primitive Cell unit"
                                       + " not recognized ({})".format(unit))
                                logger.warning(msg)
                                fac = 1.0
                            rprimd = []
                            for i in range(3):
                                xyz = [float(f) for f in next(fin).split()]
                                rprimd.append(Vector(xyz) * fac)
                            strc.axes.append(rprimd)
                        strc.nframes += 1
                    elif "== DATASET" in line:
                        break
        if strc.nframes > 1 and len(strc.axes) == 1:
            strc.axes = [strc.axes[0] for i in range(strc.nframes)]
        return strc
        
    @classmethod
    def _read_pdb_file(cls, filepath_pdb):
        '''
        read pdb file (only supports the old standard with < 100k atoms)
        '''
        
        strc = cls()
        
        all_frames = []
        all_atoms = {}
        double = False
        strc.atom_unit = "angstrom"
        with open(filepath_pdb, "r") as fin:
            i = -1
            for line in fin:
                
                if line == "":
                    continue
                
                if line[:6] == "CRYST1":
                    a, b, c, alpha, beta, gamma = map(float, line.split()[1:7])
                    alpha, beta, gamma = map(math.radians, 
                                             (alpha, beta, gamma))
                    avec = Vector((a, 0., 0.))
                    bvec = Vector((b*math.cos(gamma), b*math.sin(gamma), 0.))
                    cx = c*math.cos(beta)
                    cy = c*(math.cos(alpha) - math.cos(beta)*math.cos(gamma))
                    cz = math.sqrt(c*c - cx*cx - cy*cy)
                    cvec = Vector((cx,cy,cz))
                    strc.axes.append([avec, bvec, cvec])
                    strc.axes_unit = "angstrom"
                
                elif line[:6] == 'HETATM' or line[:4] == 'ATOM':
                    i += 1
                    coords = list(map(float,
                                      (line[30:38], line[38:46], line[46:54])))
                    location = Vector(coords)
                    
                    index = int(line[6:11])
                    element = line[76:78].strip().capitalize()
                    element = ''.join(s for s in element if s.isalpha())
                    atom_name = line[12:16].strip()
                    if "X" in element:
                        element = "Vac"
                    if index in all_atoms:
                        raise ValueError(
                            "duplicate atom indeces in {}".format(filepath_pdb)
                            )
                    all_atoms[index] = [element, atom_name, location, index]
                    
                elif line[:6] == 'CONECT':
                    # Need to make sure index is greater than 0
                    if int(line[6:11]) > 0:
                        atomID1 = int(line[6:11])
                        if not atomID1 in strc.bonds:
                            strc.bonds[atomID1] = set()
                        for i in range((len(line) - 11) // 5):
                            atomID2 = int(line[11 + i*5 : 16 + i*5])
                            if atomID2 > 0 and atomID2 > atomID1:
                                strc.bonds[atomID1].add(atomID2)
                
                elif line[:6] == 'ENDMDL':
                    all_frames.append(all_atoms)
                    strc.nframes += 1
                    all_atoms = {}
            
            # If there was only one model and no 'ENDMDL' present in file
            if all_atoms:
                all_frames.append(all_atoms)
                strc.nframes += 1
        
        for i in all_frames[0].keys():
            element, atom_name, location, index = all_frames[0][i]
            strc.all_atoms[i] = {"element": element,
                                 "name": atom_name,
                                 "coords": [location],
                                 "id": i}
        # Add other frames to coordinate lists
        for nf, frame in enumerate(all_frames[1:]):
            for i in frame:
                el, an, loc, index = frame[i]
                if strc.all_atoms[i]["name"] == an:
                    strc.all_atoms[i]["coords"].append(loc)
                else:
                    raise ValueError(
                        "ERROR: Mismatch across frames in file {}.\n".format(
                            filepath_pdb
                            )
                        + "atom {}: {}, {} (frame 0)".format(
                            i, strc.all_atoms[i]["element"],
                            strc.all_atoms[i]["name"]
                            )
                        + "vs {}, {} (frame {})".format(el, an, nf+1),
                        level=0
                        )
        
        if strc.nframes > 1 and len(strc.axes) == 1:
            strc.axes = [strc.axes for i in range(strc.nframes)]
        
        return strc
    
    @classmethod
    def _read_qe_input_file(cls, filepath):
        
        strc = cls()
        
        crystal_units = False
        with open(filepath, 'r') as fin:
            # Read all parameters
            for line in fin:
                for keyval in line.split(","):
                    if "nat" in keyval.lower():
                        na = keyval.split('=')[-1].strip().strip(",").strip()
                        n_atoms = int(na)
                    elif "celldm(1)" in keyval.lower():
                        al = keyval.split('=')[-1].strip().strip(",").strip()
                        alat = float(al)
                    elif "CELL_PARAMETERS" in keyval.upper():
                        if re.search("bohr|cubic", line):
                            strc.axes_unit = "bohr"
                        else:
                            strc.axes_unit = "angstrom"
                        for i in range(3):
                            line = next(fin)
                            coords = list(map(float, line.split()))
                            strc.axes.append(Vector(coords))
                    elif "ATOMIC_POSITIONS" in keyval.upper():
                        if "angstrom" in line.lower():
                            strc.atom_unit = "angstrom"
                        elif "bohr" in line.lower():
                            strc.atom_unit = "bohr"
                        elif "crystal" in line.lower():
                            # process at the end when both atomic coordinates and 
                            # vectors are read for certain
                            strc.atom_unit = "crystal"
                            # get unit vectors
                        elif "alat" in line.lower():
                            msg = ("Unit of ATOMIC_POSITIONS in "
                                   + "{} is alat. Implement!".format(filepath))
                            raise ValueError(msg)
                        else:
                            msg = ("Unit of ATOMIC_POSITIONS in "
                                   + "{} unclear.\n".format(filepath)
                                   + "Line:\n'{}'".format(line))
                            raise ValueError(msg)
                        
                        # read coordinates
                        for i in range(n_atoms):
                            line = next(fin)
                            line = line.strip()
                            split_line = line.split()
                            coords = list(map(float, split_line[1:4]))

                            element = split_line[0]
                            atom_name = "{}{}".format(element.capitalize(), i)
                            # If element is an 'X' then it is a vacancy.
                            if "X" in element:
                                element = "Vac"
                                atom_name = "Vacancy"
                            
                            strc.all_atoms[i] = {"element": element,
                                                 "name": atom_name,
                                                 "coords": [coords],
                                                 "id": i}

        strc.axes = [strc.axes]
        strc.nframes += 1
        return strc
    
    @classmethod
    def _read_qe_rlx_output_file(cls, filepath):
        # This doesn't abide 100% by the rule: read the raw numbers first,
        # convert afterwards, since the units might be jumbled. Will convert
        # everything into Angstrom
        
        strc = cls()
        
        strc.axes_unit = "angstrom"
        strc.atom_unit = "angstrom"
        with open(filepath, 'r') as fin:
            # read all parameters
            for line in fin:
                if "number of atoms/cell" in line:
                    n_atoms = int(line.split()[-1])
                elif "lattice parameter (alat)" in line:
                    alat = float(line.split()[-2]) * A_per_Bohr
                elif "crystal axes: (cart. coord. in units of alat)" in line:
                    unit_vectors = []
                    for i in range(3):
                        line = fin.readline()
                        coords = list(map(float, line.split()[3:6]))
                        unit_vectors.append(Vector(coords) * alat)
                    strc.axes.append(unit_vectors)
                elif "Cartesian axes" in line:
                    break
            
            # Read starting geometry
            next(fin) # empty line
            next(fin) # column headers
            cell_matrix = alat * Matrix.Identity(3)
            # read coordinates
            strc.nframes += 1
            for i in range(n_atoms):
                line = next(fin)
                line = line.strip()
                split_line = line.split()
                coords = list(map(float, split_line[-4:-1]))
                location = cell_matrix * Vector(coords)

                element = split_line[1]
                atom_name = "{}{}".format(element.capitalize(), i)
                # If element is an 'X' then it is a vacancy.
                if "X" in element:
                    element = "Vac"
                    atom_name = "Vacancy"
                
                strc.all_atoms[i] = {"element": element,
                                     "name": atom_name,
                                     "coords": [location],
                                     "id": i}
            
            # Now read all steps
            for line in fin:
                if "CELL_PARAMETERS" in line:
                    # vc-relax calculation
                    if "alat" in line:
                        pattern = r"CELL_PARAMETERS \(alat=(.+)\)$"
                        alat = A_per_Bohr * float(re.match(pattern,
                                                           line).group(1))
                    elif "angstrom" in line:
                        alat = 1.0
                    unit_vectors = []
                    for i in range(3):
                        line = fin.readline()
                        coords = list(map(float, line.split()))
                        unit_vectors.append(Vector(coords) * alat)
                    strc.axes.append(unit_vectors)
                
                if "ATOMIC_POSITIONS" in line:
                    strc.nframes += 1
                    # double check units and set correct conversion matrix
                    if "angstrom" in line.lower():
                        cell_matrix = 1.0 #Matrix.Identity(3)
                    elif "bohr" in line.lower():
                        cell_matrix = A_per_Bohr #* Matrix.Identity(3)
                    elif "crystal" in line.lower():
                        # get unit vectors
                        cell_matrix = Matrix(strc.axes[-1]).transposed()
                    elif "alat" in line.lower():
                        cell_matrix = alat #* Matrix.Identity(3)
                    else:
                        msg = ("Unit of ATOMIC_POSITIONS in "
                               + "{} unclear.\n".format(filepath)
                               + "Line:\n'{}'".format(line))
                        raise ValueError(msg)
                    
                    # read coordinates
                    for i in range(n_atoms):
                        line = next(fin)
                        line = line.strip()
                        split_line = line.split()
                        coords = list(map(float, split_line[1:4]))
                        location = cell_matrix * Vector(coords)

                        element = split_line[0]
                        atom_name = "{}{}".format(element.capitalize(), i)
                        # If element is an 'X' then it is a vacancy.
                        if "X" in element:
                            element = "Vac"
                            atom_name = "Vacancy"
                        
                        if strc.all_atoms[i]["element"] == element:
                            strc.all_atoms[i]["coords"].append(location)
                        else:
                            raise ValueError(
                                "ERROR: Mismatch across frames in file "
                                + "{}.\n".format(filepath)
                                + "atom {}: {} (frame 0)".format(
                                    i, strc.all_atoms[i]["element"]
                                    )
                                + "vs {} (frame {})".format(element,
                                                            strc.nframes),
                                level=0
                                )
        
        return strc
