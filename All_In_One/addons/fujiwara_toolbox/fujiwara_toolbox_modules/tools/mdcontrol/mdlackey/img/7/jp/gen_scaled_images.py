#! python3
import sys
import os
import shutil
import subprocess
import cv2

args = sys.argv


# print(sys.path)
print(sys.version)
print("args:")
print(args)

selfpath = args[0]
selfdir = os.path.dirname(selfpath)

"""
同ディレクトリ内のフォルダの中身を、元名_000%フォルダにコピーする？
100%フォルダを、他の%フォルダにコピーする
"""

def img_resize(path, scale, outpath):
    img = cv2.imread(path)
    h,w = img.shape[:2]

    size = (int(w*scale), int(h*scale))
    img_resized = cv2.resize(img, size)

    cv2.imwrite(outpath, img_resized)


scales = [("125%",1.25), ("150%",1.5), ("175%",1.75), ("200%",2.0)]

baseimgdir = selfdir + os.sep + "100%"

baseimages = os.listdir(baseimgdir)
for baseimage in baseimages:
    for scale in scales:
        scalepath = selfdir + os.sep + scale[0]
        if not os.path.exists(scalepath):
            os.mkdir(scalepath)
        img_resize(baseimgdir + os.sep + baseimage, scale[1], scalepath + os.sep + baseimage)


