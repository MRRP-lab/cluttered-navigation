#!/bin/bash
. ./venv
rm -rf ./data/runs
python generate_demo.py -N 500 -g 100
python data/index_gen.py

