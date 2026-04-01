PY_SRC_DIR := ./src
PY_DST_DIR := ./src/protobuf
JAVA_SRC_DIR := ./src/optimal-mrppg

all: compile

compile: 
	mkdir -p ${PY_DST_DIR}
	protoc --proto_path=${PY_SRC_DIR} --python_out=${PY_DST_DIR} ./src/multiagent-pathfinding-protobuf/problem.proto
	$(MAKE) -C ${JAVA_SRC_DIR}
