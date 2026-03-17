#!/bin/bash
. ./venv
rm -rf ./data/runs
python ./generate_demo.py "$@"
python data/index_gen.py
python ./play_demo.py "$@"
