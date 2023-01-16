#!/bin/sh

python makecard-boost.py --input ./config/input_UL_2018-amalfi.yaml --era 2018 --variable gnn_score --channel  vbs-DY  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2018-amalfi.yaml --era 2018 --variable gnn_score --channel  vbs-TT  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2018-amalfi.yaml --era 2018 --variable gnn_score --channel  vbs-EM  --rebin=5  
python makecard-boost.py --input ./config/input_UL_2018-amalfi.yaml --era 2018 --variable gnn_score --channel  vbs-3L  --rebin=5  
python makecard-boost.py --input ./config/input_UL_2018-amalfi.yaml --era 2018 --variable gnn_flat  --channel  vbs-SR  --rebin=5  

python makecard-boost.py --input ./config/input_UL_2017-amalfi.yaml --era 2017 --variable gnn_score --channel  vbs-EM  --rebin=5  
python makecard-boost.py --input ./config/input_UL_2018-amalfi.yaml --era 2017 --variable gnn_score --channel  vbs-TT  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2017-amalfi.yaml --era 2017 --variable gnn_score --channel  vbs-DY  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2017-amalfi.yaml --era 2017 --variable gnn_score --channel  vbs-3L  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2017-amalfi.yaml --era 2017 --variable gnn_flat  --channel  vbs-SR  --rebin=5   

python makecard-boost.py --input ./config/input_UL_2016-amalfi.yaml --era 2016 --variable gnn_score --channel  vbs-EM  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2018-amalfi.yaml --era 2016 --variable gnn_score --channel  vbs-TT  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2016-amalfi.yaml --era 2016 --variable gnn_score --channel  vbs-DY  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2016-amalfi.yaml --era 2016 --variable gnn_score --channel  vbs-3L  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2016-amalfi.yaml --era 2016 --variable gnn_flat  --channel  vbs-SR  --rebin=5   

python makecard-boost.py --input ./config/input_UL_2016APV-amalfi.yaml --era 2016APV --variable gnn_score --channel  vbs-EM  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2016APV-amalfi.yaml --era 2016APV --variable gnn_score --channel  vbs-TT  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2016APV-amalfi.yaml --era 2016APV --variable gnn_score --channel  vbs-DY  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2016APV-amalfi.yaml --era 2016APV --variable gnn_score --channel  vbs-3L  --rebin=5 
python makecard-boost.py --input ./config/input_UL_2016APV-amalfi.yaml --era 2016APV --variable gnn_flat  --channel  vbs-SR  --rebin=5 
