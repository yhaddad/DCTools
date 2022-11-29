#!/bin/sh

# python makecard-boost.py --variable gnn_score --channel  catSR_VBS --name=SR  --checksyst --rebin=2 --blind --plot
# python makecard-boost.py --variable gnn_score --channel  catDY_VBS --name=cr_dy  --checksyst --rebin=2 --plot
# python makecard-boost.py --variable gnn_score --channel  catEM_VBS --name=cr_em  --checksyst --rebin=2 --plot
# python makecard-boost.py --variable gnn_score --channel  cat3L_VBS --name=cr_3l  --checksyst --rebin=2 --plot
# python makecard-boost.py --variable gnn_score --channel  catTT_VBS --name=cr_tt  --checksyst --rebin=2 --plot

python makecard-boost.py --variable dilep_mt --channel catSR --checksyst --plot
python makecard-boost.py --variable dilep_mt --channel catDY --checksyst --plot
python makecard-boost.py --variable dilep_mt --channel cat3L --checksyst --plot
python makecard-boost.py --variable dilep_mt --channel catEM --checksyst --plot
python makecard-boost.py --variable dilep_mt --channel catTT --checksyst --plot
python makecard-boost.py --variable dilep_mt --channel catNR --checksyst --plot

# python makecard-boost.py --variable gnn_score --channel  catSR_MjjBin2 --name=sr_2bin  --checksyst --rebin=2 --blind
# python makecard-boost.py --variable gnn_score --channel  catSR_VBS  --checksyst --rebin=2
# python makecard-boost.py --variable gnn_score --channel  catDY_VBS  --checksyst --rebin=2
# python makecard-boost.py --variable gnn_score --channel  catEM_VBS  --checksyst --rebin=4
# python makecard-boost.py --variable gnn_score --channel  cat3L_VBS  --checksyst --rebin=4
# python makecard-boost.py --variable gnn_score --channel  catNR_VBS  --checksyst --rebin=4
# python makecard-boost.py --variable gnn_score --channel  catTT_VBS  --checksyst --rebin=4

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


# python makecard-vbs.py --channel signal --variable nnscore \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_merge-yh.yaml \
#   --xsection=config/xsections_2018-yh.yaml
# python3 makecard-vbs.py --channel catDY --variable nnscore \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_merge-yh.yaml \
#   --xsection=config/xsections_2018-yh.yaml
# python3 makecard-vbs.py --channel cat3L --variable nnscore \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_merge-yh.yaml \
#   --xsection=config/xsections_2018-yh.yaml
# python3 makecard-vbs.py --channel catEM --variable nnscore \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_merge-yh.yaml \
#   --xsection=config/xsections_2018-yh.yaml
# python3 makecard-vbs.py --channel catTOP --variable nnscore \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_merge-yh.yaml \
#   --xsection=config/xsections_2018-yh.yaml

# python makecard.py --channel signal --variable nnscoreFlat \
#   --rebin=2 --binrange 0 1 \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml \
#   --xsection=config/xsections_2018.yaml
#
# python3 makecard.py --channel catDY --variable nnscoreFlat \
#   --rebin=3 --binrange 0 1 \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml \
#   --xsection=config/xsections_2018.yaml
#
# python3 makecard.py --channel cat3L --variable nnscoreFlat \
#   --rebin=2 --binrange 0 1 \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml \
#   --xsection=config/xsections_2018.yaml
#
# python3 makecard.py --channel catEM --variable nnscoreFlat \
#   --rebin=2 --binrange 0 1 \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml \
#   --xsection=config/xsections_2018.yaml
#
# python3 makecard.py --channel cat4L --variable nnscoreFlat \
#   --rebin=2 --binrange 0 1 \
#   --stack VBS ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_VBS_with_signal_1.yaml \
#   --xsection=config/xsections_2018.yaml


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

# python makecard.py --channel "catSignal-0jet" --variable measMT \
#   --rebin=2 --binrange 100 2000 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
# python makecard.py --channel "catSignal-1jet" --variable measMT \
#   --rebin=2 --binrange 100 2000 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
# python makecard.py --channel "catSignal-2jet" --variable measMT \
#   --rebin=2 --binrange 100 2000 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
#
# python makecard.py --channel "catSignal-0jetMM" --variable measMT \
#   --rebin=2 --binrange 100 2000 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
# python makecard.py --channel "catSignal-1jetMM" --variable measMT \
#   --rebin=2 --binrange 100 2000 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
# python makecard.py --channel "catSignal-2jetMM" --variable measMT \
#   --rebin=2 --binrange 100 2000 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
#
# python makecard.py --channel "catSignal-0jetEE" --variable measMT \
#   --rebin=2 --binrange 100 2000 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
# python makecard.py --channel "catSignal-1jetEE" --variable measMT \
#   --rebin=2 --binrange 100 2000 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
# python makecard.py --channel "catSignal-2jetEE" --variable measMT \
#   --rebin=2 --binrange 100 2000 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
#
# python3 makecard.py --channel cat3L --variable measMT \
#   --rebin=2 --binrange 0 2000 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
#
# python3 makecard.py --channel catEM --variable measMT \
#   --rebin=2 --binrange 0 2000 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
#
# python3 makecard.py --channel catDY --variable measMT \
#   --rebin=1 --binrange 0 100 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
#
# python3 makecard.py --channel catTOP --variable measMT \
#   --rebin=2 --binrange 0 2000 \
#   --stack ZZ2l2nu ZZ WZ WW VVV TOP DY data --input=config/input_UL_2018_ZZinclusive.yaml \
#   --xsection=config/xsections_2018.yaml
#
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
