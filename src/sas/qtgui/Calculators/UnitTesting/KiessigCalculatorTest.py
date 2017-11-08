import sys
import unittest
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# TEMP
#import sas.qtgui.path_prepare
import path_prepare


from sas.qtgui.Calculators.KiessigPanel import KiessigPanel

if not QtWidgets.QApplication.instance():
    app = QtWidgets.QApplication(sys.argv)


class KiessigCalculatorTest(unittest.TestCase):
    """Test the KiessigCalculator"""
    def setUp(self):
        """Create the KiessigCalculator"""
        self.widget = KiessigPanel(None)

    def tearDown(self):
        """Destroy the KiessigCalculator"""
        self.widget.close()
        self.widget = None

    def testDefaults(self):
        """Test the GUI in its default state"""
        self.assertIsInstance(self.widget, QtWidgets.QWidget)
        self.assertEqual(self.widget.windowTitle(), "Kiessig Thickness Calculator")
        self.assertEqual(self.widget.sizePolicy().Policy(), QtWidgets.QSizePolicy.Fixed)

    def testHelp(self):
        """ Assure help file is shown """

        # this should not rise
        self.widget.onHelp()

    def testComplexEntryNumbers(self):
        """ User entered compound calculations and subsequent reset"""

        self.widget.deltaq_in.clear()
        self.widget.deltaq_in.insert('0.05')
        #
        # Push Compute with the left mouse button
        computeButton = self.widget.computeButton
        QTest.mouseClick(computeButton, Qt.LeftButton)
        self.assertEqual(self.widget.lengthscale_out.text(), '125.664')

    def testComplexEntryNumbers2(self):
        """ User entered compound calculations and subsequent reset"""

        self.widget.deltaq_in.clear()
        self.widget.deltaq_in.insert('1.0')
        #
        # Push Compute with the left mouse button
        computeButton = self.widget.computeButton
        QTest.mouseClick(computeButton, Qt.LeftButton)
        self.assertEqual(self.widget.lengthscale_out.text(), '6.283')

    def testComplexEntryNumbers3(self):
        """ User entered compound calculations and subsequent reset"""

        self.widget.deltaq_in.clear()
        self.widget.deltaq_in.insert('2.0')
        #
        # Push Compute with the left mouse button
        computeButton = self.widget.computeButton
        QTest.mouseClick(computeButton, Qt.LeftButton)
        self.assertEqual(self.widget.lengthscale_out.text(), '3.142')

    def testComplexEntryLetters(self):
        """ User entered compound calculations and subsequent reset"""

        self.widget.deltaq_in.insert("xyz")

        # Push Compute with the left mouse button
        computeButton = self.widget.computeButton
        QTest.mouseClick(computeButton, Qt.LeftButton)
        self.assertEqual(self.widget.lengthscale_out.text(), '')

if __name__ == "__main__":
    unittest.main()
