#!/usr/bin/env bash
yarn install

yarn build:proto

yarn publish --non-interactive
