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
    type_name = "SaveState"
    # Wildcards
    type = ["Save State (*.svs)|*.svs",
            "Fit Saves (*.fitv)|*.fitv",
            "P(r) Saves (*.prv)|*.prv",
            "Inversion Saves (*.inv)|*.inv",
            "Corfunc Saves (*.crf)|*.crf"]
    # List of allowed extensions
    ext = ['.svs', '.fitv', '.prv', '.inv', '.crf']
    # Flag to bypass extension check
    allow_all = False

    def __init__(self):
        CansasReader.__init__(self)
        self.fit_data = None
        self.prv_data = None
        self.inv_data = None
        self.cfr_data = None

    def get_file_contents(self):
        """
        Send the SASentry through each of the save state loaders
        :return:
        """
        self.data = CansasReader.get_file_contents(self)
        print("save_state_reader invoked")
        self.load_file_and_schema(self.f_open.name)
        for item in SAVE_STATE_NODES:
            print(item)
            if self.xmldoc.xpath('ns:{}'.format(item),
                                 namespaces={'ns': CANSAS_NS}):
                print("Loading {}".format(item))
                self.fit_data = FitState(self.f_open.name)
                self.cfr_data = CorfuncState(self.f_open.name)

        if self.fit_data:
            self.fit_data.show()
            self.data.append(self.fit_data)
        if self.cfr_data:
            self.cfr_data.show()
            self.data.append(self.cfr_data)
        return self.data


if __name__ == "__main__":
    try:
        # Usage: pass a file name as an argument
        #   python save_state_reader.py <filename>
        if len(sys.argv) > 1:
            filename = sys.argv[1]
            try:
                if os.path.exists(filename):
                    reader = Reader()
                    data = reader.read(filename)
                    data_set = data[0]
                else:
                    print("File path supplied is not a valid file location.")
            except Exception as e:
                msg = "File loading error: {}.\n".format(filename)
                print(msg + "\n" + e.message)
        else:
            print("No file path supplied.")
    except Exception as exc:
        print(exc.message)
