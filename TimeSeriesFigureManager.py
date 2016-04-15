#!/usr/bin/python
# -*- coding: utf-8 -*-
#   moldynplot.TimeSeriesFigureManager.py
#
#   Copyright (C) 2015-2016 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
Generates one or more time series figures to specifications in a YAML
file.
"""
################################### MODULES ###################################
from __future__ import absolute_import,division,print_function,unicode_literals
if __name__ == "__main__":
    __package__ = str("moldynplot")
    import moldynplot
from .myplotspec.FigureManager import FigureManager
################################### CLASSES ###################################
class TimeSeriesFigureManager(FigureManager):
    """
    Manages the generation of time series figures
    """

    from .myplotspec.manage_defaults_presets import manage_defaults_presets
    from .myplotspec.manage_kwargs import manage_kwargs

    defaults = """
        draw_figure:
          subplot_kw:
            autoscale_on: False
          multi_tick_params:
            left: on
            right: off
            bottom: on
            top: off
          shared_legend: True
          shared_legend_kw:
            legend_kw:
              frameon: False
              loc: 9
              numpoints: 1
              handletextpad: 0
        draw_subplot:
          title_kw:
            verticalalignment: bottom
          xlabel: Time
          tick_params:
            direction: out
            left: on
            right: off
            bottom: on
            top: off
          grid: True
          grid_kw:
            b: True
            color: [0.8,0.8,0.8]
            linestyle: '-'
        draw_dataset:
          partner_kw:
            position: right
            tick_params:
              direction: out
              bottom: on
              top: off
              right: off
              left: off
            grid: True
            grid_kw:
              b: True
              color: [0.8,0.8,0.8]
              linestyle: '-'
            xticks:
            tick_params:
              direction: out
              bottom: on
              top: off
              right: off
              left: off
          plot_kw:
            zorder: 10
          handle_kw:
            ls: none
            marker: s
            mec: black
    """

    available_presets = """
      natcon:
        class: content
        help: "% Native contacts vs. time"
        draw_subplot:
          ylabel: "% Native Contacts"
          yticks:      [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
          yticklabels: [0,10,20,30,40,50,60,70,80,90,100]
        draw_dataset:
          ykey: percent_native_contacts
          dataset_kw:
            cls: moldynplot.CpptrajDataset.NatConDataset
            downsample_mode: mean
          partner_kw:
            yticks: [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
          plot_kw:
            drawstyle: steps
      rmsd:
        class: content
        help: Root Mean Standard Deviation (RMSD) vs. time
        draw_subplot:
          ylabel: RMSD (Å)
          yticks: [0,2,4,6,8,10]
        draw_dataset:
          ykey: rmsd
          partner_kw:
            yticks: [0,2,4,6,8,10]
          dataset_kw:
            cls: moldynplot.CpptrajDataset.CpptrajDataset
            pdist: True
            pdist_key: rmsd
            read_csv_kw:
              delim_whitespace: True
              header: 0
              index_col: 0
              names: [frame, rmsd]
      rg:
        class: content
        help: Radius of Gyration (Rg) vs. time
        draw_subplot:
          ylabel: $R_g$ (Å)
          yticks: [0,5,10,15,20,25,30]
        draw_dataset:
          ykey: rg
          partner_kw:
            yticks: [0,5,10,15,20,25,30]
          dataset_kw:
            cls: moldynplot.CpptrajDataset.CpptrajDataset
            pdist: True
            pdist_key: rg
            read_csv_kw:
              delim_whitespace: True
              header: 0
              index_col: 0
              names: [frame, rg, rgmax]
      presentation:
        class: target
        inherits: presentation
        draw_figure:
          left:       1.20
          sub_width:  7.00
          bottom:     3.10
          sub_height: 3.00
          shared_legend: True
          shared_legend_kw:
            left:       1.20
            sub_width:  7.00
            bottom:     1.90
            sub_height: 0.50
            legend_kw:
              labelspacing: 0.0
              ncol: 5
        draw_dataset:
          partner_kw:
            sub_width: 1.2
            title_fp: 18r
            xlabel_kw:
              labelpad: 20
            label_fp: 18r
            tick_fp: 14r
            xticks:
            lw: 2
            tick_params:
              length: 3
              pad: 6
              width: 2
          handle_kw:
            ms: 12
            mew: 2
      manuscript:
        class: target
        inherits: manuscript
        draw_figure:
          left:       0.50
          sub_width:  4.40
          right:      0.20
          bottom:     0.70
          sub_height: 1.80
          top:        0.25
          shared_legend_kw:
            left:       0.50
            sub_width:  4.40
            bottom:     0.00
            sub_height: 0.30
            legend_kw:
              labelspacing: 0.5
              legend_fp: 7r
              ncol: 5
        draw_subplot:
          xlabel_kw:
            labelpad: 3
          ylabel_kw:
            labelpad: 6
        draw_dataset:
          partner_kw:
            hspace:    0.05
            sub_width: 0.8
            title_fp: 8b
            xlabel_kw:
              labelpad: 12.5
            label_fp: 8b
            tick_fp: 6r
            tick_params:
              length: 2
              pad: 3
              width: 1
          plot_kw:
            lw: 1
          handle_kw:
            ms: 6
            mew: 1
      notebook:
        class: target
        inherits: notebook
        draw_figure:
          left:       0.60
          sub_width:  4.40
          right:      0.20
          bottom:     1.00
          sub_height: 1.80
          top:        0.30
          shared_legend: True
          shared_legend_kw:
            left:       0.60
            sub_width:  4.40
            right:      0.20
            bottom:     0.00
            sub_height: 0.50
            legend_kw:
              labelspacing: 0.5
              legend_fp: 8r
              ncol: 2
        draw_dataset:
          plot_kw:
            lw: 1.0
          partner_kw:
            sub_width: 0.8
            title_fp: 10b
            xlabel_kw:
              labelpad:  12.5
            label_fp: 10b
            tick_fp: 8r
            xticks:
            tick_params:
              length: 2
              pad: 6
              width: 1
      pdist:
        class: appearance
        help: Draw probability distribution on right side of plot
        draw_dataset:
          draw_pdist: True
          partner_kw:
            xlabel:      Distribution
            xticks:      [0,0.000001]
            xticklabels: []
            yticklabels: []
    """

    @manage_defaults_presets()
    @manage_kwargs()
    def draw_dataset(self, subplot, label=None,
        ykey=None, handles=None,
        draw_pdist=False, draw_fill_between=False, draw_plot=True,
        verbose=1, debug=0, **kwargs):
        from warnings import warn
        from .myplotspec import get_colors, multi_get_copy

        # Load data
        dataset_kw = multi_get_copy("dataset_kw", kwargs, {})
        if "infile" in kwargs:
            dataset_kw["infile"] = kwargs["infile"]
        dataset = self.load_dataset(verbose=verbose, debug=debug, **dataset_kw)
        dataframe = dataset.dataframe

        # Configure plot settings
        plot_kw = multi_get_copy("plot_kw", kwargs, {})
        get_colors(plot_kw, kwargs)

        # Plot pdist
        if draw_pdist:

            # Add subplot if not already present
            if not hasattr(subplot, "_mps_partner_subplot"):
                from .myplotspec.axes import add_partner_subplot

                add_partner_subplot(subplot, verbose=verbose,
                  debug=debug, **kwargs)

            if not (hasattr(dataset, "pdist_x")
            and     hasattr(dataset, "pdist_y")):
                warn("'draw_pdist' is enabled but dataset does not have the "
                     "necessary attributes 'pdist_x' and 'pdist_y', skipping.")
            else:
                pdist_kw = plot_kw.copy()
                pdist_kw.update(kwargs.get("pdist_kw", {}))

                subplot._mps_partner_subplot.plot( dataset.pdist_y,
                  dataset.pdist_x, **pdist_kw)
                pdist_max = dataset.pdist_y.max()
                x_max = subplot._mps_partner_subplot.get_xbound()[1]
                if pdist_max > x_max / 1.25:
                    subplot._mps_partner_subplot.set_xbound(0, pdist_max*1.25)
                    xticks = [0, pdist_max*0.25, pdist_max*0.50,
                      pdist_max*0.75, pdist_max, pdist_max*1.25]
                    subplot._mps_partner_subplot.set_xticks(xticks)

        # Plot fill_between
        if draw_fill_between:
            fill_between_kw = multi_get_copy("fill_between_kw", kwargs, {})
            get_colors(fill_between_kw, plot_kw)
            fill_between_lb_key = kwargs.get("fill_between_lb_key")
            fill_between_ub_key = kwargs.get("fill_between_ub_key")
            subplot.fill_between(dataframe.index.values, 
              dataframe[fill_between_lb_key],
              dataframe[fill_between_ub_key], **fill_between_kw)

        # Plot series
        if draw_plot:
            plot = subplot.plot(dataframe.index.values, dataframe[ykey],
              **plot_kw)[0]
            handle_kw = multi_get_copy("handle_kw", kwargs, {})
            handle_kw["mfc"] = plot.get_color()
            handle = subplot.plot([-10, -10], [-10, -10], **handle_kw)[0]
            if handles is not None and label is not None:
                handles[label] = handle

#################################### MAIN #####################################
if __name__ == "__main__":
    TimeSeriesFigureManager().main()
