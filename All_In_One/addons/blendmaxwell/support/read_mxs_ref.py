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
import json
import shutil
import argparse
import textwrap
import os
import struct


quiet = False
LOG_FILE_PATH = None


def log(msg, indent=0):
    if(quiet):
        return
    m = "{0}> {1}".format("    " * indent, msg)
    print(m)
    if(LOG_FILE_PATH is not None):
        with open(LOG_FILE_PATH, mode='a', encoding='utf-8', ) as f:
            f.write("{}{}".format(m, "\n"))


class PercentDone():
    def __init__(self, total, prefix="> ", indent=0):
        self.current = 0
        self.percent = -1
        self.last = -1
        self.total = total
        self.prefix = prefix
        self.indent = indent
        self.t = "    "
        self.r = "\r"
        self.n = "\n"
    
    def step(self, numdone=1):
        if(quiet):
            return
        self.current += numdone
        self.percent = int(self.current / (self.total / 100))
        if(self.percent > self.last):
            sys.stdout.write(self.r)
            sys.stdout.write("{0}{1}{2}%".format(self.t * self.indent, self.prefix, self.percent))
            self.last = self.percent
        if(self.percent >= 100 or self.total == self.current):
            sys.stdout.write(self.r)
            sys.stdout.write("{0}{1}{2}%{3}".format(self.t * self.indent, self.prefix, 100, self.n))
            if(LOG_FILE_PATH is not None):
                with open(LOG_FILE_PATH, mode='a', encoding='utf-8', ) as f:
                    f.write("{}".format("{0}{1}{2}%{3}".format(self.t * self.indent, self.prefix, 100, self.n)))


class MXSBinRefVertsWriter():
    def __init__(self, path, data, ):
        o = "@"
        with open("{0}.tmp".format(path), 'wb') as f:
            p = struct.pack
            fw = f.write
            # header
            fw(p(o + "7s", 'BINREFV'.encode('utf-8')))
            fw(p(o + "?", False))
            # number of objects
            fw(p(o + "i", len(data)))
            for i in range(len(data)):
                d = data[i]
                name = d['name']
                base = d['base']
                pivot = d['pivot']
                vertices = d['vertices']
                # name
                fw(p(o + "250s", name.encode('utf-8')))
                # base and pivot
                fw(p(o + "12d", *[a for b in base for a in b]))
                fw(p(o + "12d", *[a for b in pivot for a in b]))
                # number of vertices
                fw(p(o + "i", len(vertices) * 3))
                # vertices
                lv = len(vertices)
                fw(p(o + "{}d".format(lv * 3), *[f for v in vertices for f in v]))
            fw(p(o + "?", False))
        # swap files
        if(os.path.exists(path)):
            os.remove(path)
        shutil.move("{0}.tmp".format(path), path)
        self.path = path


def get_objects_names(scene):
    it = CmaxwellObjectIterator()
    o = it.first(scene)
    l = []
    while not o.isNull():
        name, _ = o.getName()
        l.append(name)
        o = it.next()
    return l


def object(o):
    is_instance, _ = o.isInstance()
    is_mesh, _ = o.isMesh()
    if(is_instance == 0 and is_mesh == 0):
        return None
    
    def get_verts(o):
        vs = []
        nv, _ = o.getVerticesCount()
        for i in range(nv):
            v, _ = o.getVertex(i, 0)
            vs.append((v.x(), v.y(), v.z()))
        return vs
    
    b, p = global_transform(o)
    r = {'name': o.getName()[0],
         'base': b,
         'pivot': p,
         'vertices': [], }
    if(is_instance == 1):
        io = o.getInstanced()
        r['vertices'] = get_verts(io)
    else:
        r['vertices'] = get_verts(o)
    return r


def global_transform(o):
    cb, _ = o.getWorldTransform()
    o = cb.origin
    x = cb.xAxis
    y = cb.yAxis
    z = cb.zAxis
    rb = [[o.x(), o.y(), o.z()], [x.x(), x.y(), x.z()], [y.x(), y.y(), y.z()], [z.x(), z.y(), z.z()]]
    rp = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), )
    return rb, rp


def main(args):
    log("maxwell meshes to data:", 1)
    # scene
    mp = args.mxs_path
    log("reading mxs scene from: {0}".format(mp), 2)
    scene = Cmaxwell(mwcallback)
    ok = scene.readMXS(mp)
    if(not ok):
        if(not os.path.exists(mp)):
            raise RuntimeError("Error during reading scene {}, file not found..".format(mp))
        raise RuntimeError("Error during reading scene {}".format(mp))
    # read meshes and instances
    nms = get_objects_names(scene)
    data = []
    log("reading meshes..", 2)
    progress = PercentDone(len(nms), prefix="> ", indent=2, )
    for n in nms:
        d = None
        o = scene.getObject(n)
        if(not o.isNull()):
            if(o.isMesh()[0] == 1 and o.isInstance()[0] == 0):
                # is mesh, read its vertices
                d = object(o)
        if(d is not None):
            data.append(d)
        progress.step()
    log("reading instances..", 2)
    progress = PercentDone(len(nms), prefix="> ", indent=2, )
    for n in nms:
        d = None
        o = scene.getObject(n)
        if(not o.isNull()):
            if(o.isMesh()[0] == 0 and o.isInstance()[0] == 1):
                # is instance, find instanced mesh and just copy vertices
                io = o.getInstanced()
                ion = io.getName()[0]
                for a in data:
                    if(a['name'] == ion):
                        b, p = global_transform(o)
                        d = {'name': o.getName()[0],
                             'base': b,
                             'pivot': p,
                             'vertices': a['vertices'][:], }
        if(d is not None):
            data.append(d)
        progress.step()
    # save data
    log("serializing..", 2)
    p = args.scene_data_path
    w = MXSBinRefVertsWriter(p, data)
    log("done.", 2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=textwrap.dedent('''Read vertices locations for MXS reference viewport diplay'''),
                                     epilog='', formatter_class=argparse.RawDescriptionHelpFormatter, add_help=True, )
    parser.add_argument('-q', '--quiet', action='store_true', help='no logging except errors')
    parser.add_argument('pymaxwell_path', type=str, help='path to directory containing pymaxwell')
    parser.add_argument('log_file', type=str, help='path to log file')
    parser.add_argument('mxs_path', type=str, help='path to source .mxs')
    parser.add_argument('scene_data_path', type=str, help='path to serialized data')
    args = parser.parse_args()
    
    PYMAXWELL_PATH = args.pymaxwell_path
    
    try:
        from pymaxwell import *
    except ImportError:
        if(not os.path.exists(PYMAXWELL_PATH)):
            raise OSError("pymaxwell for python 3.5 does not exist ({})".format(PYMAXWELL_PATH))
        sys.path.insert(0, PYMAXWELL_PATH)
        from pymaxwell import *
    
    quiet = args.quiet
    LOG_FILE_PATH = args.log_file
    
    try:
        # import cProfile, pstats, io
        # pr = cProfile.Profile()
        # pr.enable()
        
        main(args)
        
        # pr.disable()
        # s = io.StringIO()
        # sortby = 'cumulative'
        # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        # ps.print_stats()
        # print(s.getvalue())
        
    except Exception as e:
        import traceback
        m = traceback.format_exc()
        log(m)
        sys.exit(1)
    sys.exit(0)
