# DCTools
[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

Combine datacard maker, signal extraction, statistical analysis and unfolding


--- 
## Standard Fit

```
rm -rf cards-VBS/combined.*
combineCards.py -S \
  cards-VBS/shapes-catSR_VBS2018.dat \
  cards-VBS/shapes-catDY_VBS2018.dat \
  cards-VBS/shapes-cat3L_VBS2018.dat \
  cards-VBS/shapes-catTT_VBS2018.dat \
  cards-VBS/shapes-catEM_VBS2018.dat  > cards-VBS/combined.dat

text2workspace.py -m 125 cards-VBS/combined.dat -o cards-VBS/combined.root

combine  -M AsymptoticLimits --datacard cards-VBS/combined.root \
  -m 125 -t -1 --name VBS \
  --rMax=10 --rMin=-10 \
  --cminFallbackAlgo Minuit2,Migrad,0:0.05 \
  --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH
```


## EFT fit

---
This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

## make-plots.py with combine prefit/postfit
Add to the configuration card containing the processes and channels the following block:
```

combinehist:
    dilep_mt:
        fitDiagnostics: /srv/cards-VBS/fitDiagnostics-dilep_mt.root
        PFSFW_fit_b: /srv/cards-VBS/test_pfsfw_bonly.root
        PFSFW_fit_s: /srv/cards-VBS/test_pfsfw_splusb.root
        channels:
          - cat3L16
          - cat3L16APV
          - cat3L17
          - cat3L18
          - catEM16
          - catEM16APV
          - catEM17
          - catEM18
          - catSR16
          - catSR16APV
          - catSR17
          - catSR18
        observable: dilep_mt
        label: "$M_T^{ll}$ [GeV]"
        edges: [0., 120., 240., 360., 480., 600.]
        channel_groups:
            3L:
                channels: [cat3L16, cat3L16APV, cat3L17, cat3L18]
                luminosity: 138
                era: RunII
            EM:
                channels: [catEM16, catEM16APV, catEM17, catEM18]
                luminosity: 138
                era: RunII
            SR:
                channels: [catSR16, catSR16APV, catSR17, catSR18]
                luminosity: 138
                era: RunII
```
The required arguments are a filepath to the fitDiagnostics output containing the fit and either the templates (generated with `--saveShapes --saveWithUncertainties --saveOverallShapes`), or two PostFitShapesFromWorkspace results for the background-only and signal+background postfit plots (PFSFW_fit_b, PFSFW_fit_s),
an associated list of channels to laod (since these may have changed during combine card creation, differing from the default config), and the observable of interest.
Optionally, override the label and edges for the histograms (binning is assumed the same between all channels) since combine strips this information.

Supposing a fitDiagnostics file exists for a given distribution (e.g. gnn fit), the postfit distributions for any other variable with datacards can be generated with teh following two commands:
`PostFitShapesFromWorkspace -d variable_combined.dat -w variable_workspace_from_combined.root --output variable_bonly.root --sampling --print --postfit --samples 500 --covariance -f fitDiagnostics.root:fit_b --total-shapes`
`PostFitShapesFromWorkspace -d variable_combined.dat -w variable_workspace_from_combined.root --output variable_splusb.root --sampling --print --postfit --samples 500 --covariance -f fitDiagnostics:fit_s --total-shapes`
where the differences are the output file name and the specification of the `fit_b` (backgroud only) or `fit_s` (signal + background) fits.

Optionally a subgroup of channel_groups can be added, which will stack the different channels together, allowing one to make multi-year plots.
Each group should have a unique name, a list of channels, and optionally should contain the luminositya and era tag to associated to the plot.

The individual channel histograms can then be created with the following command:
`python make-plots.py -i example_config.yaml --era 2018 --variables dilep_mt --channels cat3L16 cat3L16APV cat3L17 cat3L18 --combine_fit fit_b --combine_total_uncertainty total_background`
and the channel groups can be created with
`python make-plots.py -i example_config.yaml --era RunII --variables dilep_mt --combine_fit fit_b --combine_total_uncertainty total_background --combine_channel_groups 3L EM`
where `total_background` should be specified if the signals are not plotted in the histogram stack, and `total` should be specified if they are.

The combine_fit may be one of 'prefit', 'fit_b' (the background-only fit), or 'fit_s' (the signal+background fit).
The combine_total_uncertainty may be one of 'total', 'total_background' (only the uncertainty of non-signal processes, including correlations), or 'total_signal' (only the signal process(es))
Two options, `channel_blindings` and `combine_channel_group_blindings` can have lists of booleans passed to blind individual channel(_groups)

## make-plots.py with pre-combine inputs
The following commands will replicate the old default behavior of make-plots.py:
```
python make-plots.py -i config/input_UL_2016APV-amalfi.yaml --era 2016APV
python make-plots.py -i config/input_UL_2016-amalfi.yaml --era 2016
python make-plots.py -i config/input_UL_2017-amalfi.yaml --era 2017
python make-plots.py -i config/input_UL_2018-amalfi.yaml --era 2018
```