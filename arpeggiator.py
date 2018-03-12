from mididings import *
from mididings.event import *
from mididings.engine import output_event
from datetime import datetime
from math import floor, ceil
from random import randrange
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
        self.__outputPort = None
        self.__outputChannel = None
        self.__incomingEvent = None
        self.__noteResolution = 2
        self.__notePattern = None
        self.__randomVelocity = False
        self.__notes = {}

    def setup(self, event, outPort, outChannel, latch=False, resolution=2, pattern='+3.+0.+5.-2.', direction=DIRECTION_UP, randomVelocity=False):
        self.__incomingEvent = event
        self.__outputPort = outPort
        self.__outputChannel = outChannel
        self.__isLatched = latch
        self.__noteResolution = resolution
        self.__notePattern = pattern
        self.__randomVelocity = randomVelocity

        microSecs = 0

        if event.type == NOTEON:
            self.__notes[event.data1] = {
                'last': True,
                'active': True,
                'patternStep': 0,
                'velocity': event.velocity
            }

            self.__setLastStatus(event.data1)

        if event.type == NOTEOFF:
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

    def __applyPatternDirection(self, pattern):

        return pattern

    def __arpeggiate(self):
        pattern = filter(bool, re.split(
            r'([\+\-]?\d+|\.)', self.__notePattern))
        pattern = self.__applyPatternDirection(pattern)

        activeNotes = self.__getActiveNotes()

        for note, value in activeNotes.iteritems():
            if self.__ticks % floor(self.__tickFactor/self.__noteResolution) == 0:
                print 'tick %i pattern step %s' % (
                    self.__ticks, pattern[value['patternStep']])

                if pattern[value['patternStep']] != '.':
                    output_event(NoteOnEvent(self.__outputPort, self.__outputChannel,
                                             self.__generatePatternNote(
                                                 note, pattern[value['patternStep']]),
                                             randrange(70, 127) if self.__randomVelocity else value['velocity']))

                if value['patternStep'] + 1 >= len(pattern):
                    self.__notes[note]['patternStep'] = 0
                else:
                    self.__notes[note]['patternStep'] += 1

                # # note patterns go off... take care of duration :), probably best setting OFF
                # if pattern[value['patternStep'] - 1] != '.':
                #     offNote = __generatePatternNote(
                #         note, pattern[value['patternStep'] - 1])
                #     output_event(NoteOffEvent(outputPort, outputChannel,
                #                               offNote))

        return
