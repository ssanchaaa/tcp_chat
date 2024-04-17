#!/bin/bash

pushd ${BASH_SOURCE%/*} &>> "/dev/null"

python3.9 serverA.py 

popd &>> "/dev/null"

