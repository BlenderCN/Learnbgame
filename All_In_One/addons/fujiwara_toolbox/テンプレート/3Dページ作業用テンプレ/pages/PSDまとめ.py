import sys
import os
import shutil
import subprocess

args = sys.argv

selfpath = args[0]
selfdir = os.path.dirname(selfpath)

matomedir = selfdir + os.sep + "レンダ読み込み"

dirs = os.listdir(selfdir)
for dir in dirs:
    if not os.path.isdir(dir):
        continue
    renderdir = dir + os.sep + "render"
    psdpath = renderdir + os.sep + "レンダ読み込み.psd"
    if os.path.exists(psdpath):
        shutil.copyfile(psdpath, matomedir + os.sep + dir + ".psd")