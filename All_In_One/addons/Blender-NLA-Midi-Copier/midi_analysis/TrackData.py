from .Note import Note
from .MidiEvents import *
import bisect

# contains data for a single track
class TrackData:
    def __init__(self, name=""):
        self.notes = []
        # maps pitches to notes without end times
        self.incompleteNotes = {}
        self.events = []
        self.name = name
        self.deltaTimeTotal = 0
        # if false, time division is frames per second
        self.isTicksPerBeat = True
        self.debug = False
        return

    # Events need to be added in order, last event must be end of track
    def addEvent(self, event):
        self.events.append(event)
        if isinstance(event, TrackNameEvent):
            self.name = event.trackName
        elif (isinstance(event, NoteOnEvent) and
              not(event.isNoteOff())):
            if event.noteNumber in self.incompleteNotes and self.debug:
                print("Note on event for note " + str(event.noteNumber)
                      + " already playing, skipping...")
            else:
                self.incompleteNotes[event.noteNumber] = Note(event.startTime,
                                                              event.noteNumber,
                                                              event.velocity,
                                                              event.channel)
        elif (isinstance(event, NoteOffEvent) or
              (isinstance(event, NoteOnEvent) and event.isNoteOff())):
            if event.noteNumber in self.incompleteNotes:
                self.incompleteNotes[event.noteNumber].setEndTime(event.startTime)
                self.notes.append(self.incompleteNotes[event.noteNumber])
                del self.incompleteNotes[event.noteNumber]
            elif self.debug:
                print("Note off event for note " + str(event.noteNumber)
                      + " not playing, skipping...")
        elif isinstance(event, EndOfTrackEvent):
            self.notes.sort()


# this is kind of like an ordered dictionary
class TempoChanges:
    def __init__(self):
        self.tempoChanges = []
        self.index = 0
        return

    # tempo changes need to be added in order
    # tempo in microseconds per quarter note
    # may change the index and affect which TempoChange is marked as next
    # All tempo changes should be defined in track 0 of a type one midi file
    # (or at least before any notes, FL Studio seems to put tempo changes in track 1...)
    # so the possible index change shouldn't be an issue for MidiData
    def addTempoChange(self, deltaTimeTotal, tempo):
        bisect.insort(self.tempoChanges,
                      TempoChange(deltaTimeTotal, tempo))

    # so that class can be used as a stream
    def deltaTimeTotal(self):
        return self.tempoChanges[self.index].deltaTimeTotal

    def usPerQuarter(self):
        return self.tempoChanges[self.index].tempo

    def findNext(self):
        self.index += 1

    # returns true if the current index is a tempo change
    # (will return true if findNext will go beyond end of
    # list, this is intentional)
    def hasMore(self):
        return self.index < len(self.tempoChanges)

    def reset(self):  # go back to first tempo change
        self.index = 0


class TempoChange:
    # deltaTimeTotal in ticks
    # tempo in microseconds per quarter note
    def __init__(self, deltaTimeTotal, tempo):
        self.deltaTimeTotal = deltaTimeTotal
        self.tempo = tempo

    def __lt__(self, other):
        return self.deltaTimeTotal < other.deltaTimeTotal
