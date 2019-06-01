#
# V-Ray/Blender
#
# http://vray.cgdo.ru
#
# Author: Andrey M. Izrantsev (aka bdancer)
# E-Mail: izrantsev@cgdo.ru
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

TYPE = 'RENDERCHANNEL'

ID   = 'LIGHTSELECT'
NAME = 'Light Select'
PLUG = 'RenderChannelLightSelect'
DESC = ""
PID  = 9

PARAMS = (
    'name',
    'lights',
    'type',
    'color_mapping',   # 1
    'consider_for_aa', # 0
)


# Blender modules
import bpy

# V-Ray/Blender modules
import vb25.utils


def add_properties(parent_struct):
    class RenderChannelLightSelect(bpy.types.PropertyGroup):
        pass
    bpy.utils.register_class(RenderChannelLightSelect)

    parent_struct.RenderChannelLightSelect = bpy.props.PointerProperty(
        name        = "Light Select",
        type        =  RenderChannelLightSelect,
        description = "V-Ray \"Light Select\" render element settings"
    )

    RenderChannelLightSelect.lights = bpy.props.StringProperty(
        name        = "Lights",
        description = "Light list to appear in this channel: name{;name;...}",
        default     = ""
    )

    RenderChannelLightSelect.type = bpy.props.EnumProperty(
        name        = "Type",
        description = "Lighting Type",
        items = (
            ('RAW',      "Raw",      ""),
            ('DIFFUSE',  "Diffuse",  ""),
            ('SPECULAR', "Specular", ""),
        ),
        default = 'DIFFUSE'
    )

    RenderChannelLightSelect.consider_for_aa = bpy.props.BoolProperty(
        name        = "Consider for AA",
        description = "",
        default     = False
    )

    RenderChannelLightSelect.color_mapping = bpy.props.BoolProperty(
        name        = "Color mapping",
        description = "Apply color mapping to \"Light Select\" channel",
        default     =  True
    )



'''
  OUTPUT
'''
def write(ofile, render_channel, sce=None, name=None):
    channel_name = render_channel.name
    if name is not None:
        channel_name = name

    ofile.write("\nRenderChannelColor LightSelect_%s {"%(vb25.utils.clean_string(channel_name)))
    ofile.write("\n\tname=\"%s\";"        % channel_name)
    ofile.write("\n\tcolor_mapping=%i;"   % render_channel.color_mapping)
    ofile.write("\n\tconsider_for_aa=%i;" % render_channel.consider_for_aa)
    ofile.write("\n}\n")



'''
  GUI
'''
def draw(rna_pointer, layout, wide_ui):
    split = layout.split()
    col = split.column()

    col.prop_search(rna_pointer, 'lights', bpy.data, 'lamps')
    col.prop(rna_pointer, 'type')
    col.prop(rna_pointer, 'color_mapping')
    col.prop(rna_pointer, 'consider_for_aa')
