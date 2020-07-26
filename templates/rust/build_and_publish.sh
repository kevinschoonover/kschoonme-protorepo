#!/usr/bin/env bash
cargo build

rm src/lib.rs

for filename in src/*.rs; do
    module_name=$(echo $(basename $filename) | cut -d"." -f1)
    echo "pub mod $module_name;" >> src/lib.rs
done

cargo publish
