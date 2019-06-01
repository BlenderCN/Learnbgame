import sys
import os
import shutil
import subprocess
import zipfile

args = sys.argv

selfpath = args[0]
selfdir = os.path.dirname(selfpath)

toolbox_dir = os.path.dirname(selfdir)
addon_dir = os.path.dirname(toolbox_dir)
print(addon_dir)
zipdest = selfdir + os.sep + "fujiwara_toolbox.zip"

#既にあるzipの削除
if os.path.exists(zipdest):
    os.remove(zipdest)


#http://tokibito.hatenablog.com/entry/20110630/1309359802
def zip_directory(path):
    zip_targets = []
    # pathからディレクトリ名を取り出す
    base = os.path.basename(path)
    # 作成するzipファイルのフルパス
    zipfilepath = os.path.abspath('%s.zip' % base)
    # walkでファイルを探す
    for dirpath, dirnames, filenames in os.walk(path):
        # 特定文字列の除外
        if ".vs" in dirpath or ".vscode" in dirpath or ".git" in dirpath or "__pycache__" in dirpath or "設計とか" in dirpath or "UIutils" in dirpath:
            continue

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            # 作成するzipファイルのパスと同じファイルは除外する
            if filepath == zipfilepath:
                continue

            arc_name = os.path.relpath(filepath, os.path.dirname(path))
            print(filepath, arc_name)
            zip_targets.append((filepath, arc_name))
        for dirname in dirnames:
            filepath = os.path.join(dirpath, dirname)
            arc_name = os.path.relpath(filepath, os.path.dirname(path)) + os.path.sep
            print(filepath, arc_name)
            zip_targets.append((filepath, arc_name))

    # zipファイルの作成
    zip = zipfile.ZipFile(zipfilepath, 'w', zipfile.ZIP_DEFLATED)
    print("zip")
    print(zipfilepath)
    for filepath, name in zip_targets:
        zip.write(filepath, name)
    zip.close()
    return zipfilepath

zipped = zip_directory(toolbox_dir)
shutil.move(zipped, zipdest)