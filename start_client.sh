#!/bin/bash

pushd ${BASH_SOURCE%/*} &>> "/dev/null"

python3.9 clientA.py

popd &>> "/dev/null"

