"""
Interface to page state for cofunc fits.
 The 4.x sasview gui builds the corfunc data object directly inside the wx
GUI code.  This code separates the in-memory representation from the GUI.
Initially it is used for a headless backend that operates
directly on the saved XML; eventually it should provide methods to replace
direct access to the Corfunc_PageState object so that the code for setting up
and running fits in wx, qt, and headless versions of SasView shares a common
in-memory representation.
"""

import os
import sys
from corfunc_pagestate import CorfuncPageState
from corfunc_pagestate import Reader as CFReader
from corfunc_calculator import CorfuncCalculator


class CorfuncState(object):

    def __init__(self, crf_file):
        self.file = crf_file
        self.reader = CFReader(callback=self._add_entry)
        self.data_set = self.reader.read(self.file)
        self.calculator = CorfuncCalculator(self.data_set)
        if not self._state:
            self._state = self.data_set.meta_data['corfunc']
        self._state.data = self.data_set

    def _add_entry(self, state=None, datainfo=None, format=None):
        """
        Handed to the reader to receive and accumulate the loaded state objects.
        """
        # Note: datainfo is in state.data; format=.svs means reset fit panels
        if isinstance(state, CorfuncPageState):
            self.set_state(state)
        else:
            # ignore empty fit info
            pass

    def __str__(self):
        # type: () -> str
        return '<CorFuncFit %s>' % self.state

    def set_state(self, state):
        self._state = state

    def show(self):
        # type: () -> None
        """
        Summarize the corfunc page in the state object.
        """
        # Note: _dump_attrs isn't a closure, but putting it here anyway
        # because it is specific to show and doesn't need to be efficient.
        def _dump_attrs(obj, label=""):
            print(obj)
            print("="*20, label)
            for attr, value in sorted(obj.__dict__.items()):
                if isinstance(value, (list, tuple)):
                    print(attr)
                    for item in value:
                        print("   ", item)
                else:
                    print(attr, value)
        _dump_attrs(self._state, label="Corfunc page")


if __name__ == "__main__":
    # Usage: pass a file name as an argument
    #   python corfuncstate.py <filename>
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            if os.path.exists(filename):
                state = CorfuncState(filename)
                state.show()
            else:
                print("File path supplied is not a valid file location.")
        except Exception as e:
            msg = "File loading error: {}.\n".format(filename)
            msg += "\tFilename is of type {}.".format(filename.__class__)
            msg += "String expected."
            print(msg + "\n" + e.message)
    else:
        print("No file path supplied.")
