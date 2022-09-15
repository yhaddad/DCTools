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
