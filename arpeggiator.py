from mididings import *
from mididings.event import *
from mididings.engine import output_event
from datetime import datetime
from math import floor, ceil
from random import randrange, shuffle
import time
import re


class arpeggiator:

    DIRECTION_UP = 1
    DIRECTION_DOWN = 2
    DIRECTION_UPDOWN = 3
    DIRECTION_RANDOM = 4

    def __init__(self):
        self.__ticks = 0
        self.__tickFactor = 25  # ticks per beat
        self.__firstTickTime = None
        self.__lastTickTime = None
        self.__isLatched = False
        self.__outPort = None
        self.__outChannel = None
        self.__inChannel = None
        self.__event = None
        self.__resolution = 2
        self.__pattern = None
        self.__randomVelocity = False
        self.__direction = None
        self.__notes = {}

    def setup(self, event, outPort, outChannel, inChannel, latch=False, resolution=2, pattern='+3.+0.+5.-2.', direction=DIRECTION_UP, randomVelocity=False):
        self.__event = event
        self.__outPort = outPort
        self.__outChannel = outChannel
        self.__inChannel = inChannel
        self.__isLatched = latch
        self.__resolution = resolution
        self.__pattern = pattern
        self.__direction = direction
        self.__randomVelocity = randomVelocity

        microSecs = 0

        if event.type == NOTEON:
            if event.channel and event.channel != self.__inChannel:
                return

            self.__notes[event.data1] = {
                'last': True,
                'active': True,
                'patternStep': 0,
                'velocity': event.velocity
            }

            self.__setLastStatus(event.data1)

        if event.type == NOTEOFF:
            if event.channel and event.channel != self.__inChannel:
                return

            self.__notes[event.data1]['active'] = self.__isLatched or False
            self.__notes[event.data1]['patternStep'] = 0

            self.__setLastStatus(event.data1)

        if event.type == SYSRT_CLOCK:
            # tempo = ticks per sec * 2.5
            # beat = 25 ticks
            self.__lastTickTime = datetime.now()

            if self.__firstTickTime is not None:
                diff = self.__lastTickTime - self.__firstTickTime
                microSecs = diff.total_seconds() * 1000000

            self.__arpeggiate()

            self.__ticks += 1

        if event.type == SYSRT_START or event.type == SYSCM_SONGPOS:
            self.__ticks = 0
            self.__firstTickTime = datetime.now()
            self.__notes = {}

        if event.type == SYSEX or event.type == SYSCM_SONGPOS or event.type == SYSCM_QFRAME or event.type == SYSRT_SENSING:
            print(str(event.type))

        return event

    def __setLastStatus(self, midiNote):
        for key, value in self.__notes.iteritems():
            if key != midiNote:
                self.__notes[key]['last'] = False
        return

    def __getLastNote(self):
        for key, value in self.__notes.iteritems():
            if value['last'] is True:
                return self.__notes[key]

        return None

    def __getLastActiveNote(self):
        for key, value in self.__notes.iteritems():
            if value['last'] is True and value['active'] is True:
                return self.__notes[key]

        return None

    def __getActiveNotes(self):
        ret = {}

        for key, value in self.__notes.iteritems():
            if value['active'] is True:
                ret[key] = value

        return ret

    def __generatePatternNote(self, midiNote, offset):
        note = eval('%i %s' % (midiNote, offset))

        return note

    def __applyPatternDirection(self):
        pattern = filter(bool, re.split(r'([\+\-]?\d+|\.)', self.__pattern))

        if self.__direction == self.DIRECTION_DOWN:
            pattern = list(reversed(pattern))
        elif self.__direction == self.DIRECTION_UPDOWN:
            pattern = pattern + list(reversed(pattern))
        elif self.__direction == self.DIRECTION_RANDOM:
            shuffle(pattern)

        return pattern

    def __setPatternNotesOff(self):
        pattern = self.__applyPatternDirection()
        activeNotes = self.__getActiveNotes()

        for note, value in activeNotes.iteritems():
            if pattern[value['patternStep']] != '.':
                offNote = self.__generatePatternNote(
                    note, pattern[value['patternStep']])
                output_event(NoteOffEvent(self.__outPort, self.__outChannel,
                                          offNote))

        return

    def __arpeggiate(self):
        pattern = self.__applyPatternDirection()
        activeNotes = self.__getActiveNotes()

        for note, value in activeNotes.iteritems():
            if self.__ticks % floor(self.__tickFactor/self.__resolution) == 0:
                print 'tick %i pattern step %s' % (
                    self.__ticks, pattern[value['patternStep']])

                if pattern[value['patternStep']] != '.':
                    output_event(NoteOnEvent(self.__outPort, self.__outChannel,
                                             self.__generatePatternNote(
                                                 note, pattern[value['patternStep']]),
                                             randrange(70, 127) if self.__randomVelocity else value['velocity']))

                if value['patternStep'] + 1 >= len(pattern):
                    self.__notes[note]['patternStep'] = 0
                    self.__setPatternNotesOff()
                else:
                    self.__notes[note]['patternStep'] += 1

        return
