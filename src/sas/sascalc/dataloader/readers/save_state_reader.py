"""
    Reader for loading in save states
"""
############################################################################
# This software was developed by the University of Tennessee as part of the
# Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
# project funded by the US National Science Foundation.
# If you use DANSE applications to do scientific research that leads to
# publication, we ask that you acknowledge the use of the software with the
# following sentence:
# This work benefited from DANSE software developed under NSF award DMR-0520547.
# copyright 2008, University of Tennessee
#############################################################################

import logging
import os
import sys
from sas.sascalc.corfunc.corfuncstate import CorfuncState
from sas.sascalc.fit.fitstate import FitState
from sas.sascalc.dataloader.readers.cansas_reader import CANSAS_NS
from sas.sascalc.dataloader.readers.cansas_reader import Reader as CansasReader

logger = logging.getLogger(__name__)
SAVE_STATE_NODES = ["fitting_plug_in", "pr_inversion", "invariant", "corfunc"]


class Reader(CansasReader):
    """
    Class to load ascii files (2, 3 or 4 columns).
    """
    # File type
    type_name = "ASCII"
    # Wildcards
    type = ["ASCII files (*.txt)|*.txt",
            "ASCII files (*.dat)|*.dat",
            "ASCII files (*.abs)|*.abs",
            "CSV files (*.csv)|*.csv"]
    # List of allowed extensions
    ext = ['.txt', '.dat', '.abs', '.csv']
    # Flag to bypass extension check
    allow_all = True
    # data unless that is the only data
    min_data_pts = 5

    def __init__(self):
        CansasReader.__init__(self)
        self.fit_data = None
        self.cfr_data = None

    def get_file_contents(self):
        """
        Get the contents of the file
        """
        super(Reader, self).get_file_contents()

    def get_file_contents(self):
        """
        Send the SASentry through each of the save state loaders
        :param dom:
        :param recurse:
        :return:
        """
        self.load_file_and_schema(self.f_open.name)
        for i, item in enumerate(SAVE_STATE_NODES):
            if self.xmldoc.xpath('ns:{}'.format(item),
                                 namespaces={'ns': CANSAS_NS}):
                self.fit_data = FitState(self.f_open.name)
                self.cfr_data = CorfuncState(self.f_open.name)

        if hasattr(self.fit_data, "show"):
            print(self.fit_data.show())
        if hasattr(self.cfr_data, "show"):
            print(self.cfr_data.show())


if __name__ == "__main__":
    # Usage: pass a file name as an argument
    #   python corfuncstate.py <filename>
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            if os.path.exists(filename):
                reader = Reader()
                reader.read(filename)
            else:
                print("File path supplied is not a valid file location.")
        except Exception as e:
            msg = "File loading error: {}.\n".format(filename)
            print(msg + "\n" + e.message)
    else:
        print("No file path supplied.")