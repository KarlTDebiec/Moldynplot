#!/usr/bin/python
# -*- coding: utf-8 -*-
#   moldynplot.PDist2DFigureManager.py
#
#   Copyright (C) 2015-2017 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
Generates 2D probability distribution figures to specifications
"""
################################### MODULES ###################################
from __future__ import (absolute_import, division, print_function,
    unicode_literals)
if __name__ == "__main__":
    __package__ = str("moldynplot")
    import moldynplot
from .myplotspec.FigureManager import FigureManager
from .myplotspec.manage_defaults_presets import manage_defaults_presets
from .myplotspec.manage_kwargs import manage_kwargs
################################### CLASSES ###################################
class PDist2DFigureManager(FigureManager):
    """
    Manages the generation of 2D probability distribution figures.
    """

    defaults = """
        draw_figure:
          subplot_kw:
            autoscale_on: False
          multi_tick_params:
            bottom: on
            left: on
            right: off
            top: off
          shared_legend: False
          shared_legend_kw:
            spines: False
            handle_kw:
              ls: none
              marker: s
              mec: black
            legend_kw:
              borderaxespad: 0
              frameon: False
              handletextpad: 0
              loc: 9
              numpoints: 1
        draw_subplot:
          title_kw:
            verticalalignment: bottom
          xlabel: Residue
          tick_params:
            direction: out
            bottom: on
            top: off
            left: on
            right: off
          grid: True
          vline_kw:
            zorder: 9
            lw: 1
            color: [0.0, 0.0, 0.0]
            zorder: 9
          label_kw:
            zorder: 10
            horizontalalignment: left
            verticalalignment: top
        draw_dataset:
          draw_heatmap: True
          heatmap_kw:
            edgecolors: none
            rasterized: True
            zorder: 0.1
            vmin: 0
            vmax: 100000
          colorbar_kw:
            tick_params:
              left: off
              right: off
              bottom: off
              top: off
          mask_kw:
            cmap: Greys_r
            edgecolors: none
            rasterized: True
            vmin: 0
            vmax: 1
            zorder: 0.3
    """
    available_presets = """
      distance:
        class: content
        help: Plot inter-atomic distance in terms of probability
        draw_figure:
          multi_yticklabels: [0,10,20,30,40,50,60,70]
        draw_subplot:
          yticks: [0,10,20,30,40,50,60,70]
        draw_dataset:
          draw_heatmap: True
          min_cutoff: 0.00001
          heatmap_kw:
            cmap: magma_r
            vmin: 0.00
            vmax: 0.04
          draw_colorbar: True
          colorbar_kw:
            zticks: [0.00,0.01,0.02,0.03,0.04]
            zticklabels: []
            zlabel: Probability
      distance_free_energy:
        class: content
        help: Plot inter-atomic distance in terms of free energy
        extends: distance
        draw_dataset:
          logz: True
          heatmap_kw:
            vmin: 0
            vmax: 5
          colorbar_kw:
            zticks: [0,1,2,3,4,5]
            zlabel: ΔG (kcal/mol)
      gamma2:
        class: content
        help: Plot Γ2
        draw_figure:
          multi_yticklabels: [0,10,20,30,40,50,60,70]
        draw_subplot:
          yticks: [0,10,20,30,40,50,60,70]
        draw_dataset:
          draw_heatmap: True
          heatmap_kw:
            cmap: afmhot_r
            vmin: 0.00
            vmax: 1.00
          gamma2_z: True
          draw_mask: True
          min_cutoff: 0.00001
          draw_colorbar: True
          colorbar_kw:
            zticks: [0.2,0.4,0.6,0.8,1.0]
            zticklabels: []
            zlabel: Contribution to $Γ_2$
      manuscript:
        class: target
        inherits: manuscript
        draw_figure:
          left:       0.50
          sub_width:  3.80
          wspace:     0.10
          right:      0.10
          bottom:     0.35
          sub_height: 1.00
          hspace:     0.10
          top:        0.10
          title_kw:
            top: -0.1
          shared_xlabel_kw:
            bottom: -0.24
          shared_legend_kw:
            left:       0.50
            sub_width:  3.80
            bottom:     0.00
            sub_height: 0.20
            handle_kw:
              ms: 5
            legend_kw:
              labelspacing: 0.5
              legend_fp: 7r
              ncol: 6
        draw_subplot:
          xlabel_kw:
            labelpad: 3
          ylabel_kw:
            labelpad: 6
          y2ticks: []
          y2label_kw:
            rotation: 270
            verticalalignment: bottom
          draw_label: True
          label_kw:
            border_lw: 1
            xabs:  0.020
            yabs: -0.025
        draw_dataset:
          partner_kw:
            position: right
            wspace:    0.05
            sub_width: 0.05
          colorbar_kw:
            ztick_fp:  6r
            zlabel_fp: 8b
            zlabel_kw:
              labelpad: 0
    """

    @manage_defaults_presets()
    @manage_kwargs()
    def draw_dataset(self, subplot, min_cutoff=None, logz=False,
        draw_heatmap=True, draw_mask=True, draw_colorbar=True, **kwargs):
        import numpy as np
        from .myplotspec import get_colors, multi_get_copy

        # Process arguments and load data
        verbose = kwargs.get("verbose", 1)
        dataset_kw = multi_get_copy("dataset_kw", kwargs, {})
        if "infile" in kwargs:
            dataset_kw["infile"] = kwargs["infile"]
        dataset = self.load_dataset(verbose=verbose, **dataset_kw)
        if dataset is not None and hasattr(dataset, "pdist_df"):
            pdist_df = dataset.pdist_df
        else:
            pdist_df = dataset.dataframe
        x = np.array( [filter(lambda x: x in "0123456789.", s)
              for s in pdist_df.columns.values], np.int)

        # Configure plot settings
        plot_kw = multi_get_copy("plot_kw", kwargs, {})
        get_colors(plot_kw, kwargs)

        # Draw heatmap
        if draw_heatmap:
            heatmap_kw = multi_get_copy("heatmap_kw", kwargs, {})
            hm_x = np.arange(x.min(), x.max()+2, 1, np.int)
            hm_y = pdist_df.index.values
            hm_z = np.zeros((hm_x.size, hm_y.size)) * np.nan

            gamma2_z = kwargs.get("gamma2_z", False)
            if gamma2_z:
                k   = 0.0123    # Å6 ns-2
                w   = 800e6     # s-1
                tc  = 6.72e-9 # CVNH: 8.7e-9; LysM: 6.72e-9   # s
                gamma2 = k / (hm_y ** 6) * 1e9 * 1e9
                gamma2 *= (4 * tc + ((3 * tc) / (1 + (w * tc ) ** 2)))

            subensemble_pop = kwargs.get("subensemble_pop", None)
            draw_outline = kwargs.get("draw_outline", True)
            if draw_outline:
                ol_x = []
                ol_ylb = []
                ol_yub = []

            for residue in range(x.min(), x.max() + 1):
                index_within_hm = np.argmax(hm_x == residue)
                try:
                    index_within_pdist = np.where(x == residue)[0][0]
                except IndexError:
                    hm_z[index_within_hm][:] = np.nan
                    if draw_outline:
                        ol_x.append(None)
                        ol_ylb.append(None)
                        ol_yub.append(None)
                    continue
                    
                pdist_of_residue = pdist_df.values[:, index_within_pdist]

                # Normalize, optionally scale by extected sum
                pdist_of_residue /= np.nansum(pdist_of_residue)
                if subensemble_pop is not None:
                    pdist_of_residue *= subensemble_pop

                # Set grid points below selected weight to 0
                if min_cutoff is not None:
                    pdist_of_residue[pdist_of_residue < min_cutoff] = np.nan

                # Normalize again, and optionally scale again
                pdist_of_residue /= np.nansum(pdist_of_residue)
                if subensemble_pop is not None:
                    pdist_of_residue *= subensemble_pop

                # Convert from population to population-weighted Γ2
                if gamma2_z:
                    # Skip selected residues that have distance but for which
                    #   Γ2 cannot be back-calculated
                    if (residue in [55,56,57,58,59,60,61,
                                    111,112,113,114,115,116,117]
                    or (np.isnan(pdist_of_residue).all())):
                        hm_z[index_within_hm][:] = np.nan
                        if draw_outline:
                            ol_x.append(None)
                            ol_ylb.append(None)
                            ol_yub.append(None)
                        continue
                    pdist_of_residue *= gamma2
                    #print("{0:>4d} {1:>8.2f} {2:>8.2f}".format(residue,
                    #  np.nansum(pdist_of_residue), np.nanmax(pdist_of_residue)))
                if draw_outline:
                    ol_x.extend([residue - 0.5, residue + 0.5])
                    nonzero = np.where(np.logical_not(np.isnan(pdist_of_residue)))[0]
                    ol_ylb.extend([hm_y[nonzero[0]], hm_y[nonzero[0]]])
                    ol_yub.extend([hm_y[nonzero[-1]], hm_y[nonzero[-1]]])

                hm_z[index_within_hm] = pdist_of_residue
            hm_z = hm_z.T
            if logz:
                hm_z = -1 * np.log10(hm_z)
            pcolormesh = subplot.pcolor(hm_x - 0.5, hm_y, hm_z, **heatmap_kw)
            if draw_mask:
                mask_kw = multi_get_copy("mask_kw", kwargs, {})
                mask_z = np.ma.masked_where(
                  np.logical_not(np.isnan(hm_z)),
                  np.ones_like(hm_z))
                subplot.pcolormesh(hm_x - 0.5, hm_y, mask_z, **mask_kw)
            if draw_outline:
                outline_kw = kwargs.get("outline_kw", {})
                subplot.plot(ol_x, ol_ylb, **outline_kw)
                subplot.plot(ol_x, ol_yub, **outline_kw)

            # Draw colorbar
            if draw_colorbar:
                from .myplotspec.axes import set_colorbar
                if not hasattr(subplot, "_mps_partner_subplot"):
                    from .myplotspec.axes import add_partner_subplot
                    add_partner_subplot(subplot, **kwargs)
                set_colorbar(subplot, pcolormesh, **kwargs)

#################################### MAIN #####################################
if __name__ == "__main__":
    PDist2DFigureManager().main()