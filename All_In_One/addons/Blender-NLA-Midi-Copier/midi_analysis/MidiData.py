from .MidiEventDecoder import MidiEventDecoder

from .TrackData import TempoChanges
from .TrackData import TrackData
from .MidiEvents import *


# contains the finalized data after analysis
class MidiData:
    def __init__(self, midiFilename):
        self.eventDecoder = MidiEventDecoder(midiFilename)
        headerData = self.eventDecoder.headerData()
        # variables
        self.format = headerData.formatType
        self.numTracks = headerData.numTracks
        self.isTicksPerBeat = False
        if headerData.ticksPerBeat is None:
            self.isTicksPerBeat = False
            self.ticksPerSecond = (headerData.framesPerSecond *
                                   headerData.ticksPerFrame)
        else:
            self.isTicksPerBeat = True
            self.ticksPerBeat = headerData.ticksPerBeat

        if headerData.formatType != 1:
            raise NotSupportedException("Midi files of format " + str(headerData.formatType)
                                        + " are not supported")

        # maps running total of delta times to microsecondsPerQuarter
        tempoChanges = TempoChanges()
        self.tracks = []

        self.msPerBeat = 500  # default 120 bpm

        # read in each track
        tracknum = 0  # used to create temporary track names
        while self.eventDecoder.hasMoreEvents():
            trackName = "Track" + str(tracknum)
            tracknum += 1
            trackData = TrackData(trackName)
            # should be a track header
            event = self.eventDecoder.nextEvent()
            if not (isinstance(event, TrackHeader)):
                raise UnexpectedEventException(event, TrackHeader())
            # set up tempoChanges
            tempoChanges.reset()
            self.msPerBeat = 500  # default 120 bpm
            deltaTimeTotal = 0
            msTotal = 0  # current time in ms
            # add events
            while not (isinstance(event, EndOfTrackEvent)):
                event = self.eventDecoder.nextEvent()
                if isinstance(event, SetTempoEvent):
                    tempoChanges.addTempoChange(deltaTimeTotal, event.tempo)
                nextTotal = deltaTimeTotal + event.deltaTime
                # calculate absolute start time for event in ms
                if self.isTicksPerBeat:
                    while (tempoChanges.hasMore() and
                                   nextTotal >= tempoChanges.deltaTimeTotal()):
                        msTotal += (
                            (tempoChanges.deltaTimeTotal() - deltaTimeTotal) * self.msPerBeat / self.ticksPerBeat)
                        deltaTimeTotal = tempoChanges.deltaTimeTotal()
                        self.msPerBeat = tempoChanges.usPerQuarter() * .001
                        tempoChanges.findNext()
                    msTotal += ((nextTotal - deltaTimeTotal) * self.msPerBeat / self.ticksPerBeat)
                else:
                    msTotal = (event.deltaTime / self.ticksPerSecond) * .001
                # add event to trackData
                deltaTimeTotal = nextTotal
                event.setStartTime(msTotal)
                trackData.addEvent(event)
            self.tracks.append(trackData)

    def getNumTracks(self):
        return len(self.tracks)

    def getTrack(self, index):
        return self.tracks[index]


class UnexpectedEventException(Exception):
    def __init__(self, event, expectedEvent):
        self.event = event
        self.expectedEvent = expectedEvent

    def __str__(self):
        return str("MidiData expected event of type " + str(type(self.expectedEvent))
                   + ", got event of type " + str(type(self.event)))


class NotSupportedException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
