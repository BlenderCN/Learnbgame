# -----------------------------------------------------------------------------
# Blender Tips - Addon for daily blender tips
# Developed by Patrick W. Crawford
#

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

import bpy
import threading
import urllib.request
import urllib
import http.client
import json
import sys, os # for error handling
from datetime import datetime

from . import conf
from . import BDT_ui


# -----------------------------------------------------------------------------
# Requests
# -----------------------------------------------------------------------------



def bdt_fetch_tips():
	"""Function that generates all requests, runs in async"""

	# context even needed?

	# first, get the list of subscribed tips from preferences
	addon_prefs = bpy.context.user_preferences.addons[__package__].preferences

	tips = []

	# Each subscription tip type has the format:
	# {"title":title,"description":desc,"date":date,"thumb":tmb_path,"url":url}

	# consider doing threads even for each of these linear-requests
	if addon_prefs.tips_database==True:
		# also wrap in a try/catch
		# also if none in the DB, get direct from source where possible
		# (and the update the DB)

		res,e = fetch_database()
		if res!=None:
			tips.append(res)
			if conf.jsn["subscribed_check_cache"]=="":
				conf.jsn["subscribed_check_cache"] = {}
			conf.jsn["subscribed_check_cache"]["database"] = res
		else:
			if conf.jsn["subscribed_check_cache"]=="":
				conf.jsn["subscribed_check_cache"] = {}
			conf.jsn["subscribed_check_cache"]["database"] = None
		if e!=None:
			# some kind of error occured
			print("BDT - Error on fetching database: ",str(e))

	
	if addon_prefs.tips_yanal_sosak==True:
		# also wrap in a try/catch
		res,e = fetch_yanal_sosak()
		if res!=None:
			tips.append(res)
			if conf.jsn["subscribed_check_cache"]=="":
				conf.jsn["subscribed_check_cache"] = {}
			conf.jsn["subscribed_check_cache"]["yanal_sosak"] = res
		else:
			if conf.jsn["subscribed_check_cache"]=="":
				conf.jsn["subscribed_check_cache"] = {}
			conf.jsn["subscribed_check_cache"]["yanal_sosak"] = None
			print("No tips found from Yanal")
		if e!=None:
			# some kind of error occured
			print("BDT - Error on fetching Yanal Sosak: ",str(e))

	# potential other: http://www.blenderskool.cf/blender-tips/
	# but currently inactive.

	# eventually my auto, auto-peer based model?
	# e.g. check first against databse is any applied for today,
	# if none, then search for tips on twtter/G+/etc, 
	# and allow admin to manual override tip.

	# should also verify against FB whether a tip if still daily
	# active or not (but still display most recent)

	print("Finished gathering tips: ")
	print(tips)

	# update the conf jsn values
	conf.jsn["last_check"] = str(datetime.now()).split(".")[0]

	if len(tips) == 0:
		conf.error = ({"ERROR"},"No available tips found, see console for more info")

	BDT_ui.addResponseHandler()
	## call function for adding to handler??? in ui code



def fetch_database():
	# source to parse:
	# www.TheDuckCow.com
	return None,"Not implemented yet"


def fetch_yanal_sosak():

	# Static playlsit URL for this source
	yt_playlist_id = "PLvPwLecDlWRCaTVFs7Tx_1Mz8EDd0S8_5"

	# Used to run commands
	yt_data3_key = fetch_yt_devkey()
	if yt_data3_key==None: return None, "Failed to get yt key"

	yt_playlist_contents = []
	countout = 0
	nextPageToken = "" # for getting subsequent pages
	yt_playbase = "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId="

	# loop through all pages of playlsit, chopped into sets of 50-videos per page
	while countout<5: # update to like 25 or something eventually
		countout +=1
		yt_playlist_url = "{}{}{}&key={}".format(
				yt_playbase,yt_playlist_id,nextPageToken,yt_data3_key)		
		print("Requesting playlist pg{}, url: {}".format(
				countout,yt_playlist_url))

		res,err = get_request_raw(yt_playlist_url)
		
		if res==None:
			print("BDT - Error requesting playlist:")
			print(err)
			return None,err
		elif "items" in res and len(res["items"])>0:
			[yt_playlist_contents.append(itm["contentDetails"]) for itm in res["items"] ]
			if "nextPageToken" not in res or res["nextPageToken"]=="":
				nextPageToken = ""
				countout = 999
				break
			else:
				nextPageToken = "&pageToken="+res["nextPageToken"]
		else:
			print("BDT - items not found in request")
			return None,err

	# next, get the last video's ID 
	# (eventually, be able to select which index to get old tips)
	#conf.jsn["subscribed_check_cache"]["yanal_sosak"] = yt_playlist_contents
	#conf.jsn_save()

	# now get details of the video of interest
	# each of these even could be threaded for multiple image downloads
	def get_yt_video_info(yt_vid):
		baseurl = "https://www.googleapis.com/youtube/v3/videos?id="
		url = "{}{}&part=snippet&key={}".format(baseurl,yt_vid,fetch_yt_devkey())

		# first request, the data link itself
		res,err = get_request_raw(url)
		# print("VIDEO SPECIFIC CONTENT FOUND:")
		# print(res)
		if res==None:
			print("BDT - Error requesting playlist:")
			print(err)
			return None,err
		elif "items" in res and len(res["items"])>0:
			desc = res["items"][0]["snippet"]["description"]
			date = res["items"][0]["snippet"]["publishedAt"]
			title = res["items"][0]["snippet"]["title"]
			vid_url = "http://youtube.com/watch?v="+str(yt_vid)
		else:
			print("BDT - Did not receive expected data for video")
			print(res)
			return None,"Did not receive expected data for video"

		if conf.use_icons==False:
			print("Not using icons")
		else:
			print("Now to fetch the thumbnail")


			# only need this to get description/title/date
			# as we now know the icon download is, eg,
			yt_vidthumb_thumb = "https://i.ytimg.com/vi/{x}/mqdefault.jpg".format(x=yt_vid)
			# HQ, option
			#yt_vidthumb_img = "https://i.ytimg.com/vi/{x}/maxresdefault.jpg".format(x=yt_vid)

			# downlaod thumb by first seeing if it's locally there
			thmb = "ytthumb_"+yt_vid+"_"+yt_vidthumb_thumb.split("/")[-1]
			src = os.path.dirname(os.path.abspath(__file__))
			tmb_path = os.path.join(src,"icon_cache",thmb)
			
			if os.path.isfile(tmb_path)==False:
				try:
					urllib.request.urlretrieve(yt_vidthumb_thumb, tmb_path)
				except Exception as e:
					print("BDT encountered an error downloading thumbnail")
					print(str(e))
					tmb_path = None
			else:
				if conf.verbose:
					print("BDT - skipped thumb {x} download, already local".format(
						x=yt_vid))

		# limit description length to some reasonable number of characters
		if len(desc)>2000:
			desc = desc[:497]+"..."

		ret = {"title":title,"description":desc,"date":date,
				"thumb":tmb_path,"url":vid_url,
				"website":"https://www.youtube.com/playlist?list=PLvPwLecDlWRCaTVFs7Tx_1Mz8EDd0S8_5"}
		return ret,None


	# now, finally run the above code to get latest tip
	yt_vid = yt_playlist_contents[-1]["videoId"] # error prone? check for "videoId"
	ret, err = get_yt_video_info(yt_vid)
	if ret != None:
		print("VIDEO DETAILS: ",ret)
		return ret, err
	else:
		return None, "No video details returned"


def fetch_yt_devkey():
	# remotely grab the key for downloading youtube playlist/video info
	global ytdevkey
	if ytdevkey != None:return ytdevkey

	res,err = db_request("GET", "/v1/keys/ytkey.json", None)
	if err!=None:
		print("Error occured fetching keys")
		print(str(err))
	if res == None:
		print("No keys returned, failed attempt")
	else:
		print("Found key")
		ytdevkey = res

	return ytdevkey



# all API calls to base url
def get_request_raw(url):
	# returns: result, error
	request = urllib.request.Request(url)
	try:
		result = urllib.request.urlopen(request)
	except urllib.error.HTTPError as e:
		_error = "HTTP error with url: "+url
		_error_msg = str(e.code)
		print(_error)
		return None,"URL error, check internet connection. "+str(e)
	except urllib.error.URLError as e:
		_error = "URL error, check internet connection "+url
		_error_msg = str(e.reason)
		print(_error)
		return None,"URL error, check internet connection. "+str(e)
	else:
		result_string = result.read()
		result.close()

		# now
		try:
			tmp = json.loads(result_string.decode())
		except Exception as e:
			print("BDT - Exception, request url completed but failed to convert json; url: "+url)
			return None,"URL retreive json conversion error, "+str(e)

		return tmp,None



# raw request, may be in background thread or main
def db_request(method, path, payload, callback=None, port=443):
	url = conf.db_url

	connection = http.client.HTTPSConnection(url, port)
	try:
		connection.connect()
	except:
		print("Connection not made, verify connectivity")
		return None, 'NO_CONNECTION'

	if method=="POST" or method=="PUT":
		connection.request(method, path, payload)
	elif method == "GET": # GET
		connection.request(method, path)
	else:
		raise ValueError("raw_request input must be GET, POST, or PUT")

	raw = connection.getresponse().read()
	resp = json.loads( raw.decode() )
	if conf.verbose:print("Response: "+str(resp))	

	if callback != None:
		if conf.verbose:print("Running callback")
		callback(resp)

	return resp,None


# -----------------------------------------------------------------------------
# ASYNC SETUP
# -----------------------------------------------------------------------------

# Launch a generic, self-terminating background thread
# func = the main function of this background loop
# arguments = tuple of function inputs
# returns true if thread started without issue
# (this is NOT related to whether the thread raises an error or not)
def launch_background_thread(func, arguments=None):
	if conf.async_progress != None:
		# avoid overlapping requests
		return
	if conf.verbose: print("BDT - Starting background thread")

	if arguments == None:
		arguments = ()

	argwrap = (func, arguments)

	new_thread = threading.Thread(target=thread_starter_func,args=argwrap)
	new_thread.daemon = True

	# protect starting of a thread, pass to UI if failed
	# note: this is only for starting a thread, not capturing
	# if the function itself err's out
	try:
		new_thread.start()
	except Exception as e:
		print("BDT - exception starting thread:")
		print(str(e))
		return str(e)
	
	return True


def check_tip_async_uidraw():
	addon_prefs = bpy.context.user_preferences.addons[__package__].preferences
	if addon_prefs.auto_show_tips!=True or conf.auto_once!=False:
		return
	elif conf.async_progress == True:
		return
	else:
		# silent background starting
		conf.auto_once = True
		print("LAUNCHED BG VIA async_UIDRAW")
		res = launch_background_thread(bdt_fetch_tips)


def check_tip_async(self,context):

	if conf.async_progress == True:
		# check for tips already in progress
		return ({"INFO"},"Please wait, still checking for tips...")
	elif conf.async_progress == False:
		# this shouldn't ever occur, but just in case
		conf.async_progress = None
		return ({"ERROR"},"Error occured: "+str(res))
	else:
		# normal course
		# consider starting two threads? 
		# one being a timeout and the other the actual thread
		# (timeout popup that is)

		print("LAUNCHED ASYNC VIA TIP_ASYNC NORMAL")
		res = launch_background_thread(bdt_fetch_tips)
		if res == True:
			return ({"INFO"},"Checking for tips, please wait...")
		else:
			return ({"ERROR"},"Error occured: "+str(res))


def thread_starter_func(func,args):
	# run the function requested in a safe wrapper

	conf.async_progress = True
	if conf.failsafe==False:
		print("PRINTING BG ARGS")
		print(args)
		func(*args)
		conf.async_progress = None
	else:
		try:
			print("PRINTING BG ARGS")
			print(args)
			func(*args)
			conf.async_progress = None
			# callback handler is built in to args

		except Exception as e:
			print("BDT - Background thead exception:")
			print("\t"+str(e))
			conf.async_progress = None
			conf.error = ({"ERROR"},"Exception occured: "+str(e))

			#exc_type, exc_obj, exc_tb = sys.exc_info()
			#fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			#print(exc_type, fname, exc_tb.tb_lineno)

			# throw on handler there was an error
			BDT_ui.addResponseHandler()



def register():
	global ytdevkey
	ytdevkey = None # key for youtube api


def unregister():
	pass


