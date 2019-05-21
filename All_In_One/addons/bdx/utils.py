import os
import re
import fnmatch
import string
import bpy

p = os.path

def plugin_root():
    return p.dirname(__file__)

def gen_root():
    return p.join(plugin_root(), "gen")

proot = None 
def project_root():
    root = p.join(bpy.path.abspath('//'), p.pardir)
    if not proot:
        return p.abspath(root)
    return p.abspath(proot)

def project_name():
    with open(p.join(project_root(), "build.gradle")) as f:
        for line in f.readlines():
            if "appName" in line:
                _, name, *_ = line.split("'")
                return name


def set_file_line(file_path, line_num, text):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    lines[line_num - 1] = text + '\n'

    with open(file_path, 'w') as f:
        f.writelines(lines)

def get_file_line(file_path, line_num):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    return lines[line_num - 1]


def set_file_var(file_path, var_name, value):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for i, ln in enumerate(lines):
        if var_name+" =" in ln:
            r, _ = ln.split('=')
            lines[i] = '= '.join([r, value + ';\n'])

    with open(file_path, 'w') as f:
        f.writelines(lines)


def remove_lines_containing(file_path, pattern):
    with open(file_path, 'r') as f:
        lines = [l for l in f.readlines() if pattern not in l]

    with open(file_path, 'w') as f:
        f.writelines(lines)


def insert_lines_after(file_path, pattern, new_lines):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if pattern in line:
            break

    i += 1

    if i == len(lines):
        return

    new_lines = [l + '\n' for l in new_lines]

    lines = lines[:i] + new_lines + lines[i:]

    with open(file_path, 'w') as f:
        f.writelines(lines)


def replace_line_containing(file_path, pattern, new_line):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if pattern in line:
            break

    lines[i] = new_line + '\n';

    with open(file_path, 'w') as f:
        f.writelines(lines)


def in_bdx_project():
    return p.isdir(p.join(project_root(), "android", "assets", "bdx"))

def dict_delta(d, dp):
    return {k: dp[k] for k in set(dp) - set(d)}

def src_root(project="core", target_file="BdxApp.java"):
    for root, dirs, files in os.walk(p.join(project_root(), project, "src")):
        if target_file in files:
            return root

def package_name():
    with open(p.join(src_root(), "BdxApp.java"), 'r') as f:
        _, package = f.readline().split()
    return package[:-1]

def angel_code(path_to_fnt):
    """
    Returns dict with relevant angel code data,
    which is retreived from a .fnt file.

    """
    def line_to_items(line):
        words = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', line)
        items = [w.split('=') if '=' in w else (w, "0") 
                 for w in words]
        return [(k, eval(v)) for k, v in items]

    ac = {"char":{}}
    with open(path_to_fnt, "r") as f:
        for l in f:
            (key, _), *data = line_to_items(l)
            if key == "char":
                (_, char_id), *rest = data
                ac["char"][char_id] = dict(rest)
            else:
                ac[key] = dict(data)
    
    return ac

def listdir(path_to_dir, recursive=False, full_path=True, pattern="*", files_only=False, dirs_only=False):
    ret = []

    fds = [1, 2]
    if files_only:
        fds.remove(1)
    elif dirs_only:
        fds.remove(2)

    for root_dirs_files in os.walk(path_to_dir):
        root = root_dirs_files[0]
        for i in fds:
            for fd in root_dirs_files[i]:
                if fnmatch.fnmatch(fd, pattern):
                    ret.append(p.join(root, fd) if full_path else fd)

        if not recursive:
            break

    return ret

def gradle_cache_root():
    return p.join(p.expanduser('~'),
                  ".gradle",
                  "caches",
                  "modules-2",
                  "files-2.1")

def find_file(pattern, path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                return p.join(root, name)

def libgdx_version():
    fp = p.join(project_root(), "build.gradle")
    _, version, *_ = get_file_line(fp, 21).split("'")
    return version

def internal_java_package():
    java_texts = [t for t in bpy.data.texts.values() if t.name.endswith(".java")]

    if not java_texts:
        return None

    for text_line in java_texts[0].lines:
        line = text_line.body
        if line.startswith("package "):
            return line.split(" ")[1][:-1]

def in_packed_bdx_blend():
    return bpy.data.is_saved and internal_java_package()

def split_path(path):
    head, tail = p.split(path)
    if head:
        return split_path(head) + [tail]
    else:
        return [tail]

def save_internal_java_files(to_dir, overwrite=False):
    saved = []
    java_texts = [t for t in bpy.data.texts.values() if t.name.endswith(".java")]

    for t in java_texts:
        fp = p.join(to_dir, t.name)

        if not overwrite and p.exists(fp):
            continue

        saved.append(fp)

        with open(fp, 'w') as f:
            f.write(t.as_string())

    return saved

def str_to_valid_java_class_name(input_string):
    class_name = ['i'] # first character must be a letter

    valid_chars = string.ascii_letters + string.digits + '_'

    for char in input_string:
        if char in valid_chars:
            class_name.append(char)
        else:
            class_name.append('_'+str(ord(char))+'_')

    return "".join(class_name)
