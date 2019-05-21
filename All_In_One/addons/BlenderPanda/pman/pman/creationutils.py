import os
import shutil


def create_dirs(projectdir, dirs):
    dirs = [os.path.join(projectdir, i) for i in dirs]

    for d in dirs:
        if os.path.exists(d):
            print("\tSkipping existing directory: {}".format(d))
        else:
            print("\tCreating directory: {}".format(d))
            os.mkdir(d)


def get_template_dir():
    pmandir = os.path.dirname(__file__)
    return os.path.join(pmandir, 'templates')


def copy_template_files(projectdir, templatedir, templatefiles):
    for tmplfile in templatefiles:
        src = os.path.join(templatedir, tmplfile[0])
        dst = os.path.join(projectdir, tmplfile[1])
        print("Creating {}".format(dst))
        if os.path.exists(dst):
            print("\t{} already exists, skipping".format(dst))
        else:
            shutil.copyfile(src, dst)
            print("\t{} copied to {}".format(src, dst))
