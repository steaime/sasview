"""
    Unit tests for saving and loading .svs files
"""

import os
import sys
import unittest
import warnings
if sys.version_info[0] >= 3:
    from io import StringIO
else:
    from StringIO import StringIO

from sas.sascalc.dataloader.loader import Loader
from sas.sascalc.fit.pagestate import Reader as fit_state_reader
from sas.sasgui.perspectives.invariant.invariant_state import Reader as invariant_reader
from sas.sasgui.perspectives.pr.inversion_state import Reader as pr_reader
from sas.sasgui.perspectives.corfunc.corfunc_state import Reader as corfunc_reader

warnings.simplefilter("ignore")

TEMP_FOLDER = "temp_folder"
STATE_LOADERS = [fit_state_reader, invariant_reader, pr_reader, corfunc_reader]


class projects(unittest.TestCase):

    def setUp(self):
        """
        Set up the base unit test class and variables used throughout the tests
        """
        self.addCleanup(self.remove_dir)
        self.loader = Loader()
        self.data1d = self.loader.load("test_data/data1D.h5")
        self.data2d = self.loader.load("test_data/data2D.h5")
        if not (os.path.isdir(TEMP_FOLDER)):
            os.makedirs(TEMP_FOLDER)

    def remove_dir(self):
        if(os.path.isdir(TEMP_FOLDER)):
            os.removedirs(TEMP_FOLDER)

    def test_saveload_data1d_fitting_only(self):
        """
        Test saving and loading a project with a single data set sent to fitting
        """
        self.assertTrue(1 == 1)

        # TODO: Send 1D to fitting, select model, save project, load project
        # TODO: Send both to fitting, select model on both, save/load
        # TODO: Send both to fitting, select model on one, save/load
        # TODO: Send 1D to each other persepective, save/load
        # TODO: Send 1D to every perspective, save/load
        # TODO: Save/load simultaneous/constrained fit project
