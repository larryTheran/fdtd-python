"""Experiment arguments for terminal and notebook entry points."""
import sys


def notebook_kernel():
    # An active kernel has already imported IPython. Terminal users need no
    # notebook packages, even when asking for --help or listing experiments.
    ipython = sys.modules.get('IPython')
    if ipython is None:
        return None
    return getattr(ipython.get_ipython(), 'kernel', None)


def parse_arguments(parser, argv):
    """Use explicit, terminal or %run options; ignore the hosting kernel's own flags."""
    if argv is None:
        argv = sys.argv[1:]
        application = getattr(notebook_kernel(), 'parent', None)
        if getattr(application, 'argv', None) == argv:
            argv = []
    return parser.parse_args(argv)
