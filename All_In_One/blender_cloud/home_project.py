# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import logging

import pillarsdk
from pillarsdk import exceptions as sdk_exceptions
from .pillar import pillar_call

log = logging.getLogger(__name__)
HOME_PROJECT_ENDPOINT = '/bcloud/home-project'


async def get_home_project(params=None) -> pillarsdk.Project:
    """Returns the home project."""

    log.debug('Getting home project')
    try:
        return await pillar_call(pillarsdk.Project.find_from_endpoint,
                                 HOME_PROJECT_ENDPOINT, params=params)
    except sdk_exceptions.ForbiddenAccess:
        log.warning('Access to the home project was denied. '
                    'Double-check that you are logged in with valid BlenderID credentials.')
        raise
    except sdk_exceptions.ResourceNotFound:
        log.warning('No home project available.')
        raise


async def get_home_project_id() -> str:
    """Returns just the ID of the home project."""

    home_proj = await get_home_project({'projection': {'_id': 1}})
    home_proj_id = home_proj['_id']
    return home_proj_id
