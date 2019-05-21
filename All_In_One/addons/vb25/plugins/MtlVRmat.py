#
# V-Ray/Blender
#
# http://chaosgroup.com
#
# Author: Andrei Izrantcev
# E-Mail: andrei.izrantcev@chaosgroup.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.
#

import bpy

from vb25 import utils


TYPE      = 'BRDF'
ID        = 'MtlVRmat'
PID       = 100
MAIN_BRDF = True
NAME      = "MtlVRmat"
UI        = "VRmat"
DESC      = "MtlVRmat settings"

PARAMS = (
    'filename',
    'mtlname',
)


class MtlVRmat(bpy.types.PropertyGroup):
    filename = bpy.props.StringProperty(
        name        = "File",
        subtype     = 'FILE_PATH',
        description = "Material file path"
    )

    mtlname = bpy.props.StringProperty(
        name        = "Name",
        description = "Material name in file"
    )


def add_properties(rna_pointer):
    rna_pointer.MtlVRmat = bpy.props.PointerProperty(
        name        = "MtlVRmat",
        type        =  MtlVRmat,
        description = "V-Ray MtlVRmat settings"
    )


def mapto(bus, BRDFLayered=None):
    return {}


def influence(context, layout, slot):
    pass

def gui(context, layout, MtlVRmat, material=None, node=None):
    split = layout.split(percentage=0.2, align=True)
    split.column().label("File:")
    split.column().prop(MtlVRmat, 'filename', text="")

    split = layout.split(percentage=0.2, align=True)
    split.column().label("Name:")
    row = split.column().row(align=True)
    row.prop(MtlVRmat, 'mtlname', text="")
    row.operator("vray.get_vrscene_material_name", text="", icon='IMASEL')


def write(bus, name):
    ofile = bus['files']['materials']
    ma    = bus['material']['material']

    MtlVRmat = ma.vray.MtlVRmat

    ofile.write("\nMtlVRmat %s {" % name)
    ofile.write('\n\tfilename="%s";' % utils.get_full_filepath(bus, None, MtlVRmat.filename))
    ofile.write('\n\tmtlname="%s";'  % MtlVRmat.mtlname)
    ofile.write("\n}\n")


def GetRegClasses():
    return (
        MtlVRmat,
    )


def register():
    for regClass in GetRegClasses():
        bpy.utils.register_class(regClass)


def unregister():
    for regClass in GetRegClasses():
        bpy.utils.unregister_class(regClass)
