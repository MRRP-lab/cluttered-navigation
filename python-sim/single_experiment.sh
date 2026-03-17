#!/bin/bash
. ./venv
rm -rf ./data/runs
python ./generate_demo.py -N 1 -g 20 --boundary
python data/index_gen.py
python ./play_demo.py -N 1 -g 20 --boundary
