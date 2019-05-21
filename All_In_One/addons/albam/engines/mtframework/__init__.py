from albam.engines.mtframework.arc import Arc
from albam.engines.mtframework.mod_156 import Mod156
from albam.engines.mtframework.tex import Tex112
from albam.engines.mtframework.mappers import FILE_ID_TO_EXTENSION, EXTENSION_TO_FILE_ID


__all__ = (
    'Arc',
    'Mod156',
    'Tex112',
    'FILE_ID_TO_EXTENSION',
    'EXTENSION_TO_FILE_ID',
)


CORRUPTED_ARCS = {
    'uOmf303.arc',
    's101.arc',  # Not an arc
    'uOmf303.arc'
    'uOmS103ScrAdj.arc',
    'uOm001f.arc',  # Contains only one model that has one vertex
    'uOmS109_Truck_Rail.arc',   # Same, one model one vertex
}

# Probably due to bad indices, needs investigation
KNOWN_ARC_BLENDER_CRASH = {
    'ev108_10.arc',
    'ev612_00.arc',
    'ev204_00.arc',
    'ev606_00.arc',
    'ev613_00.arc',
    'ev614_00.arc',
    'ev615_00.arc',
    'ev616_00.arc',
    'ev617_00.arc',
    'ev618_00.arc',
    'uOm09882.arc',
    's109.arc',
    's119.arc',
    's300.arc',
    's301.arc',
    's303.arc',
    's304.arc',
    's305.arc',
    's310.arc',
    's311.arc',
    's312.arc',
    's315.arc',
    's403.arc',
    's404.arc',
    's600.arc',
    's702.arc',
    's706.arc',
    }
