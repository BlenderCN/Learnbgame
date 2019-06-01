import sys
import os
import shutil
import subprocess
import mylib

import lackey

args = sys.argv

selfpath = args[0]
selfdir = os.path.dirname(selfpath)

print(args)
rootdir = args[1]
if not os.path.isdir(rootdir):
    print("フォルダをドロップしてください。")
    sys.exit()

pathlist = []
def getfiles(dir):
    global pathlist
    files = os.listdir(dir)
    for file in files:
        path = dir + os.sep + file
        if os.path.isdir(path):
            getfiles(path)
        else:
            pathlist.append(path)

getfiles(rootdir)
# print(pathlist)

list_avatar = []
list_animation = []
list_garment = []

def get_pathdata(path):
    pathdir = os.path.dirname(path)
    fullname = os.path.basename(path)
    name,ext = os.path.splitext(fullname)
    return pathdir, name, ext

for path in pathlist:
    pathdir, name, ext = get_pathdata(path)
    # print("%s, %s, %s"%(pathdir, name, ext))

    # アニメーションを探して同名.objがあるかみたほうが確実
    # if ext == ".obj":
    #     if name != "result":
    #         list_avatar.append(path)
    if ext == ".mdd":
        list_animation.append(path)
    if ext == ".zpac":
        list_garment.append(path)

def get_garment(name):
    global list_garment
    for garment in list_garment:
        if name not in garment:
            continue
        pathdir, gname, ext = get_pathdata(garment)
        if gname == name:
            return garment
    return None

mdcontroldir = os.path.dirname(args[0])
mdcontrol = mdcontroldir + os.sep + "mdcontrol.py"

print("******************************")
print("START.")
print("******************************")

for animation in list_animation:
    loc = lackey.Mouse().getPos()
    if loc.getX() == 0 and loc.getY() == 0:
        print("abort.")
        sys.exit()

    print(animation)
    pathdir, name, ext = get_pathdata(animation)
    avatar = pathdir + os.sep + name + ".obj"

    if not os.path.exists(avatar):
        print("path not exists. %s"%avatar)
        continue

    result = pathdir + os.sep + "result.obj"

    garment = get_garment(name)
    if garment is None:
        print("garment not found.")
        continue

    print("******************************")
    print("processing... %s"%(avatar))
    cmdstr = 'python "%s" "%s" "%s" "%s" "%s"'%(mdcontrol, avatar, animation, garment, result)
    print(cmdstr)
    p = subprocess.Popen(cmdstr)
    p.wait(5*60)

print("******************************")
print("DONE.")
print("******************************")
