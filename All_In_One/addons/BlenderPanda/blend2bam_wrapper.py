import os
import sys
sys.path.append(os.path.join(
    os.path.dirname(__file__),
    'panda3d-blend2bam',
))

from blend2bam.cli import main #pylint:disable=no-name-in-module,wrong-import-position
sys.exit(main())
