from .MidiParser import MidiParser
from .MidiEvents import *
from .Util import Util


# decodes data from the MidiParser into data easier to work with in MidiData
# (will decode each piece of data from midiParser into an event,
# including header chunk pieces)
class MidiEventDecoder:
    def __init__(self, midiFilename):
        self.midiParser = MidiParser(midiFilename)
        self.runningStatus = False
        self.lastChannelStatusByte = None  # the first byte of the last channel event that didn't use running status
        return

    def hasMoreEvents(self):
        return self.midiParser.hasMoreData()

    # be sure to call this once before calling nextEvent
    def headerData(self):
        data = HeaderData()
        data.setFromBytes(self.midiParser.readNextData(),
                          self.midiParser.readNextData())
        return data

    # returns a MidiEvent
    def nextEvent(self):
        return self.midiEvent(self.midiParser.readNextData())
    # creates a MidiEvent from the midiData

    def midiEvent(self, midiData):
        # check if TrackHeader
        if midiData[0:4] == b'MTrk':
            trackHeader = TrackHeader()
            trackHeader.setFromBytes(midiData)
            return trackHeader
        # find deltaTime
        tempData = midiData
        deltaTimeBytesLength = 0
        while Util.msbIsOne(tempData[deltaTimeBytesLength:]):
            deltaTimeBytesLength += 1
        deltaTimeBytesLength += 1
        deltaTime = tempData[:deltaTimeBytesLength]
        midiData = tempData[deltaTimeBytesLength:]
        # Meta Event
        if midiData[0:1] == b'\xff':
            if midiData[1] in EventDictionaries.META_EVENT_DICTIONARY:
                metaEventClass = EventDictionaries.META_EVENT_DICTIONARY[midiData[1]]
            else:
                metaEventClass = MetaEvent
            metaEvent = metaEventClass()
            metaEvent.setDeltaTimeFromBytes(deltaTime)
            metaEvent.setFromBytes(midiData)
            return metaEvent
        # System Event
        if midiData[0:1] == b'\xf0' or midiData[0:1] == b'\xf7':
            systemEvent = SystemExclusiveEvent()
            systemEvent.setDeltaTimeFromBytes(deltaTime)
            systemEvent.setFromBytes(midiData)
            return systemEvent
        # Channel Event
        if Util.msbIsOne(midiData):  # running status
            self.lastChannelStatusByte = midiData[0]
        else:  # not running status
            midiData = self.lastChannelStatusByte + midiData
        channelEventIdentifier = midiData[0] & int('f0', 16)
        if channelEventIdentifier in EventDictionaries.CHANNEL_EVENT_DICTIONARY:
            channelEventClass = EventDictionaries.CHANNEL_EVENT_DICTIONARY[channelEventIdentifier]
        else:
            channelEventClass = ChannelEvent
        channelEvent = channelEventClass()
        channelEvent.setDeltaTimeFromBytes(deltaTime)
        channelEvent.setFromBytes(midiData)
        return channelEvent

    def close(self):
        self.midiParser.close()
