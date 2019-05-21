bl_info = {
    "name": "Youtube Uploader",
    "author": "Shelby Jueden",
    "version": (0,8),
    "blender": (2,78,0),
    "description": "Uploads a video file to Youtube from the Blender GUI",
    "warning": "Requires install of Google APIs for python",
    "category": "Render",
}

# python
import http.client
import httplib2
import os
import random
import sys
import time
import webbrowser
import threading

# blender
import bpy
from bpy.app.handlers import persistent

# google
from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow 
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# API Info
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, 
    http.client.NotConnected, http.client.IncompleteRead, 
    http.client.ImproperConnectionState, http.client.CannotSendRequest, 
    http.client.CannotSendHeader, http.client.ResponseNotReady,
    http.client.BadStatusLine
)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# Privacy settings for uploaded video
privacy_options = [
    ("public", "Public", "Everyone can see the video", 1),
    ("private", "Private", "Only you can see the video", 2),
    ("unlisted", "Unlisted", "Anyone can see the video with the link", 3),
]  


def get_authenticated_service():
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[__name__].preferences
    flow = OAuth2WebServerFlow(client_id=addon_prefs.client_id,
        client_secret=addon_prefs.client_secret,           
        scope="https://www.googleapis.com/auth/youtube " + \
            "https://www.googleapis.com/auth/youtube.upload " + \
            "https://www.googleapis.com/auth/youtubepartner",
        redirect_uri="http://localhost"
    )

    storage = Storage(bpy.path.abspath("//") + "ytu-oauth2.json")

    credentials = storage.get()

    if credentials is None or credentials.invalid:
        flags = argparser.parse_args(args=[])
        credentials = run_flow(flow, storage, flags)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()))


def initialize_upload(youtube):
    scene = bpy.context.scene
    tags = None

    body=dict(
        snippet=dict(
            title=scene.youtube_upload.video_title,
            description=scene.youtube_upload.video_description,
            tags=tags,
            categoryId=22
        ),
        status=dict(
        privacyStatus=scene.youtube_upload.video_privacy
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(list(body.keys())),
        body=body,
        media_body=MediaFileUpload(
            bpy.path.abspath(scene.youtube_upload.upload_video_path), 
            chunksize=4*1024*1024, 
            resumable=True
	)
    )
    print("Title: %s" % (scene.youtube_upload.video_title))
    resumable_upload(insert_request)


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
    scene = bpy.context.scene
    response = None
    error = None
    retry = 0
    
    # Upload file until response is received
    while response is None:
        try:
            # Upload file chunk
            status, response = insert_request.next_chunk()
            # Use status for progress
            if status:
                # MediaFileUpload chunksize determines the frequency of this
                scene.youtube_upload.upload_progress = status.progress() * 100
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" \
                    % (e.resp.status,e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e
	
	# Handle errors
        if error is not None:
            self.report({'WARNING'}, error)
            error = None
            retry += 1
            if retry > MAX_RETRIES:
                self.report({'ERROR'}, "Out of retries")
                return {'FINISHED'}  
    
	    # Wait semi-random time before retrying upload
            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            time.sleep(sleep_seconds)

    # Check for successful upload
    if 'id' in response:
        scene.youtube_upload.video_id = response['id']
        scene.youtube_upload.upload_progress = 100
    else:
        self.report({'ERROR'}, 
            "The upload failed with an unexpected response: %s" % response
        )
        return {'FINISHED'}  


def upload_begin():
    scene = bpy.context.scene
    scene.youtube_upload.video_upload_progress = 0

    youtube = get_authenticated_service()

    if scene.youtube_upload.upload_file_use_render == True:
        scene.youtube_upload.upload_video_path = scene.render.filepath

    try:
        initialize_upload(youtube)
        upload_thumbnail(youtube)

    except HttpError as e:
        print(("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)))


def upload_thumbnail(youtube):
    scene = bpy.context.scene
    youtube.thumbnails().set(
        videoId=scene.youtube_upload.video_id,
        media_body=bpy.path.abspath(scene.youtube_upload.upload_thumbnail_path)
    ).execute()


# Reset thread count to max when all is selected
def uiupdate(self,context):
    scene = context.scene
    if scene.youtube_upload.upload_file_use_render == True:
        scene.youtube_upload.upload_video_path = scene.render.filepath


class YoutubeKeyLink(bpy.types.Operator):
    '''Open web browser to API key creation guide'''
    bl_idname = "youtube_upload.open_key_link"
    bl_label = "Open page to get API Key"
    bl_options = {'REGISTER'}

    def execute(self, context):
        webbrowser.open(
            'https://developers.google.com/youtube/v3/getting-started'
        )

        privacy_options.append(("fake","Not an option","don't use this",4))
        return {'FINISHED'}   


#class AuthStorage(bpy.types.PropertyGroup):
#    token = bpy.props.StringProperty(name="Auth Token")
#    name = bpy.props.StringProperty(
#        name="Account Name", default="My Youtube Channel")


class YoutubeAddonPreferences(bpy.types.AddonPreferences):
    '''Preferences to store API key and auth tokens'''
    bl_idname = __name__
    
    client_id = bpy.props.StringProperty(name="client_id")
    client_secret = bpy.props.StringProperty(name="client_secret")
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="The API key for YouTube")
        layout.prop(self, "client_id")
        layout.prop(self, "client_secret")
        layout.operator(YoutubeKeyLink.bl_idname)


class YoutubeProperties(bpy.types.PropertyGroup):
    '''Video information for scene'''
    upload_video_path = bpy.props.StringProperty(
        name="Video", subtype="FILE_PATH")
    upload_thumbnail_path = bpy.props.StringProperty(
        name="Thumbnail", subtype="FILE_PATH")
    upload_file_use_render = bpy.props.BoolProperty(
        name="Use Video Render Path", default=True, update=uiupdate)
    upload_progress = bpy.props.FloatProperty(
        name = "Upload Progress", default=0,min=0,max=100,subtype="PERCENTAGE")
    
    video_title = bpy.props.StringProperty(
        name="Title")
    video_description = bpy.props.StringProperty(
        name="Description")
    video_privacy = bpy.props.EnumProperty(
        items=privacy_options, name = "Privacy", default="unlisted")
    video_id = bpy.props.StringProperty(
        name="Video ID", default="")

   
class YoutubePanel(bpy.types.Panel):
    '''Properties panel to configure video information and start upload'''
    bl_idname = "RENDER_PT_youtube_upload"
    bl_label = "Youtube Upload"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        
        scene = context.scene

        self.layout.label(text="File Settings:")
        col = layout.column()
        col.prop(scene.youtube_upload,"upload_file_use_render")
        sub = col.column()
        sub.prop(scene.youtube_upload,"upload_video_path")
        sub.enabled = (not scene.youtube_upload.upload_file_use_render)
        col.prop(scene.youtube_upload,"upload_thumbnail_path")
        
        self.layout.label(text="Video Info:")
        col = layout.column()
        col.prop(scene.youtube_upload,"video_title")
        sub = col.row()
        sub.prop(scene.youtube_upload,"video_description")
        col.prop(scene.youtube_upload,"video_privacy")
        col.prop(scene.youtube_upload,"video_id")
        col = layout.column()
        col.operator(YoutubeUpload.bl_idname)
        col.prop(scene.youtube_upload,"upload_progress")
        
        
class YoutubeUpload(bpy.types.Operator):
    '''Start thread to upload video'''
    bl_idname = "youtube_upload.upload"
    bl_label = "Upload Video"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        print("Start thread...")
        # Upload in thread to prevent locking UI
        t = threading.Thread(target=upload_begin)
        t.start()
        return {'FINISHED'}   


def register():
    bpy.utils.register_class(YoutubeProperties)
    bpy.utils.register_class(YoutubePanel)
    bpy.utils.register_class(YoutubeUpload)
    bpy.utils.register_class(YoutubeKeyLink)
    bpy.utils.register_class(YoutubeAddonPreferences)
    
    bpy.types.Scene.youtube_upload = \
        bpy.props.PointerProperty(type=YoutubeProperties)


def unregister():
    bpy.utils.unregister_class(YoutubeProperties)
    bpy.utils.unregister_class(YoutubePanel)
    bpy.utils.unregister_class(YoutubeUpload)
    bpy.utils.unregister_class(YoutubeKeyLink)
    bpy.utils.unregister_class(YoutubeAddonPreferences)
    
    del bpy.types.Scene.youtube_upload
    
    
if __name__ == "__main__":
    register() 
