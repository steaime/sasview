"""
    Unit tests for saving and loading .svs files
"""

import os
import unittest
import warnings
import threading
from time import sleep

import sas.sasview.sasview as sasview
from sas.sascalc.dataloader.loader import Loader
from sas.sascalc.fit.pagestate import Reader as fit_state_reader
from sas.sasgui.perspectives.invariant.invariant_state import Reader as invariant_reader
from sas.sasgui.perspectives.pr.inversion_state import Reader as pr_reader
from sas.sasgui.perspectives.corfunc.corfunc_state import Reader as corfunc_reader

warnings.simplefilter("ignore")

TEMP_FOLDER = "temp_folder"
DATA_1D = "test_data" + os.path.sep + "data1D.h5"
DATA_2D = "test_data" + os.path.sep + "data2D.h5"
STATE_LOADERS = [fit_state_reader, invariant_reader, pr_reader, corfunc_reader]


class projects(unittest.TestCase):

    def setUp(self):
        """
        Set up the base unit test class and variables used throughout the tests
        """
        self.addCleanup(self.remove_dir)
        self.loader = Loader()
        self.data1d = self.loader.load(DATA_1D)
        self.data2d = self.loader.load(DATA_2D)
        self.sasviewThread = sasviewThread(False)
        if not (os.path.isdir(TEMP_FOLDER)):
            os.makedirs(TEMP_FOLDER)
        self.sasviewThread.lock.acquire()
        self.sasviewThread.start_local()
        while self.sasviewThread.frame is None:
            sleep(0.05)
        while self.sasviewThread.frame._data_panel is None:
            sleep(0.05)
        # TODO: Do we need the frame to be visible to perform operations?
        while not self.sasviewThread.frame.IsShown():
            sleep(2)
        # self.sasviewThread.frame.get_data(DATA_1D)
        # self.sasviewThread.frame.get_data(DATA_2D)

    def tearDown(self):
        self.sasviewThread.lock.release()
        self.sasviewThread.frame = None
        self.remove_dir()

    def remove_dir(self):
        if(os.path.isdir(TEMP_FOLDER)):
            os.removedirs(TEMP_FOLDER)

    def test_saveload_data1d_fitting_only(self):
        """
        Test saving and loading a project with a single data set sent to fitting
        """
        self.assertTrue(self.data1d is not None)
        self.assertTrue(self.data2d is not None)
        self.assertTrue(1 == 1)

        # TODO: Send 1D to fitting, select model, save project, load project
        # TODO: Send both to fitting, select model on both, save/load
        # TODO: Send both to fitting, select model on one, save/load
        # TODO: Send 1D to each other persepective, save/load
        # TODO: Send 1D to every perspective, save/load
        # TODO: Save/load simultaneous/constrained fit project


class sasviewThread(threading.Thread):
    """Run the MainLoop as a thread. Access the frame with self.frame."""

    def __init__(self, autoStart=True):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.lock.acquire()  # lock until variables are set
        self.setDaemon(1)
        self.start_orig = self.start
        self.start = self.start_local
        self.frame = None  # to be defined in self.run
        if autoStart:
            self.start()  # automatically start thread on init
        self.lock.release()

    def run(self):
        app = sasview.run_gui(True)
        self.frame = app.gui.frame
        app.gui.MainLoop()

    def start_local(self):
        self.start_orig()
