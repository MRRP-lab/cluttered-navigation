#!/bin/bash
. ./venv
rm -rf ./data/runs
python ./generate_demo.py -N 500 -g 200 --boundary
python data/index_gen.py
python ./play_demo.py -N 500 -g 200 --boundary
