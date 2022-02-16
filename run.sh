#!/usr/bin/env bash
rm -rf xxx
python3 c2csdp.py test/yeti3.yaml --ingress-host=https://lrcsdp.support.cf-cd.com \
  --log-level=debug
python3 c2csdp.py test/demo2.yaml --ingress-host=https://lrcsdp.support.cf-cd.com
python3 c2csdp.py test/demo1.yaml --ingress-host=https://lrcsdp.support.cf-cd.com
