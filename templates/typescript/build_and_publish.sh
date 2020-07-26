#!/usr/bin/env bash
yarn install

yarn build:proto

for filename in ./dist/*.js; do
    module_name=`echo $(basename $filename) | cut -d"." -f1`
    export_string="export * from \"./$module_name\";"
    echo "$export_string" >> ./dist/index.js
    echo "$export_string" >> ./dist/index.d.ts
done

yarn publish --non-interactive
