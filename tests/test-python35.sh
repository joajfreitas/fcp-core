#!/bin/bash

virtualenv --python=/usr/bin/python3.5 python35
source python35/bin/activate

python ../setup.py install
fcp

deactivate
rm -rf python35
