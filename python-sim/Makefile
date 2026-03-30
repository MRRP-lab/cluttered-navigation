PY_SRC_DIR := ./src
PY_DST_DIR := ./src/protobuf
JAVA_SRC_DIR := ./src/optimal-mrppg
JAVA_DST_DIR := ./src/optimal-mrppg/source/projects/multipath/Server/protobuf


all: compile

compile: 
	mkdir -p ${PY_DST_DIR} ${JAVA_DST_DIR}
	protoc --proto_path=${PY_SRC_DIR} --python_out=${PY_DST_DIR} ./src/multiagent-pathfinding-protobuf/problem.proto
	protoc --proto_path=${JAVA_SRC_DIR} --java_out=${JAVA_DST_DIR} ./src/optimal-mrppg/multiagent-pathfinding-protobuf/problem.proto
