import json
import os
import sys

import panda3d.core as p3d

from blend2bam.common import ConverterBase

class ConverterGltf2Bam(ConverterBase):
    def convert_single(self, src, dst):
        scriptdir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(scriptdir, 'panda3d-gltf'))
        import gltf.converter #pylint: disable=import-error

        dstdir = os.path.dirname(dst)
        os.makedirs(dstdir, exist_ok=True)

        settings = gltf.GltfSettings(
            physics_engine=self.settings.physics_engine,
            skip_axis_conversion=True,
        )
        gltf.converter.convert(src, dst, settings)

    def convert_batch(self, srcroot, dstdir, files):
        for gltffile in files:
            src = gltffile
            dst = src.replace(srcroot, dstdir)

            if self.settings.append_ext:
                dst = dst.replace('.gltf', '.blend.bam')
            else:
                dst = dst.replace('.gltf', '.bam')

            self.convert_single(src, dst)
