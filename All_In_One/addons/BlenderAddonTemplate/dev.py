import os
import sys

#git_path=r'/the/path/to/the/git/project'
git_path=r'/home/gnuton/GITonio/MaterialPainter/'
sys.path.insert(0, git_path)
filename = os.path.join(git_path, 'updater.py')

exec(compile(open(filename).read(), filename, 'exec'))
