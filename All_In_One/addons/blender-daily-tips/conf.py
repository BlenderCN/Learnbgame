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
# Global variabls
# -----------------------------------------------------------------------------

import os
import json

def jsn_save():
	global jsn
	if verbose:print("BDT - Saving json file")
	print(jsn)
	json_path = os.path.join(os.path.dirname(__file__),"tip_cache.json")

	if jsn == None or jsn == {}:
		jsn_clear()

	outf = open(json_path,'w')
	data_out = json.dumps(jsn,indent=4)
	outf.write(data_out)
	outf.close()

	#with open(json_path, 'w') as outfile:
	#		json.dumps(jsn, outfile, indent=4)


def jsn_clear():
	global jsn
	jsn = {
		"checked_tip":"",
		"last_check":"",
		"subscribed_check_cache":""
	}

def latest():
	if jsn == None or jsn == {}:
		jsn_clear()
	if jsn["last_check"] == "":
		return "None"
	else:
		return str(jsn["last_check"])


def register():

	# for extra printing out and logging
	global verbose
	verbose = True

	global dev
	dev = True # set false for production

	global failsafe
	failsafe = not dev

	# ensure auto-check for tip happens at most once per blender session
	global auto_once
	auto_once = False

	global async_progress
	# None: no request in progress
	# False: Halt the ongoing thread immediately (if possible)
	# True: Request is in progress
	async_progress = None


	# for persistant local data storage
	# initialize json structure, for reference
	global jsn
	jsn_clear()

	# if json is found, load the file
	json_path = os.path.join(os.path.dirname(__file__),"tip_cache.json")
	if os.path.isfile( json_path ) == False:
		print("Blender tips warning: no tip_cache file found")
		# save out a file automatically
		jsn_save()
	else:
		with open(json_path) as data_file:
			jsn = json.load(data_file)

	# url for project database access
	global db_url
	db_url = "blender-daily-tips.firebaseio.com"

	global error
	error = () # format: ({"info"},"")

	# icon usage

	global use_icons
	try: # We only need to check this once here, so it can now be removed from e.g. UI etc.
		import bpy.utils.previews
		use_icons = True
	except:
		use_icons = False

	global preview_collections
	preview_collections = {}
	global thumb_ids # necessary, if name-based?
	thumb_ids = {}



def unregister():
	pass

