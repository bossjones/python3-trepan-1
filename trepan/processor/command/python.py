# -*- coding: utf-8 -*-
#  Copyright (C) 2009-2010, 2013 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
import code, os, sys

# Our local modules
from import_relative import import_relative

Mbase_cmd  = import_relative('base_cmd', top_name='pydbgr')
Mcmdfns    = import_relative('cmdfns', '..', 'pydbgr')
Mmisc      = import_relative('misc',   '...', 'pydbgr')

class PythonCommand(Mbase_cmd.DebuggerCommand):
    """**python** [**-d**]

Run Python as a command subshell. The *sys.ps1* prompt will be set to
`Pydbgr >>> `.

If *-d* is passed, you can access debugger state via local variable *debugger*.

To issue a debugger command use function *dbgr()*. For example:

  dbgr('info program')
"""

    aliases      = ('py','shell')
    category      = 'support'
    min_args      = 0
    max_args      = 1
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Run Python as a command subshell'

    def dbgr(self, string):
        '''Invoke a debugger command from inside a python shell called inside
        the debugger.
        '''
        self.proc.cmd_queue.append(string)
        self.proc.process_command()
        return

    def run(self, args):
        # See if python's code module is around

        # Python does it's own history thing.
        # Make sure it doesn't damage ours.
        have_line_edit = self.debugger.intf[-1].input.line_edit
        if have_line_edit:
            try:
                self.proc.write_history_file()
            except IOError:
                pass
            pass

        banner_tmpl='''Pydbgr python shell%s
Use dbgr(*string*) to issue debugger command: *string*'''

        debug = len(args) > 1 and args[1] == '-d'
        if debug:
            banner_tmpl += ("\nVariable 'debugger' contains a pydbgr" +
                            "debugger object.")
            pass

        my_locals  = {}
        my_globals = None
        if self.proc.curframe:
            my_globals = self.proc.curframe.f_globals
            if self.proc.curframe.f_locals:
                my_locals = self.proc.curframe.f_locals
                pass
            pass

        # Give python and the user a way to get access to the debugger.
        if debug: my_locals['debugger'] = self.debugger
        my_locals['dbgr'] = self.dbgr

        sys.ps1 = 'Pydbgr >>> '
        if len(my_locals):
            interact(banner=(banner_tmpl % ' with locals'),
                     my_locals=my_locals, my_globals=my_globals)
        else:
            interact(banner=(banner_tmpl % ''))
            pass

        # restore our history if we can do so.
        if have_line_edit:
            pass
#             try:
#                 self.readline.read_history_file(self.histfile)
#             except ioerror:
#                 pass
#             return
        return
    pass


# Monkey-patched from code.py
# FIXME: get changes into Python.
def interact(banner=None, readfunc=None, my_locals=None, my_globals=None):
    """Almost a copy of code.interact
    Closely emulate the interactive Python interpreter.

    This is a backwards compatible interface to the InteractiveConsole
    class.  When readfunc is not specified, it attempts to import the
    readline module to enable GNU readline if it is available.

    Arguments (all optional, all default to None):

    banner -- passed to InteractiveConsole.interact()
    readfunc -- if not None, replaces InteractiveConsole.raw_input()
    local -- passed to InteractiveInterpreter.__init__()

    """
    console = code.InteractiveConsole(my_locals, filename='<pydbgr>')
    console.runcode = lambda code_obj: runcode(console, code_obj)
    setattr(console, 'globals', my_globals)
    if readfunc is not None:
        console.raw_input = readfunc
    else:
        try:
            import readline
        except ImportError:
            pass
    console.interact(banner)
    pass

# Also monkey-patched from code.py
# FIXME: get changes into Python.
def runcode(obj, code_obj):
    """Execute a code object.

    When an exception occurs, self.showtraceback() is called to
    display a traceback.  All exceptions are caught except
    SystemExit, which is reraised.

    A note about KeyboardInterrupt: this exception may occur
    elsewhere in this code, and may not always be caught.  The
    caller should be prepared to deal with it.

    """
    try:
        exec(code_obj, obj.locals, obj.globals)
    except SystemExit:
        raise
    except:
        obj.showtraceback()
    else:
        pass
    return


if __name__ == '__main__':
    Mdebugger = import_relative('debugger', '...')
    d = Mdebugger.Debugger()
    command = PythonCommand(d.core.processor)
    command.proc.frame = sys._getframe()
    command.proc.setup()
    if len(sys.argv) > 1:
        print("Type Python commands and exit to quit.")
        print(sys.argv[1])
        if sys.argv[1] == '-d':
            print(command.run(['python', '-d']))
        else:
            print(command.run(['python']))
            pass
        pass
    pass
