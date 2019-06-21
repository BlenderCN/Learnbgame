import os
import sys

from . import core

try:
    from direct.dist.commands import build_apps

    class BuildApps(build_apps):
        def run(self):
            # Run pman build first
            core.build()

            config = core.get_config()
            sys.path.append(config['build']['export_dir'])
            if '*' not in self.include_modules:
                self.include_modules['*'] = []
            self.include_modules['*'].append(
                'pman_renderer'
            )
            stubpath = os.path.join(config['build']['export_dir'], core.RENDER_STUB_NAME)
            with open(stubpath) as stubfile:
                for line in stubfile.readlines():
                    line = line.strip()
                    if line.startswith('modname ='):
                        self.include_modules['*'].append(
                            line.split('=')[1].strip().replace("'", '')
                        )
                        break

            # Run regular build_apps
            build_apps.run(self)
except ImportError:
    class BuildApps(object):
        def __init__(self):
            pass

        def run(self):
            raise NotImplementedError(
                "Setuptools distribution not supported by this version of Panda3D"
            )
