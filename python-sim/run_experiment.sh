#!/bin/bash
. ./venv
rm -rf ./data/runs
python generate_demo.py -N 100 -g 100
python data/index_gen.py

