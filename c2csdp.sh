#!/bin/bash

codefresh get pip $1 -o yaml > /tmp/pipeline.yaml
python3 c2csdp.py /tmp/pipeline.yaml $*
