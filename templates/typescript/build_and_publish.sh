#!/usr/bin/env bash
yarn install

yarn build:proto

module_files=`ls ./dist/*.js`

mv index.js dist/

for filename in $module_files; do
    module_name=`echo $(basename $filename) | cut -d"." -f1`
    echo "__export(require(\"./$module_name\"));" >> ./dist/index.js
    echo "export * from \"./$module_name\";" >> ./dist/index.d.ts
done

yarn publish --non-interactive
