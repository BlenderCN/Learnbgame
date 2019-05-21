# easy-logging
A footage logging system for Blender VSE <br>
Download and manual : easy-logging.net
# What can it do ?
Derushing tons of footage, adding tags, 3-point editing.
# Principle
When you pick a clip from a folder, easy logging brings it to an editing table where you can choose its IN and OUT points and define some tags.
# Where is it ?
In the video sequencer
# List of functions
FROM A NORMAL SEQUENCE
- <b>import clip :</b> imports the clip directly from the file browser to your sequence. If the clip has been logged, it is imported already trimmed.
- <b>edit clip :</b> imports the clip from the file browser to the editing table.
- <b>Local edit :</b> uncheck if you use a dual-screen system. One for the normal sequence, one for the editing table

FROM THE EDITING TABLE
- <b>edit clip :</b> imports the clip from the file browser to the editing table.
- <b>in :</b> defines the starting point of your clip
- <b>out :</b> defines the end point of your clip
- <b>set in&out :</b> defines both in and out accordingly to the length of the active strip
- <b>add tag :</b> adds a tag strip to the clip
- <b>place :</b> places the logged clip back to your main sequence
- <b>as meta :</b> ask for the clip to be packed as a metastrip (in case you added some other element in the editing table)
- <b>back to sequence :</b> brings you back to the main sequence

FROM THE MENU
- <b>Build tag-scenes :</b> Create one scene for each tag with all the related video pieces inside
- <b>Delete the tag-scenes :</b> Remove all the tag-scenes
- <b>Create new log-file</b> Create a new metadata file and keep the current one in a folder located in your root directory

