#!/usr/bin/env bash
rm -rf xxx
export LEVEL=error
python3 c2csdp.py tests/pipelines/yeti5.yaml --ingress-host=https://lrcsdp.support.cf-cd.com \
  --log-level=$LEVEL
python3 c2csdp.py tests/pipelines/yeti4.yaml --ingress-host=https://lrcsdp.support.cf-cd.com \
  --log-level=$LEVEL
python3 c2csdp.py tests/pipelines/yeti3.yaml --ingress-host=https://lrcsdp.support.cf-cd.com \
  --log-level=$LEVEL
python3 c2csdp.py tests/pipelines/demo2.yaml --ingress-host=https://lrcsdp.support.cf-cd.com \
  --log-level=$LEVEL
python3 c2csdp.py tests/pipelines/demo1.yaml --ingress-host=https://lrcsdp.support.cf-cd.com \
  --log-level=$LEVEL
