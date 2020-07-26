#!/usr/bin/env sh

OUT_DIR="./dist"
TS_OUT_DIR="./src"
IN_DIR="./proto"
PROTOC="$(yarn bin)/grpc_tools_node_protoc"
PROTOC_GEN_TS="$(yarn bin)/protoc-gen-ts"

mkdir -p "$OUT_DIR"
mkdir -p "$TS_OUT_DIR"

$PROTOC \
    -I="./$IN_DIR" \
    --plugin=protoc-gen-ts=$PROTOC_GEN_TS \
    --js_out=import_style=commonjs:$OUT_DIR \
    --grpc_out=grpc_js:$OUT_DIR \
    --ts_out=generate_package_definition:$OUT_DIR \
    "$IN_DIR"/*.proto
