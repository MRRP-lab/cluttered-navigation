#!/bin/bash

python3 parameter_sweep.py
cd data/
python3 index_gen.py
python3 generate_analytics.py
python3 generate_plots.py