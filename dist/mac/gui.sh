#!/bin/bash
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:./dist
cd ./dist
./asad -g
