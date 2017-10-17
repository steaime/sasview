"""
    Unit tests for saving and loading .svs files
"""

import os
import sys
import unittest
import logging
import warnings
if sys.version_info[0] >= 3:
    from io import StringIO
else:
    from StringIO import StringIO

from sas.sasview.sasview import SasView
from sas.sascalc.dataloader.loader import Loader
from sas.sascalc.fit.pagestate import PageState
from sas.sasgui.perspectives.fitting.fitpage import FitPage

logger = logging.getLogger(__name__)
warnings.simplefilter("ignore")

TEMP_FOLDER = "temp_folder"


class projects(unittest.TestCase):

    def setUp(self):
        """
        Set up the base unit test class and variables used throughout the tests
        """
        self.loader = Loader()
        self.data1d = self.loader.load("test_data/data1D.h5")
        self.data2d = self.loader.load("test_data/data2D.h5")
        if not (os.path.isdir(TEMP_FOLDER)):
            os.makedirs(TEMP_FOLDER)
        self.gui = SasView()

    def addCleanUp(self):
        """
        Close any open files, close any open GUI elements, and remove temp files
        """
        if(os.path.isdir(TEMP_FOLDER)):
            os.removedirs(TEMP_FOLDER)
        self.gui.gui.Close()

    def test_saveload_data1d_fitting_only(self):
        """
        Test saving and loading a project with a single data set sent to fitting
        """
        #fitpage.fill_data_combobox([self.data1d])
        #fitpage.categorybox.SetSelection(4)
        #fitpage.formfactorbox.SetSelection(6)

        # TODO: Send 1D to fitting, select model, save project, load project
        # TODO: Send both to fitting, select model on both, save/load
        # TODO: Send both to fitting, select model on one, save/load
        # TODO: Send 1D to each other persepective, save/load
        # TODO: Send 1D to every perspective, save/load
        # TODO: Save/load simultaneous/constrained fit project
