#!/bin/sh

python makecard-boost.py --name DDVBS --input ./config/input_UL_2018-sinai.yaml --era 2018 --dd --variable gnn_score --channel  vbs-EM  --rebin=10  
python makecard-boost.py --name DDVBS --input ./config/input_UL_2018-sinai.yaml --era 2018 --dd --variable gnn_score --channel  vbs-3L  --rebin=10  
python makecard-boost.py --name DDVBS --input ./config/input_UL_2018-sinai.yaml --era 2018 --dd --variable gnn_flat  --channel  vbs-SR  --rebin=10  

python makecard-boost.py --name DDVBS --input ./config/input_UL_2017-sinai.yaml --era 2017 --dd --variable gnn_score --channel  vbs-EM  --rebin=10  
python makecard-boost.py --name DDVBS --input ./config/input_UL_2017-sinai.yaml --era 2017 --dd --variable gnn_score --channel  vbs-3L  --rebin=10
python makecard-boost.py --name DDVBS --input ./config/input_UL_2017-sinai.yaml --era 2017 --dd --variable gnn_flat  --channel  vbs-SR  --rebin=10   

python makecard-boost.py --name DDVBS --input ./config/input_UL_2016-sinai.yaml --era 2016 --dd --variable gnn_score --channel  vbs-EM  --rebin=10
python makecard-boost.py --name DDVBS --input ./config/input_UL_2016-sinai.yaml --era 2016 --dd --variable gnn_score --channel  vbs-3L  --rebin=10
python makecard-boost.py --name DDVBS --input ./config/input_UL_2016-sinai.yaml --era 2016 --dd --variable gnn_flat  --channel  vbs-SR  --rebin=10  

python makecard-boost.py --name DDVBS --input ./config/input_UL_2016APV-sinai.yaml --era 2016APV --dd --variable gnn_score --channel  vbs-EM  --rebin=10
python makecard-boost.py --name DDVBS --input ./config/input_UL_2016APV-sinai.yaml --era 2016APV --dd --variable gnn_score --channel  vbs-3L  --rebin=10
python makecard-boost.py --name DDVBS --input ./config/input_UL_2016APV-sinai.yaml --era 2016APV --dd --variable gnn_flat  --channel  vbs-SR  --rebin=10


python makecard-boost.py --name VBS --input ./config/input_UL_2018-sinai-woDD.yaml --era 2018 --variable gnn_score --channel  vbs-DY  --rebin=10 
python makecard-boost.py --name VBS --input ./config/input_UL_2018-sinai-woDD.yaml --era 2018 --variable gnn_score --channel  vbs-EM  --rebin=10  
python makecard-boost.py --name VBS --input ./config/input_UL_2018-sinai-woDD.yaml --era 2018 --variable gnn_score --channel  vbs-3L  --rebin=10  
python makecard-boost.py --name VBS --input ./config/input_UL_2018-sinai-woDD.yaml --era 2018 --variable gnn_flat  --channel  vbs-SR  --rebin=10  

python makecard-boost.py --name VBS --input ./config/input_UL_2017-sinai-woDD.yaml --era 2017 --variable gnn_score --channel  vbs-EM  --rebin=10  
python makecard-boost.py --name VBS --input ./config/input_UL_2017-sinai-woDD.yaml --era 2017 --variable gnn_score --channel  vbs-DY  --rebin=10  
python makecard-boost.py --name VBS --input ./config/input_UL_2017-sinai-woDD.yaml --era 2017 --variable gnn_score --channel  vbs-3L  --rebin=10
python makecard-boost.py --name VBS --input ./config/input_UL_2017-sinai-woDD.yaml --era 2017 --variable gnn_flat  --channel  vbs-SR  --rebin=10   

python makecard-boost.py --name VBS --input ./config/input_UL_2016-sinai-woDD.yaml --era 2016 --variable gnn_score --channel  vbs-EM  --rebin=10
python makecard-boost.py --name VBS --input ./config/input_UL_2016-sinai-woDD.yaml --era 2016 --variable gnn_score --channel  vbs-DY  --rebin=10
python makecard-boost.py --name VBS --input ./config/input_UL_2016-sinai-woDD.yaml --era 2016 --variable gnn_score --channel  vbs-3L  --rebin=10
python makecard-boost.py --name VBS --input ./config/input_UL_2016-sinai-woDD.yaml --era 2016 --variable gnn_flat  --channel  vbs-SR  --rebin=10  

python makecard-boost.py --name VBS --input ./config/input_UL_2016APV-sinai-woDD.yaml --era 2016APV --variable gnn_score --channel  vbs-EM  --rebin=10
python makecard-boost.py --name VBS --input ./config/input_UL_2016APV-sinai-woDD.yaml --era 2016APV --variable gnn_score --channel  vbs-DY  --rebin=10
python makecard-boost.py --name VBS --input ./config/input_UL_2016APV-sinai-woDD.yaml --era 2016APV --variable gnn_score --channel  vbs-3L  --rebin=10
python makecard-boost.py --name VBS --input ./config/input_UL_2016APV-sinai-woDD.yaml --era 2016APV --variable gnn_flat  --channel  vbs-SR  --rebin=10