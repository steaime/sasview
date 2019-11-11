################################################################################
#This software was developed by the University of Tennessee as part of the
#Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
#project funded by the US National Science Foundation.
#
#See the license text in license.txt
#
#copyright 2010, University of Tennessee
################################################################################
"""
This module manages all data loaded into the application. Data_manager makes
available all data loaded  for the current perspective.

All modules "creating Data" posts their data to data_manager .
Data_manager  make these new data available for all other perspectives.
"""
#
# REDUNDANT CLASS!!!
# ALL THE FUNCTIONALITY IS BEING MOVED TO GuiManager.py
#
import logging
import json
import types
import time
from io import BytesIO
import numpy as np

from sas.qtgui.Plotting.PlotterData import Data1D
from sas.qtgui.Plotting.PlotterData import Data2D
from sas.qtgui.Plotting.Plottables import PlottableTheory1D
from sas.qtgui.Plotting.Plottables import PlottableFit1D
from sas.qtgui.Plotting.Plottables import Text
from sas.qtgui.Plotting.Plottables import Chisq
from sas.qtgui.Plotting.Plottables import View
from sas.qtgui.Plotting.Plottables import Plottable

from sas.sascalc.dataloader.data_info import Sample, Source, Vector
from sas.sascalc.dataloader.data_info import Detector, Process, TransmissionSpectrum
from sas.sascalc.dataloader.data_info import Aperture, Collimation

from sas.sascalc.fit.AbstractFitEngine import FResult
from sas.sascalc.fit.AbstractFitEngine import FitData1D, FitData2D
from sasmodels.sasview_model import SasviewModel

from sas.qtgui.MainWindow.DataState import DataState

class JsonManager(object):
    """
    Manage a list of data
    """
    def __init__(self):
        """
        Store opened path and data object created at the loading time
        :param auto_plot: if True the datamanager sends data to plotting
                            plugin.
        :param auto_set_data: if True the datamanager sends to the current
        perspective
        """
        self.stored_data = {}
        self.message = ""
        self.data_name_dict = {}
        self.count = 0
        self.list_of_id = []
        self.time_stamp = time.time()

    def __str__(self):
        _str  = ""
        _str += "No of states  is %s \n" % str(len(self.stored_data))
        n_count = 0
        for  value in list(self.stored_data.values()):
            n_count += 1
            _str += "State No %s \n"  % str(n_count)
            _str += str(value) + "\n"
        return _str


    def save_to_writable(self, fp):
        """
        save content of stored_data to fp (a .write()-supporting file-like object)
        """

        def add_type(dict, type):
            dict['__type__'] = type.__name__
            return dict

        def jdefault(o):
            """
            objects that can't otherwise be serialized need to be converted
            """
            # tuples and sets (TODO: default JSONEncoder converts tuples to lists, create custom Encoder that preserves tuples)
            if isinstance(o, (tuple, set)):
                content = {'data': list(o)}
                return add_type(content, type(o))

            # "simple" types
            if isinstance(o, (Sample, Source, Vector, FResult)):
                return add_type(o.__dict__, type(o))
            # detector
            if isinstance(o, (Detector, Process, TransmissionSpectrum, Aperture, Collimation)):
                return add_type(o.__dict__, type(o))

            if isinstance(o, (Plottable, View)):
                return add_type(o.__dict__, type(o))

            # SasviewModel - unique
            if isinstance(o, SasviewModel):
                # don't store parent
                content = o.__dict__.copy()
                return add_type(content, SasviewModel)

            # DataState
            if isinstance(o, (Data1D, Data2D, FitData1D, FitData2D)):
                # don't store parent
                content = o.__dict__.copy()
                return add_type(content, type(o))

            # ndarray
            if isinstance(o, np.ndarray):
                content = {'data': o.tolist()}
                return add_type(content, type(o))

            if isinstance(o, types.FunctionType):
                # we have a pure function
                content = o.__dict__.copy()
                return add_type(content, type(o))

            # not supported
            logging.info("data cannot be serialized to json: %s" % type(o))
            return None

        json.dump(self.stored_data, fp, indent=2, sort_keys=True, default=jdefault)

    def save_svs(self, filename, datainfo=None, fitstate=None):
        """
        Write the content of a Data1D as a CanSAS XML file only for standalone

        :param filename: name of the file to write
        :param datainfo: Data1D object
        :param fitstate: PageState object

        """
        # Sanity check
        if self.cansas:
            # Add fitting information to the XML document
            doc = self.save_toXML(datainfo, fitstate)
            # Write the XML document
        else:
            doc = fitstate.to_xml(file=filename)

        # Save the document no matter the type
        fd = open(filename, 'w')
        fd.write(doc.toprettyxml())
        fd.close()

    def save_toXML(self, datainfo=None, state=None, batchfit=None):
        """
        Write toXML, a helper for write(),
        could be used by guimanager._on_save()

        : return: xml doc
        """

        self.batchfit_params = batchfit
        if state.data is None or not state.data.is_data:
            return None
        # make sure title and data run are filled.
        if state.data.title is None or state.data.title == '':
            state.data.title = state.data.name
        if state.data.run_name is None or state.data.run_name == {}:
            state.data.run = [str(state.data.name)]
            state.data.run_name[0] = state.data.name

        data = state.data
        doc, sasentry = self._to_xml_doc(data)

        if state is not None:
            doc = state.to_xml(doc=doc, file=data.filename, entry_node=sasentry,
                               batch_fit_state=self.batchfit_params)

        return doc

    def load_from_readable(self, fp):
        """
        load content from tp to stored_data (a .read()-supporting file-like object)
        """

        supported = [
            tuple, set, types.FunctionType,
            Sample, Source, Vector,
            Plottable, Data1D, Data2D, PlottableTheory1D, PlottableFit1D, Text, Chisq, View,
            Detector, Process, TransmissionSpectrum, Collimation, Aperture,
            DataState, np.ndarray, FResult, FitData1D, FitData2D, SasviewModel]

        lookup = dict((cls.__name__, cls) for cls in supported)

        class TooComplexException(Exception):
            pass

        def simple_type(cls, data, level):
            class Empty(object):
                def __init__(self):
                    for key, value in data.items():
                        setattr(self, key, generate(value, level))

            # create target object
            o = Empty()
            o.__class__ = cls

            return o

        def construct(type, data, level):
            try:
                cls = lookup[type]
            except KeyError:
                logging.info('unknown type: %s' % type)
                return None

            # tuples and sets
            if cls in (tuple, set):
                # convert list to tuple/set
                return cls(generate(data['data'], level))

            # "simple" types
            if cls in (Sample, Source, Vector, FResult, FitData1D, FitData2D,
                       SasviewModel, Detector, Process, TransmissionSpectrum,
                       Collimation, Aperture):
                return simple_type(cls, data, level)
            if issubclass(cls, Plottable) or (cls == View):
                return simple_type(cls, data, level)

            # DataState
            if cls == DataState:
                o = simple_type(cls, data, level)
                o.parent = None  # TODO: set to ???
                return o

            # ndarray
            if cls == np.ndarray:
                o = data['data']
                if isinstance(o, list):
                    # new format - ndarray as ascii list
                    return np.array(o)
                else:
                    # pre-5.0-release format - binary ndarray
                    buffer = BytesIO()
                    buffer.write(data['data'].encode('latin-1'))
                    buffer.seek(0)
                    return np.load(buffer)

            # function
            if cls == types.FunctionType:
                return cls

            logging.info('not implemented: %s, %s' % (type, cls))
            return None

        def generate(data, level):
            if level > 16:  # recursion limit (arbitrary number)
                raise TooComplexException()
            else:
                level += 1

            if isinstance(data, dict):
                try:
                    type = data['__type__']
                except KeyError:
                    # if dictionary doesn't have __type__ then it is assumed to be just an ordinary dictionary
                    o = {}
                    for key, value in data.items():
                        o[key] = generate(value, level)
                    return o

                return construct(type, data, level)

            if isinstance(data, list):
                return [generate(item, level) for item in data]

            return data

        new_stored_data = {}
        for id, data in json.load(fp).items():
            try:
                new_stored_data[id] = generate(data, 0)
            except TooComplexException:
                logging.info('unable to load %s' % id)


        self.stored_data = new_stored_data


if __name__ == "__main__":
    js = JsonManager()
    js.load_from_readable(open('/Users/wojciechpotrzebowski/Desktop/sasview_5.0_proj'))
    js.save_to_writable(open('local_json.json','w'))