#!/usr/bin/python
# -*- coding: utf-8 -*-
#   moldynplot.dataset.__init__.py
#
#   Copyright (C) 2015-2017 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
"""
################################### MODULES ###################################
from __future__ import (absolute_import, division, print_function,
    unicode_literals)

if __name__ == "__main__":
    __package__ = str("moldynplot.dataset")
    import moldynplot.dataset

import h5py
import numpy as np


################################### CLASSES ###################################
class H5Dataset(object):
    """
    Class for managing hdf5 datasets

    .. warning::
      Will be reimplemented or removed eventually
    """

    def __init__(self, **kwargs):
        """
        Arguments:
          infiles (list): List of infiles
          infile (str): Alternatively, single infile
        """
        self.default_address = kwargs.get("default_address", "")
        self.default_key = kwargs.get("default_key", "key")
        self.datasets = {}
        self.attrs = {}

        if "infiles" in kwargs:
            self.load(infiles=kwargs.pop("infiles"))
        elif "infile" in kwargs:
            self.load(infiles=[kwargs.pop("infile")])

    def load(self, infiles, **kwargs):
        """
        Loads data from h5 files.

        Arguments:
          infiles (list): infiles
        """
        from os.path import expandvars, isfile
        import six

        for infile in infiles:
            if isinstance(infile, six.string_types):
                path = expandvars(infile)
                address = self.default_address
                key = self.default_key
            elif isinstance(infile, dict):
                path = expandvars(infile.pop("path"))
                address = infile.pop("address", self.default_address)
                key = infile.pop("key", self.default_key)
            elif isinstance(infile, list):
                if len(infile) >= 1:
                    path = expandvars(infile[0])
                else:
                    raise OSError("Path to infile not provided")
                if len(infile) >= 2:
                    address = infile[1]
                else:
                    address = self.default_address
                if len(infile) >= 3:
                    key = infile[2]
                else:
                    key = self.default_key

            if not isfile(path):
                raise OSError("h5 file '{0}' does not exist".format(path))

            with h5py.File(path) as in_h5:
                if address not in in_h5:
                    raise KeyError(
                      "Dataset {0}[{1}] not found".format(path, address))
                dataset = in_h5[address]
                self.datasets[key] = np.array(dataset)
                self.attrs[key] = dict(dataset.attrs)
            print("Loaded Dataset {0}[{1}]; Stored at {2}".format(
              path, address, key))
