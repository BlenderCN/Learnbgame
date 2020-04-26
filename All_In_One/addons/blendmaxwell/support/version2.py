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
import argparse
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="pymaxwell version number",
                                     epilog='',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     add_help=True, )
    parser.add_argument('pymaxwell_path', type=str, help='path to pymaxwell')
    args = parser.parse_args()
    
    p = args.pymaxwell_path
    if(not os.path.exists(p)):
        sys.stderr.write("{}: No such file or directory".format(p))
        sys.exit(1)
    sys.path.insert(0, p)
    try:
        import pymaxwell
        v = pymaxwell.getPyMaxwellVersion()
        sys.stdout.write("{}".format(v))
        sys.exit(0)
    except ImportError as e:
        sys.stderr.write("{}".format(e))
        sys.exit(1)
