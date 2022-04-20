#!/bin/sh
# python makecard.py --channel signal --variable dijet_Mjj \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel catDY --variable dijet_Mjj \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel cat3L --variable dijet_Mjj \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel catEM --variable dijet_Mjj \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
#  python3 makecard.py --channel cat4L --variable dijet_Mjj \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml


# python makecard.py --channel signal --variable nnscore \
#   --rebin=1 --binrange 0 1 \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel catDY --variable nnscore \
#  --rebin=1 --binrange 0 1 \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel cat3L --variable nnscore \
#  --rebin=1 --binrange 0 1 \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel catEM --variable nnscore \
#  --rebin=1 --binrange 0 1 \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
#  python3 makecard.py --channel cat4L --variable nnscore \
#  --rebin=1 --binrange 0 1 \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml

# python makecard.py --channel signal --variable nnscoreFlat \
#   --rebin=1 --binrange 0 1 \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel catDY --variable nnscoreFlat \
#  --rebin=1 --binrange 0 1 \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel cat3L --variable nnscoreFlat \
#  --rebin=1 --binrange 0 1 \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel catEM --variable nnscoreFlat \
#  --rebin=1 --binrange 0 1 \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
#  python3 makecard.py --channel cat4L --variable nnscoreFlat \
#  --rebin=1 --binrange 0 1 \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml


# python makecard.py --channel signal --variable phizmet \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel catDY --variable phizmet \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel cat3L --variable phizmet \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel catEM --variable phizmet \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
#  python3 makecard.py --channel cat4L --variable phizmet \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml


# python makecard.py --channel signal --variable measMET \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel cat3L --variable measMET \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel catEM --variable measMET \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel cat4L --variable measMET \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml
# python3 makecard.py --channel cat4L --variable measMET \
#  --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml

python makecard.py --channel "catSignal-0jet" --variable measMT \
 --rebin=1 --binrange 0 2000 \
 --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
python makecard.py --channel "catSignal-1jet" --variable measMT \
 --rebin=1 --binrange 0 2000 \
 --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
python makecard.py --channel "catSignal-2jet" --variable measMT \
 --rebin=1 --binrange 0 2000 \
 --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml

python makecard.py --channel "catSignal-0jetMM" --variable measMT \
 --rebin=1 --binrange 0 2000 \
 --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
# python makecard.py --channel "catSignal-1jetMM" --variable measMT \
#  --rebin=1 --binrange 0 2000 \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
# python makecard.py --channel "catSignal-2jetMM" --variable measMT \
#  --rebin=1 --binrange 0 2000 \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml

#  python makecard.py --channel "catSignal-0jetEE" --variable measMT \
#  --rebin=1 --binrange 0 2000 \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
# python makecard.py --channel "catSignal-1jetEE" --variable measMT \
#  --rebin=1 --binrange 0 2000 \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
# python makecard.py --channel "catSignal-2jetEE" --variable measMT \
#  --rebin=1 --binrange 0 2000 \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml

# python3 makecard.py --channel cat3L --variable measMT \
#  --rebin=2 --binrange 0 2000 \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
# python3 makecard.py --channel catEM --variable measMT \
#  --rebin=2 --binrange 0 2000 \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
# python3 makecard.py --channel cat4L --variable measMT \
#  --rebin=2 --binrange 0 2000 \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
# python3 makecard.py --channel catDY --variable measMT \
#  --rebin=2 --binrange 0 2000 \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml



# python makecard.py --channel "catSignal-0jet" --variable phizmet \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
# python makecard.py --channel "catSignal-1jet" --variable phizmet \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
# python3 makecard.py --channel cat3L --variable phizmet \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
# python3 makecard.py --channel catEM --variable phizmet \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
# python3 makecard.py --channel cat4L --variable phizmet \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml
# python3 makecard.py --channel catDY --variable phizmet \
#  --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml

# scp -r cards-VBS lxplus.cern.ch:/afs/cern.ch/user/y/yhaddad/work/CMSSW_9_3_0/CMSSW_10_2_13/src

# combineCards.py -S \
#   cards-VBS/shapes-signal2018.dat \
#   cards-VBS/shapes-cat3L2018.dat \
#   cards-VBS/shapes-catDY2018.dat \
#   cards-VBS/shapes-catEM2018.dat > cards-VBS/combined.dat

# text2workspace.py -m 125 cards-VBS/combined.dat -o cards-VBS/combined.root

# combine  -M AsymptoticLimits --datacard cards-VBS/combined.root \
#   -m 125 -t -1 --name VBS \
#   --rMax=10 --rMin=-10 \
#   --cminFallbackAlgo Minuit2,Migrad,0:0.05 \
#   --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH
