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
import shlex
import subprocess


LOG_FILE_PATH = None


def log(msg, indent=0):
    m = "{0}> {1}".format("    " * indent, msg)
    print(m)
    if(LOG_FILE_PATH is not None):
        with open(LOG_FILE_PATH, mode='a', encoding='utf-8', ) as f:
            f.write("{}{}".format(m, "\n"))


def main(args):
    mp = os.path.join(args.directory, 'render.mxi')
    ep = os.path.join(args.directory, 'render.exr')
    a = numpy.zeros((1, 1, 3), dtype=numpy.float, )
    if(os.path.exists(mp)):
        log('reading mxi: {}'.format(mp), 2)
        i = CmaxwellMxi()
        i.read(mp)
        a, _ = i.getRenderBuffer(32)
    elif(os.path.exists(ep)):
        log('reading exr: {}'.format(ep), 2)
        i = CmaxwellMxi()
        i.readImage(ep)
        i.write(mp)
        a, _ = i.getRenderBuffer(32)
    else:
        log('image not found..', 2)
    
    np = os.path.join(args.directory, "preview.npy")
    log('writing numpy: {}'.format(np), 2)
    numpy.save(np, a)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=textwrap.dedent('''Make Maxwell Material from serialized data'''), epilog='',
                                     formatter_class=argparse.RawDescriptionHelpFormatter, add_help=True, )
    parser.add_argument('pymaxwell_path', type=str, help='path to directory containing pymaxwell')
    parser.add_argument('numpy_path', type=str, help='path to directory containing numpy')
    parser.add_argument('log_file', type=str, help='path to log file')
    parser.add_argument('directory', type=str, help='path to temp directory')
    args = parser.parse_args()
    
    PYMAXWELL_PATH = args.pymaxwell_path
    NUMPY_PATH = args.numpy_path
    
    try:
        from pymaxwell import *
    except ImportError:
        if(not os.path.exists(PYMAXWELL_PATH)):
            raise OSError("pymaxwell for python 3.5 does not exist ({})".format(PYMAXWELL_PATH))
        sys.path.insert(0, PYMAXWELL_PATH)
        from pymaxwell import *
    
    try:
        import numpy
    except ImportError:
        sys.path.insert(0, NUMPY_PATH)
        import numpy
    
    LOG_FILE_PATH = args.log_file
    
    try:
        main(args)
    except Exception as e:
        import traceback
        m = traceback.format_exc()
        log(m)
        sys.exit(1)
    sys.exit(0)
