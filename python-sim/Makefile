PY_SRC_DIR := ./src
PY_DST_DIR := ./src/protobuf
JAVA_SRC_DIR := ./src/optimal-mrppg
PROTOBUF := ./src/multiagent-pathfinding-protobuf/problem.proto
STAMPS := .stamps

export PYTHONPATH := $(shell pwd)

.PHONY: $(STAMPS)/plots parameter_sweep index

ARGS ?= 

# The point of stamps is to mark checkpoints in our data generation pipeline
# if that step produces some important files.
# Make is good because it can detect if targets need to be re-created based on timestamps.
# We use these stamps as definite files that we can point to to signify the time a processing step has been completed
# so that make can determine whether a processing step is now stale and needs to be re-ran.

# IF THE PIPELINE FAILS PARTWAY THROUGH
# then this method breaks. You'd need to clear the appropriate stamps and re-run.

all: $(STAMPS)/plots

parameter_sweep: $(STAMPS)/parameter_sweep
analytics: $(STAMPS)/analytics
index: 
	python3 scripts/index_gen.py

$(STAMPS)/parameter_sweep: scripts/parameter_sweep.py
	python scripts/parameter_sweep.py
	mkdir -p $(STAMPS) && touch $@

$(STAMPS)/analytics: $(STAMPS)/parameter_sweep
	python scripts/generate_analytics.py
	mkdir -p $(STAMPS) && touch $@

$(STAMPS)/plots: $(STAMPS)/analytics
	python scripts/generate_plots.py
	mkdir -p $(STAMPS) && touch $@

# How to use: make single_sim ARGS="(parameters go here)"
# Ex: make show_sim ARGS="--num 100 --density 1 --boundary --noise 0 --experiment-name 'Boundary visuals'"
# Ex: make show_sim ARGS="--simulation-id 51ec09fd99eb675a30b138d36fdc6a880ea92128013585f9aa76521b4ca986de"
single_sim: 
	python scripts/generate_demo.py $(ARGS)
	python scripts/index_gen.py
	python scripts/play_demo.py $(ARGS)

show_sim:
	python scripts/play_demo.py $(ARGS)

compile: 
	mkdir -p ${PY_DST_DIR}
	protoc --proto_path=${PY_SRC_DIR} --python_out=${PY_DST_DIR} ${PROTOBUF}
	$(MAKE) -C ${JAVA_SRC_DIR}

clean:
	rm -rf data/runs
	rm -f data/index.csv
	rm -rf $(STAMPS)
	rm -rf ${PY_DST_DIR}
	$(MAKE) clean -C ${JAVA_SRC_DIR}

