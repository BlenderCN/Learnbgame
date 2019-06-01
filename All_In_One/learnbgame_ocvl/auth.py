import json
import os
import logging
from collections import OrderedDict
from urllib import parse
from os.path import dirname
from shutil import copyfile


import bpy
import requests

from ocvl import bl_info

logger = logging.getLogger(__name__)

#  SETTINGS
bpy.context.preferences.view.show_splash = True
IS_WORK_ON_COPY_INPUT = True
DEBUG = True

#  CONSTANTS
ANONYMOUS = "Anonymous"
COMMUNITY_VERSION = "COMMUNITY_VERSION"
PRO_VERSION = "PRO_VERSION"
BASE_DIR = os.path.dirname(__file__)

OCVL_PANEL_URL = "http://127.0.0.1:5000/"
OCVL_PANEL_LOGIN_URL = "http://127.0.0.1:5000/api-token-auth/"
OCVL_PANEL_PRODUCTS_URL = "http://127.0.0.1:5000/api/product/"
OCVL_GITHUB_ISSUE_TEMPLATE = "https://github.com/feler404/ocvl/issues/new?title={title}&body={body}"
OCVL_AUTHORS = " & ".join(map(str, bl_info['author']))
OCVL_VERSION = ".".join(map(str, bl_info['version']))
OCVL_EXT_VERSION = OCVL_VERSION
OCVL_AUTH_PARAMS_BASE_TEMPALTE = "?&ocvl_version={}&ocvl_ext_version={}".format(OCVL_VERSION, OCVL_EXT_VERSION)
OCVL_AUTH_PARAMS_LOGIN_PASSWORD_TEMPALTE = OCVL_AUTH_PARAMS_BASE_TEMPALTE + "&login={login}&password={password}"
OCVL_AUTH_PARAMS_LICENCE_KEY_TEMPALTE = OCVL_AUTH_PARAMS_BASE_TEMPALTE + "&licence_key={licence_key}"
OCVL_HIDDEN_NODE_PREFIX = "Hidden-"

OCVL_LINK_UPGRADE_PROGRAM_TO_PRO = 'https://ocvl-cms.herokuapp.com/admin/login/'
OCVL_LINK_TO_OCVL_PANEL = 'https://ocvl-cms.herokuapp.com/admin/login/'
OCVL_LINK_TO_STORE = 'http://0.0.0.0:5000/shop/'
OCVL_LINK_TO_CREATE_ACCOUNT = 'https://ocvl-cms.herokuapp.com/admin/login/'
OCVL_LINK_TO_MORE_TUTORIALS = 'http://tutorials.ocvl.teredo.tech/'

OCVL_APP_DATA_USER_DIR = os.path.join(bpy.utils.resource_path('USER'), "config")
OCVL_APP_DATA_USER_FILE_NAME = "ocvl_auth.txt"
APP_DATA_USER_SETTINGS = {
    "first_run": None,
    "auth_token": None,

}

class Auth:

    # _ocvl_version = COMMUNITY_VERSION
    _ocvl_version = PRO_VERSION
    _ocvl_ext = None
    _ocvl_first_running = True
    # _ocvl_pro_version_auth = False
    _ocvl_pro_version_auth = True

    instance = None

    def __new__(cls):
        if not Auth.instance:
            Auth.instance = object.__new__(cls)
        return Auth.instance

    @property
    def ocvl_version(self):
        return self._ocvl_version

    @property
    def ocvl_first_running(self):
        return self._ocvl_first_running

    @property
    def ocvl_ext(self):
        if self._ocvl_ext is None:
            try:
                from .extend.extended_utils import OCLV_EXTEND_MODULE_FAKE_VAR
                self._ocvl_ext = True
            except:
                self._ocvl_ext = False
        else:
            return self._ocvl_ext

    @property
    def ocvl_pro_version_auth(self):
        return self._ocvl_pro_version_auth and self.ocvl_ext

    def set_attr_auth(self, name, value, key=None):
        setattr(self, "_{}".format(name), value)

    @property
    def viewer_name(self):
            return "OCVLImageViewerNode"


class User:

    _instance = None
    token = None
    auth_instance = None
    is_login = None
    settings = None
    name = ANONYMOUS
    password = ""
    local_tutorials = []
    tutorials = [{"name": "First steps",
                  "icon": "PARTICLE_DATA",
                  "purchase_time": None,
                  "package_site": "http://kube.pl/"
                }]
    tutorials = []
    assets = []

    def __new__(cls, *args, **kwargs):
        if not User._instance:
            User._instance = object.__new__(cls)
        return User._instance

    def __init__(self, auth, settings):
        self.auth_instance = auth
        self.settings = settings
        self.name = settings._settings.get("login", ANONYMOUS)
        self.password = settings._settings.get("password", "")

    @property
    def is_login(self):
        return self.name != ANONYMOUS and self.token is not None


class Settings:

    _settings = {}

    def __init__(self):
        self._settings = self.get_or_create_settings()

    def get_or_create_settings(self):
        if not os.path.exists(OCVL_APP_DATA_USER_DIR):
            os.makedirs(OCVL_APP_DATA_USER_DIR)
        full_path = os.path.join(OCVL_APP_DATA_USER_DIR, OCVL_APP_DATA_USER_FILE_NAME)
        self.copy_config_to_local_dir()
        if os.path.isfile(full_path):
            logger.info("Load settings file: {}".format(full_path))
            with open(full_path, "r") as fp:
                return json.load(fp)
            print("Load settings file: {}".format(full_path))
        else:
            logger.info("Create settings file: {}".format(full_path))
            with open(full_path, "w") as fp:
                json.dump(APP_DATA_USER_SETTINGS, fp)
            return APP_DATA_USER_SETTINGS

    def copy_config_to_local_dir(self):
        """
        This is hack to override defualt settings
        :return:
        """
        file_startup = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_files/build_utils/2.80/config/startup.blend")
        file_userpref = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_files/build_utils/2.80/config/userpref.blend")

        if not os.path.exists(os.path.join(OCVL_APP_DATA_USER_DIR, "startup.blend")):
            copyfile(file_startup, os.path.join(OCVL_APP_DATA_USER_DIR, "startup.blend"))
        if not os.path.exists(os.path.join(os.path.join(OCVL_APP_DATA_USER_DIR, "userpref.blend"))):
            copyfile(file_userpref, os.path.join(OCVL_APP_DATA_USER_DIR, "userpref.blend"))


ocvl_auth = Auth()
ocvl_settings = Settings()
ocvl_user = User(ocvl_auth, ocvl_settings)


def auth_refresh_token(ocvl_user=ocvl_user):
    login_data = {"username": ocvl_user.username, "password": ocvl_user.password}
    response = requests.post(OCVL_PANEL_LOGIN_URL, data=login_data, headers={"Referer": "OCVL client"})
    if response.status_code == 200:
        auth_remote_confirm(login_data, response)
    else:
        auth_remote_reject(OCVL_PANEL_LOGIN_URL, response)


def auth_remote_confirm(login_data, response, node=None):
    if node:
        node.auth = True
    # ocvl_auth.set_attr_auth("ocvl_pro_version_auth", True)
    ocvl_user.token = response.json().get("token")
    ocvl_user.name = login_data["username"]
    products_response = requests.get(OCVL_PANEL_PRODUCTS_URL, headers={"Authorization": "JWT {}".format(ocvl_user.token)})
    logger.info("Authentication confirm for {}".format(ocvl_user.name))

    products = products_response.json()
    logger.info("Products content: {}".format(products))
    ocvl_user.tutorials.extend(products)
    # ocvl_user.assets = content.get("assets", [])
    logger.info("Content payload {} for user {}".format(products, ocvl_user.name))
    from .sverchok_point import soft_reload_menu
    soft_reload_menu()


def auth_remote_reject(url, response, node=None):
    parsed = parse.urlparse(url)
    ocvl_user.name = str(parse.parse_qs(parsed.query).get('login', [ANONYMOUS])[0])
    logger.info("Authentication rejected for {}".format(ocvl_user.name))


def auth_problem(url, reason, node=None):
    parsed = parse.urlparse(url)
    ocvl_user.name = str(parse.parse_qs(parsed.query).get('login', [ANONYMOUS])[0])
    logger.info("Authentication rejected for {}".format(ocvl_user.name))


def register_extended_operators():
    if ocvl_auth.ocvl_ext:
        from .extend.extended_operatores import register; register()


def unregister_extended_operators():
    if ocvl_auth.ocvl_ext:
        from .extend.extended_operatores import unregister; unregister()


def auth_make_node_cats_new():
    '''
    this loads the index.md file and converts it to an OrderedDict of node categories.

    '''
    from .auth import DEBUG
    index_path = os.path.join(dirname(__file__), 'index.md')

    node_cats = OrderedDict()
    with open(index_path) as md:
        category = None
        temp_list = []
        for line in md:
            if not line.strip():
                continue
            if line.strip().startswith('>'):
                continue
            elif line.startswith('##'):
                if category:
                    node_cats[category] = temp_list
                category = line[2:].strip()
                temp_list = []

            elif line.strip() == '---':
                temp_list.append(['separator'])
            else:
                bl_idname = line.strip()
                if bl_idname.startswith(OCVL_HIDDEN_NODE_PREFIX) and not DEBUG:
                    continue
                else:
                    bl_idname = bl_idname.replace(OCVL_HIDDEN_NODE_PREFIX, "")
                temp_list.append([bl_idname])

        # final append
        node_cats[category] = temp_list

    return node_cats
