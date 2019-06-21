# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
import collections, json

from .. import LuxRenderAddon


class Custom_Context(object):
    """
    Imitate the real pylux Context object so that we can
    write materials to LBM2 files using the same API

    NOTE; not all API calls are supported by this context,
    just enough to allow material/texture/volume export
    """

    API_TYPE = 'FILE'

    _default_data = {
        'name': '',
        'category_id': -1,
        'version': LuxRenderAddon.BL_VERSION,
        'objects': [],
        'metadata': {}
    }

    def __init__(self, name):
        self.context_name = name
        self.lbm2_data = Custom_Context._default_data
        self.lbm2_objects = []
        self.lbm2_metadata = {}
        self._size = 244  # Rough overhead for object definition

    def set_material_name(self, name):
        self.lbm2_data['name'] = name

    def update_material_metadata(self, **kwargs):
        self.lbm2_data['metadata'].update(kwargs)

    def _get_lbm2(self, add_comment=False):
        lbm2_data = self.lbm2_data
        lbm2_data['objects'] = self.lbm2_objects
        # 1.22 mostly corrects for other data not yet accounted for ;)
        # print('lbm2 estimated_size %s' % self._size*1.22)
        lbm2_data['metadata']['estimated_size'] = round(self._size * 1.22)
        return lbm2_data

    def write(self, filename):
        with open(filename, 'w') as output_file:
            # The only reason to use OrderedDict is so that _comment
            # appears at the top of the file
            lbm2_data = collections.OrderedDict()
            lbm2_data['_comment'] = 'LBM2 material data saved by LuxBlend25'
            lbm2_data.update(self._get_lbm2())

            json.dump(
                lbm2_data,
                output_file,
                indent=2
            )

    def upload(self, lrmdb_state):
        if lrmdb_state.loggedin:
            s = lrmdb_state.server_instance()
            upload = s.material.submit(self._get_lbm2())
            if type(upload) is str:
                raise Exception(upload)
            return upload
        else:
            raise Exception("Not logged in!")

    def getRenderingServersStatus(self):
        return []

    def _api(self, identifier, args=[], extra_tokens=''):
        """
        identifier			string
        args				list

        Make a standard pylux.Context API call. In this case
        the API call is translated into a minimal dict that
        will later be passed to json.dump

        Returns None
        """

        # name is a string, and params a list
        name, params = args

        obj = {
            'type': identifier,
            'name': name,
            'extra_tokens': extra_tokens,
            'paramset': [],
        }

        # Size really is just an estimate, and is most accurate for large
        # amounts of data
        self._size += 120  # Rough overhead per object entry
        self._size += params.getSize()  # + the estimated size of encoded data
        for p in params:
            obj['paramset'].append({
                'type': p.type,
                'name': p.name,
                'value': p.value
            })

        self.lbm2_objects.append(obj)

    # Wrapped pylux.Context API calls follow ...

    def makeNamedMaterial(self, name, params):
        self._api("MakeNamedMaterial", [name, params])

    def makeNamedVolume(self, name, type, params):
        self._api("MakeNamedVolume", [name, params], extra_tokens='"%s"' % type)

    def interior(self, name):
        self._api('Interior ', [name, []])

    def exterior(self, name):
        self._api('Exterior ', [name, []])

    def texture(self, name, type, texture, params):
        self._api("Texture", [name, params], extra_tokens='"%s" "%s"' % (type, texture))

    def cleanup(self):
        pass

    def exit(self):
        pass

    def wait(self):
        pass
