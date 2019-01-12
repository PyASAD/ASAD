from __future__ import absolute_import
from __future__ import print_function

import argparse
import os, os.path
import re
import sys

import colorama
import asad.pyasad as pyasad
import asad.interactive as interactive

try:
    import asad.wizard as wizard
except:
    print("\n!! Qt not installed, GUI will not be available !!\n\n")

#===============================================================================

MODEL_OPTIONS = [
    (['-m', '--model'], {
        'metavar' : 'Model',
        'type'    : str,
        'nargs'   : '+',
        'help'    : 'Model file'
    }),

    (['-M', '--model-dir'], {
        'metavar' : 'ModelDir',
        'type'    : str,
        'nargs'   : 1,
        'help'    : 'Model directory'
    })
]

#===============================================================================

OBSERVATION_OPTIONS = [
    (['-b', '--observation'], {
        'metavar' : 'Observation',
        'type'    : str,
        'nargs'   : '+',
        'help'    : 'Observation file'
    }),

    (['-B', '--observation-dir'], {
        'metavar' : 'ObservationDir',
        'type'    : str,
        'nargs'   : 1,
        'help'    : 'Observation directory'
    })
]

#===============================================================================

INTERACTIVE_OPTIONS = [
    (['-i', '--interactive'], {
        'action'  : 'store_true',
        'default' : False,
        'help'    : 'Interactive mode'
    }),

    (['-g', '--gui'], {
        'action'  : 'store_true',
        'default' : False,
        'help'    : 'GUI mode'
    }),

    (['-r', '--run'], {
        'action'  : 'store_true',
        'default' : True,
        'help'    : 'Assistant mode'
    }),

    (['-I', '--script'], {
        'type'    : str,
        'default' : None,
        'nargs'   : '+',
        'help'    : 'Run script'
    })
]

#===============================================================================

def positive(n):
    if n <= 0:
        return 1;
    else:
        return n

GENERAL_OPTIONS = [
    (['-s', '--step'], {
        'metavar' : 'Step',
        'type'    : float,
        'nargs'   : 1,
        'help'    : 'Interpolation step',
        'default' : 3
    }),

    (['-R', '--reddening'], {
        'metavar' : ('Start', 'End'),
        'type'    : float,
        'nargs'   : 2,
        'default' : [0, 0.5],
        'help'    : 'Reddening range'
    }),

    (['--reddening-factor'], {
        'metavar' : 'ReddeningFactor',
        'type'    : float,
        'nargs'   : 1,
        'default' : 0.01,
        'help'    : 'Reddening factor'
    }),

    (['-A', '--age'], {
        'metavar' : ('AgeStart', 'AgeEnd'),
        'type'    : float,
        'nargs'   : 2,
        'default' : [6.6, 10.25],
        'help'    : 'log(Age)'
    }),

    (['--age-factor'], {
        'metavar' : 'AgeFactor',
        'type'    : float,
        'nargs'   : 1,
        'default' : 0.05,
        'help'    : 'Age factor'
    }),

    (['-S', '--stat'], {
        'metavar' : 'Statistic',
        'choices' : pyasad.Statistics.STAT_TEST_NAMES,
        'default' : pyasad.Statistics.STAT_TEST_NAMES[0],
        'help'    : 'Statistical test'
    }),

    (['-p', '--precision'], {
        'metavar' : 'Precision',
        'type'    : positive,
        'default' : 6,
        'help'    : 'Calculation precision'
    })
]

#===============================================================================

def parser_add_options(parser, options):
    for (pos, opts) in options:
        parser.add_argument(*pos, **opts)

def parse():
    parser = argparse.ArgumentParser(description='')
    parser_add_options(parser, GENERAL_OPTIONS)
#    model_group = parser.add_mutually_exclusive_group(required=True)
#    parser_add_options(model_group, MODEL_OPTIONS)
#    obsv_group = parser.add_mutually_exclusive_group(required=True)
#    parser_add_options(obsv_group, OBSERVATION_OPTIONS)
    interactive_group = parser.add_mutually_exclusive_group()
    parser_add_options(interactive_group, INTERACTIVE_OPTIONS)
    return parser.parse_args()

def list_files(directory):
    in_dir = os.path.abspath(directory)
    in_files = [
        os.path.join(in_dir, f)
        for f in os.listdir(in_dir)
        if os.path.splitext(os.path.basename(f))[1][1:]
        in ALLOWED_EXTENSIONS
    ]
    return in_files

def process(args):
    if args.interactive:
        interactive.Main_Shell().cmdloop()
    elif args.run:
        interactive.Run_Shell().cmdloop()
    elif args.gui:
        wizard.init()
    elif args.script:
        for s in args.script:
            interactive.Main_Shell().execute(s)

#===============================================================================

def _listdir(root):
    res = []
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isdir(path):
            name += os.sep
            res.append(name)
    return res

def _complete_path(path=None):
    if not path:
        return _listdir('.')
    dirname, rest = os.path.split(path)
    tmp = dirname if dirname else '.'
    res = [os.path.join(dirname, p)
           for p in _listdir(tmp) if p.startswith(rest)]
    if len(res) > 1 or not os.path.exists(path):
        return res
    if os.path.isdir(path):
        return [os.path.join(path, p) for p in _listdir(path)]
    return [path + ' ']

def complete(text, state):
    return (_complete_path(text))[state]

def init_readline():
    try:
        import readline
    except ImportError:
        if sys.platform != 'darwin':
            pass
        else:
            print("Module readline not available.")
    else:
        import rlcompleter
        readline.set_completer(complete)
        readline.set_completer_delims(' \t\n;')
	complete_key = "tab: complete"
	if sys.platform == 'darwin':
            if 'libedit' in readline.__doc__:
                complete_key = "bind ^I rl_complete"
        readline.parse_and_bind(complete_key)

def init_readline_history():
    histfile = os.path.join(".asad.hist")
    try:
        import readline
        readline.read_history_file(histfile)
    except ImportError:
        if sys.platform != 'darwin':
            pass
        else:
            print("Module readline not available.")
    except IOError:
        print("Cannot find readline history file")
    else:
	    import atexit
	    atexit.register(readline.write_history_file, histfile)

def init():
    init_readline()
    init_readline_history()
    arg = parse()
    process(arg)

#===============================================================================
