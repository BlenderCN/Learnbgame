# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "blue_velvet ::",
    "description": "An exporter of Blender's VSE audio timeline to Ardour",
    "author": "szaszak - http://blendervelvets.org",
    "version": (1, 0, 20160328),
    "blender": (2, 77, 0),
    "warning": "War, children, it's just a shot away.",
    "category": "Learnbgame",
    "location": "File > Export > Ardour (.ardour)",
    "support": "COMMUNITY"}

import bpy
import os

######## ----------------------------------------------------------------------
######## TIMELINE AND SETTINGS FUNCTIONS
######## ----------------------------------------------------------------------


def checkFPS():
    '''Checks project's FPS compatibility with Ardour's FPSs'''
    validFPS = [23.976, 24, 24.975, 25, 29.97, 30, 59.94, 60] # Ardour FPSs
    render = bpy.context.scene.render
    fps = round((render.fps / render.fps_base), 3)

    if fps in validFPS:
        if fps.is_integer():
            fps = int(fps)
            timecode = "timecode_%s" % fps
        else:
            timecode = "timecode_%s" % str(fps).replace(".", "")
    else:
        raise RuntimeError(
            "Framerate \'" + str(fps) + "\' not supported by Ardour."
            "Change to 23.976, 24, 24.975, 25, 29.97, 30, 59.94, 60."
        )
    return fps, timecode


def checkSampleFormat():
    '''Check Sample Format's compatibility with Ardour'''
    sampleFormat = bpy.context.user_preferences.system.audio_sample_format
    if (sampleFormat == "S16"):
        sampleFormat = "FormatInt16"
    elif (sampleFormat == "S24"):
        sampleFormat = "FormatInt24"
    elif (sampleFormat == "FLOAT"):
        sampleFormat = "FormatFloat"
    else:
        raise RuntimeError(
            "Sample Format %s not supported by Ardour. Change Audio "
            "Sample Format to 16, 24 or 32 bits in User Settings."
            % (sampleFormat)
        )

    return sampleFormat


def toSamples(fr, ar, fps):
    '''Transforms SMPTE to Samples'''
    return int(fr * ar / fps)


def getAudioTimeline(ar, fps):
    '''Retrieves all relevant audio information from scene's timeline'''
    timelineSources = []
    timelineRepeated = []
    tracks = []
    idCounter = 0

    path = bpy.path
    validExts = list(path.extensions_audio) + list(path.extensions_movie)

    for i in bpy.context.sequences:
        # Movies with audio such as MOV (h264 + mp3) are read by Blender as:
        # movie_strip.mov (type=='SOUND') and movie_strip.001 (type=='VIDEO').
        # If there is a movie strip with no audio, it will be read as:
        # movie_strip.mov (type=='VIDEO'). Valid tracks are type 'SOUND'.
        if (i.type == "SOUND"):
            start = i.frame_offset_start
            start = toSamples(start, ar, fps)
            position = i.frame_start + i.frame_offset_start - 1
            position = toSamples(position, ar, fps)
            length = i.frame_final_end - (i.frame_start + i.frame_offset_start)
            length = toSamples(length, ar, fps)
            folder, name = os.path.split(i.sound.filepath)

            # the "try/except" below is necessary in case if user has changed
            # the strip's name to "any anything" instead of the original
            # "anything.001" or "anything.wav", the script would fail with the
            # error "ValueError: need more than 1 value to unpack"
            try:
                base_name, ext = i.name.rsplit(".", maxsplit = 1)
            except ValueError:
                base_name = i.name
                foo, ext = name.split(".")

            if (i.channel < 10): # To keep track order: 3 will become 03.
                channel = "0" + str(i.channel)
            else:
                channel = str(i.channel)

            audioData = {'name': base_name + ".wav",
                         'base_name': base_name,
                         'ext': ext,
                         'id': idCounter,
                         'length': length,
                         'origin': i.sound.filepath,
                         'position': position,
                         'sourceID': idCounter,
                         'start': start,
                         'track': "Channel %s" % (channel)
                         }

            if (i.mute):
                audioData['muted'] = 1
            else:
                audioData['muted'] = 0

            if (i.lock):
                audioData['locked'] = 1
            else:
                audioData['locked'] = 0
            
            # Some strips may be no longer in data.sounds but present in
            # Blender's list of sources. This would cause an error when
            # running the script. Files not in data.sounds will be considered
            # as stereo here, but they will not be processed later.
            if (name in bpy.data.sounds) and (bpy.data.sounds[name].use_mono):
                audioData['channels'] = 0
            else:
                audioData['channels'] = 1

            if ("." + ext).lower() in validExts:
                audioData['nExt'] = 1
                audioData['ardour_name'] = "%s.%i" % (audioData['base_name'],
                                                      audioData['nExt'])
                timelineSources.append(audioData)
                idCounter += 1
            else:
                audioData['nExt'] = int(ext)
                audioData['ardour_name'] = "%s.%i" % (audioData['base_name'],
                                                      audioData['nExt'])
                
                # if strip name is foo.003 and the original foo.wav is not on the
                # timeline, this guarantees that foo will go to timelineSources
                # instead of going to timelineRepeated
                if any (d['base_name'] == base_name for d in timelineSources):
                    timelineRepeated.append(audioData)
                else:
                    timelineSources.append(audioData)
                    idCounter += 1

            tracks.append(audioData['track'])

    return timelineSources, timelineRepeated, tracks, idCounter


######## ----------------------------------------------------------------------
######## XML FUNCTIONS
######## ----------------------------------------------------------------------

def createSubElements(el, att):
    '''Creates XML SubElements using a dict of attributes (att)'''
    for key, value in att.items():
        el.set(key, str(value))


def createSubElementsMulti(el, att, count):
    '''Creates XML SubElements using dicts with more
than one attribute (att)'''
    for key, value in att.items():
        el.set(key, str(value[count]))


def valLength(dic):
    '''Returns length of dictionary values'''
    return len(next(iter(dic.values())))


def identXML(element):
    '''Returns a human-readable XML (pretty printing)'''
    return parseString(etree.tostring(element, "UTF-8")).toprettyxml(indent=" ")


def writeXML(outXML, xmlRoot):
    '''Writes XML to file'''
    with open(outXML, 'w') as xmlFile:
        xmlFile.write(identXML(xmlRoot))

######## ----------------------------------------------------------------------
######## SKELETAL XML
######## ----------------------------------------------------------------------


def atSession(audioRate, fileBasename, idCounter):
    '''Attributes for XML Session (root)'''
    atSession = {'event-counter': 0,
                 'id-counter': idCounter,
                 'name': fileBasename,
                 'sample-rate': audioRate,
                 'version': 3001
                 }

    return atSession


def atOption(audiosFolder, sampleFormat, timecode):
    '''Attributes for Config > Options'''
    atOption = {'name': ["audio-search-path", "timecode-format",
                         "use-video-file-fps", "videotimeline-pullup",
                         "native-file-data-format"],
                'value': [audiosFolder, timecode, 0, 0, sampleFormat]
                }

    return atOption


def atLocation(ardourStart, ardourEnd, idCounter):
    '''Attributes for Locations > Location'''
    atLocation = {'end': ardourEnd,
                  'flags': "IsSessionRange",
                  'id': idCounter,
                  'locked': "no",
                  'name': "session",
                  'position-lock-style': "AudioTime",
                  'start': ardourStart
                  }

    return atLocation


def atIO(idCounter):
    '''Attributes for Click > IO'''
    atIO = {'default-type': "audio",
            'direction': "Output",
            'id': idCounter,
            'name': "click",
            'user-latency': 0
            }
    return atIO


def atPort():
    '''Attributes for Click > IO > Port'''
    atPort = {'name': ["click/audio_out 1", "click/audio_out 2"],
              'type': ["audio", "audio"]
              }

    return atPort


def atTempo():
    '''Attributes for TempoMap > Tempo'''
    atTempo = {'beats-per-minute': "120.000000",
               'movable': "no",
               'note-type': "4.000000",
               'start': "1|1|0"
               }

    return atTempo


def atMeter():
    '''Attributes for TempoMap > Meter'''
    atMeter = {'divisions-per-bar': "4.000000",
               'movable': "no",
               'note-type': "4.000000",
               'start': "1|1|0"
               }

    return atMeter


######## ----------------------------------------------------------------------
######## SKELETAL AUDIO TRACK
######## ----------------------------------------------------------------------

def atSource(strip, n_channels):
    '''Attributes for Sources > Source'''
    atSource = {'channel': n_channels,
                'flags': "",
                'id': strip['id'],
                'name': strip['name'],
                'origin': strip['name'],
                'type': "audio"
                }
    return atSource


def atRoute(idCounter, track):
    '''Attributes for Routes > Route'''
    atRoute = {'id': idCounter, # will be the referenced atPlaylist
               'name': track,

               'active': "yes",
               'default-type': "audio",
               'denormal-protection': "no",
               'meter-point': "MeterPostFader",
               'meter-type': "MeterPeak",
               'mode': "Normal",
               'monitoring': "",
               'order-keys': "EditorSort=1:MixerSort=1", # was 0 for mono
               'phase-invert': "00", # Was 0 for mono but seems to work only with 00 for stereo
               'saved-meter-point': "MeterPostFader",
               'self-solo': "no",
               'soloed-by-downstream': 0,
               'soloed-by-upstream': 0,
               'solo-isolated': "no",
               'solo-safe': "no"
               }
    return atRoute


def atPlaylist(idCounter, routeID, track):
    '''Attributes for Playlists > Playlist'''
    atPlaylist = {'id': idCounter,
                  'name': track,
                  'orig-track-id': routeID, # generic id of atRoute

                  'combine-ops': 0,
                  'frozen': "no",
                  'type': "audio"
                  }
    return atPlaylist


def atRouteIO(idCounter, track):
    '''Attributes for Routes > Route > IO'''
    atRouteIO = {'id': [idCounter, idCounter],
                 'name': [track, track],

                 'default-type': ["audio", "audio"],
                 'direction': ["Input", "Output"],
                 'user-latency': [0, 0]
                 }
    return atRouteIO


def atRouteIOPort(track):
    '''Attributes for Routes > Route > IO > Port'''
    atRouteIOPort = {'name': [track+"/audio_in 1", track+"/audio_out 1"],
                     'type': ["audio", "audio"]
                     }
    return atRouteIOPort


def atRouteIOPort2(track):
    '''Attributes for Routes > Route > IO > Port'''
    atRouteIOPort2 = {'name': [track+"/audio_in 2", track+"/audio_out 2"],
                     'type': ["audio", "audio"]
                     }
    return atRouteIOPort2


def atDiskstream(idCounter, track):
    '''Attributes for Routes > Route > Diskstream'''
    atDiskstream = {'channels': 2, # 1 for mono file
                    'id': idCounter,
                    'name': track,
                    'playlist': track,

                    'capture-alignment': "Automatic",
                    'flags': "Recordable",
                    'speed': "1.000000"
                    }
    return atDiskstream


def atPlaylistRegion(idCounter, strip):
    '''Attributes for Playlists > Playlist > Region'''
    atPlaylistRegion = {'channels': strip['channels'] + 1, # mono file
                        'id': idCounter,
                        'length': strip['length'],
                        'locked': strip['locked'],
                        'master-source-0': strip['sourceID'], # atSource's id
                        'muted': strip['muted'],
                        'name': strip['ardour_name'],
                        'position': strip['position'],
                        'source-0': strip['sourceID'],
                        'start': strip['start'],

                        'ancestral-length': 0,
                        'ancestral-start': 0,
                        'automatic': 0,
                        'default-fade-in': 0,
                        'default-fade-out': 0,
                        'envelope-active': 0,
                        'external': 1, # audios not in ardour sources folder?
                        'fade-in-active': 1,
                        'fade-out-active': 1,
                        'first-edit': "nothing",
                        'hidden': 0,
                        'import': 0,
                        'layering-index': 0,
                        'left-of-split': 0,
                        'opaque': 1,
                        'position-locked': 0,
                        'positional-lock-style': "AudioTime",
                        'right-of-split': 0,
                        'scale-amplitude': 1,
                        'shift': 1,
                        'stretch': 1,
                        'sync-marked': 0,
                        'sync-position': 0,
                        'type': "audio",
                        'valid-transients': 0,
                        'video-locked': 0,
                        'whole-file': 0
                        }
                        
    if (strip['channels'] == 1):
        atPlaylistRegion['master-source-1'] = strip['master-source-1']
        atPlaylistRegion['source-1'] = strip['source-1']
        
    return atPlaylistRegion


######## ----------------------------------------------------------------------
######## CREATE AUDIO TRACK
######## ----------------------------------------------------------------------

def createAudioSources(Session, strip, n_channels=0):
    '''Creates audio sources in XML'''
    Source = SubElement(Session[2], "Source")
    createSubElements(Source, atSource(strip, n_channels))


def createPlaylists(Session, idCount, track):
    '''Creates Playlists (tracks) in the XML;
    in Blender, they are the Channels'''
    Route = SubElement(Session[6], "Route")
    createSubElements(Route, atRoute(idCount, track))
    routeID = idCount
    idCount += 1

    Playlist = SubElement(Session[7], "Playlist")
    createSubElements(Playlist, atPlaylist(idCount, routeID, track))
    # routeID comes from atRoute
    idCount += 1

    RouteIO = ""
    RouteIOPort = ""
    for counter in range(valLength(atRouteIO(idCount, track))):
        RouteIO = SubElement(Route, "IO")
        RouteIOPort = SubElement(RouteIO, "Port")

        createSubElementsMulti(RouteIO, atRouteIO(idCount, track), counter)
        idCount += 1

        createSubElementsMulti(RouteIOPort, atRouteIOPort(track), counter)
        RouteIOPort2 = SubElement(RouteIO, "Port")
        createSubElementsMulti(RouteIOPort2, atRouteIOPort2(track), counter)

    Diskstream = SubElement(Route, "Diskstream")
    createSubElements(Diskstream, atDiskstream(idCount, track))
    idCount += 1

    global idCounter
    idCounter = idCount


def createPlaylistRegions(Session, idCount, strip, track):
    '''Creates the Playlists' Regions in the XML;
    in Blender, these are the strips'''
    PlaylistRegion = SubElement(Session[7][track], "Region")
    createSubElements(PlaylistRegion, atPlaylistRegion(idCount, strip))
    idCount += 1

    global idCounter
    idCounter = idCount


######## ----------------------------------------------------------------------
######## CREATE XML
######## ----------------------------------------------------------------------

import xml.etree.ElementTree as etree
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.dom.minidom import parseString


def createXML(sources, startFrame, endFrame, fps, timecode, audioRate,
              ardourBasename, audiosFolder):
    '''Creates full Ardour XML to be written to a file'''
    global idCounter
    sources, repeated, tracks, idCounter = getAudioTimeline(audioRate, fps)
    tracks = sorted(set(tracks))[::-1]
    sampleFormat = checkSampleFormat()
    ardourStart = toSamples((startFrame-1), audioRate, fps)
    ardourEnd = toSamples((endFrame-1), audioRate, fps)

    ######## ------------------------------------------------------------------
    ######## STATIC XML SECTIONS
    ######## ------------------------------------------------------------------

    Session = Element("Session") # XML root = Session
    tree = ElementTree(Session)

    # Create Session Elements + Attributes
    xmlSections = ["Config", "Metadata", "Sources", "Regions", "Locations",
                   "Bundles", "Routes", "Playlists", "UnusedPlaylists",
                   "RouteGroups", "Click", "Speakers", "TempoMap",
                   "ControlProtocols", "Extra"]

    for section in xmlSections:
        Session.append(Element(section))

    # Create Option, IO, Tempo and Meter + Attributes
    for counter in range(valLength(atOption(audiosFolder, sampleFormat, timecode))):
        Option = SubElement(Session[0], "Option") # Session > Config > Option
        createSubElementsMulti(Option, atOption(audiosFolder, sampleFormat,
                                                timecode), counter)

    Location = SubElement(Session[4], "Location") # Session > Locations > Location
    IO = SubElement(Session[10], "IO") # Session > Click > IO
    Tempo = SubElement(Session[12], "Tempo") # Session > TempoMap > Tempo
    Meter = SubElement(Session[12], "Meter") # Session > TempoMap > Meter

    createSubElements(Session, atSession(audioRate, ardourBasename, idCounter))
    createSubElements(Location, atLocation(ardourStart, ardourEnd, idCounter))
    idCounter += 1
    createSubElements(IO, atIO(idCounter))
    idCounter += 1
    createSubElements(Tempo, atTempo())
    createSubElements(Meter, atMeter())

    Port = ""
    for counter in range(valLength(atPort())):
        Port = SubElement(IO, "Port") # Session > Click > IO > Port
        createSubElementsMulti(Port, atPort(), counter)

    ######## ------------------------------------------------------------------
    ######## DYNAMIC XML SECTIONS
    ######## ------------------------------------------------------------------

    # create sources and sources' regions
    for source in sources:
        createAudioSources(Session, source)

    # create another sources' entry for stereo files
    stereoSources = []
    for source in sources:
        if (source['channels'] == 1):
            source['id'] = int(source['id'] + idCounter)
            createAudioSources(Session, source, 1)
            stereoSources.append(source)
            idCounter += 1

    # create playlists (tracks)
    for track in tracks:
        createPlaylists(Session, idCounter, track)

    # correct reference to master-source-0 and source-0 in repeated audios
    for rep in repeated:
        for sour in sources:
            if (rep['name'] == sour['name']):
                rep['sourceID'] = sour['id']

    # create playlists regions (timeline)
    for audio in (sources + repeated):
        track = tracks.index(audio['track'])
        if (audio['channels'] == 0):
            createPlaylistRegions(Session, idCounter, audio, track)
        else:
            for stereos in stereoSources:
                if (audio['name'] == stereos['name']):
                    audio['master-source-1'] = stereos['id']
                    audio['source-1'] = stereos['id']
                    createPlaylistRegions(Session, idCounter, audio, track)

    Session.set('id-counter', str(idCounter))

    return Session, sources

######## ----------------------------------------------------------------------
######## RUN FFMPEG
######## ----------------------------------------------------------------------

from shutil import which
from subprocess import call


def runFFMPEG(ffCommand, sources, audioRate, outputFolder):
    if not os.path.exists(ffCommand):
        raise RuntimeError(
            "You don't seem to have FFMPEG on your system. Either"
            " install it or point to it at the addon preferences."
        )

    if (os.path.exists(outputFolder) is False):
        os.mkdir(outputFolder)

    for source in sources:
        basename, ext = os.path.splitext(source['name'])

        input = source['origin']
        if (input.startswith("//")):
            input = input.replace("//", "")

        audioChannels = source['channels'] + 1
        output = outputFolder + os.sep + basename + ".wav"

        # Due to spaces, the command entries (ffCommand, input and output) have
        # to be read as strings by the call command, thus the escapings below
        callFFMPEG = "\"%s\" -i \"%s\" -y -vn -ar %i -ac \"%s\" \"%s\"" \
                     % (ffCommand, input, audioRate, audioChannels, output)
        print(callFFMPEG)
        call(callFFMPEG, shell=True)

    return {'FINISHED'}

######## ----------------------------------------------------------------------
######## EXPORT TO ARDOUR
######## ----------------------------------------------------------------------

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty


class ExportArdour(bpy.types.Operator, ExportHelper):
    """Export audio timeline (including audios from videos) to Ardour"""
    bl_idname = "export.ardour"
    bl_label = "Export to Ardour"
    filename_ext = ".ardour"
    filter_glob = StringProperty(default="*.ardour", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        if bpy.context.sequences:
            return context.sequences is not None

    def execute(self, context):
        bpy.ops.file.make_paths_absolute()

        scene = bpy.context.scene
        startFrame = scene.frame_start
        endFrame = scene.frame_end
        fps, timecode = checkFPS()

        preferences = bpy.context.user_preferences
        system = preferences.system
        audioRate = int(system.audio_sample_rate.split("_")[1])

        audiosFolderPath, ardourFile = os.path.split(self.filepath)
        ardourBasename = os.path.splitext(ardourFile)[0]
        audiosFolder = audiosFolderPath + os.sep + "Audios_for_" + ardourBasename

        sources = []
        Session, sources = createXML(sources, startFrame, endFrame, fps,
                                     timecode, audioRate, ardourBasename,
                                     audiosFolder)

        ffCommand = preferences.addons['blue_velvet'].preferences.ffCommand
        runFFMPEG(ffCommand, sources, audioRate, audiosFolder)

        writeXML(self.filepath, Session)

        return {'FINISHED'}


class Blue_Velvet_Ardour_Exporter(bpy.types.AddonPreferences):
    bl_idname = __name__.split(".")[0]
    bl_option = {'REGISTER'}

    if which('ffmpeg') is not None:
        ffmpeg = which('ffmpeg')
    else:
        ffmpeg = "/usr/bin/ffmpeg"

    ffCommand = StringProperty(
        name="Path to FFMPEG binary or executable",
        description="If you have a local FFMPEG, change this path",
        subtype='FILE_PATH',
        default=ffmpeg,
    )

    def draw(self, context):
    
        layout = self.layout
        layout.label(text="The path below *must* be absolute. If you have to "
                          "change it, do so with no .blend files open or "
                          "they will be relative.")
        layout.prop(self, "ffCommand")


def menuEntry(self, context):
    self.layout.operator(ExportArdour.bl_idname, text="Ardour (.ardour)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menuEntry)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menuEntry)


if __name__ == "__main__":
    register()
