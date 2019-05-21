bl_info = {
	"name": "Discord Rich Presence",
	"description": "Adds Rich Presence support to Blender",
	"author": "@AlexApps#9295, @lvxejay#9771",
	"version": (0, 1),
	"blender": (2, 79, 0),
	"location": "",
	"warning": "Extremely Unstable - Still in development!",
	"wiki_url": "https://github.com/AlexApps99/blender-rich-presence/wiki",
	"tracker_url": "https://github.com/AlexApps99/blender-rich-presence/issues",
	"support": "COMMUNITY",
	"category": "System"
	}
import rpc
import time
import bpy
import threading

def register():
	print('Placeholder')
def unregister():
	print('Placeholder')

client_id = '434079082339106827'
rpc_obj = rpc.DiscordIpcClient.for_platform(client_id)
time.sleep(5)
start_time = time.time()
filename = 'test.blend'
version_no = '2.79'

def updatePresence():
	threading.Timer(30, updatePresence).start()
	
	activity = {
		"details": "Using Blender " + version_no,
		"state": "Working on " + filename,
		"timestamps": {
			"start": start_time
		},
		"assets": {
			"small_text": "Blender " + version_no,
			"small_image": "blender_logo",
			"large_text": filename,
			"large_image": "pretty_render"
		}
	}
	rpc_obj.set_activity(activity)
	
updatePresence()
