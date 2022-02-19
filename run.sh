#!/usr/bin/env bash
rm -rf xxx
export LEVEL=error
for file in CR1743.yaml yeti5.yaml yeti4.yaml yeti3.yaml demo2.yaml 
do
  echo "Run $file:"
  python3 c2csdp.py tests/pipelines/$file --ingress-host=https://lrcsdp.support.cf-cd.com \
  --log-level=$LEVEL
  echo
  echo
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
