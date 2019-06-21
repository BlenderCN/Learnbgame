import bpy

import json
from urllib.request import urlopen
import webbrowser
import time


def find_filenames():
    filenames = set()
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:

            if not area.type == 'TEXT_EDITOR':
                continue

            for s in area.spaces:
                if s.type == 'TEXT_EDITOR':
                    filenames.add(s.text.name)
    return filenames


def upload(gist_files_dict, project_name, public_switch):

    if len(gist_files_dict) == 0:
        print("nothing to send!")
        return

    pf = time.strftime("_%Y_%m_%d_%H-%M")
    gist_post_data = {
        'description': project_name+pf,
        'public': public_switch,
        'files': gist_files_dict}

    json_post_data = json.dumps(gist_post_data).encode('utf-8')

    def get_gist_url(found_json):
        wfile = json.JSONDecoder()
        wjson = wfile.decode(found_json)
        gist_url = 'https://gist.github.com/' + wjson['id']

        print(gist_url)
        webbrowser.open(gist_url)
        # or just copy url to clipboard?

    def upload_gist():
        print('sending')
        url = 'https://api.github.com/gists'
        json_to_parse = urlopen(url, data=json_post_data)
        print(json_to_parse)

        print('received response from server')
        found_json = json_to_parse.readall().decode()
        get_gist_url(found_json)

    upload_gist()


def to_gist(file_names, project_name='noname', public_switch=True):
    gist_files_dict = {}
    for f in file_names:
        tfile = bpy.data.texts.get(f)
        if tfile:
            file_content = tfile.as_string()
            gist_files_dict[f] = {"content": file_content}

    upload(gist_files_dict, project_name, public_switch)
