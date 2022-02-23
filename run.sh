#!/usr/bin/env bash
rm -rf xxx
export LEVEL=debug
for file in when6 CR1743 yeti5 yeti4 yeti3 demo2 
do
  echo "Run $file:"
  python3 c2csdp.py tests/pipelines/${file}.yaml --ingress-host=https://lrcsdp.support.cf-cd.com \
  --log-level=$LEVEL
  echo
  echo
  exit 0
done

# python3 c2csdp.py tests/pipelines/yeti5.yaml --ingress-host=https://lrcsdp.support.cf-cd.com \
#   --log-level=$LEVEL
# python3 c2csdp.py tests/pipelines/yeti4.yaml --ingress-host=https://lrcsdp.support.cf-cd.com \
#   --log-level=$LEVEL
# python3 c2csdp.py tests/pipelines/yeti3.yaml --ingress-host=https://lrcsdp.support.cf-cd.com \
#   --log-level=$LEVEL
# python3 c2csdp.py tests/pipelines/demo2.yaml --ingress-host=https://lrcsdp.support.cf-cd.com \
#   --log-level=$LEVEL
# python3 c2csdp.py tests/pipelines/demo1.yaml --ingress-host=https://lrcsdp.support.cf-cd.com \
#   --log-level=$LEVEL
