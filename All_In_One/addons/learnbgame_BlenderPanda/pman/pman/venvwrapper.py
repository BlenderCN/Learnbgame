import subprocess
import sys

ACTIVATE_PATH = sys.argv[1]

with open(ACTIVATE_PATH) as f:
    CODE = compile(f.read(), ACTIVATE_PATH, 'exec')
    exec(CODE, dict(__file__=ACTIVATE_PATH)) #pylint:disable=exec-used

sys.exit(subprocess.call(sys.argv[2:]))
