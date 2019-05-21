"""
 Hacks on external libraries
"""

import ogrepkg.materialexport
from .material import RexMaterialExporter

ogrepkg.materialexport.GameEngineMaterial = RexMaterialExporter
