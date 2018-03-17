from mididings import *
from mididings.event import *
from mididings.extra import *
from mididings.extra.inotify import AutoRestart
from mididings.extra.gm import *
from math import floor, ceil
from arpeggiator import arpeggiator as arp

hook(
    AutoRestart(filenames=['arpeggiator.py'])
)

config(
    client_name='synth-studio',
    in_ports=[
        ('in1', 'microSTATION:.*'),
        ('in2')
    ],
    out_ports=[
        ('out1-mb-1', 'MicroBrute:.*'),
        ('out2-vk-1', 'CH345:.*'),
        ('out3-ms', 'microSTATION:.*'),
        ('out3-ms-1', 'microSTATION:.*'),
        ('out3-ms-2', 'microSTATION:.*'),
        ('out3-ms-3', 'microSTATION:.*'),
        ('out3-ms-4', 'microSTATION:.*'),
        ('out3-ms-10', 'microSTATION:.*'),
        ('out4-sq1', 'SQ-1:.*')
    ],
    initial_scene=1,
)

#control = PortFilter('control') >> Filter(PROGRAM) >> SceneSwitch()

preScene = Sanitize()  # >> Filter(NOTE | SYSRT | PROGRAM | SYSCM | SYSEX)

arp1Args = {
    'outPort': 'out3-ms-2',
    'outChannel': 2,
    'inChannel': 2,
    'resolution': 4,
    'latch': False,
    'pattern': '+12.+7.-5.',
    'direction': arp.DIRECTION_RANDOM,
    'randomVelocity': True
}


arp2Args = {
    'outPort': 'out2-vk-1',
    'outChannel': 1,
    'inChannel': 1,
    'resolution': 2,
    'latch': False,
    'pattern': '+3+5+7.',
    'direction': arp.DIRECTION_RANDOM,
    'randomVelocity': True
}

song1_scene1 = [
    PortFilter('in1') >> [
        Call(arp().setup, **arp1Args),
        Call(arp().setup, **arp2Args),
        [
            ChannelFilter(1) >> KeyFilter(':d#2') >> Transpose(
                12) >> Port('out1-mb-1') >> Print('mb'),
        ],
        [
            Filter(SYSRT_CLOCK) >> Port('out2-vk-1'),
            Filter(SYSRT_CLOCK) >> Port('out4-sq1'),
            Filter(SYSRT_START) >> Port('out4-sq1') >> Print('start'),
            Filter(SYSRT_STOP) >> Port('out4-sq1') >> Print('stop'),
            Filter(SYSRT_START) >> Port('out2-vk-1') >> Print('start'),
            Filter(SYSRT_STOP) >> Port('out2-vk-1') >> Print('stop')
        ]
    ]
]

song1 = SceneGroup('song1', [
    Scene('main', song1_scene1, [
        [
            Program('out3-ms', 1, 96),
            Program('out3-ms', 2, 20),
            Program('out3-ms', 10, 45),
        ],
        [
            Ctrl(ctrl=5, value=int(ceil(127/4))) >> Output(
                'out2-vk-1', 1) >> Print('vk portamento'),
            Ctrl(ctrl=42, value=0) >> Output(
                'out2-vk-1', 1) >> Print('vk detune'),
            Ctrl(ctrl=43, value=int(ceil(127/2))) >> Output(
                'out2-vk-1', 1) >> Print('vk vco eg int'),
            Ctrl(ctrl=44, value=0) >> Output(
                'out2-vk-1', 1) >> Print('vk vcf cutoff'),
            Ctrl(ctrl=45, value=127) >> Output(
                'out2-vk-1', 1) >> Print('vk vcf eg int'),
            Ctrl(ctrl=46, value=0) >> Output(
                'out2-vk-1', 1) >> Print('vk lfo rate'),
            Ctrl(ctrl=47, value=0) >> Output(
                'out2-vk-1', 1) >> Print('vk lfo pitch'),
            Ctrl(ctrl=48, value=127) >> Output(
                'out2-vk-1', 1) >> Print('vk lfo cutoff int'),
            Ctrl(ctrl=50, value=72) >> Output(
                'out2-vk-1', 1) >> Print('vk decay/release'),
            Ctrl(ctrl=51, value=102) >> Output(
                'out2-vk-1', 1) >> Print('vk sustain'),
            Ctrl(ctrl=52, value=0) >> Output(
                'out2-vk-1', 1) >> Print('vk delay time'),
            Ctrl(ctrl=53, value=int(ceil(127*.25))) >> Output(
                'out2-vk-1', 1) >> Print('vk feedback'),
        ],
        [
            Ctrl(ctrl=70, value=24) >> Output(
                'out3-ms-1', 1) >> Print('ms-1 sustain'),
            Ctrl(ctrl=71, value=0) >> Output(
                'out3-ms-1', 1) >> Print('ms-1 res'),
            Ctrl(ctrl=72, value=74) >> Output(
                'out3-ms-1', 1) >> Print('ms-1 release'),
            Ctrl(ctrl=73, value=24) >> Output(
                'out3-ms-1', 1) >> Print('ms-1 attack'),
            Ctrl(ctrl=75, value=64) >> Output(
                'out3-ms-1', 1) >> Print('ms-1 decay'),
            Ctrl(ctrl=79, value=16) >> Output(
                'out3-ms-1', 1) >> Print('ms-1 eg int'),
        ]
    ])
])

run(
    # control=control,
    # pre=preScene,
    scenes={
        1: song1
    }
)
