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
from sas.sascalc.fit.pagestate import Reader, PageState, SimFitPageState, CUSTOM_MODEL
from sas.sascalc.dataloader.readers.cansas_reader import Reader as CansasReader

from sas.sascalc.fit.AbstractFitEngine import FResult
from sas.sascalc.fit.AbstractFitEngine import FitData1D, FitData2D

from sasmodels.sasview_model import SasviewModel
from sasmodels import convert

from sas.qtgui.MainWindow.DataState import DataState

logger = logging.getLogger(__name__)
#Probably take from fitting widget functionality that copie stored_data to fitsate

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

    def _old_first_model(self):
        """
        Handle save states from 4.0.1 and before where the first item in the
        selection boxes of category, formfactor and structurefactor were not
        saved.
        :return: None
        """
        self.categorycombobox = CUSTOM_MODEL
        if self.formfactorcombobox == '':
            FIRST_FORM = {
                'Shapes' : 'BCCrystalModel',
                'Uncategorized' : 'LineModel',
                'StructureFactor' : 'HardsphereStructure',
                'Ellipsoid' : 'core_shell_ellipsoid',
                'Lamellae' : 'lamellar',
                'Paracrystal' : 'bcc_paracrystal',
                'Parallelepiped' : 'core_shell_parallelepiped',
                'Shape Independent' : 'be_polyelectrolyte',
                'Sphere' : 'adsorbed_layer',
                'Structure Factor' : 'hardsphere',
                CUSTOM_MODEL : ''
            }
            if self.categorycombobox == '':
                if len(self.parameters) == 3:
                    self.categorycombobox = "Shape-Independent"
                    self.formfactorcombobox = 'PowerLawAbsModel'
                elif len(self.parameters) == 9:
                    self.categorycombobox = 'Cylinder'
                    self.formfactorcombobox = 'barbell'
                else:
                    msg = "Save state does not have enough information to load"
                    msg += " the all of the data."
                    logger.warning(msg=msg)
            else:
                self.formfactorcombobox = FIRST_FORM[self.categorycombobox]

    def param_remap_from_sasmodels_convert(self, params):
        """
        Converts {name : value} map back to [] param list
        :param params: parameter map returned from sasmodels
        :return: None
        """
        p_map = []
        for name, info in params.items():
            if ".fittable" in name or ".std" in name or ".upper" in name or \
                    ".lower" in name or ".units" in name:
                pass
            else:
                fittable = params.get(name + ".fittable", True)
                std = params.get(name + ".std", '0.0')
                upper = params.get(name + ".upper", 'inf')
                lower = params.get(name + ".lower", '-inf')
                units = params.get(name + ".units")
                if std is not None and std is not np.nan:
                    std = [True, str(std)]
                else:
                    std = [False, '']
                if lower is not None and lower is not np.nan:
                    lower = [True, str(lower)]
                else:
                    lower = [True, '-inf']
                if upper is not None and upper is not np.nan:
                    upper = [True, str(upper)]
                else:
                    upper = [True, 'inf']
                param_list = [bool(fittable), str(name), str(info),
                              "+/-", std, lower, upper, str(units)]
                p_map.append(param_list)
        return p_map

    def _convert_to_sasmodels(self, parameters):
        """
        Convert parameters to a form usable by sasmodels converter

        :return: None
        """
        # Create conversion dictionary to send to sasmodels
        #self._old_first_model()
        #print('Parameters', parameters.keys())

        for key in parameters.keys():
            #Skipping non-obvious cases for the moment
            if key=='is_batch' or key=='batch_grid':
                continue
            if 'cs_tab' in key:
                continue
            for kye in parameters[key].keys():
                print("kye, val", kye)
                if 'fit_params' in kye:
                    params = parameters[key][kye]
                    for parameter in params[0].keys():
                        print('Fit_parameter values', parameter, params[0][parameter])
        # p = self.param_remap_to_sasmodels_convert(parameters)
        # structurefactor, params = convert.convert_model(self.structurecombobox,
        #                                                 p, False, self.version)
        # formfactor, params = convert.convert_model(self.formfactorcombobox,
        #                                            params, False, self.version)
        # if len(self.str_parameters) > 0:
        #     str_pars = self.param_remap_to_sasmodels_convert(
        #         self.str_parameters, True)
        #     formfactor, str_params = convert.convert_model(
        #         self.formfactorcombobox, str_pars, False, self.version)
        #     for key, value in str_params.items():
        #         params[key] = value
        #
        # if self.formfactorcombobox == 'SphericalSLDModel':
        #     self.multi_factor += 1
        # self.formfactorcombobox = formfactor
        # self.structurecombobox = structurefactor
        # self.parameters = []
        # self.parameters = self.param_remap_from_sasmodels_convert(params)

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

    def save_svs(self, filename, fitstate=None):
        """
        Write the content of a Data1D as a CanSAS XML file only for standalone

        :param filename: name of the file to write
        :param datainfo: Data1D object
        :param fitstate: PageState object

        """
        # Sanity check
        if self.cansas:
            # Add fitting information to the XML document
            doc = self.save_toXML(fitstate)
            # Write the XML document
        else:
            doc = fitstate.to_xml(file=filename)

        # Save the document no matter the type
        fd = open(filename, 'w')
        fd.write(doc.toprettyxml())
        fd.close()

    def save_toXML(self, state=None, batchfit=None):
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
        return new_stored_data

#TODO: provide inverse compatibilty
#The alternative is to save xml per data file and parse only parameters.
#Take a look again how json to sasmodels is initiated
# def readProjectFromSVS(filepath):
#     """
#     Read old SVS file and convert to the project dictionary
#     """
#     from sas.sascalc.dataloader.readers.cansas_reader import Reader as CansasReader
#     from sas.sascalc.fit.pagestate import Reader
#
#     loader = Loader()
#     loader.associate_file_reader('.svs', Reader)
#     temp = loader.load(filepath)
#
#     # CRUFT: SasView 4.x uses a callback interface to register bits of state
#     state_svs = []
#     def collector(state=None, datainfo=None, format=None):
#         if state is not None:
#             state_svs.append(state)
#     state_reader = Reader(call_back=collector)
#     data_svs = state_reader.read(filepath)
#
#     if isinstance(temp, list) and isinstance(state_svs, list):
#         output = list(zip(temp, state_svs))
#     else:
#         output = [(temp, state_svs)]
#     return output
#
def convertToSVS(json_params):
    """
    Read in properties from JSON and converts it into SVS pagestate
    """
    content = {}
    reader = Reader()
    pagestate = PageState()
    #First setup what can and the remaining
    param_dict = json_params['fit_params'][0]
    #Setup model parameters first and if they need to be overwriten it should be updated later
    data = json_params['fit_data'][0]
    pagestate.data = data
    pagestate.is_2D = True if param_dict['2D_params'][0] == 'True' else False
    pagestate.enable2D = True if param_dict['2D_params'][0] == 'True' else False
    pagestate.name = param_dict['model_name']
    pagestate.categorycombobox = param_dict['fitpage_category'][0]
    pagestate.formfactorcombobox = param_dict['fitpage_model'][0]
    pagestate.structurecombobox = param_dict['fitpage_structure'][0]
    pagestate.data_id = param_dict['data_id'][0]
    pagestate.data_name = param_dict['data_name'][0]
    pagestate.is_data = param_dict['is_data'][0]
    pagestate.magnetic_on = True if param_dict['magnetic_params'][0] == 'True' else False
    pagestate.enable_disp = True if param_dict['polydisperse_params'][0] == 'True' else False
    pagestate.qmax = param_dict['q_range_max'][0]
    pagestate.qmin = param_dict['q_range_min'][0]
    pagestate.parameters = []
    index = 0
    print('param dict', json_params)
    for parameter in param_dict.keys():
        if len(param_dict[parameter]) == 6 and (parameter != 'phi' or parameter != 'theta'):
            # Skip if there are 2D parameters - what if user have custom variables called like this
            # TODO: What is the lenght for parameter dict
            pagestate.parameters.append([None] * 8)
            pagestate.parameters[index][0] = True if param_dict[parameter][0] == 'True' else False
            pagestate.parameters[index][1] = parameter
            pagestate.parameters[index][2] = param_dict[parameter][1]
            # TODO: Where is the source for this?
            pagestate.parameters[index][3] = '+/-'
            pagestate.parameters[index][4] = [''] * 2
            pagestate.parameters[index][4][0] = False
            if param_dict[parameter][2] != '':
                pagestate.parameters[index][4][0] = True
                pagestate.parameters[index][4][1] = param_dict[parameter][2]
            pagestate.parameters[index][5] = [''] * 2
            if param_dict[parameter][3] != '':
                pagestate.parameters[index][5][0] = True
                pagestate.parameters[index][5][1] = param_dict[parameter][3]
            pagestate.parameters[index][6] = [''] * 2
            if param_dict[parameter][4] != '':
                pagestate.parameters[index][6][0] = True
                pagestate.parameters[index][6][1] = param_dict[parameter][4]
            # TODO: It seems that we are missing unit in json file
            pagestate.parameters[index][7] = ''
            if pagestate.is_2D:
                pagestate.orientation_params.append([None] * 8)
                pagestate.orientation_params[index][0] = True if param_dict[parameter][0] == 'True' else False
                pagestate.orientation_params[index][1] = parameter
                pagestate.orientation_params[index][2] = param_dict[parameter][1]
                # TODO: Where is the source for this?
                pagestate.orientation_params[index][3] = '+/-'
                pagestate.orientation_params[index][4] = [''] * 2
                pagestate.orientation_params[index][4][0] = False
                if param_dict[parameter][2] != '':
                    pagestate.orientation_params[index][4][0] = True
                    pagestate.orientation_params[index][4][1] = param_dict[parameter][2]
                pagestate.orientation_params[index][5] = [''] * 2
                if param_dict[parameter][3] != '':
                    pagestate.orientation_params[index][5][0] = True
                    # TODO: Otherwise conversion needs to be provided?
                    pagestate.orientation_params[index][5][1] = '-inf' if param_dict[parameter][3] == '-360.0' else \
                        param_dict[parameter][3]
                pagestate.orientation_params[index][6] = [''] * 2
                if param_dict[parameter][4] != '':
                    pagestate.orientation_params[index][6][0] = True
                    # TODO: Otherwise conversion needs to be provided?
                    pagestate.orientation_params[index][6][1] = 'inf' if param_dict[parameter][4] == '360.0' else \
                        param_dict[parameter][3]
                # TODO: It seems that we are missing unit in json file
                pagestate.orientation_params[index][7] = ''
            index += 1

        # if param_dict['polydisperse_params'] and len(param_dict[parameter]) == 8:
        #     #TODO: Need to initialize disp_obj_dict
        #     print('Polydisperse params', param_dict['polydisperse_params'])
        #     pagestate.parameters.append([None] * 8)
        #     pagestate.parameters[index][0] = True if param_dict[parameter][0] == 'True' else False
        #     pagestate.parameters[index][1] = parameter
        #     pagestate.parameters[index][2] = param_dict[parameter][1]
        #     # TODO: Where is the source for this?
        #     pagestate.parameters[index][3] = '+/-'
        #     pagestate.parameters[index][4] = [''] * 2
        #     pagestate.parameters[index][4][0] = False
        #     if param_dict[parameter][2] != '':
        #         pagestate.parameters[index][4][0] = True
        #         pagestate.parameters[index][4][1] = param_dict[parameter][2]
        #     pagestate.parameters[index][5] = [''] * 2
        #     if param_dict[parameter][3] != '':
        #         pagestate.parameters[index][5][0] = True
        #         pagestate.parameters[index][5][1] = param_dict[parameter][3]
        #     pagestate.parameters[index][6] = [''] * 2
        #     if param_dict[parameter][4] != '':
        #         pagestate.parameters[index][6][0] = True
        #         pagestate.parameters[index][6][1] = param_dict[parameter][4]
        #     # TODO: It seems that we are missing unit in json file
        #     pagestate.parameters[index][7] = ''
        #     index += 1
        #     pagestate.parameters[index].append([None] * 9)
        #     pagestate.parameters[index][1] = parameter
        #     #[p_opt, p_width, p_min, p_max, p_npts, p_nsigmas, p_disp] = param_dict[paramter]
        #     pagestate.parameters[parameter][0] = param_dict[parameter][0]
        #     pagestate.parameters[parameter][2] = param_dict[parameter][2]
        #
        #     param_npts = parameter.replace('.npts', '.width')
        #     param_nsigmas = parameter.replace('.nsigmas', '.width')

    if param_dict['smearing'] == '1':
        pagestate.enable_smearer = True
        pagestate.slit_smearer = param_dict['smearing']
    elif param_dict['smearing'] == '2':
        pagestate.enable_smearer = True
        pagestate.pinhole_smearer = param_dict['smearing']
    else:
        pagestate.enable_smearer = False

    if param_dict['weighting'] == '2':
        pagestate.dI_noweight = True
    elif param_dict['weighting'] == '3':
        pagestate.dI_didata = True
    elif param_dict['weighting'] == '4':
        pagestate.dI_sqrdata = True
    elif param_dict['weighting'] == '5':
        pagestate.dI_idata = True
    else:
        pagestate.dI_noweight = False
        pagestate.dI_didata = False
        pagestate.dI_sqrdata = False
        pagestate.dI_jdata = False

        #content[pagestate.data_id]['fit_params'] = param_dict
    print('pagestate data ', pagestate.__repr__())
    #state_reader = Reader()
    #state_reader.write('headless.svs', data, pagestate)
    return pagestate



if __name__ == "__main__":
    js = JsonManager()
    reader = Reader()
    parameters = js.load_from_readable(open('/Users/wojciechpotrzebowski/Desktop/sasview_proj_5.0_2d.json'))
    #state_svs = []
    for state in parameters.keys():
        if state != 'batch_grid' and state!='is_batch':
            pagestate = convertToSVS(parameters[state])

    #TODO: so loading works - now need to save it to svs file
    #js.save_to_writable(open('local_json.json','w'))
