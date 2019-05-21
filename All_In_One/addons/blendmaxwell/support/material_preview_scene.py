#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2015 Jakub Uhlík
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import sys
import traceback
import argparse
import textwrap
import json
import os


LOG_FILE_PATH = None


def log(msg, indent=0):
    m = "{0}> {1}".format("    " * indent, msg)
    print(m)
    if(LOG_FILE_PATH is not None):
        with open(LOG_FILE_PATH, mode='a', encoding='utf-8', ) as f:
            f.write("{}{}".format(m, "\n"))


def main(args):
    s = Cmaxwell(mwcallback)
    log('reading scene: {}'.format(args.scene), 2)
    ok = s.readMXS(args.scene)
    if(not ok):
        sys.exit(1)
    
    def get_material_names(s):
        it = CmaxwellMaterialIterator()
        o = it.first(s)
        l = []
        while not o.isNull():
            name = o.getName()
            l.append(name)
            o = it.next()
        return l
    
    names = get_material_names(s)
    for n in names:
        if(n.lower() == 'preview'):
            break
    
    log('swapping material: {}'.format(n), 2)
    material = s.getMaterial(n)
    material.read(os.path.join(args.directory, 'material.mxm'))
    material.forceToWriteIntoScene()
    
    log('setting parameters..', 2)
    # if draft engine is selected, no mxi will be created.. now what..
    s.setRenderParameter('ENGINE', args.quality)
    
    exr = os.path.join(args.directory, "render.exr")
    s.setPath('RENDER', exr, 32)
    
    s.setRenderParameter('DO NOT SAVE MXI FILE', False)
    s.setRenderParameter('DO NOT SAVE IMAGE FILE', False)
    
    src_dir, _ = os.path.split(args.scene)
    ok = s.addSearchingPath(src_dir)
    
    sp = os.path.join(args.directory, "scene.mxs")
    log('writing scene: {}'.format(sp), 2)
    ok = s.writeMXS(sp)
    if(not ok):
        sys.exit(1)
    log('done.', 2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=textwrap.dedent('''Modify material preview scene settings'''), epilog='',
                                     formatter_class=argparse.RawDescriptionHelpFormatter, add_help=True, )
    parser.add_argument('pymaxwell_path', type=str, help='path to directory containing pymaxwell')
    parser.add_argument('log_file', type=str, help='path to log file')
    parser.add_argument('scene', type=str, help='path to source scene mxs')
    parser.add_argument('directory', type=str, help='path to temp directory')
    parser.add_argument('quality', type=str, help='quality')
    args = parser.parse_args()
    
    PYMAXWELL_PATH = args.pymaxwell_path
    
    try:
        from pymaxwell import *
    except ImportError:
        if(not os.path.exists(PYMAXWELL_PATH)):
            raise OSError("pymaxwell for python 3.5 does not exist ({})".format(PYMAXWELL_PATH))
        sys.path.insert(0, PYMAXWELL_PATH)
        from pymaxwell import *
    
    LOG_FILE_PATH = args.log_file
    
    try:
        main(args)
    except Exception as e:
        import traceback
        m = traceback.format_exc()
        log(m)
        sys.exit(1)
    sys.exit(0)
