# Mididings Arpeggiator

An awesome customizable arpeggiator to be used with Mididings along with any compatible MIDI devices or clients.

## Getting Started

As I'm not yet a Senior Python developer, this project may require better optimization. But, it currently does its job pretty well as you 
can certainly use as many arpeggiator instances you need, using different MIDI ports and channels as outputs, hence composing a full orchestation and interesting melodies with ease!

Feel free to contribute and submit pull requests if you have new ideas in mind.

### Prerequisites

You need Mididings, but you can probably change this a bit and use it with other MIDI Python libraries as well.

### Usage

Copy `arpeggiator.py` inside the folder where your Mididings scripts live. Then, import it inside your script:

```
from arpeggiator import arpeggiator
```

Initialize it and use it within your events chain. Note that at least 4 events are required to go thru this setup (do not filter any of those before chaining to the arpeggiator):

* `NOTEON`, `NOTEOFF`, `SYSRT_CLOCK` and `SYSRT_START`

Also, it is important to know that you shouldn't apply a _ChannelFilter_ before the _Call_ to the arpeggiator, since you may have your hardware's MIDI clock to be sending messages thru a different channel, hence, the arpeggiator won't work. Avoid using _ChannelFilter_ within the arpeggiator's events chain.

Initialize the arpeggiator arguments and run it:

```
arpArgs = {
    'outPort': 'my-midi-hardware-synth',
    'outChannel': 2,
    'inChannel': 2,
    'resolution': 2,
    'latch': False,
    'pattern': '+3.+2...+5.-2..+12',
    'direction': arp.DIRECTION_UP,
    'randomVelocity': True
}
```

Then, use Mididings' _Call_ method inside the events chain like this:

```
Call(arpeggiator().setup, **arpArgs)
```

See [this example](synth-studio.py) for a real world scenario.

## Options

* `outPort`: the output port (e.g. an external MIDI device)
* `outChannel`: the output channel
* `inChannel`: the channel that will be listened for incoming notes
* `resolution`: how many pattern steps will be played on each beat
* `latch`: If _True_, the pattern will keep playing even if you release the note key
* `pattern`: the arpeggio pattern (see [patterns](#patterns))
* `direction`: the classic direction feature used in many arpeggiators out there. It states in which direction should the pattern be read. Valid options are: _DIRECTION_UP_, _DIRECTION_DOWN_, _DIRECTION_UPDOWN_ and _DIRECTION_RANDOM_.
* `randomVelocity`: if _True_, the generated notes will randomize its velocities. If _False_, original note's velocity will be preserved.

## <a name="patterns"></a>Patterns

I tried to make it as much easy and comprehensible as possible but any suggestions are welcome.

* `+3.+0.+5.-2.`: this pattern has 8 steps; the `.` means _silence_, so, no note will be played at that step. A number is the note interval that will be applied to the incoming note, so `+3` means that a *C3* (MIDI 60) will output a *D#3* (MIDI 63) at that step. For example, to increase by one octave, you can do `+12`. See [this chart](http://computermusicresource.com/midikeys.html) for details.

You can write any complex patterns and combine it with the *direction* option for generating fun and interesting melodies thus adding different output ports and channels, many musical compositions can be generated with just a few keyboard notes.

## Authors

* **Nicolas Iglesias** - *Initial work* - [webpolis](https://github.com/webpolis)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
