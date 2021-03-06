#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'Unit test for trepan.io.input'
import os, unittest
from import_relative import import_relative, get_srcdir

Minput = import_relative('trepan.io.input', '...')

class TestDebuggerInput(unittest.TestCase):

    def test_DebuggerInput(self):
        cmdhelper_file=os.path.join(get_srcdir(),'cmdhelper.py')
        inp = Minput.TrepanUserInput(cmdhelper_file)
        self.assertTrue(inp, 'Should have gotten a TrepanInput object back')
        line = inp.readline()
        self.assertEqual('# -*- coding: utf-8 -*-', line)
        inp.close()
        # Should be okay
        inp.close()
        return

if __name__ == '__main__':
    unittest.main()
