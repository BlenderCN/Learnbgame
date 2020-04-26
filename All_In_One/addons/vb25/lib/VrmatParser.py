#
# V-Ray Python Tools
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

from xml.dom import minidom


def GetXMLMaterialsNames(filepath):
    xmldoc = minidom.parse(filepath)

    materialPluginNames = []

    for item in xmldoc.getElementsByTagName('Asset'):
        if item.attributes['type'].value == 'material':
            url = str(item.attributes['url'].value)
            if url.startswith("/"):
                url = url[1:]
            materialPluginNames.append(url)

    return materialPluginNames


if __name__ == '__main__':
    print(GetXMLMaterialsNames("/home/bdancer/devel/vrayblender/bug-reports/andybot_vrmat/vray_mtl_metal1.vrmat"))
