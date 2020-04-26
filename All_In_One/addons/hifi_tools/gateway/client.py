import bpy
import json
from urllib.parse import urlencode, urlparse
import http.client
from http.client import HTTPException
import uuid
import os
import mimetypes

# TODO: Better way would be to use stuff like requests. but finding a way to automate installation  for the blender plugin would be good to have
# Unfortunately, BLender doenst support pip natively, so anyone installing would have to follow some very convoluted steps just to install the plugin

# Thus, doing is by hand.

#    "new_user": "/new",
#    "asset_upload": "/upload",
#    "uploads": "/uploads"

# multipart code by rhoit
# https://gist.github.com/rhoit/9573c40feaeb3cf44b4a8544dc0ae2a1


def multipart_encoder(params, files):
    boundry = uuid.uuid4().hex
    lines = list()
    for key, val in params.items():
        if val is None:
            continue
        lines.append('--' + boundry)
        lines.append('Content-Disposition: form-data; name="%s"' % key)
        lines.extend(['', val])

    for key, uri in files.items():
        name = bpy.path.basename(uri)
        mime = mimetypes.guess_type(uri)[0] or 'application/octet-stream'

        lines.append('--' + boundry)
        lines.append(
            'Content-Disposition: form-data; name="{0}"; filename="{1}"'.format(key, name))
        lines.append('Content-Type: ' + mime)
        lines.append('')
        lines.append(open(uri, 'rb').read())

    lines.append('--%s--' % boundry)

    body = bytes()
    for l in lines:
        if isinstance(l, bytes):
            body += l + b'\r\n'
        else:
            body += bytes(l, encoding='utf8') + b'\r\n'

    headers = {
        'Content-Type': 'multipart/form-data; boundary=' + boundry,
    }

    return headers, body


def upload(server, username, token, filename, file):
    print("Connecting to Server")
    route = routes(server)
    data = None
    connection = _form_connect(server)
    try:
        connection.connect()
        print("Connection Established...")
        headers, body = multipart_encoder(
            {"username": username, "token": token}, {"file": file})

        print("Sending Request",
              route["asset_upload"], " This may take a while.")
        connection.request("POST", route["asset_upload"], body, headers)

        res = connection.getresponse()
        data = res.read()
        print("Response:")
        print(data)
    except HTTPException as e:
        print("HttpException Occurred", e)
    finally:
        connection.close()

    return data.decode("utf-8")


def new_token(server, username):
    # TODO Probabably make failure cases too?
    route = routes(server)

    if route is None:
        return ("Err", "Could not get routes to server! server is probably down")

    result = json.loads(_basic_connect(
        server, route["new_user"], "POST", username))

    if "error" in result.keys():
        return ("Err", result["error"])

    if "secret" in result.keys():
        return ("Success", result["secret"])

    return ("Err", " No conditions met, contact maintainer")


def new_token_oauth(server, username, oauth):
    route = routes(server)

    if route is None:
        return ("Err", "Could not get routes to server! server is probably down")

    result = json.loads(_basic_connect(
        server, route["new_user"], "POST", username, None, oauth))

    if "error" in result.keys():
        return ("Err", result["error"])

    if "secret" in result.keys():
        return ("Success", result["secret"])

    return ("Err", " No conditions met, contact maintainer")

    

def routes(server):
    print("Getting routes for the plugin from server.")
    return json.loads(_basic_connect(server, '/plugin_routes'))


def _form_connect(server):
    if(server.find("https://") != -1):
        return http.client.HTTPSConnection(server.replace("https://", ""))
    else:
        return http.client.HTTPConnection(server.replace("http://", ""))


def _basic_connect(server, path, method="GET", username=None, token=None, oauth=None):
    connection = _form_connect(server)
    data = None

    try:
        connection.connect()
        if username is None and token is None:
            connection.request(method, path)
        else:
            body = {}
            # Make a map to format instead of username token etc.
            if username is not None:
                body['username'] = username

            if token is not None:
                body['token'] = token
                
            if oauth is not None:
                body['oauth'] = oauth

            connection.request(
                method, path, urlencode(body), {"Content-Type": 'application/x-www-form-urlencoded'})

        res = connection.getresponse()
        data = res.read()

    except HTTPException as e:
        print("HttpException Occurred", e)
        # TODO: Should probably throw Exception here.
        return None
    finally:
        connection.close()

    return data.decode("utf-8")
