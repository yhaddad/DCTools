#!/bin/sh

#python makecard-boost.py --name VBS --input ./config/input_UL_2018-adrianople-all.yaml --era 2018 --variable gnn_score --channel  vbs-DY  --rebin=10 
#python makecard-boost.py --name VBS --input ./config/input_UL_2018-adrianople-all.yaml --era 2018 --variable gnn_score --channel  vbs-TT  --rebin=10
python makecard-boost.py --name VBS --input ./config/input_UL_2018-adrianople-all.yaml --era 2018 --variable gnn_score --channel  vbs-EM  --rebin=10 --dd=False 
python makecard-boost.py --name VBS --input ./config/input_UL_2018-adrianople-all.yaml --era 2018 --variable gnn_score --channel  vbs-3L  --rebin=10 --dd=False
python makecard-boost.py --name VBS --input ./config/input_UL_2018-edirne-allDY-SR.yaml --era 2018 --variable gnn_flat  --channel  vbs-SR  --rebin=10 --dd=True
#python makecard-boost.py --name VBS --input ./config/input_UL_2018-adrianople-all.yaml --era 2018 --variable gnn_flat  --channel  vbs-SR  --rebin=10 

python makecard-boost.py --name VBS --input ./config/input_UL_2017-adrianople-all.yaml --era 2017 --variable gnn_score --channel  vbs-EM  --rebin=10 --dd=False
#python makecard-boost.py --name VBS --input ./config/input_UL_2017-adrianople-all.yaml --era 2017 --variable gnn_score --channel  vbs-TT  --rebin=10 
#python makecard-boost.py --name VBS --input ./config/input_UL_2017-adrianople-all.yaml --era 2017 --variable gnn_score --channel  vbs-DY  --rebin=10 
python makecard-boost.py --name VBS --input ./config/input_UL_2017-adrianople-all.yaml --era 2017 --variable gnn_score --channel  vbs-3L  --rebin=10 --dd=False
python makecard-boost.py --name VBS --input ./config/input_UL_2017-edirne-allDY-SR.yaml --era 2017 --variable gnn_flat  --channel  vbs-SR  --rebin=10 --dd=True
#python makecard-boost.py --name VBS --input ./config/input_UL_2017-adrianople-all.yaml --era 2017 --variable gnn_flat  --channel  vbs-SR  --rebin=10 

python makecard-boost.py --name VBS --input ./config/input_UL_2016-adrianople-all.yaml --era 2016 --variable gnn_score --channel  vbs-EM  --rebin=10 --dd=False
#python makecard-boost.py --name VBS --input ./config/input_UL_2016-adrianople-all.yaml --era 2016 --variable gnn_score --channel  vbs-TT  --rebin=10
#python makecard-boost.py --name VBS --input ./config/input_UL_2016-adrianople-all.yaml --era 2016 --variable gnn_score --channel  vbs-DY  --rebin=10
python makecard-boost.py --name VBS --input ./config/input_UL_2016-adrianople-all.yaml --era 2016 --variable gnn_score --channel  vbs-3L  --rebin=10 --dd=False
python makecard-boost.py --name VBS --input ./config/input_UL_2016-edirne-allDY-SR.yaml --era 2016 --variable gnn_flat  --channel  vbs-SR  --rebin=10 --dd=True
#python makecard-boost.py --name VBS --input ./config/input_UL_2016-adrianople-all.yaml --era 2016 --variable gnn_flat  --channel  vbs-SR  --rebin=10

python makecard-boost.py --name VBS --input ./config/input_UL_2016APV-adrianople-all.yaml --era 2016APV --variable gnn_score --channel  vbs-EM  --rebin=10 --dd=False
#python makecard-boost.py --name VBS --input ./config/input_UL_2016APV-adrianople-all.yaml --era 2016APV --variable gnn_score --channel  vbs-TT  --rebin=10
#python makecard-boost.py --name VBS --input ./config/input_UL_2016APV-adrianople-all.yaml --era 2016APV --variable gnn_score --channel  vbs-DY  --rebin=10
python makecard-boost.py --name VBS --input ./config/input_UL_2016APV-adrianople-all.yaml --era 2016APV --variable gnn_score --channel  vbs-3L  --rebin=10 --dd=False
python makecard-boost.py --name VBS --input ./config/input_UL_2016APV-edirne-allDY-SR.yaml --era 2016APV --variable gnn_flat  --channel  vbs-SR  --rebin=10 --dd=True
#python makecard-boost.py --name VBS --input ./config/input_UL_2016APV-adrianople-all.yaml --era 2016APV --variable gnn_flat  --channel  vbs-SR  --rebin=10
