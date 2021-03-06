#!/usr/bin/python
# -*- coding: utf-8 -*-
#   moldynplot.dataset.TimeSeriesDataset.py
#
#   Copyright (C) 2015-2017 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
Represents timeseries data

.. todo:
  - Fix separation and ordering of argument groups: input, action, output
  - Move in faster text loader from cpptraj2hdf5.py
"""
################################### MODULES ###################################
from __future__ import (absolute_import, division, print_function,
    unicode_literals)
if __name__ == "__main__":
    __package__ = str("moldynplot.dataset")
    import moldynplot.dataset
import h5py
import numpy as np
import pandas as pd
import six
from IPython import embed
from ..myplotspec.Dataset import Dataset
from ..myplotspec import wiprint, sformat
################################### CLASSES ###################################
class TimeSeriesDataset(Dataset):
    """
    Represents timeseries data

    Attributes:
      timeseries_df (DataFrame): DataFrame whose index corresponds
        to time as represented by frame number or chemical time and
        whose columns are a series of quantities as a function of time.
    """

    @staticmethod
    def construct_argparser(parser_or_subparsers=None, **kwargs):
        """
        Adds arguments to an existing argument parser,
        constructs a subparser, or constructs a new parser

        Arguments:
          parser_or_subparsers (ArgumentParser, _SubParsersAction,
            optional): If ArgumentParser, existing parser to which
            arguments will be added; if _SubParsersAction, collection
            of subparsers to which a new argument parser will be
            added; if None, a new argument parser will be generated
          kwargs (dict): Additional keyword arguments

        Returns:
          ArgumentParser: Argument parser or subparser
        """
        import argparse
        add_argument = Dataset.add_argument

        # Process arguments
        help_message = """Process timeseries data"""
        if isinstance(parser_or_subparsers, argparse.ArgumentParser):
            parser = parser_or_subparsers
        elif isinstance(parser_or_subparsers, argparse._SubParsersAction):
            parser = parser_or_subparsers.add_parser(name="timeseries",
              description=help_message, help=help_message)
        elif parser_or_subparsers is None:
            parser = argparse.ArgumentParser(description=help_message)

        # Defaults
        if parser.get_default("cls") is None:
            parser.set_defaults(cls=TimeSeriesDataset)

        # Arguments unique to this class
        arg_groups = {ag.title: ag for ag in parser._action_groups}

        # Action arguments
        action_group = arg_groups.get("action",
          parser.add_argument_group("action"))
        add_argument(action_group, "-dt", type=float,
          help="""time between frames""")
        add_argument(action_group, "-toffset", type=float,
          help="""add offset to index (time or frame number)""")
        add_argument(action_group, "-downsample", metavar="N_FRAMES", type=int,
          help="""downsample data""")
        add_argument(action_group, "--pdist", const=True, default=False,
          dest="calc_pdist", nargs="?",
          help="""calculate probability distribution over timeseries""")
        add_argument(action_group, "--pdist_bandwidth",
          default=argparse.SUPPRESS, dest="pdist_bandwidth",
          metavar="BANDWIDTH", type=float,
          help="""kernel bandwidth to be used in probability distribution
          calculation""")
        add_argument(action_group, "--pdist_grid", default=argparse.SUPPRESS,
          dest="pdist_grid", nargs=3, type=float,
          help="""grid to be used in probability distribution calculation; min,
          max, and interval passed to numpy.arange""")
        add_argument(action_group, "--mean", const=True, default=False,
          dest="calc_mean", nargs="?",
          help="""calculate mean and standard error over timeseries""")

        # Arguments inherited from superclass
        Dataset.construct_argparser(parser)

        return parser

    def __init__(self, dt=None, toffset=None, downsample=None,
      calc_pdist=False, calc_mean=False, outfile=None, interactive=False,
      **kwargs):
        """
        Arguments:
          infile{s} (list): Path(s) to input file(s); may contain
            environment variables and wildcards
          outfile (): Path to output file; may contain enviroment variables
            and wildcards
          dt (float): Time interval between points; units unspecified
          toffset (float): Time offset to be added to all points (i.e.
            time of first point)
          downsample (int): Interval by which to downsample points
          downsample_mode (str): Method of downsampling; may be 'mean'
            or 'mode'
          calc_pdist (bool): Calculate probability distribution using
            :method:`calc_pdist`; store in instance variable `pdist_df`
          pdist_kw (dict): Keyword arguments used to configure
            probability distribution calculation
          calc_mean (bool): Calculate mean and standard error using
            :method:`calc_mean`; store in instance variable `sequence_df`
          interactive (bool): Provide iPython prompt and reading and
            processing data
          verbose (int): Level of verbose output
          kwargs (dict): Additional keyword arguments

          .. todo:
            - Calculate pdist using histogram
            - Verbose pdist
            - Check for pre-existance of dfs, only load if not already
            loaded;  this may be useful for allowing subclasses to smoothly
            call their parents' __init__ methods
        """

        # Process arguments
        verbose = kwargs.get("verbose", 1)
        if not hasattr(self, "dataset_cache") or self.dataset_cache is None:
            self.dataset_cache = kwargs.get("dataset_cache", None)

        # Read data
        if not hasattr(self, "timeseries_df"):
            self.timeseries_df = self.df = self.read(**kwargs)

        # Process data
        if dt:
            self.timeseries_df.set_index(
              self.timeseries_df.index.values * float(dt), inplace=True)
            self.timeseries_df.index.name = "time"
        if toffset:
            index_name = self.timeseries_df.index.name
            self.timeseries_df.set_index(
              self.timeseries_df.index.values + float(toffset), inplace=True)
            self.timeseries_df.index.name = index_name
        if downsample:
            self.timeseries_df = self.downsample(df=self.timeseries_df,
              downsample=downsample, **kwargs)

        # Output data
        if verbose >= 2:
            print("Processed timeseries DataFrame:")
            print(self.timeseries_df)
        if outfile is not None:
            self.write(df=self.timeseries_df, outfile=outfile, **kwargs)

        # Calculate probability distibution
        if calc_pdist:
            pdist_kw = kwargs.get("pdist_kw", {})
            if "pdist_bandwidth" in kwargs:
                pdist_kw["bandwidth"] = kwargs["pdist_bandwidth"]
            if "pdist_grid" in kwargs:
                pdist_kw["grid"] = np.arange(kwargs["pdist_grid"][0],
                  kwargs["pdist_grid"][1], kwargs["pdist_grid"][2])
            self.pdist_df = self.calc_pdist(df=self.timeseries_df,
              verbose=verbose, **pdist_kw)

            # Output data
            if verbose >= 2:
                print("Processed pdist DataFrame:")
                print(self.pdist_df)
            if isinstance(calc_pdist, six.string_types):
                self.write(df=self.pdist_df, outfile=calc_pdist, **kwargs)

        # Calculate mean and standard error
        if calc_mean:
            block_kw = dict(min_n_blocks=2, max_cut=0.1, all_factors=False,
              fit_exp=True, fit_sig=False)
            block_kw.update(kwargs.get("block_kw", {}))
            self.mean_df, self.block_averager = self.calc_mean(
              df=self.timeseries_df, verbose=verbose, **block_kw)

            # Output data
            if verbose >= 2:
                print("Processed mean DataFrame:")
                print(self.mean_df)
            if isinstance(calc_mean, six.string_types):
                self.write(df=self.mean_df, outfile=calc_mean, **kwargs)

        # Interactive prompt
        if interactive:
            embed()

    @staticmethod
    def downsample(df, downsample, downsample_mode="mean", **kwargs):
        """
        Downsamples time series.

        Arguments:
          df (DataFrame): Timeseries DataFrame to downsample
          downsample (int): Interval by which to downsample points
          downsample_mode (str): Method of downsampling; may be 'mean'
            or 'mode'
          verbose (int): Level of verbose output
          kwargs (dict): Additional keyword arguments
        """
        from scipy.stats.mstats import mode

        # Process arguments
        verbose = kwargs.get("verbose", 1)

        # Truncate dataset
        reduced = df.values[:df.shape[0] - (df.shape[0] % downsample), :]
        new_shape = (
            int(reduced.shape[0] / downsample), downsample, reduced.shape[1])
        index = np.reshape(
          df.index.values[:df.shape[0] - (df.shape[0] % downsample)],
          new_shape[:-1]).mean(axis=1)
        reduced = np.reshape(reduced, new_shape)

        # Downsample
        if downsample_mode == "mean":
            if verbose >= 1:
                wiprint("downsampling by factor of {0} using mean".format(
                  downsample))
            reduced = np.squeeze(reduced.mean(axis=1))
        elif downsample_mode == "mode":
            if verbose >= 1:
                wiprint("downsampling by factor of {0} using mode".format(
                  downsample))
            reduced = np.squeeze(mode(reduced, axis=1)[0])

        # Store downsampled time series
        reduced = pd.DataFrame(data=reduced, index=index,
          columns=df.columns.values)
        reduced.index.name = "time"
        df = reduced

        return df

    @staticmethod
    def calc_mean(df, mode="se", **kwargs):
        """
        Calculates the mean over a timeseries

        Arguments:
          df (DataFrame): Timeseries DataFrame over which to calculate mean and
            standard error of each column over rows
          mode (string): If 'se', calculate mean and standard error; if
            'percentile', calculate mean, 2.5th percentile, and 97.5th
            percentile (i.e. range encompassing 95% of data)
          all_factors (bool): Use all factors by which the
            dataset is divisible rather than only factors of two (standard
            error only)
          min_n_blocks (int): Minimum number of blocks after
            transformation (standard error only)
          max_cut (float): Maximum proportion of dataset of
            omit in transformation (standard error only)
          fit_exp (bool): Fit exponential curve (standard error only)
          fit_sig (bool): Fit sigmoid curve (standard error only)
          verbose (int): Level of verbose output
          kwargs (dict): Additional keyword arguments

        Returns:
          DataFrame: DataFrame including mean and standard error for each
          column
        """
        # Process arguments
        verbose = kwargs.get("verbose", 1)

        if mode == "se":
            from ..fpblockaverager.FPBlockAverager import FPBlockAverager

            # Process arguments
            fit_exp = kwargs.get("fit_exp", True)
            fit_sig = kwargs.get("fit_sig", True)
            if verbose >= 1:
                wiprint(
                  """Calculating mean and standard error over timeseries""")

            # Single-level columns
            if df.columns.nlevels == 1:
                mean_df = pd.DataFrame(data=df.mean(axis=0))
                block_averager = FPBlockAverager(df, **kwargs)
                if fit_exp and not fit_sig:
                    errors = block_averager.parameters.loc[("exp", "a (se)")]
                elif fit_sig and not fit_exp:
                    errors = block_averager.parameters.loc[("sig", "b (se)")]
                elif fit_exp and fit_sig:
                    errors = block_averager.parameters.loc[("exp", "a (se)")]
                else:
                    raise Exception()
                mean_df = mean_df.join(errors)

            # Double-level columns
            elif df.columns.nlevels == 2:
                mean_df = pd.DataFrame(data=df.mean(axis=0))
                block_averager = FPBlockAverager(df, **kwargs)
                if fit_exp and not fit_sig:
                    errors = block_averager.parameters.loc[("exp", "a (se)")]
                elif fit_sig and not fit_exp:
                    errors = block_averager.parameters.loc[("sig", "b (se)")]
                elif fit_exp and fit_sig:
                    errors = block_averager.parameters.loc[("exp", "a (se)")]
                else:
                    raise Exception()
                errors.index = pd.MultiIndex.from_tuples(
                  map(eval, errors.index.values))
                errors.index = errors.index.set_levels(
                  [c + " se" for c in errors.index.levels[1].values], level=1)
                mean_df = mean_df.squeeze().unstack().join(errors.unstack())
                mean_df = mean_df[
                    ["r1", "r1 se", "r2", "r2 se", "noe", "noe se", "s2",
                        "s2 se"]]
                mean_df = mean_df.loc[sorted(mean_df.index.values,
                  key=lambda x: int(x.split(":")[1]))]
            else:
                raise Exception("Additional MultiIndex Levels not tested")

            return mean_df, block_averager
        elif mode == "percentile":
            if verbose >= 1:
                wiprint("""Calculating mean and range encompassing 95% of data
                over timeseries""")
            mean_df = df.mean().to_frame().reset_index(drop=True)
            percentile_df = pd.DataFrame(
              np.percentile(df.values, [2.5, 97.5, 5, 95], axis=0).transpose())
            mean_df = pd.concat([mean_df, percentile_df], axis=1,
              ignore_index=True)
            mean_df.index = df.columns.values
            mean_df.columns = ["mean", "2.5th percentile", "97.5th percentile",
                "5th percentile", "95th percentile"]
            return mean_df, None
        else:
            raise Exception()

    @staticmethod
    def calc_pdist(df, columns=None, mode="kde", bandwidth=None, grid=None,
      **kwargs):
        """
        Calcualtes probability distribution over DataFrame.

        Arguments:
          df (DataFrame): DataFrame over which to calculate probability
            distribution of each column over rows
          columns (list): Columns for which to calculate probability
            distribution
          mode (ndarray, str, optional): Method of calculating
            probability distribution; eventually will support 'hist' for
            histogram and 'kde' for kernel density estimate, though
            presently only 'kde' is implemented
          bandwidth (float, dict, str, optional): Bandwidth to use for
            kernel density estimates; may be a single float that will be
            applied to all columns or a dictionary whose keys are column
            names and values are floats corresponding to the bandwidth
            for each column; for any column for which *bandwidth* is not
            specified, the standard deviation will be used
          grid (list, ndarray, dict, optional): Grid on which to
            calculate kernel density estimate; may be a single ndarray
            that will be applied to all columns or a dictionary whose
            keys are column names and values are ndarrays corresponding
            to the grid for each column; for any column for which *grid*
            is not specified, a grid of 1000 points between the minimum
            value minus three times the standard deviation and the
            maximum value plots three times the standard deviation will
            be used
          kde_kw (dict, optional): Keyword arguments passed to
            :function:`sklearn.neighbors.KernelDensity`
          verbose (int): Level of verbose output
          kwargs (dict): Additional keyword arguments

        Returns:
          OrderedDict: Dictionary whose keys are columns in *df* and
          values are DataFrames whose indexes are the *grid* for that
          column and contain a single column 'probability' containing
          the normalized probability at each grid point

        .. todo:
            - Implement flag to return single dataframe with single grid
        """
        from sklearn.neighbors import KernelDensity

        # Process arguments
        verbose = kwargs.get("verbose", 1)
        if verbose >= 1:
            wiprint("""Calculating probability distribution over DataFrame""")

        if mode == "kde":

            # Prepare bandwidths
            if bandwidth is None:
                bandwidth = df.values.std()

            # Prepare grids
            if grid is None:
                grid = np.linspace(df.values.min() - 3 * bandwidth,
                  df.values.max() + 3 * bandwidth, 1000)
            elif isinstance(grid, list):
                grid = np.array(grid)

            # Calculate probability distributions
            kde_kw = kwargs.get("kde_kw", {})
            pdist = np.zeros((grid.size, df.columns.size))
            for i, column in enumerate(df.columns.values):
                series = df[column]
                if verbose >= 1:
                    wiprint("calculating probability distribution of "
                            "{0} using a kernel density estimate".format(
                      column))
                kde = KernelDensity(bandwidth=bandwidth, **kde_kw)
                kde.fit(series.dropna()[:, np.newaxis])
                pdf = np.exp(kde.score_samples(grid[:, np.newaxis]))
                pdf /= pdf.sum()
                pdist[:,i] = pdf
            pdist = pd.DataFrame(pdist, index=grid, columns=df.columns)
        else:
            raise Exception(sformat("""only kernel density estimation is
                                    currently supported"""))

        return pdist

#################################### MAIN #####################################
if __name__ == "__main__":
    TimeSeriesDataset.main()
