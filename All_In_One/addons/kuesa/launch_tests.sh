#!/bin/bash -xe
#
# launch_tests.sh
#
# This file is part of Kuesa.
#
# Copyright (C) 2018 Klarälvdalens Datakonsult AB, a KDAB Group company, info@kdab.com
# Author: Paul Lemire <paul.lemire@kdab.com>
#
# Licensees holding valid proprietary KDAB Kuesa licenses may use this file in
# accordance with the Kuesa Enterprise License Agreement provided with the Software in the
# LICENSE.KUESA.ENTERPRISE file.
#
# Contact info@kdab.com if any conditions of this licensing are not clear to you.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

export BLENDER_USER_CONFIG="$PWD"
export BLENDER_USER_SCRIPTS="$BLENDER_USER_CONFIG/__scripts__"
BLENDER_ADDONS="$BLENDER_USER_SCRIPTS/addons"

rm -rf $BLENDER_ADDONS
mkdir -p $BLENDER_ADDONS
ln -s $PWD "$BLENDER_ADDONS/kuesa"
ln -s "$PWD/../kuesa_exporter/glTF-Blender-Exporter/scripts/addons/io_scene_gltf2" "$BLENDER_ADDONS/kuesa_exporter"

PYTHONPATH=$BLENDER_USER_CONFIG
blender -b -P tests/tests.py -- $PYTHONPATH
