import sys
import argparse

from kord import *
from bestia.output import echo

import tuner

SCALES = {
    'major': MajorScale,

    'minor': MinorScale,
    'melodic_minor': MelodicMinorScale,
    'harmonic_minor': HarmonicMinorScale,

    'major_pentatonic': MajorPentatonicScale,
    'minor_pentatonic': MinorPentatonicScale,

    'ionian': IonianMode,
    'lydian': LydianMode,
    'mixolydian': MixolydianMode,

    'aeolian': AeolianMode,
    'dorian': DorianMode,
    'phrygian': PhrygianMode,
    'locrian': LocrianMode,

    'chromatic': ChromaticScale,
}

CHORDS = {
    'maj': MajorTriad,
    'min': MinorTriad,
    'aug': AugmentedTriad,
    'dim': DiminishedTriad,

    'maj7': MajorSeventhChord,
    'min7': MinorSeventhChord,
    '7': DominantSeventhChord,
    'dim7': DiminishedSeventhChord, # °7  
    'min7dim5': HalfDiminishedSeventhChord, # ⦰7

    'maj9': MajorNinthChord,
    'min9': MinorNinthChord,
    '9': DominantNinthChord,
}

INSTRUMENTS = tuner.load_tuning_data()

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='<<< Fretboard visualizer sample tool for the kord music framework >>>',
    )
    parser.add_argument(
        'root',
        help='select key ROOT note',
    )

    group = parser.add_mutually_exclusive_group()

    scale_choices = [ m for m in SCALES.keys() ]
    group.add_argument(
        '-s', '--scale',
        help='{}'.format(str(scale_choices).lstrip('[').rstrip(']').replace('\'', '')),
        choices=scale_choices,
        default='',
        metavar='',
    )

    chord_choices = [ m for m in CHORDS.keys() ]
    group.add_argument(
        '-c', '--chord',
        help='{}'.format(str(chord_choices).lstrip('[').rstrip(']').replace('\'', '')),
        choices=chord_choices,
        default='maj',
        metavar='',
    )

    instr_choices = [ i for i in INSTRUMENTS.keys() ]
    parser.add_argument(
        '-i', '--instrument',
        help='{}'.format(str(instr_choices).lstrip('[').rstrip(']').replace('\'', '')),
        choices=instr_choices,
        default='guitar',
        metavar='',
    )
    parser.add_argument(
        '-t', '--tuning',
        help='check .json files for available options',
        default='standard',
        metavar='',
    )
    parser.add_argument(
        '-f', '--frets',
        help='1, 2, .., {}'.format(MAX_FRETS),
        choices=[ f+1 for f in range(MAX_FRETS) ],
        default=max_frets_on_screen(MAX_FRETS),
        metavar='',
        type=int,
    )
    parser.add_argument(
        '-v', '--verbosity',
        help='0, 1, 2',
        choices= (0, 1, 2),
        default=1,
        metavar='',
        type=int,
    )
    args = parser.parse_args()

    # some args require extra validation than what argparse can offer, let's do that here...
    try:
        # validate tuning
        if args.tuning not in INSTRUMENTS[args.instrument].keys():
            raise InvalidInstrument(
                "fretboard.py: error: argument -t/--tuning: invalid choice: '{}' (choose from {}) ".format(
                    args.tuning,
                    str( list( INSTRUMENTS[args.instrument].keys() ) ).lstrip('[').rstrip(']'),
                )
            )

        # validate root note
        note_chr = args.root[:1].upper()
        if note_chr not in notes._CHARS:
            raise InvalidNote(
                "fretboard.py: error: argument ROOT: invalid note: '{}' (choose from {}) ".format(
                    note_chr,
                    str( [ n for n in notes._CHARS if n ] ).lstrip('[').rstrip(']')
                )
            )

        # validate root alteration
        note_alt = args.root[1:]
        if note_alt and note_alt not in list(notes._ALTS.keys()):
            raise InvalidNote(
                "fretboard.py: error: argument ROOT: invalid alteration: '{}' (choose from {}) ".format(
                    note_alt,
                    str( list(notes._ALTS.keys()) ).lstrip('[').rstrip(']')
                )
            )

        args.root = (note_chr, note_alt)

    except Exception as x:
        parser.print_usage()
        print(x)
        args = None

    return args

def run(args):
    
    instrument = PluckedStringInstrument(
        *[ Note(*string_tuning) for string_tuning in INSTRUMENTS[args.instrument][args.tuning] ]
    )

    if args.scale:
        MODE = SCALES[args.scale]
    elif args.chord:
        MODE = CHORDS[args.chord]

    mode = MODE(chr=args.root[0], alt=args.root[1])

    echo(
        '{} {}\t\t{} ({} tuning)'.format(
            str(mode.root)[:-1],
            mode.name,
            args.instrument,
            args.tuning
        ),
        'blue'
    )

    instrument.fretboard(
        display=mode,
        frets=args.frets,
        verbose=args.verbosity,
        limit=24
    )

    return 0

if __name__ == '__main__':
    rc = -1
    valid_args = parse_arguments()
    if not valid_args:
        rc = 2
    else:
        rc = run(valid_args)
    sys.exit(rc)
