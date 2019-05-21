'''
OurBricks-Blender

Copyright (c) 2011, Katalabs Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:
 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in
   the documentation and/or other materials provided with the
   distribution.
 * Neither the name of Sirikata nor the names of its contributors may
   be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

bl_info = {
    "name": "OurBricks for Blender",
    "description": "Utilities for interacting with OurBricks within Blender.",
    "author": "Katalabs Inc.",
    "version": (0,0,1),
    "blender": (2, 5, 7),
    "api": 31236, # FIXME what's the right value here?
    "location": "File > Import-Export",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
    import imp

import os
import bpy
try:
    from bpy_extras.io_utils import ImportHelper
except:
    from io_utils import ImportHelper
from bpy.props import CollectionProperty, StringProperty, BoolProperty, FloatProperty

import zipfile, shutil, os.path
import urllib.request, urllib.parse, urllib.error

import xml.dom.minidom
import uuid

AddonDir = os.path.dirname(__file__)
ExternalDir = os.path.join(AddonDir, 'external')
import sys
# Append path for oauth2
sys.path.append( os.path.join(ExternalDir, 'oauth2') )
# and for httplib
sys.path.append(ExternalDir)
# We need to auto-install httplib2 because there isn't a convenient
try:
    import httplib2
except:
    # Grab the archive
    httplib2_zip = os.path.join(ExternalDir, 'httplib2.zip')
    urllib.request.urlretrieve('http://httplib2.googlecode.com/files/httplib2-0.6.0.zip', filename=httplib2_zip)
    # Extract data into a temporary location
    zipdata = zipfile.ZipFile(httplib2_zip)
    zipdata.extractall(path=ExternalDir)
    # Move python3 version into place
    shutil.move( os.path.join(ExternalDir, 'httplib2-0.6.0', 'python3', 'httplib2'), os.path.join(ExternalDir, 'httplib2') )
# And now that we're sure we have httplib2, its safe to get oauth2
import oauth2 as oauth2

import json, webbrowser, time

## Multipart encoding utilities
import mimetypes
def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = b'\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = b''
    for l in L:
        if len(body) > 0:
            body = body + CRLF
        if isinstance(l, str):
            body = body + bytes(l, 'utf-8')
        else:
            body = body + l
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


OurBricksURL = 'http://ourbricks.com'
ActivityURL = OurBricksURL + '/activity?rss'

DataDir = 'ourbricks'
ThumbnailFilename = 'thumbnail.jpg'


# urls for accessing oauth at the service provider
BASE_OURBRICKS_SERVER = 'ourbricks.com'
BASE_OURBRICKS    = 'http://' + BASE_OURBRICKS_SERVER
REQUEST_TOKEN_URL = BASE_OURBRICKS + '/oauth-request-token'
ACCESS_TOKEN_URL  = BASE_OURBRICKS + '/oauth-access-token'
AUTHORIZATION_URL = BASE_OURBRICKS + '/oauth-authorize'
UPLOAD_RESOURCE = '/api/upload'
UPLOAD_URL        = BASE_OURBRICKS + UPLOAD_RESOURCE
UPLOAD_STATUS_URL = BASE_OURBRICKS + '/api/upload-status'
VIEWER_URL        = BASE_OURBRICKS + '/viewer/'

# key and secret granted by the service provider for this consumer application
CONSUMER_KEY = '13e29e79c0ecd44ab4cb9655b843b6bb'
CONSUMER_SECRET = '2b026d2b7643cbdc5e654db867222e32'


bpy.ops.ourbricks = {}

def local_asset_dir(asset_id, prefix=None):
    """
    Computes the local directory for storage related to an asset,
    ensures its available, and returns it.
    """
    temp_dir = DataDir
    if prefix: temp_dir = os.path.join(temp_dir, prefix)
    temp_dir = os.path.join(temp_dir, asset_id)
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)
    return temp_dir


class Asset:
    def __init__(self, asset_id, img_url, zip_url):
        self.id = asset_id
        self.img_url = img_url
        self.zip_url = zip_url

        self._getImage()

    def _dataDir(self):
        return local_asset_dir(self.id)

    def _thumbnailFile(self):
        return os.path.join(self._dataDir(), self.id + '-' + ThumbnailFilename)

    def _textureName(self):
        return 'ourbricks-thumbnail-' + self.id

    def _getImage(self):
        if not os.path.exists(self._thumbnailFile()):
            urllib.request.urlretrieve(self.img_url, filename=self._thumbnailFile(), reporthook=None)
        self.image = bpy.data.images.load(self._thumbnailFile())
        self.texture = bpy.data.textures.new(self._textureName(), type='IMAGE')
        self.texture.image = self.image

def get_listing():
    """
    Get a listing of recent OurBricks uploads. Returns a list Assets.
    """

    result_items = []

    rss_data = urllib.request.urlopen(ActivityURL)
    rss_xml = xml.dom.minidom.parse(rss_data)

    channel = rss_xml.getElementsByTagName('channel')[0]
    items = channel.getElementsByTagName('item')
    for item in items:
        # Most of these are hackish, but a result of using the RSS
        # feed instead of something nicer like a JSON API. This
        # listing method is specifically isolated so we can easily
        # swap out the implementation later.
        asset_id = item.getElementsByTagName('guid')[0].childNodes[0].data.split('/')[-1]
        img_url = item.getElementsByTagName('description')[0].childNodes[0].data
        # Get part after start of img src attribute
        split_href = img_url.split('src="', 1)[1]
        # Get part before closing quote
        img_url = split_href.split('"', 1)[0]
        # FIXME
        zip_url = ''
        result_items.append( Asset(asset_id, img_url, zip_url) )

    return result_items


class OurBricksImport(bpy.types.Operator):

    bl_idname = "import_scene.ourbricks_collada"
    bl_description = 'Import directly from OurBricks COLLADA'
    bl_label = "Import OurBricks"

    def invoke(self, context, event):
        url = context.scene.ourbricks_model_url

        # We piggy back on the standard COLLADA importer
        print('Importing', url)

        # Extract the unique asset id. FIXME this is brittle and
        # should be coming from some other listing, like a real API
        url_parts = url.split('/')
        unique_id_part = url_parts[ url_parts.index('processed')-1 ];

        # Make sure storage area exists.
        #
        # This storage area is necessary because things like textures
        # need to remain on disk. Here we just use a centralized
        # repository and take care to name things nicely.
        import_temp_dir = local_asset_dir(unique_id_part)

        # Grab data
        path = os.path.join(import_temp_dir, 'foo.zip')
        urllib.request.urlretrieve(url, filename=path, reporthook=None)

        # Extract data into a temporary location
        zipdata = zipfile.ZipFile(path)
        zipdata.extractall(path=import_temp_dir)

        # Find the collada file
        daes = [x for x in zipdata.namelist() if x.endswith('.dae')]
        if len(daes) != 1:
            # FIXME present choice in > 1 case, use real exception
            raise RuntimeError("Found zero or more than one dae.")
        dae_path = os.path.join(import_temp_dir, daes[0])

        # Perform the import
        bpy.ops.wm.collada_import(filepath=dae_path)

        return {'FINISHED'}

def save_zip(zip_file, archive_dir):
    """
    Create a zip file out of archive dir. Unlike extraction, python
    doesn't provide this functionality built-in, so we need to iterate
    over the file ourselves to construct the file.
    """
    zipdata = zipfile.ZipFile(zip_file, mode='w')

    for root, dirs, files in os.walk(archive_dir):
        for name in files:
            fname = os.path.join(root, name)
            zipdata.write(fname)
    zipdata.close()

# Global static auth data
request_token = {}
access_token = {}

def do_start_auth():
    global request_token

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    client = oauth2.Client(consumer)

    # Step 1: Get a request token. This is a temporary token that is used for
    # having the user authorize an access token and to sign the request to obtain
    # said access token.

    resp, content = client.request(REQUEST_TOKEN_URL, "GET")
    if resp['status'] != '200':
        raise "Error code: %s" % resp['status']

    request_token_b = dict(urllib.parse.parse_qsl(content))
    request_token = {}
    for k,v in request_token_b.items():
        request_token[ k.decode('utf-8') ] = v.decode('utf-8')

    print("Request Token:")
    print("    - oauth_token        = %s" % request_token['oauth_token'])
    print("    - oauth_token_secret = %s" % request_token['oauth_token_secret'])
    print()

    # Step 2: Redirect to the provider. Since this is a CLI script we do not
    # redirect. In a web application you would redirect the user to the URL
    # below.

    auth_url = "%s?oauth_token=%s" % (AUTHORIZATION_URL, request_token['oauth_token'])
    print("Go to the following link in your browser:")
    print(auth_url)
    print()

    webbrowser.open(auth_url)


def do_finish_auth(pin):
    global request_token
    global access_token

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)

    # After the user has granted access to you, the consumer, the provider will
    # redirect you to whatever URL you have told them to redirect to. You can
    # usually define this in the oauth_callback argument as well.
    oauth_verifier = pin

    # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # URL you can request the access token the user has approved. You use the
    # request token to sign this request. After this is done you throw away the
    # request token and use the access token returned. You should store this
    # access token somewhere safe, like a database, for future use.
    token = oauth2.Token(request_token['oauth_token'],
        request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth2.Client(consumer, token)

    resp, content = client.request(ACCESS_TOKEN_URL, "POST")
    if resp['status'] != '200':
        raise "Error code: %s" % resp['status']

    access_token_b = dict(urllib.parse.parse_qsl(content))
    access_token = {}
    for k,v in access_token_b.items():
        access_token[ k.decode('utf-8') ] = v.decode('utf-8')

    print("Access Token:")
    print("    - oauth_token        = %s" % access_token['oauth_token'])
    print("    - oauth_token_secret = %s" % access_token['oauth_token_secret'])
    print()

def do_upload(zip_file, upload_params):
    global access_token
    token, token_secret = access_token['oauth_token'], access_token['oauth_token_secret']

    # Step 4: We have an access token, so we can issue
    # an upload request on behalf of the user
    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)

    token = oauth2.Token(token, token_secret)

    req = oauth2.Request.from_consumer_and_token(consumer,
                                                 token=token,
                                                 http_method="POST",
                                                 http_url=UPLOAD_URL,
                                                 parameters=upload_params)

    req.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    compiled_postdata = req.to_postdata()
    all_upload_params = urllib.parse.parse_qs(compiled_postdata, keep_blank_values=True)

    #parse_qs returns values as arrays, so convert back to strings
    multipart_fields = []
    for key, val in all_upload_params.items():
        multipart_fields.append( (key, val[0]) )

    multipart_files = []
    for i, fpath in enumerate( [zip_file] ):
        fp = open(fpath, 'rb')
        data = fp.read()
        fp.close()
        multipart_files.append( ('file' + str(i), zip_file, data) )


    try:
        import http.client
        content_type, body = encode_multipart_formdata(multipart_fields, multipart_files)
        headers = {
            'Content-Type': content_type,
            'Content-Length' : str(len(body))
            }
        conn = http.client.HTTPConnection(BASE_OURBRICKS_SERVER)
        conn.request("POST", UPLOAD_RESOURCE, body, headers)
        response = conn.getresponse()
        print(response.status, response.reason)
        respdata = response.read()
        conn.close()
    except:
        print('Exception trying to send http request.')
        return False

    result = json.loads(respdata.decode('utf-8'))
    if result.get('success') != True or 'uploadid' not in result:
        print('Upload failed. Error = ', result.get('error'), file=sys.stderr)
        print(file=sys.stderr)
        return False

    uploadid = result['uploadid']
    print('Succeeded in submitting upload. Upload id = %s Checking status...' % (uploadid,))
    print()

    client = oauth2.Client(consumer, token)

    complete = False
    while not complete:
        resp, content = client.request('%s?uploadid=%s' % (UPLOAD_STATUS_URL, uploadid), "GET")
        if resp['status'] != '200':
            exitprint(resp, content)
        result = json.loads(content.decode('utf-8'))
        if 'complete' not in result:
            exitprint(resp, content)
        complete = result['complete']
        if not(complete == False or complete == True):
            complete = False
        if complete == False:
            print('Not complete. Status = %s' % (result.get('status_message').strip()))
        time.sleep(2)

    asset_url = "%s%s" % (VIEWER_URL, uploadid)

    print()
    print('Finished. Status = %s' % (result.get('status_message'),))
    print()
    print('You can find your upload at: %s' % asset_url)

    webbrowser.open(asset_url)
    return True


class OurBricksStartAuth(bpy.types.Operator):

    bl_idname = "export_scene.ourbricks_auth_start"
    bl_description = 'Start authentication process with OurBricks'
    bl_label = "Start Authentication OurBricks"

    def invoke(self, context, event):
        do_start_auth()
        return {'FINISHED'}

class OurBricksFinishAuth(bpy.types.Operator):

    bl_idname = "export_scene.ourbricks_auth_finish"
    bl_description = 'Finish authentication process with OurBricks'
    bl_label = "Finish Authentication OurBricks"

    def invoke(self, context, event):
        do_finish_auth(pin=context.scene.ourbricks_model_oauth_pin)
        return {'FINISHED'}

class OurBricksExport(bpy.types.Operator):

    bl_idname = "export_scene.ourbricks_collada"
    bl_description = 'Exports directly to OurBricks COLLADA'
    bl_label = "Export OurBricks"

    def invoke(self, context, event):
        # Create a random id
        export_id = uuid.uuid4().hex

        # Create an export directory for this asset
        export_temp_dir = local_asset_dir(export_id, 'export')

        # FIXME name after the scene?
        dae_path = os.path.join(export_temp_dir, 'ourbricks_blender_export.dae')
        # FIXME can pick out the scene by specifying an initial parameter such as
        # {"scene":bpy.data.scenes['scene_to_export']}
        export_status = bpy.ops.wm.collada_export(filepath=dae_path)

        # FIXME handle failures from export_status

        # If blender did its thing, then we should just need to zip up
        # everything under export_temp_dir and pass it along
        zip_path = 'ourbricks_blender_export.zip'
        save_zip(zip_path, export_temp_dir)

        # Now, we should be able to grab the necessary info and perform an upload
        params = {
            'title': context.scene.ourbricks_model_title,
            'description': context.scene.ourbricks_model_description,
            'tags': context.scene.ourbricks_model_tags,
            'author': context.scene.ourbricks_model_author,
            'price': '',
            'license': 'CC Attribution'
            }

        if not do_upload(zip_path, params):
            raise "Upload failed!"

        return {'FINISHED'}

class OurBricksListing(bpy.types.Operator):
    bl_idname = "ourbricks.listing_update"
    bl_description = 'Get recent model listing from OurBricks'
    bl_label = "OurBricks Listing"

    current_listing = []
    current_offset = 0

    def invoke(self, context, event):
        OurBricksListing.current_listing = get_listing()

        return {'FINISHED'}

class OurBricksListingNext(bpy.types.Operator):
    bl_idname = "ourbricks.listing_next"
    bl_description = "Move to the next model in the OurBricks listing"
    bl_label = "OurBricks Listing Next"

    def invoke(self, context, event):
        OurBricksListing.current_offset = (OurBricksListing.current_offset + 1) % len(OurBricksListing.current_listing)
        context.scene.ourbricks_model_url = OurBricksListing.current_listing[OurBricksListing.current_offset].zip_url
        return {'FINISHED'}

class OurBricksListingPrev(bpy.types.Operator):
    bl_idname = "ourbricks.listing_prev"
    bl_description = "Move to the previous model in the OurBricks listing"
    bl_label = "OurBricks Listing Prev"

    def invoke(self, context, event):
        nopts = len(OurBricksListing.current_listing)
        OurBricksListing.current_offset = (OurBricksListing.current_offset + nopts - 1) % nopts
        context.scene.ourbricks_model_url = OurBricksListing.current_listing[OurBricksListing.current_offset].zip_url
        return {'FINISHED'}

class OurBricksBrowserPanel(bpy.types.Panel):
    '''An interface for browsing and importing OurBricks content.'''

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "OurBricks Browser"

    def draw(self, context):
        self.layout.active = True

        box = self.layout.box()
        box.label('Import')
        row = box.row()
        row.prop(context.scene, "ourbricks_model_url")
        row = box.row()
        row.operator("import_scene.ourbricks_collada", text="Import")

        box = self.layout.box()
        box.label('Export')

        row = box.row()
        row.operator("export_scene.ourbricks_auth_start", text="Start Auth")
        row = box.row()
        row.prop(context.scene, "ourbricks_model_oauth_pin")
        row = box.row()
        row.operator("export_scene.ourbricks_auth_finish", text="Finish Auth")

        row = box.row()
        row.prop(context.scene, "ourbricks_model_title")
        row = box.row()
        row.prop(context.scene, "ourbricks_model_description")
        row = box.row()
        row.prop(context.scene, "ourbricks_model_tags")
        row = box.row()
        row.prop(context.scene, "ourbricks_model_author")
        row = box.row()
        row.label('License: CC Attribution') # FIXME Fixed for now, turn into drop down
        row = box.row()
        row.operator("export_scene.ourbricks_collada", text="Export")

        return

        if OurBricksListing.current_listing:
            row = self.layout.row()
            row.template_preview(OurBricksListing.current_listing[OurBricksListing.current_offset].texture)

            row = self.layout.row()
            row.operator("ourbricks.listing_prev", text="Prev")
            row.operator("ourbricks.listing_next", text="Next")

        row = self.layout.row()
        row.operator("ourbricks.listing_update", text="Update Listing")

def register():
    bpy.utils.register_module(__name__)
    # Import
    bpy.types.Scene.ourbricks_model_url = StringProperty(default="", name="URL", description="URL of model to import")
    # Export
    bpy.types.Scene.ourbricks_model_title = StringProperty(default="", name="Title", description="Title for exported model")
    bpy.types.Scene.ourbricks_model_description = StringProperty(default="", name="Description", description="Description for exported model")
    bpy.types.Scene.ourbricks_model_tags = StringProperty(default="", name="Tags", description="Tags for exported model")
    bpy.types.Scene.ourbricks_model_author = StringProperty(default="", name="Author", description="Author for exported model")

    # FIXME hopefully these go away in favor of a full oauth process
    bpy.types.Scene.ourbricks_model_oauth_pin = StringProperty(default="", name="PIN", description="OAuth2 PIN resulting from authorization")


def unregister():
    bpy.utils.unregister_module(__name__)
    # Import
    del bpy.types.Scene.ourbricks_model_url
    # Export
    del bpy.types.Scene.ourbricks_model_title
    del bpy.types.Scene.ourbricks_model_description
    del bpy.types.Scene.ourbricks_model_tags
    del bpy.types.Scene.ourbricks_model_author

    del bpy.types.Scene.ourbricks_model_oauth_pin

if __name__ == "__main__":
    register()
