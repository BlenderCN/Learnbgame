import os
from os.path import dirname,realpath,join,basename,abspath,splitext,normpath
import xml.etree.ElementTree as ET
import json
import subprocess
import re

working_dir = dirname(dirname(realpath(__file__)))
#settings = read_json(join(working_dir,"settings.json"))

def filtering_keyword(name,search,tags=[]) :
    search = search.lower()
    keywords = [word.lower() for word in search.split(' ') if len(word)]

    tags = [t.lower() for t in tags]
    name = name.lower()

    search_list = tags +[name]

    state = False
    for t in keywords :
        #if not t in w.text().lower() :
        if not [k for k in search_list if t in k] :
            return True
        else :
            return  False

    return False



def up_dir(filepath,level) :
    if level >= 0 :
        up = '../'*level
        path = abspath(join(filepath,up))
        return path


def get_versions(filepath,depth = 2) :
    files_version = {}

    name,ext = splitext(basename(filepath))
    print('###')
    print(name,ext)
    version = re.search('[\d][\d][\d]',name).group()
    match_name =  name.replace(version,'')
    folder = up_dir(filepath,2)

    files = []
    for root,folders,files in os.walk(folder) :
        for f in files :
            f_name,f_ext = splitext(f)
            f_search_version = re.search('[\d][\d][\d]',f_name)

            if f_search_version :
                f_version = f_search_version.group()
                f_match_name = f_name.replace(f_version,'')

                if f_match_name  == match_name and f_ext == ext :
                    files.append(join(root,f))

    return files


def get_asset_type() :
    asset_type = {}

    asset_managing_folder = os.path.join(working_dir,'asset_managing')

    for folder in os.listdir(asset_managing_folder) :
        path = os.path.join(asset_managing_folder,folder)
        if os.path.isdir(path) and not folder.startswith('_'):
            asset_type[folder] = {}

            asset_type[folder]['icon'] = os.path.join(path,'icon.png').replace('\\','/')
            asset_type[folder]['image'] = os.path.join(path,'image.png').replace('\\','/')

            asset_type[folder]['load'] = 'load_%s'%folder
            asset_type[folder]['store'] ='store_%s'%folder

    return asset_type

def icon_path(image) :
    #working_dir = os.path.dirname(os.path.realpath(__file__))
    real_path = os.path.join(working_dir,'resource','icons',image+'.png')

    if not os.path.exists(real_path) :
        real_path = os.path.join(working_dir,'resource','icons',image+'.svg')

    #print(real_path,os.path.exists)

    return real_path.replace('\\','/')

def image_path(image) :
    #working_dir = os.path.dirname(os.path.realpath(__file__))
    real_path = os.path.join(working_dir,'resource','images',image+'.png')

    return real_path.replace('\\','/')

def get_css(css) :
    #working_dir = os.path.dirname(os.path.realpath(__file__))
    real_path = join(working_dir,'resource','css',css+'.css')

    #icon_folder = join(working_dir,'resource','icons').replace('\\','/')

    resource_folder = join(working_dir,'resource').replace('\\','/')

    css_to_string =  open(real_path).read().replace('RESOURCE',resource_folder)


    return css_to_string

def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clear_layout(child.layout())

def find_icon(filepath) :
    fileName = os.path.basename(filepath)
    icon = os.path.join(filepath,fileName+'_thumb.jpg')
    if not os.path.isfile(icon):
        icon = os.path.join(filepath,fileName+'_thumb.png')

    if not os.path.isfile(icon) :
        icon = icon_path("ICON_ASSET")

    return icon.replace("\\",'/')

def read_json(filepath) :
    if os.path.exists(filepath):
        with open(filepath) as data_file:
            info = json.load(data_file)
        return info

'''
def get_latest_asset(path,depth=2):
    basename = os.path.basename(path)
    asset_basename,asset_extension = os.path.splitext(basename)

    folder = up_dir(path,2)

    versions = []
    for root,folders,files in os.walk(folder) :
        for f in files :
            name,extension = os.path.splitext(f)
            full_path = os.path.join(root,f)
            if name.startswith(asset_basename) and extension == asset_extension :
                versions.append(full_path)
    if versions :
        path = os.path.normpath(sorted(versions)[-1])

    return path
'''


def read_asset(filepath) :
    settings = read_json(os.path.join(working_dir,"settings.json"))
    jsonFile = filepath
    if os.path.exists(jsonFile):
        with open(jsonFile) as data_file:
            asset_info = json.load(data_file)
            os.chdir(os.path.dirname(filepath))

        if asset_info.get('image') and not os.path.isabs(asset_info['image']) :
            asset_info['image'] = os.path.abspath(asset_info['image']).replace('\\','/')

        asset_info['info_path'] = jsonFile
        """
        if os.path.isdir(asset_info['path']) :
            versions = []
            for root,folders,files in os.walk(asset_info['path']) :
                for f in files :
                    name,extension = os.path.splitext(f)
                    full_path = os.path.join(root,f)
                    if name.startswith(asset_info['basename']) and extension == asset_info['extension'] :
                        versions.append(full_path)
            if versions :
                asset_info['path'] = os.path.normpath(versions[-1])
                """
    if asset_info['path'].startswith('.') :
        asset_info['path'] = os.path.normpath(os.path.abspath(asset_info['path']))

    else :
        asset_info['path'] = join(normpath(settings['root']),normpath(asset_info['path']))

    #print('### PATH')
    #print(asset_info['path'])
    #print('###')

    asset_info['info_path'] = jsonFile
    #print(asset_info)
    return (asset_info)

#def write_json(json,key,)

def get_asset_from_xml(xml,step) :
    assetInfo = {}

    tree = ET.parse(xml)
    root = tree.getroot()

    assetInfo['name'] = root.attrib['name']
    assetInfo['item_type'] = root.attrib['item_type']
    assetInfo['category'] = root.attrib['category']
    assetInfo['tags'] = [tag.attrib['name'] for tag in root.findall("./tags/")]
    assetInfo['folder'] = os.path.basename(os.path.dirname(os.path.dirname(xml)))

    return assetInfo


'''
def get_asset_from_xml(xml,step) :
    assetInfo = {}

    tree = ET.parse(xml)
    root = tree.getroot()

    expression = "./step[@name='%s']/task/versions[@name='OK']/version[last()]"%step

    versions = root.findall(expression)

    if len(versions) :
        last_version= versions[-1]
        assetInfo['path'] = last_version.attrib['path']


        image = last_version.findall("./image")

        if len(image) :
            assetInfo['image'] = image[-1].attrib['path']

    else :
        print('No Asset found')


    return assetInfo
'''
