##############################################################################
#
# Blender add-on for converting 3D models to SCS games
# Copyright (C) 2013  Simon Lušenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
# 
# For any additional information e-mail me to simon_lusenc (at) msn.com
#
##############################################################################

from . import export_pmd, export_pmg, export_pmc


def save(exportpath, originpath, root_ob, copy_textures, pmg_version):
    status, ob = export_pmd.save(exportpath, originpath, root_ob, copy_textures)
    if status == -1:
        return ob
    pmd = ob
    export_pmg.save(exportpath+'/'+originpath, root_ob, pmd.mat_idx_lib, len(pmd.looks_li), pmg_version)
    
    col_root = None
    for ob in root_ob.children:
        if ob.name == "collisions":
            col_root = ob
    if col_root != None:
        export_pmc.save(exportpath+'/'+originpath+'/'+root_ob.name+'.pmc', col_root, pmd)
    
    return None