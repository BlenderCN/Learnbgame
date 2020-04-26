#!/usr/bin/env python

from os.path import join, basename
import sys
from io import BytesIO
from collections import defaultdict
import requests
from requests.auth import HTTPBasicAuth
import argparse
import getpass

class JsonObject(object):
    def __init__(self, json):
        super(JsonObject,self).__setattr__("dict", json)

    def __getattr__(self, attr):
        return self.dict.get(attr, None)

    def __setattr__(self, attr, value):
        self.dict[attr] = value

    def json(self):
        return self.dict
    
    def __unicode__(self):
        return unicode(self.dict)

    def __str__(self):
        return str(self.dict)

    def __repr__(self):
        return repr(self.dict)

class Asset(JsonObject):

    def description(self):
        return """Title: {0}
Notes: {1}
License: {2}
Tags: {3}
""".format(self.title, self.notes, self.license, self.tags)

    def get_data_content_type(self):
        r = requests.head(self.data)
        r.raise_for_status()
        return r.headers.get('content-type', None)

    def download_data(self, outpath):
        r = requests.get(self.data)
        r.raise_for_status()
        with open(outpath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)

    def download_thumbnail(self, outpath):
        r = requests.get(self.image)
        r.raise_for_status()
        with open(outpath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)

    def get_thumbnail_name(self):
        return basename(self.image)

    def get_data(self, content_type=None):
        r = requests.get(self.data)
        r.raise_for_status()
        if content_type is not None:
            if r.headers.get('content-type', None) != content_type:
                raise TypeError("Asset data is not of type " + content_type)
        f = BytesIO()
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)
        result = f.getvalue()
        f.close()
        return result

    def get_filename(self):
        return basename(self.data)

components_registry = {}

class Component(JsonObject):

    @classmethod
    def get(cls, appslug, cslug):
        global components_registry
        app = components_registry.get(appslug, None)
        if app is None:
            return None
        component_class = app.get(cslug, None)
        if component_class is None:
            return None
        return component_class(dict())

    @classmethod
    def register(cls, appslug, cslug, component_class):
        if appslug is None:
            raise ValueError("Application cannot be None")
        if appslug not in components_registry:
            components_registry[appslug] = defaultdict()
        if cslug is None:
            components_registry[appslug].default_factory = component_class
        else:
            components_registry[appslug][cslug] = component_class

    def import_asset(self, asset):
        raise NotImplementedError

    def get_current_version(self):
        return None

    def get_max_compatible_version(self):
        return None

    def get_min_compatible_version(self):
        return None

class Tag(JsonObject):
    pass

class License(JsonObject):
    pass

class AssetHubClient(object):
    def __init__(self, url, application=None, component=None, username=None, password=None):
        self.url = url
        self._base_url = join(self.url, 'api', 'assets')
        if not self._base_url.endswith('/'):
            self._base_url = self._base_url + '/'
        self.application = application
        self.component = component
        self.username = username
        self.password = password
        self.tag = None
        self.author = None
        self.id = None
        self.license = None
        self.appversion = None
        self.asset_constructor = Asset

    def _get_url(self):
        if self.id is not None:
            return join(self._base_url, self.id)
        elif self.application is not None and self.component is not None:
            return join(self._base_url, self.application, self.component)
        elif self.application is not None:
            return join(self._base_url, self.application)
        else:
            return self._base_url

    def _get_params(self):
        params = {}
        if self.tag is not None:
            params['tag'] = self.tag
        if self.author is not None:
            params['author'] = author
        if self.appversion is not None:
            params['appversion'] = self.appversion
        return params

    def get_components(self, application=None):
        if application is None:
            application = self.application
        if application is None:
            raise TypeError("Application is not defined")
        
        url = join(self.url, 'api', 'applications', application)
        r = requests.get(url)
        r.raise_for_status()
        return [Component(c) for c in r.json()]
    
    def get_tags(self):
        url = join(self.url, 'api', 'tags')
        r = requests.get(url)
        r.raise_for_status()
        return [Tag(t) for t in r.json()]

    def get_licenses(self):
        url = join(self.url, 'api', 'licenses')
        r = requests.get(url)
        r.raise_for_status()
        return [License(l) for l in r.json()]

    def format_asset_url(self, id):
        return join(self.url, "asset", str(id))

    def list(self):
        r = requests.get(self._get_url(), params=self._get_params())
        r.raise_for_status()
        json = r.json()
        result = []
        if isinstance(json, list):
            for a in json:
                asset = self.asset_constructor(a) 
                asset.url = self.format_asset_url(asset.id)
                result.append(asset)
        else:
            asset = self.asset_constructor(json)
            asset.url = self.format_asset_url(asset.id)
            result.append(asset)
        return result

    def get(self, id):
        url = join(self._base_url, str(id))
        r = requests.get(url)
        r.raise_for_status()
        asset = self.asset_constructor(r.json())
        asset.url = self.format_asset_url(asset.id)
        return asset

    def post(self, asset, data_file, file_name=None, content_type=None, image_file=None):
        auth = HTTPBasicAuth(self.username, self.password)
        component = Component.get(asset.application, asset.component)
        if component and (not asset.app_version_min or not asset.app_version_max):
            if not asset.app_version_min:
                asset.app_version_min = component.get_min_compatible_version()
            if not asset.app_version_max:
                asset.app_version_max = component.get_max_compatible_version()

        data = asset.json()
        if file_name is None:
            if hasattr(data_file, "name") and data_file.name is not None:
                file_name = basename(data_file.name)
            else:
                file_name = "asset.dat"
        if content_type is None:
            content_type = "application/octet-stream"
        files = dict(data=(file_name, data_file, content_type))
        if image_file is not None:
            files['image'] = image_file
        r = requests.post(self._base_url, data=data, files=files, auth=auth)
        r.raise_for_status()
        return r.json()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='AssetHub command-line client')
    parser.add_argument('-u', '--url', metavar='HTTP://SERVER.ORG/', help='AssetHub server URL')
    parser.add_argument('-a', '--application', metavar='APP', help='Application')
    parser.add_argument('-c', '--component', metavar='COMPONENT', help='Component')
    parser.add_argument('--author', metavar='USER', help='Asset author')
    parser.add_argument('--id', metavar='ID', help='Asset ID')
    parser.add_argument('-t', '--tag', metavar='TAG', help='Asset tag')
    parser.add_argument('-L', '--license', metavar='LICENSE', help='Asset license')
    parser.add_argument('--title', metavar='TITLE', help='Asset title')
    parser.add_argument('-J', '--json', action='store_true', help='Output data as JSON')
    parser.add_argument('-D', '--download', action='store_true', help='Download asset data')
    parser.add_argument('-P', '--post', metavar='FILENAME.dat', help='Post new asset')
    parser.add_argument('-T', '--thumb', metavar='FILENAME.png', help='Thumbnail for new asset')
    parser.add_argument('--content-type', action='store_true', help='Print data content type')
    parser.add_argument('-U', '--user', metavar='USER', help='User name')
    parser.add_argument('-W', '--password', metavar='PASSWORD', help='Password')
    args = parser.parse_args()

    if args.url:
        url = args.url
    else:
        url = 'http://assethub.iportnov.tech/'

    client = AssetHubClient(url, args.application, args.component)
    client.tag = args.tag
    client.author = args.author
    client.id = args.id

    if args.post:
        if not args.title:
            print("Title is mandatory when posting an asset")
            sys.exit(1)
        if not args.application:
            print("Application is mandatory when posting an asset")
            sys.exit(1)
        if not args.component:
            print("Component is mandatory when posting an asset")
            sys.exit(1)
        if not args.license:
            print("License is not specified, defaulting to CC0")
            args.license = "CC0"
        asset = Asset(dict(title=args.title, application=args.application, component=args.component, license=args.license))
        if not args.user:
            print("User name is mandatory to post an asset")
            sys.exit(1)
        client.username = args.user
        if not args.password:
            client.password = getpass.getpass()
        else:
            client.password = args.password

        data_file = open(args.post, 'rb')
        if args.thumb:
            image_file = open(args.thumb, 'rb')
        else:
            image_file = None
        client.post(asset, data_file, image_file)

    else:

        for asset in client.list():
            if args.download:
                asset.download_data(asset.get_filename())
                print("Downloaded " + asset.get_filename())
            elif args.json:
                print(asset)
            elif args.content_type:
                print("{}\t{}\t{}".format(asset.id, asset.title, asset.get_data_content_type()))
            else:
                print("{}\t{}".format(asset.id, asset.title))

