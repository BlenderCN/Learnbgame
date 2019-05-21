# import bpy
import re
import os
import zipfile
import urllib
import json
import bpy
from urllib.request import urlopen
from console_python import add_scrollback

'''
design considerations

from past experience this should not totally flatten the existing install,
rather it it should copy the content (minus folders..2.7x etc) into a
new archive. So in the event of 'catastrophic' failure I can revert.

Further caution taken with regards to any symlinked folders which may exist.
For me inside addons and addons_contrib i have several such folders which
link to local git repository of addons in development.

I think the process should be
- [x] locate download zip (After narrow down)
- [x] remove whitelisted from zip
- [x] strip out python by default
- [ ] start external python thread
- [ ] tell it where the current .exe is
- [ ] close blender
- [ ] zip all files in the executable folder
- [ ] read whitelist of addons to remove from the download zip before copy
- [ ] remove all whitelisted folders from the download.zip
- [ ] unpack download.zip into correct place
- [ ] start blender
- [ ] end longrunning python thread

'''


def get_whitelist():
    # this whitelist allows users to prevent an overwrite of certain files
    # or folders inside
    folders = {
        "addons": [
            "/Flow",
            "/sverchok"
        ],
        "addons_contrib": [
            "/mesh_tinyCAD",
            "/BioBlender",
            "/BCPrompt"
        ],
        "addons_extern": [

        ]
    }
    return dict(items=folders)


def peek_builder_org(search_target):
    base_url = 'https://builder.blender.org/download/'
    print('reading from', base_url)
    d = urlopen(base_url)
    d = d.read().decode('utf8')
    d = d.split('\n')

    hrefs = []
    pattern = 'href=\"(.*)\"\>'

    if len(search_target) == 1:
        '''
        this allows user to type:  -up win32
        by adding >ble, the result will only be blender master, not a branch.
        '''
        search_target.append('>ble')

    for line in d:
        if ('href=' in line):
            if all([(target in line) for target in search_target]):
                full_line = line.strip()
                match = re.search(pattern, full_line)
                href_str = match.group(1)
                hrefs.append(base_url + href_str)

    return hrefs

# if True:
#     f = peek_builder_org(['win32', '>ble'])
#     print(f)


def remove_whitelisted_from_zip(archive_path, whitelist):

    archive_name = os.path.basename(archive_path)
    if not archive_name.endswith('.zip'):
        return  # end early

    # version_pattern = r'blender-(\d\.\d\d)-'
    version = '2.73'

    _dir = os.path.dirname(archive_path)
    new_archive_name = archive_name.replace('.zip', '_new.zip')
    new_archive_path = os.path.join(_dir, new_archive_name)

    archive_less_ext = archive_name[:-4]
    internal_path = archive_less_ext + '/' + version
    zipped_py = internal_path + '/python'
    scripts = internal_path + '/scripts'

    zin = zipfile.ZipFile(archive_path, 'r')
    zout = zipfile.ZipFile(new_archive_path, 'w')
    for item in zin.infolist():
        curfile = item.filename

        if curfile.startswith(zipped_py) or in_whitelist(scripts, curfile, whitelist):
            continue

        # only reaches here if the file is not /python or not in /whitelist
        buffer = zin.read(curfile)
        zout.writestr(item, buffer)

    zout.close()
    zin.close()
    print('filtered! ')


def in_whitelist(scripts, curfile, wl):
    for k, v in wl['items'].items():
        for f in v:
            if curfile.startswith(scripts + '/' + k + f):
                print('skipping:', curfile)
                return True
    return False


def process_zip(url):
    wl = get_whitelist()
    print(url)
    archive_path = r'C:\Users\dealga\Desktop\bzip_test\blender-2.73-d9fa9bf-win32.zip'
    remove_whitelisted_from_zip(archive_path, wl)

# process_zip(url=None)

'''
 ----- possibly should be own module
'''

def get_raw_url_from_gist_id(gist_id):
    
    gist_id = str(gist_id)
    url = 'https://api.github.com/gists/' + gist_id
    
    found_json = urlopen(url).readall().decode()

    wfile = json.JSONDecoder()
    wjson = wfile.decode(found_json)

    # 'files' may contain several - this will mess up gist name.
    files_flag = 'files'
    file_names = list(wjson[files_flag].keys())
    file_name = file_names[0]
    return wjson[files_flag][file_name]['raw_url']


def get_gist_as_string(gist_id):
    url = get_raw_url_from_gist_id(gist_id)
    conn = urlopen(url).readall().decode()
    return conn

def get_sv():
    add_scrollback('getting sverchok bootstrapper', 'OUTPUT')
    string_load = get_gist_as_string("5a4440e7455940174ab9")
    print(string_load[:100])
    
    svbl = bpy.data.texts.new('sverchok bootloader')
    svbl.write(string_load)
    add_scrollback('execuion bootstrapper complete', 'OUTPUT')

    # until a tidier solution comes along
    ctx = bpy.context.copy()
    ctx['edit_text'] = svbl # specify the text datablock to execute
    # ctx['area'] = area # not actually needed...
    # ctx['region'] = area.regions[-1] # ... just be nice
    bpy.ops.text.run_script(ctx)

    