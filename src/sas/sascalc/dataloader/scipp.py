import os
import sys
import logging
import time
import numpy as np

from sas.sascalc.dataloader.data_info import Data1D

logger = logging.getLogger(__name__)
has_scipp = True

try:
    import scipp as sc
except ImportError:
    print("sci++ library must be installed.")
    print("https://scipp.github.io/")
    has_scipp = False

def convert_dataset(dataset=None):
    if not has_scipp or dataset is None:
        return None
    # TODO: decide on Data1D/Data2D depending on 
    # the content of the dataset
    data = Data1D()

    data.x = dataset.coords['Q'].values
    data.y = dataset['I(Q)'].values
    # This assumes `dy` is present.
    # we should check for `dy`/`dx` in general.
    data.dy = dataset['dy'].values
    data.dx = np.array([0.0]*len(data.x))
    data.qmin = np.min(data.x)
    data.qmax = np.max(data.x)
    # mask can also be imported from Dataset
    mask = [False]*len(data.x)
    data.mask = np.array(mask)

    return data
