SRC_DIR := ./src
DST_DIR := ./src/protobuf

all: compile

compile: 
	mkdir -p ${DST_DIR}
	protoc --proto_path=${SRC_DIR} --python_out=${DST_DIR} ./src/multiagent-pathfinding-protobuf/problem.proto
